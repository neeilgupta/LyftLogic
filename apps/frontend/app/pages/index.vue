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
      <div class="badge">Simple • Consistent • Made for progress</div>

      <h1 class="title">
        LyftLogic
        <span class="title-accent">Workout + Nutrition</span>
        planning that you’ll actually stick to.
      </h1>

      <p class="subtitle">
        Get a clear plan for training and meals based on your goals—built to feel realistic,
        repeatable, and easy to follow day-to-day.
      </p>

      <div class="cta-row">
        <NuxtLink to="/generate" class="btn btn-primary">
          Build my workout
        </NuxtLink>
        <NuxtLink to="/nutrition" class="btn btn-secondary">
          Build my nutrition
        </NuxtLink>
        <NuxtLink to="/roadmap" class="btn btn-ghost">
          See what’s next
        </NuxtLink>
      </div>

      <div class="hero-stats">
        <div class="stat">
          <div class="stat-k">Clear structure</div>
          <div class="stat-v">No overwhelm, just the plan</div>
        </div>
        <div class="stat">
          <div class="stat-k">Built for real life</div>
          <div class="stat-v">Simple choices you can repeat</div>
        </div>
        <div class="stat">
          <div class="stat-k">Easy to improve</div>
          <div class="stat-v">Adjust and keep moving forward</div>
        </div>
      </div>
    </section>

    <!-- FEATURES -->
    <section class="grid">
      <article class="ll-card">
        <div class="card-title">Workout Plan</div>
        <div class="card-sub">
          A training plan that fits your schedule and goal, with a clean day-by-day layout.
        </div>

        <ul class="bullets">
          <li>Built around your goal</li>
          <li>Easy-to-follow days and exercises</li>
          <li>Consistent structure you can stick with</li>
        </ul>

        <NuxtLink to="/generate" class="btn btn-primary" style="margin-top: 14px;">
          Open workout
        </NuxtLink>
      </article>

      <article class="ll-card">
        <div class="card-title">Nutrition Plan</div>
        <div class="card-sub">
          Meal ideas that match your calorie goal and preferences, without feeling restrictive.
        </div>

        <ul class="bullets">
          <li>Diet preferences and allergies supported</li>
          <li>Simple, repeatable meals</li>
          <li>Made to help you stay on track</li>
        </ul>

        <NuxtLink to="/nutrition" class="btn btn-secondary" style="margin-top: 14px;">
          Open nutrition
        </NuxtLink>
      </article>
    </section>

    <!-- ABOUT -->
    <section class="about">
      <article class="ll-card">
        <div class="card-title">What this is</div>
        <p class="p">
          LyftLogic is a planning tool that turns your goal into something actionable: a workout plan,
          a nutrition plan, and a simple structure you can follow week after week.
        </p>
      </article>

      <article class="ll-card ll-card-muted">
        <div class="card-title">Who made it</div>
        <p class="p">
          I’m Neeil. I built LyftLogic because I wanted a plan that feels clear and realistic—not
          confusing, not random, and not hard to follow.
        </p>

        <div class="mini-cta">
          <NuxtLink to="/roadmap" class="link">
            See what’s coming →
          </NuxtLink>
        </div>
      </article>
    </section>

    <!-- FOOTER -->
    <footer class="footer">
      <div class="footer-line"></div>
      <div style="opacity: 0.75;">
        A cleaner way to plan training and nutrition—built for consistency.
      </div>
    </footer>
  </main>
</template>


<style scoped>
/* Keep consistent app background */
:global(html),
:global(body) {
  background: #0b0f19;
  margin: 0;
}

:global(#__nuxt) {
  background: #0b0f19;
  min-height: 100vh;
}

.home-page {
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

.home-page > * {
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
  gap: 8px;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid var(--border);
  background: rgba(17, 24, 39, 0.55);
  box-shadow: var(--shadow);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.2px;
  color: rgba(255, 255, 255, 0.9);
}

.title {
  margin: 14px 0 10px;
  font-size: 40px;
  line-height: 1.08;
  font-weight: 950;
  letter-spacing: -0.03em;
}

.title-accent {
  color: rgba(167, 139, 250, 1);
}

.subtitle {
  margin: 0 0 18px;
  opacity: 0.85;
  font-size: 15.5px;
  line-height: 1.6;
  max-width: 820px;
}

.cta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin: 14px 0 18px;
}

.hero-stats {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-top: 10px;
}

.stat {
  border: 1px solid var(--border);
  background: rgba(17, 24, 39, 0.55);
  border-radius: 14px;
  padding: 14px;
  box-shadow: var(--shadow);
}

.stat-k {
  font-weight: 900;
  font-size: 13px;
  margin-bottom: 6px;
}

.stat-v {
  font-size: 13px;
  opacity: 0.8;
}

/* CARDS + GRID */
.ll-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 20px;
  box-shadow: var(--shadow);
}

.ll-card-muted {
  background: rgba(17, 24, 39, 0.55);
}

.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 14px;
  margin-top: 18px;
}

.about {
  display: grid;
  grid-template-columns: 1.15fr 0.85fr;
  gap: 14px;
  margin-top: 14px;
}

.card-title {
  font-weight: 900;
  font-size: 16px;
  margin-bottom: 8px;
  letter-spacing: -0.01em;
}

.card-sub {
  opacity: 0.82;
  font-size: 14px;
  line-height: 1.5;
  margin-bottom: 10px;
}

.p {
  margin: 0;
  opacity: 0.85;
  line-height: 1.6;
  font-size: 14px;
}

.bullets {
  margin: 10px 0 0;
  padding-left: 18px;
  opacity: 0.9;
  line-height: 1.6;
  font-size: 14px;
}

.mini-cta {
  margin-top: 12px;
}

.link {
  color: rgba(167, 139, 250, 1);
  text-decoration: none;
  font-weight: 800;
}

.link:hover {
  text-decoration: underline;
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
  .home-page {
    padding: 28px 18px 24px;
  }
  .title {
    font-size: 34px;
  }
  .hero-stats {
    grid-template-columns: 1fr;
  }
  .grid {
    grid-template-columns: 1fr;
  }
  .about {
    grid-template-columns: 1fr;
  }
}
</style>
