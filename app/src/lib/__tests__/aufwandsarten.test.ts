import { describe, expect, it } from 'vitest'

import { haushalt } from '@/data/daten'
import { ABSCHREIBUNG_ZEILE, baueAufwandsarten } from '@/lib/aufwandsarten'
import { zeilenName } from '@/lib/zeilen'

const JAHRE = haushalt.jahre.map((jahr, index) => [jahr, index] as const)
const GESAMT = haushalt.ergebnisplan['GESAMT']

function aufwand(index: number): number {
  const wert = GESAMT?.berechnet.aufwand[index]
  if (wert === undefined) {
    throw new Error(`Kein Aufwand im Jahresindex ${String(index)}`)
  }
  return wert
}

describe('baueAufwandsarten (AUSG-04)', () => {
  it.each(JAHRE)(
    'Jahr %i: die Aufwandsarten ergeben den Gesamtaufwand (Druckrundung höchstens 1 €)',
    (_jahr, i) => {
      const summe = baueAufwandsarten(i).reduce((s, art) => s + art.wert, 0)
      // Z. 17 „Ordentliche Aufwendungen“ ist im PDF gedruckt; in einzelnen Jahren weicht die
      // Summe der Zeilen 11–16 wegen der Druckrundung um 1 € davon ab (2024).
      expect(Math.abs(summe - aufwand(i))).toBeLessThanOrEqual(1)
    },
  )

  it.each(JAHRE.filter(([jahr]) => jahr !== 2024))(
    'Jahr %i: die Summe stimmt auf den Euro mit dem Gesamtaufwand überein',
    (_jahr, i) => {
      const summe = baueAufwandsarten(i).reduce((s, art) => s + art.wert, 0)
      expect(summe).toBe(aufwand(i))
    },
  )

  it.each(JAHRE)(
    'Jahr %i: absteigend sortiert, keine Nullzeilen, Anteile summieren sich',
    (_j, i) => {
      const arten = baueAufwandsarten(i)
      expect(arten.length).toBeGreaterThan(0)
      for (let k = 1; k < arten.length; k += 1) {
        expect(arten[k - 1]?.wert ?? 0).toBeGreaterThanOrEqual(arten[k]?.wert ?? 0)
      }
      for (const art of arten) {
        expect(art.wert, art.schluessel).not.toBe(0)
        expect(art.anteil, art.schluessel).toBeGreaterThan(0)
      }
      const summeAnteile = arten.reduce((s, art) => s + art.anteil, 0)
      expect(summeAnteile).toBeCloseTo(1, 5)
    },
  )

  it.each(JAHRE)('Jahr %i: Namen stammen aus zeilen_namen', (_j, i) => {
    for (const art of baueAufwandsarten(i)) {
      expect(art.name, art.schluessel).toBe(zeilenName('ergebnisplan', art.schluessel))
      expect(art.name.length).toBeGreaterThan(0)
    }
  })

  it.each(JAHRE)('Jahr %i: nur die Abschreibungen sind „kein Geldfluss“', (_j, i) => {
    const arten = baueAufwandsarten(i)
    const markiert = arten.filter((art) => art.keinGeldfluss)
    expect(markiert.map((art) => art.schluessel)).toEqual([ABSCHREIBUNG_ZEILE])
  })

  it('wählt die Zeilen 11–16 und 20, keine Summenzeilen', () => {
    const schluessel = baueAufwandsarten(0).map((art) => art.schluessel)
    const erlaubt = new Set(
      haushalt.zeilen_namen.ergebnisplan
        .filter(
          (zeile) =>
            !zeile.ist_summe &&
            ((zeile.nummer >= '11' && zeile.nummer <= '16') || zeile.nummer === '20'),
        )
        .map((zeile) => zeile.schluessel),
    )
    expect(erlaubt.size).toBe(7)
    for (const eintrag of schluessel) {
      expect(erlaubt.has(eintrag), eintrag).toBe(true)
    }
  })

  it('wirft bei einem Jahresindex außerhalb der Jahre', () => {
    expect(() => baueAufwandsarten(haushalt.jahre.length)).toThrow()
  })
})

describe.runIf(haushalt.haushaltsjahr === 2026)('Aufwandsarten Haushalt 2026', () => {
  it('sieben Zeilen, Summe 30.455.569 €, größte Zeile sind die Transferaufwendungen', () => {
    const i = haushalt.jahre.indexOf(2026)
    const arten = baueAufwandsarten(i)
    expect(arten).toHaveLength(7)
    expect(arten.reduce((s, art) => s + art.wert, 0)).toBe(30455569)
    expect(arten[0]?.schluessel).toBe('transferaufwendungen')
  })
})
