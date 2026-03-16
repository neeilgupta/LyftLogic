from __future__ import annotations

from typing import List, Literal, Optional, Annotated, Dict, Any
from pydantic import BaseModel, Field, ConfigDict, field_validator

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
    focus_muscles: Optional[List[str]] = Field(default=None)

    @field_validator("equipment", mode="before")
    @classmethod
    def normalize_equipment(cls, v):
        if isinstance(v, str):
            raw = v.strip().lower()
            if raw in {"full gym", "full-gym", "fullgym"}:
                return "full_gym"
            if raw in {"body weight", "body-weight"}:
                return "bodyweight"
        return v


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
    warmup: list[str] = Field(default_factory=list)
    main: list[ExerciseItem]
    accessories: list[ExerciseItem] = Field(default_factory=list)
    estimated_minutes: int = 0


class GeneratePlanResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str
    summary: str
    weekly_split: list[DayPlan]
    progression_notes: list[str] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)
    estimated_minutes_total: int = 0
    estimated_minutes_note: str = ""

class EditPlanRequest(BaseModel):
    message: str


class PlanEditPatch(BaseModel):
    constraints_add: List[str] = Field(default_factory=list)
    constraints_remove: List[str] = Field(default_factory=list)
    preferences_add: List[str] = Field(default_factory=list)
    preferences_remove: List[str] = Field(default_factory=list)
    emphasis: Optional[str] = None
    avoid: List[str] = Field(default_factory=list)
    set_style: Optional[Literal["low", "standard", "high"]] = None
    rep_style: Optional[Literal["strength", "hypertrophy", "pump"]] = None


class EditPlanResponse(BaseModel):
    can_apply: bool = False
    proposed_patch: PlanEditPatch = Field(default_factory=PlanEditPatch)
    change_summary: List[str] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)

class RestorePlanRequest(BaseModel):
    version: Annotated[int, Field(ge=1)]


class PlanResponse(BaseModel):
    """Standardized response shape for all plan-related endpoints that return plan data."""
    plan_id: int
    version: int
    input: Any
    output: Any
    diff: Optional[Any] = None
    is_restored: bool = False
    restored_from: Optional[int] = None


def extract_restore_meta(diff: Any) -> tuple[bool, int | None]:
    """Extract is_restored and restored_from from a diff dict. Single source of truth."""
    if isinstance(diff, dict) and "restored_from" in diff:
        try:
            return True, int(diff["restored_from"])
        except Exception:
            pass
    return False, None
