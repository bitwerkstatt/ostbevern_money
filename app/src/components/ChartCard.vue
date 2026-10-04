<script setup lang="ts">
import { computed, provide, ref, useId } from 'vue'
import { CHART_KONTEXT } from '@/components/chartKontext'

const props = defineProps<{
  titel: string
  beschreibung?: string
  quelle?: string
  pdf?: { seite: number }
  beispieldaten?: boolean
}>()

const titelId = useId()
const beschreibungId = useId()

provide(CHART_KONTEXT, {
  titelId,
  beschreibungId: () => (props.beschreibung ? beschreibungId : undefined),
})

const hatQuelle = computed(() => Boolean(props.quelle || props.pdf))

// Nach einem Ebenenwechsel setzt die Seite den Fokus auf die Überschrift der Karte (UI-SPEC
// Interaction Contract „Fokusführung nach Drilldown“).
const titelElement = ref<HTMLElement | null>(null)

function fokussiereTitel() {
  titelElement.value?.focus()
}

defineExpose({ fokussiereTitel })
</script>

<template>
  <section class="om-chart-card" :aria-labelledby="titelId">
    <h2 :id="titelId" ref="titelElement" tabindex="-1">{{ titel }}</h2>
    <p v-if="beschreibung" :id="beschreibungId">{{ beschreibung }}</p>
    <wa-callout v-if="beispieldaten" variant="warning" class="om-chart-card__beispieldaten">
      <wa-icon slot="icon" name="circle-info"></wa-icon>
      Beispieldaten — noch keine echten Haushaltszahlen.
    </wa-callout>
    <div class="om-chart-card__inhalt">
      <slot />
    </div>
    <p v-if="hatQuelle" class="om-chart-card__quelle">
      Quelle:
      <template v-if="quelle">{{ quelle }}</template>
      <template v-if="quelle && pdf">, </template>
      <template v-if="pdf">PDF-Seite {{ pdf.seite }}</template>
    </p>
    <slot name="fuss" />
  </section>
</template>

<style scoped>
.om-chart-card {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-m);
  background: var(--wa-color-surface-lowered);
  padding: var(--wa-space-m);
}

.om-chart-card h2 {
  margin: 0;
  font-size: var(--wa-font-size-l);
  font-weight: var(--wa-font-weight-bold);
  line-height: var(--wa-line-height-condensed);
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-chart-card p {
  margin: 0;
}

.om-chart-card__beispieldaten {
  display: block;
  width: 100%;
}

.om-chart-card__inhalt {
  min-width: 0;
}

.om-chart-card__quelle {
  font-size: var(--wa-font-size-s);
  color: var(--wa-color-text-quiet);
}
</style>
