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
    <a class="clear-all" href="#" @click.prevent="clearAll">Clear All</a>
  </aside>
</template>

<script setup lang="ts">
const props = defineProps<{
  mode: string
  modelValue: string[]
  era: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: string[]]
  'update:era': [value: string]
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
  // Single select: clicking selected era deselects it
  emit('update:era', props.era === value ? '' : value)
}

function clearAll() {
  emit('update:modelValue', [])
  emit('update:era', '')
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
.clear-all {
  display: block;
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-muted);
}
.clear-all:hover { color: var(--accent-orange); text-decoration: none; }
</style>
