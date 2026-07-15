<template>
  <aside class="filter-panel">
    <div class="filter-section">
      <h3 class="filter-title">Biome</h3>
      <div class="checkbox-list">
        <label v-for="b in BIOME_OPTIONS" :key="b.value" class="checkbox-label">
          <input
            type="checkbox"
            :checked="biomes.includes(b.value)"
            @change="toggle('biomes', b.value)"
          />
          {{ b.label }}
        </label>
      </div>
    </div>

    <div class="filter-section">
      <h3 class="filter-title">Difficulty</h3>
      <div class="range-inputs">
        <input
          type="number"
          class="range-input"
          placeholder="Min"
          min="-2"
          max="20"
          step="1"
          :value="minDifficulty ?? ''"
          @change="
            emit(
              'update:minDifficulty',
              ($event.target as HTMLInputElement).value
                ? parseInt(($event.target as HTMLInputElement).value)
                : null,
            )
          "
        />
        <span class="range-sep">–</span>
        <input
          type="number"
          class="range-input"
          placeholder="Max"
          min="-2"
          max="20"
          step="1"
          :value="maxDifficulty ?? ''"
          @change="
            emit(
              'update:maxDifficulty',
              ($event.target as HTMLInputElement).value
                ? parseInt(($event.target as HTMLInputElement).value)
                : null,
            )
          "
        />
      </div>
    </div>

    <div class="filter-section">
      <h3 class="filter-title">Population</h3>
      <div class="checkbox-list">
        <label v-for="p in POPULATION_OPTIONS" :key="p.value" class="checkbox-label">
          <input
            type="checkbox"
            :checked="population.includes(p.value)"
            @change="toggle('population', p.value)"
          />
          {{ p.label }}
        </label>
      </div>
    </div>

    <div class="filter-section">
      <h3 class="filter-title">Tags</h3>
      <div v-for="group in TAG_GROUPS" :key="group.groupId" class="tag-group">
        <div class="tag-group-header" @click="toggleGroupExpand(group.groupId)">
          <span class="tag-group-label-text">{{ group.label }}</span>
          <span class="tag-chevron" :class="{ open: expandedGroups[group.groupId] }">›</span>
        </div>
        <div v-if="expandedGroups[group.groupId]" class="tag-options">
          <label v-for="opt in group.options" :key="opt.value" class="checkbox-label">
            <input
              type="checkbox"
              :checked="tags.includes(opt.value)"
              @change="toggle('tags', opt.value)"
            />
            {{ opt.label }}
          </label>
        </div>
      </div>
    </div>

    <a v-if="hasActiveFilters" class="clear-all" href="#" @click.prevent="clearAll">Clear All</a>
  </aside>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { humanizeTag } from '../utils/humanize'

const props = defineProps<{
  biomes: string[]
  population: string[]
  tags: string[]
  minDifficulty: number | null
  maxDifficulty: number | null
}>()

const emit = defineEmits<{
  'update:biomes': [value: string[]]
  'update:population': [value: string[]]
  'update:tags': [value: string[]]
  'update:minDifficulty': [value: number | null]
  'update:maxDifficulty': [value: number | null]
}>()

interface Option {
  value: string
  label: string
}

const BIOME_OPTIONS: Option[] = [
  'arctic',
  'badlandsParched',
  'desertParched',
  'highlandsFall',
  'highlandsSpring',
  'jungleTropical',
  'lowlandsCoastal',
  'lowlandsFall',
  'lowlandsSpring',
  'lunar',
  'lunarVacuum',
  'martian',
  'martianVacuum',
  'polarFrozen',
  'tundraFrozen',
  'urbanHighTech',
].map((v) => ({ value: v, label: humanizeTag(v) }))

const POPULATION_OPTIONS: Option[] = [
  { value: 'none', label: 'None' },
  { value: 'small', label: 'Small' },
  { value: 'medium', label: 'Medium' },
  { value: 'large', label: 'Large' },
]

interface TagGroup {
  groupId: string
  label: string
  options: Option[]
}

function tagOptions(prefix: string, values: string[]): Option[] {
  return values.map((v) => ({ value: `${prefix}${v}`, label: humanizeTag(v) }))
}

const TAG_GROUPS: TagGroup[] = [
  {
    groupId: 'climate',
    label: 'Climate',
    options: tagOptions('planet_climate_', [
      'arctic',
      'arid',
      'desert',
      'ice',
      'lunar',
      'mars',
      'rocky',
      'terran',
      'tropical',
      'water',
    ]),
  },
  {
    groupId: 'industry',
    label: 'Industry',
    options: tagOptions('planet_industry_', [
      'agriculture',
      'aquaculture',
      'chemicals',
      'electronics',
      'manufacturing',
      'mining',
      'poor',
      'recreation',
      'research',
      'rich',
      'superheavy',
    ]),
  },
  {
    groupId: 'civ',
    label: 'Civilization',
    options: tagOptions('planet_civ_', ['innersphere', 'periphery', 'primitive']),
  },
  {
    groupId: 'feature',
    label: 'Feature',
    options: tagOptions('planet_feature_', [
      'asteroids',
      'comet',
      'gasgiant',
      'moon01',
      'moon02',
      'moon03',
      'rings',
    ]),
  },
  {
    groupId: 'size',
    label: 'Size',
    options: tagOptions('planet_size_', ['large', 'medium', 'small']),
  },
]

const expandedGroups = ref<Record<string, boolean>>({})

function toggleGroupExpand(groupId: string) {
  expandedGroups.value = { ...expandedGroups.value, [groupId]: !expandedGroups.value[groupId] }
}

function toggle(field: 'biomes' | 'population' | 'tags', value: string) {
  const current = props[field]
  const next = current.includes(value) ? current.filter((v) => v !== value) : [...current, value]
  emit(`update:${field}` as any, next)
}

const hasActiveFilters = computed(
  () =>
    props.biomes.length > 0 ||
    props.population.length > 0 ||
    props.tags.length > 0 ||
    props.minDifficulty !== null ||
    props.maxDifficulty !== null,
)

function clearAll() {
  emit('update:biomes', [])
  emit('update:population', [])
  emit('update:tags', [])
  emit('update:minDifficulty', null)
  emit('update:maxDifficulty', null)
}
</script>

<style scoped>
.filter-panel {
  width: 200px;
  min-width: 200px;
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

.checkbox-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-primary);
  cursor: pointer;
  user-select: none;
}

.checkbox-label input[type='checkbox'] {
  accent-color: var(--accent-blue);
  cursor: pointer;
}

.range-inputs {
  display: flex;
  align-items: center;
  gap: 6px;
}

.range-input {
  width: 58px;
  background: var(--bg-card);
  border: var(--border-default);
  border-radius: 4px;
  color: var(--text-primary);
  font-size: 12px;
  padding: 4px 6px;
  outline: none;
  box-sizing: border-box;
}
.range-input:focus {
  border-color: var(--accent-blue);
}
.range-input::placeholder {
  color: var(--text-muted);
}

.range-sep {
  font-size: 12px;
  color: var(--text-muted);
}

.tag-group {
  margin-bottom: 4px;
}

.tag-group-header {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  user-select: none;
}

.tag-group-label-text {
  flex: 1;
  font-size: 12px;
  color: var(--text-primary);
}

.tag-chevron {
  font-size: 12px;
  color: var(--text-muted);
  transition: transform 0.15s;
  line-height: 1;
}
.tag-chevron.open {
  transform: rotate(90deg);
}

.tag-options {
  margin-left: 4px;
  margin-top: 4px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.clear-all {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  color: var(--text-muted);
  text-decoration: none;
}
.clear-all:hover {
  color: var(--accent-orange);
}
</style>
