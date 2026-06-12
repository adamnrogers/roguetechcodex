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

    <!-- Weapon: category, type hierarchy, weight/heat ranges -->
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

      <div class="filter-section">
        <h3 class="filter-title">Type</h3>
        <div v-for="group in WEAPON_TYPE_GROUPS" :key="group.type" class="type-group">
          <label class="type-group-label">
            <input
              type="checkbox"
              :checked="isGroupTypeChecked(group)"
              :indeterminate.prop="isGroupTypeIndeterminate(group)"
              @change="toggleGroupType(group)"
            />
            {{ group.label }}
          </label>
          <div v-if="group.subtypes.length" class="type-subtypes">
            <label v-for="sub in group.subtypes" :key="sub.value" class="type-sub-label">
              <input
                type="checkbox"
                :checked="isSubtypeChecked(sub.value)"
                @change="toggleSubtype(sub.value)"
              />
              {{ sub.label }}
            </label>
          </div>
        </div>
      </div>

      <div class="filter-section">
        <h3 class="filter-title">Weight (t)</h3>
        <div class="range-inputs">
          <input
            type="number" class="range-input" placeholder="Min" min="0" max="55" step="0.5"
            :value="minTonnage ?? ''"
            @change="emit('update:minTonnage', ($event.target as HTMLInputElement).value ? parseFloat(($event.target as HTMLInputElement).value) : null)"
          />
          <span class="range-sep">–</span>
          <input
            type="number" class="range-input" placeholder="Max" min="0" max="55" step="0.5"
            :value="maxTonnage ?? ''"
            @change="emit('update:maxTonnage', ($event.target as HTMLInputElement).value ? parseFloat(($event.target as HTMLInputElement).value) : null)"
          />
        </div>
      </div>

      <div class="filter-section">
        <h3 class="filter-title">Heat</h3>
        <div class="range-inputs">
          <input
            type="number" class="range-input" placeholder="Min" min="0" max="125" step="1"
            :value="minHeat ?? ''"
            @change="emit('update:minHeat', ($event.target as HTMLInputElement).value ? parseFloat(($event.target as HTMLInputElement).value) : null)"
          />
          <span class="range-sep">–</span>
          <input
            type="number" class="range-input" placeholder="Max" min="0" max="125" step="1"
            :value="maxHeat ?? ''"
            @change="emit('update:maxHeat', ($event.target as HTMLInputElement).value ? parseFloat(($event.target as HTMLInputElement).value) : null)"
          />
        </div>
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
  weaponTypes: string[]
  weaponSubtypes: string[]
  minTonnage: number | null
  maxTonnage: number | null
  minHeat: number | null
  maxHeat: number | null
}>()

const emit = defineEmits<{
  'update:includeTypes':      [value: string[]]
  'update:excludeTypes':      [value: string[]]
  'update:includeCategories': [value: string[]]
  'update:excludeCategories': [value: string[]]
  'update:includeLocations':  [value: string[]]
  'update:excludeLocations':  [value: string[]]
  'update:weaponTypes':    [value: string[]]
  'update:weaponSubtypes': [value: string[]]
  'update:minTonnage':     [value: number | null]
  'update:maxTonnage':     [value: number | null]
  'update:minHeat':        [value: number | null]
  'update:maxHeat':        [value: number | null]
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

interface WeaponSubOption { value: string; label: string }
interface WeaponTypeGroup { type: string; label: string; subtypes: WeaponSubOption[] }

const WEAPON_TYPE_GROUPS: WeaponTypeGroup[] = [
  {
    type: 'Autocannon', label: 'Autocannon',
    subtypes: [
      { value: 'AC2',   label: 'AC/2' },
      { value: 'AC5',   label: 'AC/5' },
      { value: 'AC10',  label: 'AC/10' },
      { value: 'AC20',  label: 'AC/20' },
      { value: 'UAC2',  label: 'UAC/2' },
      { value: 'UAC5',  label: 'UAC/5' },
      { value: 'UAC10', label: 'UAC/10' },
      { value: 'UAC20', label: 'UAC/20' },
      { value: 'LB2X',  label: 'LB-2X' },
      { value: 'LB5X',  label: 'LB-5X' },
      { value: 'LB10X', label: 'LB-10X' },
      { value: 'LB20X', label: 'LB-20X' },
    ],
  },
  {
    type: 'Gauss', label: 'Gauss',
    subtypes: [{ value: 'Gauss', label: 'Gauss' }],
  },
  {
    type: 'MachineGun', label: 'Machine Gun',
    subtypes: [{ value: 'MachineGun', label: 'MG' }],
  },
  {
    type: 'Laser', label: 'Laser',
    subtypes: [
      { value: 'SmallLaser',       label: 'Small' },
      { value: 'SmallLaserER',     label: 'Small ER' },
      { value: 'SmallLaserPulse',  label: 'Small Pulse' },
      { value: 'MediumLaser',      label: 'Medium' },
      { value: 'MediumLaserER',    label: 'Medium ER' },
      { value: 'MediumLaserPulse', label: 'Medium Pulse' },
      { value: 'LargeLaser',       label: 'Large' },
      { value: 'LargeLaserER',     label: 'Large ER' },
      { value: 'LargeLaserPulse',  label: 'Large Pulse' },
    ],
  },
  {
    type: 'PPC', label: 'PPC',
    subtypes: [
      { value: 'PPC',     label: 'PPC' },
      { value: 'PPCER',   label: 'ER PPC' },
      { value: 'PPCSnub', label: 'Snub-Nose' },
    ],
  },
  {
    type: 'Flamer', label: 'Flamer',
    subtypes: [{ value: 'Flamer', label: 'Flamer' }],
  },
  {
    type: 'LRM', label: 'LRM',
    subtypes: [
      { value: 'LRM5',  label: 'LRM-5' },
      { value: 'LRM10', label: 'LRM-10' },
      { value: 'LRM15', label: 'LRM-15' },
      { value: 'LRM20', label: 'LRM-20' },
    ],
  },
  {
    type: 'SRM', label: 'SRM',
    subtypes: [
      { value: 'SRM2', label: 'SRM-2' },
      { value: 'SRM4', label: 'SRM-4' },
      { value: 'SRM6', label: 'SRM-6' },
    ],
  },
  {
    type: 'Melee', label: 'Melee',
    subtypes: [],
  },
]

const hasActiveFilters = computed(() =>
  props.includeTypes.length > 0 ||
  props.excludeTypes.length > 0 ||
  props.includeCategories.length > 0 ||
  props.excludeCategories.length > 0 ||
  props.includeLocations.length > 0 ||
  props.excludeLocations.length > 0 ||
  props.weaponTypes.length > 0 ||
  props.weaponSubtypes.length > 0 ||
  props.minTonnage !== null ||
  props.maxTonnage !== null ||
  props.minHeat !== null ||
  props.maxHeat !== null
)

function clearAll() {
  emit('update:includeTypes', [])
  emit('update:excludeTypes', [])
  emit('update:includeCategories', [])
  emit('update:excludeCategories', [])
  emit('update:includeLocations', [])
  emit('update:excludeLocations', [])
  emit('update:weaponTypes', [])
  emit('update:weaponSubtypes', [])
  emit('update:minTonnage', null)
  emit('update:maxTonnage', null)
  emit('update:minHeat', null)
  emit('update:maxHeat', null)
}

function allSubtypesOf(group: WeaponTypeGroup): string[] {
  return group.subtypes.map(s => s.value)
}

function isGroupTypeChecked(group: WeaponTypeGroup): boolean {
  if (group.subtypes.length === 0) return props.weaponTypes.includes(group.type)
  return allSubtypesOf(group).every(v => props.weaponSubtypes.includes(v))
}

function isGroupTypeIndeterminate(group: WeaponTypeGroup): boolean {
  if (group.subtypes.length === 0) return false
  const subs = allSubtypesOf(group)
  const some = subs.some(v => props.weaponSubtypes.includes(v))
  return some && !subs.every(v => props.weaponSubtypes.includes(v))
}

function toggleGroupType(group: WeaponTypeGroup) {
  if (group.subtypes.length === 0) {
    const next = props.weaponTypes.includes(group.type)
      ? props.weaponTypes.filter(t => t !== group.type)
      : [...props.weaponTypes, group.type]
    emit('update:weaponTypes', next)
    return
  }
  const subs = allSubtypesOf(group)
  if (isGroupTypeChecked(group)) {
    emit('update:weaponSubtypes', props.weaponSubtypes.filter(v => !subs.includes(v)))
  } else {
    const merged = [...new Set([...props.weaponSubtypes, ...subs])]
    emit('update:weaponSubtypes', merged)
  }
}

function isSubtypeChecked(value: string): boolean {
  return props.weaponSubtypes.includes(value)
}

function toggleSubtype(value: string) {
  const next = props.weaponSubtypes.includes(value)
    ? props.weaponSubtypes.filter(v => v !== value)
    : [...props.weaponSubtypes, value]
  emit('update:weaponSubtypes', next)
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

.type-group {
  margin-bottom: 8px;
}

.type-group-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: var(--text-primary);
  cursor: pointer;
  user-select: none;
}

.type-group-label input[type="checkbox"] {
  accent-color: var(--accent-blue);
  cursor: pointer;
}

.type-subtypes {
  margin-left: 18px;
  margin-top: 2px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.type-sub-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 11px;
  color: var(--text-muted);
  cursor: pointer;
  user-select: none;
}

.type-sub-label input[type="checkbox"] {
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
</style>
