from __future__ import annotations

from typing import Literal, Optional, Annotated
from pydantic import BaseModel, Field, ConfigDict

class GeneratePlanRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    goal: Literal["strength", "hypertrophy", "fat_loss", "endurance"] = "hypertrophy"
    experience: Literal["beginner", "intermediate", "advanced"] = "intermediate"
    days_per_week: Annotated[int, Field(ge=1, le=6)] = 4
    session_minutes: Annotated[int, Field(ge=20, le=120)] = 60


    soreness_notes: str = Field(default="", description="Free-text soreness/recovery notes.")
    equipment: Literal["full_gym", "dumbbells", "bodyweight"] = "full_gym"
    constraints: Optional[str] = Field(default="", description="Any injuries, preferences, dislikes.")


class ExerciseItem(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str
    sets: Annotated[int, Field(ge=1, le=10)]
    reps: str = Field(description='e.g. "6-8" or "10-12"')
    rpe: Optional[Annotated[int, Field(ge=6, le=10)]] = None
    rest_seconds: Optional[Annotated[int, Field(ge=30, le=300)]] = None
    notes: str = ""


class DayPlan(BaseModel):
    model_config = ConfigDict(extra="forbid")
    day: str = Field(description='e.g. "Day 1"')
    focus: str = Field(description='e.g. "Upper (push emphasis)"')
    warmup: list[str] = []
    main: list[ExerciseItem]
    accessories: list[ExerciseItem] = []
    finisher: list[str] = []
    cooldown: list[str] = []


class GeneratePlanResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str
    summary: str
    weekly_split: list[DayPlan]
    progression_notes: list[str] = []
    safety_notes: list[str] = []
