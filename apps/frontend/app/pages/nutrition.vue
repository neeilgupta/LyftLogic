<template>
  <main style="padding: 20px; font-family: system-ui; max-width: 1200px; margin: 0 auto;">
    <h1 style="margin: 0 0 10px;">Nutrition</h1>
    <p style="margin: 0 0 18px; opacity: 0.8;">
      Generate and iterate meal plans independently of training.
    </p>

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
        <div style="font-weight: 800;">Controls</div>
        <div v-if="nutritionSnapshot" style="opacity: 0.7; font-size: 13px;">
          v{{ nutritionSnapshot.version }}
        </div>
      </div>

      <div style="display:flex; gap:10px; flex-wrap: wrap;">
        <button
          :disabled="nutritionLoading"
          @click="onNutritionGenerate"
          style="padding: 8px 12px; border-radius: 10px; border: 1px solid #ddd; background: white; cursor: pointer;"
        >
          {{ nutritionLoading ? "Working…" : "Generate nutrition" }}
        </button>

        <button
          :disabled="!nutritionSnapshot || nutritionLoading"
          @click="onNutritionRegenerate"
          style="padding: 8px 12px; border-radius: 10px; border: 1px solid #ddd; background: white; cursor: pointer;"
        >
          {{ nutritionLoading ? "Working…" : "Regenerate (diff)" }}
        </button>
      </div>

      <div v-if="nutritionError" style="color:#b00020; font-size: 13px; margin-top: 10px;">
        {{ nutritionError }}
      </div>
    </section>

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
import { ref } from "vue";
import NutritionDiff from "../components/NutritionDiff.vue";
import { useNutritionApi, type NutritionTargets } from "../../services/nutrition";

const { generateNutrition, regenerateNutrition } = useNutritionApi();

const nutritionLoading = ref(false);
const nutritionError = ref<string | null>(null);

const nutritionSnapshot = ref<any | null>(null);
const nutritionOutput = ref<any | null>(null);
const nutritionExplanations = ref<string[] | null>(null);

// You can swap these to real user inputs later.
// Keeping deterministic defaults for now.
const defaultNutritionTargets: NutritionTargets = {
  maintenance: 2600,
  cut: { "0.5": 2400, "1": 2200, "2": 2000 },
  bulk: { "0.5": 2800, "1": 3000, "2": 3200 },
};

function buildNutritionBaseRequest() {
  return {
    targets: defaultNutritionTargets,
    diet: null,
    allergies: [],
    meals_needed: 4,
    max_attempts: 10,
    batch_size: 6,
  };
}

function pretty(x: any) {
  return JSON.stringify(x, null, 2);
}

async function onNutritionGenerate() {
  nutritionLoading.value = true;
  nutritionError.value = null;

  try {
    const base = buildNutritionBaseRequest();
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
    const base = buildNutritionBaseRequest();
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
