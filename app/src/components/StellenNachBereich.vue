<script setup lang="ts">
import { computed, useId } from 'vue'
import type { BarSeriesOption, EChartsOption } from 'echarts'

import { balkenHoehe } from '@/charts/balken'
import { farbeFuerPb } from '@/charts/echartsTheme'
import { euroKurz, jahr as formatiereJahr, KEIN_WERT, vzae } from '@/charts/format'
import { tooltipZeilen } from '@/charts/tooltip'
import BaseChart from '@/components/BaseChart.vue'
import DatenTabelle from '@/components/DatenTabelle.vue'
import type { DatenSpalte, DatenZeile } from '@/components/datenTabelle'
import { stellenplan } from '@/data/daten'
import { useSchmalerBildschirm } from '@/lib/bildschirm'
import { alsVzae, stellenNachBereich } from '@/lib/stellen'

// Zwei horizontale Balkendiagramme mit identischen Zeilen (STEL-02, STEL-03, D-16): links die
// Stellen in VZÄ, rechts der Personalaufwand, beide in der Farbe des Aufgabenbereichs und mit
// getrennten Achsen. Es gibt bewusst keine Verrechnung beider Größen miteinander. Ab 700 px
// stehen die Diagramme nebeneinander und fluchten Zeile für Zeile (gleiche Höhe, gleiche
// Reihenfolge), das rechte ohne Namensspalte; bis 699 px stehen sie untereinander mit Namen.

const istSchmal = useSchmalerBildschirm()
const stellenId = useId()
const personalId = useId()

/** Breite der Namensspalte in px; längere Namen brechen um. */
const NAMEN_BREITE = 200
/** Schmalere Namensspalte bis 699 px, damit neben dem Namen noch Balken bleiben. */
const NAMEN_BREITE_SCHMAL = 140
/** Geschätzte Zeichenbreite der 14-px-Beschriftung in px. */
const ZEICHENBREITE = 7.5
/** Abstand zwischen Balkenende und Beschriftung plus Sicherheitsrand in px. */
const BESCHRIFTUNGS_RAND = 12
/** Mindesthöhe, falls es keine Zeilen gibt (Leerzustand). */
const LEER_HOEHE = '160px'

const zeilen = computed(() => stellenNachBereich())
const hjText = computed(() => formatiereJahr(stellenplan.haushaltsjahr))

interface BalkenEintrag {
  pb: string
  name: string
  wert: number | null
  label: string
}

const stellenBalken = computed<BalkenEintrag[]>(() =>
  zeilen.value.map((zeile) => ({
    pb: zeile.pb,
    name: zeile.name,
    wert: zeile.stellen === null ? null : alsVzae(zeile.stellen),
    label: zeile.stellen === null ? KEIN_WERT : `${vzae(alsVzae(zeile.stellen))} VZÄ`,
  })),
)

const personalBalken = computed<BalkenEintrag[]>(() =>
  zeilen.value.map((zeile) => ({
    pb: zeile.pb,
    name: zeile.name,
    wert: zeile.personalaufwand,
    label: zeile.personalaufwand === null ? KEIN_WERT : euroKurz(zeile.personalaufwand),
  })),
)

interface BalkenOptionen {
  achse: (wert: number) => string
  mitNamen: boolean
  zusatzZeile: string
}

function balkenOption(
  eintraege: readonly BalkenEintrag[],
  optionen: BalkenOptionen,
): EChartsOption {
  const laengste = eintraege.reduce((max, eintrag) => Math.max(max, eintrag.label.length), 0)
  const serie: BarSeriesOption = {
    type: 'bar',
    barCategoryGap: '30%',
    // Eine fehlende Zahl zeichnet keinen Balken, behält aber die Zeile mit „–“ (nie 0).
    data: eintraege.map((eintrag) => ({
      name: eintrag.name,
      value: eintrag.wert ?? 0,
      itemStyle: { color: farbeFuerPb(eintrag.pb) },
    })),
    label: {
      show: true,
      position: 'right',
      formatter: (params) => eintraege[params.dataIndex]?.label ?? KEIN_WERT,
    },
  }
  return {
    grid: {
      left: 8,
      right: Math.ceil(laengste * ZEICHENBREITE) + BESCHRIFTUNGS_RAND,
      top: 8,
      bottom: 8,
      outerBoundsMode: 'same',
      outerBoundsContain: 'axisLabel',
    },
    xAxis: {
      type: 'value',
      min: 0,
      splitNumber: 3,
      axisLabel: { formatter: optionen.achse, hideOverlap: true },
    },
    yAxis: {
      type: 'category',
      inverse: true,
      data: eintraege.map((eintrag) => eintrag.name),
      axisTick: { show: false },
      axisLabel: {
        show: optionen.mitNamen,
        width: istSchmal.value ? NAMEN_BREITE_SCHMAL : NAMEN_BREITE,
        overflow: 'break',
        interval: 0,
      },
    },
    tooltip: {
      trigger: 'item',
      formatter: (params) => {
        const eintrag = Array.isArray(params) ? params[0] : params
        const zeile = eintrag === undefined ? undefined : eintraege[eintrag.dataIndex]
        return zeile === undefined
          ? ''
          : tooltipZeilen([zeile.name, zeile.label, optionen.zusatzZeile])
      },
    },
    series: [serie],
  }
}

const stellenOption = computed(() =>
  balkenOption(stellenBalken.value, {
    achse: (wert) => vzae(wert),
    mitNamen: true,
    zusatzZeile: `Stellenplan ${hjText.value}`,
  }),
)

// Das rechte Diagramm hat ab 700 px keine Namensspalte; die Zeilen fluchten mit dem linken.
const personalOption = computed(() =>
  balkenOption(personalBalken.value, {
    achse: (wert) => euroKurz(wert),
    mitNamen: istSchmal.value,
    zusatzZeile: `Teilergebnisplan ${hjText.value}`,
  }),
)

const hoehe = computed(() =>
  zeilen.value.length === 0 ? LEER_HOEHE : balkenHoehe(zeilen.value.length),
)

const stellenTitel = computed(() => `Stellen ${hjText.value} (VZÄ)`)
const personalTitel = computed(() => `Personalaufwand ${hjText.value}`)

const LEER_TITEL = 'Keine Einzelwerte'
const LEER_TEXT =
  'Der Haushaltsplan nennt hier keine Aufschlüsselung nach Aufgabenbereich. Öffne die Tabelle.'

const stellenBeschreibung = computed(
  () =>
    `Balkendiagramm: Stellen in VZÄ ${hjText.value} je Aufgabenbereich, größter Wert oben. Die Farbe zeigt den Aufgabenbereich. Dieselben Werte stehen in der Tabelle darunter.`,
)
const personalBeschreibung = computed(
  () =>
    `Balkendiagramm: Personalaufwand ${hjText.value} je Aufgabenbereich, in derselben Reihenfolge wie die Stellen. Die Farbe zeigt den Aufgabenbereich. Dieselben Werte stehen in der Tabelle darunter.`,
)

const spalten = computed<DatenSpalte[]>(() => [
  { schluessel: 'bereich', titel: 'Aufgabenbereich', art: 'text' },
  { schluessel: 'stellen', titel: stellenTitel.value, art: 'dezimal' },
  { schluessel: 'personalaufwand', titel: personalTitel.value, art: 'euro' },
])

const tabelle = computed<DatenZeile[]>(() =>
  zeilen.value.map((zeile) => ({
    bereich: zeile.name,
    stellen: zeile.stellen === null ? null : alsVzae(zeile.stellen),
    personalaufwand: zeile.personalaufwand,
  })),
)

const fussnote = computed(() => {
  const seiten = [...new Set(zeilen.value.flatMap((zeile) => zeile.pdfSeiten))].sort(
    (a, b) => a - b,
  )
  return seiten.length === 0 ? undefined : `Quelle: PDF-Seiten ${seiten.join(', ')}.`
})
</script>

<template>
  <div class="om-stellen-bereich">
    <div class="om-stellen-bereich__diagramme">
      <section class="om-stellen-bereich__diagramm" :aria-labelledby="stellenId">
        <h3 :id="stellenId">{{ stellenTitel }}</h3>
        <BaseChart
          :option="stellenOption"
          :hoehe="hoehe"
          :beschreibung="stellenBeschreibung"
          :leer-titel="LEER_TITEL"
          :leer-text="LEER_TEXT"
        />
      </section>
      <section class="om-stellen-bereich__diagramm" :aria-labelledby="personalId">
        <h3 :id="personalId">{{ personalTitel }}</h3>
        <BaseChart
          :option="personalOption"
          :hoehe="hoehe"
          :beschreibung="personalBeschreibung"
          :leer-titel="LEER_TITEL"
          :leer-text="LEER_TEXT"
        />
      </section>
    </div>
    <p class="om-stellen-bereich__legende">
      Die Farbe zeigt den Aufgabenbereich. Beide Diagramme haben eigene Achsen und dieselbe
      Reihenfolge der Zeilen.
    </p>

    <wa-details summary="Tabelle anzeigen">
      <DatenTabelle
        beschriftung="Stellen und Personalaufwand nach Aufgabenbereich"
        :spalten="spalten"
        :zeilen="tabelle"
        :fussnote="fussnote"
        :leer-titel="LEER_TITEL"
        :leer-text="LEER_TEXT"
      />
    </wa-details>
  </div>
</template>

<style scoped>
.om-stellen-bereich {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-m);
  min-width: 0;
}

.om-stellen-bereich__diagramme {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: var(--wa-space-l);
}

.om-stellen-bereich__diagramm {
  min-width: 0;
}

.om-stellen-bereich__diagramm h3 {
  margin: 0 0 var(--wa-space-s);
  font-size: var(--wa-font-size-m);
  font-weight: var(--wa-font-weight-bold);
  line-height: var(--wa-line-height-condensed);
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-stellen-bereich__legende {
  margin: 0;
  font-size: var(--wa-font-size-s);
  color: var(--wa-color-text-quiet);
}

/* Ab 700 px nebeneinander; die Überschriften haben beide eine Zeile, die Diagramme fluchten. */
@media (min-width: 700px) {
  .om-stellen-bereich__diagramme {
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
    gap: var(--wa-space-m);
  }
}
</style>
