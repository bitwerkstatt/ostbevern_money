<script setup lang="ts">
import { computed } from 'vue'

import type { BalkenZeile } from '@/charts/balken'
import { euroKurz, jahr as formatiereJahr, prozent } from '@/charts/format'
import ChartCard from '@/components/ChartCard.vue'
import DatenTabelle from '@/components/DatenTabelle.vue'
import type { DatenSpalte, DatenZeile } from '@/components/datenTabelle'
import ErtragsBalken from '@/components/ErtragsBalken.vue'
import JahrUmschalter from '@/components/JahrUmschalter.vue'
import PageIntro from '@/components/PageIntro.vue'
import { haushalt } from '@/data/daten'
import { baueErtragsarten } from '@/lib/ertragsarten'
import { useJahr, wertartName } from '@/lib/jahr'

const { jahr, index, wertart } = useJahr()

const jahrText = computed(() => formatiereJahr(jahr.value))
const wertartText = computed(() => `${wertartName(wertart.value)} ${jahrText.value}`)
const leerTitel = computed(() => `Für ${jahrText.value} gibt es keine Einzelwerte`)

// Ebene 1 (EINN-01): Ertragsarten des gewählten Jahres, gelesen aus dem Gesamtergebnisplan.
const ertragsarten = computed(() => baueErtragsarten(index.value))

const balkenZeilen = computed<BalkenZeile[]>(() =>
  ertragsarten.value.map((art) => ({
    schluessel: art.schluessel,
    name: art.name,
    wert: art.wert,
    label: `${euroKurz(art.wert)} · ${prozent(art.anteil)}`,
  })),
)

const ertragsSpalten = computed<DatenSpalte[]>(() => [
  { schluessel: 'name', titel: 'Ertragsart', art: 'text' },
  { schluessel: 'wert', titel: wertartText.value, art: 'euro' },
  { schluessel: 'anteil', titel: 'Anteil', art: 'prozent' },
])

const ertragsTabelle = computed<DatenZeile[]>(() =>
  ertragsarten.value.map((art) => ({ name: art.name, wert: art.wert, anteil: art.anteil })),
)

// Quellseite der Ebene 1: der Gesamtergebnisplan.
const gesamtSeite = computed(() => {
  const seite = haushalt.knoten.find((knoten) => knoten.code === 'GESAMT')?.pdf_seite
  return seite === null || seite === undefined ? undefined : { seite }
})

const LEER_TEXT =
  'Der Haushaltsplan nennt für dieses Jahr keine Aufschlüsselung. Wähle ein anderes Jahr oder öffne die Tabelle.'
</script>

<template>
  <PageIntro
    titel="Woher kommt das Geld?"
    beschreibung="Die Gemeinde finanziert sich aus Steuern, Zuweisungen und Gebühren. Hier siehst du, wie viel aus welcher Quelle kommt."
  />
  <JahrUmschalter />

  <div class="om-einnahmen">
    <ChartCard :titel="`Ertragsarten ${jahrText}`" :pdf="gesamtSeite">
      <ErtragsBalken :zeilen="balkenZeilen" :wertart-text="wertartText" :leer-titel="leerTitel" />
      <wa-details summary="Tabelle anzeigen" class="om-einnahmen__tabelle">
        <DatenTabelle
          :beschriftung="`Ertragsarten ${jahrText}`"
          :spalten="ertragsSpalten"
          :zeilen="ertragsTabelle"
          :leer-titel="leerTitel"
          :leer-text="LEER_TEXT"
        />
      </wa-details>
    </ChartCard>
  </div>
</template>

<style scoped>
.om-einnahmen {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-xl);
  margin-top: var(--wa-space-xl);
}

.om-einnahmen__tabelle {
  margin-top: var(--wa-space-m);
}
</style>
