<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'

import { jahr as formatiereJahr } from '@/charts/format'
import PageIntro from '@/components/PageIntro.vue'
import { useJahr } from '@/lib/jahr'
import { baueProduktKopf } from '@/lib/produkt'

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
</script>

<template>
  <template v-if="kopf !== null && produkt !== undefined && zurueckZiel !== null">
    <RouterLink v-slot="{ href, navigate }" custom :to="zurueckZiel">
      <wa-button class="om-produkt__zurueck" appearance="plain" :href="href" @click="navigate">
        ← Zurück zu {{ kopf.zurueckText }}
      </wa-button>
    </RouterLink>

    <PageIntro :titel="produkt.name" :beschreibung="kopfzeile" />

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
            <dt>Bindungsgrad</dt>
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
