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

/**
 * Attribute des scrollbaren Tabellenrahmens (D-19, D-20, A11Y-01): Ein Rahmen, der waagerecht
 * scrollt, braucht Tastaturfokus, eine Rolle und einen Namen, und zwar immer zusammen (ein
 * Tabstopp ohne Rolle und Namen ist ein Verstoß, ein Name ohne Rolle ungültig). Der Name kommt
 * ausschließlich per `aria-labelledby` aus der Caption der Tabelle. Ohne Überlauf bekommt der
 * Rahmen nichts.
 */
export function rahmenAttribute(
  ueberlaeuft: boolean,
  captionId: string,
): Record<string, string | number> {
  if (!ueberlaeuft) {
    return {}
  }
  return { tabindex: 0, role: 'region', 'aria-labelledby': captionId }
}
