<script setup lang="ts">
import { computed, nextTick, ref, watch } from 'vue'
import { useRouter } from 'vue-router'

import type { BalkenZeile } from '@/charts/balken'
import { euro, euroKurz, jahr as formatiereJahr, KEIN_WERT, prozent, zahl } from '@/charts/format'
import AufwandsartBalken from '@/components/AufwandsartBalken.vue'
import AufwandTreemap from '@/components/AufwandTreemap.vue'
import Brotkrumen from '@/components/Brotkrumen.vue'
import ChartCard from '@/components/ChartCard.vue'
import DatenTabelle from '@/components/DatenTabelle.vue'
import type { DatenSpalte, DatenZeile } from '@/components/datenTabelle'
import EbenenTabelle from '@/components/EbenenTabelle.vue'
import ErklaerText from '@/components/ErklaerText.vue'
import JahrUmschalter from '@/components/JahrUmschalter.vue'
import KreisumlageCallout from '@/components/KreisumlageCallout.vue'
import PageIntro from '@/components/PageIntro.vue'
import ZuschussBalken from '@/components/ZuschussBalken.vue'
import { haushalt } from '@/data/daten'
import { ansagen } from '@/lib/ansage'
import { findeKnoten, useAnsicht, type Modus } from '@/lib/ansicht'
import {
  baueAufwandsarten,
  baueTransferaufwendungen,
  minderaufwandHinweis,
  type TransferPosten,
} from '@/lib/aufwandsarten'
import {
  baueBrotkrumen,
  baueEbene,
  ebenenElternCode,
  klickZiel,
  ueberschussTextSchluessel,
} from '@/lib/drilldown'
import { useJahr, wertartName } from '@/lib/jahr'
import { findeKlKnoten } from '@/lib/kreisumlage'
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

// Zweite Sicht (AUSG-04): Aufwand nach Aufwandsart. Dieselben Euro wie die Treemap, nur anders
// gegliedert: die sieben Zeilen des Gesamtergebnisplans ergeben den Gesamtaufwand des Jahres.
const jahrText = computed(() => formatiereJahr(jahr.value))
const wertartMitJahr = computed(() => `${wertartText.value} ${jahrText.value}`)
const leerTitel = computed(() => `Für ${jahrText.value} gibt es keine Einzelwerte`)
const ARTEN_LEER_TEXT =
  'Der Haushaltsplan nennt für dieses Jahr keine Aufschlüsselung. Wähle ein anderes Jahr oder öffne die Tabelle.'
const ABSCHREIBUNG_SATZ = 'Wertverlust von Gebäuden und Straßen, kein Geldfluss'

const aufwandsarten = computed(() => baueAufwandsarten(index.value))
const artenTitel = computed(() => `Aufwand nach Aufwandsart ${jahrText.value}`)
const hatAbschreibung = computed(() => aufwandsarten.value.some((art) => art.keinGeldfluss))

const artenBalken = computed<BalkenZeile[]>(() =>
  aufwandsarten.value.map((art) => ({
    schluessel: art.schluessel,
    name: art.name,
    wert: art.wert,
    label: `${euroKurz(art.wert)} · ${prozent(art.anteil)}`,
  })),
)

const artenSpalten = computed<DatenSpalte[]>(() => [
  { schluessel: 'name', titel: 'Aufwandsart', art: 'text' },
  { schluessel: 'wert', titel: wertartMitJahr.value, art: 'euro' },
  { schluessel: 'anteil', titel: 'Anteil', art: 'prozent' },
])

// Das Kennzeichen „kein Geldfluss“ als 0/1, weil `DatenZeile` nur Text, Zahlen und `null` kennt.
const artenTabelle = computed<DatenZeile[]>(() =>
  aufwandsarten.value.map((art) => ({
    name: art.name,
    wert: art.wert,
    anteil: art.anteil,
    keinGeldfluss: art.keinGeldfluss ? 1 : 0,
  })),
)

// Transferaufwendungen im Einzelnen (AUSG-04): Tabelle des Vorberichts für das gewählte Jahr,
// die Kita-Einrichtungen stehen eingerückt unter den Kita-Zuschüssen (nur im Haushaltsjahr).
const transferSpalten = computed<DatenSpalte[]>(() => [
  { schluessel: 'name', titel: 'Posten', art: 'text' },
  { schluessel: 'wert', titel: wertartMitJahr.value, art: 'euro' },
  { schluessel: 'quelle', titel: 'PDF-Seite', art: 'text' },
])

const transfer = computed(() => baueTransferaufwendungen(index.value))

// Kennzeichen als 0/1 (`DatenZeile` kennt nur Text, Zahlen und `null`); die Seitenzahl als Text.
function transferZeile(posten: TransferPosten, teil: boolean): DatenZeile {
  return {
    name: posten.name,
    wert: posten.wert,
    quelle: posten.quelle === null ? null : String(posten.quelle),
    gerundet: posten.gerundet ? 1 : 0,
    teil: teil ? 1 : 0,
  }
}

const transferTabelle = computed<DatenZeile[]>(() =>
  transfer.value.flatMap((posten) => [
    transferZeile(posten, false),
    ...(posten.kinder ?? []).map((kind) => transferZeile(kind, true)),
  ]),
)

const transferFussnote = computed(() => {
  const anmerkungen = new Set(
    transfer.value.flatMap((p) => [p, ...(p.kinder ?? [])]).flatMap((p) => p.anmerkung ?? []),
  )
  return anmerkungen.size === 0 ? undefined : [...anmerkungen].join(' ')
})

// Erklärungen zur Ebene (D-07): die Kreisumlage steht oben und in KL, nicht in anderen Bereichen.
const zeigeKlCallout = computed(
  () => ansicht.value.pb === null || ansicht.value.pb === findeKlKnoten().code,
)
const minderaufwand = computed(() => minderaufwandHinweis(index.value))

// Quelle der Aufwandsarten ist der Gesamtergebnisplan.
const gesamtSeite = computed(() => {
  const seite = haushalt.knoten.find((k) => k.code === 'GESAMT')?.pdf_seite
  return seite === null || seite === undefined ? undefined : { seite }
})
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
  <!-- Weitergabe an Kreis und Land: nur auf der obersten Ebene und innerhalb von KL (D-07). -->
  <div v-if="zeigeKlCallout" class="om-ausgaben-callout">
    <KreisumlageCallout :jahr-index="index" :wertart="wertartText" />
  </div>
  <!-- Globaler Minderaufwand: Hinweis unter dem Diagramm, nur bei Wert ≠ 0, nie eine Kachel. -->
  <wa-callout v-if="minderaufwand !== null" variant="neutral" class="om-ausgaben-callout">
    <wa-icon slot="icon" name="circle-info"></wa-icon>
    <strong>Globaler Minderaufwand</strong>
    <ErklaerText
      v-if="minderaufwand.textSchluessel !== null"
      :schluessel="minderaufwand.textSchluessel"
      :jahr="jahr"
      :ueberschrift="false"
    />
    <template v-else>
      <p>{{ minderaufwand.satz }}</p>
      <p v-if="minderaufwand.pdfSeite !== null" class="om-ausgaben-quelle">
        Quelle: PDF-Seite {{ minderaufwand.pdfSeite }}
      </p>
    </template>
  </wa-callout>
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
  <ChartCard :titel="artenTitel" :pdf="gesamtSeite" class="om-ausgaben-arten">
    <AufwandsartBalken
      :zeilen="artenBalken"
      :wertart-text="wertartMitJahr"
      :leer-titel="leerTitel"
    />
    <p v-if="hatAbschreibung" class="om-ausgaben-abschreibung">
      <wa-tag size="small" variant="neutral">kein Geldfluss</wa-tag>
      {{ ABSCHREIBUNG_SATZ }}
    </p>
    <wa-details summary="Transferaufwendungen im Einzelnen" class="om-ausgaben-tabelle">
      <DatenTabelle
        :beschriftung="`Transferaufwendungen im Einzelnen ${jahrText}`"
        :spalten="transferSpalten"
        :zeilen="transferTabelle"
        :fussnote="transferFussnote"
        :leer-titel="leerTitel"
        :leer-text="ARTEN_LEER_TEXT"
      >
        <template #zelle="{ zeile, spalte, wert }">
          <template v-if="spalte.schluessel === 'name'">
            <span :class="{ 'om-ausgaben-teil': zeile['teil'] === 1 }">{{ wert }}</span>
          </template>
          <template v-else-if="spalte.schluessel === 'wert' && typeof wert === 'number'">
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
    <wa-details summary="Tabelle anzeigen" class="om-ausgaben-tabelle">
      <DatenTabelle
        :beschriftung="artenTitel"
        :spalten="artenSpalten"
        :zeilen="artenTabelle"
        :leer-titel="leerTitel"
        :leer-text="ARTEN_LEER_TEXT"
      >
        <template #zeilenzusatz="{ zeile }">
          <wa-tag
            v-if="zeile['keinGeldfluss'] === 1"
            size="small"
            variant="neutral"
            class="om-ausgaben-etikett"
            >kein Geldfluss</wa-tag
          >
        </template>
      </DatenTabelle>
    </wa-details>
  </ChartCard>
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

.om-ausgaben-arten {
  margin-block-start: var(--wa-space-xl);
}

.om-ausgaben-abschreibung {
  margin: var(--wa-space-m) 0 0;
}

.om-ausgaben-tabelle {
  margin-block-start: var(--wa-space-m);
}

.om-ausgaben-teil {
  display: inline-block;
  padding-inline-start: var(--wa-space-m);
}

.om-ausgaben-etikett {
  margin-inline-start: var(--wa-space-2xs);
}
</style>
