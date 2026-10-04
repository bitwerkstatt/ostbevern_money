<script setup lang="ts">
import { datum, jahr, KEIN_WERT } from '@/charts/format'
import { KONTAKT_EMAIL, ORIGINAL_PDF_URL } from '@/config'
import { haushalt } from '@/data/daten'

// Datenstand (D-18): das Haushaltsjahr und der Tag des Satzungsbeschlusses, beides aus den
// Daten; kein Erstellungsdatum.
const haushaltsjahr = jahr(haushalt.haushaltsjahr)
const beschluss = haushalt.meta.satzung['beschluss']
const beschlussDatum = typeof beschluss?.wert === 'string' ? datum(beschluss.wert) : KEIN_WERT
</script>

<template>
  <wa-page>
    <div slot="header" class="om-header">
      <RouterLink :to="{ name: 'start' }" class="om-site-name">Ostbevern Money</RouterLink>
      <nav aria-label="Hauptnavigation" class="om-nav">
        <ul>
          <li><RouterLink :to="{ name: 'start' }">Start</RouterLink></li>
        </ul>
      </nav>
    </div>

    <div class="om-content">
      <RouterView />
    </div>

    <div slot="footer" class="om-footer">
      <p>
        Datenstand: Haushalt {{ haushaltsjahr }}, beschlossen am {{ beschlussDatum }}.
        <a :href="ORIGINAL_PDF_URL" target="_blank" rel="noopener noreferrer"
          >Original-Haushaltsplan (PDF) der Gemeinde Ostbevern<wa-icon
            name="arrow-up-right-from-square"
            class="om-extern-icon"
          ></wa-icon
          ><span class="om-visually-hidden"> (öffnet in neuem Tab)</span></a
        >
      </p>
      <p>Inoffizielles Projekt, keine Veröffentlichung der Gemeinde Ostbevern.</p>
      <p>
        Kontakt:
        <a :href="`mailto:${KONTAKT_EMAIL}`" class="om-kontakt">{{ KONTAKT_EMAIL }}</a>
      </p>
      <p>
        Inspiriert von
        <a
          href="https://github.com/codeformuenster/haushalt-muenster-2026"
          target="_blank"
          rel="noopener noreferrer"
          >Münster Money (Code for Münster)<wa-icon
            name="arrow-up-right-from-square"
            class="om-extern-icon"
          ></wa-icon
          ><span class="om-visually-hidden"> (öffnet in neuem Tab)</span></a
        >
      </p>
    </div>
  </wa-page>
</template>

<style scoped>
.om-header,
.om-footer {
  background: var(--wa-color-surface-lowered);
  padding: var(--wa-space-m) var(--wa-space-l);
  display: flex;
  align-items: center;
  gap: var(--wa-space-l);
  flex-wrap: wrap;
}

.om-site-name {
  font-size: var(--wa-font-size-l);
  font-weight: var(--wa-font-weight-bold);
  text-decoration: none;
}

.om-nav ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: var(--wa-space-m);
}

.om-nav a {
  text-decoration: none;
}

.om-nav a.router-link-exact-active {
  color: var(--wa-color-brand-40);
  font-weight: var(--wa-font-weight-bold);
}

.om-content {
  padding: var(--wa-space-l);
}

.om-footer {
  flex-direction: column;
  align-items: flex-start;
  gap: var(--wa-space-2xs);
  font-size: var(--wa-font-size-s);
  font-weight: var(--wa-font-weight-body);
  line-height: 1.5;
  color: var(--wa-color-text-quiet);
}

.om-footer p {
  margin: 0;
  overflow-wrap: anywhere;
}

.om-footer a {
  color: inherit;
  text-decoration: underline;
}

.om-extern-icon {
  margin-inline-start: var(--wa-space-3xs);
  vertical-align: -0.125em;
}

@media (max-width: 699px) {
  .om-footer {
    align-items: center;
    text-align: center;
  }
}
</style>
