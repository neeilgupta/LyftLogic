from services.nutrition.versioning import diff_nutrition


def make_version(
    *,
    maintenance=2600,
    cut=None,
    bulk=None,
    accepted_meals=None,
    rejected_meals=None,
    constraints=None,
):
    return {
        "version": 1,
        "targets": {
            "maintenance": maintenance,
            "cut": cut
            or {
                "0.5": 2350,
                "1": 2100,
                "2": 1600,
            },
            "bulk": bulk
            or {
                "0.5": 2850,
                "1": 3100,
                "2": 3600,
            },
        },
        "accepted_meals": accepted_meals or [],
        "rejected_meals": rejected_meals or [],
        "constraints_snapshot": constraints
        or {
            "diet": None,
            "allergies": [],
            "activity_level": "moderate",
        },
    }


def test_no_op_diff_is_empty():
    v1 = make_version(
        accepted_meals=[
            {"key": "protein_bar", "name": "Protein Bar"},
            {"key": "chicken_rice", "name": "Chicken Rice"},
        ]
    )
    v2 = make_version(
        accepted_meals=[
            {"key": "protein_bar", "name": "Protein Bar"},
            {"key": "chicken_rice", "name": "Chicken Rice"},
        ]
    )

    assert diff_nutrition(v1, v2) == {}


def test_maintenance_calorie_change_detected():
    prev = make_version(maintenance=2600)
    curr = make_version(maintenance=2400)

    diff = diff_nutrition(prev, curr)

    assert "calories_changed" in diff
    assert diff["calories_changed"]["maintenance"] == {
        "from": 2600,
        "to": 2400,
    }


def test_cut_rate_change_detected():
    prev = make_version(
        cut={
            "0.5": 2350,
            "1": 2100,
            "2": 1600,
        }
    )
    curr = make_version(
        cut={
            "0.5": 2350,
            "1": 2000,  # changed
            "2": 1600,
        }
    )

    diff = diff_nutrition(prev, curr)

    assert diff["calories_changed"]["cut"]["1"] == {
        "from": 2100,
        "to": 2000,
    }


def test_meal_replaced_at_same_index():
    prev = make_version(
        accepted_meals=[
            {"key": "protein_bar", "name": "Protein Bar"},
        ]
    )
    curr = make_version(
        accepted_meals=[
            {"key": "vegan_oats", "name": "Vegan Oats"},
        ]
    )

    diff = diff_nutrition(prev, curr)

    assert "meals_replaced" in diff
    assert diff["meals_replaced"][0]["index"] == 0
    assert diff["meals_replaced"][0]["from"]["name"] == "Protein Bar"
    assert diff["meals_replaced"][0]["to"]["name"] == "Vegan Oats"


def test_meal_added_detected():
    prev = make_version(
        accepted_meals=[
            {"key": "protein_bar", "name": "Protein Bar"},
        ]
    )
    curr = make_version(
        accepted_meals=[
            {"key": "protein_bar", "name": "Protein Bar"},
            {"key": "chicken_rice", "name": "Chicken Rice"},
        ]
    )

    diff = diff_nutrition(prev, curr)

    assert "meals_added" in diff
    assert diff["meals_added"][0]["index"] == 1
    assert diff["meals_added"][0]["meal"]["name"] == "Chicken Rice"


def test_order_matters_no_fuzzy_matching():
    prev = make_version(
        accepted_meals=[
            {"key": "meal_a", "name": "Meal A"},
            {"key": "meal_b", "name": "Meal B"},
        ]
    )
    curr = make_version(
        accepted_meals=[
            {"key": "meal_b", "name": "Meal B"},
            {"key": "meal_a", "name": "Meal A"},
        ]
    )

    diff = diff_nutrition(prev, curr)

    # swap should be TWO replacements, not zero
    assert "meals_replaced" in diff
    assert len(diff["meals_replaced"]) == 2
