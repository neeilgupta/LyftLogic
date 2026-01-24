# MEAL_SYSTEM_SPEC_v1

## 1) Inputs

The nutrition generator takes:

- `target_calories: number`
- `diet: string | null`  
  (ex: vegan, vegetarian, pescatarian, null)
- `allergies: string[]`  
  (tokens like dairy, egg, gluten, soy, peanut, tree_nut, sesame, etc.)
- `meals_needed: number | null`  
  (optional internal override)

---

## 2) Core policy

- We **always generate by slots internally**.
- If `meals_needed` is provided, it **overrides inference**.
- If `meals_needed` is null or missing, we **infer meal count from `target_calories`**.
- For v1, **dessert is bundled into snacks** (no separate dessert slot).

---

## 3) Meal slots

Canonical slot labels:

- `breakfast`
- `lunch`
- `dinner`
- `snack`

Ordering is deterministic:
breakfast → lunch → dinner → snacks (in order)


---

## 4) Meal count selection

### 4.1 Override behavior (internal / advanced use)

If `meals_needed` is set, use this deterministic slot mapping:

- `2` meals → `[lunch, dinner]`
- `3` meals → `[breakfast, lunch, dinner]`
- `4` meals → `[breakfast, lunch, dinner, snack]`
- `5` meals → `[breakfast, lunch, dinner, snack, snack]`
- `6` meals → `[breakfast, lunch, dinner, snack, snack, snack]`

If a value greater than `6` is provided, clamp to `6` for v1.

---

### 4.2 Inferred behavior (default user-facing)

If `meals_needed` is null or missing, infer from `target_calories`:

- `< 2300` → **4 meals**
- `2300–2800` → **5 meals**
- `> 2800` → **6 meals**

---

## 5) Slot calorie budgets

Compute per-slot calorie targets as fixed percentages of `target_calories`.

### For 4 meals (`B, L, D, S`)
- breakfast: **25%**
- lunch: **30%**
- dinner: **30%**
- snack: **15%**

### For 5 meals (`B, L, D, S, S`)
- breakfast: **24%**
- lunch: **26%**
- dinner: **26%**
- snack1: **12%**
- snack2: **12%**

### For 6 meals (`B, L, D, S, S, S`)
- breakfast: **22%**
- lunch: **24%**
- dinner: **24%**
- snack1: **10%**
- snack2: **10%**
- snack3: **10%**

#### Rounding
- Round each slot target to the nearest **10 calories**.
- Adjust the **last slot** by the remaining difference so slot totals sum exactly to `target_calories`.

---

## 6) Template selection rules

Meals come from `MEAL_LIBRARY`. Each template includes:

- `tags` containing one or more of:
  - `breakfast`
  - `lunch`
  - `dinner`
  - `snack`
- `ingredients` list with:
  - `name`
  - `grams`
  - diet and allergen metadata

### Selection process

1. Filter templates by diet compatibility and allergies.
2. Filter templates by slot tag.
3. Pick deterministically (seeded).
4. If a slot has no matching templates:
   - Fall back to any template allowed by diet/allergies (**v1 fail-open**).
   - Determinism must be preserved.

---

## 7) Portion scaling and closing

We aim for **accuracy, not perfection**.

Meals are classified as:

- **Scalable**
  - Clear protein base
  - Clear carb base
  - Optional fat knob
- **Fixed**
  - Should be used sparingly

### Portioning strategy (v1)

1. Scale the entire meal within a safe range  
   (example: `0.8 → 1.6`)
2. Close **protein** using protein base if under target
3. Close **calories** using carb base
4. Optionally close **fat** using fat knob

Dessert is treated as a **snack template** in v1.

---

## 8) Output expectations

- The number of accepted meals equals the number of slots generated.
- Slot identity is reflected using existing fields (e.g. `tags`), with **no API shape changes**.
- The frontend:
  - Groups meals by slot
  - Displays ingredients and per-meal macros
