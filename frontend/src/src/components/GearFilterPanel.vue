<template>
  <aside class="filter-panel">
    <!-- Equipment: tri-state component-type pills -->
    <template v-if="mode === 'equipment'">
      <div class="filter-section">
        <h3 class="filter-title">Type</h3>
        <p class="filter-hint">
          <span class="hint-inc">+ include only</span> · <span class="hint-exc">− exclude</span>
        </p>
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
        <p class="filter-hint">
          <span class="hint-inc">+ include only</span> · <span class="hint-exc">− exclude</span>
        </p>
        <TriStatePills
          :options="locationOptions"
          :includeValues="includeLocations"
          :excludeValues="excludeLocations"
          @update:includeValues="$emit('update:includeLocations', $event)"
          @update:excludeValues="$emit('update:excludeLocations', $event)"
        />
      </div>
    </template>

    <!-- Weapon: type hierarchy, weight/heat/slots ranges -->
    <template v-if="mode === 'weapon'">
      <div class="filter-section">
        <h3 class="filter-title">Type</h3>
        <div v-for="group in WEAPON_CATEGORY_GROUPS" :key="group.groupId" class="type-group">
          <div
            class="type-group-header"
            @click="group.subtypes.length ? toggleTypeExpand(group.groupId) : undefined"
          >
            <input
              type="checkbox"
              :checked="isGroupChecked(group)"
              :indeterminate.prop="isGroupIndeterminate(group)"
              @click.stop
              @change="toggleGroup(group)"
            />
            <span class="type-group-label-text">{{ group.label }}</span>
            <span
              v-if="group.subtypes.length"
              class="type-chevron"
              :class="{ open: expandedTypes[group.groupId] }"
              >›</span
            >
          </div>
          <div v-if="group.subtypes.length && expandedTypes[group.groupId]" class="type-subtypes">
            <label v-for="sub in group.subtypes" :key="sub.id" class="type-sub-label">
              <input
                type="checkbox"
                :checked="isCategoryIdChecked(sub.id)"
                @change="toggleCategoryId(sub.id)"
              />
              {{ sub.label }}
            </label>
          </div>
        </div>
      </div>

      <div class="filter-section">
        <h3 class="filter-title">Weight</h3>
        <div class="range-inputs">
          <input
            type="number"
            class="range-input"
            placeholder="Min"
            min="0"
            max="55"
            step="0.5"
            :value="minTonnage ?? ''"
            @change="
              emit(
                'update:minTonnage',
                ($event.target as HTMLInputElement).value
                  ? parseFloat(($event.target as HTMLInputElement).value)
                  : null,
              )
            "
          />
          <span class="range-sep">–</span>
          <input
            type="number"
            class="range-input"
            placeholder="Max"
            min="0"
            max="55"
            step="0.5"
            :value="maxTonnage ?? ''"
            @change="
              emit(
                'update:maxTonnage',
                ($event.target as HTMLInputElement).value
                  ? parseFloat(($event.target as HTMLInputElement).value)
                  : null,
              )
            "
          />
        </div>
      </div>

      <div class="filter-section">
        <h3 class="filter-title">Heat</h3>
        <div class="range-inputs">
          <input
            type="number"
            class="range-input"
            placeholder="Min"
            min="0"
            max="125"
            step="1"
            :value="minHeat ?? ''"
            @change="
              emit(
                'update:minHeat',
                ($event.target as HTMLInputElement).value
                  ? parseFloat(($event.target as HTMLInputElement).value)
                  : null,
              )
            "
          />
          <span class="range-sep">–</span>
          <input
            type="number"
            class="range-input"
            placeholder="Max"
            min="0"
            max="125"
            step="1"
            :value="maxHeat ?? ''"
            @change="
              emit(
                'update:maxHeat',
                ($event.target as HTMLInputElement).value
                  ? parseFloat(($event.target as HTMLInputElement).value)
                  : null,
              )
            "
          />
        </div>
      </div>

      <div class="filter-section">
        <h3 class="filter-title">Slots</h3>
        <div class="range-inputs">
          <input
            type="number"
            class="range-input"
            placeholder="Min"
            min="0"
            max="20"
            step="1"
            :value="minSlots ?? ''"
            @change="
              emit(
                'update:minSlots',
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
            min="0"
            max="20"
            step="1"
            :value="maxSlots ?? ''"
            @change="
              emit(
                'update:maxSlots',
                ($event.target as HTMLInputElement).value
                  ? parseInt(($event.target as HTMLInputElement).value)
                  : null,
              )
            "
          />
        </div>
      </div>
    </template>

    <a v-if="hasActiveFilters" class="clear-all" href="#" @click.prevent="clearAll">Clear All</a>
  </aside>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
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
  weaponCategoryIds: string[]
  minTonnage: number | null
  maxTonnage: number | null
  minHeat: number | null
  maxHeat: number | null
  minSlots: number | null
  maxSlots: number | null
}>()

const emit = defineEmits<{
  'update:includeTypes': [value: string[]]
  'update:excludeTypes': [value: string[]]
  'update:includeCategories': [value: string[]]
  'update:excludeCategories': [value: string[]]
  'update:includeLocations': [value: string[]]
  'update:excludeLocations': [value: string[]]
  'update:weaponTypes': [value: string[]]
  'update:weaponSubtypes': [value: string[]]
  'update:weaponCategoryIds': [value: string[]]
  'update:minTonnage': [value: number | null]
  'update:maxTonnage': [value: number | null]
  'update:minHeat': [value: number | null]
  'update:maxHeat': [value: number | null]
  'update:minSlots': [value: number | null]
  'update:maxSlots': [value: number | null]
}>()

const equipmentTypes = [
  { value: 'Upgrade', label: 'Upgrade' },
  { value: 'HeatSink', label: 'Heat Sink' },
  { value: 'AmmunitionBox', label: 'Ammo' },
  { value: 'JumpJet', label: 'Jump Jet' },
]

const locationOptions = [
  { value: 'All', label: 'Any (unrestricted)' },
  { value: 'Head', label: 'Head' },
  { value: 'Arms', label: 'Arms' },
  { value: 'CenterTorso', label: 'CT' },
  { value: 'LeftTorso', label: 'LT' },
  { value: 'RightTorso', label: 'RT' },
  { value: 'Legs', label: 'Legs' },
]

interface WeaponCategorySubOption {
  id: string
  label: string
}
interface WeaponCategoryGroup {
  groupId: string
  label: string
  subtypes: WeaponCategorySubOption[]
}

const WEAPON_CATEGORY_GROUPS: WeaponCategoryGroup[] = [
  {
    groupId: 'autocannon',
    label: 'Autocannons',
    subtypes: [
      { id: 'w/a/a/ac', label: 'AutoCannon' },
      { id: 'w/a/a/lac', label: 'Light AC' },
      { id: 'w/a/a/hvac', label: 'HV AC' },
      { id: 'w/a/a/rac', label: 'Rotary AC' },
      { id: 'w/a/a/shrac', label: 'SH Rotary AC' },
      { id: 'w/a/a/uac', label: 'Ultra AC' },
      { id: 'w/a/a/md', label: 'Mass Driver' },
      { id: 'w/a/a/lbx', label: 'LB-X AC' },
      { id: 'w/a/a/rifle', label: 'Rifle' },
    ],
  },
  {
    groupId: 'gauss',
    label: 'Magnetic Files',
    subtypes: [
      { id: 'w/a/g/gaussrifle', label: 'Gauss Rifle' },
      { id: 'w/a/g/lightgaussrifle', label: 'Light Gauss' },
      { id: 'w/a/g/heavygaussrifle', label: 'Heavy Gauss' },
      { id: 'w/a/g/sb', label: 'Silver Bullet' },
      { id: 'w/a/g/hag', label: 'Hyper-Assault' },
      { id: 'w/a/g/railgun', label: 'Railgun' },
      { id: 'w/a/g/plasmarailgun', label: 'Plasma Railgun' },
      { id: 'w/a/g/helicalrailgun', label: 'Helical Railgun' },
      { id: 'w/a/g/magshot', label: 'Magshot' },
      { id: 'w/a/g/raplbgr', label: 'RAPLBGR' },
      { id: 'w/a/g/taser', label: 'Taser' },
    ],
  },
  {
    groupId: 'other-ballistic',
    label: 'Other Ballistics',
    subtypes: [
      { id: 'w/a/o/mg', label: 'Machine Gun' },
      { id: 'w/a/o/artillery', label: 'Artillery' },
      { id: 'w/a/o/mortar', label: 'Mortar' },
    ],
  },
  {
    groupId: 'laser',
    label: 'Lasers',
    subtypes: [
      { id: 'w/e/l/laser', label: 'Laser' },
      { id: 'w/e/l/er', label: 'ER Laser' },
      { id: 'w/e/l/pulse', label: 'Pulse' },
      { id: 'w/e/l/x-pulse', label: 'X-Pulse' },
      { id: 'w/e/l/erpulse', label: 'ER Pulse' },
      { id: 'w/e/l/vspl', label: 'VSPL' },
      { id: 'w/e/l/heavy', label: 'Heavy' },
      { id: 'w/e/l/bombast', label: 'Bombast' },
      { id: 'w/e/l/binary', label: 'Binary' },
      { id: 'w/e/l/re', label: 'Re-engineered' },
      { id: 'w/e/l/chemical', label: 'Chemical' },
    ],
  },
  {
    groupId: 'ppc',
    label: 'PPCs',
    subtypes: [
      { id: 'w/e/p/ppc', label: 'PPC' },
      { id: 'w/e/p/erppc', label: 'ER PPC' },
      { id: 'w/e/p/hppc', label: 'Heavy PPC' },
      { id: 'w/e/p/snppc', label: 'Snubnose' },
      { id: 'w/e/p/lppc', label: 'Light PPC' },
      { id: 'w/e/p/rppc', label: 'Rotary PPC' },
      { id: 'w/e/p/xppc', label: 'Experimental' },
      { id: 'w/e/p/tsemp', label: 'TSEMP' },
    ],
  },
  {
    groupId: 'flamer',
    label: 'Plasma & Flamers',
    subtypes: [
      { id: 'w/e/p/flamer', label: 'Flamer' },
      { id: 'w/e/p/aflamer', label: 'Ammo Flamer' },
      { id: 'w/e/p/plasma', label: 'Plasma Cannon' },
    ],
  },
  {
    groupId: 'lrm',
    label: 'LRM',
    subtypes: [
      { id: 'w/m/l/lrm', label: 'LRM' },
      { id: 'w/m/l/clrm', label: 'Clan LRM' },
      { id: 'w/m/l/slrm', label: 'Streak LRM' },
      { id: 'w/m/l/elrm', label: 'Extended LRM' },
      { id: 'w/m/l/nlrm', label: 'Enhanced LRM' },
      { id: 'w/m/l/rlrm', label: 'Rotary LRM' },
      { id: 'w/m/l/mrm', label: 'MRM' },
      { id: 'w/m/t/thunderbolt', label: 'Thunderbolt' },
      { id: 'w/m/t/arrowiv', label: 'Arrow IV' },
    ],
  },
  {
    groupId: 'srm',
    label: 'SRM',
    subtypes: [
      { id: 'w/m/s/srm', label: 'SRM' },
      { id: 'w/m/s/csrm', label: 'Clan SRM' },
      { id: 'w/m/s/ssrm', label: 'Streak SRM' },
      { id: 'w/m/s/smrm', label: 'Streak MRM' },
      { id: 'w/m/s/hmrm', label: 'Heavy MRM' },
      { id: 'w/m/s/mrm', label: 'MRM' },
      { id: 'w/m/s/rl', label: 'Rocket Launcher' },
      { id: 'w/m/s/mms', label: 'MMS' },
    ],
  },
  {
    groupId: 'multimissile',
    label: 'Multi Missile',
    subtypes: [
      { id: 'w/m/s/mml', label: 'MML' },
      { id: 'w/m/s/smml', label: 'Streak MML' },
      { id: 'w/m/l/atm', label: 'ATM' },
      { id: 'w/m/l/iatm', label: 'iATM' },
    ],
  },
  {
    groupId: 'support',
    label: 'Support',
    subtypes: [
      { id: 'w/s/a/ams', label: 'AMS' },
      { id: 'w/s/a/lams', label: 'Laser AMS' },
      { id: 'w/s/t/tag', label: 'TAG' },
      { id: 'w/s/t/narc', label: 'NARC' },
      { id: 'w/s/t/inarc', label: 'iNARC' },
      { id: 'w/s/m/support', label: 'Support Weapon' },
      { id: 'w/s/m/explode', label: 'Suicide Weapon' },
    ],
  },
  {
    groupId: 'squad',
    label: 'Squad',
    subtypes: [
      { id: 'w/s/m/pa', label: 'Power Armor' },
      { id: 'w/s/m/ul', label: 'Ultralight' },
    ],
  },
  {
    groupId: 'specialist',
    label: 'Specialist / LAM',
    subtypes: [
      { id: 'w/s/h/HandHeld', label: 'Hand Held' },
      { id: 'w/s/h/BoltOn', label: 'Bolt On' },
      { id: 'w/w/w/bomb', label: 'Aircraft Weapon' },
      { id: 'w/b/b/InternalBombBay', label: 'Bomb Bay' },
      { id: 'LAMInternalBombBay', label: 'LAM Bomb Bay' },
      { id: 'LAMWingMount', label: 'LAM Wing Mount' },
      { id: 'LAMBAWingmountBay', label: 'LAM BA Wing Bay' },
      { id: 'LAMBooster', label: 'LAM Booster' },
      { id: 'LAMFlightSystems', label: 'LAM Flight Systems' },
      { id: 'LAMInfantryBay', label: 'LAM Infantry Bay' },
    ],
  },
]

const hasActiveFilters = computed(
  () =>
    props.includeTypes.length > 0 ||
    props.excludeTypes.length > 0 ||
    props.includeCategories.length > 0 ||
    props.excludeCategories.length > 0 ||
    props.includeLocations.length > 0 ||
    props.excludeLocations.length > 0 ||
    props.weaponCategoryIds.length > 0 ||
    props.minTonnage !== null ||
    props.maxTonnage !== null ||
    props.minHeat !== null ||
    props.maxHeat !== null ||
    props.minSlots !== null ||
    props.maxSlots !== null,
)

function clearAll() {
  emit('update:includeTypes', [])
  emit('update:excludeTypes', [])
  emit('update:includeCategories', [])
  emit('update:excludeCategories', [])
  emit('update:includeLocations', [])
  emit('update:excludeLocations', [])
  emit('update:weaponCategoryIds', [])
  emit('update:minTonnage', null)
  emit('update:maxTonnage', null)
  emit('update:minHeat', null)
  emit('update:maxHeat', null)
  emit('update:minSlots', null)
  emit('update:maxSlots', null)
}

const expandedTypes = ref<Record<string, boolean>>({})

function toggleTypeExpand(groupId: string) {
  expandedTypes.value = { ...expandedTypes.value, [groupId]: !expandedTypes.value[groupId] }
}

function groupIds(group: WeaponCategoryGroup): string[] {
  return group.subtypes.map((s) => s.id)
}

function isGroupChecked(group: WeaponCategoryGroup): boolean {
  const ids = groupIds(group)
  return ids.length > 0 && ids.every((id) => props.weaponCategoryIds.includes(id))
}

function isGroupIndeterminate(group: WeaponCategoryGroup): boolean {
  const ids = groupIds(group)
  const some = ids.some((id) => props.weaponCategoryIds.includes(id))
  return some && !ids.every((id) => props.weaponCategoryIds.includes(id))
}

function toggleGroup(group: WeaponCategoryGroup) {
  const ids = groupIds(group)
  if (isGroupChecked(group)) {
    emit(
      'update:weaponCategoryIds',
      props.weaponCategoryIds.filter((id) => !ids.includes(id)),
    )
  } else {
    emit('update:weaponCategoryIds', [...new Set([...props.weaponCategoryIds, ...ids])])
  }
}

function isCategoryIdChecked(id: string): boolean {
  return props.weaponCategoryIds.includes(id)
}

function toggleCategoryId(id: string) {
  const next = props.weaponCategoryIds.includes(id)
    ? props.weaponCategoryIds.filter((v) => v !== id)
    : [...props.weaponCategoryIds, id]
  emit('update:weaponCategoryIds', next)
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
.hint-inc {
  color: #58a6ff;
}
.hint-exc {
  color: rgba(255, 80, 80, 0.8);
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

.type-group {
  margin-bottom: 4px;
}

.type-group-header {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  user-select: none;
}

.type-group-header input[type='checkbox'] {
  accent-color: var(--accent-blue);
  cursor: pointer;
}

.type-group-label-text {
  flex: 1;
  font-size: 12px;
  color: var(--text-primary);
}

.type-chevron {
  font-size: 12px;
  color: var(--text-muted);
  transition: transform 0.15s;
  line-height: 1;
}

.type-chevron.open {
  transform: rotate(90deg);
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

.type-sub-label input[type='checkbox'] {
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
