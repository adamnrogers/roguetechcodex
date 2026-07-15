<template>
  <nav class="navbar">
    <div class="logo-block">
      <RouterLink to="/" class="logo">RTC</RouterLink>
      <span class="logo-version">{{ appVersion }}</span>
    </div>
    <div class="nav-tabs">
      <RouterLink to="/mechs" class="nav-tab" active-class="nav-tab--active">Mechs</RouterLink>
      <RouterLink to="/vehicles" class="nav-tab" active-class="nav-tab--active"
        >Vehicles</RouterLink
      >
      <RouterLink to="/vtols" class="nav-tab" active-class="nav-tab--active">VTOLs</RouterLink>
      <RouterLink to="/battle-armor" class="nav-tab" active-class="nav-tab--active"
        >Battle Armor</RouterLink
      >
      <RouterLink to="/equipment" class="nav-tab" active-class="nav-tab--active"
        >Equipment</RouterLink
      >
      <RouterLink to="/weapons" class="nav-tab" active-class="nav-tab--active">Weapons</RouterLink>
      <RouterLink to="/quirks" class="nav-tab" active-class="nav-tab--active">Quirks</RouterLink>
      <RouterLink to="/star-systems" class="nav-tab" active-class="nav-tab--active"
        >Systems</RouterLink
      >
      <RouterLink to="/rto-pilots" class="nav-tab" active-class="nav-tab--active"
        >RTO Pilots</RouterLink
      >
    </div>
    <div class="nav-right">
      <div class="search-wrapper">
        <input
          v-model="rawQuery"
          class="search-input"
          type="text"
          placeholder="Search wiki..."
          @keydown.enter="handleSearchEnter"
          @keydown.escape="closeSearch"
        />
        <GlobalSearchResults v-if="showResults" :data="searchData!" @close="closeSearch" />
      </div>
      <select v-model="scale" class="scale-select" title="Text size">
        <option value="normal">A</option>
        <option value="large">A+</option>
        <option value="xl">A++</option>
      </select>
      <button
        class="theme-toggle"
        :title="theme === 'v1' ? 'Switch to Dark mode' : 'Switch to Light mode'"
        @click="$emit('toggleTheme')"
      >
        {{ theme === 'v1' ? '☀' : '☾' }}
      </button>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUIScale } from '../composables/useUIScale'
import { useGlobalSearch } from '../composables/useGlobalSearch'
import GlobalSearchResults from './GlobalSearchResults.vue'

defineProps<{ theme: string }>()
defineEmits(['toggleTheme'])

const appVersion = __APP_VERSION__

const route = useRoute()
const router = useRouter()

const { scale } = useUIScale()

const rawQuery = ref('')
const debouncedQuery = ref('')
let debounceTimer: ReturnType<typeof setTimeout> | null = null

watch(rawQuery, (val) => {
  if (debounceTimer) clearTimeout(debounceTimer)
  if (val.length < 2) {
    debouncedQuery.value = ''
    return
  }
  debounceTimer = setTimeout(() => {
    debouncedQuery.value = val
  }, 300)
})

const { data: searchData } = useGlobalSearch(debouncedQuery)

const showResults = computed(
  () =>
    route.path !== '/search' && debouncedQuery.value.length >= 2 && searchData.value !== undefined,
)

function closeSearch() {
  rawQuery.value = ''
  debouncedQuery.value = ''
}

function handleSearchEnter() {
  if (rawQuery.value.length >= 2) {
    router.push({ path: '/search', query: { q: rawQuery.value } })
    closeSearch()
  }
}

watch(
  () => route.path,
  (path, prev) => {
    if (path === '/search' || prev === '/search') closeSearch()
  },
)
</script>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: var(--nav-height);
  background: var(--bg-nav);
  backdrop-filter: var(--nav-blur);
  -webkit-backdrop-filter: var(--nav-blur);
  border-bottom: var(--border-default);
  display: flex;
  align-items: center;
  padding: 0 24px;
  gap: var(--nav-gap, 32px);
  z-index: 1000;
}
.logo-block {
  display: flex;
  flex-direction: column;
  align-items: center;
  line-height: 1;
  gap: 2px;
  flex-shrink: 0;
}
.logo {
  color: var(--text-primary) !important;
  font-weight: bold;
  font-size: 18px;
  letter-spacing: 1px;
  text-decoration: none !important;
}
.logo-version {
  color: var(--text-muted);
  font-size: 10px;
  letter-spacing: 0.5px;
  opacity: 0.7;
}
.nav-tabs {
  display: flex;
  flex: 1;
  min-width: 0;
  overflow-x: auto;
  scrollbar-width: none;
}
.nav-tabs::-webkit-scrollbar {
  display: none;
}
.nav-tab {
  color: var(--text-muted);
  text-decoration: none;
  padding: var(--nav-tab-padding, 0 16px);
  line-height: var(--nav-height);
  font-size: 14px;
  white-space: nowrap;
  border-bottom: 2px solid transparent;
  transition:
    color 0.15s,
    border-color 0.15s;
}
.nav-tab:hover {
  color: var(--text-primary);
  text-decoration: none;
}
.nav-tab--active {
  color: var(--text-primary);
  border-bottom-color: var(--accent-blue);
}
.nav-right {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-shrink: 0;
}
.search-wrapper {
  position: relative;
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
.search-input:focus {
  border-color: var(--accent-orange);
}
.theme-toggle {
  background: transparent;
  border: var(--border-default);
  color: var(--text-muted);
  border-radius: 4px;
  padding: 4px 6px;
  font-size: 13px;
  cursor: pointer;
  transition:
    color 0.15s,
    border-color 0.15s;
  width: 28px;
  height: 26px;
  text-align: center;
  line-height: 1;
}
.theme-toggle:hover {
  color: var(--accent-blue);
  border-color: var(--accent-blue);
}
.scale-select {
  background: transparent;
  border: var(--border-default);
  color: var(--text-muted);
  border-radius: 4px;
  padding: 3px 4px;
  font-size: 11px;
  font-weight: 600;
  cursor: pointer;
  height: 26px;
  width: 48px;
  transition:
    color 0.15s,
    border-color 0.15s;
}
.scale-select:hover,
.scale-select:focus {
  color: var(--accent-blue);
  border-color: var(--accent-blue);
  outline: none;
}
</style>
