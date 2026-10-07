import { describe, expect, it } from 'vitest'

import { haushalt } from '@/data/daten'
import { einwohnerZahl } from '@/lib/einwohner'

describe('einwohnerZahl', () => {
  it('liefert ohne Argument die Einwohnerzahl aus haushalt.json', () => {
    expect(einwohnerZahl()).toBe(haushalt.meta.einwohner.wert)
  })

  it('liefert eine gültige Zahl unverändert', () => {
    expect(einwohnerZahl(11741)).toBe(11741)
  })

  it.each([
    ['null', null],
    ['undefined', undefined],
    ['ein Text', '11741'],
    ['NaN', Number.NaN],
    ['0', 0],
    ['eine negative Zahl', -5],
    ['unendlich', Number.POSITIVE_INFINITY],
  ])('wirft bei %s mit „fehlt in haushalt.json“ (TXT-06)', (_name, wert) => {
    expect(() => einwohnerZahl(wert)).toThrow(/fehlt in haushalt\.json/)
  })

  it('nennt den ungültigen Wert in der Meldung', () => {
    expect(() => einwohnerZahl('11741')).toThrow(/war 11741/)
  })
})
