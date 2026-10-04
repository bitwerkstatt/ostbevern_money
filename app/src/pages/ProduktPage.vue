<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

import { euro, jahr as formatiereJahr } from '@/charts/format'
import BerechnetEtikett from '@/components/BerechnetEtikett.vue'
import DatenTabelle from '@/components/DatenTabelle.vue'
import GlossarBegriff from '@/components/GlossarBegriff.vue'
import PageIntro from '@/components/PageIntro.vue'
import { useJahr } from '@/lib/jahr'
import {
  baueErlaeuterungen,
  baueGrundzahlen,
  baueInvestitionenTabelle,
  baueProduktInvestitionen,
  baueProduktKopf,
  baueTeilergebnisplan,
} from '@/lib/produkt'

const route = useRoute()
const { jahr, jahrLink } = useJahr()

// Der Code kommt aus der URL: er wird nur über die Produkt-Map nachgeschlagen und im
// Fehlerfall als Text (nie als HTML) angezeigt.
const code = computed(() => {
  const roh = route.params.code
  return typeof roh === 'string' ? roh : ''
})

// Der gemerkte Zustand der Ausgabenansicht (`modus`, `pb`, `pg`) wird in `baueProduktKopf`
// neu validiert; das Jahr hängt `jahrLink` an.
const kopf = computed(() => baueProduktKopf(code.value, route.query))
const produkt = computed(() => kopf.value?.produkt)

// „{Produktcode} · {Aufgabenbereich} · {Produktgruppe}“ (UI-SPEC /produkt/:code)
const kopfzeile = computed(() => {
  const k = kopf.value
  return k === null ? '' : [k.produkt.code, k.pbName, k.pgName].join(' · ')
})

const zurueckZiel = computed(() => {
  const k = kopf.value
  return k === null ? null : jahrLink(k.zurueck)
})

const teilergebnisplan = computed(() => baueTeilergebnisplan(code.value))
const erlaeuterungen = computed(() => baueErlaeuterungen(code.value))
const grundzahlen = computed(() => baueGrundzahlen(code.value))
const investitionen = computed(() => baueInvestitionenTabelle(baueProduktInvestitionen(code.value)))
</script>

<template>
  <template v-if="kopf !== null && produkt !== undefined && zurueckZiel !== null">
    <RouterLink v-slot="{ href, navigate }" custom :to="zurueckZiel">
      <wa-button class="om-produkt__zurueck" appearance="plain" :href="href" @click="navigate">
        ← Zurück zu {{ kopf.zurueckText }}
      </wa-button>
    </RouterLink>

    <PageIntro :titel="produkt.name" :beschreibung="kopfzeile">
      <p>
        Ein <GlossarBegriff schluessel="produkt">Produkt</GlossarBegriff> ist eine Leistung der
        Gemeinde.
      </p>
    </PageIntro>

    <div class="om-produkt">
      <section
        v-if="produkt.beschreibung"
        class="om-produkt__abschnitt"
        aria-labelledby="om-produkt-worum"
      >
        <h2 id="om-produkt-worum">Worum geht es?</h2>
        <p>{{ produkt.beschreibung }}</p>
      </section>

      <section
        v-if="produkt.leistungen.length > 0"
        class="om-produkt__abschnitt"
        aria-labelledby="om-produkt-leistungen"
      >
        <h2 id="om-produkt-leistungen">Leistungen</h2>
        <ul>
          <li v-for="(leistung, index) in produkt.leistungen" :key="index">{{ leistung }}</li>
        </ul>
      </section>

      <section class="om-produkt__abschnitt" aria-labelledby="om-produkt-blick">
        <h2 id="om-produkt-blick">Auf einen Blick</h2>
        <dl class="om-produkt__blick">
          <div v-if="produkt.bindungsgrad">
            <dt><GlossarBegriff schluessel="bindungsgrad">Bindungsgrad</GlossarBegriff></dt>
            <dd>
              <wa-tag size="small" variant="neutral">{{ kopf.bindungsgrad }}</wa-tag>
              <span v-if="kopf.bindungsgradOriginal !== null" class="om-produkt__hinweis">
                Im Haushaltsplan steht: „{{ kopf.bindungsgradOriginal }}“
              </span>
            </dd>
          </div>
          <div v-if="produkt.gremium">
            <dt>Gremium</dt>
            <dd>{{ produkt.gremium }}</dd>
          </div>
          <div v-if="produkt.fachbereich">
            <dt>Fachbereich</dt>
            <dd>{{ produkt.fachbereich }}</dd>
          </div>
        </dl>
      </section>

      <section
        v-if="teilergebnisplan !== null"
        class="om-produkt__abschnitt"
        aria-labelledby="om-produkt-plan"
      >
        <h2 id="om-produkt-plan">{{ teilergebnisplan.titel }}</h2>
        <DatenTabelle
          :beschriftung="teilergebnisplan.titel"
          :spalten="teilergebnisplan.spalten"
          :zeilen="teilergebnisplan.zeilen"
        >
          <template #zeilenzusatz="{ zeile }">
            <BerechnetEtikett v-if="zeile.etikett === 'berechnet'" />
          </template>
        </DatenTabelle>
      </section>

      <section
        v-if="erlaeuterungen.length > 0"
        class="om-produkt__abschnitt"
        aria-labelledby="om-produkt-erlaeuterungen"
      >
        <h2 id="om-produkt-erlaeuterungen">Erläuterungen</h2>
        <ul class="om-produkt__erlaeuterungen">
          <li v-for="(eintrag, index) in erlaeuterungen" :key="index">
            <span v-if="eintrag.betrag !== null" class="om-zahl">{{ euro(eintrag.betrag) }}</span>
            {{ eintrag.text }}
            <span v-if="eintrag.zuAnzeigen" class="om-produkt__zu">
              zu: {{ eintrag.zeilenNamen.join(', ') }}
            </span>
          </li>
        </ul>
      </section>

      <section
        v-if="grundzahlen !== null"
        class="om-produkt__abschnitt"
        aria-labelledby="om-produkt-grundzahlen"
      >
        <h2 id="om-produkt-grundzahlen">Grundzahlen</h2>
        <DatenTabelle
          beschriftung="Grundzahlen"
          :spalten="grundzahlen.spalten"
          :zeilen="grundzahlen.zeilen"
          :fussnote="grundzahlen.fussnote ?? undefined"
        >
          <template #zeilenzusatz="{ zeile }">
            <BerechnetEtikett v-if="zeile.etikett === 'berechnet'" />
          </template>
        </DatenTabelle>
      </section>

      <section class="om-produkt__abschnitt" aria-labelledby="om-produkt-investitionen">
        <h2 id="om-produkt-investitionen">Investitionen</h2>
        <DatenTabelle
          v-if="investitionen.zeilen.length > 0"
          beschriftung="Investitionen"
          :spalten="investitionen.spalten"
          :zeilen="investitionen.zeilen"
        />
        <p v-else>Für dieses Produkt sind keine Investitionen geplant.</p>
      </section>

      <p v-if="kopf.quelleSeite !== null" class="om-produkt__quelle">
        Quelle: Haushaltsplan, PDF-Seite {{ kopf.quelleSeite }}
      </p>
    </div>
  </template>
  <template v-else>
    <PageIntro titel="Dieses Produkt gibt es nicht" beschreibung="" />
    <wa-callout variant="warning">
      <wa-icon slot="icon" name="triangle-exclamation"></wa-icon>
      Zum Code „{{ code }}“ gibt es im Haushalt {{ formatiereJahr(jahr) }} kein Produkt.
      <RouterLink :to="jahrLink({ name: 'ausgaben' })">Zur Ausgabenübersicht</RouterLink>
    </wa-callout>
  </template>
</template>

<style scoped>
.om-produkt {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-xl);
}

.om-produkt__zurueck {
  margin-bottom: var(--wa-space-m);
}

.om-produkt__abschnitt h2 {
  margin: 0 0 var(--wa-space-s);
  font-size: var(--wa-font-size-l);
  font-weight: var(--wa-font-weight-bold);
  line-height: var(--wa-line-height-condensed);
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-produkt__abschnitt p,
.om-produkt__abschnitt li,
.om-produkt__blick dd {
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-produkt__abschnitt p {
  margin: 0;
}

.om-produkt__abschnitt ul {
  margin: 0;
  padding-inline-start: var(--wa-space-l);
}

.om-produkt__blick {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-s);
  margin: 0;
}

.om-produkt__blick dt {
  font-size: var(--wa-font-size-s);
  font-weight: var(--wa-font-weight-bold);
  line-height: var(--wa-line-height-condensed);
}

.om-produkt__blick dd {
  margin: 0;
}

.om-produkt__erlaeuterungen {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-xs);
}

.om-produkt__erlaeuterungen .om-zahl {
  display: inline-block;
  margin-inline-end: var(--wa-space-xs);
  font-weight: var(--wa-font-weight-bold);
}

.om-produkt__zu {
  display: block;
}

.om-produkt__zu,
.om-produkt__hinweis,
.om-produkt__quelle {
  font-size: var(--wa-font-size-s);
  font-weight: var(--wa-font-weight-normal);
  line-height: 1.5;
  color: var(--wa-color-text-quiet);
}

.om-produkt__hinweis {
  margin-inline-start: var(--wa-space-xs);
}

.om-produkt__quelle {
  margin: 0;
}
</style>
