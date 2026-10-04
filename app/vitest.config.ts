import { defineConfig, mergeConfig } from 'vitest/config'

import viteConfig from './vite.config.ts'

// Test-Läufer für die reine Datenlogik in `src/**` (Phase 5): kein DOM, keine
// Globals — Tests importieren `describe`/`it`/`expect` aus 'vitest'. Alias `@/`
// und Vue-Plugin kommen aus der Vite-Konfiguration.
export default mergeConfig(
  viteConfig,
  defineConfig({
    test: {
      environment: 'node',
      include: ['src/**/__tests__/*.test.ts'],
    },
  }),
)
