<template>
  <div class="ss-page-outer">
    <div v-if="isLoading" class="skeleton-wrap">
      <div class="skeleton skeleton-title"></div>
      <div class="skeleton skeleton-line"></div>
      <div class="skeleton skeleton-line short"></div>
    </div>

    <div v-else-if="isError || !data" class="not-found">
      <p class="not-found-msg">Star system not found.</p>
      <RouterLink to="/star-systems" class="back-link">← Back to Star Systems</RouterLink>
    </div>

    <template v-else>
      <div class="ss-layout">
        <main class="main-col">
          <header class="page-header">
            <nav class="breadcrumb">
              in:&nbsp;<RouterLink to="/star-systems" class="bc-link">Star Systems</RouterLink>
              <span class="bc-sep"> / </span>
              <span class="bc-id">{{ data.ui_name }}</span>
            </nav>
            <h1 class="ss-title">{{ data.ui_name }}</h1>
            <div class="ss-badges">
              <span v-if="data.difficulty != null" class="diff-badge" :data-band="difficultyBand">
                Difficulty {{ data.difficulty }}
              </span>
              <span v-if="data.population" class="pop-badge"
                >{{ humanizeTag(data.population) }} Pop</span
              >
            </div>
          </header>

          <section class="content-section">
            <h2 class="section-title">Description</h2>
            <div v-if="data.details" class="lore-text" v-html="renderRichText(data.details)"></div>
            <p v-else class="empty-text">No description available.</p>
          </section>

          <section v-if="data.biomes.length" class="content-section">
            <h2 class="section-title">Biomes</h2>
            <div class="chip-row">
              <span v-for="b in data.biomes" :key="b" class="biome-chip">{{ humanizeTag(b) }}</span>
            </div>
          </section>

          <section v-if="data.tags.length" class="content-section">
            <h2 class="section-title collapsible" @click="tagsOpen = !tagsOpen">
              All Tags ({{ data.tags.length }})
              <span class="collapse-chevron" :class="{ open: tagsOpen }">›</span>
            </h2>
            <div v-if="tagsOpen" class="chip-row">
              <span v-for="t in data.tags" :key="t" class="tag-chip">{{ humanizeTag(t) }}</span>
            </div>
          </section>
        </main>

        <aside class="side-col">
          <div class="infobox">
            <table class="infobox-table">
              <tbody>
                <tr v-if="data.star_type">
                  <td class="ib-label">Star Type</td>
                  <td class="ib-value">{{ data.star_type }}</td>
                </tr>
                <tr v-if="data.owner_id">
                  <td class="ib-label">Owner</td>
                  <td class="ib-value">{{ humanizeTag(data.owner_id) }}</td>
                </tr>
                <tr v-if="data.jump_distance != null">
                  <td class="ib-label">Jump Distance</td>
                  <td class="ib-value">{{ data.jump_distance }}</td>
                </tr>
                <tr>
                  <td class="ib-label">Fueling Station</td>
                  <td class="ib-value" :class="data.fueling_station ? 'ib-yes' : 'ib-no'">
                    {{ data.fueling_station ? 'Yes' : 'No' }}
                  </td>
                </tr>
                <tr v-if="data.size">
                  <td class="ib-label">Size</td>
                  <td class="ib-value">{{ humanizeTag(data.size) }}</td>
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
import { useStarSystemDetail } from '../composables/useStarSystemList'
import { renderRichText } from '../utils/richText'
import { humanizeMod, humanizeTag } from '../utils/humanize'

const route = useRoute()
const systemId = computed(() => route.params.systemId as string)

const { data, isLoading, isError } = useStarSystemDetail(systemId)

const tagsOpen = ref(false)

const difficultyBand = computed(() => {
  const d = data.value?.difficulty
  if (d == null) return 'mid'
  if (d <= 5) return 'low'
  if (d <= 12) return 'mid'
  return 'high'
})
</script>

<style scoped>
.ss-page-outer {
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
.skeleton-title {
  height: 32px;
  width: 40%;
}
.skeleton-line {
  height: 16px;
  width: 80%;
}
.skeleton-line.short {
  width: 50%;
}
@keyframes pulse {
  0%,
  100% {
    opacity: 1;
  }
  50% {
    opacity: 0.4;
  }
}

.not-found {
  padding: 48px;
  text-align: center;
}
.not-found-msg {
  color: var(--text-muted);
  font-size: 16px;
}
.back-link {
  color: var(--accent-blue);
  text-decoration: none;
  font-size: 14px;
}
.back-link:hover {
  text-decoration: underline;
}

.ss-layout {
  display: flex;
  gap: 32px;
  align-items: flex-start;
}

.main-col {
  flex: 1;
  min-width: 0;
}

.side-col {
  width: 260px;
  flex-shrink: 0;
  position: sticky;
  top: calc(var(--nav-height) + 16px);
}

.page-header {
  margin-bottom: 24px;
}

.breadcrumb {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 8px;
}
.bc-link {
  color: var(--accent-blue);
  text-decoration: none;
}
.bc-link:hover {
  text-decoration: underline;
}
.bc-sep {
  color: var(--text-muted);
}
.bc-id {
  color: var(--text-muted);
}

.ss-title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 10px;
}

.ss-badges {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.diff-badge,
.pop-badge {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  padding: 3px 10px;
  border-radius: var(--badge-radius, 3px);
  letter-spacing: 0.3px;
}

.diff-badge[data-band='low'] {
  background: rgba(63, 185, 80, 0.15);
  color: #3fb950;
}
.diff-badge[data-band='mid'] {
  background: rgba(210, 153, 34, 0.15);
  color: #d29922;
}
.diff-badge[data-band='high'] {
  background: rgba(255, 80, 80, 0.15);
  color: #ff5555;
}
.pop-badge {
  background: rgba(88, 166, 255, 0.15);
  color: #58a6ff;
}

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
.section-title.collapsible:hover {
  color: var(--accent-blue);
}
.collapse-chevron {
  font-size: 14px;
  color: var(--text-muted);
  transform: rotate(0deg);
  transition: transform 0.15s;
  line-height: 1;
  margin-left: auto;
}
.collapse-chevron.open {
  transform: rotate(90deg);
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

.chip-row {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.biome-chip,
.tag-chip {
  font-size: 11px;
  color: var(--text-primary);
  background: rgba(128, 128, 128, 0.1);
  border-radius: 3px;
  padding: 3px 8px;
}

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
.ib-yes {
  color: #50c878;
}
.ib-no {
  color: var(--text-muted);
}

@media (max-width: 700px) {
  .ss-layout {
    flex-direction: column;
  }
  .side-col {
    width: 100%;
    position: static;
  }
}
</style>
