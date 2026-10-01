<script setup lang="ts">
import { computed } from 'vue'
import type { EChartsOption } from 'echarts'
import PageIntro from '@/components/PageIntro.vue'
import ChartCard from '@/components/ChartCard.vue'
import BaseChart from '@/components/BaseChart.vue'
import DatenTabelle from '@/components/DatenTabelle.vue'
import type { DatenSpalte, DatenZeile } from '@/components/datenTabelle'
import jahrgang from '@/data/jahrgang.json'
import beispieldaten from '@/data/beispieldaten.json'
import { euro, euroKurz } from '@/charts/format'
import { POL_FARBEN } from '@/charts/echartsTheme'
import { useSchmalerBildschirm } from '@/lib/bildschirm'

const istSchmal = useSchmalerBildschirm()

const chartOption = computed<EChartsOption>(() => {
  const kategorieAchse = {
    type: 'category' as const,
    data: beispieldaten.posten.map((posten) => posten.name),
  }
  const wertAchse = {
    type: 'value' as const,
    axisLabel: {
      formatter: (wert: number) => euroKurz(wert),
    },
  }
  const serie = {
    type: 'bar' as const,
    data: beispieldaten.posten.map((posten) => ({
      value: posten.wert,
      itemStyle: posten.wert < 0 ? { color: POL_FARBEN.negativ } : undefined,
    })),
  }

  return {
    xAxis: istSchmal.value ? wertAchse : kategorieAchse,
    yAxis: istSchmal.value ? kategorieAchse : wertAchse,
    tooltip: {
      trigger: 'axis',
      valueFormatter: (wert) => euro(wert as number),
    },
    series: [serie],
  }
})

const leereOption: EChartsOption = {
  xAxis: { type: 'category', data: [] },
  yAxis: { type: 'value' },
  series: [],
}

const tabellenSpalten: DatenSpalte[] = [
  { schluessel: 'name', titel: 'Bereich', art: 'text' },
  { schluessel: 'wert', titel: 'Betrag', art: 'euro' },
]

const tabellenZeilen = computed<DatenZeile[]>(() =>
  beispieldaten.posten.map((posten) => ({ name: posten.name, wert: posten.wert })),
)
</script>

<template>
  <PageIntro
    :titel="`Der Haushalt ${jahrgang.haushaltsjahr} der Gemeinde Ostbevern`"
    beschreibung="Diese Seite zeigt, wie die Grundbausteine der App aussehen. Die echten Zahlen kommen in den nächsten Phasen dazu."
  />
  <ChartCard
    :titel="beispieldaten.titel"
    beschreibung="Beispieldiagramm mit erfundenen Beträgen für vier Bereiche"
    :beispieldaten="beispieldaten.beispieldaten"
  >
    <BaseChart :option="chartOption" />
    <DatenTabelle
      beschriftung="Beispieldaten als Tabelle"
      :spalten="tabellenSpalten"
      :zeilen="tabellenZeilen"
    />
  </ChartCard>
  <ChartCard titel="Echte Haushaltszahlen">
    <BaseChart :option="leereOption" />
  </ChartCard>
</template>
