<template>
  <div class="gear-page-outer">
    <div v-if="isLoading" class="skeleton-wrap">
      <div class="skeleton skeleton-title"></div>
      <div class="skeleton skeleton-line"></div>
      <div class="skeleton skeleton-line short"></div>
    </div>

    <div v-else-if="isError || !data" class="not-found">
      <p class="not-found-msg">Item not found.</p>
      <RouterLink :to="browsePath" class="back-link">← Back to {{ browseLabel }}</RouterLink>
    </div>

    <template v-else>
      <div class="gear-layout">
        <main class="main-col">
          <header class="page-header">
            <nav class="breadcrumb">
              in:&nbsp;<RouterLink :to="browsePath" class="bc-link">{{ browseLabel }}</RouterLink>
              <span class="bc-sep"> / </span>
              <span class="bc-id">{{ data.id }}</span>
            </nav>
            <h1 class="gear-title">{{ data.ui_name }}</h1>
            <div class="gear-badges">
              <span v-if="componentTypeLabel" class="ct-badge" :data-ct="componentTypeBadgeKey">
                {{ componentTypeLabel }}
              </span>
              <span v-if="data.weapon_category" class="wcat-badge" :data-wcat="data.weapon_category">
                {{ data.weapon_category }}
              </span>
            </div>
          </header>

          <!-- Description -->
          <section class="content-section">
            <h2 class="section-title">Description</h2>
            <div v-if="data.details" class="lore-text" v-html="renderRichText(data.details)"></div>
            <p v-else class="empty-text">No description available.</p>
          </section>

          <!-- Bonuses -->
          <section v-if="data.bonus_value_a || data.bonus_value_b" class="content-section">
            <h2 class="section-title">Effects</h2>
            <ul class="bonus-list">
              <li v-if="data.bonus_value_a" class="bonus-item">{{ data.bonus_value_a }}</li>
              <li v-if="data.bonus_value_b" class="bonus-item">{{ data.bonus_value_b }}</li>
            </ul>
          </section>

          <!-- Weapon stats (weapons only) -->
          <section v-if="data.weapon_category" class="content-section">
            <h2 class="section-title">Weapon Statistics</h2>
            <table class="stat-table">
              <tbody>
                <tr v-if="data.damage != null">
                  <td class="stat-label">Damage</td>
                  <td class="stat-value">{{ data.damage }}</td>
                </tr>
                <tr v-if="data.heat_generated != null">
                  <td class="stat-label">Heat</td>
                  <td class="stat-value">{{ data.heat_generated }}</td>
                </tr>
                <tr v-if="data.min_range != null || data.max_range != null">
                  <td class="stat-label">Range</td>
                  <td class="stat-value">{{ data.min_range ?? 0 }}–{{ data.max_range ?? '?' }} m</td>
                </tr>
                <tr v-if="data.shots_when_fired != null && data.shots_when_fired > 1">
                  <td class="stat-label">Shots/Volley</td>
                  <td class="stat-value">{{ data.shots_when_fired }}</td>
                </tr>
                <tr v-if="data.ammo_category">
                  <td class="stat-label">Ammo Type</td>
                  <td class="stat-value">{{ data.ammo_category }}</td>
                </tr>
              </tbody>
            </table>
          </section>

          <!-- Affinity data (quirk items only) -->
          <section v-if="data.related_affinities?.length" class="content-section">
            <h2 class="section-title">Affinity</h2>
            <AffinityTable :affinities="data.related_affinities" />
          </section>

          <!-- Used by mechs -->
          <section v-if="data.used_by_mechs.length" class="content-section">
            <h2 class="section-title">Used by Mechs ({{ data.used_by_mechs.length }})</h2>
            <div class="used-by-grid">
              <RouterLink
                v-for="m in data.used_by_mechs"
                :key="m.prefab_base"
                :to="`/mechs/${m.prefab_base}`"
                class="used-by-link"
              >{{ m.ui_name }}</RouterLink>
            </div>
          </section>

          <!-- Used by vehicles -->
          <section v-if="data.used_by_vehicles.length" class="content-section">
            <h2 class="section-title">Used by Vehicles ({{ data.used_by_vehicles.length }})</h2>
            <div class="used-by-grid">
              <RouterLink
                v-for="v in data.used_by_vehicles"
                :key="v.prefab_base"
                :to="`/vehicles/${v.prefab_base}`"
                class="used-by-link"
              >{{ v.ui_name }}</RouterLink>
            </div>
          </section>
        </main>

        <!-- Right infobox -->
        <aside class="side-col">
          <div class="infobox">
            <table class="infobox-table">
              <tbody>
                <tr v-if="data.tonnage != null">
                  <td class="ib-label">Tonnage</td>
                  <td class="ib-value">{{ data.tonnage }} t</td>
                </tr>
                <tr v-if="data.slots != null">
                  <td class="ib-label">Slots</td>
                  <td class="ib-value">{{ data.slots }}</td>
                </tr>
                <tr v-if="data.cost != null">
                  <td class="ib-label">Cost</td>
                  <td class="ib-value">{{ formatCost(data.cost) }}</td>
                </tr>
                <tr v-if="data.battle_value != null">
                  <td class="ib-label">Battle Value</td>
                  <td class="ib-value">{{ data.battle_value.toLocaleString() }}</td>
                </tr>
                <tr v-if="data.manufacturer">
                  <td class="ib-label">Manufacturer</td>
                  <td class="ib-value">{{ data.manufacturer }}</td>
                </tr>
                <tr v-if="data.model">
                  <td class="ib-label">Model</td>
                  <td class="ib-value">{{ data.model }}</td>
                </tr>
                <tr v-if="data.allowed_locations">
                  <td class="ib-label">Locations</td>
                  <td class="ib-value">{{ data.allowed_locations }}</td>
                </tr>
                <tr v-if="data.source_mod">
                  <td class="ib-label">Module</td>
                  <td class="ib-value">{{ humanizeMod(data.source_mod) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </aside>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { useGearDetail } from '../composables/useGearList'
import { renderRichText } from '../utils/richText'
import { humanizeMod } from '../utils/humanize'
import AffinityTable from '../components/AffinityTable.vue'

const route = useRoute()
const gearId = route.params.gearId as string

const { data, isLoading, isError } = useGearDetail(gearId)

// Infer browse mode from current URL prefix
const currentPath = route.path
const browsePath = computed(() => {
  if (currentPath.startsWith('/weapons')) return '/weapons'
  if (currentPath.startsWith('/quirks'))  return '/quirks'
  return '/equipment'
})
const browseLabel = computed(() => {
  if (currentPath.startsWith('/weapons')) return 'Weapons'
  if (currentPath.startsWith('/quirks'))  return 'Quirks'
  return 'Equipment'
})

const componentTypeLabel = computed(() => {
  if (!data.value) return null
  if (data.value.id.startsWith('Quirk_')) return 'Quirk'
  const labels: Record<string, string> = {
    Upgrade: 'Upgrade',
    Weapon: 'Weapon',
    HeatSink: 'Heat Sink',
    AmmunitionBox: 'Ammo',
    JumpJet: 'Jump Jet',
  }
  return data.value.component_type ? (labels[data.value.component_type] ?? data.value.component_type) : null
})

const componentTypeBadgeKey = computed(() => {
  if (!data.value) return ''
  if (data.value.id.startsWith('Quirk_')) return 'Quirk'
  return data.value.component_type ?? ''
})

function formatCost(c: number): string {
  if (c >= 1_000_000) return `${(c / 1_000_000).toFixed(1)}M ₵`
  if (c >= 1_000) return `${Math.round(c / 1_000).toLocaleString()}K ₵`
  return `${c.toLocaleString()} ₵`
}
</script>

<style scoped>
.gear-page-outer {
  max-width: var(--gear-max-width, 1100px);
  margin: 0 auto;
  padding: 24px 16px;
}

.skeleton-wrap {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding: 24px;
}
.skeleton {
  background: var(--bg-card);
  border-radius: 4px;
  animation: pulse 1.5s ease-in-out infinite;
}
.skeleton-title { height: 32px; width: 40%; }
.skeleton-line  { height: 16px; width: 80%; }
.skeleton-line.short { width: 50%; }
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.not-found {
  padding: 48px;
  text-align: center;
}
.not-found-msg { color: var(--text-muted); font-size: 16px; }
.back-link { color: var(--accent-blue); text-decoration: none; font-size: 14px; }
.back-link:hover { text-decoration: underline; }

.gear-layout {
  display: flex;
  gap: 32px;
  align-items: flex-start;
}

.main-col { flex: 1; min-width: 0; }

.side-col {
  width: 260px;
  flex-shrink: 0;
  position: sticky;
  top: calc(var(--nav-height) + 16px);
}

.page-header { margin-bottom: 24px; }

.breadcrumb {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 8px;
}
.bc-link { color: var(--accent-blue); text-decoration: none; }
.bc-link:hover { text-decoration: underline; }
.bc-sep { color: var(--text-muted); }
.bc-id { color: var(--text-muted); }

.gear-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 10px;
}

.gear-badges {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.ct-badge,
.wcat-badge {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  padding: 3px 10px;
  border-radius: var(--badge-radius, 3px);
  letter-spacing: 0.3px;
}

.ct-badge[data-ct="Upgrade"]       { background: rgba(88, 166, 255, 0.15); color: #58a6ff; }
.ct-badge[data-ct="Weapon"]        { background: rgba(255, 80,  80,  0.15); color: #ff5555; }
.ct-badge[data-ct="HeatSink"]      { background: rgba(255, 140, 0,   0.15); color: #ff8c00; }
.ct-badge[data-ct="AmmunitionBox"] { background: rgba(80,  200, 120, 0.15); color: #50c878; }
.ct-badge[data-ct="JumpJet"]       { background: rgba(180, 100, 255, 0.15); color: #b464ff; }
.ct-badge[data-ct="Quirk"]         { background: rgba(210, 153, 34,  0.15); color: #d29922; }

.wcat-badge[data-wcat="Ballistic"] { background: rgba(200, 160, 60, 0.15); color: #c8a03c; }
.wcat-badge[data-wcat="Energy"]    { background: rgba(80,  200, 255, 0.15); color: #50c8ff; }
.wcat-badge[data-wcat="Missile"]   { background: rgba(80,  200, 120, 0.15); color: #50c878; }
.wcat-badge[data-wcat="Melee"]     { background: rgba(255, 80,  80,  0.15); color: #ff5555; }
.wcat-badge[data-wcat="Support"]   { background: rgba(180, 100, 255, 0.15); color: #b464ff; }

.content-section {
  margin-bottom: 28px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  border-bottom: 1px solid rgba(128, 128, 128, 0.15);
  padding-bottom: 6px;
  margin: 0 0 12px;
}

.lore-text {
  font-size: 13px;
  color: var(--text-primary);
  line-height: 1.6;
}

.empty-text {
  color: var(--text-muted);
  font-size: 13px;
  font-style: italic;
}

.bonus-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.bonus-item {
  font-size: 13px;
  color: var(--text-primary);
  background: rgba(88, 166, 255, 0.06);
  border-left: 3px solid var(--accent-blue);
  padding: 6px 10px;
  border-radius: 0 4px 4px 0;
}

.stat-table {
  border-collapse: collapse;
  font-size: 13px;
  width: auto;
}

.stat-label {
  color: var(--text-muted);
  padding: 4px 16px 4px 0;
  white-space: nowrap;
  width: 140px;
}

.stat-value {
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
}

.used-by-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.used-by-link {
  font-size: 12px;
  color: var(--accent-blue);
  text-decoration: none;
  background: rgba(88, 166, 255, 0.08);
  border: 1px solid rgba(88, 166, 255, 0.2);
  border-radius: 3px;
  padding: 3px 8px;
  transition: background 0.15s, border-color 0.15s;
}

.used-by-link:hover {
  background: rgba(88, 166, 255, 0.15);
  border-color: rgba(88, 166, 255, 0.4);
}

/* Infobox */
.infobox {
  background: var(--bg-infobox, var(--bg-card));
  border: var(--border-default);
  border-radius: var(--card-radius);
  overflow: hidden;
}

.infobox-table {
  width: 100%;
  border-collapse: collapse;
}

.infobox-table tr:nth-child(odd) {
  background: rgba(255, 255, 255, 0.02);
}

.ib-label {
  color: var(--text-muted);
  font-size: 12px;
  padding: 6px 12px;
  white-space: nowrap;
}

.ib-value {
  color: var(--text-primary);
  font-size: 13px;
  text-align: right;
  padding: 6px 12px;
}

@media (max-width: 700px) {
  .gear-layout { flex-direction: column; }
  .side-col { width: 100%; position: static; }
}
</style>
