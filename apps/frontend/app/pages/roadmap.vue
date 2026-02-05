<script setup lang="ts">
useHead({
  title: "Roadmap • LyftLogic",
  meta: [
    {
      name: "description",
      content:
        "LyftLogic roadmap: deterministic training + nutrition planning, versioning, persistence, and next milestones.",
    },
  ],
})

type Item = { title: string; body: string; status: "done" | "next" | "later" }

const phases: { label: string; subtitle: string; items: Item[] }[] = [
  {
    label: "Now",
    subtitle: "What’s already working (v1 demo-ready)",
    items: [
      {
        title: "Training: deterministic plans + diffs",
        body:
          "Generate, regenerate, diff, and restore. Realistic lifting rules enforced in code (volume/rest/warmups/split logic).",
        status: "done",
      },
      {
        title: "Nutrition: deterministic plans + safety",
        body:
          "Fail-closed allergens, diet constraints, slot-based structure, deterministic regenerate with diffs + explanations.",
        status: "done",
      },
      {
        title: "Calorie repair pass (no random hacks)",
        body:
          "If meals undershoot target calories, a deterministic post-pass adds safe boosters (slot-aware, diet-safe, allergy-safe).",
        status: "done",
      },
      {
        title: "User-facing clarity (not a tracker)",
        body:
          "Daily aim macros (protein 0.8g/lb, carb-forward remainder), plan totals, debug info hidden behind a toggle.",
        status: "done",
      },
    ],
  },
  {
    label: "Next",
    subtitle: "Big product unlocks (most important)",
    items: [
      {
        title: "Accounts + saved plans",
        body:
          "Users can save training + nutrition plans, come back later, and keep iterating without re-generating from scratch.",
        status: "next",
      },
      {
        title: "Version persistence + restore (nutrition parity)",
        body:
          "Store version snapshots per user, show version history, and allow restore across both systems with consistent semantics.",
        status: "next",
      },
      {
        title: "Premium loading experience",
        body:
          "15–20s generation should feel intentional: skeleton cards + status messages + disabled inputs while generating.",
        status: "next",
      },
    ],
  },
  {
    label: "Later",
    subtitle: "Good ideas — intentionally staged",
    items: [
      {
        title: "Unified Plan dashboard",
        body:
          "A single overview page that shows training + nutrition together, with a unified version timeline and restore UX.",
        status: "later",
      },
      {
        title: "Deterministic edit flows (selective “chat”)",
        body:
          "Requests like “swap lunch protein” or “reduce calories by 200” → deterministic changes → diff + explanation.",
        status: "later",
      },
      {
        title: "Export / share",
        body:
          "PDF export and shareable snapshots (useful for demos, coaches, and keeping a record).",
        status: "later",
      },
    ],
  },
]
</script>

<template>
  <main class="roadmap-page">
    <!-- HERO -->
    <section class="hero">
      <div class="badge">LyftLogic Roadmap</div>

      <h1 class="title">
        Built for consistency.
        <span class="title-accent">Shipped in phases.</span>
      </h1>

      <p class="subtitle">
        LyftLogic is a deterministic fitness + nutrition planner. This roadmap shows what’s already
        working today and what’s next to make it a true “save and iterate” product.
      </p>

      <div class="cta-row">
        <NuxtLink to="/generate" class="btn btn-primary">Go to Workout</NuxtLink>
        <NuxtLink to="/nutrition" class="btn btn-secondary">Go to Nutrition</NuxtLink>
        <NuxtLink to="/" class="btn btn-ghost">Back Home</NuxtLink>
      </div>
    </section>

    <!-- PHASES -->
    <section class="phases">
      <div v-for="(p, i) in phases" :key="i" class="phase">
        <div class="phase-head">
          <div class="phase-title">{{ p.label }}</div>
          <div class="phase-sub">{{ p.subtitle }}</div>
        </div>

        <div class="grid">
          <article v-for="(it, j) in p.items" :key="j" class="ll-card">
            <div class="card-top">
              <div class="card-title">{{ it.title }}</div>
              <div
                class="status"
                :class="{
                  done: it.status === 'done',
                  next: it.status === 'next',
                  later: it.status === 'later',
                }"
              >
                <span v-if="it.status === 'done'">Shipped</span>
                <span v-else-if="it.status === 'next'">Next</span>
                <span v-else>Later</span>
              </div>
            </div>

            <div class="card-body">
              {{ it.body }}
            </div>
          </article>
        </div>
      </div>
    </section>

    <!-- PRINCIPLES -->
    <section class="principles ll-card ll-card-muted">
      <div class="card-title" style="margin-bottom: 8px;">Principles</div>
      <ul class="bullets">
        <li><strong>Determinism is mandatory:</strong> same inputs → same outputs.</li>
        <li><strong>AI drafts, rules decide:</strong> constraints are enforced in code.</li>
        <li><strong>Plans evolve through versions:</strong> diffs + explanations + restore.</li>
        <li><strong>Clarity over tracking:</strong> aims + structure, not micromanagement.</li>
      </ul>
    </section>

    <footer class="footer">
      <div class="footer-line"></div>
      <div style="opacity: 0.75;">
        Want to see progress? Start with Workout or Nutrition — the roadmap matches what’s in the app.
      </div>
    </footer>
  </main>
</template>

<style scoped>
/* Page background parity */
:global(html),
:global(body) {
  background: #0b0f19;
  margin: 0;
}

:global(#__nuxt) {
  background: #0b0f19;
  min-height: 100vh;
}

.roadmap-page {
  --accent: #7c3aed;
  --accent-dark: #6d28d9;
  --ink: #f8fafc;
  --muted: #a1a1aa;
  --page: #0b0f19;
  --surface: #111827;
  --surface-2: #0f172a;
  --border: rgba(255, 255, 255, 0.1);
  --shadow: 0 10px 30px rgba(0, 0, 0, 0.35);

  background: radial-gradient(1100px 500px at 20% 0%, rgba(124, 58, 237, 0.18), rgba(0, 0, 0, 0)),
    var(--page);
  color: var(--ink);
  min-height: 100vh;
  padding: 36px 48px 28px;
  font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
}

.roadmap-page > * {
  max-width: 980px;
  margin-left: auto;
  margin-right: auto;
}

/* HERO */
.hero {
  padding: 6px 0 18px;
}

.badge {
  display: inline-flex;
  align-items: center;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: rgba(17, 24, 39, 0.55);
  box-shadow: var(--shadow);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.2px;
  color: rgba(255, 255, 255, 0.9);
}

.title {
  margin: 14px 0 10px;
  font-size: 38px;
  line-height: 1.08;
  font-weight: 950;
  letter-spacing: -0.03em;
}

.title-accent {
  color: rgba(167, 139, 250, 1);
}

.subtitle {
  margin: 0 0 16px;
  opacity: 0.85;
  font-size: 15.5px;
  line-height: 1.6;
  max-width: 820px;
}

.cta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin: 14px 0 8px;
}

/* PHASES */
.phases {
  margin-top: 12px;
}

.phase {
  margin-top: 14px;
}

.phase-head {
  margin: 6px 0 10px;
}

.phase-title {
  font-weight: 950;
  font-size: 16px;
  letter-spacing: -0.01em;
}

.phase-sub {
  font-size: 13px;
  opacity: 0.78;
  margin-top: 4px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
}

.ll-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 16px;
  box-shadow: var(--shadow);
}

.ll-card-muted {
  background: rgba(17, 24, 39, 0.55);
}

.card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 8px;
}

.card-title {
  font-weight: 900;
  font-size: 15px;
  letter-spacing: -0.01em;
}

.card-body {
  font-size: 13.5px;
  opacity: 0.86;
  line-height: 1.55;
}

.status {
  font-size: 11px;
  font-weight: 900;
  padding: 4px 10px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(255, 255, 255, 0.04);
  white-space: nowrap;
  opacity: 0.95;
}

.status.done {
  border-color: rgba(16, 185, 129, 0.35);
  background: rgba(16, 185, 129, 0.08);
}

.status.next {
  border-color: rgba(167, 139, 250, 0.45);
  background: rgba(124, 58, 237, 0.12);
}

.status.later {
  border-color: rgba(255, 255, 255, 0.14);
  background: rgba(255, 255, 255, 0.04);
}

/* PRINCIPLES */
.bullets {
  margin: 10px 0 0;
  padding-left: 18px;
  opacity: 0.92;
  line-height: 1.6;
  font-size: 14px;
}

/* BUTTONS */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 11px 16px;
  border-radius: 10px;
  font-weight: 800;
  font-size: 14px;
  text-decoration: none;
  border: 1px solid transparent;
  transition: background 140ms ease, box-shadow 140ms ease, opacity 140ms ease, transform 140ms ease;
  width: fit-content;
  cursor: pointer;
}

.btn-primary {
  background: var(--accent);
  border-color: var(--accent);
  color: #fff;
}

.btn-primary:hover {
  background: var(--accent-dark);
  transform: translateY(-1px);
}

.btn-secondary {
  background: rgba(124, 58, 237, 0.12);
  border-color: rgba(124, 58, 237, 0.35);
  color: rgba(255, 255, 255, 0.92);
}

.btn-secondary:hover {
  background: rgba(124, 58, 237, 0.18);
  transform: translateY(-1px);
}

.btn-ghost {
  background: transparent;
  border-color: rgba(255, 255, 255, 0.16);
  color: rgba(255, 255, 255, 0.88);
}

.btn-ghost:hover {
  background: rgba(255, 255, 255, 0.06);
  transform: translateY(-1px);
}

/* FOOTER */
.footer {
  margin-top: 22px;
  padding-top: 18px;
  padding-bottom: 6px;
}

.footer-line {
  height: 1px;
  background: rgba(255, 255, 255, 0.08);
  margin-bottom: 14px;
}

/* RESPONSIVE */
@media (max-width: 860px) {
  .roadmap-page {
    padding: 28px 18px 24px;
  }
  .title {
    font-size: 32px;
  }
  .grid {
    grid-template-columns: 1fr;
  }
}
</style>
