import { createSSRApp } from 'vue'
import { renderToString } from 'vue/server-renderer'
import { describe, expect, it } from 'vitest'

import ErklaerText from '@/components/ErklaerText.vue'
import { texte } from '@/data/daten'

// G-09-02: Die Quellenzeile unter jedem Erklärtext schreibt „PDF-Seite“ nur bei genau einer
// Seite im Singular. Gerendert wird serverseitig ohne DOM (Muster von eurobetrag.test.ts).

function rendere(props: Record<string, unknown>): Promise<string> {
  return renderToString(createSSRApp(ErklaerText, props))
}

describe('ErklaerText Quellenzeile', () => {
  it.each(texte.texte.map((t) => [t.schluessel, t.quelle_seiten] as const))(
    'G-09-02: %s nennt „PDF-Seite“ bzw. „PDF-Seiten“ passend zur Zahl der Seiten',
    async (schluessel, seiten) => {
      const html = await rendere({ schluessel })
      const wort = seiten.length === 1 ? 'PDF-Seite' : 'PDF-Seiten'
      expect(html).toContain(`Quelle: ${wort} ${seiten.join(', ')}</p>`)
    },
  )
})
