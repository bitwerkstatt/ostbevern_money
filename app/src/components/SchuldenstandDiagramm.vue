<script setup lang="ts">
import { computed } from 'vue'

import { BERECHNET_DECAL, SCHULDEN_FARBEN } from '@/charts/echartsTheme'
import { jahr as formatiereJahr } from '@/charts/format'
import BaseChart from '@/components/BaseChart.vue'
import BerechnetEtikett from '@/components/BerechnetEtikett.vue'
import DatenTabelle from '@/components/DatenTabelle.vue'
import { useSchmalerBildschirm } from '@/lib/bildschirm'
import {
  baueSchuldenstand,
  hatBerechneteJahre,
  liquiditaetsSatz,
  schuldenKennzahlen,
  schuldenstandOption,
  schuldenTabelle,
} from '@/lib/schulden'

const LEER_TITEL = 'Keine Schuldenwerte'
const LEER_TEXT = 'Der Haushaltsplan nennt hier keinen Schuldenstand. Öffne die Tabelle.'

const istSchmal = useSchmalerBildschirm()

const reihen = baueSchuldenstand()
const kennzahlen = schuldenKennzahlen()
const tabelle = schuldenTabelle()
const satz = liquiditaetsSatz()
const berechnetVorhanden = hatBerechneteJahre()
// Die Legende zeichnet dieselben Streifen wie das Diagramm (Farbe des BERECHNET_DECAL).
const streifenFarbe = typeof BERECHNET_DECAL.color === 'string' ? BERECHNET_DECAL.color : 'white'

const option = computed(() => schuldenstandOption(istSchmal.value))

const zeitraum = computed(() => {
  const erstes = reihen.jahre[0]
  const letztes = reihen.jahre.at(-1)
  return erstes === undefined || letztes === undefined
    ? ''
    : `${formatiereJahr(erstes)}–${formatiereJahr(letztes)}`
})

const beschreibung = computed(
  () =>
    `Säulendiagramm: Schuldenstand der Gemeinde ${zeitraum.value}, gestapelt aus Investitionskrediten und NRW.Bank-Mitteln, mit der Summe über jeder Säule. ` +
    (berechnetVorhanden
      ? 'Fortgeschriebene Jahre tragen Streifen und die Achsenzeile berechnet. '
      : '') +
    'Dieselben Werte stehen in der Tabelle darunter.',
)

// Die Fußnote nennt, dass nur der Wert des Vorjahrs gedruckt ist, wenn die Daten das sagen.
const fussnote = computed(() => {
  const gedruckt = kennzahlen.berechnet
    ? ''
    : ` Gedruckt ist der Wert je Einwohner für ${formatiereJahr(kennzahlen.jahr)} (Vorbericht, PDF-Seite ${String(kennzahlen.einwohnerQuelle)}); die übrigen Jahre sind berechnet.`
  return `Je Einwohner ist der Schuldenstand geteilt durch die Einwohnerzahl, abgerundet. Quelle: PDF-Seite ${String(reihen.pdfSeite)}.${gedruckt}`
})
</script>

<template>
  <div class="om-schulden">
    <BaseChart
      :option="option"
      hoehe="320px"
      :beschreibung="beschreibung"
      :leer-titel="LEER_TITEL"
      :leer-text="LEER_TEXT"
    />

    <ul class="om-schulden__legende" role="list" aria-label="Legende">
      <li>
        <span
          class="om-schulden__farbe"
          :style="{ background: SCHULDEN_FARBEN.investitionskredite }"
          aria-hidden="true"
        ></span>
        Investitionskredite
      </li>
      <li>
        <span
          class="om-schulden__farbe"
          :style="{ background: SCHULDEN_FARBEN.nrw_bank }"
          aria-hidden="true"
        ></span>
        NRW.Bank
      </li>
      <li v-if="berechnetVorhanden">
        <span
          class="om-schulden__farbe om-schulden__farbe--streifen"
          :style="{ '--om-streifen': streifenFarbe }"
          aria-hidden="true"
        ></span>
        Streifen und „berechnet“: nicht gedruckt, aus Kreditaufnahme und Tilgung fortgeschrieben
      </li>
    </ul>

    <p v-if="satz !== null" class="om-schulden__satz">{{ satz }}</p>

    <wa-details summary="Tabelle anzeigen">
      <DatenTabelle
        :beschriftung="`Schuldenstand ${zeitraum}`"
        :spalten="tabelle.spalten"
        :zeilen="tabelle.zeilen"
        :fussnote="fussnote"
        :leer-titel="LEER_TITEL"
        :leer-text="LEER_TEXT"
      >
        <template #zeilenzusatz="{ zeile }">
          <BerechnetEtikett v-if="zeile.etikett === 'berechnet'" />
        </template>
      </DatenTabelle>
    </wa-details>

    <wa-details summary="So wurde gerechnet">
      <p class="om-schulden__formel">{{ reihen.formel }}</p>
      <p class="om-schulden__formel">Quelle: PDF-Seite {{ reihen.pdfSeite }}</p>
    </wa-details>
  </div>
</template>

<style scoped>
.om-schulden {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-m);
  min-width: 0;
}

.om-schulden__legende {
  display: flex;
  flex-wrap: wrap;
  gap: var(--wa-space-xs) var(--wa-space-m);
  margin: 0;
  padding: 0;
  list-style: none;
  font-size: var(--wa-font-size-s);
  color: var(--wa-color-text-quiet);
}

.om-schulden__legende li {
  display: flex;
  align-items: center;
  gap: var(--wa-space-2xs);
}

.om-schulden__farbe {
  display: inline-block;
  flex: none;
  inline-size: 1rem;
  block-size: 1rem;
}

/* Senkrechte Streifen wie im Diagramm (BERECHNET_DECAL), damit die Legende dasselbe zeigt. */
.om-schulden__farbe--streifen {
  background: var(--wa-color-gray-30);
  background-image: repeating-linear-gradient(
    90deg,
    var(--om-streifen) 0,
    var(--om-streifen) 2px,
    transparent 2px,
    transparent 4px
  );
}

.om-schulden__satz,
.om-schulden__formel {
  margin: 0;
  font-size: var(--wa-font-size-s);
  line-height: 1.5;
  color: var(--wa-color-text-quiet);
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-schulden__formel {
  color: inherit;
}
</style>
