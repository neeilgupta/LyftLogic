import pytest

from services.nutrition.generate import GenerationRequest, generate_safe_meals


def test_generate_loop_accepts_only_safe_meals_and_stops_when_full():
    # LLM stub: attempt 1 returns unsafe meals (missing diet_tags),
    # attempt 2 returns safe meals.
    def llm_stub(req, attempt):
        if attempt == 1:
            return [
                {
                    "name": "Chicken rice bowl",
                    "ingredients": [
                        {"name": "chicken", "contains": ["chicken"], "is_compound": False},  # missing diet_tags => reject
                    ],
                }
            ]
        return [
            {
                "name": "Tofu bowl",
                "ingredients": [
                    {"name": "tofu", "contains": ["soy"], "diet_tags": ["vegan", "vegetarian"], "is_compound": False},
                    {"name": "rice", "contains": ["rice"], "diet_tags": ["vegan", "vegetarian"], "is_compound": False},
                ],
            },
            {
                "name": "Bean salad",
                "ingredients": [
                    {"name": "beans", "contains": ["beans"], "diet_tags": ["vegan", "vegetarian"], "is_compound": False},
                    {"name": "lettuce", "contains": ["lettuce"], "diet_tags": ["vegan", "vegetarian"], "is_compound": False},
                ],
            },
        ]

    req = GenerationRequest(
        diet="vegan",
        allergies=["milk", "chocolate"],
        meals_needed=2,
        max_attempts=5,
        batch_size=2,
    )

    res = generate_safe_meals(req, llm_stub)
    assert len(res.accepted) == 2
    assert res.attempts_used == 2
    assert len(res.rejected) >= 1


def test_generate_loop_respects_allergies_and_retries():
    def llm_stub(req, attempt):
        if attempt == 1:
            return [
                {
                    "name": "Protein shake",
                    "ingredients": [
                        {"name": "whey", "contains": ["whey"], "diet_tags": ["vegetarian"], "is_compound": False},
                    ],
                }
            ]
        return [
            {
                "name": "Vegan oats",
                "ingredients": [
                    {"name": "oats", "contains": ["oats"], "diet_tags": ["vegan", "vegetarian"], "is_compound": False},
                    {"name": "banana", "contains": ["banana"], "diet_tags": ["vegan", "vegetarian"], "is_compound": False},
                ],
            }
        ]

    req = GenerationRequest(
        diet="vegetarian",
        allergies=["milk"],  # whey should be rejected via allergy alias map
        meals_needed=1,
        max_attempts=3,
        batch_size=1,
    )

    res = generate_safe_meals(req, llm_stub)
    assert len(res.accepted) == 1
    assert res.accepted[0]["name"] == "Vegan oats"
    assert res.attempts_used == 2


def test_generate_loop_bails_out_when_attempts_exhausted():
    def llm_stub(req, attempt):
        # Always unsafe: compound meal
        return [
            {
                "name": "Mystery burrito",
                "ingredients": [
                    {"name": "burrito", "contains": ["beans", "rice"], "diet_tags": ["vegan"], "is_compound": True}
                ],
            }
        ]

    req = GenerationRequest(
        diet="vegan",
        allergies=[],
        meals_needed=1,
        max_attempts=2,
        batch_size=1,
    )

    res = generate_safe_meals(req, llm_stub)
    assert len(res.accepted) == 0
    assert len(res.rejected) >= 1
    assert res.attempts_used == 2
