<script setup lang="ts">
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'

import { balkenHoehe, horizontaleBalkenOption, type BalkenZeile } from '@/charts/balken'
import { farbeFuerPb } from '@/charts/echartsTheme'
import { euroKurz } from '@/charts/format'
import BaseChart from '@/components/BaseChart.vue'
import DatenTabelle from '@/components/DatenTabelle.vue'
import type { DatenSpalte, DatenZeile } from '@/components/datenTabelle'
import { segmentZusammenfassung, type BindungsSegment } from '@/lib/bindungsgrad'
import { useSchmalerBildschirm } from '@/lib/bildschirm'
import { klickIndex } from '@/lib/hilfsfunktionen'

// D-04: die Produkte eines Bindungsgrads als Aufklapper mit horizontalen Balken, absteigend nach
// Zuschussbedarf, in der Farbe des Aufgabenbereichs. Ein Klick auf einen Balken öffnet das
// Produkt; der Tastaturpfad ist die Tabelle mit dem Produktnamen als Link.

const props = defineProps<{
  segment: BindungsSegment
  /** „{Wertart} {jahr}“ für Tooltips und Spaltenkopf. */
  wertartText: string
}>()

const router = useRouter()
const istSchmal = useSchmalerBildschirm()

// Das Diagramm entsteht erst beim ersten Öffnen und bleibt danach bestehen. In einem geschlossenen
// Aufklapper hätte es keine Breite (RESEARCH Pitfall 11, A2).
const wurdeGeoeffnet = ref(false)

function beiOeffnen(ereignis: Event) {
  // `wa-show` steigt aus verschachtelten Aufklappern („Tabelle anzeigen“) auf; nur der eigene zählt.
  if (ereignis.target === ereignis.currentTarget) {
    wurdeGeoeffnet.value = true
  }
}

const zusammenfassung = computed(() => segmentZusammenfassung(props.segment))

const zeilen = computed<BalkenZeile[]>(() =>
  props.segment.produkte.map((produkt) => ({
    schluessel: produkt.code,
    name: produkt.name,
    wert: produkt.wert,
    label: euroKurz(produkt.wert),
    farbe: farbeFuerPb(produkt.pb),
  })),
)

const option = computed(() =>
  horizontaleBalkenOption(zeilen.value, {
    farbe: farbeFuerPb('01'),
    wertartText: `Zuschussbedarf ${props.wertartText}`,
    schmal: istSchmal.value,
  }),
)

const hoehe = computed(() => balkenHoehe(props.segment.anzahl))

const beschreibung = computed(
  () =>
    `Balkendiagramm der Produkte mit dem Bindungsgrad ${props.segment.bezeichnung}, geordnet nach dem Zuschussbedarf. Die Farbe zeigt den Aufgabenbereich. Dieselben Werte stehen in der Tabelle darunter.`,
)

const spalten = computed<DatenSpalte[]>(() => [
  { schluessel: 'name', titel: 'Produkt', art: 'text' },
  { schluessel: 'wert', titel: `Zuschussbedarf (${props.wertartText})`, art: 'euro' },
])

const tabelle = computed<DatenZeile[]>(() =>
  props.segment.produkte.map((produkt) => ({
    name: produkt.name,
    wert: produkt.wert,
    code: produkt.code,
  })),
)

function beiKlick(params: unknown) {
  const index = klickIndex(params, props.segment.produkte.length)
  const produkt = index === null ? undefined : props.segment.produkte[index]
  if (produkt !== undefined) {
    void router.push({ name: 'produkt', params: { code: produkt.code } })
  }
}
</script>

<template>
  <wa-details :summary="zusammenfassung" class="om-produktbalken" @wa-show="beiOeffnen">
    <div v-if="wurdeGeoeffnet" class="om-produktbalken__inhalt">
      <BaseChart
        :option="option"
        :hoehe="hoehe"
        :beschreibung="beschreibung"
        @chart-click="beiKlick"
      />
      <wa-details summary="Tabelle anzeigen" class="om-produktbalken__tabelle">
        <DatenTabelle
          :beschriftung="`Produkte mit dem Bindungsgrad ${segment.bezeichnung}`"
          :spalten="spalten"
          :zeilen="tabelle"
        >
          <!-- Nur die erste Spalte wird ersetzt; ohne Inhalt greift die Standarddarstellung. -->
          <template #zelle="{ zeile, spalte, wert }">
            <RouterLink
              v-if="spalte.schluessel === 'name'"
              class="om-produktbalken__link"
              :to="{ name: 'produkt', params: { code: String(zeile['code']) } }"
            >
              {{ wert }}
            </RouterLink>
          </template>
        </DatenTabelle>
      </wa-details>
    </div>
  </wa-details>
</template>

<style scoped>
.om-produktbalken {
  min-width: 0;
}

.om-produktbalken::part(header) {
  min-block-size: 44px;
}

.om-produktbalken::part(summary) {
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-produktbalken__inhalt {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-m);
  min-width: 0;
}

.om-produktbalken__link {
  display: inline-flex;
  align-items: center;
  min-block-size: 44px;
  color: var(--wa-color-brand-40);
  text-decoration: underline;
  overflow-wrap: break-word;
  hyphens: auto;
}
</style>
