// Sichere HTML-Tooltips für ECharts (T-05-12): ECharts setzt den Rückgabewert
// eines `tooltip.formatter` als HTML ein. Jeder dynamische Text (Knotennamen
// aus den Daten, Beträge, Wertart) läuft deshalb durch `htmlSicher`; ein
// Tooltip wird nur aus `tooltipZeilen` gebaut, nie per Stringverkettung.

import { format } from 'echarts/core'

/** Maskiert `& < > " '` in einem Text, der in Tooltip-HTML eingesetzt wird. */
export function htmlSicher(text: string): string {
  return format.encodeHTML(text)
}

/** Maskierte Zeilen, durch `<br>` getrennt — der einzige Weg zu Tooltip-HTML. */
export function tooltipZeilen(zeilen: readonly string[]): string {
  return zeilen.map(htmlSicher).join('<br>')
}
