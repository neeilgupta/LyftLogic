<script setup lang="ts">
import { ref, onMounted } from "vue";
import { useRouter, useRoute } from "vue-router";
import { useAuth } from "../../composables/useAuth";

const router = useRouter();
const route = useRoute();
const { verifyEmail, me } = useAuth();
const user = useState<{ id: number; email: string } | null>('user', () => null);

const status = ref<"loading" | "success" | "error">("loading");
const errorMsg = ref("");

onMounted(async () => {
  const token = route.query.token as string | undefined;
  if (!token) {
    status.value = "error";
    errorMsg.value = "Invalid verification link.";
    return;
  }
  try {
    await verifyEmail(token);
    user.value = await me();
    status.value = "success";
    setTimeout(() => router.push("/plans"), 1500);
  } catch (e: any) {
    status.value = "error";
    errorMsg.value = e?.data?.detail ?? e?.message ?? "Verification failed.";
  }
});
</script>

<template>
  <div class="page">
    <div class="card">
      <div class="brand">
        <h1 class="wordmark">Lyft<span class="accent">Logic</span></h1>
      </div>

      <!-- Loading -->
      <div v-if="status === 'loading'" class="state-box">
        <div class="spinner-ring">
          <div class="spinner"></div>
        </div>
        <p class="state-title">Verifying email</p>
        <p class="state-text">Hang tight…</p>
      </div>

      <!-- Success -->
      <div v-else-if="status === 'success'" class="state-box">
        <div class="check-wrap">
          <svg class="check-svg" viewBox="0 0 48 48" fill="none">
            <circle cx="24" cy="24" r="22" stroke="#7c3aed" stroke-width="1.5" stroke-dasharray="138" stroke-dashoffset="138" class="check-circle"/>
            <polyline points="14,25 21,32 34,17" stroke="#7c3aed" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="30" stroke-dashoffset="30" class="check-mark"/>
          </svg>
        </div>
        <p class="state-title">Email verified</p>
        <p class="state-text">Redirecting to your plans…</p>
      </div>

      <!-- Error -->
      <div v-else class="state-box">
        <div class="error-icon">!</div>
        <p class="state-title error-title">Verification failed</p>
        <p class="error-msg">{{ errorMsg }}</p>
        <NuxtLink to="/login" class="link-btn">← Back to sign in</NuxtLink>
      </div>
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
  margin-bottom: 32px;
}

.wordmark {
  font-family: 'Syne', sans-serif;
  font-size: 26px;
  font-weight: 900;
  letter-spacing: -0.03em;
  margin: 0;
  color: #f0ede6;
  line-height: 1;
}

.accent {
  color: #7c3aed;
}

/* State box */
.state-box {
  text-align: center;
  padding: 8px 0 4px;
}

/* Loading spinner */
.spinner-ring {
  width: 52px;
  height: 52px;
  margin: 0 auto 20px;
  position: relative;
}

.spinner {
  width: 52px;
  height: 52px;
  border: 2px solid rgba(255,255,255,0.06);
  border-top-color: #7c3aed;
  border-right-color: rgba(124, 58, 237, 0.4);
  border-radius: 50%;
  animation: spin 0.9s cubic-bezier(0.4, 0, 0.2, 1) infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* SVG check animation */
.check-wrap {
  width: 52px;
  height: 52px;
  margin: 0 auto 20px;
}

.check-svg {
  width: 52px;
  height: 52px;
  overflow: visible;
}

.check-circle {
  animation: drawCircle 0.5s ease forwards;
}

.check-mark {
  animation: drawMark 0.35s ease 0.4s forwards;
}

@keyframes drawCircle {
  to { stroke-dashoffset: 0; }
}

@keyframes drawMark {
  to { stroke-dashoffset: 0; }
}

/* Error icon */
.error-icon {
  width: 48px;
  height: 48px;
  border: 2px solid rgba(248, 113, 113, 0.4);
  border-radius: 50%;
  color: #f87171;
  font-family: 'DM Mono', monospace;
  font-size: 22px;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 20px;
}

.state-title {
  font-family: 'Syne', sans-serif;
  font-size: 18px;
  font-weight: 700;
  margin: 0 0 8px;
  color: #f0ede6;
}

.error-title {
  color: #fca5a5;
}

.state-text {
  font-family: 'DM Mono', monospace;
  font-size: 12px;
  color: rgba(240, 237, 230, 0.42);
  margin: 0;
  letter-spacing: 0.02em;
}

.error-msg {
  font-family: 'DM Mono', monospace;
  font-size: 12px;
  color: #f87171;
  margin: 0 0 18px;
  padding: 10px 12px;
  background: rgba(248, 113, 113, 0.07);
  border-left: 2px solid #f87171;
  border-radius: 0 3px 3px 0;
  text-align: left;
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
</style>
