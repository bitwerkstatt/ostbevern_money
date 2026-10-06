<script setup lang="ts">
import { computed } from 'vue'

import { useSchmalerBildschirm } from '@/lib/bildschirm'
import {
  ARTEN,
  ergebnisText,
  MASSNAHMEN_AUFGABENBEREICHE,
  useMassnahmenFilter,
} from '@/lib/investitionen'

// Wert der Auswahl „Alle“; kein Aufgabenbereichscode und keine Art heißt so.
const ALLE = 'alle'

const istSchmal = useSchmalerBildschirm()
const { filter, vorhaben, setzePb, setzeArt } = useMassnahmenFilter()

const pbWert = computed(() => filter.value.pb ?? ALLE)
const artWert = computed(() => filter.value.art ?? ALLE)

const artOptionen = computed(() => [
  { wert: ALLE, text: 'Alle' },
  ...ARTEN.map((a) => ({ wert: a.art, text: a.text })),
])

const ergebnis = computed(() => ergebnisText(vorhaben.value))

// Das Ereignis kommt vom Web-Awesome-Host (Select bzw. Gruppe); der neue Wert steht in dessen
// `value`. Die Bibliothek prüft ihn gegen die Allowlist, der Fokus bleibt auf dem Steuerelement.
function wertAus(ereignis: Event): string | null {
  const wert = (ereignis.currentTarget as { value?: unknown } | null)?.value
  return typeof wert === 'string' ? wert : null
}

function beiPb(ereignis: Event) {
  const wert = wertAus(ereignis)
  if (wert !== null) {
    setzePb(wert === ALLE ? null : wert)
  }
}

function beiArt(ereignis: Event) {
  const wert = wertAus(ereignis)
  if (wert === null) {
    return
  }
  const art = ARTEN.find((a) => a.art === wert)
  if (wert === ALLE) {
    setzeArt(null)
  } else if (art !== undefined) {
    setzeArt(art.art)
  }
}
</script>

<template>
  <div class="om-massnahmen-filter">
    <div class="om-massnahmen-filter__steuerung">
      <wa-select
        class="om-massnahmen-filter__pb"
        label="Aufgabenbereich"
        :value="pbWert"
        @change="beiPb"
      >
        <wa-option :value="ALLE">Alle Aufgabenbereiche</wa-option>
        <wa-option
          v-for="bereich in MASSNAHMEN_AUFGABENBEREICHE"
          :key="bereich.code"
          :value="bereich.code"
        >
          {{ bereich.name }}
        </wa-option>
      </wa-select>
      <wa-select
        v-if="istSchmal"
        class="om-massnahmen-filter__art-select"
        label="Art"
        :value="artWert"
        @change="beiArt"
      >
        <wa-option v-for="option in artOptionen" :key="option.wert" :value="option.wert">
          {{ option.text }}
        </wa-option>
      </wa-select>
      <wa-radio-group
        v-else
        class="om-massnahmen-filter__art"
        label="Art"
        orientation="horizontal"
        :value="artWert"
        @change="beiArt"
      >
        <wa-radio
          v-for="option in artOptionen"
          :key="option.wert"
          appearance="button"
          :value="option.wert"
        >
          {{ option.text }}
        </wa-radio>
      </wa-radio-group>
    </div>
    <p class="om-massnahmen-filter__ergebnis" aria-live="polite">{{ ergebnis }}</p>
  </div>
</template>

<style scoped>
.om-massnahmen-filter {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-s);
}

.om-massnahmen-filter__steuerung {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-m);
}

@media (min-width: 700px) {
  .om-massnahmen-filter__steuerung {
    flex-direction: row;
    flex-wrap: wrap;
    align-items: flex-start;
    gap: var(--wa-space-xl);
  }
}

.om-massnahmen-filter__pb,
.om-massnahmen-filter__art-select {
  inline-size: 100%;
}

@media (min-width: 700px) {
  .om-massnahmen-filter__pb {
    inline-size: 22rem;
  }
}

.om-massnahmen-filter wa-radio-group::part(form-control-label),
.om-massnahmen-filter wa-select::part(form-control-label) {
  font-size: var(--wa-font-size-s);
  font-weight: var(--wa-font-weight-bold);
  line-height: var(--wa-line-height-condensed);
}

/* Mindest-Trefferfläche 44 px (WCAG 2.5.5, UI-SPEC Spacing-Ausnahmen). */
.om-massnahmen-filter wa-radio::part(control),
.om-massnahmen-filter wa-select::part(combobox),
.om-massnahmen-filter wa-option::part(base) {
  min-height: 44px;
}

.om-massnahmen-filter wa-radio::part(label) {
  white-space: nowrap;
}

/* Lange Aufgabenbereichsnamen brechen um, statt abgeschnitten zu werden (UI-SPEC E7 long-text). */
.om-massnahmen-filter wa-option::part(label) {
  white-space: normal;
}

.om-massnahmen-filter__ergebnis {
  margin: 0;
  font-size: var(--wa-font-size-s);
  color: var(--wa-color-text-quiet);
}
</style>
