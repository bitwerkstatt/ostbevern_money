<script setup lang="ts">
import { computed } from 'vue'
import type { EChartsOption } from 'echarts'

import { AUFWANDSART_FARBE, ERTRAG_FARBE, KL_FARBE, ZINSEN_FARBE } from '@/charts/echartsTheme'
import { euroKurz, jahr as formatiereJahr, KEIN_WERT } from '@/charts/format'
import { tooltipZeilen } from '@/charts/tooltip'
import { LEGENDE_TEXT, flaechenFarbe, jahresAchse, linienSerie } from '@/charts/wertartStil'
import BaseChart from '@/components/BaseChart.vue'
import BerechnetEtikett from '@/components/BerechnetEtikett.vue'
import EuroBetrag from '@/components/EuroBetrag.vue'
import DatenTabelle from '@/components/DatenTabelle.vue'
import type { DatenSpalte, DatenZeile } from '@/components/datenTabelle'
import ErklaerText from '@/components/ErklaerText.vue'
import { haushalt } from '@/data/daten'
import {
  bauePostenReihe,
  postenFussnote,
  veraenderung,
  veraenderungText,
  type EntwicklungPosten,
} from '@/lib/entwicklung'
import { wertartName } from '@/lib/jahr'
import { betragText, zeitreihenSerien } from '@/lib/zeitreihen'

const props = defineProps<{ posten: EntwicklungPosten }>()

const LEER_TITEL = 'Für diese Auswahl gibt es keine Einzelwerte'
const LEER_TEXT = 'Der Haushaltsplan nennt für diesen Posten keine Werte. Öffne die Tabelle.'

/** Linienfarbe je Posten (UI-SPEC Farbrollen): Einnahmen Gold, Aufwände neutral, Kreisumlage rosa. */
const FARBEN: ReadonlyMap<string, string> = new Map([
  ['kreisumlage', KL_FARBE],
  ['gewerbesteuer', ERTRAG_FARBE],
  ['schluesselzuweisung', ERTRAG_FARBE],
  ['personal', AUFWANDSART_FARBE],
  ['zinsen', ZINSEN_FARBE],
])

const farbe = computed(() => {
  const treffer = FARBEN.get(props.posten.schluessel)
  if (treffer === undefined) {
    throw new Error(`Keine Linienfarbe für den Posten ${props.posten.schluessel}`)
  }
  return treffer
})

const reihe = computed(() => bauePostenReihe(props.posten.schluessel))
const hatWerte = computed(() => reihe.value.some((eintrag) => eintrag.wert !== null))
const achse = jahresAchse(haushalt.jahre, haushalt.wertarten)

const erstesJahr = formatiereJahr(haushalt.jahre[0] ?? haushalt.haushaltsjahr)
const letztesJahr = formatiereJahr(
  haushalt.jahre[haushalt.jahre.length - 1] ?? haushalt.haushaltsjahr,
)
const aenderung = computed(() => veraenderung(reihe.value))
const aenderungText = computed(() => veraenderungText(aenderung.value))

const option = computed<EChartsOption>(() => {
  const flaeche = flaechenFarbe()
  return {
    grid: {
      left: 8,
      right: 16,
      top: 16,
      bottom: 8,
      outerBoundsMode: 'same',
      outerBoundsContain: 'axisLabel',
    },
    xAxis: {
      type: 'category',
      data: achse,
      // Alle Jahre bleiben sichtbar (zweizeilig, nie ausgelassen).
      axisLabel: { interval: 0, rotate: 0 },
    },
    yAxis: {
      type: 'value',
      // Jede Karte hat ihre eigene Achse ab 0.
      min: 0,
      axisLabel: { formatter: (wert: number) => euroKurz(wert) },
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const eintrag = Array.isArray(params) ? params[0] : params
        const punkt = eintrag === undefined ? undefined : reihe.value[eintrag.dataIndex]
        return punkt === undefined
          ? ''
          : tooltipZeilen([
              `${formatiereJahr(punkt.jahr)} · ${wertartName(punkt.wertart)} · ${betragText(punkt)}`,
            ])
      },
    },
    // Ohne Werte keine Serien, damit `BaseChart` den Leerzustand zeigt.
    series: hatWerte.value
      ? zeitreihenSerien(reihe.value).serien.map((serie) => ({
          ...linienSerie(serie, farbe.value, flaeche),
          // Fehlende Werte sind Lücken in der Linie, nie 0.
          connectNulls: false,
        }))
      : [],
  }
})

// Bildbeschreibung (A11Y-01): ohne Zahl, die Werte stehen in der Tabelle darunter.
const BESCHREIBUNG =
  'Liniendiagramm: der Betrag dieses Postens je Jahr. Dieselben Werte stehen in der Tabelle darunter.'

const spalten: DatenSpalte[] = [
  { schluessel: 'jahr', titel: 'Jahr', art: 'text' },
  { schluessel: 'betrag', titel: 'Betrag', art: 'euro' },
]

const tabelle = computed<DatenZeile[]>(() =>
  hatWerte.value
    ? reihe.value.map((eintrag) => ({
        jahr: `${formatiereJahr(eintrag.jahr)} · ${wertartName(eintrag.wertart)}`,
        betrag: eintrag.wert,
        gerundet: eintrag.gerundet ? 1 : 0,
      }))
    : [],
)

const fussnote = computed(() => postenFussnote(props.posten, reihe.value))
</script>

<template>
  <div class="om-posten">
    <p class="om-posten__veraenderung">
      Veränderung {{ erstesJahr }} → {{ letztesJahr }}: {{ aenderungText }}
      <BerechnetEtikett v-if="aenderung !== null" />
    </p>

    <BaseChart
      :option="option"
      hoehe="240px"
      :beschreibung="BESCHREIBUNG"
      :leer-titel="LEER_TITEL"
      :leer-text="LEER_TEXT"
    />
    <p class="om-posten__legende">{{ LEGENDE_TEXT }}</p>

    <wa-details summary="Tabelle anzeigen">
      <DatenTabelle
        :beschriftung="`Entwicklung: ${posten.titel}`"
        :spalten="spalten"
        :zeilen="tabelle"
        :fussnote="fussnote"
        :leer-titel="LEER_TITEL"
        :leer-text="LEER_TEXT"
      >
        <template #zelle="{ zeile, spalte, wert }">
          <template v-if="spalte.schluessel === 'betrag' && typeof wert === 'number'">
            <EuroBetrag :wert="wert" :gerundet="zeile['gerundet'] === 1" />
          </template>
          <template v-else-if="wert === null">
            <span aria-hidden="true">{{ KEIN_WERT }}</span>
            <span class="om-visually-hidden">kein Wert</span>
          </template>
          <template v-else>{{ wert }}</template>
        </template>
      </DatenTabelle>
    </wa-details>

    <wa-details v-if="posten.erklaertext !== null" :summary="`So funktioniert die ${posten.titel}`">
      <ErklaerText :schluessel="posten.erklaertext" :ueberschrift="false" />
    </wa-details>
  </div>
</template>

<style scoped>
.om-posten {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-m);
  min-width: 0;
}

.om-posten__veraenderung,
.om-posten__legende {
  margin: 0;
  font-size: var(--wa-font-size-s);
  line-height: 1.5;
  color: var(--wa-color-text-quiet);
  hyphens: auto;
  overflow-wrap: break-word;
}
</style>
