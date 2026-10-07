import { existsSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { createSSRApp } from 'vue'
import { renderToString } from 'vue/server-renderer'
import { describe, expect, it } from 'vitest'

import ChartCard from '@/components/ChartCard.vue'

// Beispieldaten-Callout der ChartCard (E9, 01/IN-03): Warn-Icon statt Info-Icon, Text unverändert.
// Gerendert wird serverseitig mit `vue/server-renderer` (kein DOM, kein neues Paket).

function rendere(props: Record<string, unknown>): Promise<string> {
  return renderToString(createSSRApp(ChartCard, props))
}

describe('ChartCard Beispieldaten-Callout', () => {
  it('mit Flag: Warn-Icon, unveränderter Text, kein Info-Icon', async () => {
    const html = await rendere({ titel: 'Probe', beispieldaten: true })
    expect(html).toContain('<wa-callout')
    expect(html).toContain('variant="warning"')
    expect(html).toContain('name="triangle-exclamation"')
    expect(html).toContain('Beispieldaten — noch keine echten Haushaltszahlen.')
    expect(html).not.toContain('circle-info')
  })

  it('ohne Flag: kein Callout', async () => {
    const html = await rendere({ titel: 'Probe' })
    expect(html).not.toContain('wa-callout')
  })

  it('die Icon-Datei liegt unter public/icons/solid', () => {
    const datei = fileURLToPath(
      new URL('../../../public/icons/solid/triangle-exclamation.svg', import.meta.url),
    )
    expect(existsSync(datei)).toBe(true)
  })
})
