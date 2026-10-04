<script setup lang="ts">
import { computed, useId } from 'vue'

import { ersterSatz, findeBegriff, type GlossarSchluessel } from '@/lib/glossar'

// `schluessel` ist ein Union-Typ aus den Glossarschlüsseln: ein unbekannter Schlüssel ist
// ein Typfehler, kein Laufzeit-Leerzustand (D-16). `glossar.test.ts` prüft zusätzlich
// alle Verwendungen in den Vue-Dateien.
const props = defineProps<{
  schluessel: GlossarSchluessel
}>()

const id = useId()
const begriff = computed(() => findeBegriff(props.schluessel)?.begriff ?? props.schluessel)
const satz = computed(() => ersterSatz(props.schluessel))
</script>

<template>
  <span class="om-glossar-begriff-huelle">
    <RouterLink
      :id="id"
      class="om-glossar-begriff"
      aria-current-value="false"
      :to="{ name: 'glossar', hash: '#' + schluessel }"
    >
      <slot>{{ begriff }}</slot>
    </RouterLink>
    <wa-tooltip :for="id">{{ satz }}</wa-tooltip>
  </span>
</template>

<style scoped>
/* Gepunktete Unterstreichung, Textfarbe unverändert (UI-SPEC GlossarBegriff). */
.om-glossar-begriff {
  color: inherit;
  text-decoration: underline dotted;
  text-underline-offset: 4px;
  /* Bricht nur an Leerzeichen, nie mitten im Wort (UI-SPEC E13 long-text). */
  white-space: normal;
  hyphens: none;
  overflow-wrap: normal;
}
</style>
