import { describe, expect, it } from 'vitest'

import { haushalt } from '@/data/daten'
import { anteil, minderaufwandBetrag, proKopf, summe } from '@/lib/berechnung'

describe('proKopf', () => {
  it('rundet auf ganze Euro (Math.round), nicht ab (Pitfall 3)', () => {
    expect(proKopf(30455569, 11741)).toBe(2594)
    expect(proKopf(18443000, 11741)).toBe(1571)
  })

  it('rundet .5 auf', () => {
    expect(proKopf(5, 2)).toBe(3)
  })

  it('wirft bei Einwohnerzahl 0 oder negativ', () => {
    expect(() => proKopf(100, 0)).toThrow()
    expect(() => proKopf(100, -5)).toThrow()
  })
})

describe('anteil', () => {
  it('liefert null bei Summe 0', () => {
    expect(anteil(5, 0)).toBeNull()
  })

  it('teilt Wert durch Summe', () => {
    expect(anteil(1, 4)).toBe(0.25)
  })
})

describe('summe', () => {
  it('addiert und überspringt null', () => {
    expect(summe([1, null, 2])).toBe(3)
    expect(summe([])).toBe(0)
  })
})

// Die eine Minderaufwand-Regel für /geldfluss und /ausgaben (D-08, TXT-02, 05/IN-07). Der Wurf ist
// nur an der reinen Funktion testbar, weil `haushalt` ein statischer Import ist.
describe('minderaufwandBetrag (D-08, TXT-02)', () => {
  it('liefert null für einen fehlenden Wert', () => {
    expect(minderaufwandBetrag(undefined, 2026)).toBeNull()
    expect(minderaufwandBetrag(null, 2026)).toBeNull()
  })

  it('liefert null für 0 (kein Minderaufwand, kein Hinweis)', () => {
    expect(minderaufwandBetrag(0, 2024)).toBeNull()
  })

  it('liefert für einen negativen Plan-Wert den positiven Betrag, nie ein Minuszeichen', () => {
    expect(minderaufwandBetrag(-600_000, 2026)).toBe(600_000)
  })

  it('wirft bei einem positiven Plan-Wert (Datenfehler) und nennt das Jahr', () => {
    expect(() => minderaufwandBetrag(5, 2027)).toThrow(
      /^Globaler Minderaufwand ist positiv: Datenfehler.*2027/,
    )
  })
})

describe.runIf(haushalt.haushaltsjahr === 2026)('Pro-Kopf-Werte Haushalt 2026', () => {
  it('Aufwand und Steuern pro Einwohner entsprechen den Erfolgskriterien', () => {
    const einwohner = Number(haushalt.meta.einwohner.wert)
    const i = haushalt.jahre.indexOf(2026)
    expect(proKopf(haushalt.ergebnisplan.GESAMT!.berechnet.aufwand[i]!, einwohner)).toBe(2594)
    expect(proKopf(haushalt.ergebnisplan.GESAMT!.zeilen.steuern![i]!, einwohner)).toBe(1571)
  })
})
