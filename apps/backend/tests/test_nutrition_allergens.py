import pytest

from services.nutrition.allergens import (
    build_allergen_set,
    enforce_allergies,
    meal_is_safe,
)

from services.nutrition.allergens import build_allergen_set, meal_is_safe

def test_potato_blocks_fries_mashed_chips():
    allergen_set = build_allergen_set(["potato"])

    fries = {
        "name": "Fries",
        "ingredients": [{"name": "fries", "contains": ["potatoes"], "is_compound": False}],
    }
    mashed = {
        "name": "Mashed potatoes",
        "ingredients": [{"name": "mashed potatoes", "contains": ["potato"], "is_compound": False}],
    }
    chips = {
        "name": "Potato chips",
        "ingredients": [{"name": "chips", "contains": ["potatoes"], "is_compound": False}],
    }

    assert meal_is_safe(fries, allergen_set) is False
    assert meal_is_safe(mashed, allergen_set) is False
    assert meal_is_safe(chips, allergen_set) is False


def test_chocolate_blocks_brownies_and_protein_bars():
    allergen_set = build_allergen_set(["chocolate"])

    brownies = {
        "name": "Brownies",
        "ingredients": [{"name": "brownie", "contains": ["chocolate"], "is_compound": False}],
    }
    bar = {
        "name": "Protein bar",
        "ingredients": [{"name": "protein bar", "contains": ["cocoa"], "is_compound": False}],
    }

    assert meal_is_safe(brownies, allergen_set) is False
    assert meal_is_safe(bar, allergen_set) is False


def test_milk_blocks_whey_cheese_butter():
    allergen_set = build_allergen_set(["milk"])

    whey = {
        "name": "Whey shake",
        "ingredients": [{"name": "whey", "contains": ["whey"], "is_compound": False}],
    }
    cheese = {
        "name": "Cheese snack",
        "ingredients": [{"name": "cheese", "contains": ["cheese"], "is_compound": False}],
    }
    butter = {
        "name": "Buttered toast",
        "ingredients": [{"name": "butter", "contains": ["butter"], "is_compound": False}],
    }

    assert meal_is_safe(whey, allergen_set) is False
    assert meal_is_safe(cheese, allergen_set) is False
    assert meal_is_safe(butter, allergen_set) is False


def test_missing_contains_rejected_fail_closed():
    allergen_set = build_allergen_set(["milk"])

    meal = {
        "name": "Mystery meal",
        "ingredients": [{"name": "mystery ingredient"}],  # missing contains
    }

    assert meal_is_safe(meal, allergen_set) is False

    safe, rejected = enforce_allergies([meal], allergen_set)
    assert safe == []
    assert rejected == [meal]


def test_compound_meal_rejected_fail_closed():
    allergen_set = build_allergen_set(["potato"])

    meal = {
        "name": "Chicken sandwich (not decomposed)",
        "ingredients": [
            {"name": "chicken sandwich", "contains": ["chicken", "bread"], "is_compound": True}
        ],
    }

    assert meal_is_safe(meal, allergen_set) is False


def test_safe_control_meal_passes():
    allergen_set = build_allergen_set(["potato", "chocolate", "milk"])

    meal = {
        "name": "Chicken rice bowl",
        "ingredients": [
            {
                "name": "chicken breast",
                "contains": ["chicken"],
                "diet_tags": ["omnivore"],   # or ["pescatarian"] etc
                "is_compound": False,
            },
            {
                "name": "white rice",
                "contains": ["rice"],
                "diet_tags": ["vegan", "vegetarian"],
                "is_compound": False,
            },
            {
                "name": "broccoli",
                "contains": ["broccoli"],
                "diet_tags": ["vegan", "vegetarian"],
                "is_compound": False,
            },
        ],
    }
    assert meal_is_safe(meal, allergen_set) is True


def test_missing_diet_tags_rejected_fail_closed():
    allergen_set = build_allergen_set([])
    meal = {
        "name": "Chicken rice bowl",
        "ingredients": [
            {"name": "chicken", "contains": ["chicken"], "is_compound": False},  # missing diet_tags
        ],
    }
    assert meal_is_safe(meal, allergen_set, required_diet_tags={"vegan"}) is False


def test_vegan_rejects_whey_eggs_butter():
    allergen_set = build_allergen_set([])

    whey_meal = {
        "name": "Whey shake",
        "ingredients": [
            {"name": "whey", "contains": ["whey"], "diet_tags": ["vegetarian"], "is_compound": False},
        ],
    }
    eggs_meal = {
        "name": "Eggs",
        "ingredients": [
            {"name": "eggs", "contains": ["eggs"], "diet_tags": ["vegetarian"], "is_compound": False},
        ],
    }
    butter_meal = {
        "name": "Butter toast",
        "ingredients": [
            {"name": "butter", "contains": ["butter"], "diet_tags": ["vegetarian"], "is_compound": False},
        ],
    }

    assert meal_is_safe(whey_meal, allergen_set, required_diet_tags={"vegan"}) is False
    assert meal_is_safe(eggs_meal, allergen_set, required_diet_tags={"vegan"}) is False
    assert meal_is_safe(butter_meal, allergen_set, required_diet_tags={"vegan"}) is False


def test_vegan_accepts_all_vegan_ingredients():
    allergen_set = build_allergen_set(["milk"])  # irrelevant here; nothing overlaps
    meal = {
        "name": "Tofu bowl",
        "ingredients": [
            {"name": "tofu", "contains": ["soy"], "diet_tags": ["vegan", "vegetarian"], "is_compound": False},
            {"name": "rice", "contains": ["rice"], "diet_tags": ["vegan", "vegetarian"], "is_compound": False},
        ],
    }
    assert meal_is_safe(meal, allergen_set, required_diet_tags={"vegan"}) is True


def test_vegetarian_allows_vegan_ingredients_but_rejects_meat():
    allergen_set = build_allergen_set([])

    vegan_meal = {
        "name": "Bean bowl",
        "ingredients": [
            {"name": "beans", "contains": ["beans"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    }
    meat_meal = {
        "name": "Chicken bowl",
        "ingredients": [
            {"name": "chicken", "contains": ["chicken"], "diet_tags": ["omnivore"], "is_compound": False},
        ],
    }

    assert meal_is_safe(vegan_meal, allergen_set, required_diet_tags={"vegetarian"}) is True
    assert meal_is_safe(meat_meal, allergen_set, required_diet_tags={"vegetarian"}) is False