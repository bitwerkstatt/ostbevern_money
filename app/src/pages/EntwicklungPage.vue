<script setup lang="ts">
import { jahr as formatiereJahr } from '@/charts/format'
import ChartCard from '@/components/ChartCard.vue'
import EntwicklungsDiagramm from '@/components/EntwicklungsDiagramm.vue'
import PageIntro from '@/components/PageIntro.vue'
import { haushalt } from '@/data/daten'
import { baueErgebnisReihen } from '@/lib/entwicklung'

// Die Seite zeigt immer alle ausgewiesenen Jahre, ohne Jahr-Umschalter (UI-SPEC Routes).
// Erstes und letztes Jahr kommen aus den Daten, nie aus dem Quelltext.
const erstesJahr = formatiereJahr(haushalt.jahre[0] ?? haushalt.haushaltsjahr)
const letztesJahr = formatiereJahr(
  haushalt.jahre[haushalt.jahre.length - 1] ?? haushalt.haushaltsjahr,
)
const lead = `Hier siehst du, wie sich Erträge, Aufwendungen und Ergebnis der Gemeinde bis ${letztesJahr} entwickeln und wie lange die Rücklagen als Polster reichen.`

const ergebnisplanSeite = baueErgebnisReihen().ertraege[0]?.pdfSeite
const ergebnisplanQuelle = ergebnisplanSeite == null ? undefined : { seite: ergebnisplanSeite }
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

.om-entwicklung__abschnitt > h2 {
  margin: 0;
  font-size: var(--wa-font-size-xl);
  font-weight: var(--wa-font-weight-bold);
  line-height: var(--wa-line-height-condensed);
  hyphens: auto;
  overflow-wrap: break-word;
}
</style>
