<script setup lang="ts">
import BerechnetEtikett from '@/components/BerechnetEtikett.vue'
import { betragMitHinweis } from '@/lib/geldfluss'

/**
 * Ein Euro-Betrag in einer Tabellenzelle: „rd.“ davor, wenn er nur auf T€ genau ist, und das
 * Etikett „berechnet“ dahinter, wenn er nicht im PDF steht. Die Regel steht nur hier (und in
 * `betragMitHinweis`), damit Tabellen und Tooltips nicht auseinanderlaufen.
 */
defineProps<{
  wert: number
  gerundet?: boolean
  berechnet?: boolean
}>()
</script>

<template>
  {{ betragMitHinweis(wert, gerundet === true) }}
  <BerechnetEtikett v-if="berechnet" />
</template>
