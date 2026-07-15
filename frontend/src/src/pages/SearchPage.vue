<template>
  <div class="search-page">
    <div class="search-bar-row">
      <input
        class="search-bar-input"
        type="text"
        placeholder="Search wiki..."
        :value="searchInput"
        @input="searchInput = ($event.target as HTMLInputElement).value"
        @keydown.enter="runSearch"
      />
    </div>

    <!-- Chassis section -->
    <section class="result-section">
      <h2 class="section-title">
        Chassis
        <span v-if="chassisData" class="result-count">{{ chassisData.total }} results</span>
      </h2>
      <div v-if="chassisLoading" class="loading">Loading…</div>
      <div v-else-if="q.length < 2" class="empty">Enter at least 2 characters to search.</div>
      <div v-else-if="!chassisData?.results.length" class="empty">No chassis results.</div>
      <template v-else>
        <div class="result-list">
          <button
            v-for="hit in chassisData.results"
            :key="hit.id"
            class="result-row"
            @click="navigate(hit)"
          >
            <span class="result-name">{{ hit.name }}</span>
            <span class="result-subtitle">{{ hit.subtitle }}</span>
          </button>
        </div>
        <div v-if="chassisData.total > PAGE_SIZE" class="pagination">
          <button
            class="page-btn"
            :disabled="chassisPage <= 1"
            @click="setChassisPage(chassisPage - 1)"
          >
            ← Prev
          </button>
          <span class="page-info"
            >Page {{ chassisPage }} of {{ Math.ceil(chassisData.total / PAGE_SIZE) }}</span
          >
          <button
            class="page-btn"
            :disabled="chassisPage >= Math.ceil(chassisData.total / PAGE_SIZE)"
            @click="setChassisPage(chassisPage + 1)"
          >
            Next →
          </button>
        </div>
      </template>
    </section>

    <!-- Gear section -->
    <section class="result-section">
      <h2 class="section-title">
        Gear
        <span v-if="gearData" class="result-count">{{ gearData.total }} results</span>
      </h2>
      <div v-if="gearLoading" class="loading">Loading…</div>
      <div v-else-if="q.length < 2" class="empty">Enter at least 2 characters to search.</div>
      <div v-else-if="!gearData?.results.length" class="empty">No gear results.</div>
      <template v-else>
        <div class="result-list">
          <button
            v-for="hit in gearData.results"
            :key="hit.id"
            class="result-row"
            @click="navigate(hit)"
          >
            <span class="result-name">{{ hit.name }}</span>
            <span class="result-subtitle">{{ hit.subtitle }}</span>
          </button>
        </div>
        <div v-if="gearData.total > PAGE_SIZE" class="pagination">
          <button class="page-btn" :disabled="gearPage <= 1" @click="setGearPage(gearPage - 1)">
            ← Prev
          </button>
          <span class="page-info"
            >Page {{ gearPage }} of {{ Math.ceil(gearData.total / PAGE_SIZE) }}</span
          >
          <button
            class="page-btn"
            :disabled="gearPage >= Math.ceil(gearData.total / PAGE_SIZE)"
            @click="setGearPage(gearPage + 1)"
          >
            Next →
          </button>
        </div>
      </template>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useChassisSearch, useGearSearch } from '../composables/useSearchPage'
import type { SearchHit } from '../composables/useGlobalSearch'

const PAGE_SIZE = 20

const route = useRoute()
const router = useRouter()

const q = computed(() => (route.query.q as string) || '')
const searchInput = ref(q.value)
watch(q, (v) => {
  searchInput.value = v
})

function runSearch() {
  const term = searchInput.value.trim()
  if (term.length >= 2) router.push({ path: '/search', query: { q: term } })
}
const chassisPage = computed(() => parseInt(route.query.chassis_page as string) || 1)
const gearPage = computed(() => parseInt(route.query.gear_page as string) || 1)

const { data: chassisData, isLoading: chassisLoading } = useChassisSearch(q, chassisPage)
const { data: gearData, isLoading: gearLoading } = useGearSearch(q, gearPage)

const TYPE_ROUTE: Record<string, string> = {
  mech: '/mechs',
  vehicle: '/vehicles',
  vtol: '/vtols',
  battle_armor: '/battle-armor',
  equipment: '/equipment',
  weapon: '/weapons',
  quirk: '/quirks',
}

function navigate(hit: SearchHit) {
  const base = `${TYPE_ROUTE[hit.result_type] ?? '/mechs'}/${hit.id}`
  router.push(hit.variant_id ? `${base}?variant=${encodeURIComponent(hit.variant_id)}` : base)
}

watch(q, () => {
  if (chassisPage.value !== 1 || gearPage.value !== 1) {
    router.replace({ query: { q: q.value } })
  }
})

function setChassisPage(p: number) {
  router.push({ query: { ...route.query, chassis_page: p } })
}

function setGearPage(p: number) {
  router.push({ query: { ...route.query, gear_page: p } })
}
</script>

<style scoped>
.search-page {
  max-width: var(--content-max-width, 1300px);
  margin: 0 auto;
  padding: 24px 16px;
}
.search-bar-row {
  margin-bottom: 32px;
}
.search-bar-input {
  width: 100%;
  max-width: 520px;
  background: var(--bg-card);
  border: var(--border-default);
  color: var(--text-primary);
  border-radius: 6px;
  padding: 10px 16px;
  font-size: 15px;
  outline: none;
  transition: border-color 0.15s;
}
.search-bar-input:focus {
  border-color: var(--accent-orange);
}
.search-heading {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 32px;
}
.search-term {
  color: var(--text-primary);
}
.result-section {
  margin-bottom: 40px;
}
.section-title {
  font-size: 13px;
  font-weight: 600;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  color: var(--text-muted);
  border-bottom: var(--border-default);
  padding-bottom: 8px;
  margin-bottom: 4px;
  display: flex;
  align-items: baseline;
  gap: 8px;
}
.result-count {
  font-weight: 400;
  font-size: 11px;
  text-transform: none;
  letter-spacing: 0;
}
.result-list {
  display: flex;
  flex-direction: column;
}
.result-row {
  display: flex;
  align-items: baseline;
  gap: 8px;
  padding: 8px 12px;
  background: transparent;
  border: none;
  border-bottom: 1px solid rgba(56, 96, 190, 0.15);
  color: var(--text-primary);
  cursor: pointer;
  text-align: left;
  font-size: 14px;
  transition: background 0.1s;
}
.result-row:hover {
  background: var(--bg-card-hover);
}
.result-name {
  flex: 1;
}
.result-subtitle {
  flex-shrink: 0;
  font-size: 12px;
  color: var(--text-muted);
  white-space: nowrap;
}
.pagination {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-top: 16px;
  padding: 8px 12px;
}
.page-btn {
  background: transparent;
  border: var(--border-default);
  color: var(--text-muted);
  border-radius: 4px;
  padding: 5px 12px;
  font-size: 12px;
  cursor: pointer;
  transition:
    color 0.15s,
    border-color 0.15s;
}
.page-btn:hover:not(:disabled) {
  color: var(--accent-blue);
  border-color: var(--accent-blue);
}
.page-btn:disabled {
  opacity: 0.35;
  cursor: default;
}
.page-info {
  font-size: 12px;
  color: var(--text-muted);
}
.loading,
.empty {
  padding: 16px 12px;
  font-size: 13px;
  color: var(--text-muted);
}
</style>
