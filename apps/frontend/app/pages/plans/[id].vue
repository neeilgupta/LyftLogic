<template>
  <main style="padding: 20px; font-family: system-ui; max-width: 1200px; margin: 0 auto;">
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
      <div style="display: flex; gap: 14px; align-items: flex-start;">
        <!-- LEFT -->
        <div style="flex: 1; min-width: 0;">
      <h1 style="margin: 0 0 8px;">{{ output.title }}</h1>
      <div style="opacity: 0.7; font-size: 13px; margin: 6px 0 12px;">
        Version {{ (plan as any)?.version ?? "?" }}
      </div>
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
        <div
          v-if="inputConstraints.length || preferenceLines.length || constraintTokens.length || preferenceTokens.length"
          style="margin-top: 12px;"
        >
          <h3 style="margin: 0 0 6px; font-size: 13px; text-transform: uppercase; letter-spacing: 0.06em; opacity: 0.7;">
            Preferences (informational)
          </h3>

          <!-- ✅ Tokens from backend -->
          <div v-if="constraintTokens.length" style="margin-bottom: 8px;">
            <div style="opacity: 0.8; font-size: 13px; margin-bottom: 4px;">Constraint Tokens</div>
            <ul style="margin: 0; padding-left: 18px; line-height: 1.6;">
              <li v-for="(c, i) in constraintTokens" :key="`ct-${i}`">{{ c }}</li>
            </ul>
          </div>

          <div v-if="preferenceTokens.length" style="margin-bottom: 8px;">
            <div style="opacity: 0.8; font-size: 13px; margin-bottom: 4px;">Preference Tokens</div>
            <ul style="margin: 0; padding-left: 18px; line-height: 1.6;">
              <li v-for="(p, i) in preferenceTokens" :key="`pt-${i}`">{{ p }}</li>
            </ul>
          </div>

          <!-- Existing: raw constraints text -->
          <div v-if="inputConstraints.length" style="margin-bottom: 8px;">
            <div style="opacity: 0.8; font-size: 13px; margin-bottom: 4px;">Constraints (raw)</div>
            <ul style="margin: 0; padding-left: 18px; line-height: 1.6;">
              <li v-for="(c, i) in inputConstraints" :key="`c-${i}`">{{ c }}</li>
            </ul>
          </div>

          <!-- Existing: flags -->
          <div v-if="preferenceLines.length">
            <div style="opacity: 0.8; font-size: 13px; margin-bottom: 4px;">Flags</div>
            <ul style="margin: 0; padding-left: 18px; line-height: 1.6;">
              <li v-for="(p, i) in preferenceLines" :key="`p-${i}`">{{ p }}</li>
            </ul>
          </div>
        </div>
      </div>
      <!-- ========================= -->
      <!-- What changed (diff) -->
      <!-- ========================= -->
      <div
        v-if="
          lastDiff &&
          ((lastDiff.replaced_exercises?.length ?? 0) +
          (lastDiff.added_exercises?.length ?? 0) +
          (lastDiff.removed_exercises?.length ?? 0)) > 0
        "
        style="
          margin-bottom: 14px;
          border: 1px solid #eee;
          border-radius: 12px;
          padding: 12px;
          background: #fff;
        "
      >
        <div style="font-weight: 800; margin-bottom: 6px;">What changed</div>

        <div v-if="lastDiff.replaced_exercises?.length">
          <div style="font-weight: 700; font-size: 13px; margin: 8px 0 4px;">
            Replaced
          </div>
          <ul style="margin: 0; padding-left: 18px; line-height: 1.6;">
            <li
              v-for="(r, i) in lastDiff.replaced_exercises"
              :key="`rep-${i}`"
            >
              Day {{ (r.day ?? 0) + 1 }}
              ({{ r.block }} #{{ (r.slot ?? 0) + 1 }}):
              <code>{{ r.from }}</code> → <code>{{ r.to }}</code>
            </li>
          </ul>
        </div>

        <div
          v-if="
            !lastDiff.replaced_exercises?.length &&
            !lastDiff.removed_exercises?.length &&
            !lastDiff.added_exercises?.length
          "
          style="opacity: 0.7; font-size: 13px;"
        >
          No changes detected.
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
          {{ dayChipLabel(day) }}
        </a>
      </div>

      <article
        v-for="(day, i) in output.weekly_split"
        :key="i"
        :id="`day-${i}`"
        style="border: 1px solid #eee; border-radius: 12px; padding: 14px; margin-bottom: 14px;"
      >
        <h2 style="margin: 0 0 6px; font-weight: 600;">
          {{ day.day }} — {{ isRestDay(day) ? "Rest Day" : day.focus }}

        </h2>

        

        <!-- REST DAY -->
        <div
          v-if="isRestDay(day)"
          style="margin-top: 10px; padding: 12px; border: 1px dashed #ddd; border-radius: 10px; opacity: 0.85;"
        >
          <strong>Rest Day</strong>
          <div style="margin-top: 6px;">
            No lifting today. Optional: light walking and mobility.
          </div>
        </div>

        <!-- TRAINING DAY -->
        <template v-else>
          <TableSection title="Main" :lifts="normalizeToLifts(day.main)" />
          <TableSection title="Accessories" :lifts="normalizeToLifts(day.accessories)" />
        </template>
      </article>
    </div>

    <!-- RIGHT -->
    <div style="display: flex; gap: 14px; align-items: flex-start; flex-wrap: wrap;">
      <!-- ========================= -->
      <!-- Phase 1: Chat Panel -->
      <!-- ========================= -->
      <section style="border: 1px solid #eee; border-radius: 12px; padding: 14px; height: calc(100vh - 140px); display: flex; flex-direction: column;">
        <div style="display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 10px;">
          <div>
            <div style="font-weight: 800;">Chat</div>
            <div style="opacity: 0.7; font-size: 13px;">
              Adjust the plan. Example: <code>no barbells</code>, <code>prefer cables</code>, <code>avoid shoulders</code>
            </div>
          </div>
          <div style="opacity: 0.7; font-size: 13px;">
            v{{ (plan as any)?.version ?? "?" }}
          </div>
        </div>

        <!-- Messages -->
        <div ref="chatScrollEl" style="flex: 1; overflow: auto; border: 1px solid #eee; border-radius: 12px; padding: 10px; background: #fafafa;">
          <div v-if="!chatHistory.length" style="opacity: 0.7; font-size: 13px; padding: 10px;">
            No edits yet — send a message to start.
          </div>

          <div v-for="(m, i) in chatHistory" :key="`ch-${i}`" style="margin-bottom: 10px;">
            <div style="display: flex; justify-content: flex-end;">
              <div style="max-width: 85%; background: white; border: 1px solid #e6e6e6; border-radius: 12px; padding: 10px;">
                <div style="font-weight: 700; font-size: 13px; margin-bottom: 4px;">You</div>
                <div style="white-space: pre-wrap; word-break: break-word;">{{ m.message }}</div>
                <div style="opacity: 0.6; font-size: 12px; margin-top: 6px;">
                  {{ formatChatTime(m.created_at) }}
                </div>

                <!-- Optional: patch preview -->
                <details style="margin-top: 8px;">
                  <summary style="cursor: pointer; opacity: 0.75; font-size: 12px;">patch</summary>
                  <pre style="margin: 8px 0 0; white-space: pre-wrap; word-break: break-word; font-size: 12px;">
      {{ JSON.stringify(m.patch, null, 2) }}
                  </pre>
                </details>
              </div>
            </div>
          </div>
        </div>

        <!-- Composer -->
        <div style="margin-top: 10px;">
          <textarea
            v-model="editMessage"
            rows="3"
            placeholder="Type an adjustment…"
            style="
              width: 100%;
              padding: 10px;
              border: 1px solid #ddd;
              border-radius: 10px;
              font-family: inherit;
              font-size: 14px;
              line-height: 1.4;
            "
          />
          <div style="display: flex; gap: 10px; margin-top: 8px; align-items: center;">
            <button
              :disabled="editPending || applyPending || !editMessage.trim()"
              @click="sendEditAndApply()"
              style="padding: 10px 12px; border-radius: 10px; border: 1px solid #ddd; background: white; cursor: pointer;"
            >
              {{ (editPending || applyPending) ? "Working…" : "Send" }}
            </button>

            <span v-if="appliedOk" style="color: #137333; font-size: 13px;">Applied ✓</span>
            <span v-if="editError" style="color: #b00020; font-size: 13px;">{{ editError }}</span>
            <span v-if="applyError" style="color: #b00020; font-size: 13px;">{{ applyError }}</span>
          </div>
        </div>
      </section>
    </div>
  </div>
</section>

    <p v-else>No plan data found.</p>
  </main>
</template>

<script setup lang="ts">
import { computed, defineComponent, h, ref, nextTick, watch } from "vue";
import type { PropType } from "vue";
import { useRoute } from "vue-router";
import { usePlans } from "../../../composables/usePlans";
import { useRuntimeConfig } from "#imports";



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

const { data: plan, pending, error, refresh} = await useAsyncData(
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

const chatHistory = computed<any[]>(() => {
  const h = (plan.value as any)?.input?.chat_history;
  return Array.isArray(h) ? h : [];
});

const chatScrollEl = ref<HTMLElement | null>(null);

function scrollChatToBottom() {
  const el = chatScrollEl.value;
  if (!el) return;
  el.scrollTop = el.scrollHeight;
}

watch(
  () => id.value,
  () => {
    lastDiff.value = null;
    applyResponse.value = null;
    applyError.value = null;
    editResponse.value = null;
    editError.value = null;
    editMessage.value = "";
  }
);


function formatChatTime(iso: any) {
  if (!iso) return ""
  try {
    const d = new Date(String(iso))
    return d.toLocaleString()
  } catch {
    return String(iso)
  }
}


const constraintTokens = computed<string[]>(() => {
  const t = (plan.value as any)?.input?.constraints_tokens;
  return Array.isArray(t) ? t.map(String).filter(Boolean) : [];
});

const preferenceTokens = computed<string[]>(() => {
  const t = (plan.value as any)?.input?.preferences_tokens;
  return Array.isArray(t) ? t.map(String).filter(Boolean) : [];
});


const inputConstraints = computed<string[]>(() => {
  const i = input.value
  if (!i) return []

  // ✅ Prefer raw base text if present
  const raw = i.base_constraints_text ?? null
  const c = raw && String(raw).trim().length ? raw : i.constraints

  if (!c) return []
  if (Array.isArray(c)) return c.map(String).filter(Boolean)
  if (typeof c === "string") return c.split("\n").map(s => s.trim()).filter(Boolean)
  return [String(c)]
})

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

function isRestDay(day: Day) {
  const focus = String(day.focus ?? "").toLowerCase();
  const label = String(day.day ?? "").toLowerCase();

  // Strong signals
  if (focus.includes("rest")) return true;
  if (label.includes("rest")) return true;

  // Treat "no lifts" as rest
  const hasAny = (arr: any[] | undefined) =>
    Array.isArray(arr) && arr.some((x) => {
      if (!x) return false;
      if (typeof x === "string") return x.trim().length > 0;
      if (typeof x === "object") {
        // lift-like objects might exist with empty name
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

type EditPlanResponseT = {
  can_apply: boolean;
  proposed_patch: {
    constraints_add: string[];
    constraints_remove: string[];
    preferences_add: string[];
    preferences_remove: string[];
    emphasis: string | null;
    avoid: string[];
    set_style: "low" | "standard" | "high" | null;
    rep_style: "strength" | "hypertrophy" | "pump" | null;
  };
  change_summary: string[];
  errors: string[];
};

const editMessage = ref("");
const editPending = ref(false);
const appliedOk = ref(false)
const editError = ref<string | null>(null);
const editResponse = ref<EditPlanResponseT | null>(null);
const applyPending = ref(false);
const applyError = ref<string | null>(null);
const applyResponse = ref<any>(null);
const lastDiff = ref<any | null>(null)


const hasRealPatch = computed(() => {
  const p = editResponse.value?.proposed_patch;
  if (!p) return false;

  return (
    (p.constraints_add?.length ?? 0) > 0 ||
    (p.constraints_remove?.length ?? 0) > 0 ||
    (p.preferences_add?.length ?? 0) > 0 ||
    (p.preferences_remove?.length ?? 0) > 0 ||
    (p.avoid?.length ?? 0) > 0 ||
    !!p.emphasis ||
    !!p.set_style ||
    !!p.rep_style
  );
});


const config = useRuntimeConfig();
const apiBase = (config.public as any)?.apiBase ?? "http://127.0.0.1:8000";

async function applyPatch() {
  applyError.value = null;
  applyResponse.value = null;

  const patch = editResponse.value?.proposed_patch;
  if (!patch) {
    applyError.value = "No proposed_patch to apply. Send an edit first.";
    return;
  }
  if (!hasRealPatch.value) {
    applyError.value = "No real changes to apply yet.";
    return;
}

  applyPending.value = true;
  try {
    const res = await $fetch(`${apiBase}/plans/${id.value}/apply`, {
      method: "POST",
      body: patch,
    });

    // show immediate response (optional)
    applyResponse.value = res;
    lastDiff.value = (res as any)?.diff ?? null;


    // refresh the plan content (new version)
    await refresh();
    appliedOk.value = true;
    setTimeout(() => (appliedOk.value = false), 1500);

    // ✅ clear editor UI so it doesn't show stale state
    editMessage.value = "";
    editResponse.value = null;
    editError.value = null;
    applyError.value = null;
  } catch (e: any) {
    const d = e?.data?.detail;
    applyResponse.value = d ?? e?.data ?? null;
    applyError.value = e?.data?.detail ?? e?.message ?? String(e);
  } finally {
    applyPending.value = false;
  }
}


async function sendEdit() {
  editError.value = null;
  editResponse.value = null;

  applyResponse.value = null;
  applyError.value = null;

  const msg = editMessage.value.trim();
  if (!msg) return;

  editPending.value = true;
  try {
    const res = await $fetch<EditPlanResponseT>(`${apiBase}/plans/${id.value}/edit`, {
      method: "POST",
      body: { message: msg },
    });
    editResponse.value = res;
  } catch (e: any) {
    editError.value = e?.data?.detail ?? e?.message ?? String(e);
  } finally {
    editPending.value = false;
  }
}

async function sendEditAndApply() {
  editError.value = null;
  applyError.value = null;

  const msg = editMessage.value.trim();
  if (!msg) return;

  editPending.value = true;
  applyPending.value = true;

  try {
    // 1) EDIT
    const res = await $fetch<EditPlanResponseT>(`${apiBase}/plans/${id.value}/edit`, {
      method: "POST",
      body: { message: msg },
    });

    editResponse.value = res;

    if (!res?.can_apply) {
      editError.value = (res?.errors?.[0] ?? "No actionable changes detected.");
      return;
    }

    const patch = res.proposed_patch;
    if (!patch) {
      editError.value = "No proposed_patch returned.";
      return;
    }

    // 2) APPLY (same request shape you already use)
    // 2) APPLY
const applyRes = await $fetch(`${apiBase}/plans/${id.value}/apply`, {
  method: "POST",
  body: patch,
});

applyResponse.value = applyRes;
lastDiff.value = (applyRes as any)?.diff ?? null;


    // 3) Refresh plan (pulls updated output + chat_history)
    await refresh();

    appliedOk.value = true;
    setTimeout(() => (appliedOk.value = false), 1500);

    // clear composer
    editMessage.value = "";
    editResponse.value = null;
  } catch (e: any) {
    const msg = e?.data?.detail ?? e?.message ?? String(e);
    // decide whether it was edit vs apply by which part has a response
    if (!editResponse.value) editError.value = msg;
    else applyError.value = msg;
  } finally {
    editPending.value = false;
    applyPending.value = false;
  }
}

</script>
