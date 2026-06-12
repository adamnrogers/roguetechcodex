<template>
  <div class="chassis-page-outer">

    <!-- ── Loading ─────────────────────────────────────────── -->
    <div v-if="isLoading" class="skeleton-wrap">
      <div class="skeleton skeleton-title"></div>
      <div class="skeleton skeleton-line"></div>
      <div class="skeleton skeleton-line short"></div>
    </div>

    <!-- ── Error ───────────────────────────────────────────── -->
    <div v-else-if="isError || !data" class="not-found">
      <p class="not-found-msg">Chassis not found.</p>
      <RouterLink :to="browsePath" class="back-link">← Back to {{ browseLabel }}</RouterLink>
    </div>

    <!-- ── Content ─────────────────────────────────────────── -->
    <template v-else>
      <div class="chassis-layout">

        <!-- ════════════════════════════════════════════════
             LEFT COLUMN
             ════════════════════════════════════════════════ -->
        <main class="main-col">

          <!-- Page header -->
          <header class="page-header">
            <nav class="breadcrumb">
              <button class="back-btn" @click="router.go(-1)">← Back</button>
              <span class="bc-sep">·</span>
              in:&nbsp;<RouterLink :to="browsePath" class="bc-link">{{ browseLabel }}</RouterLink>
              <span class="bc-sep"> / </span>
              <span class="bc-id">{{ data.ui_name }}</span>
            </nav>
            <h1 class="chassis-title">{{ data.ui_name }}</h1>
          </header>

          <!-- ── Description section ────────────────────── -->
          <section class="content-section">
            <div class="section-head">
              <h2 class="section-title">Description</h2>
            </div>
            <div
              v-if="selectedVariant?.details"
              class="lore-text"
              v-html="renderRichText(selectedVariant.details)"
            ></div>
            <p v-else class="empty-text">No description available.</p>
          </section>

          <!-- ── Bay section ───────────────────────────── -->
          <section class="content-section">
            <div class="section-head">
              <h2 class="section-title">{{ bayLabel }}</h2>
            </div>

            <!-- Affinity table -->
            <div class="subsection">
              <h3 class="subsection-title">Affinity</h3>
              <AffinityTable :affinities="selectedVariant?.affinities ?? []" />
            </div>

            <!-- Component layout table -->
            <div class="subsection">
              <h3 class="subsection-title">Component Layout</h3>
              <ComponentLayoutTable
                :variant-locations="selectedVariant?.locations ?? []"
                :loadout-locations="selectedVariant?.loadout_locations ?? []"
                :fixed-equipment="selectedVariant?.fixed_equipment ?? []"
                :inventory="selectedVariant?.inventory ?? []"
                :unit-type="data.unit_type"
              />
            </div>
          </section>

        </main>

        <!-- ════════════════════════════════════════════════
             RIGHT SIDEBAR
             ════════════════════════════════════════════════ -->
        <aside class="sidebar">

          <!-- Identity card -->
          <div class="identity-card">
            <div class="identity-header">{{ data.ui_name }}</div>
            <div class="identity-image">
              <img
                v-if="data.icon && !portraitImgError"
                :src="portraitUrl(data.icon)!"
                class="chassis-portrait"
                alt=""
                @error="portraitImgError = true"
              />
              <div v-else class="mech-image-placeholder">
                <span class="mech-silhouette">⬡</span>
              </div>
            </div>
            <table class="identity-table">
              <tbody>
                <tr v-if="selectedVariant?.variant_name">
                  <td class="id-label">Signature</td>
                  <td class="id-value">{{ selectedVariant.variant_name }}</td>
                </tr>
                <tr v-if="data.weight_class">
                  <td class="id-label">Class</td>
                  <td class="id-value">
                    <span class="wc-badge" :data-wc="data.weight_class">{{ data.weight_class }}</span>
                  </td>
                </tr>
                <tr v-if="data.tonnage != null">
                  <td class="id-label">Tonnage</td>
                  <td class="id-value">{{ data.tonnage }}&thinsp;t</td>
                </tr>
                <tr v-if="selectedVariant">
                  <td class="id-label">HardPoints</td>
                  <td class="id-value">
                    <span v-if="parsedHardpoints.length" class="hp-badges">
                      <span v-for="hp in parsedHardpoints" :key="hp.cat" class="hp-entry">
                        <span class="hp-count">{{ hp.count }}</span><span class="hp-badge" :style="{ background: hp.style.bg, color: hp.style.color }">{{ hp.cat }}</span>
                      </span>
                    </span>
                    <span v-else class="id-muted">—</span>
                  </td>
                </tr>
                <tr v-if="selectedVariant">
                  <td class="id-label">Total Health</td>
                  <td class="id-value">
                    <div>{{ selectedVariant.health_summary?.split(' S=')[0] }}</div>
                    <div v-if="selectedVariant.health_summary?.includes(' S=')">S={{ selectedVariant.health_summary.split(' S=')[1] }}</div>
                  </td>
                </tr>
                <tr v-if="selectedVariant?.source_mod">
                  <td class="id-label">RT Module</td>
                  <td class="id-value">{{ humanizeMod(selectedVariant.source_mod) }}</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- Compatible Variants -->
          <div class="sidebar-section">
            <div class="sidebar-section-header">Compatible Variants</div>
            <ul class="sidebar-list">
              <li v-for="variant in data.variants" :key="variant.id">
                <a
                  href="#"
                  class="sidebar-link"
                  :class="{ 'sidebar-link-active': variant.id === effectiveVariantId }"
                  @click.prevent="selectedVariantId = variant.id"
                >{{ variant.variant_name || variant.id }}</a>
              </li>
            </ul>
          </div>

          <!-- Factions -->
          <div class="sidebar-section">
            <div class="sidebar-section-header">Factions</div>
            <ul class="sidebar-list">
              <li v-for="faction in allFactions" :key="faction">
                <RouterLink
                  :to="{ path: browsePath, query: { faction } }"
                  class="sidebar-link"
                >{{ faction }}</RouterLink>
              </li>
              <li v-if="!allFactions.length" class="sidebar-empty">None</li>
            </ul>
          </div>

          <!-- Biome Restrictions -->
          <div v-if="biomeRestrictions.length" class="sidebar-section">
            <div class="sidebar-section-header">Biome Restrictions</div>
            <ul class="sidebar-list">
              <li v-for="biome in biomeRestrictions" :key="biome" class="sidebar-plain">
                {{ biome }}
              </li>
            </ul>
          </div>

        </aside>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useChassisDetail } from '../composables/useChassisDetail'
import { renderRichText } from '../utils/richText'
import { humanizeMod, canonicalizeFaction, humanizeBiomeTag } from '../utils/humanize'
import { portraitUrl } from '../utils/portrait'
import ComponentLayoutTable from '../components/ComponentLayoutTable.vue'
import AffinityTable from '../components/AffinityTable.vue'

const route = useRoute()
const router = useRouter()
const prefabBase    = computed(() => route.params.prefabBase as string)
const isVehicle     = computed(() => route.path.startsWith('/vehicles/'))
const isVtol        = computed(() => route.path.startsWith('/vtols/'))
const isBattleArmor = computed(() => route.path.startsWith('/battle-armor/'))

const { data, isLoading, isError } = useChassisDetail(
  prefabBase,
  computed(() => isVehicle.value || isVtol.value),
  isBattleArmor,
)

const browsePath  = computed(() =>
  isVtol.value ? '/vtols' : isVehicle.value ? '/vehicles' : isBattleArmor.value ? '/battle-armor' : '/mechs'
)
const browseLabel = computed(() =>
  isVtol.value ? 'VTOLs' : isVehicle.value ? 'Vehicles' : isBattleArmor.value ? 'Battle Armor' : 'Mechs'
)
const bayLabel = computed(() =>
  isVtol.value ? 'VTOL Bay' : isVehicle.value ? 'Vehicle Bay' : isBattleArmor.value ? 'Battle Armor Bay' : 'Mech Bay'
)

const portraitImgError = ref(false)

// Which variant's data is shown
const selectedVariantId = ref<string | null>(null)
const queryVariantId = route.query.variant as string | undefined
if (queryVariantId) selectedVariantId.value = queryVariantId
watch(selectedVariantId, () => { window.scrollTo(0, 0) })

// Reset variant selection and portrait error when navigating to a different chassis
watch(prefabBase, () => {
  portraitImgError.value = false
  selectedVariantId.value = (route.query.variant as string | undefined) ?? null
})

const effectiveVariantId = computed(() =>
  selectedVariantId.value ?? data.value?.variants[0]?.id ?? null
)

const selectedVariant = computed(() => {
  if (!data.value?.variants.length) return null
  return (
    data.value.variants.find(v => v.id === effectiveVariantId.value) ??
    data.value.variants[0]
  )
})

const allFactions = computed(() => {
  if (!data.value) return []
  const seen = new Map<string, string>() // canonical name → first canonical name (dedup)
  for (const v of data.value.variants) {
    for (const raw of v.faction_tags) {
      const canonical = canonicalizeFaction(raw)
      if (canonical !== null && !seen.has(canonical)) {
        seen.set(canonical, canonical)
      }
    }
  }
  return [...seen.keys()].sort()
})

const biomeRestrictions = computed(() => {
  if (!data.value) return []
  const seen = new Set<string>()
  const result: string[] = []
  for (const v of data.value.variants) {
    for (const tag of v.chassis_tags) {
      if (typeof tag === 'string' && tag.startsWith('NoBiome_') && !seen.has(tag)) {
        seen.add(tag)
        result.push(humanizeBiomeTag(tag))
      }
    }
  }
  return result.sort()
})

const HP_BADGE_STYLES: Record<string, { bg: string; color: string }> = {
  B:  { bg: 'rgba(88,166,255,0.2)',   color: '#58a6ff' },
  E:  { bg: 'rgba(63,185,80,0.2)',    color: '#3fb950' },
  M:  { bg: 'rgba(180,130,255,0.2)',  color: '#b482ff' },
  S:  { bg: 'rgba(240,136,62,0.2)',   color: '#f0883e' },
  WM: { bg: 'rgba(128,128,128,0.15)', color: '#8b96a3' },
  IB: { bg: 'rgba(248,81,73,0.15)',   color: '#f85149' },
  SH: { bg: 'rgba(56,189,193,0.15)',  color: '#38bdc1' },
  JJ: { bg: 'rgba(139,150,163,0.15)', color: '#8b96a3' },
}

const parsedHardpoints = computed(() => {
  const summary = selectedVariant.value?.hardpoints_summary
  if (!summary || summary === '—') return []
  return summary.split(' ').flatMap(token => {
    const m = token.match(/^(\d+)(.+)$/)
    if (!m) return []
    const [, count, cat] = m
    const style = HP_BADGE_STYLES[cat] ?? { bg: 'rgba(128,128,128,0.15)', color: '#8b96a3' }
    return [{ count, cat, style }]
  })
})
</script>

<style scoped>
/* ── Outer wrapper ─────────────────────────────────────────── */
.chassis-page-outer {
  min-height: 100vh;
}

/* ── Two-column grid ───────────────────────────────────────── */
.chassis-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 300px;
  gap: 28px;
  align-items: start;
  max-width: var(--content-max-width, 1300px);
  margin: 0 auto;
  padding: 24px 32px;
}

/* ── Left column ───────────────────────────────────────────── */
.main-col { min-width: 0; }

/* ── Page header ───────────────────────────────────────────── */
.page-header {
  margin-bottom: 20px;
}

.chassis-portrait {
  width: 72px;
  height: 72px;
  object-fit: contain;
  display: block;
  margin: 0 auto;
}

.breadcrumb {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 8px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 2px;
}

.back-btn {
  background: none;
  border: none;
  color: var(--accent-blue);
  font-size: 12px;
  cursor: pointer;
  padding: 0;
  font-family: inherit;
}
.back-btn:hover { text-decoration: underline; }

.bc-link { color: var(--accent-blue); text-decoration: none; }
.bc-link:hover { text-decoration: underline; }
.bc-sep { color: var(--text-muted); padding: 0 2px; }
.bc-id  { color: var(--text-muted); font-family: monospace; font-size: 11px; }

.chassis-title {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.2;
}

/* ── Content sections ──────────────────────────────────────── */
.content-section { margin-bottom: 28px; }

.section-head {
  display: flex;
  align-items: center;
  gap: 8px;
  border-bottom: 1px solid rgba(88, 166, 255, 0.2);
  padding-bottom: 8px;
  margin-bottom: 14px;
}

.section-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.subsection { margin-bottom: 20px; }

.subsection-title {
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted);
  margin: 0 0 8px;
}

/* ── Description ───────────────────────────────────────────── */
.lore-text {
  font-size: 13px;
  line-height: 1.7;
  color: var(--text-primary);
  margin-bottom: 12px;
}

.empty-text {
  color: var(--text-muted);
  font-size: 13px;
  font-style: italic;
  margin: 0;
}

/* ── Variant selector ──────────────────────────────────────── */
.variant-selector {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.vs-label { font-size: 12px; color: var(--text-muted); }

.vs-select {
  background: var(--bg-card);
  border: 1px solid rgba(88, 166, 255, 0.3);
  color: var(--text-primary);
  font-size: 12px;
  padding: 3px 8px;
  border-radius: 4px;
  cursor: pointer;
}
.vs-select:focus { outline: none; border-color: var(--accent-blue); }

/* ── Right sidebar ─────────────────────────────────────────── */
.sidebar {
  position: sticky;
  top: 72px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

/* Identity card */
.identity-card {
  background: var(--bg-infobox);
  border: var(--border-default);
  border-radius: var(--card-radius);
  overflow: hidden;
}

.identity-header {
  background: rgba(88, 166, 255, 0.1);
  border-bottom: var(--border-default);
  font-size: 14px;
  font-weight: 700;
  color: var(--text-primary);
  padding: 10px 14px;
  text-align: center;
}

.identity-image {
  padding: 12px 0 8px;
  text-align: center;
}

.mech-image-placeholder {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 72px;
  height: 72px;
  background: rgba(88, 166, 255, 0.06);
  border: 1px dashed rgba(88, 166, 255, 0.2);
  border-radius: 4px;
}

.mech-silhouette {
  font-size: 32px;
  color: rgba(88, 166, 255, 0.3);
}

.identity-table { width: 100%; border-collapse: collapse; }

.identity-table td {
  padding: 5px 12px;
  font-size: 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.03);
}

.id-label {
  color: var(--text-muted);
  text-align: right;
  white-space: nowrap;
  width: 50%;
}

.id-value { color: var(--text-primary); text-align: left; }

.wc-badge {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  padding: 2px 6px;
  border-radius: var(--badge-radius, 4px);
  letter-spacing: 0.3px;
}
.wc-badge[data-wc="LIGHT"]   { background: var(--badge-light-bg);   color: var(--badge-light-fg); }
.wc-badge[data-wc="MEDIUM"]  { background: var(--badge-medium-bg);  color: var(--badge-medium-fg); }
.wc-badge[data-wc="HEAVY"]   { background: var(--badge-heavy-bg);   color: var(--badge-heavy-fg); }
.wc-badge[data-wc="ASSAULT"] { background: var(--badge-assault-bg); color: var(--badge-assault-fg); }

/* Sidebar hardpoint badges */
.hp-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  align-items: center;
}
.hp-entry {
  display: inline-flex;
  align-items: center;
  gap: 2px;
}
.hp-count {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-primary);
}
.hp-badge {
  font-size: 10px;
  font-weight: 700;
  padding: 1px 5px;
  border-radius: 3px;
  letter-spacing: 0.2px;
}
.id-muted { color: var(--text-muted); }

/* Sidebar sections */
.sidebar-section {
  background: var(--bg-infobox);
  border: var(--border-default);
  border-radius: var(--card-radius);
  overflow: hidden;
}

.sidebar-section-header {
  background: rgba(88, 166, 255, 0.06);
  border-bottom: var(--border-default);
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--text-muted);
  padding: 7px 12px;
}

.sidebar-list {
  list-style: disc;
  padding: 8px 12px 8px 26px;
  margin: 0;
}

.sidebar-list li { margin-bottom: 4px; }

.sidebar-link {
  color: var(--accent-blue);
  font-size: 12px;
  text-decoration: none;
  transition: color 0.12s;
}
.sidebar-link:hover { text-decoration: underline; }
.sidebar-link-active { color: var(--accent-orange); font-weight: 600; }

.sidebar-empty {
  font-size: 12px;
  color: var(--text-muted);
  font-style: italic;
  list-style: none;
  margin-left: -14px;
  padding: 4px 0;
}

.sidebar-plain {
  font-size: 12px;
  color: var(--text-primary);
}

/* ── Loading skeleton ──────────────────────────────────────── */
.skeleton-wrap {
  padding: 32px;
  max-width: var(--content-max-width, 1300px);
  margin: 0 auto;
}

.skeleton {
  background: rgba(255, 255, 255, 0.06);
  border-radius: 6px;
  margin-bottom: 12px;
  animation: pulse 1.4s ease-in-out infinite;
}
.skeleton-title { height: 32px; width: 280px; max-width: 100%; }
.skeleton-line  { height: 14px; width: 100%; }
.skeleton-line.short { width: 55%; }

@keyframes pulse {
  0%, 100% { opacity: 0.4; }
  50%       { opacity: 0.9; }
}

/* ── Not found ─────────────────────────────────────────────── */
.not-found { padding: 60px 32px; text-align: center; }
.not-found-msg { color: var(--text-muted); font-size: 15px; margin-bottom: 12px; }
.back-link { color: var(--accent-blue); font-size: 14px; text-decoration: none; }
.back-link:hover { text-decoration: underline; }
</style>
