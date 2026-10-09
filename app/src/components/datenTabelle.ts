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

/** Name der Tabelle, wenn der Aufrufer keine Beschriftung liefert (leer oder nur Leerzeichen). */
export const ERSATZ_BESCHRIFTUNG = 'Tabelle'

/** Was über den Rahmen einer `DatenTabelle` bekannt sein muss, um ihn auszustatten. */
export interface RahmenLage {
  /** Der Inhalt ist breiter als der Rahmen. */
  ueberlaeuft: boolean
  laedt: boolean
  /** Es gibt keine Zeilen (Leerzustand statt Tabelle). */
  leer: boolean
  beschriftung: string
}

export interface TabellenRahmen {
  /** Text der Caption und damit Name der Region. */
  name: string
  /** Attribute des scrollbaren Rahmens (siehe `rahmenAttribute`). */
  attribute: Record<string, string | number>
}

/**
 * Caption-Text und Rahmenattribute einer `DatenTabelle` (08/WR-01, 08/WR-02, A11Y-01, D-20):
 * Der Rahmen einer überlaufenden, gerenderten Tabelle bekommt immer Fokus, Rolle und Namen. Eine
 * leere oder aus Leerzeichen bestehende `beschriftung` fällt auf „Tabelle“ zurück, damit die
 * Tastaturbedienung (WCAG 2.1.1) nie davon abhängt, was ein Aufrufer übergibt. Ohne Überlauf, beim
 * Laden und im Leerzustand bleiben die Attribute leer.
 */
export function tabellenRahmen(lage: RahmenLage, captionId: string): TabellenRahmen {
  const gekuerzt = lage.beschriftung.trim()
  return {
    name: gekuerzt === '' ? ERSATZ_BESCHRIFTUNG : gekuerzt,
    attribute: rahmenAttribute(lage.ueberlaeuft && !lage.laedt && !lage.leer, captionId),
  }
}
