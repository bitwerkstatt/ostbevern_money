<script setup lang="ts">
import PageIntro from '@/components/PageIntro.vue'
import jahrgang from '@/data/jahrgang.json'
</script>

<template>
  <PageIntro
    :titel="`Der Haushalt ${jahrgang.haushaltsjahr} der Gemeinde Ostbevern`"
    beschreibung="Diese Seite zeigt, wie die Grundbausteine der App aussehen. Die echten Zahlen kommen in den nächsten Phasen dazu."
  />
</template>
