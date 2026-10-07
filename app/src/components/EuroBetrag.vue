<script setup lang="ts">
import BerechnetEtikett from '@/components/BerechnetEtikett.vue'
import { betragMitHinweis, kurzMitHinweis } from '@/charts/format'

/**
 * Ein Euro-Betrag in einer Tabellenzelle: „rd.“ davor, wenn er nur auf T€ genau ist, und das
 * Etikett „berechnet“ dahinter, wenn er nicht im PDF steht. Die Regel „rd.“/„rund“ steht nur in
 * `charts/format.ts`; diese Komponente ist ihre Template-Form plus das Etikett „berechnet“.
 * Mit `kurz` erscheint der Betrag gekürzt (`euroKurz`, z. B. „27,5 Mio. €“).
 */
defineProps<{
  wert: number
  gerundet?: boolean
  berechnet?: boolean
  kurz?: boolean
}>()
</script>

<template>
  {{
    kurz === true
      ? kurzMitHinweis(wert, gerundet === true)
      : betragMitHinweis(wert, gerundet === true)
  }}
  <BerechnetEtikett v-if="berechnet" />
</template>
