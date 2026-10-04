// Drilldown der Ausgabenseite (D-05, D-06, D-08): baut je Ebene (Aufgabenbereiche, dann
// Produktgruppen, dann Produkte) die Einträge für Treemap, Zuschuss-Balken und Tabelle.
// Alle Beträge werden unverändert aus `ergebnisplan[code].berechnet` gelesen; in diesem
// Modul wird weder Aufwand noch Zuschussbedarf neu gerechnet (D-05). URL-Werte kommen
// nur als validierte Codes hierher und werden ausschließlich über Map-Lookups aufgelöst.

import type { EChartsOption } from 'echarts'

import { abstufung, farbeFuerPb, KL_DECAL, type Decal } from '@/charts/echartsTheme'
import { euro, prozent } from '@/charts/format'
import { tooltipZeilen } from '@/charts/tooltip'
import { haushalt } from '@/data/daten'
import type { Knoten } from '@/data/typen'
import type { Modus } from '@/lib/ansicht'
import { anteil as anteilVon } from '@/lib/berechnung'
import { findeKlKnoten } from '@/lib/kreisumlage'

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
  const betrag = eintrag.gerundet ? `rd. ${euro(eintrag.wert)}` : euro(eintrag.wert)
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
 * Flächenheuristik (RESEARCH A3): eine Kachel mit Flächenanteil `anteil` auf einer
 * Zeichenfläche `breite` × `hoehe` px wird nur beschriftet, wenn ihre Fläche für
 * 72 × 44 px reicht. Das Squarify-Layout liefert kein exaktes Rechteck vorab; der Name
 * bleibt bei unbeschrifteten Kacheln im Tooltip und in der Tabelle.
 */
export function kachelBeschriftet(anteil: number, breite: number, hoehe: number): boolean {
  return anteil * breite * hoehe >= MIN_KACHEL_BREITE * MIN_KACHEL_HOEHE
}

// RED-Stub (Task 2): nur Signaturen, damit die Tests an Assertions statt am Import scheitern.
export function ueberschussTextSchluessel(_code: string): string {
  return ''
}

export function zuschussBalkenHoehe(_zeilen: number): number {
  return 0
}

export function zuschussBalkenOption(
  _eintraege: readonly EbenenEintrag[],
  _optionen: { wertartText: string },
): EChartsOption {
  return {}
}
