<script setup lang="ts">
import { computed } from 'vue'
import type { EChartsOption, LineSeriesOption } from 'echarts'

import { AUFWANDSART_FARBE, ERTRAG_FARBE } from '@/charts/echartsTheme'
import { euro, euroKurz, jahr as formatiereJahr, KEIN_WERT } from '@/charts/format'
import { tooltipZeilen } from '@/charts/tooltip'
import { LEGENDE_TEXT, flaechenFarbe, jahresAchse, linienSerie } from '@/charts/wertartStil'
import BaseChart from '@/components/BaseChart.vue'
import DatenTabelle from '@/components/DatenTabelle.vue'
import type { DatenSpalte, DatenZeile } from '@/components/datenTabelle'
import { haushalt } from '@/data/daten'
import { useSchmalerBildschirm } from '@/lib/bildschirm'
import { baueErgebnisReihen, type Jahreswert } from '@/lib/entwicklung'
import { wertartName } from '@/lib/jahr'
import { zeitreihenSerien } from '@/lib/zeitreihen'

const LEER_TITEL = 'Für diese Auswahl gibt es keine Einzelwerte'
const LEER_TEXT = 'Der Haushaltsplan nennt für diese Jahre keine Werte. Öffne die Tabelle.'
const BESCHREIBUNG =
  'Liniendiagramm: Erträge und Aufwendungen der Gemeinde je Jahr, getrennt nach Ist, Ansatz und Planung. Die Werte stehen in der Tabelle darunter.'

const istSchmal = useSchmalerBildschirm()
const reihen = baueErgebnisReihen()
const achse = jahresAchse(haushalt.jahre, haushalt.wertarten)

const hatWerte = [reihen.ertraege, reihen.aufwendungen].some((reihe) =>
  reihe.some((eintrag) => eintrag.wert !== null),
)
const letzterIndex = haushalt.jahre.length - 1

interface Linie {
  name: string
  reihe: readonly Jahreswert[]
  farbe: string
}

const ERTRAEGE: Linie = { name: 'Erträge', reihe: reihen.ertraege, farbe: ERTRAG_FARBE }
const AUFWENDUNGEN: Linie = {
  name: 'Aufwendungen',
  reihe: reihen.aufwendungen,
  farbe: AUFWANDSART_FARBE,
}

/**
 * Die Serien einer Linie, je Wertart eine. Die Serie, die das letzte Jahr trägt, bekommt die
 * Direktbeschriftung: rechtsbündig am letzten Punkt, über dem Punkt, wenn die Linie am Ende oben
 * liegt, sonst darunter. So bleibt der Text im Diagramm, auch bei sechs Jahren auf 360 px.
 */
function serienDerLinie(linie: Linie, oben: boolean, flaeche: string): LineSeriesOption[] {
  const { serien } = zeitreihenSerien(linie.reihe)
  let traeger = -1
  serien.forEach((serie, index) => {
    if (
      serie.werte[letzterIndex] !== null &&
      serie.werte[letzterIndex] !== undefined &&
      serie.geteilt[letzterIndex] !== true
    ) {
      traeger = index
    }
  })
  return serien.map((serie, index) => ({
    ...linienSerie(serie, linie.farbe, flaeche),
    name: `${linie.name} · ${wertartName(serie.wertart)}`,
    ...(index === traeger
      ? {
          endLabel: {
            show: true,
            formatter: linie.name,
            align: 'right' as const,
            verticalAlign: oben ? ('bottom' as const) : ('top' as const),
            distance: 0,
          },
        }
      : {}),
  }))
}

function betrag(wert: number | null): string {
  return wert === null ? KEIN_WERT : euro(wert)
}

const option = computed<EChartsOption>(() => {
  const flaeche = flaechenFarbe()
  // Die Linie mit dem größeren Endwert steht oben; der Text der anderen sitzt darunter.
  const ertraegeOben =
    (ERTRAEGE.reihe[letzterIndex]?.wert ?? 0) >= (AUFWENDUNGEN.reihe[letzterIndex]?.wert ?? 0)
  return {
    grid: {
      left: 8,
      right: istSchmal.value ? 8 : 16,
      top: 24,
      bottom: 8,
      outerBoundsMode: 'same',
      outerBoundsContain: 'axisLabel',
    },
    xAxis: {
      type: 'category',
      data: achse,
      // Alle Jahre bleiben sichtbar, auch auf schmalen Bildschirmen (zweizeilig, nie ausgelassen).
      axisLabel: { interval: 0, rotate: 0 },
    },
    yAxis: {
      type: 'value',
      min: 0,
      axisLabel: { formatter: (wert: number) => euroKurz(wert) },
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const eintrag = Array.isArray(params) ? params[0] : params
        const index = eintrag?.dataIndex
        const jahr = index === undefined ? undefined : haushalt.jahre[index]
        const wertart = index === undefined ? undefined : haushalt.wertarten[index]
        if (index === undefined || jahr === undefined || wertart === undefined) {
          return ''
        }
        return tooltipZeilen([
          `${formatiereJahr(jahr)} · ${wertartName(wertart)}`,
          ...[ERTRAEGE, AUFWENDUNGEN].map(
            (linie) => `${linie.name}: ${betrag(linie.reihe[index]?.wert ?? null)}`,
          ),
        ])
      },
    },
    // Ohne Werte keine Serien, damit `BaseChart` den Leerzustand zeigt.
    series: hatWerte
      ? [
          ...serienDerLinie(ERTRAEGE, ertraegeOben, flaeche),
          ...serienDerLinie(AUFWENDUNGEN, !ertraegeOben, flaeche),
        ]
      : [],
  }
})

const spalten: DatenSpalte[] = [
  { schluessel: 'jahr', titel: 'Jahr', art: 'text' },
  { schluessel: 'ertraege', titel: 'Erträge', art: 'euro' },
  { schluessel: 'aufwendungen', titel: 'Aufwendungen', art: 'euro' },
]

const tabelle: DatenZeile[] = hatWerte
  ? haushalt.jahre.map((jahr, index) => ({
      jahr: `${formatiereJahr(jahr)} · ${wertartName(haushalt.wertarten[index] ?? '')}`,
      ertraege: reihen.ertraege[index]?.wert ?? null,
      aufwendungen: reihen.aufwendungen[index]?.wert ?? null,
    }))
  : []

const seite = reihen.ertraege[0]?.pdfSeite ?? null
const fussnote =
  seite === null
    ? 'Beträge vor globalem Minderaufwand.'
    : `Quelle: Gesamtergebnisplan, PDF-Seite ${String(seite)}. Beträge vor globalem Minderaufwand.`
</script>

<template>
  <div class="om-entwicklungsdiagramm">
    <BaseChart
      :option="option"
      hoehe="320px"
      :beschreibung="BESCHREIBUNG"
      :leer-titel="LEER_TITEL"
      :leer-text="LEER_TEXT"
    />
    <p class="om-entwicklungsdiagramm__legende">{{ LEGENDE_TEXT }}</p>

    <wa-details summary="Tabelle anzeigen">
      <DatenTabelle
        beschriftung="Erträge und Aufwendungen je Jahr"
        :spalten="spalten"
        :zeilen="tabelle"
        :fussnote="fussnote"
        :leer-titel="LEER_TITEL"
        :leer-text="LEER_TEXT"
      />
    </wa-details>
  </div>
</template>

<style scoped>
.om-entwicklungsdiagramm {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-m);
  min-width: 0;
}

.om-entwicklungsdiagramm__legende {
  margin: 0;
  font-size: var(--wa-font-size-s);
  color: var(--wa-color-text-quiet);
}
</style>
