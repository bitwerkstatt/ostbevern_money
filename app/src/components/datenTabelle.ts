/**
 * Zahlenart einer Spalte. `zahl` rundet auf ganze Zahlen, `dezimal` behält bis zu zwei
 * Nachkommastellen (Grundzahlen mit Gebühren oder Quoten, AUSG-05). `quelle` (Phase 7, D-01):
 * der Zellwert ist ein Belegschlüssel (`lib/quelle.ts`); `DatenTabelle` zeichnet daraus selbst
 * den Knopf „PDF-Seite {n}“.
 */
export type SpaltenArt = 'text' | 'euro' | 'zahl' | 'dezimal' | 'prozent' | 'quelle'

export interface DatenSpalte {
  schluessel: string
  titel: string
  art: SpaltenArt
}

export type DatenZeile = Readonly<Record<string, string | number | null>>

/**
 * Die Spalten, die eine Tabelle tatsächlich zeigt: Eine `quelle`-Spalte entfällt, solange keine
 * Zeile einen auflösbaren Beleg hat (kein leerer Spaltenkopf ohne einen einzigen Knopf); alle
 * anderen Spalten bleiben unverändert und in ihrer Reihenfolge. `hatBeleg` entscheidet je
 * Zellwert, ob er einen Beleg auflöst.
 */
export function sichtbareSpalten(
  spalten: readonly DatenSpalte[],
  zeilen: readonly DatenZeile[],
  hatBeleg: (wert: string | number | null) => boolean,
): readonly DatenSpalte[] {
  return spalten.filter(
    (spalte) =>
      spalte.art !== 'quelle' || zeilen.some((zeile) => hatBeleg(zeile[spalte.schluessel] ?? null)),
  )
}
