<script setup lang="ts">
import { computed } from 'vue'
import type { BarSeriesOption, EChartsOption } from 'echarts'

import { KATEGORIE_FARBEN } from '@/charts/echartsTheme'
import { jahr as formatiereJahr, vzae } from '@/charts/format'
import { tooltipZeilen } from '@/charts/tooltip'
import BaseChart from '@/components/BaseChart.vue'
import DatenTabelle from '@/components/DatenTabelle.vue'
import type { DatenSpalte, DatenZeile } from '@/components/datenTabelle'
import { stellenplan } from '@/data/daten'
import { useSchmalerBildschirm } from '@/lib/bildschirm'
import { alsVzae, stellenNachGruppe, TEILE } from '@/lib/stellen'

// Säulen je Gruppe eines Teils (STEL-02, D-17): Kategorieachse = Gruppe wie gedruckt, sortiert
// von der niedrigen zur hohen Gruppe, Wert über jeder Säule. Ein Teil ohne Zeilen rendert nichts.

const props = defineProps<{
  /** Wert von `StellenplanZeile.teil`, z. B. „beamte“. */
  teil: string
}>()

const istSchmal = useSchmalerBildschirm()

/** Platz über der höchsten Säule für den Direktwert; schmal läuft die Beschriftung senkrecht. */
const KOPFRAUM = 1.15
const KOPFRAUM_SCHMAL = 1.35
/** Höchstbreite einer Säule in px, damit eine einzelne Gruppe nicht wie ein Block wirkt. */
const SAEULE_MAX = 48

const farbe = KATEGORIE_FARBEN[1] ?? '#545868'

const info = computed(() => TEILE.find((eintrag) => eintrag.teil === props.teil))
const zeilen = computed(() => stellenNachGruppe(props.teil))
const hjText = computed(() => formatiereJahr(stellenplan.haushaltsjahr))
const titel = computed(() => info.value?.gruppenTitel ?? props.teil)

const option = computed<EChartsOption>(() => {
  const schmal = istSchmal.value
  const hoechster = zeilen.value.reduce((max, zeile) => Math.max(max, zeile.stellen), 0)
  const serie: BarSeriesOption = {
    type: 'bar',
    barMaxWidth: SAEULE_MAX,
    itemStyle: { color: farbe },
    data: zeilen.value.map((zeile) => alsVzae(zeile.stellen)),
    label: {
      show: true,
      position: 'top',
      formatter: (params) => vzae(Number(params.value)),
      ...(schmal ? { rotate: 90, align: 'left', verticalAlign: 'middle' } : {}),
    },
  }
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
      data: zeilen.value.map((zeile) => zeile.gruppe),
      axisTick: { show: false },
      axisLabel: { interval: 0 },
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: alsVzae(hoechster) * (schmal ? KOPFRAUM_SCHMAL : KOPFRAUM),
      axisLabel: { formatter: (wert: number) => vzae(wert), hideOverlap: true },
    },
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        const eintrag = Array.isArray(params) ? params[0] : params
        const zeile = eintrag === undefined ? undefined : zeilen.value[eintrag.dataIndex]
        return zeile === undefined
          ? ''
          : tooltipZeilen([
              `${titel.value}: ${zeile.gruppe}`,
              `${vzae(alsVzae(zeile.stellen))} VZÄ`,
              `Stellenplan ${hjText.value}`,
            ])
      },
    },
    series: [serie],
  }
})

const beschreibung = computed(
  () =>
    `Säulendiagramm: Stellen in VZÄ ${hjText.value} je Gruppe, Bereich ${titel.value}, von der niedrigen zur hohen Gruppe. Dieselben Werte stehen in der Tabelle darunter.`,
)

const spalten: DatenSpalte[] = [
  { schluessel: 'gruppe', titel: 'Gruppe', art: 'text' },
  { schluessel: 'stellen', titel: 'Stellen (VZÄ)', art: 'dezimal' },
  { schluessel: 'quelle', titel: 'Quelle', art: 'text' },
]

const tabelle = computed<DatenZeile[]>(() =>
  zeilen.value.map((zeile) => ({
    gruppe: zeile.gruppe,
    stellen: alsVzae(zeile.stellen),
    quelle: `PDF-Seite ${String(zeile.pdfSeite)}`,
  })),
)
</script>

<template>
  <div v-if="zeilen.length > 0" class="om-stellen-gruppe">
    <BaseChart :option="option" hoehe="240px" :beschreibung="beschreibung" />

    <wa-details summary="Tabelle anzeigen">
      <DatenTabelle
        :beschriftung="`Stellen nach Gruppe: ${titel}`"
        :spalten="spalten"
        :zeilen="tabelle"
      />
    </wa-details>
  </div>
</template>

<style scoped>
.om-stellen-gruppe {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-m);
  min-width: 0;
}
</style>
