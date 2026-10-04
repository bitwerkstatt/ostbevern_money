<script setup lang="ts">
import GlossarListe from '@/components/GlossarListe.vue'
import PageIntro from '@/components/PageIntro.vue'
import { glossarBegriffe } from '@/lib/glossar'

const sprungmarken = glossarBegriffe().map((begriff) => ({
  schluessel: begriff.schluessel,
  begriff: begriff.begriff,
}))
</script>

<template>
  <PageIntro
    titel="Glossar und alle Produkte"
    beschreibung="Hier findest du die wichtigsten Begriffe des Haushalts und alle Produkte der Gemeinde."
  />

  <nav aria-label="Begriffe" class="om-glossar-sprung">
    <ul>
      <li v-for="marke in sprungmarken" :key="marke.schluessel">
        <RouterLink :to="{ name: 'glossar', hash: '#' + marke.schluessel }">{{
          marke.begriff
        }}</RouterLink>
      </li>
    </ul>
  </nav>

  <GlossarListe />
</template>

<style scoped>
.om-glossar-sprung {
  margin-bottom: var(--wa-space-3xl);
}

.om-glossar-sprung ul {
  display: flex;
  flex-wrap: wrap;
  gap: var(--wa-space-xs) var(--wa-space-s);
  margin: 0;
  padding: 0;
  list-style: none;
}

.om-glossar-sprung a {
  display: inline-flex;
  align-items: center;
  min-height: 44px;
  padding-inline: var(--wa-space-s);
  font-size: var(--wa-font-size-m);
  line-height: var(--wa-line-height-condensed);
  overflow-wrap: break-word;
}
</style>
