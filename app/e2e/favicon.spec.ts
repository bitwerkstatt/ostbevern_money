import { expect, test } from '@playwright/test'

// Favicon-Prüfung des Produktions-Builds (Quick-Aufgabe 261010-r8z): Die App trägt ein eigenes
// Haushalts-Motiv als einziges Icon. Geprüft wird
// - genau ein Icon-Link mit Typ image/svg+xml,
// - ein relativer href (./…), damit das Icon unter jedem GitHub-Pages-Unterpfad gefunden wird,
// - gleicher Ursprung (keine Drittanbieter-Anfrage), Status 200 und passender Content-Type,
// - ein in sich geschlossenes SVG (keine Schrift, kein Script, kein Stil, keine Verweise),
// - dass der Browser das SVG fehlerfrei mit 16 × 16 px dekodiert.
// Warum es nur das SVG gibt (kein ICO, PNG oder apple-touch-icon), steht in der SUMMARY der
// Aufgabe 261010-r8z.

const ORIGIN = 'http://localhost:4173/'

// Bausteine, die in einem in sich geschlossenen Favicon nichts verloren haben.
const VERBOTENE_BAUSTEINE = ['<text', '<script', '<style', '<image', 'href', 'url(', '@import']

test('Favicon: ein relatives, in sich geschlossenes SVG vom eigenen Ursprung', async ({ page }) => {
  await page.goto('/')

  const links = page.locator('link[rel~="icon"]')
  await expect(links).toHaveCount(1)
  await expect(links).toHaveAttribute('type', 'image/svg+xml')

  const rohHref = await links.getAttribute('href')
  expect(rohHref, 'roher href des Icon-Links').not.toBeNull()
  expect(rohHref ?? '', 'href ist relativ (./…)').toMatch(/^\.\//)

  const url = new URL(rohHref ?? '', page.url()).href
  expect(url.startsWith(ORIGIN), `Icon-URL ${url} liegt auf dem eigenen Ursprung`).toBe(true)

  const antwort = await page.request.get(url)
  expect(antwort.status()).toBe(200)
  expect(antwort.headers()['content-type'] ?? '').toContain('image/svg+xml')

  const rumpf = (await antwort.text()).trim()
  expect(rumpf.startsWith('<svg')).toBe(true)
  expect(rumpf).toContain('viewBox="0 0 16 16"')
  for (const baustein of VERBOTENE_BAUSTEINE) {
    expect(rumpf, `SVG enthält ${baustein}`).not.toContain(baustein)
  }

  const groesse = await page.evaluate(async (bildUrl: string) => {
    const bild = new Image()
    bild.src = bildUrl
    await bild.decode()
    return { breite: bild.naturalWidth, hoehe: bild.naturalHeight }
  }, url)
  expect(groesse).toEqual({ breite: 16, hoehe: 16 })
})
