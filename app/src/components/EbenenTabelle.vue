<script setup lang="ts">
import { computed } from 'vue'

import { euro, jahr as formatiereJahr, KEIN_WERT, prozent } from '@/charts/format'
import DatenTabelle from '@/components/DatenTabelle.vue'
import type { DatenSpalte, DatenZeile } from '@/components/datenTabelle'
import { haushalt } from '@/data/daten'
import type { Modus } from '@/lib/ansicht'
import { proKopf } from '@/lib/berechnung'
import { klickZiel, type EbenenEintrag } from '@/lib/drilldown'
import { ebenenBeleg } from '@/lib/ebenenBeleg'

const props = defineProps<{
  eintraege: readonly EbenenEintrag[]
  modus: Modus
  /** Wertart des Jahres („Ist“, „Ansatz“, „Planung“). */
  wertartText: string
  jahr: number
  /** Query für den Link auf `/produkt/:code` (jahr, modus, pb, pg). */
  produktQuery: Readonly<Record<string, string>>
  /** Zugängliche Beschriftung der Tabelle. */
  beschriftung: string
}>()

const emit = defineEmits<{
  waehle: [code: string]
}>()

const einwohner = haushalt.meta.einwohner.wert

const spalten = computed<DatenSpalte[]>(() => {
  const liste: DatenSpalte[] = [
    { schluessel: 'name', titel: 'Name', art: 'text' },
    {
      schluessel: 'betrag',
      titel: `${props.wertartText} ${formatiereJahr(props.jahr)}`,
      art: 'euro',
    },
    { schluessel: 'anteil', titel: 'Anteil', art: 'prozent' },
  ]
  if (props.modus === 'zuschussbedarf') {
    liste.push({ schluessel: 'proKopf', titel: 'pro Einwohner (berechnet)', art: 'euro' })
  }
  liste.push({ schluessel: 'quelle', titel: 'Quelle', art: 'quelle' })
  return liste
})

// Die Zeilen tragen nur Zahlen und Texte (`DatenZeile`); Wahrheitswerte stehen als 0/1.
const zeilen = computed<DatenZeile[]>(() => {
  const jahrIndex = haushalt.jahre.indexOf(props.jahr)
  return props.eintraege.map((e) => {
    const beleg = ebenenBeleg(e, jahrIndex, props.modus)
    return {
      code: e.code,
      name: e.name,
      betrag: e.wert,
      anteil: e.anteil,
      proKopf: typeof einwohner === 'number' ? proKopf(e.wert, einwohner) : null,
      ziel: klickZiel(e),
      farbe: e.farbe,
      kl: e.istKl ? 1 : 0,
      gerundet: e.gerundet ? 1 : 0,
      ueberschuss: e.ueberschuss ? 1 : 0,
      quelle: beleg?.schluessel ?? null,
      quelleHerleitung: beleg?.herleitung ?? null,
    }
  })
})

function codeVon(zeile: DatenZeile): string {
  return String(zeile.code)
}

function produktZiel(zeile: DatenZeile) {
  return { name: 'produkt', params: { code: codeVon(zeile) }, query: props.produktQuery }
}

function betragText(betrag: number, gerundet: boolean): string {
  return gerundet ? `rd. ${euro(betrag)}` : euro(betrag)
}
</script>

<template>
  <DatenTabelle :beschriftung="beschriftung" :spalten="spalten" :zeilen="zeilen">
    <template #zelle="{ zeile, spalte, wert }">
      <template v-if="spalte.schluessel === 'name'">
        <span
          class="om-ebenen-farbe"
          :class="{ 'om-ebenen-farbe--kl': zeile.kl === 1 }"
          :style="{ '--om-ebenen-farbe': String(zeile.farbe) }"
          aria-hidden="true"
        ></span>
        <button
          v-if="zeile.ziel === 'drill'"
          type="button"
          class="om-ebenen-knopf"
          @click="emit('waehle', codeVon(zeile))"
        >
          {{ zeile.name }}
        </button>
        <RouterLink
          v-else-if="zeile.ziel === 'produkt'"
          class="om-ebenen-link"
          :to="produktZiel(zeile)"
        >
          {{ zeile.name }}
        </RouterLink>
        <span v-else>{{ zeile.name }}</span>
      </template>
      <template v-else-if="typeof wert !== 'number'">
        <span aria-hidden="true">{{ KEIN_WERT }}</span>
        <span class="om-visually-hidden">{{
          spalte.schluessel === 'anteil' ? 'kein Anteil' : 'kein Wert'
        }}</span>
      </template>
      <template v-else-if="spalte.schluessel === 'betrag'">
        {{ betragText(wert, zeile.gerundet === 1) }}
        <span v-if="zeile.ueberschuss === 1" class="om-ebenen-hinweis">(Überschuss)</span>
        <span v-if="typeof zeile.quelleHerleitung === 'string'" class="om-ebenen-hinweis">
          (berechnet)
        </span>
      </template>
      <template v-else-if="spalte.schluessel === 'anteil'">{{ prozent(wert) }}</template>
      <template v-else>{{ euro(wert) }}</template>
    </template>
  </DatenTabelle>
</template>

<style scoped>
.om-ebenen-farbe {
  display: inline-block;
  inline-size: 0.75em;
  block-size: 0.75em;
  margin-inline-end: var(--wa-space-xs);
  background-color: var(--om-ebenen-farbe);
  vertical-align: baseline;
}

/* Streifen wie das KL-Decal im Diagramm: KL bleibt auch ohne Farbwahrnehmung erkennbar. */
.om-ebenen-farbe--kl {
  background-image: repeating-linear-gradient(
    45deg,
    transparent 0 2px,
    var(--wa-color-surface-default) 2px 3px
  );
}

/* Mindest-Trefferfläche 44 px (WCAG 2.5.5, UI-SPEC Spacing-Ausnahmen). */
.om-ebenen-knopf,
.om-ebenen-link {
  display: inline-flex;
  align-items: center;
  min-block-size: 44px;
  min-inline-size: 44px;
  padding: 0;
  border: 0;
  background: none;
  font: inherit;
  color: var(--wa-color-brand-40);
  text-align: start;
  text-decoration: underline;
  cursor: pointer;
  overflow-wrap: break-word;
  hyphens: auto;
}

.om-ebenen-hinweis {
  color: var(--wa-color-text-quiet);
}
</style>
