from services.nutrition.regenerate import regenerate_nutrition_v1, finalize_nutrition_run_v1, NutritionRunV1
from services.nutrition.versioning import build_nutrition_version_v1
from services.nutrition.generate import GenerationRequest


def make_targets():
    return {
        "maintenance": 2600,
        "cut": {"0.5": 2350, "1": 2100, "2": 1600},
        "bulk": {"0.5": 2850, "1": 3100, "2": 3600},
    }


def _llm_gen_two_meals(req, attempt):
    # produce two simple valid meals according to contracts
    meal = lambda name: {
        "name": name,
        "ingredients": [
            {"name": "ing1", "contains": ["rice"], "diet_tags": ["omnivore"], "is_compound": False}
        ],
    }
    return [meal("Meal A"), meal("Meal B")]


def test_regenerate_creates_snapshot_and_diff():
    prev = build_nutrition_version_v1(
        version=1,
        targets=make_targets(),
        accepted_meals=[],
        rejected_meals=[],
        constraints_snapshot={"diet": None},
    )

    req = GenerationRequest(diet=None, allergies=[], meals_needed=2, max_attempts=1, batch_size=2)

    curr, diff, explanations = regenerate_nutrition_v1(
        prev=prev,
        version=2,
        targets=make_targets(),
        req=req,
        llm_generate=_llm_gen_two_meals,
        constraints_snapshot={"diet": None},
    )

    # Snapshot should have accepted meals
    assert len(curr["accepted_meals"]) == 2

    # Diff should show added meals at index 0 and 1
    assert "meals_added" in diff
    assert diff["meals_added"][0]["index"] == 0
    assert diff["meals_added"][1]["index"] == 1

    # Explanations should include Meal 1/2 added lines
    assert "Meal 1 added: Meal A." in explanations
    assert "Meal 2 added: Meal B." in explanations


def test_finalize_helper_builds_version():
    # Simulate a GenerationResult-like object
    from services.nutrition.generate import GenerationResult

    gen = GenerationResult(accepted=[{"name": "X"}], rejected=[{"name": "Y"}], attempts_used=1)
    run = NutritionRunV1(version=3, targets=make_targets(), generation=gen, constraints_snapshot={"diet": None})

    snap = finalize_nutrition_run_v1(run)
    assert snap["version"] == 3
    assert snap["accepted_meals"][0]["name"] == "X"
    assert snap["rejected_meals"][0]["name"] == "Y"
