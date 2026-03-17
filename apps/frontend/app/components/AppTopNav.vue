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
  <header class="nav">
    <div class="nav-inner">
      <NuxtLink to="/" class="wordmark">Lyft<span class="accent">Logic</span></NuxtLink>

      <nav class="nav-links">
        <NuxtLink to="/generate" class="nav-link">Generate</NuxtLink>
        <NuxtLink to="/nutrition" class="nav-link">Nutrition</NuxtLink>
        <NuxtLink to="/roadmap" class="nav-link">Roadmap</NuxtLink>

        <template v-if="user">
          <span class="nav-email">{{ user.email }}</span>
          <NuxtLink to="/settings" class="nav-link">Settings</NuxtLink>
          <button class="nav-signout" @click="handleLogout">Sign out</button>
        </template>
        <NuxtLink v-else to="/login" class="nav-sign-in">Sign in</NuxtLink>

        <NuxtLink to="/plans" class="nav-plans-icon" title="My Plans">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M20 21C20 19.6044 20 18.9067 19.8278 18.3389C19.44 17.0605 18.4395 16.06 17.1611 15.6722C16.5933 15.5 15.8956 15.5 14.5 15.5H9.5C8.10444 15.5 7.40665 15.5 6.83886 15.6722C5.56045 16.06 4.56004 17.0605 4.17224 18.3389C4 18.9067 4 19.6044 4 21M16.5 7.5C16.5 9.98528 14.4853 12 12 12C9.51472 12 7.5 9.98528 7.5 7.5C7.5 5.01472 9.51472 3 12 3C14.4853 3 16.5 5.01472 16.5 7.5Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </NuxtLink>
      </nav>
    </div>
  </header>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;900&family=DM+Mono:wght@400;500&family=DM+Sans:wght@400;500;600&display=swap');

.nav {
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  background: #090907;
  position: sticky;
  top: 0;
  z-index: 100;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.nav-inner {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 32px;
  height: 54px;
  display: flex;
  align-items: center;
  gap: 0;
  box-sizing: border-box;
}

.wordmark {
  font-family: 'Syne', sans-serif;
  font-size: 19px;
  font-weight: 900;
  letter-spacing: -0.03em;
  text-decoration: none;
  color: #f0ede6;
  flex-shrink: 0;
}

.accent {
  color: #7c3aed;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 22px;
  margin-left: auto;
  flex-wrap: nowrap;
}

.nav-link {
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.07em;
  text-transform: uppercase;
  color: rgba(240, 237, 230, 0.45);
  text-decoration: none;
  transition: color 0.15s;
  white-space: nowrap;
}

.nav-link:hover,
.nav-link.router-link-active {
  color: #f0ede6;
}

.nav-email {
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  color: rgba(240, 237, 230, 0.3);
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.nav-signout {
  background: none;
  border: 1px solid rgba(124, 58, 237, 0.25);
  color: rgba(124, 58, 237, 0.7);
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  padding: 5px 12px;
  border-radius: 3px;
  cursor: pointer;
  transition: border-color 0.15s, color 0.15s;
  white-space: nowrap;
}

.nav-signout:hover {
  border-color: #7c3aed;
  color: #7c3aed;
}

.nav-sign-in {
  font-family: 'DM Mono', monospace;
  font-size: 11px;
  font-weight: 500;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: #7c3aed;
  text-decoration: none;
  opacity: 0.75;
  transition: opacity 0.15s;
  white-space: nowrap;
}

.nav-sign-in:hover {
  opacity: 1;
}

.nav-plans-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border: 1px solid rgba(124, 58, 237, 0.25);
  border-radius: 3px;
  background: rgba(124, 58, 237, 0.04);
  text-decoration: none;
  color: rgba(124, 58, 237, 0.6);
  transition: border-color 0.15s, color 0.15s, background 0.15s;
  flex-shrink: 0;
}

.nav-plans-icon:hover {
  border-color: #7c3aed;
  color: #7c3aed;
  background: rgba(124, 58, 237, 0.08);
}

@media (max-width: 768px) {
  .nav-inner {
    padding: 0 18px;
  }

  .nav-links {
    gap: 14px;
  }

  .nav-email {
    display: none;
  }
}
</style>
