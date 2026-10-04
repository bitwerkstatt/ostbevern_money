<script setup lang="ts">
import { computed, useId } from 'vue'

import BaseChart from '@/components/BaseChart.vue'
import DatenTabelle from '@/components/DatenTabelle.vue'
import type { DatenSpalte, DatenZeile } from '@/components/datenTabelle'
import {
  balkenOption,
  baueGeldflussBalken,
  type BalkenSegment,
  type Geldfluss,
} from '@/lib/geldfluss'
import { euro, euroKurz } from '@/charts/format'
import BerechnetEtikett from '@/components/BerechnetEtikett.vue'
import { useJahr } from '@/lib/jahr'

const props = defineProps<{
  geldfluss: Geldfluss
  /** „{Wertart} {jahr}“ für Tooltips und Spaltenkopf. */
  wertartText: string
}>()

const { jahrLink } = useJahr()
const idBasis = useId()

const spalten = computed<DatenSpalte[]>(() => [
  { schluessel: 'name', titel: 'Name', art: 'text' },
  { schluessel: 'wert', titel: props.wertartText, art: 'euro' },
  { schluessel: 'anteil', titel: 'Anteil', art: 'prozent' },
])

/** Muster des Farbfelds: KL und Globaler Minderaufwand tragen es auch im Diagramm (nie Farbe allein). */
function muster(segment: BalkenSegment): string {
  if (segment.art === 'kl') {
    return 'streifen'
  }
  return segment.art === 'minderaufwand' ? 'punkte' : ''
}

function zeilen(segmente: readonly BalkenSegment[]): DatenZeile[] {
  return segmente.map((segment) => ({
    name: segment.name,
    wert: segment.wert,
    anteil: segment.anteil,
    farbe: segment.farbe,
    muster: muster(segment),
    code: segment.code,
    gerundet: segment.gerundet ? 1 : 0,
    berechnet: segment.berechnet ? 1 : 0,
  }))
}

const istLeer = computed(() => props.geldfluss.knoten.length === 0)

const gruppen = computed(() => {
  const balken = baueGeldflussBalken(props.geldfluss)
  return [
    { schluessel: 'woher', titel: 'Woher', segmente: balken.woher, summe: balken.summeWoher },
    { schluessel: 'wohin', titel: 'Wohin', segmente: balken.wohin, summe: balken.summeWohin },
  ].map((gruppe) => ({
    ...gruppe,
    id: `${idBasis}-${gruppe.schluessel}`,
    option: balkenOption(gruppe.segmente, gruppe.summe, props.wertartText),
    beschreibung: `${gruppe.titel}: ${String(gruppe.segmente.length)} Abschnitte, zusammen ${euroKurz(gruppe.summe)}. Die Einzelwerte stehen in der Tabelle darunter.`,
    zeilen: zeilen(gruppe.segmente),
  }))
})
</script>

<template>
  <BaseChart v-if="istLeer" :option="{ series: [] }" hoehe="160px" />
  <div v-else class="om-geldfluss-balken">
    <section v-for="gruppe in gruppen" :key="gruppe.schluessel" :aria-labelledby="gruppe.id">
      <h3 :id="gruppe.id" class="om-geldfluss-balken__titel">{{ gruppe.titel }}</h3>
      <BaseChart :option="gruppe.option" hoehe="56px" :beschreibung="gruppe.beschreibung" />
      <DatenTabelle
        :beschriftung="`${gruppe.titel}: Einzelwerte`"
        :spalten="spalten"
        :zeilen="gruppe.zeilen"
      >
        <template #zelle="{ zeile, spalte, wert }">
          <template v-if="spalte.schluessel === 'wert' && typeof wert === 'number'">
            <span v-if="zeile['gerundet'] === 1">rd. </span>{{ euro(wert) }}
            <BerechnetEtikett v-if="zeile['berechnet'] === 1" />
          </template>
          <span v-else-if="spalte.schluessel === 'name'" class="om-geldfluss-balken__name">
            <span
              class="om-farbfeld"
              :class="zeile.muster ? `om-farbfeld--${String(zeile.muster)}` : undefined"
              :style="{ backgroundColor: String(zeile.farbe) }"
              aria-hidden="true"
            ></span>
            <RouterLink
              v-if="typeof zeile.code === 'string'"
              :to="jahrLink({ name: 'ausgaben', query: { pb: zeile.code } })"
              >{{ zeile.name }}</RouterLink
            >
            <template v-else>{{ zeile.name }}</template>
          </span>
        </template>
      </DatenTabelle>
    </section>
  </div>
</template>

<style scoped>
.om-geldfluss-balken {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-xl);
}

.om-geldfluss-balken section {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-xs);
}

.om-geldfluss-balken__titel {
  margin: 0;
  height: 24px;
  font-size: var(--wa-font-size-m);
  font-weight: var(--wa-font-weight-bold);
  line-height: 24px;
}

.om-geldfluss-balken__name {
  display: inline-flex;
  align-items: flex-start;
  gap: var(--wa-space-xs);
}

.om-farbfeld {
  flex: none;
  width: 16px;
  height: 16px;
  margin-top: 2px;
  border-radius: var(--wa-border-radius-s);
}

/* Muster wie im Diagramm: KL diagonal gestreift, Globaler Minderaufwand gepunktet. */
.om-farbfeld--streifen {
  background-image: repeating-linear-gradient(
    45deg,
    transparent 0 3px,
    color-mix(in srgb, var(--wa-color-surface-default) 45%, transparent) 3px 5px
  );
}

.om-farbfeld--punkte {
  background-image: radial-gradient(
    circle,
    color-mix(in srgb, var(--wa-color-surface-default) 55%, transparent) 1px,
    transparent 1.5px
  );
  background-size: 4px 4px;
}
</style>
