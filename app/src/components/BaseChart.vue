<script setup lang="ts">
import { computed, inject } from 'vue'
import type { EChartsOption } from 'echarts'
import VChart from 'vue-echarts'
import { CHART_THEME } from '@/charts/echartsTheme'
import { CHART_KONTEXT } from '@/components/chartKontext'
import { ohneAnimation, useReducedMotion } from '@/lib/bewegung'

const props = withDefaults(
  defineProps<{
    option: EChartsOption
    hoehe?: string
    beschreibung?: string
    laedt?: boolean
    fehler?: boolean
    /** Überschrift des Leerzustands (UI-SPEC Copywriting). */
    leerTitel?: string
    /** Erklärtext des Leerzustands (UI-SPEC Copywriting). */
    leerText?: string
  }>(),
  {
    hoehe: '320px',
    leerTitel: 'Keine Einzelwerte',
    leerText:
      'Der Haushaltsplan nennt hier keine Aufschlüsselung. Wähle ein anderes Jahr oder öffne die Tabelle.',
  },
)

const emit = defineEmits<{
  chartClick: [params: unknown]
}>()

const kontext = inject(CHART_KONTEXT, undefined)
const reduzierteBewegung = useReducedMotion()

// Bei `prefers-reduced-motion: reduce` läuft jedes Diagramm ohne Animation
// (UI-SPEC Chart Contract „Bewegung“).
const chartOption = computed(() => ohneAnimation(props.option, reduzierteBewegung.value))

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
  // Eine Serie ist leer, wenn weder `data` noch (Sankey) `links`/`edges` Einträge haben.
  return serienListe.every((eintrag) => {
    const { data, links, edges } = eintrag as {
      data?: unknown[]
      links?: unknown[]
      edges?: unknown[]
    }
    return !data?.length && !links?.length && !edges?.length
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
          weiter, nutze den Kontakt in der Fußzeile.
        </slot>
      </p>
    </div>
    <div v-else-if="istLeer" class="om-base-chart__zustand">
      <h3>{{ props.leerTitel }}</h3>
      <p>{{ props.leerText }}</p>
    </div>
    <div
      v-else
      class="om-base-chart__chart"
      role="img"
      :aria-label="props.beschreibung"
      :aria-labelledby="ariaLabelledby"
    >
      <VChart :option="chartOption" :theme="CHART_THEME" autoresize @click="onClick" />
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
