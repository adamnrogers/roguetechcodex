<template>
  <div class="infobox">
    <table class="infobox-table">
      <tbody>
        <tr v-if="weight_class" class="row-alt">
          <td class="label">Weight Class</td>
          <td class="value">
            <span class="wc-badge" :data-wc="weight_class">{{ weight_class }}</span>
          </td>
        </tr>
        <tr v-if="tonnage != null">
          <td class="label">Tonnage</td>
          <td class="value">{{ tonnage }} t</td>
        </tr>
        <tr v-if="top_speed != null" class="row-alt">
          <td class="label">Top Speed</td>
          <td class="value">{{ top_speed }} kph</td>
        </tr>
        <tr v-if="max_jumpjets != null">
          <td class="label">Max Jump Jets</td>
          <td class="value">{{ max_jumpjets }}</td>
        </tr>
        <tr v-if="battle_value" class="row-alt">
          <td class="label">Battle Value</td>
          <td class="value">{{ formatBV(battle_value) }}</td>
        </tr>
        <tr v-if="stock_role">
          <td class="label">Stock Role</td>
          <td class="value">{{ stock_role }}</td>
        </tr>
        <tr v-if="unique_mech" class="row-alt">
          <td class="label">Classification</td>
          <td class="value"><span class="unique-badge">Unique Mech</span></td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
interface InfoBoxProps {
  tonnage?: number | null
  weight_class?: string | null
  top_speed?: number | null
  max_jumpjets?: number | null
  battle_value?: number | null
  stock_role?: string | null
  unique_mech?: boolean
}

defineProps<InfoBoxProps>()

function formatBV(bv: number): string {
  return (bv / 1000).toLocaleString(undefined, { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}
</script>

<style scoped>
.infobox {
  float: right;
  margin: 0 0 20px 28px;
  width: 260px;
  background: var(--bg-infobox);
  border: var(--border-default);
  border-radius: var(--card-radius);
  overflow: hidden;
  flex-shrink: 0;
}

.infobox-table {
  width: 100%;
  border-collapse: collapse;
}

.infobox-table td {
  padding: 6px 12px;
  vertical-align: middle;
}

.label {
  color: var(--text-muted);
  font-size: 12px;
  white-space: nowrap;
}

.value {
  color: var(--text-primary);
  font-size: 13px;
  text-align: right;
}

.row-alt {
  background: rgba(255, 255, 255, 0.02);
}

.wc-badge {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  padding: 2px 7px;
  border-radius: var(--badge-radius);
  letter-spacing: 0.3px;
}

.wc-badge[data-wc="LIGHT"]   { background: var(--badge-light-bg);   color: var(--badge-light-fg); }
.wc-badge[data-wc="MEDIUM"]  { background: var(--badge-medium-bg);  color: var(--badge-medium-fg); }
.wc-badge[data-wc="HEAVY"]   { background: var(--badge-heavy-bg);   color: var(--badge-heavy-fg); }
.wc-badge[data-wc="ASSAULT"] { background: var(--badge-assault-bg); color: var(--badge-assault-fg); }

.unique-badge {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  padding: 2px 7px;
  border-radius: var(--badge-radius);
  letter-spacing: 0.3px;
  background: rgba(210, 153, 34, 0.18);
  color: #d29922;
}
</style>
