// Horizontale Balken mit Direktbeschriftung (UI-SPEC „ErtragsBalken“, Chart Contract): eine
// Zeile je Eintrag, größter Wert oben, Beschriftung „{Betrag} · {Anteil}“ am Balkenende.
// Der Builder bekommt fertige Texte (`label`), formatiert also selbst keine Zahlen; nur die
// Achsenbeschriftung läuft über `euroKurz`. Tooltips entstehen ausschließlich über
// `tooltipZeilen` (T-05-25).

import type { BarSeriesOption, EChartsOption } from 'echarts'

import type { Decal } from '@/charts/echartsTheme'
import { euroKurz, KEIN_WERT } from '@/charts/format'
import { tooltipZeilen } from '@/charts/tooltip'

/** Eine Zeile des Balkendiagramms; `wert: null` bleibt als Zeile stehen und zeigt „–“. */
export interface BalkenZeile {
  schluessel: string
  name: string
  wert: number | null
  /** Fertige Beschriftung am Balkenende, z. B. „18,4 Mio. € · 54,5 %“. */
  label: string
  /** Eigene Balkenfarbe; ohne Angabe gilt `farbe` der Optionen. */
  farbe?: string
  decal?: Decal
}

export interface BalkenOptionen {
  /** Standardfarbe der Balken. */
  farbe: string
  /** Zweite Tooltip-Zeile, z. B. „Ansatz 2026“ (Wertart und Jahr, D-10). */
  wertartText: string
  /** Bis 699 px: Beschriftung zweizeilig, schmalerer Namensbereich. */
  schmal?: boolean
}

/** Zeilenhöhe in px (UI-SPEC E3 overflow). */
const ZEILENHOEHE = 40
/** Platz für Wertachse und Ränder in px (UI-SPEC E3 overflow). */
const RAHMENHOEHE = 48
/** Breite der Kategoriebeschriftung in px; längere Namen brechen um (UI-SPEC E3 long-text). */
const NAMEN_BREITE = 160
/** Schmalere Kategoriebeschriftung bis 699 px, damit neben der Beschriftung noch Balken bleiben. */
const NAMEN_BREITE_SCHMAL = 120
/** Geschätzte Zeichenbreite der 14-px-Beschriftung in px. */
const ZEICHENBREITE = 8
/** Abstand zwischen Balkenende und Beschriftung plus Sicherheitsrand in px. */
const BESCHRIFTUNGS_RAND = 16

/** Höhe des Diagramms für `anzahl` Zeilen: `anzahl × 40 px + 48 px`. */
export function balkenHoehe(anzahl: number): string {
  return `${String(anzahl * ZEILENHOEHE + RAHMENHOEHE)}px`
}

/** Beschriftung am Balkenende; ohne Wert „–“ statt der Zeilenbeschriftung (nie 0). */
export function balkenBeschriftung(zeile: BalkenZeile): string {
  return zeile.wert === null ? KEIN_WERT : zeile.label
}

/** Tooltip-HTML: Name, Betrag mit Anteil, Wertart mit Jahr — alles maskiert. */
export function balkenTooltip(zeile: BalkenZeile, wertartText: string): string {
  return tooltipZeilen([zeile.name, balkenBeschriftung(zeile), wertartText])
}

function zweizeilig(text: string): string {
  return text.replace(' · ', '\n')
}

/** Rechter Gitterrand: Platz für die längste Beschriftung neben dem längsten Balken. */
function rechterRand(texte: readonly string[]): number {
  const zeichen = texte
    .flatMap((text) => text.split('\n'))
    .reduce((laengste, zeile) => Math.max(laengste, zeile.length), 0)
  return Math.ceil(zeichen * ZEICHENBREITE) + BESCHRIFTUNGS_RAND
}

export function horizontaleBalkenOption(
  zeilen: readonly BalkenZeile[],
  optionen: BalkenOptionen,
): EChartsOption {
  const schmal = optionen.schmal === true
  const texte = zeilen.map((zeile) => {
    const text = balkenBeschriftung(zeile)
    return schmal ? zweizeilig(text) : text
  })

  const daten = zeilen.map((zeile) => ({
    name: zeile.name,
    // Eine fehlende Zahl zeichnet keinen Balken, behält aber die Zeile; ECharts beschriftet
    // einen Datenpunkt ohne Wert nicht, daher 0 mit der Beschriftung „–“.
    value: zeile.wert ?? 0,
    itemStyle: {
      color: zeile.farbe ?? optionen.farbe,
      ...(zeile.decal === undefined ? {} : { decal: zeile.decal }),
    },
  }))

  const serie: BarSeriesOption = {
    type: 'bar',
    data: daten,
    barCategoryGap: '30%',
    label: {
      show: true,
      position: 'right',
      formatter: (params) => texte[params.dataIndex] ?? KEIN_WERT,
      lineHeight: 17,
    },
  }

  return {
    grid: {
      left: 8,
      right: rechterRand(texte),
      top: 8,
      bottom: 8,
      // Entspricht `containLabel: true` (in ECharts 6 veraltet): Achsenbeschriftungen liegen
      // innerhalb des Gitters, lange Namen drücken die Balken nicht aus der Karte.
      outerBoundsMode: 'same',
      outerBoundsContain: 'axisLabel',
    },
    xAxis: {
      type: 'value',
      min: 0,
      splitNumber: 3,
      axisLabel: {
        formatter: (wert: number) => euroKurz(wert),
        hideOverlap: true,
      },
    },
    yAxis: {
      type: 'category',
      inverse: true,
      data: zeilen.map((zeile) => zeile.name),
      axisTick: { show: false },
      axisLabel: {
        width: schmal ? NAMEN_BREITE_SCHMAL : NAMEN_BREITE,
        overflow: 'break',
        interval: 0,
      },
    },
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        const eintrag = Array.isArray(params) ? params[0] : params
        const zeile = eintrag === undefined ? undefined : zeilen[eintrag.dataIndex]
        return zeile === undefined ? '' : balkenTooltip(zeile, optionen.wertartText)
      },
    },
    series: [serie],
  }
}
