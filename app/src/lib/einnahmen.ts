// Ebene 2 der Einnahmen-Seite (EINN-02 bis EINN-04, EINN-06). Rein lesend: Werte kommen aus
// `haushalt.vorbericht`, `haushalt.meta` und `haushalt.finanzplan`; nichts wird neu berechnet
// außer den beiden gekennzeichneten Resten „Sonstige“ (Vorbericht) und „Sonstige (berechnet)“
// (investive Einnahmen).

export interface PostenZeile {
  posten: string
  name: string
  wert: number | null
  gerundet: boolean
  berechnet: boolean
  quelle: number | null
  keinGeldfluss: boolean
}

export interface SteuerZeile extends PostenZeile {
  selbstFestgelegt: boolean
  hebesatz: number | null
  hebesatzQuelle: number | null
}

export interface SonstigeErtragZeile extends PostenZeile {
  teilVon: string | null
}

export type InvestiveGruppe = 'pauschale' | 'sonstige' | 'finanzplan'

export interface InvestiveZeile {
  schluessel: string
  name: string
  wert: number | null
  gerundet: boolean
  berechnet: boolean
  quelle: number | null
  gruppe: InvestiveGruppe
}

export const SELBST_FESTGELEGTE_STEUERN: readonly string[] = []
export const SONDERPOSTEN_POSTEN: readonly string[] = []
export const GEZEIGTE_PAUSCHALEN: readonly string[] = []

export function baueSteuern(_jahrIndex: number): SteuerZeile[] {
  return []
}

export function baueZuwendungen(_jahrIndex: number): PostenZeile[] {
  return []
}

export function baueSonstigeErtraege(_jahrIndex: number): SonstigeErtragZeile[] {
  return []
}

export function baueInvestiveEinnahmen(_jahrIndex: number): InvestiveZeile[] {
  return []
}

export type Aufschluesselung = 'steuern' | 'zuwendungen' | 'sonstige'

export const AUFSCHLUESSELUNG_FUER_ERTRAGSART: ReadonlyMap<string, Aufschluesselung> = new Map()

export function baueInvestiveTabelle(_jahrIndex: number): InvestiveZeile[] {
  return []
}

export function hatInvestiveWerte(_zeilen: readonly InvestiveZeile[]): boolean {
  return false
}
