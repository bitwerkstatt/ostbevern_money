<script setup lang="ts">
import { computed } from 'vue'
import type { EChartsOption } from 'echarts'

import { ERTRAG_FARBE } from '@/charts/echartsTheme'
import { euro, euroKurz, jahr as formatiereJahr, KEIN_WERT } from '@/charts/format'
import { tooltipZeilen } from '@/charts/tooltip'
import { LEGENDE_TEXT, flaechenFarbe, linienSerie } from '@/charts/wertartStil'
import BaseChart from '@/components/BaseChart.vue'
import DatenTabelle from '@/components/DatenTabelle.vue'
import type { DatenSpalte, DatenZeile } from '@/components/datenTabelle'
import ErklaerText from '@/components/ErklaerText.vue'
import { useSchmalerBildschirm } from '@/lib/bildschirm'
import { wertartName } from '@/lib/jahr'
import {
  baueZeitreihe,
  betragText,
  quellenFussnote,
  zeitreihenOptionen,
  zeitreihenSerien,
} from '@/lib/zeitreihen'

/** Schlüssel des gewählten Postens (`ZEITREIHEN_POSTEN`); die Seite hält den Zustand. */
const posten = defineModel<string>({ required: true })

const istSchmal = useSchmalerBildschirm()
const optionen = zeitreihenOptionen()

const LEER_TITEL = 'Für diese Auswahl gibt es keine Einzelwerte'
const LEER_TEXT =
  'Der Haushaltsplan nennt für diese Steuerart keine Werte. Wähle eine andere Steuerart oder öffne die Tabelle.'
/** Posten mit kuratiertem Erklärtext (`texte.json`); Schlüssel von Text und Posten stimmen überein. */
const MIT_ERKLAERTEXT: ReadonlySet<string> = new Set(['gewerbesteuer', 'schluesselzuweisung'])

const punkte = computed(() => baueZeitreihe(posten.value))
const reihe = computed(() => zeitreihenSerien(punkte.value))
const hatWerte = computed(() => punkte.value.some((punkt) => punkt.wert !== null))

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
      data: reihe.value.jahre.map((jahr) => formatiereJahr(jahr)),
      // Alle Jahre bleiben sichtbar; nur auf schmalen Bildschirmen werden sie gedreht.
      axisLabel: { interval: 0, rotate: istSchmal.value ? 45 : 0 },
    },
    yAxis: {
      type: 'value',
      min: 0,
      axisLabel: { formatter: (wert: number) => euroKurz(wert) },
    },
    tooltip: {
      trigger: 'axis',
      formatter: (params) => {
        const eintrag = Array.isArray(params) ? params[0] : params
        const punkt = eintrag === undefined ? undefined : punkte.value[eintrag.dataIndex]
        return punkt === undefined
          ? ''
          : tooltipZeilen([
              `${formatiereJahr(punkt.jahr)} · ${wertartName(punkt.wertart)} · ${betragText(punkt)}`,
            ])
      },
    },
    // Ohne Werte keine Serien, damit `BaseChart` den Leerzustand zeigt.
    series: hatWerte.value
      ? reihe.value.serien.map((serie) => linienSerie(serie, ERTRAG_FARBE, flaeche))
      : [],
  }
})

const spalten: DatenSpalte[] = [
  { schluessel: 'jahr', titel: 'Jahr', art: 'text' },
  { schluessel: 'wertart', titel: 'Wertart', art: 'text' },
  { schluessel: 'betrag', titel: 'Betrag', art: 'euro' },
  { schluessel: 'quelle', titel: 'Quelle', art: 'quelle' },
]

const tabelle = computed<DatenZeile[]>(() =>
  hatWerte.value
    ? punkte.value.map((punkt) => ({
        jahr: formatiereJahr(punkt.jahr),
        wertart: wertartName(punkt.wertart),
        betrag: punkt.wert,
        quelle: punkt.beleg,
        gerundet: punkt.gerundet ? 1 : 0,
      }))
    : [],
)

const fussnote = computed(() => quellenFussnote(punkte.value))

function beiAuswahl(ereignis: Event) {
  const wert = (ereignis.currentTarget as { value?: unknown } | null)?.value
  if (typeof wert === 'string' && optionen.some((option) => option.posten === wert)) {
    posten.value = wert
  }
}
</script>

<template>
  <div class="om-zeitreihe">
    <wa-select class="om-zeitreihe__auswahl" label="Steuerart" :value="posten" @change="beiAuswahl">
      <wa-option v-for="eintrag in optionen" :key="eintrag.posten" :value="eintrag.posten">
        {{ eintrag.name }}
      </wa-option>
    </wa-select>

    <BaseChart :option="option" hoehe="320px" :leer-titel="LEER_TITEL" :leer-text="LEER_TEXT" />
    <p class="om-zeitreihe__legende">{{ LEGENDE_TEXT }}</p>

    <wa-details summary="Tabelle anzeigen">
      <DatenTabelle
        beschriftung="Entwicklung der gewählten Steuerart"
        :spalten="spalten"
        :zeilen="tabelle"
        :fussnote="fussnote"
        :leer-titel="LEER_TITEL"
        :leer-text="LEER_TEXT"
      >
        <template #zelle="{ zeile, spalte, wert }">
          <template v-if="spalte.schluessel === 'betrag' && typeof wert === 'number'">
            <span v-if="zeile['gerundet'] === 1">rd. </span>{{ euro(wert) }}
          </template>
          <template v-else-if="wert === null">
            <span aria-hidden="true">{{ KEIN_WERT }}</span>
            <span class="om-visually-hidden">kein Wert</span>
          </template>
          <template v-else>{{ wert }}</template>
        </template>
      </DatenTabelle>
    </wa-details>

    <ErklaerText v-if="MIT_ERKLAERTEXT.has(posten)" :schluessel="posten" />
  </div>
</template>

<style scoped>
.om-zeitreihe {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-m);
  min-width: 0;
}

.om-zeitreihe__auswahl {
  max-width: 24rem;
}

.om-zeitreihe__auswahl::part(combobox) {
  min-height: 44px;
}

.om-zeitreihe__auswahl::part(form-control-label) {
  font-size: var(--wa-font-size-s);
  font-weight: var(--wa-font-weight-bold);
}

.om-zeitreihe__legende {
  margin: 0;
  font-size: var(--wa-font-size-s);
  color: var(--wa-color-text-quiet);
}

/* Bis 699 px füllt die Auswahl die Breite, lange Namen bleiben vollständig lesbar. */
@media (max-width: 699px) {
  .om-zeitreihe__auswahl {
    max-width: none;
    width: 100%;
  }
}
</style>
