<template>
  <main class="generate-page">
    <h1 style="margin: 0 0 10px; font-size: 32px; font-weight: 900; letter-spacing: -0.02em;">Generate Plan</h1>
    <p style="margin: 0 0 24px; opacity: 0.8; font-size: 15px;">
      Create a personalized training program tailored to your goals and experience.
    </p>

    <form @submit.prevent="onSubmit" class="generate-form">
      <section class="ll-card">
        <div style="font-weight: 800; margin-bottom: 12px; font-size: 16px;">Training Parameters</div>
        
        <div class="form-grid">
          <label class="form-field">
            <span class="form-label">Goal</span>
            <select v-model="form.goal" class="form-input">
              <option value="hypertrophy">hypertrophy</option>
              <option value="strength">strength</option>
              <option value="fat_loss">fat_loss</option>
            </select>
          </label>

          <label class="form-field">
            <span class="form-label">Experience</span>
            <select v-model="form.experience" class="form-input">
              <option value="beginner">beginner</option>
              <option value="intermediate">intermediate</option>
              <option value="advanced">advanced</option>
            </select>
          </label>

          <label class="form-field">
            <span class="form-label">Days per week</span>
            <input v-model.number="form.days_per_week" type="number" min="1" max="7" class="form-input" />
          </label>

          <label class="form-field">
            <span class="form-label">Session minutes</span>
            <input v-model.number="form.session_minutes" type="number" min="20" max="180" class="form-input" />
          </label>

          <label class="form-field full-width">
            <span class="form-label">Equipment</span>
            <select v-model="form.equipment" class="form-input">
              <option value="full_gym">full_gym</option>
              <option value="dumbbells">dumbbells</option>
              <option value="home_gym">home_gym</option>
              <option value="bodyweight">bodyweight</option>
            </select>
          </label>
        </div>
      </section>

      <section class="ll-card">
        <label class="form-field">
          <span class="form-label">User Notes / Preferences</span>
          <textarea
            v-model="form.constraints"
            rows="6"
            class="form-input"
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
        {{ loading ? "Generating..." : "Generate plan" }}
      </button>

      <div v-if="error" class="error-message">{{ error }}</div>
      <pre v-if="result" class="result-output">{{ result }}</pre>
    </form>
  </main>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { usePlans } from "../../composables/usePlans";

const router = useRouter();
const { generatePlan } = usePlans();

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

async function onSubmit() {
  loading.value = true;
  error.value = null;
  result.value = null;

  try {
    const res = await generatePlan(form.value);
    result.value = res;
    // ✅ route to details page once we create it
    router.push(`/plans/${res.id}`);
  } catch (e: any) {
    console.log(e);
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
/* Make the dark theme cover the entire app page */
:global(html),
:global(body) {
  background: #0b0f19;
  margin: 0;
}

:global(#__nuxt) {
  background: #0b0f19;
  min-height: 100vh;
}

.generate-page {
  --accent: #7c3aed;
  --accent-dark: #6d28d9;
  --ink: #f8fafc;
  --muted: #a1a1aa;
  --page: #0b0f19;
  --surface: #111827;
  --surface-2: #0f172a;
  --border: rgba(255,255,255,0.10);
  --shadow: 0 10px 30px rgba(0,0,0,0.35);

  background: var(--page);
  color: var(--ink);
  padding: 32px 48px;
  font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
  max-width: none;
  margin: 0;
  min-height: 100vh;
}

.generate-page > * {
  max-width: 900px;
  margin-left: auto;
  margin-right: auto;
}

.generate-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.ll-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 20px;
  box-shadow: var(--shadow);
}

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
  font-size: 13px;
  font-weight: 600;
  opacity: 0.85;
  letter-spacing: -0.01em;
}

.form-input {
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: var(--surface-2);
  color: var(--ink);
  font-size: 14px;
  font-family: inherit;
  transition: border-color 140ms ease, box-shadow 140ms ease;
}

.form-input:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.15);
}

.form-input::placeholder {
  color: rgba(255, 255, 255, 0.35);
}

textarea.form-input {
  resize: vertical;
  line-height: 1.5;
}

.generate-button {
  background: var(--accent);
  border: 1px solid var(--accent);
  color: #fff;
  font-weight: 700;
  font-size: 15px;
  padding: 12px 24px;
  border-radius: 10px;
  cursor: pointer;
  transition: background 140ms ease, box-shadow 140ms ease, opacity 140ms ease;
  width: fit-content;
}

.generate-button:hover:not(:disabled) {
  background: var(--accent-dark);
  box-shadow: 0 4px 12px rgba(124, 58, 237, 0.4);
}

.generate-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error-message {
  background: rgba(220, 38, 38, 0.15);
  border: 1px solid rgba(220, 38, 38, 0.3);
  color: #fca5a5;
  padding: 12px 16px;
  border-radius: 10px;
  font-size: 14px;
}

.result-output {
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 10px;
  padding: 16px;
  white-space: pre-wrap;
  font-size: 13px;
  color: var(--ink);
  opacity: 0.9;
  overflow-x: auto;
}

@media (max-width: 900px) {
  .generate-page {
    padding: 20px 16px;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .form-field.full-width {
    grid-column: span 1;
  }
}
</style>