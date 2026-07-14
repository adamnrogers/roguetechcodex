import { ref } from 'vue'
import { domToPng } from 'modern-screenshot'

function nextFrame(): Promise<void> {
  return new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(() => resolve())))
}

function waitForImages(target: HTMLElement): Promise<void> {
  const images = Array.from(target.querySelectorAll('img'))
  return Promise.all(
    images.map(img =>
      img.complete ? Promise.resolve() : img.decode().catch(() => undefined)
    )
  ).then(() => undefined)
}

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
      // Settle layout after the sidebar override and make sure fonts/images
      // are fully ready before measuring — the library's own internal
      // measurement can race image decode/font-swap and end up with a
      // canvas size that doesn't match what actually gets rendered.
      await document.fonts.ready
      await waitForImages(target)
      await nextFrame()

      const rect = target.getBoundingClientRect()
      const width = Math.ceil(rect.width)
      const height = Math.ceil(rect.height)

      const dataUrl = await domToPng(target, {
        width,
        height,
        scale: 1,
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
