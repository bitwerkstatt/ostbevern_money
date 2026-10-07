// Drilldown der Ausgabenseite (D-05, D-06, D-08): baut je Ebene (Aufgabenbereiche, dann
// Produktgruppen, dann Produkte) die Einträge für Treemap, Zuschuss-Balken und Tabelle.
// Alle Beträge werden unverändert aus `ergebnisplan[code].berechnet` gelesen; in diesem
// Modul wird weder Aufwand noch Zuschussbedarf neu gerechnet (D-05). URL-Werte kommen
// nur als validierte Codes hierher und werden ausschließlich über Map-Lookups aufgelöst.

import type { EChartsOption } from 'echarts'

import { abstufung, farbeFuerPb, KL_DECAL, PUNKT_DECAL, type Decal } from '@/charts/echartsTheme'
import { betragMitHinweis, euro, euroKurz, kurzMitHinweis, prozent } from '@/charts/format'
import { tooltipZeilen } from '@/charts/tooltip'
import { haushalt } from '@/data/daten'
import type { Knoten } from '@/data/typen'
import type { Modus } from '@/lib/ansicht'
import { anteil as anteilVon } from '@/lib/berechnung'
import { findeKlKnoten } from '@/lib/kreisumlage'
import { findeText } from '@/lib/texte'

const WURZEL = 'GESAMT'

/** Name des Wurzelknotens in den Brotkrumen (UI-SPEC Copywriting „Brotkrumen-Wurzel“). */
export const WURZEL_NAME = 'Alle Bereiche'

/** Was ein Klick auf einen Eintrag bewirkt. */
export type KlickZiel = 'drill' | 'produkt' | 'keins'

/** Ein Eintrag einer Ebene: eine Kachel, ein Balken und eine Tabellenzeile. */
export interface EbenenEintrag {
  code: string
  name: string
  /** Aufwand bzw. Zuschussbedarf des gewählten Jahres in Euro (aus `berechnet`). */
  wert: number
  /**
   * Anteil an der Ebene (0–1). Im Modus Aufwand `wert / Σ Werte`, im Modus Zuschussbedarf
   * `wert / Σ positive Werte`; `null` bei Überschuss-Einträgen und leerer Summe.
   */
  anteil: number | null
  /** `true`, wenn der Betrag nur auf T€ genau ist (App zeigt „rd.“). */
  gerundet: boolean
  /** `true`, wenn im Modus Zuschussbedarf der Wert des Knotens negativ ist (Überschuss); im Modus Aufwand immer `false`. */
  ueberschuss: boolean
  /** `true` für „Weitergabe an Kreis und Land“ und seine Unterposten. */
  istKl: boolean
  hatKinder: boolean
  istProdukt: boolean
  farbe: string
  /** Streifenmuster für KL und seine Unterposten. */
  decal?: Decal
}

export interface Brotkrume {
  code: string
  name: string
}

function betragVon(code: string, jahrIndex: number, modus: Modus): number {
  const berechnet = haushalt.ergebnisplan[code]?.berechnet
  const werte = modus === 'aufwand' ? berechnet?.aufwand : berechnet?.zuschussbedarf
  const betrag = werte?.[jahrIndex]
  if (betrag === undefined) {
    throw new Error(`Kein ${modus}-Wert für Knoten „${code}“ im Jahresindex ${String(jahrIndex)}`)
  }
  return betrag
}

function istUeberschuss(code: string, jahrIndex: number): boolean {
  const flag = haushalt.ergebnisplan[code]?.berechnet.ueberschuss[jahrIndex]
  if (flag === undefined) {
    throw new Error(`Kein Überschuss-Flag für Knoten „${code}“ im Jahresindex ${String(jahrIndex)}`)
  }
  return flag
}

// Map statt Objekt: URL-Codes wie `__proto__` treffen nichts (Sicherheit V5).
const KNOTEN: ReadonlyMap<string, Knoten> = new Map(haushalt.knoten.map((k) => [k.code, k]))

const KINDER: ReadonlyMap<string, readonly Knoten[]> = (() => {
  const nachEltern = new Map<string, Knoten[]>()
  for (const knoten of haushalt.knoten) {
    if (knoten.eltern === null) {
      continue
    }
    const liste = nachEltern.get(knoten.eltern)
    if (liste === undefined) {
      nachEltern.set(knoten.eltern, [knoten])
    } else {
      liste.push(knoten)
    }
  }
  return nachEltern
})()

function knoten(code: string): Knoten {
  const treffer = KNOTEN.get(code)
  if (treffer === undefined) {
    throw new Error(`Unbekannter Knoten „${code}“`)
  }
  return treffer
}

/** Kinder eines Knotens in Datenreihenfolge; leer für Blätter. Unbekannte Codes werfen. */
export function kinderVon(code: string): readonly Knoten[] {
  return KINDER.get(knoten(code).code) ?? []
}

/** Der Aufgabenbereich (direktes Kind von GESAMT) über oder gleich dem Knoten. */
function bereichVon(code: string): Knoten {
  let aktuell = knoten(code)
  while (aktuell.eltern !== WURZEL) {
    if (aktuell.eltern === null) {
      throw new Error(`Knoten „${code}“ hängt nicht unter einem Aufgabenbereich`)
    }
    aktuell = knoten(aktuell.eltern)
  }
  return aktuell
}

/** Code der Ebene, deren Kinder gezeigt werden: Produktgruppe vor Aufgabenbereich vor Wurzel. */
export function ebenenElternCode(pb: string | null, pg: string | null): string {
  return pg ?? pb ?? WURZEL
}

/**
 * Die Einträge einer Ebene: alle Kinder von `elternCode`, Werte aus `berechnet` des
 * gewählten Jahres, Einträge mit Wert 0 entfallen (eine Kachel kann keine 0 zeigen),
 * absteigend nach Wert sortiert. Farbe: Aufgabenbereiche behalten `PB_FARBEN`, tiefere
 * Ebenen dunkeln sie je Rang ab (D-08); KL und seine Unterposten tragen `KL_DECAL`.
 */
export function baueEbene(elternCode: string, jahrIndex: number, modus: Modus): EbenenEintrag[] {
  const eltern = knoten(elternCode)
  const kl = findeKlKnoten()

  const roh = (KINDER.get(eltern.code) ?? [])
    .map((kind) => ({ kind, betrag: betragVon(kind.code, jahrIndex, modus) }))
    .filter(({ betrag }) => betrag !== 0)
    .sort((a, b) => b.betrag - a.betrag || a.kind.code.localeCompare(b.kind.code))

  // Anteilsbasis: Aufwand = alle Werte, Zuschussbedarf = nur die positiven (Überschüsse
  // haben keinen Anteil, sie sind keine Kosten der Ebene).
  const basis = roh.reduce(
    (summe, { betrag }) => (modus === 'aufwand' || betrag > 0 ? summe + betrag : summe),
    0,
  )

  return roh.map(({ kind, betrag }, rang) => {
    const bereich = bereichVon(kind.code)
    const istKl = bereich.code === kl.code
    const ueberschuss = modus === 'zuschussbedarf' && istUeberschuss(kind.code, jahrIndex)
    const grundfarbe = farbeFuerPb(bereich.code)
    const eintrag: EbenenEintrag = {
      code: kind.code,
      name: kind.name,
      wert: betrag,
      anteil: modus === 'zuschussbedarf' && betrag <= 0 ? null : anteilVon(betrag, basis),
      gerundet: kind.gerundet,
      ueberschuss,
      istKl,
      hatKinder: (KINDER.get(kind.code)?.length ?? 0) > 0,
      istProdukt: kind.ebene === 'P',
      farbe: kind.eltern === WURZEL ? grundfarbe : abstufung(grundfarbe, rang),
    }
    if (istKl) {
      eintrag.decal = KL_DECAL
    }
    return eintrag
  })
}

/** Brotkrumen „Alle Bereiche › Aufgabenbereich › Produktgruppe“ aus validierten Codes. */
export function baueBrotkrumen(pb: string | null, pg: string | null): Brotkrume[] {
  const krumen: Brotkrume[] = [{ code: WURZEL, name: WURZEL_NAME }]
  if (pb === null) {
    return krumen
  }
  krumen.push({ code: pb, name: knoten(pb).name })
  if (pg !== null) {
    krumen.push({ code: pg, name: knoten(pg).name })
  }
  return krumen
}

/** Produkte öffnen ihre Seite, Knoten mit Kindern die nächste Ebene, alles andere (KL-Unterposten) nichts. */
export function klickZiel(eintrag: EbenenEintrag): KlickZiel {
  if (eintrag.istProdukt) {
    return 'produkt'
  }
  return eintrag.hatKinder ? 'drill' : 'keins'
}

/** Hinweiszeile im Tooltip je Klickziel (UI-SPEC Chart Contract). */
export function klickHinweis(ziel: KlickZiel): string | null {
  if (ziel === 'drill') {
    return 'Klicken, um die Unterteilung zu öffnen'
  }
  return ziel === 'produkt' ? 'Klicken, um das Produkt zu öffnen' : null
}

/** Tooltip-HTML eines Eintrags: Name, Betrag, Anteil, Wertart, Klickhinweis (alles maskiert). */
export function eintragTooltip(eintrag: EbenenEintrag, wertartText: string): string {
  const zeilen = [eintrag.name]
  const betrag = betragMitHinweis(eintrag.wert, eintrag.gerundet)
  zeilen.push(eintrag.ueberschuss ? `Überschuss: ${euro(Math.abs(eintrag.wert))}` : betrag)
  if (eintrag.anteil !== null) {
    zeilen.push(`Anteil: ${prozent(eintrag.anteil)}`)
  }
  zeilen.push(wertartText)
  const hinweis = klickHinweis(klickZiel(eintrag))
  if (hinweis !== null) {
    zeilen.push(hinweis)
  }
  return tooltipZeilen(zeilen)
}

/**
 * Typ-Guard für die Klick-/Tooltip-Parameter von ECharts (Pitfall 16): liefert den
 * `code` des Datensatzes oder `null`, nie ein `any`.
 */
export function codeAusParams(params: unknown): string | null {
  if (typeof params !== 'object' || params === null || !('data' in params)) {
    return null
  }
  const daten = params.data
  if (typeof daten !== 'object' || daten === null || !('code' in daten)) {
    return null
  }
  return typeof daten.code === 'string' ? daten.code : null
}

/** Mindestmaße einer beschrifteten Kachel in px (UI-SPEC Chart Contract). */
const MIN_KACHEL_BREITE = 72
const MIN_KACHEL_HOEHE = 44

/**
 * Sicherheitsfaktor der Flächenheuristik: Squarify legt auch langgestreckte Kacheln an, und
 * ein Name braucht mehr als die Mindestbreite, um nicht zu „Natu…“ zu verkürzen. Gemessen am
 * SVG-Lauf (900 × 480 px) bleiben damit Kacheln unter etwa 85 × 85 px unbeschriftet.
 */
const FLAECHENFAKTOR = 2.5

/**
 * Flächenheuristik (RESEARCH A3): eine Kachel mit Flächenanteil `anteil` auf einer
 * Zeichenfläche `breite` × `hoehe` px wird nur beschriftet, wenn ihre Fläche das
 * `FLAECHENFAKTOR`-fache von 72 × 44 px erreicht. Das Squarify-Layout liefert kein exaktes
 * Rechteck vorab; der Name bleibt bei unbeschrifteten Kacheln im Tooltip und in der Tabelle.
 */
export function kachelBeschriftet(anteil: number, breite: number, hoehe: number): boolean {
  return anteil * breite * hoehe >= MIN_KACHEL_BREITE * MIN_KACHEL_HOEHE * FLAECHENFAKTOR
}

const ALLGEMEINER_UEBERSCHUSS_TEXT = 'ueberschuss_allgemein'

/**
 * Schlüssel des Erklärtexts zu einem Überschussknoten (AUSG-03): `ueberschuss_pb_<PB>`, wenn
 * es für den Aufgabenbereich des Knotens einen eigenen Text gibt, sonst der allgemeine Text.
 * Die Wurzel und unbekannte Codes werfen.
 */
export function ueberschussTextSchluessel(code: string): string {
  const eigener = `ueberschuss_pb_${bereichVon(code).code}`
  return findeText(eigener) === undefined ? ALLGEMEINER_UEBERSCHUSS_TEXT : eigener
}

/** Zeilenhöhe der Zuschuss-Balken in px (UI-SPEC Chart Contract). */
const BALKEN_ZEILENHOEHE = 40
/** Platz für Wertachse und Ränder in px. */
const BALKEN_RAND = 48

/** Diagrammhöhe der Zuschuss-Balken: `Zeilenzahl × 40 px + 48 px`. */
export function zuschussBalkenHoehe(zeilen: number): number {
  return zeilen * BALKEN_ZEILENHOEHE + BALKEN_RAND
}

/** Rundet einen Rohschritt auf 1, 2, 2,5, 5 oder 10 mal eine Zehnerpotenz. */
function schoenerSchritt(roh: number): number {
  const basis = 10 ** Math.floor(Math.log10(roh))
  const rest = roh / basis
  const faktor = [1, 2, 2.5, 5, 10].find((f) => rest <= f) ?? 10
  return faktor * basis
}

/**
 * Optionen der horizontalen Zuschuss-Balken (D-05, AUSG-03): ein Balken je Eintrag in PB-Farbe,
 * absteigend von oben. Überschüsse sind negative Balken links der Nulllinie mit Punktmuster und
 * der Beschriftung „Überschuss: {Betrag}“; die Werte kommen unverändert aus den Einträgen.
 * Die Wertachse hat feste, „schöne“ Grenzen, die immer die 0 enthalten und rechts Platz für die
 * Beschriftungen lassen (bei nur negativen Werten steht das Label rechts der Nulllinie).
 */
export function zuschussBalkenOption(
  eintraege: readonly EbenenEintrag[],
  optionen: { wertartText: string; schmal?: boolean },
): EChartsOption {
  const schmal = optionen.schmal === true
  const nachCode = new Map(eintraege.map((e) => [e.code, e] as const))
  const codes = eintraege.map((e) => e.code)
  const werte = eintraege.map((e) => e.wert)

  const kleinster = Math.min(0, ...werte)
  const groesster = Math.max(0, ...werte)
  const spanne = groesster - kleinster || 1
  const schritt = schoenerSchritt(spanne / (schmal ? 3 : 5))
  const min = kleinster < 0 ? Math.floor(kleinster / schritt) * schritt : 0
  const max = Math.ceil((groesster + spanne * (schmal ? 0.45 : 0.3)) / schritt) * schritt

  const beschriftungsbreite = schmal ? 104 : 160

  return {
    tooltip: {
      trigger: 'item',
      confine: true,
      formatter: (params: unknown) => {
        const code = codeAusParams(params)
        const eintrag = code === null ? undefined : nachCode.get(code)
        return eintrag === undefined ? '' : eintragTooltip(eintrag, optionen.wertartText)
      },
    },
    grid: { left: beschriftungsbreite + 16, right: 12, top: 8, bottom: 32 },
    xAxis: {
      type: 'value',
      min,
      max,
      interval: schritt,
      axisLabel: { formatter: (wert: number) => euroKurz(wert), hideOverlap: true },
    },
    yAxis: [
      // Namen am linken Rand: die Achse liegt nicht auf der Nulllinie, sonst überdeckten
      // die Namen die Überschussbalken.
      {
        type: 'category',
        data: codes,
        inverse: true,
        axisLine: { show: false, onZero: false },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: {
          width: beschriftungsbreite,
          overflow: 'break',
          margin: 12,
          formatter: (code: string) => nachCode.get(code)?.name ?? '',
        },
      },
      // Die Nulllinie (1 px, Farbe aus dem Theme) trägt eine zweite, unbeschriftete Achse.
      {
        type: 'category',
        data: codes,
        inverse: true,
        axisLine: { show: true, onZero: true, lineStyle: { width: 1 } },
        axisTick: { show: false },
        splitLine: { show: false },
        axisLabel: { show: false },
      },
    ],
    series: [
      {
        type: 'bar',
        xAxisIndex: 0,
        yAxisIndex: 0,
        barWidth: 24,
        data: eintraege.map((eintrag) => {
          const decal = eintrag.wert < 0 ? PUNKT_DECAL : eintrag.decal
          const betrag = kurzMitHinweis(Math.abs(eintrag.wert), eintrag.gerundet)
          return {
            value: eintrag.wert,
            code: eintrag.code,
            cursor: klickZiel(eintrag) === 'keins' ? 'default' : 'pointer',
            itemStyle: { color: eintrag.farbe, ...(decal === undefined ? {} : { decal }) },
            label: {
              show: true,
              position: 'right',
              formatter: eintrag.wert < 0 ? `Überschuss: ${betrag}` : betrag,
            },
          }
        }),
      },
    ],
  }
}
