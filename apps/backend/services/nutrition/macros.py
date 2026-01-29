from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Literal, Tuple


Sex = Literal["male", "female"]
Units = Literal["imperial", "metric"]

ActivityLevel = Literal["sedentary", "light", "moderate", "active", "very_active"]

Rate = Literal["0.5", "1", "2"]  # lb/week
Direction = Literal["cut", "bulk"]

_ACTIVITY_FACTORS: dict[ActivityLevel, float] = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}

# ---- Phase 4-A (Roadmap v4) macro-calc: metric + explicit multipliers ----

V4ActivityLevel = Literal["sedentary", "light", "moderate", "very", "athlete"]

_V4_ACTIVITY_FACTORS: dict[V4ActivityLevel, float] = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "very": 1.725,
    "athlete": 1.9,
}

def _round_nearest_10(x: float) -> int:
    return int(round(x / 10.0) * 10)

def _normalize_activity_level_v4(s: str) -> V4ActivityLevel:
    """
    Accepts strict Roadmap v4 labels + a few safe aliases without changing core planner logic.

    Supported canonical (Roadmap v4):
      sedentary, light, moderate, very, athlete

    Safe aliases accepted:
      very_active -> athlete
      active -> very
    """
    raw = (s or "").strip().lower()
    alias = {
        "very_active": "athlete",
        "active": "very",
    }.get(raw, raw)

    if alias not in _V4_ACTIVITY_FACTORS:
        raise ValueError(
            "invalid activity_level; expected one of: sedentary, light, moderate, very, athlete"
        )
    return alias  # type: ignore[return-value]


_RATE_DELTAS: dict[Rate, int] = {
    "0.5": 250,
    "1": 500,
    "2": 1000,
}


@dataclass(frozen=True)
class MacroResult:
    calories: int
    protein_g: int
    carbs_g: int
    fats_g: int


@dataclass(frozen=True)
class CalorieTargets:
    bmr: int
    maintenance: int
    # (direction, rate) -> calories
    targets: Dict[Tuple[Direction, Rate], int]


def _lb_to_kg(lb: float) -> float:
    return lb * 0.45359237


def _in_to_cm(inches: float) -> float:
    return inches * 2.54


def _round_int(x: float) -> int:
    return int(round(x))


def calculate_bmr_mifflin(
    *,
    weight: float,
    height: float,
    age: int,
    sex: Sex,
    units: Units = "imperial",
) -> int:
    """
    Mifflin-St Jeor BMR:
      Men:    10W + 6.25H - 5A + 5
      Women:  10W + 6.25H - 5A - 161
    Where W=kg, H=cm, A=years
    """
    if age <= 0:
        raise ValueError("age must be > 0")
    if weight <= 0:
        raise ValueError("weight must be > 0")
    if height <= 0:
        raise ValueError("height must be > 0")
    if sex not in ("male", "female"):
        raise ValueError("sex must be 'male' or 'female'")

    if units == "imperial":
        W = _lb_to_kg(weight)
        H = _in_to_cm(height)
    elif units == "metric":
        W = weight
        H = height
    else:
        raise ValueError("units must be 'imperial' or 'metric'")

    s = 5 if sex == "male" else -161
    bmr = 10.0 * W + 6.25 * H - 5.0 * age + s
    return _round_int(bmr)


def calculate_calorie_targets(
    *,
    weight_lb: float,
    height_in: float,
    age: int,
    sex: Sex,
    activity_level: ActivityLevel,
) -> CalorieTargets:
    """
    Returns maintenance calories plus cut/bulk targets for 0.5/1/2 lb per week.
    Uses:
      maintenance = round(BMR * activity_factor)
      cut targets: maintenance - {250,500,1000}
      bulk targets: maintenance + {250,500,1000}
    """
    if activity_level not in _ACTIVITY_FACTORS:
        raise ValueError("invalid activity_level")
    if weight_lb <= 0:
        raise ValueError("weight_lb must be > 0")
    if height_in <= 0:
        raise ValueError("height_in must be > 0")

    bmr = calculate_bmr_mifflin(
        weight=weight_lb,
        height=height_in,
        age=age,
        sex=sex,
        units="imperial",
    )

    maintenance = _round_int(bmr * _ACTIVITY_FACTORS[activity_level])

    targets: Dict[Tuple[Direction, Rate], int] = {}
    for rate, delta in _RATE_DELTAS.items():
        targets[("cut", rate)] = maintenance - delta
        targets[("bulk", rate)] = maintenance + delta

    return CalorieTargets(bmr=bmr, maintenance=maintenance, targets=targets)

def calculate_macro_calc_v4_metric(
    *,
    sex: Sex,
    age: int,
    height_cm: float,
    weight_kg: float,
    activity_level: str,
) -> dict:
    """
    Roadmap v4 Phase 4-A deterministic macro calculator (no persistence, no LLM).

    Formula:
      Mifflin–St Jeor BMR:
        Men:    10W + 6.25H - 5A + 5
        Women:  10W + 6.25H - 5A - 161
      TDEE = BMR * activity_multiplier

    Rounding:
      maintenance is rounded to nearest 10 kcal/day

    Suggested targets:
      uses existing _RATE_DELTAS mapping (0.5/1/2 lb per week -> 250/500/1000 kcal/day)
    """
    # Validation (fail-closed)
    if sex not in ("male", "female"):
        raise ValueError("sex must be 'male' or 'female'")
    if age is None or age <= 0:
        raise ValueError("age must be > 0")
    if height_cm is None or height_cm <= 0:
        raise ValueError("height_cm must be > 0")
    if weight_kg is None or weight_kg <= 0:
        raise ValueError("weight_kg must be > 0")

    lvl = _normalize_activity_level_v4(activity_level)
    mult = _V4_ACTIVITY_FACTORS[lvl]

    bmr = calculate_bmr_mifflin(
        weight=weight_kg,
        height=height_cm,
        age=age,
        sex=sex,
        units="metric",
    )

    tdee_raw = float(bmr) * float(mult)
    maintenance = _round_nearest_10(tdee_raw)

    cut: dict[str, int] = {}
    bulk: dict[str, int] = {}

    # Use existing deterministic delta mapping (do not change)
    for rate, delta in _RATE_DELTAS.items():
        cut[str(rate)] = maintenance - int(delta)
        bulk[str(rate)] = maintenance + int(delta)

    explanation_lines = [
        "Formula: Mifflin–St Jeor (metric)",
        f"Inputs: sex={sex}, age={age}, height_cm={height_cm}, weight_kg={weight_kg}, activity_level={lvl}",
        f"BMR: {bmr} kcal/day",
        f"Activity multiplier ({lvl}): {mult}",
        f"TDEE (raw): {tdee_raw:.2f} kcal/day",
        f"Maintenance (rounded to nearest 10): {maintenance} kcal/day",
        "Rate deltas (lb/week): 0.5→250, 1→500, 2→1000 kcal/day",
    ]

    return {
        "tdee": tdee_raw,
        "maintenance": maintenance,
        "targets": {
            "maintenance": maintenance,
            "cut": cut,
            "bulk": bulk,
        },
        "explanation": "\n".join(explanation_lines),
        "activity_multiplier": mult,
        "bmr": bmr,
    }



def macros_for_calories(*, weight_lb: float, calories: int) -> MacroResult:
    """
    Deterministic macro breakdown:
      protein = 1.0 g/lb
      fat = 0.3 g/lb
      carbs = remaining calories / 4
      fail-closed: if remaining < 0 => carbs = 0
      normalize calories to match macro totals exactly
    """
    if weight_lb <= 0:
        raise ValueError("weight_lb must be > 0")
    if calories <= 0:
        raise ValueError("calories must be > 0")

    protein_g = _round_int(1.0 * weight_lb)
    fats_g = _round_int(0.3 * weight_lb)

    remaining = calories - (4 * protein_g + 9 * fats_g)
    carbs_g = 0 if remaining <= 0 else _round_int(remaining / 4.0)

    final_calories = 4 * protein_g + 4 * carbs_g + 9 * fats_g

    return MacroResult(
        calories=final_calories,
        protein_g=protein_g,
        carbs_g=carbs_g,
        fats_g=fats_g,
    )
