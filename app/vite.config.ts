import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  // Relativer Pfad statt fest codiertem Repo-Namen: GitHub Pages dient
  // Projekt-Seiten unter `https://<account>.github.io/<repo>/`, der endgültige
  // Repo-Name steht noch nicht fest. Mit Hash-Router funktioniert `'./'`
  // sowohl lokal (`npm run dev`) als auch unter jedem Pages-Unterpfad.
  base: './',
  plugins: [
    vue({
      template: {
        compilerOptions: {
          isCustomElement: (tag) => tag.startsWith('wa-'),
        },
      },
    }),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
})
