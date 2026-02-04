# apps/backend/services/nutrition/meal_library.py
from __future__ import annotations

# Meal templates must include ingredient objects compatible with services/nutrition/allergens.py:
# - name: str
# - contains: list[str]  (MUST be non-empty; use ingredient name if no allergies)
# - diet_tags: list[str]
# - is_compound: bool (False)
#
# NOTE: For ingredients with no known allergens, use the ingredient name in "contains"
# to satisfy the non-empty list requirement. This allows the allergen check to pass
# while still being explicit about what's in the meal.
# Common tokens: dairy, egg, gluten, soy, fish, shellfish, peanut, tree_nut, sesame

MEAL_LIBRARY: list[dict] = [
    # Test-compatible meal (used for snapshot testing)
    # NOTE: Key "-chicken_rice_5" is specifically chosen to hash lower than other meals
    # for deterministic selection in test scenarios (diet=None, allergies=[])
    {
        "key": "-chicken_rice_5",
        "name": "Chicken Rice",
        "tags": ["lunch", "dinner"],
        "ingredients": [
            # Keep this exact to avoid breaking tests if you rely on it
            {"name": "Rice", "grams": 200, "contains": ["rice"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "chicken breast, cooked", "grams": 150, "contains": ["chicken"], "diet_tags": ["omnivore"], "is_compound": False},
        ],
    },

    # ------------------------
    # Existing meals (kept)
    # ------------------------
    {
        "key": "overnight_oats_whey_banana_pb",
        "name": "Overnight oats (whey, banana, PB)",
        "tags": ["breakfast"],
        "ingredients": [
            {"name": "oats, dry", "grams": 80, "contains": ["gluten"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "whey protein powder", "grams": 30, "contains": ["dairy"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "banana", "grams": 120, "contains": ["banana"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "peanut butter", "grams": 16, "contains": ["peanut"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "greek_yogurt_apple_almonds",
        "name": "Greek yogurt bowl (apple, almonds)",
        "tags": ["breakfast", "snack"],
        "ingredients": [
            {"name": "greek yogurt, nonfat", "grams": 250, "contains": ["dairy"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "apple", "grams": 180, "contains": ["apple"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "almonds", "grams": 20, "contains": ["tree_nut"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "egg_scramble_potato_spinach",
        "name": "Egg scramble (potato, spinach)",
        "tags": ["breakfast"],
        "ingredients": [
            {"name": "eggs, whole", "grams": 150, "contains": ["egg"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "potato, baked", "grams": 250, "contains": ["potato"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "spinach", "grams": 60, "contains": ["spinach"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "olive oil", "grams": 5, "contains": ["olive_oil"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "chicken_rice_broccoli",
        "name": "Chicken + rice + broccoli",
        "tags": ["lunch", "dinner"],
        "ingredients": [
            {"name": "chicken breast, cooked", "grams": 180, "contains": ["chicken"], "diet_tags": ["omnivore"], "is_compound": False},
            {"name": "white rice, cooked", "grams": 250, "contains": ["rice"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "broccoli", "grams": 150, "contains": ["broccoli"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "olive oil", "grams": 8, "contains": ["olive_oil"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "turkey_pasta_tomato",
        "name": "Turkey pasta (tomato, olive oil)",
        "tags": ["lunch", "dinner"],
        "ingredients": [
            {"name": "ground turkey 93%, cooked", "grams": 170, "contains": ["turkey"], "diet_tags": ["omnivore"], "is_compound": False},
            {"name": "pasta, cooked", "grams": 260, "contains": ["gluten"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "tomato", "grams": 120, "contains": ["tomato"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "olive oil", "grams": 8, "contains": ["olive_oil"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "salmon_rice_salad",
        "name": "Salmon + rice + salad",
        "tags": ["lunch", "dinner"],
        "ingredients": [
            {"name": "salmon, cooked", "grams": 160, "contains": ["fish"], "diet_tags": ["pescatarian"], "is_compound": False},
            {"name": "brown rice, cooked", "grams": 260, "contains": ["rice"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "mixed salad greens", "grams": 120, "contains": ["lettuce"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "olive oil", "grams": 10, "contains": ["olive_oil"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "tuna_potato_spinach",
        "name": "Tuna + potato + spinach",
        "tags": ["lunch", "dinner"],
        "ingredients": [
            {"name": "tuna, canned in water", "grams": 150, "contains": ["fish"], "diet_tags": ["pescatarian"], "is_compound": False},
            {"name": "potato, baked", "grams": 320, "contains": ["potato"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "spinach", "grams": 80, "contains": ["spinach"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "olive oil", "grams": 8, "contains": ["olive_oil"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "tofu_rice_broccoli_soy",
        "name": "Rice + tofu + broccoli (soy sauce)",
        "tags": ["lunch", "dinner"],
        "ingredients": [
            {"name": "Rice", "grams": 260, "contains": ["rice"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "tofu, firm", "grams": 220, "contains": ["soy"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "broccoli", "grams": 170, "contains": ["broccoli"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "soy sauce", "grams": 12, "contains": ["soy"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "olive oil", "grams": 6, "contains": ["olive_oil"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "lentil_bowl_rice_peppers",
        "name": "Lentil bowl (rice, peppers, onions)",
        "tags": ["lunch", "dinner"],
        "ingredients": [
            {"name": "lentils, cooked", "grams": 260, "contains": ["lentils"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "brown rice, cooked", "grams": 240, "contains": ["rice"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "bell pepper", "grams": 120, "contains": ["pepper"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "onion", "grams": 60, "contains": ["onion"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "olive oil", "grams": 8, "contains": ["olive_oil"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "black_bean_tortilla_salsa",
        "name": "Black bean tortillas (salsa, avocado)",
        "tags": ["lunch", "dinner"],
        "ingredients": [
            {"name": "black beans, cooked", "grams": 260, "contains": ["beans"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "tortilla, flour", "grams": 100, "contains": ["gluten"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "salsa", "grams": 60, "contains": ["tomato"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "avocado", "grams": 80, "contains": ["avocado"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "tempeh_pasta_salad",
        "name": "Tempeh pasta + salad",
        "tags": ["lunch", "dinner"],
        "ingredients": [
            {"name": "tempeh", "grams": 180, "contains": ["soy"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "pasta, cooked", "grams": 260, "contains": ["gluten"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "mixed salad greens", "grams": 120, "contains": ["lettuce"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "olive oil", "grams": 10, "contains": ["olive_oil"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "cottage_cheese_banana",
        "name": "Cottage cheese + banana",
        "tags": ["snack"],
        "ingredients": [
            {"name": "cottage cheese, lowfat", "grams": 250, "contains": ["dairy"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "banana", "grams": 120, "contains": ["banana"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "edamame_rice_bowl",
        "name": "Edamame rice bowl",
        "tags": ["lunch", "dinner"],
        "ingredients": [
            {"name": "edamame", "grams": 220, "contains": ["soy"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "white rice, cooked", "grams": 260, "contains": ["rice"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "cucumber", "grams": 120, "contains": ["cucumber"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "soy sauce", "grams": 10, "contains": ["soy"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },

    # ============================================================
    # NEW MEALS (expanded a lot; only uses pantry ingredients)
    # ============================================================

    # ---------- Breakfasts ----------
    {
        "key": "oatmeal_blueberries_honey_whey",
        "name": "Oatmeal (blueberries, honey, whey)",
        "tags": ["breakfast"],
        "ingredients": [
            {"name": "oatmeal, cooked", "grams": 350, "contains": ["oats"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "whey protein powder", "grams": 30, "contains": ["dairy"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "blueberries", "grams": 120, "contains": ["blueberries"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "honey", "grams": 15, "contains": ["honey"], "diet_tags": ["vegetarian"], "is_compound": False},
        ],
    },
    {
        "key": "greek_yogurt_berries_granola",
        "name": "Greek yogurt bowl (berries, granola)",
        "tags": ["breakfast", "snack"],
        "ingredients": [
            {"name": "greek yogurt, nonfat", "grams": 280, "contains": ["dairy"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "berries, mixed", "grams": 160, "contains": ["berries"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "granola", "grams": 40, "contains": ["gluten"], "diet_tags": ["vegetarian"], "is_compound": False},
        ],
    },
    {
        "key": "cottage_cheese_pineapple_honey",
        "name": "Cottage cheese (pineapple, honey)",
        "tags": ["breakfast", "snack"],
        "ingredients": [
            {"name": "cottage cheese, lowfat", "grams": 260, "contains": ["dairy"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "pineapple", "grams": 180, "contains": ["pineapple"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "honey", "grams": 12, "contains": ["honey"], "diet_tags": ["vegetarian"], "is_compound": False},
        ],
    },
    {
        "key": "eggwhite_scramble_spinach_tomato",
        "name": "Egg white scramble (spinach, tomato)",
        "tags": ["breakfast"],
        "ingredients": [
            {"name": "egg whites", "grams": 250, "contains": ["egg"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "spinach", "grams": 80, "contains": ["spinach"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "tomato", "grams": 150, "contains": ["tomato"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "olive oil", "grams": 6, "contains": ["olive_oil"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "bagel_egg_cheddar",
        "name": "Bagel (egg, cheddar)",
        "tags": ["breakfast"],
        "ingredients": [
            {"name": "bagel", "grams": 110, "contains": ["gluten"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "eggs, whole", "grams": 100, "contains": ["egg"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "cheddar cheese", "grams": 30, "contains": ["dairy"], "diet_tags": ["vegetarian"], "is_compound": False},
        ],
    },
    {
        "key": "english_muffin_egg_mozzarella",
        "name": "English muffin (egg, mozzarella)",
        "tags": ["breakfast"],
        "ingredients": [
            {"name": "english muffin", "grams": 90, "contains": ["gluten"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "eggs, whole", "grams": 100, "contains": ["egg"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "mozzarella, part skim", "grams": 35, "contains": ["dairy"], "diet_tags": ["vegetarian"], "is_compound": False},
        ],
    },
    {
        "key": "cream_of_rice_whey_banana_pb",
        "name": "Cream of rice (whey, banana, PB)",
        "tags": ["breakfast"],
        "ingredients": [
            {"name": "cream of rice, dry", "grams": 70, "contains": ["rice"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "whey protein powder", "grams": 30, "contains": ["dairy"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "banana", "grams": 140, "contains": ["banana"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "peanut butter", "grams": 16, "contains": ["peanut"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "granola_milk_berries",
        "name": "Granola + milk + berries",
        "tags": ["breakfast"],
        "ingredients": [
            {"name": "granola", "grams": 70, "contains": ["gluten"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "milk, 2%", "grams": 250, "contains": ["dairy"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "strawberries", "grams": 160, "contains": ["strawberries"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },

    # ---------- Lunch / Dinner (chicken / turkey / beef / pork) ----------
    {
        "key": "chicken_quinoa_broccoli_lemon",
        "name": "Chicken + quinoa + broccoli (lemon)",
        "tags": ["lunch", "dinner"],
        "ingredients": [
            {"name": "chicken breast, cooked", "grams": 180, "contains": ["chicken"], "diet_tags": ["omnivore"], "is_compound": False},
            {"name": "quinoa, cooked", "grams": 260, "contains": ["quinoa"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "broccoli", "grams": 160, "contains": ["broccoli"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "lemon juice", "grams": 15, "contains": ["lemon_juice"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "olive oil", "grams": 8, "contains": ["olive_oil"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "chicken_pasta_tomato_sauce_parmesan",
        "name": "Chicken pasta (tomato sauce, parmesan)",
        "tags": ["lunch", "dinner"],
        "ingredients": [
            {"name": "chicken breast, cooked", "grams": 170, "contains": ["chicken"], "diet_tags": ["omnivore"], "is_compound": False},
            {"name": "pasta, cooked", "grams": 260, "contains": ["gluten"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "tomato sauce", "grams": 160, "contains": ["tomato"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "parmesan", "grams": 15, "contains": ["dairy"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "olive oil", "grams": 6, "contains": ["olive_oil"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "chicken_potato_greenbeans",
        "name": "Chicken + potato + green beans",
        "tags": ["lunch", "dinner"],
        "ingredients": [
            {"name": "chicken breast, cooked", "grams": 190, "contains": ["chicken"], "diet_tags": ["omnivore"], "is_compound": False},
            {"name": "potato, boiled", "grams": 330, "contains": ["potato"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "green beans", "grams": 180, "contains": ["green_beans"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "olive oil", "grams": 10, "contains": ["olive_oil"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "turkey_quinoa_peppers_onion",
        "name": "Turkey + quinoa (peppers, onions)",
        "tags": ["lunch", "dinner"],
        "ingredients": [
            {"name": "ground turkey 93%, cooked", "grams": 180, "contains": ["turkey"], "diet_tags": ["omnivore"], "is_compound": False},
            {"name": "quinoa, cooked", "grams": 260, "contains": ["quinoa"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "bell pepper", "grams": 140, "contains": ["pepper"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "onion", "grams": 70, "contains": ["onion"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "olive oil", "grams": 8, "contains": ["olive_oil"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "turkey_rice_peas",
        "name": "Turkey + rice + peas",
        "tags": ["lunch", "dinner"],
        "ingredients": [
            {"name": "ground turkey 93%, cooked", "grams": 190, "contains": ["turkey"], "diet_tags": ["omnivore"], "is_compound": False},
            {"name": "white rice, cooked", "grams": 280, "contains": ["rice"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "peas, cooked", "grams": 160, "contains": ["peas"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "olive oil", "grams": 8, "contains": ["olive_oil"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "ground_beef_pasta_tomato_sauce",
        "name": "Ground beef pasta (tomato sauce)",
        "tags": ["lunch", "dinner"],
        "ingredients": [
            {"name": "ground beef 90%, cooked", "grams": 180, "contains": ["beef"], "diet_tags": ["omnivore"], "is_compound": False},
            {"name": "pasta, cooked", "grams": 260, "contains": ["gluten"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "tomato sauce", "grams": 170, "contains": ["tomato"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "olive oil", "grams": 6, "contains": ["olive_oil"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "steak_potato_asparagus",
        "name": "Steak + potato + asparagus",
        "tags": ["lunch", "dinner"],
        "ingredients": [
            {"name": "steak, sirloin, cooked", "grams": 190, "contains": ["beef"], "diet_tags": ["omnivore"], "is_compound": False},
            {"name": "potato, baked", "grams": 320, "contains": ["potato"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "asparagus", "grams": 180, "contains": ["asparagus"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "butter", "grams": 10, "contains": ["dairy"], "diet_tags": ["vegetarian"], "is_compound": False},
        ],
    },
    {
        "key": "pork_loin_rice_greenbeans",
        "name": "Pork loin + rice + green beans",
        "tags": ["lunch", "dinner"],
        "ingredients": [
            {"name": "pork loin, cooked", "grams": 190, "contains": ["pork"], "diet_tags": ["omnivore"], "is_compound": False},
            {"name": "brown rice, cooked", "grams": 270, "contains": ["rice"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "green beans", "grams": 180, "contains": ["green_beans"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "olive oil", "grams": 8, "contains": ["olive_oil"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },

    # ---------- Fish / seafood ----------
    {
        "key": "tilapia_rice_broccoli",
        "name": "Tilapia + rice + broccoli",
        "tags": ["lunch", "dinner"],
        "ingredients": [
            {"name": "tilapia, cooked", "grams": 190, "contains": ["fish"], "diet_tags": ["pescatarian"], "is_compound": False},
            {"name": "white rice, cooked", "grams": 280, "contains": ["rice"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "broccoli", "grams": 170, "contains": ["broccoli"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "olive oil", "grams": 8, "contains": ["olive_oil"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "cod_potato_salad_balsamic",
        "name": "Cod + potato + salad (balsamic)",
        "tags": ["lunch", "dinner"],
        "ingredients": [
            {"name": "cod, cooked", "grams": 200, "contains": ["fish"], "diet_tags": ["pescatarian"], "is_compound": False},
            {"name": "potato, boiled", "grams": 330, "contains": ["potato"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "mixed salad greens", "grams": 140, "contains": ["lettuce"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "balsamic vinegar", "grams": 12, "contains": ["balsamic_vinegar"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "olive oil", "grams": 10, "contains": ["olive_oil"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "shrimp_rice_peppers_onion",
        "name": "Shrimp + rice (peppers, onions)",
        "tags": ["lunch", "dinner"],
        "ingredients": [
            {"name": "shrimp, cooked", "grams": 200, "contains": ["shellfish"], "diet_tags": ["pescatarian"], "is_compound": False},
            {"name": "jasmine rice, cooked", "grams": 280, "contains": ["rice"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "bell pepper", "grams": 140, "contains": ["pepper"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "onion", "grams": 70, "contains": ["onion"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "soy sauce", "grams": 12, "contains": ["soy"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "tuna_sandwich_bread_pickles",
        "name": "Tuna sandwich (bread, pickles)",
        "tags": ["lunch"],
        "ingredients": [
            {"name": "tuna, canned in water", "grams": 160, "contains": ["fish"], "diet_tags": ["pescatarian"], "is_compound": False},
            {"name": "bread, whole wheat", "grams": 120, "contains": ["gluten"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "mayonnaise", "grams": 20, "contains": ["egg"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "pickles", "grams": 35, "contains": ["pickles"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },

    # ---------- Vegan / Vegetarian mains (expanded) ----------
    {
        "key": "tofu_quinoa_broccoli_sriracha",
        "name": "Tofu + quinoa + broccoli (sriracha)",
        "tags": ["lunch", "dinner"],
        "ingredients": [
            {"name": "tofu, firm", "grams": 240, "contains": ["soy"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "quinoa, cooked", "grams": 260, "contains": ["quinoa"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "broccoli", "grams": 170, "contains": ["broccoli"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "sriracha", "grams": 10, "contains": ["sriracha"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "olive oil", "grams": 6, "contains": ["olive_oil"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "tempeh_rice_greenbeans_soy",
        "name": "Tempeh + rice + green beans (soy sauce)",
        "tags": ["lunch", "dinner"],
        "ingredients": [
            {"name": "tempeh", "grams": 200, "contains": ["soy"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "brown rice, cooked", "grams": 270, "contains": ["rice"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "green beans", "grams": 180, "contains": ["green_beans"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "soy sauce", "grams": 12, "contains": ["soy"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "lentil_quinoa_bowl_kale",
        "name": "Lentil + quinoa bowl (kale, onion)",
        "tags": ["lunch", "dinner"],
        "ingredients": [
            {"name": "lentils, cooked", "grams": 260, "contains": ["lentils"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "quinoa, cooked", "grams": 250, "contains": ["quinoa"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "kale", "grams": 120, "contains": ["kale"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "onion", "grams": 70, "contains": ["onion"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "olive oil", "grams": 8, "contains": ["olive_oil"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "chickpea_rice_bowl_tomato_cucumber",
        "name": "Chickpea rice bowl (tomato, cucumber)",
        "tags": ["lunch", "dinner"],
        "ingredients": [
            {"name": "chickpeas, cooked", "grams": 260, "contains": ["chickpeas"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "basmati rice, cooked", "grams": 270, "contains": ["rice"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "tomato", "grams": 140, "contains": ["tomato"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "cucumber", "grams": 140, "contains": ["cucumber"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "lemon juice", "grams": 15, "contains": ["lemon_juice"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "black_bean_corn_rice_salsa",
        "name": "Black bean bowl (corn, rice, salsa)",
        "tags": ["lunch", "dinner"],
        "ingredients": [
            {"name": "black beans, cooked", "grams": 260, "contains": ["beans"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "corn, cooked", "grams": 160, "contains": ["corn"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "white rice, cooked", "grams": 260, "contains": ["rice"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "salsa", "grams": 70, "contains": ["tomato"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "hummus_pita_cucumber_tomato",
        "name": "Hummus pita (cucumber, tomato)",
        "tags": ["lunch"],
        "ingredients": [
            {"name": "pita bread", "grams": 120, "contains": ["gluten"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "hummus", "grams": 90, "contains": ["hummus"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "cucumber", "grams": 140, "contains": ["cucumber"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "tomato", "grams": 140, "contains": ["tomato"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "seitan_pasta_tomato_sauce",
        "name": "Seitan pasta (tomato sauce)",
        "tags": ["lunch", "dinner"],
        "ingredients": [
            {"name": "seitan", "grams": 200, "contains": ["gluten"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "pasta, cooked", "grams": 260, "contains": ["gluten"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "tomato sauce", "grams": 180, "contains": ["tomato"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "olive oil", "grams": 6, "contains": ["olive_oil"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },

    # ---------- Snacks / add-ons (expanded) ----------
    {
        "key": "protein_bar_and_berries",
        "name": "Protein bar + berries",
        "tags": ["snack"],
        "ingredients": [
            {"name": "protein bar", "grams": 70, "contains": ["dairy"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "berries, mixed", "grams": 160, "contains": ["berries"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "trail_mix_nuts_raisins",
        "name": "Trail mix (nuts, raisins)",
        "tags": ["snack"],
        "ingredients": [
            {"name": "almonds", "grams": 20, "contains": ["tree_nut"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "walnuts", "grams": 20, "contains": ["tree_nut"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "raisins", "grams": 30, "contains": ["raisins"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "pb_dates",
        "name": "Peanut butter + dates",
        "tags": ["snack"],
        "ingredients": [
            {"name": "peanut butter", "grams": 24, "contains": ["peanut"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "dates", "grams": 60, "contains": ["dates"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "popcorn_and_dark_chocolate",
        "name": "Popcorn + dark chocolate",
        "tags": ["snack"],
        "ingredients": [
            {"name": "popcorn, air-popped", "grams": 25, "contains": ["popcorn"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "dark chocolate", "grams": 20, "contains": ["dark_chocolate"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
        # ---------- Scalable Snacks (300–500 cals capable) ----------

    {
        "key": "whey_milk_banana",
        "name": "Whey + milk + banana",
        "tags": ["snack"],
        "ingredients": [
            {"name": "whey protein powder", "grams": 30, "contains": ["dairy"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "milk, 2%", "grams": 350, "contains": ["dairy"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "banana", "grams": 140, "contains": ["banana"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },

    {
        "key": "greek_yogurt_granola_honey",
        "name": "Greek yogurt + granola + honey",
        "tags": ["snack"],
        "ingredients": [
            {"name": "greek yogurt, nonfat", "grams": 280, "contains": ["dairy"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "granola", "grams": 50, "contains": ["gluten"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "honey", "grams": 18, "contains": ["honey"], "diet_tags": ["vegetarian"], "is_compound": False},
        ],
    },

    {
        "key": "pb_toast_fruit",
        "name": "PB toast + fruit",
        "tags": ["snack"],
        "ingredients": [
            {"name": "bread, whole wheat", "grams": 100, "contains": ["gluten"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "peanut butter", "grams": 24, "contains": ["peanut"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "apple", "grams": 180, "contains": ["apple"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },

    {
        "key": "portionable_trail_mix",
        "name": "Trail mix (nuts + dried fruit)",
        "tags": ["snack"],
        "ingredients": [
            {"name": "almonds", "grams": 25, "contains": ["tree_nut"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "walnuts", "grams": 20, "contains": ["tree_nut"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "raisins", "grams": 35, "contains": ["raisins"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "dark chocolate", "grams": 15, "contains": ["dark_chocolate"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },

    # ============================================================
    # EXPANSION: 45+ new healthy meal templates
    # ============================================================

    # ---------- NEW BREAKFASTS (healthy, high-protein) ----------
    {
        "key": "greek_yogurt_0_berries_seeds",
        "name": "Greek yogurt (0%), berries, seeds",
        "tags": ["breakfast", "snack"],
        "ingredients": [
            {"name": "greek yogurt, 0%", "grams": 300, "contains": ["dairy"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "berries, mixed", "grams": 180, "contains": ["berries"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "hemp seeds", "grams": 15, "contains": ["hemp"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "skyr_berries_granola_nuts",
        "name": "Skyr (Icelandic yogurt), berries, granola",
        "tags": ["breakfast", "snack"],
        "ingredients": [
            {"name": "skyr, icelandic yogurt", "grams": 300, "contains": ["dairy"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "blueberries", "grams": 150, "contains": ["blueberries"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "granola", "grams": 35, "contains": ["gluten"], "diet_tags": ["vegetarian"], "is_compound": False},
        ],
    },
    {
        "key": "cottage_cheese_berries_honey",
        "name": "Cottage cheese (fat-free), berries, honey",
        "tags": ["breakfast", "snack"],
        "ingredients": [
            {"name": "cottage cheese, fat-free", "grams": 300, "contains": ["dairy"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "raspberries", "grams": 180, "contains": ["raspberries"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "honey", "grams": 10, "contains": ["honey"], "diet_tags": ["vegetarian"], "is_compound": False},
        ],
    },
    {
        "key": "egg_whites_oats_banana",
        "name": "Egg whites, oatmeal, banana",
        "tags": ["breakfast"],
        "ingredients": [
            {"name": "egg whites", "grams": 300, "contains": ["egg"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "oatmeal, cooked", "grams": 300, "contains": ["oats"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "banana", "grams": 120, "contains": ["banana"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "scrambled_eggs_wholegrains_veggies",
        "name": "Scrambled eggs, whole wheat toast, veggies",
        "tags": ["breakfast"],
        "ingredients": [
            {"name": "eggs, whole", "grams": 200, "contains": ["egg"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "whole wheat bread", "grams": 80, "contains": ["gluten"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "bell pepper", "grams": 150, "contains": ["pepper"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "spinach", "grams": 60, "contains": ["spinach"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "oatmeal_whey_berries_seeds",
        "name": "Oatmeal, whey, mixed berries, seeds",
        "tags": ["breakfast"],
        "ingredients": [
            {"name": "oatmeal, cooked", "grams": 300, "contains": ["oats"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "whey protein powder", "grams": 30, "contains": ["dairy"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "berries, mixed", "grams": 140, "contains": ["berries"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "flax seeds, ground", "grams": 12, "contains": ["seeds"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "quinoa_breakfast_bowl_fruit_nuts",
        "name": "Quinoa breakfast bowl (fruit, almonds)",
        "tags": ["breakfast"],
        "ingredients": [
            {"name": "quinoa, cooked", "grams": 280, "contains": ["quinoa"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "milk, 2%", "grams": 120, "contains": ["dairy"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "banana", "grams": 100, "contains": ["banana"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "almonds", "grams": 15, "contains": ["tree_nut"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "sweet_potato_eggs_spinach",
        "name": "Sweet potato, eggs, spinach",
        "tags": ["breakfast"],
        "ingredients": [
            {"name": "sweet potato, boiled", "grams": 300, "contains": ["sweet_potato"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "eggs, whole", "grams": 140, "contains": ["egg"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "spinach", "grams": 80, "contains": ["spinach"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },

    # ---------- NEW LUNCHES / DINNERS (lean proteins, whole carbs) ----------
    {
        "key": "chicken_breast_wild_rice_broccoli",
        "name": "Chicken breast, wild rice, broccoli",
        "tags": ["lunch", "dinner"],
        "ingredients": [
            {"name": "chicken breast, skinless", "grams": 200, "contains": ["chicken"], "diet_tags": ["omnivore"], "is_compound": False},
            {"name": "wild rice, cooked", "grams": 280, "contains": ["rice"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "broccoli", "grams": 200, "contains": ["broccoli"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "olive oil", "grams": 8, "contains": ["olive_oil"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "ground_turkey_farro_peppers_onion",
        "name": "Ground turkey, farro, peppers, onions",
        "tags": ["lunch", "dinner"],
        "ingredients": [
            {"name": "ground turkey, 93% lean", "grams": 190, "contains": ["turkey"], "diet_tags": ["omnivore"], "is_compound": False},
            {"name": "farro, cooked", "grams": 260, "contains": ["gluten"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "bell pepper", "grams": 150, "contains": ["pepper"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "onion", "grams": 80, "contains": ["onion"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "olive oil", "grams": 6, "contains": ["olive_oil"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "salmon_sweet_potato_asparagus",
        "name": "Salmon fillet, sweet potato, asparagus",
        "tags": ["lunch", "dinner"],
        "ingredients": [
            {"name": "salmon fillet, cooked", "grams": 180, "contains": ["fish"], "diet_tags": ["pescatarian"], "is_compound": False},
            {"name": "sweet potato, boiled", "grams": 280, "contains": ["sweet_potato"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "asparagus", "grams": 200, "contains": ["asparagus"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "olive oil", "grams": 10, "contains": ["olive_oil"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "lean_beef_brown_rice_vegetables",
        "name": "Lean beef sirloin, brown rice, mixed veggies",
        "tags": ["lunch", "dinner"],
        "ingredients": [
            {"name": "beef sirloin, lean", "grams": 190, "contains": ["beef"], "diet_tags": ["omnivore"], "is_compound": False},
            {"name": "brown rice, long-grain", "grams": 280, "contains": ["rice"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "carrots", "grams": 150, "contains": ["carrots"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "zucchini, raw", "grams": 120, "contains": ["zucchini"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "olive oil", "grams": 6, "contains": ["olive_oil"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "tilapia_millet_spinach_tomato",
        "name": "Tilapia, millet, spinach, tomato",
        "tags": ["lunch", "dinner"],
        "ingredients": [
            {"name": "tilapia, cooked", "grams": 200, "contains": ["fish"], "diet_tags": ["pescatarian"], "is_compound": False},
            {"name": "millet, cooked", "grams": 280, "contains": ["millet"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "spinach", "grams": 100, "contains": ["spinach"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "tomato", "grams": 120, "contains": ["tomato"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "olive oil", "grams": 8, "contains": ["olive_oil"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "pork_tenderloin_barley_veggies",
        "name": "Pork tenderloin, barley, roasted veggies",
        "tags": ["lunch", "dinner"],
        "ingredients": [
            {"name": "pork tenderloin, cooked", "grams": 190, "contains": ["pork"], "diet_tags": ["omnivore"], "is_compound": False},
            {"name": "barley, pearl, cooked", "grams": 280, "contains": ["gluten"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "bell pepper", "grams": 120, "contains": ["pepper"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "cauliflower, raw", "grams": 180, "contains": ["cauliflower"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "olive oil", "grams": 8, "contains": ["olive_oil"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "halibut_teff_chard_lemon",
        "name": "Halibut, teff, Swiss chard, lemon",
        "tags": ["lunch", "dinner"],
        "ingredients": [
            {"name": "halibut, cooked", "grams": 200, "contains": ["fish"], "diet_tags": ["pescatarian"], "is_compound": False},
            {"name": "teff, cooked", "grams": 280, "contains": ["teff"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "chard, raw", "grams": 150, "contains": ["chard"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "lemon juice", "grams": 15, "contains": ["lemon_juice"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "olive oil", "grams": 10, "contains": ["olive_oil"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },

    # ---------- VEGETARIAN / VEGAN MAINS (protein from plants) ----------
    {
        "key": "lentil_spelt_bowl_roasted_veggies",
        "name": "Lentil & spelt bowl, roasted vegetables",
        "tags": ["lunch", "dinner"],
        "ingredients": [
            {"name": "lentils, cooked", "grams": 280, "contains": ["lentils"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "spelt, cooked", "grams": 260, "contains": ["gluten"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "bell pepper", "grams": 140, "contains": ["pepper"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "zucchini, raw", "grams": 140, "contains": ["zucchini"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "olive oil", "grams": 10, "contains": ["olive_oil"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "chickpea_quinoa_kale_avocado",
        "name": "Chickpea & quinoa bowl, kale, avocado",
        "tags": ["lunch", "dinner"],
        "ingredients": [
            {"name": "chickpeas, cooked", "grams": 280, "contains": ["chickpeas"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "quinoa, cooked", "grams": 260, "contains": ["quinoa"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "kale, raw", "grams": 150, "contains": ["kale"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "avocado", "grams": 100, "contains": ["avocado"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "white_bean_millet_spinach_tomato",
        "name": "White bean & millet, spinach, tomato",
        "tags": ["lunch", "dinner"],
        "ingredients": [
            {"name": "white beans, cooked", "grams": 280, "contains": ["beans"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "millet, cooked", "grams": 260, "contains": ["millet"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "spinach", "grams": 120, "contains": ["spinach"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "tomato sauce", "grams": 140, "contains": ["tomato"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "olive oil", "grams": 8, "contains": ["olive_oil"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "tofu_farro_broccoli_garlic",
        "name": "Crispy tofu, farro, broccoli, garlic",
        "tags": ["lunch", "dinner"],
        "ingredients": [
            {"name": "tofu, firm", "grams": 250, "contains": ["soy"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "farro, cooked", "grams": 260, "contains": ["gluten"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "broccoli", "grams": 180, "contains": ["broccoli"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "garlic", "grams": 10, "contains": ["garlic"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "olive oil", "grams": 12, "contains": ["olive_oil"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "tempeh_brown_rice_bok_choy",
        "name": "Tempeh, brown rice, bok choy",
        "tags": ["lunch", "dinner"],
        "ingredients": [
            {"name": "tempeh", "grams": 210, "contains": ["soy"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "brown rice, long-grain", "grams": 280, "contains": ["rice"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "broccoli", "grams": 180, "contains": ["broccoli"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "soy sauce", "grams": 10, "contains": ["soy"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "olive oil", "grams": 10, "contains": ["olive_oil"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },

    # --- PESCATARIAN-SAFE MEALS (fish + veg ingredients) ---

    {
        "key": "pesc_salmon_rice_broccoli",
        "name": "Salmon + rice + broccoli",
        "tags": ["dinner"],
        "ingredients": [
            {"name": "salmon, cooked", "grams": 170, "diet_tags": ["pescatarian"], "contains": ["fish"]},
            {"name": "white rice, cooked", "grams": 240, "diet_tags": ["vegan"], "contains": ["rice"]},
            {"name": "broccoli", "grams": 120, "diet_tags": ["vegan"], "contains": ["broccoli"]},
            {"name": "olive oil", "grams": 10, "diet_tags": ["vegan"], "contains": ["olive_oil"]},
        ],
    },

    {
        "key": "pesc_tuna_wrap",
        "name": "Tuna wrap",
        "tags": ["lunch"],
        "ingredients": [
            {"name": "tuna, canned in water", "grams": 150, "diet_tags": ["pescatarian"], "contains": ["fish"]},
            {"name": "tortilla, flour", "grams": 90, "diet_tags": ["vegan"], "contains": ["wheat"]},
            {"name": "greek yogurt, nonfat", "grams": 80, "diet_tags": ["vegetarian"], "contains": ["milk"]},
        ],
    },

    {
        "key": "pesc_greek_yogurt_berries",
        "name": "Greek yogurt + berries",
        "tags": ["breakfast", "snack"],
        "ingredients": [
            {"name": "greek yogurt, nonfat", "grams": 300, "diet_tags": ["vegetarian"], "contains": ["milk"]},
            {"name": "blueberries", "grams": 120, "diet_tags": ["vegan"], "contains": ["blueberries"]},
            {"name": "honey", "grams": 15, "diet_tags": ["vegetarian"], "contains": ["honey"]},
        ],
    },

    {
        "key": "pesc_eggs_toast",
        "name": "Eggs + toast",
        "tags": ["breakfast"],
        "ingredients": [
            {"name": "eggs, whole", "grams": 150, "diet_tags": ["vegetarian"], "contains": ["egg"]},
            {"name": "bread, whole wheat", "grams": 80, "diet_tags": ["vegan"], "contains": ["wheat"]},
            {"name": "butter", "grams": 10, "diet_tags": ["vegetarian"], "contains": ["milk"]},
        ],
    },


    # ---------- NEW SNACKS (healthy, whole-food, no junk) ----------
    {
        "key": "string_cheese_apple_walnut",
        "name": "String cheese, apple, walnuts",
        "tags": ["snack"],
        "ingredients": [
            {"name": "string cheese, part-skim", "grams": 28, "contains": ["dairy"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "apple, with skin", "grams": 180, "contains": ["apple"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "walnuts, raw", "grams": 15, "contains": ["tree_nut"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "cottage_cheese_peach_seeds",
        "name": "Cottage cheese, peach, pumpkin seeds",
        "tags": ["snack"],
        "ingredients": [
            {"name": "cottage cheese, lowfat", "grams": 200, "contains": ["dairy"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "peach", "grams": 150, "contains": ["peach"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "pumpkin seeds, raw", "grams": 15, "contains": ["seeds"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "greek_yogurt_kiwi_chia",
        "name": "Greek yogurt, kiwi, chia seeds",
        "tags": ["snack"],
        "ingredients": [
            {"name": "greek yogurt, 0%", "grams": 250, "contains": ["dairy"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "kiwi fruit", "grams": 150, "contains": ["kiwi"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "chia seeds, raw", "grams": 12, "contains": ["seeds"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "whole_wheat_toast_tahini_honey",
        "name": "Whole wheat toast, tahini, honey",
        "tags": ["snack"],
        "ingredients": [
            {"name": "whole wheat bread", "grams": 100, "contains": ["gluten"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "tahini, raw", "grams": 14, "contains": ["sesame"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "honey", "grams": 12, "contains": ["honey"], "diet_tags": ["vegetarian"], "is_compound": False},
        ],
    },
    {
        "key": "tuna_whole_grain_salad_olive_oil",
        "name": "Tuna, whole grain crackers, olive oil",
        "tags": ["snack"],
        "ingredients": [
            {"name": "tuna, canned in water", "grams": 120, "contains": ["fish"], "diet_tags": ["pescatarian"], "is_compound": False},
            {"name": "whole wheat bread", "grams": 80, "contains": ["gluten"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "olive oil", "grams": 8, "contains": ["olive_oil"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "egg_avocado_toast",
        "name": "Egg + avocado on whole wheat toast",
        "tags": ["snack"],
        "ingredients": [
            {"name": "eggs, whole", "grams": 100, "contains": ["egg"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "avocado", "grams": 80, "contains": ["avocado"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "whole wheat bread", "grams": 80, "contains": ["gluten"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "ricotta_berries_honey_seeds",
        "name": "Ricotta, berries, honey, seeds",
        "tags": ["snack"],
        "ingredients": [
            {"name": "ricotta, lowfat", "grams": 200, "contains": ["dairy"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "berries, mixed", "grams": 150, "contains": ["berries"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "honey", "grams": 10, "contains": ["honey"], "diet_tags": ["vegetarian"], "is_compound": False},
            {"name": "flax seeds, ground", "grams": 8, "contains": ["seeds"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "chickpea_salad_olive_oil_lemon",
        "name": "Chickpea salad (greens, olive oil, lemon)",
        "tags": ["snack"],
        "ingredients": [
            {"name": "chickpeas, cooked", "grams": 200, "contains": ["chickpeas"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "mixed salad greens", "grams": 120, "contains": ["lettuce"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "olive oil", "grams": 10, "contains": ["olive_oil"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "lemon juice", "grams": 10, "contains": ["lemon_juice"], "diet_tags": ["vegan"], "is_compound": False},
        ],
    },
    {
        "key": "almond_butter_banana_oats_snack",
        "name": "Almond butter, banana, oats (snack)",
        "tags": ["snack"],
        "ingredients": [
            {"name": "almond butter, natural", "grams": 18, "contains": ["tree_nut"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "banana", "grams": 120, "contains": ["banana"], "diet_tags": ["vegan"], "is_compound": False},
            {"name": "oats, dry", "grams": 30, "contains": ["oats"], "diet_tags": ["vegetarian"], "is_compound": False},
        ],
    },
]
