<template>
  <RouterLink :to="cardLink" class="gear-card-link">
    <div class="gear-card">
      <div class="gear-name">{{ ui_name }}</div>
      <div v-if="qualifier" class="gear-qualifier">{{ qualifier }}</div>
      <div class="gear-badges">
        <span v-if="mode !== 'weapon'" class="ct-badge" :data-ct="badgeKey">{{ badgeLabel }}</span>
        <span v-if="weapon_category && mode !== 'quirk'" class="wcat-badge" :data-wcat="weapon_category">
          {{ weapon_category }}
        </span>
      </div>
      <div class="gear-stats">
        <!-- Weapon mode: show damage + heat -->
        <template v-if="mode === 'weapon'">
          <span v-if="damage != null" class="stat-item">{{ damage }} dmg</span>
          <span v-if="heat_generated != null" class="stat-item">{{ heat_generated }} heat</span>
          <span v-if="tonnage != null" class="stat-item">{{ tonnage }}t</span>
        </template>
        <!-- Equipment/quirk mode: show tonnage + slots -->
        <template v-else>
          <span v-if="tonnage != null" class="stat-item">{{ tonnage }}t</span>
          <span v-if="slots != null" class="stat-item">{{ slots }} slots</span>
        </template>
      </div>
    </div>
  </RouterLink>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import type { GearSummary } from '../composables/useGearList'
import { gearQualifier } from '../utils/humanize'

const props = defineProps<GearSummary & { mode: string }>()

const cardLink = computed(() => {
  const base = props.mode === 'weapon' ? '/weapons'
             : props.mode === 'quirk'  ? '/quirks'
             : '/equipment'
  return `${base}/${props.id}`
})

const CT_LABELS: Record<string, string> = {
  Upgrade: 'Upgrade',
  Weapon: 'Weapon',
  HeatSink: 'Heat Sink',
  AmmunitionBox: 'Ammo',
  JumpJet: 'Jump Jet',
}

const badgeLabel = computed(() => {
  if (props.mode === 'quirk') return 'Quirk'
  return props.component_type ? (CT_LABELS[props.component_type] ?? props.component_type) : ''
})

const qualifier = computed(() => gearQualifier(props.id, props.ui_name))

const badgeKey = computed(() => {
  if (props.mode === 'quirk') return 'Quirk'
  return props.component_type ?? ''
})

</script>

<style scoped>
.gear-card-link {
  text-decoration: none !important;
  display: block;
  color: inherit;
  height: 100%;
}

.gear-card {
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

.gear-card:hover {
  border-color: var(--accent-blue);
  background: var(--bg-card-hover);
  box-shadow: var(--card-shadow-hover);
}

.gear-name {
  color: var(--text-primary);
  font-size: 14px;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.gear-qualifier {
  font-size: 11px;
  color: var(--text-muted);
  margin-top: -2px;
}

.gear-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.ct-badge,
.wcat-badge {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  padding: 2px 7px;
  border-radius: var(--badge-radius, 3px);
  letter-spacing: 0.3px;
}

.ct-badge[data-ct="Upgrade"]       { background: rgba(88, 166, 255, 0.15); color: #58a6ff; }
.ct-badge[data-ct="Weapon"]        { background: rgba(255, 80,  80,  0.15); color: #ff5555; }
.ct-badge[data-ct="HeatSink"]      { background: rgba(255, 140, 0,   0.15); color: #ff8c00; }
.ct-badge[data-ct="AmmunitionBox"] { background: rgba(80,  200, 120, 0.15); color: #50c878; }
.ct-badge[data-ct="JumpJet"]       { background: rgba(180, 100, 255, 0.15); color: #b464ff; }
.ct-badge[data-ct="Quirk"]         { background: rgba(210, 153, 34,  0.15); color: #d29922; }

.wcat-badge[data-wcat="Ballistic"] { background: rgba(88,  166, 255, 0.15); color: #58a6ff; }
.wcat-badge[data-wcat="Energy"]    { background: rgba(63,  185, 80,  0.15); color: #3fb950; }
.wcat-badge[data-wcat="Missile"]   { background: rgba(180, 130, 255, 0.15); color: #b482ff; }
.wcat-badge[data-wcat="Melee"]     { background: rgba(255, 80,  80,  0.15); color: #ff5555; }
.wcat-badge[data-wcat="Support"]   { background: rgba(180, 100, 255, 0.15); color: #b464ff; }

.gear-stats {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  margin-top: auto;
}

.stat-item {
  font-size: 11px;
  color: var(--text-muted);
}
</style>
