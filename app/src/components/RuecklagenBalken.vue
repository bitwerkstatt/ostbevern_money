<script setup lang="ts">
import { computed } from 'vue'
import type { BarSeriesOption, EChartsOption } from 'echarts'

import { KATEGORIE_FARBEN } from '@/charts/echartsTheme'
import { euro, euroKurz, jahr as formatiereJahr, KEIN_WERT } from '@/charts/format'
import { zweizeilig } from '@/charts/beschriftung'
import { tooltipZeilen } from '@/charts/tooltip'
import { flaechenFarbe, jahresAchse, saeulenStil } from '@/charts/wertartStil'
import BaseChart from '@/components/BaseChart.vue'
import { haushalt } from '@/data/daten'
import { useSchmalerBildschirm } from '@/lib/bildschirm'
import { wertartName } from '@/lib/jahr'
import { baueRuecklagen } from '@/lib/ruecklagen'

const LEER_TITEL = 'Für diese Auswahl gibt es keine Einzelwerte'
const LEER_TEXT = 'Der Haushaltsplan nennt für diese Jahre keine Rücklagen. Öffne die Tabelle.'
const BESCHREIBUNG =
  'Säulendiagramm: Ausgleichsrücklage und allgemeine Rücklage der Gemeinde als Bestand zu Jahresbeginn je Jahr, mit der Summe über jeder Säule. Die Werte stehen in der Tabelle darunter.'
/** Die Spaltenüberschrift von S. 311, wörtlich: die Werte sind der Bestand zu Jahresbeginn. */
const ACHSEN_UNTERSCHRIFT = 'Bestand zu Jahresbeginn'

const AUSGLEICH_NAME = 'Ausgleichsrücklage'
const ALLGEMEINE_NAME = 'Allgemeine Rücklage'
const SUMME_NAME = 'Summe'
/** Trennlinie zwischen den gestapelten Segmenten (UI-SPEC: 2 px in der Kartenfläche). */
const TRENNER_BREITE = 2
/** Name des gemeinsamen Stapels. */
const STAPEL = 'ruecklagen'

const istSchmal = useSchmalerBildschirm()
const zeilen = baueRuecklagen()
const achse = jahresAchse(haushalt.jahre, haushalt.wertarten)
const hatWerte = zeilen.some((zeile) => zeile.allgemeine !== null || zeile.ausgleich !== null)
const letzterIndex = zeilen.length - 1

type Segment = NonNullable<BarSeriesOption['data']>[number]

/**
 * Ein Segment der Säule. Ein fehlender Wert bleibt leer, eine echte 0 zeichnet nichts (weder Fläche
 * noch Rand), steht aber in Tooltip und Tabelle als „0 €“.
 */
function segment(wert: number | null, wertart: string, farbe: string, flaeche: string): Segment {
  if (wert === null) {
    return { value: null }
  }
  if (wert === 0) {
    return { value: 0, itemStyle: { color: 'transparent', borderWidth: 0 } }
  }
  const stil = saeulenStil(wertart, farbe)
  return {
    value: wert,
    itemStyle:
      wertart === 'planung' ? stil : { ...stil, borderColor: flaeche, borderWidth: TRENNER_BREITE },
  }
}

/**
 * Zweizeilig („38,8“ über „Mio. €“), damit die Summe über eine schmale Säule passt. Auch Beträge
 * unter 1 Mio. € („712.600“ über „€“) brechen vor „€“ um.
 */
function summenText(wert: number): string {
  return zweizeilig(euroKurz(wert))
}

function betragText(wert: number | null): string {
  return wert === null ? KEIN_WERT : euro(wert)
}

const option = computed<EChartsOption>(() => {
  const flaeche = flaechenFarbe()
  const farbeAusgleich = KATEGORIE_FARBEN[1] ?? ''
  const farbeAllgemeine = KATEGORIE_FARBEN[2] ?? ''
  return {
    legend: { data: [AUSGLEICH_NAME, ALLGEMEINE_NAME], top: 0, icon: 'rect', itemGap: 16 },
    grid: {
      left: 8,
      right: istSchmal.value ? 28 : 16,
      top: 72,
      bottom: 8,
      outerBoundsMode: 'same',
      outerBoundsContain: 'axisLabel',
    },
    xAxis: {
      type: 'category',
      data: achse,
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
        const zeile = index === undefined ? undefined : zeilen[index]
        if (zeile === undefined) {
          return ''
        }
        return tooltipZeilen([
          `${formatiereJahr(zeile.jahr)} · ${wertartName(zeile.wertart)} · ${ACHSEN_UNTERSCHRIFT}`,
          `${ALLGEMEINE_NAME}: ${betragText(zeile.allgemeine)}`,
          `${AUSGLEICH_NAME}: ${betragText(zeile.ausgleich)}`,
          `${SUMME_NAME}: ${betragText(zeile.summe)}`,
        ])
      },
    },
    // Ohne Werte keine Serien, damit `BaseChart` den Leerzustand zeigt.
    series: hatWerte
      ? [
          {
            type: 'bar',
            name: AUSGLEICH_NAME,
            stack: STAPEL,
            itemStyle: { color: farbeAusgleich },
            data: zeilen.map((zeile) =>
              segment(zeile.ausgleich, zeile.wertart, farbeAusgleich, flaeche),
            ),
          },
          {
            type: 'bar',
            name: ALLGEMEINE_NAME,
            stack: STAPEL,
            itemStyle: { color: farbeAllgemeine },
            data: zeilen.map((zeile) =>
              segment(zeile.allgemeine, zeile.wertart, farbeAllgemeine, flaeche),
            ),
          },
          // Unsichtbare Linie auf der Säulenspitze: sie trägt nur die Summe über der Säule. Auf
          // schmalen Bildschirmen steht nur die letzte Summe, die übrigen stehen in Tooltip und Tabelle.
          {
            type: 'line',
            name: SUMME_NAME,
            silent: true,
            symbol: 'none',
            lineStyle: { opacity: 0 },
            tooltip: { show: false },
            data: zeilen.map((zeile, index) => ({
              value: zeile.summe,
              label: {
                show: zeile.summe !== null && (!istSchmal.value || index === letzterIndex),
                position: 'top',
                formatter: zeile.summe === null ? '' : summenText(zeile.summe),
                lineHeight: 18,
              },
            })),
          },
        ]
      : [],
  }
})
</script>

<template>
  <div class="om-ruecklagen">
    <BaseChart
      :option="option"
      hoehe="320px"
      :beschreibung="BESCHREIBUNG"
      :leer-titel="LEER_TITEL"
      :leer-text="LEER_TEXT"
    />
    <p v-if="hatWerte" class="om-ruecklagen__unterschrift">{{ ACHSEN_UNTERSCHRIFT }}</p>
  </div>
</template>

<style scoped>
.om-ruecklagen {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-xs);
  min-width: 0;
}

.om-ruecklagen__unterschrift {
  margin: 0;
  text-align: center;
  font-size: var(--wa-font-size-s);
  color: var(--wa-color-text-quiet);
}
</style>
