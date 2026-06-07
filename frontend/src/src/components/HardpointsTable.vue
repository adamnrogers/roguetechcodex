<template>
  <div class="hp-table-wrap">
    <table class="hp-table">
      <thead>
        <tr>
          <th>Location</th>
          <th>Hardpoints</th>
          <th>Max Armour</th>
          <th>Structure</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(loc, i) in locations" :key="loc.location" :class="{ 'row-alt': i % 2 === 1 }">
          <td class="col-location">{{ loc.location }}</td>
          <td class="col-hardpoints">
            <span
              v-for="(hp, j) in loc.hardpoints"
              :key="j"
              class="hp-badge"
              :style="hpStyle(hp.weapon_mount_id)"
              :title="hp.weapon_mount_id + (hp.omni ? ' (Omni)' : '')"
            >{{ hpLabel(hp.weapon_mount_id) }}</span>
            <span v-if="!loc.hardpoints.length" class="none-text">—</span>
          </td>
          <td class="col-armor">{{ formatArmor(loc.max_armor, loc.max_rear_armor) }}</td>
          <td class="col-structure">{{ loc.internal_structure }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import type { VariantLocation } from '../composables/useChassisDetail'

defineProps<{ locations: VariantLocation[] }>()

const HP_MAP: Record<string, { label: string; bg: string; color: string }> = {
  Ballistic:         { label: 'B',   bg: 'rgba(88,166,255,0.2)',   color: '#58a6ff' },
  Energy:            { label: 'E',   bg: 'rgba(63,185,80,0.2)',    color: '#3fb950' },
  Missile:           { label: 'M',   bg: 'rgba(180,130,255,0.2)',  color: '#b482ff' },
  Special:           { label: 'S',   bg: 'rgba(240,136,62,0.2)',   color: '#f0883e' },
  AntiPersonnel:     { label: 'AP',  bg: 'rgba(248,81,73,0.15)',   color: '#f85149' },
  WingMountedWeapon: { label: 'WM',  bg: 'rgba(128,128,128,0.15)', color: '#8b96a3' },
}

function hpLabel(id: string): string {
  return HP_MAP[id]?.label ?? id.slice(0, 4)
}

function hpStyle(id: string): Record<string, string> {
  const entry = HP_MAP[id]
  if (entry) return { background: entry.bg, color: entry.color }
  return { background: 'rgba(128,128,128,0.15)', color: '#8b96a3' }
}

function formatArmor(max: number, rear: number): string {
  if (rear > 0) return `${max} / ${rear}r`
  return String(max)
}
</script>

<style scoped>
.hp-table-wrap {
  overflow-x: auto;
}

.hp-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}

.hp-table thead tr {
  background: rgba(88, 166, 255, 0.08);
}

.hp-table thead th {
  color: var(--text-muted);
  font-size: 11px;
  text-transform: uppercase;
  font-weight: 600;
  letter-spacing: 0.4px;
  padding: 7px 12px;
  text-align: left;
  white-space: nowrap;
}

.hp-table tbody td {
  padding: 6px 12px;
  color: var(--text-primary);
  vertical-align: middle;
}

.row-alt {
  background: rgba(255, 255, 255, 0.02);
}

.col-location {
  font-size: 13px;
  white-space: nowrap;
}

.col-hardpoints {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  align-items: center;
}

/* flex on td doesn't work in all browsers — use a wrapper div approach via CSS grid trick */
td.col-hardpoints {
  display: table-cell;
}

.col-hardpoints .hp-badge,
.col-hardpoints .none-text {
  display: inline-flex;
  align-items: center;
}

.hp-badge {
  font-size: 10px;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
  margin-right: 3px;
  letter-spacing: 0.3px;
  white-space: nowrap;
}

.none-text {
  color: var(--text-muted);
  font-size: 12px;
}

.col-armor {
  font-size: 13px;
  white-space: nowrap;
}

.col-structure {
  font-size: 13px;
}
</style>
