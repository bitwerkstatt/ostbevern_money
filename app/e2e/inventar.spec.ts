import { expect, test } from '@playwright/test'

import { routen } from './routen'

// Inventar der Tabellenalternativen (A11Y-01, D-16): auf jeder Route hat jede ChartCard
// mindestens so viele Tabellen wie Diagramme (`.om-base-chart`), und jedes Diagramm mit
// `role="img"` trägt eine Beschreibung. Gaps werden in der Komponente geschlossen; die
// Ausnahmeliste unten wird nicht erweitert (T-07-20).

/**
 * Geschlossene Ausnahmeliste, genau ein Eintrag. Auf `/entwicklung` stehen die beiden
 * Rücklagen-Karten („Rücklagen …“ und „Rückgang der allgemeinen Rücklage“) im Abschnitt
 * `om-entwicklung-polster`; beide Diagramme belegt die dort immer sichtbare, gemeinsame
 * Rücklagentabelle (UI-SPEC „Chart Contract / Tabellenalternative“: „kurze Rücklagentabelle auf
 * /entwicklung“ ist eine Ausnahme der immer sichtbaren Tabellen). Die Ausnahme gilt nur, solange
 * der Abschnitt wirklich eine Tabelle außerhalb eines geschlossenen wa-details enthält.
 */
const AUSNAHMEN: readonly { route: string; abschnitt: string }[] = [
  { route: 'entwicklung', abschnitt: 'om-entwicklung-polster' },
]

interface KartenBefund {
  titel: string
  abschnitt: string
  diagramme: number
  tabellen: number
  abschnittHatSichtbareTabelle: boolean
}

interface Befund {
  karten: KartenBefund[]
  /** Diagramme, die in keiner ChartCard stehen (Überschrift des nächsten Abschnitts). */
  ohneKarte: string[]
  /** `role="img"`-Diagramme ohne ausreichende Beschreibung, mit Kartentitel. */
  ohneBeschreibung: string[]
}

for (const route of routen()) {
  test(`Inventar ${route.pfad}: jedes Diagramm hat Tabelle und Beschreibung`, async ({ page }) => {
    await page.goto(`/#${route.pfad}`)
    await expect(page.locator('h1')).toBeVisible()
    await page.waitForLoadState('networkidle')

    const befund: Befund = await page.evaluate(() => {
      const text = (id: string): string => (document.getElementById(id)?.textContent ?? '').trim()
      const kartenTitel = (karte: Element | null): string =>
        karte?.querySelector('h2')?.textContent?.trim() ?? 'ohne Karte'

      const karten = [...document.querySelectorAll('.om-chart-card')].map((karte) => {
        const abschnitt = karte.closest('section:not(.om-chart-card)')
        const tabellenImAbschnitt =
          abschnitt === null ? [] : [...abschnitt.querySelectorAll('table')]
        return {
          titel: kartenTitel(karte),
          abschnitt: abschnitt?.getAttribute('aria-labelledby') ?? '',
          diagramme: karte.querySelectorAll('.om-base-chart').length,
          // Eine Tabelle zählt für ein Diagramm. Trägt sie `data-om-deckt-diagramme="n"` am
          // umgebenden Element (UI-SPEC: „eine Tabelle mit allen Werten beider Diagramme“),
          // zählt sie für n Diagramme, aber nur, wenn sie Kopfzellen für die Zeilenbezeichnung und
          // je eine Wertspalte je Diagramm hat.
          tabellen: [...karte.querySelectorAll('table')].reduce((summe, tabelle) => {
            const erklaert = Number(
              tabelle.closest('[data-om-deckt-diagramme]')?.getAttribute('data-om-deckt-diagramme'),
            )
            const spalten = tabelle.querySelectorAll('thead th, tr:first-child th').length
            return (
              summe +
              (Number.isInteger(erklaert) && erklaert > 1 && spalten > erklaert ? erklaert : 1)
            )
          }, 0),
          abschnittHatSichtbareTabelle: tabellenImAbschnitt.some(
            (tabelle) => tabelle.closest('wa-details') === null,
          ),
        }
      })

      const ohneKarte = [...document.querySelectorAll('.om-base-chart')]
        .filter((chart) => chart.closest('.om-chart-card') === null)
        .map(
          (chart) =>
            chart.closest('section')?.querySelector('h2')?.textContent?.trim() ?? 'ohne Abschnitt',
        )

      const ohneBeschreibung = [...document.querySelectorAll('.om-base-chart [role="img"]')]
        .filter((bild) => {
          const label = bild.getAttribute('aria-label')?.trim() ?? ''
          if (label !== '') {
            return false
          }
          const ids = (bild.getAttribute('aria-labelledby') ?? '').split(/\s+/).filter(Boolean)
          // Titel und mindestens eine nicht leere Beschreibung.
          const titel = ids[0] === undefined ? '' : text(ids[0])
          const beschreibung = ids.slice(1).map(text).join('').trim()
          return titel === '' || beschreibung === ''
        })
        .map((bild) => kartenTitel(bild.closest('.om-chart-card')))

      return { karten, ohneKarte, ohneBeschreibung }
    })

    // Es gibt Diagramme auf der Route, sonst prüft der Test nichts (Seiten ohne Diagramm: leer).
    const luecken: string[] = []
    for (const karte of befund.karten) {
      if (karte.tabellen >= karte.diagramme) {
        continue
      }
      const ausgenommen = AUSNAHMEN.some(
        (eintrag) =>
          eintrag.route === route.name &&
          eintrag.abschnitt === karte.abschnitt &&
          karte.abschnittHatSichtbareTabelle,
      )
      if (!ausgenommen) {
        luecken.push(
          `${route.pfad}: Karte „${karte.titel}“ hat ${String(karte.diagramme)} Diagramm(e), aber ${String(karte.tabellen)} Tabelle(n)`,
        )
      }
    }
    for (const titel of befund.ohneKarte) {
      luecken.push(`${route.pfad}: Diagramm außerhalb einer ChartCard (Abschnitt „${titel}“)`)
    }
    for (const titel of befund.ohneBeschreibung) {
      luecken.push(
        `${route.pfad}: Diagramm in Karte „${titel}“ hat weder aria-label noch aria-labelledby mit Titel und Beschreibung`,
      )
    }
    expect(luecken, luecken.join('\n')).toEqual([])
  })
}
