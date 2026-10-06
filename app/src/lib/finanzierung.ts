// Verpflichtungsermächtigungen (VE) und Finanzierung für `/investitionen` (INV-02, INV-03, D-08,
// D-10). Reine Funktionen über `investitionen.json` und `haushalt.json`: nichts wird neu
// gerechnet außer der Summe je Fälligkeitsjahr; kein Jahr steht im Code.

import type { EChartsOption } from 'echarts'

import { INVEST_FARBE } from '@/charts/echartsTheme'
import { euro, euroKurz, jahr as formatiereJahr } from '@/charts/format'
import { tooltipZeilen } from '@/charts/tooltip'
import type { DatenSpalte } from '@/components/datenTabelle'
import { investitionen } from '@/data/daten'
import type { Massnahme, VeFaelligkeit } from '@/data/typen'
import type { Tabelle } from '@/lib/produkt'

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
