<script setup lang="ts">
import { computed } from 'vue'

import { datum, jahr as formatiereJahr, KEIN_WERT, vzae, zahl } from '@/charts/format'
import ChartCard from '@/components/ChartCard.vue'
import GlossarBegriff from '@/components/GlossarBegriff.vue'
import KennzahlKachel from '@/components/KennzahlKachel.vue'
import PageIntro from '@/components/PageIntro.vue'
import StellenNachBereich from '@/components/StellenNachBereich.vue'
import StellenNachGruppe from '@/components/StellenNachGruppe.vue'
import StellenNachTeil from '@/components/StellenNachTeil.vue'
import WertartEtikett from '@/components/WertartEtikett.vue'
import { haushalt, stellenplan } from '@/data/daten'
import { wertartFuerJahr } from '@/lib/jahr'
import {
  alsVzae,
  differenzText,
  nachwuchs,
  stellenNachGruppe,
  stellenSummen,
  TEILE,
} from '@/lib/stellen'

// Die Seite zeigt das Haushaltsjahr, ohne Jahr-Umschalter (UI-SPEC Routes). Jahr und Wertart
// kommen aus den Daten.
const haushaltsjahr = formatiereJahr(haushalt.haushaltsjahr)
const vorjahr = formatiereJahr(stellenplan.haushaltsjahr - 1)
const wertart = wertartFuerJahr(haushalt.haushaltsjahr)
const lead = `Hier siehst du, wie viele Stellen die Gemeinde ${haushaltsjahr} vorsieht, wie viele davon besetzt sind und in welchen Bereichen sie liegen.`

const summen = stellenSummen()
const personen = nachwuchs()

/** „PDF-Seite 284“ bzw. „PDF-Seiten 284, 285, 286“. */
function seitenText(seiten: readonly number[]): string {
  return `${seiten.length === 1 ? 'PDF-Seite' : 'PDF-Seiten'} ${seiten.join(', ')}`
}

/** Wert in VZÄ für eine Kachel; ohne Wert „–“, nie 0 (UI-SPEC E10 empty). */
function kachelWert(hundertstel: number | null): string {
  return hundertstel === null ? KEIN_WERT : `${vzae(alsVzae(hundertstel))} VZÄ`
}

interface StellenKachel {
  schluessel: string
  bezeichnung: string
  wert: string
  zeile: string
  berechnet: boolean
}

/** Zeile unter dem Wert: optional die berechnete Differenz, dann Quelle mit PDF-Seiten. */
function kachelZeile(quelle: string, differenz: string | null): string {
  const beleg = `${quelle} · ${seitenText(summen.pdfSeiten)}`
  return differenz === null ? beleg : `${differenz} · ${beleg}`
}

const stichtagText = summen.stichtag === null ? null : datum(summen.stichtag)

// Die Differenzen in Kachel 1 und 3 sind berechnet (nicht im PDF gedruckt) und tragen das
// Etikett; fehlt ein Vergleichswert, entfällt die Differenzzeile.
const diffVorjahr = differenzText(summen.haushaltsjahr, summen.vorjahr)
const diffBesetzt = differenzText(summen.besetzt, summen.haushaltsjahr)

const kacheln: StellenKachel[] = [
  {
    schluessel: 'haushaltsjahr',
    bezeichnung: `Stellen ${haushaltsjahr}`,
    wert: kachelWert(summen.haushaltsjahr),
    zeile: kachelZeile(
      `Stellenplan ${haushaltsjahr}`,
      diffVorjahr === null ? null : `${diffVorjahr} gegenüber Stellen ${vorjahr}`,
    ),
    berechnet: diffVorjahr !== null,
  },
  {
    schluessel: 'vorjahr',
    bezeichnung: `Stellen ${vorjahr}`,
    wert: kachelWert(summen.vorjahr),
    zeile: kachelZeile(`Stellenplan ${vorjahr}`, null),
    berechnet: false,
  },
  {
    schluessel: 'besetzt',
    bezeichnung: stichtagText === null ? 'Besetzte Stellen' : `Besetzt am ${stichtagText}`,
    wert: kachelWert(summen.besetzt),
    zeile: kachelZeile(
      'Stellenplan',
      diffBesetzt === null ? null : `${diffBesetzt} gegenüber Stellen ${haushaltsjahr}`,
    ),
    berechnet: diffBesetzt !== null,
  },
]

/** „1 Person“ bzw. „5 Personen“. */
function personenText(anzahl: number): string {
  return `${zahl(anzahl)} ${anzahl === 1 ? 'Person' : 'Personen'}`
}

// Fehlen Personenzahlen für ein Jahr, nennt der Satz nur das vorhandene Jahr (UI-SPEC E10
// partial); Nachwuchskräfte sind nie Stellen.
const nachwuchsSatz = computed(() => {
  const { vorjahr: vorher, haushaltsjahr: dann } = personen
  const beleg = personen.pdfSeiten.length === 0 ? '' : ` (${seitenText(personen.pdfSeiten)})`
  if (vorher !== null && dann !== null) {
    return `Nachwuchskräfte zählen nicht als Stellen. Im Haushaltsplan stehen ${personenText(vorher)} für ${vorjahr} und ${zahl(dann)} für ${haushaltsjahr}.${beleg}`
  }
  if (dann !== null) {
    return `Nachwuchskräfte zählen nicht als Stellen. Im Haushaltsplan stehen ${personenText(dann)} für ${haushaltsjahr}.${beleg}`
  }
  if (vorher !== null) {
    return `Nachwuchskräfte zählen nicht als Stellen. Im Haushaltsplan stehen ${personenText(vorher)} für ${vorjahr}.${beleg}`
  }
  return null
})

const teilQuelle = `Stellenplan, ${seitenText(summen.pdfSeiten)}`

// Je Teil ein Abschnitt; Teile ohne Zeilen entfallen samt Überschrift (UI-SPEC E10 zero-one-many).
const gruppenTeile = TEILE.filter((teil) => stellenNachGruppe(teil.teil).length > 0)
const gruppenQuelle = `Stellenplan, ${seitenText(
  [
    ...new Set(gruppenTeile.flatMap((teil) => stellenNachGruppe(teil.teil).map((z) => z.pdfSeite))),
  ].sort((a, b) => a - b),
)}`
</script>

<template>
  <div class="om-stellenplan">
    <PageIntro titel="Wie viele Stellen hat die Verwaltung?" :beschreibung="lead">
      <WertartEtikett :wertart="wertart" />
    </PageIntro>

    <section class="om-stellenplan__abschnitt" aria-label="Die Stellen im Überblick">
      <ul class="om-stellenplan__raster" role="list">
        <li v-for="kachel in kacheln" :key="kachel.schluessel">
          <KennzahlKachel
            :bezeichnung="kachel.bezeichnung"
            :wert="kachel.wert"
            :zeile="kachel.zeile"
            :berechnet="kachel.berechnet"
          />
        </li>
      </ul>
    </section>

    <div class="om-stellenplan__abschnitt">
      <ChartCard titel="Stellen nach Teil des Stellenplans" :quelle="teilQuelle">
        <StellenNachTeil />
      </ChartCard>
    </div>

    <wa-callout variant="neutral" class="om-stellenplan__hinweis">
      <p v-if="nachwuchsSatz !== null">{{ nachwuchsSatz }}</p>
      <p>
        <GlossarBegriff schluessel="vzae">VZÄ</GlossarBegriff> steht für Vollzeitäquivalent. Zwei
        halbe Stellen zählen zusammen als eine volle Stelle.
      </p>
    </wa-callout>

    <div class="om-stellenplan__abschnitt">
      <ChartCard titel="Stellen und Personalaufwand nach Aufgabenbereich">
        <StellenNachBereich />
        <p class="om-stellenplan__hinweis-text">
          Den Aufwand je Stelle rechnen wir bewusst nicht aus, weil Stellen und Personalaufwand
          nicht deckungsgleich sind. Die Aufteilung nach Aufgabenbereich steht im Haushaltsplan nur
          für {{ haushaltsjahr }}.
        </p>
      </ChartCard>
    </div>

    <div v-if="gruppenTeile.length > 0" class="om-stellenplan__abschnitt">
      <ChartCard titel="Stellen nach Gruppe" :quelle="gruppenQuelle">
        <p class="om-stellenplan__text">
          Jede Stelle gehört zu einer Gruppe. Was
          <GlossarBegriff schluessel="entgeltgruppen"
            >Besoldungs-, Entgelt- und S-Gruppen</GlossarBegriff
          >
          bedeuten, steht im Glossar. Die Gruppen laufen in jedem Diagramm von der niedrigen zur
          hohen Gruppe.
        </p>
        <section
          v-for="teil in gruppenTeile"
          :key="teil.teil"
          class="om-stellenplan__gruppe"
          :aria-labelledby="`om-stellenplan-gruppe-${teil.teil}`"
        >
          <h3 :id="`om-stellenplan-gruppe-${teil.teil}`">{{ teil.gruppenTitel }}</h3>
          <StellenNachGruppe :teil="teil.teil" />
        </section>
      </ChartCard>
    </div>
  </div>
</template>

<style scoped>
.om-stellenplan {
  max-width: 72rem;
  margin-inline: auto;
}

.om-stellenplan__abschnitt {
  margin-block-end: var(--wa-space-xl);
  min-width: 0;
}

.om-stellenplan__raster {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: var(--wa-space-m);
  margin: 0;
  padding: 0;
  list-style: none;
}

.om-stellenplan__raster > li {
  min-width: 0;
}

.om-stellenplan__hinweis {
  display: block;
  margin-block-end: var(--wa-space-xl);
}

.om-stellenplan__hinweis p {
  margin: 0;
}

.om-stellenplan__hinweis p + p {
  margin-block-start: var(--wa-space-xs);
}

.om-stellenplan__text {
  margin: 0 0 var(--wa-space-m);
  line-height: var(--wa-line-height-normal);
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-stellenplan__gruppe + .om-stellenplan__gruppe {
  margin-block-start: var(--wa-space-l);
}

.om-stellenplan__gruppe h3 {
  margin: 0 0 var(--wa-space-s);
  font-size: var(--wa-font-size-m);
  font-weight: var(--wa-font-weight-bold);
  line-height: var(--wa-line-height-condensed);
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-stellenplan__hinweis-text {
  margin: var(--wa-space-m) 0 0;
  font-size: var(--wa-font-size-s);
  line-height: 1.5;
  color: var(--wa-color-text-quiet);
}

@media (min-width: 700px) {
  .om-stellenplan__raster {
    gap: var(--wa-space-l);
  }
}
</style>
