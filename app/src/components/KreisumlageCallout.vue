<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'

import { euroKurz, jahr as formatJahr } from '@/charts/format'
import ErklaerText from '@/components/ErklaerText.vue'
import { haushalt } from '@/data/daten'
import { baueKreisumlage } from '@/lib/kreisumlage'
import { textFuerJahr } from '@/lib/texte'

const props = withDefaults(
  defineProps<{
    jahrIndex: number
    /** Anzeigename der Wertart des Jahres, z. B. „Ansatz“ (liefert die Seite). */
    wertart: string
    kurz?: boolean
  }>(),
  { kurz: false },
)

const kreisumlage = computed(() => baueKreisumlage(props.jahrIndex))
const jahrZahl = computed(() => {
  const jahr = haushalt.jahre[props.jahrIndex]
  if (jahr === undefined) {
    throw new Error(`Jahresindex ${String(props.jahrIndex)} liegt außerhalb der Jahre`)
  }
  return jahr
})
const jahrText = computed(() => formatJahr(jahrZahl.value))
const hatErklaerung = computed(() => textFuerJahr('kreisumlage', jahrZahl.value) !== null)

const aufteilungSeiten = computed(() => {
  const seiten = new Set<number>()
  for (const u of kreisumlage.value.unterposten) {
    if (u.pdfSeite !== null) {
      seiten.add(u.pdfSeite)
    }
  }
  return [...seiten].join(', ')
})
</script>

<template>
  <wa-callout variant="neutral" class="om-kreisumlage">
    <wa-icon slot="icon" name="circle-info"></wa-icon>

    <template v-if="kurz">
      <p>
        Der größte Einzelposten ist die Weitergabe an Kreis und Land:
        <span class="om-zahl">{{ euroKurz(kreisumlage.gesamt) }}</span
        >. Diesen Betrag reicht Ostbevern weiter, die Gemeinde kann ihn nicht selbst steuern.
      </p>
      <p v-if="kreisumlage.pdfSeite !== null" class="om-kreisumlage__quelle">
        Quelle: PDF-Seite {{ kreisumlage.pdfSeite }}
      </p>
      <p>
        <RouterLink :to="{ name: 'ausgaben' }">Mehr dazu bei den Ausgaben</RouterLink>
      </p>
    </template>

    <template v-else>
      <p>
        Weitergabe an Kreis und Land:
        <span class="om-zahl">{{ euroKurz(kreisumlage.gesamt) }}</span> ({{ wertart }}
        {{ jahrText }}). Diesen Betrag reicht Ostbevern weiter und kann ihn nicht selbst steuern.
      </p>
      <ul class="om-kreisumlage__liste">
        <li v-for="u in kreisumlage.unterposten" :key="u.code">
          {{ u.name }}:
          <span class="om-zahl">rd. {{ euroKurz(u.wert) }}</span>
        </li>
      </ul>
      <p class="om-kreisumlage__quelle">
        Quelle:
        <template v-if="kreisumlage.pdfSeite !== null">
          PDF-Seite {{ kreisumlage.pdfSeite }} (Gesamtbetrag)<template v-if="aufteilungSeiten"
            >,
          </template>
        </template>
        <template v-if="aufteilungSeiten">PDF-Seite {{ aufteilungSeiten }} (Aufteilung)</template>
      </p>
      <wa-details v-if="hatErklaerung" summary="So funktioniert die Kreisumlage">
        <ErklaerText schluessel="kreisumlage" :jahr="jahrZahl" :ueberschrift="false" />
      </wa-details>
    </template>
  </wa-callout>
</template>

<style scoped>
.om-kreisumlage {
  display: block;
  width: 100%;
}

.om-kreisumlage p {
  margin: 0 0 var(--wa-space-s);
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-kreisumlage__liste {
  margin: 0 0 var(--wa-space-s);
  padding-inline-start: var(--wa-space-l);
}

.om-kreisumlage__quelle {
  font-size: var(--wa-font-size-s);
  color: var(--wa-color-text-quiet);
}
</style>
