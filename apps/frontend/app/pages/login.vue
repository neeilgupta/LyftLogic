<script setup lang="ts">
import { ref } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useAuth } from "../../composables/useAuth";

const router = useRouter();
const route = useRoute();
const { requestCode, verifyCode, register, passwordLogin, me, resendVerification } = useAuth();
const user = useState<{ id: number; email: string } | null>('user', () => null);

// "password" | "register" | "otp"
const mode = ref<"password" | "register" | "otp">("password");

// Shared
const email = ref("");
const error = ref<string | null>(null);
const loading = ref(false);

// Password / Register fields
const password = ref("");
const confirmPassword = ref("");

// Post-register state
const registered = ref(false);
const resendLoading = ref(false);
const resendSent = ref(false);

// OTP fields
const codeSent = ref(false);
const code = ref("");

// Banner for successful password reset redirect
const resetSuccess = route.query.reset === "1";

function resetState() {
  error.value = null;
  password.value = "";
  confirmPassword.value = "";
  codeSent.value = false;
  code.value = "";
  registered.value = false;
  resendSent.value = false;
}

function switchMode(m: "password" | "register" | "otp") {
  mode.value = m;
  resetState();
}

async function handlePasswordLogin() {
  error.value = null;
  if (!email.value || !password.value) {
    error.value = "Email and password are required";
    return;
  }
  loading.value = true;
  try {
    await passwordLogin(email.value.trim().toLowerCase(), password.value);
    user.value = await me();
    router.push("/plans");
  } catch (e: any) {
    error.value = e?.data?.detail ?? e?.message ?? "Login failed";
  } finally {
    loading.value = false;
  }
}

async function handleRegister() {
  error.value = null;
  if (!email.value || !password.value) {
    error.value = "Email and password are required";
    return;
  }
  if (password.value.length < 8) {
    error.value = "Password must be at least 8 characters";
    return;
  }
  if (password.value !== confirmPassword.value) {
    error.value = "Passwords do not match";
    return;
  }
  loading.value = true;
  try {
    await register(email.value.trim().toLowerCase(), password.value);
    registered.value = true;
  } catch (e: any) {
    error.value = e?.data?.detail ?? e?.message ?? "Registration failed";
  } finally {
    loading.value = false;
  }
}

async function handleResendVerification() {
  resendSent.value = false;
  resendLoading.value = true;
  try {
    await resendVerification(email.value.trim().toLowerCase());
    resendSent.value = true;
  } catch (e: any) {
    error.value = e?.data?.detail ?? e?.message ?? "Failed to resend link";
  } finally {
    resendLoading.value = false;
  }
}

async function handleRequestCode() {
  error.value = null;
  if (!email.value) {
    error.value = "Email is required";
    return;
  }
  loading.value = true;
  try {
    await requestCode(email.value.trim().toLowerCase());
    codeSent.value = true;
  } catch (e: any) {
    error.value = e?.data?.detail ?? e?.message ?? "Failed to send code";
  } finally {
    loading.value = false;
  }
}

async function handleVerifyCode() {
  error.value = null;
  if (!code.value) {
    error.value = "Enter the 6-digit code";
    return;
  }
  loading.value = true;
  try {
    await verifyCode(email.value.trim().toLowerCase(), code.value.trim());
    user.value = await me();
    router.push("/plans");
  } catch (e: any) {
    error.value = e?.data?.detail ?? e?.message ?? "Invalid or expired code";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div class="page">
    <div class="card">
      <div class="brand">
        <h1 class="wordmark">Lyft<span class="accent">Logic</span></h1>
        <p class="sub">
          <template v-if="mode === 'register'">Create your account</template>
          <template v-else-if="mode === 'otp'">Sign in with a magic link</template>
          <template v-else>Sign in to your account</template>
        </p>
      </div>

      <div v-if="resetSuccess" class="banner success-banner">
        Password reset — sign in with your new password.
      </div>

      <!-- Tab strip -->
      <div class="tabs">
        <button
          class="tab"
          :class="{ active: mode === 'password' || mode === 'register' }"
          @click="switchMode('password')"
        >
          Password
        </button>
        <button
          class="tab"
          :class="{ active: mode === 'otp' }"
          @click="switchMode('otp')"
        >
          Magic link
        </button>
      </div>

      <!-- Email field (all modes) -->
      <div class="field">
        <label class="label">Email</label>
        <input
          v-model="email"
          type="email"
          class="input"
          placeholder="you@example.com"
          autocomplete="email"
          @keydown.enter="mode === 'otp' ? (codeSent ? handleVerifyCode() : handleRequestCode()) : (mode === 'register' ? handleRegister() : handlePasswordLogin())"
        />
      </div>

      <!-- Password login -->
      <template v-if="mode === 'password'">
        <div class="field">
          <label class="label">Password</label>
          <input
            v-model="password"
            type="password"
            class="input"
            placeholder="••••••••"
            autocomplete="current-password"
            @keydown.enter="handlePasswordLogin"
          />
        </div>

        <div v-if="error" class="error-msg">{{ error }}</div>

        <button class="btn-primary" :disabled="loading" @click="handlePasswordLogin">
          <span class="btn-text">{{ loading ? "Signing in…" : "Sign in" }}</span>
          <span v-if="loading" class="btn-spinner"></span>
        </button>

        <div class="links-row">
          <NuxtLink to="/forgot-password" class="link-btn">Forgot password?</NuxtLink>
          <span class="links-sep">·</span>
          <button class="link-btn" @click="switchMode('register')">Create account</button>
        </div>
      </template>

      <!-- Register -->
      <template v-else-if="mode === 'register'">
        <template v-if="registered">
          <div class="state-box">
            <div class="state-icon">✉</div>
            <p class="state-title">Check your inbox</p>
            <p class="state-text">We sent a verification link to <strong>{{ email }}</strong>. Click it to activate your account.</p>
            <div v-if="error" class="error-msg">{{ error }}</div>
            <p class="state-text">
              Didn't get it?
              <button class="link-btn" :disabled="resendLoading" @click="handleResendVerification">
                {{ resendLoading ? "Sending…" : resendSent ? "Sent!" : "Resend link" }}
              </button>
            </p>
          </div>
        </template>
        <template v-else>
          <div class="field">
            <label class="label">Password</label>
            <input
              v-model="password"
              type="password"
              class="input"
              placeholder="Min. 8 characters"
              autocomplete="new-password"
            />
          </div>
          <div class="field">
            <label class="label">Confirm password</label>
            <input
              v-model="confirmPassword"
              type="password"
              class="input"
              placeholder="••••••••"
              autocomplete="new-password"
              @keydown.enter="handleRegister"
            />
          </div>

          <div v-if="error" class="error-msg">{{ error }}</div>

          <button class="btn-primary" :disabled="loading" @click="handleRegister">
            <span class="btn-text">{{ loading ? "Creating account…" : "Create account" }}</span>
            <span v-if="loading" class="btn-spinner"></span>
          </button>

          <div class="links-row">
            <button class="link-btn" @click="switchMode('password')">Already have an account?</button>
          </div>
        </template>
      </template>

      <!-- OTP -->
      <template v-else-if="mode === 'otp'">
        <template v-if="!codeSent">
          <div v-if="error" class="error-msg">{{ error }}</div>
          <button class="btn-primary" :disabled="loading" @click="handleRequestCode">
            <span class="btn-text">{{ loading ? "Sending…" : "Send magic link" }}</span>
            <span v-if="loading" class="btn-spinner"></span>
          </button>
        </template>
        <template v-else>
          <div class="field">
            <label class="label">6-digit code</label>
            <input
              v-model="code"
              type="text"
              class="input input-code"
              placeholder="123456"
              inputmode="numeric"
              maxlength="6"
              autocomplete="one-time-code"
              @keydown.enter="handleVerifyCode"
            />
          </div>
          <p class="hint">Code sent to {{ email }}</p>
          <div v-if="error" class="error-msg">{{ error }}</div>
          <button class="btn-primary" :disabled="loading" @click="handleVerifyCode">
            <span class="btn-text">{{ loading ? "Verifying…" : "Verify code" }}</span>
            <span v-if="loading" class="btn-spinner"></span>
          </button>
          <div class="links-row">
            <button class="link-btn" @click="codeSent = false; error = null">
              ← Different email
            </button>
          </div>
        </template>
      </template>
    </div>
  </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;900&family=DM+Mono:ital,wght@0,400;0,500&family=DM+Sans:wght@400;500;600&display=swap');

:root {
  --amber: #7c3aed;
  --amber-dim: rgba(124, 58, 237, 0.12);
  --amber-glow: rgba(124, 58, 237, 0.07);
  --bg: #090907;
  --surface: #111110;
  --surface-2: #191917;
  --border: rgba(255, 255, 255, 0.07);
  --border-strong: rgba(255, 255, 255, 0.12);
  --text: #f0ede6;
  --text-dim: rgba(240, 237, 230, 0.42);
  --error-color: #f87171;
  --success-color: #4ade80;
}

.page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px 16px;
  background-color: var(--bg);
  background-image:
    linear-gradient(rgba(124, 58, 237, 0.025) 1px, transparent 1px),
    linear-gradient(90deg, rgba(124, 58, 237, 0.025) 1px, transparent 1px);
  background-size: 44px 44px;
  font-family: 'DM Sans', sans-serif;
  color: var(--text);
}

.card {
  width: 100%;
  max-width: 420px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-left: 3px solid var(--amber);
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
}

.wordmark {
  font-family: 'Syne', sans-serif;
  font-size: 26px;
  font-weight: 900;
  letter-spacing: -0.03em;
  margin: 0 0 4px;
  color: var(--text);
  line-height: 1;
}

.accent {
  color: var(--amber);
}

.sub {
  font-family: 'DM Mono', monospace;
  font-size: 12px;
  color: var(--text-dim);
  margin: 0;
  letter-spacing: 0.02em;
}

/* Tab strip */
.tabs {
  display: flex;
  border-bottom: 1px solid var(--border);
  margin-bottom: 24px;
}

.tab {
  flex: 1;
  padding: 9px 0;
  border: none;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  background: transparent;
  color: var(--text-dim);
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  cursor: pointer;
  transition: color 0.15s, border-color 0.15s;
}

.tab.active {
  color: var(--amber);
  border-bottom-color: var(--amber);
}

.tab:hover:not(.active) {
  color: rgba(240, 237, 230, 0.7);
}

/* Fields */
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
  color: var(--text-dim);
}

.input {
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 3px;
  padding: 11px 14px;
  color: var(--text);
  font-size: 15px;
  font-family: 'DM Sans', sans-serif;
  outline: none;
  transition: border-color 0.15s, box-shadow 0.15s;
  width: 100%;
  box-sizing: border-box;
}

.input:focus {
  border-color: var(--amber);
  box-shadow: 0 0 0 3px var(--amber-glow);
}

.input::placeholder {
  color: var(--text-dim);
  opacity: 0.6;
}

.input-code {
  font-family: 'DM Mono', monospace;
  font-size: 20px;
  letter-spacing: 0.3em;
  text-align: center;
}

/* Button */
.btn-primary {
  width: 100%;
  padding: 12px;
  background: var(--amber);
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
  position: relative;
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

/* Messages */
.error-msg {
  font-family: 'DM Mono', monospace;
  font-size: 12px;
  color: var(--error-color);
  margin-bottom: 12px;
  padding: 10px 12px;
  background: rgba(248, 113, 113, 0.07);
  border-left: 2px solid var(--error-color);
  border-radius: 0 3px 3px 0;
}

.hint {
  font-size: 13px;
  color: var(--text-dim);
  margin: 0 0 14px;
}

.banner {
  font-size: 13px;
  padding: 10px 14px;
  border-radius: 3px;
  margin-bottom: 18px;
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  letter-spacing: 0.02em;
}

.success-banner {
  background: rgba(74, 222, 128, 0.07);
  border-left: 2px solid var(--success-color);
  color: #86efac;
}

/* Links */
.links-row {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 18px;
}

.links-sep {
  color: var(--border-strong);
  font-size: 14px;
}

.link-btn {
  background: none;
  border: none;
  color: var(--amber);
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

.link-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* State box (post-register, etc.) */
.state-box {
  text-align: center;
  padding: 8px 0 4px;
}

.state-icon {
  font-size: 28px;
  margin-bottom: 12px;
  opacity: 0.75;
  font-style: normal;
}

.state-title {
  font-family: 'Syne', sans-serif;
  font-size: 17px;
  font-weight: 700;
  margin: 0 0 10px;
  color: var(--text);
}

.state-text {
  font-size: 13px;
  color: var(--text-dim);
  margin: 0 0 10px;
  line-height: 1.55;
}
</style>
