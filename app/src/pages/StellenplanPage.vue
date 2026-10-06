<script setup lang="ts">
import { jahr as formatiereJahr } from '@/charts/format'
import PageIntro from '@/components/PageIntro.vue'
import WertartEtikett from '@/components/WertartEtikett.vue'
import { haushalt } from '@/data/daten'
import { wertartFuerJahr } from '@/lib/jahr'

// Die Seite zeigt das Haushaltsjahr, ohne Jahr-Umschalter (UI-SPEC Routes). Jahr und Wertart
// kommen aus den Daten.
const haushaltsjahr = formatiereJahr(haushalt.haushaltsjahr)
const wertart = wertartFuerJahr(haushalt.haushaltsjahr)
const lead = `Hier siehst du, wie viele Stellen die Gemeinde ${haushaltsjahr} vorsieht, wie viele davon besetzt sind und in welchen Bereichen sie liegen.`
</script>

<template>
  <div class="om-stellenplan">
    <PageIntro titel="Wie viele Stellen hat die Verwaltung?" :beschreibung="lead">
      <WertartEtikett :wertart="wertart" />
    </PageIntro>
  </div>
</template>

<style scoped>
.om-stellenplan {
  max-width: 72rem;
  margin-inline: auto;
}
</style>
