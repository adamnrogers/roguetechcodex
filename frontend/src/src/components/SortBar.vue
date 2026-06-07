<template>
  <div class="sort-bar">
    <span class="results-count">{{ total.toLocaleString() }} {{ label }}</span>
    <div class="sort-controls">
      <span class="sort-label">Sort:</span>
      <div class="select-wrapper">
        <select
          class="sort-select"
          :value="sortKey"
          @change="onSortChange"
        >
          <template v-if="options && options.length">
            <option v-for="opt in options" :key="opt.value" :value="opt.value">{{ opt.label }}</option>
          </template>
          <template v-else>
            <option value="name:asc">Name (A–Z)</option>
            <option value="name:desc">Name (Z–A)</option>
            <option value="tonnage:asc">Tonnage ↑</option>
            <option value="tonnage:desc">Tonnage ↓</option>
          </template>
        </select>
        <svg class="select-arrow" width="10" height="6" viewBox="0 0 10 6" fill="currentColor">
          <path d="M0 0l5 6 5-6z"/>
        </svg>
      </div>
      <div class="view-toggle">
        <button class="view-btn view-btn--active" title="Grid view">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="currentColor">
            <rect x="0" y="0" width="6" height="6"/><rect x="8" y="0" width="6" height="6"/>
            <rect x="0" y="8" width="6" height="6"/><rect x="8" y="8" width="6" height="6"/>
          </svg>
        </button>
        <button class="view-btn" title="List view">
          <svg width="14" height="14" viewBox="0 0 14 14" fill="currentColor">
            <rect x="0" y="0" width="14" height="2"/><rect x="0" y="4" width="14" height="2"/>
            <rect x="0" y="8" width="14" height="2"/><rect x="0" y="12" width="14" height="2"/>
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
export interface SortOption {
  value: string
  label: string
}

const props = defineProps<{
  total: number
  label: string
  sortKey: string
  options?: SortOption[]
}>()

const emit = defineEmits<{
  'update:sortKey': [value: string]
}>()

function onSortChange(event: Event) {
  emit('update:sortKey', (event.target as HTMLSelectElement).value)
}
</script>

<style scoped>
.sort-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: var(--bg-primary);
  border-bottom: 1px solid var(--sortbar-divider);
}
.results-count {
  color: var(--text-primary);
  font-size: 13px;
  font-weight: 500;
}
.sort-controls {
  display: flex;
  align-items: center;
  gap: 10px;
}
.sort-label {
  font-size: 12px;
  color: var(--text-muted);
}

.select-wrapper {
  position: relative;
  display: inline-flex;
  align-items: center;
}
.sort-select {
  appearance: none;
  -webkit-appearance: none;
  background: var(--bg-select);
  border: var(--border-default);
  color: var(--text-primary);
  border-radius: 4px;
  padding: 4px 28px 4px 8px;
  font-size: 12px;
  cursor: pointer;
  outline: none;
  transition: border-color 0.15s;
  color-scheme: dark;
}
.sort-select:focus { border-color: var(--accent-blue); }
.sort-select option {
  background: var(--bg-select);
  color: var(--text-primary);
}
.select-arrow {
  position: absolute;
  right: 8px;
  pointer-events: none;
  color: var(--text-muted);
}

.view-toggle {
  display: flex;
  border: var(--border-default);
  border-radius: 4px;
  overflow: hidden;
}
.view-btn {
  background: transparent;
  border: none;
  color: var(--text-muted);
  padding: 5px 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: background 0.15s, color 0.15s;
}
.view-btn:hover { background: var(--viewbtn-hover); color: var(--text-primary); }
.view-btn--active { background: var(--viewbtn-active); color: var(--text-primary); }
</style>
