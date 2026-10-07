<script setup lang="ts">
import { computed } from 'vue'

import { euro } from '@/charts/format'
import BaseChart from '@/components/BaseChart.vue'
import DatenTabelle from '@/components/DatenTabelle.vue'
import { veFaelligkeiten, veOption, veTabelle, vePdfSeiten } from '@/lib/finanzierung'

const LEER_TITEL = 'Keine Verpflichtungsermächtigungen'
const LEER_TEXT = 'Der Haushaltsplan nennt keine Fälligkeiten. Öffne die Tabelle.'
const BESCHREIBUNG =
  'Säulendiagramm: Verpflichtungsermächtigungen nach dem Jahr, in dem sie fällig werden. Dieselben Werte und die zugehörigen Maßnahmen stehen in der Tabelle darunter.'

const eintraege = veFaelligkeiten()
const option = computed(() => veOption(eintraege))
const tabelle = veTabelle(eintraege)
const seiten = vePdfSeiten()
const fussnote = `Quelle: Haushaltsplan, PDF-Seiten ${seiten.join(', ')}.`

/** Die Maßnahmen eines Fälligkeitsjahres für die Zelle „Maßnahmen“ (Link auf das Produkt). */
function massnahmenVon(faelligkeitsjahr: unknown) {
  return eintraege.find((eintrag) => eintrag.jahr === faelligkeitsjahr)?.massnahmen ?? []
}
</script>

<template>
  <div class="om-ve">
    <BaseChart
      :option="option"
      hoehe="280px"
      :beschreibung="BESCHREIBUNG"
      :leer-titel="LEER_TITEL"
      :leer-text="LEER_TEXT"
    />
    <p class="om-ve__caption">Fälligkeit laut Haushaltsplan</p>

    <wa-details summary="Tabelle anzeigen">
      <DatenTabelle
        beschriftung="Verpflichtungsermächtigungen nach Fälligkeitsjahr"
        :spalten="tabelle.spalten"
        :zeilen="tabelle.zeilen"
        :fussnote="fussnote"
        :leer-titel="LEER_TITEL"
        :leer-text="LEER_TEXT"
      >
        <!-- Nur die Zelle „Maßnahmen“ wird ersetzt; ohne Inhalt greift die Standarddarstellung. -->
        <template #zelle="{ zeile, spalte }">
          <ul v-if="spalte.schluessel === 'massnahmen'" class="om-ve__liste" role="list">
            <li
              v-for="m in massnahmenVon(zeile['faelligkeitsjahr'])"
              :key="`${m.produkt}/${m.massnahmeId}`"
            >
              <RouterLink
                class="om-ve__link"
                :to="{ name: 'produkt', params: { code: m.produkt } }"
              >
                {{ m.name }}
              </RouterLink>
              <span class="om-zahl">{{ euro(m.betrag) }}</span>
            </li>
          </ul>
        </template>
      </DatenTabelle>
    </wa-details>
  </div>
</template>

<style scoped>
.om-ve {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-m);
  min-width: 0;
}

.om-ve__caption {
  margin: 0;
  font-size: var(--wa-font-size-s);
  color: var(--wa-color-text-quiet);
}

.om-ve__liste {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-2xs);
  margin: 0;
  padding: 0;
  list-style: none;
}

.om-ve__liste li {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 0 var(--wa-space-s);
}

.om-ve__link {
  display: inline-flex;
  align-items: center;
  min-block-size: 44px;
  color: var(--wa-color-brand-40);
  text-decoration: underline;
  overflow-wrap: break-word;
  hyphens: auto;
}
</style>
