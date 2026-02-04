# apps/backend/services/nutrition/stub_meals.py
from __future__ import annotations

import hashlib
import math
from typing import Any, Iterable

try:
    from .ingredients_pantry import INGREDIENT_PANTRY_PER_100G
    from .meal_library import MEAL_LIBRARY
    from services.nutrition.allergens import build_allergen_set
except ImportError:
    # Fallback for standalone testing
    from meal_library import MEAL_LIBRARY
    # Create minimal mocks for testing
    INGREDIENT_PANTRY_PER_100G = {}
    def build_allergen_set(allergies):
        return set(str(a).lower() for a in allergies if a)


# Ingredient name aliases: map common/shorthand names to pantry keys
# This enables deterministic ingredient lookup without changing output names
INGREDIENT_ALIASES: dict[str, str] = {
    # Rice varieties
    "rice": "white rice, cooked",
    "white rice": "white rice, cooked",
    "brown rice": "brown rice, cooked",
    "brown rice, long-grain": "brown rice, long-grain",
    "jasmine rice": "jasmine rice, cooked",
    "basmati rice": "basmati rice, cooked",
    "wild rice": "wild rice, cooked",
    # Proteins (expanded)
    "chicken breast": "chicken breast, cooked",
    "chicken breast, cooked": "chicken breast, cooked",
    "chicken breast, skinless": "chicken breast, skinless",
    "turkey breast": "turkey breast, cooked",
    "ground chicken": "ground chicken, 93% lean",
    "ground turkey": "ground turkey, 93% lean",
    "ground beef": "ground beef, 90%, cooked",
    "ground beef 90%": "ground beef, 90%, cooked",
    "ground beef 93%": "ground beef, 93% lean",
    "salmon": "salmon, cooked",
    "salmon fillet": "salmon fillet, cooked",
    "tuna": "tuna, canned in water",
    "tuna canned": "tuna, canned in water",
    "tilapia": "tilapia, cooked",
    "cod": "cod, cooked",
    "halibut": "halibut, cooked",
    "trout": "trout, cooked",
    "tofu": "tofu, firm",
    "lentils": "lentils, cooked",
    "chickpeas": "chickpeas, cooked",
    "black beans": "black beans, cooked",
    "white beans": "white beans, cooked",
    "pinto beans": "pinto beans, cooked",
    "eggs": "eggs, whole",
    # Grains & carbs
    "pasta": "pasta, cooked",
    "oats": "oats, dry",
    "oatmeal": "oatmeal, cooked",
    "quinoa": "quinoa, cooked",
    "couscous": "couscous, cooked",
    "farro": "farro, cooked",
    "barley": "barley, pearl, cooked",
    "millet": "millet, cooked",
    "potato": "potato, baked",
    "sweet potato": "sweet potato, baked",
    "sweet potato, boiled": "sweet potato, boiled",
    "bread": "bread, whole wheat",
    "whole wheat bread": "bread, whole wheat",
    "tortilla": "tortilla, flour",
    "greek yogurt": "greek yogurt, nonfat",
    "yogurt": "greek yogurt, nonfat",
    # Fats & oils
    "olive oil": "olive oil",
    "avocado oil": "avocado oil",
    "coconut oil": "coconut oil",
    "avocado": "avocado",
}


def _stable_int_hash(s: str) -> int:
    h = hashlib.sha256(s.encode("utf-8")).hexdigest()
    return int(h[:16], 16)


def _round1(x: float) -> float:
    return float(round(x, 1))


def _meal_macros_from_pantry(ingredients: list[dict[str, Any]], debug_meta: dict[str, Any] | None = None) -> dict[str, float]:
    cals = p = c = f = 0.0
    for ing in ingredients:
        name = ing["name"]
        grams = float(ing.get("grams", 0.0))
        
        # Try alias first, then direct lookup
        canonical_name = _canonical_pantry_key(name)
        per100 = INGREDIENT_PANTRY_PER_100G.get(canonical_name)
        
        # Track missing lookups for instrumentation
        if not per100 and debug_meta is not None and grams > 0:
            if "missing_ingredients" not in debug_meta:
                debug_meta["missing_ingredients"] = []
            if canonical_name not in debug_meta["missing_ingredients"]:
                debug_meta["missing_ingredients"].append(canonical_name)
        
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

def _infer_goal_from_targets(req) -> str:
    targets = getattr(req, "targets", None)
    if not isinstance(targets, dict):
        return "maintenance"

    if "cut" in targets:
        return "cut"
    if "bulk" in targets:
        return "bulk"
    return "maintenance"


def _macro_bias_from_goal(goal: str) -> tuple[float, float, float]:
    # (protein, carbs, fat)
    if goal == "bulk":
        return (1.2, 1.1, 0.9)
    if goal == "cut":
        return (1.3, 0.8, 0.6)
    return (1.0, 1.0, 1.0)

def _canonical_pantry_key(name: Any) -> str:
    raw = str(name or "").strip()
    norm = raw.lower()
    return INGREDIENT_ALIASES.get(norm, norm)




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
        return {"vegetarian", "vegan"}
    if d == "pescatarian":
        return {"pescatarian", "vegetarian", "vegan"}  # ✅ FIX
    return set()



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


def _deterministic_pick(meals: list[dict[str, Any]], seed: str, k: int, goal: str = "maintenance") -> list[dict[str, Any]]:
    if not meals:
        return []

    scored = []
    for m in meals:
        key = str(m.get("key", m.get("name", "")))

        # 0 = pinned (test-compatible), 1 = normal
        bucket = 0 if key.startswith("-") else 1

        macro_score = float(m.get("_macro_score", 0.0))
        hash_score = _stable_int_hash(seed + "::" + key)
        # Add goal-aware ranking: bulk favors higher macros, cut disfavors fat
        goal_bias = 0
        if goal == "bulk":
            goal_bias = int(macro_score)  # higher scores for bulk
        elif goal == "cut":
            # For cut, penalize fat slightly to encourage leaner meals
            macros = m.get("_macros", {})
            fat_penalty = int(float(macros.get("fat_g", 0.0)) * 0.5)
            goal_bias = -fat_penalty
        scored.append(((bucket, goal_bias, -macro_score, hash_score), m))

    scored.sort(key=lambda x: x[0])
    ordered = [m for _, m in scored]

    if k <= 0:
        return []
    out: list[dict[str, Any]] = []
    i = 0
    while len(out) < k:
        out.append(ordered[i % len(ordered)])
        i += 1
    return out

def _deterministic_pick_for_slot(
    meals: list[dict[str, Any]],
    seed: str,
    k: int,
    slot: str,
    goal: str = "maintenance",
) -> list[dict[str, Any]]:
    """
    Deterministic slot-aware picker:
    - For snacks: prioritize variety (hash) over macro_score so you don't always get trail mix.
    - For other slots: keep existing behavior.
    """
    if not meals:
        return []

    scored = []
    for m in meals:
        key = str(m.get("key", m.get("name", "")))
        bucket = 0 if key.startswith("-") else 1

        macro_score = float(m.get("_macro_score", 0.0))
        hash_score = _stable_int_hash(seed + "::" + key)

        # Snack: variety-first (hash dominates), macro_score only as a weak tie-breaker
        if slot == "snack":
            scored.append(((bucket, hash_score, -macro_score), m))
            continue

        # Default: keep current behavior (macro_score dominates)
        goal_bias = 0
        if goal == "bulk":
            goal_bias = int(macro_score)
        elif goal == "cut":
            macros = m.get("_macros", {})
            fat_penalty = int(float(macros.get("fat_g", 0.0)) * 0.5)
            goal_bias = -fat_penalty

        scored.append(((bucket, goal_bias, -macro_score, hash_score), m))

    scored.sort(key=lambda x: x[0])
    ordered = [m for _, m in scored]

    out: list[dict[str, Any]] = []
    i = 0
    while len(out) < max(0, int(k)):
        out.append(ordered[i % len(ordered)])
        i += 1
    return out




def _find_carb_adjust_ingredient(meal: dict[str, Any]) -> int | None:
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
        "cream of rice, dry",
    ]

    ings = meal.get("ingredients", [])
    canon_to_idx = {}
    for idx, ing in enumerate(ings):
        canon_to_idx[_canonical_pantry_key(ing.get("name"))] = idx

    for want in preferred:
        if want in canon_to_idx:
            return int(canon_to_idx[want])
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
    # Use alias for lookup
    canonical_name = _canonical_pantry_key(name)
    per100 = INGREDIENT_PANTRY_PER_100G.get(canonical_name)

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
    
def _macro_targets_v1(goal: str, target_cals: float) -> dict[str, float]:
    # v1 fixed protein targets; fat is % of calories; carbs are remainder
    if goal == "cut":
        protein_g = 200.0
        fat_pct = 0.25
    elif goal == "bulk":
        protein_g = 180.0
        fat_pct = 0.30
    else:
        protein_g = 170.0
        fat_pct = 0.28

    fat_g = (target_cals * fat_pct) / 9.0
    # carbs from remaining calories
    carbs_cals = target_cals - (protein_g * 4.0) - (fat_g * 9.0)
    carbs_g = max(0.0, carbs_cals / 4.0)

    return {
        "protein_g": _round1(protein_g),
        "fat_g": _round1(fat_g),
        "carbs_g": _round1(carbs_g),
        "calories": _round1(target_cals),
    }

def _clamp_int(x: int, lo: int, hi: int) -> int:
    return lo if x < lo else hi if x > hi else x


def _infer_meals_needed_from_target(target_cals: float | None) -> int:
    if target_cals is None or target_cals <= 0:
        return 4
    if target_cals < 2300:
        return 4
    if target_cals <= 2800:
        return 5
    return 6


def _slots_for_meals_needed(n: int) -> list[str]:
    n = _clamp_int(int(n), 2, 6)
    if n == 2:
        return ["lunch", "dinner"]
    if n == 3:
        return ["breakfast", "lunch", "dinner"]
    if n == 4:
        return ["breakfast", "lunch", "dinner", "snack"]
    if n == 5:
        return ["breakfast", "lunch", "dinner", "snack", "snack"]
    return ["breakfast", "lunch", "dinner", "snack", "snack", "snack"]


def _slot_budget_percents(slots: list[str]) -> list[float]:
    n = len(slots)
    if n == 2:
        return [0.50, 0.50]
    if n == 3:
        return [1/3, 1/3, 1/3]
    if n == 4:
        return [0.25, 0.30, 0.30, 0.15]
    if n == 5:
        return [0.24, 0.26, 0.26, 0.12, 0.12]
    # n == 6
    return [0.22, 0.24, 0.24, 0.10, 0.10, 0.10]


def _round_to_nearest_10(x: float) -> int:
    # nearest 10, deterministic (0.5 goes up)
    return int(((x + 5.0) // 10.0) * 10)


def _slot_budgets(target_cals: float, slots: list[str]) -> list[int]:
    perc = _slot_budget_percents(slots)
    raw = [target_cals * p for p in perc]
    budgets = [_round_to_nearest_10(v) for v in raw]
    if budgets:
        budgets[-1] += int(round(target_cals)) - sum(budgets)
    return budgets


def _scale_meal_ingredients(meal: dict[str, Any], scale: float) -> bool:
    ings = meal.get("ingredients") or []
    if not ings:
        return False
    changed = False
    for ing in ings:
        g = ing.get("grams")
        if g is None:
            continue
        try:
            g0 = int(g)
        except Exception:
            continue
        g1 = int(round(g0 * scale))
        if g1 < 1:
            g1 = 1
        if g1 != g0:
            ing["grams"] = g1
            changed = True
    return changed


def _slot_tag_match(slot: str, tags: Iterable[str]) -> bool:
    tset = {str(t).strip().lower() for t in (tags or [])}
    if slot == "snack":
        return bool(tset & {"snack", "dessert"})
    return slot in tset



def _find_first_matching_ingredient_idx(meal: dict[str, Any], preferred_names: list[str]) -> int | None:
    ings = meal.get("ingredients", [])
    canon_to_idx = {}
    for idx, ing in enumerate(ings):
        canon_to_idx[_canonical_pantry_key(ing.get("name"))] = idx

    for want in preferred_names:
        if want in canon_to_idx:
            return int(canon_to_idx[want])
    return None



def _clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def _apply_ingredient_grams_delta(
    meal: dict[str, Any],
    idx: int,
    delta_g: float,
    per_step_cap_g: float,
    abs_cap_g: float,
) -> bool:
    # Returns True if we actually changed grams
    ings = meal.get("ingredients", [])
    if idx < 0 or idx >= len(ings):
        return False

    ing = ings[idx]
    grams_now = float(ing.get("grams", 0.0))
    if grams_now < 0:
        grams_now = 0.0

    delta_g = _clamp(delta_g, -per_step_cap_g, per_step_cap_g)
    grams_new = _clamp(grams_now + delta_g, 0.0, abs_cap_g)

    # deterministic integer grams
    grams_new_i = int(round(grams_new))
    if grams_new_i == int(round(grams_now)):
        return False

    ing["grams"] = grams_new_i
    return True


def _multi_meal_calorie_close_carbs(
    meals: list[dict[str, Any]],
    target_cals: float,
    tolerance_cals: float = 100.0,
) -> None:
    if not meals:
        return

    # Walk meals last -> first for determinism
    for _pass in range(6):  # two passes is enough for v1
        totals = _sum_macros(meals)
        delta = float(target_cals) - float(totals["calories"])
        if abs(delta) <= tolerance_cals:
            return

        for meal in reversed(meals):
            idx = _find_carb_adjust_ingredient(meal)
            if idx is None:
                continue

            ing = meal["ingredients"][idx]
            name = ing.get("name")
            # Use alias for lookup
            canonical_name = _canonical_pantry_key(name)
            per100 = INGREDIENT_PANTRY_PER_100G.get(canonical_name)
            if not per100:
                continue

            kcal_per_g = float(per100.get("calories", 0.0)) / 100.0
            if kcal_per_g <= 0:
                continue

            # grams needed to fix remaining delta
            grams_needed = delta / kcal_per_g

            changed = _apply_ingredient_grams_delta(
                meal,
                idx,
                grams_needed,
                per_step_cap_g=500.0,  # Increased from 250.0
                abs_cap_g=1000.0,        # Increased from 650.0
            )
            if not changed:
                continue

            # recompute after each change
            meal["macros"] = _meal_macros_from_pantry(meal["ingredients"])
            totals = _sum_macros(meals)
            delta = float(target_cals) - float(totals["calories"])
            if abs(delta) <= tolerance_cals:
                return


def _macro_close_v1(
    meals: list[dict[str, Any]],
    goal: str,
    target_cals: float,
) -> None:
    """
    Calories are HARD. Macros are SOFT.

    When target_cals is provided, we only close calories using carb-adjustable
    ingredients across meals. We do NOT add protein/fat to chase macro targets,
    because that can push calories away from target and trigger per-meal cap
    rejections (especially on cut targets).
    """
    if not meals:
        return

    tol_cals = 100.0
    _multi_meal_calorie_close_carbs(meals, target_cals, tolerance_cals=tol_cals)

    # Final recompute to ensure consistency
    for m in meals:
        m["macros"] = _meal_macros_from_pantry(m["ingredients"])



def generate_stub_meals(req: Any, attempt: int) -> dict[str, Any]:
    # Determine constraints
    blocked = build_allergen_set(list(getattr(req, "allergies", None) or []))
    diet = getattr(req, "diet", None)
    required = _diet_required_tags(diet)

    # Prefilter meals by diet BEFORE any selection attempts
    def _meal_passes_diet(meal: dict) -> bool:
        if not required:
            return True
        for ing in meal.get("ingredients", []):
            tags = set(t.lower() for t in (ing.get("diet_tags") or []))
            if tags.isdisjoint(required):
                return False
        return True

    # Build diet-filtered candidate pool
    diet_candidates = [m for m in MEAL_LIBRARY if _meal_passes_diet(m)]
    
    # Fail-closed: if diet is specified but no meals are available, raise error
    if diet and not diet_candidates:
        raise ValueError(f"No meals available for diet={diet}")
    
    # Use diet-filtered pool (or full library if no diet specified)
    pool = diet_candidates if diet else MEAL_LIBRARY

    # Candidate meals (apply allergy filtering to the diet-filtered pool)
    candidates_by_key: dict[str, dict[str, Any]] = {}
    for m in pool:
        if not _meal_allowed_by_allergies(m, blocked):
            continue

        k = str(m.get("key") or m.get("name") or "")
        if not k:
            continue

        # keep first occurrence deterministically
        if k not in candidates_by_key:
            candidates_by_key[k] = m

    candidates: list[dict[str, Any]] = list(candidates_by_key.values())

    # Target calories (routes usually inject this into req)
    target = getattr(req, "calories", None) or getattr(req, "target_calories", None)
    try:
        target_f = float(target) if target is not None else None
    except Exception:
        target_f = None

    # Phase 4-D: infer meals from calories unless meals_needed explicitly provided
    # Sentinel: meals_needed <= 0 means "infer from target_calories"
    raw_meals_needed = getattr(req, "meals_needed", None)
    if raw_meals_needed is not None:
        try:
            meals_needed_int = int(raw_meals_needed)
        except Exception:
            meals_needed_int = 0
        
        if meals_needed_int > 0:
            # Explicit override: user provided a positive meals_needed
            meals_needed_final = _clamp_int(meals_needed_int, 2, 6)
        else:
            # Sentinel (0 or negative): infer from calories
            meals_needed_final = _infer_meals_needed_from_target(target_f)
    else:
        # No meals_needed provided at all: infer from calories
        meals_needed_final = _infer_meals_needed_from_target(target_f)

    # batch_size (if present and positive) overrides total returned meals
    # Sentinel: batch_size <= 0 means "use meals_needed_final, don't override"
    raw_batch = getattr(req, "batch_size", None)
    if raw_batch is not None:
        try:
            batch_int = int(raw_batch)
        except Exception:
            batch_int = 0
        
        if batch_int > 0:
            # Explicit override: user provided a positive batch_size
            meals_needed_final = _clamp_int(batch_int, 2, 6)
        # else: sentinel (0 or negative) means don't override, keep meals_needed_final

    # Slots + budgets
    slots = _slots_for_meals_needed(meals_needed_final)
    budgets: list[int] = _slot_budgets(float(target_f), slots) if target_f is not None else []

    # Precompute macro scores for candidates (goal-aware ranking)
    goal = _infer_goal_from_targets(req)
    wp, wc, wf = _macro_bias_from_goal(goal)

    def _macro_score_from_macros(macros: dict[str, float]) -> float:
        return (
            wp * float(macros.get("protein_g", 0.0))
            + wc * float(macros.get("carbs_g", 0.0))
            + wf * float(macros.get("fat_g", 0.0))
        )

    for tm in candidates:
        ings = tm.get("ingredients") or []
        macros = _meal_macros_from_pantry(ings)
        tm["_macro_score"] = _macro_score_from_macros(macros)
        tm["_macros"] = macros

    # Per-slot deterministic pick
    seed = _seed_string(req, attempt)
    picked: list[dict[str, Any]] = []
    remaining = list(candidates)

    used_template_keys: set[str] = set()

    def _tkey(m: dict[str, Any]) -> str:
        return str(m.get("key") or m.get("name") or "")

    for i, slot in enumerate(slots):
        # First try: slot-match + unused templates
        slot_candidates = [
            m for m in remaining
            if _slot_tag_match(slot, m.get("tags")) and _tkey(m) not in used_template_keys
        ]

        # Fallback 1: slot-match even if repeats (only if we ran out)
        if not slot_candidates:
            slot_candidates = [m for m in remaining if _slot_tag_match(slot, m.get("tags"))]

        # Fallback 2: anything remaining (still deterministic)
        if not slot_candidates:
            if remaining:
                slot_candidates = list(remaining)
            else:
                # Prefer unused candidates even when remaining is empty
                unused_any = [m for m in candidates if _tkey(m) not in used_template_keys]
                slot_candidates = unused_any if unused_any else list(candidates)


        one = _deterministic_pick_for_slot(
            slot_candidates,
            seed + f"|slot={slot}|i={i}",
            1,
            slot=slot,
            goal=goal,
        )

        if not one:
            continue

        tm = one[0]
        tk = _tkey(tm)
        picked.append(tm)
        if tk:
            used_template_keys.add(tk)

        # Remove by key (not object identity) so duplicates can't slip through
        if tk:
            remaining = [m for m in remaining if _tkey(m) != tk]


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

    # Phase 4-D: scale each meal toward its slot calorie budget (scale ALL ingredients)
    if target_f is not None and budgets:
        for i, m in enumerate(out_meals):
            if i >= len(budgets):
                break

            meal_cals = float((m.get("macros") or {}).get("calories", 0.0))
            if meal_cals <= 0:
                continue

            s = float(budgets[i]) / meal_cals
            if s < 0.5:
                s = 0.5
            elif s > 3.0:
                s = 3.0

            if _scale_meal_ingredients(m, s):
                m["macros"] = _meal_macros_from_pantry(m["ingredients"])

    # Day-level closing still runs after scaling
    if target_f is not None:
        _macro_close_v1(out_meals, goal=goal, target_cals=float(target_f))
    else:
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
            "slots": slots,
            "slot_budgets": budgets if budgets else None,
            "diet_required": sorted(list(required)),
            "allergy_blocked": sorted(list(blocked)),
            "candidate_count": len(candidates),
        },
    }