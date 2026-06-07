<template>
  <div class="variant-list">
    <VariantPanel
      v-for="(variant, i) in variants"
      :key="variant.id"
      :variant="variant"
      :default-open="i === 0"
    />
  </div>
</template>

<script setup lang="ts">
import VariantPanel from './VariantPanel.vue'
import type { VariantDetail } from '../composables/useChassisDetail'

defineProps<{ variants: VariantDetail[] }>()
</script>

<style scoped>
.variant-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
</style>
