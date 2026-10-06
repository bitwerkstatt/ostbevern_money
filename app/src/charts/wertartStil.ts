// Gerüst für den TDD-Zyklus (RED): Signaturen ohne Verhalten, damit die Tests laden und an den
// Behauptungen scheitern, nicht am Modulimport. Die Umsetzung folgt im GREEN-Schritt.
import type { BarSeriesOption, LineSeriesOption } from 'echarts'

import type { ZeitreihenSerie } from '@/lib/zeitreihen'

export interface Linienstil {
  linie: 'solid' | number[]
  symbol: 'circle' | 'diamond'
  gefuellt: boolean
}

export const LINIENSTILE: ReadonlyMap<string, Linienstil> = new Map()

export const LEGENDE_TEXT = ''

export function linienSerie(
  _serie: ZeitreihenSerie,
  _farbe: string,
  _flaeche: string,
): LineSeriesOption {
  throw new Error('nicht implementiert')
}

export function jahresAchse(
  _jahre: readonly number[],
  _wertarten: readonly string[],
  _berechnet?: readonly boolean[],
): string[] {
  throw new Error('nicht implementiert')
}

export function saeulenStil(_wertart: string, _farbe: string): BarSeriesOption['itemStyle'] {
  throw new Error('nicht implementiert')
}
