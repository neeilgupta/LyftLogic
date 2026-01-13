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
# Snapshot helpers / builders
# -------------------------

def _snapshot_meal_list(meals: list[dict]) -> list[dict]:
    """Return a stable snapshot list of meals preserving order.

    Each output item is a dict containing exactly:
      - key: stable key (use normalize_meal_key(name) when missing/empty)
      - name: original meal name
    """
    out: list[dict] = []
    for m in meals or []:
        # tolerate non-dict inputs defensively
        if not isinstance(m, dict):
            name = str(m)
            key = normalize_meal_key(name)
        else:
            name = str(m.get("name", ""))
            key = (m.get("key") or "").strip()
            if not key:
                key = normalize_meal_key(name)
        out.append({"key": key, "name": name})
    return out


def build_nutrition_version_v1(
    *,
    version: int,
    targets: NutritionTargets,
    accepted_meals: list[dict],
    rejected_meals: list[dict],
    constraints_snapshot: Dict[str, object],
) -> NutritionVersionV1:
    """Construct a NutritionVersionV1 snapshot using stable meal lists.

    This function intentionally performs shallow copies of provided dicts where
    appropriate to avoid retaining external references for mutable objects.
    """
    return {
        "version": version,
        "targets": targets,
        "accepted_meals": _snapshot_meal_list(accepted_meals or []),
        "rejected_meals": _snapshot_meal_list(rejected_meals or []),
        "constraints_snapshot": dict(constraints_snapshot) if constraints_snapshot is not None else {},
    }


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


# -------------------------
# Explainers / formatting
# -------------------------

def _rate_label(rate_str: str) -> str:
    mapping = {"0.5": "0.5 lb/week", "1": "1 lb/week", "2": "2 lb/week"}
    return mapping.get(rate_str, f"{rate_str} lb/week")


def explain_nutrition_diff(diff: dict) -> list[str]:
    """Turn a nutrition diff into stable, human-readable one-line messages.

    Ordering: calories first, then meal replacements, then removals, then additions.
    """
    out: list[str] = []

    # Calories
    cal = diff.get("calories_changed") or {}
    if "maintenance" in cal:
        m = cal["maintenance"]
        out.append(f"Calories: maintenance changed from {m['from']} to {m['to']}.")

    for mode in ("cut", "bulk"):
        mode_block = cal.get(mode)
        if not mode_block:
            continue
        # sort rates numerically
        try:
            sorted_rates = sorted(mode_block.keys(), key=lambda s: float(s))
        except Exception:
            sorted_rates = sorted(mode_block.keys())
        for rate in sorted_rates:
            r = mode_block[rate]
            out.append(
                f"Calories: {mode} {_rate_label(rate)} changed from {r['from']} to {r['to']}."
            )

    # Meals: replacements
    for key in ("meals_replaced", "meals_removed", "meals_added"):
        items = diff.get(key) or []
        # sort by index ascending
        items_sorted = sorted(items, key=lambda x: int(x.get("index", 0)))
        if key == "meals_replaced":
            for item in items_sorted:
                idx = int(item.get("index", 0)) + 1
                frm = (item.get("from") or {}).get("name")
                to = (item.get("to") or {}).get("name")
                out.append(f"Meal {idx} replaced: {frm} → {to}.")
        elif key == "meals_removed":
            for item in items_sorted:
                idx = int(item.get("index", 0)) + 1
                name = (item.get("meal") or {}).get("name")
                out.append(f"Meal {idx} removed: {name}.")
        elif key == "meals_added":
            for item in items_sorted:
                idx = int(item.get("index", 0)) + 1
                name = (item.get("meal") or {}).get("name")
                out.append(f"Meal {idx} added: {name}.")

    return out

