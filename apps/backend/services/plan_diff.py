from typing import Dict, List, Any


def compute_plan_diff(prev_output: Dict[str, Any], new_output: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
    diff = {
        "replaced_exercises": [],
        "removed_exercises": [],
        "added_exercises": [],
    }

    prev_days = prev_output.get("weekly_split", [])
    new_days = new_output.get("weekly_split", [])

    for day_idx, (prev_day, new_day) in enumerate(zip(prev_days, new_days)):
        for block in ["main", "accessories"]:
            prev_ex = prev_day.get(block, [])
            new_ex = new_day.get(block, [])

            max_len = max(len(prev_ex), len(new_ex))

            for i in range(max_len):
                prev_name = prev_ex[i]["name"] if i < len(prev_ex) else None
                new_name = new_ex[i]["name"] if i < len(new_ex) else None

                if prev_name and new_name and prev_name != new_name:
                    diff["replaced_exercises"].append({
                        "day": day_idx,
                        "day_label": prev_day.get("day") or new_day.get("day") or f"Day {day_idx+1}",
                        "block": block,
                        "slot": i,
                        "from": prev_name,
                        "to": new_name,
                    })
                elif prev_name and not new_name:
                    diff["removed_exercises"].append({
                        "day": day_idx,
                        "day_label": prev_day.get("day") or new_day.get("day") or f"Day {day_idx+1}",
                        "block": block,
                        "slot": i,
                        "name": prev_name,
                    })
                elif new_name and not prev_name:
                    diff["added_exercises"].append({
                        "day": day_idx,
                        "day_label": prev_day.get("day") or new_day.get("day") or f"Day {day_idx+1}",
                        "block": block,
                        "slot": i,
                        "name": new_name,
                    })

    return diff
