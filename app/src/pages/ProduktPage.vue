<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

import { jahr as formatiereJahr } from '@/charts/format'
import PageIntro from '@/components/PageIntro.vue'
import { findeKnoten, findeProdukt } from '@/lib/ansicht'
import { useJahr } from '@/lib/jahr'

const route = useRoute()
const { jahr, jahrLink } = useJahr()

// Der Code kommt aus der URL: er wird nur über die Produkt-Map nachgeschlagen und im
// Fehlerfall als Text (nie als HTML) angezeigt.
const code = computed(() => {
  const roh = route.params.code
  return typeof roh === 'string' ? roh : ''
})

const produkt = computed(() => findeProdukt(code.value))

// „{Produktcode} · {Aufgabenbereich} · {Produktgruppe}“ (UI-SPEC /produkt/:code)
const kopfzeile = computed(() => {
  const gefunden = produkt.value
  if (gefunden === undefined) {
    return ''
  }
  return [gefunden.code, findeKnoten(gefunden.pb)?.name, findeKnoten(gefunden.pg)?.name]
    .filter((teil) => teil !== undefined)
    .join(' · ')
})
</script>

<template>
  <template v-if="produkt !== undefined">
    <PageIntro :titel="produkt.name" :beschreibung="kopfzeile" />
  </template>
  <template v-else>
    <PageIntro titel="Dieses Produkt gibt es nicht" beschreibung="" />
    <wa-callout variant="warning">
      <wa-icon slot="icon" name="triangle-exclamation"></wa-icon>
      Zum Code „{{ code }}“ gibt es im Haushalt {{ formatiereJahr(jahr) }} kein Produkt.
      <RouterLink :to="jahrLink({ name: 'ausgaben' })">Zur Ausgabenübersicht</RouterLink>
    </wa-callout>
  </template>
</template>
