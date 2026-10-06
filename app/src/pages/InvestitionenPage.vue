<script setup lang="ts">
import PageIntro from '@/components/PageIntro.vue'

// Die Seite zeigt alle ausgewiesenen Jahre, ohne Jahr-Umschalter (UI-SPEC Routes). Der Lead
// enthält keine Zahlen und darf deshalb als Text im Code stehen.
const lead =
  'Hier siehst du, was die Gemeinde in den kommenden Jahren baut und anschafft, wie sie das bezahlt und wie hoch ihre Schulden sind.'
</script>

<template>
  <div class="om-investitionen">
    <PageIntro titel="Investitionen und Schulden" :beschreibung="lead" />
  </div>
</template>

<style scoped>
.om-investitionen {
  max-width: 72rem;
  margin-inline: auto;
}
</style>
