<script setup lang="ts">
import { computed, inject } from 'vue'
import type { EChartsOption } from 'echarts'
import VChart from 'vue-echarts'
import { CHART_THEME } from '@/charts/echartsTheme'
import { CHART_KONTEXT } from '@/components/chartKontext'

const props = withDefaults(
  defineProps<{
    option: EChartsOption
    hoehe?: string
    beschreibung?: string
    laedt?: boolean
    fehler?: boolean
  }>(),
  {
    hoehe: '320px',
  },
)

const emit = defineEmits<{
  chartClick: [params: unknown]
}>()

const kontext = inject(CHART_KONTEXT, undefined)

const ariaLabelledby = computed(() => {
  if (props.beschreibung || !kontext) {
    return undefined
  }
  const beschreibungId = kontext.beschreibungId()
  return beschreibungId ? `${kontext.titelId} ${beschreibungId}` : kontext.titelId
})

const istLeer = computed(() => {
  const series = props.option.series
  if (!series) {
    return true
  }
  const serienListe = Array.isArray(series) ? series : [series]
  if (serienListe.length === 0) {
    return true
  }
  return serienListe.every((eintrag) => {
    const daten = (eintrag as { data?: unknown[] }).data
    return !daten || daten.length === 0
  })
})

function onClick(params: unknown) {
  emit('chartClick', params)
}
</script>

<template>
  <div class="om-base-chart" :style="{ height: props.hoehe }">
    <wa-skeleton v-if="props.laedt" effect="sheen" class="om-base-chart__skeleton"></wa-skeleton>
    <div v-else-if="props.fehler" class="om-base-chart__zustand">
      <wa-icon name="triangle-exclamation"></wa-icon>
      <p>
        <slot name="fehler">
          Diagramm kann nicht angezeigt werden. Bitte lade die Seite neu. Besteht das Problem
          weiter, melde das Problem über GitHub Issues im Quell-Repository.
        </slot>
      </p>
    </div>
    <div v-else-if="istLeer" class="om-base-chart__zustand">
      <h3>Noch keine Daten</h3>
      <p>
        Die Haushaltsdaten werden ab Phase 2 automatisch aus dem PDF erzeugt und erscheinen hier,
        sobald die Pipeline gelaufen ist.
      </p>
    </div>
    <div
      v-else
      class="om-base-chart__chart"
      role="img"
      :aria-label="props.beschreibung"
      :aria-labelledby="ariaLabelledby"
    >
      <VChart :option="props.option" :theme="CHART_THEME" autoresize @click="onClick" />
    </div>
  </div>
</template>

<style scoped>
.om-base-chart {
  width: 100%;
}

.om-base-chart__skeleton {
  width: 100%;
  height: 100%;
}

.om-base-chart__chart {
  width: 100%;
  height: 100%;
}

.om-base-chart__chart :deep(> div) {
  width: 100%;
  height: 100%;
}

.om-base-chart__zustand {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--wa-space-xs);
  height: 100%;
  text-align: center;
  color: var(--wa-color-text-quiet);
}

.om-base-chart__zustand h3 {
  margin: 0;
  font-size: var(--wa-font-size-l);
  font-weight: var(--wa-font-weight-bold);
}

.om-base-chart__zustand p {
  margin: 0;
  max-width: 32rem;
}
</style>
