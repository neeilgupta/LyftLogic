<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from "vue";

const containerRef = ref<HTMLElement | null>(null);
const scrollProgress = ref(0);
const isMobile = ref(false);

function checkMobile() {
  isMobile.value = window.innerWidth <= 768;
}

function onScroll() {
  const el = containerRef.value;
  if (!el) return;
  const rect = el.getBoundingClientRect();
  const wh = window.innerHeight;
  const raw = (wh - rect.top) / (wh + rect.height);
  scrollProgress.value = Math.max(0, Math.min(1, raw));
}

onMounted(() => {
  checkMobile();
  window.addEventListener("resize", checkMobile, { passive: true });
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll(); // seed initial value
});

onUnmounted(() => {
  window.removeEventListener("resize", checkMobile);
  window.removeEventListener("scroll", onScroll);
});

const rotate = computed(() => 20 * (1 - scrollProgress.value));

const scale = computed(() => {
  const [from, to] = isMobile.value ? [0.7, 0.9] : [1.05, 1.0];
  return from + (to - from) * scrollProgress.value;
});

const translateY = computed(() => -100 * scrollProgress.value);

const cardStyle = computed(() => ({
  transform: `rotateX(${rotate.value}deg) scale(${scale.value})`,
  boxShadow: "0 0 #0000004d, 0 9px 20px #0000004a, 0 37px 37px #00000042, 0 84px 50px #00000026, 0 149px 60px #0000000a, 0 233px 65px #00000003",
  willChange: "transform",
}));

const headerStyle = computed(() => ({
  transform: `translateY(${translateY.value}px)`,
  willChange: "transform",
}));
</script>

<template>
  <div ref="containerRef" class="csa-container">
    <div class="csa-inner">
      <div :style="headerStyle" class="csa-header">
        <slot name="title" />
      </div>
      <div :style="cardStyle" class="csa-card">
        <div class="csa-card-inner">
          <slot />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.csa-container {
  height: 44rem;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  padding: 8px;
}

@media (min-width: 768px) {
  .csa-container {
    height: 54rem;
    padding: 80px;
  }
}

.csa-inner {
  padding: 20px 0;
  width: 100%;
  position: relative;
  perspective: 1000px;
}

@media (min-width: 768px) {
  .csa-inner {
    padding: 60px 0;
  }
}

.csa-header {
  max-width: 860px;
  margin: 0 auto;
  text-align: center;
}

.csa-card {
  max-width: 860px;
  margin: -48px auto 0;
  height: 26rem;
  width: 100%;
  border: 2px solid rgba(124, 58, 237, 0.35);
  padding: 8px;
  background: #111110;
  border-radius: 20px;
  transform-origin: top center;
}

@media (min-width: 768px) {
  .csa-card {
    height: 36rem;
    padding: 24px;
  }
}

.csa-card-inner {
  height: 100%;
  width: 100%;
  overflow: hidden;
  border-radius: 12px;
  background: #0d0d0b;
}
</style>
