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
  </nav>
</div>

  </header>
</template>
