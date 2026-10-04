<script setup lang="ts">
import type { Brotkrume } from '@/lib/drilldown'

// Der Dateiname „Brotkrumen“ steht so im UI-SPEC; der Komponentenname trägt das Projektpräfix.
defineOptions({ name: 'OmBrotkrumen' })

defineProps<{
  /** Pfad von der Wurzel bis zur aktuellen Ebene; der letzte Eintrag ist die aktuelle Ebene. */
  eintraege: readonly Brotkrume[]
}>()

const emit = defineEmits<{
  geheZu: [code: string]
}>()
</script>

<template>
  <nav aria-label="Ebene im Haushalt" class="om-brotkrumen">
    <ol>
      <li v-for="(eintrag, n) in eintraege" :key="eintrag.code">
        <template v-if="n < eintraege.length - 1">
          <wa-button
            appearance="plain"
            class="om-brotkrumen__knopf"
            @click="emit('geheZu', eintrag.code)"
          >
            {{ eintrag.name }}
          </wa-button>
          <span class="om-brotkrumen__trenner" aria-hidden="true">›</span>
        </template>
        <span v-else class="om-brotkrumen__aktuell" aria-current="location">{{
          eintrag.name
        }}</span>
      </li>
    </ol>
  </nav>
</template>

<style scoped>
.om-brotkrumen ol {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--wa-space-2xs);
  margin: 0;
  padding: 0;
  list-style: none;
}

.om-brotkrumen li {
  display: flex;
  align-items: center;
  gap: var(--wa-space-2xs);
  min-inline-size: 0;
}

/* Mindest-Trefferfläche 44 px (WCAG 2.5.5); lange Namen brechen um. */
.om-brotkrumen wa-button::part(base) {
  min-block-size: 44px;
  min-inline-size: 44px;
  block-size: auto;
  white-space: normal;
  text-align: start;
}

.om-brotkrumen wa-button::part(label) {
  white-space: normal;
  overflow-wrap: break-word;
  hyphens: auto;
}

.om-brotkrumen__trenner {
  color: var(--wa-color-text-quiet);
}

.om-brotkrumen__aktuell {
  font-weight: var(--wa-font-weight-bold);
  overflow-wrap: break-word;
  hyphens: auto;
}
</style>
