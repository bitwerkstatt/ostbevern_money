import AxeBuilder from '@axe-core/playwright'
import { expect, test, type Page } from '@playwright/test'

import { routen, type Route } from './routen'

// Smoke-Test des Produktions-Builds (QUAL-02, Plan 07-11, D-11 bis D-13): jede Route aus
// `routen()` (Menü, Fußzeile und Produktseite, nichts davon getippt) wird im Desktop-Fenster
// geöffnet und geprüft auf
// - sichtbare Überschrift,
// - keine Konsolenmeldung der Art error oder warning und keinen pageerror (nichts gefiltert),
// - ausschließlich Anfragen an den Preview-Server und keine Antwort mit Status ab 400
//   (stützt die Datenschutzaussage „keine Drittanbieter“),
// - kein ".invalid" im Dokument (Platzhalterkontakt, T-07-27),
// - Diagramme mit Daten (Chart-Routen erkennt der Test an `.om-base-chart`, keine Liste von
//   Hand), auf der Produktseite Tabellen mit mindestens einer Zeile,
// - null axe-Verstöße gegen WCAG 2.0/2.1 A und AA (A11Y-02, Kontrast eingeschlossen).
//
// Axe-Regeln werden nicht abgeschaltet, Konsolenmeldungen nicht gefiltert. Ein Befund wird an
// seiner Ursache behoben (Komponente, Token, Markup), nicht hier.

const ORIGIN = 'http://localhost:4173/'

const AXE_TAGS = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']

/**
 * Wartet, bis die Seite ruht: Netz still, jedes Diagramm aus dem Ladezustand heraus (gezeichnet
 * oder leer) und alle endlichen CSS-Animationen beendet. Erst dann sind Farben und Größen für
 * axe endgültig.
 */
async function warteAufRuhe(page: Page): Promise<void> {
  await page.waitForLoadState('networkidle')
  await expect(page.locator('h1')).toBeVisible()
  await expect
    .poll(
      () =>
        page.evaluate(() =>
          [...document.querySelectorAll('.om-base-chart')].every((karte) => {
            if (karte.querySelector('wa-skeleton') !== null) {
              return false
            }
            // Leer- und Fehlerzustand haben keinen Diagrammcontainer; sie meldet der Datentest.
            if (karte.querySelector('.om-base-chart__chart') === null) {
              return true
            }
            const flaeche = karte.querySelector(
              '.om-base-chart__chart canvas, .om-base-chart__chart svg',
            )
            return flaeche instanceof Element && flaeche.getBoundingClientRect().width > 0
          }),
        ),
      { message: 'Diagramme sind gezeichnet' },
    )
    .toBe(true)
  await page.evaluate(() =>
    Promise.all(
      document
        .getAnimations()
        .filter((animation) => animation.effect?.getTiming().iterations !== Infinity)
        .map((animation) => animation.finished.catch(() => undefined)),
    ),
  )
}

/** Öffnet alle `wa-details`, damit auch deren Tabellen in die axe-Prüfung kommen. */
async function oeffneAlleBereiche(page: Page): Promise<void> {
  await page.evaluate(async () => {
    const bereiche = [...document.querySelectorAll('wa-details')]
    for (const bereich of bereiche) {
      bereich.setAttribute('open', '')
    }
    // Zwei Frames, damit Web Awesome auf das Attribut reagiert und seine Übergänge angelegt hat.
    await new Promise((fertig) => requestAnimationFrame(() => requestAnimationFrame(fertig)))
    await Promise.all(
      document
        .getAnimations()
        .filter((animation) => animation.effect?.getTiming().iterations !== Infinity)
        .map((animation) => animation.finished.catch(() => undefined)),
    )
  })
}

interface AxeBefund {
  id: string
  wirkung: string | null | undefined
  anzahl: number
  ziele: string[]
  hinweis: string
}

/** Axe-Verstöße einer Seite in einer Form, die in der Fehlermeldung Regel und Element nennt. */
async function axeBefunde(page: Page): Promise<AxeBefund[]> {
  const ergebnis = await new AxeBuilder({ page }).withTags(AXE_TAGS).analyze()
  return ergebnis.violations.map((verstoss) => ({
    id: verstoss.id,
    wirkung: verstoss.impact,
    anzahl: verstoss.nodes.length,
    ziele: verstoss.nodes.slice(0, 5).map((knoten) => knoten.target.join(' >> ')),
    hinweis: verstoss.nodes[0]?.failureSummary ?? verstoss.help,
  }))
}

interface Sammler {
  meldungen: string[]
  fremd: string[]
  fehlerantworten: string[]
}

/** Hängt Beobachter an die Seite, bevor sie geladen wird. */
function beobachte(page: Page): Sammler {
  const sammler: Sammler = { meldungen: [], fremd: [], fehlerantworten: [] }
  page.on('console', (nachricht) => {
    if (nachricht.type() === 'error' || nachricht.type() === 'warning') {
      sammler.meldungen.push(`console.${nachricht.type()}: ${nachricht.text()}`)
    }
  })
  page.on('pageerror', (fehler) => {
    sammler.meldungen.push(`pageerror: ${fehler.message}`)
  })
  page.on('request', (anfrage) => {
    if (!anfrage.url().startsWith(ORIGIN)) {
      sammler.fremd.push(anfrage.url())
    }
  })
  page.on('response', (antwort) => {
    if (antwort.status() >= 400) {
      sammler.fehlerantworten.push(`${String(antwort.status())} ${antwort.url()}`)
    }
  })
  return sammler
}

function istProdukt(route: Route): boolean {
  return route.name === 'produkt'
}

for (const route of routen()) {
  test.describe(`Smoke ${route.pfad}`, () => {
    test('rendert ohne Konsolenmeldung, Fremdanfrage oder Platzhalter, mit Daten', async ({
      page,
    }) => {
      const sammler = beobachte(page)
      await page.goto(`/#${route.pfad}`)
      await warteAufRuhe(page)

      // Konsole, Netz (D-11, T-07-26): nichts gefiltert.
      expect(sammler.meldungen, `${route.pfad}: Konsolenmeldungen`).toEqual([])
      expect(sammler.fremd, `${route.pfad}: Anfragen außerhalb von ${ORIGIN}`).toEqual([])
      expect(sammler.fehlerantworten, `${route.pfad}: Antworten ab Status 400`).toEqual([])

      // Kein Platzhalterkontakt im Dokument (T-07-27).
      const html = await page.content()
      expect(html.includes('.invalid'), `${route.pfad}: Dokument enthält ".invalid"`).toBe(false)

      // Diagramme: jedes trägt Daten (data-om-datenpunkte > 0), keines ist leer oder fehlerhaft.
      const diagramme = await page.locator('.om-base-chart').count()
      if (diagramme > 0) {
        const mitDaten = await page.evaluate(
          () =>
            [...document.querySelectorAll('.om-base-chart__chart[data-om-datenpunkte]')].filter(
              (container) => Number(container.getAttribute('data-om-datenpunkte')) > 0,
            ).length,
        )
        expect(
          mitDaten,
          `${route.pfad}: ${String(diagramme)} Diagramme, davon ${String(mitDaten)} mit Daten`,
        ).toBe(diagramme)
        expect(mitDaten).toBeGreaterThanOrEqual(1)
      }

      // Produktseite: nur Tabellen, jede mit mindestens einer Zeile (D-12).
      if (istProdukt(route)) {
        const tabellen = await page.evaluate(() =>
          [...document.querySelectorAll('.om-tabelle-rahmen')].map(
            (rahmen) => rahmen.querySelectorAll('tbody tr').length,
          ),
        )
        expect(tabellen.length, `${route.pfad}: Zahl der Tabellen`).toBeGreaterThan(0)
        expect(
          tabellen.filter((zeilen) => zeilen < 1).length,
          `${route.pfad}: Tabellen ohne Zeile (Zeilen je Tabelle: ${tabellen.join(', ')})`,
        ).toBe(0)
      }
    })

    test('axe: keine Verstöße gegen WCAG 2.0/2.1 A und AA', async ({ page }) => {
      await page.goto(`/#${route.pfad}`)
      await warteAufRuhe(page)
      expect(await axeBefunde(page), `${route.pfad}: axe-Verstöße`).toEqual([])
    })

    test('axe: auch mit geöffneten Bereichen (Tabellen in wa-details)', async ({ page }) => {
      // Mit reduzierter Bewegung öffnen die Bereiche ohne Einblenden (Plan 07-09); sonst misst
      // axe Text mitten im Einblenden mit halber Deckkraft und meldet Scheinverstöße.
      await page.emulateMedia({ reducedMotion: 'reduce' })
      await page.goto(`/#${route.pfad}`)
      await warteAufRuhe(page)
      await oeffneAlleBereiche(page)
      expect(
        await axeBefunde(page),
        `${route.pfad}: axe-Verstöße bei geöffneten Bereichen`,
      ).toEqual([])
    })
  })
}
