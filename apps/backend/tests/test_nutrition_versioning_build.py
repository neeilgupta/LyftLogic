from services.nutrition.versioning import (
    _snapshot_meal_list,
    build_nutrition_version_v1,
)


def test_snapshot_meal_list_normalizes_and_preserves_order():
    meals = [
        {"name": "Chicken Rice"},
        {"key": "protein_bar", "name": "Protein Bar"},
        {"name": "Vegan Salad", "key": ""},
    ]

    snap = _snapshot_meal_list(meals)

    assert [m["name"] for m in snap] == ["Chicken Rice", "Protein Bar", "Vegan Salad"]
    assert snap[0]["key"] == "chicken_rice"
    assert snap[1]["key"] == "protein_bar"
    assert snap[2]["key"] == "vegan_salad"


def test_build_nutrition_version_v1_returns_snapshot_and_copies_constraints():
    targets = {
        "maintenance": 2600,
        "cut": {"0.5": 2350},
        "bulk": {"0.5": 2850},
    }
    accepted = [{"name": "A"}, {"name": "B"}]
    rejected = [{"name": "C"}]
    constraints = {"diet": "vegan"}

    v = build_nutrition_version_v1(
        version=5,
        targets=targets,
        accepted_meals=accepted,
        rejected_meals=rejected,
        constraints_snapshot=constraints,
    )

    assert v["version"] == 5
    assert v["targets"] is targets
    assert v["accepted_meals"][0]["key"] == "a"
    assert v["rejected_meals"][0]["key"] == "c"
    assert v["constraints_snapshot"] == constraints
    assert v["constraints_snapshot"] is not constraints
