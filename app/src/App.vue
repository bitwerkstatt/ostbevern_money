<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, type RouteLocationRaw } from 'vue-router'

import { datum, jahr, KEIN_WERT } from '@/charts/format'
import MenueGruppe from '@/components/MenueGruppe.vue'
import QuelleSeitenleiste from '@/components/QuelleSeitenleiste.vue'
import { KONTAKT_EMAIL, ORIGINAL_PDF_URL } from '@/config'
import { haushalt } from '@/data/daten'
import { useSchmalerBildschirm } from '@/lib/bildschirm'
import { useJahr } from '@/lib/jahr'
import { MENUE, type MenueLink } from '@/lib/menue'

// Datenstand (D-18): das Haushaltsjahr und der Tag des Satzungsbeschlusses, beides aus den
// Daten; kein Erstellungsdatum.
const haushaltsjahr = jahr(haushalt.haushaltsjahr)
const beschluss = haushalt.meta.satzung['beschluss']
const beschlussDatum = typeof beschluss?.wert === 'string' ? datum(beschluss.wert) : KEIN_WERT

// Kopfmenü (D-13): Die Links zu Woher?, Wofür? und Geldfluss behalten das gewählte Jahr (D-10).
const { jahrLink } = useJahr()
function menueZiel(eintrag: MenueLink): RouteLocationRaw {
  return eintrag.mitJahr ? jahrLink({ name: eintrag.name }) : { name: eintrag.name }
}

// Eine leere Gruppe wird nicht gerendert (D-19, UI-SPEC E12 zero-one-many).
const menue = computed(() =>
  MENUE.filter((eintrag) => eintrag.typ === 'link' || eintrag.eintraege.length > 0),
)

// Mobiles Menü: Bis 699 px ersetzt ein Drawer die horizontale Liste.
const route = useRoute()
const schmal = useSchmalerBildschirm()
const DRAWER_ID = 'om-menue-drawer'
const drawerOffen = ref(false)
const drawerAktiv = ref(false) // offen oder noch beim Schließen (Animation)
const schliesstDurchSeitenwechsel = ref(false)
const menueSchalter = ref<HTMLButtonElement | null>(null)

function oeffneDrawer() {
  drawerOffen.value = true
  drawerAktiv.value = true
}

// `wa-hide` kommt auch bei Escape, Schließen-Knopf und Klick daneben: den Zustand angleichen,
// sonst bleibt `open` in Vue auf true und der Schalter öffnet nicht erneut.
function beiHide(ereignis: Event) {
  if (ereignis.target === ereignis.currentTarget) {
    drawerOffen.value = false
  }
}

// Nach dem Schließen zurück zum Schalter. Nach einem Seitenwechsel gehört der Fokus der neuen
// Seite (Router: Überschrift, D-13), ihn jetzt zum Schalter zu holen wäre ein Fokusraub.
function beiAfterHide(ereignis: Event) {
  if (ereignis.target !== ereignis.currentTarget) {
    return
  }
  drawerAktiv.value = false
  if (schliesstDurchSeitenwechsel.value) {
    schliesstDurchSeitenwechsel.value = false
    return
  }
  menueSchalter.value?.focus()
}

watch(
  () => route.path,
  () => {
    if (drawerAktiv.value) {
      schliesstDurchSeitenwechsel.value = true
      drawerOffen.value = false
    }
  },
)

// Ein Wechsel auf die breite Ansicht entfernt den Drawer; er darf nicht „offen“ zurückbleiben.
watch(schmal, (istSchmal) => {
  if (!istSchmal) {
    drawerOffen.value = false
    drawerAktiv.value = false
    schliesstDurchSeitenwechsel.value = false
  }
})

// Skip-Link (RESEARCH Pitfall 2): Der eingebaute Link von wa-page zeigt auf `#main-content`,
// im Hash-Router wäre das der Pfad `/main-content` (Weiterleitung zum Start). Der Klick wird in
// der Capture-Phase abgefangen (der Link liegt im Shadow-DOM, `composedPath()` findet ihn über
// sein `part`) und stattdessen die Überschrift der Seite fokussiert.
const seite = ref<HTMLElement | null>(null)

function beiSeitenklick(ereignis: Event) {
  const istSkipLink = ereignis
    .composedPath()
    .some(
      (knoten) => knoten instanceof Element && knoten.getAttribute('part') === 'skip-to-content',
    )
  if (!istSkipLink) {
    return
  }
  ereignis.preventDefault()
  const ziel =
    document.querySelector<HTMLElement>('h1') ?? document.querySelector<HTMLElement>('main')
  if (ziel !== null) {
    if (!ziel.hasAttribute('tabindex')) {
      ziel.setAttribute('tabindex', '-1')
    }
    ziel.focus()
  }
}

onMounted(() => {
  seite.value?.addEventListener('click', beiSeitenklick, { capture: true })
})
onBeforeUnmount(() => {
  seite.value?.removeEventListener('click', beiSeitenklick, { capture: true })
})
</script>

<template>
  <wa-page ref="seite">
    <span slot="skip-to-content">Zum Inhalt springen</span>

    <div slot="header" class="om-header">
      <RouterLink :to="{ name: 'start' }" class="om-site-name">Ostbevern Money</RouterLink>

      <nav v-if="!schmal" aria-label="Hauptnavigation" class="om-nav">
        <ul>
          <li
            v-for="eintrag in menue"
            :key="eintrag.typ === 'gruppe' ? eintrag.text : eintrag.name"
          >
            <MenueGruppe v-if="eintrag.typ === 'gruppe'" :gruppe="eintrag" :ziel="menueZiel" />
            <RouterLink v-else :to="menueZiel(eintrag)">{{ eintrag.text }}</RouterLink>
          </li>
        </ul>
      </nav>

      <template v-else>
        <button
          ref="menueSchalter"
          type="button"
          class="om-menue-schalter"
          aria-label="Menü öffnen"
          :aria-expanded="drawerOffen ? 'true' : 'false'"
          :aria-controls="DRAWER_ID"
          @click="oeffneDrawer"
        >
          <wa-icon name="bars" aria-hidden="true"></wa-icon>
        </button>

        <wa-drawer
          :id="DRAWER_ID"
          placement="end"
          label="Menü"
          light-dismiss
          :open="drawerOffen"
          @wa-hide="beiHide"
          @wa-after-hide="beiAfterHide"
        >
          <nav aria-label="Hauptnavigation" class="om-nav om-nav-drawer">
            <ul>
              <li
                v-for="(eintrag, nummer) in menue"
                :key="eintrag.typ === 'gruppe' ? eintrag.text : eintrag.name"
              >
                <template v-if="eintrag.typ === 'gruppe'">
                  <span :id="`om-drawer-gruppe-${nummer}`" class="om-nav-gruppe__titel">{{
                    eintrag.text
                  }}</span>
                  <ul class="om-nav-gruppe__liste" :aria-labelledby="`om-drawer-gruppe-${nummer}`">
                    <li v-for="link in eintrag.eintraege" :key="link.name">
                      <RouterLink :to="menueZiel(link)">{{ link.text }}</RouterLink>
                    </li>
                  </ul>
                </template>
                <RouterLink v-else :to="menueZiel(eintrag)">{{ eintrag.text }}</RouterLink>
              </li>
            </ul>
          </nav>
        </wa-drawer>
      </template>
    </div>

    <main class="om-content">
      <RouterView />
    </main>

    <QuelleSeitenleiste />

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
        <RouterLink :to="{ name: 'ueber' }" class="om-footer__ueber"
          >Über dieses Projekt, Impressum und Datenschutz</RouterLink
        >
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

.om-header {
  justify-content: space-between;
}

.om-site-name {
  font-size: var(--wa-font-size-l);
  font-weight: var(--wa-font-weight-bold);
  text-decoration: none;
  overflow-wrap: anywhere;
}

.om-nav ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: var(--wa-space-xs) var(--wa-space-m);
}

.om-nav a {
  display: inline-flex;
  align-items: center;
  min-height: 44px;
  text-decoration: none;
  overflow-wrap: anywhere;
}

/* Der aktive Eintrag fällt nie nur durch die Farbe auf: Gewicht und Unterstreichung kommen dazu. */
.om-nav a[aria-current='page'] {
  color: var(--wa-color-brand-40);
  font-weight: var(--wa-font-weight-bold);
  text-decoration: underline;
  text-underline-offset: 0.25em;
}

.om-nav-drawer ul {
  flex-direction: column;
  gap: 0;
}

.om-nav-drawer a {
  display: flex;
  width: 100%;
}

.om-nav-gruppe__titel {
  display: flex;
  align-items: center;
  min-height: 44px;
  font-size: var(--wa-font-size-s);
  font-weight: var(--wa-font-weight-bold);
  line-height: var(--wa-line-height-condensed);
  color: var(--wa-color-text-quiet);
}

/* Im Drawer ist die Gruppe nie eingeklappt: die vier Links stehen eingerückt unter der Überschrift. */
.om-nav-drawer .om-nav-gruppe__liste {
  padding-inline-start: var(--wa-space-m);
}

.om-menue-schalter {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 44px;
  min-height: 44px;
  padding: 0;
  border: 1px solid var(--wa-color-surface-border);
  border-radius: var(--wa-border-radius-m);
  background: var(--wa-color-surface-default);
  color: var(--wa-color-text-normal);
  font-size: var(--wa-font-size-l);
  cursor: pointer;
}

.om-content {
  display: block;
  padding: var(--wa-space-l);
}

.om-footer {
  flex-direction: column;
  align-items: flex-start;
  gap: var(--wa-space-2xs);
  font-size: var(--wa-font-size-s);
  font-weight: var(--wa-font-weight-normal);
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

.om-footer__ueber {
  display: inline-flex;
  align-items: center;
  min-height: 44px;
}

.om-extern-icon {
  margin-inline-start: var(--wa-space-2xs);
  vertical-align: -0.125em;
}

@media (max-width: 699px) {
  .om-footer {
    align-items: center;
    text-align: center;
  }
}
</style>
