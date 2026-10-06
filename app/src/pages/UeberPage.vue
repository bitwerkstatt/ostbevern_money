<script setup lang="ts">
import { jahr } from '@/charts/format'
import PageIntro from '@/components/PageIntro.vue'
import { IMPRESSUM_ANSCHRIFT, IMPRESSUM_NAME, KONTAKT_EMAIL, ORIGINAL_PDF_URL } from '@/config'
import { haushalt } from '@/data/daten'

// Die Jahreszahl im Text kommt aus den Daten, nie aus dem Text selbst (UI-05).
const haushaltsjahr = jahr(haushalt.haushaltsjahr)
</script>

<template>
  <PageIntro
    titel="Über dieses Projekt"
    beschreibung="Hier steht, wer hinter Ostbevern Money steckt und was mit deinen Daten passiert."
  />

  <div class="om-ueber">
    <section aria-labelledby="om-ueber-inoffiziell" class="om-ueber__abschnitt">
      <h2 id="om-ueber-inoffiziell">Ein inoffizielles Projekt</h2>
      <p>
        Ostbevern Money ist ein privates Projekt. Es ist keine Veröffentlichung der Gemeinde
        Ostbevern. Alle Zahlen stammen aus dem Haushaltsplan {{ haushaltsjahr }} der Gemeinde, den
        du im Original nachlesen kannst.
      </p>
      <p>
        <a :href="ORIGINAL_PDF_URL" target="_blank" rel="noopener noreferrer"
          >Original-Haushaltsplan (PDF) der Gemeinde Ostbevern<wa-icon
            name="arrow-up-right-from-square"
            class="om-extern-icon"
          ></wa-icon
          ><span class="om-visually-hidden"> (öffnet in neuem Tab)</span></a
        >
      </p>
    </section>

    <section aria-labelledby="om-ueber-dank" class="om-ueber__abschnitt">
      <h2 id="om-ueber-dank">Dank</h2>
      <p>
        Die Idee und große Teile der Technik stammen von Münster Money von Code for Münster,
        entstanden beim Münsterhack. Danke dafür!
      </p>
      <p>
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
    </section>

    <section aria-labelledby="om-ueber-impressum" class="om-ueber__abschnitt">
      <h2 id="om-ueber-impressum">Impressum</h2>
      <dl class="om-ueber__impressum">
        <div>
          <dt>Verantwortlich</dt>
          <dd>{{ IMPRESSUM_NAME }}</dd>
        </div>
        <div>
          <dt>Anschrift</dt>
          <dd>
            <address class="om-ueber__anschrift">
              <span v-for="(zeile, nummer) in IMPRESSUM_ANSCHRIFT" :key="nummer">{{ zeile }}</span>
            </address>
          </dd>
        </div>
        <div>
          <dt>Kontakt</dt>
          <dd>
            <a :href="`mailto:${KONTAKT_EMAIL}`" class="om-ueber__kontakt">{{ KONTAKT_EMAIL }}</a>
          </dd>
        </div>
      </dl>
    </section>

    <section aria-labelledby="om-ueber-datenschutz" class="om-ueber__abschnitt">
      <h2 id="om-ueber-datenschutz">Datenschutz</h2>
      <p>
        Diese Seite setzt keine Cookies und verwendet kein Tracking. Beim Aufruf werden keine Daten
        an Drittanbieter geschickt. Die Seite wird bei GitHub Pages gehostet.
      </p>
    </section>
  </div>
</template>

<style scoped>
.om-ueber {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-3xl);
}

.om-ueber__abschnitt {
  max-width: 40rem;
}

.om-ueber__abschnitt h2 {
  margin: 0 0 var(--wa-space-l);
  font-size: var(--wa-font-size-l);
  font-weight: var(--wa-font-weight-bold);
  line-height: var(--wa-line-height-condensed);
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-ueber__abschnitt p {
  margin: 0 0 var(--wa-space-m);
  font-size: var(--wa-font-size-m);
  font-weight: var(--wa-font-weight-normal);
  line-height: var(--wa-line-height-normal);
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-ueber__abschnitt a {
  overflow-wrap: anywhere;
}

.om-extern-icon {
  margin-inline-start: var(--wa-space-2xs);
  vertical-align: -0.125em;
}

.om-ueber__impressum {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-l);
  margin: 0;
}

.om-ueber__impressum dt {
  font-size: var(--wa-font-size-s);
  font-weight: var(--wa-font-weight-bold);
  line-height: var(--wa-line-height-condensed);
  color: var(--wa-color-text-quiet);
}

.om-ueber__impressum dd {
  margin: 0;
  font-size: var(--wa-font-size-m);
  font-weight: var(--wa-font-weight-normal);
  line-height: var(--wa-line-height-normal);
  hyphens: auto;
  overflow-wrap: anywhere;
}

.om-ueber__anschrift {
  display: flex;
  flex-direction: column;
  font-style: normal;
}

.om-ueber__anschrift span {
  hyphens: auto;
  overflow-wrap: anywhere;
}

.om-ueber__kontakt {
  overflow-wrap: anywhere;
}
</style>
