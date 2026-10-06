import { nextTick } from 'vue'
import {
  START_LOCATION,
  createRouter,
  createWebHashHistory,
  type RouteLocationNormalized,
} from 'vue-router'

import AusgabenPage from '@/pages/AusgabenPage.vue'
import EinnahmenPage from '@/pages/EinnahmenPage.vue'
import EntwicklungPage from '@/pages/EntwicklungPage.vue'
import GeldflussPage from '@/pages/GeldflussPage.vue'
import GlossarPage from '@/pages/GlossarPage.vue'
import InvestitionenPage from '@/pages/InvestitionenPage.vue'
import ProduktPage from '@/pages/ProduktPage.vue'
import RatEntscheidetPage from '@/pages/RatEntscheidetPage.vue'
import StartPage from '@/pages/StartPage.vue'
import StellenplanPage from '@/pages/StellenplanPage.vue'
import UeberPage from '@/pages/UeberPage.vue'
import { ansagen } from '@/lib/ansage'
import { findeProdukt } from '@/lib/ansicht'
import { elementFuerHash, sprungPosition } from '@/lib/sprungziel'

declare module 'vue-router' {
  interface RouteMeta {
    /** Seitentitel für `document.title` und die Ansage nach einem Seitenwechsel (D-13). */
    titel: string
  }
}

const SEITENNAME = 'Ostbevern Money'
const PRODUKT_UNBEKANNT = 'Dieses Produkt gibt es nicht'

/** Titel der Zielseite; die Produktseite trägt den Produktnamen (bzw. den Fehlertitel). */
function seitentitel(route: RouteLocationNormalized): string {
  if (route.name === 'produkt') {
    return findeProdukt(route.params.code)?.name ?? PRODUKT_UNBEKANNT
  }
  return route.meta.titel
}

function fokussiere(ziel: HTMLElement | null, ohneScrollen: boolean) {
  if (ziel === null) {
    return
  }
  if (!ziel.hasAttribute('tabindex')) {
    ziel.setAttribute('tabindex', '-1')
  }
  ziel.focus({ preventScroll: ohneScrollen })
}

const router = createRouter({
  history: createWebHashHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'start', component: StartPage, meta: { titel: 'Start' } },
    {
      path: '/einnahmen',
      name: 'einnahmen',
      component: EinnahmenPage,
      meta: { titel: 'Woher kommt das Geld?' },
    },
    {
      path: '/ausgaben',
      name: 'ausgaben',
      component: AusgabenPage,
      meta: { titel: 'Wofür wird das Geld ausgegeben?' },
    },
    {
      path: '/produkt/:code',
      name: 'produkt',
      component: ProduktPage,
      meta: { titel: 'Produkt' },
    },
    {
      path: '/geldfluss',
      name: 'geldfluss',
      component: GeldflussPage,
      meta: { titel: 'Vom Ertrag zur Ausgabe' },
    },
    {
      path: '/entwicklung',
      name: 'entwicklung',
      component: EntwicklungPage,
      meta: { titel: 'Wie entwickelt sich der Haushalt?' },
    },
    {
      path: '/investitionen',
      name: 'investitionen',
      component: InvestitionenPage,
      meta: { titel: 'Investitionen und Schulden' },
    },
    {
      path: '/rat-entscheidet',
      name: 'rat-entscheidet',
      component: RatEntscheidetPage,
      meta: { titel: 'Worüber entscheidet der Rat?' },
    },
    {
      path: '/stellenplan',
      name: 'stellenplan',
      component: StellenplanPage,
      meta: { titel: 'Wie viele Stellen hat die Verwaltung?' },
    },
    {
      path: '/glossar',
      name: 'glossar',
      component: GlossarPage,
      meta: { titel: 'Glossar' },
    },
    {
      path: '/ueber',
      name: 'ueber',
      component: UeberPage,
      meta: { titel: 'Über dieses Projekt' },
    },
    { path: '/:pathMatch(.*)*', redirect: { name: 'start' } },
  ],
  // Mit Fragment zum Element scrollen (Glossar-Sprungziele), sonst nach oben. Reine
  // Query-Wechsel (Jahr, Modus, Drilldown) lassen die Scrollposition in Ruhe. Der Versatz
  // unter der festen Kopfzeile kommt aus dem scroll-margin-top des Ziels (lib/sprungziel.ts).
  scrollBehavior(to, from, gespeichert) {
    return sprungPosition(to, from, gespeichert)
  },
})

// Nach jedem Seitenwechsel: Titel, Fokus und höfliche Ansage (D-13). Ein reiner
// Query-Wechsel (gleicher Pfad, kein Fragment) ändert nichts: der Fokus bleibt am Steuerelement.
router.afterEach(async (to, from) => {
  const titel = seitentitel(to)
  if (from === START_LOCATION) {
    // Erster Aufruf: nur den Titel setzen, Fokus und Ansage übernimmt der Browser.
    document.title = `${titel} – ${SEITENNAME}`
    return
  }
  if (to.path === from.path && !to.hash) {
    return
  }
  document.title = `${titel} – ${SEITENNAME}`
  await nextTick()
  const hashZiel = elementFuerHash(to.hash)
  if (hashZiel !== null) {
    // Gescrollt hat bereits scrollBehavior; der Fokus soll nicht erneut springen.
    fokussiere(hashZiel, true)
  } else {
    // Ohne (oder mit unbekanntem) Fragment: Fokus auf die Überschrift der neuen Seite.
    fokussiere(document.querySelector('h1'), false)
  }
  ansagen(`Seite ${titel} geladen`)
})

export default router
