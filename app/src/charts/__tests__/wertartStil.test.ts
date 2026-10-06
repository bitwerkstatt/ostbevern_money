import { describe, expect, it } from 'vitest'

import { HOHL_FLAECHE } from '@/charts/echartsTheme'
import {
  LEGENDE_TEXT,
  LINIENSTILE,
  jahresAchse,
  linienSerie,
  saeulenStil,
} from '@/charts/wertartStil'
import { jahr } from '@/charts/format'
import { haushalt } from '@/data/daten'
import type { ZeitreihenSerie } from '@/lib/zeitreihen'

const FARBE = '#da7e00'

function serie(wertart: string): ZeitreihenSerie {
  return { wertart, werte: [1, 2, null], geteilt: [false, false, false] }
}

describe('LINIENSTILE', () => {
  it('kennt genau die Wertarten ergebnis, ansatz und planung', () => {
    expect([...LINIENSTILE.keys()].sort()).toEqual(['ansatz', 'ergebnis', 'planung'])
  })

  it('beschreibt die Stile in der Legende', () => {
    expect(LEGENDE_TEXT).toBe('durchgezogen: Ist · gestrichelt: Ansatz · gepunktet: Planung')
  })
})

describe('linienSerie', () => {
  it('wirft für eine unbekannte Wertart und nennt sie', () => {
    expect(() => linienSerie(serie('unbekannt'), FARBE, 'white')).toThrow(/unbekannt/)
  })

  it('zeichnet Ist gefüllt und Ansatz mit hohlem Marker in der übergebenen Farbe', () => {
    const ist = linienSerie(serie('ergebnis'), FARBE, 'white')
    expect(ist.lineStyle?.color).toBe(FARBE)
    expect(ist.itemStyle).toEqual({ color: FARBE })
    const ansatz = linienSerie(serie('ansatz'), FARBE, 'white')
    expect(ansatz.itemStyle).toEqual({ color: 'white', borderColor: FARBE, borderWidth: 2 })
    expect(ansatz.name).toBe('Ansatz')
  })

  it('lässt den übernommenen Punkt ohne Marker', () => {
    const geteilt: ZeitreihenSerie = {
      wertart: 'ansatz',
      werte: [5, 6],
      geteilt: [true, false],
    }
    expect(linienSerie(geteilt, FARBE, 'white').data).toEqual([{ value: 5, symbol: 'none' }, 6])
  })
})

describe('jahresAchse', () => {
  it('liefert je Jahr „<jahr>\\n<Wertart>“ aus den Haushaltsdaten', () => {
    const achse = jahresAchse(haushalt.jahre, haushalt.wertarten)
    const namen: Record<string, string> = { ergebnis: 'Ist', ansatz: 'Ansatz', planung: 'Planung' }
    expect(achse).toEqual(
      haushalt.jahre.map((j, i) => `${jahr(j)}\n${namen[haushalt.wertarten[i] ?? ''] ?? ''}`),
    )
    expect(achse.every((zeile) => zeile.split('\n').length === 2)).toBe(true)
  })

  it('hängt „berechnet“ genau dort an, wo das dritte Feld true ist', () => {
    const achse = jahresAchse([10, 11, 12], ['ansatz', 'planung', 'planung'], [false, true, true])
    expect(achse).toEqual(['10\nAnsatz', '11\nPlanung\nberechnet', '12\nPlanung\nberechnet'])
  })

  it('wirft, wenn die Längen nicht übereinstimmen', () => {
    expect(() => jahresAchse([10, 11], ['ansatz'])).toThrow()
    expect(() => jahresAchse([10], ['ansatz'], [true, false])).toThrow()
  })

  it('wirft für eine unbekannte Wertart', () => {
    expect(() => jahresAchse([10], ['unbekannt'])).toThrow(/unbekannt/)
  })
})

describe('saeulenStil', () => {
  it('zeichnet Planung hohl: Rand 2 px in der Farbe, Fläche HOHL_FLAECHE', () => {
    expect(saeulenStil('planung', FARBE)).toEqual({
      color: HOHL_FLAECHE,
      borderColor: FARBE,
      borderWidth: 2,
    })
  })

  it('füllt Ist und Ansatz mit der Farbe', () => {
    expect(saeulenStil('ergebnis', FARBE)).toEqual({ color: FARBE })
    expect(saeulenStil('ansatz', FARBE)).toEqual({ color: FARBE })
  })

  it('wirft für eine unbekannte Wertart', () => {
    expect(() => saeulenStil('unbekannt', FARBE)).toThrow(/unbekannt/)
  })
})
