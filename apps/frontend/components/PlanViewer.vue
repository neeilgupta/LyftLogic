<template>
  <section v-if="plan" class="plan-view">
    <div class="ll-card">
      <h2 class="title">{{ plan.title }}</h2>
      <p class="summary">{{ plan.summary }}</p>

      <div v-if="plan.progression_notes?.length" class="notes">
        <div class="notes-title">Training Notes</div>
        <ul>
          <li v-for="(n, i) in plan.progression_notes" :key="`pn-${i}`">{{ n }}</li>
        </ul>
      </div>

      <div v-if="plan.safety_notes?.length" class="notes">
        <div class="notes-title">Safety Notes</div>
        <ul>
          <li v-for="(n, i) in plan.safety_notes" :key="`sn-${i}`">{{ n }}</li>
        </ul>
      </div>
    </div>

    <div class="ll-card">
      <div class="day-tabs">
        <a
          v-for="(day, i) in plan.weekly_split"
          :key="`tab-${i}`"
          class="day-tab"
          :href="`#gen-day-${i}`"
        >
          {{ dayChipLabel(day) }}
        </a>
      </div>

      <article
        v-for="(day, i) in plan.weekly_split"
        :key="`day-${i}`"
        :id="`gen-day-${i}`"
        class="day-card"
      >
        <h3 class="day-title">
          {{ day.day }} — {{ isRestDay(day) ? "Rest Day" : day.focus }}
        </h3>

        <div v-if="isRestDay(day)" class="rest-day">
          <strong>Rest Day</strong>
          <div class="rest-body">No lifting today. Optional: light walking and mobility.</div>
        </div>

        <template v-else>
          <TableSection title="Warmup" :lifts="normalizeToLifts(day.warmup)" />
          <TableSection title="Main" :lifts="normalizeToLifts(day.main)" />
          <TableSection title="Accessories" :lifts="normalizeToLifts(day.accessories)" />
        </template>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, defineComponent, h } from "vue";
import type { PropType } from "vue";

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

const props = defineProps({
  plan: { type: Object as PropType<PlanOutput | null>, default: null },
});

const plan = computed(() => props.plan);

function normalizeToLifts(items: any[] | undefined): Lift[] {
  if (!items?.length) return [];
  if (items.every((x) => typeof x === "string")) {
    return (items as string[]).map((s) => ({ name: s }));
  }
  if (items.every((x) => x && typeof x === "object" && "name" in x)) {
    return (items as any[]).map((x) => ({
      name: String(x.name ?? ""),
      sets: x.sets ?? undefined,
      reps: x.reps ?? undefined,
      rest_seconds: x.rest_seconds ?? null,
      notes: x.notes ?? "",
    }));
  }
  return items.map((x) => ({
    name:
      typeof x === "string"
        ? x
        : x && typeof x === "object"
          ? JSON.stringify(x)
          : String(x),
  }));
}

function isRestDay(day: Day) {
  const focus = String(day.focus ?? "").toLowerCase();
  const label = String(day.day ?? "").toLowerCase();
  if (focus.includes("rest")) return true;
  if (label.includes("rest")) return true;
  const hasAny = (arr: any[] | undefined) =>
    Array.isArray(arr) && arr.some((x) => {
      if (!x) return false;
      if (typeof x === "string") return x.trim().length > 0;
      if (typeof x === "object") {
        const n = (x as any).name;
        return typeof n === "string" ? n.trim().length > 0 : true;
      }
      return true;
    });
  const hasWarmup = hasAny(day.warmup);
  const hasMain = hasAny(day.main);
  const hasAcc = hasAny(day.accessories);
  return !(hasWarmup || hasMain || hasAcc);
}

function dayChipLabel(day: Day) {
  return isRestDay(day) ? `${day.day} (Rest)` : day.day;
}

const TableSection = defineComponent({
  props: {
    title: { type: String, required: true },
    lifts: { type: Array as PropType<Lift[]>, default: () => [] },
  },
  setup(sectionProps) {
    return () => {
      if (!sectionProps.lifts?.length) return null;
      const showNotes = sectionProps.lifts.some((l) => !!(l.notes && String(l.notes).trim().length));
      const thStyle =
        "text-align: left; font-size: 12px; text-transform: uppercase; letter-spacing: 0.06em; opacity: 0.7; padding: 8px 10px; border-bottom: 1px solid rgba(255,255,255,0.08);";
      const tdStyle = "padding: 8px 10px; border-bottom: 1px solid rgba(255,255,255,0.08); vertical-align: top;";
      return h("section", { style: "margin-top: 12px;" }, [
        h(
          "h4",
          {
            style:
              "margin: 0 0 6px; font-size: 13px; text-transform: uppercase; letter-spacing: 0.06em; opacity: 0.7;",
          },
          sectionProps.title
        ),
        h(
          "div",
          { style: "overflow-x: auto; border: 1px solid rgba(255,255,255,0.08); border-radius: 10px;" },
          [
            h(
              "table",
              {
                style:
                  "width: 100%; border-collapse: collapse; font-size: 14px; table-layout: fixed;",
              },
              [
                h("colgroup", [
                  h("col", { style: "width: 45%;" }),
                  h("col", { style: "width: 15%;" }),
                  h("col", { style: "width: 15%;" }),
                  h("col", { style: "width: 15%;" }),
                  ...(showNotes ? [h("col", { style: "width: 10%;" })] : []),
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
                  sectionProps.lifts.map((l, idx) =>
                    h("tr", { key: `${sectionProps.title}-${idx}` }, [
                      h("td", { style: tdStyle }, l.name ?? ""),
                      h("td", { style: tdStyle }, l.sets != null ? String(l.sets) : ""),
                      h("td", { style: tdStyle }, l.reps ?? ""),
                      h("td", { style: tdStyle }, l.rest_seconds != null ? `${l.rest_seconds}s` : ""),
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

<style scoped>
.plan-view {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.title {
  margin: 0 0 8px;
}

.summary {
  margin: 0 0 12px;
  opacity: 0.85;
}

.notes {
  margin-top: 10px;
}

.notes-title {
  font-weight: 700;
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  opacity: 0.8;
  margin-bottom: 6px;
}

.day-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}

.day-tab {
  padding: 6px 10px;
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 999px;
  text-decoration: none;
  color: inherit;
  opacity: 0.9;
}

.day-card {
  border: 1px solid rgba(255,255,255,0.12);
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 12px;
  background: rgba(12, 14, 22, 0.35);
}

.day-title {
  margin: 0 0 6px;
  font-weight: 600;
}

.rest-day {
  margin-top: 10px;
  padding: 12px;
  border: 1px dashed rgba(255,255,255,0.2);
  border-radius: 10px;
  opacity: 0.85;
}

.rest-body {
  margin-top: 6px;
}
</style>
