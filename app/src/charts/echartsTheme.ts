// ECharts-Theme für Ostbevern Money. Liest ausschließlich die Web-Awesome-
// Design-Tokens (--wa-color-*, --wa-font-family-body) zur Laufzeit via
// getComputedStyle — es gibt keine zweite, hart codierte Farbpalette.
// Diese Datei registriert beim Modul-Laden (Münster-Muster) den Renderer,
// die verwendeten Diagrammtypen und das Theme selbst.

import { registerTheme, use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart, SankeyChart, TreemapChart } from 'echarts/charts'
import { AriaComponent, GridComponent, LegendComponent, TooltipComponent } from 'echarts/components'
import type { TreemapSeriesOption } from 'echarts'

/** Decal-Muster eines Datenpunkts (ECharts exportiert den Typ nicht unter eigenem Namen). */
export type Decal = Exclude<
  NonNullable<NonNullable<TreemapSeriesOption['itemStyle']>['decal']>,
  'none'
>

// Einzige Stelle, die `use()` aufruft: nur hier registrierte Module stehen den
// Diagrammen zur Verfügung (Treemap/Balken/Sankey/Linie, Legende, Aria).
use([
  CanvasRenderer,
  BarChart,
  LineChart,
  SankeyChart,
  TreemapChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  AriaComponent,
])

/**
 * Liest einen Web-Awesome-Token zur Laufzeit; fällt auf `ersatz` zurück,
 * wenn der Token (noch) leer ist oder kein DOM existiert (z. B. SSR/Tests).
 * `ersatz`-Werte sind aus der installierten Web-Awesome-CSS kopiert.
 *
 * ACHTUNG: `ersatz`-Werte sind eine manuelle Kopie der installierten
 * Web-Awesome-CSS. Sie werden nur einmal beim Modul-Laden gelesen und
 * NICHT automatisch aktualisiert, falls sich die CSS-Variablen später
 * ändern (z. B. durch eine künftige Theme-Umschaltung). Bei Divergenz
 * zwischen CSS und `ersatz` beide Stellen von Hand synchron halten.
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

/**
 * Aufgabenbereich-Palette (D-08): eine feste Farbe je PB-Code (15 Produktbereiche
 * plus KL), identisch in Treemap, Balken, Sankey und Mobil-Balken. Nur die Töne
 * 30/40/50 der WA-Hues; kein Gold (Akzent), kein Rot/Grün (Datensemantik).
 * Jede Farbe erreicht gegen Weiß mindestens 4,5:1 (siehe farben.test.ts).
 */
export const PB_FARBEN: Readonly<Record<string, string>> = {
  '01': token('--wa-color-gray-30', '#424554'),
  '02': token('--wa-color-gray-40', '#545868'),
  '16': token('--wa-color-gray-50', '#717584'),
  '03': token('--wa-color-indigo-30', '#3933a7'),
  '04': token('--wa-color-indigo-40', '#4945cb'),
  '08': token('--wa-color-indigo-50', '#6163f2'),
  '05': token('--wa-color-blue-30', '#003f9c'),
  '06': token('--wa-color-blue-40', '#0053c0'),
  '12': token('--wa-color-blue-50', '#0071ec'),
  '09': token('--wa-color-cyan-30', '#014c5b'),
  '10': token('--wa-color-cyan-40', '#026274'),
  '11': token('--wa-color-cyan-50', '#078098'),
  '13': token('--wa-color-purple-30', '#612692'),
  '14': token('--wa-color-purple-40', '#7936b3'),
  '15': token('--wa-color-purple-50', '#9951db'),
  KL: token('--wa-color-pink-40', '#9e2a6c'),
}

/** Farbe der Kachel „Weitergabe an Kreis und Land“ (immer mit `KL_DECAL`). */
export const KL_FARBE = PB_FARBEN['KL'] ?? token('--wa-color-pink-40', '#9e2a6c')

/** Farbe eines Produktbereichs; wirft bei unbekanntem Code, statt still eine Ersatzfarbe zu liefern. */
export function farbeFuerPb(code: string): string {
  const farbe = PB_FARBEN[code]
  if (farbe === undefined) {
    throw new Error(`Keine Aufgabenbereich-Farbe für den Code „${code}“`)
  }
  return farbe
}

const ABSTUFUNG_ANTEILE = [0, 0.1, 0.2] as const

/**
 * Dunkelt eine Hex-Farbe (#rrggbb) für Geschwisterkacheln ab (D-08): Rang 0
 * unverändert, Rang 1 zu 10 %, Rang 2 zu 20 % mit Schwarz gemischt, danach
 * wiederholt. Es wird nur abgedunkelt, nie aufgehellt (Kontrast zu weißer
 * Beschriftung wächst). Andere Farbformate kommen unverändert zurück.
 */
export function abstufung(farbe: string, rang: number): string {
  if (!/^#[0-9a-f]{6}$/i.test(farbe)) {
    return farbe
  }
  const anteil = ABSTUFUNG_ANTEILE[((rang % 3) + 3) % 3] ?? 0
  const kanaele = [1, 3, 5].map((start) => {
    const kanal = Math.round(parseInt(farbe.slice(start, start + 2), 16) * (1 - anteil))
    return kanal.toString(16).padStart(2, '0')
  })
  return `#${kanaele.join('')}`
}

/**
 * Löst eine beliebige CSS-Farbe (Schlüsselwort wie `white`, `rgb()`, `oklch()` …) zu RGB auf,
 * indem der Browser sie auf eine 1×1-Zeichenfläche malt. Ohne DOM oder Zeichenfläche `null`.
 * Die Web-Awesome-Tokens sind nicht immer Hex (`--wa-color-surface-default` ist `white`).
 */
function alsRgb(farbe: string): [number, number, number] | null {
  if (typeof document === 'undefined') {
    return null
  }
  const kontext = document.createElement('canvas').getContext('2d', { willReadFrequently: true })
  if (kontext === null) {
    return null
  }
  kontext.canvas.width = 1
  kontext.canvas.height = 1
  kontext.clearRect(0, 0, 1, 1)
  kontext.fillStyle = farbe
  kontext.fillRect(0, 0, 1, 1)
  const [r, g, b, a] = kontext.getImageData(0, 0, 1, 1).data
  if (r === undefined || g === undefined || b === undefined || a !== 255) {
    return null
  }
  return [r, g, b]
}

/**
 * Farbe mit Deckkraft als rgba(). Hex wird direkt umgerechnet, jede andere CSS-Farbe über
 * `alsRgb`; ist keine Auflösung möglich, bleibt `color-mix` als Ausweg, damit die Deckkraft
 * nie still verloren geht.
 */
export function mitDeckkraft(farbe: string, deckkraft: number): string {
  const rgb = /^#[0-9a-f]{6}$/i.test(farbe)
    ? ([1, 3, 5].map((start) => parseInt(farbe.slice(start, start + 2), 16)) as [
        number,
        number,
        number,
      ])
    : alsRgb(farbe)
  if (rgb === null) {
    return `color-mix(in srgb, ${farbe} ${String(Math.round(deckkraft * 100))}%, transparent)`
  }
  return `rgba(${String(rgb[0])}, ${String(rgb[1])}, ${String(rgb[2])}, ${String(deckkraft)})`
}

/** Diagonale Streifen (45°) für KL: KL bleibt auch ohne Farbwahrnehmung erkennbar. */
export const KL_DECAL: Decal = {
  symbol: 'rect',
  symbolSize: 1,
  rotation: Math.PI / 4,
  dashArrayX: [1, 0],
  dashArrayY: [3, 5],
  color: mitDeckkraft(token('--wa-color-surface-default', '#ffffff'), 0.45),
}

/** Punktmuster für Überschuss und Minderaufwand (nie Farbe allein). */
export const PUNKT_DECAL: Decal = {
  symbol: 'circle',
  symbolSize: 1,
  dashArrayX: [1, 0],
  dashArrayY: [2, 6],
  color: mitDeckkraft(token('--wa-color-surface-default', '#ffffff'), 0.55),
}

/** Erträge: Ertragsbalken, linke Sankey-Knoten, Zeitreihe (Akzent „Geld kommt herein“). */
export const ERTRAG_FARBE = token('--wa-color-brand-60', '#da7e00')
/** Gruppe „Steuern“ im Sankey. */
export const STEUER_FARBE = token('--wa-color-brand-50', '#b45f04')
/** Investive Einnahmen: bewusst nicht Gold, damit sie nicht wie Erträge wirken. */
export const INVEST_FARBE = token('--wa-color-neutral-40', '#545868')
/** Aufwandsarten: neutral, nie PB-Farben. */
export const AUFWANDSART_FARBE = token('--wa-color-neutral-40', '#545868')
/** Knoten „Gemeindehaushalt“ (Sankey Mitte). */
export const GEMEINDE_FARBE = token('--wa-color-gray-40', '#545868')
/** Knoten „Zinsen“ (Sankey rechts). */
export const ZINSEN_FARBE = token('--wa-color-gray-60', '#9194a2')
/** Knoten „Globaler Minderaufwand“ (mit `PUNKT_DECAL`). */
export const MINDERAUFWAND_FARBE = token('--wa-color-neutral-50', '#717584')

/**
 * Diagrammschriftgröße in px: mindestens 14 (UI-SPEC Typography). Nur ein
 * aufgelöster px-Wert des Tokens zählt; WA liefert `round(calc(...))` als
 * unaufgelösten Text, dann gilt der Ersatz 14.
 */
function schriftgroesse(): number {
  const roh = token('--wa-font-size-s', '14px')
  const treffer = /^(\d+(?:\.\d+)?)px$/.exec(roh)
  const px = treffer ? Number(treffer[1]) : 14
  return Math.max(14, px)
}

const SCHRIFTGROESSE = schriftgroesse()

registerTheme(CHART_THEME, {
  color: KATEGORIE_FARBEN,
  textStyle: {
    fontFamily: token('--wa-font-family-body', 'ui-sans-serif, system-ui, sans-serif'),
    color: token('--wa-color-text-normal', '#1a1d29'),
    fontSize: SCHRIFTGROESSE,
  },
  tooltip: {
    textStyle: { fontSize: SCHRIFTGROESSE },
  },
  legend: {
    textStyle: { fontSize: SCHRIFTGROESSE },
  },
  categoryAxis: {
    axisLine: { lineStyle: { color: token('--wa-color-text-quiet', '#545868') } },
    axisLabel: { color: token('--wa-color-text-quiet', '#545868'), fontSize: SCHRIFTGROESSE },
    splitLine: { lineStyle: { color: token('--wa-color-surface-border', '#dcdfe4') } },
  },
  valueAxis: {
    axisLine: { lineStyle: { color: token('--wa-color-text-quiet', '#545868') } },
    axisLabel: { color: token('--wa-color-text-quiet', '#545868'), fontSize: SCHRIFTGROESSE },
    splitLine: { lineStyle: { color: token('--wa-color-surface-border', '#dcdfe4') } },
  },
})
