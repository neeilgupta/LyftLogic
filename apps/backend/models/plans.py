from __future__ import annotations

from typing import Literal, Optional, Annotated
from pydantic import BaseModel, Field, ConfigDict

class GeneratePlanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # v1 keeps this for UI, but internally only fat_loss changes structure
    goal: Literal["strength", "hypertrophy", "fat_loss", "endurance"] = "hypertrophy"
    experience: Literal["beginner", "intermediate", "advanced"] = "intermediate"
    days_per_week: Annotated[int, Field(ge=1, le=6)] = 4
    session_minutes: Annotated[int, Field(ge=20, le=120)] = 60

    equipment: Literal["full_gym", "dumbbells", "bodyweight"] = "full_gym"
    soreness_notes: Optional[str] = None
    constraints: Optional[str] = Field(default="", description="Any injuries, preferences, dislikes.")


class ExerciseItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str

    # Interpret 'sets' as WORKING sets only. Users always do 1 warm-up set separately.
    # Enforced by rules engine: 1–3.
    sets: Annotated[int, Field(ge=1, le=3)]

    # Only allowed: "6-8" or "8-12"
    reps: str = Field(description='Recommended rep range: "6-8" or "8-12"')

    # Enforced: compounds >= 240, isolations >= 180
    rest_seconds: Annotated[int, Field(ge=180, le=600)]

    # Keep notes for effort cue + optional alternatives, e.g. "Effort: close to failure final set. Alt: ..."
    notes: str = ""


class DayPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")

    day: str = Field(description='e.g. "Day 1"')
    focus: str = Field(description='e.g. "Upper (push emphasis)"')

    # Warmup must be simple bullets; no time/sets/reps, no cardio
    warmup: list[str] = []

    main: list[ExerciseItem]
    accessories: list[ExerciseItem] = []


class GeneratePlanResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str
    summary: str
    weekly_split: list[DayPlan]

    progression_notes: list[str] = []
    safety_notes: list[str] = []
