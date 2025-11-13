# apps/backend/routes/plans.py
"""
Workout Planning API Routes
- POST /plans/workout: single-session plan
- POST /plans/week:    full weekly plan
"""

from fastapi import APIRouter
from pydantic import BaseModel, conint
from typing import Dict, List, Optional, Literal

from services.nlp import parse_soreness
from services.planner import build_workout_plan, build_week_plan
from services.db import get_recent_sets_map  # <-- NEW
from services.llm import explain_workout


router = APIRouter()

# Type definitions for request validation
Focus = Literal["upper", "lower", "full"]
Equipment = Literal["gym", "dumbbells", "none"]

class SetLog(BaseModel):
    """One prior set (used for overload calc)."""
    reps: int
    weight_kg: Optional[float] = None
    rir: Optional[int] = None

class WorkoutRequest(BaseModel):
    """Generate a single workout."""
    focus: Focus
    equipment: Equipment = "gym"
    soreness_text: Optional[str] = ""
    last_log: Optional[Dict[str, List[SetLog]]] = None
    use_db_logs: bool = True  # <-- NEW (fallback to DB if last_log not given)

class WeekRequest(BaseModel):
    """Generate a weekly plan."""
    days_per_week: conint(ge=2, le=7)  # <-- add bounds
    equipment: Equipment = "gym"
    soreness_text: Optional[str] = ""
    last_log: Optional[Dict[str, List[SetLog]]] = None
    use_db_logs: bool = True  # <-- NEW

    class Config:
        json_schema_extra = {
            "example": {
                "days_per_week": 4,
                "equipment": "gym",
                "soreness_text": "quads 4",
                "last_log": None,
                "use_db_logs": True
            }
        }

def _db_last_log_if_needed(last_log: Optional[Dict[str, List[SetLog]]],
                           enable: bool) -> Dict[str, List[Dict]]:
    """
    If last_log is None and DB fallback is enabled, pull recent sets
    and convert them to the planner's expected structure.
    """
    if last_log is not None or not enable:
        return last_log or {}

    recent = get_recent_sets_map(days=14)  # { name: [ {reps, weight_kg, rir, ts} ] }
    # map to List[SetLog]-compatible dicts (weight_kg key name matches your model)
    mapped: Dict[str, List[Dict]] = {}
    for ex_name, sets in recent.items():
        mapped[ex_name] = [
            {"reps": s["reps"], "weight_kg": s["weight_kg"], "rir": s["rir"]}
            for s in sets
        ]
    return mapped

@router.post("/workout")
def workout(req: WorkoutRequest):
    """
    Generate a single workout plan based on:
    - equipment (substitutions)
    - soreness (lighten aggravated movements)
    - prior performance (progressive overload)
    """
    soreness = parse_soreness(req.soreness_text or "")
    last = _db_last_log_if_needed(req.last_log, req.use_db_logs)
    plan = build_workout_plan(req.focus, last, soreness, req.equipment)
    # Optionally guard this so tests don't require an API key:
    try:
        plan["explanation"] = explain_workout(plan)
    except Exception as e:
        print("Explain workout failed in /plans/workout:", e)
        plan["explanation"] = None

    return plan
@router.post("/week")
def week(req: WeekRequest):
    """
    Generate a complete weekly schedule (adaptive split).
    """
    soreness = parse_soreness(req.soreness_text or "")
    last = _db_last_log_if_needed(req.last_log, req.use_db_logs)
    return build_week_plan(req.days_per_week, last, soreness, req.equipment)
