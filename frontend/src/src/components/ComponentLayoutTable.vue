<template>
  <div class="layout-table-wrap">
    <table class="layout-table">
      <thead>
        <tr>
          <th class="th-group"></th>
          <th class="th-sub"></th>
          <th class="th-col">{{ colHeaders[0] }}</th>
          <th class="th-col">{{ colHeaders[1] }}</th>
          <th class="th-col">{{ colHeaders[2] }}</th>
        </tr>
      </thead>
      <tbody>
        <template v-for="group in tableData" :key="group.name">
          <tr v-for="(row, ri) in group.rows" :key="row.subrow" :class="`row-${row.subrow.toLowerCase()}`">
            <td v-if="ri === 0" :rowspan="SUBROWS.length" class="group-label">
              {{ group.name }}
            </td>
            <td class="sub-label">{{ row.subrow }}</td>

            <!-- Col 0 (Right for mechs, Front for vehicles) -->
            <td class="data-cell">
              <template v-if="row.subrow === 'Health'">
                <div v-for="(line, i) in row.right.healthLines" :key="i" class="health-line">{{ line }}</div>
              </template>
              <template v-else-if="row.subrow === 'HardPoints'">
                <span v-for="(hp, i) in row.right.hps" :key="i" class="hp-badge" :style="hp.style">{{ hp.label }}</span>
                <span v-if="!row.right.hps?.length" class="cell-empty">—</span>
              </template>
              <template v-else>
                <div v-for="(item, i) in row.right.items" :key="i" class="cell-item" :data-itype="item.type">
                  <RouterLink v-if="item.route" :to="item.route" class="item-link">
                    <span :style="item.weaponCategory ? { color: WEAPON_CAT_COLOURS[item.weaponCategory] } : {}">{{ item.text }}</span>
                  </RouterLink>
                  <template v-else>
                    <span :style="item.weaponCategory ? { color: WEAPON_CAT_COLOURS[item.weaponCategory] } : {}">{{ item.text }}</span>
                  </template>
                </div>
                <span v-if="!row.right.items?.length" class="cell-empty">—</span>
              </template>
            </td>

            <!-- Col 1 (Center / Turret) -->
            <td class="data-cell">
              <template v-if="!row.center">
                <span class="cell-empty">—</span>
              </template>
              <template v-else-if="row.subrow === 'Health'">
                <div v-for="(line, i) in row.center.healthLines" :key="i" class="health-line">{{ line }}</div>
              </template>
              <template v-else-if="row.subrow === 'HardPoints'">
                <span v-for="(hp, i) in row.center.hps" :key="i" class="hp-badge" :style="hp.style">{{ hp.label }}</span>
                <span v-if="!row.center.hps?.length" class="cell-empty">—</span>
              </template>
              <template v-else>
                <div v-for="(item, i) in row.center.items" :key="i" class="cell-item" :data-itype="item.type">
                  <RouterLink v-if="item.route" :to="item.route" class="item-link">
                    <span :style="item.weaponCategory ? { color: WEAPON_CAT_COLOURS[item.weaponCategory] } : {}">{{ item.text }}</span>
                  </RouterLink>
                  <template v-else>
                    <span :style="item.weaponCategory ? { color: WEAPON_CAT_COLOURS[item.weaponCategory] } : {}">{{ item.text }}</span>
                  </template>
                </div>
                <span v-if="!row.center.items?.length" class="cell-empty">—</span>
              </template>
            </td>

            <!-- Col 2 (Left / Rear) -->
            <td class="data-cell">
              <template v-if="row.subrow === 'Health'">
                <div v-for="(line, i) in row.left.healthLines" :key="i" class="health-line">{{ line }}</div>
              </template>
              <template v-else-if="row.subrow === 'HardPoints'">
                <span v-for="(hp, i) in row.left.hps" :key="i" class="hp-badge" :style="hp.style">{{ hp.label }}</span>
                <span v-if="!row.left.hps?.length" class="cell-empty">—</span>
              </template>
              <template v-else>
                <div v-for="(item, i) in row.left.items" :key="i" class="cell-item" :data-itype="item.type">
                  <RouterLink v-if="item.route" :to="item.route" class="item-link">
                    <span :style="item.weaponCategory ? { color: WEAPON_CAT_COLOURS[item.weaponCategory] } : {}">{{ item.text }}</span>
                  </RouterLink>
                  <template v-else>
                    <span :style="item.weaponCategory ? { color: WEAPON_CAT_COLOURS[item.weaponCategory] } : {}">{{ item.text }}</span>
                  </template>
                </div>
                <span v-if="!row.left.items?.length" class="cell-empty">—</span>
              </template>
            </td>
          </tr>
        </template>

        <!-- Unlocated catch-all: items whose mounted_location doesn't match any known column -->
        <template v-if="unlocatedFixed.length || unlocatedDynamic.length">
          <tr class="row-health unlocated-header-row">
            <td class="group-label" :rowspan="2">Unlocated</td>
            <td class="sub-label">Fixed</td>
            <td class="data-cell" colspan="3">
              <template v-if="unlocatedFixed.length">
                <div v-for="(item, i) in unlocatedFixed" :key="i" class="cell-item" :data-itype="item.type">
                  <RouterLink v-if="item.route" :to="item.route" class="item-link">
                    <span :style="item.weaponCategory ? { color: WEAPON_CAT_COLOURS[item.weaponCategory] } : {}">{{ item.text }}</span>
                  </RouterLink>
                  <template v-else>
                    <span :style="item.weaponCategory ? { color: WEAPON_CAT_COLOURS[item.weaponCategory] } : {}">{{ item.text }}</span>
                  </template>
                </div>
              </template>
              <span v-else class="cell-empty">—</span>
            </td>
          </tr>
          <tr class="row-dynamic">
            <td class="sub-label">Dynamic</td>
            <td class="data-cell" colspan="3">
              <template v-if="unlocatedDynamic.length">
                <div v-for="(item, i) in unlocatedDynamic" :key="i" class="cell-item" :data-itype="item.type">
                  <RouterLink v-if="item.route" :to="item.route" class="item-link">
                    <span :style="item.weaponCategory ? { color: WEAPON_CAT_COLOURS[item.weaponCategory] } : {}">{{ item.text }}</span>
                  </RouterLink>
                  <template v-else>
                    <span :style="item.weaponCategory ? { color: WEAPON_CAT_COLOURS[item.weaponCategory] } : {}">{{ item.text }}</span>
                  </template>
                </div>
              </template>
              <span v-else class="cell-empty">—</span>
            </td>
          </tr>
        </template>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import type { VariantLocation, LoadoutLocation, InventoryItem, EquipmentItem } from '../composables/useChassisDetail'

const props = defineProps<{
  variantLocations: VariantLocation[]
  loadoutLocations?: LoadoutLocation[]
  fixedEquipment: EquipmentItem[]
  inventory: InventoryItem[]
  unitType?: string
}>()

const SUBROWS = ['Health', 'HardPoints', 'Fixed', 'Dynamic'] as const

const isVehicle = computed(() =>
  props.unitType === 'vehicle' || props.unitType === 'vtol'
)

// Mech groups: 3 groups × 3 cols (Right/Center/Left)
const MECH_GROUPS = [
  { name: 'Arms / Head', cols: ['RightArm',   'Head',        'LeftArm']   },
  { name: 'Torso',       cols: ['RightTorso', 'CenterTorso', 'LeftTorso'] },
  { name: 'Legs',        cols: ['RightLeg',   null,          'LeftLeg']   },
]
// Vehicle groups: 2 groups × 3 cols
const VEHICLE_GROUPS = [
  { name: 'Sides',   cols: ['Right',  null,     'Left']   },
  { name: 'F/T/R',   cols: ['Front',  'Turret', 'Rear']   },
]

const groups = computed(() => isVehicle.value ? VEHICLE_GROUPS : MECH_GROUPS)
const colHeaders = computed(() =>
  isVehicle.value ? ['Right', 'Turret/Center', 'Left / Rear'] : ['Right', 'Center', 'Left']
)

const HP_STYLES: Record<string, { label: string; bg: string; color: string }> = {
  Omni:              { label: 'O',  bg: 'rgba(230,180,60,0.2)',   color: '#e6b43c' },
  Ballistic:         { label: 'B',  bg: 'rgba(88,166,255,0.2)',   color: '#58a6ff' },
  Energy:            { label: 'E',  bg: 'rgba(63,185,80,0.2)',    color: '#3fb950' },
  Missile:           { label: 'M',  bg: 'rgba(180,130,255,0.2)',  color: '#b482ff' },
  Special:           { label: 'S',  bg: 'rgba(240,136,62,0.2)',   color: '#f0883e' },
  WingMountedWeapon: { label: 'WM', bg: 'rgba(128,128,128,0.15)', color: '#8b96a3' },
  InternalBombBay:   { label: 'IB', bg: 'rgba(248,81,73,0.15)',   color: '#f85149' },
  SpecialHandHeld:   { label: 'SH', bg: 'rgba(56,189,193,0.15)',  color: '#38bdc1' },
}

// Index variant locations by name
const locMap = computed(() => {
  const m: Record<string, VariantLocation> = {}
  for (const loc of props.variantLocations) m[loc.location] = loc
  return m
})

// Index loadout locations by name (for current armor values)
const loadoutLocMap = computed(() => {
  const m: Record<string, LoadoutLocation> = {}
  for (const loc of props.loadoutLocations ?? []) m[loc.location] = loc
  return m
})

// For vehicles all equipment lives in inventory; split by ComponentDefType:
//   Upgrade / HeatSink → structurally fixed (engine, structure, crew, traits, etc.)
//   Weapon / AmmunitionBox → dynamic loadout
const VEHICLE_FIXED_TYPES = new Set(['Upgrade', 'HeatSink'])

const effectiveFixed = computed<EquipmentItem[]>(() => {
  if (!isVehicle.value) return props.fixedEquipment
  return props.inventory.filter(i => VEHICLE_FIXED_TYPES.has(i.component_def_type))
})

const effectiveInventory = computed<InventoryItem[]>(() => {
  if (!isVehicle.value) return props.inventory
  return props.inventory.filter(i => !VEHICLE_FIXED_TYPES.has(i.component_def_type))
})

// Index fixed equipment by location
const fixedByLoc = computed(() => {
  const m: Record<string, EquipmentItem[]> = {}
  for (const item of effectiveFixed.value) {
    ;(m[item.mounted_location] ??= []).push(item)
  }
  return m
})

// Index inventory by location
const invByLoc = computed(() => {
  const m: Record<string, InventoryItem[]> = {}
  for (const item of effectiveInventory.value) {
    ;(m[item.mounted_location] ??= []).push(item)
  }
  return m
})

const WEAPON_CAT_COLOURS: Record<string, string> = {
  Ballistic: '#58a6ff',
  Energy:    '#3fb950',
  Missile:   '#b482ff',
  Melee:     '#ff5555',
  Support:   '#f0883e',
}

interface HpBadge { label: string; style: Record<string, string> }
interface CellItem { text: string; type: string; route: string | null; weaponCategory: string | null }
interface CellData {
  healthLines?: string[]
  hps?: HpBadge[]
  items?: CellItem[]
}

function componentType(id: string): string {
  if (/[Hh]and[Hh]eld/.test(id)) return 'handheld'
  if (/[Ss]pecialist/.test(id)) return 'specialist'
  if (/^Weapon_/.test(id)) return 'weapon'
  if (/^Ammo_/.test(id)) return 'ammo'
  if (/^Gear_JumpJet_/.test(id)) return 'jumpjet'
  if (/^(Gear_HeatSinkKit_|Gear_Heatsink_|Gear_HeatSink_)/.test(id)) return 'heatsink'
  if (/^Quirk_/.test(id)) return 'quirk'
  return 'upgrade'
}

function gearRoute(id: string, defType: string): string | null {
  if (!id) return null
  // Structural defaults (e.g. Default_Cockpit) have no gear page
  if (/^Default_/.test(id)) return null
  // Quirks take precedence
  if (/^Quirk_/.test(id)) return `/quirks/${id}`
  if (defType === 'Weapon') return `/weapons/${id}`
  if (defType === 'Upgrade' || defType === 'HeatSink' || defType === 'AmmunitionBox' || defType === 'JumpJet') return `/equipment/${id}`
  return null
}

function aggregateItems(rawItems: { component_def_id: string; component_def_type: string; weapon_category?: string | null; ui_name?: string | null }[]): CellItem[] {
  // Track first-seen defType, weapon_category, and ui_name per id
  const counts = new Map<string, number>()
  const defTypes = new Map<string, string>()
  const weaponCategories = new Map<string, string | null>()
  const uiNames = new Map<string, string | null>()
  for (const item of rawItems) {
    counts.set(item.component_def_id, (counts.get(item.component_def_id) ?? 0) + 1)
    if (!defTypes.has(item.component_def_id)) defTypes.set(item.component_def_id, item.component_def_type)
    if (!weaponCategories.has(item.component_def_id)) weaponCategories.set(item.component_def_id, item.weapon_category ?? null)
    if (!uiNames.has(item.component_def_id)) uiNames.set(item.component_def_id, item.ui_name ?? null)
  }
  return [...counts.entries()].map(([id, count]) => {
    const displayName = uiNames.get(id) || formatName(id)
    return {
      text: count > 1 ? `${count}x ${displayName}` : displayName,
      type: componentType(id),
      route: gearRoute(id, defTypes.get(id) ?? ''),
      weaponCategory: weaponCategories.get(id) ?? null,
    }
  })
}

const _PREFIX_RE = /^(Weapon|Ammo|Gear|Linked|emod|Quirk|Default|VehicleTrait|Unique|BoltOn)_/

// Display name overrides for known IDs that format poorly from their ComponentDefID
const _DISPLAY_NAME_OVERRIDES: Record<string, string> = {
  'Default_Armor_Standard':       'Armor',
  'Default_Structure_Standard':   'Structure',
  'Default_HeatSinkKit_Single':   'Cooling',
  'Default_Gyro_Standard':        'Gyro',
  'Gear_Engine_Standard':         'Engine',
  'Default_EnginePart_Heatsinks': 'Engine HS',
}

function formatName(id: string): string {
  if (_DISPLAY_NAME_OVERRIDES[id]) return _DISPLAY_NAME_OVERRIDES[id]
  // Strip up to two chained prefixes (e.g. BoltOn_Weapon_AMS_Flare → AMS_Flare)
  let s = id.replace(_PREFIX_RE, '')
  if (_PREFIX_RE.test(s)) s = s.replace(_PREFIX_RE, '')
  return s
    .replace(/_/g, ' ')
    .replace(/([a-z])([A-Z])/g, '$1 $2')
    .replace(/([A-Z]{2,})([A-Z][a-z])/g, '$1 $2')
    .replace(/([a-zA-Z])(\d{2,})/g, '$1 $2')
    .replace(/\s{2,}/g, ' ')
    .trim()
}

function buildCell(locName: string | null, subrow: string): CellData | null {
  if (!locName) return null
  const loc = locMap.value[locName]

  if (subrow === 'Health') {
    if (!loc) return { healthLines: ['—'] }
    const ll = loadoutLocMap.value[locName]
    const structure = Math.round(loc.internal_structure)
    const lines: string[] = []
    if (loc.max_rear_armor > 0) {
      const curF = ll?.current_armor ?? loc.max_armor
      const curR = ll?.current_rear_armor ?? loc.max_rear_armor
      lines.push(`FA: ${curF}/${loc.max_armor}`)
      lines.push(`RA: ${curR}/${loc.max_rear_armor}`)
    } else {
      const curF = ll?.current_armor ?? loc.max_armor
      lines.push(`A: ${curF}/${loc.max_armor}`)
    }
    lines.push(`S: ${structure}`)
    return { healthLines: lines }
  }

  if (subrow === 'HardPoints') {
    if (!loc) return { hps: [] }
    const hps: HpBadge[] = loc.hardpoints
      .filter(hp => hp.weapon_mount_id !== 'AntiPersonnel' && hp.weapon_mount_id !== 'BattleArmor')
      .map(hp => {
        const s = hp.omni ? HP_STYLES['Omni'] : HP_STYLES[hp.weapon_mount_id]
        return {
          label: s?.label ?? hp.weapon_mount_id.slice(0, 1),
          style: s
            ? { background: s.bg, color: s.color }
            : { background: 'rgba(128,128,128,0.15)', color: '#8b96a3' },
        }
      })
    return { hps }
  }

  if (subrow === 'Fixed') {
    return { items: aggregateItems(fixedByLoc.value[locName] ?? []) }
  }

  // Dynamic: mechdef loadout inventory
  return { items: aggregateItems(invByLoc.value[locName] ?? []) }
}

const tableData = computed(() =>
  groups.value.map(group => ({
    name: group.name,
    rows: SUBROWS.map(subrow => ({
      subrow,
      right:  buildCell(group.cols[0], subrow) ?? _emptyCell(subrow),
      center: buildCell(group.cols[1], subrow),
      left:   buildCell(group.cols[2], subrow) ?? _emptyCell(subrow),
    })),
  }))
)

// All location column names known to the current layout
const knownLocations = computed<Set<string>>(() => {
  const s = new Set<string>()
  for (const group of groups.value) {
    for (const col of group.cols) {
      if (col) s.add(col)
    }
  }
  return s
})

// Fixed equipment items with unknown or blank mounted_location
const unlocatedFixed = computed<CellItem[]>(() => {
  const unknown = effectiveFixed.value.filter(
    item => !item.mounted_location || !knownLocations.value.has(item.mounted_location)
  )
  return aggregateItems(unknown)
})

// Inventory items with unknown or blank mounted_location
const unlocatedDynamic = computed<CellItem[]>(() => {
  const unknown = effectiveInventory.value.filter(
    item => !item.mounted_location || !knownLocations.value.has(item.mounted_location)
  )
  return aggregateItems(unknown)
})

function _emptyCell(subrow: string): CellData {
  if (subrow === 'Health') return { healthLines: ['—'] }
  if (subrow === 'HardPoints') return { hps: [] }
  return { items: [] }
}
</script>

<style scoped>
.layout-table-wrap {
  overflow-x: auto;
  margin-top: 8px;
}

.layout-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
  table-layout: fixed;
}

.layout-table thead tr {
  background: rgba(88, 166, 255, 0.07);
}

.layout-table th {
  color: var(--text-muted);
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  padding: 6px 10px;
  text-align: left;
  border-bottom: 1px solid rgba(88, 166, 255, 0.15);
}

.th-group { width: 90px; }
.th-sub   { width: 80px; }

.group-label {
  background: rgba(88, 166, 255, 0.06);
  color: var(--text-primary);
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 6px 10px;
  vertical-align: top;
  border-right: 1px solid rgba(88, 166, 255, 0.15);
  border-bottom: 1px solid rgba(88, 166, 255, 0.15);
  white-space: nowrap;
}

.sub-label {
  color: var(--text-muted);
  font-size: 11px;
  padding: 5px 10px;
  white-space: nowrap;
  vertical-align: top;
  border-right: 1px solid rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

.data-cell {
  padding: 5px 8px;
  vertical-align: top;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
  border-right: 1px solid rgba(255, 255, 255, 0.04);
}

.row-health td {
  border-top: 1px solid rgba(88, 166, 255, 0.15);
}

.health-line {
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
  font-size: 11px;
  white-space: nowrap;
  line-height: 1.6;
}

.hp-badge {
  display: inline-block;
  font-size: 10px;
  font-weight: 700;
  padding: 1px 5px;
  border-radius: 3px;
  margin-right: 2px;
  margin-bottom: 2px;
  letter-spacing: 0.2px;
  white-space: nowrap;
}

.cell-item {
  font-size: 11px;
  line-height: 1.5;
  color: var(--text-primary);
  word-break: break-word;
}

.cell-item[data-itype="weapon"]     { color: #58a6ff; font-weight: 700; }
.cell-item[data-itype="ammo"]       { color: #f0883e; }
.cell-item[data-itype="heatsink"]   { color: #38bdc1; }
.cell-item[data-itype="jumpjet"]    { color: #b482ff; }
.cell-item[data-itype="quirk"]      { color: #3fb950; }
.cell-item[data-itype="upgrade"]    { color: var(--text-muted); }
.cell-item[data-itype="handheld"]   { color: #58a6ff; background: rgba(88,166,255,0.12); padding: 0 4px; border-radius: 3px; }
.cell-item[data-itype="specialist"] { color: #3fb950; background: rgba(63,185,80,0.12);  padding: 0 4px; border-radius: 3px; }

.cell-empty {
  color: var(--text-muted);
  font-size: 11px;
}

.item-link {
  color: inherit;
  text-decoration: none;
}

.item-link:hover {
  text-decoration: underline;
  opacity: 0.85;
}
</style>
