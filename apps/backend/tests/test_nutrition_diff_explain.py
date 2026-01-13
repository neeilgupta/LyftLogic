from services.nutrition.versioning import explain_nutrition_diff


def test_explain_calories_and_rates_ordering():
    diff = {
        "calories_changed": {
            "maintenance": {"from": 2600, "to": 2400},
            "cut": {
                "1": {"from": 2100, "to": 2000},
                "0.5": {"from": 2350, "to": 2300},
            },
            "bulk": {
                "2": {"from": 3600, "to": 3700},
            },
        }
    }

    lines = explain_nutrition_diff(diff)

    assert lines[0] == "Calories: maintenance changed from 2600 to 2400."
    # cut rates should be sorted numerically (0.5 then 1)
    assert "Calories: cut 0.5 lb/week changed from 2350 to 2300." in lines
    assert "Calories: cut 1 lb/week changed from 2100 to 2000." in lines
    # bulk rate
    assert "Calories: bulk 2 lb/week changed from 3600 to 3700." in lines


def test_explain_meal_changes_order_and_format():
    diff = {
        "meals_replaced": [
            {"index": 2, "from": {"name": "Old C"}, "to": {"name": "New C"}},
            {"index": 0, "from": {"name": "Old A"}, "to": {"name": "New A"}},
        ],
        "meals_removed": [
            {"index": 3, "meal": {"name": "D"}},
        ],
        "meals_added": [
            {"index": 1, "meal": {"name": "B"}},
            {"index": 4, "meal": {"name": "E"}},
        ],
    }

    lines = explain_nutrition_diff(diff)

    # replacements come first and are sorted by index: index 0 then 2
    assert lines[0] == "Meal 1 replaced: Old A → New A."
    assert lines[1] == "Meal 3 replaced: Old C → New C."

    # removals next
    assert "Meal 4 removed: D." in lines

    # additions last and sorted by index
    assert "Meal 2 added: B." in lines
    assert "Meal 5 added: E." in lines


def test_combined_ordering():
    diff = {
        "calories_changed": {"maintenance": {"from": 2000, "to": 2100}},
        "meals_added": [{"index": 0, "meal": {"name": "M1"}}],
    }

    lines = explain_nutrition_diff(diff)

    assert lines[0].startswith("Calories:"), "Calories line must be first"
    assert lines[1] == "Meal 1 added: M1."