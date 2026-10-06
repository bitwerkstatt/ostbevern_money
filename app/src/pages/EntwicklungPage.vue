<script setup lang="ts">
import { jahr as formatiereJahr, prozent } from '@/charts/format'
import BerechnetEtikett from '@/components/BerechnetEtikett.vue'
import ChartCard from '@/components/ChartCard.vue'
import DatenTabelle from '@/components/DatenTabelle.vue'
import type { DatenSpalte, DatenZeile } from '@/components/datenTabelle'
import EntwicklungsDiagramm from '@/components/EntwicklungsDiagramm.vue'
import ErgebnisBalken from '@/components/ErgebnisBalken.vue'
import ErklaerText from '@/components/ErklaerText.vue'
import GlossarBegriff from '@/components/GlossarBegriff.vue'
import PageIntro from '@/components/PageIntro.vue'
import { haushalt } from '@/data/daten'
import PostenZeitreihe from '@/components/PostenZeitreihe.vue'
import RueckgangBalken from '@/components/RueckgangBalken.vue'
import RuecklagenBalken from '@/components/RuecklagenBalken.vue'
import { ENTWICKLUNG_POSTEN, baueErgebnisReihen, bauePostenReihe } from '@/lib/entwicklung'
import { wertartName } from '@/lib/jahr'
import {
  baueRuecklagen,
  hskSchwellen,
  rueckgangPlanjahre,
  ruecklagenTabelle,
} from '@/lib/ruecklagen'

// Die Seite zeigt immer alle ausgewiesenen Jahre, ohne Jahr-Umschalter (UI-SPEC Routes).
// Erstes und letztes Jahr kommen aus den Daten, nie aus dem Quelltext.
const erstesJahr = formatiereJahr(haushalt.jahre[0] ?? haushalt.haushaltsjahr)
const letztesJahr = formatiereJahr(
  haushalt.jahre[haushalt.jahre.length - 1] ?? haushalt.haushaltsjahr,
)
const lead = `Hier siehst du, wie sich Erträge, Aufwendungen und Ergebnis der Gemeinde bis ${letztesJahr} entwickeln und wie lange die Rücklagen als Polster reichen.`

// Das Jahresergebnis steht nach dem globalen Minderaufwand, wie in der Haushaltssatzung und auf der
// Startseite (Entscheidung 1 der Phase); die Linien zeigen die Werte davor.
const ERGEBNIS_UNTERTITEL =
  'Jahresergebnis nach globalem Minderaufwand, wie in der Haushaltssatzung. Die Linien oben zeigen Erträge und Aufwendungen vor diesem Abzug. Ein Defizit liegt unter der Nulllinie.'

const ergebnisplanSeite = baueErgebnisReihen().ertraege[0]?.pdfSeite
const ergebnisplanQuelle = ergebnisplanSeite == null ? undefined : { seite: ergebnisplanSeite }

/** Die fünf Posten-Karten mit ihrer Quellseite (erste Seite, die die Reihe nennt). */
const karten = ENTWICKLUNG_POSTEN.map((posten) => {
  const seite = bauePostenReihe(posten.schluessel).find(
    (punkt) => punkt.pdfSeite !== null,
  )?.pdfSeite
  return { posten, pdf: seite == null ? undefined : { seite } }
})

// Die Rücklagen stehen in der Eigenkapitalübersicht des Vorberichts (Quellseite aus den Daten).
const eigenkapitalSeite = haushalt.eigenkapital.gesamt_vorbericht.quelle
const eigenkapitalQuelle = eigenkapitalSeite === null ? undefined : { seite: eigenkapitalSeite }

// Ohne Rücklagenwerte zeigt die Karte den Leerzustand; Tabelle, Rückgang und Polster-Text entfallen.
const hatRuecklagen = baueRuecklagen().some(
  (zeile) => zeile.allgemeine !== null || zeile.ausgleich !== null,
)
// Mit nur einem Planjahr gibt es keinen Verlauf: die Rückgang-Karte entfällt, die Tabelle bleibt.
const zeigeRueckgang = hatRuecklagen && rueckgangPlanjahre().length >= 2

const schwellen = hskSchwellen()
const SCHWELLEN_TEXT = `Laut Vorbericht (PDF-Seite ${String(schwellen.pdfSeite)}) ist die Schwelle ein Rückgang der allgemeinen Rücklage um mehr als ${prozent(schwellen.einJahr)} in einem Jahr oder um mehr als ${prozent(schwellen.zweiJahre)} in zwei aufeinanderfolgenden Jahren.`
const RUECKGANG_ERKLAERUNG =
  'Um diesen Anteil sinkt die allgemeine Rücklage im jeweiligen Jahr, bezogen auf ihren Bestand zu Jahresbeginn.'

const TABELLEN_SPALTEN: DatenSpalte[] = [
  { schluessel: 'jahr', titel: 'Jahr', art: 'text' },
  { schluessel: 'allgemeine', titel: 'Allgemeine Rücklage (Bestand zu Jahresbeginn)', art: 'euro' },
  { schluessel: 'ausgleich', titel: 'Ausgleichsrücklage (Bestand zu Jahresbeginn)', art: 'euro' },
  { schluessel: 'rueckgang', titel: 'Rückgang im Jahr (berechnet)', art: 'prozent' },
]
const tabellenZeilen: DatenZeile[] = ruecklagenTabelle().map((zeile) => ({
  jahr: `${formatiereJahr(zeile.jahr)} · ${wertartName(zeile.wertart)}`,
  allgemeine: zeile.allgemeine,
  ausgleich: zeile.ausgleich,
  rueckgang: zeile.rueckgang,
}))
const tabellenFussnote =
  (eigenkapitalSeite === null
    ? ''
    : `Quelle: Eigenkapitalübersicht, PDF-Seite ${String(eigenkapitalSeite)}. `) +
  `Der Rückgang im Jahr ist berechnet wie im Vorbericht (PDF-Seite ${String(schwellen.pdfSeite)}): ` +
  'der Fehlbetrag des Jahres, soweit die Ausgleichsrücklage ihn nicht deckt, geteilt durch die allgemeine Rücklage zu Jahresbeginn.'
</script>

<template>
  <div class="om-entwicklung">
    <PageIntro titel="Wie entwickelt sich der Haushalt?" :beschreibung="lead" />

    <section class="om-entwicklung__abschnitt" aria-labelledby="om-entwicklung-ergebnis">
      <h2 id="om-entwicklung-ergebnis">Erträge, Aufwendungen und Ergebnis</h2>
      <ChartCard
        :titel="`Erträge und Aufwendungen ${erstesJahr}–${letztesJahr}`"
        :pdf="ergebnisplanQuelle"
      >
        <EntwicklungsDiagramm />
      </ChartCard>
      <ChartCard
        :titel="`Jahresergebnis ${erstesJahr}–${letztesJahr}`"
        :beschreibung="ERGEBNIS_UNTERTITEL"
        :pdf="ergebnisplanQuelle"
      >
        <ErgebnisBalken />
      </ChartCard>
      <wa-callout variant="neutral" class="om-entwicklung__callout">
        <wa-icon slot="icon" name="circle-info"></wa-icon>
        <strong
          ><GlossarBegriff schluessel="globaler_minderaufwand"
            >Globaler Minderaufwand</GlossarBegriff
          ></strong
        >
        <ErklaerText schluessel="globaler_minderaufwand" :ueberschrift="false" />
      </wa-callout>
    </section>

    <section class="om-entwicklung__abschnitt" aria-labelledby="om-entwicklung-posten">
      <h2 id="om-entwicklung-posten">Wichtige Posten im Verlauf</h2>
      <div class="om-entwicklung__raster">
        <ChartCard
          v-for="karte in karten"
          :key="karte.posten.schluessel"
          :titel="karte.posten.titel"
          :pdf="karte.pdf"
        >
          <PostenZeitreihe :posten="karte.posten" />
        </ChartCard>
      </div>
    </section>

    <section class="om-entwicklung__abschnitt" aria-labelledby="om-entwicklung-polster">
      <h2 id="om-entwicklung-polster">Wie lange reicht das Polster?</h2>
      <ChartCard :titel="`Rücklagen ${erstesJahr}–${letztesJahr}`" :pdf="eigenkapitalQuelle">
        <RuecklagenBalken />
      </ChartCard>

      <ChartCard
        v-if="zeigeRueckgang"
        titel="Rückgang der allgemeinen Rücklage"
        :pdf="eigenkapitalQuelle"
      >
        <p class="om-entwicklung__berechnet">
          <BerechnetEtikett />
          {{ RUECKGANG_ERKLAERUNG }}
        </p>
        <RueckgangBalken />
        <p class="om-entwicklung__unterschrift">{{ SCHWELLEN_TEXT }}</p>
      </ChartCard>

      <template v-if="hatRuecklagen">
        <DatenTabelle
          beschriftung="Rücklagen und Rückgang der allgemeinen Rücklage je Jahr"
          :spalten="TABELLEN_SPALTEN"
          :zeilen="tabellenZeilen"
          :fussnote="tabellenFussnote"
        />
        <wa-callout variant="neutral" class="om-entwicklung__callout">
          <wa-icon slot="icon" name="circle-info"></wa-icon>
          <strong><GlossarBegriff schluessel="haushaltssicherung" /></strong>
          <ErklaerText schluessel="polster" :ueberschrift="false" />
        </wa-callout>
      </template>
    </section>
  </div>
</template>

<style scoped>
.om-entwicklung {
  max-width: 72rem;
  margin-inline: auto;
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-xl);
}

.om-entwicklung__abschnitt {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-m);
}

.om-entwicklung__raster {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: var(--wa-space-m);
}

/* Ab 700 px laufen die Karten in zwei oder mehr Spalten, darunter in einer. */
@media (min-width: 700px) {
  .om-entwicklung__raster {
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  }
}

.om-entwicklung__raster > * {
  min-width: 0;
}

.om-entwicklung__callout {
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-entwicklung__berechnet,
.om-entwicklung__unterschrift {
  margin: 0;
  font-size: var(--wa-font-size-s);
  color: var(--wa-color-text-quiet);
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-entwicklung__berechnet {
  /* Das Etikett sitzt vor dem Satz, ohne Außenabstand links. */
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--wa-space-xs);
}

.om-entwicklung__callout strong {
  display: block;
  margin-block-end: var(--wa-space-xs);
}

.om-entwicklung__abschnitt > h2 {
  margin: 0;
  font-size: var(--wa-font-size-xl);
  font-weight: var(--wa-font-weight-bold);
  line-height: var(--wa-line-height-condensed);
  hyphens: auto;
  overflow-wrap: break-word;
}
</style>
