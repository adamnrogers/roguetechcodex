<template>
  <div class="search-dropdown" ref="dropdownRef">
    <template v-if="hasResults">
      <div v-if="data.chassis.length" class="result-group">
        <div class="group-label">Mechs &amp; Vehicles</div>
        <button
          v-for="hit in data.chassis"
          :key="hit.id"
          class="result-row"
          @click="navigate(hit)"
        >
          <span class="result-name">{{ hit.name }}</span>
          <span class="result-subtitle">{{ hit.subtitle }}</span>
        </button>
      </div>
      <div v-if="data.gear.length" class="result-group">
        <div class="group-label">Gear</div>
        <button
          v-for="hit in data.gear"
          :key="hit.id"
          class="result-row"
          @click="navigate(hit)"
        >
          <span class="result-name">{{ hit.name }}</span>
          <span class="result-subtitle">{{ hit.subtitle }}</span>
        </button>
      </div>
    </template>
    <div v-else class="no-results">No results</div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import type { SearchHit, SearchResponse } from '../composables/useGlobalSearch'

const props = defineProps<{ data: SearchResponse }>()
const emit = defineEmits<{ close: [] }>()

const router = useRouter()
const dropdownRef = ref<HTMLElement | null>(null)

const hasResults = computed(
  () => props.data.chassis.length > 0 || props.data.gear.length > 0
)

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
  router.push(`${TYPE_ROUTE[hit.result_type] ?? '/mechs'}/${hit.id}`)
  emit('close')
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Escape') emit('close')
}

function onMousedown(e: MouseEvent) {
  if (dropdownRef.value && !dropdownRef.value.contains(e.target as Node)) {
    emit('close')
  }
}

onMounted(() => {
  document.addEventListener('keydown', onKeydown)
  document.addEventListener('mousedown', onMousedown)
})
onUnmounted(() => {
  document.removeEventListener('keydown', onKeydown)
  document.removeEventListener('mousedown', onMousedown)
})
</script>

<style scoped>
.search-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  min-width: 320px;
  background: var(--bg-card);
  border: var(--border-default);
  border-radius: 6px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  z-index: 200;
  overflow: hidden;
}
.result-group + .result-group {
  border-top: var(--border-default);
}
.group-label {
  padding: 6px 12px 4px;
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  color: var(--text-muted);
}
.result-row {
  display: flex;
  align-items: baseline;
  gap: 8px;
  width: 100%;
  padding: 7px 12px;
  background: transparent;
  border: none;
  color: var(--text-primary);
  cursor: pointer;
  text-align: left;
  font-size: 13px;
  transition: background 0.1s;
}
.result-row:hover {
  background: var(--bg-hover, rgba(255, 255, 255, 0.05));
}
.result-name {
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.result-subtitle {
  flex-shrink: 0;
  font-size: 11px;
  color: var(--text-muted);
  white-space: nowrap;
}
.no-results {
  padding: 12px;
  font-size: 13px;
  color: var(--text-muted);
  text-align: center;
}
</style>
