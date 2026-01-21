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
          <span style="font-size: 12px; opacity: 0.75;">Meals per day</span>
          <input
            v-model.number="mealsPerDay"
            :disabled="nutritionLoading"
            type="number"
            inputmode="numeric"
            min="3"
            max="6"
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
const mealsPerDay = ref<number>(4);
const allergiesText = ref<string>("");
const diet = ref<DietChoice>("none");
const rate = ref<RateChoice>("1");


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
  mealsPerDay: number;
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

  return {
    targets,
    diet: inputs.diet === "none" ? null : inputs.diet,
    allergies: inputs.allergies,
    meals_needed: inputs.mealsPerDay,
    max_attempts: 10,
    batch_size: 6,
  };
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
