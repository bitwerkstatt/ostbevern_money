<script setup lang="ts">
import { computed, ref } from 'vue'

import type { BalkenZeile } from '@/charts/balken'
import { INVEST_FARBE } from '@/charts/echartsTheme'
import {
  euro,
  euroKurz,
  formatiere,
  jahr as formatiereJahr,
  KEIN_WERT,
  prozent,
} from '@/charts/format'
import BerechnetEtikett from '@/components/BerechnetEtikett.vue'
import ChartCard from '@/components/ChartCard.vue'
import DatenTabelle from '@/components/DatenTabelle.vue'
import type { DatenSpalte, DatenZeile } from '@/components/datenTabelle'
import ErklaerText from '@/components/ErklaerText.vue'
import ErtragsBalken from '@/components/ErtragsBalken.vue'
import GlossarBegriff from '@/components/GlossarBegriff.vue'
import HinweisNichtImHaushalt from '@/components/HinweisNichtImHaushalt.vue'
import JahrUmschalter from '@/components/JahrUmschalter.vue'
import PageIntro from '@/components/PageIntro.vue'
import SteuerZeitreihe from '@/components/SteuerZeitreihe.vue'
import { haushalt } from '@/data/daten'
import { useReducedMotion } from '@/lib/bewegung'
import {
  AUFSCHLUESSELUNG_FUER_ERTRAGSART,
  baueInvestiveEinnahmen,
  baueInvestiveTabelle,
  baueSonstigeErtraege,
  baueSteuern,
  baueZuwendungen,
  hatInvestiveWerte,
  quellenText,
  type Aufschluesselung,
  type PostenZeile,
} from '@/lib/einnahmen'
import { baueErtragsarten } from '@/lib/ertragsarten'
import { useJahr, wertartName } from '@/lib/jahr'
import { STANDARD_ZEITREIHE, baueZeitreihe, zeitreihenSeite } from '@/lib/zeitreihen'
import { zeilenName } from '@/lib/zeilen'

const { jahr, index, wertart } = useJahr()
const reduzierteBewegung = useReducedMotion()

const jahrText = computed(() => formatiereJahr(jahr.value))
const haushaltsjahrText = formatiereJahr(haushalt.haushaltsjahr)
const wertartText = computed(() => `${wertartName(wertart.value)} ${jahrText.value}`)
const leerTitel = computed(() => `Für ${jahrText.value} gibt es keine Einzelwerte`)

const LEER_TEXT =
  'Der Haushaltsplan nennt für dieses Jahr keine Aufschlüsselung. Wähle ein anderes Jahr oder öffne die Tabelle.'

// Ebene 1 (EINN-01): Ertragsarten des gewählten Jahres, gelesen aus dem Gesamtergebnisplan.
const ertragsarten = computed(() => baueErtragsarten(index.value))

const balkenZeilen = computed<BalkenZeile[]>(() =>
  ertragsarten.value.map((art) => ({
    schluessel: art.schluessel,
    name: art.name,
    wert: art.wert,
    label: `${euroKurz(art.wert)} · ${prozent(art.anteil)}`,
  })),
)

const ertragsSpalten = computed<DatenSpalte[]>(() => [
  { schluessel: 'name', titel: 'Ertragsart', art: 'text' },
  { schluessel: 'wert', titel: wertartText.value, art: 'euro' },
  { schluessel: 'anteil', titel: 'Anteil', art: 'prozent' },
])

const ertragsTabelle = computed<DatenZeile[]>(() =>
  ertragsarten.value.map((art) => ({ name: art.name, wert: art.wert, anteil: art.anteil })),
)

// Quellseite der Ebene 1: der Gesamtergebnisplan.
const gesamtSeite = computed(() => {
  const seite = haushalt.knoten.find((knoten) => knoten.code === 'GESAMT')?.pdf_seite
  return seite === null || seite === undefined ? undefined : { seite }
})

// Ebene 2 (EINN-02 bis EINN-04): nur Ertragsarten mit Aufschlüsselung bekommen ein wa-details.
interface Aufklapper {
  id: Aufschluesselung
  titel: string
  /** Betrag der Ertragsart aus Ebene 1 (eurogenau) für die Überschrift, `null` ohne Zeile. */
  betrag: number | null
  spalten: DatenSpalte[]
  tabelle: DatenZeile[]
  fussnote: string | undefined
}

const GEMEINDE_LEGT_FEST = 'selbst festgelegt'
const NICHT_SELBST_FESTGELEGT = 'nicht selbst festgelegt'

/** Eine Tabellenzeile; Kennzeichen als 0/1, weil `DatenZeile` nur Text, Zahlen und `null` kennt. */
function tabellenZeile(
  zeile: PostenZeile,
  extra: { festlegung?: string; teil?: boolean } = {},
): DatenZeile {
  return {
    schluessel: zeile.posten,
    name: zeile.name,
    wert: zeile.wert,
    festlegung: extra.festlegung ?? null,
    gerundet: zeile.gerundet ? 1 : 0,
    berechnet: zeile.berechnet ? 1 : 0,
    keinGeldfluss: zeile.keinGeldfluss ? 1 : 0,
    teil: extra.teil === true ? 1 : 0,
  }
}

function hatWerte(zeilen: readonly PostenZeile[]): boolean {
  return zeilen.some((zeile) => zeile.wert !== null)
}

function betragVon(ertragsart: string): number | null {
  return ertragsarten.value.find((art) => art.schluessel === ertragsart)?.wert ?? null
}

function titelVon(ertragsart: string): string {
  return zeilenName('ergebnisplan', ertragsart)
}

const steuern = computed(() => baueSteuern(index.value))
const zuwendungen = computed(() => baueZuwendungen(index.value))
const sonstigeErtraege = computed(() => baueSonstigeErtraege(index.value))

const aufklapper = computed<Aufklapper[]>(() => {
  const liste: Aufklapper[] = []
  if (hatWerte(steuern.value)) {
    liste.push({
      id: 'steuern',
      titel: titelVon('steuern'),
      betrag: betragVon('steuern'),
      spalten: [
        { schluessel: 'name', titel: 'Steuerart', art: 'text' },
        { schluessel: 'wert', titel: wertartText.value, art: 'euro' },
        { schluessel: 'festlegung', titel: 'Festlegung', art: 'text' },
      ],
      tabelle: steuern.value.map((zeile) =>
        tabellenZeile(zeile, {
          festlegung: zeile.selbstFestgelegt ? GEMEINDE_LEGT_FEST : NICHT_SELBST_FESTGELEGT,
        }),
      ),
      fussnote: quellenText(steuern.value.map((zeile) => zeile.quelle)),
    })
  }
  if (hatWerte(zuwendungen.value)) {
    liste.push({
      id: 'zuwendungen',
      titel: titelVon('zuwendungen'),
      betrag: betragVon('zuwendungen'),
      spalten: [
        { schluessel: 'name', titel: 'Posten', art: 'text' },
        { schluessel: 'wert', titel: wertartText.value, art: 'euro' },
      ],
      tabelle: zuwendungen.value.map((zeile) => tabellenZeile(zeile)),
      fussnote: quellenText(zuwendungen.value.map((zeile) => zeile.quelle)),
    })
  }
  if (hatWerte(sonstigeErtraege.value)) {
    liste.push({
      id: 'sonstige',
      titel: titelVon('sonstige_ordentliche_ertraege'),
      betrag: betragVon('sonstige_ordentliche_ertraege'),
      spalten: [
        { schluessel: 'name', titel: 'Posten', art: 'text' },
        { schluessel: 'wert', titel: wertartText.value, art: 'euro' },
      ],
      tabelle: sonstigeErtraege.value.map((zeile) =>
        tabellenZeile(zeile, { teil: zeile.teilVon !== null }),
      ),
      fussnote: quellenText(sonstigeErtraege.value.map((zeile) => zeile.quelle)),
    })
  }
  return liste
})

// Hebesätze stehen nur für das Haushaltsjahr im PDF; die Zeile trägt deshalb immer dessen Jahr
// (EINN-02), auch wenn ein anderes Jahr gewählt ist.
const hebesaetze = computed(() => steuern.value.filter((zeile) => zeile.hebesatz !== null))
const hebesatzText = computed(() =>
  hebesaetze.value
    .map((zeile) => `${zeile.name} ${formatiere(zeile.hebesatz, 'prozent')}`)
    .join(', '),
)
const hebesatzQuelle = computed(() =>
  quellenText(hebesaetze.value.map((zeile) => zeile.hebesatzQuelle)),
)

const AUFKLAPPER_PREFIX = 'om-aufschluesselung-'

/** Klick auf einen Ertragsbalken: öffnet die passende Aufschlüsselung und scrollt dorthin. */
function oeffneAufschluesselung(ertragsart: string) {
  const art = AUFSCHLUESSELUNG_FUER_ERTRAGSART.get(ertragsart)
  if (art === undefined) {
    return
  }
  const element = document.getElementById(`${AUFKLAPPER_PREFIX}${art}`)
  if (element === null || !('open' in element)) {
    return
  }
  element.open = true
  element.scrollIntoView({ behavior: reduzierteBewegung.value ? 'auto' : 'smooth', block: 'start' })
}

// Zeitreihe (EINN-05): hängt nicht am Jahr-Umschalter, sie zeigt immer alle Jahre (D-01).
const steuerart = ref(STANDARD_ZEITREIHE)

const entwicklungTitel = computed(() => {
  const punkte = baueZeitreihe(steuerart.value)
  const erster = punkte[0]
  const letzter = punkte.at(-1)
  return erster === undefined || letzter === undefined
    ? 'Entwicklung'
    : `Entwicklung ${formatiereJahr(erster.jahr)}–${formatiereJahr(letzter.jahr)}`
})

const entwicklungSeite = computed(() => {
  const seite = zeitreihenSeite(steuerart.value)
  return seite === null ? undefined : { seite }
})

// Investive Einnahmen (EINN-06, D-03): Finanzplan, nie im selben Diagramm wie die Erträge.
const investiv = computed(() => baueInvestiveEinnahmen(index.value))
const investivTabelleZeilen = computed(() => baueInvestiveTabelle(index.value))

const investivBalken = computed<BalkenZeile[]>(() =>
  hatInvestiveWerte(investiv.value)
    ? investiv.value.map((zeile) => ({
        schluessel: zeile.schluessel,
        name: zeile.name,
        wert: zeile.wert,
        label: zeile.wert === null ? KEIN_WERT : euroKurz(zeile.wert),
      }))
    : [],
)

const investivSpalten = computed<DatenSpalte[]>(() => [
  { schluessel: 'name', titel: 'Posten', art: 'text' },
  { schluessel: 'wert', titel: wertartText.value, art: 'euro' },
  { schluessel: 'quelle', titel: 'Quelle', art: 'text' },
])

const investivTabelle = computed<DatenZeile[]>(() =>
  investivTabelleZeilen.value.map((zeile) => ({
    schluessel: zeile.schluessel,
    name: zeile.name,
    wert: zeile.wert,
    quelle: zeile.quelle === null ? null : `PDF-Seite ${String(zeile.quelle)}`,
    gerundet: zeile.gerundet ? 1 : 0,
    berechnet: zeile.berechnet ? 1 : 0,
    keinGeldfluss: 0,
    teil: 0,
  })),
)

const investivSeite = computed(() => {
  const seite = investivTabelleZeilen.value.find((zeile) => zeile.gruppe === 'finanzplan')?.quelle
  return seite === null || seite === undefined ? undefined : { seite }
})
</script>

<template>
  <PageIntro
    titel="Woher kommt das Geld?"
    beschreibung="Die Gemeinde finanziert sich aus Steuern, Zuweisungen und Gebühren. Hier siehst du, wie viel aus welcher Quelle kommt."
  />
  <JahrUmschalter />

  <div class="om-einnahmen">
    <ChartCard :titel="`Ertragsarten ${jahrText}`" :pdf="gesamtSeite">
      <ErtragsBalken
        :zeilen="balkenZeilen"
        :wertart-text="wertartText"
        :leer-titel="leerTitel"
        @waehle="oeffneAufschluesselung"
      />
      <wa-details summary="Tabelle anzeigen" class="om-einnahmen__tabelle">
        <DatenTabelle
          :beschriftung="`Ertragsarten ${jahrText}`"
          :spalten="ertragsSpalten"
          :zeilen="ertragsTabelle"
          :leer-titel="leerTitel"
          :leer-text="LEER_TEXT"
        />
      </wa-details>
    </ChartCard>

    <section v-if="aufklapper.length > 0" aria-labelledby="om-zusammensetzung-titel">
      <h2 id="om-zusammensetzung-titel" class="om-einnahmen__ueberschrift">
        Woraus sich die Erträge zusammensetzen
      </h2>
      <div class="om-einnahmen__aufklapper-liste">
        <wa-details
          v-for="gruppe in aufklapper"
          :id="`${AUFKLAPPER_PREFIX}${gruppe.id}`"
          :key="gruppe.id"
          :open="gruppe.id === 'steuern'"
          class="om-einnahmen__aufklapper"
        >
          <span slot="summary" class="om-einnahmen__summary">
            <span class="om-einnahmen__summary-name">{{ gruppe.titel }}</span>
            <span v-if="gruppe.betrag !== null" class="om-zahl">{{ euroKurz(gruppe.betrag) }}</span>
          </span>

          <div class="om-einnahmen__inhalt">
            <DatenTabelle
              :beschriftung="`${gruppe.titel} ${jahrText}`"
              :spalten="gruppe.spalten"
              :zeilen="gruppe.tabelle"
              :fussnote="gruppe.fussnote"
              :leer-titel="leerTitel"
              :leer-text="LEER_TEXT"
            >
              <template #zelle="{ zeile, spalte, wert }">
                <template v-if="spalte.schluessel === 'name'">
                  <span :class="{ 'om-einnahmen__teil': zeile['teil'] === 1 }">{{ wert }}</span>
                  <wa-tag
                    v-if="zeile['keinGeldfluss'] === 1"
                    size="s"
                    variant="neutral"
                    class="om-einnahmen__etikett"
                    >kein Geldfluss</wa-tag
                  >
                </template>
                <template v-else-if="spalte.schluessel === 'wert' && typeof wert === 'number'">
                  <span v-if="zeile['gerundet'] === 1">rd. </span>{{ euro(wert) }}
                  <BerechnetEtikett v-if="zeile['berechnet'] === 1" />
                </template>
                <template v-else-if="wert === null">
                  <span aria-hidden="true">{{ KEIN_WERT }}</span>
                  <span class="om-visually-hidden">kein Wert</span>
                </template>
                <template v-else>{{ wert }}</template>
              </template>
            </DatenTabelle>

            <template v-if="gruppe.id === 'steuern'">
              <p v-if="hebesaetze.length > 0" class="om-einnahmen__hebesaetze">
                <GlossarBegriff schluessel="hebesatz">Hebesätze</GlossarBegriff>
                {{ haushaltsjahrText }}: {{ hebesatzText }}.
                <span v-if="hebesatzQuelle" class="om-einnahmen__quelle">{{ hebesatzQuelle }}</span>
              </p>
              <ErklaerText schluessel="grundsteuer_hebesaetze" :jahr="jahr" />
              <ErklaerText schluessel="steuern_selbst_festgelegt" />
            </template>
            <template v-else-if="gruppe.id === 'zuwendungen'">
              <p class="om-einnahmen__glossar">
                Was
                <GlossarBegriff schluessel="schluesselzuweisung"
                  >Schlüsselzuweisungen</GlossarBegriff
                >
                und
                <GlossarBegriff schluessel="sonderposten">Sonderposten</GlossarBegriff>
                sind, erklärt das Glossar.
              </p>
              <ErklaerText schluessel="zuwendungen_laufende_zwecke" />
              <ErklaerText schluessel="sonderposten" :jahr="jahr" />
            </template>
            <ErklaerText
              v-else-if="gruppe.id === 'sonstige'"
              schluessel="sonderposten"
              :jahr="jahr"
            />
          </div>
        </wa-details>
      </div>
    </section>

    <ChartCard :titel="entwicklungTitel" :pdf="entwicklungSeite">
      <SteuerZeitreihe v-model="steuerart" />
    </ChartCard>

    <wa-divider></wa-divider>

    <section aria-labelledby="om-investiv-titel" class="om-einnahmen__investiv">
      <h2 id="om-investiv-titel" class="om-einnahmen__ueberschrift">Investive Einnahmen</h2>
      <wa-callout variant="neutral">
        <wa-icon slot="icon" name="circle-info"></wa-icon>
        Diese Einnahmen fließen nicht in den laufenden Haushalt. Sie bezahlen Investitionen wie
        Gebäude, Straßen oder Fahrzeuge.
      </wa-callout>
      <ChartCard :titel="`Investive Einnahmen ${jahrText}`" :pdf="investivSeite">
        <ErtragsBalken
          :zeilen="investivBalken"
          :farbe="INVEST_FARBE"
          :wertart-text="wertartText"
          :leer-titel="leerTitel"
        />
        <wa-details summary="Tabelle anzeigen" class="om-einnahmen__tabelle">
          <DatenTabelle
            :beschriftung="`Investive Einnahmen ${jahrText}`"
            :spalten="investivSpalten"
            :zeilen="investivTabelle"
            :leer-titel="leerTitel"
            :leer-text="LEER_TEXT"
          >
            <template #zelle="{ zeile, spalte, wert }">
              <template v-if="spalte.schluessel === 'wert' && typeof wert === 'number'">
                <span v-if="zeile['gerundet'] === 1">rd. </span>{{ euro(wert) }}
                <BerechnetEtikett v-if="zeile['berechnet'] === 1" />
              </template>
              <template v-else-if="wert === null">
                <span aria-hidden="true">{{ KEIN_WERT }}</span>
                <span class="om-visually-hidden">kein Wert</span>
              </template>
              <template v-else>{{ wert }}</template>
            </template>
          </DatenTabelle>
        </wa-details>
      </ChartCard>
    </section>
  </div>
  <!-- Was nicht im Haushalt steht (Abwasser, TEO): am Seitenende, nach Investive Einnahmen (D-18). -->
  <HinweisNichtImHaushalt variante="einnahmen" />
</template>

<style scoped>
.om-einnahmen {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-xl);
  margin-top: var(--wa-space-xl);
}

.om-einnahmen__ueberschrift {
  margin: 0 0 var(--wa-space-m);
  font-size: var(--wa-font-size-l);
  font-weight: var(--wa-font-weight-bold);
  line-height: var(--wa-line-height-condensed);
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-einnahmen__tabelle {
  margin-top: var(--wa-space-m);
}

.om-einnahmen__aufklapper-liste {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-s);
}

.om-einnahmen__aufklapper {
  /* wa-page liefert die Kopfzeilenhöhe über --scroll-margin-top, scrollIntoView beachtet es. */
  scroll-margin-top: calc(var(--scroll-margin-top, 0px) + var(--wa-space-m));
}

/* Name links, Betrag rechts; bis 699 px rutscht der Betrag unter den Namen (UI-SPEC E4). */
.om-einnahmen__summary {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: baseline;
  gap: var(--wa-space-2xs) var(--wa-space-m);
  width: 100%;
}

.om-einnahmen__summary-name {
  font-weight: var(--wa-font-weight-bold);
  hyphens: auto;
  overflow-wrap: break-word;
  min-width: 0;
}

.om-einnahmen__inhalt {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-m);
  min-width: 0;
}

.om-einnahmen__hebesaetze,
.om-einnahmen__glossar {
  margin: 0;
}

.om-einnahmen__quelle {
  font-size: var(--wa-font-size-s);
  color: var(--wa-color-text-quiet);
}

.om-einnahmen__teil {
  display: inline-block;
  padding-inline-start: var(--wa-space-m);
}

.om-einnahmen__etikett {
  margin-inline-start: var(--wa-space-2xs);
}

.om-einnahmen__investiv {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-m);
}

.om-einnahmen__investiv .om-einnahmen__ueberschrift {
  margin-bottom: 0;
}
</style>
