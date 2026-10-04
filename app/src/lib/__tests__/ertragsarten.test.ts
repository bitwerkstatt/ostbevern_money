import { describe, expect, it } from 'vitest'

import { haushalt } from '@/data/daten'
import { baueErtragsarten } from '@/lib/ertragsarten'

const GESAMT = haushalt.ergebnisplan.GESAMT

describe('baueErtragsarten', () => {
  it.each(haushalt.jahre.map((j, i) => [j, i] as const))(
    'Jahr %i: Summe der Werte entspricht berechnet.ertraege, absteigend, ohne Nullwerte, Anteile = 100 %%',
    (_jahr, i) => {
      expect(GESAMT).toBeDefined()
      const reihen = baueErtragsarten(i)
      expect(reihen.length).toBeGreaterThan(0)

      const summeWerte = reihen.reduce((s, r) => s + r.wert, 0)
      expect(summeWerte).toBe(GESAMT?.berechnet.ertraege[i])

      for (const r of reihen) {
        expect(r.wert, r.schluessel).not.toBe(0)
        expect(r.name.length, r.schluessel).toBeGreaterThan(0)
      }
      for (let k = 1; k < reihen.length; k++) {
        expect(reihen[k - 1]!.wert).toBeGreaterThanOrEqual(reihen[k]!.wert)
      }

      const summeAnteile = reihen.reduce((s, r) => s + r.anteil, 0)
      expect(Math.abs(summeAnteile - 1)).toBeLessThanOrEqual(0.001)
    },
  )
})

describe.runIf(haushalt.haushaltsjahr === 2026)('Ertragsarten Haushalt 2026', () => {
  it('2026 liefert 7 Zeilen, größte Zeile sind die Steuern', () => {
    const reihen = baueErtragsarten(haushalt.jahre.indexOf(2026))
    expect(reihen).toHaveLength(7)
    expect(reihen[0]?.schluessel).toBe('steuern')
    expect(reihen[0]?.wert).toBe(18443000)
  })

  it('2024 liefert 8 Zeilen', () => {
    expect(baueErtragsarten(haushalt.jahre.indexOf(2024))).toHaveLength(8)
  })
})
