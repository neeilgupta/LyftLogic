from services.nutrition.generate import GenerationRequest, generate_safe_meals


def test_accepts_unique_template_keys_only_even_within_same_attempt():
    # LLM stub returns the SAME safe meal twice in one batch.
    def llm_stub(req, attempt):
        return [
            {
                "template_key": "trail_mix_1",
                "name": "Trail Mix",
                "ingredients": [
                    {"name": "nuts", "contains": ["nuts"], "diet_tags": ["vegan"], "is_compound": False},
                ],
            },
            {
                "template_key": "trail_mix_1",
                "name": "Trail Mix",
                "ingredients": [
                    {"name": "nuts", "contains": ["nuts"], "diet_tags": ["vegan"], "is_compound": False},
                ],
            },
        ]

    req = GenerationRequest(
        diet="vegan",
        allergies=[],
        meals_needed=2,
        max_attempts=1,
        batch_size=2,
    )

    res = generate_safe_meals(req, llm_stub)

    # Should NOT accept duplicates. (So it won't reach meals_needed in 1 attempt.)
    assert len(res.accepted) == 1
    assert res.accepted[0]["template_key"] == "trail_mix_1"


def test_does_not_pad_repeats_when_uniques_less_than_batch_size():
    # Only 1 unique safe meal exists, batch_size asks for more, attempts exhausted.
    def llm_stub(req, attempt):
        return [
            {
                "template_key": "oats_1",
                "name": "Oats",
                "ingredients": [
                    {"name": "oats", "contains": ["oats"], "diet_tags": ["vegan"], "is_compound": False},
                    {"name": "banana", "contains": ["banana"], "diet_tags": ["vegan"], "is_compound": False},
                ],
            }
        ]

    req = GenerationRequest(
        diet="vegan",
        allergies=[],
        meals_needed=5,
        max_attempts=1,
        batch_size=5,
    )

    res = generate_safe_meals(req, llm_stub)

    # Unique list may be < batch_size (allowed). No repeats should be accepted.
    assert len(res.accepted) == 1
    assert res.accepted[0]["template_key"] == "oats_1"
