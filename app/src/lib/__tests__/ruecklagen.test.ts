import { describe, expect, it } from 'vitest'

import { haushalt, texte } from '@/data/daten'
import type { Meta, VorberichtTabelle } from '@/data/typen'
import {
  abbau,
  ausgleichsruecklageAufgebrauchtJahr,
  baueRuecklagen,
  hskSchwellen,
  rueckgang,
} from '@/lib/ruecklagen'

const EIGENKAPITAL = haushalt.eigenkapital
const LETZTER_INDEX = haushalt.jahre.length - 1
const START_INDEX = haushalt.jahre.indexOf(haushalt.haushaltsjahr)

function posten(schluessel: string): (number | null)[] {
  const eintrag = EIGENKAPITAL.posten.find((kandidat) => kandidat.posten === schluessel)
  if (eintrag === undefined) {
    throw new Error(`Posten ${schluessel} fehlt in den Testdaten`)
  }
  return eintrag.werte
}

/** Eine Kopie der Tabelle mit einem veränderten Posten, für Randfälle. */
function mitPosten(schluessel: string, werte: (number | null)[]): VorberichtTabelle {
  return {
    ...EIGENKAPITAL,
    posten: EIGENKAPITAL.posten.map((eintrag) =>
      eintrag.posten === schluessel ? { ...eintrag, werte } : eintrag,
    ),
  }
}

describe('baueRuecklagen (ENTW-03, S. 311)', () => {
  const zeilen = baueRuecklagen()

  it('liefert je Jahr aus haushalt.jahre genau eine Zeile mit der Wertart aus den Daten', () => {
    expect(zeilen.map((zeile) => zeile.jahr)).toEqual(haushalt.jahre)
    expect(zeilen.map((zeile) => zeile.wertart)).toEqual(haushalt.wertarten)
  })

  it('übernimmt allgemeine Rücklage und Ausgleichsrücklage unverändert aus eigenkapital.posten', () => {
    expect(zeilen.map((zeile) => zeile.allgemeine)).toEqual(posten('allgemeine_ruecklage'))
    expect(zeilen.map((zeile) => zeile.ausgleich)).toEqual(posten('ausgleichsruecklage'))
  })

  it('summiert die beiden Rücklagen je Spalte zum Wert über der Säule', () => {
    for (const zeile of zeilen) {
      expect(zeile.summe).toBe((zeile.allgemeine ?? 0) + (zeile.ausgleich ?? 0))
    }
  })

  it('lässt einen fehlenden Wert null und eine echte 0 eine 0 bleiben', () => {
    const tabelle = mitPosten(
      'ausgleichsruecklage',
      haushalt.jahre.map((_jahr, index) => (index === 0 ? null : 0)),
    )
    const geprueft = baueRuecklagen(tabelle)
    expect(geprueft[0]?.ausgleich).toBeNull()
    expect(geprueft[1]?.ausgleich).toBe(0)
    expect(geprueft[0]?.summe).toBe(geprueft[0]?.allgemeine)
  })

  it('hat ohne beide Werte keine Summe', () => {
    const ohneAusgleich = mitPosten(
      'ausgleichsruecklage',
      haushalt.jahre.map(() => null),
    )
    const ohneBeide = {
      ...ohneAusgleich,
      posten: ohneAusgleich.posten.map((eintrag) =>
        eintrag.posten === 'allgemeine_ruecklage'
          ? { ...eintrag, werte: haushalt.jahre.map(() => null) }
          : eintrag,
      ),
    }
    expect(baueRuecklagen(ohneBeide).every((zeile) => zeile.summe === null)).toBe(true)
  })

  it('nennt einen fehlenden Posten beim Namen', () => {
    const ohne: VorberichtTabelle = {
      ...EIGENKAPITAL,
      posten: EIGENKAPITAL.posten.filter((eintrag) => eintrag.posten !== 'ausgleichsruecklage'),
    }
    expect(() => baueRuecklagen(ohne)).toThrow(/ausgleichsruecklage/)
  })

  it('erfüllt die S.-311-Arithmetik je Spalte: Σ der Posten = gedruckte Summe', () => {
    const summen = EIGENKAPITAL.gesamt_vorbericht.werte
    haushalt.jahre.forEach((_jahr, index) => {
      const gesamt =
        (posten('allgemeine_ruecklage')[index] ?? 0) +
        (posten('verrechnung_bilanzierungshilfe')[index] ?? 0) +
        (posten('ausgleichsruecklage')[index] ?? 0) +
        (posten('jahresergebnis')[index] ?? 0)
      expect(gesamt).toBe(summen[index])
    })
  })
})

describe('rueckgang (ENTW-03, S. 23)', () => {
  it('ist für jedes Jahr vor dem letzten das Gefälle zum Bestand des Folgejahres', () => {
    const allgemeine = posten('allgemeine_ruecklage')
    for (let index = 0; index < LETZTER_INDEX; index += 1) {
      const jetzt = allgemeine[index]
      const spaeter = allgemeine[index + 1]
      expect(jetzt).not.toBeNull()
      expect(spaeter).not.toBeNull()
      expect(abbau(index)).toBe((jetzt ?? 0) - (spaeter ?? 0))
    }
  })

  it('teilt den Abbau durch den Bestand zu Jahresbeginn', () => {
    const allgemeine = posten('allgemeine_ruecklage')
    for (let index = 0; index <= LETZTER_INDEX; index += 1) {
      expect(rueckgang(index)).toBeCloseTo((abbau(index) ?? 0) / (allgemeine[index] ?? 1), 12)
    }
  })

  it('gehört zu dem Jahr, dessen Spalte es berechnet (kein Versatz um ein Jahr, Pitfall 1)', () => {
    // Die Spalte des Haushaltsjahres trägt den ersten echten Rückgang; die Spalte davor keinen.
    expect(rueckgang(START_INDEX - 1)).toBe(0)
    expect(rueckgang(START_INDEX) ?? 0).toBeGreaterThan(0)
    // Das letzte Planjahr ist nicht ausgelassen.
    expect(rueckgang(LETZTER_INDEX) ?? 0).toBeGreaterThan(0)
  })

  it('hat ohne Bestand oder ohne Eingangswert keinen Rückgang statt NaN', () => {
    const ohneBestand = mitPosten(
      'allgemeine_ruecklage',
      haushalt.jahre.map(() => 0),
    )
    expect(rueckgang(START_INDEX, ohneBestand)).toBeNull()
    const ohneErgebnis = mitPosten(
      'jahresergebnis',
      haushalt.jahre.map(() => null),
    )
    expect(rueckgang(START_INDEX, ohneErgebnis)).toBeNull()
  })

  it('wirft für einen Index außerhalb der Jahre', () => {
    expect(() => rueckgang(haushalt.jahre.length)).toThrow(/Index/)
    expect(() => rueckgang(-1)).toThrow(/Index/)
  })

  describe.runIf(haushalt.haushaltsjahr === 2026)('gedruckte Werte der S. 23', () => {
    it('reproduziert 1,77 / 4,23 / 4,73 / 10,04 % auf zwei Nachkommastellen', () => {
      const geprueft = haushalt.jahre
        .slice(START_INDEX)
        .map(
          (_jahr, versatz) =>
            Math.round((rueckgang(START_INDEX + versatz) ?? Number.NaN) * 10000) / 100,
        )
      expect(geprueft).toEqual([1.77, 4.23, 4.73, 10.04])
    })
  })
})

describe('hskSchwellen (ENTW-03, D-14, S. 23)', () => {
  it('liest beide Schwellen als Anteil aus meta.vorbericht_werte, mit der Quellseite', () => {
    const werte = haushalt.meta.vorbericht_werte
    const ein = werte['hsk_schwelle_ein_jahr']
    const zwei = werte['hsk_schwelle_zwei_jahre']
    const schwellen = hskSchwellen()
    expect(schwellen.einJahr).toBe(Number(ein?.wert) / 100)
    expect(schwellen.zweiJahre).toBe(Number(zwei?.wert) / 100)
    expect(schwellen.pdfSeite).toBe(zwei?.quelle)
  })

  const meta = (ersatz: Record<string, unknown>): Meta => ({
    ...haushalt.meta,
    vorbericht_werte: { ...haushalt.meta.vorbericht_werte, ...ersatz } as Meta['vorbericht_werte'],
  })

  it('wirft, wenn ein Schlüssel fehlt, und nennt ihn', () => {
    const ohne = { ...haushalt.meta.vorbericht_werte }
    delete ohne['hsk_schwelle_zwei_jahre']
    expect(() => hskSchwellen({ ...haushalt.meta, vorbericht_werte: ohne })).toThrow(
      /hsk_schwelle_zwei_jahre/,
    )
  })

  it('wirft, wenn ein Wert keine Zahl ist', () => {
    expect(() =>
      hskSchwellen(
        meta({ hsk_schwelle_ein_jahr: { wert: 'viel', einheit: 'prozent', quelle: 23 } }),
      ),
    ).toThrow(/hsk_schwelle_ein_jahr/)
  })
})

describe('ausgleichsruecklageAufgebrauchtJahr (ENTW-03, D-14)', () => {
  it('ist das Jahr vor der ersten Spalte nach dem Haushaltsjahr mit Ausgleichsrücklage 0', () => {
    const ausgleich = posten('ausgleichsruecklage')
    const nullIndex = ausgleich.findIndex((wert, index) => index > START_INDEX && wert === 0)
    expect(nullIndex).toBeGreaterThan(START_INDEX)
    expect(ausgleichsruecklageAufgebrauchtJahr()).toBe((haushalt.jahre[nullIndex] ?? 0) - 1)
  })

  it('hat ohne Nullspalte kein Jahr', () => {
    const nieNull = mitPosten(
      'ausgleichsruecklage',
      haushalt.jahre.map(() => 1),
    )
    expect(ausgleichsruecklageAufgebrauchtJahr(nieNull)).toBeNull()
  })

  it('überspringt eine fehlende Spalte, statt sie als 0 zu lesen', () => {
    const luecke = mitPosten(
      'ausgleichsruecklage',
      haushalt.jahre.map((_jahr, index) => (index > START_INDEX ? null : 1)),
    )
    expect(ausgleichsruecklageAufgebrauchtJahr(luecke)).toBeNull()
  })

  it('stimmt mit der Pipeline-Regel (texte.werte) überein', () => {
    const wert = texte.werte['abgeleitet.ausgleichsruecklage_aufgebraucht_jahr']
    if (wert === undefined) {
      // Der Wert steht nur in texte.json, solange ein Text ihn nutzt.
      expect(ausgleichsruecklageAufgebrauchtJahr()).not.toBeUndefined()
      return
    }
    expect(ausgleichsruecklageAufgebrauchtJahr()).toBe(wert)
  })

  describe.runIf(haushalt.haushaltsjahr === 2026)('Haushalt 2026', () => {
    it('nennt das Jahr, an dessen Ende die Ausgleichsrücklage aufgebraucht ist', () => {
      expect(ausgleichsruecklageAufgebrauchtJahr()).toBe(2026)
    })
  })
})
