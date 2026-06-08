<template>
  <div ref="containerRef" class="entity-grid-outer">
    <!-- Skeleton loading state -->
    <div v-if="loading" class="entity-grid">
      <SkeletonCard v-for="n in 12" :key="n" />
    </div>

    <!-- Virtual scrolled grid -->
    <div
      v-else
      :style="{ position: 'relative', height: totalSize + 'px' }"
    >
      <div
        v-for="vRow in virtualRows"
        :key="vRow.index"
        :style="{
          position: 'absolute',
          top: vRow.start + 'px',
          width: '100%',
          display: 'grid',
          gridTemplateColumns: `repeat(${columns}, 1fr)`,
          gap: GAP + 'px',
          padding: '0 16px',
          boxSizing: 'border-box',
        }"
      >
        <MechCard
          v-for="item in rowItems(vRow.index)"
          :key="item.variant_id"
          v-bind="item"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useVirtualizer } from '@tanstack/vue-virtual'
import MechCard from './MechCard.vue'
import SkeletonCard from './SkeletonCard.vue'
import type { ChassisSummary } from '../composables/useMechList'

const props = defineProps<{
  items: ChassisSummary[]
  mode: string
  loading?: boolean
}>()

const containerRef = ref<HTMLElement>()
const containerWidth = ref(800)
const CARD_MIN_WIDTH = 200
const GAP = 12

const columns = computed(() =>
  Math.max(1, Math.floor((containerWidth.value - 32 + GAP) / (CARD_MIN_WIDTH + GAP)))
)

const rows = computed(() => Math.ceil(props.items.length / columns.value))

let ro: ResizeObserver | null = null

onMounted(() => {
  ro = new ResizeObserver(entries => {
    containerWidth.value = entries[0].contentRect.width
  })
  if (containerRef.value) ro.observe(containerRef.value)
})

onUnmounted(() => {
  ro?.disconnect()
})

const rowVirtualizer = useVirtualizer(
  computed(() => ({
    count: rows.value,
    getScrollElement: () => document.documentElement,
    estimateSize: () => 140,
    overscan: 3,
  }))
)

const virtualRows = computed(() => rowVirtualizer.value.getVirtualItems())
const totalSize = computed(() => rowVirtualizer.value.getTotalSize())

function rowItems(rowIndex: number): ChassisSummary[] {
  const start = rowIndex * columns.value
  return props.items.slice(start, start + columns.value)
}
</script>

<style scoped>
.entity-grid-outer {
  padding-top: 16px;
  padding-bottom: 16px;
}
.entity-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 12px;
  padding: 0 16px;
}
</style>
