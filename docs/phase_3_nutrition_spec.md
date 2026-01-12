Phase 3 — Nutrition Output Contract (Allergy-Safe, Fail-Closed)
Core Guarantee
LyftLogic will never output a meal unless it has an explicit ingredient list that passes a deterministic allergy scan.
If the system cannot prove safety, it rejects the meal and regenerates (fail-closed).
A) Required Data Model
NutritionPlanOutputV1
type NutritionPlanOutputV1 = {
  title: string
  summary: string

  targets: {
    calories: number
    protein_g: number
    carbs_g: number
    fat_g: number
  }

  weekly_plan: DayMealsV1[]

  grocery_list: GroceryItemV1[] // derived from ingredients, deterministic
}
DayMealsV1
type DayMealsV1 = {
  day_index: number // 0..6
  label: string     // e.g. "Mon"
  meals: MealV1[]
  day_totals?: {
    calories: number
    protein_g: number
    carbs_g: number
    fat_g: number
  }
}
MealV1 (NON-NEGOTIABLE)
type MealV1 = {
  meal_id: string        // stable key, e.g. "d2_breakfast_0"
  name: string           // display name

  ingredients: IngredientV1[]  // REQUIRED, cannot be empty
  instructions?: string[]      // optional

  macros_estimate?: {
    calories: number
    protein_g: number
    carbs_g: number
    fat_g: number
  }
}
IngredientV1 (STRUCTURED)
type IngredientV1 = {
  name: string          // e.g. "potato", "cocoa powder", "whey protein"
  quantity?: string     // e.g. "200g", "1 tbsp"
  tags?: string[]       // optional: ["dairy"], ["nightshade"], etc.
  sub_ingredients?: IngredientV1[] // REQUIRED when ingredient is "compound"
}
GroceryItemV1
type GroceryItemV1 = {
  name: string
  total_quantity?: string
}
B) “Compound Ingredient” Rule (Prevents Hidden Allergens)
Certain ingredient names are not allowed unless decomposed via sub_ingredients.
Compounds that must be decomposed
Examples (not exhaustive):
"sauce"
"seasoning"
"spice mix"
"curry paste"
"dressing"
"marinade"
"protein bar"
"granola"
"store-bought broth"
"mixed frozen vegetables"
"processed snack"
Contract
If an ingredient matches a compound class:
it must include sub_ingredients[] with explicit items
else the meal is rejected/regenerated
This is what makes “weird allergy” enforcement actually reliable.
C) Allergy / Diet Constraints Model
NutritionInputV1
type NutritionInputV1 = {
  profile: {
    age?: number
    sex?: "male" | "female" | "other"
    height_cm?: number
    weight_kg?: number
    activity_level?: "low" | "moderate" | "high"
    goal?: "cut" | "maintain" | "bulk"
  }

  allergy_terms: string[]     // freeform: ["potato", "chocolate", "kiwi"]
  allergy_aliases?: string[]  // optional user-provided expansions

  diet_mode?: "none" | "vegetarian" | "vegan" | "pescatarian"

  preferences_tokens?: string[] // e.g. ["high_protein", "budget_friendly"]
}
Diet mode → deterministic banned terms
vegetarian bans: meat, poultry, fish, gelatin, anchovy, etc.
vegan bans: + eggs, dairy, honey, etc.
(These are finite and can be curated safely.)
D) Deterministic Enforcement Algorithm (Fail-Closed)
1) Normalize
Normalize both:
user allergy terms
every ingredient name
Steps:
lowercase
strip punctuation
collapse whitespace
basic singularization (potatoes → potato)
2) Expand banned terms
banned_terms = allergy_terms + allergy_aliases + diet_mode_bans
Optional: allow a small curated expansion for common allergens (nuts/dairy/etc.)
But for “potato/chocolate”, literal enforcement already works if ingredients are explicit.
3) Ingredient scan (recursive)
For each meal:
For each ingredient (including sub_ingredients recursively):
if ingredient.name matches any banned term (word-boundary match) → REJECT meal
If any compound ingredient lacks sub_ingredients → REJECT meal
4) Plan-level validity
A NutritionPlanOutput is valid only if:
all meals pass
all days meet macro targets within tolerance (separate rule)
grocery list can be derived
If invalid → regenerate offending meals (not whole plan if you want efficiency)
E) Versioning & Diff (mirrors Phase 2)
Nutrition versions table mirrors workout versions
Each version stores:
input snapshot
output snapshot
diff snapshot
restored_from
Nutrition diff schema
type NutritionDiffV1 = {
  replaced_meals: { day_index: number, meal_id: string, from: string, to: string }[]
  removed_meals: { day_index: number, meal_id: string, name: string }[]
  added_meals: { day_index: number, meal_id: string, name: string }[]
  macro_changes?: { calories_delta: number, protein_delta_g: number, carbs_delta_g: number, fat_delta_g: number }
  notes?: string[] // short reasons: "Removed potato due to allergy"
}
F) UI Trust Signals
Always show:
“Allergy-safe: passed ingredient scan” badge
Display allergy terms being enforced
If user adds new allergy: immediate version diff shows the removed/replaced meals
TL;DR Rules (the 3 rules that make it “perfect”)
Meal must include explicit ingredients[]
Compound ingredients must be decomposed (sub_ingredients[])
If the scanner can’t prove it safe → reject/regenerate


## Phase 3 Implementation Order

A) Macro calculator (pure math, no LLM)
B) Allergy-safe meal schema + scanner
C) LLM meal generation + regeneration loop
D) Nutrition versioning + diff
E) UI (after correctness)
