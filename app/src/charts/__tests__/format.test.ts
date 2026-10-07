import { describe, expect, it } from 'vitest'

import {
  anzahlText,
  betragMitHinweis,
  datum,
  euro,
  euroKurz,
  formatiere,
  jahr,
  kurzMitHinweis,
  prozent,
  RD_PRAEFIX,
  rundKurz,
  rundMitHinweis,
  RUND_PRAEFIX,
  type FormatKuerzel,
} from '@/charts/format'

// Erwartete Strings stehen als Literale da (U+00A0 vor „€“ wie von Intl de-DE),
// damit ein Locale-Drift den Test bricht.
describe('euro', () => {
  it('gruppiert Tausender mit Punkt und hängt das Eurozeichen an', () => {
    expect(euro(2353506)).toBe('2.353.506 €')
  })
})

describe('euroKurz', () => {
  it('kürzt Beträge ab 1 Mio. € auf drei signifikante Stellen', () => {
    expect(euroKurz(27502063)).toBe('27,5 Mio. €')
  })

  it('behält das Vorzeichen bei negativen Beträgen', () => {
    expect(euroKurz(-2353506)).toBe('-2,35 Mio. €')
  })
})

describe('jahr', () => {
  it('gruppiert Jahreszahlen nicht (CR-01)', () => {
    expect(jahr(2026)).toBe('2026')
  })
})

describe('formatiere', () => {
  it('formatiert Prozentrohwerte als ganze Prozentpunkte', () => {
    expect(formatiere(554, 'prozent')).toBe(prozent(5.54))
  })

  it('formatiert Promillerohwerte über den Anteil', () => {
    expect(formatiere(363, 'promille')).toBe(prozent(0.363))
  })

  it('lässt bestehende Ausgaben unverändert', () => {
    expect(formatiere(27502063, 'mio')).toBe('27,5 Mio. €')
    expect(formatiere(2026, 'jahr')).toBe('2026')
  })
})

describe('formatiere: sichtbarer Fallback (UI-05, WR-06/IN-01)', () => {
  it('zeigt den Gedankenstrich für null', () => {
    expect(formatiere(null, 'euro')).toBe('–')
  })

  it('zeigt den Gedankenstrich für undefined', () => {
    expect(formatiere(undefined, 'mio')).toBe('–')
  })

  it('zeigt den Gedankenstrich für NaN', () => {
    expect(formatiere(NaN, 'zahl')).toBe('–')
  })

  it('zeigt den Gedankenstrich für Infinity', () => {
    expect(formatiere(Infinity, 'jahr')).toBe('–')
  })

  it('zeigt den Gedankenstrich für -Infinity', () => {
    expect(formatiere(-Infinity, 'prozent')).toBe('–')
  })

  it('zeigt für 0 weiterhin 0 und nicht den Fallback', () => {
    expect(formatiere(0, 'zahl')).toBe('0')
  })

  it('wirft bei unbekanntem Formatkürzel und nennt das Kürzel', () => {
    expect(() => formatiere(1, 'unbekannt' as FormatKuerzel)).toThrow(/unbekannt/)
  })
})

describe('anzahlText (WR-02)', () => {
  it('nutzt den Singular genau für 1', () => {
    expect(anzahlText(1, 'Maßnahme', 'Maßnahmen')).toBe('1 Maßnahme')
  })

  it('nutzt für 0 den Plural', () => {
    expect(anzahlText(0, 'Maßnahme', 'Maßnahmen')).toBe('0 Maßnahmen')
  })

  it('nutzt für 2 den Plural', () => {
    expect(anzahlText(2, 'Maßnahme', 'Maßnahmen')).toBe('2 Maßnahmen')
  })

  it('gruppiert große Anzahlen mit Tausenderpunkt', () => {
    expect(anzahlText(1000, 'Maßnahme', 'Maßnahmen')).toBe('1.000 Maßnahmen')
  })
})

describe('datum (UI-03, D-18)', () => {
  it('formatiert ein ISO-Datum auf Deutsch mit ausgeschriebenem Monat', () => {
    expect(datum('2026-03-03')).toBe('3. März 2026')
  })

  it('rechnet unabhängig von der Zeitzone (UTC)', () => {
    expect(datum('2026-01-01')).toBe('1. Januar 2026')
    expect(datum('2026-12-31')).toBe('31. Dezember 2026')
  })

  it.each(['kein-datum', '', '2026-13-01', '2026-02-30', '03.03.2026'])(
    'zeigt den Gedankenstrich für %j',
    (roh) => {
      expect(datum(roh)).toBe('–')
    },
  )
})

describe('Regel „rd.“ und „rund“ (D-22, TXT-04)', () => {
  it('trennt „rd.“ und „rund“ vom Betrag durch ein geschütztes Leerzeichen (U+00A0)', () => {
    expect(RD_PRAEFIX).toBe('rd.\u00a0')
    expect(RD_PRAEFIX.charCodeAt(3)).toBe(0xa0)
    expect(RUND_PRAEFIX).toBe('rund\u00a0')
    expect(RUND_PRAEFIX.charCodeAt(4)).toBe(0xa0)
  })

  it('betragMitHinweis setzt „rd.“ nur bei gerundeten Beträgen', () => {
    expect(betragMitHinweis(7_800_000, true)).toBe(`${RD_PRAEFIX}${euro(7_800_000)}`)
    expect(betragMitHinweis(7_800_000, false)).toBe(euro(7_800_000))
  })

  it('kurzMitHinweis kürzt über euroKurz und setzt „rd.“ nur bei gerundeten Beträgen', () => {
    expect(kurzMitHinweis(27_502_063, true)).toBe(`${RD_PRAEFIX}${euroKurz(27_502_063)}`)
    expect(kurzMitHinweis(27_502_063, false)).toBe(euroKurz(27_502_063))
    expect(kurzMitHinweis(5_000, true)).toBe(`${RD_PRAEFIX}${euro(5_000)}`)
  })

  it('rundMitHinweis setzt „rund“ im Fließtext nur bei gerundeten Beträgen', () => {
    expect(rundMitHinweis(600_000, true)).toBe(`${RUND_PRAEFIX}${euro(600_000)}`)
    expect(rundMitHinweis(600_000, false)).toBe(euro(600_000))
  })

  it('rundKurz setzt „rund“ immer vor den gekürzten Betrag', () => {
    expect(rundKurz(30_455_569)).toBe(`${RUND_PRAEFIX}${euroKurz(30_455_569)}`)
  })
})
