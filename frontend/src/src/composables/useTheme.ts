import { ref, watch } from 'vue'

export type Theme = 'v1' | 'v2'

const STORAGE_KEY = 'theme'

function readTheme(): Theme {
  const v = localStorage.getItem(STORAGE_KEY)
  return v === 'v1' ? 'v1' : 'v2'
}

const theme = ref<Theme>(readTheme())

function applyTheme(v: Theme) {
  if (v === 'v2') {
    document.documentElement.setAttribute('data-theme', 'v2')
  } else {
    document.documentElement.removeAttribute('data-theme')
  }
}

watch(theme, (v) => {
  localStorage.setItem(STORAGE_KEY, v)
  applyTheme(v)
})

applyTheme(theme.value)

export function useTheme() {
  return { theme }
}
