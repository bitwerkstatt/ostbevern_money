import type { InjectionKey } from 'vue'

export interface ChartKontext {
  titelId: string
  beschreibungId: () => string | undefined
}

export const CHART_KONTEXT: InjectionKey<ChartKontext> = Symbol('om-chart-kontext')
