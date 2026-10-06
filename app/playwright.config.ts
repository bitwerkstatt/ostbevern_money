import { defineConfig } from '@playwright/test'

// Browser-Tests gegen `vite preview` des Produktions-Builds (`npm run build-only` zuerst).
// Projekte: `ci` (Desktop, läuft in der CI), `mobil` (360 px, nur für die Verifikation, Plan
// 07-09) und `texte` (Textliste für den Abnahme-Checkpoint, Plan 07-10). Die Specs für
// `mobil` und `texte` folgen in diesen Plänen.
const MOBIL_SPEC = /mobil\.spec\.ts$/
const TEXTE_SPEC = /textliste\.spec\.ts$/

export default defineConfig({
  testDir: './e2e',
  reporter: 'list',
  forbidOnly: !!process.env.CI,
  retries: 0,
  use: { baseURL: 'http://localhost:4173/' },
  projects: [
    {
      name: 'ci',
      use: { browserName: 'chromium', viewport: { width: 1280, height: 800 } },
      testIgnore: [MOBIL_SPEC, TEXTE_SPEC],
    },
    {
      name: 'mobil',
      use: { browserName: 'chromium', viewport: { width: 360, height: 640 } },
      testMatch: MOBIL_SPEC,
    },
    {
      name: 'texte',
      use: { browserName: 'chromium', viewport: { width: 1280, height: 800 } },
      testMatch: TEXTE_SPEC,
    },
  ],
  webServer: {
    command: 'npm run preview -- --port 4173 --strictPort',
    url: 'http://localhost:4173/',
    reuseExistingServer: false,
  },
})
