import { ref } from 'vue'
import { domToPng } from 'modern-screenshot'

export function useExportImage() {
  const isExporting = ref(false)
  const exportError = ref<string | null>(null)

  async function exportAsImage(target: HTMLElement, filename: string) {
    isExporting.value = true
    exportError.value = null
    const sidebars = target.querySelectorAll<HTMLElement>('.sidebar, .side-col')
    const prevPositions = Array.from(sidebars).map(el => el.style.position)
    sidebars.forEach(el => { el.style.position = 'static' })
    try {
      const dataUrl = await domToPng(target, {
        backgroundColor: getComputedStyle(document.body).backgroundColor,
        filter: node => !(node instanceof HTMLElement && node.hasAttribute('data-export-exclude')),
      })
      const a = document.createElement('a')
      a.href = dataUrl
      a.download = filename
      a.click()
    } catch {
      exportError.value = 'Could not generate image. Try again or use your browser\'s screenshot tool.'
    } finally {
      sidebars.forEach((el, i) => { el.style.position = prevPositions[i] })
      isExporting.value = false
    }
  }

  return { isExporting, exportError, exportAsImage }
}
