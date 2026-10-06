import { readFileSync } from 'node:fs'

import { expect, test, type Locator, type Page } from '@playwright/test'

// Browser-Beweis des Tracer-Pfads (Plan 07-01): Start-Kachel „Erträge“ -> Quelle anzeigen ->
// Seitenleiste mit Seitenbild und markierter Zeile. Die erwartete Seite steht in
// `quellen.json`, keine Seitenzahl ist getippt.

interface QuellenJson {
  seiten: Record<string, { bild: string; breite: number; hoehe: number }>
  belege: Record<string, { pdf_seite: number; bild: string; bbox: number[] | null }>
}

const quellen: QuellenJson = JSON.parse(
  readFileSync(new URL('../src/data/quellen.json', import.meta.url), 'utf-8'),
)
const ertraege = quellen.belege['ep:GESAMT:ordentliche_ertraege']
if (ertraege === undefined) {
  throw new Error('quellen.json enthält ep:GESAMT:ordentliche_ertraege nicht')
}
const SEITE = ertraege.pdf_seite
const BILD = ertraege.bild
const TITEL = `Quelle: PDF-Seite ${String(SEITE)}`
const ORIGIN = 'http://localhost:4173/'

function ertraegeKnopf(page: Page): Locator {
  return page.getByRole('button', { name: /^Quelle anzeigen: Erträge/ })
}

function seitenleiste(page: Page): Locator {
  return page.getByRole('dialog', { name: TITEL })
}

interface Kasten {
  links: number
  oben: number
  rechts: number
  unten: number
}

interface Lage {
  bild: Kasten
  markierung: Kasten
  hoehe: number
}

/** Seitenzahl am Ende eines Knopfnamens „Quelle anzeigen: …, PDF-Seite {n}“. */
async function seiteDesKnopfs(knopf: Locator): Promise<number> {
  const name = (await knopf.getAttribute('aria-label')) ?? ''
  const treffer = /PDF-Seite (\d+)$/.exec(name)
  expect(treffer, `Knopfname ohne Seitenzahl: ${name}`).not.toBeNull()
  return Number(treffer?.[1])
}

/**
 * Wartet, bis die Seitenleiste ruht: Bild geladen und alle endlichen Animationen (das
 * Einfahren der Leiste) beendet. Erst danach haben Bild und Markierung ihre endgültige Lage.
 * Die Flackerursache des ersten Tests (07-01) war, dass beide Rechtecke zu verschiedenen
 * Zeitpunkten der Einfahranimation gemessen wurden.
 */
async function warteAufRuhe(page: Page): Promise<void> {
  const bild = page.locator('#om-quelle-drawer img.om-quelle-seite__bild')
  await expect
    .poll(() => bild.evaluate((el) => (el instanceof HTMLImageElement ? el.naturalWidth : 0)))
    .toBeGreaterThan(0)
  await page.evaluate(() =>
    Promise.all(
      document
        .getAnimations()
        .filter((animation) => animation.effect?.getTiming().iterations !== Infinity)
        .map((animation) => animation.finished.catch(() => undefined)),
    ),
  )
}

/** Liest Bild- und Markierungsrechteck in einem Schritt im selben Frame. */
function messeLage(page: Page): Promise<Lage | null> {
  return page.evaluate(() => {
    const bild = document.querySelector('#om-quelle-drawer img.om-quelle-seite__bild')
    const markierung = document.querySelector('#om-quelle-drawer .om-quelle-seite__markierung')
    if (bild === null || markierung === null) {
      return null
    }
    const b = bild.getBoundingClientRect()
    const m = markierung.getBoundingClientRect()
    return {
      bild: { links: b.left, oben: b.top, rechts: b.right, unten: b.bottom },
      markierung: { links: m.left, oben: m.top, rechts: m.right, unten: m.bottom },
      hoehe: m.height,
    }
  })
}

function liegtImBild(lage: Lage | null): boolean {
  if (lage === null) {
    return false
  }
  const { bild, markierung } = lage
  return (
    lage.hoehe > 0 &&
    markierung.links >= bild.links - 1 &&
    markierung.oben >= bild.oben - 1 &&
    markierung.rechts <= bild.rechts + 1 &&
    markierung.unten <= bild.unten + 1
  )
}

/** Beweist, dass die Markierung innerhalb des Seitenbildes liegt, ohne Zeitabhängigkeit. */
async function pruefeMarkierungImBild(page: Page): Promise<void> {
  await expect(page.locator('#om-quelle-drawer .om-quelle-seite__markierung')).toBeVisible()
  await warteAufRuhe(page)
  await expect.poll(async () => liegtImBild(await messeLage(page))).toBe(true)
}

test.describe('Quelle anzeigen an der Start-Kachel Erträge', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/#/')
    await expect(page.locator('h1')).toBeVisible()
  })

  test('Klick öffnet die Seitenleiste mit Bild und Markierung, Escape gibt den Fokus zurück', async ({
    page,
  }) => {
    const knopf = ertraegeKnopf(page)
    await expect(knopf).toBeVisible()
    await knopf.click()

    await expect(seitenleiste(page)).toBeVisible()

    const bild = page.locator('#om-quelle-drawer img.om-quelle-seite__bild')
    await expect(bild).toHaveAttribute('src', new RegExp(`quellen/${BILD}$`))
    await pruefeMarkierungImBild(page)

    await page.keyboard.press('Escape')
    await expect(seitenleiste(page)).toBeHidden()
    await expect(knopf).toBeFocused()
  })

  test('Enter und Leertaste öffnen die Seitenleiste, der Schließen-Knopf gibt den Fokus zurück', async ({
    page,
  }) => {
    const knopf = ertraegeKnopf(page)
    await knopf.focus()

    await page.keyboard.press('Enter')
    await expect(seitenleiste(page)).toBeVisible()
    await page.keyboard.press('Escape')
    await expect(seitenleiste(page)).toBeHidden()
    await expect(knopf).toBeFocused()

    await page.keyboard.press('Space')
    await expect(seitenleiste(page)).toBeVisible()
    await seitenleiste(page).getByRole('button', { name: 'Schließen' }).click()
    await expect(seitenleiste(page)).toBeHidden()
    await expect(knopf).toBeFocused()
  })

  test('beim Öffnen liegt der Fokus im Dialog der Seitenleiste, der erste Tab-Stopp ist Schließen', async ({
    page,
  }) => {
    await ertraegeKnopf(page).click()
    await expect(seitenleiste(page)).toBeVisible()
    await warteAufRuhe(page)

    // Web Awesome fokussiert den benannten Dialog selbst (Standard, 07-01); der Fokus verlässt
    // die Seitenleiste nicht. Der Test hält die gemessene Reihenfolge fest.
    const aktiv = await page.evaluate(() => {
      const drawer = document.querySelector('#om-quelle-drawer')
      const tiefstes = (wurzel: Document | ShadowRoot): Element | null => {
        const element = wurzel.activeElement
        return element?.shadowRoot ? (tiefstes(element.shadowRoot) ?? element) : element
      }
      const element = tiefstes(document)
      return {
        imDrawer: drawer !== null && (drawer.shadowRoot?.contains(element) ?? false),
        etikett: element?.getAttribute('aria-label') ?? element?.getAttribute('part') ?? '',
        tag: element?.tagName ?? '',
      }
    })
    expect(aktiv.imDrawer, JSON.stringify(aktiv)).toBe(true)

    await page.keyboard.press('Tab')
    await expect(seitenleiste(page).getByRole('button', { name: 'Schließen' })).toBeFocused()
  })

  test('zeigt Wertzeile, Hinweis zum berechneten Wert und den seitengenauen Original-Link', async ({
    page,
  }) => {
    await ertraegeKnopf(page).click()
    await expect(seitenleiste(page)).toBeVisible()

    const leiste = page.locator('#om-quelle-drawer')
    await expect(leiste.getByText('Berechneter Wert')).toBeVisible()
    await expect(leiste.getByText('Dieser Wert steht nicht im PDF.')).toBeVisible()
    const link = leiste.getByRole('link', {
      name: `Seite ${String(SEITE)} im Original-PDF öffnen`,
    })
    await expect(link).toHaveAttribute('href', new RegExp(`#page=${String(SEITE)}$`))
    await expect(link).toHaveAttribute('target', '_blank')
    await expect(link).toHaveAttribute('rel', 'noopener noreferrer')
  })

  test('ersetzt das Bild bei einem Ladefehler durch den Hinweis mit Link ins Original', async ({
    page,
  }) => {
    await page.route('**/quellen/*.webp', (route) => route.abort())
    await ertraegeKnopf(page).click()
    await expect(seitenleiste(page)).toBeVisible()

    const leiste = page.locator('#om-quelle-drawer')
    await expect(
      leiste.getByText('Die Seite konnte nicht geladen werden. Du findest sie im Original-PDF.'),
    ).toBeVisible()
    await expect(leiste.locator('.om-quelle-seite__markierung')).toHaveCount(0)
    await expect(leiste.getByRole('link', { name: /im Original-PDF öffnen/ })).toBeVisible()
  })

  test('setzt bei reduzierter Bewegung Übergänge und Drawer-Dauern auf null', async ({ page }) => {
    await page.emulateMedia({ reducedMotion: 'reduce' })
    const werte = await page.evaluate(() => {
      const stil = (element: Element | null, name: string) =>
        element === null ? null : getComputedStyle(element).getPropertyValue(name).trim()
      const drawer = document.querySelector('#om-quelle-drawer')
      return {
        schnell: stil(document.documentElement, '--wa-transition-fast'),
        normal: stil(document.documentElement, '--wa-transition-normal'),
        langsam: stil(document.documentElement, '--wa-transition-slow'),
        zeigen: stil(drawer, '--show-duration'),
        verbergen: stil(drawer, '--hide-duration'),
      }
    })
    // Chromium kann `0ms` als `0s` zurückgeben; entscheidend ist eine Dauer mit Einheit und Wert 0.
    for (const [name, wert] of Object.entries(werte)) {
      expect(wert, name).toMatch(/^0(ms|s)$/)
    }
  })

  test('alle Anfragen gehen an den Preview-Server (keine Drittanbieter)', async ({ page }) => {
    const anfragen: string[] = []
    page.on('request', (anfrage) => anfragen.push(anfrage.url()))

    await ertraegeKnopf(page).click()
    await expect(seitenleiste(page)).toBeVisible()
    const bild = page.locator('#om-quelle-drawer img.om-quelle-seite__bild')
    await expect
      .poll(() => bild.evaluate((el) => (el instanceof HTMLImageElement ? el.naturalWidth : 0)))
      .toBeGreaterThan(0)

    expect(anfragen.length).toBeGreaterThan(0)
    expect(anfragen.filter((url) => !url.startsWith(ORIGIN))).toEqual([])
  })
})

// Weitere Auslöser und Belegarten (Plan 07-09, UI-02, D-03). Erwartete Seiten stehen nie im
// Quelltext: sie kommen aus dem Namen des Knopfs und werden gegen `quellen.json` geprüft.

function belegeDerSeite(seite: number) {
  return Object.entries(quellen.belege).filter(([, beleg]) => beleg.pdf_seite === seite)
}

test.describe('Weitere Auslöser der Seitenleiste', () => {
  test('ein Tabellenzeilen-Knopf auf /ausgaben öffnet sich mit Enter und gibt den Fokus zurück', async ({
    page,
  }) => {
    await page.goto('/#/ausgaben')
    await expect(page.locator('h1')).toBeVisible()
    const knopf = page
      .locator('table')
      .getByRole('button', { name: /^Quelle anzeigen: .*PDF-Seite \d+$/ })
      .first()
    await expect(knopf).toBeVisible()
    const seite = await seiteDesKnopfs(knopf)
    expect(
      belegeDerSeite(seite).length,
      `Seite ${String(seite)} fehlt in quellen.json`,
    ).toBeGreaterThan(0)

    await knopf.focus()
    await page.keyboard.press('Enter')
    await expect(
      page.getByRole('dialog', { name: `Quelle: PDF-Seite ${String(seite)}` }),
    ).toBeVisible()
    await expect(
      page.locator('#om-quelle-drawer').getByRole('link', {
        name: `Seite ${String(seite)} im Original-PDF öffnen`,
      }),
    ).toBeVisible()

    await page.keyboard.press('Escape')
    await expect(page.locator('#om-quelle-drawer')).toBeHidden()
    await expect(knopf).toBeFocused()
  })

  test('eine Stellenplan-Zeile öffnet eine Querformatseite mit der Markierung im Bild', async ({
    page,
  }) => {
    await page.goto('/#/stellenplan')
    await expect(page.locator('h1')).toBeVisible()
    // Die Stellentabellen stehen in geschlossenen Bereichen „Tabelle anzeigen“; geöffnet wird der
    // erste Bereich, dessen Tabelle Quelle-Knöpfe trägt.
    const bereich = page
      .locator('wa-details')
      .filter({ has: page.locator('.om-quelle-knopf') })
      .first()
    await bereich.locator('summary').click()
    await expect(bereich).toHaveAttribute('open', '')
    const knopf = page
      .locator('table')
      .getByRole('button', { name: /^Quelle anzeigen: .*PDF-Seite \d+$/ })
      .first()
    await expect(knopf).toBeVisible()
    const seite = await seiteDesKnopfs(knopf)
    const masse = quellen.seiten[String(seite)]
    expect(masse, `Seite ${String(seite)} fehlt unter seiten in quellen.json`).toBeDefined()
    expect(masse?.breite ?? 0).toBeGreaterThan(masse?.hoehe ?? Infinity)

    await knopf.click()
    await expect(
      page.getByRole('dialog', { name: `Quelle: PDF-Seite ${String(seite)}` }),
    ).toBeVisible()

    const bild = page.locator('#om-quelle-drawer img.om-quelle-seite__bild')
    await expect
      .poll(() =>
        bild.evaluate((el) =>
          el instanceof HTMLImageElement && el.naturalHeight > 0
            ? el.naturalWidth / el.naturalHeight
            : 0,
        ),
      )
      .toBeGreaterThan(1)
    await pruefeMarkierungImBild(page)
  })

  test('ein Beleg nur mit Seite nennt „Zeile nicht automatisch markiert“ und zeichnet keine Markierung', async ({
    page,
  }) => {
    await page.goto('/#/stellenplan')
    await expect(page.locator('h1')).toBeVisible()
    // Die Kacheln der Stellenplan-Seite zeigen die Seite als Ganzes (kein Zeilenrechteck).
    const knopf = page
      .getByRole('button', { name: /^Quelle anzeigen: Stellen .*PDF-Seite \d+$/ })
      .first()
    await expect(knopf).toBeVisible()
    const seite = await seiteDesKnopfs(knopf)
    const beleg = quellen.belege[`seite:${String(seite)}`]
    expect(beleg, `seite:${String(seite)} fehlt in quellen.json`).toBeDefined()
    expect(beleg?.bbox).toBeNull()

    await knopf.click()
    await expect(
      page.getByRole('dialog', { name: `Quelle: PDF-Seite ${String(seite)}` }),
    ).toBeVisible()
    const leiste = page.locator('#om-quelle-drawer')
    await expect(leiste.getByText('Zeile nicht automatisch markiert')).toBeVisible()
    await expect(leiste.locator('img.om-quelle-seite__bild')).toBeVisible()
    await expect(leiste.locator('.om-quelle-seite__markierung')).toHaveCount(0)
  })

  test('eine Pro-Kopf-Kachel zeigt „Berechneter Wert“ mit der Herleitung', async ({ page }) => {
    await page.goto('/#/')
    await expect(page.locator('h1')).toBeVisible()
    const knopf = page
      .getByRole('button', { name: /^Quelle anzeigen: .* pro Einwohner, PDF-Seite \d+$/ })
      .first()
    await expect(knopf).toBeVisible()
    const seite = await seiteDesKnopfs(knopf)

    await knopf.click()
    await expect(
      page.getByRole('dialog', { name: `Quelle: PDF-Seite ${String(seite)}` }),
    ).toBeVisible()
    const leiste = page.locator('#om-quelle-drawer')
    await expect(leiste.getByText('Berechneter Wert')).toBeVisible()
    await expect(
      leiste.getByText(/Dieser Wert steht nicht im PDF\. Er wird berechnet: /),
    ).toBeVisible()
  })
})
