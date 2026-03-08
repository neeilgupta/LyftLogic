<template>
  <div class="page">
    <header class="hero">
      <div>
        <p class="kicker">LyftLogic</p>
        <h1>Plans</h1>
        <p class="sub">Sign in to see your saved plans.</p>
      </div>
    </header>

    <section class="ll-card">
      <div class="auth-row">
        <div>
          <p class="label">Account</p>
          <p v-if="user" class="status">Logged in as {{ user.email }}</p>
          <p v-else class="status muted">Not logged in</p>
        </div>

        <div class="auth-actions">
          <!-- Step 1: enter email -->
          <template v-if="!user && authStep === 'idle'">
            <input
              v-model="email"
              class="input"
              type="email"
              placeholder="you@example.com"
              :disabled="authLoading"
            />
            <button class="btn" @click="onRequestCode" :disabled="authLoading || !email.trim()">
              {{ authLoading ? "Sending..." : "Send Code" }}
            </button>
          </template>

          <!-- Step 2: enter OTP code -->
          <template v-else-if="!user && authStep === 'code_sent'">
            <input
              v-model="code"
              class="input"
              type="text"
              inputmode="numeric"
              placeholder="6-digit code"
              maxlength="6"
              :disabled="authLoading"
            />
            <button class="btn" @click="onVerifyCode" :disabled="authLoading || code.trim().length < 6">
              {{ authLoading ? "Verifying..." : "Verify" }}
            </button>
            <button class="btn ghost" @click="authStep = 'idle'" :disabled="authLoading">
              Back
            </button>
          </template>

          <!-- Logged in -->
          <button v-if="user" class="btn ghost" @click="onLogout" :disabled="authLoading">
            Logout
          </button>
        </div>
      </div>

      <p v-if="authError" class="error">{{ authError }}</p>
    </section>

    <section class="ll-card">
      <div class="section-head">
        <h2>Workout Plans</h2>
        <button class="btn ghost" @click="loadMine" :disabled="plansLoading || !user">
          {{ plansLoading ? "Loading..." : "Refresh" }}
        </button>
      </div>

      <p v-if="plansError" class="error">{{ plansError }}</p>
      <p v-if="plansLoading && user" class="muted">Loading your plans…</p>
      <p v-if="!plansLoading && user && plans.length === 0" class="empty">
        No workout plans yet. Generate one and it will appear here.
      </p>
      <p v-if="!user" class="muted">Log in to see your plans.</p>

      <div v-if="plans.length" class="plan-list">
        <div v-for="p in plans" :key="p.plan_id" class="plan-row-wrap">
          <NuxtLink v-if="editingId !== `w-${p.plan_id}`" class="plan-row" :to="`/plans/${p.plan_id}`">
            <div>
              <p class="plan-title">{{ p.title || "Untitled plan" }}</p>
              <p class="plan-meta">Plan #{{ p.plan_id }} • {{ p.created_at }}</p>
            </div>
            <span class="chev">→</span>
          </NuxtLink>
          <div v-else class="plan-row editing">
            <input
              v-model="editingTitle"
              class="rename-input"
              @keydown.enter="submitRename(p, 'workout')"
              @keydown.escape="cancelRename"
              autofocus
            />
            <div class="rename-actions">
              <button class="btn rename-save" @click="submitRename(p, 'workout')">Save</button>
              <button class="btn ghost rename-cancel" @click="cancelRename">Cancel</button>
            </div>
          </div>
          <button class="rename-btn" title="Rename" @click.prevent.stop="startRename(`w-${p.plan_id}`, p.title || '')">✎</button>
        </div>
      </div>
    </section>

    <section class="ll-card">
      <div class="section-head">
        <h2>Nutrition Plans</h2>
      </div>

      <p v-if="nutritionError" class="error">{{ nutritionError }}</p>
      <p v-if="plansLoading && user" class="muted">Loading your plans…</p>
      <p v-if="!plansLoading && user && nutritionPlans.length === 0" class="empty">
        No nutrition plans yet. Generate one and it will appear here.
      </p>
      <p v-if="!user" class="muted">Log in to see your plans.</p>

      <div v-if="nutritionPlans.length" class="plan-list">
        <div v-for="p in nutritionPlans" :key="p.id" class="plan-row-wrap">
          <NuxtLink v-if="editingId !== `n-${p.id}`" class="plan-row" :to="`/plans/nutrition/${p.id}`">
            <div>
              <p class="plan-title">{{ p.title || "Untitled nutrition plan" }}</p>
              <p class="plan-meta">Plan #{{ p.id }} • {{ p.created_at }}</p>
            </div>
            <span class="chev">→</span>
          </NuxtLink>
          <div v-else class="plan-row editing">
            <input
              v-model="editingTitle"
              class="rename-input"
              @keydown.enter="submitRename(p, 'nutrition')"
              @keydown.escape="cancelRename"
              autofocus
            />
            <div class="rename-actions">
              <button class="btn rename-save" @click="submitRename(p, 'nutrition')">Save</button>
              <button class="btn ghost rename-cancel" @click="cancelRename">Cancel</button>
            </div>
          </div>
          <button class="rename-btn" title="Rename" @click.prevent.stop="startRename(`n-${p.id}`, p.title || '')">✎</button>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { usePlans } from "../../../composables/usePlans";
import { useAuth } from "../../../composables/useAuth";

type User = { id: number; email: string };

const { listMyPlans, listMyNutritionPlans, renamePlan, renameNutritionPlan } = usePlans();
const { requestCode, verifyCode, logout, me } = useAuth();

const user = ref<User | null>(null);
const email = ref("");
const code = ref("");
const authStep = ref<"idle" | "code_sent">("idle");
const authLoading = ref(false);
const authError = ref<string | null>(null);

const plans = ref<any[]>([]);
const nutritionPlans = ref<any[]>([]);
const plansLoading = ref(false);
const plansError = ref<string | null>(null);
const nutritionError = ref<string | null>(null);

const editingId = ref<string | null>(null);
const editingTitle = ref("");
const renameError = ref<string | null>(null);

async function loadMine() {
  if (!user.value) return;
  plansLoading.value = true;
  plansError.value = null;
  nutritionError.value = null;
  try {
    const [workoutRes, nutritionRes]: any[] = await Promise.all([
      listMyPlans(),
      listMyNutritionPlans(),
    ]);
    plans.value = workoutRes?.items ?? [];
    nutritionPlans.value = nutritionRes?.items ?? [];
  } catch (e: any) {
    plansError.value = e?.data?.detail ?? e?.message ?? String(e);
  } finally {
    plansLoading.value = false;
  }
}

async function onRequestCode() {
  authLoading.value = true;
  authError.value = null;
  try {
    await requestCode(email.value.trim().toLowerCase());
    authStep.value = "code_sent";
  } catch (e: any) {
    authError.value = e?.data?.detail ?? e?.message ?? String(e);
  } finally {
    authLoading.value = false;
  }
}

async function onVerifyCode() {
  authLoading.value = true;
  authError.value = null;
  try {
    const res = await verifyCode(email.value.trim().toLowerCase(), code.value.trim());
    user.value = res;
    authStep.value = "idle";
    code.value = "";
    await loadMine();
  } catch (e: any) {
    authError.value = e?.data?.detail ?? e?.message ?? String(e);
  } finally {
    authLoading.value = false;
  }
}

async function onLogout() {
  authLoading.value = true;
  authError.value = null;
  try {
    await logout();
    user.value = null;
    plans.value = [];
  } catch (e: any) {
    authError.value = e?.data?.detail ?? e?.message ?? String(e);
  } finally {
    authLoading.value = false;
  }
}

function startRename(key: string, currentTitle: string) {
  editingId.value = key;
  editingTitle.value = currentTitle;
  renameError.value = null;
}

function cancelRename() {
  editingId.value = null;
  editingTitle.value = "";
}

async function submitRename(plan: any, type: "workout" | "nutrition") {
  const title = editingTitle.value.trim();
  if (!title) return;
  try {
    if (type === "workout") {
      await renamePlan(plan.plan_id, title);
      plan.title = title;
    } else {
      await renameNutritionPlan(plan.id, title);
      plan.title = title;
    }
    editingId.value = null;
  } catch (err: any) {
    renameError.value = err?.data?.detail ?? "Rename failed";
  }
}

onMounted(async () => {
  authLoading.value = true;
  try {
    user.value = await me();
    if (user.value) {
      await loadMine();
    }
  } catch (e: any) {
    authError.value = e?.data?.detail ?? e?.message ?? String(e);
  } finally {
    authLoading.value = false;
  }
});
</script>

<style scoped>
.page {
  padding: 28px 20px 80px;
  color: #e5e7eb;
  font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
  background: radial-gradient(circle at top left, #2a1658 0%, #0b0b12 45%);
  min-height: 100vh;
}

.hero {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
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
  font-size: 32px;
  margin: 0 0 6px;
}

.sub {
  margin: 0;
  opacity: 0.75;
}

.ll-card {
  background: rgba(16, 10, 32, 0.8);
  border: 1px solid rgba(124, 58, 237, 0.25);
  border-radius: 14px;
  padding: 20px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.35);
  margin-bottom: 16px;
}

.auth-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.auth-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
}

.label {
  font-weight: 700;
  margin: 0 0 6px;
}

.status {
  margin: 0;
  font-size: 14px;
}

.muted {
  opacity: 0.7;
}

.input {
  background: rgba(12, 8, 26, 0.9);
  border: 1px solid rgba(124, 58, 237, 0.4);
  border-radius: 10px;
  color: #e5e7eb;
  padding: 10px 12px;
  min-width: 220px;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 10px;
  border: 1px solid rgba(124, 58, 237, 0.6);
  background: rgba(124, 58, 237, 0.2);
  color: #e5e7eb;
  font-weight: 700;
  cursor: pointer;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn.ghost {
  background: transparent;
  border-color: rgba(148, 163, 184, 0.3);
}

.section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

h2 {
  margin: 0;
  font-size: 18px;
}

.plan-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 8px;
}

.plan-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 14px;
  border-radius: 12px;
  border: 1px solid rgba(124, 58, 237, 0.2);
  background: rgba(20, 12, 40, 0.8);
  color: inherit;
  text-decoration: none;
}

.plan-title {
  margin: 0 0 4px;
  font-weight: 700;
}

.plan-meta {
  margin: 0;
  font-size: 12px;
  opacity: 0.7;
}

.chev {
  opacity: 0.6;
  font-size: 18px;
}

.plan-row-wrap {
  position: relative;
  display: flex;
  align-items: center;
  gap: 8px;
}

.plan-row-wrap .plan-row {
  flex: 1;
}

.plan-row.editing {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}

.rename-input {
  flex: 1;
  min-width: 160px;
  background: rgba(12, 8, 26, 0.9);
  border: 1px solid rgba(124, 58, 237, 0.6);
  border-radius: 8px;
  color: #e5e7eb;
  padding: 8px 12px;
  font-size: 14px;
  font-weight: 700;
  outline: none;
}

.rename-actions {
  display: flex;
  gap: 8px;
}

.rename-save {
  padding: 8px 14px;
  font-size: 13px;
}

.rename-cancel {
  padding: 8px 14px;
  font-size: 13px;
}

.rename-btn {
  flex-shrink: 0;
  background: none;
  border: none;
  color: rgba(167, 139, 250, 0.5);
  font-size: 16px;
  cursor: pointer;
  padding: 4px 6px;
  border-radius: 6px;
  line-height: 1;
  transition: color 0.15s;
}

.rename-btn:hover {
  color: rgba(167, 139, 250, 1);
}

.error {
  color: #fca5a5;
  margin-top: 12px;
}

.empty {
  margin: 8px 0 0;
  opacity: 0.8;
}

@media (max-width: 720px) {
  .hero {
    flex-direction: column;
    align-items: flex-start;
    gap: 6px;
  }

  .auth-actions {
    width: 100%;
  }

  .input {
    flex: 1;
    min-width: 180px;
  }
}
</style>
