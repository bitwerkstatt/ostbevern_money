<script setup lang="ts">
import { RouterLink, type RouteLocationRaw } from 'vue-router'

// `wa-card`, `wa-button` und `wa-icon` sind in `main.ts` registriert.
defineProps<{
  /** Die Leitfrage, z. B. „Woher kommt das Geld?“ (als Überschrift der Kachel). */
  frage: string
  /** Zeile unter dem Datensatz: „{Wertart} {jahr} · PDF-Seite {n}“. */
  zeile: string
  /** Ziel des einen Buttons (benannte Route). */
  ziel: RouteLocationRaw
  /** Beschriftung des Buttons, z. B. „Einnahmen ansehen“. */
  cta: string
}>()
</script>

<template>
  <wa-card class="om-einstieg">
    <div class="om-einstieg__inhalt">
      <h2 class="om-einstieg__frage">{{ frage }}</h2>
      <p class="om-einstieg__satz"><slot /></p>
      <p class="om-einstieg__zeile">{{ zeile }}</p>
      <RouterLink :to="ziel" custom v-slot="{ href, navigate }">
        <wa-button
          class="om-einstieg__cta"
          variant="brand"
          size="large"
          :href="href"
          @click="navigate"
          >{{ cta }}</wa-button
        >
      </RouterLink>
    </div>
  </wa-card>
</template>

<style scoped>
.om-einstieg {
  display: block;
  width: 100%;
  height: 100%;
}

.om-einstieg__inhalt {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-m);
  height: 100%;
}

.om-einstieg__inhalt p,
.om-einstieg__inhalt h2 {
  margin: 0;
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-einstieg__frage {
  font-size: var(--wa-font-size-l);
  font-weight: var(--wa-font-weight-bold);
  line-height: var(--wa-line-height-condensed);
}

.om-einstieg__satz {
  font-size: var(--wa-font-size-m);
  font-weight: var(--wa-font-weight-normal);
  line-height: var(--wa-line-height-normal);
}

.om-einstieg__zeile {
  font-size: var(--wa-font-size-s);
  font-weight: var(--wa-font-weight-normal);
  line-height: 1.5;
  color: var(--wa-color-text-quiet);
}

.om-einstieg__cta {
  margin-top: auto;
  width: 100%;
  font-size: var(--wa-font-size-l);
  font-weight: var(--wa-font-weight-bold);
}

.om-einstieg__cta::part(base) {
  font-size: var(--wa-font-size-l);
  font-weight: var(--wa-font-weight-bold);
  min-height: 44px;
}

.om-einstieg__cta::part(label) {
  white-space: normal;
  text-align: center;
}
</style>
