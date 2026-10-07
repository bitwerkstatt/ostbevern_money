<script setup lang="ts">
import { computed } from 'vue'

import { balkenHoehe, horizontaleBalkenOption, type BalkenZeile } from '@/charts/balken'
import { AUFWANDSART_FARBE } from '@/charts/echartsTheme'
import { betragMitHinweis, jahr as formatJahr, kurzMitHinweis } from '@/charts/format'
import BaseChart from '@/components/BaseChart.vue'
import ChartCard from '@/components/ChartCard.vue'
import DatenTabelle from '@/components/DatenTabelle.vue'
import EuroBetrag from '@/components/EuroBetrag.vue'
import type { DatenSpalte, DatenZeile } from '@/components/datenTabelle'
import { haushalt } from '@/data/daten'
import { useSchmalerBildschirm } from '@/lib/bildschirm'
import { wertartFuerJahr, wertartName } from '@/lib/jahr'
import {
  kitaZuschuesse,
  weitereZuschuesse,
  zusammen,
  type Zuschuss,
  type ZuschussGruppe,
  type ZuschussSumme,
} from '@/lib/zuschuesse'

// RAT-03, D-03: die Einzelzuschüsse aus dem Vorbericht in zwei Karten. Alle Beträge sind
// T€-Werte × 1000 und stehen deshalb als „rd.“ da (die Regel steht nur in `charts/format.ts`). Die Balken tragen `AUFWANDSART_FARBE`, nie
// Produktbereichsfarben (UI-SPEC).

interface GruppeAnsicht {
  schluessel: string
  /** Überschrift der Quellgruppe; leer, wenn die Karte nur eine Gruppe zeigt. */
  titel: string
  quelle: string
  /** Summe der Gruppe; `berechnet` steuert das Etikett (D-12, TXT-05); `null` ohne einen Wert. */
  zusammen: ZuschussSumme | null
  zeilen: BalkenZeile[]
  tabelle: DatenZeile[]
  beschriftung: string
}

interface KarteAnsicht {
  schluessel: string
  titel: string
  beschreibung: string
  gruppen: GruppeAnsicht[]
}

const istSchmal = useSchmalerBildschirm()

const wertartText = `${wertartName(wertartFuerJahr(haushalt.haushaltsjahr))} ${formatJahr(haushalt.haushaltsjahr)}`

const spalten: DatenSpalte[] = [
  { schluessel: 'name', titel: 'Empfänger', art: 'text' },
  { schluessel: 'betrag', titel: `Zuschuss (${wertartText})`, art: 'text' },
  { schluessel: 'quelle', titel: 'Quelle', art: 'quelle' },
]

function seitenText(seiten: readonly number[]): string {
  const wort = seiten.length === 1 ? 'PDF-Seite' : 'PDF-Seiten'
  return `${wort} ${seiten.join(', ')}`
}

/** Größter Wert oben, Zeilen ohne Wert ans Ende (sie bleiben als „–“ stehen, nie als 0). */
function absteigend(posten: readonly Zuschuss[]): Zuschuss[] {
  return [...posten].sort((a, b) => (b.wert ?? -1) - (a.wert ?? -1))
}

/** Alle Vorberichtswerte sind T€ × 1000, also immer „rd.“; ohne Wert bleibt die Zelle leer. */
function betragText(wert: number | null): string | null {
  return wert === null ? null : betragMitHinweis(wert, true)
}

function gruppeAnsicht(
  schluessel: string,
  titel: string,
  quellenName: string,
  gruppe: ZuschussGruppe,
  beschriftung: string,
): GruppeAnsicht | null {
  if (gruppe.posten.length === 0) {
    return null
  }
  const posten = absteigend(gruppe.posten)
  return {
    schluessel,
    titel,
    quelle: `Quelle: ${quellenName}, ${seitenText(gruppe.pdfSeiten)}`,
    zusammen: zusammen(gruppe),
    zeilen: posten.map((p) => ({
      schluessel: p.schluessel,
      name: p.name,
      wert: p.wert,
      label: p.wert === null ? '' : kurzMitHinweis(p.wert, true),
    })),
    tabelle: posten.map((p) => ({
      name: p.name,
      betrag: betragText(p.wert),
      quelle: p.beleg,
    })),
    beschriftung,
  }
}

function nichtLeer<T>(wert: T | null): wert is T {
  return wert !== null
}

/**
 * Die gedruckte Kita-Summe steht in der Beschreibung ohne Etikett. Wäre sie berechnet, stünde sie
 * dort als Fließtext ohne Etikett; dann trägt die Zeile „Zusammen“ im Kartenkörper das Etikett.
 */
function kitaBeschreibung(summe: ZuschussSumme | null): string {
  return summe !== null && !summe.berechnet
    ? `Zusammen ${betragMitHinweis(summe.wert, true)}`
    : 'Zuschuss je Einrichtung.'
}

const karten = computed<KarteAnsicht[]>(() => {
  const kita = gruppeAnsicht(
    'kita',
    '',
    'Vorbericht, Zuschüsse an Kindertageseinrichtungen',
    kitaZuschuesse(),
    'Zuschüsse an Kindertagesstätten',
  )
  const weitere = weitereZuschuesse()
  const weitereGruppen = [
    gruppeAnsicht(
      'transfer',
      'Zuschüsse aus den Transferaufwendungen',
      'Vorbericht, Transferaufwendungen',
      weitere.transfer,
      'Weitere Zuschüsse aus den Transferaufwendungen',
    ),
    gruppeAnsicht(
      'lfd',
      'Zuschüsse für laufende Zwecke',
      'Vorbericht, Zuschüsse für laufende Zwecke',
      weitere.lfdZwecke,
      'Weitere Zuschüsse für laufende Zwecke',
    ),
  ].filter(nichtLeer)

  const liste: KarteAnsicht[] = []
  if (kita !== null) {
    liste.push({
      schluessel: 'kita',
      titel: 'Kindertagesstätten',
      beschreibung: kitaBeschreibung(kita.zusammen),
      gruppen: [kita],
    })
  }
  if (weitereGruppen.length > 0) {
    liste.push({
      schluessel: 'weitere',
      titel: 'Weitere Zuschüsse',
      beschreibung:
        'Zuschüsse, die der Vorbericht einzeln nennt, außerhalb der Kindertagesstätten.',
      gruppen: weitereGruppen,
    })
  }
  return liste
})

function option(gruppe: GruppeAnsicht) {
  return horizontaleBalkenOption(gruppe.zeilen, {
    farbe: AUFWANDSART_FARBE,
    wertartText,
    schmal: istSchmal.value,
  })
}

function beschreibung(gruppe: GruppeAnsicht): string {
  return `Balkendiagramm ${gruppe.beschriftung}. Dieselben Werte stehen in der Tabelle darunter.`
}
</script>

<template>
  <section class="om-zuschuesse" aria-labelledby="om-zuschuesse-titel">
    <h2 id="om-zuschuesse-titel" class="om-zuschuesse__titel">Einzelne Zuschüsse im Vorbericht</h2>
    <div class="om-zuschuesse__karten">
      <ChartCard
        v-for="karte in karten"
        :key="karte.schluessel"
        :titel="karte.titel"
        :beschreibung="karte.beschreibung"
      >
        <div v-for="gruppe in karte.gruppen" :key="gruppe.schluessel" class="om-zuschuesse__gruppe">
          <h3 v-if="gruppe.titel" class="om-zuschuesse__untertitel">{{ gruppe.titel }}</h3>
          <p
            v-if="gruppe.zusammen !== null && (gruppe.titel || gruppe.zusammen.berechnet)"
            class="om-zuschuesse__zeile"
          >
            Zusammen
            <EuroBetrag
              :wert="gruppe.zusammen.wert"
              gerundet
              :berechnet="gruppe.zusammen.berechnet"
            />
          </p>
          <p class="om-zuschuesse__zeile om-zuschuesse__zeile--leise">{{ gruppe.quelle }}</p>
          <BaseChart
            :option="option(gruppe)"
            :hoehe="balkenHoehe(gruppe.zeilen.length)"
            :beschreibung="beschreibung(gruppe)"
          />
          <wa-details summary="Tabelle anzeigen" class="om-zuschuesse__tabelle">
            <DatenTabelle
              :beschriftung="gruppe.beschriftung"
              :spalten="spalten"
              :zeilen="gruppe.tabelle"
            />
          </wa-details>
        </div>
      </ChartCard>
    </div>
  </section>
</template>

<style scoped>
.om-zuschuesse {
  margin-block-start: var(--wa-space-xl);
  min-width: 0;
}

.om-zuschuesse__titel {
  margin: 0 0 var(--wa-space-m);
  font-size: var(--wa-font-size-l);
  font-weight: var(--wa-font-weight-bold);
  line-height: var(--wa-line-height-condensed);
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-zuschuesse__karten {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: var(--wa-space-m);
  align-items: start;
}

.om-zuschuesse__gruppe {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-s);
  min-width: 0;
}

.om-zuschuesse__gruppe + .om-zuschuesse__gruppe {
  margin-block-start: var(--wa-space-l);
}

.om-zuschuesse__untertitel {
  margin: 0;
  font-size: var(--wa-font-size-l);
  font-weight: var(--wa-font-weight-bold);
  line-height: var(--wa-line-height-condensed);
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-zuschuesse__zeile {
  margin: 0;
  line-height: var(--wa-line-height-normal);
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-zuschuesse__zeile--leise {
  font-size: var(--wa-font-size-s);
  color: var(--wa-color-text-quiet);
}

@media (min-width: 900px) {
  .om-zuschuesse__karten {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: var(--wa-space-l);
  }
}
</style>
