<script setup lang="ts">
import { computed, nextTick, ref, useTemplateRef, watch } from 'vue'

import { bboxProzent, bildUrl, type AufgeloesterBeleg } from '@/lib/quelle'

// Bild einer PDF-Seite samt Zeilenmarkierung (D-02). Wird von der Seitenleiste nur gerendert,
// solange sie geöffnet ist (kein Vorabladen) und je Auslösung neu aufgebaut (`:key`).
const props = defineProps<{
  beleg: AufgeloesterBeleg
  /** Bezeichnung des Werts für die Bildbeschreibung. */
  bezeichnung: string
  /** `true`, sobald die Leiste vollständig geöffnet ist (`wa-after-show`). */
  angezeigt: boolean
}>()

const geladen = ref(false)
const fehler = ref(false)
const markierung = useTemplateRef<HTMLElement>('markierung')

const markiert = computed(() => props.beleg.bbox !== null && geladen.value && !fehler.value)
const prozent = computed(() =>
  props.beleg.bbox === null
    ? null
    : bboxProzent(props.beleg.bbox, props.beleg.breite, props.beleg.hoehe),
)

const markierungStil = computed(() => {
  const p = prozent.value
  return p === null
    ? {}
    : {
        left: `${String(p.links)}%`,
        top: `${String(p.oben)}%`,
        width: `${String(p.breite)}%`,
        height: `${String(p.hoehe)}%`,
      }
})

// Die Seitenbreite in Punkten kommt aus den Daten; die Anzeigebreite ist mindestens 1 px je
// Punkt (Querformat und 360 px scrollen waagerecht nur in diesem Rahmen).
const blattStil = computed(() => ({ '--om-seite-breite': `${String(props.beleg.breite)}px` }))
const platzhalterStil = computed(() => ({
  aspectRatio: `${String(props.beleg.breite)} / ${String(props.beleg.hoehe)}`,
}))

const altText = computed(() => {
  const basis = `Ausschnitt des Haushaltsplans, PDF-Seite ${String(props.beleg.pdfSeite)}.`
  return props.beleg.bbox === null
    ? basis
    : `${basis} Die markierte Zeile gehört zu: ${props.bezeichnung}.`
})

function beiLaden() {
  geladen.value = true
}

function beiFehler() {
  fehler.value = true
}

// Scrollen erst, wenn Bild und Leiste fertig sind: vorher ist die Markierung noch nicht
// gezeichnet bzw. die Leiste noch in Bewegung. Immer `auto` (nie weich, A11Y-02).
watch(
  [markiert, () => props.angezeigt],
  async ([istMarkiert, istAngezeigt]) => {
    if (!istMarkiert || !istAngezeigt) {
      return
    }
    await nextTick()
    markierung.value?.scrollIntoView({ block: 'center', inline: 'center', behavior: 'auto' })
  },
  { immediate: true, flush: 'post' },
)
</script>

<template>
  <div
    class="om-quelle-seite"
    role="region"
    :aria-label="`PDF-Seite ${beleg.pdfSeite} des Haushaltsplans`"
    :aria-busy="!geladen && !fehler ? 'true' : undefined"
    tabindex="0"
  >
    <wa-callout v-if="fehler" variant="warning" class="om-quelle-seite__fehler">
      <wa-icon slot="icon" name="triangle-exclamation" aria-hidden="true"></wa-icon>
      Die Seite konnte nicht geladen werden. Du findest sie im Original-PDF.
    </wa-callout>
    <div v-else class="om-quelle-seite__blatt" :style="blattStil">
      <wa-skeleton
        v-if="!geladen"
        effect="sheen"
        class="om-quelle-seite__platzhalter"
        :style="platzhalterStil"
      ></wa-skeleton>
      <img
        v-show="geladen"
        class="om-quelle-seite__bild"
        :src="bildUrl(beleg.bild)"
        :alt="altText"
        :width="Math.round(2 * beleg.breite)"
        :height="Math.round(2 * beleg.hoehe)"
        @load="beiLaden"
        @error="beiFehler"
      />
      <span
        v-if="markiert"
        ref="markierung"
        class="om-quelle-seite__markierung"
        :style="markierungStil"
        aria-hidden="true"
      ></span>
    </div>
  </div>
</template>

<style scoped>
.om-quelle-seite {
  position: relative;
  overflow-x: auto;
  border: 1px solid var(--wa-color-surface-border);
}

.om-quelle-seite:focus-visible {
  outline: 2px solid var(--wa-color-focus);
  outline-offset: var(--wa-space-2xs);
}

/* Das Blatt ist mindestens 1 px je PDF-Punkt breit; die Markierung bezieht sich auf das Blatt,
   nicht auf den (kleineren) scrollenden Rahmen. */
.om-quelle-seite__blatt {
  position: relative;
  width: max(100%, var(--om-seite-breite));
}

.om-quelle-seite__bild {
  display: block;
  width: 100%;
  height: auto;
}

.om-quelle-seite__platzhalter {
  display: block;
  width: 100%;
}

.om-quelle-seite__markierung {
  position: absolute;
  box-sizing: border-box;
  min-height: 8px;
  outline: 2px solid var(--wa-color-brand-40);
  outline-offset: -2px;
  background: color-mix(in srgb, var(--wa-color-brand-60) 25%, transparent);
  pointer-events: none;
}

.om-quelle-seite__fehler {
  margin: var(--wa-space-m);
}
</style>
