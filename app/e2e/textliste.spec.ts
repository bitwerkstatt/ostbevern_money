import { mkdirSync, writeFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'

import { expect, test, type Page } from '@playwright/test'

import { routen } from './routen'

// Textliste für den Abnahme-Checkpoint (Plan 07-10, D-15). Läuft nur im Projekt `texte` und
// nicht in der CI. Das Skript geht jede Route aus `routen()` durch, sammelt alle sichtbaren
// und zugänglichen Texte (Überschrift, Lead, Kartentitel, Callouts, Knopf- und Linktexte,
// `aria-label`, `alt`, versteckte Texte, Tabellenköpfe, Fließtext) und schreibt sie nach
// `test-results/textliste.md`. Am Ende steht der Text einer geöffneten Quelle-Seitenleiste.
// Die Datei ist die Grundlage für die Textabnahme; sie enthält keine Zahlen von Hand.

const AUSGABE = fileURLToPath(new URL('../test-results/textliste.md', import.meta.url))

interface Sammlung {
  h1: string[]
  lead: string[]
  ueberschriften: string[]
  callouts: string[]
  bedienelemente: string[]
  ariaLabel: string[]
  alt: string[]
  attribute: string[]
  versteckt: string[]
  tabellen: string[]
  fliesstext: string[]
}

/** Sammelt alle Texte unterhalb des Elements, das `wurzelSelektor` trifft. */
function sammle(page: Page, wurzelSelektor: string): Promise<Sammlung | null> {
  return page.evaluate((selektor) => {
    const wurzel = document.querySelector(selektor)
    if (wurzel === null) {
      return null
    }
    const glatt = (text: string | null): string => (text ?? '').replace(/\s+/g, ' ').trim()
    // `innerText` trennt Blockelemente durch Zeilenumbrüche und lässt Verborgenes (zugeklappte
    // Erklärungen, Tooltips) weg; bei Elementen ohne Layout fällt es auf `textContent` zurück.
    const sichtbar = (element: Element): string =>
      glatt(element instanceof HTMLElement ? element.innerText : element.textContent)
    const einzig = (liste: string[]): string[] => Array.from(new Set(liste.filter((t) => t !== '')))
    const elemente = (auswahl: string): Element[] => Array.from(wurzel.querySelectorAll(auswahl))
    const texte = (auswahl: string): string[] => einzig(elemente(auswahl).map(sichtbar))
    const mitAttribut = (auswahl: string, attribut: string): string[] =>
      einzig(
        elemente(auswahl).map((element) => {
          const wert = glatt(element.getAttribute(attribut))
          return wert === '' ? '' : `${element.tagName.toLowerCase()}: ${wert}`
        }),
      )

    const bedienelemente = einzig(
      elemente('button, a, wa-button').map((element) => {
        const text = sichtbar(element)
        const etikett = glatt(element.getAttribute('aria-label'))
        if (text === '' && etikett === '') {
          return ''
        }
        return etikett === '' ? text : `${text} [aria-label: ${etikett}]`
      }),
    )
    const attribute = einzig([
      ...mitAttribut('[title]', 'title').map((eintrag) => `title ${eintrag}`),
      ...mitAttribut('[summary]', 'summary').map((eintrag) => `summary ${eintrag}`),
      ...mitAttribut('[label]', 'label').map((eintrag) => `label ${eintrag}`),
    ])

    return {
      h1: texte('h1'),
      lead: texte('header.om-page-intro p'),
      ueberschriften: texte('h2, h3, h4'),
      callouts: texte('wa-callout'),
      bedienelemente,
      ariaLabel: mitAttribut('[aria-label]', 'aria-label'),
      alt: mitAttribut('img[alt]', 'alt'),
      attribute,
      versteckt: texte('.om-visually-hidden'),
      tabellen: texte('caption, th'),
      fliesstext: einzig(
        elemente('p, li, dd, figcaption')
          .filter((element) => element.querySelector('p, li, dd, figcaption') === null)
          .map(sichtbar),
      ),
    }
  }, wurzelSelektor)
}

function liste(titel: string, eintraege: string[]): string[] {
  if (eintraege.length === 0) {
    return []
  }
  return [`**${titel}**`, '', ...eintraege.map((eintrag) => `- ${eintrag}`), '']
}

function abschnitt(ueberschrift: string, sammlung: Sammlung | null): string[] {
  if (sammlung === null) {
    return [`## ${ueberschrift}`, '', '_Nicht gefunden._', '']
  }
  return [
    `## ${ueberschrift}`,
    '',
    ...liste('Überschrift (h1)', sammlung.h1),
    ...liste('Lead', sammlung.lead),
    ...liste('Zwischenüberschriften und Kartentitel', sammlung.ueberschriften),
    ...liste('Callouts', sammlung.callouts),
    ...liste('Knöpfe und Links', sammlung.bedienelemente),
    ...liste('aria-label', sammlung.ariaLabel),
    ...liste('alt', sammlung.alt),
    ...liste('title, summary, label', sammlung.attribute),
    ...liste('Versteckte Texte', sammlung.versteckt),
    ...liste('Tabellenköpfe und Beschriftungen', sammlung.tabellen),
    ...liste('Fließtext', sammlung.fliesstext),
  ]
}

test('schreibt die Textliste je Route nach test-results/textliste.md', async ({ page }) => {
  test.setTimeout(180_000)
  const zeilen: string[] = [
    '# Textliste für die Abnahme (D-15)',
    '',
    'Je Route alle sichtbaren und zugänglichen Texte, danach der Rahmen (Kopf, Menü, Fußzeile)',
    'und der Text einer geöffneten Quelle-Seitenleiste.',
    '',
  ]

  for (const route of routen()) {
    await page.goto(`/#${route.pfad}`)
    await expect(page.locator('h1')).toBeVisible()
    zeilen.push(...abschnitt(`Route ${route.pfad} (${route.name})`, await sammle(page, 'main')))
  }

  await page.goto('/#/')
  await expect(page.locator('h1')).toBeVisible()
  zeilen.push(...abschnitt('Rahmen: Kopf und Menü', await sammle(page, '.om-header')))
  zeilen.push(...abschnitt('Rahmen: Fußzeile', await sammle(page, '.om-footer')))

  await page
    .getByRole('button', { name: /^Quelle anzeigen: / })
    .first()
    .click()
  const leiste = page.locator('#om-quelle-drawer')
  await expect(page.getByRole('dialog', { name: /^Quelle: PDF-Seite / })).toBeVisible()
  await expect(leiste.locator('img.om-quelle-seite__bild')).toBeVisible()
  const titel = (await leiste.getAttribute('label')) ?? ''
  zeilen.push(`### Titel der Seitenleiste: ${titel}`, '')
  zeilen.push(
    ...abschnitt('Geöffnete Quelle-Seitenleiste', await sammle(page, '#om-quelle-drawer')),
  )

  mkdirSync(fileURLToPath(new URL('../test-results/', import.meta.url)), { recursive: true })
  writeFileSync(AUSGABE, `${zeilen.join('\n')}\n`, 'utf-8')
  expect(zeilen.length).toBeGreaterThan(100)
})
