<template>
  <main style="padding: 20px; font-family: system-ui; max-width: 900px; margin: 0 auto;">
    <nav style="margin-bottom: 16px;">
      <NuxtLink to="/" style="text-decoration: underline;">← Back to home</NuxtLink>
      <span style="margin: 0 10px;">·</span>
      <NuxtLink to="/generate" style="text-decoration: underline;">Generate another plan</NuxtLink>
    </nav>

    <p v-if="pending">Loading plan…</p>
    <p v-else-if="errorMsg" style="color: red;">{{ errorMsg }}</p>

    <section v-else-if="output">
      <h1 style="margin: 0 0 8px;">{{ output.title }}</h1>
      <p style="margin: 0 0 18px; opacity: 0.85;">{{ output.summary }}</p>

      <!-- simple day nav -->
      <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 16px;">
        <a
          v-for="(day, i) in output.weekly_split"
          :key="i"
          :href="`#day-${i}`"
          style="padding: 6px 10px; border: 1px solid #ddd; border-radius: 999px; text-decoration: none;"
        >
          {{ day.day }}
        </a>
      </div>

      <article
        v-for="(day, i) in output.weekly_split"
        :key="i"
        :id="`day-${i}`"
        style="border: 1px solid #eee; border-radius: 12px; padding: 14px; margin-bottom: 14px;"
      >
        <h2 style="margin: 0 0 6px;">{{ day.day }} — {{ day.focus }}</h2>

        <Section title="Warmup" :items="normalizeToStrings(day.warmup)" />
        <Section title="Main" :items="normalizeToStrings(day.main)" />
        <Section title="Accessories" :items="normalizeToStrings(day.accessories)" />
        <Section title="Finisher" :items="normalizeToStrings(day.finisher)" />
        <Section title="Cooldown" :items="normalizeToStrings(day.cooldown)" />
      </article>
    </section>

    <p v-else>No plan data found.</p>
  </main>
</template>

<script setup lang="ts">
import { computed, defineComponent, h } from "vue";
import type { PropType } from "vue";
import { useRoute } from "vue-router";
import { usePlans } from "../../../composables/usePlans";

type Lift = {
  name: string;
  sets?: number;
  reps?: string;
  rpe?: number | null;
  rest_seconds?: number | null;
  notes?: string;
};

type Day = {
  day: string;
  focus: string;
  warmup?: any[];
  main?: any[];
  accessories?: any[];
  finisher?: any[];
  cooldown?: any[];
};

type PlanOutput = {
  title: string;
  summary: string;
  weekly_split: Day[];
};

type PlanDetail = {
  id: number;
  created_at?: string;
  title?: string;
  input?: any;
  output?: PlanOutput;
  // some endpoints might return output directly; we handle both
  summary?: string;
  weekly_split?: Day[];
};

const route = useRoute();
const id = computed(() => String(route.params.id));

const { getPlan } = usePlans();

const { data: plan, pending, error } = await useAsyncData(
  () => `plan-${id.value}`,
  () => getPlan(id.value)
);

const errorMsg = computed(() => {
  const e: any = error.value;
  return e?.data?.detail ?? e?.message ?? (e ? String(e) : null);
});

/**
 * Supports either:
 *  - { output: { title, summary, weekly_split } }
 *  - { title, summary, weekly_split }  (if backend ever returns output directly)
 */
const output = computed<PlanOutput | null>(() => {
  const p = plan.value as PlanDetail | null;
  if (!p) return null;

  if (p.output?.weekly_split) return p.output;
  if ((p as any).weekly_split) {
    return {
      title: (p as any).title ?? "Workout Plan",
      summary: (p as any).summary ?? "",
      weekly_split: (p as any).weekly_split ?? [],
    };
  }
  return null;
});

/**
 * Normalize different shapes into a list of strings for rendering.
 * - string[] stays string[]
 * - Lift[] becomes formatted lines
 * - unknown objects become best-effort JSON-ish lines
 */
function normalizeToStrings(items: any[] | undefined) {
  if (!items?.length) return [];

  // If array of strings
  if (items.every((x) => typeof x === "string")) return items as string[];

  // If array of lift-like objects
  if (items.every((x) => x && typeof x === "object" && "name" in x)) {
    return (items as Lift[]).map(formatLift);
  }

  // Fallback: stringify unknown objects
  return items.map((x) => {
    if (typeof x === "string") return x;
    if (x && typeof x === "object") {
      if ("text" in x && typeof x.text === "string") return x.text;
      return JSON.stringify(x);
    }
    return String(x);
  });
}

function formatLift(l: Lift) {
  const parts: string[] = [];
  if (l.sets != null) parts.push(`${l.sets} sets`);
  if (l.reps) parts.push(`${l.reps} reps`);
  if (l.rpe != null) parts.push(`RPE ${l.rpe}`);
  if (l.rest_seconds != null) parts.push(`${l.rest_seconds}s rest`);

  const meta = parts.length ? ` (${parts.join(" · ")})` : "";
  const notes = l.notes ? ` — ${l.notes}` : "";
  return `${l.name}${meta}${notes}`;
}

const Section = defineComponent({
  props: {
    title: { type: String, required: true },
    items: { type: Array as PropType<string[]>, default: () => [] },
  },
  setup(props) {
    return () =>
      props.items?.length
        ? h("section", { style: "margin-top: 12px;" }, [
            h(
              "h3",
              {
                style:
                  "margin: 0 0 6px; font-size: 13px; text-transform: uppercase; letter-spacing: 0.06em; opacity: 0.7;",
              },
              props.title
            ),
            h(
              "ul",
              { style: "margin: 0; padding-left: 18px; line-height: 1.6;" },
              props.items.map((it) => h("li", it))
            ),
          ])
        : null;
  },
});
</script>
