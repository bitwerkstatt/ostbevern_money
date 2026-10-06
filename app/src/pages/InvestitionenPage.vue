<script setup lang="ts">
import { computed } from 'vue'

import { jahr as formatiereJahr } from '@/charts/format'
import ChartCard from '@/components/ChartCard.vue'
import GlossarBegriff from '@/components/GlossarBegriff.vue'
import MassnahmenListe from '@/components/MassnahmenListe.vue'
import PageIntro from '@/components/PageIntro.vue'
import { baueVorhaben, planjahre } from '@/lib/investitionen'

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

const vorhaben = computed(() => baueVorhaben({ pb: null, art: null }))
</script>

<template>
  <div class="om-investitionen">
    <PageIntro titel="Investitionen und Schulden" :beschreibung="lead" />
    <p class="om-investitionen__hinweis">
      Diese Seite zeigt Ein- und Auszahlungen (<GlossarBegriff schluessel="finanzplan"
        >Finanzplan</GlossarBegriff
      >), nicht Erträge und Aufwendungen.
    </p>
    <section class="om-investitionen__abschnitt" aria-labelledby="om-investitionen-massnahmen">
      <h2 id="om-investitionen-massnahmen">{{ massnahmenTitel }}</h2>
      <ChartCard titel="Die größten Maßnahmen">
        <MassnahmenListe :vorhaben="vorhaben" />
      </ChartCard>
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
</style>
