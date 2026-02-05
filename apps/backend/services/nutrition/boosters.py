from __future__ import annotations

from typing import Any


def _norm_set(xs) -> set[str]:
    if not xs:
        return set()
    out: set[str] = set()
    for x in xs:
        if x is None:
            continue
        s = str(x).strip().lower()
        if s:
            out.add(s)
    return out


def _diet_allowed_tags(diet: str | None) -> set[str]:
    """
    Diet tags allowed for boosters. Mirrors the idea that vegan meals satisfy vegetarian, etc.
    Keep conservative + deterministic.
    """
    d = (diet or "").strip().lower()
    if not d:
        # if no diet given, allow all booster tags
        return {"vegan", "vegetarian", "pescatarian", "omnivore"}
    if d == "vegan":
        return {"vegan"}
    if d == "vegetarian":
        return {"vegetarian", "vegan"}
    if d == "pescatarian":
        return {"pescatarian", "vegetarian", "vegan"}
    # fallback (keto, omnivore, etc.) – allow all boosters that are broadly safe
    return {"vegan", "vegetarian", "pescatarian", "omnivore"}


def _get_meal_calories(meal: dict) -> int:
    # 1) top-level calories
    if "calories" in meal and isinstance(meal.get("calories"), (int, float, str)):
        try:
            return int(round(float(str(meal.get("calories")).split()[0])))
        except Exception:
            pass

    # 2) nested macros calories
    macros = meal.get("macros")
    if isinstance(macros, dict) and "calories" in macros:
        try:
            return int(round(float(str(macros.get("calories")).split()[0])))
        except Exception:
            pass

    return 0


def _set_meal_calories(meal: dict, new_cals: int) -> None:
    """
    Preserve whichever calorie field the meal already uses; otherwise create top-level.
    """
    if "calories" in meal:
        meal["calories"] = int(new_cals)
        return

    macros = meal.get("macros")
    if isinstance(macros, dict):
        macros["calories"] = int(new_cals)
        meal["macros"] = macros
        return

    meal["calories"] = int(new_cals)


def _ensure_ingredients_list(meal: dict) -> list[dict[str, Any]]:
    ing = meal.get("ingredients")
    if isinstance(ing, list):
        # ensure list of dict-ish
        return ing  # type: ignore[return-value]
    ing2: list[dict[str, Any]] = []
    meal["ingredients"] = ing2
    return ing2

def _upsert_ingredient(
    ingredients: list[dict[str, Any]],
    *,
    name: str,
    grams_add: int,
    calories_add: int,
    type_value: str = "booster",
) -> None:
    """
    If an ingredient with the same name+type already exists, increment it.
    Otherwise append a new row.
    """
    name_l = name.strip().lower()
    for ing in ingredients:
        if not isinstance(ing, dict):
            continue
        iname = str(ing.get("name") or "").strip().lower()
        itype = str(ing.get("type") or "").strip().lower()
        if iname == name_l and itype == type_value:
            try:
                ing["grams"] = int(ing.get("grams") or 0) + int(grams_add)
            except Exception:
                ing["grams"] = int(grams_add)
            try:
                ing["calories"] = int(ing.get("calories") or 0) + int(calories_add)
            except Exception:
                ing["calories"] = int(calories_add)
            ing["type"] = type_value
            return

    ingredients.append(
        {"name": name, "grams": int(grams_add), "calories": int(calories_add), "type": type_value}
    )

def _meal_slot(meal: dict) -> str:
    """
    Best-effort slot detection.
    Prefer explicit keys; fallback to name inference.
    Returns: breakfast | lunch | dinner | snack | unknown
    """
    for k in ("slot", "meal_slot", "mealSlot", "meal_time", "mealTime", "type"):
        v = meal.get(k)
        if isinstance(v, str) and v.strip():
            s = v.strip().lower()
            # normalize common variants
            if "break" in s:
                return "breakfast"
            if "lunch" in s:
                return "lunch"
            if "dinner" in s or "supper" in s:
                return "dinner"
            if "snack" in s:
                return "snack"

    name = str(meal.get("name") or meal.get("title") or "").strip().lower()
    if any(x in name for x in ("overnight", "oats", "pancake", "toast", "breakfast", "yogurt")):
        return "breakfast"
    if any(x in name for x in ("salad", "sandwich", "wrap", "bowl")):
        return "lunch"
    if any(x in name for x in ("chicken", "steak", "salmon", "pasta", "stir", "dinner")):
        return "dinner"
    return "unknown"

def _text(meal: dict, key: str) -> str:
    v = meal.get(key)
    return str(v or "").strip().lower()


def _meal_name_text(meal: dict) -> str:
    return " ".join(
        [
            _text(meal, "name"),
            _text(meal, "title"),
            _text(meal, "template_key"),
            _text(meal, "templateKey"),
        ]
    ).strip()


def _existing_ingredient_names(meal: dict) -> set[str]:
    out: set[str] = set()
    ing = meal.get("ingredients")
    if not isinstance(ing, list):
        return out
    for row in ing:
        if not isinstance(row, dict):
            continue
        nm = str(row.get("name") or "").strip().lower()
        if nm:
            out.add(nm)
    return out


def _is_sweet_context(meal: dict) -> bool:
    """
    Conservative check: only treat as sweet/breakfast context if there are strong signals.
    """
    name = _meal_name_text(meal)
    sweet_name_tokens = (
        "oat",
        "overnight",
        "pancake",
        "yogurt",
        "smoothie",
        "toast",
        "granola",
        "cereal",
        "parfait",
    )
    if any(tok in name for tok in sweet_name_tokens):
        return True

    ing = _existing_ingredient_names(meal)
    sweet_ings = (
        "oats",
        "yogurt",
        "banana",
        "berries",
        "strawberry",
        "blueberry",
        "peanut butter",
        "pb",
        "honey",
        "maple syrup",
        "granola",
    )
    return any(s in ing for s in sweet_ings)





# Ordered boosters (priority order) — deterministic
# calories per gram are intentionally simple (we just need consistent + plausible fill)
BOOSTERS: list[dict[str, Any]] = [
    # Sweet-only boosters (must pass sweet-context gate)
    {
        "name": "maple syrup",
        "cal_per_g": 2.6,
        "diet_tags": {"vegan", "vegetarian", "pescatarian", "omnivore"},
        "allergens": set(),
        "step_g": 10,
        "max_g": 40,
        "allowed_slots": {"breakfast", "snack"},  # NOT unknown
        "category": "sweet",
    },
    {
        "name": "honey",
        "cal_per_g": 3.0,
        "diet_tags": {"vegetarian", "pescatarian", "omnivore"},  # not vegan
        "allergens": set(),
        "step_g": 10,
        "max_g": 40,
        "allowed_slots": {"breakfast", "snack"},  # NOT unknown
        "category": "sweet",
    },

    # Neutral breakfast-ish boosters
    {
        "name": "oats",
        "cal_per_g": 3.9,
        "diet_tags": {"vegan", "vegetarian", "pescatarian", "omnivore"},
        "allergens": {"gluten"},
        "step_g": 20,
        "max_g": 80,
        "allowed_slots": {"breakfast", "snack", "unknown"},
        "category": "neutral",
    },
    {
        "name": "banana",
        "cal_per_g": 0.9,
        "diet_tags": {"vegan", "vegetarian", "pescatarian", "omnivore"},
        "allergens": set(),
        "step_g": 50,
        "max_g": 150,
        "allowed_slots": {"breakfast", "snack", "unknown"},
        "category": "neutral",
    },

    # Savory boosters
    {
        "name": "rice",
        "cal_per_g": 1.3,
        "diet_tags": {"vegan", "vegetarian", "pescatarian", "omnivore"},
        "allergens": set(),
        "step_g": 25,
        "max_g": 100,
        "allowed_slots": {"lunch", "dinner", "unknown"},
        "category": "savory",
    },
    {
        "name": "olive oil",
        "cal_per_g": 8.0,
        "diet_tags": {"vegan", "vegetarian", "pescatarian", "omnivore"},
        "allergens": set(),
        "step_g": 5,
        "max_g": 20,
        "allowed_slots": {"lunch", "dinner", "unknown"},
        "category": "savory",
    },
]




def apply_calorie_fill_boosters(
    meals: list[dict],
    target_calories: int,
    diet: str | None,
    allergies: list[str] | None,
) -> list[dict]:
    """
    Deterministic post-pass: if total calories are under target, add safe boosters
    to existing meals until we reach target (or best effort).

    - No random selection
    - Fixed booster order
    - Fixed gram step increments
    - Mutates meals in place (and returns same list)
    """
    if target_calories <= 0:
        return meals

    allowed_diet = _diet_allowed_tags(diet)
    allergens = _norm_set(allergies)

    total = sum(_get_meal_calories(m) for m in meals if isinstance(m, dict))
    deficit = target_calories - total
    if deficit <= 0:
        return meals

    for booster in BOOSTERS:
        if not booster["diet_tags"].intersection(allowed_diet):
            continue
        if booster["allergens"].intersection(allergens):
            continue

        step_g: int = int(booster["step_g"])
        max_g: int = int(booster["max_g"])
        cal_per_g: float = float(booster["cal_per_g"])
        name: str = str(booster["name"])

        for meal in meals:
            if not isinstance(meal, dict):
                continue
            slot = _meal_slot(meal)
            allowed_slots = booster.get("allowed_slots") or {"unknown"}
            if slot not in allowed_slots:
                continue

            # Sweet boosters only if the meal already looks like a sweet/breakfast context
            category = str(booster.get("category") or "").strip().lower()
            if category == "sweet" and not _is_sweet_context(meal):
                continue

            cal_per_step = int(round(step_g * cal_per_g))
            if cal_per_step <= 0:
                continue

            # How many steps can we add without exceeding max_g or deficit?
            max_steps_by_g = (max_g // step_g)
            max_steps_by_deficit = (deficit // cal_per_step)
            # distribute per meal: at most half of max_g per meal on the first pass
            soft_cap_steps = max(1, (max_steps_by_g // 2))
            steps = int(min(soft_cap_steps, max_steps_by_deficit))

            if steps <= 0:
                continue

            grams_add = steps * step_g
            calories_add = steps * cal_per_step

            ingredients = _ensure_ingredients_list(meal)
            _upsert_ingredient(
                ingredients,
                name=name,
                grams_add=grams_add,
                calories_add=calories_add,
                type_value="booster",
            )

            new_cals = _get_meal_calories(meal) + calories_add
            _set_meal_calories(meal, new_cals)

            deficit -= calories_add
            if deficit <= 0:
                return meals

