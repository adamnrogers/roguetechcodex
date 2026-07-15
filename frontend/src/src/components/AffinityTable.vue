<template>
  <div class="affinity-wrap">
    <table class="affinity-table">
      <thead>
        <tr>
          <th class="th-missions">Missions</th>
          <th class="th-source">Source</th>
          <th class="th-desc">Affinity</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, i) in flatRows" :key="i">
          <td class="td-missions">{{ row.missions }}</td>
          <td class="td-source">
            <RouterLink
              v-if="row.affinityType === 'Quirk'"
              :to="`/quirks/${row.quirk_name}`"
              class="affinity-link"
              >{{ row.source }}</RouterLink
            >
            <span v-else class="td-source-text">{{ row.source }}</span>
          </td>
          <td class="td-desc">
            <span class="level-name">{{ row.levelName }}</span>
            <span v-if="row.description" class="level-desc">: {{ row.description }}</span>
          </td>
        </tr>
        <tr v-if="!flatRows.length">
          <td colspan="3" class="td-empty">No affinity data available.</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { humanizeTag } from '../utils/humanize'
import type { AffinityEntry } from '../composables/useChassisDetail'

const props = defineProps<{ affinities: AffinityEntry[] }>()

interface FlatRow {
  missions: number
  source: string
  affinityType: string
  quirk_name: string
  levelName: string
  description: string
  sortKey: number
}

const flatRows = computed((): FlatRow[] => {
  const rows: FlatRow[] = []
  for (const aff of props.affinities) {
    for (const lv of aff.levels) {
      let source: string
      if (aff.affinity_type === 'Global') {
        source = 'Generic'
      } else if (aff.affinity_type === 'Chassis') {
        source = 'Chassis'
      } else if (aff.affinity_type === 'Quirk') {
        source = aff.quirk_ui_name || humanizeTag(aff.quirk_name.replace(/^Quirk_/, ''))
      } else {
        source = aff.affinity_type
      }
      rows.push({
        missions: lv.missions_required,
        source,
        affinityType: aff.affinity_type,
        quirk_name: aff.quirk_name,
        levelName: lv.level_name,
        description: lv.description,
        sortKey: lv.missions_required,
      })
    }
  }
  return rows.sort((a, b) => a.sortKey - b.sortKey)
})
</script>

<style scoped>
.affinity-wrap {
  overflow-x: auto;
}

.affinity-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.affinity-table thead tr {
  background: rgba(88, 166, 255, 0.07);
}

.affinity-table th {
  color: var(--text-muted);
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.4px;
  padding: 6px 10px;
  text-align: left;
  white-space: nowrap;
  border-bottom: 1px solid rgba(88, 166, 255, 0.15);
}

.th-missions {
  width: 72px;
}
.th-source {
  width: 160px;
}

.affinity-table td {
  padding: 5px 10px;
  color: var(--text-primary);
  vertical-align: top;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

.td-missions {
  color: var(--text-muted);
  text-align: right;
  font-variant-numeric: tabular-nums;
}

.td-source-text {
  color: var(--text-muted);
}

.affinity-link {
  color: var(--accent-blue);
  text-decoration: none;
}

.affinity-link:hover {
  text-decoration: underline;
}

.level-name {
  font-weight: 600;
  color: var(--accent-orange);
}

.level-desc {
  color: var(--text-primary);
}

.td-empty {
  color: var(--text-muted);
  font-style: italic;
  text-align: center;
  padding: 12px;
}
</style>
