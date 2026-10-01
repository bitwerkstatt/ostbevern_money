<script setup lang="ts">
import type { EChartsOption } from 'echarts'
import VChart from 'vue-echarts'
import { CHART_THEME } from '@/charts/echartsTheme'

const props = withDefaults(
  defineProps<{
    option: EChartsOption
    hoehe?: string
    beschreibung?: string
  }>(),
  {
    hoehe: '320px',
  },
)

const emit = defineEmits<{
  chartClick: [params: unknown]
}>()

function onClick(params: unknown) {
  emit('chartClick', params)
}
</script>

<template>
  <div
    class="om-base-chart"
    :style="{ height: props.hoehe }"
    role="img"
    :aria-label="props.beschreibung"
  >
    <VChart :option="props.option" :theme="CHART_THEME" autoresize @click="onClick" />
  </div>
</template>

<style scoped>
.om-base-chart {
  width: 100%;
}

.om-base-chart :deep(> div) {
  width: 100%;
  height: 100%;
}
</style>
