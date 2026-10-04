<script setup lang="ts">
import { computed } from 'vue'

import { euro, euroKurz, jahr as formatJahr } from '@/charts/format'
import KennzahlKachel from '@/components/KennzahlKachel.vue'
import PageIntro from '@/components/PageIntro.vue'
import { haushalt } from '@/data/daten'
import { baueKennzahlen, quellenZeile, type Kennzahl } from '@/lib/kennzahlen'

const jahrText = formatJahr(haushalt.haushaltsjahr)

const kennzahlen = computed(() =>
  baueKennzahlen().map((k) => ({
    ...k,
    wertText: wertText(k),
    zeile: quellenZeile(k.wertart, k.jahr, k.pdfSeiten),
  })),
)

function wertText(kennzahl: Kennzahl): string {
  return kennzahl.anzeige === 'kurz' ? euroKurz(kennzahl.wert) : euro(kennzahl.wert)
}
</script>

<template>
  <PageIntro
    :titel="`Der Haushalt ${jahrText} der Gemeinde Ostbevern`"
    beschreibung="Hier siehst du, woher das Geld der Gemeinde kommt und wofür sie es ausgibt. Alle Zahlen stammen direkt aus dem Haushaltsplan."
  />

  <section class="om-start__kennzahlen" aria-labelledby="om-start-kennzahlen">
    <h2 id="om-start-kennzahlen">Die wichtigsten Zahlen {{ jahrText }}</h2>
    <ul class="om-start__raster" role="list">
      <li v-for="k in kennzahlen" :key="k.schluessel">
        <KennzahlKachel
          :bezeichnung="k.bezeichnung"
          :wert="k.wertText"
          :zeile="k.zeile"
          :berechnet="k.berechnet"
        />
      </li>
    </ul>
  </section>
</template>

<style scoped>
.om-start__kennzahlen h2 {
  margin: 0 0 var(--wa-space-m);
  font-size: var(--wa-font-size-l);
  font-weight: var(--wa-font-weight-bold);
  line-height: var(--wa-line-height-condensed);
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-start__raster {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: var(--wa-space-m);
  margin: 0;
  padding: 0;
  list-style: none;
}

@media (min-width: 700px) {
  .om-start__raster {
    gap: var(--wa-space-l);
  }
}
</style>
