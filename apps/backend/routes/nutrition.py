from __future__ import annotations

import re

from fastapi import APIRouter, HTTPException

from services.nutrition.generate import GenerationRequest, generate_safe_meals
from services.nutrition.regenerate import regenerate_nutrition_v1
from services.nutrition.versioning import (
    NutritionTargets,
    diff_nutrition,
    explain_nutrition_diff,
)
from services.nutrition.stub_meals import generate_stub_meals
from services.nutrition.macros import calculate_macro_calc_v4_metric

from models.nutrition import (
    NutritionGenerateRequest,
    NutritionGenerateResponse,
    NutritionRegenerateRequest,
    NutritionRegenerateResponse,
    MacroCalcRequest,
    MacroCalcResponse,
)
from services.nutrition.boosters import apply_calorie_fill_boosters




router = APIRouter(prefix="/nutrition", tags=["nutrition"])

def _infer_target_calories(targets: dict) -> float | None:
    m = targets.get("maintenance")
    if isinstance(m, (int, float)):
        return float(m)

    for k in ("bulk", "cut"):
        v = targets.get(k)
        if isinstance(v, dict):
            for vv in v.values():
                if isinstance(vv, (int, float)):
                    return float(vv)
    return None

def _infer_meals_needed_from_target_cals(tc: float | None) -> int:
    if tc is None:
        return 4
    if tc < 2300:
        return 4
    if tc <= 2800:
        return 5
    return 6

def _parse_calories(value) -> int:
    # Accept int/float directly
    if isinstance(value, (int, float)):
        return int(round(float(value)))

    # Accept strings like "632", "632.0", "632 kcal", "632kcal"
    if isinstance(value, str):
        s = value.strip().lower()
        m = re.search(r"(\d+(\.\d+)?)", s)
        if m:
            return int(round(float(m.group(1))))
    return 0


def _meal_calories(meal: dict) -> int:
    # 1) common: {"calories": 632}
    if "calories" in meal:
        return _parse_calories(meal.get("calories"))

    # 2) sometimes nested: {"macros": {"calories": 632}}
    macros = meal.get("macros")
    if isinstance(macros, dict) and "calories" in macros:
        return _parse_calories(macros.get("calories"))

    # 3) fallback: nothing found
    return 0


def _sum_plan_calories(meals: list[dict]) -> int:
    total = 0
    for m in meals:
        if not isinstance(m, dict):
            continue
        total += _meal_calories(m)
    return total



def _selected_target_from_req(
    req: NutritionGenerateRequest | NutritionRegenerateRequest,
    targets: dict,
) -> int | None:
    """
    Only enforce calorie-range checks when the client explicitly provides target_calories.
    Tests and older clients may only send targets (maintenance/cut/bulk table).
    """
    tc = getattr(req, "target_calories", None)
    if tc is None:
        return None
    try:
        return int(tc)
    except Exception:
        return None



def _fail_closed_calorie_guard(target: int | None, accepted: list[dict]) -> None:
    if target is None:
        return

    total = _sum_plan_calories(accepted)

    tol = 0.15
    lo = int(target * (1 - tol))
    hi = int(target * (1 + tol))

    if total < lo or total > hi:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Generated plan calories {total} out of range for target {target} "
                f"(allowed {lo}-{hi}). accepted_len={len(accepted)}"
            ),
        )


def _stub_llm_generate(req: GenerationRequest, attempt: int):
    stub = generate_stub_meals(req, attempt)
    meals = stub.get("meals", [])
    if not isinstance(meals, list):
        return []

    # 1) Deduplicate by original template key (the MEAL_LIBRARY key)
    unique: list[dict] = []
    seen: set[str] = set()

    for m in meals:
        if not isinstance(m, dict):
            continue
        tk = str(m.get("key") or "").strip().lower()
        if not tk:
            continue
        if tk in seen:
            continue
        seen.add(tk)
        unique.append(m)

    # 2) Do NOT cycle repeats here.
    #    If we have fewer uniques than batch_size, return fewer.
    #    generate_safe_meals() will make additional attempts if it needs more uniques.
    out: list[dict] = [dict(m) for m in unique[: int(req.batch_size)]]

    # 3) Preserve UI/test contract keys while keeping template identity
    for i, m in enumerate(out):
        m["template_key"] = m.get("key")  # original stable key
        m["key"] = f"meal_{i+1}_(attempt_{attempt})"

    return out

def _constraints_snapshot(req: NutritionGenerateRequest | NutritionRegenerateRequest) -> dict:
    return {
        "diet": req.diet,
        "allergies": list(req.allergies or []),
        "meals_needed": req.meals_needed,
        "max_attempts": req.max_attempts,
        "batch_size": req.batch_size,
        "target_calories": getattr(req, "target_calories", None),
    }


@router.post("/generate", response_model=NutritionGenerateResponse)
def nutrition_generate(req: NutritionGenerateRequest):
    targets: NutritionTargets = req.targets.model_dump()
    selected_target = _selected_target_from_req(req, targets)

    tc = float(selected_target) if selected_target is not None else _infer_target_calories(targets)

    meals_needed_final = int(req.meals_needed)
    if meals_needed_final <= 0:
        meals_needed_final = _infer_meals_needed_from_target_cals(tc)

    per_meal_cap = None
    if selected_target is not None and meals_needed_final > 0:
        per_meal_cap = int((selected_target / meals_needed_final) * 2.0)


    batch_size_final = int(req.batch_size)
    if batch_size_final <= 0:
        batch_size_final = meals_needed_final

    gen_req = GenerationRequest(
        diet=req.diet,
        allergies=req.allergies,
        meals_needed=meals_needed_final,
        max_attempts=req.max_attempts,
        batch_size=batch_size_final,
        target_calories=float(selected_target) if selected_target is not None else None,
        calorie_cap_per_meal=per_meal_cap,
    )

    gen = generate_safe_meals(gen_req, _stub_llm_generate)

    selected_target = _selected_target_from_req(req, targets)
    if selected_target is not None:
        apply_calorie_fill_boosters(
            meals=gen.accepted,
            target_calories=int(selected_target),
            diet=req.diet,
            allergies=req.allergies,
        )

    _fail_closed_calorie_guard(selected_target, gen.accepted)


    from services.nutrition.versioning import build_nutrition_version_v1

    snap = build_nutrition_version_v1(
        version=1,
        targets=targets,
        accepted_meals=gen.accepted,
        rejected_meals=gen.rejected,
        constraints_snapshot=_constraints_snapshot(req),
    )

    output = {
        "accepted": gen.accepted,
        "rejected": gen.rejected,
        "attempts_used": gen.attempts_used,
        "targets": targets,
    }

    return NutritionGenerateResponse(output=output, version_snapshot=snap)

@router.post("/regenerate", response_model=NutritionRegenerateResponse)
def nutrition_regenerate(req: NutritionRegenerateRequest):
    targets: NutritionTargets = req.targets.model_dump()
    selected_target = _selected_target_from_req(req, targets)
    tc = float(selected_target) if selected_target is not None else _infer_target_calories(targets)

    meals_needed_final = int(req.meals_needed)
    if meals_needed_final <= 0:
        meals_needed_final = _infer_meals_needed_from_target_cals(tc)

    

    per_meal_cap = None
    if selected_target is not None and meals_needed_final > 0:
        per_meal_cap = int((selected_target / meals_needed_final) * 2.0)

    batch_size_final = int(req.batch_size)
    if batch_size_final <= 0:
        batch_size_final = meals_needed_final

    gen_req = GenerationRequest(
        diet=req.diet,
        allergies=req.allergies,
        meals_needed=meals_needed_final,
        max_attempts=req.max_attempts,
        batch_size=batch_size_final,
        target_calories=float(selected_target) if selected_target is not None else None,
        calorie_cap_per_meal=per_meal_cap,
    )

    attempt_offset = int(req.prev_snapshot.version)

    gen = generate_safe_meals(
        gen_req,
        lambda r, attempt: _stub_llm_generate(r, attempt + attempt_offset),
    )

    selected_target = _selected_target_from_req(req, targets)
    if selected_target is not None:
        apply_calorie_fill_boosters(
            meals=gen.accepted,
            target_calories=int(selected_target),
            diet=req.diet,
            allergies=req.allergies,
        )

    _fail_closed_calorie_guard(selected_target, gen.accepted)



    output = {
        "accepted": gen.accepted,
        "rejected": gen.rejected,
        "attempts_used": gen.attempts_used,
        "targets": targets,
    }

    from services.nutrition.versioning import build_nutrition_version_v1

    snap = build_nutrition_version_v1(
        version=int(req.prev_snapshot.version) + 1,
        targets=targets,
        accepted_meals=gen.accepted,
        rejected_meals=gen.rejected,
        constraints_snapshot=_constraints_snapshot(req),
    )

    diff = diff_nutrition(req.prev_snapshot.model_dump(), snap)
    explanations = explain_nutrition_diff(diff)

    return NutritionRegenerateResponse(
        output=output,
        version_snapshot=snap,
        diff=diff,
        explanations=explanations,
    )
@router.post("/macro-calc", response_model=MacroCalcResponse)
def macro_calc(req: MacroCalcRequest):
    # Fail-closed validation (keep deterministic + explicit)
    if req.sex is None:
        raise HTTPException(status_code=422, detail="sex is required")
    if req.age is None:
        raise HTTPException(status_code=422, detail="age is required")
    if req.height_cm is None:
        raise HTTPException(status_code=422, detail="height_cm is required")
    if req.weight_kg is None:
        raise HTTPException(status_code=422, detail="weight_kg is required")
    if req.activity_level is None:
        raise HTTPException(status_code=422, detail="activity_level is required")

    try:
        payload = calculate_macro_calc_v4_metric(
            sex=req.sex.strip().lower(),  # type: ignore[arg-type]
            age=int(req.age),
            height_cm=float(req.height_cm),
            weight_kg=float(req.weight_kg),
            activity_level=str(req.activity_level),
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

        # Optional: if client provided goal/rate, include deterministic selection for convenience
    goal = (req.goal or "").strip().lower() if req.goal else None
    rate = str(req.rate) if getattr(req, "rate", None) is not None else None

    if goal in ("maintenance", "cut", "bulk"):
        payload["selected"] = {"goal": goal, "rate": rate}

        # Deterministic selected calories from computed targets
        if goal == "maintenance":
            payload["selected"]["calories"] = payload["targets"]["maintenance"]
            payload["selected"]["rate"] = None
        else:
            # default to "1" if missing (still deterministic)
            r = rate if rate in ("0.5", "1", "2") else "1"
            payload["selected"]["rate"] = r
            payload["selected"]["calories"] = payload["targets"][goal][r]

    return MacroCalcResponse(
        implemented=True,
        message="ok",
        macros=payload,
    )

