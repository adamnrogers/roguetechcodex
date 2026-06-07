<template>
  <div class="skeleton-card">
    <div class="skel skel-title"></div>
    <div class="skel skel-badge"></div>
    <div class="skel skel-role"></div>
    <div class="skel skel-footer"></div>
  </div>
</template>

<style scoped>
.skeleton-card {
  background: var(--bg-card);
  border: var(--border-default);
  border-radius: var(--card-radius);
  padding: 14px;
  height: 120px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.skel {
  background: linear-gradient(90deg, #1a2235 25%, #232e4a 50%, #1a2235 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: 4px;
}
.skel-title  { height: 16px; width: 70%; }
.skel-badge  { height: 12px; width: 40%; }
.skel-role   { height: 12px; width: 55%; }
.skel-footer { height: 10px; width: 90%; margin-top: auto; }
@keyframes shimmer {
  0%   { background-position: 200% 0 }
  100% { background-position: -200% 0 }
}
</style>
