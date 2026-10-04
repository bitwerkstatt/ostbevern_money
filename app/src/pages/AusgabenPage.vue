<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import { jahr as formatiereJahr, zahl } from '@/charts/format'
import AufwandTreemap from '@/components/AufwandTreemap.vue'
import Brotkrumen from '@/components/Brotkrumen.vue'
import ChartCard from '@/components/ChartCard.vue'
import EbenenTabelle from '@/components/EbenenTabelle.vue'
import JahrUmschalter from '@/components/JahrUmschalter.vue'
import PageIntro from '@/components/PageIntro.vue'
import ZuschussBalken from '@/components/ZuschussBalken.vue'
import { ansagen } from '@/lib/ansage'
import { findeKnoten, useAnsicht, type Modus } from '@/lib/ansicht'
import {
  baueBrotkrumen,
  baueEbene,
  ebenenElternCode,
  klickZiel,
  ueberschussTextSchluessel,
} from '@/lib/drilldown'
import { useJahr, wertartName } from '@/lib/jahr'
import { rendereAbsatz, textFuerJahr } from '@/lib/texte'

const router = useRouter()
const { jahr, index, wertart } = useJahr()
const { ansicht, setzeModus, oeffne, zurueck, ansichtsQuery } = useAnsicht()

const wertartText = computed(() => wertartName(wertart.value))
const modus = computed(() => ansicht.value.modus)
const modusName = computed(() => (modus.value === 'aufwand' ? 'Aufwand' : 'Zuschussbedarf'))

// Die aktuelle Ebene: Produktgruppe vor Aufgabenbereich vor der obersten Ebene.
const elternCode = computed(() => ebenenElternCode(ansicht.value.pb, ansicht.value.pg))
const elternKnoten = computed(() => findeKnoten(elternCode.value))
const eintraege = computed(() => baueEbene(elternCode.value, index.value, modus.value))
const brotkrumen = computed(() => baueBrotkrumen(ansicht.value.pb, ansicht.value.pg))
const istOberste = computed(() => ansicht.value.pb === null)
const ebenenName = computed(() => brotkrumen.value[brotkrumen.value.length - 1]?.name ?? '')

const kartenTitel = computed(() => {
  const basis = `${modusName.value} nach Aufgabenbereich ${formatiereJahr(jahr.value)}`
  return istOberste.value ? basis : `${basis} – ${ebenenName.value}`
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

// Klick auf Kachel, Balken oder Tabellenschaltfläche: nur Codes der aktuellen Ebene zählen.
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

// Modus-Umschalter: nur `modus` in der URL ändert sich (replace), die Ebene bleibt, der Fokus
// bleibt auf dem Umschalter, eine Live-Region meldet den Wechsel (D-06).
function beiModus(ereignis: Event) {
  const wert = (ereignis.currentTarget as { value?: unknown } | null)?.value
  if (wert !== 'aufwand' && wert !== 'zuschussbedarf') {
    return
  }
  const neu: Modus = wert
  setzeModus(neu)
  ansagen(neu === 'zuschussbedarf' ? 'Zeige Zuschussbedarf' : 'Zeige Aufwand')
}

// Fokus und Ansage nach einem Ebenenwechsel (Klick, Brotkrumen oder Zurück-Taste). Der
// Schlüssel ist ein String, damit Jahr- oder Modus-Wechsel (neue `ansicht`) nichts auslösen.
const karte = ref<InstanceType<typeof ChartCard> | null>(null)
watch(
  () => `${ansicht.value.pb ?? ''}|${ansicht.value.pg ?? ''}`,
  async () => {
    await nextTick()
    karte.value?.fokussiereTitel()
    const anzahl = eintraege.value.length
    ansagen(`Ebene ${ebenenName.value}, ${zahl(anzahl)} ${anzahl === 1 ? 'Eintrag' : 'Einträge'}`)
  },
)

// Überschuss-Erklärung (AUSG-03): nur im Modus Zuschussbedarf (nur dort sind Einträge als
// Überschuss markiert), ein Absatz je Überschussknoten der Ebene; Text des Aufgabenbereichs
// oder, falls keiner existiert, der allgemeine Text.
const ueberschussZeilen = computed(() =>
  eintraege.value.flatMap((eintrag) => {
    if (!eintrag.ueberschuss) {
      return []
    }
    const text = textFuerJahr(ueberschussTextSchluessel(eintrag.code), jahr.value)
    const absatz = text?.absaetze[0]
    if (text === null || absatz === undefined) {
      return []
    }
    return [
      {
        code: eintrag.code,
        name: eintrag.name,
        text: rendereAbsatz(absatz),
        seiten: text.quelle_seiten.join(', '),
      },
    ]
  }),
)
</script>

<template>
  <PageIntro
    titel="Wofür wird das Geld ausgegeben?"
    beschreibung="Hier siehst du, wohin das Geld der Gemeinde fließt. Klicke auf einen Bereich, um genauer hinzuschauen."
  />
  <div class="om-ausgaben-steuerung">
    <JahrUmschalter />
    <wa-radio-group
      class="om-ausgaben-modus"
      label="Ansicht"
      hint="Zuschussbedarf: Was ein Bereich mehr kostet, als er selbst einnimmt. Das bezahlt die Gemeinde aus Steuern."
      orientation="horizontal"
      :value="modus"
      @change="beiModus"
    >
      <wa-radio appearance="button" value="aufwand">Aufwand</wa-radio>
      <wa-radio appearance="button" value="zuschussbedarf">Zuschussbedarf</wa-radio>
    </wa-radio-group>
  </div>
  <ChartCard ref="karte" :titel="kartenTitel" :pdf="quelle">
    <div class="om-ausgaben-ebene">
      <Brotkrumen :eintraege="brotkrumen" @gehe-zu="zurueck" />
      <AufwandTreemap
        v-if="modus === 'aufwand'"
        :eintraege="eintraege"
        :wertart-text="wertartText"
        :eltern-name="ebenenName"
        @waehle="beiWahl"
      />
      <ZuschussBalken
        v-else
        :eintraege="eintraege"
        :wertart-text="wertartText"
        :eltern-name="ebenenName"
        @waehle="beiWahl"
      />
      <EbenenTabelle
        :eintraege="eintraege"
        :modus="modus"
        :wertart-text="wertartText"
        :jahr="jahr"
        :produkt-query="produktQuery"
        :beschriftung="kartenTitel"
        @waehle="beiWahl"
      />
    </div>
  </ChartCard>
  <wa-callout v-if="ueberschussZeilen.length > 0" variant="neutral" class="om-ausgaben-callout">
    <wa-icon slot="icon" name="circle-info"></wa-icon>
    <strong>Warum manche Bereiche im Plus liegen</strong>
    <p v-for="zeile in ueberschussZeilen" :key="zeile.code">
      {{ zeile.name }}: {{ zeile.text }}
      <span v-if="zeile.seiten !== ''" class="om-ausgaben-quelle"
        >(PDF-Seite {{ zeile.seiten }})</span
      >
    </p>
  </wa-callout>
</template>

<style scoped>
.om-ausgaben-steuerung {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-m);
  margin-block-end: var(--wa-space-l);
}

@media (min-width: 700px) {
  .om-ausgaben-steuerung {
    flex-direction: row;
    flex-wrap: wrap;
    align-items: flex-start;
    gap: var(--wa-space-xl);
  }
}

.om-ausgaben-modus {
  max-inline-size: 32rem;
}

.om-ausgaben-modus::part(form-control-label) {
  font-size: var(--wa-font-size-s);
  font-weight: var(--wa-font-weight-bold);
  line-height: var(--wa-line-height-condensed);
}

/* Mindest-Trefferfläche 44 px (WCAG 2.5.5, UI-SPEC Spacing-Ausnahmen). */
.om-ausgaben-modus wa-radio::part(control) {
  min-height: 44px;
}

.om-ausgaben-modus wa-radio::part(label) {
  white-space: nowrap;
}

.om-ausgaben-ebene {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-m);
}

.om-ausgaben-callout {
  margin-block-start: var(--wa-space-l);
}

.om-ausgaben-callout p {
  margin: var(--wa-space-xs) 0 0;
}

.om-ausgaben-quelle {
  color: var(--wa-color-text-quiet);
}
</style>
