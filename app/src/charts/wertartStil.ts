// Die eine Stiltabelle für Ist, Ansatz und Planung (UI-SPEC Chart Contract, „Wertart-Kennzeichnung
// auf Zeitachsen“): Linien unterscheiden die Wertart über Strichart und Marker, Säulen über die
// Fläche, die Zeitachse trägt sie als Text. Aus `SteuerZeitreihe.vue` herausgezogen, damit
// Steuer-Zeitreihe und die Diagramme der Phase 6 dieselbe Tabelle nutzen.

import type { BarSeriesOption, LineSeriesOption } from 'echarts'

import { HOHL_FLAECHE } from '@/charts/echartsTheme'
import { jahr as formatiereJahr } from '@/charts/format'
import { wertartName } from '@/lib/jahr'
import type { ZeitreihenSerie } from '@/lib/zeitreihen'

export interface Linienstil {
  linie: 'solid' | number[]
  symbol: 'circle' | 'diamond'
  gefuellt: boolean
}

// Ist durchgezogen mit gefülltem Kreis, Ansatz gestrichelt mit hohlem Kreis, Planung gepunktet
// mit hohler Raute: die Wertart ist ohne Farbe erkennbar.
export const LINIENSTILE: ReadonlyMap<string, Linienstil> = new Map([
  ['ergebnis', { linie: 'solid', symbol: 'circle', gefuellt: true }],
  ['ansatz', { linie: [6, 4], symbol: 'circle', gefuellt: false }],
  ['planung', { linie: [2, 4], symbol: 'diamond', gefuellt: false }],
])

/** Erklärt die Linienstile unter einem Diagramm. */
export const LEGENDE_TEXT = 'durchgezogen: Ist · gestrichelt: Ansatz · gepunktet: Planung'

/** Wort in der dritten Achsenzeile eines berechneten Jahres (INV-04). */
const BERECHNET_ZEILE = 'berechnet'

/** Randbreite hohler Säulen (UI-SPEC: Rand 2 px). */
const HOHL_RAND = 2

/** Fläche für hohle Marker (Ansatz, Planung): der Token der Kartenfläche, sonst Weiß. */
export function flaechenFarbe(): string {
  if (typeof document === 'undefined') {
    return 'white'
  }
  const wert = getComputedStyle(document.documentElement)
    .getPropertyValue('--wa-color-surface-default')
    .trim()
  return wert === '' ? 'white' : wert
}

/**
 * Eine Linienserie in der Farbe `farbe` mit dem Stil ihrer Wertart; `flaeche` füllt die hohlen
 * Marker. Eine unbekannte Wertart ist ein Datenfehler und wirft.
 */
export function linienSerie(
  serie: ZeitreihenSerie,
  farbe: string,
  flaeche: string,
): LineSeriesOption {
  const stil = LINIENSTILE.get(serie.wertart)
  if (stil === undefined) {
    throw new Error(`Kein Linienstil für die Wertart ${serie.wertart}`)
  }
  return {
    type: 'line',
    name: wertartName(serie.wertart),
    // Der von der vorigen Serie übernommene Punkt bleibt ohne Marker, damit er nicht doppelt
    // gezeichnet wird.
    data: serie.werte.map((wert, index) =>
      serie.geteilt[index] === true ? { value: wert, symbol: 'none' } : wert,
    ),
    connectNulls: false,
    symbol: stil.symbol,
    symbolSize: 8,
    lineStyle: { color: farbe, width: 2, type: stil.linie },
    itemStyle: stil.gefuellt
      ? { color: farbe }
      : { color: flaeche, borderColor: farbe, borderWidth: HOHL_RAND },
  }
}

/**
 * Die Beschriftungen der Jahresachse: je Jahr „{jahr}“ und darunter die Wertart („Ist“, „Ansatz“,
 * „Planung“). Ist `berechnet` gesetzt, folgt dort, wo der Wert `true` ist, eine dritte Zeile
 * „berechnet“. Die Zeilen sind durch `\n` getrennt (ECharts bricht daran um). Alle Felder müssen
 * gleich lang sein, sonst wirft die Funktion.
 */
export function jahresAchse(
  jahre: readonly number[],
  wertarten: readonly string[],
  berechnet?: readonly boolean[],
): string[] {
  if (wertarten.length !== jahre.length) {
    throw new Error(
      `Jahre (${String(jahre.length)}) und Wertarten (${String(wertarten.length)}) sind verschieden lang`,
    )
  }
  if (berechnet !== undefined && berechnet.length !== jahre.length) {
    throw new Error(
      `Jahre (${String(jahre.length)}) und berechnet (${String(berechnet.length)}) sind verschieden lang`,
    )
  }
  return jahre.map((jahr, index) => {
    const zeilen = [formatiereJahr(jahr), wertartName(wertarten[index] ?? '')]
    if (berechnet?.[index] === true) {
      zeilen.push(BERECHNET_ZEILE)
    }
    return zeilen.join('\n')
  })
}

/**
 * Säulenstil je Wertart: Ist und Ansatz voll in `farbe`, Planung hohl (Rand 2 px in `farbe`,
 * Fläche `HOHL_FLAECHE`). Eine unbekannte Wertart ist ein Datenfehler und wirft.
 */
export function saeulenStil(wertart: string, farbe: string): BarSeriesOption['itemStyle'] {
  if (!LINIENSTILE.has(wertart)) {
    throw new Error(`Kein Säulenstil für die Wertart ${wertart}`)
  }
  return wertart === 'planung'
    ? { color: HOHL_FLAECHE, borderColor: farbe, borderWidth: HOHL_RAND }
    : { color: farbe }
}
