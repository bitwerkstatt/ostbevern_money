<script setup lang="ts">
import { jahr as formatiereJahr } from '@/charts/format'
import PageIntro from '@/components/PageIntro.vue'
import { haushalt } from '@/data/daten'

// Die Seite zeigt immer alle ausgewiesenen Jahre, ohne Jahr-Umschalter (UI-SPEC Routes).
// Das letzte Jahr kommt aus den Daten, nie aus dem Quelltext.
const letztesJahr = formatiereJahr(
  haushalt.jahre[haushalt.jahre.length - 1] ?? haushalt.haushaltsjahr,
)
const lead = `Hier siehst du, wie sich Erträge, Aufwendungen und Ergebnis der Gemeinde bis ${letztesJahr} entwickeln und wie lange die Rücklagen als Polster reichen.`
</script>

<template>
  <div class="om-entwicklung">
    <PageIntro titel="Wie entwickelt sich der Haushalt?" :beschreibung="lead" />
  </div>
</template>

<style scoped>
.om-entwicklung {
  max-width: 72rem;
  margin-inline: auto;
}
</style>
