<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'

import BaseChart from '@/components/BaseChart.vue'
import { useJahr } from '@/lib/jahr'
import { geldflussOption, zielCodeAusKlick, type Geldfluss } from '@/lib/geldfluss'

const props = defineProps<{
  geldfluss: Geldfluss
  /** „{Wertart} {jahr}“ für die Tooltips. */
  wertartText: string
}>()

const router = useRouter()
const { jahrLink } = useJahr()

const option = computed(() => geldflussOption(props.geldfluss, { wertartText: props.wertartText }))

// Nur ein Klick auf einen Aufgabenbereich oder KL öffnet die Ausgaben (D-10); Ertragsknoten
// und Flüsse navigieren nicht. Der Tastaturpfad sind die Links in der Tabelle darunter.
function beiKlick(params: unknown) {
  const code = zielCodeAusKlick(params, props.geldfluss)
  if (code !== null) {
    void router.push(jahrLink({ name: 'ausgaben', query: { pb: code } }))
  }
}
</script>

<template>
  <BaseChart :option="option" hoehe="640px" @chart-click="beiKlick" />
</template>
