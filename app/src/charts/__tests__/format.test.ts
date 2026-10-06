import { describe, expect, it } from 'vitest'

import {
  anzahlText,
  datum,
  euro,
  euroKurz,
  formatiere,
  jahr,
  prozent,
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
