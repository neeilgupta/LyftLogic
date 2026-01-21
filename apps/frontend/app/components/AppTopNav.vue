<template>
  <header style="border-bottom: 1px solid #eee; background: #fff;">
    <div style="max-width: 1200px; margin: 0 auto; padding: 14px 20px; font-family: system-ui; display:flex; align-items:center; justify-content:space-between; gap: 12px;">
      <div style="font-weight: 800;">
        <NuxtLink to="/generate" style="text-decoration: none; color: inherit;">
          LyftLogic
        </NuxtLink>
      </div>

      <nav style="display:flex; gap: 14px; align-items:center;">
        <NuxtLink to="/generate" style="text-decoration: underline;">Generate</NuxtLink>
        <NuxtLink to="/nutrition" style="text-decoration: underline;">Nutrition</NuxtLink>
        <NuxtLink to="/roadmap" style="text-decoration: underline;">Roadmap</NuxtLink>
      </nav>
    </div>
  </header>
</template>
