import { defineConfig, type Plugin } from 'vite'
import vue from '@vitejs/plugin-vue'
import { readFileSync, writeFileSync } from 'node:fs'

const { version, rogueTechVersion } = JSON.parse(readFileSync('../../version.json', 'utf-8')) as {
  version: string
  rogueTechVersion: string
}

function syncVersionPlugin(): Plugin {
  return {
    name: 'sync-version',
    buildStart() {
      const pkgPath = './package.json'
      const pkg = JSON.parse(readFileSync(pkgPath, 'utf-8')) as Record<string, unknown>
      if (pkg.version !== version) {
        pkg.version = version
        writeFileSync(pkgPath, JSON.stringify(pkg, null, 2) + '\n')
      }
    },
    transformIndexHtml(html) {
      return html.replace(/<title>(.*?)<\/title>/, `<title>$1 — v${version}</title>`)
    },
  }
}

export default defineConfig({
  plugins: [vue(), syncVersionPlugin()],
  define: {
    __APP_VERSION__: JSON.stringify(version),
    __RT_VERSION__: JSON.stringify(rogueTechVersion),
  },
})
