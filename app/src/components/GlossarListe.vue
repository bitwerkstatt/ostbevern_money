<script setup lang="ts">
import { glossarBegriffe } from '@/lib/glossar'
import { rendereAbsatz } from '@/lib/texte'

const begriffe = glossarBegriffe().map((begriff) => ({
  schluessel: begriff.schluessel,
  begriff: begriff.begriff,
  absaetze: begriff.absaetze.map((absatz) => rendereAbsatz(absatz)),
  quelle:
    begriff.quelle_seiten.length === 0
      ? ''
      : `Quelle: PDF-${begriff.quelle_seiten.length === 1 ? 'Seite' : 'Seiten'} ${begriff.quelle_seiten.join(', ')}`,
}))

/**
 * Der Router fokussiert das Sprungziel (die Section mit der ID aus dem Fragment). Der
 * Fokus gehört auf die Überschrift des Begriffs: Screenreader lesen so den Begriff vor.
 */
function fokussiereUeberschrift(ereignis: FocusEvent) {
  const abschnitt = ereignis.currentTarget
  if (abschnitt instanceof HTMLElement && ereignis.target === abschnitt) {
    abschnitt.querySelector('h3')?.focus({ preventScroll: true })
  }
}
</script>

<template>
  <div class="om-glossar-liste">
    <section
      v-for="eintrag in begriffe"
      :id="eintrag.schluessel"
      :key="eintrag.schluessel"
      class="om-glossar-liste__begriff"
      @focus="fokussiereUeberschrift"
    >
      <h3 tabindex="-1">{{ eintrag.begriff }}</h3>
      <p v-for="(absatz, index) in eintrag.absaetze" :key="index">{{ absatz }}</p>
      <p v-if="eintrag.quelle" class="om-glossar-liste__quelle">{{ eintrag.quelle }}</p>
    </section>
  </div>
</template>

<style scoped>
.om-glossar-liste {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-2xl);
}

.om-glossar-liste__begriff {
  display: flex;
  flex-direction: column;
  gap: var(--wa-space-s);
  max-width: 100%;
  /* Unter der Kopfzeile: wa-page liefert die Höhe über --scroll-margin-top, --wa-space-m ist
     der Abstand über dem Begriff. Der Router liest diesen Wert als Scroll-Versatz
     (lib/sprungziel.ts). */
  scroll-margin-top: calc(var(--scroll-margin-top, 0px) + var(--wa-space-m));
}

.om-glossar-liste__begriff:focus {
  outline: none;
}

.om-glossar-liste__begriff h3 {
  margin: 0;
  font-size: var(--wa-font-size-l);
  font-weight: var(--wa-font-weight-semibold);
  line-height: var(--wa-line-height-condensed);
  hyphens: auto;
  overflow-wrap: break-word;
}

/* Ziel-Begriff: sichtbarer Fokusrahmen von 2 px, auch nach Mausklick auf einen Sprunglink. */
.om-glossar-liste__begriff h3:focus {
  outline: 2px solid var(--wa-color-focus);
  outline-offset: var(--wa-space-3xs);
  border-radius: var(--wa-border-radius-s);
}

.om-glossar-liste__begriff p {
  margin: 0;
  font-size: var(--wa-font-size-m);
  font-weight: var(--wa-font-weight-normal);
  line-height: var(--wa-line-height-normal);
  hyphens: auto;
  overflow-wrap: break-word;
}

.om-glossar-liste__begriff .om-glossar-liste__quelle {
  font-size: var(--wa-font-size-s);
  color: var(--wa-color-text-quiet);
}
</style>
