import { ref, watch } from 'vue'

export type UIScale = 'normal' | 'large' | 'xl'

const STORAGE_KEY = 'ui-scale'

function readScale(): UIScale {
  const v = localStorage.getItem(STORAGE_KEY)
  return v === 'large' || v === 'xl' ? v : 'normal'
}

const scale = ref<UIScale>(readScale())

function applyScale(v: UIScale) {
  document.documentElement.setAttribute('data-scale', v)
}

watch(scale, v => {
  localStorage.setItem(STORAGE_KEY, v)
  applyScale(v)
})

applyScale(scale.value)

export function useUIScale() {
  return { scale }
}
