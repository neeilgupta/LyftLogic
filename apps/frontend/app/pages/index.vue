<script setup lang="ts">
useHead({
  title: "LyftLogic",
  meta: [
    {
      name: "description",
      content:
        "LyftLogic helps you build workout and nutrition plans that are simple, consistent, and easy to follow.",
    },
  ],
})
</script>

<template>
  <main class="home-page">
    <!-- HERO -->
    <section class="hero">
      <div class="hero-eyebrow">
        <span class="eyebrow-dot"></span>
        <span>Deterministic · Versioned · No randomness</span>
      </div>

      <h1 class="hero-title">
        Training plans.<br>
        Nutrition plans.<br>
        <span class="hero-accent">Built without guessing.</span>
      </h1>

      <p class="hero-sub">
        A rules-based engine that turns your goals into a structured plan.
        Same inputs, same output — every time.
      </p>

      <div class="cta-row">
        <NuxtLink to="/generate" class="btn btn-primary">Build workout plan</NuxtLink>
        <NuxtLink to="/nutrition" class="btn btn-outline">Build nutrition plan</NuxtLink>
        <NuxtLink to="/roadmap" class="btn btn-ghost">Roadmap →</NuxtLink>
      </div>

      <div class="hero-stats">
        <div class="stat">
          <GlowingEffect :spread="40" :glow="true" :disabled="false" :proximity="64" :inactive-zone="0.01" :border-width="2" />
          <div class="stat-label">Deterministic</div>
          <div class="stat-value">Same inputs → same plan, always</div>
        </div>
        <div class="stat">
          <GlowingEffect :spread="40" :glow="true" :disabled="false" :proximity="64" :inactive-zone="0.01" :border-width="2" />
          <div class="stat-label">Versioned</div>
          <div class="stat-value">Every edit creates a snapshot + diff</div>
        </div>
        <div class="stat">
          <GlowingEffect :spread="40" :glow="true" :disabled="false" :proximity="64" :inactive-zone="0.01" :border-width="2" />
          <div class="stat-label">Rules-based</div>
          <div class="stat-value">No AI hallucinations in the output</div>
        </div>
      </div>
    </section>

    <!-- SCROLL ANIMATION DEMO -->
    <section class="scroll-section">
      <ContainerScrollAnimation>
        <template #title>
          <p class="scroll-eyebrow">Output preview</p>
          <h2 class="scroll-title">
            Your plan, structured.<br>
            <span class="hero-accent">No guesswork in the output.</span>
          </h2>
        </template>

        <!-- Static mockup of a generated workout plan -->
        <div class="plan-mock">
          <div class="plan-mock__header">
            <span class="plan-mock__tag">Training</span>
            <span class="plan-mock__meta">Hypertrophy · Intermediate · 4 days/week</span>
          </div>

          <div class="plan-mock__day">
            <div class="plan-mock__day-label">Week 1 · Day 1 · Upper</div>
            <div class="plan-mock__exercises">
              <div class="plan-mock__ex">
                <span class="plan-mock__ex-name">Barbell Bench Press</span>
                <span class="plan-mock__ex-detail">3 × 8–12 · 120s rest</span>
              </div>
              <div class="plan-mock__ex">
                <span class="plan-mock__ex-name">Cable Row (Seated)</span>
                <span class="plan-mock__ex-detail">3 × 8–12 · 90s rest</span>
              </div>
              <div class="plan-mock__ex">
                <span class="plan-mock__ex-name">Overhead Press</span>
                <span class="plan-mock__ex-detail">3 × 8–12 · 120s rest</span>
              </div>
              <div class="plan-mock__ex">
                <span class="plan-mock__ex-name">Lat Pulldown</span>
                <span class="plan-mock__ex-detail">3 × 8–12 · 90s rest</span>
              </div>
              <div class="plan-mock__ex">
                <span class="plan-mock__ex-name">Cable Lateral Raise</span>
                <span class="plan-mock__ex-detail">2 × 12–15 · 60s rest</span>
              </div>
            </div>
          </div>

          <div class="plan-mock__footer">
            <span>Rules engine</span>
            <span class="plan-mock__sep">·</span>
            <span>100% deterministic</span>
            <span class="plan-mock__sep">·</span>
            <span>v1 snapshot</span>
          </div>
        </div>
      </ContainerScrollAnimation>
    </section>

    <!-- FEATURE CARDS -->
    <section class="grid-2col">
      <article class="feature-card">
        <GlowingEffect :spread="40" :glow="true" :disabled="false" :proximity="64" :inactive-zone="0.01" :border-width="2" />
        <div class="feature-tag">Training</div>
        <div class="feature-title">Workout Plan</div>
        <div class="feature-sub">
          A training split built around your goal, schedule, and equipment.
          Day-by-day, no ambiguity.
        </div>
        <ul class="feature-list">
          <li>FB / Upper-Lower / PPL splits</li>
          <li>Equipment-aware exercise selection</li>
          <li>Versioned edits with full diff history</li>
        </ul>
        <NuxtLink to="/generate" class="btn btn-primary feature-btn">Open workout →</NuxtLink>
      </article>

      <article class="feature-card">
        <GlowingEffect :spread="40" :glow="true" :disabled="false" :proximity="64" :inactive-zone="0.01" :border-width="2" />
        <div class="feature-tag">Nutrition</div>
        <div class="feature-title">Nutrition Plan</div>
        <div class="feature-sub">
          Meal templates scaled to your calorie target, diet, and allergy constraints.
          Deterministic macro math.
        </div>
        <ul class="feature-list">
          <li>Mifflin-St Jeor BMR + TDEE</li>
          <li>Diet + allergen enforcement (fail-closed)</li>
          <li>Slot-based meal generation</li>
        </ul>
        <NuxtLink to="/nutrition" class="btn btn-outline feature-btn">Open nutrition →</NuxtLink>
      </article>
    </section>

    <!-- ABOUT -->
    <section class="grid-about">
      <article class="about-card about-card-wide">
        <GlowingEffect :spread="40" :glow="true" :disabled="false" :proximity="64" :inactive-zone="0.01" :border-width="2" />
        <div class="about-label">What this is</div>
        <p class="about-p">
          LyftLogic is a planning engine — not a chatbot. It turns a fixed set of inputs
          into a structured workout or nutrition plan through deterministic rule trees.
          The same request always produces the same result.
        </p>
      </article>

      <article class="about-card">
        <GlowingEffect :spread="40" :glow="true" :disabled="false" :proximity="64" :inactive-zone="0.01" :border-width="2" />
        <div class="about-label">Who built it</div>
        <p class="about-p">
          Built by Neeil — a tool for plans that feel clear and
          repeatable, not random.
        </p>
        <NuxtLink to="/roadmap" class="roadmap-link">See what's coming →</NuxtLink>
      </article>
    </section>

    <!-- FOOTER -->
    <footer class="footer">
      <div class="footer-rule"></div>
      <div class="footer-text">
        Lyft<span class="accent">Logic</span> — a deterministic fitness planning engine
      </div>
    </footer>
  </main>
</template>


<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800;900&family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600&display=swap');

:global(html),
:global(body) {
  background: #090907;
  margin: 0;
}

:global(#__nuxt) {
  background: #090907;
  min-height: 100vh;
}

.home-page {
  background-color: #090907;
  background-image:
    linear-gradient(rgba(124, 58, 237, 0.025) 1px, transparent 1px),
    linear-gradient(90deg, rgba(124, 58, 237, 0.025) 1px, transparent 1px);
  background-size: 44px 44px;
  color: #f0ede6;
  min-height: 100vh;
  padding: 48px 48px 28px;
  font-family: 'DM Sans', sans-serif;
}

.home-page > * {
  max-width: 960px;
  margin-left: auto;
  margin-right: auto;
}

/* HERO */
.hero {
  padding: 16px 0 24px;
}

.hero-eyebrow {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.08em;
  color: rgba(240, 237, 230, 0.4);
  text-transform: uppercase;
  margin-bottom: 20px;
}

.eyebrow-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #7c3aed;
  opacity: 0.7;
  flex-shrink: 0;
}

.hero-title {
  font-family: 'Syne', sans-serif;
  font-size: 52px;
  font-weight: 900;
  line-height: 1.05;
  letter-spacing: -0.03em;
  margin: 0 0 18px;
  color: #f0ede6;
}

.hero-accent {
  color: #7c3aed;
}

.hero-sub {
  font-size: 16px;
  line-height: 1.65;
  color: rgba(240, 237, 230, 0.6);
  max-width: 580px;
  margin: 0 0 28px;
}

/* CTA */
.cta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-bottom: 32px;
}

.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 11px 20px;
  border-radius: 3px;
  font-family: 'DM Mono', monospace;
  font-size: 12px;
  font-weight: 500;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  text-decoration: none;
  border: 1px solid transparent;
  cursor: pointer;
  transition: background 0.15s, border-color 0.15s, color 0.15s, transform 0.1s;
}

.btn-primary {
  background: #7c3aed;
  border-color: #7c3aed;
  color: #ffffff;
}

.btn-primary:hover {
  background: #6d28d9;
  transform: translateY(-1px);
}

.btn-outline {
  background: rgba(124, 58, 237, 0.06);
  border-color: rgba(124, 58, 237, 0.3);
  color: rgba(124, 58, 237, 0.85);
}

.btn-outline:hover {
  background: rgba(124, 58, 237, 0.1);
  border-color: rgba(124, 58, 237, 0.55);
  color: #7c3aed;
  transform: translateY(-1px);
}

.btn-ghost {
  background: transparent;
  border-color: rgba(255, 255, 255, 0.1);
  color: rgba(240, 237, 230, 0.6);
}

.btn-ghost:hover {
  background: rgba(255, 255, 255, 0.04);
  color: rgba(240, 237, 230, 0.9);
  transform: translateY(-1px);
}

/* HERO STATS */
.hero-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}

.stat {
  position: relative;
  background: #111110;
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 4px;
  padding: 16px 18px;
}

.stat-label {
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #7c3aed;
  margin-bottom: 6px;
}

.stat-value {
  font-size: 13px;
  color: rgba(240, 237, 230, 0.6);
  line-height: 1.4;
}

/* FEATURE CARDS */
.grid-2col {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-top: 20px;
}

.feature-card {
  position: relative;
  background: #111110;
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-left: 3px solid #7c3aed;
  border-radius: 4px;
  padding: 24px 22px;
}

.feature-tag {
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(124, 58, 237, 0.6);
  margin-bottom: 10px;
}

.feature-title {
  font-family: 'Syne', sans-serif;
  font-size: 20px;
  font-weight: 800;
  color: #f0ede6;
  margin-bottom: 10px;
  letter-spacing: -0.02em;
}

.feature-sub {
  font-size: 14px;
  line-height: 1.6;
  color: rgba(240, 237, 230, 0.55);
  margin-bottom: 16px;
}

.feature-list {
  margin: 0 0 20px;
  padding: 0;
  list-style: none;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.feature-list li {
  font-size: 13px;
  color: rgba(240, 237, 230, 0.7);
  padding-left: 16px;
  position: relative;
}

.feature-list li::before {
  content: '—';
  position: absolute;
  left: 0;
  color: #7c3aed;
  opacity: 0.5;
  font-size: 11px;
}

.feature-btn {
  margin-top: auto;
}

/* ABOUT */
.grid-about {
  display: grid;
  grid-template-columns: 1.2fr 0.8fr;
  gap: 12px;
  margin-top: 12px;
}

.about-card {
  position: relative;
  background: #111110;
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-radius: 4px;
  padding: 22px 22px;
}

.about-label {
  font-family: 'DM Mono', monospace;
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(240, 237, 230, 0.35);
  margin-bottom: 12px;
}

.about-p {
  font-size: 14px;
  line-height: 1.65;
  color: rgba(240, 237, 230, 0.65);
  margin: 0 0 12px;
}

.roadmap-link {
  font-family: 'DM Mono', monospace;
  font-size: 12px;
  color: #7c3aed;
  text-decoration: none;
  opacity: 0.8;
  letter-spacing: 0.03em;
  transition: opacity 0.15s;
}

.roadmap-link:hover {
  opacity: 1;
  text-decoration: underline;
  text-underline-offset: 3px;
}

/* FOOTER */
.footer {
  margin-top: 28px;
  padding-bottom: 10px;
}

.footer-rule {
  height: 1px;
  background: rgba(255, 255, 255, 0.06);
  margin-bottom: 14px;
}

.footer-text {
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  letter-spacing: 0.04em;
  color: rgba(240, 237, 230, 0.25);
}

.accent {
  color: #7c3aed;
}

/* SCROLL ANIMATION SECTION */
.scroll-section {
  max-width: 960px;
  margin: 0 auto;
}

.scroll-eyebrow {
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: rgba(124, 58, 237, 0.6);
  margin: 0 0 14px;
}

.scroll-title {
  font-family: 'Syne', sans-serif;
  font-size: 36px;
  font-weight: 900;
  line-height: 1.1;
  letter-spacing: -0.03em;
  margin: 0;
  color: #f0ede6;
}

@media (min-width: 768px) {
  .scroll-title {
    font-size: 48px;
  }
}

/* Plan mockup inside the scroll card */
.plan-mock {
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 20px 24px;
  font-family: 'DM Mono', monospace;
  color: #f0ede6;
}

@media (min-width: 768px) {
  .plan-mock {
    padding: 28px 32px;
  }
}

.plan-mock__header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  padding-bottom: 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.plan-mock__tag {
  font-size: 10px;
  font-weight: 500;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  padding: 3px 8px;
  border-radius: 2px;
  border: 1px solid rgba(124, 58, 237, 0.3);
  background: rgba(124, 58, 237, 0.07);
  color: rgba(124, 58, 237, 0.85);
}

.plan-mock__meta {
  font-size: 11px;
  letter-spacing: 0.04em;
  color: rgba(240, 237, 230, 0.35);
}

.plan-mock__day {
  flex: 1;
}

.plan-mock__day-label {
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #7c3aed;
  margin-bottom: 14px;
}

.plan-mock__exercises {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.plan-mock__ex {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-left: 2px solid rgba(124, 58, 237, 0.3);
  border-radius: 3px;
}

.plan-mock__ex-name {
  font-size: 13px;
  color: rgba(240, 237, 230, 0.88);
  font-family: 'DM Sans', sans-serif;
}

.plan-mock__ex-detail {
  font-size: 11px;
  letter-spacing: 0.04em;
  color: rgba(240, 237, 230, 0.38);
  white-space: nowrap;
}

.plan-mock__footer {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
  font-size: 10px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(240, 237, 230, 0.2);
}

.plan-mock__sep {
  color: rgba(124, 58, 237, 0.3);
}

/* RESPONSIVE */
@media (max-width: 860px) {
  .home-page {
    padding: 32px 20px 24px;
  }

  .hero-title {
    font-size: 38px;
  }

  .hero-stats {
    grid-template-columns: 1fr;
  }

  .grid-2col {
    grid-template-columns: 1fr;
  }

  .grid-about {
    grid-template-columns: 1fr;
  }
}
</style>
