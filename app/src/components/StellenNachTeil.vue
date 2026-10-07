<script setup lang="ts">
import { computed } from 'vue'
import type { BarSeriesOption, EChartsOption } from 'echarts'

import { HOHL_FLAECHE, NEUTRAL_DUNKEL_FARBE, NEUTRAL_MITTEL_FARBE } from '@/charts/echartsTheme'
import { datum, jahr as formatiereJahr, KEIN_WERT, vzae } from '@/charts/format'
import { tooltipZeilen } from '@/charts/tooltip'
import BaseChart from '@/components/BaseChart.vue'
import DatenTabelle from '@/components/DatenTabelle.vue'
import type { DatenSpalte, DatenZeile } from '@/components/datenTabelle'
import { stellenplan } from '@/data/daten'
import { useSchmalerBildschirm } from '@/lib/bildschirm'
import { alsVzae, stellenNachTeil, stellenSummen } from '@/lib/stellen'

// Gruppierte Säulen je Teil des Stellenplans (STEL-01, D-15): drei Säulen je Teil in fester
// Reihenfolge Haushaltsjahr, Vorjahr, besetzt am Stichtag. Die Summen kommen in Hundertstel aus
// `lib/stellen.ts` und werden nur zur Anzeige über `vzae()` formatiert.

const istSchmal = useSchmalerBildschirm()

/** Rand der hohlen „besetzt“-Säule in px (UI-SPEC: 2 px). */
const HOHL_RAND = 2
/** Platz über der höchsten Säule für die Direktwerte; schmal braucht die gedrehte Beschriftung mehr. */
const KOPFRAUM = 1.15
const KOPFRAUM_SCHMAL = 1.35

const teile = computed(() => stellenNachTeil())
const summen = computed(() => stellenSummen())

const hjText = computed(() => formatiereJahr(stellenplan.haushaltsjahr))
const vjText = computed(() => formatiereJahr(stellenplan.haushaltsjahr - 1))
const stichtagText = computed(() =>
  summen.value.stichtag === null ? null : datum(summen.value.stichtag),
)

const NAME_HJ = computed(() => `Stellen ${hjText.value}`)
const NAME_VJ = computed(() => `Stellen ${vjText.value}`)
const NAME_BESETZT = computed(() =>
  stichtagText.value === null ? 'Besetzt' : `Besetzt am ${stichtagText.value}`,
)

const legende = computed(
  () =>
    `dunkel: ${NAME_HJ.value} · hell: ${NAME_VJ.value} · mit Rand: ${
      stichtagText.value === null ? 'besetzt' : `besetzt am ${stichtagText.value}`
    }`,
)

const FARBE_DUNKEL = NEUTRAL_DUNKEL_FARBE
const FARBE_HELL = NEUTRAL_MITTEL_FARBE

type Feld = 'haushaltsjahr' | 'vorjahr' | 'besetzt'

interface SerieDef {
  feld: Feld
  name: string
  stil: BarSeriesOption['itemStyle']
}

const serien = computed<SerieDef[]>(() => [
  { feld: 'haushaltsjahr', name: NAME_HJ.value, stil: { color: FARBE_DUNKEL } },
  { feld: 'vorjahr', name: NAME_VJ.value, stil: { color: FARBE_HELL } },
  {
    feld: 'besetzt',
    name: NAME_BESETZT.value,
    stil: { color: HOHL_FLAECHE, borderColor: FARBE_DUNKEL, borderWidth: HOHL_RAND },
  },
])

/** Anzeigetext eines Hundertstelwerts; ohne Wert „–“, nie 0 (UI-SPEC E10 empty). */
function wertText(hundertstel: number | null): string {
  return hundertstel === null ? KEIN_WERT : vzae(alsVzae(hundertstel))
}

const hoechster = computed(() =>
  teile.value.reduce(
    (max, teil) => Math.max(max, teil.haushaltsjahr ?? 0, teil.vorjahr ?? 0, teil.besetzt ?? 0),
    0,
  ),
)

const option = computed<EChartsOption>(() => {
  const schmal = istSchmal.value
  const daten = serien.value
  return {
    grid: {
      left: 8,
      right: 8,
      top: 8,
      bottom: 8,
      outerBoundsMode: 'same',
      outerBoundsContain: 'axisLabel',
    },
    xAxis: {
      type: 'category',
      data: teile.value.map((teil) => teil.name),
      axisTick: { show: false },
      axisLabel: { interval: 0, width: schmal ? 90 : 200, overflow: 'break' },
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: hoechster.value * (schmal ? KOPFRAUM_SCHMAL : KOPFRAUM),
      axisLabel: { formatter: (wert: number) => vzae(alsVzae(wert)), hideOverlap: true },
    },
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        const eintrag = Array.isArray(params) ? params[0] : params
        const teil = eintrag === undefined ? undefined : teile.value[eintrag.dataIndex]
        const serie = eintrag === undefined ? undefined : daten[eintrag.seriesIndex ?? 0]
        return teil === undefined || serie === undefined
          ? ''
          : tooltipZeilen([teil.name, `${serie.name}: ${wertText(teil[serie.feld])} VZÄ`])
      },
    },
    series:
      teile.value.length === 0
        ? []
        : daten.map<BarSeriesOption>((serie) => ({
            type: 'bar',
            name: serie.name,
            barGap: '10%',
            barCategoryGap: '30%',
            itemStyle: serie.stil,
            // Ein fehlender Wert zeichnet keine Säule, bleibt aber mit „–“ beschriftet (nie 0).
            data: teile.value.map((teil) => teil[serie.feld] ?? 0),
            label: {
              show: true,
              position: 'top',
              formatter: (params) => wertText(teile.value[params.dataIndex]?.[serie.feld] ?? null),
              // Schmal stehen drei Werte je Teil auf wenig Breite: die Beschriftung läuft senkrecht.
              ...(schmal ? { rotate: 90, align: 'left', verticalAlign: 'middle' } : {}),
            },
          })),
  }
})

const spalten = computed<DatenSpalte[]>(() => [
  { schluessel: 'teil', titel: 'Teil des Stellenplans', art: 'text' },
  { schluessel: 'haushaltsjahr', titel: `${NAME_HJ.value} (VZÄ)`, art: 'dezimal' },
  { schluessel: 'vorjahr', titel: `${NAME_VJ.value} (VZÄ)`, art: 'dezimal' },
  { schluessel: 'besetzt', titel: `${NAME_BESETZT.value} (VZÄ)`, art: 'dezimal' },
])

function alsZeile(teil: string, werte: Record<Feld, number | null>): DatenZeile {
  const hundertstelZuVzae = (wert: number | null): number | null =>
    wert === null ? null : alsVzae(wert)
  return {
    teil,
    haushaltsjahr: hundertstelZuVzae(werte.haushaltsjahr),
    vorjahr: hundertstelZuVzae(werte.vorjahr),
    besetzt: hundertstelZuVzae(werte.besetzt),
  }
}

const tabelle = computed<DatenZeile[]>(() => [
  ...teile.value.map((teil) => alsZeile(teil.name, teil)),
  ...(teile.value.length === 0 ? [] : [alsZeile('Insgesamt', summen.value)]),
])

const fussnote = computed(() => {
  const seitenText = summen.value.pdfSeiten.join(', ')
  return seitenText === '' ? undefined : `Quelle: PDF-Seiten ${seitenText}.`
})

const beschreibung = computed(
  () =>
    `Gruppierte Säulen: Stellen in VZÄ je Teil des Stellenplans, jeweils ${hjText.value}, ${vjText.value} und der besetzte Stand. Dieselben Werte stehen in der Tabelle darunter.`,
)
</script>

<template>
  <div class="om-stellen-teil">
    <BaseChart
      :option="option"
      hoehe="320px"
      :beschreibung="beschreibung"
      leer-titel="Keine Stellen"
      leer-text="Der Haushaltsplan nennt hier keine Stellen. Öffne die Tabelle."
    />
    <p class="om-stellen-teil__legende">{{ legende }}</p>

    <wa-details summary="Tabelle anzeigen">
      <DatenTabelle
        beschriftung="Stellen nach Teil des Stellenplans"
        :spalten="spalten"
        :zeilen="tabelle"
        :fussnote="fussnote"
        leer-titel="Keine Stellen"
        leer-text="Der Haushaltsplan nennt hier keine Stellen."
      />
    </wa-details>
  </div>
</template>

<style scoped>
.om-stellen-teil {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-m);
  min-width: 0;
}

.om-stellen-teil__legende {
  margin: 0;
  font-size: var(--wa-font-size-s);
  color: var(--wa-color-text-quiet);
}
</style>
