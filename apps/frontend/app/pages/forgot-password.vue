<script setup lang="ts">
import { ref } from "vue";
import { useAuth } from "../../composables/useAuth";

const { forgotPassword } = useAuth();

const email = ref("");
const loading = ref(false);
const submitted = ref(false);
const error = ref<string | null>(null);

async function handleSubmit() {
  error.value = null;
  if (!email.value.trim()) {
    error.value = "Email is required";
    return;
  }
  loading.value = true;
  try {
    await forgotPassword(email.value.trim().toLowerCase());
    submitted.value = true;
  } catch (e: any) {
    error.value = e?.data?.detail ?? e?.message ?? "Something went wrong. Try again.";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="page">
    <div class="card">
      <div class="brand">
        <NuxtLink to="/login" class="back-link">← Sign in</NuxtLink>
        <h1 class="wordmark">Lyft<span class="accent">Logic</span></h1>
        <p class="sub">Reset your password</p>
      </div>

      <template v-if="submitted">
        <div class="state-box">
          <div class="state-icon">✉</div>
          <p class="state-title">Check your inbox</p>
          <p class="state-text">
            If an account with that email exists, a reset link has been sent.
          </p>
          <NuxtLink to="/login" class="link-btn">← Back to sign in</NuxtLink>
        </div>
      </template>

      <template v-else>
        <div class="field">
          <label class="label">Email</label>
          <input
            v-model="email"
            type="email"
            class="input"
            placeholder="you@example.com"
            autocomplete="email"
            @keydown.enter="handleSubmit"
          />
        </div>

        <div v-if="error" class="error-msg">{{ error }}</div>

        <button class="btn-primary" :disabled="loading" @click="handleSubmit">
          <span class="btn-text">{{ loading ? "Sending…" : "Send reset link" }}</span>
          <span v-if="loading" class="btn-spinner"></span>
        </button>

        <div class="links-row">
          <NuxtLink to="/login" class="link-btn">← Back to sign in</NuxtLink>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;900&family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600&display=swap');

.page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px 16px;
  background-color: #090907;
  background-image:
    linear-gradient(rgba(124, 58, 237, 0.025) 1px, transparent 1px),
    linear-gradient(90deg, rgba(124, 58, 237, 0.025) 1px, transparent 1px);
  background-size: 44px 44px;
  font-family: 'DM Sans', sans-serif;
  color: #f0ede6;
}

.card {
  width: 100%;
  max-width: 420px;
  background: #111110;
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-left: 3px solid #7c3aed;
  border-radius: 4px;
  padding: 36px 32px;
  box-shadow: 0 32px 64px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(0,0,0,0.4);
  animation: slideUp 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}

@keyframes slideUp {
  from { opacity: 0; transform: translateY(14px); }
  to   { opacity: 1; transform: translateY(0); }
}

.brand {
  margin-bottom: 28px;
  position: relative;
}

.back-link {
  position: absolute;
  top: 0;
  right: 0;
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  color: rgba(124, 58, 237, 0.6);
  text-decoration: none;
  letter-spacing: 0.03em;
  transition: color 0.15s;
}

.back-link:hover {
  color: #7c3aed;
}

.wordmark {
  font-family: 'Syne', sans-serif;
  font-size: 26px;
  font-weight: 900;
  letter-spacing: -0.03em;
  margin: 0 0 4px;
  color: #f0ede6;
  line-height: 1;
}

.accent {
  color: #7c3aed;
}

.sub {
  font-family: 'DM Mono', monospace;
  font-size: 12px;
  color: rgba(240, 237, 230, 0.42);
  margin: 0;
  letter-spacing: 0.02em;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 7px;
  margin-bottom: 14px;
}

.label {
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: rgba(240, 237, 230, 0.42);
}

.input {
  background: #191917;
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 3px;
  padding: 11px 14px;
  color: #f0ede6;
  font-size: 15px;
  font-family: 'DM Sans', sans-serif;
  outline: none;
  transition: border-color 0.15s, box-shadow 0.15s;
  width: 100%;
  box-sizing: border-box;
}

.input:focus {
  border-color: #7c3aed;
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.07);
}

.input::placeholder {
  color: rgba(240, 237, 230, 0.25);
}

.btn-primary {
  width: 100%;
  padding: 12px;
  background: #7c3aed;
  border: none;
  border-radius: 3px;
  color: #ffffff;
  font-size: 12px;
  font-weight: 500;
  font-family: 'DM Mono', monospace;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  cursor: pointer;
  margin-top: 4px;
  transition: background 0.15s, transform 0.1s, opacity 0.15s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.btn-primary:hover:not(:disabled) {
  background: #6d28d9;
}

.btn-primary:active:not(:disabled) {
  transform: scale(0.99);
}

.btn-primary:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.btn-spinner {
  width: 14px;
  height: 14px;
  border: 1.5px solid rgba(10,10,8,0.3);
  border-top-color: #ffffff;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  flex-shrink: 0;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.error-msg {
  font-family: 'DM Mono', monospace;
  font-size: 12px;
  color: #f87171;
  margin-bottom: 12px;
  padding: 10px 12px;
  background: rgba(248, 113, 113, 0.07);
  border-left: 2px solid #f87171;
  border-radius: 0 3px 3px 0;
}

.links-row {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-top: 18px;
}

.link-btn {
  background: none;
  border: none;
  color: #7c3aed;
  font-size: 12px;
  font-family: 'DM Mono', monospace;
  letter-spacing: 0.03em;
  cursor: pointer;
  padding: 0;
  text-decoration: none;
  opacity: 0.8;
  transition: opacity 0.15s;
}

.link-btn:hover {
  opacity: 1;
  text-decoration: underline;
  text-underline-offset: 3px;
}

.state-box {
  text-align: center;
  padding: 8px 0 4px;
}

.state-icon {
  font-size: 28px;
  margin-bottom: 12px;
  opacity: 0.75;
}

.state-title {
  font-family: 'Syne', sans-serif;
  font-size: 17px;
  font-weight: 700;
  margin: 0 0 10px;
  color: #f0ede6;
}

.state-text {
  font-size: 13px;
  color: rgba(240, 237, 230, 0.55);
  margin: 0 0 18px;
  line-height: 1.6;
}
</style>
