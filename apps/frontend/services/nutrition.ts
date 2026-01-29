// apps/frontend/services/nutrition.ts
import { useRuntimeConfig } from "nuxt/app";
import { $fetch } from "ofetch";

export type NutritionTargets = {
  maintenance: number;
  cut: Record<string, number>;   // keys: "0.5" | "1" | "2"
  bulk: Record<string, number>;
};

export type NutritionVersionSnapshotV1 = {
  version: number;
  targets: NutritionTargets;
  accepted_meals: Array<{ key: string; name: string }>;
  rejected_meals: Array<{ key: string; name: string }>;
  constraints_snapshot: Record<string, any>;
};

export type NutritionGenerateRequest = {
  targets: NutritionTargets;
  diet?: string | null;
  allergies?: string[];
  meals_needed: number;
  max_attempts: number;
  batch_size: number;
};

export type MacroCalcRequest = {
  sex: "male" | "female";
  age: number;
  height_cm: number;
  weight_kg: number;
  activity_level: "sedentary" | "light" | "moderate" | "very" | "athlete" | "active" | "very_active";
};

export type MacroCalcResponse = {
  implemented: boolean;
  message: string;
  macros: {
    tdee: number;
    maintenance: number;
    targets: NutritionTargets;
    explanation: string;
    activity_multiplier: number;
    bmr: number;
  };
};

export type NutritionGenerateResponse = {
  output: Record<string, any>;
  version_snapshot: NutritionVersionSnapshotV1;
};

export type NutritionRegenerateRequest = NutritionGenerateRequest & {
  prev_snapshot: NutritionVersionSnapshotV1;
};

export type NutritionRegenerateResponse = {
  output: Record<string, any>;
  version_snapshot: NutritionVersionSnapshotV1;
  diff: Record<string, any>;
  explanations: string[];
};

export function useNutritionApi() {
  const config = useRuntimeConfig();
  const baseURL = String((config.public as any).apiBase || "http://127.0.0.1:8000");

  async function generateNutrition(payload: NutritionGenerateRequest) {
    return await $fetch<NutritionGenerateResponse>("/nutrition/generate", {
      baseURL,
      method: "POST",
      body: payload,
    });
  }

  async function regenerateNutrition(payload: NutritionRegenerateRequest) {
    return await $fetch<NutritionRegenerateResponse>("/nutrition/regenerate", {
      baseURL,
      method: "POST",
      body: payload,
    });
  }
  
  async function macroCalc(payload: MacroCalcRequest) {
    return await $fetch<MacroCalcResponse>("/nutrition/macro-calc", {
      baseURL,
      method: "POST",
      body: payload,
    });
  }


    return { generateNutrition, regenerateNutrition, macroCalc };

}
