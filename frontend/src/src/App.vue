<template>
  <TheNavBar :theme="currentTheme" @toggle-theme="toggleTheme" />
  <main class="main-content">
    <RouterView />
  </main>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import TheNavBar from './components/TheNavBar.vue'
import { useUIScale } from './composables/useUIScale'
useUIScale()

const currentTheme = ref<'v1' | 'v2'>('v2')

function applyTheme(theme: 'v1' | 'v2') {
  if (theme === 'v2') {
    document.documentElement.setAttribute('data-theme', 'v2')
  } else {
    document.documentElement.removeAttribute('data-theme')
  }
}

function toggleTheme() {
  currentTheme.value = currentTheme.value === 'v1' ? 'v2' : 'v1'
  const url = new URL(window.location.href)
  if (currentTheme.value === 'v1') {
    url.searchParams.set('theme', 'v1')
  } else {
    url.searchParams.delete('theme')
  }
  window.history.replaceState({}, '', url)
}

watch(currentTheme, applyTheme)

onMounted(() => {
  const params = new URLSearchParams(window.location.search)
  if (params.get('theme') === 'v1') {
    currentTheme.value = 'v1'
  }
  applyTheme(currentTheme.value)
})
</script>

<style>
.main-content {
  margin-top: var(--nav-height);
  min-height: calc(100vh - var(--nav-height));
}
</style>
