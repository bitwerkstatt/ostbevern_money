import { describe, expect, it } from 'vitest'

import { haushalt, texte } from '@/data/daten'
import type { Meta, VorberichtTabelle } from '@/data/typen'
import {
  abbau,
  ausgleichsruecklageAufgebrauchtJahr,
  baueRuecklagen,
  hskSchwellen,
  rueckgang,
  rueckgangAchsenMaximum,
  rueckgangFormelText,
  rueckgangPlanjahre,
  ruecklagenTabelle,
} from '@/lib/ruecklagen'

// Der Quelltext der Seite (wie in `menue.test.ts` über `?raw`): die Formelprosa der Fußnote darf nur
// in `ruecklagen.ts` stehen, die Seite ruft `rueckgangFormelText()` auf.
const seitenQuelltexte = import.meta.glob<string>('/src/pages/EntwicklungPage.vue', {
  query: '?raw',
  import: 'default',
  eager: true,
})
const seitenQuelltext = seitenQuelltexte['/src/pages/EntwicklungPage.vue'] ?? ''

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
      expect(zeile.allgemeine).not.toBeNull()
      expect(zeile.ausgleich).not.toBeNull()
      expect(zeile.summe).toBe((zeile.allgemeine as number) + (zeile.ausgleich as number))
    }
  })

  it('lässt einen fehlenden Wert null und eine echte 0 eine 0 bleiben', () => {
    const tabelle = mitPosten(
      'ausgleichsruecklage',
      haushalt.jahre.map((_jahr, index) => (index === 0 ? null : 0)),
    )
    const geprueft = baueRuecklagen(tabelle)
    expect(geprueft[0]?.ausgleich).toBeNull()
    expect(geprueft[0]?.summe).toBeNull()
    expect(geprueft[1]?.ausgleich).toBe(0)
    expect(geprueft[1]?.summe).toBe(geprueft[1]?.allgemeine)
  })

  it('zeigt ohne eine der beiden Rücklagen keine Teilsumme als Summe (WR-04)', () => {
    const allgemeine = posten('allgemeine_ruecklage')
    const tabelle = mitPosten(
      'allgemeine_ruecklage',
      allgemeine.map((wert, index) => (index === 0 ? null : wert)),
    )
    const geprueft = baueRuecklagen(tabelle)
    expect(geprueft[0]?.allgemeine).toBeNull()
    expect(geprueft[0]?.summe).toBeNull()
    geprueft.slice(1).forEach((zeile, versatz) => {
      expect(zeile.summe).toBe((allgemeine[versatz + 1] ?? Number.NaN) + (zeile.ausgleich ?? 0))
    })
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

describe('rueckgangFormelText (CR-01, S. 23)', () => {
  const VERRECHNUNG = 'verrechnung_bilanzierungshilfe'
  const verrechnungsWerte = posten(VERRECHNUNG)
  const datenHabenVerrechnung = verrechnungsWerte.some((wert) => wert !== null && wert !== 0)
  const verrechnungsName = EIGENKAPITAL.posten.find(
    (eintrag) => eintrag.posten === VERRECHNUNG,
  )?.name

  const ohneVerrechnung = mitPosten(
    VERRECHNUNG,
    haushalt.jahre.map(() => 0),
  )
  const verrechnungNull = mitPosten(
    VERRECHNUNG,
    haushalt.jahre.map(() => null),
  )
  const nurErsteSpalte = mitPosten(
    VERRECHNUNG,
    haushalt.jahre.map((_jahr, index) => (index === 0 ? -5 : 0)),
  )

  /**
   * Rückgang, nachgerechnet allein aus den Termen, die der Text nennt: das Defizit, soweit die
   * Ausgleichsrücklage es nicht deckt, plus (nur wenn der Text sie nennt) die Verrechnung, geteilt durch
   * die allgemeine Rücklage zu Jahresbeginn.
   */
  function nachgerechnet(tabelle: VorberichtTabelle, text: string, index: number): number {
    const wert = (schluessel: string): number => {
      const eintrag = tabelle.posten.find((kandidat) => kandidat.posten === schluessel)
      const einzel = eintrag?.werte[index]
      if (einzel === null || einzel === undefined) {
        throw new Error(`Testdaten: ${schluessel} ohne Wert an Index ${String(index)}`)
      }
      return einzel
    }
    const nenntVerrechnung = text.includes('Verrechnung')
    const abbau =
      Math.max(0, -wert('jahresergebnis') - wert('ausgleichsruecklage')) -
      (nenntVerrechnung ? wert(VERRECHNUNG) : 0)
    return abbau / wert('allgemeine_ruecklage')
  }

  it('nennt die Verrechnung samt Postenname aus den Daten genau dann, wenn ein Jahr sie ungleich 0 hat', () => {
    const text = rueckgangFormelText()
    expect(text.includes('Verrechnung')).toBe(datenHabenVerrechnung)
    if (datenHabenVerrechnung) {
      expect(verrechnungsName).toBeDefined()
      expect(text).toContain(verrechnungsName ?? '')
    }
  })

  describe.runIf(haushalt.haushaltsjahr === 2026)('Jahrgang 2026', () => {
    it('nennt die Verrechnung der Bilanzierungshilfe', () => {
      expect(datenHabenVerrechnung).toBe(true)
      expect(rueckgangFormelText()).toContain('Einmalige Verrechnung Bilanzierungshilfe')
    })

    it('ergäbe ohne den Verrechnungs-Term 0,56 % statt der gezeigten 1,77 % (Regressionsschutz CR-01)', () => {
      const ohneTerm = nachgerechnet(EIGENKAPITAL, '', START_INDEX)
      expect(Math.round(ohneTerm * 10000) / 100).toBe(0.56)
      expect(Math.round((rueckgang(START_INDEX) ?? Number.NaN) * 10000) / 100).toBe(1.77)
      expect(Math.round(ohneTerm * 10000) / 100).not.toBe(
        Math.round((rueckgang(START_INDEX) ?? Number.NaN) * 10000) / 100,
      )
    })
  })

  it('nennt die Verrechnung nicht, wenn alle Werte 0 sind', () => {
    expect(rueckgangFormelText(ohneVerrechnung)).not.toContain('Verrechnung')
  })

  it('nennt die Verrechnung nicht, wenn alle Werte fehlen', () => {
    expect(rueckgangFormelText(verrechnungNull)).not.toContain('Verrechnung')
  })

  it('nennt die Verrechnung auch, wenn nur eine Spalte vor dem Haushaltsjahr sie hat', () => {
    expect(rueckgangFormelText(nurErsteSpalte)).toContain('Verrechnung')
  })

  it('rechnet jedes Planjahr aus den im Text genannten Termen auf rueckgang() zurück (echte Daten)', () => {
    const text = rueckgangFormelText()
    for (let index = START_INDEX; index <= LETZTER_INDEX; index += 1) {
      expect(nachgerechnet(EIGENKAPITAL, text, index)).toBeCloseTo(
        rueckgang(index) ?? Number.NaN,
        12,
      )
    }
  })

  it('rechnet jedes Planjahr auch ohne Verrechnung aus den genannten Termen zurück', () => {
    const text = rueckgangFormelText(ohneVerrechnung)
    for (let index = START_INDEX; index <= LETZTER_INDEX; index += 1) {
      expect(nachgerechnet(ohneVerrechnung, text, index)).toBeCloseTo(
        rueckgang(index, ohneVerrechnung) ?? Number.NaN,
        12,
      )
    }
  })

  it('enthält keine Ziffer und endet mit einem Punkt', () => {
    for (const tabelle of [EIGENKAPITAL, ohneVerrechnung, verrechnungNull, nurErsteSpalte]) {
      const text = rueckgangFormelText(tabelle)
      expect(text).not.toMatch(/\d/)
      expect(text.endsWith('.')).toBe(true)
    }
  })

  it('wirft ohne den Posten und nennt seinen Schlüssel', () => {
    const ohne: VorberichtTabelle = {
      ...EIGENKAPITAL,
      posten: EIGENKAPITAL.posten.filter((eintrag) => eintrag.posten !== VERRECHNUNG),
    }
    expect(() => rueckgangFormelText(ohne)).toThrow(/verrechnung_bilanzierungshilfe/)
  })

  it('wird von EntwicklungPage.vue aufgerufen, die Formelprosa steht nicht in der Seite', () => {
    expect(seitenQuelltext).toContain('rueckgangFormelText(')
    expect(seitenQuelltext).not.toContain('soweit die Ausgleichsrücklage')
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

describe('rueckgangPlanjahre (ENTW-03, A7)', () => {
  it('hat je Jahr ab dem Haushaltsjahr einen Eintrag mit Wertart und Anteil', () => {
    const planjahre = rueckgangPlanjahre()
    expect(planjahre.map((eintrag) => eintrag.jahr)).toEqual(haushalt.jahre.slice(START_INDEX))
    expect(planjahre.map((eintrag) => eintrag.wertart)).toEqual(
      haushalt.wertarten.slice(START_INDEX),
    )
  })

  it('trägt je Eintrag den Rückgang der eigenen Spalte, ohne Versatz um ein Jahr', () => {
    rueckgangPlanjahre().forEach((eintrag, versatz) => {
      expect(eintrag.anteil).toBe(rueckgang(START_INDEX + versatz))
    })
  })

  it('führt kein Jahr vor dem Haushaltsjahr', () => {
    expect(rueckgangPlanjahre().some((eintrag) => eintrag.jahr < haushalt.haushaltsjahr)).toBe(
      false,
    )
  })

  it('lässt einen fehlenden Eingangswert null und nicht 0', () => {
    const ohneErgebnis = mitPosten(
      'jahresergebnis',
      haushalt.jahre.map(() => null),
    )
    expect(rueckgangPlanjahre(ohneErgebnis).every((eintrag) => eintrag.anteil === null)).toBe(true)
  })
})

describe('rueckgangAchsenMaximum (UI-SPEC E3 overflow)', () => {
  it('ist das 1,2-Fache des größeren aus Werten und Schwelle', () => {
    expect(rueckgangAchsenMaximum([0.02, 0.1], 0.05)).toBeCloseTo(0.12, 12)
    expect(rueckgangAchsenMaximum([0.01, 0.02], 0.05)).toBeCloseTo(0.06, 12)
  })

  it('hält die Schwelle ohne Werte im Diagramm', () => {
    expect(rueckgangAchsenMaximum([], 0.05)).toBeCloseTo(0.06, 12)
  })

  it('liegt für die Daten über Schwelle und jedem Wert', () => {
    const anteile = rueckgangPlanjahre().flatMap((eintrag) =>
      eintrag.anteil === null ? [] : [eintrag.anteil],
    )
    const schwelle = hskSchwellen().zweiJahre
    const maximum = rueckgangAchsenMaximum(anteile, schwelle)
    expect(maximum).toBeGreaterThan(schwelle)
    expect(maximum).toBeGreaterThan(Math.max(...anteile))
  })
})

describe('ruecklagenTabelle (ENTW-03)', () => {
  it('hat eine Zeile je Jahr mit Wertart, beiden Rücklagen und dem Rückgang', () => {
    const tabelle = ruecklagenTabelle()
    expect(tabelle.map((zeile) => zeile.jahr)).toEqual(haushalt.jahre)
    expect(tabelle.map((zeile) => zeile.wertart)).toEqual(haushalt.wertarten)
    expect(tabelle.map((zeile) => zeile.allgemeine)).toEqual(posten('allgemeine_ruecklage'))
    expect(tabelle.map((zeile) => zeile.ausgleich)).toEqual(posten('ausgleichsruecklage'))
  })

  it('führt den Rückgang erst ab dem Haushaltsjahr, davor null', () => {
    ruecklagenTabelle().forEach((zeile, index) => {
      expect(zeile.rueckgang).toBe(index < START_INDEX ? null : rueckgang(index))
    })
  })

  it('zeigt eine echte 0 der Ausgleichsrücklage als 0 und keinen Wert als null', () => {
    const mitLuecke = mitPosten(
      'ausgleichsruecklage',
      haushalt.jahre.map((_jahr, index) => (index === 0 ? null : 0)),
    )
    const zeilen = ruecklagenTabelle(mitLuecke)
    expect(zeilen[0]?.ausgleich).toBeNull()
    expect(zeilen[1]?.ausgleich).toBe(0)
  })
})
