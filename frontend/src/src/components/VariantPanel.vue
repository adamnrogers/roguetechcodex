<template>
  <div class="variant-panel">
    <!-- Header row -->
    <div class="variant-header" @click="open = !open">
      <span class="variant-name">{{ variant.variant_name || variant.id }}</span>
      <div class="variant-tags">
        <span v-for="tag in variant.era_tags" :key="'era-' + tag" class="tag tag-era">{{
          humanizeTag(tag)
        }}</span>
        <span v-for="tag in canonicalFactionTags" :key="'fac-' + tag" class="tag tag-faction">{{
          tag
        }}</span>
      </div>
      <span class="chevron" :class="{ open }">&#x25BE;</span>
    </div>

    <!-- Body -->
    <div v-if="open" class="variant-body">
      <!-- Armour summary -->
      <div class="armor-summary">
        <span v-for="loc in sortedLocations" :key="loc.location" class="armor-item">
          <span class="armor-loc">{{ abbreviateLocation(loc.location) }}:</span>
          <span class="armor-val">{{ formatArmorVal(loc.max_armor, loc.max_rear_armor) }}</span>
        </span>
      </div>

      <!-- Inventory table -->
      <table class="inv-table" v-if="groupedInventory.length">
        <thead>
          <tr>
            <th>Location</th>
            <th>Component</th>
            <th>Type</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="group in groupedInventory" :key="group.location">
            <tr
              v-for="(item, i) in group.items"
              :key="item.component_def_id + '-' + i"
              :class="{ 'row-alt': i % 2 === 1 }"
            >
              <td class="col-loc">{{ i === 0 ? group.location : '' }}</td>
              <td class="col-comp">{{ formatComponentName(item.component_def_id) }}</td>
              <td class="col-type">
                <span class="type-badge" :data-ctype="getComponentType(item.component_def_id)">
                  {{ getComponentType(item.component_def_id) }}
                </span>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { VariantDetail } from '../composables/useChassisDetail'
import { humanizeTag, canonicalizeFaction } from '../utils/humanize'

const props = defineProps<{
  variant: VariantDetail
  defaultOpen: boolean
}>()

const open = ref(props.defaultOpen)

const LOCATION_ORDER = [
  'CenterTorso',
  'LeftTorso',
  'RightTorso',
  'Head',
  'LeftArm',
  'RightArm',
  'LeftLeg',
  'RightLeg',
]

function locationIndex(loc: string): number {
  const i = LOCATION_ORDER.indexOf(loc)
  return i === -1 ? 99 : i
}

const sortedLocations = computed(() =>
  [...props.variant.locations].sort(
    (a, b) => locationIndex(a.location) - locationIndex(b.location),
  ),
)

const canonicalFactionTags = computed(() => {
  const seen = new Set<string>()
  const result: string[] = []
  for (const raw of props.variant.faction_tags) {
    const canonical = canonicalizeFaction(raw)
    if (canonical !== null && !seen.has(canonical)) {
      seen.add(canonical)
      result.push(canonical)
    }
  }
  return result.sort()
})

const groupedInventory = computed(() => {
  const order = LOCATION_ORDER
  const groups: Record<string, typeof props.variant.inventory> = {}
  for (const item of props.variant.inventory) {
    const loc = item.mounted_location
    if (!groups[loc]) groups[loc] = []
    groups[loc].push(item)
  }
  return Object.entries(groups)
    .sort(([a], [b]) => {
      const ai = order.indexOf(a)
      const bi = order.indexOf(b)
      return (ai === -1 ? 99 : ai) - (bi === -1 ? 99 : bi)
    })
    .map(([location, items]) => ({ location, items }))
})

function abbreviateLocation(loc: string): string {
  const map: Record<string, string> = {
    CenterTorso: 'C.Torso',
    LeftTorso: 'L.Torso',
    RightTorso: 'R.Torso',
    Head: 'Head',
    LeftArm: 'L.Arm',
    RightArm: 'R.Arm',
    LeftLeg: 'L.Leg',
    RightLeg: 'R.Leg',
  }
  return map[loc] ?? loc
}

function formatArmorVal(armor: number, rear: number): string {
  if (rear > 0) return `${armor}/${rear}r`
  return String(armor)
}

function getComponentType(id: string): string {
  if (/^(Gear_EngineCore_|Gear_Engine_|Linked_Engine_)/.test(id)) return 'Engine'
  if (/^(Gear_HeatSinkKit_|Gear_Heatsink_)/.test(id)) return 'Heat Sink'
  if (/^Gear_JumpJet_/.test(id)) return 'Jump Jet'
  if (/^Weapon_/.test(id)) return 'Weapon'
  if (/^Ammo_/.test(id)) return 'Ammo'
  return 'Equipment'
}

function formatComponentName(id: string): string {
  // Remove the first underscore-delimited segment (type prefix)
  const parts = id.split('_')
  if (parts.length <= 1) return id
  return parts.slice(1).join(' ')
}
</script>

<style scoped>
.variant-panel {
  border: var(--border-default);
  border-radius: var(--card-radius);
  margin-bottom: 8px;
  overflow: hidden;
}

.variant-header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 14px;
  cursor: pointer;
  background: var(--bg-card);
  transition: background 0.12s;
  user-select: none;
}

.variant-header:hover {
  background: var(--bg-card-hover);
}

.variant-name {
  font-weight: 700;
  color: var(--text-primary);
  font-size: 14px;
  flex-shrink: 0;
}

.variant-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  flex: 1;
}

.tag {
  font-size: 11px;
  padding: 2px 7px;
  border-radius: 10px;
}

.tag-era {
  background: rgba(88, 166, 255, 0.12);
  color: var(--accent-blue);
}

.tag-faction {
  background: rgba(255, 255, 255, 0.07);
  color: var(--text-muted);
}

.chevron {
  color: var(--text-muted);
  font-size: 14px;
  transition: transform 0.2s;
  flex-shrink: 0;
  transform: rotate(-90deg);
}

.chevron.open {
  transform: rotate(0deg);
}

.variant-body {
  padding: 12px 14px;
  background: var(--bg-primary);
}

/* Armour summary */
.armor-summary {
  display: flex;
  flex-wrap: wrap;
  gap: 10px 18px;
  margin-bottom: 14px;
}

.armor-item {
  font-size: 12px;
  color: var(--text-muted);
  white-space: nowrap;
}

.armor-loc {
  margin-right: 4px;
  color: var(--text-muted);
}

.armor-val {
  color: var(--text-primary);
}

/* Inventory table */
.inv-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.inv-table thead th {
  color: var(--text-muted);
  font-size: 11px;
  text-transform: uppercase;
  font-weight: 600;
  letter-spacing: 0.4px;
  padding: 5px 10px;
  text-align: left;
  background: rgba(88, 166, 255, 0.06);
}

.inv-table tbody td {
  padding: 4px 10px;
  color: var(--text-primary);
  vertical-align: top;
}

.row-alt {
  background: rgba(255, 255, 255, 0.02);
}

.col-loc {
  color: var(--text-muted);
  font-size: 12px;
  white-space: nowrap;
  min-width: 90px;
}

.col-comp {
  font-size: 12px;
}

.col-type {
  white-space: nowrap;
}

.type-badge {
  font-size: 10px;
  font-weight: 600;
  padding: 1px 6px;
  border-radius: 4px;
}

.type-badge[data-ctype='Weapon'] {
  background: rgba(88, 166, 255, 0.2);
  color: #58a6ff;
}
.type-badge[data-ctype='Ammo'] {
  background: rgba(240, 136, 62, 0.2);
  color: #f0883e;
}
.type-badge[data-ctype='Engine'] {
  background: rgba(139, 150, 163, 0.2);
  color: #8b96a3;
}
.type-badge[data-ctype='Heat Sink'] {
  background: rgba(56, 189, 193, 0.2);
  color: #38bdc1;
}
.type-badge[data-ctype='Jump Jet'] {
  background: rgba(180, 130, 255, 0.2);
  color: #b482ff;
}
.type-badge[data-ctype='Equipment'] {
  background: rgba(139, 150, 163, 0.12);
  color: #8b96a3;
}
</style>
