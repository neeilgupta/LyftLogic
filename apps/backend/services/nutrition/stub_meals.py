# apps/backend/services/nutrition/stub_meals.py
from __future__ import annotations

import hashlib
import math
from typing import Any, Iterable

from .ingredients_pantry import INGREDIENT_PANTRY_PER_100G
from .meal_library import MEAL_LIBRARY


def _stable_int_hash(s: str) -> int:
    h = hashlib.sha256(s.encode("utf-8")).hexdigest()
    return int(h[:16], 16)


def _round1(x: float) -> float:
    return float(round(x, 1))


def _meal_macros_from_pantry(ingredients: list[dict[str, Any]]) -> dict[str, float]:
    cals = p = c = f = 0.0
    for ing in ingredients:
        name = ing["name"]
        grams = float(ing.get("grams", 0.0))
        per100 = INGREDIENT_PANTRY_PER_100G.get(name)
        if not per100 or grams <= 0:
            continue
        factor = grams / 100.0
        cals += per100.get("calories", 0.0) * factor
        p += per100.get("protein_g", 0.0) * factor
        c += per100.get("carbs_g", 0.0) * factor
        f += per100.get("fat_g", 0.0) * factor
    return {
        "calories": _round1(cals),
        "protein_g": _round1(p),
        "carbs_g": _round1(c),
        "fat_g": _round1(f),
    }


def _sum_macros(meals: list[dict[str, Any]]) -> dict[str, float]:
    cals = p = c = f = 0.0
    for m in meals:
        mm = m.get("macros") or {}
        cals += float(mm.get("calories", 0.0))
        p += float(mm.get("protein_g", 0.0))
        c += float(mm.get("carbs_g", 0.0))
        f += float(mm.get("fat_g", 0.0))
    return {
        "calories": _round1(cals),
        "protein_g": _round1(p),
        "carbs_g": _round1(c),
        "fat_g": _round1(f),
    }


def _normalize_tokens(xs: Any) -> set[str]:
    if xs is None:
        return set()
    if isinstance(xs, str):
        return {xs.strip().lower()} if xs.strip() else set()
    out: set[str] = set()
    try:
        for x in xs:
            if x is None:
                continue
            s = str(x).strip().lower()
            if s:
                out.add(s)
    except TypeError:
        s = str(xs).strip().lower()
        if s:
            out.add(s)
    return out


def _diet_required_tags(diet: Any) -> set[str]:
    d = (str(diet).strip().lower() if diet is not None else "")
    if d == "vegan":
        return {"vegan"}
    if d == "vegetarian":
        return {"vegetarian", "vegan"}  # vegan satisfies vegetarian
    if d == "pescatarian":
        return {"pescatarian", "vegan"}  # allow vegan meals too
    return set()  # fail-open for keto/halal/etc


def _meal_allowed_by_diet(meal: dict[str, Any], required: set[str]) -> bool:
    if not required:
        return True
    # A meal is allowed if every ingredient has at least one acceptable diet tag
    for ing in meal.get("ingredients", []):
        tags = {t.lower() for t in (ing.get("diet_tags") or [])}
        if not (tags & required):
            return False
    return True


def _meal_allowed_by_allergies(meal: dict[str, Any], blocked_tokens: set[str]) -> bool:
    if not blocked_tokens:
        return True
    for ing in meal.get("ingredients", []):
        contains = {t.lower() for t in (ing.get("contains") or [])}
        if contains & blocked_tokens:
            return False
    return True


def _seed_string(req: Any, attempt: int) -> str:
    # Keep deterministic but sensitive to relevant user inputs.
    # Use getattr so we don't depend on exact schema.
    parts = [
        f"diet={getattr(req, 'diet', None)}",
        f"allergies={sorted(list(_normalize_tokens(getattr(req, 'allergies', None))))}",
        f"calories={getattr(req, 'calories', None) or getattr(req, 'target_calories', None)}",
        f"macros={getattr(req, 'macros', None)}",
        f"meals_per_day={getattr(req, 'meals_per_day', None) or getattr(req, 'meals', None)}",
        f"attempt={attempt}",
    ]
    return "|".join(parts)


def _deterministic_pick(meals: list[dict[str, Any]], seed: str, k: int) -> list[dict[str, Any]]:
    if not meals:
        return []
    # Sort by stable per-meal hash so "regenerate" changes (attempt changes seed).
    scored = []
    for m in meals:
        key = str(m.get("key", m.get("name", "")))
        score = _stable_int_hash(seed + "::" + key)
        scored.append((score, m))
    scored.sort(key=lambda x: x[0])
    ordered = [m for _, m in scored]
    if k <= 0:
        return []
    # If not enough unique meals, cycle deterministically.
    out: list[dict[str, Any]] = []
    i = 0
    while len(out) < k:
        out.append(ordered[i % len(ordered)])
        i += 1
    return out


def _find_carb_adjust_ingredient(meal: dict[str, Any]) -> int | None:
    # Prefer these carb bases for calorie-closing.
    preferred = [
        "white rice, cooked",
        "brown rice, cooked",
        "oats, dry",
        "pasta, cooked",
        "potato, baked",
        "sweet potato, baked",
        "bread, whole wheat",
        "tortilla, flour",
        "banana",
        "apple",
    ]
    ings = meal.get("ingredients", [])
    name_to_idx = {ing.get("name"): idx for idx, ing in enumerate(ings)}
    for n in preferred:
        if n in name_to_idx:
            return int(name_to_idx[n])
    return None


def _calorie_close_by_adjusting_last_meal_carbs(meals: list[dict[str, Any]], target_cals: float | None) -> None:
    if not meals or not target_cals:
        return
    totals = _sum_macros(meals)
    delta = float(target_cals) - float(totals["calories"])
    # If already close enough, do nothing.
    if abs(delta) <= 60.0:
        return

    last = meals[-1]
    idx = _find_carb_adjust_ingredient(last)
    if idx is None:
        return

    ing = last["ingredients"][idx]
    name = ing["name"]
    per100 = INGREDIENT_PANTRY_PER_100G.get(name)
    if not per100:
        return
    kcal_per_g = float(per100.get("calories", 0.0)) / 100.0
    if kcal_per_g <= 0:
        return

    grams_now = float(ing.get("grams", 0.0))
    grams_delta = delta / kcal_per_g

    # Clamp adjustment to avoid absurd meals.
    grams_new = max(0.0, min(grams_now + grams_delta, grams_now + 250.0, 600.0))
    # If we were reducing and hit 0, that's fine.
    ing["grams"] = int(round(grams_new))


def generate_stub_meals(req: Any, attempt: int) -> dict[str, Any]:
    # Determine constraints
    blocked = _normalize_tokens(getattr(req, "allergies", None))
    required = _diet_required_tags(getattr(req, "diet", None))

    # Candidate meals
    candidates = []
    for m in MEAL_LIBRARY:
        if not _meal_allowed_by_diet(m, required):
            continue
        if not _meal_allowed_by_allergies(m, blocked):
            continue
        candidates.append(m)

    # Use batch_size, meals_needed, meals_per_day, or meals from request
    k = (
        getattr(req, "batch_size", None)
        or getattr(req, "meals_needed", None)
        or getattr(req, "meals_per_day", None)
        or getattr(req, "meals", None)
        or 3
    )
    try:
        k = int(k)
    except Exception:
        k = 3

    seed = _seed_string(req, attempt)
    picked = _deterministic_pick(candidates, seed, k)

    # Build output meals (copy templates so we can mutate grams)
    out_meals: list[dict[str, Any]] = []
    for tm in picked:
        ingredients = [dict(ing) for ing in (tm.get("ingredients") or [])]
        user_diet = (str(getattr(req, "diet", "") or "").strip().lower())
        fail_open = user_diet not in {"vegan", "vegetarian", "pescatarian"}

        if fail_open:
            for ing in ingredients:
                tags = list(ing.get("diet_tags") or [])
                if "omnivore" not in {t.lower() for t in tags}:
                    tags.append("omnivore")
                ing["diet_tags"] = tags

        # Aggregate meal-level fields for allergen engine compatibility
        meal_contains: set[str] = set()
        meal_diet_tags: set[str] = set()

        for ing in ingredients:
            for t in (ing.get("contains") or []):
                s = str(t).strip().lower()
                if s:
                    meal_contains.add(s)
            for t in (ing.get("diet_tags") or []):
                s = str(t).strip().lower()
                if s:
                    meal_diet_tags.add(s)

        # If diet is None/unknown, ensure omnivore exists at meal level too
        if fail_open:
            meal_diet_tags.add("omnivore")

        macros = _meal_macros_from_pantry(ingredients)
        out_meals.append(
            {
                "key": tm.get("key"),
                "name": tm.get("name"),
                "tags": tm.get("tags", []),
                "diet_tags": sorted(list(meal_diet_tags)),
                "contains": sorted(list(meal_contains)),
                "ingredients": ingredients,
                "macros": macros,
            }
        )

    # Calorie-close if request has a target
    target = getattr(req, "calories", None) or getattr(req, "target_calories", None)
    try:
        target_f = float(target) if target is not None else None
    except Exception:
        target_f = None

    _calorie_close_by_adjusting_last_meal_carbs(out_meals, target_f)

    # Recompute macros after any adjustment
    for m in out_meals:
        m["macros"] = _meal_macros_from_pantry(m["ingredients"])

    totals = _sum_macros(out_meals)

    return {
        "meals": out_meals,
        "totals": totals,
        "meta": {
            "seed": seed,
            "diet_required": sorted(list(required)),
            "allergy_blocked": sorted(list(blocked)),
            "candidate_count": len(candidates),
        },
    }
