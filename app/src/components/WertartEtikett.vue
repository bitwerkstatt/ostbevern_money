<script setup lang="ts">
import { wertartName } from '@/lib/jahr'

// Der Text trägt die Information („Ist“, „Ansatz“, „Planung“); keine Farbcodierung je
// Wertart (UI-SPEC „Farbe nie allein“).
defineProps<{
  /** Wertart aus `haushalt.wertarten` (`ergebnis`, `ansatz`, `planung`). */
  wertart: string
}>()
</script>

<template>
  <wa-tag size="small" variant="neutral">{{ wertartName(wertart) }}</wa-tag>
</template>
