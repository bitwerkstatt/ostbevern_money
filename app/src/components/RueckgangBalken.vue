<script setup lang="ts">
import { computed } from 'vue'
import type { BarSeriesOption, EChartsOption } from 'echarts'

import { HOHL_FLAECHE, KATEGORIE_FARBEN, SCHWELLE_FARBE } from '@/charts/echartsTheme'
import { jahr as formatiereJahr, KEIN_WERT, prozent } from '@/charts/format'
import { tooltipZeilen } from '@/charts/tooltip'
import { jahresAchse, saeulenStil } from '@/charts/wertartStil'
import BaseChart from '@/components/BaseChart.vue'
import { useSchmalerBildschirm } from '@/lib/bildschirm'
import { wertartName } from '@/lib/jahr'
import { hskSchwellen, rueckgangAchsenMaximum, rueckgangPlanjahre } from '@/lib/ruecklagen'

const LEER_TITEL = 'Für diese Auswahl gibt es keine Einzelwerte'
const LEER_TEXT = 'Der Haushaltsplan nennt für diese Jahre keine Rücklagen. Öffne die Tabelle.'
const BESCHREIBUNG =
  'Säulendiagramm: Rückgang der allgemeinen Rücklage je Jahr in Prozent des Bestands zu Jahresbeginn, mit einer gestrichelten Linie bei der Schwelle für zwei aufeinanderfolgende Jahre. Die Werte stehen in der Tabelle darunter.'
const MIN_PLANJAHRE = 2
/** Breite der Linienbeschriftung in px: auf schmalen Bildschirmen bricht sie früher um. */
const BESCHRIFTUNG_BREITE_SCHMAL = 170
const BESCHRIFTUNG_BREITE = 320

const istSchmal = useSchmalerBildschirm()
const planjahre = rueckgangPlanjahre()
const schwellen = hskSchwellen()
const achse = jahresAchse(
  planjahre.map((eintrag) => eintrag.jahr),
  planjahre.map((eintrag) => eintrag.wertart),
)
const werte = planjahre.flatMap((eintrag) => (eintrag.anteil === null ? [] : [eintrag.anteil]))
const hatWerte = werte.length > 0
/** Mit nur einem Planjahr gibt es keinen Verlauf: das Diagramm entfällt, die Tabelle bleibt. */
const zeigeDiagramm = planjahre.length >= MIN_PLANJAHRE
const achsenMaximum = rueckgangAchsenMaximum(werte, schwellen.zweiJahre)
const schwellenText = `Schwelle bei zwei Jahren in Folge: ${prozent(schwellen.zweiJahre)}`

const option = computed<EChartsOption>(() => {
  const farbe = KATEGORIE_FARBEN[1] ?? ''
  const daten = planjahre.map((eintrag): NonNullable<BarSeriesOption['data']>[number] =>
    eintrag.anteil === null
      ? { value: null }
      : {
          value: eintrag.anteil,
          itemStyle: saeulenStil(eintrag.wertart, farbe),
          label: { show: true, position: 'top', formatter: prozent(eintrag.anteil) },
        },
  )
  return {
    grid: {
      left: 8,
      right: istSchmal.value ? 28 : 16,
      top: 24,
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
      max: achsenMaximum,
      axisLabel: { formatter: (wert: number) => prozent(wert) },
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const eintrag = Array.isArray(params) ? params[0] : params
        const index = eintrag?.dataIndex
        const jahr = index === undefined ? undefined : planjahre[index]
        if (jahr === undefined) {
          return ''
        }
        const anteil = jahr.anteil === null ? KEIN_WERT : prozent(jahr.anteil)
        return tooltipZeilen([
          `${formatiereJahr(jahr.jahr)} · ${wertartName(jahr.wertart)} · Rückgang im Jahr (berechnet): ${anteil}`,
          schwellenText,
        ])
      },
    },
    // Ohne Werte keine Serie, damit `BaseChart` den Leerzustand zeigt.
    series: hatWerte
      ? [
          {
            type: 'bar',
            itemStyle: { color: farbe },
            data: daten,
            // Die Schwelle ist ein Bezug, kein Alarm: gestrichelt in der ruhigen Textfarbe, die
            // Beschriftung links über der Linie auf der Kartenfläche und mit Umbruch.
            markLine: {
              silent: true,
              symbol: 'none',
              lineStyle: { color: SCHWELLE_FARBE, width: 2, type: [6, 4] },
              label: {
                show: true,
                formatter: schwellenText,
                position: 'insideStartTop',
                color: SCHWELLE_FARBE,
                backgroundColor: HOHL_FLAECHE,
                padding: [2, 4],
                width: istSchmal.value ? BESCHRIFTUNG_BREITE_SCHMAL : BESCHRIFTUNG_BREITE,
                overflow: 'break',
              },
              data: [{ yAxis: schwellen.zweiJahre }],
            },
          },
        ]
      : [],
  }
})
</script>

<template>
  <BaseChart
    v-if="zeigeDiagramm"
    :option="option"
    hoehe="200px"
    :beschreibung="BESCHREIBUNG"
    :leer-titel="LEER_TITEL"
    :leer-text="LEER_TEXT"
  />
</template>
