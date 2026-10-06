<script setup lang="ts">
import { computed } from 'vue'
import type { EChartsOption } from 'echarts'

import { BINDUNG_FARBEN } from '@/charts/echartsTheme'
import { euro, euroKurz, prozent } from '@/charts/format'
import { tooltipZeilen } from '@/charts/tooltip'
import { flaechenFarbe } from '@/charts/wertartStil'
import BaseChart from '@/components/BaseChart.vue'
import BerechnetEtikett from '@/components/BerechnetEtikett.vue'
import DatenTabelle from '@/components/DatenTabelle.vue'
import type { DatenSpalte, DatenZeile } from '@/components/datenTabelle'
import { produkteText, type BindungsgradModell, type BindungsSegment } from '@/lib/bindungsgrad'
import { useSchmalerBildschirm } from '@/lib/bildschirm'

// RAT-01, D-01: ein gestapelter Balken, drei Segmente in fester Reihenfolge (pflichtig, teils,
// freiwillig). Die Segmente tragen keinen Text; Name, Betrag und Anteil stehen ab 700 px unter
// dem Segment, bis 699 px in der Legendentabelle (UI-SPEC E4 overflow). Farbe ist nie alleiniger
// Träger: jede Zeile der Legende nennt den Namen.

const props = defineProps<{
  modell: BindungsgradModell
  /** „{Wertart} {jahr}“ für Tooltips und Spaltenkopf. */
  wertartText: string
}>()

const istSchmal = useSchmalerBildschirm()

/** Balkenhöhe und Diagrammhöhe in px (UI-SPEC Chart Contract). */
const BALKEN_HOEHE = 56
const DIAGRAMM_HOEHE = '160px'

const option = computed<EChartsOption>(() => {
  const nachName = new Map<string, BindungsSegment>(
    props.modell.segmente.map((s) => [s.bindungsgrad, s] as const),
  )
  const trenner = flaechenFarbe()
  return {
    grid: { left: 0, right: 0, top: 0, bottom: 0 },
    tooltip: {
      trigger: 'item',
      confine: true,
      formatter: (params: unknown) => {
        const name =
          typeof params === 'object' && params !== null && 'seriesName' in params
            ? params.seriesName
            : undefined
        const segment = typeof name === 'string' ? nachName.get(name) : undefined
        return segment === undefined
          ? ''
          : tooltipZeilen([
              segment.bezeichnung,
              `${euro(segment.summe)} · ${prozent(segment.anteil)}`,
              `${produkteText(segment.anzahl)} · ${props.wertartText}`,
            ])
      },
    },
    xAxis: { type: 'value', show: false, min: 0, max: props.modell.summe },
    yAxis: { type: 'category', show: false, data: [''] },
    series: props.modell.segmente.map((segment) => ({
      type: 'bar' as const,
      name: segment.bindungsgrad,
      stack: 'summe',
      data: [segment.summe],
      barWidth: BALKEN_HOEHE,
      label: { show: false },
      itemStyle: {
        color: BINDUNG_FARBEN[segment.bindungsgrad],
        borderColor: trenner,
        borderWidth: 2,
      },
      emphasis: { focus: 'series' as const },
    })),
  }
})

const beschreibung = computed(
  () =>
    `Gestapelter Balken: Zuschussbedarf nach Bindungsgrad, ${props.modell.segmente
      .map((s) => `${s.bezeichnung} ${euroKurz(s.summe)}`)
      .join(', ')}. Dieselben Werte stehen in der Tabelle.`,
)

/** Spaltenbreiten der Beschriftungen unter den Segmenten, proportional zum Betrag. */
const beschriftungsRaster = computed(() =>
  props.modell.segmente.map((s) => `minmax(0, ${String(s.summe)}fr)`).join(' '),
)

const spalten: DatenSpalte[] = [
  { schluessel: 'name', titel: 'Bindungsgrad', art: 'text' },
  { schluessel: 'anzahl', titel: 'Produkte', art: 'zahl' },
  { schluessel: 'summe', titel: 'Betrag', art: 'euro' },
  { schluessel: 'anteil', titel: 'Anteil', art: 'prozent' },
]

const zeilen = computed<DatenZeile[]>(() =>
  props.modell.segmente.map((segment) => ({
    name: segment.bezeichnung,
    anzahl: segment.anzahl,
    summe: segment.summe,
    anteil: segment.anteil,
    farbe: BINDUNG_FARBEN[segment.bindungsgrad],
  })),
)

const tabellenBeschriftung = computed(
  () => `Zuschussbedarf nach Bindungsgrad, ${props.wertartText}`,
)
</script>

<template>
  <BaseChart
    v-if="modell.segmente.length === 0"
    :option="{ series: [] }"
    :hoehe="DIAGRAMM_HOEHE"
    leer-titel="Kein Zuschussbedarf"
    leer-text="Für dieses Haushaltsjahr gibt es keine Produkte mit Zuschussbedarf."
  />
  <div v-else class="om-bindungsgrad">
    <p class="om-bindungsgrad__etikett">Summen und Anteile <BerechnetEtikett /></p>
    <BaseChart :option="option" :hoehe="DIAGRAMM_HOEHE" :beschreibung="beschreibung" />
    <ul
      v-if="!istSchmal"
      class="om-bindungsgrad__beschriftung"
      :style="{ gridTemplateColumns: beschriftungsRaster }"
      role="list"
    >
      <li v-for="segment in modell.segmente" :key="segment.bindungsgrad">
        <span class="om-bindungsgrad__name">{{ segment.bezeichnung }}</span>
        <span class="om-bindungsgrad__wert"
          >{{ euroKurz(segment.summe) }} · {{ prozent(segment.anteil) }}</span
        >
      </li>
    </ul>
    <component
      :is="istSchmal ? 'div' : 'wa-details'"
      :summary="istSchmal ? undefined : 'Tabelle anzeigen'"
      class="om-bindungsgrad__tabelle"
    >
      <DatenTabelle :beschriftung="tabellenBeschriftung" :spalten="spalten" :zeilen="zeilen">
        <template #zelle="{ zeile, spalte, wert }">
          <span v-if="spalte.schluessel === 'name'" class="om-bindungsgrad__legende">
            <span
              class="om-bindungsgrad__farbfeld"
              :style="{ backgroundColor: String(zeile.farbe) }"
              aria-hidden="true"
            ></span>
            {{ wert }}
          </span>
        </template>
      </DatenTabelle>
    </component>
  </div>
</template>

<style scoped>
.om-bindungsgrad {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-s);
  min-width: 0;
}

.om-bindungsgrad__etikett {
  margin: 0;
  font-size: var(--wa-font-size-s);
  color: var(--wa-color-text-quiet);
}

.om-bindungsgrad__beschriftung {
  display: grid;
  gap: 0;
  margin: 0;
  padding: 0;
  list-style: none;
}

.om-bindungsgrad__beschriftung > li {
  display: flex;
  flex-direction: column;
  min-width: 0;
  padding-inline-end: var(--wa-space-xs);
  overflow-wrap: anywhere;
  hyphens: auto;
}

.om-bindungsgrad__name {
  font-weight: var(--wa-font-weight-bold);
}

.om-bindungsgrad__wert {
  font-size: var(--wa-font-size-s);
}

.om-bindungsgrad__legende {
  display: inline-flex;
  align-items: flex-start;
  gap: var(--wa-space-xs);
}

.om-bindungsgrad__farbfeld {
  flex: none;
  width: 16px;
  height: 16px;
  margin-top: 2px;
  border-radius: var(--wa-border-radius-s);
}
</style>
