<script setup lang="ts">
import { computed } from 'vue'

import { jahr as formatiereJahr } from '@/charts/format'
import WertartEtikett from '@/components/WertartEtikett.vue'
import { haushalt } from '@/data/daten'
import { ansagen } from '@/lib/ansage'
import { useSchmalerBildschirm } from '@/lib/bildschirm'
import { useJahr, wertartFuerJahr, wertartName } from '@/lib/jahr'

const istSchmal = useSchmalerBildschirm()
const { jahr, wertart, setzeJahr } = useJahr()

// Jahre und Wertarten stammen aus haushalt.json, im Code steht keine Jahreszahl (D-10).
const optionen = computed(() =>
  haushalt.jahre.map((j) => ({
    wert: String(j),
    text: `${formatiereJahr(j)} · ${wertartName(wertartFuerJahr(j))}`,
  })),
)

const gewaehlt = computed(() => String(jahr.value))

// Erstes Jahr mit Wertart „ergebnis“ (Ist): im PDF ein vorläufiges Rechnungsergebnis
// („vorl. RE“, RESEARCH Open Question 3). Das Jahr kommt aus den Daten.
const istJahr = computed(() => {
  const index = haushalt.wertarten.indexOf('ergebnis')
  return haushalt.jahre[index]
})

// Das Ereignis kommt vom Web-Awesome-Host (Gruppe bzw. Select); der neue Wert steht in
// dessen `value`. Nur ein Jahr aus haushalt.jahre wird weitergegeben; der Fokus bleibt auf
// dem Steuerelement, die Änderung meldet eine höfliche Live-Region (D-10).
function beiAenderung(ereignis: Event) {
  const wert = (ereignis.currentTarget as { value?: unknown } | null)?.value
  if (typeof wert !== 'string' || !/^\d+$/.test(wert)) {
    return
  }
  const neu = Number(wert)
  if (haushalt.jahre.includes(neu)) {
    setzeJahr(neu)
    ansagen(`Zeige ${wertartName(wertartFuerJahr(neu))} ${formatiereJahr(neu)}`)
  }
}
</script>

<template>
  <div class="om-jahr-umschalter">
    <wa-select
      v-if="istSchmal"
      class="om-jahr-umschalter__select"
      label="Haushaltsjahr"
      :value="gewaehlt"
      @change="beiAenderung"
    >
      <wa-option v-for="option in optionen" :key="option.wert" :value="option.wert">
        {{ option.text }}
      </wa-option>
    </wa-select>
    <wa-radio-group
      v-else
      class="om-jahr-umschalter__gruppe"
      label="Haushaltsjahr"
      orientation="horizontal"
      :value="gewaehlt"
      @change="beiAenderung"
    >
      <wa-radio
        v-for="option in optionen"
        :key="option.wert"
        appearance="button"
        :value="option.wert"
      >
        {{ option.text }}
      </wa-radio>
    </wa-radio-group>
    <p class="om-jahr-umschalter__wertart">
      <WertartEtikett :wertart="wertart" />
    </p>
    <wa-details
      class="om-jahr-umschalter__erklaerung"
      summary="Was bedeuten Ist, Ansatz und Planung?"
    >
      <p>
        Ist: das Ergebnis eines abgeschlossenen Jahres. Ansatz: der im Haushaltsplan beschlossene
        Wert. Planung: die mittelfristige Finanzplanung der folgenden Jahre.
      </p>
      <p v-if="istJahr !== undefined">
        Für {{ formatiereJahr(istJahr) }} ist der Ist-Wert das vorläufige Rechnungsergebnis (im
        Haushaltsplan „vorl. RE“).
      </p>
    </wa-details>
  </div>
</template>

<style scoped>
.om-jahr-umschalter {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-xs);
}

.om-jahr-umschalter wa-radio-group::part(form-control-label),
.om-jahr-umschalter wa-select::part(form-control-label) {
  font-size: var(--wa-font-size-s);
  font-weight: var(--wa-font-weight-bold);
  line-height: var(--wa-line-height-condensed);
}

/* Mindest-Trefferfläche 44 px (WCAG 2.5.5, UI-SPEC Spacing-Ausnahmen). */
.om-jahr-umschalter wa-radio::part(control),
.om-jahr-umschalter wa-select::part(combobox),
.om-jahr-umschalter wa-option::part(base) {
  min-height: 44px;
}

.om-jahr-umschalter wa-radio::part(label) {
  white-space: nowrap;
}

.om-jahr-umschalter__select {
  width: 100%;
}

.om-jahr-umschalter__wertart {
  margin: 0;
}

.om-jahr-umschalter__erklaerung p {
  margin: 0 0 var(--wa-space-xs);
}

.om-jahr-umschalter__erklaerung p:last-child {
  margin-bottom: 0;
}

.om-jahr-umschalter wa-details::part(summary) {
  min-height: 44px;
}
</style>
