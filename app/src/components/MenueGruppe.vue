<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, useId, watch } from 'vue'
import { useRoute, type RouteLocationRaw } from 'vue-router'

import type { MenueGruppe, MenueLink } from '@/lib/menue'
import { listenVersatz, randAusMaximalbreite } from '@/lib/menueVersatz'

// Disclosure-Gruppe im Kopfmenü (D-19): ein Schalter mit `aria-expanded` und eine Linkliste
// aus echten Links. Bewusst keine Menü-Rolle und kein `wa-dropdown`: es ist Seitennavigation,
// keine Anwendungsmenü-Semantik (UI-SPEC „Bewusst nicht verwendet“). Die Liste fängt den Fokus
// nicht ein; Tab verlässt sie in natürlicher Reihenfolge.
const props = defineProps<{
  gruppe: MenueGruppe
  /** Linkziel eines Eintrags; `App.vue` hängt bei `mitJahr` das gewählte Jahr an (D-10). */
  ziel: (link: MenueLink) => RouteLocationRaw
}>()

const route = useRoute()
const listenId = useId()
const offen = ref(false)
const wurzel = ref<HTMLElement | null>(null)
const schalter = ref<HTMLButtonElement | null>(null)
const liste = ref<HTMLUListElement | null>(null)
/** Horizontale Verschiebung der Liste in px, damit sie am Fensterrand nicht abgeschnitten wird. */
const versatz = ref(0)

/** Ist ein Untereintrag die aktuelle Seite? Dann trägt der Schalter den aktiven Stil. */
const aktiv = computed(() => props.gruppe.eintraege.some((link) => link.name === route.name))

function schliesse() {
  offen.value = false
}

/**
 * Hält die geöffnete Liste innerhalb des Fensters (`max-width` der Liste legt den Rand fest).
 * Misst einmal und weist den absoluten Versatz zu, unabhängig vom vorherigen (WR-01): das
 * gemessene Rechteck trägt den inline gesetzten Versatz (`style.left`) auch dann, wenn Vue
 * einen neueren reaktiven Wert noch nicht geschrieben hat.
 */
function positioniere() {
  const element = liste.value
  if (element === null) {
    return
  }
  const breite = document.documentElement.clientWidth
  const rand = randAusMaximalbreite(breite, getComputedStyle(element).maxWidth)
  const angewandt = parseFloat(element.style.left)
  const kasten = element.getBoundingClientRect()
  versatz.value = listenVersatz({
    links: kasten.left,
    rechts: kasten.right,
    angewandterVersatz: Number.isNaN(angewandt) ? 0 : angewandt,
    fensterbreite: breite,
    rand,
  })
}

async function wechsle() {
  offen.value = !offen.value
  if (offen.value) {
    await nextTick()
    positioniere()
  }
}

// Escape schließt und gibt den Fokus an den Schalter zurück (T-06-05: kein Fokusfänger).
function beiTaste(ereignis: KeyboardEvent) {
  if (ereignis.key === 'Escape' && offen.value) {
    ereignis.stopPropagation()
    schliesse()
    schalter.value?.focus()
  }
}

// Verlässt der Fokus die Gruppe (Tab), schließt die Liste. Ein `relatedTarget` von `null`
// (Klick auf Nicht-Fokussierbares, Fensterwechsel) fängt `beiZeigerAussen` bzw. der nächste
// Fokus ab; es zu schließen würde den Schalter in Safari und Firefox beim Klick sofort wieder öffnen.
function beiFokusVerlust(ereignis: FocusEvent) {
  const ziel = ereignis.relatedTarget
  if (ziel instanceof Node && wurzel.value !== null && !wurzel.value.contains(ziel)) {
    schliesse()
  }
}

function beiZeigerAussen(ereignis: PointerEvent) {
  if (
    offen.value &&
    ereignis.target instanceof Node &&
    wurzel.value !== null &&
    !wurzel.value.contains(ereignis.target)
  ) {
    schliesse()
  }
}

function beiGroessenaenderung() {
  if (offen.value) {
    positioniere()
  }
}

// Ein Seitenwechsel schließt die Liste; den Fokus übernimmt der Router (Überschrift der Seite).
watch(
  () => route.fullPath,
  () => {
    schliesse()
  },
)

onMounted(() => {
  document.addEventListener('pointerdown', beiZeigerAussen)
  window.addEventListener('resize', beiGroessenaenderung)
})
onBeforeUnmount(() => {
  document.removeEventListener('pointerdown', beiZeigerAussen)
  window.removeEventListener('resize', beiGroessenaenderung)
})
</script>

<template>
  <div
    v-if="gruppe.eintraege.length > 0"
    ref="wurzel"
    class="om-menuegruppe"
    @keydown="beiTaste"
    @focusout="beiFokusVerlust"
  >
    <button
      ref="schalter"
      type="button"
      class="om-menuegruppe__schalter"
      :class="{ 'om-menuegruppe__schalter--aktiv': aktiv }"
      :aria-expanded="offen ? 'true' : 'false'"
      :aria-controls="listenId"
      :aria-current="aktiv ? 'true' : undefined"
      @click="wechsle"
    >
      {{ gruppe.text }}
      <!-- Der Pfeil ist inline gezeichnet: keine Icon-Datei, kein zusätzlicher Request (T-06-06). -->
      <svg
        class="om-menuegruppe__pfeil"
        viewBox="0 0 16 16"
        width="16"
        height="16"
        aria-hidden="true"
        focusable="false"
      >
        <path
          d="M3 6l5 5 5-5"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </svg>
    </button>

    <ul
      v-show="offen"
      :id="listenId"
      ref="liste"
      class="om-menuegruppe__liste"
      :style="{ left: `${versatz}px` }"
    >
      <li v-for="link in gruppe.eintraege" :key="link.name">
        <RouterLink :to="ziel(link)" @click="schliesse">{{ link.text }}</RouterLink>
      </li>
    </ul>
  </div>
</template>

<style scoped>
.om-menuegruppe {
  position: relative;
}

.om-menuegruppe__schalter {
  display: inline-flex;
  align-items: center;
  gap: var(--wa-space-2xs);
  min-height: 44px;
  padding: 0;
  border: 0;
  background: none;
  color: var(--wa-color-text-link);
  font: inherit;
  cursor: pointer;
}

/* Eine aktive Unterseite fällt nie nur durch die Farbe auf: Gewicht und Unterstreichung kommen
   dazu (wie beim aktiven Menülink). */
.om-menuegruppe__schalter--aktiv {
  color: var(--wa-color-brand-40);
  font-weight: var(--wa-font-weight-bold);
  text-decoration: underline;
  text-underline-offset: 0.25em;
}

.om-menuegruppe__pfeil {
  flex: none;
}

.om-menuegruppe__schalter[aria-expanded='true'] .om-menuegruppe__pfeil {
  transform: rotate(180deg);
}

/* Die Liste überdeckt den Inhalt; die Kopfzeile liegt selbst über dem Seiteninhalt. Das Öffnen
   bleibt ohne Animation (UI-SPEC Bewegung). */
.om-menuegruppe__liste {
  position: absolute;
  top: 100%;
  left: 0;
  z-index: 1;
  box-sizing: border-box;
  min-width: 224px;
  max-width: calc(100vw - 2 * var(--wa-space-m));
  margin: 0;
  padding: var(--wa-space-xs);
  list-style: none;
  background: var(--wa-color-surface-default);
  border: 1px solid var(--wa-color-surface-border);
  border-radius: var(--wa-border-radius-m);
  box-shadow: var(--wa-shadow-m);
}

.om-menuegruppe__liste a {
  display: flex;
  align-items: center;
  min-height: 44px;
  padding-inline: var(--wa-space-xs);
  text-decoration: none;
  overflow-wrap: anywhere;
}

.om-menuegruppe__liste a[aria-current='page'] {
  color: var(--wa-color-brand-40);
  font-weight: var(--wa-font-weight-bold);
  text-decoration: underline;
  text-underline-offset: 0.25em;
}
</style>
