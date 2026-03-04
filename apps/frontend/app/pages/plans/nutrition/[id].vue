<script setup lang="ts">
import { ref, onMounted, computed } from "vue";
import { useRoute } from "vue-router";
import { usePlans } from "../../../../composables/usePlans";

const route = useRoute();
const { getNutritionPlan } = usePlans();

const plan = ref<any>(null);
const loading = ref(true);
const error = ref<string | null>(null);

const input = computed(() => {
  try { return plan.value ? JSON.parse(plan.value.input_json) : null; } catch { return null; }
});

const output = computed(() => {
  try { return plan.value ? JSON.parse(plan.value.output_json) : null; } catch { return null; }
});

// Group accepted meals by slot order
const SLOT_ORDER = ["breakfast", "snack 1", "snack", "lunch", "snack 2", "dinner"];
const mealsBySlot = computed(() => {
  const accepted: any[] = output.value?.accepted ?? [];
  const groups: Record<string, any[]> = {};
  for (const meal of accepted) {
    const slot = (meal.slot || meal.meal_type || "other").toLowerCase();
    if (!groups[slot]) groups[slot] = [];
    groups[slot].push(meal);
  }
  // Return in slot order, then any remaining keys
  const ordered: { slot: string; meals: any[] }[] = [];
  const seen = new Set<string>();
  for (const s of SLOT_ORDER) {
    if (groups[s]) { ordered.push({ slot: s, meals: groups[s] }); seen.add(s); }
  }
  for (const [slot, meals] of Object.entries(groups)) {
    if (!seen.has(slot)) ordered.push({ slot, meals });
  }
  return ordered;
});

const totals = computed(() => {
  const accepted: any[] = output.value?.accepted ?? [];
  return accepted.reduce(
    (acc, meal) => {
      const m = meal.macros ?? meal;
      acc.calories += Number(m.calories ?? 0);
      acc.protein  += Number(m.protein  ?? 0);
      acc.carbs    += Number(m.carbs    ?? 0);
      acc.fat      += Number(m.fat ?? m.fats ?? 0);
      return acc;
    },
    { calories: 0, protein: 0, carbs: 0, fat: 0 }
  );
});

function slotLabel(slot: string) {
  return slot.charAt(0).toUpperCase() + slot.slice(1);
}

function mealCalories(meal: any): number {
  return Number(meal.macros?.calories ?? meal.calories ?? 0);
}

onMounted(async () => {
  try {
    plan.value = await getNutritionPlan(route.params.id as string);
  } catch (e: any) {
    error.value = e?.data?.detail ?? e?.message ?? "Failed to load plan.";
  } finally {
    loading.value = false;
  }
});
</script>

<template>
  <div class="page">
    <div class="breadcrumb">
      <NuxtLink to="/plans" class="back-link">← Back to Plans</NuxtLink>
    </div>

    <div v-if="loading" class="muted">Loading…</div>
    <div v-else-if="error" class="error">{{ error }}</div>

    <template v-else-if="plan">
      <!-- Header -->
      <header class="hero">
        <div>
          <p class="kicker">Nutrition Plan</p>
          <h1>{{ plan.title }}</h1>
          <p class="sub">Saved {{ plan.created_at }}</p>
        </div>
      </header>

      <!-- Constraints summary -->
      <section class="ll-card" v-if="input">
        <h2 class="section-title">Plan Details</h2>
        <div class="detail-grid">
          <div class="detail-item">
            <span class="detail-label">Target</span>
            <span class="detail-value">{{ input.target_calories ?? "—" }} kcal</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Diet</span>
            <span class="detail-value">{{ input.diet || "None" }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Allergies</span>
            <span class="detail-value">{{ input.allergies?.join(", ") || "None" }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Meals</span>
            <span class="detail-value">{{ output?.accepted?.length ?? 0 }} accepted</span>
          </div>
        </div>
      </section>

      <!-- Macro totals -->
      <section class="ll-card" v-if="output">
        <h2 class="section-title">Total Macros</h2>
        <div class="macro-row">
          <div class="macro-chip">
            <span class="macro-val">{{ Math.round(totals.calories) }}</span>
            <span class="macro-label">kcal</span>
          </div>
          <div class="macro-chip">
            <span class="macro-val">{{ Math.round(totals.protein) }}g</span>
            <span class="macro-label">protein</span>
          </div>
          <div class="macro-chip">
            <span class="macro-val">{{ Math.round(totals.carbs) }}g</span>
            <span class="macro-label">carbs</span>
          </div>
          <div class="macro-chip">
            <span class="macro-val">{{ Math.round(totals.fat) }}g</span>
            <span class="macro-label">fat</span>
          </div>
        </div>
      </section>

      <!-- Meals by slot -->
      <section class="ll-card" v-if="mealsBySlot.length">
        <h2 class="section-title">Meals</h2>
        <div class="slot-list">
          <div v-for="group in mealsBySlot" :key="group.slot" class="slot-group">
            <p class="slot-label">{{ slotLabel(group.slot) }}</p>
            <div v-for="meal in group.meals" :key="meal.key ?? meal.name" class="meal-row">
              <span class="meal-name">{{ meal.name }}</span>
              <span class="meal-kcal">{{ mealCalories(meal) }} kcal</span>
            </div>
          </div>
        </div>
      </section>
    </template>
  </div>
</template>

<style scoped>
.page {
  padding: 28px 20px 80px;
  color: #e5e7eb;
  font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
  background: radial-gradient(circle at top left, #2a1658 0%, #0b0b12 45%);
  min-height: 100vh;
}

.breadcrumb {
  margin-bottom: 16px;
}

.back-link {
  color: rgba(167, 139, 250, 1);
  text-decoration: none;
  font-weight: 700;
  font-size: 14px;
}

.back-link:hover { text-decoration: underline; }

.hero {
  margin-bottom: 18px;
}

.kicker {
  text-transform: uppercase;
  letter-spacing: 0.2em;
  font-size: 11px;
  opacity: 0.7;
  margin: 0 0 6px;
}

h1 {
  font-size: 28px;
  margin: 0 0 6px;
  font-weight: 900;
}

.sub {
  margin: 0;
  opacity: 0.6;
  font-size: 13px;
}

.ll-card {
  background: rgba(16, 10, 32, 0.8);
  border: 1px solid rgba(124, 58, 237, 0.25);
  border-radius: 14px;
  padding: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.35);
  margin-bottom: 16px;
}

.section-title {
  font-size: 14px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  opacity: 0.6;
  margin: 0 0 14px;
}

/* Detail grid */
.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 12px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  opacity: 0.55;
}

.detail-value {
  font-size: 15px;
  font-weight: 700;
}

/* Macro totals */
.macro-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.macro-chip {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  background: rgba(124, 58, 237, 0.12);
  border: 1px solid rgba(124, 58, 237, 0.25);
  border-radius: 10px;
  padding: 10px 18px;
  min-width: 72px;
}

.macro-val {
  font-size: 18px;
  font-weight: 900;
  color: rgba(167, 139, 250, 1);
}

.macro-label {
  font-size: 11px;
  opacity: 0.6;
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

/* Slots */
.slot-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.slot-group {}

.slot-label {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  opacity: 0.55;
  margin: 0 0 8px;
}

.meal-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  border-radius: 10px;
  background: rgba(20, 12, 40, 0.8);
  border: 1px solid rgba(124, 58, 237, 0.15);
  margin-bottom: 6px;
}

.meal-name {
  font-weight: 600;
  font-size: 14px;
}

.meal-kcal {
  font-size: 13px;
  opacity: 0.65;
}

.muted { opacity: 0.7; }
.error { color: #fca5a5; }
</style>
