from services.nutrition.allergens import build_allergen_set, meal_rejection_reason


def test_typo_and_unknown_allergen_terms_stay_in_block_set():
    allergens = build_allergen_set(["penut", "xyzunknownfood"])

    assert "penut" in allergens
    assert "xyzunknownfood" in allergens


def test_missing_ingredient_list_rejects():
    reason = meal_rejection_reason({"name": "Mystery Meal"}, set())

    assert reason is not None
    assert "missing_ingredients" in reason


def test_every_ingredient_is_checked_before_acceptance():
    meal = {
        "name": "Buried Allergen Bowl",
        "ingredients": [
            {"name": "rice", "contains": ["rice"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "peanut oil", "contains": ["peanut"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    }

    reason = meal_rejection_reason(meal, {"peanut"})

    assert reason is not None
    assert "allergy_conflict" in reason


def test_alias_expansion_catches_variants():
    allergens = build_allergen_set(["peanut", "milk"])

    assert "nuts" in allergens
    assert "dairy" in allergens
    assert "whey" in allergens


def test_diet_enforcement_requires_every_ingredient_to_have_required_tag():
    meal = {
        "name": "Almost Vegan",
        "ingredients": [
            {"name": "tofu", "contains": ["soy"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "honey", "contains": ["honey"], "diet_tags": ["vegetarian"], "is_compound": False},
        ],
    }

    reason = meal_rejection_reason(meal, set(), required_diet_tags={"vegan"})

    assert reason is not None
    assert "diet_conflict" in reason
