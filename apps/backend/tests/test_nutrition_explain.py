from services.nutrition.versioning import explain_nutrition_diff


def test_calories_ordering_and_exact_strings():
    diff = {
        "calories_changed": {
            "maintenance": {"from": 2600, "to": 2400},
            "cut": {
                "2": {"from": 3600, "to": 3700},
                "0.5": {"from": 2350, "to": 2300},
            },
            "bulk": {
                "1": {"from": 3100, "to": 3200}
            },
        }
    }

    lines = explain_nutrition_diff(diff)

    expected = [
        "Calories: maintenance changed from 2600 to 2400.",
        "Calories: cut 0.5 lb/week changed from 2350 to 2300.",
        "Calories: cut 2 lb/week changed from 3600 to 3700.",
        "Calories: bulk 1 lb/week changed from 3100 to 3200.",
    ]

    assert lines == expected


def test_meals_ordering_and_exact_strings():
    diff = {
        "meals_replaced": [
            {"index": 2, "from": {"name": "Old C"}, "to": {"name": "New C"}},
            {"index": 0, "from": {"name": "Old A"}, "to": {"name": "New A"}},
        ],
        "meals_removed": [
            {"index": 1, "meal": {"name": "B"}},
        ],
        "meals_added": [
            {"index": 3, "meal": {"name": "D"}},
        ],
    }

    lines = explain_nutrition_diff(diff)

    expected = [
        "Meal 1 replaced: Old A → New A.",
        "Meal 3 replaced: Old C → New C.",
        "Meal 2 removed: B.",
        "Meal 4 added: D.",
    ]

    assert lines == expected