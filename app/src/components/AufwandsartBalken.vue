<script setup lang="ts">
import { computed } from 'vue'

import { balkenHoehe, horizontaleBalkenOption, type BalkenZeile } from '@/charts/balken'
import { AUFWANDSART_FARBE } from '@/charts/echartsTheme'
import BaseChart from '@/components/BaseChart.vue'
import { useSchmalerBildschirm } from '@/lib/bildschirm'

const props = defineProps<{
  zeilen: readonly BalkenZeile[]
  /** Zweite Tooltip-Zeile, z. B. „Ansatz 2026“. */
  wertartText: string
  /** Überschrift des Leerzustands, z. B. „Für 2026 gibt es keine Einzelwerte“. */
  leerTitel: string
}>()

const istSchmal = useSchmalerBildschirm()

// Alle Balken tragen die eine Aufwandsart-Farbe, nie Aufgabenbereichs-Farben (UI-SPEC).
const option = computed(() =>
  horizontaleBalkenOption(props.zeilen, {
    farbe: AUFWANDSART_FARBE,
    wertartText: props.wertartText,
    schmal: istSchmal.value,
  }),
)

const hoehe = computed(() =>
  props.zeilen.length === 0 ? '160px' : balkenHoehe(props.zeilen.length),
)
</script>

<template>
  <BaseChart
    :option="option"
    :hoehe="hoehe"
    :leer-titel="leerTitel"
    leer-text="Der Haushaltsplan nennt für dieses Jahr keine Aufschlüsselung. Wähle ein anderes Jahr oder öffne die Tabelle."
  />
</template>
