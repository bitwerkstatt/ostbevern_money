import { readFileSync } from 'node:fs'

import { expect, test, type Locator, type Page } from '@playwright/test'

// Browser-Beweis des Tracer-Pfads (Plan 07-01): Start-Kachel „Erträge“ -> Quelle anzeigen ->
// Seitenleiste mit Seitenbild und markierter Zeile. Die erwartete Seite steht in
// `quellen.json`, keine Seitenzahl ist getippt.

interface QuellenJson {
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
    await expect
      .poll(() => bild.evaluate((el) => (el instanceof HTMLImageElement ? el.naturalWidth : 0)))
      .toBeGreaterThan(0)

    const markierung = page.locator('#om-quelle-drawer .om-quelle-seite__markierung')
    await expect(markierung).toBeVisible()
    const markierungBox = await markierung.boundingBox()
    const bildBox = await bild.boundingBox()
    expect(markierungBox).not.toBeNull()
    expect(bildBox).not.toBeNull()
    if (markierungBox === null || bildBox === null) {
      return
    }
    expect(markierungBox.height).toBeGreaterThan(0)
    expect(markierungBox.x).toBeGreaterThanOrEqual(bildBox.x - 1)
    expect(markierungBox.y).toBeGreaterThanOrEqual(bildBox.y - 1)
    expect(markierungBox.x + markierungBox.width).toBeLessThanOrEqual(bildBox.x + bildBox.width + 1)
    expect(markierungBox.y + markierungBox.height).toBeLessThanOrEqual(
      bildBox.y + bildBox.height + 1,
    )

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
