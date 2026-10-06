// Abdeckung der Kennzahlkacheln mit Quell-Beleg (Phase 7, UI-02, D-01): jede Kachel von Start,
// Investitionen und Stellenplan bekommt einen Belegschlüssel, der in `quellen.json` aufgelöst
// wird. Die Kacheln der Seiten Investitionen und Stellenplan entstehen teils im Seitenskript;
// dort prüft ein Quelltext-Scan, dass jede Kachel `:quelle` bindet.

import { describe, expect, it } from 'vitest'

import { haushalt } from '@/data/daten'
import { veGesamt } from '@/lib/finanzierung'
import { baueKennzahlen } from '@/lib/kennzahlen'
import { belegSchluessel, findeBeleg } from '@/lib/quelle'
import { schuldenKacheln } from '@/lib/schulden'
import { stellenSummen } from '@/lib/stellen'
import investitionenSeite from '@/pages/InvestitionenPage.vue?raw'
import startSeite from '@/pages/StartPage.vue?raw'
import stellenplanSeite from '@/pages/StellenplanPage.vue?raw'

/** Alle `<KennzahlKachel … />`-Elemente einer Vue-Datei. */
function kachelElemente(quelltext: string): string[] {
  return Array.from(quelltext.matchAll(/<KennzahlKachel\b[\s\S]*?\/>/g), (treffer) => treffer[0])
}

const SEITEN: [string, string][] = [
  ['StartPage.vue', startSeite],
  ['InvestitionenPage.vue', investitionenSeite],
  ['StellenplanPage.vue', stellenplanSeite],
]

describe('Quelle an den Kacheln (D-01)', () => {
  it.each(SEITEN)('jede KennzahlKachel in %s bindet :quelle', (_name, quelltext) => {
    const elemente = kachelElemente(quelltext)
    expect(elemente.length).toBeGreaterThan(0)
    for (const element of elemente) {
      expect(element).toMatch(/:quelle="/)
    }
  })

  it.each(['InvestitionenPage.vue', 'StellenplanPage.vue'])(
    'jede KennzahlKachel in %s reicht Herleitung und Wertart weiter',
    (name) => {
      const quelltext = SEITEN.find(([datei]) => datei === name)?.[1] ?? ''
      for (const element of kachelElemente(quelltext)) {
        expect(element).toMatch(/:herleitung="/)
        expect(element).toMatch(/:wertart="/)
      }
    },
  )

  it('alle Kennzahl-Schlüssel der Startseite lösen auf', () => {
    for (const kennzahl of baueKennzahlen()) {
      expect(findeBeleg(kennzahl.quelle), kennzahl.schluessel).not.toBeNull()
    }
  })

  it('beide Schulden-Kacheln lösen auf', () => {
    for (const kachel of schuldenKacheln()) {
      expect(findeBeleg(kachel.quelle), kachel.schluessel).not.toBeNull()
    }
  })

  it('die Kachel Verpflichtungsermächtigungen zeigt die Summenzeile des Finanzplans, deren VE-Spalte sie nennt', () => {
    const schluessel = belegSchluessel.fp('GESAMT', 'auszahlungen_investitionen')
    expect(findeBeleg(schluessel)).not.toBeNull()
    expect(investitionenSeite).toContain(
      "belegSchluessel.fp('GESAMT', 'auszahlungen_investitionen')",
    )
    expect(haushalt.finanzplan.GESAMT?.ve.auszahlungen_investitionen).toBe(veGesamt())
  })

  it('die Stellenplan-Kacheln zeigen die erste Seite der Stellenübersicht als Seitenbeleg', () => {
    const erste = stellenSummen().pdfSeiten[0]
    expect(erste).toBeDefined()
    const beleg = findeBeleg(belegSchluessel.seite(erste ?? 0))
    expect(beleg).not.toBeNull()
    expect(beleg?.bbox).toBeNull()
    expect(stellenplanSeite).toContain('belegSchluessel.seite(summen.pdfSeiten[0]')
  })
})
