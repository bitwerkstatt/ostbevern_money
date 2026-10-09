<script setup lang="ts">
import { computed } from 'vue'

import { seitenText } from '@/lib/hilfsfunktionen'
import { findeText, rendereAbsatz, textFuerJahr } from '@/lib/texte'

const props = withDefaults(
  defineProps<{
    schluessel: string
    /** Gewähltes Jahr; fehlt es, wird der Text immer gezeigt. */
    jahr?: number
    ueberschrift?: boolean
  }>(),
  { jahr: undefined, ueberschrift: true },
)

const text = computed(() =>
  props.jahr === undefined
    ? (findeText(props.schluessel) ?? null)
    : textFuerJahr(props.schluessel, props.jahr),
)
const absaetze = computed(() => text.value?.absaetze.map((absatz) => rendereAbsatz(absatz)) ?? [])
const quelle = computed(() => seitenText(text.value?.quelle_seiten ?? []))
</script>

<template>
  <div v-if="text" class="om-erklaertext">
    <h3 v-if="ueberschrift">{{ text.titel }}</h3>
    <p v-for="(absatz, index) in absaetze" :key="index">{{ absatz }}</p>
    <p v-if="quelle !== ''" class="om-erklaertext__quelle">Quelle: {{ quelle }}</p>
  </div>
</template>

<style scoped>
.om-erklaertext {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-s);
}

.om-erklaertext h3 {
  margin: 0;
  font-size: var(--wa-font-size-l);
  font-weight: var(--wa-font-weight-bold);
  line-height: var(--wa-line-height-condensed);
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-erklaertext p {
  margin: 0;
  font-size: var(--wa-font-size-m);
  line-height: var(--wa-line-height-normal);
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-erklaertext .om-erklaertext__quelle {
  font-size: var(--wa-font-size-s);
  color: var(--wa-color-text-quiet);
}
</style>
