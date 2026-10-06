<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import QuelleSeite from '@/components/QuelleSeite.vue'
import { useSchmalerBildschirm } from '@/lib/bildschirm'
import {
  belegHinweis,
  findeBeleg,
  fokusNachSchliessen,
  originalSeitenUrl,
  schliesseQuelle,
  useQuelle,
} from '@/lib/quelle'

// Die eine globale Quell-Seitenleiste (D-02, D-04), gesteuert über `lib/quelle.ts`. Kein
// URL-Zustand. Das Bild lädt erst, wenn die Leiste geöffnet wird (`v-if` auf der Anfrage).
const quelle = useQuelle()
const route = useRoute()
const schmal = useSchmalerBildschirm()

const anfrage = computed(() => quelle.anfrage)
const beleg = computed(() => (anfrage.value === null ? null : findeBeleg(anfrage.value.schluessel)))
const titel = computed(() =>
  beleg.value === null ? 'Quelle' : `Quelle: PDF-Seite ${String(beleg.value.pdfSeite)}`,
)

// Ab 700 px 56 rem breit, darunter vollbreit (UI-SPEC Seitenleiste, Rahmen).
const drawerStil = computed(() =>
  schmal.value
    ? { '--size': '100vw', '--spacing': 'var(--wa-space-m)' }
    : { '--size': 'min(56rem, 100vw)', '--spacing': 'var(--wa-space-l)' },
)

const angezeigt = ref(false)

// `wa-hide` kommt auch bei Escape, Schließen-Knopf und Klick daneben: den Zustand angleichen.
function beiHide(ereignis: Event) {
  if (ereignis.target === ereignis.currentTarget) {
    schliesseQuelle()
  }
}

function beiAfterShow(ereignis: Event) {
  if (ereignis.target === ereignis.currentTarget) {
    angezeigt.value = true
  }
}

function beiAfterHide(ereignis: Event) {
  if (ereignis.target === ereignis.currentTarget) {
    angezeigt.value = false
    fokusNachSchliessen()
  }
}

// Ein Seitenwechsel schließt die Leiste; der Fokus gehört dann der neuen Seite (Router).
watch(
  () => route.path,
  () => {
    if (quelle.offen) {
      schliesseQuelle({ ohneFokus: true })
    }
  },
)

// Fokus beim Öffnen: Web Awesome 3.14 fokussiert den benannten Dialog, der Schließen-Knopf ist
// der erste Tab-Stopp. Das bleibt der Standard (UI-SPEC: „WA-Standard, nicht überschreiben“).
// Der Satz der UI-SPEC, der den Schließen-Knopf als Fokusziel nennt, wird beim Checkpoint in
// Plan 07-10 neu bewertet.

const hinweis = computed(() =>
  beleg.value === null || anfrage.value === null
    ? null
    : belegHinweis(beleg.value, anfrage.value.herleitung),
)
</script>

<template>
  <wa-drawer
    id="om-quelle-drawer"
    placement="end"
    light-dismiss
    :label="titel"
    :open="quelle.offen"
    :style="drawerStil"
    @wa-hide="beiHide"
    @wa-after-show="beiAfterShow"
    @wa-after-hide="beiAfterHide"
  >
    <div v-if="anfrage !== null && beleg !== null" class="om-quelle-inhalt">
      <div class="om-quelle-wertzeile">
        <p class="om-quelle-wertzeile__bezeichnung">{{ anfrage.bezeichnung }}</p>
        <p v-if="anfrage.wert !== undefined" class="om-quelle-wertzeile__wert om-zahl">
          {{ anfrage.wert }}
        </p>
        <p v-if="anfrage.wertart !== undefined" class="om-quelle-wertzeile__wertart">
          {{ anfrage.wertart }}
        </p>
      </div>

      <template v-if="hinweis !== null">
        <wa-callout v-if="hinweis.art !== 'markiert'" variant="neutral">
          <wa-icon slot="icon" name="circle-info" aria-hidden="true"></wa-icon>
          <strong v-if="hinweis.titel !== undefined" class="om-quelle-hinweis__titel">{{
            hinweis.titel
          }}</strong>
          <p class="om-quelle-hinweis__text">{{ hinweis.text }}</p>
        </wa-callout>
        <p v-else class="om-quelle-wertzeile__wertart">{{ hinweis.text }}</p>
      </template>

      <p class="om-quelle-link">
        <a :href="originalSeitenUrl(beleg.pdfSeite)" target="_blank" rel="noopener noreferrer"
          >Seite {{ beleg.pdfSeite }} im Original-PDF öffnen<wa-icon
            name="arrow-up-right-from-square"
            class="om-extern-icon"
          ></wa-icon
          ><span class="om-visually-hidden"> (öffnet in neuem Tab)</span></a
        >
      </p>

      <QuelleSeite
        :key="beleg.schluessel"
        :beleg="beleg"
        :bezeichnung="anfrage.bezeichnung"
        :angezeigt="angezeigt"
      />
    </div>
  </wa-drawer>
</template>

<style scoped>
.om-quelle-inhalt {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-m);
}

.om-quelle-inhalt p {
  margin: 0;
}

.om-quelle-wertzeile {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-2xs);
}

.om-quelle-wertzeile__bezeichnung {
  font-size: var(--wa-font-size-s);
  font-weight: var(--wa-font-weight-bold);
  line-height: var(--wa-line-height-condensed);
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-quelle-wertzeile__wert {
  font-size: var(--wa-font-size-l);
  font-weight: var(--wa-font-weight-bold);
  line-height: var(--wa-line-height-condensed);
  text-align: start;
}

.om-quelle-wertzeile__wertart {
  font-size: var(--wa-font-size-s);
  font-weight: var(--wa-font-weight-normal);
  line-height: 1.5;
  color: var(--wa-color-text-quiet);
}

.om-quelle-hinweis__titel {
  display: block;
  font-size: var(--wa-font-size-m);
  font-weight: var(--wa-font-weight-bold);
}

.om-quelle-hinweis__text,
.om-quelle-link {
  font-size: var(--wa-font-size-m);
  font-weight: var(--wa-font-weight-normal);
  line-height: var(--wa-line-height-normal);
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-quelle-link a {
  display: inline-flex;
  align-items: center;
  min-height: 44px;
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-extern-icon {
  margin-inline-start: var(--wa-space-2xs);
  vertical-align: -0.125em;
}
</style>
