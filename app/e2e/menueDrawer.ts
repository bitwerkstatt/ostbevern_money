import { expect, type Locator, type Page } from '@playwright/test'

import { menueLinks } from '../src/lib/menue'

// Gemeinsame Fälle für den mobilen Menü-Drawer bei 360 px (A11Y-02, D-21). `mobil.spec.ts`
// führt sie im Projekt `mobil` aus, `interaktion.spec.ts` spiegelt sie in das CI-Projekt (das
// Projekt `mobil` läuft nicht in der CI). Linknamen und Routen stammen aus `MENUE`, nichts davon
// ist getippt.

const links = menueLinks()
const AKTUELL = links.find((link) => link.name === 'einnahmen')
const ANDERE = links.find((link) => link.name === 'ausgaben')
if (AKTUELL === undefined || ANDERE === undefined) {
  throw new Error('MENUE enthält die Routen einnahmen und ausgaben nicht')
}

function schalter(page: Page): Locator {
  return page.getByRole('button', { name: 'Menü öffnen' })
}

function drawerLink(page: Page, text: string): Locator {
  return page.locator('#om-menue-drawer').getByRole('link', { name: text, exact: true })
}

async function oeffneMenue(page: Page): Promise<void> {
  await page.goto(`/#/${AKTUELL?.name ?? ''}`)
  await expect(page.locator('h1')).toBeVisible()
  await schalter(page).click()
  await expect(page.getByRole('dialog', { name: 'Menü' })).toBeVisible()
}

/** Der Fokus steht (nach einem Makrotask von `wa-drawer`) auf der h1 der Seite. */
async function erwarteFokusAufUeberschrift(page: Page): Promise<void> {
  await expect
    .poll(() =>
      page.evaluate(() => ({
        tag: document.activeElement?.tagName ?? '',
        istUeberschrift: document.activeElement === document.querySelector('h1'),
      })),
    )
    .toEqual({ tag: 'H1', istUeberschrift: true })
}

/** Link der aktuellen Seite: der Drawer schließt, der Fokus steht auf der h1. */
export async function pruefeLinkDerAktuellenSeite(page: Page): Promise<void> {
  await oeffneMenue(page)
  await drawerLink(page, AKTUELL?.text ?? '').click()

  await expect(page.getByRole('dialog', { name: 'Menü' })).toBeHidden()
  await expect(schalter(page)).toHaveAttribute('aria-expanded', 'false')
  await erwarteFokusAufUeberschrift(page)
  await expect(schalter(page)).not.toBeFocused()
}

/** Link einer anderen Seite: die Route wechselt, der Fokus steht ebenfalls auf der h1. */
export async function pruefeLinkEinerAnderenSeite(page: Page): Promise<void> {
  await oeffneMenue(page)
  const vorher = await page.locator('h1').innerText()
  await drawerLink(page, ANDERE?.text ?? '').click()

  await expect(page).toHaveURL(new RegExp(`#/${ANDERE?.name ?? ''}(\\?|$)`))
  await expect.poll(() => page.locator('h1').innerText()).not.toBe(vorher)
  await expect(page.getByRole('dialog', { name: 'Menü' })).toBeHidden()
  await expect(schalter(page)).toHaveAttribute('aria-expanded', 'false')
  await erwarteFokusAufUeberschrift(page)
}

/** Escape schließt den Drawer und gibt den Fokus an den Menüknopf zurück. */
export async function pruefeEscape(page: Page): Promise<void> {
  await oeffneMenue(page)
  await page.keyboard.press('Escape')

  await expect(page.getByRole('dialog', { name: 'Menü' })).toBeHidden()
  await expect(schalter(page)).toHaveAttribute('aria-expanded', 'false')
  await expect(schalter(page)).toBeFocused()
}

/**
 * Ctrl/Cmd-Klick auf einen Link öffnet ihn in einem neuen Tab und schließt den Drawer NICHT.
 * Der Fokus bleibt beim Link (oder im Drawer), nicht auf der h1 (WR-02, A11Y-02).
 */
export async function pruefeLinkMitZusatztaste(
  page: Page,
  modifier: 'ControlOrMeta' | 'Shift',
): Promise<void> {
  await oeffneMenue(page)
  const link = drawerLink(page, ANDERE?.text ?? '')

  // Mit Zusatztaste klicken: öffnet einen neuen Tab, navigiert hier nicht
  const newPagePromise = page.context().waitForEvent('page')
  await link.click({ modifiers: [modifier] })
  // Neue Seite akzeptieren und schließen, um kein Leck zu erzeugen
  const newPage = await newPagePromise
  await newPage.close()

  // Der Drawer bleibt offen (ist nicht geschlossen)
  await expect(page.getByRole('dialog', { name: 'Menü' })).toBeVisible()
  // aria-expanded bleibt 'true'
  await expect(schalter(page)).toHaveAttribute('aria-expanded', 'true')
  // Der Fokus steht NICHT auf der h1
  const aktiv = await page.evaluate(() => ({
    tag: document.activeElement?.tagName ?? '',
    istUeberschrift: document.activeElement === document.querySelector('h1'),
  }))
  expect(aktiv.istUeberschrift).toBe(false)
}
