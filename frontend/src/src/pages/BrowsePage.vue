<template>
  <div class="browse-layout">
    <FilterPanel
      :mode="mode"
      :modelValue="filters.weightClass"
      :era="filters.era"
      :minTonnage="filters.minTonnage"
      :maxTonnage="filters.maxTonnage"
      :hasLowerArm="filters.hasLowerArm"
      :hasHand="filters.hasHand"
      @update:modelValue="onWeightClassChange"
      @update:era="onEraChange"
      @update:minTonnage="v => filters = { ...filters, minTonnage: v, page: 1 }"
      @update:maxTonnage="v => filters = { ...filters, maxTonnage: v, page: 1 }"
      @update:hasLowerArm="v => filters = { ...filters, hasLowerArm: v, page: 1 }"
      @update:hasHand="v => filters = { ...filters, hasHand: v, page: 1 }"
      @clearAll="filters = { ...filters, weightClass: [], era: '', minTonnage: null, maxTonnage: null, hasLowerArm: null, hasHand: null, page: 1 }"
    />
    <div class="browse-main">
      <div class="search-row">
        <input
          v-model="searchInput"
          class="search-input"
          type="text"
          :placeholder="searchPlaceholder"
          @input="onSearchInput"
        />
      </div>
      <div v-if="filters.tag" class="tag-filter-bar">
        <span class="tag-filter-label">Filtered by quirk:</span>
        <span class="tag-filter-chip">
          {{ filters.tag }}
          <button class="tag-filter-clear" @click="clearTag" title="Remove filter">×</button>
        </span>
      </div>
      <SortBar
        :total="data?.total ?? 0"
        :label="modeLabel"
        :sortKey="`${filters.sort}:${filters.sortDir}`"
        @update:sortKey="onSortKeyChange"
      />
      <div v-if="isError" class="error-msg">
        Failed to load data. Please check your connection and try again.
      </div>
      <EntityGrid
        v-else
        :items="isLoading ? [] : (data?.results ?? [])"
        :mode="mode"
        :loading="isLoading"
      />
      <div class="pagination">
        <button
          class="page-btn"
          :disabled="filters.page <= 1"
          @click="prevPage"
        >&lt; Prev</button>
        <span class="page-info">
          Page {{ filters.page }} of {{ totalPages }}
        </span>
        <button
          class="page-btn"
          :disabled="isLastPage"
          @click="nextPage"
        >Next &gt;</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, toRef, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import FilterPanel from '../components/FilterPanel.vue'
import SortBar from '../components/SortBar.vue'
import EntityGrid from '../components/EntityGrid.vue'
import { useMechList, type MechFilters } from '../composables/useMechList'

const props = defineProps<{ mode: string }>()
const route = useRoute()
const router = useRouter()

const PAGE_SIZE = 60

const modeLabel = computed(() => {
  const map: Record<string, string> = {
    mech: 'Variants',
    vehicle: 'Variants',
    vtol: 'Variants',
    battle_armor: 'Variants',
    weapon: 'Weapons',
    equipment: 'Equipment',
  }
  return map[props.mode] ?? 'Items'
})

const searchPlaceholder = computed(() => {
  const map: Record<string, string> = {
    mech: 'Search mechs...',
    vehicle: 'Search vehicles...',
    vtol: 'Search VTOLs...',
    battle_armor: 'Search battle armor...',
    weapon: 'Search weapons...',
    equipment: 'Search equipment...',
  }
  return map[props.mode] ?? 'Search...'
})

// Read initial filter state from URL params
function readFiltersFromRoute(): MechFilters {
  const q = route.query.q as string ?? ''
  const wc = route.query.wc
  const weightClass = wc
    ? (Array.isArray(wc) ? wc as string[] : [wc as string])
    : []
  const era = route.query.era as string ?? ''
  const faction = route.query.faction as string ?? ''
  const tag = route.query.tag as string ?? ''
  const page = parseInt(route.query.page as string ?? '1') || 1
  const sort = route.query.sort as string ?? 'name'
  const sortDir = route.query.dir as string ?? 'asc'
  const minT = route.query.min_t ? parseFloat(route.query.min_t as string) : null
  const maxT = route.query.max_t ? parseFloat(route.query.max_t as string) : null
  const hasLowerArm = route.query.la === '1' ? true : route.query.la === '0' ? false : null
  const hasHand = route.query.ha === '1' ? true : route.query.ha === '0' ? false : null
  return { q, weightClass, era, faction, tag, page, sort, sortDir, minTonnage: minT, maxTonnage: maxT, hasLowerArm, hasHand }
}

function clearTag() {
  filters.value = { ...filters.value, tag: '', page: 1 }
}

const filters = ref<MechFilters>(readFiltersFromRoute())
const searchInput = ref(filters.value.q)

let searchTimer: ReturnType<typeof setTimeout> | null = null

function onSearchInput() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    filters.value = { ...filters.value, q: searchInput.value, page: 1 }
  }, 300)
}

function onWeightClassChange(wc: string[]) {
  filters.value = { ...filters.value, weightClass: wc, page: 1 }
}

function onEraChange(era: string) {
  filters.value = { ...filters.value, era, page: 1 }
}

function onSortKeyChange(key: string) {
  const [sort, sortDir] = key.split(':')
  filters.value = { ...filters.value, sort, sortDir, page: 1 }
}

function prevPage() {
  if (filters.value.page > 1) {
    filters.value = { ...filters.value, page: filters.value.page - 1 }
  }
}

function nextPage() {
  if (!isLastPage.value) {
    filters.value = { ...filters.value, page: filters.value.page + 1 }
  }
}

// Clear everything when tab changes
watch(() => props.mode, () => {
  if (searchTimer) clearTimeout(searchTimer)
  searchInput.value = ''
  filters.value = { q: '', weightClass: [], era: '', faction: '', tag: '', page: 1, sort: 'name', sortDir: 'asc', minTonnage: null, maxTonnage: null, hasLowerArm: null, hasHand: null }
})

// Sync filters to URL
watch(filters, (f) => {
  const query: Record<string, any> = {}
  if (f.q) query.q = f.q
  if (f.weightClass.length) query.wc = f.weightClass
  if (f.era) query.era = f.era
  if (f.faction) query.faction = f.faction
  if (f.tag) query.tag = f.tag
  if (f.page > 1) query.page = String(f.page)
  if (f.sort !== 'name') query.sort = f.sort
  if (f.sortDir !== 'asc') query.dir = f.sortDir
  if (f.minTonnage !== null) query.min_t = String(f.minTonnage)
  if (f.maxTonnage !== null) query.max_t = String(f.maxTonnage)
  if (f.hasLowerArm !== null) query.la = f.hasLowerArm ? '1' : '0'
  if (f.hasHand !== null) query.ha = f.hasHand ? '1' : '0'
  router.replace({ query })
}, { deep: true })

const { data, isLoading, isError } = useMechList(filters, toRef(props, 'mode'))

const totalPages = computed(() => {
  if (!data.value) return 1
  return Math.ceil(data.value.total / PAGE_SIZE)
})

const isLastPage = computed(() => {
  if (!data.value) return true
  return filters.value.page * PAGE_SIZE >= data.value.total
})
</script>

<style scoped>
.browse-layout {
  display: flex;
  min-height: calc(100vh - var(--nav-height));
}
.browse-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.search-row {
  padding: 12px 16px 0;
}
.search-input {
  width: 100%;
  max-width: 400px;
  background: var(--bg-card);
  border: var(--border-default);
  border-radius: 4px;
  color: var(--text-primary);
  font-size: 13px;
  padding: 7px 12px;
  outline: none;
  box-sizing: border-box;
  transition: border-color 0.15s;
}
.search-input::placeholder {
  color: var(--text-muted);
}
.search-input:focus {
  border-color: var(--accent-blue);
}
.tag-filter-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 16px 0;
  font-size: 12px;
}
.tag-filter-label {
  color: var(--text-muted);
}
.tag-filter-chip {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: rgba(88, 166, 255, 0.12);
  border: 1px solid rgba(88, 166, 255, 0.35);
  color: var(--accent-blue);
  border-radius: 20px;
  padding: 2px 8px 2px 10px;
  font-size: 12px;
  font-weight: 500;
}
.tag-filter-clear {
  background: none;
  border: none;
  color: var(--accent-blue);
  cursor: pointer;
  font-size: 14px;
  line-height: 1;
  padding: 0 1px;
  opacity: 0.7;
  transition: opacity 0.15s;
}
.tag-filter-clear:hover {
  opacity: 1;
}
.error-msg {
  padding: 32px 16px;
  color: var(--accent-orange);
  font-size: 14px;
  text-align: center;
}
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 16px 0;
}
.page-btn {
  border: var(--border-default);
  background: transparent;
  color: var(--text-primary);
  padding: 6px 14px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  transition: border-color 0.15s, color 0.15s;
}
.page-btn:hover:not(:disabled) {
  border-color: var(--accent-orange);
  color: var(--accent-orange);
}
.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.page-info {
  font-size: 13px;
  color: var(--text-muted);
}
</style>
