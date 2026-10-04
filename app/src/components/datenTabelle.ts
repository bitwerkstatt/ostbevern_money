/**
 * Zahlenart einer Spalte. `zahl` rundet auf ganze Zahlen, `dezimal` behält bis zu zwei
 * Nachkommastellen (Grundzahlen mit Gebühren oder Quoten, AUSG-05).
 */
export type SpaltenArt = 'text' | 'euro' | 'zahl' | 'dezimal' | 'prozent'

export interface DatenSpalte {
  schluessel: string
  titel: string
  art: SpaltenArt
}

export type DatenZeile = Readonly<Record<string, string | number | null>>
