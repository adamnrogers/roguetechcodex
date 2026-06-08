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
          <span class="tonnage-val">{{ minTonnage ?? 0 }}t</span>
        </label>
        <label class="tonnage-row">
          <span class="tonnage-label">Max</span>
          <input type="range" min="0" max="420" step="5"
            :value="maxTonnage ?? 420"
            @input="onMaxChange"
            class="range-slider" />
          <span class="tonnage-val">{{ maxTonnage ?? '—' }}</span>
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
    <a class="clear-all" href="#" @click.prevent="clearAll">Clear All</a>
  </aside>
</template>

<script setup lang="ts">
const props = defineProps<{
  mode: string
  modelValue: string[]
  era: string
  minTonnage: number | null
  maxTonnage: number | null
  hasLowerArm: boolean | null
  hasHand: boolean | null
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string[]]
  'update:era': [value: string]
  'update:minTonnage': [value: number | null]
  'update:maxTonnage': [value: number | null]
  'update:hasLowerArm': [value: boolean | null]
  'update:hasHand': [value: boolean | null]
  'clearAll': []
}>()

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
  width: 220px;
  min-width: 220px;
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
.tonnage-val { font-size: 11px; color: var(--text-muted); width: 32px; text-align: right; flex-shrink: 0; }
.range-slider { flex: 1; accent-color: var(--accent-blue); cursor: pointer; }
.clear-all {
  display: block;
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-muted);
}
.clear-all:hover { color: var(--accent-orange); text-decoration: none; }
</style>
