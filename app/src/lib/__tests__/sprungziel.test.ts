import { describe, expect, it } from 'vitest'

import {
  elementFuerHash,
  scrollVersatz,
  sprungPosition,
  versatzAusScrollMargin,
} from '@/lib/sprungziel'

const ziel = { id: 'bindungsgrad' } as unknown as HTMLElement
const findeZiel = () => ziel
const findeNichts = () => null
const versatz96 = () => 96

describe('versatzAusScrollMargin', () => {
  it('liest eine Pixellaenge als Zahl', () => {
    expect(versatzAusScrollMargin('96px')).toBe(96)
    expect(versatzAusScrollMargin('24.5px')).toBe(24.5)
  })

  it('liefert 0 fuer 0px, leere und nicht auswertbare Werte', () => {
    expect(versatzAusScrollMargin('0px')).toBe(0)
    expect(versatzAusScrollMargin('')).toBe(0)
    expect(versatzAusScrollMargin('auto')).toBe(0)
  })

  it('scrollt nie ueber das Ziel hinaus: negative Werte werden 0', () => {
    expect(versatzAusScrollMargin('-8px')).toBe(0)
  })
})

describe('scrollVersatz', () => {
  it('liefert 0, wenn getComputedStyle fehlt (vitest unter Node)', () => {
    expect(typeof getComputedStyle).toBe('undefined')
    expect(scrollVersatz(ziel)).toBe(0)
  })
})

describe('elementFuerHash', () => {
  it('liefert ohne document null', () => {
    expect(typeof document).toBe('undefined')
    expect(elementFuerHash('#bindungsgrad')).toBeNull()
  })

  it('liefert fuer das nackte # null', () => {
    expect(elementFuerHash('#')).toBeNull()
    expect(elementFuerHash('')).toBeNull()
  })
})

describe('sprungPosition', () => {
  const nach = { path: '/glossar', hash: '#bindungsgrad' }
  const von = { path: '/produkt/030101' }

  it('liefert fuer ein Hash-Ziel exakt { el, top } mit dem Versatz', () => {
    expect(sprungPosition(nach, von, null, findeZiel, versatz96)).toEqual({
      el: ziel,
      top: 96,
    })
  })

  it('bleibt ein Sofortsprung: kein behavior-Schluessel', () => {
    const position = sprungPosition(nach, von, null, findeZiel, versatz96)
    expect(position).not.toHaveProperty('behavior')
  })

  it('liefert bei unbekanntem Hash ohne gespeicherte Position { top: 0 }', () => {
    expect(sprungPosition(nach, von, null, findeNichts, versatz96)).toEqual({ top: 0 })
  })

  it('gibt bei unbekanntem Hash die gespeicherte Position unveraendert zurueck', () => {
    const gespeichert = { left: 0, top: 500 }
    expect(sprungPosition(nach, von, gespeichert, findeNichts, versatz96)).toBe(gespeichert)
  })

  it('liefert bei reinem Query-Wechsel (gleicher Pfad, kein Ziel) false', () => {
    const gleich = { path: '/einnahmen', hash: '' }
    expect(sprungPosition(gleich, { path: '/einnahmen' }, null, findeNichts, versatz96)).toBe(false)
  })
})
