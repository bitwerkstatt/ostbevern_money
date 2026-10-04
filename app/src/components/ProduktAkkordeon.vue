<script setup lang="ts">
import { produktGruppen } from '@/lib/glossar'

// Die Gruppen leiten sich aus den Daten ab (D-16): keine feste Gruppenzahl im Code, und
// ein Bereich ohne Produkte kommt gar nicht erst in die Liste.
const gruppen = produktGruppen()
</script>

<template>
  <div class="om-produkt-akkordeon">
    <wa-details v-for="gruppe in gruppen" :key="gruppe.pb" :summary="gruppe.name">
      <div class="om-produkt-akkordeon__produkte">
        <wa-details
          v-for="produkt in gruppe.produkte"
          :key="produkt.code"
          :summary="`${produkt.code} ${produkt.name}`"
        >
          <p v-if="produkt.beschreibung" class="om-produkt-akkordeon__beschreibung">
            {{ produkt.beschreibung }}
          </p>
          <p class="om-produkt-akkordeon__link">
            <RouterLink :to="{ name: 'produkt', params: { code: produkt.code } }"
              >Produkt öffnen</RouterLink
            >
          </p>
        </wa-details>
      </div>
    </wa-details>
  </div>
</template>

<style scoped>
.om-produkt-akkordeon {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-s);
  max-width: 100%;
}

.om-produkt-akkordeon__produkte {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-xs);
}

/* Mindest-Trefferfläche 44 px (WCAG 2.5.5); lange Summary-Texte brechen um. */
.om-produkt-akkordeon wa-details::part(summary) {
  min-height: 44px;
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-produkt-akkordeon wa-details {
  max-width: 100%;
}

.om-produkt-akkordeon p {
  margin: 0;
  font-size: var(--wa-font-size-m);
  line-height: var(--wa-line-height-normal);
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-produkt-akkordeon__beschreibung {
  margin-bottom: var(--wa-space-s);
}

.om-produkt-akkordeon__link a {
  display: inline-flex;
  align-items: center;
  min-height: 44px;
}
</style>
