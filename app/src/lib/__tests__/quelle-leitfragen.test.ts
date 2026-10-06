// Abdeckung der Quelle-Spalten auf den beiden Leitfragen-Seiten (Phase 7, D-01, UI-02):
// Jede Tabellenzeile mit PDF-Seite auf /einnahmen und /ausgaben trägt einen Belegschlüssel, den
// `findeBeleg` auflöst und der auf dieselbe Seite zeigt; die Seitenquelltexte definieren keine
// Seitenspalte mehr als Text (es gibt genau eine Spalte „Quelle“ mit `art: 'quelle'`).

import { describe, expect, it } from 'vitest'

import { haushalt } from '@/data/daten'
import {
  baueInvestiveEinnahmen,
  baueInvestiveTabelle,
  baueSonstigeErtraege,
  baueSteuern,
  baueZuwendungen,
} from '@/lib/einnahmen'
import { findeBeleg } from '@/lib/quelle'
import { ZEITREIHEN_POSTEN, baueZeitreihe } from '@/lib/zeitreihen'

const quelltexte = import.meta.glob<string>('/src/**/*.vue', {
  query: '?raw',
  import: 'default',
  eager: true,
})

function quelltext(dateiname: string): string {
  const eintrag = Object.entries(quelltexte).find(([pfad]) => pfad.endsWith(`/${dateiname}`))
  if (eintrag === undefined) {
    throw new Error(`Quelltext ${dateiname} nicht gefunden`)
  }
  return eintrag[1]
}

/** Eine Spaltendefinition mit Titel „PDF-Seite“ oder „Quelle“, deren Art `text` ist. */
const SEITENSPALTE_ALS_TEXT =
  /titel:\s*(?:'(?:PDF-Seite|Quelle)'|"(?:PDF-Seite|Quelle)")[^}]*art:\s*'text'/

function fehlendeBelege(
  zeilen: readonly { beleg: string | null; quelle: number | null }[],
  bezeichnung: (index: number) => string,
): string[] {
  const fehler: string[] = []
  zeilen.forEach((zeile, index) => {
    if (zeile.quelle === null) {
      return
    }
    const beleg = zeile.beleg === null ? null : findeBeleg(zeile.beleg)
    if (beleg === null) {
      fehler.push(`${bezeichnung(index)}: Schlüssel ${String(zeile.beleg)} löst nicht auf`)
    } else if (beleg.pdfSeite !== zeile.quelle) {
      fehler.push(`${bezeichnung(index)}: Beleg zeigt auf S. ${String(beleg.pdfSeite)}`)
    }
  })
  return fehler
}

describe('Einnahmen: jede Tabellenzeile mit Seite hat einen auflösbaren Beleg', () => {
  haushalt.jahre.forEach((jahr, index) => {
    it(`Aufschlüsselungen und investive Einnahmen ${String(jahr)}`, () => {
      const gruppen = [
        ['Steuern', baueSteuern(index)],
        ['Zuwendungen', baueZuwendungen(index)],
        ['Sonstige Erträge', baueSonstigeErtraege(index)],
        ['Investive Tabelle', baueInvestiveTabelle(index)],
        ['Investive Einnahmen', baueInvestiveEinnahmen(index)],
      ] as const
      const fehler = gruppen.flatMap(([name, zeilen]) =>
        fehlendeBelege(zeilen, (i) => `${name}[${String(i)}]`),
      )
      expect(fehler, fehler.join('; ')).toEqual([])
    })
  })

  it('Steuer-Zeitreihe: jeder Punkt aller Posten hat einen auflösbaren Beleg', () => {
    const fehler = ZEITREIHEN_POSTEN.flatMap((eintrag) =>
      fehlendeBelege(
        baueZeitreihe(eintrag.posten).map((punkt) => ({
          beleg: punkt.beleg,
          quelle: punkt.pdfSeite,
        })),
        (i) => `${eintrag.posten}[${String(i)}]`,
      ),
    )
    expect(fehler, fehler.join('; ')).toEqual([])
  })

  it('der Test erkennt einen Schlüssel, den findeBeleg nicht auflöst', () => {
    const fehler = fehlendeBelege([{ beleg: 'vb:steuerarten:erfunden', quelle: 27 }], () => 'x')
    expect(fehler).toHaveLength(1)
  })
})

describe('Einnahmen: Seitenquelltexte definieren keine Seitenspalte als Text', () => {
  it.each(['EinnahmenPage.vue', 'SteuerZeitreihe.vue'])('%s nutzt art quelle', (datei) => {
    const text = quelltext(datei)
    expect(text).toContain("art: 'quelle'")
    expect(
      SEITENSPALTE_ALS_TEXT.test(text),
      `${datei} hat noch eine Textspalte für die Seite`,
    ).toBe(false)
    expect(text).not.toMatch(/`PDF-Seite \$\{/)
  })

  it('der Quelltext-Test erkennt eine Textspalte „Quelle“', () => {
    expect(
      SEITENSPALTE_ALS_TEXT.test("{ schluessel: 'quelle', titel: 'Quelle', art: 'text' }"),
    ).toBe(true)
  })
})
