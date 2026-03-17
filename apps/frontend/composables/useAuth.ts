// apps/frontend/composables/useAuth.ts
import { useRuntimeConfig } from "nuxt/app";
import { $fetch } from "ofetch";

type User = {
  id: number;
  email: string;
  has_password?: boolean;
  created_at?: string;
  email_verified?: boolean;
};

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

  const register = async (email: string, password: string): Promise<{ detail: string }> => {
    return await $fetch("/auth/register", {
      baseURL,
      method: "POST",
      credentials: "include",
      body: { email, password },
    });
  };

  const passwordLogin = async (email: string, password: string): Promise<User> => {
    return await $fetch("/auth/password-login", {
      baseURL,
      method: "POST",
      credentials: "include",
      body: { email, password },
    });
  };

  const verifyEmail = async (token: string): Promise<User> => {
    return await $fetch("/auth/verify-email", {
      baseURL,
      method: "GET",
      credentials: "include",
      params: { token },
    });
  };

  const resendVerification = async (email: string): Promise<{ detail: string }> => {
    return await $fetch("/auth/resend-verification", {
      baseURL,
      method: "POST",
      credentials: "include",
      body: { email },
    });
  };

  const forgotPassword = async (email: string): Promise<{ detail: string }> => {
    return await $fetch("/auth/forgot-password", {
      baseURL,
      method: "POST",
      credentials: "include",
      body: { email },
    });
  };

  const resetPassword = async (token: string, password: string): Promise<{ detail: string }> => {
    return await $fetch("/auth/reset-password", {
      baseURL,
      method: "POST",
      credentials: "include",
      body: { token, password },
    });
  };

  const changePassword = async (currentPassword: string, newPassword: string): Promise<{ ok: boolean; detail: string }> => {
    return await $fetch("/auth/change-password", {
      baseURL,
      method: "POST",
      credentials: "include",
      body: { current_password: currentPassword, new_password: newPassword },
    });
  };

  const deleteAccount = async (password?: string): Promise<{ ok: boolean }> => {
    return await $fetch("/auth/account", {
      baseURL,
      method: "DELETE",
      credentials: "include",
      body: { password: password ?? null },
    });
  };

  return {
    requestCode,
    verifyCode,
    logout,
    me,
    register,
    passwordLogin,
    verifyEmail,
    resendVerification,
    forgotPassword,
    resetPassword,
    changePassword,
    deleteAccount,
  };
}
