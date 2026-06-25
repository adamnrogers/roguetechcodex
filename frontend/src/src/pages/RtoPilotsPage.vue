<template>
  <div class="rto-page">
    <h1 class="rto-title">RTO Pilots</h1>
    <input
      class="rto-search"
      type="text"
      placeholder="Search by callsign or name..."
      v-model="query"
    />
    <div v-if="isError" class="error-msg">
      Failed to load data. Please check your connection and try again.
    </div>
    <div v-else-if="isLoading" class="rto-grid">
      <SkeletonCard v-for="n in 12" :key="n" />
    </div>
    <div v-else class="rto-grid">
      <RtoPilotCard v-for="p in filtered" :key="p.id" :pilot="p" />
      <div v-if="!filtered.length" class="empty-msg">No RTO pilots found.</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRtoPilots } from '../composables/useRtoPilots'
import RtoPilotCard from '../components/RtoPilotCard.vue'
import SkeletonCard from '../components/SkeletonCard.vue'

const { data, isLoading, isError } = useRtoPilots()

const query = ref('')

const filtered = computed(() => {
  const pilots = data.value ?? []
  const q = query.value.trim().toLowerCase()
  if (!q) return pilots
  return pilots.filter(p =>
    (p.callsign?.toLowerCase().includes(q)) || p.ui_name.toLowerCase().includes(q)
  )
})
</script>

<style scoped>
.rto-page {
  padding: 16px;
}

.rto-title {
  color: var(--text-primary);
  font-size: 22px;
  margin: 0 0 16px;
}

.rto-search {
  display: block;
  background: var(--bg-primary);
  border: var(--border-default);
  color: var(--text-primary);
  border-radius: 4px;
  padding: 8px 12px;
  width: 280px;
  font-size: 13px;
  outline: none;
  margin-bottom: 16px;
  transition: border-color 0.15s;
}

.rto-search:focus {
  border-color: var(--accent-orange);
}

.rto-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
  gap: 14px;
}

.empty-msg,
.error-msg {
  color: var(--text-muted);
  grid-column: 1 / -1;
  text-align: center;
  padding: 32px 0;
}

.error-msg {
  color: var(--accent-orange);
}
</style>
