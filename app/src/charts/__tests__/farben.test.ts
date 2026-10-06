import { afterEach, describe, expect, it, vi } from 'vitest'

import { haushalt } from '@/data/daten'
import {
  BERECHNET_DECAL,
  BINDUNG_FARBEN,
  HOHL_FLAECHE,
  KL_DECAL,
  PB_FARBEN,
  PUNKT_DECAL,
  SCHULDEN_FARBEN,
  SCHWELLE_FARBE,
  abstufung,
  farbeFuerPb,
  mitDeckkraft,
} from '@/charts/echartsTheme'

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

describe('mitDeckkraft (WR-03)', () => {
  afterEach(() => {
    vi.unstubAllGlobals()
  })

  it('rechnet Hex in rgba um', () => {
    expect(mitDeckkraft('#ffffff', 0.45)).toBe('rgba(255, 255, 255, 0.45)')
  })

  it('löst ein Farbschlüsselwort über die Zeichenfläche auf, statt es unverändert zu lassen', () => {
    const kontext = {
      canvas: { width: 0, height: 0 },
      fillStyle: '',
      clearRect: () => undefined,
      fillRect: () => undefined,
      getImageData: () => ({ data: [255, 255, 255, 255] }),
    }
    vi.stubGlobal('document', { createElement: () => ({ getContext: () => kontext }) })
    expect(mitDeckkraft('white', 0.55)).toBe('rgba(255, 255, 255, 0.55)')
    expect(kontext.fillStyle).toBe('white')
  })

  it('fällt ohne Auflösung auf color-mix zurück, nie auf die deckende Farbe', () => {
    expect(mitDeckkraft('white', 0.45)).toBe('color-mix(in srgb, white 45%, transparent)')
  })
})

describe('Farben der Phase 6 (UI-SPEC „Farbvergabe je Diagramm“)', () => {
  it('Bindungsgrad-Segmente erreichen gegen Weiß mindestens 3:1', () => {
    for (const [name, farbe] of Object.entries(BINDUNG_FARBEN)) {
      expect(farbe, name).toMatch(/^#[0-9a-f]{6}$/i)
      expect(kontrast(farbe, '#ffffff'), name).toBeGreaterThanOrEqual(3)
    }
    expect(Object.keys(BINDUNG_FARBEN)).toEqual(['pflichtig', 'teils', 'freiwillig'])
  })

  it('Schuldenfarben erreichen gegen Weiß mindestens 3:1', () => {
    for (const [name, farbe] of Object.entries(SCHULDEN_FARBEN)) {
      expect(farbe, name).toMatch(/^#[0-9a-f]{6}$/i)
      expect(kontrast(farbe, '#ffffff'), name).toBeGreaterThanOrEqual(3)
    }
    expect(SCHULDEN_FARBEN.investitionskredite).toBeDefined()
    expect(SCHULDEN_FARBEN.nrw_bank).toBeDefined()
  })

  it('Schwellenlinie erreicht gegen Weiß mindestens 3:1', () => {
    expect(SCHWELLE_FARBE).toMatch(/^#[0-9a-f]{6}$/i)
    expect(kontrast(SCHWELLE_FARBE, '#ffffff')).toBeGreaterThanOrEqual(3)
  })

  it('die Fläche hohler Säulen ist ein Hex-Wert und nicht Weiß (der Rand trägt den Kontrast)', () => {
    expect(HOHL_FLAECHE).toMatch(/^#[0-9a-f]{6}$/i)
    expect(HOHL_FLAECHE.toLowerCase()).not.toBe('#ffffff')
  })

  it('BERECHNET_DECAL unterscheidet sich von KL_DECAL und PUNKT_DECAL (senkrechte Streifen)', () => {
    expect(BERECHNET_DECAL).not.toEqual(KL_DECAL)
    expect(BERECHNET_DECAL).not.toEqual(PUNKT_DECAL)
    expect(BERECHNET_DECAL.symbol).toBe('rect')
    expect(BERECHNET_DECAL.rotation).toBe(Math.PI / 2)
    expect(BERECHNET_DECAL.rotation).not.toBe(KL_DECAL.rotation)
  })
})
