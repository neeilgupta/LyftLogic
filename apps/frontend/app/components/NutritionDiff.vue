<template>
  <div>
    <div style="display:flex; align-items:baseline; justify-content:space-between; gap:10px;">
      <div style="font-weight: 800;">Nutrition changes</div>
      <div v-if="version != null" style="opacity:0.7; font-size: 13px;">v{{ version }}</div>
    </div>

    <div v-if="!explanations || explanations.length === 0" style="opacity: 0.7; font-size: 13px; margin-top: 8px;">
      No changes.
    </div>

    <ul v-else style="margin: 8px 0 0; padding-left: 18px; line-height: 1.6;">
      <li v-for="(e, i) in explanations" :key="`ne-${i}`">{{ e }}</li>
    </ul>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  explanations: string[] | null;
  version: number | null;
}>();
</script>
