<template>
  <nav class="navbar">
    <RouterLink to="/" class="logo">RT</RouterLink>
    <div class="nav-tabs">
      <RouterLink to="/mechs"     class="nav-tab" active-class="nav-tab--active">Mechs</RouterLink>
      <RouterLink to="/vehicles"  class="nav-tab" active-class="nav-tab--active">Vehicles</RouterLink>
      <RouterLink to="/vtols"     class="nav-tab" active-class="nav-tab--active">VTOLs</RouterLink>
      <RouterLink to="/battle-armor" class="nav-tab" active-class="nav-tab--active">Battle Armor</RouterLink>
      <RouterLink to="/equipment" class="nav-tab" active-class="nav-tab--active">Equipment</RouterLink>
      <RouterLink to="/weapons"   class="nav-tab" active-class="nav-tab--active">Weapons</RouterLink>
      <RouterLink to="/quirks"    class="nav-tab" active-class="nav-tab--active">Quirks</RouterLink>
    </div>
    <div class="nav-right">
      <input class="search-input" type="text" placeholder="Search wiki..." />
      <div class="scale-btns">
        <button
          v-for="s in (['normal', 'large', 'xl'] as const)"
          :key="s"
          class="scale-btn"
          :class="{ active: scale === s }"
          :title="s === 'normal' ? 'Normal size' : s === 'large' ? 'Large size' : 'Extra large size'"
          @click="scale = s"
        >{{ s === 'normal' ? 'A' : s === 'large' ? 'A+' : 'A++' }}</button>
      </div>
      <button class="theme-toggle" @click="$emit('toggleTheme')" :title="theme === 'v1' ? 'Switch to V2 (Modern)' : 'Switch to V1 (Fandom)'">
        {{ theme === 'v1' ? 'V2 ↗' : 'V1 ↗' }}
      </button>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { useUIScale } from '../composables/useUIScale'
defineProps<{ theme: string }>()
defineEmits(['toggleTheme'])
const { scale } = useUIScale()
</script>

<style scoped>
.navbar {
  position: fixed;
  top: 0; left: 0; right: 0;
  height: var(--nav-height);
  background: var(--bg-nav);
  backdrop-filter: var(--nav-blur);
  -webkit-backdrop-filter: var(--nav-blur);
  border-bottom: var(--border-default);
  display: flex;
  align-items: center;
  padding: 0 24px;
  gap: 32px;
  z-index: 100;
}
.logo {
  color: var(--text-primary) !important;
  font-weight: bold;
  font-size: 18px;
  letter-spacing: 1px;
  text-decoration: none !important;
}
.nav-tabs { display: flex; flex: 1; }
.nav-tab {
  color: var(--text-muted);
  text-decoration: none;
  padding: 0 16px;
  line-height: var(--nav-height);
  font-size: 14px;
  border-bottom: 2px solid transparent;
  transition: color 0.15s, border-color 0.15s;
}
.nav-tab:hover { color: var(--text-primary); text-decoration: none; }
.nav-tab--active { color: var(--text-primary); border-bottom-color: var(--accent-blue); }
.nav-right {
  display: flex;
  align-items: center;
  gap: 10px;
}
.search-input {
  background: var(--bg-primary);
  border: var(--border-default);
  color: var(--text-primary);
  border-radius: 4px;
  padding: 6px 12px;
  width: 200px;
  font-size: 13px;
  outline: none;
  transition: border-color 0.15s;
}
.search-input:focus { border-color: var(--accent-orange); }
.theme-toggle {
  background: transparent;
  border: var(--border-default);
  color: var(--text-muted);
  border-radius: 4px;
  padding: 5px 10px;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  letter-spacing: 0.5px;
  transition: color 0.15s, border-color 0.15s;
  white-space: nowrap;
}
.theme-toggle:hover {
  color: var(--accent-blue);
  border-color: var(--accent-blue);
}
.scale-btns { display: flex; gap: 4px; }
.scale-btn {
  background: transparent;
  border: var(--border-default);
  color: var(--text-muted);
  border-radius: 4px;
  padding: 5px 8px;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  letter-spacing: 0.5px;
  transition: color 0.15s, border-color 0.15s;
  white-space: nowrap;
}
.scale-btn:hover { color: var(--accent-blue); border-color: var(--accent-blue); }
.scale-btn.active { color: var(--accent-blue); border-color: var(--accent-blue); }
</style>
