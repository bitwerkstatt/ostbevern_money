// ECharts-Theme für Ostbevern Money. Liest ausschließlich die Web-Awesome-
// Design-Tokens (--wa-color-*, --wa-font-family-body) zur Laufzeit via
// getComputedStyle — es gibt keine zweite, hart codierte Farbpalette.
// Diese Datei registriert beim Modul-Laden (Münster-Muster) den Renderer,
// die verwendeten Diagrammtypen und das Theme selbst.

import { registerTheme, use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'

use([CanvasRenderer, BarChart, GridComponent, TooltipComponent])

/**
 * Liest einen Web-Awesome-Token zur Laufzeit; fällt auf `ersatz` zurück,
 * wenn der Token (noch) leer ist oder kein DOM existiert (z. B. SSR/Tests).
 * `ersatz`-Werte sind aus der installierten Web-Awesome-CSS kopiert.
 */
function token(name: string, ersatz: string): string {
  if (typeof document === 'undefined') {
    return ersatz
  }
  const wert = getComputedStyle(document.documentElement).getPropertyValue(name).trim()
  return wert === '' ? ersatz : wert
}

export const CHART_THEME = 'ostbevern-money'

/** Kategorische Serienfarben: Ostbevern-Gold zuerst, dann Grautöne. */
export const KATEGORIE_FARBEN = [
  token('--wa-color-brand-60', '#da7e00'),
  token('--wa-color-neutral-40', '#545868'),
  token('--wa-color-neutral-60', '#9194a2'),
  token('--wa-color-neutral-80', '#c7c9d0'),
]

/** Sequenzielle Farben hell -> dunkel (Ostbevern-Gold-Verlauf). */
export const SEQUENZ_FARBEN = [
  token('--wa-color-brand-90', '#ffe495'),
  token('--wa-color-brand-80', '#fac22b'),
  token('--wa-color-brand-70', '#ef9d00'),
  token('--wa-color-brand-60', '#da7e00'),
  token('--wa-color-brand-50', '#b45f04'),
  token('--wa-color-brand-40', '#8c4602'),
]

/** Datensemantik: positiv/negativ/neutral — niemals als Kategorienfarbe genutzt. */
export const POL_FARBEN = {
  positiv: token('--wa-color-success-50', '#00883c'),
  negativ: token('--wa-color-danger-50', '#dc3146'),
  neutral: token('--wa-color-neutral-50', '#717584'),
}

registerTheme(CHART_THEME, {
  color: KATEGORIE_FARBEN,
  textStyle: {
    fontFamily: token('--wa-font-family-body', 'ui-sans-serif, system-ui, sans-serif'),
    color: token('--wa-color-text-normal', '#1a1d29'),
  },
  categoryAxis: {
    axisLine: { lineStyle: { color: token('--wa-color-text-quiet', '#545868') } },
    axisLabel: { color: token('--wa-color-text-quiet', '#545868') },
    splitLine: { lineStyle: { color: token('--wa-color-surface-border', '#dcdfe4') } },
  },
  valueAxis: {
    axisLine: { lineStyle: { color: token('--wa-color-text-quiet', '#545868') } },
    axisLabel: { color: token('--wa-color-text-quiet', '#545868') },
    splitLine: { lineStyle: { color: token('--wa-color-surface-border', '#dcdfe4') } },
  },
})
