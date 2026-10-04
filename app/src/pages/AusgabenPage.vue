<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'

import { jahr as formatiereJahr } from '@/charts/format'
import AufwandTreemap from '@/components/AufwandTreemap.vue'
import ChartCard from '@/components/ChartCard.vue'
import EbenenTabelle from '@/components/EbenenTabelle.vue'
import JahrUmschalter from '@/components/JahrUmschalter.vue'
import PageIntro from '@/components/PageIntro.vue'
import { findeKnoten, useAnsicht } from '@/lib/ansicht'
import { baueEbene, ebenenElternCode, klickZiel } from '@/lib/drilldown'
import { useJahr, wertartName } from '@/lib/jahr'

const router = useRouter()
const { jahr, index, wertart } = useJahr()
const { ansicht, oeffne, ansichtsQuery } = useAnsicht()

const wertartText = computed(() => wertartName(wertart.value))

// Die aktuelle Ebene: Produktgruppe vor Aufgabenbereich vor der obersten Ebene.
const elternCode = computed(() => ebenenElternCode(ansicht.value.pb, ansicht.value.pg))
const elternKnoten = computed(() => findeKnoten(elternCode.value))
const eintraege = computed(() => baueEbene(elternCode.value, index.value, 'aufwand'))
const istOberste = computed(() => ansicht.value.pb === null)

const kartenTitel = computed(() => {
  const basis = `Aufwand nach Aufgabenbereich ${formatiereJahr(jahr.value)}`
  const name = elternKnoten.value?.name
  return istOberste.value || name === undefined ? basis : `${basis} – ${name}`
})

const quelle = computed(() => {
  const seite = elternKnoten.value?.pdf_seite
  return seite === null || seite === undefined ? undefined : { seite }
})

// Links auf ein Produkt tragen Jahr und Ansicht, damit „Zurück“ dieselbe Ebene öffnet (D-09).
const produktQuery = computed<Record<string, string>>(() => ({
  jahr: String(jahr.value),
  ...ansichtsQuery(),
}))

// Klick auf Kachel oder Tabellenschaltfläche: nur Codes der aktuellen Ebene zählen.
function beiWahl(code: string) {
  const eintrag = eintraege.value.find((e) => e.code === code)
  if (eintrag === undefined) {
    return
  }
  const ziel = klickZiel(eintrag)
  if (ziel === 'drill') {
    oeffne(code)
  } else if (ziel === 'produkt') {
    void router.push({ name: 'produkt', params: { code }, query: produktQuery.value })
  }
}
</script>

<template>
  <PageIntro
    titel="Wofür wird das Geld ausgegeben?"
    beschreibung="Hier siehst du, wohin das Geld der Gemeinde fließt. Klicke auf einen Bereich, um genauer hinzuschauen."
  />
  <JahrUmschalter />
  <ChartCard :titel="kartenTitel" :pdf="quelle">
    <div class="om-ausgaben-ebene">
      <AufwandTreemap
        :eintraege="eintraege"
        :wertart-text="wertartText"
        :eltern-name="elternKnoten?.name ?? ''"
        @waehle="beiWahl"
      />
      <EbenenTabelle
        :eintraege="eintraege"
        modus="aufwand"
        :wertart-text="wertartText"
        :jahr="jahr"
        :produkt-query="produktQuery"
        :beschriftung="kartenTitel"
        @waehle="beiWahl"
      />
    </div>
  </ChartCard>
</template>

<style scoped>
.om-ausgaben-ebene {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-m);
}
</style>
