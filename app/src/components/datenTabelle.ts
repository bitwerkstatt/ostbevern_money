export type SpaltenArt = 'text' | 'euro' | 'zahl' | 'prozent'

export interface DatenSpalte {
  schluessel: string
  titel: string
  art: SpaltenArt
}

export type DatenZeile = Readonly<Record<string, string | number | null>>
