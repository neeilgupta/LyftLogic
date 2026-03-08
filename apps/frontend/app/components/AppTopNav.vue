<script setup>
import { useAuth } from "../../composables/useAuth"

const { me, logout } = useAuth()
const user = useState('user', () => null)

onMounted(async () => {
  user.value = await me()
})

async function handleLogout() {
  await logout()
  user.value = null
  navigateTo('/login')
}
</script>

<template>
  <header
    style="
      border-bottom: 1px solid rgba(255,255,255,0.08);
      background: radial-gradient(1200px 600px at 20% 0%, rgba(124,58,237,0.18), rgba(0,0,0,0)) , #070A12;
    "
  >
<div
  style="
    width: 100%;
    margin: 0;
    padding: 14px 18px;
    box-sizing: border-box;
    font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
    display: flex;
    align-items: center;
    gap: 14px;
  "
>
  <!-- LEFT: logo -->
  <div style="font-weight: 900; font-size: 20px; letter-spacing: 0.2px;">
    <NuxtLink
      to="/"
      style="text-decoration: none; color: rgba(255,255,255,0.95);"
    >
      LyftLogic
    </NuxtLink>

  </div>

  <!-- RIGHT: tabs -->
  <nav
    style="
      display: flex;
      align-items: center;
      gap: 18px;
      margin-left: auto;
      flex-wrap: wrap;
      row-gap: 10px;
    "
  >
    <NuxtLink to="/generate" style="color: rgba(255,255,255,0.9); text-decoration: none; font-weight: 650; white-space: nowrap;">
      Generate
    </NuxtLink>
    <NuxtLink to="/nutrition" style="color: rgba(255,255,255,0.9); text-decoration: none; font-weight: 650; white-space: nowrap;">
      Nutrition
    </NuxtLink>
    <NuxtLink to="/roadmap" style="color: rgba(255,255,255,0.9); text-decoration: none; font-weight: 650; white-space: nowrap;">
      Roadmap
    </NuxtLink>
    <template v-if="user">
      <span style="color: rgba(255,255,255,0.5); font-size: 13px; white-space: nowrap; max-width: 160px; overflow: hidden; text-overflow: ellipsis;">{{ user.email }}</span>
      <button
        @click="handleLogout"
        style="background: none; border: 1px solid rgba(124,58,237,0.5); color: rgba(167,139,250,1); font-weight: 700; font-size: 14px; padding: 4px 12px; border-radius: 6px; cursor: pointer; white-space: nowrap; font-family: inherit;"
      >Sign out</button>
    </template>
    <NuxtLink v-else to="/login" style="color: rgba(167,139,250,1); text-decoration: none; font-weight: 700; white-space: nowrap;">
      Sign in
    </NuxtLink>
    <NuxtLink
      to="/plans"
      style="
        display: flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        border: 1px solid rgba(124,58,237,0.5);
        background: rgba(124,58,237,0.15);
        text-decoration: none;
        font-size: 16px;
        line-height: 1;
        flex-shrink: 0;
        color: rgba(124,58,237,1);
      "
      title="My Plans"
    ><svg width="100%" height="100%" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
 <path d="M20 21C20 19.6044 20 18.9067 19.8278 18.3389C19.44 17.0605 18.4395 16.06 17.1611 15.6722C16.5933 15.5 15.8956 15.5 14.5 15.5H9.5C8.10444 15.5 7.40665 15.5 6.83886 15.6722C5.56045 16.06 4.56004 17.0605 4.17224 18.3389C4 18.9067 4 19.6044 4 21M16.5 7.5C16.5 9.98528 14.4853 12 12 12C9.51472 12 7.5 9.98528 7.5 7.5C7.5 5.01472 9.51472 3 12 3C14.4853 3 16.5 5.01472 16.5 7.5Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
 </svg></NuxtLink>
  </nav>
</div>

  </header>
</template>
