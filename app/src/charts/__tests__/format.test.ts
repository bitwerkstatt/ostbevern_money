import { describe, expect, it } from 'vitest'

import { euro, euroKurz, formatiere, jahr, prozent } from '@/charts/format'

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
})
