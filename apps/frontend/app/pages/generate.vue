<template>
  <div style="padding: 20px; font-family: system-ui; max-width: 720px;">
    <h1>Generate Plan</h1>

    <form @submit.prevent="onSubmit" style="display: grid; gap: 12px; margin-top: 16px;">
      <label>
        Goal
        <select v-model="form.goal">
          <option value="hypertrophy">hypertrophy</option>
          <option value="strength">strength</option>
          <option value="fat_loss">fat_loss</option>
        </select>
      </label>

      <label>
        Experience
        <select v-model="form.experience">
          <option value="beginner">beginner</option>
          <option value="intermediate">intermediate</option>
          <option value="advanced">advanced</option>
        </select>
      </label>

      <label>
        Days per week
        <input v-model.number="form.days_per_week" type="number" min="1" max="7" />
      </label>

      <label>
        Session minutes
        <input v-model.number="form.session_minutes" type="number" min="20" max="180" />
      </label>

      <label>
        Equipment
        <select v-model="form.equipment">
          <option value="full_gym">full_gym</option>
          <option value="dumbbells">dumbbells</option>
          <option value="home_gym">home_gym</option>
          <option value="bodyweight">bodyweight</option>
        </select>
      </label>

      <label>
  User Notes / Preferences
  <textarea
    v-model="form.constraints"
    rows="4"
    placeholder="Examples:
- No dumbbells
- No barbells
- Prefer machines
- Extra glute focus
- Avoid shoulders (pain)"
  />
</label>


      <button :disabled="loading" type="submit" style="padding: 10px 14px; width: fit-content;">
        {{ loading ? "Generating..." : "Generate plan" }}
      </button>

      <p v-if="error" style="color: red;">{{ error }}</p>

      <pre v-if="result" style="white-space: pre-wrap;">{{ result }}</pre>
    </form>
  </div>
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
