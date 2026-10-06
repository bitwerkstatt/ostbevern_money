import { describe, expect, it } from 'vitest'

import { euro, euroKurz } from '@/charts/format'
import { haushalt } from '@/data/daten'
import { baueKennzahlen } from '@/lib/kennzahlen'
import {
  baueErgebnisReihen,
  ergebnisBeschriftung,
  ergebnisTabelle,
  type Jahreswert,
} from '@/lib/entwicklung'

const GESAMT = haushalt.ergebnisplan['GESAMT']
const GESAMT_KNOTEN = haushalt.knoten.find((knoten) => knoten.code === 'GESAMT')

function zeile(schluessel: string): number[] {
  const werte = GESAMT?.zeilen[schluessel]
  if (werte === undefined) {
    throw new Error(`Zeile ${schluessel} fehlt in den Testdaten`)
  }
  return werte
}

function werte(reihe: readonly Jahreswert[]): (number | null)[] {
  return reihe.map((eintrag) => eintrag.wert)
}

describe('baueErgebnisReihen (ENTW-01, D-11)', () => {
  const reihen = baueErgebnisReihen()
  const alle = [
    reihen.ertraege,
    reihen.aufwendungen,
    reihen.ergebnisVor,
    reihen.minderaufwand,
    reihen.ergebnisNach,
  ]

  it.each([
    ['ertraege', reihen.ertraege],
    ['aufwendungen', reihen.aufwendungen],
    ['ergebnisVor', reihen.ergebnisVor],
    ['minderaufwand', reihen.minderaufwand],
    ['ergebnisNach', reihen.ergebnisNach],
  ] as const)('%s hat je Jahr aus haushalt.jahre genau einen Wert mit Wertart', (_name, reihe) => {
    expect(reihe.map((eintrag) => eintrag.jahr)).toEqual(haushalt.jahre)
    expect(reihe.map((eintrag) => eintrag.wertart)).toEqual(haushalt.wertarten)
    expect(reihe.every((eintrag) => !eintrag.gerundet)).toBe(true)
  })

  it('führt nie ein Jahr vor dem ersten Planjahr (D-12, keine Grundzahlen)', () => {
    const erstes = haushalt.jahre[0] ?? 0
    for (const reihe of alle) {
      expect(reihe.every((eintrag) => eintrag.jahr >= erstes)).toBe(true)
    }
  })

  it('nennt für jeden Wert die PDF-Seite des Gesamtergebnisplans', () => {
    const seite = GESAMT_KNOTEN?.pdf_seite
    expect(seite).toBeTypeOf('number')
    for (const reihe of alle) {
      expect(reihe.every((eintrag) => eintrag.pdfSeite === seite)).toBe(true)
    }
  })

  it('liest Erträge und Aufwendungen aus GESAMT.berechnet, vor dem globalen Minderaufwand', () => {
    expect(werte(reihen.ertraege)).toEqual(GESAMT?.berechnet.ertraege)
    expect(werte(reihen.aufwendungen)).toEqual(GESAMT?.berechnet.aufwand)
  })

  it('Ergebnis vor Minderaufwand ist die GEP-Zeile Jahresergebnis und gleicht Erträge minus Aufwendungen auf 1 € genau', () => {
    expect(werte(reihen.ergebnisVor)).toEqual(zeile('jahresergebnis'))
    reihen.ergebnisVor.forEach((eintrag, index) => {
      const differenz =
        (reihen.ertraege[index]?.wert ?? Number.NaN) -
        (reihen.aufwendungen[index]?.wert ?? Number.NaN)
      expect(Math.abs(differenz - (eintrag.wert ?? Number.NaN))).toBeLessThanOrEqual(1)
    })
  })

  it('Ergebnis nach Minderaufwand ist die GEP-Zeile und gleicht Ergebnis vor plus Minderaufwand', () => {
    expect(werte(reihen.ergebnisNach)).toEqual(zeile('ergebnis_nach_minderaufwand'))
    reihen.ergebnisNach.forEach((eintrag, index) => {
      const summe =
        (reihen.ergebnisVor[index]?.wert ?? Number.NaN) +
        (reihen.minderaufwand[index]?.wert ?? Number.NaN)
      expect(Math.abs(summe - (eintrag.wert ?? Number.NaN))).toBeLessThanOrEqual(1)
    })
  })

  it('führt den globalen Minderaufwand als positive Kürzung des Aufwands', () => {
    expect(werte(reihen.minderaufwand)).toEqual(
      zeile('globaler_minderaufwand').map((wert) => (wert === 0 ? 0 : -wert)),
    )
  })

  it('führt bei einem Minderaufwand von 0 eine echte Null, kein negatives Null', () => {
    const nullen = reihen.minderaufwand.filter((eintrag) => eintrag.wert === 0)
    expect(nullen.every((eintrag) => Object.is(eintrag.wert, 0))).toBe(true)
  })

  it('zeigt das Jahresergebnis des Haushaltsjahrs wie die Startseite (Satzung, Nutzerentscheidung 1)', () => {
    const index = haushalt.jahre.indexOf(haushalt.haushaltsjahr)
    const startseite = baueKennzahlen().find((kennzahl) => kennzahl.schluessel === 'ergebnis')
    expect(startseite).toBeDefined()
    expect(reihen.ergebnisNach[index]?.wert).toBe(startseite?.wert)
  })

  describe.runIf(haushalt.haushaltsjahr === 2026)('Sollwerte Haushalt 2026', () => {
    it('Ergebnis nach Minderaufwand: erstes Jahr +191.990 €, letztes Jahr −3.557.700 €', () => {
      expect(reihen.ergebnisNach[0]?.wert).toBe(191990)
      expect(reihen.ergebnisNach[reihen.ergebnisNach.length - 1]?.wert).toBe(-3557700)
    })

    it('Erträge im Haushaltsjahr: 27.502.063 €', () => {
      const index = haushalt.jahre.indexOf(haushalt.haushaltsjahr)
      expect(reihen.ertraege[index]?.wert).toBe(27502063)
    })
  })
})

describe('ergebnisBeschriftung (ENTW-01, Säulenbeschriftung)', () => {
  it('nennt ein negatives Ergebnis ein Defizit mit dem Betrag ohne Vorzeichen', () => {
    expect(ergebnisBeschriftung(-3557700)).toBe(`Defizit ${euroKurz(3557700)}`)
    expect(ergebnisBeschriftung(-3557700)).toBe('Defizit 3,56 Mio. €')
  })

  it('nennt ein positives Ergebnis einen Überschuss', () => {
    expect(ergebnisBeschriftung(191990)).toBe(`Überschuss ${euroKurz(191990)}`)
  })

  it('zeigt „–“ ohne Wert, nie „Defizit 0“', () => {
    expect(ergebnisBeschriftung(null)).toBe('–')
  })

  it('nennt ein Ergebnis von genau 0 weder Defizit noch Überschuss', () => {
    expect(ergebnisBeschriftung(0)).toBe(euroKurz(0))
  })

  it('nennt mit genau=true den Betrag auf den Euro genau (Tooltip)', () => {
    expect(ergebnisBeschriftung(-3557700, true)).toBe(`Defizit ${euro(3557700)}`)
    expect(ergebnisBeschriftung(191990, true)).toBe(`Überschuss ${euro(191990)}`)
  })
})

describe('ergebnisTabelle (ENTW-01, Tabelle zur Säule)', () => {
  const reihen = baueErgebnisReihen()
  const zeilen = ergebnisTabelle()

  it('hat je Jahr aus haushalt.jahre genau eine Zeile mit der Wertart des Jahres', () => {
    expect(zeilen.map((eintrag) => eintrag.jahr)).toEqual(haushalt.jahre)
    expect(zeilen.map((eintrag) => eintrag.wertart)).toEqual(haushalt.wertarten)
  })

  it('führt Erträge, Aufwendungen, Ergebnis vor Minderaufwand, Minderaufwand und Ergebnis nach Minderaufwand', () => {
    expect(zeilen.map((eintrag) => eintrag.ertraege)).toEqual(werte(reihen.ertraege))
    expect(zeilen.map((eintrag) => eintrag.aufwendungen)).toEqual(werte(reihen.aufwendungen))
    expect(zeilen.map((eintrag) => eintrag.ergebnisVor)).toEqual(werte(reihen.ergebnisVor))
    expect(zeilen.map((eintrag) => eintrag.minderaufwand)).toEqual(werte(reihen.minderaufwand))
    expect(zeilen.map((eintrag) => eintrag.ergebnisNach)).toEqual(werte(reihen.ergebnisNach))
  })

  it('Ergebnis nach Minderaufwand je Zeile gleicht Ergebnis vor plus Minderaufwand auf 1 € genau', () => {
    for (const eintrag of zeilen) {
      const summe = (eintrag.ergebnisVor ?? Number.NaN) + (eintrag.minderaufwand ?? Number.NaN)
      expect(Math.abs(summe - (eintrag.ergebnisNach ?? Number.NaN))).toBeLessThanOrEqual(1)
    }
  })
})

describe('Quelltext von lib/entwicklung.ts', () => {
  const quelltexte = import.meta.glob<string>('/src/lib/entwicklung.ts', {
    query: '?raw',
    import: 'default',
    eager: true,
  })

  it('enthält keine Jahreszahl im Code (Konvention: keine Jahrgangswerte)', () => {
    const quelltext = Object.values(quelltexte)[0] ?? ''
    expect(quelltext).not.toBe('')
    const ohneKommentare = quelltext
      .split('\n')
      .filter((zeilentext) => !/^\s*(\/\/|\*|\/\*)/.test(zeilentext))
      .join('\n')
    expect(ohneKommentare.match(/\b20\d{2}\b/g)).toBeNull()
  })
})
