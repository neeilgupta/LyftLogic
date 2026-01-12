import pytest

from services.nutrition.macros import (
    calculate_calorie_targets,
    macros_for_calories,
)

def test_targets_include_maintenance_and_all_rates():
    t = calculate_calorie_targets(
        weight_lb=180,
        height_in=70,
        age=21,
        sex="male",
        activity_level="moderate",
    )
    assert isinstance(t.maintenance, int)
    assert t.maintenance > 0

    # exact deltas
    assert t.targets[("cut", "0.5")] == t.maintenance - 250
    assert t.targets[("cut", "1")] == t.maintenance - 500
    assert t.targets[("cut", "2")] == t.maintenance - 1000

    assert t.targets[("bulk", "0.5")] == t.maintenance + 250
    assert t.targets[("bulk", "1")] == t.maintenance + 500
    assert t.targets[("bulk", "2")] == t.maintenance + 1000


def test_macros_calorie_math_is_exact():
    res = macros_for_calories(weight_lb=180, calories=2500)
    assert 4 * res.protein_g + 4 * res.carbs_g + 9 * res.fats_g == res.calories
    assert res.protein_g == 180
    assert res.fats_g == round(0.3 * 180)


def test_macros_fail_closed_if_not_enough_calories_for_protein_and_fat():
    # tiny calories forces remaining negative -> carbs = 0
    res = macros_for_calories(weight_lb=200, calories=500)
    assert res.carbs_g == 0
    assert 4 * res.protein_g + 4 * res.carbs_g + 9 * res.fats_g == res.calories


def test_invalid_inputs_fail():
    with pytest.raises(ValueError):
        calculate_calorie_targets(
            weight_lb=0,
            height_in=70,
            age=21,
            sex="male",
            activity_level="moderate",
        )
    with pytest.raises(ValueError):
        macros_for_calories(weight_lb=180, calories=0)
