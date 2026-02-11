// apps/frontend/composables/useAuth.ts
import { useRuntimeConfig } from "nuxt/app";
import { $fetch } from "ofetch";

type User = { id: number; email: string };

export function useAuth() {
  const config = useRuntimeConfig();
  const baseURL = String((config.public as any).apiBase || "http://localhost:8000");

  const login = async (email: string): Promise<User> => {
    return await $fetch("/auth/login", {
      baseURL,
      method: "POST",
      credentials: "include",
      body: { email },
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

  return { login, logout, me };
}
