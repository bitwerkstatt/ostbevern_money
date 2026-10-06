<script setup lang="ts">
import { computed } from 'vue'
import type { BarSeriesOption, EChartsOption } from 'echarts'

import { POL_FARBEN, SCHWELLE_FARBE } from '@/charts/echartsTheme'
import { euroKurz, jahr as formatiereJahr } from '@/charts/format'
import { tooltipZeilen } from '@/charts/tooltip'
import { jahresAchse, saeulenStil } from '@/charts/wertartStil'
import BaseChart from '@/components/BaseChart.vue'
import DatenTabelle from '@/components/DatenTabelle.vue'
import type { DatenSpalte, DatenZeile } from '@/components/datenTabelle'
import { haushalt } from '@/data/daten'
import { useSchmalerBildschirm } from '@/lib/bildschirm'
import { baueErgebnisReihen, ergebnisBeschriftung, ergebnisTabelle } from '@/lib/entwicklung'
import { wertartName } from '@/lib/jahr'

const LEER_TITEL = 'Für diese Auswahl gibt es keine Einzelwerte'
const LEER_TEXT = 'Der Haushaltsplan nennt für diese Jahre keine Werte. Öffne die Tabelle.'
const BESCHREIBUNG =
  'Säulendiagramm: Jahresergebnis der Gemeinde nach globalem Minderaufwand je Jahr. Ein Defizit liegt unter der Nulllinie, ein Überschuss darüber. Die Werte stehen in der Tabelle darunter.'

const istSchmal = useSchmalerBildschirm()
const reihen = baueErgebnisReihen()
const achse = jahresAchse(haushalt.jahre, haushalt.wertarten)
const hatWerte = reihen.ergebnisNach.some((eintrag) => eintrag.wert !== null)
const letzterIndex = haushalt.jahre.length - 1

/** Zweizeilig („Defizit“ über dem Betrag), damit die Beschriftung unter eine Säule passt. */
function beschriftung(wert: number | null): string {
  return ergebnisBeschriftung(wert).replace(' ', '\n')
}

const option = computed<EChartsOption>(() => {
  const daten = reihen.ergebnisNach.map(
    (eintrag, index): NonNullable<BarSeriesOption['data']>[number] => {
      const wert = eintrag.wert
      if (wert === null) {
        return { value: null }
      }
      const farbe = wert < 0 ? POL_FARBEN.negativ : POL_FARBEN.positiv
      // Auf schmalen Bildschirmen sechs Beschriftungen nebeneinander nicht lesbar: dann trägt nur
      // die letzte Säule einen Text, Tooltip und Tabelle tragen die übrigen Werte.
      const beschriftet = !istSchmal.value || index === letzterIndex
      return {
        value: wert,
        itemStyle: saeulenStil(eintrag.wertart, farbe),
        label: {
          show: beschriftet,
          position: wert < 0 ? 'bottom' : 'top',
          formatter: beschriftung(wert),
          lineHeight: 18,
        },
      }
    },
  )
  return {
    grid: {
      left: 8,
      right: istSchmal.value ? 28 : 16,
      top: 16,
      bottom: 8,
      outerBoundsMode: 'same',
      outerBoundsContain: 'axisLabel',
    },
    xAxis: {
      type: 'category',
      data: achse,
      // Die Beschriftung steht am unteren Rand, nicht an der Nulllinie, wo negative Säulen sie
      // überdecken würden.
      axisLine: { onZero: false },
      axisLabel: { interval: 0, rotate: 0 },
    },
    yAxis: {
      type: 'value',
      // Luft über und unter den Säulen für die zweizeiligen Beschriftungen; die Ticks bleiben glatt.
      boundaryGap: ['40%', '40%'],
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
        const wert = reihen.ergebnisNach[index]?.wert ?? null
        return tooltipZeilen([
          `${formatiereJahr(jahr)} · ${wertartName(wertart)} · ${ergebnisBeschriftung(wert, true)}`,
        ])
      },
    },
    // Ohne Werte keine Serie, damit `BaseChart` den Leerzustand zeigt.
    series: hatWerte
      ? [
          {
            type: 'bar',
            data: daten,
            // Die Nulllinie: 1 px in der ruhigen Textfarbe, ohne Beschriftung.
            markLine: {
              silent: true,
              symbol: 'none',
              label: { show: false },
              lineStyle: { color: SCHWELLE_FARBE, width: 1, type: 'solid' },
              data: [{ yAxis: 0 }],
            },
          },
        ]
      : [],
  }
})

const spalten: DatenSpalte[] = [
  { schluessel: 'jahr', titel: 'Jahr', art: 'text' },
  { schluessel: 'ertraege', titel: 'Erträge', art: 'euro' },
  { schluessel: 'aufwendungen', titel: 'Aufwendungen', art: 'euro' },
  { schluessel: 'ergebnisVor', titel: 'Ergebnis vor Minderaufwand', art: 'euro' },
  { schluessel: 'minderaufwand', titel: 'Globaler Minderaufwand (Kürzung)', art: 'euro' },
  { schluessel: 'ergebnisNach', titel: 'Ergebnis nach Minderaufwand', art: 'euro' },
]

const tabelle = computed<DatenZeile[]>(() =>
  hatWerte
    ? ergebnisTabelle().map((zeile) => ({
        jahr: `${formatiereJahr(zeile.jahr)} · ${wertartName(zeile.wertart)}`,
        ertraege: zeile.ertraege,
        aufwendungen: zeile.aufwendungen,
        ergebnisVor: zeile.ergebnisVor,
        minderaufwand: zeile.minderaufwand,
        ergebnisNach: zeile.ergebnisNach,
      }))
    : [],
)

const seite = reihen.ergebnisNach[0]?.pdfSeite ?? null
const fussnote =
  (seite === null ? '' : `Quelle: Gesamtergebnisplan, PDF-Seite ${String(seite)}. `) +
  'Der globale Minderaufwand kürzt den Aufwand und verbessert das Ergebnis.'
</script>

<template>
  <div class="om-ergebnisbalken">
    <BaseChart
      :option="option"
      hoehe="240px"
      :beschreibung="BESCHREIBUNG"
      :leer-titel="LEER_TITEL"
      :leer-text="LEER_TEXT"
    />

    <wa-details summary="Tabelle anzeigen">
      <DatenTabelle
        beschriftung="Jahresergebnis vor und nach globalem Minderaufwand je Jahr"
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
.om-ergebnisbalken {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-m);
  min-width: 0;
}
</style>
