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
import type { Modus } from '@/lib/ansicht'
import { baueEbene } from '@/lib/drilldown'
import { ebenenBeleg } from '@/lib/ebenenBeleg'
import { findeKlKnoten } from '@/lib/kreisumlage'
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

const MODI: readonly Modus[] = ['aufwand', 'zuschussbedarf']
const WURZEL = 'GESAMT'

/** Alle Ebenen des Drilldowns: die Wurzel und jeder Knoten mit Kindern. */
function ebenenCodes(): string[] {
  const eltern = new Set(haushalt.knoten.flatMap((k) => (k.eltern === null ? [] : [k.eltern])))
  return [WURZEL, ...[...eltern].filter((code) => code !== WURZEL)]
}

describe('Ausgaben: jede Zeile des Drilldowns hat einen auflösbaren Beleg', () => {
  const kl = findeKlKnoten()

  haushalt.jahre.forEach((jahr, index) => {
    it.each(MODI)(`Jahr ${String(jahr)}, Modus %s`, (modus) => {
      const fehler: string[] = []
      let geprueft = 0
      for (const code of ebenenCodes()) {
        for (const eintrag of baueEbene(code, index, modus)) {
          geprueft += 1
          const beleg = ebenenBeleg(eintrag, index, modus)
          if (beleg === null || findeBeleg(beleg.schluessel) === null) {
            fehler.push(`${eintrag.code}: ${String(beleg?.schluessel)} löst nicht auf`)
            continue
          }
          if (modus === 'zuschussbedarf') {
            if (beleg.herleitung !== 'Aufwendungen minus Erträge') {
              fehler.push(`${eintrag.code}: Herleitung fehlt im Modus Zuschussbedarf`)
            }
          } else if (!eintrag.istKl) {
            const aufwand = haushalt.ergebnisplan[eintrag.code]?.berechnet.aufwand[index]
            const gedruckt =
              haushalt.ergebnisplan[eintrag.code]?.zeilen['ordentliche_aufwendungen']?.[index]
            if ((beleg.herleitung === null) !== (aufwand === gedruckt)) {
              fehler.push(`${eintrag.code}: Herleitung passt nicht zum Vergleich mit Z. 17`)
            }
          }
        }
      }
      expect(geprueft).toBeGreaterThan(50)
      expect(fehler, fehler.join('; ')).toEqual([])
    })
  })

  it.each(MODI)(
    'Modus %s: Knoten außerhalb von KL zeigen auf ep:{code}:ordentliche_aufwendungen',
    (modus) => {
      for (const code of ebenenCodes()) {
        for (const eintrag of baueEbene(code, 0, modus).filter((e) => !e.istKl)) {
          expect(ebenenBeleg(eintrag, 0, modus)?.schluessel, eintrag.code).toBe(
            `ep:${eintrag.code}:ordentliche_aufwendungen`,
          )
        }
      }
    },
  )

  it('KL-Unterposten zeigen auf ihren Vorbericht-Posten, KL selbst auf die Seite des Knotens', () => {
    expect(ebenenBeleg({ code: kl.code, istKl: true }, 0, 'aufwand')?.schluessel).toBe(
      `seite:${String(kl.pdf_seite)}`,
    )
    const unterposten = baueEbene(kl.code, 0, 'aufwand')
    expect(unterposten.length).toBeGreaterThan(0)
    for (const unter of unterposten) {
      const posten = unter.code.slice(kl.code.length + 1)
      expect(ebenenBeleg(unter, 0, 'aufwand')?.schluessel, unter.code).toBe(
        `vb:transferaufwendungen:${posten}`,
      )
    }
  })
})

describe('Ausgaben: Seitenquelltexte definieren keine Seitenspalte als Text', () => {
  it.each(['AusgabenPage.vue', 'EbenenTabelle.vue'])('%s nutzt art quelle', (datei) => {
    const text = quelltext(datei)
    expect(text).toContain("art: 'quelle'")
    expect(
      SEITENSPALTE_ALS_TEXT.test(text),
      `${datei} hat noch eine Textspalte für die Seite`,
    ).toBe(false)
  })

  it('AusgabenPage.vue nennt die Quelle-Spalte der Transferaufwendungen', () => {
    expect(quelltext('AusgabenPage.vue')).toContain("titel: 'Quelle', art: 'quelle'")
  })
})
