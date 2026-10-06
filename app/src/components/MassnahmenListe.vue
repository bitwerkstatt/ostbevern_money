<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'

import { balkenHoehe, horizontaleBalkenOption, type BalkenZeile } from '@/charts/balken'
import { farbeFuerPb } from '@/charts/echartsTheme'
import { euroKurz, jahr as formatiereJahr, zahl } from '@/charts/format'
import BaseChart from '@/components/BaseChart.vue'
import DatenTabelle from '@/components/DatenTabelle.vue'
import { useSchmalerBildschirm } from '@/lib/bildschirm'
import {
  baueMassnahmenTabelle,
  GROESSTE_ANZAHL,
  klickIndex,
  planjahre,
  type Vorhaben,
} from '@/lib/investitionen'

const props = defineProps<{
  /** Alle Maßnahmen der Auswahl, absteigend nach Summe (`baueVorhaben`). */
  vorhaben: readonly Vorhaben[]
}>()

const router = useRouter()
const istSchmal = useSchmalerBildschirm()

const groesste = computed(() => props.vorhaben.slice(0, GROESSTE_ANZAHL))

const zeitraum = computed(() => {
  const jahre = planjahre()
  const erstes = jahre[0]
  const letztes = jahre.at(-1)
  return erstes === undefined || letztes === undefined
    ? ''
    : `${formatiereJahr(erstes)}–${formatiereJahr(letztes)}`
})

const zeilen = computed<BalkenZeile[]>(() =>
  groesste.value.map((eintrag) => ({
    schluessel: eintrag.schluessel,
    name: eintrag.name,
    wert: eintrag.summe,
    label: euroKurz(eintrag.summe),
    farbe: farbeFuerPb(eintrag.pb),
  })),
)

const option = computed(() =>
  horizontaleBalkenOption(zeilen.value, {
    farbe: farbeFuerPb('01'),
    wertartText: `Summe ${zeitraum.value}`,
    schmal: istSchmal.value,
  }),
)

const hoehe = computed(() => balkenHoehe(groesste.value.length))

const beschreibung = computed(
  () =>
    `Balkendiagramm der größten Investitionsmaßnahmen ${zeitraum.value}, geordnet nach der Summe der Auszahlungen. Dieselben Werte stehen in der Tabelle darunter.`,
)

const tabelle = computed(() => baueMassnahmenTabelle(props.vorhaben))

const hinweis = computed(() =>
  props.vorhaben.length > GROESSTE_ANZAHL
    ? `Gezeigt werden die ${zahl(GROESSTE_ANZAHL)} größten von ${zahl(props.vorhaben.length)}. Alle stehen in der Tabelle.`
    : null,
)

// Klick auf einen Balken öffnet das Produkt der Maßnahme (ohne Query); der Tastaturpfad ist die
// Tabelle mit den Links.
function beiKlick(params: unknown) {
  const index = klickIndex(params, groesste.value.length)
  const eintrag = index === null ? undefined : groesste.value[index]
  if (eintrag !== undefined) {
    void router.push({ name: 'produkt', params: { code: eintrag.produkt } })
  }
}
</script>

<template>
  <div class="om-massnahmen-liste">
    <BaseChart
      :option="option"
      :hoehe="hoehe"
      :beschreibung="beschreibung"
      @chart-click="beiKlick"
    />
    <p v-if="hinweis !== null" class="om-massnahmen-hinweis">{{ hinweis }}</p>
    <wa-details summary="Tabelle anzeigen" class="om-massnahmen-tabelle">
      <DatenTabelle
        :beschriftung="`Investitionsmaßnahmen ${zeitraum}`"
        :spalten="tabelle.spalten"
        :zeilen="tabelle.zeilen"
      >
        <!-- Nur die erste Spalte wird ersetzt; ohne Inhalt greift die Standarddarstellung. -->
        <template #zelle="{ zeile, spalte, wert }">
          <RouterLink
            v-if="spalte.schluessel === 'name'"
            class="om-massnahmen-link"
            :to="{ name: 'produkt', params: { code: String(zeile['produkt']) } }"
          >
            {{ wert }}
          </RouterLink>
        </template>
      </DatenTabelle>
    </wa-details>
  </div>
</template>

<style scoped>
.om-massnahmen-liste {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-m);
}

.om-massnahmen-hinweis {
  margin: 0;
  font-size: var(--wa-font-size-s);
  color: var(--wa-color-text-quiet);
}

.om-massnahmen-link {
  display: inline-flex;
  align-items: center;
  min-block-size: 44px;
  color: var(--wa-color-brand-40);
  text-decoration: underline;
  overflow-wrap: break-word;
  hyphens: auto;
}
</style>
