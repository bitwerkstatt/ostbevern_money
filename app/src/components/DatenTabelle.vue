<script setup lang="ts">
import { computed } from 'vue'
import { EURO_OPTIONEN } from '@/charts/format'
import type { DatenSpalte, DatenZeile } from '@/components/datenTabelle'

const props = defineProps<{
  beschriftung?: string
  spalten?: readonly DatenSpalte[]
  zeilen?: readonly DatenZeile[]
  laedt?: boolean
}>()

const istDatenModus = computed(() => props.zeilen !== undefined)
const istLeer = computed(() => istDatenModus.value && (props.zeilen?.length ?? 0) === 0)

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
      <h3>Noch keine Daten</h3>
      <p>
        Die Haushaltsdaten werden ab Phase 2 automatisch aus dem PDF erzeugt und erscheinen hier,
        sobald die Pipeline gelaufen ist.
      </p>
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
              {{ zeile[spalte.schluessel] }}
            </th>
            <td v-else :class="{ 'om-zahl': spalte.art !== 'text' }">
              <span v-if="zeile[spalte.schluessel] === null" class="om-visually-hidden"
                >kein Wert</span
              >
              <template v-else-if="spalte.art === 'text'">{{ zeile[spalte.schluessel] }}</template>
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
                v-else-if="spalte.art === 'prozent'"
                lang="de"
                type="percent"
                maximum-fraction-digits="1"
                :value="alsZahl(zeile[spalte.schluessel])"
              ></wa-format-number>
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
