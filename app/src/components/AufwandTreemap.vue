<script setup lang="ts">
import { computed } from 'vue'
import type { EChartsOption } from 'echarts'

import { flaechenFarbe } from '@/charts/echartsTheme'
import { kurzMitHinweis } from '@/charts/format'
import BaseChart from '@/components/BaseChart.vue'
import { useSchmalerBildschirm } from '@/lib/bildschirm'
import {
  codeAusParams,
  eintragTooltip,
  kachelBeschriftet,
  klickZiel,
  type EbenenEintrag,
} from '@/lib/drilldown'

const props = defineProps<{
  eintraege: readonly EbenenEintrag[]
  /** Wertart des Jahres („Ist“, „Ansatz“, „Planung“) für den Tooltip. */
  wertartText: string
  /** Name der Ebene, deren Kinder die Kacheln zeigen (für die Bildbeschreibung). */
  elternName: string
}>()

const emit = defineEmits<{
  waehle: [code: string]
}>()

const istSchmal = useSchmalerBildschirm()

// Diagrammhöhe laut UI-SPEC: 480 px ab 700 px, 400 px bis 699 px.
const hoehe = computed(() => (istSchmal.value ? 400 : 480))
// Bezugsbreiten der Flächenheuristik (RESEARCH A3): Inhaltsbreite ab 700 px bzw. bei 360 px.
const bezugsbreite = computed(() => (istSchmal.value ? 328 : 900))

const nachCode = computed(() => new Map(props.eintraege.map((e) => [e.code, e] as const)))

// `{` und `}` leiten in ECharts Rich-Text-Abschnitte ein; Namen aus den Daten enthalten sie
// nicht, werden aber vorsorglich davon befreit.
function beschriftung(eintrag: EbenenEintrag): string {
  const name = eintrag.name.replace(/[{}]/g, '')
  const betrag = kurzMitHinweis(eintrag.wert, eintrag.gerundet)
  return `{n|${name}}\n{b|${betrag}}`
}

const option = computed<EChartsOption>(() => {
  const flaeche = flaechenFarbe()
  const summe = props.eintraege.reduce((s, e) => s + e.wert, 0)
  return {
    tooltip: {
      trigger: 'item',
      confine: true,
      formatter: (params: unknown) => {
        const code = codeAusParams(params)
        const eintrag = code === null ? undefined : nachCode.value.get(code)
        return eintrag === undefined ? '' : eintragTooltip(eintrag, props.wertartText)
      },
    },
    series: [
      {
        type: 'treemap',
        // Navigation läuft über den Router (D-06): kein natives Drilldown, Zoom oder Breadcrumb.
        roam: false,
        nodeClick: false,
        breadcrumb: { show: false },
        left: 0,
        top: 0,
        right: 0,
        bottom: 0,
        label: {
          position: 'insideTopLeft',
          padding: [6, 8],
          rich: {
            n: { fontSize: 14, fontWeight: 600, lineHeight: 20, color: flaeche },
            b: { fontSize: 14, fontWeight: 400, lineHeight: 20, color: flaeche },
          },
        },
        data: props.eintraege.map((eintrag) => {
          const beschriftet = kachelBeschriftet(
            eintrag.wert / summe,
            bezugsbreite.value,
            hoehe.value,
          )
          return {
            // Eindeutige ID als `name` (RESEARCH Pitfall 16); der Anzeigetext steht im Label.
            name: eintrag.code,
            value: eintrag.wert,
            code: eintrag.code,
            cursor: klickZiel(eintrag) === 'keins' ? 'default' : 'pointer',
            itemStyle: {
              color: eintrag.farbe,
              borderColor: flaeche,
              borderWidth: 2,
              ...(eintrag.decal === undefined ? {} : { decal: eintrag.decal }),
            },
            label: {
              show: beschriftet,
              formatter: beschriftung(eintrag),
              // KL-Streifen dürfen die Beschriftung nicht unlesbar machen: Pill in KL-Farbe.
              ...(eintrag.istKl
                ? { backgroundColor: eintrag.farbe, borderRadius: 4, padding: [4, 8] }
                : {}),
            },
          }
        }),
      },
    ],
  }
})

const beschreibung = computed(
  () =>
    `Flächendiagramm der Ebene ${props.elternName}. Dieselben Werte stehen in der Tabelle darunter.`,
)

function beiKlick(params: unknown) {
  const code = codeAusParams(params)
  if (code !== null && nachCode.value.has(code)) {
    emit('waehle', code)
  }
}
</script>

<template>
  <BaseChart
    :option="option"
    :hoehe="`${hoehe}px`"
    :beschreibung="beschreibung"
    leer-titel="Keine Unterteilung"
    leer-text="Auf dieser Ebene gibt es keine weiteren Einträge. Wähle in den Brotkrumen eine höhere Ebene."
    @chart-click="beiKlick"
  />
</template>
