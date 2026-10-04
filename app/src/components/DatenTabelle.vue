<script setup lang="ts">
import { computed, watchEffect } from 'vue'
import { EURO_OPTIONEN, KEIN_WERT } from '@/charts/format'
import type { DatenSpalte, DatenZeile } from '@/components/datenTabelle'

const props = withDefaults(
  defineProps<{
    beschriftung?: string
    spalten?: readonly DatenSpalte[]
    zeilen?: readonly DatenZeile[]
    laedt?: boolean
    /** Überschrift des Leerzustands (UI-SPEC Copywriting). */
    leerTitel?: string
    /** Erklärtext des Leerzustands (UI-SPEC Copywriting). */
    leerText?: string
    /** Quellen-/Hinweiszeile unter der Tabelle (Caption-Stil). */
    fussnote?: string
  }>(),
  {
    leerTitel: 'Keine Einzelwerte',
    leerText:
      'Der Haushaltsplan nennt hier keine Aufschlüsselung. Wähle ein anderes Jahr oder öffne die Tabelle.',
  },
)

defineSlots<{
  /**
   * Eigener Zelleninhalt (Schaltflächen, Links, Etiketten). Die Zelle selbst
   * (`th`/`td`) bleibt Eigentum der Tabelle, damit ihr Scoped-CSS greift.
   */
  zelle?(props: { zeile: DatenZeile; spalte: DatenSpalte; wert: string | number | null }): unknown
  /**
   * Zusatz hinter dem Inhalt der ersten Zelle einer Zeile (z. B. das Etikett „berechnet“),
   * ohne den Standardinhalt der Zelle zu ersetzen.
   */
  zeilenzusatz?(props: { zeile: DatenZeile }): unknown
  default?(): unknown
}>()

const istDatenModus = computed(() => props.zeilen !== undefined)
const istLeer = computed(() => istDatenModus.value && (props.zeilen?.length ?? 0) === 0)

// `spalten` ist unabhängig von `zeilen` optional, wird im Datenmodus aber
// zwingend für Kopf- und Datenzellen benötigt. Ohne `spalten` rendert die
// Tabelle still eine leere Kopf-/Datenzeile ohne <th>/<td> — daher ein
// lautes Dev-Warning statt eines unsichtbaren Fehlers.
if (import.meta.env.DEV) {
  watchEffect(() => {
    if (istDatenModus.value && !props.spalten?.length) {
      console.warn('DatenTabelle: `zeilen` wurde ohne `spalten` übergeben.')
    }
  })
}

/**
 * Prüft zur Laufzeit, dass ein Zellwert tatsächlich eine Zahl ist, bevor er
 * an `<wa-format-number>` übergeben wird. `DatenZeile` erlaubt
 * `string | number | null` ohne Bezug zu `DatenSpalte.art`, daher schlägt
 * eine Typinkonsistenz zwischen Spaltendefinition und Daten hier laut fehl,
 * statt NaN/Garbage stillschweigend zu rendern.
 */
function alsZahl(wert: string | number | null | undefined): number {
  if (typeof wert !== 'number') {
    throw new TypeError(`Erwartete Zahl für numerische Spalte, erhalten: ${typeof wert}`)
  }
  return wert
}
</script>

<template>
  <div
    class="om-tabelle-rahmen"
    :role="beschriftung ? 'region' : undefined"
    :aria-label="beschriftung"
    :tabindex="beschriftung ? 0 : undefined"
  >
    <div v-if="laedt" class="om-tabelle-skeleton">
      <wa-skeleton effect="sheen"></wa-skeleton>
      <wa-skeleton effect="sheen"></wa-skeleton>
      <wa-skeleton effect="sheen"></wa-skeleton>
    </div>
    <div v-else-if="istLeer" class="om-tabelle-zustand">
      <h3>{{ leerTitel }}</h3>
      <p>{{ leerText }}</p>
    </div>
    <table v-else-if="istDatenModus" class="om-tabelle">
      <caption v-if="beschriftung" class="om-visually-hidden">
        {{
          beschriftung
        }}
      </caption>
      <thead>
        <tr>
          <th v-for="spalte in spalten" :key="spalte.schluessel" scope="col">
            {{ spalte.titel }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(zeile, index) in zeilen" :key="index">
          <template v-for="(spalte, spaltenIndex) in spalten" :key="spalte.schluessel">
            <th v-if="spaltenIndex === 0" scope="row" class="om-tabelle__label">
              <slot
                name="zelle"
                :zeile="zeile"
                :spalte="spalte"
                :wert="zeile[spalte.schluessel] ?? null"
              >
                <template v-if="zeile[spalte.schluessel] === null">
                  <span aria-hidden="true">{{ KEIN_WERT }}</span>
                  <span class="om-visually-hidden">kein Wert</span>
                </template>
                <template v-else>{{ zeile[spalte.schluessel] }}</template>
              </slot>
              <slot name="zeilenzusatz" :zeile="zeile" />
            </th>
            <td v-else :class="{ 'om-zahl': spalte.art !== 'text' }">
              <slot
                name="zelle"
                :zeile="zeile"
                :spalte="spalte"
                :wert="zeile[spalte.schluessel] ?? null"
              >
                <template v-if="zeile[spalte.schluessel] === null">
                  <span aria-hidden="true">{{ KEIN_WERT }}</span>
                  <span class="om-visually-hidden">kein Wert</span>
                </template>
                <template v-else-if="spalte.art === 'text'">{{
                  zeile[spalte.schluessel]
                }}</template>
                <wa-format-number
                  v-else-if="spalte.art === 'euro'"
                  lang="de"
                  type="currency"
                  :currency="EURO_OPTIONEN.currency"
                  :maximum-fraction-digits="EURO_OPTIONEN.maximumFractionDigits"
                  :value="alsZahl(zeile[spalte.schluessel])"
                ></wa-format-number>
                <wa-format-number
                  v-else-if="spalte.art === 'zahl'"
                  lang="de"
                  type="decimal"
                  maximum-fraction-digits="0"
                  :value="alsZahl(zeile[spalte.schluessel])"
                ></wa-format-number>
                <wa-format-number
                  v-else-if="spalte.art === 'dezimal'"
                  lang="de"
                  type="decimal"
                  maximum-fraction-digits="2"
                  :value="alsZahl(zeile[spalte.schluessel])"
                ></wa-format-number>
                <wa-format-number
                  v-else-if="spalte.art === 'prozent'"
                  lang="de"
                  type="percent"
                  maximum-fraction-digits="1"
                  :value="alsZahl(zeile[spalte.schluessel])"
                ></wa-format-number>
              </slot>
            </td>
          </template>
        </tr>
      </tbody>
    </table>
    <table v-else class="om-tabelle">
      <caption v-if="beschriftung">
        {{
          beschriftung
        }}
      </caption>
      <slot />
    </table>
    <p v-if="fussnote && !laedt && !istLeer" class="om-tabelle__fussnote">{{ fussnote }}</p>
  </div>
</template>

<style scoped>
.om-tabelle-rahmen {
  overflow-x: auto;
}

.om-tabelle-skeleton {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-xs);
}

.om-tabelle-zustand {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--wa-space-xs);
  text-align: center;
  color: var(--wa-color-text-quiet);
  padding: var(--wa-space-m);
}

.om-tabelle-zustand h3 {
  margin: 0;
  font-size: var(--wa-font-size-l);
  font-weight: var(--wa-font-weight-bold);
}

.om-tabelle-zustand p {
  margin: 0;
  max-width: 32rem;
}

.om-tabelle {
  width: 100%;
  border-collapse: collapse;
}

.om-tabelle th,
.om-tabelle td {
  padding: var(--wa-space-xs) var(--wa-space-s);
  text-align: left;
}

.om-tabelle thead th {
  font-size: var(--wa-font-size-s);
  font-weight: var(--wa-font-weight-bold);
}

.om-tabelle tbody tr:nth-child(even) {
  background: var(--wa-color-surface-lowered);
}

.om-tabelle__fussnote {
  margin: var(--wa-space-xs) 0 0;
  font-size: var(--wa-font-size-s);
  font-weight: var(--wa-font-weight-normal);
  line-height: 1.5;
  color: var(--wa-color-text-quiet);
}

.om-tabelle__label {
  position: sticky;
  left: 0;
  background: var(--wa-color-surface-default);
  max-width: 16rem;
  hyphens: auto;
  overflow-wrap: break-word;
  font-weight: var(--wa-font-weight-normal);
}

.om-tabelle tbody tr:nth-child(even) .om-tabelle__label {
  background: var(--wa-color-surface-lowered);
}
</style>
