<template>
  <RouterLink :to="cardLink" class="mech-card-link">
    <div class="mech-card">
      <div class="card-body">
        <img
          v-if="portraitSrc"
          :src="portraitSrc"
          class="mech-portrait"
          alt=""
          @error="portraitError = true"
        />
        <div class="card-text">
          <div class="mech-name">{{ ui_name }}</div>
          <div class="mech-meta">
            <span v-if="weight_class" class="wc-badge" :data-wc="weight_class">{{ weight_class }}</span>
            <span v-if="tonnage != null" class="mech-tonnage">{{ tonnage }}t</span>
          </div>
          <div class="mech-type">{{ unitTypeLabel }}</div>
        </div>
      </div>
      <div class="mech-footer">
        <span class="mech-vars">{{ variant_count }} variants</span>
      </div>
    </div>
  </RouterLink>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { portraitUrl } from '../utils/portrait'

interface MechCardProps {
  prefab_base: string
  ui_name: string
  unit_type: string
  weight_class: string | null
  tonnage: number | null
  variant_count: number
  icon: string | null
}

const props = defineProps<MechCardProps>()

const portraitError = ref(false)
watch(() => props.icon, () => { portraitError.value = false })
const portraitSrc = computed(() =>
  portraitError.value ? null : portraitUrl(props.icon)
)

const cardLink = computed(() => {
  if (props.unit_type === 'vtol') return `/vtols/${props.prefab_base}`
  if (props.unit_type === 'vehicle') return `/vehicles/${props.prefab_base}`
  return `/mechs/${props.prefab_base}`
})

const unitTypeLabel = computed(() => {
  const labels: Record<string, string> = {
    mech: 'BattleMech',
    battle_armor: 'Battle Armor',
    vehicle: 'Combat Vehicle',
    vtol: 'VTOL',
  }
  return labels[props.unit_type] ?? props.unit_type
})
</script>

<style scoped>
.mech-card-link {
  text-decoration: none !important;
  display: block;
  color: inherit;
  height: 100%;
}
.mech-card {
  background: var(--bg-card);
  border: var(--border-default);
  border-radius: var(--card-radius);
  padding: 14px;
  box-shadow: var(--card-shadow);
  transition: border-color 0.15s, background 0.15s, box-shadow 0.15s;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 0;
}
.mech-card:hover {
  border-color: var(--accent-blue);
  background: var(--bg-card-hover);
  box-shadow: var(--card-shadow-hover);
}
.card-body {
  display: flex;
  gap: 10px;
  align-items: flex-start;
  flex: 1;
}
.mech-portrait {
  width: 64px;
  height: 64px;
  object-fit: contain;
  flex-shrink: 0;
  border-radius: 4px;
  background: rgba(255,255,255,0.04);
}
.card-text {
  flex: 1;
  min-width: 0;
}
.mech-name {
  color: var(--text-primary);
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.mech-meta {
  display: flex;
  align-items: center;
  gap: 8px;
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
.mech-tonnage {
  font-size: 12px;
  color: var(--text-muted);
}
.mech-type {
  color: var(--text-muted);
  font-size: 12px;
  margin-top: 5px;
}
.mech-footer {
  display: flex;
  justify-content: flex-end;
  margin-top: 10px;
  padding-top: 8px;
  border-top: 1px solid rgba(128, 128, 128, 0.12);
}
.mech-vars {
  color: var(--text-muted);
  font-size: 11px;
}
</style>
