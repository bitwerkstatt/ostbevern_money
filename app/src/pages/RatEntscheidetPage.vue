<script setup lang="ts">
import { jahr as formatJahr } from '@/charts/format'
import BindungsgradBalken from '@/components/BindungsgradBalken.vue'
import ChartCard from '@/components/ChartCard.vue'
import ErklaerText from '@/components/ErklaerText.vue'
import GlossarBegriff from '@/components/GlossarBegriff.vue'
import HinweisNichtImHaushalt from '@/components/HinweisNichtImHaushalt.vue'
import NichtBeeinflussbarBlock from '@/components/NichtBeeinflussbarBlock.vue'
import PageIntro from '@/components/PageIntro.vue'
import ProduktBalkenListe from '@/components/ProduktBalkenListe.vue'
import UeberschussListe from '@/components/UeberschussListe.vue'
import WertartEtikett from '@/components/WertartEtikett.vue'
import ZuschussListe from '@/components/ZuschussListe.vue'
import { haushalt } from '@/data/daten'
import { baueBindungsgrad, FINANZIERUNGSPRODUKT } from '@/lib/bindungsgrad'
import { findeProdukt } from '@/lib/ansicht'
import { wertartFuerJahr, wertartName } from '@/lib/jahr'

// Die Seite zeigt das Haushaltsjahr, ohne Jahr-Umschalter: der Bindungsgrad ist eine Aussage
// zum Haushaltsjahr (UI-SPEC Routes). Die Wertart folgt aus den Daten.
const wertart = wertartFuerJahr(haushalt.haushaltsjahr)
const jahrText = formatJahr(haushalt.haushaltsjahr)
const wertartText = `${wertartName(wertart)} ${jahrText}`
const lead =
  'Nicht jeder Euro im Haushalt ist frei verfügbar. Hier siehst du, was der Rat beeinflussen kann und was vorgegeben ist.'

// RAT-01, D-01: der Balken summiert nur Produkte mit Zuschussbedarf > 0. Das Finanzierungsprodukt
// steht nicht darin; sein Name kommt aus den Daten.
const bindungsgrad = baueBindungsgrad()
const finanzierungsName = findeProdukt(FINANZIERUNGSPRODUKT)?.name
if (finanzierungsName === undefined) {
  throw new Error(`Das Finanzierungsprodukt ${FINANZIERUNGSPRODUKT} fehlt in produkte.json`)
}
</script>

<template>
  <div class="om-rat-entscheidet">
    <PageIntro titel="Worüber entscheidet der Rat?" :beschreibung="lead">
      <WertartEtikett :wertart="wertart" />
    </PageIntro>
    <section class="om-rat-entscheidet__abschnitt">
      <ChartCard :titel="`Zuschussbedarf ${jahrText} nach Bindungsgrad`">
        <BindungsgradBalken :modell="bindungsgrad" :wertart-text="wertartText" />
        <template #fuss>
          <p class="om-rat-entscheidet__hinweis">
            Im Balken stehen nur Produkte, die mehr kosten, als sie selbst einnehmen.
            {{ finanzierungsName }} (Steuern und Schlüsselzuweisung) bringt Geld ein, das diese
            Kosten bezahlt, und steht deshalb nicht im Balken. Die Summe im Balken ist deshalb nicht
            der Zuschussbedarf des ganzen Haushalts.
          </p>
        </template>
      </ChartCard>
      <wa-callout variant="neutral" class="om-rat-entscheidet__callout">
        <wa-icon slot="icon" name="circle-info"></wa-icon>
        <ErklaerText schluessel="bindungsgrad_selbstauskunft" />
        <p>Was der <GlossarBegriff schluessel="bindungsgrad" /> bedeutet, steht im Glossar.</p>
      </wa-callout>
    </section>
    <section
      v-if="bindungsgrad.segmente.length > 0"
      class="om-rat-entscheidet__abschnitt om-rat-entscheidet__produkte"
      aria-labelledby="om-rat-entscheidet-produkte"
    >
      <h2 id="om-rat-entscheidet-produkte" class="om-rat-entscheidet__titel">
        Die Produkte hinter dem Balken
      </h2>
      <p class="om-rat-entscheidet__lead">
        Öffne einen Bindungsgrad, um seine Produkte mit dem Zuschussbedarf zu sehen.
      </p>
      <ProduktBalkenListe
        v-for="segment in bindungsgrad.segmente"
        :key="segment.bindungsgrad"
        :segment="segment"
        :wertart-text="wertartText"
      />
    </section>
    <UeberschussListe :produkte="bindungsgrad.ueberschuss" :wertart-text="wertartText" />
    <NichtBeeinflussbarBlock :balken-summe="bindungsgrad.summe" />
    <ZuschussListe />
    <HinweisNichtImHaushalt variante="kurz" />
  </div>
</template>

<style scoped>
.om-rat-entscheidet {
  max-width: 72rem;
  margin-inline: auto;
}

.om-rat-entscheidet__abschnitt {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-m);
  min-width: 0;
}

.om-rat-entscheidet__produkte {
  margin-block-start: var(--wa-space-xl);
}

.om-rat-entscheidet__titel {
  margin: 0;
  font-size: var(--wa-font-size-xl);
  font-weight: var(--wa-font-weight-bold);
  line-height: var(--wa-line-height-condensed);
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-rat-entscheidet__lead {
  margin: 0;
  line-height: var(--wa-line-height-normal);
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-rat-entscheidet__hinweis {
  margin: 0;
  font-size: var(--wa-font-size-s);
  line-height: var(--wa-line-height-normal);
  color: var(--wa-color-text-quiet);
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-rat-entscheidet__callout {
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-rat-entscheidet__callout p {
  margin: var(--wa-space-s) 0 0;
}
</style>
