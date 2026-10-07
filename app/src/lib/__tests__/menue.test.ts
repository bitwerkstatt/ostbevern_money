import { describe, expect, it } from 'vitest'

import { FUSSZEILEN_ROUTEN, MENUE, menueLinks, type MenueGruppe } from '@/lib/menue'

// Der Quelltext des Routers (wie in `quelltext.test.ts` über `?raw`): jeder Menüeintrag muss
// auf eine Route zeigen, die dort als `name: '…'` steht.
// Warum Quelltext: Das Menüinventar muss zu den Routen passen. `router/index.ts` baut den Router
// beim Import mit Hash-Verlauf auf, der einen Browser braucht; die Testumgebung
// (`environment: 'node'`) hat kein DOM und kein DOM-Paket. Deshalb liest der Test die
// Routennamen aus dem Quelltext (D-14).
const routerQuelltexte = import.meta.glob<string>('/src/router/index.ts', {
  query: '?raw',
  import: 'default',
  eager: true,
})
const routerQuelltext = routerQuelltexte['/src/router/index.ts'] ?? ''

const PHASE_6_ROUTEN = ['entwicklung', 'investitionen', 'rat-entscheidet', 'stellenplan']

function gruppen(): MenueGruppe[] {
  return MENUE.filter((eintrag): eintrag is MenueGruppe => eintrag.typ === 'gruppe')
}

describe('MENUE (D-13, D-19)', () => {
  it('flacht zur Linkliste in der Reihenfolge von D-19 ab', () => {
    expect(menueLinks().map((link) => link.name)).toEqual([
      'start',
      'einnahmen',
      'ausgaben',
      'geldfluss',
      'entwicklung',
      'investitionen',
      'rat-entscheidet',
      'stellenplan',
      'glossar',
    ])
  })

  it('ordnet die Gruppe „Mehr wissen“ zwischen Geldfluss und Glossar ein', () => {
    expect(
      MENUE.map((eintrag) => (eintrag.typ === 'gruppe' ? eintrag.text : eintrag.name)),
    ).toEqual(['start', 'einnahmen', 'ausgaben', 'geldfluss', 'Mehr wissen', 'glossar'])
  })

  it('hat genau eine Gruppe mit den vier Seiten der Phase 6 in dieser Reihenfolge', () => {
    const alle = gruppen()
    expect(alle).toHaveLength(1)
    expect(alle[0]?.text).toBe('Mehr wissen')
    expect(alle[0]?.eintraege.map((link) => link.name)).toEqual(PHASE_6_ROUTEN)
    expect(alle[0]?.eintraege.map((link) => link.text)).toEqual([
      'Entwicklung',
      'Investitionen',
      'Rat entscheidet',
      'Stellenplan',
    ])
  })

  it('behält das gewählte Jahr genau bei einnahmen, ausgaben und geldfluss (D-10)', () => {
    expect(
      menueLinks()
        .filter((link) => link.mitJahr)
        .map((link) => link.name),
    ).toEqual(['einnahmen', 'ausgaben', 'geldfluss'])
  })

  it('führt keinen Linknamen doppelt, auch nicht über Gruppen hinweg', () => {
    const namen = menueLinks().map((link) => link.name)
    expect(new Set(namen).size).toBe(namen.length)
  })

  it('verweist nur auf Routen, die im Router stehen', () => {
    expect(routerQuelltext).not.toBe('')
    for (const link of menueLinks()) {
      expect(routerQuelltext, `Route ${link.name}`).toContain(`name: '${link.name}'`)
    }
  })

  it('führt jede Route der Phase 6 in der Gruppe', () => {
    const imMenue = new Set(gruppen().flatMap((gruppe) => gruppe.eintraege.map((l) => l.name)))
    for (const name of PHASE_6_ROUTEN) {
      expect(imMenue.has(name), `Route ${name} in der Gruppe`).toBe(true)
    }
  })
})

// Routen, die nicht im Kopfmenü stehen, aber erreichbar sein müssen:
// - `produkt` hat einen Parameter (`/produkt/:code`) und wird aus Tabellen und Karten verlinkt.
// - `ueber` („Über dieses Projekt“, Impressum, Datenschutz) ist nur aus der Fußzeile verlinkt
//   (D-08) und steht deshalb in FUSSZEILEN_ROUTEN statt im Menü.
// Jede weitere Route muss im Menü oder in dieser Ausnahmeliste stehen, sonst ist sie nur per
// Adresse erreichbar und scheitert hier.
const OHNE_MENUEEINTRAG = ['produkt']

function routenNamen(): string[] {
  return Array.from(routerQuelltext.matchAll(/\bname: '([^']+)'/g), (treffer) => treffer[1]!)
}

describe('FUSSZEILEN_ROUTEN (D-08)', () => {
  it('enthält genau die Route ueber', () => {
    expect(FUSSZEILEN_ROUTEN).toEqual(['ueber'])
  })

  it('überschneidet sich nicht mit dem Menü', () => {
    const imMenue = new Set(menueLinks().map((link) => link.name))
    for (const name of FUSSZEILEN_ROUTEN) {
      expect(imMenue.has(name), `Route ${name} nicht im Menü`).toBe(false)
    }
  })

  it('verweist nur auf Routen, die im Router stehen', () => {
    for (const name of FUSSZEILEN_ROUTEN) {
      expect(routerQuelltext, `Route ${name}`).toContain(`name: '${name}'`)
    }
  })
})

describe('Jede Route ist im Menü oder in der Fußzeile erreichbar', () => {
  it('findet die Routen im Quelltext des Routers', () => {
    expect(routenNamen()).toContain('start')
    expect(routenNamen()).toContain('ueber')
  })

  it('führt jede Route außer produkt im Menü oder in FUSSZEILEN_ROUTEN', () => {
    const erreichbar = new Set<string>([
      ...menueLinks().map((link) => link.name),
      ...FUSSZEILEN_ROUTEN,
      ...OHNE_MENUEEINTRAG,
    ])
    for (const name of routenNamen()) {
      expect(erreichbar.has(name), `Route ${name} im Menü oder in FUSSZEILEN_ROUTEN`).toBe(true)
    }
  })
})
