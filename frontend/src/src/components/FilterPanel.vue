<template>
  <aside class="filter-panel">
    <div class="filter-section">
      <h3 class="filter-title">Weight Class</h3>
      <label v-for="wc in weightClasses" :key="wc.value" class="filter-check">
        <input
          type="checkbox"
          :checked="modelValue.includes(wc.value)"
          @change="toggleWeightClass(wc.value)"
        />
        <span class="wc-dot" :class="wc.cls"></span>
        {{ wc.label }}
      </label>
    </div>
    <div class="filter-section">
      <h3 class="filter-title">Era</h3>
      <label v-for="eraOpt in eras" :key="eraOpt" class="filter-check">
        <input
          type="checkbox"
          :checked="era === eraOpt"
          @change="toggleEra(eraOpt)"
        />
        {{ eraOpt }}
      </label>
    </div>
    <div v-if="['mech','vehicle','vtol','battle_armor'].includes(mode)" class="filter-section">
      <h3 class="filter-title">Tonnage</h3>
      <div class="tonnage-range">
        <label class="tonnage-row">
          <span class="tonnage-label">Min</span>
          <input type="range" min="0" max="420" step="5"
            :value="minTonnage ?? 0"
            @input="onMinChange"
            class="range-slider" />
          <span class="tonnage-val">{{ minTonnage != null ? minTonnage + 't' : '0t' }}</span>
        </label>
        <label class="tonnage-row">
          <span class="tonnage-label">Max</span>
          <input type="range" min="0" max="420" step="5"
            :value="maxTonnage ?? 420"
            @input="onMaxChange"
            class="range-slider" />
          <span class="tonnage-val">{{ maxTonnage != null ? maxTonnage + 't' : '∞' }}</span>
        </label>
      </div>
    </div>
    <div v-if="mode === 'mech'" class="filter-section">
      <h3 class="filter-title">Arm Actuators</h3>
      <label class="filter-check">
        <input type="checkbox" :checked="!!hasLowerArm" @change="emit('update:hasLowerArm', hasLowerArm ? null : true)" />
        Lower Arm
      </label>
      <label class="filter-check">
        <input type="checkbox" :checked="!!hasHand" @change="emit('update:hasHand', hasHand ? null : true)" />
        Hand
      </label>
    </div>
    <div v-if="mode === 'mech'" class="filter-section hardpoints-section">
      <h3 class="filter-title">Hardpoints</h3>
      <div class="hp-grid">
        <div class="hp-header-row">
          <span class="hp-type-col"></span>
          <span class="hp-amt-col">AMT</span>
          <span v-for="col in HP_LOCS" :key="col.key" class="hp-loc-col">{{ col.label }}</span>
        </div>
        <div v-for="row in HP_TYPES" :key="row.key" class="hp-row" :class="{ 'hp-row-dim': hardpoints[row.key].count === 0 }">
          <span class="hp-type-label" :style="{ color: row.color }">{{ row.label }}</span>
          <span class="hp-amt-col">
            <button class="hp-step" @click="stepCount(row.key, -1)" :disabled="hardpoints[row.key].count === 0">−</button>
            <span class="hp-count">{{ hardpoints[row.key].count }}</span>
            <button class="hp-step" @click="stepCount(row.key, 1)" :disabled="hardpoints[row.key].count >= 20">+</button>
          </span>
          <label v-for="col in HP_LOCS" :key="col.key" class="hp-loc-col">
            <input
              type="radio"
              :name="`hp-loc-${row.key}`"
              :value="col.key"
              :checked="hardpoints[row.key].loc === col.key"
              @change="setLoc(row.key, col.key)"
            />
          </label>
        </div>
      </div>
    </div>
    <a class="clear-all" href="#" @click.prevent="clearAll">Clear All</a>
  </aside>
</template>

<script setup lang="ts">
import type { HardpointFilters } from '../composables/useMechList'

const props = defineProps<{
  mode: string
  modelValue: string[]
  era: string
  minTonnage: number | null
  maxTonnage: number | null
  hasLowerArm: boolean | null
  hasHand: boolean | null
  hardpoints: HardpointFilters
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string[]]
  'update:era': [value: string]
  'update:minTonnage': [value: number | null]
  'update:maxTonnage': [value: number | null]
  'update:hasLowerArm': [value: boolean | null]
  'update:hasHand': [value: boolean | null]
  'update:hardpoints': [value: HardpointFilters]
  'clearAll': []
}>()

const HP_TYPES = [
  { key: 'ballistic' as const, label: 'Ballistic',   color: '#58a6ff' },
  { key: 'energy'    as const, label: 'Energy',      color: '#3fb950' },
  { key: 'missile'   as const, label: 'Missile',     color: '#b482ff' },
  { key: 'special'   as const, label: 'Special',     color: '#f0883e' },
  { key: 'wing'      as const, label: 'WingMount',   color: '#8b96a3' },
  { key: 'bomb'      as const, label: 'BombBay',     color: '#f85149' },
  { key: 'handheld'  as const, label: 'HandHeld',    color: '#38bdc1' },
]

const HP_LOCS = [
  { key: '',             label: 'ANY' },
  { key: 'RightArm',    label: 'RA'  },
  { key: 'RightTorso',  label: 'RT'  },
  { key: 'CenterTorso', label: 'CT'  },
  { key: 'Head',        label: 'HD'  },
  { key: 'LeftTorso',   label: 'LT'  },
  { key: 'LeftArm',     label: 'LA'  },
  { key: 'RightLeg',    label: 'RL'  },
  { key: 'LeftLeg',     label: 'LL'  },
]

const weightClasses = [
  { value: 'LIGHT',   label: 'Light',   cls: 'dot-light' },
  { value: 'MEDIUM',  label: 'Medium',  cls: 'dot-medium' },
  { value: 'HEAVY',   label: 'Heavy',   cls: 'dot-heavy' },
  { value: 'ASSAULT', label: 'Assault', cls: 'dot-assault' },
]
const eras = ['Succession Wars', 'Clan Invasion', 'Civil War', 'Jihad', 'Dark Age']


function toggleWeightClass(value: string) {
  const current = props.modelValue
  if (current.includes(value)) {
    emit('update:modelValue', current.filter(v => v !== value))
  } else {
    emit('update:modelValue', [...current, value])
  }
}

function toggleEra(value: string) {
  emit('update:era', props.era === value ? '' : value)
}

function onMinChange(e: Event) {
  const val = parseInt((e.target as HTMLInputElement).value)
  const max = props.maxTonnage ?? 420
  emit('update:minTonnage', val <= 0 ? null : Math.min(val, max))
}

function onMaxChange(e: Event) {
  const val = parseInt((e.target as HTMLInputElement).value)
  const min = props.minTonnage ?? 0
  emit('update:maxTonnage', val >= 420 ? null : Math.max(val, min))
}


function stepCount(key: keyof HardpointFilters, delta: number) {
  const updated = { ...props.hardpoints }
  const cur = updated[key].count
  const next = Math.max(0, Math.min(20, cur + delta))
  updated[key] = { ...updated[key], count: next }
  emit('update:hardpoints', updated)
}

function setLoc(key: keyof HardpointFilters, loc: string) {
  const updated = { ...props.hardpoints }
  updated[key] = { ...updated[key], loc }
  emit('update:hardpoints', updated)
}

function clearAll() {
  emit('update:modelValue', [])
  emit('update:era', '')
  emit('update:minTonnage', null)
  emit('update:maxTonnage', null)
  emit('update:hasLowerArm', null)
  emit('update:hasHand', null)
  emit('clearAll')
}
</script>

<style scoped>
.filter-panel {
  width: var(--filter-panel-width, 220px);
  min-width: var(--filter-panel-width, 220px);
  background: var(--bg-sidebar);
  border-right: var(--border-default);
  padding: 16px;
  min-height: 100%;
}
.filter-section { margin-bottom: 20px; }
.filter-title {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: var(--text-muted);
  margin-bottom: 8px;
}
.filter-check {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
  cursor: pointer;
  font-size: 13px;
  color: var(--text-primary);
}
.filter-check input[type=checkbox] { cursor: pointer; accent-color: var(--accent-blue); }
.wc-dot { width: 10px; height: 10px; border-radius: 2px; flex-shrink: 0; transition: background 0.2s; }
.dot-light   { background: var(--badge-light-fg); }
.dot-medium  { background: var(--badge-medium-fg); }
.dot-heavy   { background: var(--badge-heavy-fg); }
.dot-assault { background: var(--badge-assault-fg); }
.tonnage-range { display: flex; flex-direction: column; gap: 8px; }
.tonnage-row { display: flex; align-items: center; gap: 6px; cursor: pointer; }
.tonnage-label { font-size: 11px; color: var(--text-muted); width: 26px; flex-shrink: 0; }
.tonnage-val { font-size: 11px; color: var(--text-muted); width: 32px; text-align: left; flex-shrink: 0; margin-left: 4px; margin-right: 8px; }
.range-slider { flex: 1; accent-color: var(--accent-blue); cursor: pointer; }
.clear-all {
  display: block;
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-muted);
}
.clear-all:hover { color: var(--accent-orange); text-decoration: none; }

.hardpoints-section {
  overflow-x: auto;
}

.hp-grid {
  font-size: 11px;
  min-width: 0;
}

.hp-header-row,
.hp-row {
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 2px 0;
}

.hp-row-dim {
  opacity: 0.5;
}

.hp-type-col,
.hp-type-label {
  width: 60px;
  flex-shrink: 0;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.hp-amt-col {
  display: flex;
  align-items: center;
  gap: 1px;
  width: 44px;
  flex-shrink: 0;
}

.hp-step {
  background: var(--bg-tertiary, #2d333b);
  border: 1px solid var(--border, #444c56);
  color: var(--text-primary, #e6edf3);
  width: 14px;
  height: 14px;
  font-size: 10px;
  line-height: 1;
  cursor: pointer;
  padding: 0;
  border-radius: 2px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.hp-step:disabled {
  opacity: 0.3;
  cursor: default;
}

.hp-count {
  width: 14px;
  text-align: center;
  font-size: 10px;
  flex-shrink: 0;
}

.hp-loc-col {
  width: 18px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 9px;
  text-align: center;
  cursor: pointer;
}

.hp-header-row .hp-loc-col {
  font-size: 9px;
  color: var(--text-secondary, #8b949e);
  cursor: default;
}

.hp-loc-col input[type="radio"] {
  width: 10px;
  height: 10px;
  margin: 0;
  cursor: pointer;
  accent-color: var(--accent, #58a6ff);
}
</style>
