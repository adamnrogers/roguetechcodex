<template>
  <div class="wst-wrap">
    <div class="wst-scroll">
      <table class="wst-table">
        <thead>
          <!-- Super-headers -->
          <tr class="super-row">
            <th class="col-mode" rowspan="2">Mode</th>
            <th class="col-ammo" rowspan="2">Ammo</th>
            <th class="group-header" colspan="3">Damage</th>
            <th class="group-header" colspan="4">Per Salvo</th>
            <th class="group-header" colspan="2">Modifiers</th>
            <th class="group-header" colspan="2">TAC</th>
            <th class="group-header" colspan="5">Range</th>
            <th class="group-header" colspan="1">Other</th>
          </tr>
          <!-- Sub-headers -->
          <tr class="sub-row">
            <th class="col-num">Norm</th>
            <th class="col-num">Heat</th>
            <th class="col-num">Stab</th>
            <th class="col-num">Rounds</th>
            <th class="col-num">Proj</th>
            <th class="col-num">Heat</th>
            <th class="col-num">Recoil</th>
            <th class="col-num">Accuracy</th>
            <th class="col-num">Ev.Ign</th>
            <th class="col-num">Chance</th>
            <th class="col-num">Shards</th>
            <th class="col-num col-range">Min</th>
            <th class="col-num col-range">Short</th>
            <th class="col-num col-range">Med</th>
            <th class="col-num col-range">Long</th>
            <th class="col-num col-range">Max</th>
            <th class="col-num">Indirect</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="mode in modes" :key="mode.mode_id" :class="{ 'row-base': mode.is_base_mode }">
            <td class="col-mode">
              <span class="mode-name">{{ mode.mode_ui_name }}</span>
            </td>
            <td class="col-ammo ammo-cell">{{ mode.ammo_category ?? '' }}</td>
            <td class="col-num">{{ fmtNum(mode.damage) }}</td>
            <td class="col-num">{{ fmtNum(mode.heat_damage) }}</td>
            <td class="col-num">{{ fmtNum(mode.instability) }}</td>
            <td class="col-num">{{ fmtNum(mode.shots_when_fired) }}</td>
            <td class="col-num">{{ fmtNum(mode.projectiles_per_shot) }}</td>
            <td class="col-num">{{ fmtNum(mode.heat_generated) }}</td>
            <td class="col-num">{{ fmtNum(mode.attack_recoil) }}</td>
            <td class="col-num">{{ fmtNum(mode.accuracy_modifier) }}</td>
            <td class="col-num">{{ fmtNum(mode.evasion_pips_ignored) }}</td>
            <td class="col-num">{{ fmtPct(mode.ap_crit_chance_mult) }}</td>
            <td class="col-num">{{ fmtNum(mode.ap_shards_mod) }}</td>
            <td class="col-num col-range">{{ fmtRange(mode.min_range) }}</td>
            <td class="col-num col-range">{{ fmtRange(mode.range_short) }}</td>
            <td class="col-num col-range">{{ fmtRange(mode.range_medium) }}</td>
            <td class="col-num col-range">{{ fmtRange(mode.range_long) }}</td>
            <td class="col-num col-range">{{ fmtRange(mode.max_range) }}</td>
            <td class="col-num">
              <span :class="mode.indirect_fire_capable ? 'yes' : 'no'">
                {{ mode.indirect_fire_capable ? 'Yes' : 'No' }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { WeaponMode } from '../composables/useGearList'

defineProps<{ modes: WeaponMode[] }>()

function fmtNum(v: number | null | undefined): string {
  if (v == null || v === 0) return '0'
  return Number.isInteger(v) ? String(v) : v.toFixed(v < 1 ? 3 : 2).replace(/\.?0+$/, '')
}

function fmtPct(v: number | null | undefined): string {
  if (v == null || v === 0) return '0'
  return (v * 100).toFixed(1).replace(/\.0$/, '') + '%'
}

function fmtRange(v: number | null | undefined): string {
  if (v == null || v <= 0) return '0'
  return String(v)
}
</script>

<style scoped>
.wst-wrap {
  margin-top: 4px;
}

.wst-scroll {
  overflow-x: auto;
  border-radius: 6px;
  border: 1px solid rgba(128, 128, 128, 0.15);
}

.wst-table {
  border-collapse: collapse;
  font-size: 12px;
  width: 100%;
  min-width: 480px;
  white-space: nowrap;
}

/* Super-header row */
.super-row th {
  background: rgba(255, 255, 255, 0.06);
  color: var(--text-primary);
  font-weight: 700;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  padding: 5px 10px;
  text-align: center;
  border-bottom: 1px solid rgba(128, 128, 128, 0.15);
  border-right: 1px solid rgba(128, 128, 128, 0.1);
}

.super-row th:last-child {
  border-right: none;
}

.super-row th.col-mode,
.super-row th.col-ammo {
  text-align: left;
  background: rgba(255, 255, 255, 0.03);
  color: var(--text-muted);
}

/* Sub-header row */
.sub-row th {
  background: rgba(255, 255, 255, 0.03);
  color: var(--text-muted);
  font-weight: 600;
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  padding: 4px 8px;
  text-align: right;
  border-bottom: 1px solid rgba(128, 128, 128, 0.2);
}

/* Data cells */
.wst-table td {
  padding: 5px 8px;
  border-bottom: 1px solid rgba(128, 128, 128, 0.07);
  color: var(--text-primary);
  text-align: right;
  font-variant-numeric: tabular-nums;
  font-size: 12px;
}

.wst-table td.col-mode,
.wst-table td.col-ammo {
  text-align: left;
}

.wst-table tbody tr:last-child td {
  border-bottom: none;
}

.wst-table tbody tr:hover td {
  background: rgba(255, 255, 255, 0.03);
}

.row-base td {
  background: rgba(88, 166, 255, 0.05);
}

.row-base:hover td {
  background: rgba(88, 166, 255, 0.08) !important;
}

.mode-name {
  font-weight: 600;
  color: var(--text-primary);
}

.ammo-cell {
  color: var(--text-muted);
  font-size: 11px;
}

.col-range {
  color: var(--text-muted);
}

.yes {
  color: #50c878;
}
.no {
  color: var(--text-muted);
}
</style>
