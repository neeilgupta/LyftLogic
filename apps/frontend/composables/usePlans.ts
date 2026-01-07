// apps/frontend/composables/usePlans.ts
import { useRuntimeConfig } from "nuxt/app";
import { $fetch } from "ofetch";

export function usePlans() {
  const config = useRuntimeConfig();

  const baseURL = String((config.public as any).apiBase || "http://127.0.0.1:8000");


  const listPlans = async () => {
    return await $fetch("/plans", { baseURL, method: "GET" });
  };

  async function getPlan(id: string) {
    const n = Number(id);
    if (!Number.isFinite(n) || n <= 0) {
      // prevent /plans/undefined (or any invalid id) from ever hitting backend
    throw new Error(`Invalid plan id: ${String(id)}`);
  }

  return await $fetch(`/plans/${n}`, { baseURL, method: "GET" });
}


  const generatePlan = async (payload: any) => {
    return await $fetch("/plans/generate", {
      baseURL,
      method: "POST",
      body: payload,
    });
  };

  return { listPlans, getPlan, generatePlan };
}
