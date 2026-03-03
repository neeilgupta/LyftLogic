<script setup lang="ts">
import { ref, onMounted, onUnmounted } from "vue";
import { animate } from "motion";

const props = withDefaults(
  defineProps<{
    blur?: number;
    inactiveZone?: number;
    proximity?: number;
    spread?: number;
    variant?: "default" | "white";
    glow?: boolean;
    disabled?: boolean;
    movementDuration?: number;
    borderWidth?: number;
  }>(),
  {
    blur: 0,
    inactiveZone: 0.7,
    proximity: 0,
    spread: 20,
    variant: "default",
    glow: false,
    disabled: true,
    movementDuration: 2,
    borderWidth: 1,
  }
);

const containerRef = ref<HTMLDivElement | null>(null);
const lastPosition = { x: 0, y: 0 };
let animationFrameId = 0;

const gradientDefault = [
  "radial-gradient(circle, #dd7bbb 10%, #dd7bbb00 20%)",
  "radial-gradient(circle at 40% 40%, #d79f1e 5%, #d79f1e00 15%)",
  "radial-gradient(circle at 60% 60%, #5a922c 10%, #5a922c00 20%)",
  "radial-gradient(circle at 40% 60%, #4c7894 10%, #4c789400 20%)",
  "repeating-conic-gradient(from 236.84deg at 50% 50%, #dd7bbb 0%, #d79f1e calc(25% / var(--repeating-conic-gradient-times)), #5a922c calc(50% / var(--repeating-conic-gradient-times)), #4c7894 calc(75% / var(--repeating-conic-gradient-times)), #dd7bbb calc(100% / var(--repeating-conic-gradient-times)))",
].join(", ");

const gradientWhite =
  "repeating-conic-gradient(from 236.84deg at 50% 50%, var(--black), var(--black) calc(25% / var(--repeating-conic-gradient-times)))";

function handleMove(e?: { x: number; y: number }) {
  if (!containerRef.value) return;
  if (animationFrameId) cancelAnimationFrame(animationFrameId);
  animationFrameId = requestAnimationFrame(() => {
    const element = containerRef.value;
    if (!element) return;

    const { left, top, width, height } = element.getBoundingClientRect();
    const mouseX = e?.x ?? lastPosition.x;
    const mouseY = e?.y ?? lastPosition.y;
    if (e) {
      lastPosition.x = mouseX;
      lastPosition.y = mouseY;
    }

    const centerX = left + width * 0.5;
    const centerY = top + height * 0.5;
    const distanceFromCenter = Math.hypot(mouseX - centerX, mouseY - centerY);
    const inactiveRadius = 0.5 * Math.min(width, height) * props.inactiveZone;

    if (distanceFromCenter < inactiveRadius) {
      element.style.setProperty("--active", "0");
      return;
    }

    const isActive =
      mouseX > left - props.proximity &&
      mouseX < left + width + props.proximity &&
      mouseY > top - props.proximity &&
      mouseY < top + height + props.proximity;

    element.style.setProperty("--active", isActive ? "1" : "0");
    if (!isActive) return;

    const currentAngle =
      parseFloat(element.style.getPropertyValue("--start")) || 0;
    const targetAngle =
      (180 * Math.atan2(mouseY - centerY, mouseX - centerX)) / Math.PI + 90;
    const angleDiff = ((targetAngle - currentAngle + 180) % 360) - 180;

    animate(currentAngle, currentAngle + angleDiff, {
      duration: props.movementDuration,
      ease: [0.16, 1, 0.3, 1],
      onUpdate: (value: number) =>
        element.style.setProperty("--start", String(value)),
    });
  });
}

function handleScroll() {
  handleMove();
}
function handlePointerMove(e: PointerEvent) {
  handleMove(e);
}

onMounted(() => {
  if (props.disabled) return;
  window.addEventListener("scroll", handleScroll, { passive: true });
  document.body.addEventListener("pointermove", handlePointerMove, {
    passive: true,
  });
});

onUnmounted(() => {
  if (animationFrameId) cancelAnimationFrame(animationFrameId);
  window.removeEventListener("scroll", handleScroll);
  document.body.removeEventListener("pointermove", handlePointerMove);
});
</script>

<template>
  <!-- Static border overlay — shown when glow=true (always-on) or when disabled -->
  <div
    class="ge-border"
    :class="{
      'ge-border-visible': glow,
      'ge-border-white': variant === 'white',
      'ge-border-show': disabled,
    }"
  />

  <!-- Animated glow container — hidden when disabled -->
  <div
    v-if="!disabled"
    ref="containerRef"
    class="ge-container"
    :class="{ 'ge-blur': blur > 0 }"
    :style="{
      '--blur': `${blur}px`,
      '--spread': spread,
      '--start': '0',
      '--active': '0',
      '--glowingeffect-border-width': `${borderWidth}px`,
      '--repeating-conic-gradient-times': '5',
      '--gradient': variant === 'white' ? gradientWhite : gradientDefault,
    } as any"
  >
    <div class="ge-glow" />
  </div>
</template>

<style scoped>
/* Static border fallback (no mouse tracking) */
.ge-border {
  pointer-events: none;
  position: absolute;
  inset: -1px;
  display: none;
  border-radius: inherit;
  border: 1px solid rgba(255, 255, 255, 0.15);
  opacity: 0;
  transition: opacity 300ms;
}

.ge-border-visible {
  opacity: 1;
}

.ge-border-white {
  border-color: white;
}

/* !important to override display:none when disabled=true */
.ge-border-show {
  display: block !important;
}

/* Animated glow wrapper */
.ge-container {
  pointer-events: none;
  position: absolute;
  inset: 0;
  border-radius: inherit;
  transition: opacity 300ms;
}

.ge-blur {
  filter: blur(var(--blur));
}

/* Inner glow shell — the ::after does the real work */
.ge-glow {
  border-radius: inherit;
  position: relative;
  height: 100%;
  width: 100%;
}

.ge-glow::after {
  content: "";
  border-radius: inherit;
  position: absolute;
  inset: calc(-1 * var(--glowingeffect-border-width));
  border: var(--glowingeffect-border-width) solid transparent;

  /* The full multi-color conic gradient background */
  background: var(--gradient);
  background-attachment: fixed;

  /* Fade in/out based on proximity */
  opacity: var(--active);
  transition: opacity 300ms;

  /*
    Dual-layer mask:
    - Layer 1 (padding-box): hides everything inside the border → only border ring visible
    - Layer 2 (border-box): conic sweep reveals just the arc near the cursor
    mask-composite: intersect → only pixels visible in BOTH layers are shown
  */
  -webkit-mask-clip: padding-box, border-box;
  mask-clip: padding-box, border-box;
  -webkit-mask-composite: destination-in;
  mask-composite: intersect;
  -webkit-mask-image: linear-gradient(#0000, #0000),
    conic-gradient(
      from calc((var(--start) - var(--spread)) * 1deg),
      #00000000 0deg,
      #fff,
      #00000000 calc(var(--spread) * 2deg)
    );
  mask-image: linear-gradient(#0000, #0000),
    conic-gradient(
      from calc((var(--start) - var(--spread)) * 1deg),
      #00000000 0deg,
      #fff,
      #00000000 calc(var(--spread) * 2deg)
    );
}
</style>
