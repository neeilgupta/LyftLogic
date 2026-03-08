// apps/frontend/composables/usePlans.ts
import { useRuntimeConfig } from "nuxt/app";
import { $fetch } from "ofetch";

export function usePlans() {
  const config = useRuntimeConfig();

  const baseURL = String((config.public as any).apiBase || "http://localhost:8000");


  async function getPlan(id: string) {
    const n = Number(id);
    if (!Number.isFinite(n) || n <= 0) {
      // prevent /plans/undefined (or any invalid id) from ever hitting backend
    throw new Error(`Invalid plan id: ${String(id)}`);
  }

  return await $fetch(`/plans/${n}`, { baseURL, method: "GET", credentials: "include" });
}


  const generatePlan = async (payload: any) => {
    return await $fetch("/plans/generate", {
      baseURL,
      method: "POST",
      credentials: "include",
      body: payload,
    });
  };

  const listMyPlans = async () => {
    return await $fetch("/plans", { baseURL, method: "GET", credentials: "include" });
  };

  const listMyNutritionPlans = async () => {
    return await $fetch("/nutrition/plans", { baseURL, method: "GET", credentials: "include" });
  };

  const getNutritionPlan = async (id: string | number) => {
    const n = Number(id);
    if (!Number.isFinite(n) || n <= 0) throw new Error(`Invalid nutrition plan id: ${String(id)}`);
    return await $fetch(`/nutrition/plans/${n}`, { baseURL, method: "GET", credentials: "include" });
  };

  const renamePlan = async (id: number, title: string) => {
    return await $fetch(`/plans/${id}/rename`, { baseURL, method: "PATCH", credentials: "include", body: { title } });
  };

  const renameNutritionPlan = async (id: number, title: string) => {
    return await $fetch(`/nutrition/plans/${id}/rename`, { baseURL, method: "PATCH", credentials: "include", body: { title } });
  };

  return { listMyPlans, getPlan, generatePlan, listMyNutritionPlans, getNutritionPlan, renamePlan, renameNutritionPlan };
}
