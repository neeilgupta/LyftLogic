<template>
  <main style="padding: 20px; font-family: system-ui; max-width: 1200px; margin: 0 auto;">
    <h1 style="margin: 0 0 10px;">Nutrition</h1>
    <p style="margin: 0 0 18px; opacity: 0.8;">
      Generate and iterate meal plans independently of training.
    </p>

        <!-- Maintenance calories guidance -->
    <section
      style="
        border: 1px solid #eee;
        border-radius: 12px;
        padding: 14px;
        background: #fafafa;
        margin-bottom: 14px;
      "
    >
      <div style="font-weight: 800; margin-bottom: 6px;">
        How to find your maintenance calories
      </div>

      <p style="margin: 0 0 10px; line-height: 1.5; opacity: 0.9;">
        Estimate your daily maintenance calories using a TDEE calculator, then enter that number
        in <strong>Maintenance Calories</strong> below.
      </p>

      <ul style="margin: 0 0 10px; padding-left: 18px; line-height: 1.5;">
        <li>Enter age, sex, height, and weight</li>
        <li>Select your activity level</li>
        <li>Use the <strong>Calories/day</strong> result as maintenance</li>
      </ul>

      <a
        href="https://www.calculator.net/calorie-calculator.html"
        target="_blank"
        rel="noopener noreferrer"
        style="text-decoration: underline; font-weight: 600;"
      >
        Open Calorie Calculator (calculator.net)
      </a>
    </section>


    <!-- Inputs + Controls -->
    <section
      style="
        border: 1px solid #eee;
        border-radius: 12px;
        padding: 14px;
        background: #fff;
        margin-bottom: 14px;
      "
    >
      <div style="display:flex; align-items:baseline; justify-content:space-between; gap:10px; margin-bottom: 12px;">
        <div style="font-weight: 800;">Inputs</div>

        <div v-if="nutritionSnapshot" style="opacity: 0.7; font-size: 13px;">
          v{{ nutritionSnapshot.version }} • {{ goalLabel }} • {{ calories }} cal
        </div>
        <div v-else style="opacity: 0.7; font-size: 13px;">
          {{ goalLabel }}<span v-if="goal !== 'maintenance'"> ({{ rate }} lb/wk)</span> • {{ calories }} cal
        </div>
      </div>

      <!-- Minimal inputs grid -->
      <div
        style="
          display: grid;
          grid-template-columns: repeat(12, 1fr);
          gap: 10px;
          margin-bottom: 12px;
        "
      >
        <label style="grid-column: span 3; display:flex; flex-direction:column; gap:6px;">
          <span style="font-size: 12px; opacity: 0.75;">Goal</span>
          <select
            v-model="goal"
            :disabled="nutritionLoading"
            style="padding: 8px 10px; border-radius: 10px; border: 1px solid #ddd; background: white;"
          >
            <option value="maintenance">Maintenance</option>
            <option value="cut">Cut</option>
            <option value="bulk">Bulk</option>
          </select>
        </label>

        <label style="grid-column: span 3; display:flex; flex-direction:column; gap:6px;">
            <span style="font-size: 12px; opacity: 0.75;">
            {{ goal === "maintenance" ? "Maintenance Calories" : "Target Calories" }}
            </span>
          <input
            v-model.number="calories"
            :disabled="nutritionLoading"
            type="number"
            inputmode="numeric"
            min="0"
            style="padding: 8px 10px; border-radius: 10px; border: 1px solid #ddd; background: white;"
          />
        </label>

        <label
            v-if="goal !== 'maintenance'"
            style="grid-column: span 3; display:flex; flex-direction:column; gap:6px;"
        >
            <span style="font-size: 12px; opacity: 0.75;">Rate</span>
            <select
                v-model="rate"
                :disabled="nutritionLoading"
                style="padding: 8px 10px; border-radius: 10px; border: 1px solid #ddd; background: white;"
            >
                <option value="0.5">0.5 lb/week</option>
                <option value="1">1 lb/week</option>
                <option value="2">2 lb/week</option>
            </select>
        </label>

        <label style="grid-column: span 3; display:flex; flex-direction:column; gap:6px;">
        <span style="font-size: 12px; opacity: 0.75;">Meals per day (blank = infer)</span>
        <input
            v-model="mealsPerDayText"
            :disabled="nutritionLoading"
            type="text"
            inputmode="numeric"
            placeholder="infer"
            style="padding: 8px 10px; border-radius: 10px; border: 1px solid #ddd; background: white;"
        />
        </label>


        <label style="grid-column: span 3; display:flex; flex-direction:column; gap:6px;">
          <span style="font-size: 12px; opacity: 0.75;">Diet</span>
          <select
            v-model="diet"
            :disabled="nutritionLoading"
            style="padding: 8px 10px; border-radius: 10px; border: 1px solid #ddd; background: white;"
          >
            <option value="none">None</option>
            <option value="vegetarian">Vegetarian</option>
            <option value="vegan">Vegan</option>
            <option value="pescatarian">Pescatarian</option>
            <option value="keto">Keto</option>
            <option value="paleo">Paleo</option>
            <option value="halal">Halal</option>
            <option value="kosher">Kosher</option>
            <option value="gluten_free">Gluten-free</option>
            <option value="dairy_free">Dairy-free</option>

          </select>
        </label>

        <label style="grid-column: span 12; display:flex; flex-direction:column; gap:6px;">
          <span style="font-size: 12px; opacity: 0.75;">Allergies (one per line)</span>
          <textarea
            v-model="allergiesText"
            :disabled="nutritionLoading"
            rows="3"
            :placeholder="`e.g.\npeanuts\nshellfish`"
            style="padding: 10px; border-radius: 10px; border: 1px solid #ddd; background: white; resize: vertical;"
          />
        </label>
      </div>

      <!-- Controls -->
      <div style="display:flex; gap:10px; flex-wrap: wrap;">
        <button
          :disabled="nutritionLoading"
          @click="onNutritionGenerate"
          :style="buttonStyle(nutritionLoading)"
        >
          {{ nutritionLoading ? "Working…" : "Generate nutrition" }}
        </button>

        <button
          :disabled="!nutritionSnapshot || nutritionLoading"
          @click="onNutritionRegenerate"
          :style="buttonStyle(!nutritionSnapshot || nutritionLoading)"
        >
          {{ nutritionLoading ? "Working…" : "Regenerate (diff)" }}
        </button>
      </div>

      <div v-if="nutritionError" style="color:#b00020; font-size: 13px; margin-top: 10px;">
        {{ nutritionError }}
      </div>
    </section>

        <!-- Generated meals -->
    <section
      v-if="nutritionOutput"
      style="
        border: 1px solid #eee;
        border-radius: 12px;
        padding: 14px;
        background: #fff;
        margin-bottom: 14px;
      "
    >
      <div style="display:flex; justify-content:space-between; align-items:baseline; gap:10px; margin-bottom: 10px;">
        <div style="font-weight: 800;">Meal Plan</div>
        <div style="opacity: 0.7; font-size: 13px;">
          {{ (nutritionOutput.accepted?.length ?? 0) }} accepted • {{ (nutritionOutput.rejected?.length ?? 0) }} rejected
        </div>
      </div>

      <div v-if="!nutritionOutput.accepted || nutritionOutput.accepted.length === 0" style="opacity: 0.75;">
        No accepted meals returned. Try increasing batch size or loosening constraints.
      </div>

      <div v-else>
        <div
            v-for="slot in SLOT_ORDER.filter(s => getMealsForSlot(s.key).length)"
            :key="slot.key"
            style="margin-bottom: 16px;"
        >
            <div style="font-weight: 800; margin-bottom: 8px;">
            {{ slot.label }} ({{ getMealsForSlot(slot.key).length }})
            </div>

            <div style="display: grid; grid-template-columns: repeat(12, 1fr); gap: 10px;">
            <div
                v-for="(meal, idx) in getMealsForSlot(slot.key)"
                :key="meal.template_key || meal.key || meal.name || idx"
                style="grid-column: span 6; border: 1px solid #eee; border-radius: 12px; padding: 12px;"
            >
                <div style="font-weight: 700; margin-bottom: 6px;">
                {{ meal.name }}
                <div style="font-size: 11px; opacity: 0.6; margin-bottom: 6px;">
                template_key: {{ meal.template_key || "—" }} • key: {{ meal.key || "—" }}
                </div>

                </div>

                

                <div style="font-size: 12px; opacity: 0.7; margin-bottom: 8px;">
                {{ mealMacrosLine(meal) }}
                </div>

                <div style="font-size: 13px; opacity: 0.85; margin-bottom: 10px;">
                <span style="font-weight: 600;">Ingredients:</span>
                <span v-if="meal.ingredients?.length">
                    {{ meal.ingredients.map((i: any) => i.name).join(", ") }}
                </span>
                <span v-else>—</span>
                </div>

                <details style="margin-top: 8px; border-top: 1px solid #eee; padding-top: 8px;">
                <summary style="cursor: pointer; font-size: 12px; font-weight: 600; opacity: 0.7;">
                    View ingredients & macros
                </summary>

                <div style="margin-top: 8px; display: flex; flex-direction: column; gap: 8px;">
                    <div style="background: #fafafa; border-radius: 8px; padding: 8px;">
                    <div style="font-weight: 600; font-size: 12px; margin-bottom: 4px;">Macros</div>
                    <div style="font-size: 11px; line-height: 1.5; opacity: 0.85;">
                        <div>Calories: {{ meal.macros?.calories ?? 0 }}</div>
                        <div>Protein: {{ meal.macros?.protein_g ?? 0 }} g</div>
                        <div>Carbs: {{ meal.macros?.carbs_g ?? 0 }} g</div>
                        <div>Fat: {{ meal.macros?.fat_g ?? 0 }} g</div>
                    </div>
                    </div>

                    <div style="background: #fafafa; border-radius: 8px; padding: 8px;">
                    <div style="font-weight: 600; font-size: 12px; margin-bottom: 4px;">Ingredients</div>
                    <ul style="margin: 0; padding-left: 16px; font-size: 11px;">
                        <li v-for="(ing, j) in meal.ingredients ?? []" :key="j">
                        <strong>{{ ing.name }}</strong>
                        <span v-if="ing.grams != null"> — {{ ing.grams }} g</span>
                        </li>
                    </ul>
                    </div>
                </div>
                </details>
            </div>
            </div>
        </div>
    </div>

      <details v-if="nutritionOutput.rejected && nutritionOutput.rejected.length" style="margin-top: 12px;">
        <summary style="cursor: pointer; font-weight: 600;">
          Rejected meals ({{ nutritionOutput.rejected.length }})
        </summary>
        <ul style="margin: 10px 0 0; padding-left: 18px; line-height: 1.5;">
          <li v-for="(meal, idx) in nutritionOutput.rejected" :key="meal.template_key || meal.key || meal.name || idx">
            {{ meal.name }}
          </li>
        </ul>
      </details>
    </section>


    <!-- Diff / Explanations -->
    <section
      style="
        border: 1px solid #eee;
        border-radius: 12px;
        padding: 14px;
        background: #fff;
        margin-bottom: 14px;
      "
    >
      <NutritionDiff :explanations="nutritionExplanations" :version="nutritionSnapshot?.version ?? null" />
    </section>

    <!-- Raw JSON -->
    <section
      v-if="nutritionSnapshot"
      style="
        border: 1px solid #eee;
        border-radius: 12px;
        padding: 14px;
        background: #fff;
      "
    >
      <div style="font-weight: 800; margin-bottom: 8px;">Raw JSON</div>

      <details style="margin-bottom: 10px;">
        <summary style="cursor: pointer; font-weight: 600;">Version snapshot</summary>
        <pre style="white-space: pre-wrap; margin-top: 8px;">{{ pretty(nutritionSnapshot) }}</pre>
      </details>

      <details v-if="nutritionOutput">
        <summary style="cursor: pointer; font-weight: 600;">Output</summary>
        <pre style="white-space: pre-wrap; margin-top: 8px;">{{ pretty(nutritionOutput) }}</pre>
      </details>
    </section>

    <p v-else style="opacity: 0.7;">
      No nutrition generated yet. Click “Generate nutrition”.
    </p>
  </main>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import NutritionDiff from "../components/NutritionDiff.vue";
import { useNutritionApi, type NutritionTargets } from "../../services/nutrition";

const { generateNutrition, regenerateNutrition } = useNutritionApi();

const nutritionLoading = ref(false);
const nutritionError = ref<string | null>(null);

const nutritionSnapshot = ref<any | null>(null);
const nutritionOutput = ref<any | null>(null);
const nutritionExplanations = ref<string[] | null>(null);

type NutritionGoal = "maintenance" | "cut" | "bulk";
type DietChoice =
  | "none"
  | "vegetarian"
  | "vegan"
  | "pescatarian"
  | "keto"
  | "paleo"
  | "halal"
  | "kosher"
  | "gluten_free"
  | "dairy_free";
  type RateChoice = "0.5" | "1" | "2";


// Deterministic defaults (unchanged from your current hardcoded values)
const defaultNutritionTargets: NutritionTargets = {
  maintenance: 2600,
  cut: { "0.5": 2400, "1": 2200, "2": 2000 },
  bulk: { "0.5": 2800, "1": 3000, "2": 3200 },
};

// UI state (fresh refresh resets state — expected)
const goal = ref<NutritionGoal>("maintenance");
const calories = ref<number>(defaultNutritionTargets.maintenance);
const mealsPerDay = ref<number | null>(null);
const allergiesText = ref<string>("");
const diet = ref<DietChoice>("none");
const rate = ref<RateChoice>("1");

const mealsPerDayText = ref<string>(String(mealsPerDay.value ?? ""));

// Keep mealsPerDay in sync (null when blank)
watch(mealsPerDayText, (v) => {
  const t = String(v ?? "").trim();
  if (t === "") {
    mealsPerDay.value = null;
    return;
  }
  const n = Number(t);
  mealsPerDay.value = Number.isFinite(n) ? n : null;
});

watch(mealsPerDay, (v) => {
  mealsPerDayText.value = v == null ? "" : String(v);
});




const goalLabel = computed(() => {
  if (goal.value === "maintenance") return "Maintenance";
  if (goal.value === "cut") return "Cut";
  return "Bulk";
});

function defaultCaloriesForGoal(g: NutritionGoal): number {
  if (g === "maintenance") return defaultNutritionTargets.maintenance;

  if (g === "cut") {
    return (
      defaultNutritionTargets.cut["1"] ??
      defaultNutritionTargets.cut["0.5"] ??
      defaultNutritionTargets.cut["2"] ??
      defaultNutritionTargets.maintenance
    );
  }

  // bulk
  return (
    defaultNutritionTargets.bulk["1"] ??
    defaultNutritionTargets.bulk["0.5"] ??
    defaultNutritionTargets.bulk["2"] ??
    defaultNutritionTargets.maintenance
  );
}

function presetCaloriesFor(goal: NutritionGoal, r: RateChoice): number {
  if (goal === "maintenance") return defaultNutritionTargets.maintenance;

  if (goal === "cut") {
    return (
      defaultNutritionTargets.cut[r] ??
      defaultNutritionTargets.cut["1"] ??
      defaultNutritionTargets.maintenance
    );
  }

  // bulk
  return (
    defaultNutritionTargets.bulk[r] ??
    defaultNutritionTargets.bulk["1"] ??
    defaultNutritionTargets.maintenance
  );
}




// Small UX win: when goal changes, snap calories to that goal’s default.
// (Still deterministic; no backend changes.)
watch(
  [() => goal.value, () => rate.value],
  ([g, r]) => {
    calories.value = presetCaloriesFor(g, r);
  }
);

const allergies = computed<string[]>(() => {
  return allergiesText.value
    .split("\n")
    .map((s) => s.trim())
    .filter((s) => s.length > 0);
});

// Pure function: inputs -> request payload (no side effects)
function buildNutritionBaseRequest(inputs: {
  goal: NutritionGoal;
  calories: number;
  mealsPerDay: number | null; // <-- allow blank/infer
  allergies: string[];
  diet: DietChoice;
}) {
  const targets: NutritionTargets = {
    maintenance: defaultNutritionTargets.maintenance,
    cut: { ...defaultNutritionTargets.cut },
    bulk: { ...defaultNutritionTargets.bulk },
  };

  // Map the single calories input onto the selected goal.
  // Backend doesn’t use targets for generation today, but it’s correct for snapshot/versioning.
  if (inputs.goal === "maintenance") {
    targets.maintenance = inputs.calories;
  } else if (inputs.goal === "cut") {
    targets.cut = { "0.5": inputs.calories, "1": inputs.calories, "2": inputs.calories };
  } else {
    targets.bulk = { "0.5": inputs.calories, "1": inputs.calories, "2": inputs.calories };
  }

  const req: any = {
    targets,
    diet: inputs.diet === "none" ? null : inputs.diet,
    allergies: inputs.allergies,
    max_attempts: 10,
  };

  // Determine meals_needed and batch_size:
  // - If mealsPerDay is blank/null: send 0 as sentinel (backend will infer from calories)
  // - If mealsPerDay is provided: clamp to 2..6 and send actual value
  let mealsNeeded = 0;
  let batchSize = 0;
  if (inputs.mealsPerDay !== null && Number.isFinite(Number(inputs.mealsPerDay))) {
    mealsNeeded = Math.max(2, Math.min(6, Math.trunc(Number(inputs.mealsPerDay))));
    batchSize = mealsNeeded;
  }
  req.meals_needed = mealsNeeded;
  req.batch_size = batchSize;

  return req;
}


function pretty(x: any) {
  return JSON.stringify(x, null, 2);
}

function buttonStyle(disabled: boolean) {
  return {
    padding: "8px 12px",
    borderRadius: "10px",
    border: "1px solid #ddd",
    background: "white",
    cursor: disabled ? "not-allowed" : "pointer",
    opacity: disabled ? 0.6 : 1,
  } as any;
}

function currentInputs() {
  return {
    goal: goal.value,
    calories: calories.value,
    mealsPerDay: mealsPerDay.value,
    allergies: allergies.value,
    diet: diet.value,
    rate: rate.value,
  };
}

function mealMacrosLine(meal: any): string {
  const macros = meal.macros;
  if (!macros) return "";
  
  const cal = Math.round(macros.calories || 0);
  const p = Math.round(macros.protein_g || 0);
  const c = Math.round(macros.carbs_g || 0);
  const f = Math.round(macros.fat_g || 0);
  
  return `${cal} cal • P ${p}g • C ${c}g • F ${f}g`;
}


const SLOT_ORDER = [
  { key: "breakfast", label: "Breakfast" },
  { key: "lunch", label: "Lunch" },
  { key: "dinner", label: "Dinner" },
  { key: "snack", label: "Snacks" },
] as const;

type SlotKey = typeof SLOT_ORDER[number]["key"];

function mealSlot(meal: any): SlotKey | null {
  const tags = (meal.tags || []).map((t: string) => t.toLowerCase());
  if (tags.includes("breakfast")) return "breakfast";
  if (tags.includes("lunch")) return "lunch";
  if (tags.includes("dinner")) return "dinner";
  if (tags.includes("snack")) return "snack";
  return null;
}

type MealSlot = "breakfast" | "lunch" | "dinner" | "snack"


const groupedMeals = computed<Record<MealSlot, any[]>>(() => {
  const groups: Record<MealSlot, any[]> = {
    breakfast: [],
    lunch: [],
    dinner: [],
    snack: [],
  };

  const accepted = nutritionOutput.value?.accepted ?? [];

  // Track duplicates globally + per-slot (for debugging)
  const seenGlobal = new Set<string>();

  function sig(meal: any): string {
    return String(meal?.template_key || meal?.key || meal?.name || "").trim().toLowerCase();
  }

  for (const meal of accepted) {
    const s = sig(meal);
    const slot = mealSlot(meal);

    if (!slot || !s) continue;

    // If something duplicated AFTER acceptance, you'll catch it here instantly.
    if (seenGlobal.has(s)) {
      console.warn("[nutrition] DUPLICATE IN accepted (post-acceptance):", {
        sig: s,
        name: meal?.name,
        key: meal?.key,
        template_key: meal?.template_key,
        tags: meal?.tags,
      });
    } else {
      seenGlobal.add(s);
    }

    groups[slot].push(meal);
  }

  if (groups.dinner.length === 0 && groups.lunch.length >= 2) {
    const dinnerMeal = groups.lunch.pop();
    if (dinnerMeal) groups.dinner.push(dinnerMeal);
  }

  // FINAL GUARD: dedupe within each slot deterministically
  for (const k of Object.keys(groups) as MealSlot[]) {
    const seenSlot = new Set<string>();
    groups[k] = groups[k].filter((m) => {
      const s = sig(m);
      if (!s) return false;
      if (seenSlot.has(s)) {
        console.warn("[nutrition] DUPLICATE IN slot render:", { slot: k, sig: s, name: m?.name });
        return false;
      }
      seenSlot.add(s);
      return true;
    });
  }

  return groups;
});



function getMealsForSlot(slotKey: string): any[] {
  return (groupedMeals.value as Record<string, any[]>)[slotKey] ?? [];
}


async function onNutritionGenerate() {
  nutritionLoading.value = true;
  nutritionError.value = null;

  try {
    const base = buildNutritionBaseRequest(currentInputs());
    const res = await generateNutrition(base);
    nutritionSnapshot.value = res.version_snapshot;
    nutritionOutput.value = res.output ?? null;
    nutritionExplanations.value = [];
  } catch (e: any) {
    nutritionError.value = e?.data?.detail ?? e?.message ?? String(e);
  } finally {
    nutritionLoading.value = false;
  }
}

async function onNutritionRegenerate() {
  if (!nutritionSnapshot.value) {
    nutritionError.value = "No snapshot available for regeneration.";
    return;
  }

  nutritionLoading.value = true;
  nutritionError.value = null;

  try {
    const base = buildNutritionBaseRequest(currentInputs());
    const res = await regenerateNutrition({
      ...base,
      prev_snapshot: nutritionSnapshot.value,
    });

    nutritionSnapshot.value = res.version_snapshot;
    nutritionOutput.value = res.output ?? null;
    nutritionExplanations.value = res.explanations || [];
  } catch (e: any) {
    nutritionError.value = e?.data?.detail ?? e?.message ?? String(e);
  } finally {
    nutritionLoading.value = false;
  }
}
</script>
