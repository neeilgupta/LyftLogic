<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import { useAuth } from "../../composables/useAuth";

const router = useRouter();
const { requestCode, verifyCode, register, passwordLogin, me } = useAuth();
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

// OTP fields
const codeSent = ref(false);
const code = ref("");

function resetState() {
  error.value = null;
  password.value = "";
  confirmPassword.value = "";
  codeSent.value = false;
  code.value = "";
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
    user.value = await me();
    router.push("/plans");
  } catch (e: any) {
    error.value = e?.data?.detail ?? e?.message ?? "Registration failed";
  } finally {
    loading.value = false;
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
      <h1 class="title">LyftLogic</h1>
      <p class="sub">Sign in to your account</p>

      <!-- Tab strip -->
      <div class="tabs">
        <button
          class="tab"
          :class="{ active: mode === 'password' || mode === 'register' }"
          @click="switchMode('password')"
        >
          Email + Password
        </button>
        <button
          class="tab"
          :class="{ active: mode === 'otp' }"
          @click="switchMode('otp')"
        >
          Magic Link
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

        <div v-if="error" class="error">{{ error }}</div>

        <button class="btn-primary" :disabled="loading" @click="handlePasswordLogin">
          {{ loading ? "Signing in…" : "Sign in" }}
        </button>

        <p class="switch-link">
          Don't have an account?
          <button class="link-btn" @click="switchMode('register')">Create one</button>
        </p>
      </template>

      <!-- Register -->
      <template v-else-if="mode === 'register'">
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

        <div v-if="error" class="error">{{ error }}</div>

        <button class="btn-primary" :disabled="loading" @click="handleRegister">
          {{ loading ? "Creating account…" : "Create account" }}
        </button>

        <p class="switch-link">
          Already have an account?
          <button class="link-btn" @click="switchMode('password')">Sign in</button>
        </p>
      </template>

      <!-- OTP -->
      <template v-else-if="mode === 'otp'">
        <template v-if="!codeSent">
          <div v-if="error" class="error">{{ error }}</div>
          <button class="btn-primary" :disabled="loading" @click="handleRequestCode">
            {{ loading ? "Sending…" : "Send magic link" }}
          </button>
        </template>
        <template v-else>
          <div class="field">
            <label class="label">6-digit code</label>
            <input
              v-model="code"
              type="text"
              class="input"
              placeholder="123456"
              inputmode="numeric"
              maxlength="6"
              autocomplete="one-time-code"
              @keydown.enter="handleVerifyCode"
            />
          </div>
          <p class="hint">Code sent to {{ email }}. Check your inbox.</p>
          <div v-if="error" class="error">{{ error }}</div>
          <button class="btn-primary" :disabled="loading" @click="handleVerifyCode">
            {{ loading ? "Verifying…" : "Verify code" }}
          </button>
          <p class="switch-link">
            <button class="link-btn" @click="codeSent = false; error = null">
              ← Use a different email
            </button>
          </p>
        </template>
      </template>
    </div>
  </div>
</template>

<style scoped>
.page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px 16px;
  background: radial-gradient(circle at top left, #2a1658 0%, #0b0b12 50%);
  font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
  color: #e5e7eb;
}

.card {
  width: 100%;
  max-width: 400px;
  background: rgba(16, 10, 32, 0.85);
  border: 1px solid rgba(124, 58, 237, 0.3);
  border-radius: 16px;
  padding: 32px 28px;
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.4);
}

.title {
  font-size: 24px;
  font-weight: 900;
  margin: 0 0 4px;
  text-align: center;
}

.sub {
  text-align: center;
  opacity: 0.55;
  font-size: 14px;
  margin: 0 0 24px;
}

.tabs {
  display: flex;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.05);
  padding: 3px;
  margin-bottom: 22px;
  gap: 3px;
}

.tab {
  flex: 1;
  padding: 8px 0;
  border: none;
  border-radius: 8px;
  background: transparent;
  color: rgba(229, 231, 235, 0.55);
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}

.tab.active {
  background: rgba(124, 58, 237, 0.25);
  color: rgba(167, 139, 250, 1);
}

.tab:hover:not(.active) {
  color: rgba(229, 231, 235, 0.85);
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 14px;
}

.label {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  opacity: 0.6;
}

.input {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(124, 58, 237, 0.3);
  border-radius: 9px;
  padding: 10px 13px;
  color: #e5e7eb;
  font-size: 15px;
  outline: none;
  transition: border-color 0.15s;
}

.input:focus {
  border-color: rgba(124, 58, 237, 0.7);
}

.input::placeholder {
  opacity: 0.35;
}

.btn-primary {
  width: 100%;
  padding: 11px;
  background: rgba(124, 58, 237, 0.85);
  border: none;
  border-radius: 10px;
  color: #fff;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  margin-top: 4px;
  transition: background 0.15s;
}

.btn-primary:hover:not(:disabled) {
  background: rgba(124, 58, 237, 1);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error {
  color: #fca5a5;
  font-size: 13px;
  margin-bottom: 10px;
}

.hint {
  font-size: 13px;
  opacity: 0.6;
  margin: 0 0 12px;
}

.switch-link {
  text-align: center;
  font-size: 13px;
  opacity: 0.65;
  margin-top: 16px;
}

.link-btn {
  background: none;
  border: none;
  color: rgba(167, 139, 250, 1);
  font-size: 13px;
  cursor: pointer;
  padding: 0;
  font-weight: 600;
}

.link-btn:hover {
  text-decoration: underline;
}
</style>
