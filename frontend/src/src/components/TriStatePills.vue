<template>
  <div class="tsp-list">
    <button
      v-for="opt in options"
      :key="opt.value"
      class="tsp-pill"
      :class="stateOf(opt.value)"
      :data-pill="opt.value"
      @click="cycle(opt.value)"
    >
      <span class="tsp-prefix">{{ prefixOf(opt.value) }}</span>{{ opt.label }}
    </button>
  </div>
</template>

<script setup lang="ts">
export interface PillOption {
  value: string
  label: string
}

const props = defineProps<{
  options: PillOption[]
  includeValues: string[]
  excludeValues: string[]
}>()

const emit = defineEmits<{
  'update:includeValues': [value: string[]]
  'update:excludeValues': [value: string[]]
}>()

type State = 'off' | 'include' | 'exclude'

function stateOf(v: string): State {
  if (props.includeValues.includes(v)) return 'include'
  if (props.excludeValues.includes(v)) return 'exclude'
  return 'off'
}

function prefixOf(v: string): string {
  const s = stateOf(v)
  if (s === 'include') return '+ '
  if (s === 'exclude') return '− '
  return ''
}

function cycle(v: string) {
  const s = stateOf(v)
  let inc = [...props.includeValues]
  let exc = [...props.excludeValues]
  if (s === 'off') {
    inc.push(v)
  } else if (s === 'include') {
    inc = inc.filter(x => x !== v)
    exc.push(v)
  } else {
    exc = exc.filter(x => x !== v)
  }
  emit('update:includeValues', inc)
  emit('update:excludeValues', exc)
}
</script>

<style scoped>
.tsp-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tsp-pill {
  display: flex;
  align-items: center;
  text-align: left;
  font-size: 12px;
  font-weight: 500;
  padding: 5px 10px;
  border-radius: 3px;
  border: 1px solid rgba(128, 128, 128, 0.2);
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  width: 100%;
  transition: background 0.12s, border-color 0.12s, color 0.12s;
}

.tsp-pill:hover {
  color: var(--text-primary);
  border-color: rgba(128, 128, 128, 0.45);
}

.tsp-prefix {
  min-width: 14px;
  font-weight: 700;
  font-size: 13px;
  line-height: 1;
}

/* Include — colored by value */
.tsp-pill.include { color: #fff; border-color: transparent; }

/* Fallback include color (used when no matching data-pill rule applies) */
.tsp-pill.include { background: rgba(88, 166, 255, 0.55); }

/* Equipment types */
.tsp-pill.include[data-pill="Upgrade"]       { background: rgba(88,  166, 255, 0.65); }
.tsp-pill.include[data-pill="HeatSink"]      { background: rgba(255, 140, 0,   0.65); }
.tsp-pill.include[data-pill="AmmunitionBox"] { background: rgba(80,  200, 120, 0.65); }
.tsp-pill.include[data-pill="JumpJet"]       { background: rgba(180, 100, 255, 0.65); }

/* Weapon categories */
.tsp-pill.include[data-pill="Ballistic"] { background: rgba(88,  166, 255, 0.6); }
.tsp-pill.include[data-pill="Energy"]    { background: rgba(63,  185, 80,  0.6); }
.tsp-pill.include[data-pill="Missile"]   { background: rgba(180, 130, 255, 0.6); }
.tsp-pill.include[data-pill="Melee"]     { background: rgba(255, 80,  80,  0.6); }
.tsp-pill.include[data-pill="Support"]   { background: rgba(180, 100, 255, 0.6); }

/* Exclude */
.tsp-pill.exclude {
  border-color: rgba(255, 80, 80, 0.45);
  color: rgba(255, 80, 80, 0.8);
  text-decoration: line-through;
  background: rgba(255, 80, 80, 0.05);
}
</style>
