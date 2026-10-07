<script setup lang="ts">
import { computed } from 'vue'

import { euroKurz, jahr as formatiereJahr } from '@/charts/format'
import ChartCard from '@/components/ChartCard.vue'
import ErklaerText from '@/components/ErklaerText.vue'
import FinanzierungsDiagramm from '@/components/FinanzierungsDiagramm.vue'
import GlossarBegriff from '@/components/GlossarBegriff.vue'
import KennzahlKachel from '@/components/KennzahlKachel.vue'
import MassnahmenFilter from '@/components/MassnahmenFilter.vue'
import MassnahmenListe from '@/components/MassnahmenListe.vue'
import PageIntro from '@/components/PageIntro.vue'
import SchuldenstandDiagramm from '@/components/SchuldenstandDiagramm.vue'
import VeFaelligkeiten from '@/components/VeFaelligkeiten.vue'
import { haushalt, investitionen } from '@/data/daten'
import { vePdfSeiten, veGesamt } from '@/lib/finanzierung'
import { quellenZeile } from '@/lib/hilfsfunktionen'
import { planjahre, useMassnahmenFilter } from '@/lib/investitionen'
import { wertartFuerJahr, wertartName } from '@/lib/jahr'
import { belegSchluessel } from '@/lib/quelle'
import { baueSchuldenstand, schuldenKacheln } from '@/lib/schulden'

// Die Seite zeigt alle ausgewiesenen Jahre, ohne Jahr-Umschalter (UI-SPEC Routes). Der Lead
// enthält keine Zahlen und darf deshalb als Text im Code stehen.
const lead =
  'Hier siehst du, was die Gemeinde in den kommenden Jahren baut und anschafft, wie sie das bezahlt und wie hoch ihre Schulden sind.'

const massnahmenTitel = computed(() => {
  const jahre = planjahre()
  const erstes = jahre[0]
  const letztes = jahre.at(-1)
  return erstes === undefined || letztes === undefined
    ? 'Maßnahmen'
    : `Maßnahmen ${formatiereJahr(erstes)}–${formatiereJahr(letztes)}`
})

// Kennzahlkacheln zum Schuldenstand am Ende des Vorjahrs (D-10). Beide Schuldenkacheln baut
// `schuldenKacheln()`; „berechnet“ steht nur, wenn das Datenfeld des Vorjahrs es sagt (WR-03).
const schuldenstand = baueSchuldenstand()
const veWertart = wertartName(wertartFuerJahr(haushalt.haushaltsjahr))
const kacheln = [
  ...schuldenKacheln(),
  {
    schluessel: 'verpflichtungsermaechtigungen',
    bezeichnung: 'Verpflichtungsermächtigungen',
    wert: euroKurz(veGesamt()),
    zeile: quellenZeile(veWertart, haushalt.haushaltsjahr, vePdfSeiten()),
    berechnet: false,
    // Die VE-Summe steht in der VE-Spalte der gedruckten Summenzeile „Auszahlungen aus
    // Investitionstätigkeit“ des Gesamtfinanzplans; dieselbe Zeile belegt sie, ohne Herleitung.
    quelle: belegSchluessel.fp('GESAMT', 'auszahlungen_investitionen'),
    herleitung: null as string | null,
    wertart: `${veWertart} ${formatiereJahr(haushalt.haushaltsjahr)}`,
  },
]

const finanzierungSeite = investitionen.finanzierung.quelle
const veQuelle = `Haushaltsplan, PDF-Seiten ${vePdfSeiten().join(', ')}`

const schuldenTitel = (() => {
  const erstes = schuldenstand.jahre[0]
  const letztes = schuldenstand.jahre.at(-1)
  return erstes === undefined || letztes === undefined
    ? 'Schuldenstand'
    : `Schuldenstand ${formatiereJahr(erstes)}–${formatiereJahr(letztes)}`
})()

// Der Filterzustand liegt in der URL (`pb`, `art`) und wird hier genau einmal je Seite angelegt;
// die Filterzeile bekommt ihn als Prop, die Seite braucht die Treffer und den Rücksetzer.
const steuerung = useMassnahmenFilter()
const { vorhaben, zuruecksetzen } = steuerung
</script>

<template>
  <div class="om-investitionen">
    <PageIntro titel="Investitionen und Schulden" :beschreibung="lead" />
    <p class="om-investitionen__hinweis">
      Diese Seite zeigt Ein- und Auszahlungen (<GlossarBegriff schluessel="finanzplan"
        >Finanzplan</GlossarBegriff
      >), nicht Erträge und Aufwendungen.
    </p>
    <ul class="om-kachelraster" role="list" aria-label="Kennzahlen zu Schulden und Verpflichtungen">
      <li v-for="kachel in kacheln" :key="kachel.schluessel">
        <KennzahlKachel
          :bezeichnung="kachel.bezeichnung"
          :wert="kachel.wert"
          :zeile="kachel.zeile"
          :berechnet="kachel.berechnet"
          :quelle="kachel.quelle"
          :herleitung="kachel.herleitung"
          :wertart="kachel.wertart"
        />
      </li>
    </ul>
    <section class="om-investitionen__abschnitt" aria-labelledby="om-investitionen-massnahmen">
      <h2 id="om-investitionen-massnahmen">{{ massnahmenTitel }}</h2>
      <MassnahmenFilter :steuerung="steuerung" />
      <ChartCard v-if="vorhaben.length > 0" titel="Die größten Maßnahmen">
        <MassnahmenListe :vorhaben="vorhaben" />
      </ChartCard>
      <div v-else class="om-investitionen__leer">
        <h3>Keine Maßnahmen für diese Auswahl</h3>
        <p>
          Für diese Kombination gibt es im Haushaltsplan keine Maßnahmen. Wähle einen anderen
          Aufgabenbereich oder eine andere Art, oder setze den Filter zurück.
        </p>
        <wa-button class="om-investitionen__zuruecksetzen" @click="zuruecksetzen">
          Filter zurücksetzen
        </wa-button>
      </div>
    </section>
    <section class="om-investitionen__abschnitt" aria-labelledby="om-investitionen-ve">
      <h2 id="om-investitionen-ve">Verpflichtungsermächtigungen</h2>
      <ErklaerText schluessel="verpflichtungsermaechtigungen" />
      <p class="om-investitionen__erklaerung">
        Die Säulen zeigen
        <GlossarBegriff schluessel="verpflichtungsermaechtigung"
          >Verpflichtungsermächtigungen</GlossarBegriff
        >
        nach dem Jahr, in dem sie fällig werden.
      </p>
      <ChartCard titel="Verpflichtungsermächtigungen nach Fälligkeit" :quelle="veQuelle">
        <VeFaelligkeiten />
      </ChartCard>
    </section>
    <section class="om-investitionen__abschnitt" aria-labelledby="om-investitionen-finanzierung">
      <h2 id="om-investitionen-finanzierung">Wie die Investitionen bezahlt werden</h2>
      <p class="om-investitionen__erklaerung">
        Beide Diagramme zeigen Ein- und Auszahlungen des
        <GlossarBegriff schluessel="finanzplan">Finanzplans</GlossarBegriff>, nicht Erträge und
        Aufwendungen.
      </p>
      <ChartCard titel="Investitionen und ihre Einzahlungen" :pdf="{ seite: finanzierungSeite }">
        <FinanzierungsDiagramm variante="investitionen" />
      </ChartCard>
      <ChartCard titel="Kreditaufnahme und Tilgung" :pdf="{ seite: finanzierungSeite }">
        <FinanzierungsDiagramm variante="kredite" />
      </ChartCard>
    </section>
    <section class="om-investitionen__abschnitt" aria-labelledby="om-investitionen-schulden">
      <h2 id="om-investitionen-schulden">Schulden</h2>
      <ChartCard :titel="schuldenTitel" :pdf="{ seite: schuldenstand.pdfSeite }">
        <SchuldenstandDiagramm />
      </ChartCard>
      <ErklaerText schluessel="schulden_anstieg" />
    </section>
  </div>
</template>

<style scoped>
.om-investitionen {
  max-width: 72rem;
  margin-inline: auto;
}

.om-investitionen__hinweis {
  margin: 0 0 var(--wa-space-l);
  font-size: var(--wa-font-size-s);
  color: var(--wa-color-text-quiet);
}

.om-investitionen__erklaerung {
  margin: 0;
  font-size: var(--wa-font-size-s);
  color: var(--wa-color-text-quiet);
}

.om-investitionen__abschnitt {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-m);
  margin-block-start: var(--wa-space-xl);
}

.om-investitionen__abschnitt h2 {
  margin: 0;
  font-size: var(--wa-font-size-l);
  font-weight: var(--wa-font-weight-bold);
  line-height: var(--wa-line-height-condensed);
}

.om-investitionen__leer {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--wa-space-s);
  padding: var(--wa-space-l) var(--wa-space-m);
  background: var(--wa-color-surface-lowered);
  text-align: center;
}

.om-investitionen__leer h3 {
  margin: 0;
  font-size: var(--wa-font-size-l);
  font-weight: var(--wa-font-weight-bold);
}

.om-investitionen__leer p {
  margin: 0;
  max-width: 32rem;
  color: var(--wa-color-text-quiet);
}

/* Mindest-Trefferfläche 44 px (WCAG 2.5.5, UI-SPEC Spacing-Ausnahmen). */
.om-investitionen__zuruecksetzen::part(base) {
  min-height: 44px;
}
</style>
