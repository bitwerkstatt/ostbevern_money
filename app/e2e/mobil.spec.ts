import AxeBuilder from '@axe-core/playwright'
import { expect, test, type Page } from '@playwright/test'

import {
  pruefeEscape,
  pruefeLinkDerAktuellenSeite,
  pruefeLinkEinerAnderenSeite,
} from './menueDrawer'
import { routen } from './routen'
import { befundeTabellenrahmen, oeffneAlleBereiche } from './tabellenrahmen'

// WCAG-Tags des Smoke-Tests (`smoke.spec.ts`); Best-Practice-Regeln wie `landmark-unique` und
// `region` gehören nicht dazu (Web Awesomes eigene `wa-details`-Regionen verletzen sie).
const AXE_TAGS = ['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa']

// Nutzbarkeit bei 360 × 640 (A11Y-03, Projekt `mobil`, nicht im CI-Smoke-Pfad, D-12):
// - kein waagerechtes Scrollen der Seite (`scrollWidth <= innerWidth`),
// - jedes Ziel der Auswahl ist mindestens 44 × 44 px groß,
// und beides auch bei geöffneter Quell-Leiste (`/`) und geöffnetem Menü-Drawer.
//
// Zielauswahl: `.om-quelle-knopf`, `.om-footer a`, `.om-menue-schalter`, `.om-nav-drawer a` und
// alle Schaltflächen im Light-DOM. Ausnahme (WCAG 2.5.8, Ausnahme „Inline“): Textlinks im
// Fließtext, also Links mit der Anzeigeart `inline`, deren umgebender Absatz weiteren Text
// trägt (Fußzeile: „Datenstand … Original-Haushaltsplan“, „Kontakt: …“, „Inspiriert von …“).
// Sie sind Teil des Satzes und lassen sich nicht größer machen, ohne den Text zu zerreißen.
// Alle Verstöße einer Route werden gesammelt, damit ein Lauf jeden Überlauf und jedes zu kleine
// Ziel mit Selektor, Größe und Route nennt.

const MINDESTMASS = 44
const ZIELE = '.om-quelle-knopf, .om-footer a, .om-menue-schalter, .om-nav-drawer a, button'

interface Messung {
  scrollWidth: number
  innerWidth: number
  geprueft: number
  zuKlein: string[]
  ueberlauf: string[]
}

/** Misst Seitenüberlauf und Zielgrößen im aktuellen Zustand der Seite (eine Auswertung im Browser). */
function messe(page: Page, minimum: number): Promise<Messung> {
  return page.evaluate(
    ([auswahl, mindest]) => {
      const beschreibe = (element: Element): string => {
        const klassen = [...element.classList].map((name) => `.${name}`).join('')
        const text = (element.getAttribute('aria-label') ?? element.textContent ?? '')
          .replace(/\s+/g, ' ')
          .trim()
          .slice(0, 40)
        return `${element.tagName.toLowerCase()}${klassen} „${text}“`
      }

      const istInlineImText = (element: Element): boolean => {
        if (element.tagName !== 'A' || getComputedStyle(element).display !== 'inline') {
          return false
        }
        const eltern = element.parentElement
        if (eltern === null) {
          return false
        }
        const rest = (eltern.textContent ?? '').replace(element.textContent ?? '', '')
        return rest.replace(/\s+/g, '').length > 0
      }

      const ziele = new Set(document.querySelectorAll(auswahl))
      const zuKlein: string[] = []
      let geprueft = 0
      for (const element of ziele) {
        if (!element.checkVisibility({ checkVisibilityCSS: true })) {
          continue
        }
        if (element.closest('.om-visually-hidden') !== null || istInlineImText(element)) {
          continue
        }
        const kasten = element.getBoundingClientRect()
        if (kasten.width === 0 && kasten.height === 0) {
          continue
        }
        geprueft += 1
        if (kasten.width < mindest - 0.5 || kasten.height < mindest - 0.5) {
          zuKlein.push(
            `${beschreibe(element)}: ${kasten.width.toFixed(1)} × ${kasten.height.toFixed(1)} px`,
          )
        }
      }

      const breite = document.documentElement.clientWidth
      const ueberlauf: string[] = []
      if (document.documentElement.scrollWidth > window.innerWidth) {
        // Die breitesten Verursacher nennen, damit der Befund auf eine Komponente zeigt.
        for (const element of document.body.querySelectorAll('*')) {
          const kasten = element.getBoundingClientRect()
          if (kasten.right > breite + 0.5 && kasten.width > 0) {
            ueberlauf.push(`${beschreibe(element)} reicht bis ${kasten.right.toFixed(1)} px`)
          }
          if (ueberlauf.length >= 8) {
            break
          }
        }
      }

      return {
        scrollWidth: document.documentElement.scrollWidth,
        innerWidth: window.innerWidth,
        geprueft,
        zuKlein,
        ueberlauf,
      }
    },
    [ZIELE, minimum] as const,
  )
}

/** Fehlertext einer Messung oder `null`, wenn alles stimmt. */
function befund(ort: string, messung: Messung): string | null {
  const meldungen: string[] = []
  if (messung.scrollWidth > messung.innerWidth) {
    meldungen.push(
      `${ort}: Seite scrollt waagerecht (scrollWidth ${String(messung.scrollWidth)} > innerWidth ${String(messung.innerWidth)})`,
      ...messung.ueberlauf.map((zeile) => `  ${zeile}`),
    )
  }
  for (const eintrag of messung.zuKlein) {
    meldungen.push(`${ort}: Ziel unter ${String(MINDESTMASS)} px: ${eintrag}`)
  }
  return meldungen.length === 0 ? null : meldungen.join('\n')
}

function tabellenzeile(ort: string, messung: Messung, ok: boolean): string {
  return `| ${ort} | ${String(messung.scrollWidth)} | ${String(messung.geprueft)} | ${ok ? 'bestanden' : 'FEHLER'} |`
}

async function warteAufRuhe(page: Page): Promise<void> {
  await page.evaluate(() =>
    Promise.all(
      document
        .getAnimations()
        .filter((animation) => animation.effect?.getTiming().iterations !== Infinity)
        .map((animation) => animation.finished.catch(() => undefined)),
    ),
  )
}

test.describe('360 × 640: Überlauf und Zielgröße je Route (A11Y-03)', () => {
  test.beforeEach(({ viewport }) => {
    expect(viewport).toEqual({ width: 360, height: 640 })
  })

  for (const route of routen()) {
    test(`Route ${route.pfad}`, async ({ page }) => {
      await page.goto(`/#${route.pfad}`)
      await expect(page.locator('h1')).toBeVisible()
      await page.waitForLoadState('networkidle')

      // Die Bereiche „Tabelle anzeigen“ sind geschlossen: ihr Inhalt zählt erst, wenn er sichtbar
      // ist. Für die Messung werden alle geöffnet (Eigenschaft statt Klick: auf /glossar sind es
      // Dutzende, und das Öffnen selbst belegt `interaktion.spec.ts`).
      await page.evaluate(() => {
        for (const bereich of document.querySelectorAll('wa-details')) {
          bereich.setAttribute('open', '')
        }
      })
      await page.waitForTimeout(100)
      await warteAufRuhe(page)

      const messung = await messe(page, MINDESTMASS)
      const fehler = befund(route.pfad, messung)
      console.log(tabellenzeile(route.pfad, messung, fehler === null))
      expect(fehler ?? '', fehler ?? '').toBe('')
    })
  }
})

test.describe('Tabellenrahmen bei 360 px (A11Y-01, A11Y-03)', () => {
  test.beforeEach(({ viewport }) => {
    expect(viewport).toEqual({ width: 360, height: 640 })
  })

  for (const route of routen()) {
    test(`Rahmen mit Rolle und genau einem Namen auf ${route.pfad}`, async ({ page }) => {
      await page.goto(`/#${route.pfad}`)
      await expect(page.locator('h1')).toBeVisible()
      await page.waitForLoadState('networkidle')
      await oeffneAlleBereiche(page)

      // Der ResizeObserver der Tabelle setzt Tabstopp und Rolle nach dem Layout: bis zur Ruhe
      // wiederholen, der letzte Befund steht in der Meldung.
      await expect
        .poll(() => befundeTabellenrahmen(page), { message: `Tabellenrahmen auf ${route.pfad}` })
        .toEqual([])
    })

    test(`axe meldet bei geöffneten Bereichen auf ${route.pfad} keinen Verstoß`, async ({
      page,
    }) => {
      // Wie im Smoke-Test: ohne Bewegung blendet Web Awesome nichts ein, sonst sähe axe Text
      // mitten im Einblenden mit halber Deckkraft und meldete Scheinverstöße beim Kontrast.
      await page.emulateMedia({ reducedMotion: 'reduce' })
      await page.goto(`/#${route.pfad}`)
      await expect(page.locator('h1')).toBeVisible()
      await page.waitForLoadState('networkidle')
      await oeffneAlleBereiche(page)
      await warteAufRuhe(page)
      await expect.poll(() => befundeTabellenrahmen(page)).toEqual([])

      const ergebnis = await new AxeBuilder({ page }).withTags(AXE_TAGS).analyze()
      const meldung = ergebnis.violations
        .map(
          (verstoss) =>
            `${verstoss.id} (${verstoss.impact ?? 'ohne Gewicht'}, ${String(verstoss.nodes.length)} Knoten): ${verstoss.nodes
              .slice(0, 3)
              .map((knoten) => `${knoten.target.join(' ')} – ${knoten.any[0]?.message ?? ''}`)
              .join('; ')}`,
        )
        .join('\n')
      expect(meldung, meldung).toBe('')
    })
  }
})

test.describe('Mobiles Menü schließt bei jedem Linkklick (A11Y-02, D-21)', () => {
  test('Link der aktuellen Seite: Drawer zu, aria-expanded false, Fokus auf der Überschrift', async ({
    page,
  }) => {
    await pruefeLinkDerAktuellenSeite(page)
  })

  test('Link einer anderen Seite: Route wechselt, Fokus auf der Überschrift', async ({ page }) => {
    await pruefeLinkEinerAnderenSeite(page)
  })

  test('Escape schließt den Drawer, der Fokus kehrt zum Menüknopf zurück', async ({ page }) => {
    await pruefeEscape(page)
  })
})

test.describe('360 × 640 mit geöffneter Leiste und geöffnetem Menü (A11Y-03)', () => {
  test('mit geöffneter Quell-Leiste auf /', async ({ page }) => {
    await page.goto('/#/')
    await expect(page.locator('h1')).toBeVisible()
    await page
      .getByRole('button', { name: /^Quelle anzeigen: / })
      .first()
      .click()
    const leiste = page.getByRole('dialog', { name: /^Quelle: PDF-Seite/ })
    await expect(leiste).toBeVisible()
    await expect(page.locator('#om-quelle-drawer img.om-quelle-seite__bild')).toBeVisible()
    await warteAufRuhe(page)

    const messung = await messe(page, MINDESTMASS)
    // Die Schaltflächen im Shadow-DOM der Leiste (Schließen) liegen außerhalb der Light-DOM-Suche.
    const schliessen = await leiste.getByRole('button', { name: 'Schließen' }).boundingBox()
    expect(schliessen).not.toBeNull()
    const fehler = [befund('/ (Quell-Leiste offen)', messung)]
    if (
      schliessen !== null &&
      (schliessen.width < MINDESTMASS || schliessen.height < MINDESTMASS)
    ) {
      fehler.push(
        `/ (Quell-Leiste offen): Ziel unter ${String(MINDESTMASS)} px: Schließen-Knopf ${schliessen.width.toFixed(1)} × ${schliessen.height.toFixed(1)} px`,
      )
    }
    const text = fehler.filter((eintrag) => eintrag !== null).join('\n')
    console.log(tabellenzeile('/ mit Quell-Leiste', messung, text === ''))
    expect(text, text).toBe('')
  })

  test('mit geöffnetem Menü-Drawer', async ({ page }) => {
    await page.goto('/#/')
    await expect(page.locator('h1')).toBeVisible()
    await page.getByRole('button', { name: 'Menü öffnen' }).click()
    await expect(page.getByRole('dialog', { name: 'Menü' })).toBeVisible()
    await warteAufRuhe(page)

    const messung = await messe(page, MINDESTMASS)
    const schliessen = await page
      .getByRole('dialog', { name: 'Menü' })
      .getByRole('button', { name: 'Schließen' })
      .boundingBox()
    expect(schliessen).not.toBeNull()
    const fehler = [befund('/ (Menü offen)', messung)]
    if (
      schliessen !== null &&
      (schliessen.width < MINDESTMASS || schliessen.height < MINDESTMASS)
    ) {
      fehler.push(
        `/ (Menü offen): Ziel unter ${String(MINDESTMASS)} px: Schließen-Knopf ${schliessen.width.toFixed(1)} × ${schliessen.height.toFixed(1)} px`,
      )
    }
    // Der Menü-Drawer zeigt alle Links der Liste; die Ziele des Drawers müssen mitgezählt sein.
    const drawerLinks = await page.locator('.om-nav-drawer a').count()
    expect(drawerLinks).toBeGreaterThan(0)
    const text = fehler.filter((eintrag) => eintrag !== null).join('\n')
    console.log(tabellenzeile('/ mit Menü-Drawer', messung, text === ''))
    expect(text, text).toBe('')
  })

  test('eine Querformatseite scrollt nur im eigenen Rahmen, nicht die Seite', async ({ page }) => {
    await page.goto('/#/stellenplan')
    await expect(page.locator('h1')).toBeVisible()
    const bereich = page
      .locator('wa-details')
      .filter({ has: page.locator('.om-quelle-knopf') })
      .first()
    await bereich.locator('summary').click()
    await page
      .locator('table')
      .getByRole('button', { name: /^Quelle anzeigen: / })
      .first()
      .click()
    await expect(page.locator('#om-quelle-drawer img.om-quelle-seite__bild')).toBeVisible()
    await expect(page.locator('#om-quelle-drawer .om-quelle-seite__markierung')).toBeVisible()
    await warteAufRuhe(page)

    const lage = await page.evaluate(() => {
      const rahmen = document.querySelector('#om-quelle-drawer .om-quelle-seite')
      return {
        seite: document.documentElement.scrollWidth,
        fenster: window.innerWidth,
        rahmenBreit: rahmen?.scrollWidth ?? 0,
        rahmenSicht: rahmen?.clientWidth ?? 0,
      }
    })
    const messung = await messe(page, MINDESTMASS)
    console.log(tabellenzeile('/stellenplan mit Quell-Leiste (Querformat)', messung, true))
    expect(lage.seite).toBeLessThanOrEqual(lage.fenster)
    expect(lage.rahmenBreit).toBeGreaterThan(lage.rahmenSicht)
  })
})
