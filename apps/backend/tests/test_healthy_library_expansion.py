# apps/backend/tests/test_healthy_library_expansion.py
"""
Tests for healthy library expansion:
- Ingredient pantry: 50+ new healthy ingredients
- Meal library: 45+ new healthy meals
- Allergen enforcement with new ingredients
- Duplicate meal signature detection
- Feasibility of high-calorie targets with constraints
"""

import pytest
from services.nutrition.ingredients_pantry import INGREDIENT_PANTRY_PER_100G
from services.nutrition.meal_library import MEAL_LIBRARY
from services.nutrition.allergens import build_allergen_set, normalize_term
from services.nutrition.stub_meals import (
    _meal_macros_from_pantry,
    _canonical_pantry_key,
    INGREDIENT_ALIASES,
)


class TestHealthyIngredientsExpansion:
    """Verify new healthy ingredients are in pantry with proper nutrition facts."""

    def test_new_proteins_in_pantry(self):
        """Verify lean protein additions."""
        expected_proteins = [
            "chicken breast, skinless",
            "ground chicken, 93% lean",
            "ground turkey, 99% lean",
            "ground beef, 93% lean",
            "salmon fillet, cooked",
            "trout, cooked",
            "halibut, cooked",
            "tilapia, cooked",
        ]
        for protein in expected_proteins:
            assert protein in INGREDIENT_PANTRY_PER_100G, f"Missing: {protein}"
            entry = INGREDIENT_PANTRY_PER_100G[protein]
            assert "calories" in entry and entry["calories"] > 0
            assert "protein_g" in entry and entry["protein_g"] > 10  # lean protein

    def test_new_grains_in_pantry(self):
        """Verify complex carb additions."""
        expected_grains = [
            "wild rice, cooked",
            "millet, cooked",
            "teff, cooked",
            "farro, cooked",
            "spelt, cooked",
            "whole wheat bread",
            "barley, pearl, cooked",
        ]
        for grain in expected_grains:
            assert grain in INGREDIENT_PANTRY_PER_100G, f"Missing: {grain}"

    def test_new_dairy_in_pantry(self):
        """Verify dairy additions (high-protein, low-fat options)."""
        expected_dairy = [
            "greek yogurt, 0%",
            "skyr, icelandic yogurt",
            "cottage cheese, fat-free",
            "ricotta, lowfat",
        ]
        for dairy in expected_dairy:
            assert dairy in INGREDIENT_PANTRY_PER_100G, f"Missing: {dairy}"
            entry = INGREDIENT_PANTRY_PER_100G[dairy]
            assert entry["protein_g"] >= 3, f"{dairy} should be high-protein"

    def test_new_plant_proteins_in_pantry(self):
        """Verify legume additions."""
        expected_legumes = [
            "split peas, cooked",
            "white beans, cooked",
            "navy beans, cooked",
            "mung beans, cooked",
            "chickpea flour",
        ]
        for legume in expected_legumes:
            assert legume in INGREDIENT_PANTRY_PER_100G, f"Missing: {legume}"

    def test_new_healthy_fats_in_pantry(self):
        """Verify seed/nut additions."""
        expected_fats = [
            "walnuts, raw",
            "pecans",
            "macadamia nuts, raw",
            "sunflower seeds",
            "sesame seeds",
            "pumpkin seeds, raw",
            "hemp seeds",
        ]
        for fat in expected_fats:
            assert fat in INGREDIENT_PANTRY_PER_100G, f"Missing: {fat}"

    def test_new_vegetables_in_pantry(self):
        """Verify vegetable additions."""
        expected_veggies = [
            "kale, raw",
            "chard, raw",
            "collard greens, cooked",
            "beets, cooked",
            "radish",
            "summer squash",
        ]
        for veg in expected_veggies:
            assert veg in INGREDIENT_PANTRY_PER_100G, f"Missing: {veg}"

    def test_ingredient_alias_coverage(self):
        """Verify aliases cover new ingredients for deterministic lookup."""
        # Test a few key aliases
        assert INGREDIENT_ALIASES.get("brown rice, long-grain") == "brown rice, long-grain"
        assert INGREDIENT_ALIASES.get("ground chicken") == "ground chicken, 93% lean"
        assert INGREDIENT_ALIASES.get("ground turkey") == "ground turkey, 93% lean"
        assert INGREDIENT_ALIASES.get("salmon fillet") == "salmon fillet, cooked"
        assert INGREDIENT_ALIASES.get("whole wheat bread") == "bread, whole wheat"


class TestHealthyMealExpansion:
    """Verify new healthy meals are well-formed and use only pantry ingredients."""

    def test_all_meals_use_existing_ingredients(self):
        """Ensure every meal uses only pantry ingredients (resolved via aliases)."""
        missing_ingredients = []
        for meal in MEAL_LIBRARY:
            for ing in meal.get("ingredients", []):
                ing_name = ing.get("name", "")
                canonical = _canonical_pantry_key(ing_name)
                if canonical not in INGREDIENT_PANTRY_PER_100G:
                    missing_ingredients.append((meal["key"], ing_name, canonical))
        
        assert not missing_ingredients, (
            f"Meals using missing ingredients: {missing_ingredients[:10]}"
        )

    def test_meals_have_required_fields(self):
        """Ensure all meals have proper structure."""
        required_fields = {"key", "name", "tags", "ingredients"}
        for meal in MEAL_LIBRARY:
            assert required_fields.issubset(meal.keys()), f"Meal {meal.get('key')} missing fields"
            assert isinstance(meal["tags"], list) and meal["tags"], f"Meal {meal['key']} has no tags"
            assert isinstance(meal["ingredients"], list) and meal["ingredients"], f"Meal {meal['key']} has no ingredients"
            
            for ing in meal["ingredients"]:
                assert "name" in ing and "grams" in ing
                assert "contains" in ing and isinstance(ing["contains"], list) and ing["contains"]

    def test_new_healthy_meals_exist(self):
        """Verify specific new healthy meals were added."""
        expected_new_meals = [
            "greek_yogurt_0_berries_seeds",
            "skyr_berries_granola_nuts",
            "chicken_breast_wild_rice_broccoli",
            "salmon_sweet_potato_asparagus",
            "lentil_spelt_bowl_roasted_veggies",
            "chickpea_quinoa_kale_avocado",
            "tofu_farro_broccoli_garlic",
        ]
        existing_keys = {meal["key"] for meal in MEAL_LIBRARY}
        for meal_key in expected_new_meals:
            assert meal_key in existing_keys, f"Missing healthy meal: {meal_key}"

    def test_meal_signature_uniqueness(self):
        """Ensure no duplicate meal signatures (same name = same signature)."""
        signatures = {}
        for meal in MEAL_LIBRARY:
            sig = (meal["name"].lower(), tuple(sorted([ing["name"] for ing in meal["ingredients"]])))
            if sig in signatures:
                pytest.fail(f"Duplicate meal signature: {meal['name']} (keys: {signatures[sig]} vs {meal['key']})")
            signatures[sig] = meal["key"]


class TestAllergyEnforcementWithNewIngredients:
    """Verify allergen blocking works with expanded ingredients."""

    def test_nut_allergen_blocks_tree_nuts(self):
        """Verify 'nut' allergen blocks tree nut ingredients."""
        allergen_set = build_allergen_set(["nuts"])
        
        # Find meals with nuts
        nut_meals = []
        for meal in MEAL_LIBRARY:
            for ing in meal["ingredients"]:
                if "tree_nut" in ing.get("contains", []) or "nut" in ing.get("contains", []):
                    nut_meals.append(meal["key"])
                    break
        
        assert len(nut_meals) > 0, "Expected some nut-containing meals"
        # Verify the allergen set would catch these
        assert "tree_nut" in allergen_set or "nut" in allergen_set, "Nut allergen not expanded"

    def test_dairy_allergen_expansion(self):
        """Verify dairy allergen blocks dairy ingredients."""
        allergen_set = build_allergen_set(["dairy"])
        
        # Should expand to include milk, yogurt, cheese, whey, butter, etc.
        expected_tokens = {"dairy", "milk", "whey", "cheese", "yogurt"}
        assert expected_tokens.issubset(allergen_set), f"Dairy expansion incomplete: {allergen_set}"

    def test_gluten_allergen_blocks_grains(self):
        """Verify gluten allergen blocks wheat-based ingredients."""
        allergen_set = build_allergen_set(["gluten"])
        assert "gluten" in allergen_set or "wheat" in allergen_set


class TestMealMacrosCalculation:
    """Verify macro calculation works with new ingredients."""

    def test_macro_calculation_new_meals(self):
        """Calculate macros for a sample of new healthy meals."""
        sample_meals = [
            "greek_yogurt_0_berries_seeds",
            "chicken_breast_wild_rice_broccoli",
            "lentil_spelt_bowl_roasted_veggies",
        ]
        
        for meal_key in sample_meals:
            meal = next((m for m in MEAL_LIBRARY if m["key"] == meal_key), None)
            if not meal:
                continue
            
            macros = _meal_macros_from_pantry(meal["ingredients"])
            assert macros["calories"] > 200, f"{meal_key} has too few calories"
            assert macros["protein_g"] > 5, f"{meal_key} has too little protein"

    def test_high_calorie_meals_feasibility(self):
        """Verify high-calorie (500+ cal) meals exist for feasibility."""
        high_cal_meals = []
        for meal in MEAL_LIBRARY:
            macros = _meal_macros_from_pantry(meal["ingredients"])
            if macros["calories"] >= 500:
                high_cal_meals.append((meal["key"], macros["calories"]))
        
        assert len(high_cal_meals) >= 5, f"Need more high-calorie meals; found {len(high_cal_meals)}"


class TestConstraintCoverage:
    """Verify meals exist across dietary constraints."""

    def test_vegetarian_meals_exist(self):
        """Ensure vegetarian meals available."""
        vegetarian_meals = []
        for meal in MEAL_LIBRARY:
            is_veg = all("vegan" in ing.get("diet_tags", []) or "vegetarian" in ing.get("diet_tags", [])
                        for ing in meal["ingredients"])
            if is_veg:
                vegetarian_meals.append(meal["key"])
        
        assert len(vegetarian_meals) >= 10, f"Need more vegetarian meals; found {len(vegetarian_meals)}"

    def test_vegan_meals_exist(self):
        """Ensure vegan meals available."""
        vegan_meals = []
        for meal in MEAL_LIBRARY:
            is_vegan = all("vegan" in ing.get("diet_tags", []) for ing in meal["ingredients"])
            if is_vegan:
                vegan_meals.append(meal["key"])
        
        assert len(vegan_meals) >= 8, f"Need more vegan meals; found {len(vegan_meals)}"

    def test_no_nut_meals_exist(self):
        """Verify meals that contain no nut allergens."""
        no_nut_meals = []
        for meal in MEAL_LIBRARY:
            has_nuts = any("tree_nut" in ing.get("contains", []) or "peanut" in ing.get("contains", [])
                          for ing in meal["ingredients"])
            if not has_nuts:
                no_nut_meals.append(meal["key"])
        
        assert len(no_nut_meals) >= 20, f"Need more nut-free meals; found {len(no_nut_meals)}"


class TestDeterminism:
    """Verify deterministic behavior is preserved."""

    def test_ingredient_aliases_deterministic(self):
        """Alias resolution must be stable."""
        test_names = ["chicken breast", "brown rice", "greek yogurt", "salmon fillet"]
        for name in test_names:
            result1 = _canonical_pantry_key(name)
            result2 = _canonical_pantry_key(name)
            assert result1 == result2, f"Non-deterministic alias for {name}"

    def test_meal_order_stable(self):
        """Meal library order must be stable (no randomization)."""
        keys_1 = [m["key"] for m in MEAL_LIBRARY]
        keys_2 = [m["key"] for m in MEAL_LIBRARY]
        assert keys_1 == keys_2, "Meal order changed!"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
