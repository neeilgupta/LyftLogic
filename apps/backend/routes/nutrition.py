from __future__ import annotations

from fastapi import APIRouter

from services.nutrition.generate import GenerationRequest, generate_safe_meals
from services.nutrition.regenerate import regenerate_nutrition_v1
from services.nutrition.versioning import (
    NutritionTargets,
    diff_nutrition,
    explain_nutrition_diff,
)
from services.nutrition.stub_meals import generate_stub_meals

from models.nutrition import (
    NutritionGenerateRequest,
    NutritionGenerateResponse,
    NutritionRegenerateRequest,
    NutritionRegenerateResponse,
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



def _stub_llm_generate(req: GenerationRequest, attempt: int):
    stub = generate_stub_meals(req, attempt)
    meals = stub["meals"]

    # Preserve test contract: stable keys based on index + attempt
    for i, m in enumerate(meals):
        m["template_key"] = m.get("key")  # keep your real key for debugging
        m["key"] = f"meal_{i+1}_(attempt_{attempt})"

    return meals


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
    gen_req = GenerationRequest(
        diet=req.diet,
        allergies=req.allergies,
        meals_needed=req.meals_needed,
        max_attempts=req.max_attempts,
        batch_size=req.batch_size,
    )

    targets: NutritionTargets = req.targets.model_dump()
    object.__setattr__(gen_req, "targets", targets)


    tc = _infer_target_calories(targets)
    if tc is not None:
        object.__setattr__(gen_req, "target_calories", float(tc))

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
    gen_req = GenerationRequest(
        diet=req.diet,
        allergies=req.allergies,
        meals_needed=req.meals_needed,
        max_attempts=req.max_attempts,
        batch_size=req.batch_size,
    )

    targets: NutritionTargets = req.targets.model_dump()
    object.__setattr__(gen_req, "targets", targets)

    tc = _infer_target_calories(targets)
    if tc is not None:
        object.__setattr__(gen_req, "target_calories", float(tc))


    curr, diff, explanations = regenerate_nutrition_v1(
        prev=req.prev_snapshot.model_dump(),
        version=int(req.prev_snapshot.version) + 1,
        targets=targets,
        req=gen_req,
        llm_generate=_stub_llm_generate,
        constraints_snapshot=_constraints_snapshot(req),
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

