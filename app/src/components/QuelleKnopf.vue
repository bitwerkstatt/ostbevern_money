<script setup lang="ts">
import { computed } from 'vue'

import { findeBeleg, oeffneQuelle } from '@/lib/quelle'

// D-01: der einzige Auslöser für einen Beleg. Er wird nur gerendert, wenn der Schlüssel in
// `quellen.json` existiert (kein toter Knopf, kein Platzhaltertext).
const props = defineProps<{
  schluessel: string
  /** Bezeichnung des Werts, geht in den zugänglichen Namen und in die Seitenleiste. */
  bezeichnung: string
  variante: 'kachel' | 'produkt' | 'zeile'
  /** Bereits formatierter Wert für die Wertzeile der Seitenleiste. */
  wert?: string
  /** Zeile „{Wertart} {jahr}“ für die Wertzeile der Seitenleiste. */
  wertart?: string
  /** Herleitung eines berechneten Werts (D-03). */
  herleitung?: string | null
}>()

const beleg = computed(() => findeBeleg(props.schluessel))

// Der sichtbare Text bleibt im zugänglichen Namen „Quelle anzeigen: {Bezeichnung}, PDF-Seite {n}“
// enthalten (WCAG 2.5.3); der Rest steht als versteckte Textspanne daneben.
const versteckterAnfang = computed(() => `Quelle anzeigen: ${props.bezeichnung}, `)
const versteckterRest = computed(() =>
  beleg.value === null ? '' : `: ${props.bezeichnung}, PDF-Seite ${String(beleg.value.pdfSeite)}`,
)

function beiKlick(ereignis: MouseEvent) {
  const knopf = ereignis.currentTarget
  oeffneQuelle({
    schluessel: props.schluessel,
    bezeichnung: props.bezeichnung,
    wert: props.wert,
    wertart: props.wertart,
    herleitung: props.herleitung,
    ausloeser: knopf instanceof HTMLElement ? knopf : null,
  })
}
</script>

<template>
  <button
    v-if="beleg !== null"
    type="button"
    class="om-quelle-knopf"
    :class="`om-quelle-knopf--${variante}`"
    aria-haspopup="dialog"
    @click="beiKlick"
  >
    <template v-if="variante === 'zeile'">
      <span class="om-visually-hidden">{{ versteckterAnfang }}</span>
      <span class="om-quelle-knopf__text">PDF-Seite {{ beleg.pdfSeite }}</span>
    </template>
    <template v-else>
      <wa-icon name="file-lines" aria-hidden="true"></wa-icon>
      <span class="om-quelle-knopf__text"
        >Quelle anzeigen<span class="om-visually-hidden">{{ versteckterRest }}</span></span
      >
    </template>
  </button>
</template>

<style scoped>
.om-quelle-knopf {
  display: inline-flex;
  align-items: center;
  gap: var(--wa-space-2xs);
  min-width: 44px;
  min-height: 44px;
  padding: 0;
  border: 0;
  background: transparent;
  color: var(--wa-color-brand-40);
  font-family: inherit;
  font-size: var(--wa-font-size-m);
  font-weight: var(--wa-font-weight-normal);
  line-height: var(--wa-line-height-normal);
  text-align: start;
  text-decoration: underline;
  text-underline-offset: 0.25em;
  cursor: pointer;
}

.om-quelle-knopf:focus-visible {
  outline: 2px solid var(--wa-color-focus);
  outline-offset: var(--wa-space-2xs);
}

/* Tabellenzeile: Caption-Größe, nie umbrechen (die Tabelle scrollt in ihrem Rahmen). */
.om-quelle-knopf--zeile {
  font-size: var(--wa-font-size-s);
  line-height: 1.5;
  white-space: nowrap;
}

/* Kachel und Produktseite: darf bei 360 px auf zwei Zeilen umbrechen, nie mit Auslassungspunkten. */
.om-quelle-knopf--kachel .om-quelle-knopf__text,
.om-quelle-knopf--produkt .om-quelle-knopf__text {
  hyphens: auto;
  overflow-wrap: break-word;
}
</style>
