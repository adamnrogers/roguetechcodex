<template>
  <TheNavBar :theme="currentTheme" @toggle-theme="toggleTheme" />
  <main class="main-content">
    <RouterView />
  </main>
</template>

<script setup lang="ts">
import TheNavBar from './components/TheNavBar.vue'
import { useUIScale } from './composables/useUIScale'
import { useTheme } from './composables/useTheme'
useUIScale()

const { theme: currentTheme } = useTheme()

function toggleTheme() {
  currentTheme.value = currentTheme.value === 'v1' ? 'v2' : 'v1'
}
</script>

<style>
.main-content {
  margin-top: var(--nav-height);
  min-height: calc(100vh - var(--nav-height));
}
</style>
