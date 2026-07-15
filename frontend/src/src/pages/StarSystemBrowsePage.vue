<template>
  <div class="browse-layout">
    <StarSystemFilterPanel
      :biomes="filters.biomes"
      :population="filters.population"
      :tags="filters.tags"
      :minDifficulty="filters.minDifficulty"
      :maxDifficulty="filters.maxDifficulty"
      @update:biomes="(v) => onFilterUpdate({ biomes: v })"
      @update:population="(v) => onFilterUpdate({ population: v })"
      @update:tags="(v) => onFilterUpdate({ tags: v })"
      @update:minDifficulty="(v) => onFilterUpdate({ minDifficulty: v })"
      @update:maxDifficulty="(v) => onFilterUpdate({ maxDifficulty: v })"
    />
    <div class="browse-main">
      <div class="search-row">
        <input
          v-model="searchInput"
          class="search-input"
          type="text"
          placeholder="Search star systems..."
          @input="onSearchInput"
        />
      </div>
      <SortBar
        :total="data?.total ?? 0"
        label="Star Systems"
        :sortKey="`${filters.sort}:${filters.sortDir}`"
        :options="sortOptions"
        :viewMode="viewMode"
        @update:sortKey="onSortKeyChange"
        @update:viewMode="(v) => (viewMode = v)"
      />
      <div v-if="isError" class="error-msg">
        Failed to load data. Please check your connection and try again.
      </div>
      <div v-else-if="isLoading" :class="['ss-grid', viewMode === 'list' && 'ss-list']">
        <SkeletonCard v-for="n in 12" :key="n" />
      </div>
      <div v-else :class="['ss-grid', viewMode === 'list' && 'ss-list']">
        <StarSystemCard
          v-for="item in data?.results ?? []"
          :key="item.id"
          v-bind="item"
          :list="viewMode === 'list'"
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
import StarSystemFilterPanel from '../components/StarSystemFilterPanel.vue'
import SortBar from '../components/SortBar.vue'
import SkeletonCard from '../components/SkeletonCard.vue'
import StarSystemCard from '../components/StarSystemCard.vue'
import { useStarSystemList, type StarSystemFilters } from '../composables/useStarSystemList'
import type { SortOption } from '../components/SortBar.vue'

const route = useRoute()
const router = useRouter()

const PAGE_SIZE = 60
const viewMode = ref<'grid' | 'list'>(
  (localStorage.getItem('star-system-view-mode') as 'grid' | 'list') ?? 'grid',
)
watch(viewMode, (v) => localStorage.setItem('star-system-view-mode', v))

const sortOptions: SortOption[] = [
  { value: 'name:asc', label: 'Name (A–Z)' },
  { value: 'name:desc', label: 'Name (Z–A)' },
  { value: 'difficulty:asc', label: 'Difficulty ↑' },
  { value: 'difficulty:desc', label: 'Difficulty ↓' },
]

function readFilters(): StarSystemFilters {
  const q = (route.query.q as string) ?? ''
  const page = parseInt((route.query.page as string) ?? '1') || 1
  const sort = (route.query.sort as string) ?? 'name'
  const sortDir = (route.query.dir as string) ?? 'asc'
  const biomesRaw = (route.query.biomes as string) ?? ''
  const popRaw = (route.query.pop as string) ?? ''
  const tagsRaw = (route.query.tags as string) ?? ''
  const minD = route.query.mind ? parseInt(route.query.mind as string) : null
  const maxD = route.query.maxd ? parseInt(route.query.maxd as string) : null
  return {
    q,
    biomes: biomesRaw ? biomesRaw.split(',').filter(Boolean) : [],
    population: popRaw ? popRaw.split(',').filter(Boolean) : [],
    tags: tagsRaw ? tagsRaw.split(',').filter(Boolean) : [],
    minDifficulty: minD,
    maxDifficulty: maxD,
    page,
    sort,
    sortDir,
  }
}

const filters = ref<StarSystemFilters>(readFilters())
const searchInput = ref(filters.value.q)

function onFilterUpdate(patch: Partial<StarSystemFilters>) {
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

watch(
  filters,
  (f) => {
    const query: Record<string, any> = {}
    if (f.q) query.q = f.q
    if (f.biomes.length) query.biomes = f.biomes.join(',')
    if (f.population.length) query.pop = f.population.join(',')
    if (f.tags.length) query.tags = f.tags.join(',')
    if (f.minDifficulty !== null) query.mind = String(f.minDifficulty)
    if (f.maxDifficulty !== null) query.maxd = String(f.maxDifficulty)
    if (f.page > 1) query.page = String(f.page)
    if (f.sort !== 'name') query.sort = f.sort
    if (f.sortDir !== 'asc') query.dir = f.sortDir
    router.replace({ query })
  },
  { deep: true },
)

const { data, isLoading, isError } = useStarSystemList(filters)

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
.search-input::placeholder {
  color: var(--text-muted);
}
.search-input:focus {
  border-color: var(--accent-blue);
}

.ss-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
  padding: 16px;
}
.ss-list {
  grid-template-columns: 1fr;
  gap: 4px;
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
  transition:
    border-color 0.15s,
    color 0.15s;
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
