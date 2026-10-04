<script setup lang="ts">
import { computed } from 'vue'

import { jahr as formatiereJahr } from '@/charts/format'
import ChartCard from '@/components/ChartCard.vue'
import DatenTabelle from '@/components/DatenTabelle.vue'
import type { DatenSpalte, DatenZeile } from '@/components/datenTabelle'
import JahrUmschalter from '@/components/JahrUmschalter.vue'
import PageIntro from '@/components/PageIntro.vue'
import SankeyDiagramm from '@/components/SankeyDiagramm.vue'
import { baueGeldfluss, geldflussZeilen } from '@/lib/geldfluss'
import { useJahr, wertartName } from '@/lib/jahr'

const { jahr, index, wertart, jahrLink } = useJahr()

const geldfluss = computed(() => baueGeldfluss(index.value))
const wertartText = computed(() => `${wertartName(wertart.value)} ${formatiereJahr(jahr.value)}`)
const kartenTitel = computed(() => `Vom Ertrag zur Ausgabe ${formatiereJahr(jahr.value)}`)

const spalten = computed<DatenSpalte[]>(() => [
  { schluessel: 'name', titel: 'Name', art: 'text' },
  { schluessel: 'wert', titel: wertartText.value, art: 'euro' },
  { schluessel: 'anteil', titel: 'Anteil', art: 'prozent' },
])

function tabellenZeilen(seite: 'links' | 'rechts'): DatenZeile[] {
  return geldflussZeilen(geldfluss.value, seite).map((z) => ({
    name: z.name,
    wert: z.wert,
    anteil: z.anteil,
    code: z.code,
  }))
}
const zeilenWoher = computed(() => tabellenZeilen('links'))
const zeilenWohin = computed(() => tabellenZeilen('rechts'))
</script>

<template>
  <PageIntro
    titel="Vom Ertrag zur Ausgabe"
    beschreibung="Das Diagramm zeigt, woher das Geld kommt und wohin es fließt."
  />
  <JahrUmschalter />
  <ChartCard
    :titel="kartenTitel"
    quelle="Gesamtergebnisplan"
    :pdf="geldfluss.pdfSeite === null ? undefined : { seite: geldfluss.pdfSeite }"
  >
    <SankeyDiagramm :geldfluss="geldfluss" :wertart-text="wertartText" />
    <wa-details summary="Tabelle anzeigen">
      <div class="om-geldfluss__tabellen">
        <section aria-labelledby="om-geldfluss-woher">
          <h3 id="om-geldfluss-woher">Woher</h3>
          <DatenTabelle
            :beschriftung="`Woher kommt das Geld ${formatiereJahr(jahr)}`"
            :spalten="spalten"
            :zeilen="zeilenWoher"
          />
        </section>
        <section aria-labelledby="om-geldfluss-wohin">
          <h3 id="om-geldfluss-wohin">Wohin</h3>
          <DatenTabelle
            :beschriftung="`Wohin das Geld fließt ${formatiereJahr(jahr)}`"
            :spalten="spalten"
            :zeilen="zeilenWohin"
          >
            <template #zelle="{ zeile, spalte }">
              <template v-if="spalte.schluessel === 'name' && typeof zeile.code === 'string'">
                {{ zeile.name }}
                <RouterLink :to="jahrLink({ name: 'ausgaben', query: { pb: zeile.code } })">
                  Im Detail ansehen<span class="om-visually-hidden"> zu {{ zeile.name }}</span>
                </RouterLink>
              </template>
            </template>
          </DatenTabelle>
        </section>
      </div>
    </wa-details>
  </ChartCard>
</template>

<style scoped>
.om-geldfluss__tabellen {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-l);
}

.om-geldfluss__tabellen h3 {
  margin: 0 0 var(--wa-space-xs);
  font-size: var(--wa-font-size-m);
  font-weight: var(--wa-font-weight-bold);
}
</style>
