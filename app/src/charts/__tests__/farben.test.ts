import { describe, expect, it } from 'vitest'

import { haushalt } from '@/data/daten'
import { PB_FARBEN, abstufung, farbeFuerPb } from '@/charts/echartsTheme'

// WCAG-2.x-Kontrast: relative Luminanz nach sRGB-Linearisierung.
function luminanz(hex: string): number {
  const kanaele = [1, 3, 5].map((start) => parseInt(hex.slice(start, start + 2), 16) / 255)
  const [r, g, b] = kanaele.map((c) => (c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4))
  return 0.2126 * (r ?? 0) + 0.7152 * (g ?? 0) + 0.0722 * (b ?? 0)
}

function kontrast(vordergrund: string, hintergrund: string): number {
  const hell = Math.max(luminanz(vordergrund), luminanz(hintergrund))
  const dunkel = Math.min(luminanz(vordergrund), luminanz(hintergrund))
  return (hell + 0.05) / (dunkel + 0.05)
}

const pbCodes = haushalt.knoten.filter((knoten) => knoten.ebene === 'PB').map((k) => k.code)

describe('PB_FARBEN (D-08)', () => {
  it('deckt jeden PB-Knoten der Haushaltsdaten ab (15 PB und KL)', () => {
    expect(pbCodes).toHaveLength(16)
    for (const code of pbCodes) {
      expect(farbeFuerPb(code), `Farbe fuer ${code}`).toMatch(/^#[0-9a-f]{6}$/i)
    }
  })

  it('enthaelt keinen Schluessel ausserhalb der PB-Codes', () => {
    expect(Object.keys(PB_FARBEN).sort()).toEqual([...pbCodes].sort())
  })

  it('vergibt jede Farbe genau einmal', () => {
    const farben = Object.values(PB_FARBEN).map((farbe) => farbe.toLowerCase())
    expect(new Set(farben).size).toBe(farben.length)
  })

  it('wirft bei einem unbekannten Code und nennt ihn', () => {
    expect(() => farbeFuerPb('99')).toThrow(/99/)
  })
})

describe('abstufung', () => {
  it('laesst Rang 0 unveraendert', () => {
    expect(abstufung('#424554', 0)).toBe('#424554')
  })

  it('dunkelt Rang 1 und 2 pro Kanal ab', () => {
    const rang1 = abstufung('#424554', 1)
    const rang2 = abstufung('#424554', 2)
    expect(rang1).toBe('#3b3e4c')
    expect(rang2).toBe('#353743')
  })

  it('wiederholt ab Rang 3', () => {
    expect(abstufung('#424554', 3)).toBe(abstufung('#424554', 0))
    expect(abstufung('#424554', 4)).toBe(abstufung('#424554', 1))
  })

  it('gibt Nicht-Hex-Eingaben unveraendert zurueck', () => {
    expect(abstufung('rgb(1, 2, 3)', 1)).toBe('rgb(1, 2, 3)')
  })

  it('erreicht fuer alle 16 Farben x 3 Stufen Kontrast >= 4,5:1 gegen Weiss', () => {
    for (const code of pbCodes) {
      for (const rang of [0, 1, 2]) {
        const farbe = abstufung(farbeFuerPb(code), rang)
        expect(
          kontrast(farbe, '#ffffff'),
          `${code} Rang ${rang} (${farbe})`,
        ).toBeGreaterThanOrEqual(4.5)
      }
    }
  })
})
