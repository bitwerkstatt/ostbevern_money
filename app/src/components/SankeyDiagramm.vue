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

// Bildbeschreibung (A11Y-01): ohne Zahl, die Werte und die Links stehen in den Tabellen darunter.
const BESCHREIBUNG =
  'Flussdiagramm: links stehen die Ertragsarten, in der Mitte der Gemeindehaushalt, rechts die Ausgaben. Die Breite der Bänder zeigt den Betrag. Dieselben Werte und die Links zu den Aufgabenbereichen stehen in den Tabellen darunter.'

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
  <BaseChart :option="option" hoehe="640px" :beschreibung="BESCHREIBUNG" @chart-click="beiKlick" />
</template>
