<template>
  <div style="padding: 20px; font-family: system-ui;">
    <h1>LyftLogic</h1>

    <button @click="test" :disabled="loading" style="padding: 10px 14px;">
      {{ loading ? "Loading..." : "Test GET /plans" }}
    </button>

    <p v-if="error" style="color: red; margin-top: 12px;">{{ error }}</p>

    <pre style="margin-top: 12px; white-space: pre-wrap;">{{ data }}</pre>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { usePlans } from "../../composables/usePlans";

const { listPlans } = usePlans();

const loading = ref(false);
const error = ref<string | null>(null);
const data = ref<any>(null);

async function test() {
  loading.value = true;
  error.value = null;

  try {
    data.value = await listPlans();
  } catch (e: any) {
    error.value = e?.data?.detail ?? e?.message ?? String(e);
  } finally {
    loading.value = false;
  }
}
</script>
