import { describe, expect, it } from 'vitest'

import { euro, euroKurz, prozent } from '@/charts/format'
import { haushalt } from '@/data/daten'
import { baueAufwandsarten } from '@/lib/aufwandsarten'
import { baueKennzahlen } from '@/lib/kennzahlen'
import { baueKreisumlage } from '@/lib/kreisumlage'
import { baueZeitreihe } from '@/lib/zeitreihen'
import { findeText } from '@/lib/texte'
import {
  ENTWICKLUNG_POSTEN,
  baueErgebnisReihen,
  bauePostenReihe,
  ergebnisBeschriftung,
  ergebnisTabelle,
  postenFussnote,
  veraenderung,
  veraenderungText,
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

function jw(jahr: number, wert: number | null): Jahreswert {
  return { jahr, wert, wertart: 'planung', pdfSeite: 1, gerundet: false }
}

const POSTEN_SCHLUESSEL = ENTWICKLUNG_POSTEN.map((posten) => posten.schluessel)

describe('ENTWICKLUNG_POSTEN (ENTW-02, D-12)', () => {
  it('führt genau die fünf Posten in der Reihenfolge der Seite', () => {
    expect(POSTEN_SCHLUESSEL).toEqual([
      'kreisumlage',
      'gewerbesteuer',
      'schluesselzuweisung',
      'personal',
      'zinsen',
    ])
    expect(ENTWICKLUNG_POSTEN.map((posten) => posten.titel)).toEqual([
      'Kreisumlage',
      'Gewerbesteuer',
      'Schlüsselzuweisung',
      'Personalaufwand',
      'Zinsen',
    ])
  })

  it('nur die Kreisumlage trägt einen Erklärtext, und der steht in texte.json (Pitfall 6)', () => {
    const mitText = ENTWICKLUNG_POSTEN.filter((posten) => posten.erklaertext !== null)
    expect(mitText.map((posten) => posten.schluessel)).toEqual(['kreisumlage'])
    expect(findeText(mitText[0]?.erklaertext ?? '')).toBeDefined()
  })
})

describe('bauePostenReihe (ENTW-02, D-12, D-13)', () => {
  it.each(POSTEN_SCHLUESSEL)(
    '%s hat je Jahr aus haushalt.jahre genau einen Punkt, nie ein Grundzahl-Jahr',
    (schluessel) => {
      const reihe = bauePostenReihe(schluessel)
      expect(reihe.map((eintrag) => eintrag.jahr)).toEqual(haushalt.jahre)
      expect(reihe.map((eintrag) => eintrag.wertart)).toEqual(haushalt.wertarten)
      expect(reihe.every((eintrag) => eintrag.jahr >= (haushalt.jahre[0] ?? 0))).toBe(true)
    },
  )

  it.each(['gewerbesteuer', 'schluesselzuweisung'])(
    '%s gleicht der Zeitreihe von /einnahmen in den Planjahren',
    (schluessel) => {
      const erwartet = baueZeitreihe(schluessel).filter(
        (punkt) => punkt.jahr >= (haushalt.jahre[0] ?? 0),
      )
      const reihe = bauePostenReihe(schluessel)
      expect(reihe.length).toBeGreaterThan(0)
      expect(reihe.map((eintrag) => eintrag.wert)).toEqual(erwartet.map((punkt) => punkt.wert))
      expect(reihe.map((eintrag) => eintrag.gerundet)).toEqual(
        erwartet.map((punkt) => punkt.gerundet),
      )
      expect(reihe.map((eintrag) => eintrag.pdfSeite)).toEqual(
        erwartet.map((punkt) => punkt.pdfSeite),
      )
    },
  )

  it('Kreisumlage gleicht dem Unterposten Kreisumlage der Weitergabe an Kreis und Land (wie /ausgaben)', () => {
    const reihe = bauePostenReihe('kreisumlage')
    expect(reihe.length).toBeGreaterThan(0)
    reihe.forEach((eintrag, index) => {
      const unterposten = baueKreisumlage(index).unterposten.find(
        (posten) => posten.code === 'KL.kreisumlage',
      )
      expect(unterposten).toBeDefined()
      expect(eintrag.wert).toBe(unterposten?.wert)
      expect(eintrag.gerundet).toBe(unterposten?.gerundet)
    })
  })

  it.each([
    ['personal', 'personalaufwendungen'],
    ['zinsen', 'zinsaufwendungen'],
  ])('%s gleicht der GEP-Zeile %s und der Aufwandsart von /ausgaben', (schluessel, zeilenname) => {
    const reihe = bauePostenReihe(schluessel)
    expect(reihe.map((eintrag) => eintrag.wert)).toEqual(zeile(zeilenname))
    expect(reihe.every((eintrag) => !eintrag.gerundet)).toBe(true)
    expect(reihe.every((eintrag) => eintrag.pdfSeite === GESAMT_KNOTEN?.pdf_seite)).toBe(true)
    reihe.forEach((eintrag, index) => {
      const art = baueAufwandsarten(index).find(
        (eintragsart) => eintragsart.schluessel === zeilenname,
      )
      expect(art?.wert).toBe(eintrag.wert)
    })
  })

  it('wirft bei einem unbekannten Posten mit dessen Namen', () => {
    expect(() => bauePostenReihe('gibt_es_nicht')).toThrow('gibt_es_nicht')
  })

  describe.runIf(haushalt.haushaltsjahr === 2026)('Sollwerte Haushalt 2026', () => {
    it('Kreisumlage steigt vom ersten zum letzten Planjahr um rund 14,2 %', () => {
      expect(veraenderung(bauePostenReihe('kreisumlage'))).toBeCloseTo(0.142, 3)
    })
  })
})

describe('veraenderung (ENTW-02, D-13)', () => {
  it('ist (letzter − erster) / erster', () => {
    expect(veraenderung([jw(1, 100), jw(2, 150), jw(3, 125)])).toBeCloseTo(0.25, 10)
    expect(veraenderung([jw(1, 200), jw(2, 150)])).toBeCloseTo(-0.25, 10)
  })

  it('ist null, wenn der Ausgangswert 0 ist (nie ∞ %)', () => {
    expect(veraenderung([jw(1, 0), jw(2, 150)])).toBeNull()
  })

  it('ist null, wenn der Ausgangswert fehlt', () => {
    expect(veraenderung([jw(1, null), jw(2, 150)])).toBeNull()
  })

  it('ist null, wenn der Endwert fehlt (nie NaN)', () => {
    expect(veraenderung([jw(1, 100), jw(2, null)])).toBeNull()
  })

  it('ist null ohne Punkte', () => {
    expect(veraenderung([])).toBeNull()
  })

  it('ist 0 bei gleichem Anfangs- und Endwert', () => {
    expect(veraenderung([jw(1, 100), jw(2, 100)])).toBe(0)
  })
})

describe('veraenderungText (ENTW-02, D-13)', () => {
  it('setzt ein Plus vor einen Anstieg und nutzt das Minuszeichen für einen Rückgang', () => {
    expect(veraenderungText(0.142)).toBe(`+${prozent(0.142)}`)
    expect(veraenderungText(-0.25)).toBe(`−${prozent(0.25)}`)
  })

  it('zeigt „–“ ohne Wert', () => {
    expect(veraenderungText(null)).toBe('–')
  })

  it('zeigt keine Richtung, wenn die Veränderung auf eine Nachkommastelle 0 ergibt', () => {
    expect(veraenderungText(0)).toBe(prozent(0))
    expect(veraenderungText(0.0001)).toBe(prozent(0))
    expect(veraenderungText(-0.0001)).toBe(prozent(0))
  })
})

describe('postenFussnote (ENTW-02, Quelle je Karte)', () => {
  it('nennt für einen Vorbericht-Posten Vorbericht und die PDF-Seite', () => {
    const posten = ENTWICKLUNG_POSTEN.find((eintrag) => eintrag.schluessel === 'gewerbesteuer')
    expect(posten).toBeDefined()
    if (posten === undefined) {
      return
    }
    const reihe = bauePostenReihe(posten.schluessel)
    expect(postenFussnote(posten, reihe)).toBe(
      `Quelle: Vorbericht, PDF-Seite ${String(reihe[0]?.pdfSeite)}`,
    )
  })

  it('nennt für eine GEP-Zeile den Gesamtergebnisplan und die PDF-Seite', () => {
    const posten = ENTWICKLUNG_POSTEN.find((eintrag) => eintrag.schluessel === 'personal')
    expect(posten).toBeDefined()
    if (posten === undefined) {
      return
    }
    const reihe = bauePostenReihe(posten.schluessel)
    expect(postenFussnote(posten, reihe)).toBe(
      `Quelle: Gesamtergebnisplan, PDF-Seite ${String(reihe[0]?.pdfSeite)}`,
    )
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
