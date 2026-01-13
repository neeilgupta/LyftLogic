from services.nutrition.regenerate import regenerate_nutrition_v1
from services.nutrition.versioning import build_nutrition_version_v1
from services.nutrition.generate import GenerationRequest


def make_targets():
    return {
        "maintenance": 2600,
        "cut": {"0.5": 2350, "1": 2100, "2": 1600},
        "bulk": {"0.5": 2850, "1": 3100, "2": 3600},
    }


def meal(name):
    return {
        "name": name,
        "ingredients": [
            {"name": "ing1", "contains": ["rice"], "diet_tags": ["omnivore"], "is_compound": False}
        ],
    }


def test_regenerate_detects_replacement():
    prev = build_nutrition_version_v1(
        version=1,
        targets=make_targets(),
        accepted_meals=[{"name": "A"}, {"name": "B"}],
        rejected_meals=[],
        constraints_snapshot={"diet": None},
    )

    # stub llm returns A, C so B -> C at index 1
    def stub_llm(req, attempt):
        return [meal("A"), meal("C")]

    req = GenerationRequest(diet=None, allergies=[], meals_needed=2, max_attempts=1, batch_size=2)

    curr, diff, explanations = regenerate_nutrition_v1(
        prev=prev,
        version=2,
        targets=make_targets(),
        req=req,
        llm_generate=stub_llm,
        constraints_snapshot={"diet": None},
    )

    assert curr["version"] == 2

    assert "meals_replaced" in diff
    # replacement at zero-based index 1
    rep = diff["meals_replaced"][0]
    assert rep["index"] == 1
    assert rep["from"]["name"] == "B"
    assert rep["to"]["name"] == "C"

    # exact explanation string
    assert "Meal 2 replaced: B → C." in explanations
