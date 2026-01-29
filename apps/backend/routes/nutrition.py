from __future__ import annotations

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
    }


@router.post("/generate", response_model=NutritionGenerateResponse)
def nutrition_generate(req: NutritionGenerateRequest):
    targets: NutritionTargets = req.targets.model_dump()
    tc = _infer_target_calories(targets)

    meals_needed_final = int(req.meals_needed)
    if meals_needed_final <= 0:
        meals_needed_final = _infer_meals_needed_from_target_cals(tc)

    batch_size_final = int(req.batch_size)
    if batch_size_final <= 0:
        batch_size_final = meals_needed_final

    gen_req = GenerationRequest(
        diet=req.diet,
        allergies=req.allergies,
        meals_needed=meals_needed_final,
        max_attempts=req.max_attempts,
        batch_size=batch_size_final,
    )

    gen = generate_safe_meals(gen_req, _stub_llm_generate)
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
    tc = _infer_target_calories(targets)

    meals_needed_final = int(req.meals_needed)
    if meals_needed_final <= 0:
        meals_needed_final = _infer_meals_needed_from_target_cals(tc)

    batch_size_final = int(req.batch_size)
    if batch_size_final <= 0:
        batch_size_final = meals_needed_final

    gen_req = GenerationRequest(
        diet=req.diet,
        allergies=req.allergies,
        meals_needed=meals_needed_final,
        max_attempts=req.max_attempts,
        batch_size=batch_size_final,
    )

    attempt_offset = int(req.prev_snapshot.version)

    gen = generate_safe_meals(
        gen_req,
        lambda r, attempt: _stub_llm_generate(r, attempt + attempt_offset),
    )

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

