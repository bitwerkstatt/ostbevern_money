// Schuldenstand für `/investitionen` (INV-04, D-09). Reine Funktionen über
// `investitionen.json`: nichts wird neu gerechnet, die Reihen kommen unverändert aus den Daten.
//
// Dokumentierte Abweichungen von UI-SPEC E9 (Nutzerentscheidung 4, 2026-10-05):
// - Liquiditätskredite werden nicht gestapelt und zählen nicht zum Schuldenstand (`gesamt` =
//   Investitionskredite + NRW.Bank). Sie stehen nur in der Tabelle; fehlt der Wert, ist er
//   `null` und erscheint als „–“, nie als 0.
// - Die Kachel „Schulden je Einwohner“ trägt kein „berechnet“, wenn der Vorjahreswert gedruckt
//   ist (Vorbericht, Einwohner-Seite): das Etikett folgt dem Datenfeld `berechnet`.
//
// Welche Jahre berechnet sind, steht allein in `schuldenstand.berechnet`; keine Jahresliste im Code.

import type { EChartsOption } from 'echarts'

import { zweizeilig } from '@/charts/beschriftung'
import { BERECHNET_DECAL, SCHULDEN_FARBEN } from '@/charts/echartsTheme'
import { euro, euroKurz, jahr as formatiereJahr, KEIN_WERT } from '@/charts/format'
import { tooltipZeilen } from '@/charts/tooltip'
import { flaechenFarbe, jahresAchse } from '@/charts/wertartStil'
import type { DatenSpalte, DatenZeile } from '@/components/datenTabelle'
import { haushalt, investitionen } from '@/data/daten'
import { wertartName } from '@/lib/jahr'
import type { Tabelle } from '@/lib/produkt'

/** Die Schuldenreihen je Jahr von `haushalt.jahre`, unverändert aus `investitionen.json`. */
export interface Schuldenreihen {
  jahre: number[]
  wertarten: string[]
  investitionskredite: number[]
  nrwBank: number[]
  /** `null` für ein Jahr ohne gedruckten Stand (nie 0). */
  liquiditaetskredite: (number | null)[]
  /** Investitionskredite plus NRW.Bank, ohne Liquiditätskredite. */
  gesamt: number[]
  /** Abgerundet. */
  proKopf: number[]
  /** `true` für ein fortgeschriebenes (nicht gedrucktes) Jahr. */
  berechnet: boolean[]
  formel: string
  /** 1-basierte PDF-Seite der Verbindlichkeiten-Tabelle. */
  pdfSeite: number
}

/**
 * Die Schuldenreihen aus den Daten. Eine Reihe mit abweichender Länge ist ein Datenfehler und
 * wirft mit dem Namen der Reihe.
 */
export function baueSchuldenstand(): Schuldenreihen {
  const stand = investitionen.schuldenstand
  const jahre = investitionen.jahre
  const reihen: [string, readonly unknown[]][] = [
    ['wertarten', investitionen.wertarten],
    ['investitionskredite', stand.investitionskredite],
    ['nrw_bank', stand.nrw_bank],
    ['liquiditaetskredite', stand.liquiditaetskredite],
    ['gesamt', stand.gesamt],
    ['pro_kopf', stand.pro_kopf],
    ['berechnet', stand.berechnet],
  ]
  for (const [name, werte] of reihen) {
    if (werte.length !== jahre.length) {
      throw new Error(
        `schuldenstand.${name} hat ${String(werte.length)} Einträge, erwartet ${String(jahre.length)} (investitionen.jahre)`,
      )
    }
  }
  return {
    jahre: [...jahre],
    wertarten: [...investitionen.wertarten],
    investitionskredite: [...stand.investitionskredite],
    nrwBank: [...stand.nrw_bank],
    liquiditaetskredite: [...stand.liquiditaetskredite],
    gesamt: [...stand.gesamt],
    proKopf: [...stand.pro_kopf],
    berechnet: [...stand.berechnet],
    formel: stand.formel,
    pdfSeite: stand.quelle,
  }
}

/** Die Jahre, in denen der Haushaltsplan keine Liquiditätskredite nennt (Eintrag `null`). */
export function jahreOhneLiquiditaetskredite(): number[] {
  const reihen = baueSchuldenstand()
  return reihen.jahre.filter((_jahr, index) => reihen.liquiditaetskredite[index] === null)
}

/** Jahreszahlen als Aufzählung: „2027“, „2027 und 2028“, „2027, 2028 und 2029“. */
export function jahreListe(jahre: readonly number[]): string {
  const texte = jahre.map(formatiereJahr)
  const letztes = texte.at(-1)
  if (letztes === undefined) {
    return ''
  }
  return texte.length === 1 ? letztes : `${texte.slice(0, -1).join(', ')} und ${letztes}`
}

/** Der datengetriebene Satz zu fehlenden Liquiditätskrediten; `null`, wenn keine fehlen. */
export function liquiditaetsSatz(): string | null {
  const jahre = jahreOhneLiquiditaetskredite()
  return jahre.length === 0
    ? null
    : `Für ${jahreListe(jahre)} nennt der Haushaltsplan keine Liquiditätskredite.`
}

/**
 * Beschriftungen der Jahresachse: „{jahr}“ / Wertart, dazu „berechnet“ genau dort, wo
 * `schuldenstand.berechnet` wahr ist (dreizeilig, T-06-24).
 */
export function achsenZusatz(): string[] {
  const reihen = baueSchuldenstand()
  return jahresAchse(reihen.jahre, reihen.wertarten, reihen.berechnet)
}

/** `true`, wenn mindestens ein Jahr berechnet ist (sonst entfallen Achsenzeile und Erklärung). */
export function hatBerechneteJahre(): boolean {
  return baueSchuldenstand().berechnet.some((berechnet) => berechnet)
}

/** Werte der Kennzahlkacheln zum Schuldenstand am Ende des Vorjahrs. */
export interface SchuldenKennzahlen {
  /** Vorjahr des Haushaltsjahrs. */
  jahr: number
  /** Anzeigename der Wertart des Vorjahrs. */
  wertart: string
  gesamt: number
  proKopf: number
  /** Seite der Verbindlichkeiten-Tabelle. */
  quelle: number
  /** Seite der Einwohnerzahl (meta). */
  einwohnerQuelle: number
  /** Belege des Pro-Kopf-Werts: Verbindlichkeiten-Tabelle und Einwohnerzahl. */
  pdfSeiten: number[]
  /** `schuldenstand.berechnet` des Vorjahrs: gedruckt = `false`, dann kein Etikett. */
  berechnet: boolean
}

/**
 * Schuldenstand gesamt und je Einwohner am Ende des Vorjahrs (Haushaltsjahr − 1 über den
 * Index in `haushalt.jahre`, kein Jahr im Code).
 */
export function schuldenKennzahlen(): SchuldenKennzahlen {
  const reihen = baueSchuldenstand()
  const haushaltsIndex = haushalt.jahre.indexOf(haushalt.haushaltsjahr)
  if (haushaltsIndex < 1) {
    throw new Error('Das Haushaltsjahr hat kein Vorjahr in haushalt.jahre')
  }
  const index = haushaltsIndex - 1
  const jahr = reihen.jahre[index]
  const wertart = reihen.wertarten[index]
  const gesamt = reihen.gesamt[index]
  const proKopf = reihen.proKopf[index]
  const berechnet = reihen.berechnet[index]
  if (
    jahr === undefined ||
    wertart === undefined ||
    gesamt === undefined ||
    proKopf === undefined ||
    berechnet === undefined
  ) {
    throw new Error('Der Schuldenstand des Vorjahrs fehlt in investitionen.json')
  }
  const einwohnerQuelle = haushalt.meta.einwohner.quelle
  return {
    jahr,
    wertart: wertartName(wertart),
    gesamt,
    proKopf,
    quelle: reihen.pdfSeite,
    einwohnerQuelle,
    pdfSeiten: [reihen.pdfSeite, einwohnerQuelle],
    berechnet,
  }
}

/** Eine Kennzahlkachel zum Schuldenstand (D-10). */
export interface SchuldenKachel {
  schluessel: string
  bezeichnung: string
  wert: string
  zeile: string
  berechnet: boolean
}

export function schuldenKacheln(
  _kennzahlen: SchuldenKennzahlen = schuldenKennzahlen(),
): SchuldenKachel[] {
  return []
}

/** Randbreite der Weißtrenner zwischen den Segmenten (UI-SPEC: 2 px). */
const TRENNER = 2

const NAME_INVESTITIONSKREDITE = 'Investitionskredite'
const NAME_NRW_BANK = 'NRW.Bank'

/**
 * Option der gestapelten Säulen: Investitionskredite und NRW.Bank, die Gesamtsumme (aus
 * `schuldenstand.gesamt`) als Beschriftung über der Säule. Berechnete Jahre tragen
 * `BERECHNET_DECAL` und die dritte Achsenzeile, gedruckte beides nicht. Liquiditätskredite
 * kommen nie in den Stapel. Bis 699 px steht die Summe zweizeilig, damit sechs Beschriftungen
 * nebeneinander passen. Tooltips entstehen nur über `tooltipZeilen`.
 */
export function schuldenstandOption(schmal: boolean): EChartsOption {
  const reihen = baueSchuldenstand()
  const flaeche = flaechenFarbe()

  function daten(werte: readonly number[], farbe: string) {
    return werte.map((wert, index) => ({
      value: wert,
      itemStyle: {
        color: farbe,
        borderColor: flaeche,
        borderWidth: TRENNER,
        ...(reihen.berechnet[index] === true ? { decal: BERECHNET_DECAL } : {}),
      },
    }))
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
      data: achsenZusatz(),
      axisLabel: { interval: 0, rotate: 0 },
    },
    yAxis: {
      type: 'value',
      min: 0,
      // Luft über der höchsten Säule für die Summenbeschriftung.
      boundaryGap: [0, '12%'],
      axisLabel: { formatter: (wert: number) => euroKurz(wert) },
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params) => {
        const eintrag = Array.isArray(params) ? params[0] : params
        const index = eintrag?.dataIndex
        if (index === undefined) {
          return ''
        }
        return tooltipZeilen(tooltipTexte(reihen, index))
      },
    },
    series: [
      {
        type: 'bar',
        name: NAME_INVESTITIONSKREDITE,
        stack: 'schulden',
        data: daten(reihen.investitionskredite, SCHULDEN_FARBEN.investitionskredite),
      },
      {
        type: 'bar',
        name: NAME_NRW_BANK,
        stack: 'schulden',
        data: daten(reihen.nrwBank, SCHULDEN_FARBEN.nrw_bank),
        // Das oberste Segment trägt die Summe über dem Stapel.
        label: {
          show: true,
          position: 'top',
          lineHeight: 18,
          formatter: (params) => {
            const gesamt = reihen.gesamt[params.dataIndex]
            if (gesamt === undefined) {
              return KEIN_WERT
            }
            const text = euroKurz(gesamt)
            return schmal ? zweizeilig(text) : text
          },
        },
      },
    ],
  }
}

/** Tooltip-Zeilen eines Jahres (noch unmaskiert, `tooltipZeilen` maskiert). */
function tooltipTexte(reihen: Schuldenreihen, index: number): string[] {
  const jahr = reihen.jahre[index]
  const wertart = reihen.wertarten[index]
  if (jahr === undefined || wertart === undefined) {
    return []
  }
  const liquiditaet = reihen.liquiditaetskredite[index] ?? null
  const kopf = `${formatiereJahr(jahr)} · ${wertartName(wertart)}${reihen.berechnet[index] === true ? ' · berechnet' : ''}`
  return [
    kopf,
    `${NAME_INVESTITIONSKREDITE}: ${euro(reihen.investitionskredite[index] ?? 0)}`,
    `${NAME_NRW_BANK}: ${euro(reihen.nrwBank[index] ?? 0)}`,
    `Schuldenstand: ${euro(reihen.gesamt[index] ?? 0)}`,
    `Je Einwohner: ${euro(reihen.proKopf[index] ?? 0)}`,
    `Liquiditätskredite (nicht im Schuldenstand): ${liquiditaet === null ? KEIN_WERT : euro(liquiditaet)}`,
  ]
}

/** Spaltenschlüssel der Tabelle. */
const SPALTEN: readonly DatenSpalte[] = [
  { schluessel: 'jahr', titel: 'Jahr', art: 'text' },
  { schluessel: 'investitionskredite', titel: NAME_INVESTITIONSKREDITE, art: 'euro' },
  { schluessel: 'nrwBank', titel: NAME_NRW_BANK, art: 'euro' },
  { schluessel: 'gesamt', titel: 'Schuldenstand', art: 'euro' },
  {
    schluessel: 'liquiditaetskredite',
    titel: 'Liquiditätskredite (kurzfristig, nicht im Schuldenstand)',
    art: 'euro',
  },
  { schluessel: 'proKopf', titel: 'Je Einwohner', art: 'euro' },
]

/**
 * Tabelle der Schuldenreihen je Jahr. Ein fehlender Liquiditätskredit bleibt `null` und
 * erscheint als „–“ (nie 0); `etikett` ist „berechnet“ in berechneten Jahren (Etikett in der
 * ersten Zelle).
 */
export function schuldenTabelle(): Tabelle {
  const reihen = baueSchuldenstand()
  const zeilen: DatenZeile[] = reihen.jahre.map((jahr, index) => {
    const wertart = reihen.wertarten[index]
    return {
      jahr: `${formatiereJahr(jahr)} · ${wertart === undefined ? '' : wertartName(wertart)}`,
      etikett: reihen.berechnet[index] === true ? 'berechnet' : null,
      investitionskredite: reihen.investitionskredite[index] ?? null,
      nrwBank: reihen.nrwBank[index] ?? null,
      gesamt: reihen.gesamt[index] ?? null,
      liquiditaetskredite: reihen.liquiditaetskredite[index] ?? null,
      proKopf: reihen.proKopf[index] ?? null,
    }
  })
  return { spalten: [...SPALTEN], zeilen }
}
