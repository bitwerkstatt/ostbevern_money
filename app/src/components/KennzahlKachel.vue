<script setup lang="ts">
import BerechnetEtikett from '@/components/BerechnetEtikett.vue'

withDefaults(
  defineProps<{
    bezeichnung: string
    /** Bereits formatierter Wert (über `charts/format.ts`). */
    wert: string
    /** Zeile unter dem Wert: „{Wertart} {jahr} · PDF-Seite {n}“. */
    zeile: string
    berechnet?: boolean
  }>(),
  { berechnet: false },
)
</script>

<template>
  <div class="om-kennzahl">
    <p class="om-kennzahl__bezeichnung">{{ bezeichnung }}</p>
    <p class="om-kennzahl__wert">
      <span class="om-zahl">{{ wert }}</span
      ><BerechnetEtikett v-if="berechnet" />
    </p>
    <p class="om-kennzahl__zeile">{{ zeile }}</p>
  </div>
</template>

<style scoped>
.om-kennzahl {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-xs);
  height: 100%;
  box-sizing: border-box;
  background: var(--wa-color-surface-lowered);
  padding: var(--wa-space-m);
}

.om-kennzahl p {
  margin: 0;
}

.om-kennzahl__bezeichnung {
  font-size: var(--wa-font-size-s);
  font-weight: var(--wa-font-weight-bold);
  line-height: var(--wa-line-height-condensed);
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-kennzahl__wert {
  font-size: var(--wa-font-size-l);
  font-weight: var(--wa-font-weight-bold);
  line-height: var(--wa-line-height-condensed);
}

.om-kennzahl__wert .om-zahl {
  text-align: start;
}

.om-kennzahl__zeile {
  margin-top: auto;
  font-size: var(--wa-font-size-s);
  font-weight: var(--wa-font-weight-normal);
  line-height: 1.5;
  color: var(--wa-color-text-quiet);
  hyphens: auto;
  overflow-wrap: break-word;
}

@media (min-width: 700px) {
  .om-kennzahl__wert {
    font-size: var(--wa-font-size-2xl);
  }
}
</style>
