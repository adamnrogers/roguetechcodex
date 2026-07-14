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

    <div v-else-if="isClassified" class="classified-page">
      <div class="classified-header">
        <span class="classified-warning">Warning</span>
        <span class="classified-subtitle">You are attempting to access classified information</span>
      </div>
      <div class="classified-body">
        <img src="/classified.png" alt="CLASSIFIED" class="classified-img" />
        <div class="classified-text">
          <p>This item or unit has been marked as restricted (not directly for player use) or spoiler by the Developers.</p>
          <p>If you feel this was done in error, open a ticket on <a href="https://discord.gg/93kxWQZ" target="_blank" rel="noopener" class="classified-link">Discuss</a>.</p>
        </div>
      </div>
    </div>

    <template v-else>
      <div class="gear-layout" ref="captureTarget">
        <main class="main-col">
          <header class="page-header">
            <nav class="breadcrumb">
              in:&nbsp;<RouterLink :to="browsePath" class="bc-link">{{ browseLabel }}</RouterLink>
              <span class="bc-sep"> / </span>
              <span class="bc-id">{{ data.ui_name }}</span>
            </nav>
            <h1 class="gear-title">{{ data.ui_name }}</h1>
            <div v-if="qualifier" class="gear-qualifier">{{ qualifier }}</div>
            <div class="gear-badges">
              <span v-if="componentTypeLabel" class="ct-badge" :data-ct="componentTypeBadgeKey">
                {{ componentTypeLabel }}
              </span>
              <span v-if="data.weapon_category" class="wcat-badge" :data-wcat="data.weapon_category">
                {{ data.weapon_category }}
              </span>
            </div>
            <button
              class="export-btn"
              data-export-exclude
              :disabled="isExporting"
              @click="handleExport"
            >
              {{ isExporting ? 'Generating…' : 'Export as Image' }}
            </button>
            <p v-if="exportError" class="export-error" data-export-exclude>{{ exportError }}</p>
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

          <!-- Traits (resolved BonusDescriptions) -->
          <section v-if="data.bonus_descriptions?.length" class="content-section">
            <h2 class="section-title">Traits</h2>
            <ul class="trait-list">
              <li v-for="(trait, i) in data.bonus_descriptions" :key="i" class="trait-item">
                {{ trait }}
              </li>
            </ul>
          </section>

          <!-- Weapon stats (weapons only) -->
          <section v-if="data.weapon_category" class="content-section">
            <h2 class="section-title">Weapon Stats</h2>
            <WeaponStatsTable v-if="data.modes?.length" :modes="(data.modes as any)" />
            <table v-else class="stat-table">
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
            <h2 class="section-title collapsible" @click="mechsOpen = !mechsOpen">
              Used by Mechs ({{ data.used_by_mechs.length }})
              <span class="collapse-chevron" :class="{ open: mechsOpen }">›</span>
            </h2>
            <div v-if="mechsOpen" class="used-by-grid">
              <RouterLink
                v-for="m in data.used_by_mechs"
                :key="m.variant_id"
                :to="`/mechs/${m.prefab_base}?variant=${m.variant_id}`"
                class="used-by-link"
              >{{ m.ui_name }} {{ m.variant_name }}</RouterLink>
            </div>
          </section>

          <!-- Used by vehicles -->
          <section v-if="data.used_by_vehicles.length" class="content-section">
            <h2 class="section-title collapsible" @click="vehiclesOpen = !vehiclesOpen">
              Used by Vehicles ({{ data.used_by_vehicles.length }})
              <span class="collapse-chevron" :class="{ open: vehiclesOpen }">›</span>
            </h2>
            <div v-if="vehiclesOpen" class="used-by-grid">
              <RouterLink
                v-for="v in data.used_by_vehicles"
                :key="v.variant_id"
                :to="`/${v.unit_type === 'vtol' ? 'vtols' : 'vehicles'}/${v.prefab_base}?variant=${v.variant_id}`"
                class="used-by-link"
              >{{ v.ui_name }} {{ v.variant_name }}</RouterLink>
            </div>
          </section>
        </main>

        <!-- Right infobox -->
        <aside class="side-col">
          <div class="infobox">
            <table class="infobox-table">
              <tbody>
                <tr v-if="data.tonnage != null">
                  <td class="ib-label">Weight</td>
                  <td class="ib-value">{{ data.tonnage }}t</td>
                </tr>
                <tr v-if="data.slots != null">
                  <td class="ib-label">Slots</td>
                  <td class="ib-value">{{ data.slots }}</td>
                </tr>
                <tr v-if="data.allowed_locations">
                  <td class="ib-label">Locations</td>
                  <td class="ib-value">{{ data.allowed_locations }}</td>
                </tr>
                <tr v-if="data.cost != null">
                  <td class="ib-label">Value</td>
                  <td class="ib-value">{{ data.cost.toLocaleString() }} ¢</td>
                </tr>
                <tr v-if="data.weapon_category">
                  <td class="ib-label">Salvage</td>
                  <td class="ib-value" :class="data.purchasable ? 'ib-yes' : 'ib-no'">
                    {{ data.purchasable ? 'Yes' : 'No' }}
                  </td>
                </tr>
                <tr v-if="data.manufacturer">
                  <td class="ib-label">Manufacturer</td>
                  <td class="ib-value">{{ data.manufacturer }}</td>
                </tr>
                <tr v-if="data.weapon_category">
                  <td class="ib-label">Weapon</td>
                  <td class="ib-value">{{ data.weapon_category }}</td>
                </tr>
                <tr v-if="data.weapon_type">
                  <td class="ib-label">Type</td>
                  <td class="ib-value">{{ data.weapon_type }}</td>
                </tr>
                <tr v-if="data.weapon_subtype">
                  <td class="ib-label">SubType</td>
                  <td class="ib-value">{{ data.weapon_subtype }}</td>
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
import { computed, ref } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { useGearDetail } from '../composables/useGearList'
import { useExportImage } from '../composables/useExportImage'
import { renderRichText } from '../utils/richText'
import { humanizeMod, gearQualifier } from '../utils/humanize'
import AffinityTable from '../components/AffinityTable.vue'
import WeaponStatsTable from '../components/WeaponStatsTable.vue'

const route = useRoute()
const gearId = computed(() => route.params.gearId as string)

const { data, isLoading, isError } = useGearDetail(gearId)

const hideBlacklisted = import.meta.env.VITE_HIDE_BLACKLISTED === 'true'
const isClassified = computed(() =>
  hideBlacklisted && !!data.value?.component_tags.includes('BLACKLISTED')
)

// Infer browse mode from current URL prefix
const browsePath = computed(() => {
  if (route.path.startsWith('/weapons')) return '/weapons'
  if (route.path.startsWith('/quirks'))  return '/quirks'
  return '/equipment'
})
const browseLabel = computed(() => {
  if (route.path.startsWith('/weapons')) return 'Weapons'
  if (route.path.startsWith('/quirks'))  return 'Quirks'
  return 'Equipment'
})

const qualifier = computed(() => data.value ? gearQualifier(data.value.id, data.value.ui_name) : null)

const mechsOpen = ref(false)
const vehiclesOpen = ref(false)

const captureTarget = ref<HTMLElement | null>(null)
const { isExporting, exportError, exportAsImage } = useExportImage()
function handleExport() {
  if (!captureTarget.value || !data.value) return
  const slug = data.value.ui_name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '')
  exportAsImage(captureTarget.value, `${slug}.png`)
}

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

.classified-page {
  max-width: 700px;
  margin: 48px auto;
  padding: 0 16px;
}

.classified-header {
  border: 1px solid rgba(200, 50, 50, 0.4);
  background: rgba(200, 50, 50, 0.08);
  border-radius: 4px;
  padding: 12px 20px;
  margin-bottom: 24px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.classified-warning {
  font-size: 18px;
  font-weight: 700;
  color: #e05050;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.classified-subtitle {
  font-size: 14px;
  color: var(--text-muted);
}

.classified-body {
  display: flex;
  gap: 28px;
  align-items: flex-start;
}

.classified-img {
  width: 260px;
  flex-shrink: 0;
  border-radius: 4px;
}

.classified-text {
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.6;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.classified-link {
  color: var(--accent-blue);
  text-decoration: none;
}
.classified-link:hover { text-decoration: underline; }

@media (max-width: 600px) {
  .classified-body { flex-direction: column; }
  .classified-img { width: 100%; }
}

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

.export-btn {
  background: none;
  border: 1px solid var(--accent-blue);
  color: var(--accent-blue);
  font-size: 12px;
  cursor: pointer;
  padding: 4px 10px;
  border-radius: 4px;
  font-family: inherit;
  margin-top: 8px;
}
.export-btn:hover:not(:disabled) { background: var(--accent-blue); color: var(--bg-card); }
.export-btn:disabled { opacity: 0.6; cursor: default; }

.export-error {
  font-size: 12px;
  color: var(--accent-red, #f85149);
  margin-top: 4px;
}

.gear-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 10px;
}

.gear-qualifier {
  font-size: 13px;
  color: var(--text-muted);
  margin-bottom: 8px;
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

.section-title.collapsible {
  cursor: pointer;
  user-select: none;
  display: flex;
  align-items: center;
  gap: 6px;
}
.section-title.collapsible:hover { color: var(--accent-blue); }
.collapse-chevron {
  font-size: 14px;
  color: var(--text-muted);
  transform: rotate(0deg);
  transition: transform 0.15s;
  line-height: 1;
  margin-left: auto;
}
.collapse-chevron.open { transform: rotate(90deg); }

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

.trait-list {
  list-style: disc;
  padding-left: 20px;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.trait-item {
  font-size: 13px;
  color: var(--text-primary);
  line-height: 1.5;
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
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 6px;
}

.used-by-link {
  font-size: 12px;
  color: #8ab4f8;
  text-decoration: none;
  background: rgba(88, 166, 255, 0.08);
  border: 1px solid rgba(88, 166, 255, 0.2);
  border-radius: 3px;
  padding: 3px 8px;
  transition: background 0.15s, border-color 0.15s;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.used-by-link:hover {
  background: rgba(88, 166, 255, 0.18);
  border-color: rgba(88, 166, 255, 0.5);
  color: #c0d8ff;
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

.ib-yes { color: #50c878; }
.ib-no  { color: var(--text-muted); }

@media (max-width: 700px) {
  .gear-layout { flex-direction: column; }
  .side-col { width: 100%; position: static; }
}
</style>
