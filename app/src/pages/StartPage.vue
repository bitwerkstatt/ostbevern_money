<script setup lang="ts">
import { computed } from 'vue'
import type { EChartsOption } from 'echarts'
import PageIntro from '@/components/PageIntro.vue'
import ChartCard from '@/components/ChartCard.vue'
import BaseChart from '@/components/BaseChart.vue'
import jahrgang from '@/data/jahrgang.json'
import beispieldaten from '@/data/beispieldaten.json'
import { euro, euroKurz } from '@/charts/format'
import { POL_FARBEN } from '@/charts/echartsTheme'

const chartOption = computed<EChartsOption>(() => ({
  xAxis: {
    type: 'category',
    data: beispieldaten.posten.map((posten) => posten.name),
  },
  yAxis: {
    type: 'value',
    axisLabel: {
      formatter: (wert: number) => euroKurz(wert),
    },
  },
  tooltip: {
    trigger: 'axis',
    valueFormatter: (wert) => euro(wert as number),
  },
  series: [
    {
      type: 'bar',
      data: beispieldaten.posten.map((posten) => ({
        value: posten.wert,
        itemStyle: posten.wert < 0 ? { color: POL_FARBEN.negativ } : undefined,
      })),
    },
  ],
}))

const leereOption: EChartsOption = {
  xAxis: { type: 'category', data: [] },
  yAxis: { type: 'value' },
  series: [],
}
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
  </ChartCard>
  <ChartCard titel="Echte Haushaltszahlen">
    <BaseChart :option="leereOption" />
  </ChartCard>
</template>
