# apps/backend/services/nutrition/ingredients_pantry.py
# Deterministic, local "USDA-ish" macros per 100g.
# Values are approximate; consistency > perfect accuracy for v1.

from __future__ import annotations

INGREDIENT_PANTRY_PER_100G: dict[str, dict[str, float]] = {
    # ---------- CARB BASES ----------
    "white rice, cooked": {"calories": 130, "protein_g": 2.7, "carbs_g": 28.0, "fat_g": 0.3},
    "brown rice, cooked": {"calories": 112, "protein_g": 2.3, "carbs_g": 23.0, "fat_g": 0.9},
    "oats, dry": {"calories": 389, "protein_g": 16.9, "carbs_g": 66.3, "fat_g": 6.9},
    "pasta, cooked": {"calories": 131, "protein_g": 5.0, "carbs_g": 25.0, "fat_g": 1.1},
    "bread, whole wheat": {"calories": 247, "protein_g": 13.0, "carbs_g": 41.0, "fat_g": 4.2},
    "tortilla, flour": {"calories": 304, "protein_g": 8.0, "carbs_g": 50.0, "fat_g": 7.5},
    "potato, baked": {"calories": 93, "protein_g": 2.5, "carbs_g": 21.0, "fat_g": 0.1},
    "sweet potato, baked": {"calories": 90, "protein_g": 2.0, "carbs_g": 21.0, "fat_g": 0.2},
    "banana": {"calories": 89, "protein_g": 1.1, "carbs_g": 22.8, "fat_g": 0.3},
    "apple": {"calories": 52, "protein_g": 0.3, "carbs_g": 13.8, "fat_g": 0.2},

    # ---------- PROTEINS ----------
    "chicken breast, cooked": {"calories": 165, "protein_g": 31.0, "carbs_g": 0.0, "fat_g": 3.6},
    "ground turkey 93%, cooked": {"calories": 170, "protein_g": 23.0, "carbs_g": 0.0, "fat_g": 9.0},
    "salmon, cooked": {"calories": 208, "protein_g": 20.0, "carbs_g": 0.0, "fat_g": 13.0},
    "tuna, canned in water": {"calories": 116, "protein_g": 26.0, "carbs_g": 0.0, "fat_g": 1.0},
    "eggs, whole": {"calories": 143, "protein_g": 13.0, "carbs_g": 0.7, "fat_g": 9.5},
    "egg whites": {"calories": 52, "protein_g": 11.0, "carbs_g": 0.7, "fat_g": 0.2},
    "greek yogurt, nonfat": {"calories": 59, "protein_g": 10.0, "carbs_g": 3.6, "fat_g": 0.4},
    "cottage cheese, lowfat": {"calories": 98, "protein_g": 11.0, "carbs_g": 3.4, "fat_g": 4.3},
    "whey protein powder": {"calories": 400, "protein_g": 80.0, "carbs_g": 8.0, "fat_g": 6.0},
    "tofu, firm": {"calories": 144, "protein_g": 17.0, "carbs_g": 3.0, "fat_g": 9.0},
    "tempeh": {"calories": 193, "protein_g": 20.0, "carbs_g": 9.0, "fat_g": 11.0},
    "lentils, cooked": {"calories": 116, "protein_g": 9.0, "carbs_g": 20.0, "fat_g": 0.4},
    "black beans, cooked": {"calories": 132, "protein_g": 8.9, "carbs_g": 23.7, "fat_g": 0.5},
    "edamame": {"calories": 121, "protein_g": 11.9, "carbs_g": 8.9, "fat_g": 5.2},

    # ---------- FATS ----------
    "olive oil": {"calories": 884, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 100.0},
    "avocado": {"calories": 160, "protein_g": 2.0, "carbs_g": 8.5, "fat_g": 14.7},
    "peanut butter": {"calories": 588, "protein_g": 25.0, "carbs_g": 20.0, "fat_g": 50.0},
    "almonds": {"calories": 579, "protein_g": 21.0, "carbs_g": 22.0, "fat_g": 50.0},
    "butter": {"calories": 717, "protein_g": 0.9, "carbs_g": 0.1, "fat_g": 81.0},

    # ---------- VEG / FRUIT / EXTRAS ----------
    "spinach": {"calories": 23, "protein_g": 2.9, "carbs_g": 3.6, "fat_g": 0.4},
    "broccoli": {"calories": 34, "protein_g": 2.8, "carbs_g": 6.6, "fat_g": 0.4},
    "mixed salad greens": {"calories": 17, "protein_g": 1.4, "carbs_g": 3.3, "fat_g": 0.2},
    "tomato": {"calories": 18, "protein_g": 0.9, "carbs_g": 3.9, "fat_g": 0.2},
    "onion": {"calories": 40, "protein_g": 1.1, "carbs_g": 9.3, "fat_g": 0.1},
    "bell pepper": {"calories": 31, "protein_g": 1.0, "carbs_g": 6.0, "fat_g": 0.3},
    "cucumber": {"calories": 15, "protein_g": 0.7, "carbs_g": 3.6, "fat_g": 0.1},

    # ---------- “SAUCE / CONDIMENT” (keep tiny grams anyway) ----------
    "soy sauce": {"calories": 53, "protein_g": 8.0, "carbs_g": 4.9, "fat_g": 0.6},
    "salsa": {"calories": 36, "protein_g": 1.5, "carbs_g": 7.0, "fat_g": 0.2},
}
