<template>
  <aside class="filter-panel">

    <!-- Equipment: tri-state component-type pills -->
    <template v-if="mode === 'equipment'">
      <div class="filter-section">
        <h3 class="filter-title">Type</h3>
        <p class="filter-hint"><span class="hint-inc">+ include only</span> · <span class="hint-exc">− exclude</span></p>
        <TriStatePills
          :options="equipmentTypes"
          :includeValues="includeTypes"
          :excludeValues="excludeTypes"
          @update:includeValues="$emit('update:includeTypes', $event)"
          @update:excludeValues="$emit('update:excludeTypes', $event)"
        />
      </div>
      <div class="filter-section">
        <h3 class="filter-title">Location</h3>
        <p class="filter-hint"><span class="hint-inc">+ include only</span> · <span class="hint-exc">− exclude</span></p>
        <TriStatePills
          :options="locationOptions"
          :includeValues="includeLocations"
          :excludeValues="excludeLocations"
          @update:includeValues="$emit('update:includeLocations', $event)"
          @update:excludeValues="$emit('update:excludeLocations', $event)"
        />
      </div>
    </template>

    <!-- Weapon: tri-state weapon-category pills -->
    <template v-if="mode === 'weapon'">
      <div class="filter-section">
        <h3 class="filter-title">Category</h3>
        <p class="filter-hint"><span class="hint-inc">+ include only</span> · <span class="hint-exc">− exclude</span></p>
        <TriStatePills
          :options="weaponCategories"
          :includeValues="includeCategories"
          :excludeValues="excludeCategories"
          @update:includeValues="$emit('update:includeCategories', $event)"
          @update:excludeValues="$emit('update:excludeCategories', $event)"
        />
      </div>
    </template>

    <a v-if="hasActiveFilters" class="clear-all" href="#" @click.prevent="clearAll">Clear All</a>
  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import TriStatePills from './TriStatePills.vue'

const props = defineProps<{
  mode: string
  includeTypes: string[]
  excludeTypes: string[]
  includeCategories: string[]
  excludeCategories: string[]
  includeLocations: string[]
  excludeLocations: string[]
}>()

const emit = defineEmits<{
  'update:includeTypes': [value: string[]]
  'update:excludeTypes': [value: string[]]
  'update:includeCategories': [value: string[]]
  'update:excludeCategories': [value: string[]]
  'update:includeLocations': [value: string[]]
  'update:excludeLocations': [value: string[]]
}>()

const equipmentTypes = [
  { value: 'Upgrade',       label: 'Upgrade' },
  { value: 'HeatSink',      label: 'Heat Sink' },
  { value: 'AmmunitionBox', label: 'Ammo' },
  { value: 'JumpJet',       label: 'Jump Jet' },
]

const locationOptions = [
  { value: 'All',          label: 'Any (unrestricted)' },
  { value: 'Head',         label: 'Head' },
  { value: 'Arms',         label: 'Arms' },
  { value: 'CenterTorso',  label: 'CT' },
  { value: 'LeftTorso',    label: 'LT' },
  { value: 'RightTorso',   label: 'RT' },
  { value: 'Legs',         label: 'Legs' },
]

const weaponCategories = [
  { value: 'Ballistic', label: 'Ballistic' },
  { value: 'Energy',    label: 'Energy' },
  { value: 'Missile',   label: 'Missile' },
  { value: 'Melee',     label: 'Melee' },
  { value: 'Support',   label: 'Support' },
]

const hasActiveFilters = computed(() =>
  props.includeTypes.length > 0 ||
  props.excludeTypes.length > 0 ||
  props.includeCategories.length > 0 ||
  props.excludeCategories.length > 0 ||
  props.includeLocations.length > 0 ||
  props.excludeLocations.length > 0
)

function clearAll() {
  emit('update:includeTypes', [])
  emit('update:excludeTypes', [])
  emit('update:includeCategories', [])
  emit('update:excludeCategories', [])
  emit('update:includeLocations', [])
  emit('update:excludeLocations', [])
}
</script>

<style scoped>
.filter-panel {
  width: 180px;
  min-width: 180px;
  background: var(--bg-sidebar);
  border-right: var(--border-default);
  padding: 16px;
  min-height: 100%;
}

.filter-section {
  margin-bottom: 20px;
}

.filter-title {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: var(--text-muted);
  margin-bottom: 6px;
}

.filter-hint {
  font-size: 11px;
  color: var(--text-muted);
  margin-bottom: 8px;
  line-height: 1.4;
}
.hint-inc { color: #58a6ff; }
.hint-exc { color: rgba(255, 80, 80, 0.8); }

.clear-all {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  color: var(--text-muted);
  text-decoration: none;
}
.clear-all:hover { color: var(--accent-orange); }
</style>
