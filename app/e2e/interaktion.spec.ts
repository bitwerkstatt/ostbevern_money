import { expect, test, type Locator, type Page } from '@playwright/test'

import { MENUE, menueLinks, type MenueGruppe } from '../src/lib/menue'
import {
  pruefeEscape,
  pruefeLinkDerAktuellenSeite,
  pruefeLinkEinerAnderenSeite,
  pruefeLinkMitZusatztaste,
} from './menueDrawer'
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

  // Ersetzt den Quelltext-Test „Verdrahtung in MenueGruppe.vue“ (06/IN-09, D-14): Öffnen und
  // Resize-Handler rufen `positioniere()` auf; das wird hier am Verhalten geprüft. Die reine
  // Rechnung (`listenVersatz`) bleibt in `menueVersatz.test.ts`.
  test('die geöffnete Liste bleibt nach dem Öffnen und nach einem Resize im Fenster, style.left passt zur Lage', async ({
    page,
  }) => {
    await page.setViewportSize({ width: 720, height: 800 })
    await expect(page.locator('h1')).toBeVisible()
    await schalter(page).click()
    const zielListe = await liste(page)
    await expect(zielListe).toBeVisible()

    // Lage der Liste samt Rand (aus `max-width` der Liste, wie im Code): `ok` heißt, die Liste
    // liegt mit dem Rand im Fenster und `style.left` passt dazu, nämlich ein Pixelwert, der die
    // Liste entweder gar nicht verschiebt (sie passt) oder genau an den Rand rückt.
    const lage = () =>
      zielListe.evaluate((element) => {
        const kasten = element.getBoundingClientRect()
        const fenster = document.documentElement.clientWidth
        const rand = Math.max(0, (fenster - parseFloat(getComputedStyle(element).maxWidth)) / 2)
        const styleLeft = (element as HTMLElement).style.left
        const versatz = parseFloat(styleLeft)
        const imFenster = kasten.left >= rand - 0.5 && kasten.right <= fenster - rand + 0.5
        const anDerKante =
          Math.abs(kasten.right - (fenster - rand)) < 0.5 || Math.abs(kasten.left - rand) < 0.5
        const passt = /^-?\d+(\.\d+)?px$/.test(styleLeft) && (versatz === 0 || anDerKante)
        return {
          fenster,
          styleLeft,
          links: kasten.left,
          rechts: kasten.right,
          ok: imFenster && passt,
        }
      })

    // Nach dem Öffnen (`wechsle()` → `positioniere()`).
    const schmal = await lage()
    expect(schmal.fenster).toBe(720)
    expect(schmal.ok, JSON.stringify(schmal)).toBe(true)

    // Breiter Resize bei offener Liste: der Resize-Handler misst neu (das Ereignis kommt erst
    // nach `setViewportSize`, daher wird gewartet), die Liste bleibt offen und im Fenster.
    await page.setViewportSize({ width: 1200, height: 800 })
    await expect(zielListe).toBeVisible()
    await expect
      .poll(async () => {
        const messung = await lage()
        return messung.fenster === 1200 && messung.ok
      })
      .toBe(true)

    // Zurück auf 720 px: dieselbe Lage wie beim ersten Öffnen, kein hängengebliebener Versatz
    // (WR-01).
    await page.setViewportSize({ width: 720, height: 800 })
    await expect(zielListe).toBeVisible()
    await expect
      .poll(async () => {
        const messung = await lage()
        return messung.fenster === 720 && messung.ok && messung.styleLeft === schmal.styleLeft
      })
      .toBe(true)
    const zurueck = await lage()
    expect(zurueck.links).toBeCloseTo(schmal.links, 0)
    expect(zurueck.rechts).toBeCloseTo(schmal.rechts, 0)
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

// Spiegel von `mobil.spec.ts` (das Projekt `mobil` läuft nicht in der CI): Bei 360 px schließt
// jeder Linkklick im Menü den Drawer, der Fokus steht danach auf der Überschrift, Escape gibt ihn
// an den Menüknopf zurück (A11Y-02, D-21).
test.describe('Mobiles Menü schließt bei jedem Linkklick (A11Y-02, D-21)', () => {
  test.beforeEach(async ({ page }) => {
    await page.setViewportSize({ width: 360, height: 640 })
  })

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

  test('Ctrl-Klick auf einen Link: öffnet neuen Tab, Drawer bleibt offen, Fokus nicht auf h1 (WR-02)', async ({
    page,
  }) => {
    await pruefeLinkMitZusatztaste(page, 'ControlOrMeta')
  })

  test('Shift-Klick auf einen Link: öffnet neues Fenster, Drawer bleibt offen, Fokus nicht auf h1 (WR-02)', async ({
    page,
  }) => {
    await pruefeLinkMitZusatztaste(page, 'Shift')
  })
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

test.describe('Maßnahmenfilter auf /investitionen (06/IN-05, T-08-18)', () => {
  const ERGEBNIS = '.om-massnahmen-filter__ergebnis'

  /** Zahl am Anfang der Ergebniszeile („1.234 Maßnahmen · zusammen …“), Tausenderpunkt entfernt. */
  async function anzahl(page: Page): Promise<number> {
    const zeile = page.locator(ERGEBNIS)
    await expect(zeile).toBeVisible()
    const text = (await zeile.innerText()).trim()
    const treffer = /^([\d.]+)\s/.exec(text)
    expect(treffer, `Ergebniszeile „${text}“ beginnt nicht mit einer Zahl`).not.toBeNull()
    return Number((treffer?.[1] ?? '').replaceAll('.', ''))
  }

  test('ein gültiger Aufgabenbereich verringert die Zahl der Maßnahmen, ein ungültiger verschwindet aus der URL', async ({
    page,
  }) => {
    await page.goto('/#/investitionen')
    const alle = await anzahl(page)
    expect(alle).toBeGreaterThan(0)

    // Der Code kommt aus den Optionen der Auswahl, nichts davon ist getippt.
    const codes = await page
      .locator('.om-massnahmen-filter__pb wa-option')
      .evaluateAll((optionen) =>
        optionen.map((option) => (option as unknown as { value: string }).value),
      )
    const pb = codes.find((code) => code !== 'alle')
    expect(pb, 'die Auswahl bietet keinen Aufgabenbereich an').toBeDefined()

    await page.goto(`/#/investitionen?pb=${String(pb)}`)
    await expect.poll(() => anzahl(page)).toBeLessThan(alle)
    expect(page.url()).toContain(`pb=${String(pb)}`)

    await page.goto('/#/investitionen?pb=zz')
    await expect(page.locator(ERGEBNIS)).toBeVisible()
    await expect.poll(() => page.url()).not.toContain('pb=')
    expect(await anzahl(page)).toBe(alle)
  })
})
