import { expect, test, type Locator, type Page } from '@playwright/test'

import { MENUE, menueLinks, type MenueGruppe } from '../src/lib/menue'
import { routen } from './routen'
import { befundeTabellenrahmen, oeffneAlleBereiche } from './tabellenrahmen'

// Browser-Beweis der Bedienung (Plan 07-09): Menügruppe „Mehr wissen“ (D-19), Fokus und Titel
// bei jedem Routenwechsel (A11Y-02) und reduzierte Bewegung bei den Web-Awesome-Komponenten.
// Gruppenname und Untereinträge stammen aus `MENUE`, nichts davon ist getippt.

const TITEL_ENDE = '– Ostbevern Money'

const gruppe = MENUE.find((eintrag): eintrag is MenueGruppe => eintrag.typ === 'gruppe')
if (gruppe === undefined) {
  throw new Error('MENUE enthält keine Gruppe')
}
const GRUPPENNAME = gruppe.text
const GRUPPEN_LINKS = gruppe.eintraege
const ERSTER = GRUPPEN_LINKS[0]
const LETZTER = GRUPPEN_LINKS[GRUPPEN_LINKS.length - 1]
if (ERSTER === undefined || LETZTER === undefined) {
  throw new Error('Die Menügruppe hat keine Untereinträge')
}

function hauptnavigation(page: Page): Locator {
  return page.getByRole('navigation', { name: 'Hauptnavigation' })
}

function schalter(page: Page): Locator {
  return hauptnavigation(page).getByRole('button', { name: GRUPPENNAME })
}

function gruppenLink(page: Page, text: string): Locator {
  return hauptnavigation(page).getByRole('link', { name: text, exact: true })
}

/** Die ausgeklappte Liste der Gruppe, gefunden über `aria-controls` des Schalters. */
async function liste(page: Page): Promise<Locator> {
  const id = await schalter(page).getAttribute('aria-controls')
  expect(id).toBeTruthy()
  return page.locator(`[id="${String(id)}"]`)
}

async function istOffen(page: Page): Promise<boolean> {
  return (await schalter(page).getAttribute('aria-expanded')) === 'true'
}

test.describe('Menügruppe „Mehr wissen“ (Desktop, D-19)', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/#/')
    await expect(page.locator('h1')).toBeVisible()
  })

  test('Enter und Leertaste öffnen und schließen die Liste, aria-expanded und aria-controls stimmen', async ({
    page,
  }) => {
    const knopf = schalter(page)
    const zielListe = await liste(page)
    await expect(knopf).toHaveAttribute('aria-expanded', 'false')
    await expect(zielListe).toBeHidden()

    await knopf.focus()
    await page.keyboard.press('Enter')
    await expect(knopf).toHaveAttribute('aria-expanded', 'true')
    await expect(zielListe).toBeVisible()
    await expect(zielListe.getByRole('link')).toHaveCount(GRUPPEN_LINKS.length)

    await page.keyboard.press('Enter')
    await expect(knopf).toHaveAttribute('aria-expanded', 'false')
    await expect(zielListe).toBeHidden()

    await page.keyboard.press('Space')
    await expect(knopf).toHaveAttribute('aria-expanded', 'true')
    await expect(zielListe).toBeVisible()

    await page.keyboard.press('Space')
    await expect(knopf).toHaveAttribute('aria-expanded', 'false')
    await expect(zielListe).toBeHidden()
  })

  test('Escape schließt die offene Liste, der Fokus liegt auf dem Schalter', async ({ page }) => {
    const knopf = schalter(page)
    await knopf.focus()
    await page.keyboard.press('Enter')
    await expect(knopf).toHaveAttribute('aria-expanded', 'true')

    await page.keyboard.press('Tab')
    await expect(gruppenLink(page, ERSTER.text)).toBeFocused()

    await page.keyboard.press('Escape')
    await expect(knopf).toHaveAttribute('aria-expanded', 'false')
    await expect(await liste(page)).toBeHidden()
    await expect(knopf).toBeFocused()
  })

  test('Tab läuft ohne Fokusfalle durch die Links, das Verlassen der Gruppe schließt die Liste', async ({
    page,
  }) => {
    const knopf = schalter(page)
    await knopf.focus()
    await page.keyboard.press('Enter')
    await expect(await liste(page)).toBeVisible()

    for (const link of GRUPPEN_LINKS) {
      await page.keyboard.press('Tab')
      await expect(gruppenLink(page, link.text)).toBeFocused()
    }
    expect(await istOffen(page)).toBe(true)

    // Der nächste Tab-Stopp liegt hinter der Gruppe (Glossar): die Liste schließt.
    await page.keyboard.press('Tab')
    await expect(knopf).toHaveAttribute('aria-expanded', 'false')
    await expect(await liste(page)).toBeHidden()
    await expect(knopf).not.toBeFocused()
    const fokusInGruppe = await page.evaluate(
      () => document.activeElement?.closest('.om-menuegruppe') !== null,
    )
    expect(fokusInGruppe).toBe(false)

    // Rückwärts: Shift+Tab aus der offenen Liste führt zum Schalter zurück, ohne Falle.
    await knopf.focus()
    await page.keyboard.press('Enter')
    await page.keyboard.press('Tab')
    await expect(gruppenLink(page, ERSTER.text)).toBeFocused()
    await page.keyboard.press('Shift+Tab')
    await expect(knopf).toBeFocused()
  })

  test('ein Klick außerhalb schließt die Liste', async ({ page }) => {
    const knopf = schalter(page)
    await knopf.click()
    await expect(knopf).toHaveAttribute('aria-expanded', 'true')

    await page.locator('h1').click()
    await expect(knopf).toHaveAttribute('aria-expanded', 'false')
    await expect(await liste(page)).toBeHidden()
  })

  test('ein Routenwechsel schließt die Liste', async ({ page }) => {
    const knopf = schalter(page)
    await knopf.click()
    await expect(knopf).toHaveAttribute('aria-expanded', 'true')

    await page.evaluate(() => {
      window.location.hash = '#/glossar'
    })
    await expect(page).toHaveTitle(new RegExp(`${TITEL_ENDE}$`))
    await expect(page.locator('h1')).toHaveText(/Glossar/)
    await expect(knopf).toHaveAttribute('aria-expanded', 'false')
    await expect(await liste(page)).toBeHidden()
  })

  test('auf einer aktiven Unterseite trägt der Eintrag aria-current page und der Schalter aria-current true', async ({
    page,
  }) => {
    await page.goto(`/#/${LETZTER.name}`)
    const knopf = schalter(page)
    await expect(knopf).toHaveAttribute('aria-current', 'true')

    await knopf.click()
    await expect(gruppenLink(page, LETZTER.text)).toHaveAttribute('aria-current', 'page')
    await expect(gruppenLink(page, ERSTER.text)).not.toHaveAttribute('aria-current', /.+/)

    // Auf einer Seite außerhalb der Gruppe trägt der Schalter keine Marke.
    await page.goto('/#/glossar')
    await expect(page.locator('h1')).toBeVisible()
    await expect(schalter(page)).not.toHaveAttribute('aria-current', /.+/)
  })

  test('die Gruppe nutzt weder role menu noch role menuitem', async ({ page }) => {
    await schalter(page).click()
    await expect(page.locator('[role="menu"], [role="menuitem"], [role="menubar"]')).toHaveCount(0)
    await expect(await liste(page)).toBeVisible()
  })

  test('bis 699 px zeigt der Drawer die Gruppe als Überschrift mit vier sichtbaren Links', async ({
    page,
  }) => {
    await page.setViewportSize({ width: 360, height: 640 })
    await page.goto('/#/')
    await expect(page.locator('h1')).toBeVisible()
    await page.getByRole('button', { name: 'Menü öffnen' }).click()

    const drawer = page.locator('#om-menue-drawer')
    await expect(drawer.getByRole('link', { name: ERSTER.text, exact: true })).toBeVisible()

    const titel = drawer.getByText(GRUPPENNAME, { exact: true })
    await expect(titel).toBeVisible()
    expect(await titel.evaluate((element) => element.tagName)).not.toBe('BUTTON')
    await expect(drawer.getByRole('button', { name: GRUPPENNAME })).toHaveCount(0)
    await expect(drawer.locator('[aria-expanded]')).toHaveCount(0)

    for (const link of GRUPPEN_LINKS) {
      await expect(drawer.getByRole('link', { name: link.text, exact: true })).toBeVisible()
    }
    await expect(page.locator('[role="menu"], [role="menuitem"]')).toHaveCount(0)
  })
})

test.describe('Fokus und Titel bei jedem Routenwechsel (A11Y-02)', () => {
  const ziele = routen().filter((route) => route.name !== 'produkt')
  const links = menueLinks()
  const gruppenNamen = new Set(GRUPPEN_LINKS.map((link) => link.name))

  for (const ziel of ziele) {
    test(`Route ${ziel.pfad}: nach dem Klick steht der Fokus auf der Überschrift und der Titel endet auf „${TITEL_ENDE}“`, async ({
      page,
    }) => {
      // Startseite so wählen, dass der Klick wirklich die Route wechselt.
      await page.goto(ziel.pfad === '/glossar' ? '/#/' : '/#/glossar')
      await expect(page.locator('h1')).toBeVisible()

      const link = links.find((eintrag) => eintrag.name === ziel.name)
      if (link !== undefined) {
        if (gruppenNamen.has(link.name)) {
          await schalter(page).click()
        }
        await gruppenLink(page, link.text).click()
      } else {
        // Fußzeilenroute (/ueber): über den Link der Fußzeile.
        await page.locator(`.om-footer a[href$="#${ziel.pfad}"]`).click()
      }

      await expect(page).toHaveTitle(new RegExp(`${TITEL_ENDE}$`))
      await expect.poll(() => page.evaluate(() => document.activeElement?.tagName ?? '')).toBe('H1')
      const aktivIstUeberschrift = await page.evaluate(
        () => document.activeElement === document.querySelector('h1'),
      )
      expect(aktivIstUeberschrift).toBe(true)
    })
  }
})

// Spiegel von `mobil.spec.ts` (das Projekt `mobil` läuft nicht in der CI): Der scrollbare
// Tabellenrahmen auf /investitionen bei 360 px hat Tabstopp, Rolle und genau einen Namen
// (A11Y-01, A11Y-03).
test.describe('Tabellenrahmen bei 360 px (A11Y-01, A11Y-03)', () => {
  test('/investitionen: überlaufende Rahmen sind benannte Regionen mit Tabstopp, die Seite scrollt nicht', async ({
    page,
  }) => {
    await page.setViewportSize({ width: 360, height: 640 })
    await page.goto('/#/investitionen')
    await expect(page.locator('h1')).toBeVisible()
    await page.waitForLoadState('networkidle')
    await oeffneAlleBereiche(page)

    await expect
      .poll(() => befundeTabellenrahmen(page), { message: 'Tabellenrahmen auf /investitionen' })
      .toEqual([])
    // Der Test ist nur aussagekräftig, wenn mindestens ein Rahmen wirklich überläuft.
    await expect(
      page.locator('.om-tabelle-rahmen[role="region"][tabindex="0"]').first(),
    ).toBeAttached()
  })
})

test.describe('Reduzierte Bewegung bei Web-Awesome-Komponenten (A11Y-02)', () => {
  test.beforeEach(async ({ page }) => {
    await page.emulateMedia({ reducedMotion: 'reduce' })
  })

  /** Läuft nach dem Öffnen noch eine Animation? Der Name der Läufer steht in der Meldung. */
  async function laufendeAnimationen(page: Page): Promise<string[]> {
    return page.evaluate(() =>
      document
        .getAnimations()
        .filter((animation) => animation.playState === 'running')
        .map((animation) => animation.constructor.name + ':' + (animation.id || 'ohne Namen')),
    )
  }

  async function dauer(page: Page, selektor: string, eigenschaft: string): Promise<string> {
    return page.evaluate(
      ([auswahl, name]) => {
        const element = document.querySelector(auswahl ?? '')
        return element === null
          ? 'fehlt'
          : getComputedStyle(element)
              .getPropertyValue(name ?? '')
              .trim()
      },
      [selektor, eigenschaft],
    )
  }

  test('die Quell-Seitenleiste öffnet ohne Übergang', async ({ page }) => {
    await page.goto('/#/')
    await expect(page.locator('h1')).toBeVisible()
    await page
      .getByRole('button', { name: /^Quelle anzeigen: / })
      .first()
      .click()
    await expect(page.getByRole('dialog', { name: /^Quelle: PDF-Seite/ })).toBeVisible()

    expect(await dauer(page, '#om-quelle-drawer', '--show-duration')).toMatch(/^0(ms|s)$/)
    expect(await dauer(page, '#om-quelle-drawer', '--hide-duration')).toMatch(/^0(ms|s)$/)
    expect(await laufendeAnimationen(page)).toEqual([])
  })

  test('der Menü-Drawer (360 px) öffnet ohne Übergang', async ({ page }) => {
    await page.setViewportSize({ width: 360, height: 640 })
    await page.goto('/#/')
    await expect(page.locator('h1')).toBeVisible()
    await page.getByRole('button', { name: 'Menü öffnen' }).click()
    await expect(page.getByRole('dialog', { name: 'Menü' })).toBeVisible()

    expect(await dauer(page, '#om-menue-drawer', '--show-duration')).toMatch(/^0(ms|s)$/)
    expect(await dauer(page, '#om-menue-drawer', '--hide-duration')).toMatch(/^0(ms|s)$/)
    expect(await laufendeAnimationen(page)).toEqual([])
  })

  test('ein wa-details „Tabelle anzeigen“ öffnet ohne Übergang', async ({ page }) => {
    await page.goto('/#/einnahmen')
    await expect(page.locator('h1')).toBeVisible()
    // Der Titel steht im Shadow-DOM von wa-details (Eigenschaft, kein Attribut): die Suche
    // geht über die summary im Schatten.
    const details = page
      .locator('wa-details')
      .filter({ has: page.locator('summary', { hasText: 'Tabelle anzeigen' }) })
      .first()
    await expect(details).toBeVisible()
    await details.locator('summary').click()
    await expect(details).toHaveAttribute('open', '')

    const showDuration = await details.evaluate((element) =>
      getComputedStyle(element).getPropertyValue('--show-duration').trim(),
    )
    expect(showDuration).toMatch(/^0(ms|s)$/)
    expect(await laufendeAnimationen(page)).toEqual([])
  })
})
