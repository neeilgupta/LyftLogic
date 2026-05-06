"""
Scoring heuristics for the eval harness. Each function returns True (pass) or False (fail).
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models.plans import DayPlan, GeneratePlanRequest, GeneratePlanResponse
from routes.rules.engine import apply_rules_v1, _allowed_for_equipment, _estimate_day_minutes, _expand_focus_set
from routes.rules.exercise_catalog import EXERCISES


_BARBELL_KEYWORDS = (
    "barbell", "ez bar", "back squat", "front squat",
    "deadlift", "rdl", "t-bar row", "incline bench press", "hip thrust",
)

_DUMBBELL_SAFE_PREFIXES = ("dumbbell", "db ")


def _is_barbell_like(name: str) -> bool:
    n = name.lower()
    if any(n.startswith(p) for p in _DUMBBELL_SAFE_PREFIXES):
        return False
    return any(k in n for k in _BARBELL_KEYWORDS)


def session_time_within_budget(day: DayPlan, session_minutes: int) -> bool:
    estimated = _estimate_day_minutes(day)
    return estimated <= session_minutes * 1.10


def no_equipment_violations(day: DayPlan, equipment: str) -> bool:
    if equipment == "full_gym":
        return True
    all_exercises = day.main + day.accessories
    return all(_allowed_for_equipment(ex.name, equipment) for ex in all_exercises)


def no_duplicate_exercises(day: DayPlan) -> bool:
    names = [ex.name.lower() for ex in day.main + day.accessories]
    return len(names) == len(set(names))


def focus_muscles_prioritized(plan: GeneratePlanResponse, focus_muscles: list[str]) -> bool:
    if not focus_muscles:
        return True
    focus_set = _expand_focus_set(focus_muscles)
    for day in plan.weekly_split:
        combined = day.main + day.accessories
        top3 = combined[:3]
        for ex in top3:
            meta = EXERCISES.get(ex.name)
            if meta and any(t in focus_set for t in meta.tags):
                return True
    return False


def idempotent(plan: GeneratePlanResponse, req: GeneratePlanRequest) -> bool:
    run1 = apply_rules_v1(plan=plan, req=req)
    run2 = apply_rules_v1(plan=run1, req=req)
    return run1.model_dump_json() == run2.model_dump_json()
