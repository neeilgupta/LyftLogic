from typing import Dict, List, Any, Optional


def _norm_name(name: Optional[str]) -> str:
    if not name:
        return ""
    return " ".join(str(name).strip().split()).lower()


def compute_plan_diff(
    prev_output: Dict[str, Any],
    new_output: Dict[str, Any],
    *,
    reason: Optional[str] = None,
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Deterministic diff between two plan outputs.

    Semantics rules:
    - Never emit same-name replacements (case/whitespace-insensitive).
    - Never emit empty from/to swaps.
    - Replacement is slot-aligned by (day_idx, block, slot).
    - 'reason' is an optional short hint (e.g., 'avoid_shoulders', 'prefer_cables').
    """
    diff: Dict[str, List[Dict[str, Any]]] = {
        "replaced_exercises": [],
        "removed_exercises": [],
        "added_exercises": [],
    }

    prev_days = prev_output.get("weekly_split", []) or []
    new_days = new_output.get("weekly_split", []) or []

    for day_idx, (prev_day, new_day) in enumerate(zip(prev_days, new_days)):
        day_label = (
            prev_day.get("day")
            or new_day.get("day")
            or f"Day {day_idx+1}"
        )

        for block in ("main", "accessories"):
            prev_ex = prev_day.get(block, []) or []
            new_ex = new_day.get(block, []) or []

            max_len = max(len(prev_ex), len(new_ex))

            for i in range(max_len):
                prev_name = prev_ex[i].get("name") if i < len(prev_ex) else None
                new_name = new_ex[i].get("name") if i < len(new_ex) else None

                prev_norm = _norm_name(prev_name)
                new_norm = _norm_name(new_name)

                # Meaningful replacement
                if prev_norm and new_norm:
                    if prev_norm == new_norm:
                        continue  # same-name replacement (ignore)
                    entry = {
                        "day": day_idx,
                        "day_label": day_label,
                        "block": block,
                        "slot": i,
                        "from": str(prev_name).strip(),
                        "to": str(new_name).strip(),
                    }
                    if reason:
                        entry["reason"] = reason
                    diff["replaced_exercises"].append(entry)
                    continue

                # Removal
                if prev_norm and not new_norm:
                    entry = {
                        "day": day_idx,
                        "day_label": day_label,
                        "block": block,
                        "slot": i,
                        "name": str(prev_name).strip(),
                    }
                    if reason:
                        entry["reason"] = reason
                    diff["removed_exercises"].append(entry)
                    continue

                # Addition
                if new_norm and not prev_norm:
                    entry = {
                        "day": day_idx,
                        "day_label": day_label,
                        "block": block,
                        "slot": i,
                        "name": str(new_name).strip(),
                    }
                    if reason:
                        entry["reason"] = reason
                    diff["added_exercises"].append(entry)
                    continue

    return diff
