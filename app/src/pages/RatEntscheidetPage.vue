<script setup lang="ts">
import PageIntro from '@/components/PageIntro.vue'
import WertartEtikett from '@/components/WertartEtikett.vue'
import { haushalt } from '@/data/daten'
import { wertartFuerJahr } from '@/lib/jahr'

// Die Seite zeigt das Haushaltsjahr, ohne Jahr-Umschalter: der Bindungsgrad ist eine Aussage
// zum Haushaltsjahr (UI-SPEC Routes). Die Wertart folgt aus den Daten.
const wertart = wertartFuerJahr(haushalt.haushaltsjahr)
const lead =
  'Nicht jeder Euro im Haushalt ist frei verfügbar. Hier siehst du, was der Rat beeinflussen kann und was vorgegeben ist.'
</script>

<template>
  <div class="om-rat-entscheidet">
    <PageIntro titel="Worüber entscheidet der Rat?" :beschreibung="lead">
      <WertartEtikett :wertart="wertart" />
    </PageIntro>
  </div>
</template>

<style scoped>
.om-rat-entscheidet {
  max-width: 72rem;
  margin-inline: auto;
}
</style>
