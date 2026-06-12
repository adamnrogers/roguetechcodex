<template>
  <aside class="filter-panel">
    <div class="filter-section">
      <h3 class="filter-title">{{ mode === 'battle_armor' ? 'Tonnage' : 'Class &amp; Tonnage' }}</h3>
      <template v-if="mode === 'battle_armor'">
        <label v-for="t in BA_TONNAGES" :key="t.value" class="filter-check">
          <input type="checkbox" :checked="tonnage.includes(t.value)" @change="toggleTonnage(t.value)" />
          {{ t.label }}
        </label>
      </template>
      <template v-else>
        <div v-for="group in activeGroups" :key="group.key" class="tg-group">
          <div class="tg-header" @click="toggleExpand(group.key)">
            <input
              type="checkbox"
              :checked="isGroupChecked(group)"
              :indeterminate="isGroupIndeterminate(group)"
              @click.stop
              @change="toggleGroup(group)"
            />
            <span class="tg-label">{{ group.label }}</span>
            <span class="tg-sublabel">{{ group.sublabel }}</span>
            <span class="tg-chevron" :class="{ open: expanded[group.key] }">›</span>
          </div>
          <div v-if="expanded[group.key]" class="tg-options">
            <label v-for="opt in group.options" :key="opt.label" class="filter-check tg-opt">
              <input
                type="checkbox"
                :checked="isOptionChecked(opt)"
                @change="toggleOption(opt)"
              />
              {{ opt.label }}
            </label>
          </div>
        </div>
      </template>
    </div>
    <div class="filter-section">
      <h3 class="filter-title">Era</h3>
      <label v-for="eraOpt in eras" :key="eraOpt.label" class="filter-check">
        <input
          type="checkbox"
          :checked="era.includes(eraOpt.label)"
          @change="toggleEra(eraOpt.label)"
        />
        {{ eraOpt.label }} <span class="era-years">[{{ eraOpt.years }}]</span>
      </label>
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
      <div class="hp-omni-toggles">
        <label class="filter-check hp-excl-omni">
          <input
            type="checkbox"
            :checked="hardpoints.excludeOmni"
            @change="emit('update:hardpoints', { ...hardpoints, excludeOmni: !hardpoints.excludeOmni, omniOnly: false })"
          />
          Exclude Omni
        </label>
        <label class="filter-check hp-omni-only">
          <input
            type="checkbox"
            :checked="hardpoints.omniOnly"
            @change="emit('update:hardpoints', { ...hardpoints, omniOnly: !hardpoints.omniOnly, excludeOmni: false })"
          />
          Omni only
        </label>
      </div>
    </div>
    <a class="clear-all" href="#" @click.prevent="clearAll">Clear All</a>
  </aside>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { defaultHardpoints } from '../composables/useMechList'
import type { HardpointFilters, HpKey } from '../composables/useMechList'

interface TonnageOption {
  label: string
  values: number[]
}
interface TonnageGroup {
  key: string
  label: string
  sublabel: string
  options: TonnageOption[]
}

const MECH_GROUPS: TonnageGroup[] = [
  { key: 'protomech', label: 'ProtoMech', sublabel: '',
    options: [
      { label: '1–5t',   values: [1, 5] },
      { label: '6–10t',  values: [10] },
      { label: '11–15t', values: [15] },
      { label: '16–24t', values: [20, 21, 24] },
    ],
  },
  { key: 'light', label: 'Light', sublabel: '25–35t',
    options: [
      { label: '25t', values: [25, 26, 27, 28] },
      { label: '30t', values: [30] },
      { label: '35t', values: [35] },
    ],
  },
  { key: 'medium', label: 'Medium', sublabel: '40–55t',
    options: [
      { label: '40t', values: [40] },
      { label: '45t', values: [45] },
      { label: '50t', values: [50] },
      { label: '55t', values: [55] },
    ],
  },
  { key: 'heavy', label: 'Heavy', sublabel: '60–75t',
    options: [
      { label: '60t', values: [60] },
      { label: '65t', values: [65] },
      { label: '70t', values: [70] },
      { label: '75t', values: [75] },
    ],
  },
  { key: 'assault', label: 'Assault', sublabel: '80–100t',
    options: [
      { label: '80t',  values: [80] },
      { label: '85t',  values: [85] },
      { label: '90t',  values: [90] },
      { label: '95t',  values: [95] },
      { label: '100t', values: [100] },
    ],
  },
  { key: 'superheavy', label: 'Super Heavy', sublabel: '100t+',
    options: [
      { label: '105–125t', values: [105, 110, 115, 120, 125] },
      { label: '130–150t', values: [130, 135, 140, 145, 150] },
      { label: '155–200t', values: [155, 160, 165, 170, 175, 180, 185, 190, 195, 200] },
      { label: '200t+',    values: [255] },
    ],
  },
]

const BA_TONNAGES = [
  { value: 1.6,  label: '1.6t'  },
  { value: 2.4,  label: '2.4t'  },
  { value: 3.0,  label: '3t'    },
  { value: 3.75, label: '3.75t' },
  { value: 4.0,  label: '4t'    },
  { value: 4.5,  label: '4.5t'  },
  { value: 5.0,  label: '5t'    },
  { value: 6.0,  label: '6t'    },
  { value: 7.5,  label: '7.5t'  },
  { value: 8.0,  label: '8t'    },
  { value: 10.0, label: '10t'   },
  { value: 12.0, label: '12t'   },
]

const VTOL_GROUPS: TonnageGroup[] = [
  { key: 'light', label: 'Light', sublabel: '≤35t',
    options: [
      { label: '≤15t',   values: [0.5, 5, 10, 13, 15] },
      { label: '20–24t', values: [20, 21, 22, 24] },
      { label: '25t',    values: [25] },
      { label: '30t',    values: [30] },
      { label: '35t',    values: [35] },
    ],
  },
  { key: 'medium', label: 'Medium', sublabel: '40–55t',
    options: [
      { label: '40t',    values: [40] },
      { label: '45t',    values: [45] },
      { label: '50–51t', values: [50, 51] },
      { label: '55t',    values: [55] },
    ],
  },
  { key: 'heavy', label: 'Heavy', sublabel: '60t',
    options: [
      { label: '60t', values: [60] },
    ],
  },
]

const VEHICLE_GROUPS: TonnageGroup[] = [
  { key: 'light', label: 'Light', sublabel: '≤35t',
    options: [
      { label: '≤15t', values: [3, 5, 8, 10, 11, 12, 15] },
      { label: '20t',  values: [20] },
      { label: '25t',  values: [25, 27] },
      { label: '30t',  values: [30] },
      { label: '35t',  values: [35] },
    ],
  },
  { key: 'medium', label: 'Medium', sublabel: '40–55t',
    options: [
      { label: '40t', values: [40] },
      { label: '45t', values: [45] },
      { label: '50t', values: [50] },
      { label: '55t', values: [55] },
    ],
  },
  { key: 'heavy', label: 'Heavy', sublabel: '60–75t',
    options: [
      { label: '60t',    values: [60] },
      { label: '65t',    values: [65] },
      { label: '70t',    values: [70] },
      { label: '73–75t', values: [73, 75] },
    ],
  },
  { key: 'assault', label: 'Assault', sublabel: '80–100t',
    options: [
      { label: '80t',  values: [80] },
      { label: '85t',  values: [85] },
      { label: '90t',  values: [90] },
      { label: '95t',  values: [95] },
      { label: '100t', values: [100] },
    ],
  },
  { key: 'superheavy', label: 'Super Heavy', sublabel: '100t+',
    options: [
      { label: '110–150t', values: [110, 125, 130, 140, 150] },
      { label: '160–200t', values: [160, 175, 190, 200] },
      { label: '200t+',    values: [300, 316] },
    ],
  },
]

const props = defineProps<{
  mode: string
  tonnage: number[]
  era: string[]
  hasLowerArm: boolean | null
  hasHand: boolean | null
  hardpoints: HardpointFilters
}>()

const emit = defineEmits<{
  'update:tonnage': [value: number[]]
  'update:era': [value: string[]]
  'update:hasLowerArm': [value: boolean | null]
  'update:hasHand': [value: boolean | null]
  'update:hardpoints': [value: HardpointFilters]
  'clearAll': []
}>()

const HP_TYPES = [
  { key: 'ballistic' as const, label: 'Ballistic',   color: 'var(--hp-ballistic)' },
  { key: 'energy'    as const, label: 'Energy',      color: 'var(--hp-energy)'    },
  { key: 'missile'   as const, label: 'Missile',     color: 'var(--hp-missile)'   },
  { key: 'special'   as const, label: 'Special',     color: 'var(--hp-special)'   },
  { key: 'wing'      as const, label: 'WingMount',   color: 'var(--hp-wingmount)' },
  { key: 'bomb'      as const, label: 'BombBay',     color: 'var(--hp-bombbay)'   },
  { key: 'handheld'  as const, label: 'HandHeld',    color: 'var(--hp-handheld)'  },
]

const HP_LOCS = [
  { key: '',             label: 'ANY' },
  { key: 'RightArm',    label: 'RA'  },
  { key: 'RightTorso',  label: 'RT'  },
  { key: 'CenterTorso', label: 'CT'  },
  { key: 'Head',        label: 'HD'  },
  { key: 'LeftTorso',   label: 'LT'  },
  { key: 'LeftArm',     label: 'LA'  },
]

const eras = [
  { label: 'Succession Wars', years: '2781–3049' },
  { label: 'Clan Invasion',   years: '3050–3061' },
  { label: 'Civil War',       years: '3062–3067' },
  { label: 'Jihad',           years: '3068–3080' },
  { label: 'Republic',        years: '3081–3130' },
  { label: 'Dark Age',        years: '3131+' },
]

const activeGroups = computed(() => {
  if (props.mode === 'vtol') return VTOL_GROUPS
  if (props.mode === 'vehicle') return VEHICLE_GROUPS
  return MECH_GROUPS
})

const expanded = ref<Record<string, boolean>>({})

function toggleExpand(key: string) {
  expanded.value = { ...expanded.value, [key]: !expanded.value[key] }
}

function allGroupValues(group: TonnageGroup): number[] {
  return [...new Set(group.options.flatMap(o => o.values))]
}

function isGroupChecked(group: TonnageGroup): boolean {
  return allGroupValues(group).every(v => props.tonnage.includes(v))
}

function isGroupIndeterminate(group: TonnageGroup): boolean {
  const vals = allGroupValues(group)
  const some = vals.some(v => props.tonnage.includes(v))
  return some && !vals.every(v => props.tonnage.includes(v))
}

function isOptionChecked(opt: TonnageOption): boolean {
  return opt.values.every(v => props.tonnage.includes(v))
}

function toggleGroup(group: TonnageGroup) {
  const vals = allGroupValues(group)
  if (isGroupChecked(group)) {
    emit('update:tonnage', props.tonnage.filter(v => !vals.includes(v)))
  } else {
    const next = [...new Set([...props.tonnage, ...vals])]
    emit('update:tonnage', next)
  }
}

function toggleOption(opt: TonnageOption) {
  if (isOptionChecked(opt)) {
    emit('update:tonnage', props.tonnage.filter(v => !opt.values.includes(v)))
  } else {
    const next = [...new Set([...props.tonnage, ...opt.values])]
    emit('update:tonnage', next)
  }
}

function toggleTonnage(value: number) {
  const next = props.tonnage.includes(value)
    ? props.tonnage.filter(v => v !== value)
    : [...props.tonnage, value]
  emit('update:tonnage', next)
}

function toggleEra(value: string) {
  const next = props.era.includes(value)
    ? props.era.filter(e => e !== value)
    : [...props.era, value]
  emit('update:era', next)
}

function stepCount(key: HpKey, delta: number) {
  const updated = { ...props.hardpoints }
  const cur = updated[key].count
  const next = Math.max(0, Math.min(20, cur + delta))
  updated[key] = { ...updated[key], count: next }
  emit('update:hardpoints', updated)
}

function setLoc(key: HpKey, loc: string) {
  const updated = { ...props.hardpoints }
  updated[key] = { ...updated[key], loc }
  emit('update:hardpoints', updated)
}

function clearAll() {
  emit('update:tonnage', [])
  emit('update:era', [])
  emit('update:hasLowerArm', null)
  emit('update:hasHand', null)
  emit('update:hardpoints', defaultHardpoints())
  emit('clearAll')
}
</script>

<style scoped>
.filter-panel {
  width: var(--filter-panel-width, 280px);
  min-width: var(--filter-panel-width, 280px);
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
.era-years { font-size: 11px; color: var(--text-muted); }
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

/* Tonnage accordion */
.tg-group { margin-bottom: 2px; }
.tg-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
  cursor: pointer;
  font-size: 13px;
  color: var(--text-primary);
  user-select: none;
}
.tg-header input[type=checkbox] { cursor: pointer; accent-color: var(--accent-blue); flex-shrink: 0; }
.tg-label { font-weight: 500; }
.tg-sublabel { font-size: 11px; color: var(--text-muted); flex: 1; }
.tg-chevron {
  font-size: 14px;
  color: var(--text-muted);
  transform: rotate(0deg);
  transition: transform 0.15s;
  line-height: 1;
}
.tg-chevron.open { transform: rotate(90deg); }
.tg-options {
  padding-left: 22px;
  border-left: 1px solid var(--border-default);
  margin-left: 7px;
  margin-bottom: 4px;
}
.tg-opt { font-size: 12px; padding: 2px 0; }

.clear-all {
  display: block;
  margin-top: 8px;
  font-size: 12px;
  color: var(--text-muted);
}
.clear-all:hover { color: var(--accent-orange); text-decoration: none; }

.hardpoints-section { overflow-x: auto; }
.hp-grid { font-size: 11px; min-width: 0; }
.hp-header-row,
.hp-row {
  display: flex;
  align-items: center;
  gap: 2px;
  padding: 2px 0;
}
.hp-row-dim { opacity: 0.5; }
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
.hp-step:disabled { opacity: 0.3; cursor: default; }
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
.hp-omni-toggles { margin-top: 6px; }
</style>
