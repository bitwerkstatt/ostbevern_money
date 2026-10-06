<script setup lang="ts">
import { computed } from 'vue'

import { euro, euroKurz, jahr as formatiereJahr } from '@/charts/format'
import ChartCard from '@/components/ChartCard.vue'
import ErklaerText from '@/components/ErklaerText.vue'
import GlossarBegriff from '@/components/GlossarBegriff.vue'
import KennzahlKachel from '@/components/KennzahlKachel.vue'
import MassnahmenFilter from '@/components/MassnahmenFilter.vue'
import MassnahmenListe from '@/components/MassnahmenListe.vue'
import PageIntro from '@/components/PageIntro.vue'
import SchuldenstandDiagramm from '@/components/SchuldenstandDiagramm.vue'
import VeFaelligkeiten from '@/components/VeFaelligkeiten.vue'
import { haushalt } from '@/data/daten'
import { vePdfSeiten, veGesamt } from '@/lib/finanzierung'
import { planjahre, useMassnahmenFilter } from '@/lib/investitionen'
import { wertartFuerJahr, wertartName } from '@/lib/jahr'
import { quellenZeile } from '@/lib/kennzahlen'
import { baueSchuldenstand, schuldenKennzahlen } from '@/lib/schulden'

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

// Kennzahlkacheln zum Schuldenstand am Ende des Vorjahrs (D-10). „Schulden je Einwohner“ trägt nur
// dann „berechnet“, wenn das Datenfeld des Vorjahrs es sagt (gedruckt: kein Etikett).
const schuldenstand = baueSchuldenstand()
const schulden = schuldenKennzahlen()
const kacheln = [
  {
    schluessel: 'schuldenstand',
    bezeichnung: `Schuldenstand Ende ${formatiereJahr(schulden.jahr)}`,
    wert: euroKurz(schulden.gesamt),
    zeile: quellenZeile(schulden.wertart, schulden.jahr, [schulden.quelle]),
    berechnet: false,
  },
  {
    schluessel: 'schulden_je_einwohner',
    bezeichnung: 'Schulden je Einwohner',
    wert: euro(schulden.proKopf),
    zeile: quellenZeile(schulden.wertart, schulden.jahr, schulden.pdfSeiten),
    berechnet: schulden.berechnet,
  },
  {
    schluessel: 'verpflichtungsermaechtigungen',
    bezeichnung: 'Verpflichtungsermächtigungen',
    wert: euroKurz(veGesamt()),
    zeile: quellenZeile(
      wertartName(wertartFuerJahr(haushalt.haushaltsjahr)),
      haushalt.haushaltsjahr,
      vePdfSeiten(),
    ),
    berechnet: false,
  },
]

const veQuelle = `Haushaltsplan, PDF-Seiten ${vePdfSeiten().join(', ')}`

const schuldenTitel = (() => {
  const erstes = schuldenstand.jahre[0]
  const letztes = schuldenstand.jahre.at(-1)
  return erstes === undefined || letztes === undefined
    ? 'Schuldenstand'
    : `Schuldenstand ${formatiereJahr(erstes)}–${formatiereJahr(letztes)}`
})()

// Der Filterzustand liegt in der URL (`pb`, `art`); die Filterzeile liest ihn selbst, die Seite
// braucht die Treffer und den Rücksetzer für den Leerzustand.
const { vorhaben, zuruecksetzen } = useMassnahmenFilter()
</script>

<template>
  <div class="om-investitionen">
    <PageIntro titel="Investitionen und Schulden" :beschreibung="lead" />
    <p class="om-investitionen__hinweis">
      Diese Seite zeigt Ein- und Auszahlungen (<GlossarBegriff schluessel="finanzplan"
        >Finanzplan</GlossarBegriff
      >), nicht Erträge und Aufwendungen.
    </p>
    <ul
      class="om-investitionen__kacheln"
      role="list"
      aria-label="Kennzahlen zu Schulden und Verpflichtungen"
    >
      <li v-for="kachel in kacheln" :key="kachel.schluessel">
        <KennzahlKachel
          :bezeichnung="kachel.bezeichnung"
          :wert="kachel.wert"
          :zeile="kachel.zeile"
          :berechnet="kachel.berechnet"
        />
      </li>
    </ul>
    <section class="om-investitionen__abschnitt" aria-labelledby="om-investitionen-massnahmen">
      <h2 id="om-investitionen-massnahmen">{{ massnahmenTitel }}</h2>
      <MassnahmenFilter />
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

.om-investitionen__kacheln {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: var(--wa-space-m);
  margin: 0;
  padding: 0;
  list-style: none;
}

.om-investitionen__abschnitt {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-m);
  margin-block-start: var(--wa-space-xl);
}

.om-investitionen__abschnitt h2 {
  margin: 0;
  font-size: var(--wa-font-size-xl);
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
