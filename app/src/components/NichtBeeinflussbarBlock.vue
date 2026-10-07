<script setup lang="ts">
import { computed } from 'vue'

import { euroKurz, jahr as formatJahr, kurzMitHinweis, prozent } from '@/charts/format'
import BerechnetEtikett from '@/components/BerechnetEtikett.vue'
import KennzahlKachel from '@/components/KennzahlKachel.vue'
import { haushalt } from '@/data/daten'
import { klAnteil } from '@/lib/bindungsgrad'
import { wertartFuerJahr, wertartName } from '@/lib/jahr'
import { quellenZeile } from '@/lib/kennzahlen'
import { nichtBeeinflussbar } from '@/lib/zuschuesse'

// RAT-02, D-02: große Posten, die der Rat nicht steuern kann. Die Kacheln nennen nur Betrag,
// Wertart, Jahr und PDF-Seite; sie bewerten nichts und deuten keinen Posten als Sparpotenzial.
// Die Kacheln der Weitergabe an Kreis und Land stammen aus `lib/kreisumlage.ts` und zeigen
// dieselben Werte wie /ausgaben.

const props = defineProps<{
  /** Summe aller Segmente des Bindungsgrad-Balkens in Euro; ohne Angabe entfällt der Vergleichssatz. */
  balkenSumme?: number
}>()

defineSlots<{
  /** Platz für weitere Hinweise unter dem Vergleichssatz. */
  vergleich?(): unknown
}>()

const wertart = wertartName(wertartFuerJahr(haushalt.haushaltsjahr))
const wertartZeile = `${wertart} ${formatJahr(haushalt.haushaltsjahr)}`

const lead =
  'Diese Beträge legen Gesetze sowie Kreis und Land fest, der Rat kann sie nicht steuern.'

const posten = computed(() => nichtBeeinflussbar())

// RAT-02, D-02: nur Betrag und Anteil, keine Aussage über die Größenordnung. Ohne Balkensumme
// (oder bei der Summe 0) gibt es keinen Anteil und damit keinen Satz.
const vergleich = computed(() => {
  if (props.balkenSumme === undefined) {
    return null
  }
  const anteil = klAnteil(posten.value.klGesamt, props.balkenSumme)
  return anteil === null
    ? null
    : { betrag: euroKurz(posten.value.klGesamt), anteil: prozent(anteil) }
})

const kacheln = computed(() =>
  posten.value.posten.map((p) => ({
    schluessel: p.schluessel,
    bezeichnung: p.name,
    wert: p.wert === null ? '' : kurzMitHinweis(p.wert, p.gerundet),
    quelle: p.beleg ?? undefined,
    zeile:
      p.pdfSeite === null
        ? wertartZeile
        : quellenZeile(wertart, haushalt.haushaltsjahr, [p.pdfSeite]),
  })),
)
</script>

<template>
  <section
    v-if="kacheln.length > 0"
    class="om-nicht-beeinflussbar"
    aria-labelledby="om-nicht-beeinflussbar-titel"
  >
    <h2 id="om-nicht-beeinflussbar-titel" class="om-nicht-beeinflussbar__titel">
      Was der Rat nicht beeinflussen kann
    </h2>
    <p class="om-nicht-beeinflussbar__lead">{{ lead }}</p>
    <ul class="om-kachelraster" role="list" lang="de">
      <li v-for="k in kacheln" :key="k.schluessel">
        <KennzahlKachel
          :bezeichnung="k.bezeichnung"
          :wert="k.wert"
          :zeile="k.zeile"
          :quelle="k.quelle"
          :wertart="wertartZeile"
        />
      </li>
    </ul>
    <div class="om-nicht-beeinflussbar__vergleich">
      <p v-if="vergleich !== null" class="om-nicht-beeinflussbar__satz">
        Die Weitergabe an Kreis und Land beträgt {{ vergleich.betrag }}. Das entspricht
        {{ vergleich.anteil }}<BerechnetEtikett /> der Summe im Balken oben.
      </p>
      <slot name="vergleich" />
    </div>
  </section>
</template>

<style scoped>
.om-nicht-beeinflussbar {
  margin-block-start: var(--wa-space-xl);
  min-width: 0;
}

.om-nicht-beeinflussbar__titel {
  margin: 0 0 var(--wa-space-m);
  font-size: var(--wa-font-size-l);
  font-weight: var(--wa-font-weight-bold);
  line-height: var(--wa-line-height-condensed);
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-nicht-beeinflussbar__lead {
  margin: 0 0 var(--wa-space-m);
  line-height: var(--wa-line-height-normal);
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-nicht-beeinflussbar__satz {
  margin: 0;
  line-height: var(--wa-line-height-normal);
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-nicht-beeinflussbar__vergleich:not(:empty) {
  margin-block-start: var(--wa-space-m);
}
</style>
