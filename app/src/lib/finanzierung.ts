// Verpflichtungsermächtigungen und Finanzierung für `/investitionen` (INV-02, INV-03, D-08, D-10).
// Gerüst für den RED-Schritt der TDD-Aufgabe: die Funktionen sind noch ohne Wirkung.

import type { EChartsOption } from 'echarts'

import type { VeFaelligkeit, Massnahme } from '@/data/typen'
import type { Tabelle } from '@/lib/produkt'

/** Eine Maßnahme mit Verpflichtungsermächtigung, die in einem Jahr fällig wird. */
export interface VeMassnahme {
  produkt: string
  massnahmeId: string
  name: string
  betrag: number
  pdfSeite: number
}

/** Die in einem Fälligkeitsjahr fälligen Verpflichtungsermächtigungen. */
export interface VeFaelligkeitsjahr {
  jahr: number
  betrag: number
  massnahmen: VeMassnahme[]
}

export function baueVeFaelligkeiten(
  _zeilen: readonly VeFaelligkeit[],
  _massnahmen: readonly Massnahme[],
): VeFaelligkeitsjahr[] {
  return []
}

export function veFaelligkeiten(): VeFaelligkeitsjahr[] {
  return []
}

export function veGesamt(): number {
  return 0
}

export function vePdfSeiten(): number[] {
  return []
}

export function veOption(_eintraege?: readonly VeFaelligkeitsjahr[]): EChartsOption {
  return { series: [] }
}

export function veTabelle(_eintraege?: readonly VeFaelligkeitsjahr[]): Tabelle {
  return { spalten: [], zeilen: [] }
}
