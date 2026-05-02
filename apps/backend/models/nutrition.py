from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

from services.nutrition.generate import normalize_supported_diet


class NutritionTargets(BaseModel):
    model_config = ConfigDict(extra="forbid")

    maintenance: int
    # keys are stringified rates: "0.5", "1", "2"
    cut: Dict[str, int]
    bulk: Dict[str, int]


class NutritionMealSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    key: str
    name: str


class NutritionVersionV1(BaseModel):
    model_config = ConfigDict(extra="forbid")

    version: int
    targets: NutritionTargets
    accepted_meals: List[NutritionMealSnapshot]
    rejected_meals: List[NutritionMealSnapshot]
    constraints_snapshot: Dict[str, Any] = Field(default_factory=dict)


class NutritionGenerateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    targets: NutritionTargets
    target_calories: Optional[int] = Field(default=None, ge=900, le=4500) 
    diet: Optional[str] = None
    allergies: List[str] = Field(default_factory=list)
    

    meals_needed: int = Field(ge=0, le=20)
    batch_size: int = Field(ge=0, le=20)
    max_attempts: int = Field(ge=1, le=50)

    @field_validator("diet", mode="before")
    @classmethod
    def validate_diet(cls, value: Optional[str]) -> Optional[str]:
        return normalize_supported_diet(value)


class NutritionGenerateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    output: Dict[str, Any]
    version_snapshot: NutritionVersionV1
    plan_id: int


class NutritionRegenerateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prev_snapshot: NutritionVersionV1

    targets: NutritionTargets
    target_calories: Optional[int] = Field(default=None, ge=900, le=4500)
    diet: Optional[str] = None
    allergies: List[str] = Field(default_factory=list)

    meals_needed: int = Field(ge=1, le=20)
    max_attempts: int = Field(ge=1, le=50)
    batch_size: int = Field(ge=1, le=20)

    @field_validator("diet", mode="before")
    @classmethod
    def validate_diet(cls, value: Optional[str]) -> Optional[str]:
        return normalize_supported_diet(value)


class NutritionRegenerateResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    output: Dict[str, Any]
    version_snapshot: NutritionVersionV1

    diff: Dict[str, Any]
    explanations: List[str]

class MacroCalcRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    sex: Optional[str] = None
    age: Optional[int] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    activity_level: Optional[str] = None
    goal: Optional[str] = None
    rate: Optional[str] = None  # "0.5" | "1" | "2"



class MacroCalcResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    implemented: bool
    message: str
    macros: Optional[Dict[str, Any]] = None
