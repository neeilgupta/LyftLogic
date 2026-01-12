from __future__ import annotations

from typing import TypedDict, Dict, List, Optional


# -------------------------
# Helpers
# -------------------------

def normalize_meal_key(name: str) -> str:
    return name.lower().strip().replace(" ", "_")


# -------------------------
# Snapshot schemas
# -------------------------

class RateTargets(TypedDict):
    # keys are stringified rates: "0.5", "1", "2"
    # values are calories
    ...


class NutritionTargets(TypedDict):
    maintenance: int
    cut: RateTargets
    bulk: RateTargets


class Meal(TypedDict):
    key: str
    name: str
    # optional future fields:
    # macros: dict
    # ingredients: list[str]


class NutritionVersionV1(TypedDict):
    version: int
    targets: NutritionTargets
    accepted_meals: List[Meal]        # ORDER MATTERS
    rejected_meals: List[Meal]        # optional but useful
    constraints_snapshot: Dict[str, object]


# -------------------------
# Diff engine
# -------------------------

def diff_nutrition(prev: NutritionVersionV1, curr: NutritionVersionV1) -> dict:
    diff: dict = {}

    # -------------------------
    # 1) Target diffs
    # -------------------------

    targets_diff: dict = {}

    # maintenance
    if prev["targets"]["maintenance"] != curr["targets"]["maintenance"]:
        targets_diff["maintenance"] = {
            "from": prev["targets"]["maintenance"],
            "to": curr["targets"]["maintenance"],
        }

    # cut / bulk by rate
    for mode in ("cut", "bulk"):
        rate_changes = {}
        prev_rates = prev["targets"][mode]
        curr_rates = curr["targets"][mode]

        for rate, prev_val in prev_rates.items():
            curr_val = curr_rates.get(rate)
            if curr_val is None:
                continue
            if prev_val != curr_val:
                rate_changes[rate] = {
                    "from": prev_val,
                    "to": curr_val,
                }

        if rate_changes:
            targets_diff[mode] = rate_changes

    if targets_diff:
        diff["calories_changed"] = targets_diff

    # -------------------------
    # 2) Meal diffs (index-based)
    # -------------------------

    prev_meals = prev["accepted_meals"]
    curr_meals = curr["accepted_meals"]

    meals_added = []
    meals_removed = []
    meals_replaced = []

    max_len = max(len(prev_meals), len(curr_meals))

    for idx in range(max_len):
        p = prev_meals[idx] if idx < len(prev_meals) else None
        c = curr_meals[idx] if idx < len(curr_meals) else None

        if p and not c:
            meals_removed.append({
                "index": idx,
                "meal": p,
            })
        elif not p and c:
            meals_added.append({
                "index": idx,
                "meal": c,
            })
        elif p and c:
            p_key = p.get("key") or normalize_meal_key(p["name"])
            c_key = c.get("key") or normalize_meal_key(c["name"])

            if p_key != c_key:
                meals_replaced.append({
                    "index": idx,
                    "from": p,
                    "to": c,
                })

    if meals_added:
        diff["meals_added"] = meals_added
    if meals_removed:
        diff["meals_removed"] = meals_removed
    if meals_replaced:
        diff["meals_replaced"] = meals_replaced

    return diff
