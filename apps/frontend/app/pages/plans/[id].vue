<template>
  <main style="padding: 20px; font-family: system-ui; max-width: 900px; margin: 0 auto;">
    <nav style="margin-bottom: 16px;">
      <NuxtLink to="/" style="text-decoration: underline;">← Back to home</NuxtLink>
      <span style="margin: 0 10px;">·</span>
      <NuxtLink to="/generate" style="text-decoration: underline;">Generate another plan</NuxtLink>
      <span style="margin: 0 10px;">·</span>
      <NuxtLink to="/plans" style="text-decoration: underline;">All plans</NuxtLink>
    </nav>

    <p v-if="pending">Loading plan…</p>
    <p v-else-if="errorMsg" style="color: red;">{{ errorMsg }}</p>

    <section v-else-if="output">
      <h1 style="margin: 0 0 8px;">{{ output.title }}</h1>
      <p style="margin: 0 0 18px; opacity: 0.85;">{{ output.summary }}</p>

      <!-- Global notes -->
      <div style="border: 1px solid #eee; border-radius: 12px; padding: 14px; margin-bottom: 14px;">
        <div v-if="output.progression_notes?.length" style="margin-bottom: 10px;">
          <h3
  style="
    margin: 0 0 6px;
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    opacity: 0.8;
  "
>
  Training Notes
</h3>
          <ul style="margin: 0; padding-left: 18px; line-height: 1.6;">
            <li v-for="(n, i) in output.progression_notes" :key="`pn-${i}`">{{ n }}</li>
          </ul>
        </div>

        <div v-if="output.safety_notes?.length">
          <h3
  style="
    margin: 0 0 6px;
    font-size: 13px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    opacity: 0.8;
  "
>
            Safety Notes
          </h3>
          <ul style="margin: 0; padding-left: 18px; line-height: 1.6;">
            <li v-for="(n, i) in output.safety_notes" :key="`sn-${i}`">{{ n }}</li>
          </ul>
        </div>

        <!-- Input / constraints / preferences (text only) -->
        <div v-if="inputConstraints.length || preferenceLines.length" style="margin-top: 12px;">
          <h3 style="margin: 0 0 6px; font-size: 13px; text-transform: uppercase; letter-spacing: 0.06em; opacity: 0.7;">
            Preferences (informational)
          </h3>

          <div v-if="inputConstraints.length" style="margin-bottom: 8px;">
            <div style="opacity: 0.8; font-size: 13px; margin-bottom: 4px;">Constraints</div>
            <ul style="margin: 0; padding-left: 18px; line-height: 1.6;">
              <li v-for="(c, i) in inputConstraints" :key="`c-${i}`">{{ c }}</li>
            </ul>
          </div>

          <div v-if="preferenceLines.length">
            <div style="opacity: 0.8; font-size: 13px; margin-bottom: 4px;">Flags</div>
            <ul style="margin: 0; padding-left: 18px; line-height: 1.6;">
              <li v-for="(p, i) in preferenceLines" :key="`p-${i}`">{{ p }}</li>
            </ul>
          </div>
        </div>
      </div>

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
        <h2 style="margin: 0 0 6px; font-weight: 600;">
          {{ day.day }} — {{ day.focus }}
        </h2>

        <TableSection title="Main" :lifts="normalizeToLifts(day.main)" />
        <TableSection title="Accessories" :lifts="normalizeToLifts(day.accessories)" />
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
  rest_seconds?: number | null;
  notes?: string;
};

type Day = {
  day: string;
  focus: string;
  warmup?: any[];
  main?: any[];
  accessories?: any[];
};

type PlanOutput = {
  title: string;
  summary: string;
  weekly_split: Day[];
  progression_notes?: string[];
  safety_notes?: string[];
};

type PlanDetail = {
  id: number;
  created_at?: string;
  input?: any;
  output?: PlanOutput;
  summary?: string;
  weekly_split?: Day[];
  title?: string;
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

const output = computed<PlanOutput | null>(() => {
  const p = plan.value as PlanDetail | null;
  if (!p) return null;

  if (p.output?.weekly_split) return p.output;

  if ((p as any).weekly_split) {
    return {
      title: (p as any).title ?? "Workout Plan",
      summary: (p as any).summary ?? "",
      weekly_split: (p as any).weekly_split ?? [],
      progression_notes: (p as any).progression_notes ?? [],
      safety_notes: (p as any).safety_notes ?? [],
    };
  }
  return null;
});

const input = computed<any>(() => {
  const p: any = plan.value;
  return p?.input ?? null;
});

const inputConstraints = computed<string[]>(() => {
  const c = input.value?.constraints;
  if (!c) return [];
  if (Array.isArray(c)) return c.map(String).filter(Boolean);
  if (typeof c === "string") return c.split("\n").map(s => s.trim()).filter(Boolean);
  return [String(c)];
});

const preferenceLines = computed<string[]>(() => {
  const i = input.value;
  if (!i) return [];

  const out: string[] = [];

  if (i.prefer_machines !== undefined && i.prefer_machines !== null) {
    out.push(`prefer_machines: ${String(i.prefer_machines)}`);
  }
  if (i.include_sharms !== undefined && i.include_sharms !== null) {
    out.push(`include_sharms: ${String(i.include_sharms)}`);
  }
  if (i.barbell_avoidance !== undefined && i.barbell_avoidance !== null) {
    out.push(`barbell_avoidance: ${String(i.barbell_avoidance)}`);
  }

  return out;
});

/** Warmup list rendering: stringy bullets */
function normalizeToStrings(items: any[] | undefined) {
  if (!items?.length) return [];
  if (items.every((x) => typeof x === "string")) return items as string[];

  return items.map((x) => {
    if (typeof x === "string") return x;
    if (x && typeof x === "object") {
      if ("text" in x && typeof x.text === "string") return x.text;
      if ("name" in x && typeof x.name === "string") return x.name; // fallback
      return JSON.stringify(x);
    }
    return String(x);
  });
}

/** Main/accessories rendering: turn anything into lift rows */
function normalizeToLifts(items: any[] | undefined): Lift[] {
  if (!items?.length) return [];

  // If strings, treat as "name-only" lifts
  if (items.every((x) => typeof x === "string")) {
    return (items as string[]).map((s) => ({ name: s }));
  }

  // If lift-like objects
  if (items.every((x) => x && typeof x === "object" && "name" in x)) {
    return (items as any[]).map((x) => ({
      name: String(x.name ?? ""),
      sets: x.sets ?? undefined,
      reps: x.reps ?? undefined,
      rest_seconds: x.rest_seconds ?? null,
      notes: x.notes ?? "",
    }));
  }

  // Fallback: stringify
  return items.map((x) => ({
    name:
      typeof x === "string"
        ? x
        : x && typeof x === "object"
          ? JSON.stringify(x)
          : String(x),
  }));
}

const ListSection = defineComponent({
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

const TableSection = defineComponent({
  props: {
    title: { type: String, required: true },
    lifts: { type: Array as PropType<Lift[]>, default: () => [] },
  },
  setup(props) {
    return () => {
      if (!props.lifts?.length) return null;

      const showNotes = props.lifts.some((l) => !!(l.notes && String(l.notes).trim().length));

      const thStyle =
        "text-align: left; font-size: 12px; text-transform: uppercase; letter-spacing: 0.06em; opacity: 0.7; padding: 8px 10px; border-bottom: 1px solid #eee;";
      const tdStyle = "padding: 8px 10px; border-bottom: 1px solid #f3f3f3; vertical-align: top;";

      return h("section", { style: "margin-top: 12px;" }, [
        h(
          "h3",
          {
            style:
              "margin: 0 0 6px; font-size: 13px; text-transform: uppercase; letter-spacing: 0.06em; opacity: 0.7;",
          },
          props.title
        ),
        h(
          "div",
          { style: "overflow-x: auto; border: 1px solid #eee; border-radius: 10px;" },
          [
            h(
  "table",
  {
    style:
      "width: 100%; border-collapse: collapse; font-size: 14px; table-layout: fixed;",
  },
  [
    h("colgroup", [
      h("col", { style: "width: 45%;" }), // Exercise
      h("col", { style: "width: 15%;" }), // Sets
      h("col", { style: "width: 15%;" }), // Reps
      h("col", { style: "width: 15%;" }), // Rest
      ...(showNotes ? [h("col", { style: "width: 10%;" })] : []), // Notes
    ]),

    h("thead", [
      h("tr", [
        h("th", { style: thStyle }, "Exercise"),
        h("th", { style: thStyle }, "Sets"),
        h("th", { style: thStyle }, "Reps"),
        h("th", { style: thStyle }, "Rest"),
        ...(showNotes ? [h("th", { style: thStyle }, "Notes")] : []),
      ]),
    ]),

    h(
      "tbody",
      props.lifts.map((l, idx) =>
        h("tr", { key: `${props.title}-${idx}` }, [
          h("td", { style: tdStyle }, l.name ?? ""),
          h("td", { style: tdStyle }, l.sets != null ? String(l.sets) : ""),
          h("td", { style: tdStyle }, l.reps ?? ""),
          h(
            "td",
            { style: tdStyle },
            l.rest_seconds != null ? `${l.rest_seconds}s` : ""
          ),
          ...(showNotes ? [h("td", { style: tdStyle }, l.notes ?? "")] : []),
        ])
      )
    ),
  ]
),

          ]
        ),
      ]);
    };
  },
});
</script>
