<template>
  <div class="browse-layout">
    <FilterPanel
      :mode="mode"
      :tonnage="filters.tonnage"
      :era="filters.era"
      :hasLowerArm="filters.hasLowerArm"
      :hasHand="filters.hasHand"
      :hardpoints="filters.hardpoints"
      @update:tonnage="v => filters = { ...filters, tonnage: v, page: 1 }"
      @update:era="onEraChange"
      @update:hasLowerArm="v => filters = { ...filters, hasLowerArm: v, page: 1 }"
      @update:hasHand="v => filters = { ...filters, hasHand: v, page: 1 }"
      @update:hardpoints="v => filters = { ...filters, hardpoints: v, page: 1 }"
      @clearAll="filters = { ...filters, tonnage: [], era: [], hasLowerArm: null, hasHand: null, hardpoints: defaultHardpoints(), page: 1 }"
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
import { useMechList, type MechFilters, defaultHardpoints } from '../composables/useMechList'

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
  const tRaw = route.query.t
  const tonnage = tRaw
    ? (Array.isArray(tRaw) ? tRaw : [tRaw]).map(Number).filter(n => !isNaN(n))
    : []
  const eraRaw = route.query.era
  const era = Array.isArray(eraRaw) ? eraRaw as string[] : eraRaw ? [eraRaw as string] : []
  const faction = route.query.faction as string ?? ''
  const tag = route.query.tag as string ?? ''
  const page = parseInt(route.query.page as string ?? '1') || 1
  const sort = route.query.sort as string ?? 'name'
  const sortDir = route.query.dir as string ?? 'asc'
  const hasLowerArm = route.query.la === '1' ? true : route.query.la === '0' ? false : null
  const hasHand = route.query.ha === '1' ? true : route.query.ha === '0' ? false : null
  const hardpoints = defaultHardpoints()
  hardpoints.ballistic.count = parseInt(route.query.hp_b as string ?? '0') || 0
  hardpoints.ballistic.loc   = route.query.hp_b_loc as string ?? ''
  hardpoints.energy.count    = parseInt(route.query.hp_e as string ?? '0') || 0
  hardpoints.energy.loc      = route.query.hp_e_loc as string ?? ''
  hardpoints.missile.count   = parseInt(route.query.hp_m as string ?? '0') || 0
  hardpoints.missile.loc     = route.query.hp_m_loc as string ?? ''
  hardpoints.special.count   = parseInt(route.query.hp_s as string ?? '0') || 0
  hardpoints.special.loc     = route.query.hp_s_loc as string ?? ''
  hardpoints.wing.count      = parseInt(route.query.hp_w as string ?? '0') || 0
  hardpoints.wing.loc        = route.query.hp_w_loc as string ?? ''
  hardpoints.bomb.count      = parseInt(route.query.hp_bm as string ?? '0') || 0
  hardpoints.bomb.loc        = route.query.hp_bm_loc as string ?? ''
  hardpoints.handheld.count  = parseInt(route.query.hp_hh as string ?? '0') || 0
  hardpoints.handheld.loc    = route.query.hp_hh_loc as string ?? ''
  hardpoints.excludeOmni     = route.query.hp_excl_omni === '1'
  hardpoints.omniOnly        = route.query.hp_omni_only === '1'
  return { q, tonnage, era, faction, tag, page, sort, sortDir, hasLowerArm, hasHand, hardpoints }
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

function onEraChange(era: string[]) {
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
  filters.value = { q: '', tonnage: [], era: [], faction: '', tag: '', page: 1, sort: 'name', sortDir: 'asc', hasLowerArm: null, hasHand: null, hardpoints: defaultHardpoints() }
})

// Sync filters to URL
watch(filters, (f) => {
  const query: Record<string, any> = {}
  if (f.q) query.q = f.q
  if (f.tonnage.length) query.t = f.tonnage.map(String)
  if (f.era.length) query.era = f.era
  if (f.faction) query.faction = f.faction
  if (f.tag) query.tag = f.tag
  if (f.page > 1) query.page = String(f.page)
  if (f.sort !== 'name') query.sort = f.sort
  if (f.sortDir !== 'asc') query.dir = f.sortDir
  if (f.hasLowerArm !== null) query.la = f.hasLowerArm ? '1' : '0'
  if (f.hasHand !== null) query.ha = f.hasHand ? '1' : '0'
  if (f.hardpoints.ballistic.count) { query.hp_b = String(f.hardpoints.ballistic.count); if (f.hardpoints.ballistic.loc) query.hp_b_loc = f.hardpoints.ballistic.loc }
  if (f.hardpoints.energy.count)    { query.hp_e = String(f.hardpoints.energy.count);    if (f.hardpoints.energy.loc)    query.hp_e_loc = f.hardpoints.energy.loc }
  if (f.hardpoints.missile.count)   { query.hp_m = String(f.hardpoints.missile.count);   if (f.hardpoints.missile.loc)   query.hp_m_loc = f.hardpoints.missile.loc }
  if (f.hardpoints.special.count)   { query.hp_s = String(f.hardpoints.special.count);   if (f.hardpoints.special.loc)   query.hp_s_loc = f.hardpoints.special.loc }
  if (f.hardpoints.wing.count)      { query.hp_w = String(f.hardpoints.wing.count);      if (f.hardpoints.wing.loc)      query.hp_w_loc = f.hardpoints.wing.loc }
  if (f.hardpoints.bomb.count)      { query.hp_bm = String(f.hardpoints.bomb.count);     if (f.hardpoints.bomb.loc)      query.hp_bm_loc = f.hardpoints.bomb.loc }
  if (f.hardpoints.handheld.count)  { query.hp_hh = String(f.hardpoints.handheld.count); if (f.hardpoints.handheld.loc)  query.hp_hh_loc = f.hardpoints.handheld.loc }
  if (f.hardpoints.excludeOmni) query.hp_excl_omni = '1'
  if (f.hardpoints.omniOnly)    query.hp_omni_only = '1'
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
  padding: 8px 0;
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
