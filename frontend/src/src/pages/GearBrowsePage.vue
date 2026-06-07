<template>
  <div class="browse-layout">
    <GearFilterPanel
      :mode="mode"
      :includeTypes="filters.includeTypes"
      :excludeTypes="filters.excludeTypes"
      :includeCategories="filters.includeCategories"
      :excludeCategories="filters.excludeCategories"
      :includeLocations="filters.includeLocations"
      :excludeLocations="filters.excludeLocations"
      @update:includeTypes="v => onFilterUpdate({ includeTypes: v })"
      @update:excludeTypes="v => onFilterUpdate({ excludeTypes: v })"
      @update:includeCategories="v => onFilterUpdate({ includeCategories: v })"
      @update:excludeCategories="v => onFilterUpdate({ excludeCategories: v })"
      @update:includeLocations="v => onFilterUpdate({ includeLocations: v })"
      @update:excludeLocations="v => onFilterUpdate({ excludeLocations: v })"
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
      <SortBar
        :total="data?.total ?? 0"
        :label="modeLabel"
        :sortKey="`${filters.sort}:${filters.sortDir}`"
        :options="sortOptions"
        @update:sortKey="onSortKeyChange"
      />
      <div v-if="isError" class="error-msg">
        Failed to load data. Please check your connection and try again.
      </div>
      <div v-else-if="isLoading" class="gear-grid">
        <SkeletonCard v-for="n in 12" :key="n" />
      </div>
      <div v-else class="gear-grid">
        <GearCard
          v-for="item in data?.results ?? []"
          :key="item.id"
          v-bind="item"
          :mode="mode"
        />
        <div v-if="!data?.results?.length" class="empty-msg">No results found.</div>
      </div>
      <div class="pagination">
        <button class="page-btn" :disabled="filters.page <= 1" @click="prevPage">&lt; Prev</button>
        <span class="page-info">Page {{ filters.page }} of {{ totalPages }}</span>
        <button class="page-btn" :disabled="isLastPage" @click="nextPage">Next &gt;</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import GearFilterPanel from '../components/GearFilterPanel.vue'
import SortBar from '../components/SortBar.vue'
import SkeletonCard from '../components/SkeletonCard.vue'
import GearCard from '../components/GearCard.vue'
import { useGearList, type GearFilters } from '../composables/useGearList'
import type { SortOption } from '../components/SortBar.vue'

const props = defineProps<{ mode: string }>()
const route = useRoute()
const router = useRouter()

const PAGE_SIZE = 60

// ── Computed labels ──────────────────────────────────────────────────────────

const modeLabel = computed(() => {
  const map: Record<string, string> = { equipment: 'Equipment', weapon: 'Weapons', quirk: 'Quirks' }
  return map[props.mode] ?? 'Items'
})

const searchPlaceholder = computed(() => {
  const map: Record<string, string> = {
    equipment: 'Search equipment...',
    weapon:    'Search weapons...',
    quirk:     'Search quirks...',
  }
  return map[props.mode] ?? 'Search...'
})

const sortOptions = computed((): SortOption[] => {
  if (props.mode === 'weapon') {
    return [
      { value: 'name:asc',    label: 'Name (A–Z)' },
      { value: 'name:desc',   label: 'Name (Z–A)' },
      { value: 'damage:desc', label: 'Damage ↓' },
      { value: 'damage:asc',  label: 'Damage ↑' },
      { value: 'tonnage:asc', label: 'Tonnage ↑' },
    ]
  }
  return [
    { value: 'name:asc',     label: 'Name (A–Z)' },
    { value: 'name:desc',    label: 'Name (Z–A)' },
    { value: 'tonnage:asc',  label: 'Tonnage ↑' },
    { value: 'tonnage:desc', label: 'Tonnage ↓' },
  ]
})

const componentTypeParam = computed(() => {
  const map: Record<string, string> = { equipment: 'equipment', weapon: 'weapon', quirk: 'quirk' }
  return map[props.mode] ?? ''
})

// ── Filter state ─────────────────────────────────────────────────────────────

function defaultFilters(): GearFilters {
  return {
    q: '',
    componentType: componentTypeParam.value,
    includeTypes: [],
    excludeTypes: [],
    includeCategories: [],
    excludeCategories: [],
    includeLocations: [],
    excludeLocations: [],
    page: 1,
    sort: 'name',
    sortDir: 'asc',
  }
}

function readFilters(): GearFilters {
  const q           = (route.query.q    as string) ?? ''
  const page        = parseInt((route.query.page as string) ?? '1') || 1
  const defaultSort = 'name'
  const defaultDir  = 'asc'
  const sort        = (route.query.sort as string) ?? defaultSort
  const sortDir     = (route.query.dir  as string) ?? defaultDir
  const incRaw      = (route.query.inc  as string) ?? ''
  const excRaw      = (route.query.exc  as string) ?? ''
  const incCatRaw   = (route.query.incc as string) ?? ''
  const excCatRaw   = (route.query.excc as string) ?? ''
  const incLocRaw   = (route.query.incl as string) ?? ''
  const excLocRaw   = (route.query.excl as string) ?? ''
  return {
    q,
    componentType: componentTypeParam.value,
    includeTypes:      incRaw    ? incRaw.split(',').filter(Boolean)    : [],
    excludeTypes:      excRaw    ? excRaw.split(',').filter(Boolean)    : [],
    includeCategories: incCatRaw ? incCatRaw.split(',').filter(Boolean) : [],
    excludeCategories: excCatRaw ? excCatRaw.split(',').filter(Boolean) : [],
    includeLocations:  incLocRaw ? incLocRaw.split(',').filter(Boolean) : [],
    excludeLocations:  excLocRaw ? excLocRaw.split(',').filter(Boolean) : [],
    page, sort, sortDir,
  }
}

const filters = ref<GearFilters>(readFilters())
const searchInput = ref(filters.value.q)

function onFilterUpdate(patch: Partial<GearFilters>) {
  filters.value = { ...filters.value, ...patch, page: 1 }
}

let searchTimer: ReturnType<typeof setTimeout> | null = null

function onSearchInput() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    filters.value = { ...filters.value, q: searchInput.value, page: 1 }
  }, 300)
}

function onSortKeyChange(key: string) {
  const [sort, sortDir] = key.split(':')
  filters.value = { ...filters.value, sort, sortDir, page: 1 }
}

function prevPage() {
  if (filters.value.page > 1) filters.value = { ...filters.value, page: filters.value.page - 1 }
}

function nextPage() {
  if (!isLastPage.value) filters.value = { ...filters.value, page: filters.value.page + 1 }
}

// Reset on mode change
watch(() => props.mode, () => {
  if (searchTimer) clearTimeout(searchTimer)
  searchInput.value = ''
  filters.value = defaultFilters()
})

// Sync to URL
watch(filters, (f) => {
  const defaultSort = 'name'
  const defaultDir  = 'asc'
  const query: Record<string, any> = {}
  if (f.q)                        query.q    = f.q
  if (f.includeTypes.length)      query.inc  = f.includeTypes.join(',')
  if (f.excludeTypes.length)      query.exc  = f.excludeTypes.join(',')
  if (f.includeCategories.length) query.incc = f.includeCategories.join(',')
  if (f.excludeCategories.length) query.excc = f.excludeCategories.join(',')
  if (f.includeLocations.length)  query.incl = f.includeLocations.join(',')
  if (f.excludeLocations.length)  query.excl = f.excludeLocations.join(',')
  if (f.page > 1)                 query.page = String(f.page)
  if (f.sort !== defaultSort) query.sort = f.sort
  if (f.sortDir !== defaultDir) query.dir = f.sortDir
  router.replace({ query })
}, { deep: true })

const { data, isLoading, isError } = useGearList(filters)

const totalPages = computed(() => {
  if (!data.value) return 1
  return Math.max(1, Math.ceil(data.value.total / PAGE_SIZE))
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
.search-input::placeholder { color: var(--text-muted); }
.search-input:focus { border-color: var(--accent-blue); }

.gear-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
  padding: 16px;
}

.empty-msg {
  color: var(--text-muted);
  font-size: 14px;
  grid-column: 1 / -1;
  text-align: center;
  padding: 32px 0;
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
.page-btn:hover:not(:disabled) { border-color: var(--accent-orange); color: var(--accent-orange); }
.page-btn:disabled { opacity: 0.4; cursor: not-allowed; }

.page-info { font-size: 13px; color: var(--text-muted); }
</style>
