import { createSSRApp } from 'vue'
import { renderToString } from 'vue/server-renderer'
import { describe, expect, it } from 'vitest'

import { euro, euroKurz, RD_PRAEFIX } from '@/charts/format'
import EuroBetrag from '@/components/EuroBetrag.vue'

// Template-Form der Regel „rd.“ (D-22): EuroBetrag rendert serverseitig, ohne DOM
// (Muster von zustaende.test.ts).

function rendere(props: Record<string, unknown>): Promise<string> {
  return renderToString(createSSRApp(EuroBetrag, props))
}

describe('EuroBetrag', () => {
  it('setzt „rd.“ vor den vollen Betrag, wenn er gerundet ist', async () => {
    const html = await rendere({ wert: 7_800_000, gerundet: true })
    expect(html).toContain(`${RD_PRAEFIX}${euro(7_800_000)}`)
  })

  it('kürzt den Betrag mit kurz und setzt „rd.“ davor', async () => {
    const html = await rendere({ wert: 7_800_000, gerundet: true, kurz: true })
    expect(html).toContain(`${RD_PRAEFIX}${euroKurz(7_800_000)}`)
    expect(html).not.toContain(euro(7_800_000))
  })

  it('zeigt das Etikett „berechnet“ nur für berechnete Beträge', async () => {
    const html = await rendere({ wert: 5, berechnet: true })
    expect(html).toContain('berechnet')
  })

  it('zeigt ohne Flags weder „rd.“ noch „berechnet“', async () => {
    const html = await rendere({ wert: 5 })
    expect(html).toContain(euro(5))
    expect(html).not.toContain(RD_PRAEFIX)
    expect(html).not.toContain('berechnet')
  })
})
