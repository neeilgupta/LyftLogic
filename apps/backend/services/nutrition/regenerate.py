from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, Dict, List

from services.nutrition.generate import (
    GenerationRequest,
    GenerationResult,
    generate_safe_meals,
    LLMGenerator,
)
from services.nutrition.versioning import (
    build_nutrition_version_v1,
    diff_nutrition,
    explain_nutrition_diff,
    NutritionVersionV1,
    NutritionTargets,
)


@dataclass(frozen=True)
class NutritionRunV1:
    version: int
    targets: NutritionTargets
    generation: GenerationResult
    constraints_snapshot: Dict[str, object]


def finalize_nutrition_run_v1(run: NutritionRunV1) -> NutritionVersionV1:
    """Build a snapshot NutritionVersionV1 from a run object."""
    gen = run.generation
    return build_nutrition_version_v1(
        version=run.version,
        targets=run.targets,
        accepted_meals=gen.accepted,
        rejected_meals=gen.rejected,
        constraints_snapshot=run.constraints_snapshot,
    )


def regenerate_nutrition_v1(
    *,
    prev: NutritionVersionV1,
    version: int,
    targets: NutritionTargets,
    req: GenerationRequest,
    llm_generate: LLMGenerator,
    constraints_snapshot: Dict[str, object],
) -> Tuple[NutritionVersionV1, dict, List[str]]:
    """Run deterministic regeneration: generate meals, snapshot, diff, and explanations.

    Returns (curr_snapshot, diff, explanations)
    """
    gen: GenerationResult = generate_safe_meals(req, llm_generate)

    curr = build_nutrition_version_v1(
        version=version,
        targets=targets,
        accepted_meals=gen.accepted,
        rejected_meals=gen.rejected,
        constraints_snapshot=constraints_snapshot,
    )

    diff = diff_nutrition(prev, curr)
    explanations = explain_nutrition_diff(diff)

    return curr, diff, explanations
