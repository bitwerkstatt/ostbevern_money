// Verpflichtungsermächtigungen (VE) und Finanzierung für `/investitionen` (INV-02, INV-03, D-08,
// D-10). Reine Funktionen über `investitionen.json` und `haushalt.json`: nichts wird neu
// gerechnet außer der Summe je Fälligkeitsjahr; kein Jahr steht im Code.

import type { EChartsOption } from 'echarts'

import { zweizeilig } from '@/charts/beschriftung'
import { INVEST_FARBE, KATEGORIE_FARBEN } from '@/charts/echartsTheme'
import { euro, euroKurz, jahr as formatiereJahr, KEIN_WERT } from '@/charts/format'
import { tooltipZeilen } from '@/charts/tooltip'
import { jahresAchse } from '@/charts/wertartStil'
import type { DatenSpalte } from '@/components/datenTabelle'
import { haushalt, investitionen } from '@/data/daten'
import type { Massnahme, VeFaelligkeit } from '@/data/typen'
import { wertartName } from '@/lib/jahr'
import { jahrSchluessel, type Tabelle } from '@/lib/produkt'

// ---------------------------------------------------------------------------------------
// Verpflichtungsermächtigungen nach Fälligkeit (INV-02, D-10)
// ---------------------------------------------------------------------------------------

/** Eine Maßnahme mit Verpflichtungsermächtigung, die in einem Jahr fällig wird. */
export interface VeMassnahme {
  produkt: string
  massnahmeId: string
  name: string
  betrag: number
  pdfSeite: number
}

/** Die in einem Fälligkeitsjahr fälligen Verpflichtungsermächtigungen. */
export interface VeFaelligkeitsjahr {
  jahr: number
  /** Summe der Beträge aller Maßnahmen dieses Jahres. */
  betrag: number
  /** Absteigend nach Betrag. */
  massnahmen: VeMassnahme[]
}

const SORTIERUNG = new Intl.Collator('de')

function massnahmenSchluessel(produkt: string, massnahmeId: string): string {
  return `${produkt}/${massnahmeId}`
}

/**
 * Fasst VE-Zeilen je Fälligkeitsjahr zusammen (aufsteigend nach Jahr). Innerhalb eines Jahres
 * werden die Konten einer Maßnahme `(produkt, massnahme_id)` gebündelt und absteigend nach
 * Betrag geordnet; den Namen liefert die Maßnahmenzeile mit demselben Schlüssel. Eine VE-Zeile
 * ohne Maßnahme ist ein Datenfehler und wirft mit Produkt und Kennung. Jahre ohne VE kommen
 * nicht vor.
 */
export function baueVeFaelligkeiten(
  zeilen: readonly VeFaelligkeit[],
  massnahmen: readonly Massnahme[],
): VeFaelligkeitsjahr[] {
  const namen = new Map<string, string>()
  for (const massnahme of massnahmen) {
    const schluessel = massnahmenSchluessel(massnahme.produkt, massnahme.massnahme_id)
    if (!namen.has(schluessel)) {
      namen.set(schluessel, massnahme.massnahme_name)
    }
  }

  const jahre = new Map<number, Map<string, VeMassnahme>>()
  for (const zeile of zeilen) {
    const schluessel = massnahmenSchluessel(zeile.produkt, zeile.massnahme_id)
    const name = namen.get(schluessel)
    if (name === undefined) {
      throw new Error(
        `VE-Zeile ohne Maßnahme: Produkt ${zeile.produkt}, Maßnahme ${zeile.massnahme_id}`,
      )
    }
    const dieses = jahre.get(zeile.jahr) ?? new Map<string, VeMassnahme>()
    jahre.set(zeile.jahr, dieses)
    const vorhanden = dieses.get(schluessel)
    if (vorhanden === undefined) {
      dieses.set(schluessel, {
        produkt: zeile.produkt,
        massnahmeId: zeile.massnahme_id,
        name,
        betrag: zeile.betrag,
        pdfSeite: zeile.pdf_seite,
      })
    } else {
      vorhanden.betrag += zeile.betrag
    }
  }

  return [...jahre.entries()]
    .sort(([a], [b]) => a - b)
    .map(([jahr, dieses]) => {
      const liste = [...dieses.values()].sort(
        (a, b) =>
          b.betrag - a.betrag ||
          SORTIERUNG.compare(a.name, b.name) ||
          SORTIERUNG.compare(a.massnahmeId, b.massnahmeId),
      )
      return { jahr, betrag: liste.reduce((s, m) => s + m.betrag, 0), massnahmen: liste }
    })
}

/** Die Verpflichtungsermächtigungen der Daten je Fälligkeitsjahr. */
export function veFaelligkeiten(): VeFaelligkeitsjahr[] {
  return baueVeFaelligkeiten(investitionen.ve_faelligkeiten, investitionen.massnahmen)
}

/** Summe aller Verpflichtungsermächtigungen; gleich der VE-Zeile des Gesamtfinanzplans. */
export function veGesamt(): number {
  return investitionen.ve_faelligkeiten.reduce((summe, zeile) => summe + zeile.betrag, 0)
}

/** Die PDF-Seiten der VE-Zeilen, aufsteigend und ohne Wiederholung. */
export function vePdfSeiten(): number[] {
  return [...new Set(investitionen.ve_faelligkeiten.map((zeile) => zeile.pdf_seite))].sort(
    (a, b) => a - b,
  )
}

/**
 * Säulen je Fälligkeitsjahr in `INVEST_FARBE` mit `euroKurz` über der Säule. Die Achse zeigt nur
 * das Jahr (Fälligkeiten sind Plandaten, keine Jahresergebnisse). Ohne Fälligkeit gibt es keine
 * Serie, damit `BaseChart` den Leerzustand zeigt. Tooltips nur über `tooltipZeilen`.
 */
export function veOption(
  eintraege: readonly VeFaelligkeitsjahr[] = veFaelligkeiten(),
): EChartsOption {
  if (eintraege.length === 0) {
    return { series: [] }
  }
  return {
    grid: {
      left: 8,
      right: 16,
      top: 24,
      bottom: 8,
      outerBoundsMode: 'same',
      outerBoundsContain: 'axisLabel',
    },
    xAxis: {
      type: 'category',
      data: eintraege.map((eintrag) => formatiereJahr(eintrag.jahr)),
      axisLabel: { interval: 0, rotate: 0 },
    },
    yAxis: {
      type: 'value',
      min: 0,
      // Luft über der höchsten Säule für die Beschriftung.
      boundaryGap: [0, '12%'],
      axisLabel: { formatter: (wert: number) => euroKurz(wert) },
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params) => {
        const eintrag = Array.isArray(params) ? params[0] : params
        const gewaehlt = eintrag === undefined ? undefined : eintraege[eintrag.dataIndex]
        if (gewaehlt === undefined) {
          return ''
        }
        return tooltipZeilen([
          `Fällig ${formatiereJahr(gewaehlt.jahr)}: ${euro(gewaehlt.betrag)}`,
          ...gewaehlt.massnahmen.map((m) => `${m.name}: ${euro(m.betrag)}`),
        ])
      },
    },
    series: [
      {
        type: 'bar',
        data: eintraege.map((eintrag) => eintrag.betrag),
        barMaxWidth: 96,
        itemStyle: { color: INVEST_FARBE },
        label: {
          show: true,
          position: 'top',
          lineHeight: 18,
          formatter: (params) => {
            const gewaehlt = eintraege[params.dataIndex]
            return gewaehlt === undefined ? '' : euroKurz(gewaehlt.betrag)
          },
        },
      },
    ],
  }
}

const VE_SPALTEN: readonly DatenSpalte[] = [
  { schluessel: 'jahr', titel: 'Fälligkeitsjahr', art: 'text' },
  { schluessel: 'betrag', titel: 'Betrag', art: 'euro' },
  { schluessel: 'massnahmen', titel: 'Maßnahmen', art: 'text' },
]

/**
 * Tabelle der Fälligkeiten: Fälligkeitsjahr, Betrag und die Namen der Maßnahmen. Die Zeile
 * trägt zusätzlich das Jahr als Zahl (`faelligkeitsjahr`), damit die Seite die Maßnahmen mit
 * Links auf das Produkt darstellen kann.
 */
export function veTabelle(eintraege: readonly VeFaelligkeitsjahr[] = veFaelligkeiten()): Tabelle {
  return {
    spalten: [...VE_SPALTEN],
    zeilen: eintraege.map((eintrag) => ({
      jahr: formatiereJahr(eintrag.jahr),
      faelligkeitsjahr: eintrag.jahr,
      betrag: eintrag.betrag,
      massnahmen: eintrag.massnahmen.map((m) => m.name).join(', '),
    })),
  }
}

// ---------------------------------------------------------------------------------------
// Finanzierung der Investitionen (INV-03, D-08)
// ---------------------------------------------------------------------------------------
//
// Die Diagramme lesen nur Finanzplan-Reihen (Ein- und Auszahlungen); ein Ergebnisplan-Wert
// (Erträge, Aufwendungen) steht nie im selben Diagramm (Spez. 3.1).

/** Die beiden Diagramme: Investitionen mit Einzahlungen, Kreditaufnahme mit Tilgung. */
export type FinanzierungsVariante = 'investitionen' | 'kredite'

/** Die Finanzierungsreihen je Eintrag von `haushalt.jahre`; ein fehlender Wert ist `null`. */
export interface Finanzierungsreihen {
  jahre: number[]
  wertarten: string[]
  /** GFP Z. 23, Einzahlungen aus Investitionstätigkeit. */
  einzahlungen: (number | null)[]
  /** GFP Z. 30, Auszahlungen aus Investitionstätigkeit. */
  auszahlungen: (number | null)[]
  /** GFP Z. 33, Aufnahme und Rückflüsse von Darlehen. */
  kreditaufnahme: (number | null)[]
  /** GFP Z. 35, Tilgung und Gewährung von Darlehen. */
  tilgung: (number | null)[]
}

/** Eine Einzahlungszeile des Gesamtfinanzplans (Z. 18 bis 22) mit gedrucktem Namen. */
export interface EinzahlungsZeile {
  schluessel: string
  /** Zweistellige Zeilennummer, z. B. „18“. */
  nummer: string
  name: string
  werte: (number | null)[]
}

/** Namen der dunklen (erste Serie) und der hellen (zweite Serie) Säule je Variante. */
export const FINANZIERUNG_NAMEN: Readonly<
  Record<FinanzierungsVariante, readonly [string, string]>
> = {
  investitionen: ['Auszahlungen', 'Einzahlungen'],
  kredite: ['Kreditaufnahme', 'Tilgung'],
}

/** Die Textlegende unter dem Diagramm: „dunkel: …, hell: …“. */
export function finanzierungsLegende(variante: FinanzierungsVariante): string {
  const [dunkel, hell] = FINANZIERUNG_NAMEN[variante]
  return `dunkel: ${dunkel}, hell: ${hell}`
}

/** Genau `anzahl` Werte; was fehlt oder keine endliche Zahl ist, wird `null` (nie 0). */
function alsReihe(
  werte: readonly (number | null | undefined)[],
  anzahl: number,
): (number | null)[] {
  return Array.from({ length: anzahl }, (_leer, index) => {
    const wert = werte[index]
    return typeof wert === 'number' && Number.isFinite(wert) ? wert : null
  })
}

/** Die vier Finanzierungsreihen aus `investitionen.finanzierung`, je Eintrag von `haushalt.jahre`. */
export function finanzierungsReihen(): Finanzierungsreihen {
  const zeilen = investitionen.finanzierung.zeilen
  const anzahl = haushalt.jahre.length
  return {
    jahre: [...haushalt.jahre],
    wertarten: [...haushalt.wertarten],
    einzahlungen: alsReihe(zeilen.einzahlungen_investitionen, anzahl),
    auszahlungen: alsReihe(zeilen.auszahlungen_investitionen, anzahl),
    kreditaufnahme: alsReihe(zeilen.kreditaufnahme, anzahl),
    tilgung: alsReihe(zeilen.tilgung, anzahl),
  }
}

/** Die Zeilen 18 bis 22 des Gesamtfinanzplans, aus denen die Einzahlungen bestehen. */
const EINZAHLUNGS_SCHLUESSEL: readonly string[] = [
  'investitionszuwendungen',
  'veraeusserung_sachanlagen',
  'veraeusserung_finanzanlagen',
  'beitraege',
  'sonstige_investitionseinzahlungen',
]

/** Gedruckter Name einer Finanzplan-Zeile (einzige Namensquelle: `zeilen_namen.finanzplan`). */
function finanzplanZeilenname(schluessel: string): { nummer: string; name: string } {
  const eintrag = haushalt.zeilen_namen.finanzplan.find((name) => name.schluessel === schluessel)
  if (eintrag === undefined) {
    throw new Error(`Kein Zeilenname für die Finanzplan-Zeile ${schluessel}`)
  }
  return { nummer: eintrag.nummer, name: eintrag.name }
}

/**
 * Woraus die Einzahlungen aus Investitionstätigkeit bestehen: die fünf Zeilen 18 bis 22 mit den
 * gedruckten Namen und einem Wert je Eintrag von `haushalt.jahre`.
 */
export function einzahlungsAufteilung(): EinzahlungsZeile[] {
  const zeilen = haushalt.finanzplan['GESAMT']?.zeilen
  if (zeilen === undefined) {
    throw new Error('Der Finanzplan GESAMT fehlt in haushalt.json')
  }
  const anzahl = haushalt.jahre.length
  return EINZAHLUNGS_SCHLUESSEL.map((schluessel) => ({
    schluessel,
    ...finanzplanZeilenname(schluessel),
    werte: alsReihe(zeilen[schluessel] ?? [], anzahl),
  }))
}

/**
 * Die Jahre, in denen die Summe der Zeilen 18 bis 22 von der gedruckten Summenzeile (Z. 23)
 * abweicht, mit der Differenz (Summe der Einzelzeilen minus Summenzeile). Leer, wenn alles passt.
 */
export function einzahlungsAbweichungen(): { jahr: number; differenz: number }[] {
  const zeilen = einzahlungsAufteilung()
  const reihen = finanzierungsReihen()
  return reihen.jahre.flatMap((jahr, index) => {
    const gedruckt = reihen.einzahlungen[index]
    if (gedruckt === null || gedruckt === undefined) {
      return []
    }
    const summe = zeilen.reduce((s, zeile) => s + (zeile.werte[index] ?? 0), 0)
    return summe === gedruckt ? [] : [{ jahr, differenz: summe - gedruckt }]
  })
}

/** Die dunkle und die helle Reihe einer Variante, in Serienreihenfolge. */
function reihenVon(
  variante: FinanzierungsVariante,
  reihen: Finanzierungsreihen,
): readonly [(number | null)[], (number | null)[]] {
  return variante === 'investitionen'
    ? [reihen.auszahlungen, reihen.einzahlungen]
    : [reihen.kreditaufnahme, reihen.tilgung]
}

/**
 * Zwei gruppierte Säulen je Jahr: dunkel in `INVEST_FARBE`, hell in `KATEGORIE_FARBEN[2]`. Die
 * Datenpunkte sind die Finanzplan-Werte unverändert (ein fehlender Wert bleibt `null`). Die
 * Achse hat zwei Zeilen („{jahr}“ / Wertart). Beschriftung als `euroKurz`, zweizeilig; bis
 * 699 px trägt nur der größte Wert je Jahr eine Beschriftung (bei Gleichstand die erste Serie),
 * alle weiteren stehen im Tooltip und in der Tabelle. Tooltips nur über `tooltipZeilen`.
 */
export function finanzierungsOption(
  variante: FinanzierungsVariante,
  schmal: boolean,
  reihen: Finanzierungsreihen = finanzierungsReihen(),
): EChartsOption {
  const [dunkelName, hellName] = FINANZIERUNG_NAMEN[variante]
  const [dunkel, hell] = reihenVon(variante, reihen)
  const hellFarbe = KATEGORIE_FARBEN[2] ?? INVEST_FARBE

  /** `true`, wenn der Wert der Serie `nummer` im Jahr `index` beschriftet wird. */
  function beschriftet(nummer: 0 | 1, index: number): boolean {
    const mein = (nummer === 0 ? dunkel : hell)[index]
    if (mein === null || mein === undefined) {
      return false
    }
    if (!schmal) {
      return true
    }
    const anderer = (nummer === 0 ? hell : dunkel)[index]
    if (anderer === null || anderer === undefined) {
      return true
    }
    return nummer === 0 ? mein >= anderer : mein > anderer
  }

  function serie(nummer: 0 | 1, name: string, daten: (number | null)[], farbe: string) {
    return {
      type: 'bar' as const,
      name,
      data: daten,
      barGap: '10%',
      itemStyle: { color: farbe },
      label: {
        show: true,
        position: 'top' as const,
        lineHeight: 17,
        formatter: (params: { dataIndex: number }) => {
          const wert = daten[params.dataIndex]
          return wert === null || wert === undefined || !beschriftet(nummer, params.dataIndex)
            ? ''
            : zweizeilig(euroKurz(wert))
        },
      },
    }
  }

  function text(wert: number | null | undefined): string {
    return wert === null || wert === undefined ? KEIN_WERT : euro(wert)
  }

  return {
    grid: {
      left: 8,
      right: schmal ? 16 : 24,
      top: 24,
      bottom: 8,
      outerBoundsMode: 'same',
      outerBoundsContain: 'axisLabel',
    },
    xAxis: {
      type: 'category',
      data: jahresAchse(reihen.jahre, reihen.wertarten),
      axisLabel: { interval: 0, rotate: 0 },
    },
    yAxis: {
      type: 'value',
      min: 0,
      // Luft über der höchsten Säule für die zweizeilige Beschriftung.
      boundaryGap: [0, '18%'],
      axisLabel: { formatter: (wert: number) => euroKurz(wert) },
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params) => {
        const eintrag = Array.isArray(params) ? params[0] : params
        const index = eintrag?.dataIndex
        const jahr = index === undefined ? undefined : reihen.jahre[index]
        const wertart = index === undefined ? undefined : reihen.wertarten[index]
        if (index === undefined || jahr === undefined || wertart === undefined) {
          return ''
        }
        return tooltipZeilen([
          `${formatiereJahr(jahr)} · ${wertartName(wertart)}`,
          `${dunkelName}: ${text(dunkel[index])}`,
          `${hellName}: ${text(hell[index])}`,
        ])
      },
    },
    series: [serie(0, dunkelName, dunkel, INVEST_FARBE), serie(1, hellName, hell, hellFarbe)],
  }
}

/** Beschriftung der Jahreszeile der Finanzierungstabelle: „{jahr} · {Wertart}“. */
function jahrBeschriftung(jahr: number, wertart: string | undefined): string {
  return `${formatiereJahr(jahr)} · ${wertart === undefined ? '' : wertartName(wertart)}`
}

/**
 * Tabelle eines Finanzierungsdiagramms: je Jahr eine Zeile mit der dunklen und der hellen
 * Reihe. Ein fehlender Wert bleibt `null` und erscheint als „–“, nie als 0.
 */
export function finanzierungsTabelle(
  variante: FinanzierungsVariante,
  reihen: Finanzierungsreihen = finanzierungsReihen(),
): Tabelle {
  const [dunkelName, hellName] = FINANZIERUNG_NAMEN[variante]
  const [dunkel, hell] = reihenVon(variante, reihen)
  const spalten: DatenSpalte[] = [
    { schluessel: 'jahr', titel: 'Jahr', art: 'text' },
    { schluessel: 'dunkel', titel: dunkelName, art: 'euro' },
    { schluessel: 'hell', titel: hellName, art: 'euro' },
  ]
  return {
    spalten,
    zeilen: reihen.jahre.map((jahr, index) => ({
      jahr: jahrBeschriftung(jahr, reihen.wertarten[index]),
      dunkel: dunkel[index] ?? null,
      hell: hell[index] ?? null,
    })),
  }
}

/**
 * Tabelle „Woraus die Einzahlungen bestehen“: die Zeilen 18 bis 22 je Jahr, darunter die
 * gedruckte Summenzeile (Z. 23, Einzahlungen aus Investitionstätigkeit). Spaltenkopf je Jahr:
 * „{Jahr} {Wertart}“.
 */
export function einzahlungsTabelle(): Tabelle {
  const reihen = finanzierungsReihen()
  const spalten: DatenSpalte[] = [
    { schluessel: 'name', titel: 'Zeile', art: 'text' },
    ...reihen.jahre.map((jahr, index): DatenSpalte => {
      const wertart = reihen.wertarten[index]
      return {
        schluessel: jahrSchluessel(jahr),
        titel:
          wertart === undefined
            ? formatiereJahr(jahr)
            : `${formatiereJahr(jahr)} ${wertartName(wertart)}`,
        art: 'euro',
      }
    }),
  ]

  function zeile(
    name: string,
    werte: readonly (number | null)[],
  ): Record<string, string | number | null> {
    const eintrag: Record<string, string | number | null> = { name }
    reihen.jahre.forEach((jahr, index) => {
      eintrag[jahrSchluessel(jahr)] = werte[index] ?? null
    })
    return eintrag
  }

  const summe = finanzplanZeilenname('einzahlungen_investitionen')
  return {
    spalten,
    zeilen: [
      ...einzahlungsAufteilung().map((eintrag) => zeile(eintrag.name, eintrag.werte)),
      zeile(summe.name, reihen.einzahlungen),
    ],
  }
}
