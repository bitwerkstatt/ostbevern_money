// Geldfluss-Modell der Seite „Vom Ertrag zur Ausgabe“ (FLUSS-01 bis FLUSS-04, D-11, D-19).
// Gebaut ausschließlich aus dem Ergebnisplan: links die Ertragsarten, in der Mitte der
// Gemeindehaushalt, rechts Weitergabe an Kreis und Land, die Aufgabenbereiche und die
// Zinsen. Der Ausgleich entsteht datengetrieben, ohne Sonderfall je Jahr:
//   Defizit (Entnahme aus Rücklagen) = −Jahresergebnis nach Minderaufwand, links, wenn negativ
//   Globaler Minderaufwand           = −Z. 27, links, wenn ≠ 0
//   Überschuss (Zuführung zur Rücklage) = Jahresergebnis nach Minderaufwand, rechts, wenn positiv
// weil „nach Minderaufwand“ = Jahresergebnis − Z. 27 gilt (RESEARCH Pitfall 1).

import type { EChartsOption } from 'echarts'

import {
  abstufung,
  ERTRAG_FARBE,
  farbeFuerPb,
  GEMEINDE_FARBE,
  KL_DECAL,
  KL_FARBE,
  MINDERAUFWAND_FARBE,
  POL_FARBEN,
  PUNKT_DECAL,
  STEUER_FARBE,
  ZINSEN_FARBE,
  type Decal,
} from '@/charts/echartsTheme'
import {
  betragMitHinweis,
  euro,
  jahr as formatiereJahr,
  kurzMitHinweis,
  rundKurz,
} from '@/charts/format'
import { tooltipZeilen } from '@/charts/tooltip'
import { haushalt } from '@/data/daten'
import { anteil } from '@/lib/berechnung'
import { findeKlKnoten } from '@/lib/kreisumlage'
import { textFuerJahr } from '@/lib/texte'

export type KnotenSeite = 'links' | 'mitte' | 'rechts'

export type KnotenArt =
  | 'steuer'
  | 'ertrag'
  | 'defizit'
  | 'minderaufwand'
  | 'gemeinde'
  | 'kl'
  | 'pb'
  | 'zinsen'
  | 'ueberschuss'

export interface GeldflussKnoten {
  /** Eindeutiger Bezeichner (ECharts identifiziert Knoten über ihren Namen). */
  id: string
  /** Angezeigter Name. */
  name: string
  wert: number
  seite: KnotenSeite
  art: KnotenArt
  /** Knotencode (Aufgabenbereich oder KL) als Klickziel; sonst `null`. */
  code: string | null
  farbe: string
  decal?: Decal
  /** `true`, wenn der Betrag nur auf T€ genau ist (Vorbericht-Tabelle × 1000): Anzeige „rd.“. */
  gerundet: boolean
  /** `true` für einen Rest (Differenz aus genauem und gerundetem Wert): Anzeige „berechnet“. */
  berechnet: boolean
}

export interface GeldflussKante {
  quelle: string
  ziel: string
  wert: number
}

export interface Geldfluss {
  knoten: GeldflussKnoten[]
  kanten: GeldflussKante[]
  summeLinks: number
  summeRechts: number
  /** 1-basierte PDF-Seite des Gesamtergebnisplans; `null`, falls die Daten keine nennen. */
  pdfSeite: number | null
}

const GEMEINDE_ID = 'mitte:gemeinde'

/** Gruppen der Steuern (Vorbericht-Posten); der Rest bis zur Plan-Zeile ist „Übrige Steuern“. */
const STEUER_GRUPPEN: readonly { id: string; name: string; posten: readonly string[] }[] = [
  { id: 'gewerbesteuer', name: 'Gewerbesteuer', posten: ['gewerbesteuer'] },
  { id: 'einkommensteuer', name: 'Anteil Einkommensteuer', posten: ['anteil_einkommensteuer'] },
  { id: 'grundsteuer', name: 'Grundsteuer (A+B)', posten: ['grundsteuer_a', 'grundsteuer_b'] },
]

function gesamtWerte() {
  const gesamt = haushalt.ergebnisplan.GESAMT
  if (gesamt === undefined) {
    throw new Error('Ergebnisplan GESAMT fehlt in haushalt.json')
  }
  return gesamt
}

/** Wert einer Plan-Zeile von GESAMT; eine fehlende Zeile ist ein Datenfehler. */
function planZeile(schluessel: string, jahrIndex: number): number {
  const wert = gesamtWerte().zeilen[schluessel]?.[jahrIndex]
  if (wert === undefined) {
    throw new Error(`Zeile „${schluessel}“ fehlt im Jahresindex ${String(jahrIndex)}`)
  }
  return wert
}

/** Wert eines Vorbericht-Postens; `null` (nicht gedruckt) zählt als 0, ein fehlender Posten wirft. */
function postenWert(tabelle: string, posten: string, jahrIndex: number): number {
  const eintrag = haushalt.vorbericht[tabelle]?.posten.find((p) => p.posten === posten)
  if (eintrag === undefined) {
    throw new Error(`Posten „${posten}“ fehlt in der Vorbericht-Tabelle „${tabelle}“`)
  }
  return eintrag.werte[jahrIndex] ?? 0
}

/** `true`, wenn der Vorbericht-Posten nur auf T€ genau ist (die Tabelle führt T€ × 1000). */
function postenGerundet(tabelle: string, posten: string): boolean {
  const eintrag = haushalt.vorbericht[tabelle]?.posten.find((p) => p.posten === posten)
  if (eintrag === undefined) {
    throw new Error(`Posten „${posten}“ fehlt in der Vorbericht-Tabelle „${tabelle}“`)
  }
  return eintrag.gerundet
}

/** Z. 17 (ordentliche Aufwendungen) eines Knotens; ohne Eintrag 0. */
function ordentlicherAufwand(code: string, jahrIndex: number): number {
  return haushalt.ergebnisplan[code]?.zeilen.ordentliche_aufwendungen?.[jahrIndex] ?? 0
}

export function baueGeldfluss(jahrIndex: number): Geldfluss {
  if (!Number.isInteger(jahrIndex) || jahrIndex < 0 || jahrIndex >= haushalt.jahre.length) {
    throw new Error(`Jahresindex ${String(jahrIndex)} liegt außerhalb der Jahre`)
  }

  const knoten: GeldflussKnoten[] = []

  // ---- links: Ertragsarten ------------------------------------------------------------
  const steuern = planZeile('steuern', jahrIndex)
  const zuwendungen = planZeile('zuwendungen', jahrIndex)
  const entgelte =
    planZeile('oeffentlich_rechtliche_entgelte', jahrIndex) +
    planZeile('privatrechtliche_entgelte', jahrIndex)
  const ordentlicheErtraege = planZeile('ordentliche_ertraege', jahrIndex)

  interface ErtragEintrag {
    id: string
    name: string
    wert: number
    gerundet: boolean
    berechnet: boolean
  }
  const steuerKnoten: ErtragEintrag[] = STEUER_GRUPPEN.map((gruppe) => ({
    id: gruppe.id,
    name: gruppe.name,
    wert: gruppe.posten.reduce((s, p) => s + postenWert('steuerarten', p, jahrIndex), 0),
    gerundet: gruppe.posten.some((p) => postenGerundet('steuerarten', p)),
    berechnet: false,
  }))
  const gruppenSumme = steuerKnoten.reduce((s, k) => s + k.wert, 0)
  // Rest aus genauer Plan-Zeile minus gerundeten Gruppen: weder genau noch gedruckt.
  steuerKnoten.push({
    id: 'uebrige_steuern',
    name: 'Übrige Steuern',
    wert: steuern - gruppenSumme,
    gerundet: steuerKnoten.some((k) => k.gerundet),
    berechnet: true,
  })

  const schluesselzuweisung = postenWert('zuwendungen', 'schluesselzuweisung', jahrIndex)
  const schluesselGerundet = postenGerundet('zuwendungen', 'schluesselzuweisung')
  const uebrigeErtraege: ErtragEintrag[] = [
    {
      id: 'schluesselzuweisung',
      name: 'Schlüsselzuweisung',
      wert: schluesselzuweisung,
      gerundet: schluesselGerundet,
      berechnet: false,
    },
    {
      id: 'sonstige_zuwendungen',
      name: 'Sonstige Zuwendungen',
      wert: zuwendungen - schluesselzuweisung,
      gerundet: schluesselGerundet,
      berechnet: true,
    },
    {
      id: 'entgelte',
      name: 'Gebühren und Entgelte',
      wert: entgelte,
      gerundet: false,
      berechnet: false,
    },
    {
      id: 'sonstige_ertraege',
      name: 'Sonstige Erträge',
      wert: ordentlicheErtraege - steuern - zuwendungen - entgelte,
      gerundet: false,
      berechnet: false,
    },
    {
      id: 'finanzertraege',
      name: 'Finanzerträge',
      wert: planZeile('finanzertraege', jahrIndex),
      gerundet: false,
      berechnet: false,
    },
  ]

  function fuegeErtragHinzu(art: 'steuer' | 'ertrag', eintrag: ErtragEintrag, rang: number) {
    if (eintrag.wert < 0) {
      // Ein negativer Rest würde den Ausgleich still verfälschen: Datenfehler, laut abbrechen.
      throw new Error(`Ertragsknoten „${eintrag.name}“ hat einen negativen Wert`)
    }
    if (eintrag.wert === 0) {
      return
    }
    knoten.push({
      id: `ertrag:${eintrag.id}`,
      name: eintrag.name,
      wert: eintrag.wert,
      seite: 'links',
      art,
      code: null,
      farbe: abstufung(art === 'steuer' ? STEUER_FARBE : ERTRAG_FARBE, rang),
      gerundet: eintrag.gerundet,
      berechnet: eintrag.berechnet,
    })
  }
  steuerKnoten.forEach((eintrag, rang) => {
    fuegeErtragHinzu('steuer', eintrag, rang)
  })
  uebrigeErtraege.forEach((eintrag, rang) => {
    fuegeErtragHinzu('ertrag', eintrag, rang)
  })

  // ---- links: Ausgleich (Defizit, Minderaufwand) und rechts: Überschuss --------------
  const nachMinderaufwand = planZeile('ergebnis_nach_minderaufwand', jahrIndex)
  const minderaufwand = -planZeile('globaler_minderaufwand', jahrIndex)

  if (nachMinderaufwand < 0) {
    knoten.push({
      id: 'ausgleich:defizit',
      name: 'Defizit (Entnahme aus Rücklagen)',
      wert: -nachMinderaufwand,
      seite: 'links',
      art: 'defizit',
      code: null,
      farbe: POL_FARBEN.negativ,
      gerundet: false,
      berechnet: false,
    })
  }
  if (minderaufwand !== 0) {
    if (minderaufwand < 0) {
      throw new Error('Globaler Minderaufwand ist positiv: Datenfehler')
    }
    knoten.push({
      id: 'ausgleich:minderaufwand',
      name: 'Globaler Minderaufwand',
      wert: minderaufwand,
      seite: 'links',
      art: 'minderaufwand',
      code: null,
      farbe: MINDERAUFWAND_FARBE,
      decal: PUNKT_DECAL,
      gerundet: false,
      berechnet: false,
    })
  }

  // ---- Mitte -----------------------------------------------------------------------------
  const summeLinks = knoten.reduce((s, k) => s + k.wert, 0)
  knoten.push({
    id: GEMEINDE_ID,
    name: 'Gemeindehaushalt',
    wert: summeLinks,
    seite: 'mitte',
    art: 'gemeinde',
    code: null,
    farbe: GEMEINDE_FARBE,
    gerundet: false,
    berechnet: false,
  })

  // ---- rechts: Kreis und Land, Aufgabenbereiche, Zinsen, Überschuss ------------------
  const kl = findeKlKnoten()
  const klWert = ordentlicherAufwand(kl.code, jahrIndex)
  if (klWert > 0) {
    knoten.push({
      id: `ziel:${kl.code}`,
      name: kl.name,
      wert: klWert,
      seite: 'rechts',
      art: 'kl',
      code: kl.code,
      farbe: KL_FARBE,
      decal: KL_DECAL,
      gerundet: false,
      berechnet: false,
    })
  }
  for (const pb of haushalt.knoten) {
    if (pb.ebene !== 'PB' || pb.eltern !== 'GESAMT' || pb.synthetisch) {
      continue
    }
    const wert = ordentlicherAufwand(pb.code, jahrIndex)
    if (wert > 0) {
      knoten.push({
        id: `ziel:${pb.code}`,
        name: pb.name,
        wert,
        seite: 'rechts',
        art: 'pb',
        code: pb.code,
        farbe: farbeFuerPb(pb.code),
        gerundet: false,
        berechnet: false,
      })
    }
  }
  const zinsen = planZeile('zinsaufwendungen', jahrIndex)
  if (zinsen > 0) {
    knoten.push({
      id: 'ziel:zinsen',
      name: 'Zinsen',
      wert: zinsen,
      seite: 'rechts',
      art: 'zinsen',
      code: null,
      farbe: ZINSEN_FARBE,
      gerundet: false,
      berechnet: false,
    })
  }
  if (nachMinderaufwand > 0) {
    knoten.push({
      id: 'ausgleich:ueberschuss',
      name: 'Überschuss (Zuführung zur Rücklage)',
      wert: nachMinderaufwand,
      seite: 'rechts',
      art: 'ueberschuss',
      code: null,
      farbe: POL_FARBEN.positiv,
      gerundet: false,
      berechnet: false,
    })
  }

  // ---- Kanten ----------------------------------------------------------------------------
  const kanten: GeldflussKante[] = knoten
    .filter((k) => k.seite !== 'mitte')
    .map((k) =>
      k.seite === 'links'
        ? { quelle: k.id, ziel: GEMEINDE_ID, wert: k.wert }
        : { quelle: GEMEINDE_ID, ziel: k.id, wert: k.wert },
    )

  return {
    knoten,
    kanten,
    summeLinks,
    summeRechts: knoten.filter((k) => k.seite === 'rechts').reduce((s, k) => s + k.wert, 0),
    pdfSeite: haushalt.knoten.find((k) => k.code === 'GESAMT')?.pdf_seite ?? null,
  }
}

// ---- Tabellenzeilen -----------------------------------------------------------------------

export interface GeldflussZeile {
  id: string
  name: string
  /** Klickziel (Aufgabenbereich oder KL) für den Link „Im Detail ansehen“; sonst `null`. */
  code: string | null
  wert: number
  /** Anteil an der Summe der Seite (0–1). */
  anteil: number | null
  /** `true`: Betrag nur auf T€ genau (Anzeige „rd.“). */
  gerundet: boolean
  /** `true`: Rest aus genauem und gerundetem Wert (Anzeige „berechnet“). */
  berechnet: boolean
}

/** Zeilen der Tabelle „Woher“ (links) bzw. „Wohin“ (rechts) in Diagrammreihenfolge. */
export function geldflussZeilen(geldfluss: Geldfluss, seite: 'links' | 'rechts'): GeldflussZeile[] {
  const summe = seite === 'links' ? geldfluss.summeLinks : geldfluss.summeRechts
  return geldfluss.knoten
    .filter((k) => k.seite === seite)
    .map((k) => ({
      id: k.id,
      name: k.name,
      code: k.code,
      wert: k.wert,
      anteil: anteil(k.wert, summe),
      gerundet: k.gerundet,
      berechnet: k.berechnet,
    }))
}

// ---- Klick-Ziel ---------------------------------------------------------------------------

function istObjekt(wert: unknown): wert is Record<string, unknown> {
  return typeof wert === 'object' && wert !== null && !Array.isArray(wert)
}

/**
 * Code des Aufgabenbereichs (oder KL), auf den ein Klick im Diagramm zielt (D-10). Nur ein
 * Klick auf einen Knoten mit Code navigiert; Ertragsknoten, Kanten und alles Unbrauchbare
 * ergeben `null`. Der Name wird nur in einer `Map` nachgeschlagen, nie als Objektschlüssel.
 */
export function zielCodeAusKlick(params: unknown, geldfluss: Geldfluss): string | null {
  if (!istObjekt(params) || params.dataType !== 'node' || typeof params.name !== 'string') {
    return null
  }
  const nachId = new Map(geldfluss.knoten.map((k) => [k.id, k] as const))
  return nachId.get(params.name)?.code ?? null
}

// ---- ECharts-Option -----------------------------------------------------------------------

const TIEFE: Readonly<Record<KnotenSeite, number>> = { links: 0, mitte: 1, rechts: 2 }
const LABEL_POSITION = { links: 'left', mitte: 'top', rechts: 'right' } as const

/** Zeilen des Tooltips zu einem Knoten oder einer Kante; `null`, wenn nichts passt. */
function tooltipInhalt(
  params: unknown,
  nachId: ReadonlyMap<string, GeldflussKnoten>,
  wertartText: string,
): string[] | null {
  if (!istObjekt(params)) {
    return null
  }
  if (params.dataType === 'node' && typeof params.name === 'string') {
    const knoten = nachId.get(params.name)
    return knoten === undefined
      ? null
      : [knoten.name, betragMitHinweis(knoten.wert, knoten.gerundet), wertartText]
  }
  if (params.dataType === 'edge' && istObjekt(params.data)) {
    const { source, target, value } = params.data
    if (typeof source !== 'string' || typeof target !== 'string' || typeof value !== 'number') {
      return null
    }
    const von = nachId.get(source)
    const nach = nachId.get(target)
    if (von === undefined || nach === undefined) {
      return null
    }
    // Eine Kante hat den Betrag ihres Ertrags- bzw. Ziel-Knotens und erbt dessen Genauigkeit.
    const gerundet = von.seite === 'links' ? von.gerundet : nach.gerundet
    return [`${von.name} → ${nach.name}`, betragMitHinweis(value, gerundet), wertartText]
  }
  return null
}

/**
 * Sankey-Option (UI-SPEC „Sankey“): 640 px Diagramm, Knotenbreite 16, Abstand 8, Fluss in der
 * Farbe der Quelle bei 35 % Deckkraft, Hervorhebung des Pfades samt Nachbarn, Knoten nicht
 * verschiebbar, Beschriftung außerhalb mit Name und Betrag (Umbruch bei 160 px). Die
 * Knotenreihenfolge folgt den Daten (`layoutIterations: 0`), damit Gold oben, Defizit und
 * Minderaufwand unten stehen. Tooltips laufen ausschließlich über `tooltipZeilen`.
 */
export function geldflussOption(
  geldfluss: Geldfluss,
  text: { wertartText: string },
): EChartsOption {
  const nachId = new Map(geldfluss.knoten.map((k) => [k.id, k] as const))

  return {
    tooltip: {
      trigger: 'item',
      confine: true,
      formatter: (params: unknown) => {
        const zeilen = tooltipInhalt(params, nachId, text.wertartText)
        return zeilen === null ? '' : tooltipZeilen(zeilen)
      },
    },
    series: [
      {
        type: 'sankey',
        left: 176,
        right: 176,
        top: 44,
        bottom: 16,
        nodeWidth: 16,
        nodeGap: 8,
        draggable: false,
        layoutIterations: 0,
        orient: 'horizontal',
        emphasis: { focus: 'adjacency' },
        blur: {
          itemStyle: { opacity: 0.15 },
          lineStyle: { opacity: 0.15 },
        },
        lineStyle: { color: 'source', opacity: 0.35, curveness: 0.5 },
        label: {
          show: true,
          width: 160,
          overflow: 'break',
          distance: 6,
          fontSize: 14,
          lineHeight: 18,
          formatter: (params: unknown) => {
            const knoten = istObjekt(params) ? params.name : undefined
            const eintrag = typeof knoten === 'string' ? nachId.get(knoten) : undefined
            if (eintrag === undefined) {
              return ''
            }
            return `${eintrag.name}\n${kurzMitHinweis(eintrag.wert, eintrag.gerundet)}`
          },
        },
        labelLayout: { hideOverlap: false, moveOverlap: 'shiftY' },
        data: geldfluss.knoten.map((k) => ({
          name: k.id,
          depth: TIEFE[k.seite],
          value: k.wert,
          itemStyle: k.decal ? { color: k.farbe, decal: k.decal } : { color: k.farbe },
          label: { position: LABEL_POSITION[k.seite] },
        })),
        links: geldfluss.kanten.map((k) => ({ source: k.quelle, target: k.ziel, value: k.wert })),
      },
    ],
  }
}

// ---- Mobil-Alternative: zwei gleich lange gestapelte Balken (D-12, D-19) --------------------

export interface BalkenSegment {
  id: string
  name: string
  wert: number
  /** Anteil an der Summe des Balkens (0–1). */
  anteil: number | null
  art: KnotenArt
  /** Klickziel (Aufgabenbereich oder KL) für den Link in der Legendentabelle; sonst `null`. */
  code: string | null
  farbe: string
  decal?: Decal
  /** `true`: Betrag nur auf T€ genau (Anzeige „rd.“). */
  gerundet: boolean
  /** `true`: Rest aus genauem und gerundetem Wert (Anzeige „berechnet“). */
  berechnet: boolean
}

export interface GeldflussBalken {
  /** Ertragsarten plus Defizit und Globaler Minderaufwand. */
  woher: BalkenSegment[]
  /** KL, Aufgabenbereiche, Zinsen plus Überschuss. */
  wohin: BalkenSegment[]
  summeWoher: number
  summeWohin: number
}

function segmente(geldfluss: Geldfluss, seite: 'links' | 'rechts', summe: number): BalkenSegment[] {
  return geldfluss.knoten
    .filter((k) => k.seite === seite)
    .map((k) => ({
      id: k.id,
      name: k.name,
      wert: k.wert,
      anteil: anteil(k.wert, summe),
      art: k.art,
      code: k.code,
      farbe: k.farbe,
      decal: k.decal,
      gerundet: k.gerundet,
      berechnet: k.berechnet,
    }))
}

/** Die Segmente beider Balken aus demselben Modell wie das Sankey: dieselben Summen, Farben und Muster. */
export function baueGeldflussBalken(geldfluss: Geldfluss): GeldflussBalken {
  return {
    woher: segmente(geldfluss, 'links', geldfluss.summeLinks),
    wohin: segmente(geldfluss, 'rechts', geldfluss.summeRechts),
    summeWoher: geldfluss.summeLinks,
    summeWohin: geldfluss.summeRechts,
  }
}

/** Trennerfarbe der Segmente: die Flächenfarbe aus dem Web-Awesome-Token, Ersatz Weiß (wie `token()` im Theme). */
function trennerFarbe(): string {
  if (typeof document === 'undefined') {
    return '#ffffff'
  }
  const wert = getComputedStyle(document.documentElement)
    .getPropertyValue('--wa-color-surface-default')
    .trim()
  return wert === '' ? '#ffffff' : wert
}

/**
 * Option für einen einzelnen gestapelten Balken (56 px, keine Achsen, keine Beschriftung in
 * den Segmenten, 2 px Trenner). Die Skala reicht von 0 bis zur Summe des Balkens, daher füllt
 * jeder Balken die ganze Breite und beide sind gleich lang. Tooltip nur über `tooltipZeilen`.
 */
export function balkenOption(
  segmenteDesBalkens: readonly BalkenSegment[],
  summe: number,
  wertartText: string,
): EChartsOption {
  const nachId = new Map(segmenteDesBalkens.map((s) => [s.id, s] as const))
  const trenner = trennerFarbe()

  return {
    grid: { left: 0, right: 0, top: 0, bottom: 0 },
    tooltip: {
      trigger: 'item',
      confine: true,
      formatter: (params: unknown) => {
        const id = istObjekt(params) ? params.seriesName : undefined
        const segment = typeof id === 'string' ? nachId.get(id) : undefined
        return segment === undefined
          ? ''
          : tooltipZeilen([
              segment.name,
              betragMitHinweis(segment.wert, segment.gerundet),
              wertartText,
            ])
      },
    },
    xAxis: { type: 'value', show: false, min: 0, max: summe },
    yAxis: { type: 'category', show: false, data: [''] },
    series: segmenteDesBalkens.map((segment) => ({
      type: 'bar' as const,
      name: segment.id,
      stack: 'summe',
      data: [segment.wert],
      barWidth: '100%',
      label: { show: false },
      itemStyle: {
        color: segment.farbe,
        borderColor: trenner,
        borderWidth: 2,
        ...(segment.decal ? { decal: segment.decal } : {}),
      },
      emphasis: { focus: 'series' as const },
    })),
  }
}

// ---- Lesehilfe „So liest du das Diagramm“ --------------------------------------------------

/**
 * Satz aus den Daten des gewählten Jahres (D-11, Pitfall 6): nennt Defizit bzw. Überschuss
 * und den Globalen Minderaufwand mit ihren Beträgen und die PDF-Seite. `wertart` ist der
 * Anzeigename der Wertart („Ist“, „Ansatz“, „Planung“). Zahlen kommen nur aus `geldfluss`.
 */
export function lesehilfeSatz(geldfluss: Geldfluss, jahr: number, wertart: string): string {
  const defizit = geldfluss.knoten.find((k) => k.art === 'defizit')
  const ueberschuss = geldfluss.knoten.find((k) => k.art === 'ueberschuss')
  const minderaufwand = geldfluss.knoten.find((k) => k.art === 'minderaufwand')

  const saetze = [
    `Für ${formatiereJahr(jahr)} (${wertart}) sind beide Seiten gleich groß: ${rundKurz(geldfluss.summeLinks)}.`,
  ]
  if (defizit) {
    saetze.push(
      `Das Defizit von ${euro(defizit.wert)} steht links, weil die Gemeinde diesen Betrag aus ihren Rücklagen deckt.`,
    )
  }
  if (minderaufwand) {
    saetze.push(
      `Der globale Minderaufwand von ${euro(minderaufwand.wert)} steht ebenfalls links: Er senkt die geplanten Aufwendungen rechnerisch, ohne dass dafür ein Ertrag eingeht.`,
    )
  }
  if (ueberschuss) {
    saetze.push(
      `Der Überschuss von ${euro(ueberschuss.wert)} steht rechts, weil er den Rücklagen zugeführt wird.`,
    )
  }
  if (!defizit && !ueberschuss) {
    saetze.push('Erträge und Aufwendungen gleichen sich in diesem Jahr genau aus.')
  }
  if (geldfluss.pdfSeite !== null) {
    saetze.push(`Quelle: PDF-Seite ${String(geldfluss.pdfSeite)}.`)
  }
  return saetze.join(' ')
}

/**
 * Schlüssel der Erklärtexte unter dem Diagramm: die Lesehilfe immer, `defizit_ruecklagen`
 * nur bei einem Defizit, `ueberschuss_ruecklage` nur bei einem Überschuss. Jahrgebundene
 * Texte (mit Zahlen des Haushaltsjahrs) bleiben außen vor, wenn das gewählte Jahr ein
 * anderes ist (RESEARCH Pitfall 6): diese Entscheidung trifft `textFuerJahr`.
 */
export function welcheLesetexte(jahr: number, geldfluss: Geldfluss): string[] {
  const kandidaten = ['geldfluss_lesehilfe']
  if (geldfluss.knoten.some((k) => k.art === 'defizit')) {
    kandidaten.push('defizit_ruecklagen')
  }
  if (geldfluss.knoten.some((k) => k.art === 'ueberschuss')) {
    kandidaten.push('ueberschuss_ruecklage')
  }
  return kandidaten.filter((schluessel) => textFuerJahr(schluessel, jahr) !== null)
}
