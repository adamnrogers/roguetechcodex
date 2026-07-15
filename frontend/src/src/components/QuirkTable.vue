<template>
  <div class="quirk-wrap">
    <table class="quirk-table">
      <thead>
        <tr>
          <th class="th-source">Source</th>
          <th class="th-desc">Effect</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(row, i) in flatRows" :key="i">
          <td class="td-source">
            <RouterLink :to="`/quirks/${row.id}`" class="quirk-link">{{ row.source }}</RouterLink>
          </td>
          <td class="td-desc">{{ row.effect }}</td>
        </tr>
        <tr v-if="!flatRows.length">
          <td colspan="2" class="td-empty">No quirk data available.</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import type { QuirkEffect } from '../composables/useChassisDetail'

const props = defineProps<{ quirks: QuirkEffect[] }>()

interface FlatRow {
  id: string
  source: string
  effect: string
}

const flatRows = computed((): FlatRow[] => {
  const rows: FlatRow[] = []
  for (const quirk of props.quirks) {
    for (const effect of quirk.bonus_descriptions) {
      rows.push({
        id: quirk.id,
        source: quirk.ui_name || quirk.id,
        effect,
      })
    }
  }
  return rows
})
</script>

<style scoped>
.quirk-wrap {
  overflow-x: auto;
}

.quirk-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.quirk-table thead tr {
  background: rgba(88, 166, 255, 0.07);
}

.quirk-table th {
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

.th-source {
  width: 160px;
}

.quirk-table td {
  padding: 5px 10px;
  color: var(--text-primary);
  vertical-align: top;
  border-bottom: 1px solid rgba(255, 255, 255, 0.04);
}

.quirk-link {
  color: var(--accent-blue);
  text-decoration: none;
}

.quirk-link:hover {
  text-decoration: underline;
}

.td-empty {
  color: var(--text-muted);
  font-style: italic;
  text-align: center;
  padding: 12px;
}
</style>
