# apps/backend/routes/plans.py
"""
Workout Planning API Routes

This module defines the API endpoints for generating workout plans.
It handles two main functionalities:
1. Creating single workout plans (/workout)
2. Generating weekly training schedules (/week)

Each endpoint validates requests using Pydantic models and returns
structured workout data considering equipment availability and soreness.
"""

from fastapi import APIRouter
from pydantic import BaseModel, conint
from typing import Dict, List, Optional, Literal

from services.nlp import parse_soreness
from services.planner import build_workout_plan, build_week_plan

router = APIRouter()

# Type definitions for request validation
Focus = Literal["upper","lower","full"]  # Available workout focuses
Equipment = Literal["gym","dumbbells","none"]  # Equipment availability options

class SetLog(BaseModel):
    """Model for logging individual exercise sets.
    
    Attributes:
        reps (int): Number of repetitions performed
        weight_kg (float, optional): Weight used in kilograms
        rir (int, optional): Reps In Reserve (0-5 scale)
                           Indicates how many more reps could have been done
    """
    reps: int
    weight_kg: Optional[float] = None
    rir: Optional[int] = None

class WorkoutRequest(BaseModel):
    """Request model for generating a single workout.
    
    Attributes:
        focus (Focus): Target area ("upper", "lower", or "full")
        equipment (Equipment): Available equipment (defaults to "gym")
        soreness_text (str, optional): Natural language description of muscle soreness
        last_log (Dict[str, List[SetLog]], optional): Previous workout data for progression
    
    Example:
        {
            "focus": "upper",
            "equipment": "dumbbells",
            "soreness_text": "triceps 3, chest 4",
            "last_log": {
                "DB Bench Press": [
                    {"reps": 8, "weight_kg": 20, "rir": 2}
                ]
            }
        }
    """
    focus: Focus
    equipment: Equipment = "gym"
    soreness_text: Optional[str] = ""
    last_log: Optional[Dict[str, List[SetLog]]] = None

class WeekRequest(BaseModel):
    """Request model for generating a weekly training plan.
    
    Attributes:
        days_per_week (int): Number of training days (2-6)
        equipment (Equipment): Available equipment (defaults to "gym")
        soreness_text (str, optional): Natural language description of muscle soreness
        last_log (Dict[str, List[SetLog]], optional): Previous workout data for progression
    """
    days_per_week: int
    equipment: Equipment = "gym"
    soreness_text: Optional[str] = ""
    last_log: Optional[Dict[str, List[SetLog]]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "days_per_week": 4,
                "equipment": "gym",
                "soreness_text": "quads 4",
                "last_log": None
            }
        }

@router.post("/workout")
def workout(req: WorkoutRequest):
    """Generate a single workout plan based on focus, equipment, and soreness.
    
    The workout will be adapted based on:
    - Available equipment (substituting exercises as needed)
    - Muscle soreness (reducing load for affected exercises)
    - Previous performance (progressive overload)
    
    Args:
        req (WorkoutRequest): Contains focus area, equipment availability,
                            soreness description, and previous workout data
    
    Returns:
        dict: Workout plan with exercises, sets, reps, and weight adjustments
    """
    soreness = parse_soreness(req.soreness_text or "")
    last = req.last_log or {}
    return build_workout_plan(req.focus, last, soreness, req.equipment)

@router.post("/week")
def week(req: WeekRequest):
    """Generate a complete weekly training schedule.
    
    Creates an optimal training split based on available training days:
    - 2 days: Upper/Lower
    - 3 days: Full body x3
    - 4 days: Upper/Lower/Upper/Lower
    - 5 days: Upper/Lower/Full/Upper/Lower
    - 6 days: Upper/Lower x3
    
    Args:
        req (WeekRequest): Contains number of training days, equipment availability,
                          soreness description, and previous workout data
    
    Returns:
        dict: Complete weekly plan with day-by-day workouts
    """
    soreness = parse_soreness(req.soreness_text or "")
    last = req.last_log or {}
    return build_week_plan(req.days_per_week, last, soreness, req.equipment)