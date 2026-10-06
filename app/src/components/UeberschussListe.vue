<script setup lang="ts">
import { computed } from 'vue'

import DatenTabelle from '@/components/DatenTabelle.vue'
import type { DatenSpalte, DatenZeile } from '@/components/datenTabelle'
import ErklaerText from '@/components/ErklaerText.vue'
import EuroBetrag from '@/components/EuroBetrag.vue'
import type { BindungsProdukt } from '@/lib/bindungsgrad'

// D-01: Produkte mit negativem Zuschussbedarf stehen nicht im Bindungsgrad-Balken, sondern in
// dieser kurzen Liste. Der Überschuss steht als positiver Betrag; ohne Überschuss-Produkte
// erscheint der Abschnitt nicht (UI-SPEC E5 partial).

const props = defineProps<{
  /** Produkte mit negativem Zuschussbedarf (`BindungsProdukt.wert` < 0). */
  produkte: readonly BindungsProdukt[]
  /** „{Wertart} {jahr}“ für den Spaltenkopf. */
  wertartText: string
}>()

const spalten = computed<DatenSpalte[]>(() => [
  { schluessel: 'name', titel: 'Produkt', art: 'text' },
  { schluessel: 'ueberschuss', titel: `Überschuss (${props.wertartText})`, art: 'euro' },
])

const zeilen = computed<DatenZeile[]>(() =>
  props.produkte.map((produkt) => ({
    name: produkt.name,
    ueberschuss: Math.abs(produkt.wert),
    code: produkt.code,
  })),
)
</script>

<template>
  <section v-if="produkte.length > 0" class="om-ueberschuss" aria-labelledby="om-ueberschuss-titel">
    <h2 id="om-ueberschuss-titel" class="om-ueberschuss__titel">
      Diese Produkte bringen mehr ein, als sie kosten
    </h2>
    <ErklaerText schluessel="ueberschuss_produkte" :ueberschrift="false" />
    <DatenTabelle beschriftung="Produkte mit Überschuss" :spalten="spalten" :zeilen="zeilen">
      <template #zelle="{ zeile, spalte, wert }">
        <RouterLink
          v-if="spalte.schluessel === 'name'"
          class="om-ueberschuss__link"
          :to="{ name: 'produkt', params: { code: String(zeile['code']) } }"
        >
          {{ wert }}
        </RouterLink>
        <EuroBetrag v-else-if="typeof wert === 'number'" :wert="wert" berechnet />
      </template>
    </DatenTabelle>
  </section>
</template>

<style scoped>
.om-ueberschuss {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-m);
  margin-block-start: var(--wa-space-xl);
  min-width: 0;
}

.om-ueberschuss__titel {
  margin: 0;
  font-size: var(--wa-font-size-xl);
  font-weight: var(--wa-font-weight-bold);
  line-height: var(--wa-line-height-condensed);
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-ueberschuss__link {
  display: inline-flex;
  align-items: center;
  min-block-size: 44px;
  color: var(--wa-color-brand-40);
  text-decoration: underline;
  overflow-wrap: break-word;
  hyphens: auto;
}
</style>
