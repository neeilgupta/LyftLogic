<template>
  <main class="plan-detail-page">    <nav style="margin-bottom: 16px;">
      <NuxtLink to="/" class="nav-link">← Back to home</NuxtLink>
      <span style="margin: 0 10px;">·</span>
      <NuxtLink to="/generate" class="nav-link">Generate another plan</NuxtLink>
      <span style="margin: 0 10px;">·</span>
      <NuxtLink to="/plans" class="nav-link">All plans</NuxtLink>
    </nav>

    <!-- ========================= -->
    <!-- Phase 2: Version Bar (Always Visible) -->
    <!-- ========================= -->
    <div class="version-bar"
    >
      <div style="font-weight: 800;">
        Version
        <span style="opacity: 0.7; font-weight: 600;">
          — viewing v{{ selectedVersionNumber ?? ((plan as any)?.version ?? "?") }}
          <template v-if="selectedVersion?.is_restored && selectedVersion?.restored_from">
            (restored from v{{ selectedVersion.restored_from }})
          </template>
          <template v-else-if="selectedVersionNumber != null && selectedVersionNumber === latestVersionNumber">
            (latest)
          </template>
        </span>
      </div>

      <div style="display:flex; gap:8px; align-items:center;">
        <select
          v-model.number="selectedVersionNumber"
          :disabled="versionsPending"
          class="version-select"
        >
          <option v-if="versionsPending" :value="null">Loading versions…</option>
          <option v-else-if="!versions.length" :value="null">No versions</option>

          <option v-for="v in versions" :key="v.version" :value="v.version">
            v{{ v.version }}
            <template v-if="v.is_restored && v.restored_from">
              (restored from v{{ v.restored_from }})
            </template>
            <template v-else-if="v.version === latestVersionNumber">
              (latest)
            </template>
          </option>
        </select>

        <button
          v-if="selectedVersionNumber != null && selectedVersionNumber !== latestVersionNumber"
          :disabled="restoring || versionsPending"
          @click="restoreSelected"
            class="restore-button"        >
          {{ restoring ? "Restoring…" : "Restore this version" }}
        </button>

        <span v-if="versionsError" style="color:#b00020; font-size: 13px;">
          {{ versionsError }}
        </span>
      </div>
    </div>


    <p v-if="pending">Loading plan…</p>
    <p v-else-if="errorMsg" style="color: red;">{{ errorMsg }}</p>

    <section v-else-if="selectedOutput">
      <div style="display: flex; gap: 14px; align-items: flex-start;">
        <!-- LEFT -->
        <div style="flex: 1; min-width: 0;">
      <PlanViewer :plan="selectedOutput">
        <template #after-notes>
          <!-- Input / constraints / preferences (text only) -->
          <div
            v-if="inputConstraints.length || preferenceLines.length || constraintTokens.length || preferenceTokens.length"
            class="notes-card"
          >
            <h3 style="margin: 0 0 6px; font-size: 13px; text-transform: uppercase; letter-spacing: 0.06em; opacity: 0.7;">
              Preferences (informational)
            </h3>

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

            <div v-if="inputConstraints.length" style="margin-bottom: 8px;">
              <div style="opacity: 0.8; font-size: 13px; margin-bottom: 4px;">Constraints (raw)</div>
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

          <!-- What changed (diff) -->
          <div
            v-if="displayDiff !== null"
            class="diff-card"
          >
            <div style="font-weight: 800; margin-bottom: 6px;">What changed</div>

            <div v-if="displayDiff.replaced_exercises?.length">
              <div style="font-weight: 700; font-size: 13px; margin: 8px 0 4px;">Replaced</div>
              <ul style="margin: 0; padding-left: 18px; line-height: 1.6;">
                <li v-for="(r, i) in displayDiff.replaced_exercises" :key="`rep-${i}`">
                  Day {{ (r.day ?? 0) + 1 }}
                  ({{ r.block }} #{{ (r.slot ?? 0) + 1 }}):
                  <code>{{ r.from }}</code> → <code>{{ r.to }}</code>
                </li>
              </ul>
            </div>

            <div v-if="displayDiff.added_exercises?.length">
              <div style="font-weight: 700; font-size: 13px; margin: 8px 0 4px;">Added</div>
              <ul style="margin: 0; padding-left: 18px; line-height: 1.6;">
                <li v-for="(a, i) in displayDiff.added_exercises" :key="`add-${i}`">
                  Day {{ (a.day ?? 0) + 1 }} ({{ a.block }} #{{ (a.slot ?? 0) + 1 }}):
                  <code>{{ a.name }}</code>
                </li>
              </ul>
            </div>

            <div v-if="displayDiff.removed_exercises?.length">
              <div style="font-weight: 700; font-size: 13px; margin: 8px 0 4px;">Removed</div>
              <ul style="margin: 0; padding-left: 18px; line-height: 1.6;">
                <li v-for="(r, i) in displayDiff.removed_exercises" :key="`rem-${i}`">
                  Day {{ (r.day ?? 0) + 1 }} ({{ r.block }} #{{ (r.slot ?? 0) + 1 }}):
                  <code>{{ r.name }}</code>
                </li>
              </ul>
            </div>

            <div
              v-if="
                !displayDiff.replaced_exercises?.length &&
                !displayDiff.removed_exercises?.length &&
                !displayDiff.added_exercises?.length
              "
              style="opacity: 0.7; font-size: 13px;"
            >
              No changes detected.
            </div>
          </div>
        </template>
      </PlanViewer>
    </div>

    <!-- RIGHT -->
    <div style="width: 380px; min-width: 320px;">
      <!-- ========================= -->
      <!-- Phase 1: Chat Panel -->
      <!-- ========================= -->
      <section class="chat-panel">
        <div style="display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-bottom: 10px;">
          <div>
            <div style="font-weight: 800;">Chat</div>
            <div style="opacity: 0.7; font-size: 13px;">
              Adjust the plan. Example: <code>no barbells</code>, <code>prefer cables</code>, <code>avoid shoulders</code>
            </div>
          </div>
          <div style="opacity: 0.7; font-size: 13px;">
            v{{ selectedVersionNumber ?? ((plan as any)?.version ?? "?") }}
          </div>
        </div>

        <!-- Messages -->
        <div ref="chatScrollEl" class="chat-messages">
          <div v-if="!chatHistory.length" style="opacity: 0.7; font-size: 13px; padding: 10px;">
            No edits yet — send a message to start.
          </div>

          <div v-for="(m, i) in chatHistory" :key="`ch-${i}`" style="margin-bottom: 10px;">
            <div style="display: flex; justify-content: flex-end;">
              <div class="chat-message">
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
            class="chat-textarea"
          />
          <div style="display: flex; gap: 10px; margin-top: 8px; align-items: center;">
            <button
              :disabled="editPending || applyPending || !editMessage.trim()"
              @click="sendEditAndApply()"
              class="send-button"
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
definePageMeta({ layout: "plan" });
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { usePlans } from "../../../composables/usePlans";
import { useRuntimeConfig } from "#imports";
import PlanViewer from "../../../components/PlanViewer.vue";

type PlanOutput = {
  title: string;
  summary: string;
  weekly_split: any[];
  progression_notes?: string[];
  safety_notes?: string[];
};

type PlanDetail = {
  plan_id: number;
  version: number;
  input?: any;
  output?: PlanOutput;
  diff?: any;
  is_restored?: boolean;
  restored_from?: number | null;
  created_at?: string;
  summary?: string;
  weekly_split?: any[];
  title?: string;
};

type VersionItem = {
  version: number;
  created_at?: string;
  input: any;
  output: any;
  diff?: any;
  is_restored?: boolean;
  restored_from?: number | null;
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
    versions.value = [];
    selectedVersionNumber.value = null;
    fetchVersions();
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
  const t = (selectedInput.value as any)?.constraints_tokens;
  return Array.isArray(t) ? t.map(String).filter(Boolean) : [];
});

const preferenceTokens = computed<string[]>(() => {
  const t = (selectedInput.value as any)?.preferences_tokens;
  return Array.isArray(t) ? t.map(String).filter(Boolean) : [];
});


const inputConstraints = computed<string[]>(() => {
  const i = selectedInput.value
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
  const i = selectedInput.value;

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


const versions = ref<VersionItem[]>([]);
const selectedVersionNumber = ref<number | null>(null);
const restoring = ref(false);
const versionsPending = ref(false);
const versionsError = ref<string | null>(null);
const versionsReqToken = ref(0);

const latestVersionNumber = computed(() => {
  if (!versions.value.length) return (plan.value as any)?.version ?? null;
  return Math.max(...versions.value.map(v => v.version));
});

const selectedVersion = computed<VersionItem | null>(() => {
  if (selectedVersionNumber.value == null) return null;
  return versions.value.find(v => v.version === selectedVersionNumber.value) ?? null;
});

const selectedOutput = computed<PlanOutput | null>(() => {
  // Prefer selected snapshot if available
  const sv = selectedVersion.value;
  if (sv?.output?.weekly_split) return sv.output as PlanOutput;

  // Fallback to latest plan output (existing behavior)
  return output.value;
});

const selectedInput = computed<any>(() => {
  const sv = selectedVersion.value;
  if (sv?.input) return sv.input;
  return input.value;
});

// Diff to show in UI:
// - if viewing a snapshot, show its stored diff
// - otherwise show the last apply diff (immediate feedback)
// Diff rules:
// - If user has selected a specific version: show THAT version's persisted diff (even if null).
// - Only fall back to lastDiff for *latest* when selected version has no diff yet (immediate feedback).
const displayDiff = computed<any | null>(() => {
  const sv = selectedVersion.value;
  const selNum = selectedVersionNumber.value;

  if (selNum != null && sv) {
    // snapshot mode: never leak lastDiff from a different selection
    if (sv.diff !== undefined) return sv.diff ?? null;
    return null;
  }

  return lastDiff.value;
});


async function fetchVersions(opts?: { keepSelection?: boolean }) {
  const keepSelection = opts?.keepSelection ?? false;

  versionsPending.value = true;
  versionsError.value = null;

  const token = ++versionsReqToken.value;

  try {
    const res: any = await $fetch(`${apiBase}/plans/${id.value}/versions`, {
      credentials: "include",
    });
    if (token !== versionsReqToken.value) return; // ignore stale response

    const items: VersionItem[] = res.items ?? res ?? [];
    versions.value = [...items].sort((a, b) => b.version - a.version);

    const latest = versions.value[0]?.version ?? null;

    // Default selection = latest (unless explicitly keeping selection and it still exists)
    if (keepSelection && selectedVersionNumber.value != null) {
      const stillExists = versions.value.some(v => v.version === selectedVersionNumber.value);
      if (!stillExists) selectedVersionNumber.value = latest;
    } else {
      selectedVersionNumber.value = latest;
    }
  } catch (e: any) {
    if (token !== versionsReqToken.value) return;
    versionsError.value = e?.data?.detail ?? e?.message ?? String(e);
    versions.value = [];
    selectedVersionNumber.value = null;
  } finally {
    if (token === versionsReqToken.value) versionsPending.value = false;
  }
}

await fetchVersions();


async function restoreSelected() {
  if (!selectedVersion.value) return;

  const v = selectedVersion.value.version;
  if (v === latestVersionNumber.value) return;

  restoring.value = true;
  try {
    await $fetch(`${apiBase}/plans/${id.value}/restore`, {
      method: "POST",
      body: { version: v },
      credentials: "include",
    });

    // 1) pull newest versions first (so we can select latest deterministically)
    await fetchVersions({ keepSelection: false });

    // 2) refresh plan detail (latest output / chat_history)
    await refresh();

    // 3) avoid leaking prior apply diff into snapshot mode
    lastDiff.value = null;
  } catch (e: any) {
    versionsError.value = e?.data?.detail ?? e?.message ?? String(e);
  } finally {
    restoring.value = false;
  }
}


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
    await fetchVersions({ keepSelection: false });
    lastDiff.value = null;
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
    await fetchVersions({ keepSelection: false });
    lastDiff.value = null;

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
<style scoped>
/* Global dark theme setup */
:global(html),
:global(body) {
  background: #0b0f19;
  margin: 0;
}

:global(#__nuxt) {
  background: #0b0f19;
  min-height: 100vh;
}

.plan-detail-page {
  --accent: #7c3aed;
  --accent-dark: #6d28d9;
  --ink: #f8fafc;
  --muted: #a1a1aa;
  --page: #0b0f19;
  --surface: #111827;
  --surface-2: #0f172a;
  --border: rgba(255,255,255,0.10);
  --shadow: 0 10px 30px rgba(0,0,0,0.35);

  background: var(--page);
  color: var(--ink);
  padding: 32px 48px;
  font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
  max-width: 1500px;
  margin: 0 auto;
  min-height: 100vh;
}

/* Navigation links */
.nav-link {
  color: rgba(255,255,255,0.88);
  text-decoration: none;
  font-weight: 600;
  transition: color 140ms ease;
}

.nav-link:hover {
  color: var(--accent);
}

/* Version bar */
.version-bar {
  margin-bottom: 14px;
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 12px;
  background: var(--surface);
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
  box-shadow: var(--shadow);
}

.version-select {
  padding: 6px 10px;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: var(--surface-2);
  color: var(--ink);
  font-family: inherit;
  font-size: 14px;
}

.restore-button {
  padding: 6px 10px;
  border-radius: 10px;
  border: 1px solid var(--border);
  background: var(--accent);
  color: #fff;
  cursor: pointer;
  font-weight: 600;
  transition: background 140ms ease, box-shadow 140ms ease;
}

.restore-button:hover:not(:disabled) {
  background: var(--accent-dark);
  box-shadow: 0 2px 8px rgba(124, 58, 237, 0.35);
}

.restore-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Notes card */
.notes-card {
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 14px;
  background: var(--surface);
  box-shadow: var(--shadow);
}

/* Diff card */
.diff-card {
  margin-bottom: 14px;
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 12px;
  background: var(--surface);
  box-shadow: var(--shadow);
}

/* Day card */
.day-card {
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 14px;
  margin-bottom: 14px;
  background: var(--surface);
  box-shadow: var(--shadow);
}

/* Chat panel */
.chat-panel {
  position: sticky;
  top: 14px;
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 14px;
  height: calc(100vh - 140px);
  display: flex;
  flex-direction: column;
  background: var(--surface);
  box-shadow: var(--shadow);
}

.chat-messages {
  flex: 1;
  overflow: auto;
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 10px;
  background: var(--surface-2);
}

.chat-message {
  max-width: 85%;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 10px;
}

.chat-textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--border);
  border-radius: 10px;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.4;
  background: var(--surface-2);
  color: var(--ink);
  resize: vertical;
  transition: border-color 140ms ease;
}

.chat-textarea:focus {
  outline: none;
  border-color: var(--accent);
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.15);
}

.chat-textarea::placeholder {
  color: rgba(255, 255, 255, 0.35);
}

.send-button {
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid var(--accent);
  background: var(--accent);
  color: #fff;
  cursor: pointer;
  font-weight: 600;
  transition: background 140ms ease, box-shadow 140ms ease;
}

.send-button:hover:not(:disabled) {
  background: var(--accent-dark);
  box-shadow: 0 2px 8px rgba(124, 58, 237, 0.35);
}

.send-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 900px) {
  .plan-detail-page {
    padding: 20px 16px;
  }
}
</style>
