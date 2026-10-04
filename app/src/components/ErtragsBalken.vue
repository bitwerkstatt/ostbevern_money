<script setup lang="ts">
import { computed } from 'vue'

import { balkenHoehe, horizontaleBalkenOption, type BalkenZeile } from '@/charts/balken'
import { ERTRAG_FARBE } from '@/charts/echartsTheme'
import BaseChart from '@/components/BaseChart.vue'
import { useSchmalerBildschirm } from '@/lib/bildschirm'

const props = withDefaults(
  defineProps<{
    zeilen: readonly BalkenZeile[]
    /** Standardfarbe der Balken; Ertragsarten gold, investive Einnahmen `INVEST_FARBE`. */
    farbe?: string
    /** Zweite Tooltip-Zeile, z. B. „Ansatz 2026“. */
    wertartText: string
    /** Überschrift des Leerzustands, z. B. „Für 2026 gibt es keine Einzelwerte“. */
    leerTitel: string
  }>(),
  { farbe: ERTRAG_FARBE },
)

const emit = defineEmits<{
  waehle: [schluessel: string]
}>()

const istSchmal = useSchmalerBildschirm()

const option = computed(() =>
  horizontaleBalkenOption(props.zeilen, {
    farbe: props.farbe,
    wertartText: props.wertartText,
    schmal: istSchmal.value,
  }),
)

// Ohne Zeilen braucht der Leerzustand mehr Platz als die 48 px der Balkenregel.
const hoehe = computed(() =>
  props.zeilen.length === 0 ? '160px' : balkenHoehe(props.zeilen.length),
)

/** Der Klick liefert `unknown`; nur ein gültiger `dataIndex` führt zu einer Zeile. */
function beiKlick(params: unknown) {
  if (typeof params !== 'object' || params === null || !('dataIndex' in params)) {
    return
  }
  const index = params.dataIndex
  if (typeof index !== 'number') {
    return
  }
  const zeile = props.zeilen[index]
  if (zeile !== undefined) {
    emit('waehle', zeile.schluessel)
  }
}
</script>

<template>
  <BaseChart
    :option="option"
    :hoehe="hoehe"
    :leer-titel="leerTitel"
    leer-text="Der Haushaltsplan nennt für dieses Jahr keine Aufschlüsselung. Wähle ein anderes Jahr oder öffne die Tabelle."
    @chart-click="beiKlick"
  />
</template>
