<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, useId, watch } from 'vue'
import { EURO_OPTIONEN, KEIN_WERT } from '@/charts/format'
import QuelleKnopf from '@/components/QuelleKnopf.vue'
import {
  rahmenAttribute,
  sichtbareSpalten,
  type DatenSpalte,
  type DatenZeile,
} from '@/components/datenTabelle'
import { findeBeleg } from '@/lib/quelle'

// Bewusste Abweichung von den Münster-Props (D-16, D-19): `beschriftung`, `spalten` und `zeilen`
// sind Pflicht, der Slot-Modus (Default-Slot mit eigener Tabelle) ist entfernt. Jede Tabelle der
// App ist eine Datentabelle; ohne Pflicht-Beschriftung gäbe es keinen Namen für den scrollbaren
// Rahmen (A11Y-01, A11Y-03). Die Slots `zelle` und `zeilenzusatz` bleiben.
const props = withDefaults(
  defineProps<{
    /** Name der Tabelle: wird zur unsichtbaren Caption und ist der einzige Ort des Namens. */
    beschriftung: string
    spalten: readonly DatenSpalte[]
    zeilen: readonly DatenZeile[]
    laedt?: boolean
    /** Überschrift des Leerzustands (UI-SPEC Copywriting). */
    leerTitel?: string
    /** Erklärtext des Leerzustands (UI-SPEC Copywriting). */
    leerText?: string
    /** Quellen-/Hinweiszeile unter der Tabelle (Caption-Stil). */
    fussnote?: string
    /**
     * Vorangestellter Teil der Bezeichnung des Quellen-Knopfes, wenn die erste Spalte allein den
     * Wert nicht benennt (z. B. nur das Jahr einer Zeitreihe): „Gewerbesteuer 2026“.
     */
    bezeichnungPraefix?: string
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
}>()

// Eine Spalte `art: 'quelle'` (Phase 7, D-01) erscheint nur, wenn mindestens eine Zeile einen
// auflösbaren Beleg hat; die Tabelle zeichnet ihre Zelle selbst (außerhalb des Slots `zelle`),
// damit auch Tabellen mit eigenem Zellen-Slot den Knopf ohne Slotänderung bekommen.
function hatBeleg(wert: string | number | null): boolean {
  return typeof wert === 'string' && findeBeleg(wert) !== null
}

const sichtbar = computed(() => sichtbareSpalten(props.spalten, props.zeilen, hatBeleg))

/**
 * Bezeichnung des Werts für den Namen des Knopfes: der Wert der ersten sichtbaren Spalte,
 * gegebenenfalls mit `bezeichnungPraefix` davor.
 */
function zeilenBezeichnung(zeile: DatenZeile): string {
  const erste = sichtbar.value[0]
  const wert = erste === undefined ? null : zeile[erste.schluessel]
  const text = wert === null || wert === undefined ? '' : String(wert)
  return [props.bezeichnungPraefix, text].filter((teil) => teil).join(' ')
}

function herleitungVon(zeile: DatenZeile, spalte: DatenSpalte): string | null {
  const wert = zeile[`${spalte.schluessel}Herleitung`]
  return typeof wert === 'string' ? wert : null
}
const istLeer = computed(() => props.zeilen.length === 0)

// Ein waagerecht scrollbarer Bereich muss per Tastatur erreichbar und benannt sein; eine
// Tabelle, die in die Breite passt, braucht das nicht (kein überflüssiger Tabstopp, keine
// Region ohne Not). Daher bekommt der Rahmen Fokus, Rolle und Namen nur gemeinsam und nur,
// solange der Inhalt einer gerenderten Tabelle breiter ist als der Rahmen (`rahmenAttribute`).
// Der Name kommt genau einmal: per `aria-labelledby` aus der Caption der Tabelle (D-20), kein
// `aria-label` daneben.
const captionId = useId()
const rahmen = ref<HTMLElement | null>(null)
const ueberlaeuft = ref(false)
let beobachter: ResizeObserver | undefined

function pruefeUeberlauf() {
  const element = rahmen.value
  ueberlaeuft.value = element !== null && element.scrollWidth > element.clientWidth
}

// Der Inhalt des Rahmens wechselt per v-if zwischen Skeleton, Leerzustand und Tabelle. Ein
// Element, das erst nach dem Mounten entsteht, würde sonst nie beobachtet; daher wird bei
// jedem Zweigwechsel neu beobachtet und der Überlauf sofort neu geprüft.
function beobachteInhalt() {
  beobachter?.disconnect()
  const element = rahmen.value
  if (element === null) {
    return
  }
  beobachter?.observe(element)
  for (const kind of Array.from(element.children)) {
    beobachter?.observe(kind)
  }
  pruefeUeberlauf()
}

onMounted(() => {
  if (typeof ResizeObserver !== 'undefined') {
    beobachter = new ResizeObserver(pruefeUeberlauf)
  }
  beobachteInhalt()
})

watch([() => props.laedt, istLeer], () => void nextTick(beobachteInhalt))

onBeforeUnmount(() => {
  beobachter?.disconnect()
})

// Nur eine gerenderte Tabelle trägt eine Caption, auf die der Rahmen verweisen kann.
const rahmenAttributeGebunden = computed(() =>
  rahmenAttribute(ueberlaeuft.value && !props.laedt && !istLeer.value, captionId),
)

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
  <div ref="rahmen" class="om-tabelle-rahmen" v-bind="rahmenAttributeGebunden">
    <div v-if="laedt" class="om-tabelle-skeleton">
      <wa-skeleton effect="sheen"></wa-skeleton>
      <wa-skeleton effect="sheen"></wa-skeleton>
      <wa-skeleton effect="sheen"></wa-skeleton>
    </div>
    <div v-else-if="istLeer" class="om-tabelle-zustand">
      <h3>{{ leerTitel }}</h3>
      <p>{{ leerText }}</p>
    </div>
    <table v-else class="om-tabelle">
      <caption :id="captionId" class="om-visually-hidden">
        {{
          beschriftung
        }}
      </caption>
      <thead>
        <tr>
          <th v-for="spalte in sichtbar" :key="spalte.schluessel" scope="col">
            {{ spalte.titel }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(zeile, index) in zeilen" :key="index">
          <template v-for="(spalte, spaltenIndex) in sichtbar" :key="spalte.schluessel">
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
            <td v-else-if="spalte.art === 'quelle'" class="om-tabelle__quelle">
              <QuelleKnopf
                v-if="hatBeleg(zeile[spalte.schluessel] ?? null)"
                :schluessel="String(zeile[spalte.schluessel])"
                :bezeichnung="zeilenBezeichnung(zeile)"
                variante="zeile"
                :herleitung="herleitungVon(zeile, spalte)"
              />
            </td>
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
    <p v-if="fussnote && !laedt && !istLeer" class="om-tabelle__fussnote">{{ fussnote }}</p>
  </div>
</template>

<style scoped>
/* `position: relative` macht den Rahmen zum Bezugsrahmen der absolut positionierten
   `om-visually-hidden`-Texte in den Zellen; sonst ragen sie über den Rahmen hinaus und die Seite
   scrollt bei 360 px waagerecht (A11Y-03, gemessen auf /investitionen). */
.om-tabelle-rahmen {
  position: relative;
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

.om-tabelle__quelle {
  white-space: nowrap;
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
