<template>
  <RouterLink :to="`/star-systems/${id}`" :class="['ss-card-link', list && 'ss-card-link--list']">
    <div :class="['ss-card', list && 'ss-card--list']">
      <div class="ss-name">{{ ui_name }}</div>
      <div class="ss-badges">
        <span v-if="difficulty != null" class="diff-badge" :data-band="difficultyBand">
          Difficulty {{ difficulty }}
        </span>
        <span v-if="population" class="pop-badge">{{ humanizeTag(population) }} Pop</span>
      </div>
      <div class="ss-biomes">
        <span v-for="b in visibleBiomes" :key="b" class="biome-chip">{{ humanizeTag(b) }}</span>
        <span v-if="overflowCount > 0" class="biome-chip biome-chip--overflow">+{{ overflowCount }}</span>
      </div>
    </div>
  </RouterLink>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import type { StarSystemSummary } from '../composables/useStarSystemList'
import { humanizeTag } from '../utils/humanize'

const props = defineProps<StarSystemSummary & { list?: boolean }>()

const difficultyBand = computed(() => {
  if (props.difficulty == null) return 'mid'
  if (props.difficulty <= 5) return 'low'
  if (props.difficulty <= 12) return 'mid'
  return 'high'
})

const MAX_VISIBLE_BIOMES = 3
const visibleBiomes = computed(() => props.biomes.slice(0, MAX_VISIBLE_BIOMES))
const overflowCount = computed(() => Math.max(0, props.biomes.length - MAX_VISIBLE_BIOMES))
</script>

<style scoped>
.ss-card-link {
  text-decoration: none !important;
  display: block;
  color: inherit;
  height: 100%;
}

.ss-card {
  background: var(--bg-card);
  border: var(--border-default);
  border-radius: var(--card-radius);
  padding: 14px;
  box-shadow: var(--card-shadow);
  transition: border-color 0.15s, background 0.15s, box-shadow 0.15s;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.ss-card:hover {
  border-color: var(--accent-blue);
  background: var(--bg-card-hover);
  box-shadow: var(--card-shadow-hover);
}

.ss-name {
  color: var(--text-primary);
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.ss-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.diff-badge,
.pop-badge {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  padding: 2px 7px;
  border-radius: var(--badge-radius, 3px);
  letter-spacing: 0.3px;
}

.diff-badge[data-band="low"]  { background: rgba(63,  185, 80,  0.15); color: #3fb950; }
.diff-badge[data-band="mid"]  { background: rgba(210, 153, 34,  0.15); color: #d29922; }
.diff-badge[data-band="high"] { background: rgba(255, 80,  80,  0.15); color: #ff5555; }

.pop-badge { background: rgba(88, 166, 255, 0.15); color: #58a6ff; }

.ss-biomes {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
  margin-top: auto;
}

.biome-chip {
  font-size: 10px;
  color: var(--text-muted);
  background: rgba(128, 128, 128, 0.1);
  border-radius: 3px;
  padding: 2px 6px;
}

.biome-chip--overflow {
  color: var(--text-muted);
  font-style: italic;
}

.ss-card-link--list { height: auto; }
.ss-card--list {
  padding: 6px 14px;
  height: auto;
  flex-direction: row;
  align-items: center;
  gap: 10px;
}
.ss-card--list .ss-name { flex: 1; min-width: 0; font-size: 13px; }
.ss-card--list .ss-badges { flex-shrink: 0; }
.ss-card--list .ss-biomes { flex-shrink: 0; margin-top: 0; }
</style>
