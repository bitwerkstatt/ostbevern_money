<script setup lang="ts">
import { computed } from 'vue'

import { euro, euroKurz, jahr as formatJahr, prozent } from '@/charts/format'
import EinstiegsKachel from '@/components/EinstiegsKachel.vue'
import GlossarBegriff from '@/components/GlossarBegriff.vue'
import KennzahlKachel from '@/components/KennzahlKachel.vue'
import KreisumlageCallout from '@/components/KreisumlageCallout.vue'
import PageIntro from '@/components/PageIntro.vue'
import { haushalt } from '@/data/daten'
import { baueEinstiege, baueKennzahlen, quellenZeile, type Kennzahl } from '@/lib/kennzahlen'

// Die Startseite zeigt immer das Haushaltsjahr, ohne Jahr-Umschalter (UI-SPEC Routes).
const jahrText = formatJahr(haushalt.haushaltsjahr)
const jahrIndex = haushalt.jahre.indexOf(haushalt.haushaltsjahr)

function wertText(kennzahl: Kennzahl): string {
  return kennzahl.anzeige === 'kurz' ? euroKurz(kennzahl.wert) : euro(kennzahl.wert)
}

const kennzahlen = computed(() =>
  baueKennzahlen().map((k) => ({
    ...k,
    wertText: wertText(k),
    zeile: quellenZeile(k.wertart, k.jahr, k.pdfSeiten),
  })),
)

const einstiege = computed(() => {
  const e = baueEinstiege()
  return {
    wertart: e.wertart,
    einnahmen: {
      ...e.einnahmen,
      betrag: euroKurz(e.einnahmen.wert),
      anteilText: prozent(e.einnahmen.anteil),
      zeile: quellenZeile(e.wertart, e.jahr, [e.einnahmen.pdfSeite]),
    },
    ausgaben: {
      ...e.ausgaben,
      betrag: euroKurz(e.ausgaben.wert),
      zeile: quellenZeile(e.wertart, e.jahr, [e.ausgaben.pdfSeite]),
    },
  }
})
</script>

<template>
  <PageIntro
    :titel="`Der Haushalt ${jahrText} der Gemeinde Ostbevern`"
    beschreibung="Hier siehst du, woher das Geld der Gemeinde kommt und wofür sie es ausgibt. Alle Zahlen stammen direkt aus dem Haushaltsplan."
  />

  <section class="om-start__kennzahlen" aria-labelledby="om-start-kennzahlen">
    <h2 id="om-start-kennzahlen">Die wichtigsten Zahlen {{ jahrText }}</h2>
    <p class="om-start__hinweis">
      Der
      <GlossarBegriff schluessel="ergebnisplan">Ergebnisplan</GlossarBegriff>
      stellt
      <GlossarBegriff schluessel="ertrag_aufwand">Erträge und Aufwendungen</GlossarBegriff>
      gegenüber, der
      <GlossarBegriff schluessel="finanzplan">Finanzplan</GlossarBegriff>
      erfasst die geplanten Zahlungen.
    </p>
    <ul class="om-start__raster" role="list">
      <li v-for="k in kennzahlen" :key="k.schluessel">
        <KennzahlKachel
          :bezeichnung="k.bezeichnung"
          :wert="k.wertText"
          :zeile="k.zeile"
          :berechnet="k.berechnet"
          :quelle="k.quelle"
          :herleitung="k.herleitung"
          :wertart="`${k.wertart} ${formatJahr(k.jahr)}`"
        />
      </li>
    </ul>
  </section>

  <section class="om-start__einstiege" aria-label="Die beiden Leitfragen">
    <EinstiegsKachel
      frage="Woher kommt das Geld?"
      :zeile="einstiege.einnahmen.zeile"
      :ziel="{ name: 'einnahmen' }"
      cta="Einnahmen ansehen"
    >
      Den größten Teil der Erträge machen {{ einstiege.einnahmen.name }} aus:
      <span class="om-zahl">{{ einstiege.einnahmen.betrag }}</span> ({{
        einstiege.einnahmen.anteilText
      }}).
    </EinstiegsKachel>
    <EinstiegsKachel
      frage="Wofür wird das Geld ausgegeben?"
      :zeile="einstiege.ausgaben.zeile"
      :ziel="{ name: 'ausgaben' }"
      cta="Ausgaben ansehen"
    >
      Ohne die Weitergabe an Kreis und Land bekommt {{ einstiege.ausgaben.name }} den größten
      Anteil: <span class="om-zahl">{{ einstiege.ausgaben.betrag }}</span
      >.
    </EinstiegsKachel>
  </section>

  <div class="om-start__kreisumlage">
    <KreisumlageCallout kurz :jahr-index="jahrIndex" :wertart="einstiege.wertart" />
  </div>
</template>

<style scoped>
.om-start__kennzahlen h2 {
  margin: 0 0 var(--wa-space-m);
  font-size: var(--wa-font-size-l);
  font-weight: var(--wa-font-weight-bold);
  line-height: var(--wa-line-height-condensed);
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-start__hinweis {
  margin: 0 0 var(--wa-space-m);
  font-size: var(--wa-font-size-m);
  line-height: var(--wa-line-height-normal);
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-start__raster {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: var(--wa-space-m);
  margin: 0;
  padding: 0;
  list-style: none;
}

.om-start__einstiege {
  display: grid;
  grid-template-columns: 1fr;
  gap: var(--wa-space-m);
  margin-top: var(--wa-space-xl);
}

.om-start__kreisumlage {
  margin-top: var(--wa-space-xl);
}

@media (min-width: 700px) {
  .om-start__raster,
  .om-start__einstiege {
    gap: var(--wa-space-l);
  }

  .om-start__einstiege {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
