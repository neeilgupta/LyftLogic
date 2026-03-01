// apps/frontend/composables/useAuth.ts
import { useRuntimeConfig } from "nuxt/app";
import { $fetch } from "ofetch";

type User = { id: number; email: string };

export function useAuth() {
  const config = useRuntimeConfig();
  const baseURL = String((config.public as any).apiBase || "http://localhost:8000");

  const requestCode = async (email: string): Promise<{ detail: string }> => {
    return await $fetch("/auth/request-code", {
      baseURL,
      method: "POST",
      credentials: "include",
      body: { email },
    });
  };

  const verifyCode = async (email: string, code: string): Promise<User> => {
    return await $fetch("/auth/verify-code", {
      baseURL,
      method: "POST",
      credentials: "include",
      body: { email, code },
    });
  };

  const logout = async (): Promise<{ ok: boolean }> => {
    return await $fetch("/auth/logout", {
      baseURL,
      method: "POST",
      credentials: "include",
    });
  };

  const me = async (): Promise<User | null> => {
    try {
      return await $fetch("/auth/me", {
        baseURL,
        method: "GET",
        credentials: "include",
      });
    } catch (e: any) {
      if (e?.status === 401) return null;
      if (e?.response?.status === 401) return null;
      throw e;
    }
  };

  return { requestCode, verifyCode, logout, me };
}
