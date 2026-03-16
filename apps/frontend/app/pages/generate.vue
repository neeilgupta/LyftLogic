<template>
  <main class="generate-page">
    <div class="page-header">
      <h1 class="page-title">Generate Plan</h1>
      <p class="page-sub">
        Create a training program. Rules engine only — deterministic, no randomness.
      </p>
    </div>

    <form @submit.prevent="onSubmit" class="generate-form">
      <section class="ll-card">
        <div class="card-heading">Training Parameters</div>

        <div class="form-grid">
          <label class="form-field">
            <span class="form-label">Goal</span>
            <select v-model="form.goal" class="form-input form-select" :disabled="loading">
              <option value="hypertrophy">Hypertrophy</option>
              <option value="strength">Strength</option>
              <option value="fat_loss">Fat loss</option>
            </select>
          </label>

          <label class="form-field">
            <span class="form-label">Experience</span>
            <select v-model="form.experience" class="form-input form-select" :disabled="loading">
              <option value="beginner">Beginner</option>
              <option value="intermediate">Intermediate</option>
              <option value="advanced">Advanced</option>
            </select>
          </label>

          <label class="form-field">
            <span class="form-label">Days per week</span>
            <input v-model.number="form.days_per_week" type="number" min="1" max="6" class="form-input" :disabled="loading" />
          </label>

          <label class="form-field">
            <span class="form-label">Session minutes</span>
            <input v-model.number="form.session_minutes" type="number" min="20" max="120" class="form-input" :disabled="loading" />
          </label>

          <label class="form-field full-width">
            <span class="form-label">Equipment</span>
            <select v-model="form.equipment" class="form-input form-select" :disabled="loading">
              <option value="full_gym">Full gym</option>
              <option value="dumbbells">Dumbbells</option>
              <option value="bodyweight">Bodyweight</option>
            </select>
          </label>
        </div>
      </section>

      <section class="ll-card">
        <label class="form-field">
          <span class="form-label">Notes / Preferences</span>
          <textarea
            v-model="form.constraints"
            rows="6"
            class="form-input"
            :disabled="loading"
            placeholder="Examples:
- No dumbbells
- No barbells
- Prefer machines
- Extra glute focus
- Avoid shoulders (pain)"
          />
        </label>
      </section>

      <button :disabled="loading" type="submit" class="generate-button">
        <span>{{ loading ? "Generating…" : "Generate plan" }}</span>
        <span v-if="loading" class="btn-spinner"></span>
      </button>

      <LLLoadingPanel
        v-if="loading"
        title="Generating your training plan"
        subtitle="Deterministic rules engine — same inputs always produce the same output."
        :elapsed="elapsedSeconds"
        :steps="trainingSteps"
        hint="This can take ~15–20 seconds on cold start. No randomness, no AI source-of-truth."
      />

      <div v-if="error" class="error-message">{{ error }}</div>
      <PlanViewer v-if="result?.output" :plan="result.output" />
    </form>
  </main>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, ref, watch } from "vue";
import { useRouter } from "vue-router";
import { usePlans } from "../../composables/usePlans";
import { useAuth } from "../../composables/useAuth";
import PlanViewer from "../../components/PlanViewer.vue";
import LLLoadingPanel from "../components/LLLoadingPanel.vue";

const router = useRouter();
const { generatePlan } = usePlans();
const { me } = useAuth();

const loading = ref(false);
const error = ref<string | null>(null);
const result = ref<any>(null);

const form = ref({
  goal: "hypertrophy",
  experience: "intermediate",
  days_per_week: 4,
  session_minutes: 60,
  equipment: "full_gym",
  constraints: "",
});

// --- premium loading UX (status text + elapsed time)
const startedAtMs = ref<number | null>(null);
const elapsedSec = ref(0);
let timer: number | null = null;

const elapsedSeconds = computed(() => elapsedSec.value);

const trainingSteps = [
  "Locking inputs + split structure",
  "Selecting exercises by equipment + goal",
  "Building sets/reps + progression notes",
  "Snapshotting version + preparing diffs",
];

watch(loading, (isLoading) => {
  if (isLoading) {
    startedAtMs.value = Date.now();
    elapsedSec.value = 0;

    if (timer != null) window.clearInterval(timer);
    timer = window.setInterval(() => {
      if (!startedAtMs.value) return;
      elapsedSec.value = Math.floor((Date.now() - startedAtMs.value) / 1000);
    }, 250);
  } else {
    if (timer != null) window.clearInterval(timer);
    timer = null;
  }
});

onBeforeUnmount(() => {
  if (timer != null) window.clearInterval(timer);
});

async function onSubmit() {
  loading.value = true;
  error.value = null;
  result.value = null;

  try {
    const res: any = await generatePlan(form.value);
    result.value = res;

    const user = await me();
    const planId = res?.plan_id;
    if (user && planId) {
      router.push(`/plans/${planId}`);
    }
  } catch (e: any) {
    error.value =
      e?.data?.detail ??
      e?.data?.message ??
      e?.message ??
      JSON.stringify(e, null, 2);
  } finally {
    loading.value = false;
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

.generate-page {
  background-color: #090907;
  background-image:
    linear-gradient(rgba(124, 58, 237, 0.025) 1px, transparent 1px),
    linear-gradient(90deg, rgba(124, 58, 237, 0.025) 1px, transparent 1px);
  background-size: 44px 44px;
  color: #f0ede6;
  padding: 40px 48px;
  font-family: 'DM Sans', sans-serif;
  min-height: 100vh;
}

.generate-page > * {
  max-width: 860px;
  margin-left: auto;
  margin-right: auto;
}

/* Page header */
.page-header {
  margin-bottom: 28px;
}

.page-title {
  font-family: 'Syne', sans-serif;
  font-size: 32px;
  font-weight: 900;
  letter-spacing: -0.03em;
  margin: 0 0 6px;
  color: #f0ede6;
}

.page-sub {
  font-family: 'DM Mono', monospace;
  font-size: 12px;
  color: rgba(240, 237, 230, 0.4);
  margin: 0;
  letter-spacing: 0.02em;
}

/* Form */
.generate-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.ll-card {
  background: #111110;
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-left: 3px solid rgba(124, 58, 237, 0.4);
  border-radius: 4px;
  padding: 22px 20px;
}

.card-heading {
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(240, 237, 230, 0.4);
  margin-bottom: 18px;
}

/* Form grid */
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-field.full-width {
  grid-column: span 2;
}

.form-label {
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(240, 237, 230, 0.4);
}

.form-input {
  padding: 10px 14px;
  border-radius: 3px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: #191917;
  color: #f0ede6;
  font-size: 14px;
  font-family: 'DM Sans', sans-serif;
  transition: border-color 0.15s, box-shadow 0.15s;
  box-sizing: border-box;
  width: 100%;
}

.form-input:focus {
  outline: none;
  border-color: #7c3aed;
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.07);
}

.form-input::placeholder {
  color: rgba(240, 237, 230, 0.25);
  font-size: 13px;
}

.form-input:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.form-select {
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  cursor: pointer;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath d='M1 1l5 5 5-5' stroke='rgba(240,237,230,0.35)' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round' fill='none'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 14px center;
  padding-right: 38px;
}

.form-select option {
  background: #191917;
  color: #f0ede6;
}

textarea.form-input {
  resize: vertical;
  line-height: 1.55;
  min-height: 120px;
}

/* Generate button */
.generate-button {
  background: #7c3aed;
  border: none;
  border-radius: 3px;
  color: #ffffff;
  font-family: 'DM Mono', monospace;
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  padding: 13px 28px;
  cursor: pointer;
  transition: background 0.15s, transform 0.1s, opacity 0.15s;
  width: fit-content;
  display: flex;
  align-items: center;
  gap: 10px;
}

.generate-button:hover:not(:disabled) {
  background: #6d28d9;
  transform: translateY(-1px);
}

.generate-button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.btn-spinner {
  width: 14px;
  height: 14px;
  border: 1.5px solid rgba(255, 255, 255, 0.3);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Makes loading panel feel like part of the form flow */
.generate-form :deep(.ll-loading) {
  margin-top: 6px;
}

.error-message {
  background: rgba(248, 113, 113, 0.07);
  border-left: 2px solid #f87171;
  border-radius: 0 3px 3px 0;
  color: #fca5a5;
  padding: 12px 16px;
  font-family: 'DM Mono', monospace;
  font-size: 12px;
  line-height: 1.5;
}

@media (max-width: 900px) {
  .generate-page {
    padding: 24px 18px;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .form-field.full-width {
    grid-column: span 1;
  }
}
</style>
