<template>
  <main class="nutrition-page">
    <h1 style="margin: 0 0 10px;">Nutrition</h1>
    <p style="margin: 0 0 18px; opacity: 0.8;">
      Generate and iterate meal plans independently of training.
    </p>

        <!-- Maintenance calories guidance -->
    <section class="ll-card ll-card-muted">
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

<section class="ll-card">
  <div style="display:flex; justify-content:space-between; align-items:baseline; gap:10px; margin-bottom: 10px;">
    <div style="font-weight: 800;">Macro Calculator</div>
    <div v-if="macroResult" style="opacity: 0.7; font-size: 13px;">
      TDEE {{ Math.round(macroResult.macros.tdee) }} • Maint {{ macroResult.macros.maintenance }}
    </div>
  </div>

  <div
    style="
      display: grid;
      grid-template-columns: repeat(12, 1fr);
      gap: 10px;
      margin-bottom: 12px;
    "
  >
    <label style="grid-column: span 2; display:flex; flex-direction:column; gap:6px;">
      <span style="font-size: 12px; opacity: 0.75;">Sex</span>
      <select
        v-model="macroSex"
        :disabled="macroLoading || nutritionLoading"
        style="padding: 8px 10px; border-radius: 10px; border: 1px solid #ddd; background: white;"
      >
        <option value="male">Male</option>
        <option value="female">Female</option>
      </select>
    </label>

    <label style="grid-column: span 2; display:flex; flex-direction:column; gap:6px;">
      <span style="font-size: 12px; opacity: 0.75;">Age</span>
      <input
        v-model.number="macroAge"
        :disabled="macroLoading || nutritionLoading"
        type="number"
        inputmode="numeric"
        min="1"
        style="padding: 8px 10px; border-radius: 10px; border: 1px solid #ddd; background: white;"
      />
    </label>

    <label style="grid-column: span 2; display:flex; flex-direction:column; gap:6px;">
    <span style="font-size: 12px; opacity: 0.75;">Height (ft)</span>
    <input
        v-model.number="macroHeightFt"
        :disabled="macroLoading || nutritionLoading"
        type="number"
        inputmode="numeric"
        min="0"
        style="padding: 8px 10px; border-radius: 10px; border: 1px solid #ddd; background: white;"
    />
    </label>

    <label style="grid-column: span 2; display:flex; flex-direction:column; gap:6px;">
    <span style="font-size: 12px; opacity: 0.75;">Height (in)</span>
    <input
        v-model.number="macroHeightIn"
        :disabled="macroLoading || nutritionLoading"
        type="number"
        inputmode="numeric"
        min="0"
        max="11"
        style="padding: 8px 10px; border-radius: 10px; border: 1px solid #ddd; background: white;"
    />
    </label>


    <label style="grid-column: span 2; display:flex; flex-direction:column; gap:6px;">
    <span style="font-size: 12px; opacity: 0.75;">Weight (lb)</span>
    <input
        v-model.number="macroWeightLb"
        :disabled="macroLoading || nutritionLoading"
        type="number"
        inputmode="numeric"
        min="1"
        style="padding: 8px 10px; border-radius: 10px; border: 1px solid #ddd; background: white;"
    />
    </label>


    <label style="grid-column: span 4; display:flex; flex-direction:column; gap:6px;">
      <span style="font-size: 12px; opacity: 0.75;">Activity</span>
      <select
        v-model="macroActivity"
        :disabled="macroLoading || nutritionLoading"
        style="padding: 8px 10px; border-radius: 10px; border: 1px solid #ddd; background: white;"
      >
        <option value="sedentary">Sedentary (1.2)</option>
        <option value="light">Light (1.375)</option>
        <option value="moderate">Moderate (1.55)</option>
        <option value="very">Very (1.725)</option>
        <option value="athlete">Athlete (1.9)</option>
      </select>
    </label>
  </div>

  <div style="display:flex; gap:10px; flex-wrap:wrap; align-items:center; margin-bottom: 10px;">
    <button
      :disabled="macroLoading || nutritionLoading"
      @click="onMacroCalc"
      :style="buttonStyle(macroLoading || nutritionLoading)"
    >
      {{ macroLoading ? "Calculating…" : "Calculate" }}
    </button>

    <div v-if="macroResult" style="display:flex; gap:10px; flex-wrap:wrap; align-items:center;">
      <div style="font-size: 13px; opacity: 0.85;">
        <strong>Maintenance:</strong> {{ macroResult.macros.maintenance }} cal/day
      </div>

      <div style="font-size: 13px; opacity: 0.85;">
        <strong>BMR:</strong> {{ macroResult.macros.bmr }} • <strong>Multiplier:</strong> {{ macroResult.macros.activity_multiplier }}
      </div>
    </div>
  </div>

  <!-- Goal/rate selection (drives planner inputs) -->
  <div v-if="macroResult"
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
        :disabled="macroLoading || nutritionLoading"
        style="padding: 8px 10px; border-radius: 10px; border: 1px solid #ddd; background: white;"
      >
        <option value="maintenance">Maintenance</option>
        <option value="cut">Cut</option>
        <option value="bulk">Bulk</option>
      </select>
    </label>

    <label style="grid-column: span 2; display:flex; flex-direction:column; gap:6px;">
      <span style="font-size: 12px; opacity: 0.75;">Rate</span>
      <select
        v-model="rate"
        :disabled="goal === 'maintenance' || macroLoading || nutritionLoading"
        :style="{padding: '8px 10px', borderRadius: '10px', border: '1px solid #ddd', background: 'white', opacity: goal === 'maintenance' ? 0.5 : 1, cursor: goal === 'maintenance' ? 'not-allowed' : 'pointer'}"
      >
        <option value="0.5">0.5 lb/week</option>
        <option value="1">1 lb/week</option>
        <option value="2">2 lb/week</option>
      </select>
    </label>

    <div style="grid-column: span 4; display:flex; gap:10px; flex-wrap:wrap; align-items:flex-end;">
      <button
        :disabled="macroLoading || nutritionLoading"
        @click="onApplyTargetsAndGenerate"
        :style="buttonStyle(macroLoading || nutritionLoading)"
      >
        Apply targets & generate
      </button>
      <button
        :disabled="macroLoading || nutritionLoading"
        @click="onCopyTargets"
        :style="buttonStyle(macroLoading || nutritionLoading)"
        title="Copy targets to clipboard"
      >
        {{ copyStatusLabel }}
      </button>
    </div>

    <div style="grid-column: span 12; font-size: 12px; opacity: 0.75;">
      Uses the Diet/Allergies/Meals-per-day inputs below for generation.
    </div>
  </div>

  <div v-if="macroError" style="color:#b00020; font-size: 13px; margin-top: 10px;">
    {{ macroError }}
  </div>

  <details v-if="macroResult" style="margin-top: 10px;">
    <summary style="cursor: pointer; font-weight: 600; opacity: 0.85;">How this was calculated</summary>
    <pre style="white-space: pre-wrap; margin-top: 8px;">{{ macroResult.macros.explanation }}</pre>
  </details>
</section>




    <!-- Inputs + Controls -->
    <section class="ll-card">
      <div style="display:flex; align-items:baseline; justify-content:space-between; gap:10px; margin-bottom: 12px;">
        <div style="font-weight: 800;">Inputs</div>

        <div v-if="nutritionSnapshot" style="opacity: 0.7; font-size: 13px; text-align:right;">
        v{{ nutritionSnapshot.version }} • {{ goalLabel }} • {{ selectedCaloriesFromTargets }} cal
        <div style="font-size: 12px; opacity: 0.85;">
            Maint {{ appliedTargets?.maintenance ?? "—" }} •
            Cut {{ appliedTargets?.cut?.["0.5"] ?? "—" }}/{{ appliedTargets?.cut?.["1"] ?? "—" }}/{{ appliedTargets?.cut?.["2"] ?? "—" }} •
            Bulk {{ appliedTargets?.bulk?.["0.5"] ?? "—" }}/{{ appliedTargets?.bulk?.["1"] ?? "—" }}/{{ appliedTargets?.bulk?.["2"] ?? "—" }}
        </div>
        </div>

        <div v-else style="opacity: 0.7; font-size: 13px; text-align:right;">
        {{ goalLabel }}<span v-if="goal !== 'maintenance'"> ({{ rate }} lb/wk)</span> • {{ selectedCaloriesFromTargets }} cal
        <div v-if="appliedTargets" style="font-size: 12px; opacity: 0.85;">
            Maint {{ appliedTargets.maintenance }} •
            Cut {{ appliedTargets.cut["0.5"] }}/{{ appliedTargets.cut["1"] }}/{{ appliedTargets.cut["2"] }} •
            Bulk {{ appliedTargets.bulk["0.5"] }}/{{ appliedTargets.bulk["1"] }}/{{ appliedTargets.bulk["2"] }}
        </div>
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

      <!-- Premium loading panel (no spinner) -->
      <LLLoadingPanel
        v-if="nutritionLoading"
        title="Generating nutrition"
        subtitle="Fail-closed: diet + allergens enforced deterministically"
        :elapsed="nutritionElapsedSeconds"
        :steps="nutritionSteps"
        hint="These are daily aims + an example plan (not food tracking). Same inputs → same output."
      />

      <div v-if="nutritionError" style="color:#b00020; font-size: 13px; margin-top: 10px;">
        {{ nutritionError }}
      </div>

    </section>

        <!-- Generated meals -->
    <section v-if="nutritionOutput" class="ll-card">
      <div style="display:flex; justify-content:space-between; align-items:baseline; gap:10px; margin-bottom: 10px;">
        <div style="font-weight: 800;">Meal Plan</div>
        <div style="opacity: 0.7; font-size: 13px;">
          {{ (nutritionOutput.accepted?.length ?? 0) }} accepted • {{ (nutritionOutput.rejected?.length ?? 0) }} rejected
        </div>
      </div>

      <div class="totals-bar">
        <div class="totals-left">
          <div class="totals-title">Daily totals</div>
          <div class="totals-sub">
            <span style="opacity:0.75; font-weight:800;">Aim:</span>
            <span class="pill">{{ macroAims.calories ?? "—" }} cal</span>
            · P <span class="pill">{{ macroAims.protein ?? "—" }}g</span>
            · C <span class="pill">{{ macroAims.carbs ?? "—" }}g</span>
            · F <span class="pill">{{ macroAims.fat ?? "—" }}g</span>

            <template v-if="hasPlanTotals">
              <span class="totals-sep">•</span>
              <span style="opacity:0.75; font-weight:800;">Plan:</span>
              <span class="pill">{{ dailyTotals.calories }} cal</span>
              · P <span class="pill">{{ dailyTotals.protein }}g</span>
              · C <span class="pill">{{ dailyTotals.carbs }}g</span>
              · F <span class="pill">{{ dailyTotals.fat }}g</span>
            </template>
          </div>


        </div>

        <button class="debug-toggle" type="button" @click="showDebug = !showDebug">
          {{ showDebug ? "Hide debug" : "Show debug" }}
        </button>
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
              class="meal-card"
              style="grid-column: span 6;"
            >

                <div style="font-weight: 700; margin-bottom: 6px;">
                {{ meal.name }}
                <div v-if="showDebug" style="font-size: 11px; opacity: 0.6; margin-bottom: 6px;">
                  template_key: {{ meal.template_key || "—" }} • key: {{ meal.key || "—" }}
                </div>


                </div>

                

                <div style="font-size: 12px; opacity: 0.7; margin-bottom: 8px;">
                {{ mealMacrosLine(meal) }}
                </div>

                <div style="font-size: 13px; opacity: 0.85; margin-bottom: 10px;">
                  <span style="font-weight: 600;">Ingredients:</span>
                  <span v-if="baseIngredientNames(meal).length">
                    {{ baseIngredientNames(meal).join(", ") }}
                  </span>
                  <span v-else>—</span>

                  <div v-if="boosterIngredientNames(meal).length" style="margin-top: 6px; font-size: 12px; opacity: 0.75;">
                    <span style="font-weight: 700; color: #7c3aed;">Adjustments:</span>
                    <span>{{ boosterIngredientNames(meal).join(", ") }}</span>
                  </div>
                </div>


                <details style="margin-top: 8px; border-top: 1px solid rgba(255,255,255,0.07); padding-top: 8px; border: none; background: none; border-radius: 0; padding: 0; margin-top: 10px;">
                <summary style="cursor: pointer; font-size: 12px; font-weight: 600; opacity: 0.7;">
                    View ingredients & macros
                </summary>

                <div style="margin-top: 8px; display: flex; flex-direction: column; gap: 8px;">
                    <div class="meal-card__detail-panel">
                    <div style="font-weight: 600; font-size: 12px; margin-bottom: 4px;">Macros</div>
                    <div style="font-size: 11px; line-height: 1.5; opacity: 0.85;">
                        <div>Calories: {{ meal.macros?.calories ?? 0 }}</div>
                        <div>Protein: {{ meal.macros?.protein_g ?? 0 }} g</div>
                        <div>Carbs: {{ meal.macros?.carbs_g ?? 0 }} g</div>
                        <div>Fat: {{ meal.macros?.fat_g ?? 0 }} g</div>
                    </div>
                    </div>

                    <div class="meal-card__detail-panel">
                    <div style="font-weight: 600; font-size: 12px; margin-bottom: 4px;">Ingredients</div>
                    <ul style="margin: 0; padding-left: 16px; font-size: 11px;">
                        <li v-for="(ing, j) in meal.ingredients ?? []" :key="j" style="display:flex; align-items:center; gap:8px;">
                          <span style="display:flex; align-items:center; gap:8px;">
                            <strong>{{ ing.name }}</strong>

                            <span v-if="isBooster(ing)" class="booster-badge">
                              Adjustment
                            </span>
                          </span>

                          <span v-if="ing.grams != null" style="margin-left:auto; opacity:0.85;">
                            {{ ing.grams }} g
                          </span>
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

    <!-- Skeleton Meal Plan while loading (only if no output yet) -->
    <section v-else-if="nutritionLoading" class="ll-card">
      <div style="display:flex; justify-content:space-between; align-items:baseline; gap:10px; margin-bottom: 10px;">
        <div style="font-weight: 800;">Meal Plan</div>
        <div style="opacity: 0.7; font-size: 13px;">Preparing…</div>
      </div>

      <div class="ll-skel-meals">
        <div class="ll-skel-row" />
        <div class="ll-skel-row" />
        <div class="ll-skel-row" />
        <div class="ll-skel-row" />
        <div class="ll-skel-row" />
      </div>
    </section>


    <!-- Diff / Explanations -->
    <section class="ll-card">
      <NutritionDiff :explanations="nutritionExplanations" :version="nutritionSnapshot?.version ?? null" />
    </section>

    <!-- Raw JSON -->
    <section v-if="nutritionSnapshot" class="ll-card">
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
import { computed, onBeforeUnmount, ref, watch } from "vue";
import NutritionDiff from "../components/NutritionDiff.vue";
import LLLoadingPanel from "../components/LLLoadingPanel.vue";
import { useNutritionApi, type NutritionTargets, type MacroCalcResponse } from "../../services/nutrition";

const { generateNutrition, regenerateNutrition, macroCalc } = useNutritionApi();

const showDebug = ref(false)
const nutritionLoading = ref(false);
// --- premium loading UX (status text + elapsed time)
const nutritionStartedAtMs = ref<number | null>(null);
const nutritionElapsedSec = ref(0);
let nutritionTimer: number | null = null;

const nutritionElapsedSeconds = computed(() => nutritionElapsedSec.value);

const nutritionSteps = [
  "Selecting meals for each slot",
  "Enforcing diet + allergens (fail-closed)",
  "Repairing calories (slot-aware boosters)",
  "Snapshotting version + preparing diffs",
];

watch(nutritionLoading, (isLoading) => {
  if (isLoading) {
    nutritionStartedAtMs.value = Date.now();
    nutritionElapsedSec.value = 0;

    if (nutritionTimer != null) window.clearInterval(nutritionTimer);
    nutritionTimer = window.setInterval(() => {
      if (!nutritionStartedAtMs.value) return;
      nutritionElapsedSec.value = Math.floor((Date.now() - nutritionStartedAtMs.value) / 1000);
    }, 250);
  } else {
    if (nutritionTimer != null) window.clearInterval(nutritionTimer);
    nutritionTimer = null;
  }
});

onBeforeUnmount(() => {
  if (nutritionTimer != null) window.clearInterval(nutritionTimer);
});

const nutritionError = ref<string | null>(null);
const DEBUG_NUTRITION = false;

const nutritionSnapshot = ref<any | null>(null);
const nutritionOutput = ref<any | null>(null);
const nutritionExplanations = ref<string[] | null>(null);

const macroLoading = ref(false);
const macroError = ref<string | null>(null);
const macroResult = ref<MacroCalcResponse | null>(null);

type MacroSex = "male" | "female";
type MacroActivity = "sedentary" | "light" | "moderate" | "very" | "athlete";

const macroSex = ref<MacroSex>("male");
const macroAge = ref<number>(25);
const macroHeightFt = ref<number>(5);
const macroHeightIn = ref<number>(11);
const macroWeightLb = ref<number>(175);
const macroActivity = ref<MacroActivity>("moderate");
const copyStatusLabel = ref<string>("Copy targets");

// Clamp macro inputs to valid ranges
watch(macroHeightFt, (v) => {
  macroHeightFt.value = Math.max(0, Math.trunc(v ?? 0));
});
watch(macroHeightIn, (v) => {
  macroHeightIn.value = Math.max(0, Math.min(11, Math.trunc(v ?? 0)));
});
watch(macroWeightLb, (v) => {
  macroWeightLb.value = Math.max(1, Math.trunc(v ?? 1));
});

// Prefill plannerTargets from nutritionSnapshot if available
watch(nutritionSnapshot, (snapshot) => {
  if (snapshot?.targets) {
    plannerTargets.value = { ...snapshot.targets };
    // Backward compatibility: set goal/rate if available
    if (snapshot.goal) goal.value = snapshot.goal;
    if (snapshot.rate) rate.value = snapshot.rate;
  }
}, { immediate: true });

type NutritionGoal = "maintenance" | "cut" | "bulk";
type DietChoice =
  | "none"
  | "vegetarian"
  | "vegan"
  | "pescatarian";
  type RateChoice = "0.5" | "1" | "2";


// Deterministic defaults (unchanged from your current hardcoded values)
const defaultNutritionTargets: NutritionTargets = {
  maintenance: 2600,
  cut: { "0.5": 2400, "1": 2200, "2": 2000 },
  bulk: { "0.5": 2800, "1": 3000, "2": 3200 },
};

const plannerTargets = ref<NutritionTargets>({ ...defaultNutritionTargets });
const appliedTargets = computed(() => plannerTargets.value);


// UI state (fresh refresh resets state — expected)
const goal = ref<NutritionGoal>("maintenance");
const calories = computed(() => presetCaloriesFor(goal.value, rate.value));
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

const selectedCaloriesFromTargets = computed(() => {
  return presetCaloriesFor(goal.value, rate.value);
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

function inchesFromFtIn(ft: number, inches: number): number {
  const f = Number.isFinite(ft) ? ft : 0;
  const i = Number.isFinite(inches) ? inches : 0;
  return f * 12 + i;
}

function cmFromInches(totalIn: number): number {
  return totalIn * 2.54;
}

function kgFromLb(lb: number): number {
  return lb * 0.45359237;
}


function presetCaloriesFor(goal: NutritionGoal, r: RateChoice): number {
  const t = plannerTargets.value;

  if (goal === "maintenance") return t.maintenance;

  if (goal === "cut") {
    return t.cut[r] ?? t.cut["1"] ?? t.maintenance;
  }

  // bulk
  return t.bulk[r] ?? t.bulk["1"] ?? t.maintenance;
}




const allergies = computed<string[]>(() => {
  return allergiesText.value
    .split("\n")
    .map((s) => s.trim())
    .filter((s) => s.length > 0);
});

// Pure function: inputs -> request payload (no side effects)
function buildNutritionBaseRequest(inputs: {
  goal: NutritionGoal;
  rate: "0.5" | "1" | "2" | null; // ✅ add this
  calories: number;
  mealsPerDay: number | null; // <-- allow blank/infer
  allergies: string[];
  diet: DietChoice;
}) {
  const targets: NutritionTargets = {
    maintenance: plannerTargets.value.maintenance,
    cut: { ...plannerTargets.value.cut },
    bulk: { ...plannerTargets.value.bulk },
  };

  // ✅ Only update the selected goal + selected rate
  // Keep the rest of the table intact for snapshot/versioning.
  if (inputs.goal === "maintenance") {
    targets.maintenance = inputs.calories;
  } else if (inputs.goal === "cut") {
    const r = (inputs.rate ?? "1");
    targets.cut = { ...targets.cut, [r]: inputs.calories };
  } else if (inputs.goal === "bulk") {
    const r = (inputs.rate ?? "1");
    targets.bulk = { ...targets.bulk, [r]: inputs.calories };
  }

  const req: any = {
    targets,
    target_calories: inputs.calories,
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

function num(v: any): number {
  const n = typeof v === "string" ? parseFloat(v) : Number(v)
  return Number.isFinite(n) ? n : 0
}

function mealCalories(meal: any): number {
  if (!meal) return 0
  if (meal.calories != null) return num(meal.calories)
  if (meal.macros?.calories != null) return num(meal.macros.calories)
  return 0
}

function mealProtein(meal: any): number {
  if (!meal) return 0
  // common variants
  if (meal.protein_g != null) return num(meal.protein_g)
  if (meal.protein != null) return num(meal.protein)
  if (meal.macros?.protein_g != null) return num(meal.macros.protein_g)
  if (meal.macros?.protein != null) return num(meal.macros.protein)
  return 0
}

function mealCarbs(meal: any): number {
  if (!meal) return 0
  if (meal.carbs_g != null) return num(meal.carbs_g)
  if (meal.carbs != null) return num(meal.carbs)
  if (meal.macros?.carbs_g != null) return num(meal.macros.carbs_g)
  if (meal.macros?.carbs != null) return num(meal.macros.carbs)
  return 0
}

function mealFat(meal: any): number {
  if (!meal) return 0
  if (meal.fat_g != null) return num(meal.fat_g)
  if (meal.fat != null) return num(meal.fat)
  if (meal.macros?.fat_g != null) return num(meal.macros.fat_g)
  if (meal.macros?.fat != null) return num(meal.macros.fat)
  return 0
}

const acceptedMeals = computed<any[]>(() => {
  // Adjust these paths if your response shape differs
  // Most likely: data.output.accepted
  const out = (nutritionOutput.value as any)?.output?.accepted
  return Array.isArray(out) ? out : []
})

const dailyTotals = computed(() => {
  const meals = Array.isArray(nutritionOutput.value?.accepted) ? nutritionOutput.value.accepted : []

  const calories = meals.reduce((s: number, m: any) => s + mealCalories(m), 0)
  const protein = meals.reduce((s: number, m: any) => s + mealProtein(m), 0)
  const carbs = meals.reduce((s: number, m: any) => s + mealCarbs(m), 0)
  const fat = meals.reduce((s: number, m: any) => s + mealFat(m), 0)

  return {
    calories: Math.round(calories),
    protein: Math.round(protein * 10) / 10,
    carbs: Math.round(carbs * 10) / 10,
    fat: Math.round(fat * 10) / 10,
  }
})

const hasPlanTotals = computed(() => {
  return (
    dailyTotals.value.calories > 0 ||
    dailyTotals.value.protein > 0 ||
    dailyTotals.value.carbs > 0 ||
    dailyTotals.value.fat > 0
  )
})

function clamp(n: number, lo: number, hi: number): number {
  return Math.max(lo, Math.min(hi, n))
}

const macroAims = computed(() => {
  const calAim = Number(selectedCaloriesFromTargets.value) || 0
  if (calAim <= 0) {
    return { calories: null, protein: null, carbs: null, fat: null }
  }

  // weight_lb: prefer macroWeightLb input (what user typed), fallback to 175 if unset
  const weightLb = clamp(Number(macroWeightLb.value || 0) || 0, 50, 450)

  // Protein aim (0.8 g/lb)
  const proteinAim = Math.round(weightLb * 0.8)

  // Deterministic fat target: 30% of calories
  const fatCals = Math.round(calAim * 0.30)
  const fatAim = Math.round(fatCals / 9)

  // Carbs get the remainder (favor carbs)
  const proteinCals = proteinAim * 4
  const usedCals = proteinCals + fatAim * 9
  const remainingCals = Math.max(0, calAim - usedCals)
  const carbsAim = Math.round(remainingCals / 4)

  return {
    calories: Math.round(calAim),
    protein: proteinAim,
    carbs: carbsAim,
    fat: fatAim,
  }
})




function pretty(x: any) {
  return JSON.stringify(x, null, 2);
}

function isBooster(ing: any): boolean {
  const t = String(ing?.type || "").toLowerCase().trim();
  return t === "booster" || t === "adjustment";
}

function baseIngredientNames(meal: any): string[] {
  const ings = Array.isArray(meal?.ingredients) ? meal.ingredients : [];
  return ings
    .filter((i: any) => i && !isBooster(i))
    .map((i: any) => String(i.name || "").trim())
    .filter((s: string) => !!s);
}

function boosterIngredientNames(meal: any): string[] {
  const ings = Array.isArray(meal?.ingredients) ? meal.ingredients : [];
  // dedupe while preserving order
  const out: string[] = [];
  const seen = new Set<string>();
  for (const i of ings) {
    if (!i || !isBooster(i)) continue;
    const nm = String(i.name || "").trim();
    const key = nm.toLowerCase();
    if (!nm || seen.has(key)) continue;
    seen.add(key);
    out.push(nm);
  }
  return out;
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
    if (DEBUG_NUTRITION && seenGlobal.has(s)) {
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
      if (DEBUG_NUTRITION && seenSlot.has(s)) {
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

async function onCopyTargets() {
  try {
    const targets = plannerTargets.value;
    const selectedCal = presetCaloriesFor(goal.value, rate.value);
    const text = `Selected: ${selectedCal} cal (${goalLabel.value}${goal.value !== 'maintenance' ? ' @ ' + rate.value + ' lb/wk' : ''})\nMaintenance: ${targets.maintenance} cal\nCut: 0.5 lb/wk=${targets.cut["0.5"]} cal, 1 lb/wk=${targets.cut["1"]} cal, 2 lb/wk=${targets.cut["2"]} cal\nBulk: 0.5 lb/wk=${targets.bulk["0.5"]} cal, 1 lb/wk=${targets.bulk["1"]} cal, 2 lb/wk=${targets.bulk["2"]} cal`;
    await navigator.clipboard.writeText(text);
    copyStatusLabel.value = "Copied!";
    setTimeout(() => { copyStatusLabel.value = "Copy targets"; }, 1400);
  } catch (e) {
    copyStatusLabel.value = "Copy failed";
    setTimeout(() => { copyStatusLabel.value = "Copy targets"; }, 1400);
  }
}

async function onMacroCalc() {
  macroLoading.value = true;
  macroError.value = null;

  try {
    const totalIn = inchesFromFtIn(macroHeightFt.value, macroHeightIn.value);

    // ===== BLOCK 0 DEBUG: MACRO CALC (payload + conversions) =====
    const heightCmDebug = cmFromInches(totalIn);
    const weightKgDebug = kgFromLb(macroWeightLb.value);

    console.log("[BLOCK 0] Macro Calc — frontend inputs + converted payload", {
      sex: macroSex.value,
      age: macroAge.value,
      height_ft: macroHeightFt.value,
      height_in: macroHeightIn.value,
      total_inches: totalIn,
      height_cm: heightCmDebug,
      weight_lb: macroWeightLb.value,
      weight_kg: weightKgDebug,
      activity_level: macroActivity.value,
    });
    // ============================================================

    // Fail-closed frontend validation (keeps UI errors clean)
    if (totalIn <= 0) throw new Error("Height must be > 0.");
    if (!Number.isFinite(macroWeightLb.value) || macroWeightLb.value <= 0)
      throw new Error("Weight must be > 0.");

    const res = await macroCalc({
      sex: macroSex.value,
      age: macroAge.value,
      height_cm: heightCmDebug,
      weight_kg: weightKgDebug,
      activity_level: macroActivity.value,
    });

    if (!res.implemented) {
      throw new Error(res.message || "Macro calculator not implemented.");
    }

    macroResult.value = res;

    // Do NOT auto-apply. Just update preview calories to match computed targets
    // (stays deterministic; user still controls Apply)
    plannerTargets.value = { ...res.macros.targets };
  } catch (e: any) {
    macroError.value = e?.data?.detail ?? e?.message ?? String(e);
    macroResult.value = null;
  } finally {
    macroLoading.value = false;
  }
}


async function onApplyTargetsAndGenerate() {
  // Fail closed: must have a valid calc result
  if (!macroResult.value) {
    macroError.value = "Run Calculate first.";
    return;
  }
  macroError.value = null;

  // Apply the targets deterministically (plannerTargets drives snapshot + header display)
  plannerTargets.value = { ...macroResult.value.macros.targets };


  // Immediately generate (Option A)
  await onNutritionGenerate();
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
    nutritionSnapshot.value = null;
    nutritionOutput.value = null;
    nutritionExplanations.value = null;
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
    nutritionSnapshot.value = null;
    nutritionOutput.value = null;
    nutritionExplanations.value = null;
  } finally {
    nutritionLoading.value = false;
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;900&family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600&display=swap');

:global(html),
:global(body) {
  background: #090907;
  margin: 0;
}

:global(#__nuxt) {
  background: #090907;
  min-height: 100vh;
}

.nutrition-page {
  --amber: #7c3aed;
  --bg: #090907;
  --surface: #111110;
  --surface-2: #191917;
  --border: rgba(255, 255, 255, 0.07);
  --text: #f0ede6;
  --text-dim: rgba(240, 237, 230, 0.42);

  background-color: var(--bg);
  background-image:
    linear-gradient(rgba(124, 58, 237, 0.025) 1px, transparent 1px),
    linear-gradient(90deg, rgba(124, 58, 237, 0.025) 1px, transparent 1px);
  background-size: 44px 44px;
  color: var(--text);
  padding: 40px 48px;
  font-family: 'DM Sans', sans-serif;
  min-height: 100vh;
}

.nutrition-page > * {
  max-width: 1400px;
  margin-left: auto;
  margin-right: auto;
}

/* Page heading override */
.nutrition-page > h1 {
  font-family: 'Syne', sans-serif !important;
  font-size: 32px !important;
  font-weight: 900 !important;
  letter-spacing: -0.03em !important;
  color: var(--text) !important;
}

.nutrition-page > p {
  font-family: 'DM Mono', monospace !important;
  font-size: 12px !important;
  color: var(--text-dim) !important;
  opacity: 1 !important;
  letter-spacing: 0.02em !important;
}

/* === CRITICAL: Override all white-background inline-styled form elements === */
.nutrition-page input,
.nutrition-page select,
.nutrition-page textarea {
  background: var(--surface-2) !important;
  border: 1px solid var(--border) !important;
  color: var(--text) !important;
  border-radius: 3px !important;
  font-family: 'DM Sans', sans-serif !important;
}

.nutrition-page input:focus,
.nutrition-page select:focus,
.nutrition-page textarea:focus {
  border-color: var(--amber) !important;
  outline: none !important;
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.07) !important;
}

.nutrition-page input:disabled,
.nutrition-page select:disabled,
.nutrition-page textarea:disabled {
  opacity: 0.4 !important;
  cursor: not-allowed !important;
}

.nutrition-page input::placeholder,
.nutrition-page textarea::placeholder {
  color: rgba(240, 237, 230, 0.25) !important;
}

.nutrition-page option {
  background: #191917;
  color: #f0ede6;
}

/* Card wrapper */
.ll-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-left: 3px solid rgba(124, 58, 237, 0.35);
  border-radius: 4px;
  padding: 18px 20px;
  margin-bottom: 14px;
}

.ll-card-muted {
  background: #0f0f0d;
  border-left-color: rgba(124, 58, 237, 0.12);
}

/* Card section headings with inline font-weight: 800 */
.ll-card > div[style*="font-weight: 800"],
.ll-card > div[style*="font-weight:800"] {
  font-family: 'DM Mono', monospace !important;
  font-size: 11px !important;
  font-weight: 500 !important;
  letter-spacing: 0.1em !important;
  text-transform: uppercase !important;
  color: var(--text-dim) !important;
  margin-bottom: 14px !important;
}

/* Inline span labels (font-size: 12px; opacity: 0.75) */
.nutrition-page span[style*="opacity: 0.75"],
.nutrition-page span[style*="opacity:0.75"] {
  font-family: 'DM Mono', monospace !important;
  font-size: 10px !important;
  letter-spacing: 0.08em !important;
  text-transform: uppercase !important;
  opacity: 1 !important;
  color: var(--text-dim) !important;
}

/* Maintenance link */
.ll-card a[href] {
  color: var(--amber) !important;
  opacity: 0.8;
  transition: opacity 0.15s;
}

.ll-card a[href]:hover {
  opacity: 1;
}

/* Error text inline style */
.nutrition-page div[style*="color:#b00020"],
.nutrition-page div[style*="color: #b00020"] {
  color: #f87171 !important;
  font-family: 'DM Mono', monospace !important;
  font-size: 12px !important;
  padding: 10px 12px !important;
  background: rgba(248, 113, 113, 0.07) !important;
  border-left: 2px solid #f87171 !important;
  border-radius: 0 3px 3px 0 !important;
  margin-top: 12px !important;
}

/* Meal cards */
.meal-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 14px;
  transition: border-color 0.15s, transform 0.12s;
}

.meal-card:hover {
  border-color: rgba(124, 58, 237, 0.35);
  transform: translateY(-1px);
}

.booster-badge {
  font-size: 10px;
  font-weight: 500;
  font-family: 'DM Mono', monospace;
  padding: 2px 7px;
  border-radius: 2px;
  border: 1px solid rgba(124, 58, 237, 0.3);
  background: rgba(124, 58, 237, 0.06);
  color: rgba(124, 58, 237, 0.8);
  letter-spacing: 0.04em;
}

.meal-card__detail-panel {
  background: var(--surface-2);
  border-radius: 3px;
  padding: 10px;
}

/* === Buttons using buttonStyle() — override via attribute selector === */
.nutrition-page button[style] {
  background: var(--amber) !important;
  border: none !important;
  border-radius: 3px !important;
  color: #ffffff !important;
  font-family: 'DM Mono', monospace !important;
  font-size: 11px !important;
  font-weight: 500 !important;
  letter-spacing: 0.07em !important;
  text-transform: uppercase !important;
  padding: 9px 16px !important;
  transition: background 0.15s, opacity 0.15s !important;
}

.nutrition-page button[style]:hover:not(:disabled) {
  background: #6d28d9 !important;
}

.nutrition-page button[style]:disabled {
  background: var(--amber) !important;
  opacity: 0.4 !important;
  cursor: not-allowed !important;
}

/* Totals bar */
.totals-bar {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  padding: 12px 16px;
  border: 1px solid rgba(124, 58, 237, 0.12);
  background: rgba(124, 58, 237, 0.03);
  border-radius: 4px;
  margin: 10px 0 14px;
}

.totals-title {
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--text-dim);
  margin-bottom: 6px;
}

.totals-sub {
  font-size: 13px;
  color: var(--text);
  line-height: 1.7;
}

.pill {
  display: inline-flex;
  align-items: center;
  padding: 1px 7px;
  border-radius: 2px;
  border: 1px solid rgba(124, 58, 237, 0.25);
  background: rgba(124, 58, 237, 0.06);
  font-weight: 700;
  font-family: 'DM Mono', monospace;
  font-size: 12px;
  letter-spacing: 0.02em;
  margin: 0 2px;
}

.debug-toggle {
  appearance: none;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.03);
  color: rgba(240, 237, 230, 0.45);
  padding: 7px 12px;
  border-radius: 3px;
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
  white-space: nowrap;
  flex-shrink: 0;
}

.debug-toggle:hover {
  background: rgba(255, 255, 255, 0.06);
  color: rgba(240, 237, 230, 0.85);
}

/* Details/summary global */
details {
  border: 1px solid var(--border);
  border-radius: 4px;
  padding: 10px 12px;
  background: var(--surface-2);
}

details summary {
  cursor: pointer;
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  letter-spacing: 0.05em;
  color: var(--text-dim);
}

@media (max-width: 900px) {
  .nutrition-page {
    padding: 24px 18px;
  }
}

/* === Loading skeleton === */
.ll-skel-meals {
  display: grid;
  gap: 10px;
}

.ll-skel-row {
  height: 54px;
  border-radius: 4px;
  border: 1px solid rgba(124, 58, 237, 0.06);
  background: linear-gradient(
    90deg,
    rgba(124, 58, 237, 0.03),
    rgba(124, 58, 237, 0.07),
    rgba(124, 58, 237, 0.03)
  );
  background-size: 200% 100%;
  animation: ll-shimmer 1.4s ease-in-out infinite;
}

@keyframes ll-shimmer {
  0% { background-position: 0% 0; }
  100% { background-position: 200% 0; }
}

</style>
