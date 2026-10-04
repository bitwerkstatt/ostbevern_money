<script setup lang="ts">
import { computed } from 'vue'

import BaseChart from '@/components/BaseChart.vue'
import { useSchmalerBildschirm } from '@/lib/bildschirm'
import {
  codeAusParams,
  zuschussBalkenHoehe,
  zuschussBalkenOption,
  type EbenenEintrag,
} from '@/lib/drilldown'

const props = defineProps<{
  eintraege: readonly EbenenEintrag[]
  /** Wertart des Jahres („Ist“, „Ansatz“, „Planung“) für den Tooltip. */
  wertartText: string
  /** Name der Ebene, deren Kinder die Balken zeigen (für die Bildbeschreibung). */
  elternName: string
}>()

const emit = defineEmits<{
  waehle: [code: string]
}>()

const istSchmal = useSchmalerBildschirm()

const option = computed(() =>
  zuschussBalkenOption(props.eintraege, {
    wertartText: props.wertartText,
    schmal: istSchmal.value,
  }),
)

// Ohne Einträge zeigt BaseChart den Leerzustand, der mehr Platz braucht als eine leere Balkenhöhe.
const hoehe = computed(() =>
  props.eintraege.length === 0 ? 240 : zuschussBalkenHoehe(props.eintraege.length),
)

const beschreibung = computed(
  () =>
    `Balkendiagramm Zuschussbedarf der Ebene ${props.elternName}. Überschüsse liegen links der Nulllinie. Dieselben Werte stehen in der Tabelle darunter.`,
)

function beiKlick(params: unknown) {
  const code = codeAusParams(params)
  if (code !== null && props.eintraege.some((e) => e.code === code)) {
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
