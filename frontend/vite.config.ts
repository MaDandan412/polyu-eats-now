import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { readFileSync, writeFileSync } from 'node:fs'
import { createHash } from 'node:crypto'
export default defineConfig({
  plugins: [react(), tailwindcss(), {
    name: 'food-now-offline-shell',
    writeBundle(options, bundle) {
      const assets = Object.keys(bundle).filter(file => /\.(js|css)$/.test(file)).map(file => `/${file}`)
      const shell = ['/', '/manifest.webmanifest', '/polyu-favicon.ico', '/polyu-logo.png', '/polyu-wordmark.png', '/block-y-order-qr.png', '/icon-192.png', '/icon-512.png', ...assets]
      const version = createHash('sha256').update(JSON.stringify(assets)).digest('hex').slice(0,12)
      const source = readFileSync('public/sw.js', 'utf8').replace("'polyu-food-now-v1'", `'polyu-food-now-${version}'`).replace('const SHELL = [];', `const SHELL = ${JSON.stringify(shell)};`)
      writeFileSync(`${options.dir || 'dist'}/sw.js`, source)
    },
  }],
  server: { port: 5173, strictPort: true, proxy: { '/api': 'http://127.0.0.1:8000' } },
  preview: { port: 4173, strictPort: true, proxy: { '/api': 'http://127.0.0.1:8000' } },
})
