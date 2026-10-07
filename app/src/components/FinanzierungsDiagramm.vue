<script setup lang="ts">
import { computed } from 'vue'

import { euro } from '@/charts/format'
import BaseChart from '@/components/BaseChart.vue'
import DatenTabelle from '@/components/DatenTabelle.vue'
import { investitionen } from '@/data/daten'
import { useSchmalerBildschirm } from '@/lib/bildschirm'
import {
  einzahlungsAbweichungen,
  einzahlungsTabelle,
  finanzierungsLegende,
  finanzierungsOption,
  finanzierungsTabelle,
  type FinanzierungsVariante,
} from '@/lib/finanzierung'
import { jahreListe } from '@/lib/hilfsfunktionen'

const props = defineProps<{
  variante: FinanzierungsVariante
}>()

const LEER_TITEL = 'Keine Finanzierungswerte'
const LEER_TEXT = 'Der Haushaltsplan nennt hier keine Werte. Öffne die Tabelle.'

const TEXTE: Readonly<Record<FinanzierungsVariante, { beschreibung: string; tabelle: string }>> = {
  investitionen: {
    beschreibung:
      'Gruppiertes Säulendiagramm: Auszahlungen für Investitionen und die zugehörigen Einzahlungen je Jahr. Dieselben Werte stehen in der Tabelle darunter.',
    tabelle: 'Auszahlungen und Einzahlungen aus Investitionstätigkeit je Jahr',
  },
  kredite: {
    beschreibung:
      'Gruppiertes Säulendiagramm: Kreditaufnahme und Tilgung je Jahr. Dieselben Werte stehen in der Tabelle darunter.',
    tabelle: 'Kreditaufnahme und Tilgung je Jahr',
  },
}

const istSchmal = useSchmalerBildschirm()

const option = computed(() => finanzierungsOption(props.variante, istSchmal.value))
const tabelle = computed(() => finanzierungsTabelle(props.variante))
const legende = computed(() => finanzierungsLegende(props.variante))
const texte = computed(() => TEXTE[props.variante])

const seite = investitionen.finanzierung.quelle
const fussnote = `Quelle: Gesamtfinanzplan, PDF-Seite ${String(seite)}.`

const aufteilung = einzahlungsTabelle()

// Weichen die Einzelzeilen von der gedruckten Summenzeile ab, sagt die Fußnote das datengetrieben.
const aufteilungFussnote = (() => {
  const abweichungen = einzahlungsAbweichungen()
  if (abweichungen.length === 0) {
    return fussnote
  }
  const groesste = Math.max(...abweichungen.map((eintrag) => Math.abs(eintrag.differenz)))
  return `${fussnote} Für ${jahreListe(abweichungen.map((eintrag) => eintrag.jahr))} weicht die Summe der Einzelzeilen um höchstens ${euro(groesste)} von der gedruckten Summenzeile ab.`
})()
</script>

<template>
  <div class="om-finanzierung">
    <BaseChart
      :option="option"
      hoehe="280px"
      :beschreibung="texte.beschreibung"
      :leer-titel="LEER_TITEL"
      :leer-text="LEER_TEXT"
    />
    <p class="om-finanzierung__legende">{{ legende }}</p>

    <wa-details summary="Tabelle anzeigen">
      <DatenTabelle
        :beschriftung="texte.tabelle"
        :spalten="tabelle.spalten"
        :zeilen="tabelle.zeilen"
        :fussnote="fussnote"
        :leer-titel="LEER_TITEL"
        :leer-text="LEER_TEXT"
      />
    </wa-details>

    <wa-details v-if="variante === 'investitionen'" summary="Woraus die Einzahlungen bestehen">
      <DatenTabelle
        beschriftung="Einzahlungen aus Investitionstätigkeit nach Zeilen des Gesamtfinanzplans"
        :spalten="aufteilung.spalten"
        :zeilen="aufteilung.zeilen"
        :fussnote="aufteilungFussnote"
        :leer-titel="LEER_TITEL"
        :leer-text="LEER_TEXT"
      />
    </wa-details>
  </div>
</template>

<style scoped>
.om-finanzierung {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-m);
  min-width: 0;
}

.om-finanzierung__legende {
  margin: 0;
  font-size: var(--wa-font-size-s);
  color: var(--wa-color-text-quiet);
}
</style>
