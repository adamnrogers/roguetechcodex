<template>
  <div class="rp-card">
    <div class="rp-header">
      <div class="rp-name">{{ pilot.callsign ? `"${pilot.callsign}"` : pilot.ui_name }}</div>
      <div v-if="pilot.callsign" class="rp-callsign">{{ pilot.ui_name }}</div>
      <div v-if="metaLine" class="rp-meta">{{ metaLine }}</div>
    </div>

    <div v-if="canPilotLabels.length" class="rp-cp-badges">
      <span v-for="cp in canPilotLabels" :key="cp.tag" class="cp-badge" :data-cp="cp.tag">{{
        cp.label
      }}</span>
    </div>

    <div v-if="pilot.details" class="rp-bio">
      <p class="rp-bio-text">{{ bioExpanded ? pilot.details : truncatedBio }}</p>
      <button v-if="bioTruncatable" class="bio-toggle" @click="bioExpanded = !bioExpanded">
        {{ bioExpanded ? 'Show less' : 'Show more' }}
      </button>
    </div>

    <div v-if="pilot.tags.length" class="rp-quirks">
      <div v-for="t in pilot.tags" :key="t.tag" class="quirk-entry">
        <div class="quirk-name">{{ t.label ?? humanizeTag(t.tag.replace(/^pilot_/, '')) }}</div>
        <div v-if="t.description" class="quirk-desc">{{ t.description }}</div>
      </div>
    </div>

    <div v-if="pilot.requirements" class="rp-requirements">
      <div v-if="pilot.requirements.hiring_requirements.length" class="req-group">
        <div class="req-label">Hiring Requirements</div>
        <div class="req-chips">
          <span
            v-for="(r, i) in pilot.requirements.hiring_requirements"
            :key="i"
            class="req-chip"
            >{{ r }}</span
          >
        </div>
      </div>

      <div v-if="pilot.requirements.hiring_visibility_requirements.length" class="req-group">
        <div class="req-label">Visibility Requirements</div>
        <div class="req-chips">
          <span
            v-for="(r, i) in pilot.requirements.hiring_visibility_requirements"
            :key="i"
            class="req-chip"
            >{{ r }}</span
          >
        </div>
      </div>

      <div v-if="pilot.requirements.required_system_owner.length" class="req-group">
        <div class="req-label">Required System Owner</div>
        <div class="req-chips">
          <span v-for="f in pilot.requirements.required_system_owner" :key="f" class="req-chip">{{
            canonicalizeFaction(f) ?? f
          }}</span>
        </div>
      </div>

      <div v-if="pilot.requirements.required_system_core_ids.length" class="req-group">
        <div class="req-label">Required System</div>
        <div class="req-chips">
          <template v-for="id in pilot.requirements.required_system_core_ids" :key="id">
            <RouterLink
              v-if="id.startsWith('starsystemdef_')"
              :to="`/star-systems/${id}`"
              class="req-chip req-chip--link"
            >
              {{ humanizeTag(id.replace(/^starsystemdef_/, '')) }}
            </RouterLink>
            <span v-else class="req-chip">{{ humanizeTag(id) }}</span>
          </template>
        </div>
      </div>

      <div v-if="pilot.requirements.required_pilot_ids.length" class="req-group">
        <div class="req-label">Required Pilots</div>
        <div class="req-chips">
          <span v-for="r in pilot.requirements.required_pilot_ids" :key="r.id" class="req-chip">{{
            r.name ?? humanizeTag(r.id.replace(/^pilot_/, ''))
          }}</span>
        </div>
      </div>

      <div v-if="pilot.requirements.conflicting_pilot_ids.length" class="req-group">
        <div class="req-label">Conflicts With</div>
        <div class="req-chips">
          <span
            v-for="r in pilot.requirements.conflicting_pilot_ids"
            :key="r.id"
            class="req-chip req-chip--conflict"
            >{{ r.name ?? humanizeTag(r.id.replace(/^pilot_/, '')) }}</span
          >
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'
import type { RtoPilotDetail } from '../composables/useRtoPilots'
import { humanizeTag, canonicalizeFaction } from '../utils/humanize'

const props = defineProps<{ pilot: RtoPilotDetail }>()
const pilot = props.pilot

const bioExpanded = ref(false)
const BIO_TRUNCATE_LENGTH = 280

const bioTruncatable = computed(() => (pilot.details?.length ?? 0) > BIO_TRUNCATE_LENGTH)
const truncatedBio = computed(() => {
  if (!pilot.details) return ''
  if (!bioTruncatable.value) return pilot.details
  return pilot.details.slice(0, BIO_TRUNCATE_LENGTH).trimEnd() + '…'
})

const metaLine = computed(() => {
  const parts: string[] = []
  if (pilot.gender) parts.push(pilot.gender)
  if (pilot.age != null) parts.push(`Age ${pilot.age}`)
  const faction = pilot.faction ? canonicalizeFaction(pilot.faction) : null
  if (faction) parts.push(faction)
  return parts.join(' · ')
})

const CAN_PILOT_LABELS: Record<string, string> = {
  can_pilot_generic_mech: 'MECH',
  can_pilot_generic_vehicle: 'VEH',
  can_pilot_vtol: 'VTOL',
  can_pilot_landairmech: 'LAM',
  can_pilot_battle_armor: 'BA',
}

const canPilotLabels = computed(() =>
  pilot.can_pilot.map((tag) => ({
    tag,
    label: CAN_PILOT_LABELS[tag] ?? humanizeTag(tag.replace(/^can_pilot_/, '')),
  })),
)
</script>

<style scoped>
.rp-card {
  background: var(--bg-card);
  border: var(--border-default);
  border-radius: var(--card-radius);
  padding: 14px;
  box-shadow: var(--card-shadow);
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.rp-header {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.rp-name {
  color: var(--text-primary);
  font-size: 15px;
  font-weight: 600;
}

.rp-callsign {
  color: var(--text-muted);
  font-size: 12px;
  font-style: italic;
}

.rp-meta {
  color: var(--text-muted);
  font-size: 11px;
}

.rp-cp-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.cp-badge {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  padding: 2px 7px;
  border-radius: var(--badge-radius, 3px);
  letter-spacing: 0.3px;
}

.cp-badge[data-cp='can_pilot_generic_mech'] {
  background: rgba(88, 166, 255, 0.15);
  color: #58a6ff;
}
.cp-badge[data-cp='can_pilot_generic_vehicle'] {
  background: rgba(80, 200, 120, 0.15);
  color: #50c878;
}
.cp-badge[data-cp='can_pilot_vtol'] {
  background: rgba(180, 100, 255, 0.15);
  color: #b464ff;
}
.cp-badge[data-cp='can_pilot_landairmech'] {
  background: rgba(255, 140, 0, 0.15);
  color: #ff8c00;
}
.cp-badge[data-cp='can_pilot_battle_armor'] {
  background: rgba(210, 153, 34, 0.15);
  color: #d29922;
}

.rp-bio-text {
  color: var(--text-primary);
  font-size: 12.5px;
  line-height: 1.5;
  white-space: pre-line;
  margin: 0;
}

.bio-toggle {
  background: transparent;
  border: none;
  color: var(--accent-blue);
  font-size: 11px;
  cursor: pointer;
  padding: 4px 0 0;
}

.rp-quirks {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.quirk-entry {
  background: rgba(128, 128, 128, 0.08);
  border-radius: 4px;
  padding: 6px 8px;
}

.quirk-name {
  color: var(--text-primary);
  font-size: 12px;
  font-weight: 600;
}

.quirk-desc {
  color: var(--text-muted);
  font-size: 11px;
  line-height: 1.4;
  margin-top: 2px;
}

.rp-requirements {
  display: flex;
  flex-direction: column;
  gap: 8px;
  border-top: var(--border-default);
  padding-top: 8px;
}

.req-label {
  color: var(--text-muted);
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  margin-bottom: 4px;
}

.req-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.req-chip {
  font-size: 10px;
  color: var(--text-primary);
  background: rgba(128, 128, 128, 0.12);
  border-radius: 3px;
  padding: 2px 6px;
  text-decoration: none;
}

.req-chip--link {
  color: var(--accent-blue);
}

.req-chip--conflict {
  color: #ff5555;
  background: rgba(255, 80, 80, 0.12);
}
</style>
