<template>
  <main class="settings-page">
    <div class="page-header">
      <h1 class="page-title">Account Settings</h1>
      <p class="page-sub">Manage your account credentials and data.</p>
    </div>

    <div v-if="loadError" class="error-message">{{ loadError }}</div>

    <template v-if="user">
      <!-- Account Info -->
      <section class="ll-card">
        <div class="card-heading">Account</div>
        <div class="info-grid">
          <div class="info-row">
            <span class="info-label">Email</span>
            <span class="info-value">{{ user.email }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">Account type</span>
            <span class="info-value">{{ user.has_password ? "Password" : "Magic Link (OTP only)" }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">Member since</span>
            <span class="info-value">{{ formatDate(user.created_at) }}</span>
          </div>
          <div class="info-row">
            <span class="info-label">Email verified</span>
            <span :class="['info-badge', user.email_verified ? 'info-badge--ok' : 'info-badge--warn']">
              {{ user.email_verified ? "Verified" : "Not verified" }}
            </span>
          </div>
        </div>
      </section>

      <!-- Change Password — only for password accounts -->
      <section v-if="user.has_password" class="ll-card">
        <div class="card-heading">Change Password</div>
        <form @submit.prevent="onChangePassword" class="settings-form">
          <label class="form-field">
            <span class="form-label">Current password</span>
            <input
              v-model="pwForm.current"
              type="password"
              class="form-input"
              autocomplete="current-password"
              :disabled="pwLoading"
              required
            />
          </label>
          <label class="form-field">
            <span class="form-label">New password</span>
            <input
              v-model="pwForm.next"
              type="password"
              class="form-input"
              autocomplete="new-password"
              minlength="8"
              :disabled="pwLoading"
              required
            />
          </label>
          <div v-if="pwError" class="error-message">{{ pwError }}</div>
          <button type="submit" class="action-button" :disabled="pwLoading">
            {{ pwLoading ? "Updating…" : "Update password" }}
          </button>
        </form>
      </section>

      <!-- Delete Account -->
      <section class="ll-card ll-card--danger">
        <div class="card-heading">Delete Account</div>
        <p class="danger-body">
          Permanently deletes your account, all training plans, and all nutrition plans.
          This cannot be undone.
        </p>
        <form @submit.prevent="onDeleteAccount" class="settings-form">
          <label v-if="user.has_password" class="form-field">
            <span class="form-label">Confirm with your password</span>
            <input
              v-model="deletePassword"
              type="password"
              class="form-input"
              autocomplete="current-password"
              :disabled="deleteLoading"
              required
            />
          </label>
          <div v-if="deleteError" class="error-message">{{ deleteError }}</div>
          <button type="submit" class="action-button action-button--danger" :disabled="deleteLoading">
            {{ deleteLoading ? "Deleting…" : "Delete my account" }}
          </button>
        </form>
      </section>
    </template>
  </main>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useAuth } from "../../composables/useAuth";

const router = useRouter();
const { me, changePassword, deleteAccount } = useAuth();

const user = ref<any>(null);
const loadError = ref<string | null>(null);

const pwForm = ref({ current: "", next: "" });
const pwLoading = ref(false);
const pwError = ref<string | null>(null);

const deletePassword = ref("");
const deleteLoading = ref(false);
const deleteError = ref<string | null>(null);

onMounted(async () => {
  try {
    const u = await me();
    if (!u) {
      router.push("/login");
      return;
    }
    user.value = u;
  } catch (e: any) {
    loadError.value = e?.data?.detail ?? e?.message ?? "Failed to load account";
  }
});

function formatDate(iso?: string): string {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleDateString("en-US", { year: "numeric", month: "long", day: "numeric" });
  } catch {
    return iso;
  }
}

async function onChangePassword() {
  pwError.value = null;
  pwLoading.value = true;
  try {
    await changePassword(pwForm.value.current, pwForm.value.next);
    router.push("/login");
  } catch (e: any) {
    pwError.value = e?.data?.detail ?? e?.message ?? "Failed to update password";
  } finally {
    pwLoading.value = false;
  }
}

async function onDeleteAccount() {
  deleteError.value = null;
  deleteLoading.value = true;
  try {
    await deleteAccount(user.value?.has_password ? deletePassword.value : undefined);
    useState("user").value = null;
    router.push("/");
  } catch (e: any) {
    deleteError.value = e?.data?.detail ?? e?.message ?? "Failed to delete account";
  } finally {
    deleteLoading.value = false;
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

.settings-page {
  background-color: #090907;
  color: #f0ede6;
  padding: 40px 48px;
  font-family: 'DM Sans', sans-serif;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.settings-page > * {
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
  width: 100%;
}

.page-header {
  margin-bottom: 4px;
}

.page-title {
  font-family: 'Syne', sans-serif;
  font-size: 28px;
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

.ll-card {
  background: #111110;
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-left: 3px solid rgba(124, 58, 237, 0.4);
  border-radius: 4px;
  padding: 22px 20px;
}

.ll-card--danger {
  border-left-color: rgba(248, 113, 113, 0.5);
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

/* Info grid */
.info-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.info-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.info-label {
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  color: rgba(240, 237, 230, 0.4);
  text-transform: uppercase;
  letter-spacing: 0.06em;
  min-width: 120px;
}

.info-value {
  font-size: 13px;
  color: #f0ede6;
}

.info-badge {
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  letter-spacing: 0.04em;
  padding: 3px 8px;
  border-radius: 3px;
}

.info-badge--ok {
  background: rgba(52, 211, 153, 0.1);
  color: #6ee7b7;
  border: 1px solid rgba(52, 211, 153, 0.2);
}

.info-badge--warn {
  background: rgba(251, 191, 36, 0.08);
  color: #fcd34d;
  border: 1px solid rgba(251, 191, 36, 0.2);
}

/* Forms */
.settings-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
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

.form-input:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.action-button {
  background: #7c3aed;
  border: none;
  border-radius: 3px;
  color: #ffffff;
  font-family: 'DM Mono', monospace;
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  padding: 11px 22px;
  cursor: pointer;
  transition: background 0.15s, opacity 0.15s;
  width: fit-content;
}

.action-button:hover:not(:disabled) {
  background: #6d28d9;
}

.action-button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.action-button--danger {
  background: transparent;
  border: 1px solid rgba(248, 113, 113, 0.4);
  color: #fca5a5;
}

.action-button--danger:hover:not(:disabled) {
  background: rgba(248, 113, 113, 0.08);
  border-color: #f87171;
}

.danger-body {
  font-size: 13px;
  color: rgba(240, 237, 230, 0.55);
  margin: 0 0 16px;
  line-height: 1.55;
}

.error-message {
  background: rgba(248, 113, 113, 0.07);
  border-left: 2px solid #f87171;
  border-radius: 0 3px 3px 0;
  color: #fca5a5;
  padding: 10px 14px;
  font-family: 'DM Mono', monospace;
  font-size: 12px;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .settings-page {
    padding: 24px 18px;
  }
}
</style>
