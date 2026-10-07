import type { Page } from '@playwright/test'

// Gemeinsame Prüfung der scrollbaren Tabellenrahmen von `DatenTabelle` (A11Y-01, A11Y-03, D-19,
// D-20). `mobil.spec.ts` prüft sie auf jeder Route bei 360 px, `interaktion.spec.ts` spiegelt sie
// für `/investitionen` in das CI-Projekt (das Projekt `mobil` läuft nicht in der CI).
//
// Soll-Zustand: Ein Rahmen, dessen Inhalt überläuft, hat zusammen `tabindex="0"`,
// `role="region"` und ein `aria-labelledby`, das auf eine Caption mit Text zeigt, und kein
// `aria-label`. Ein Rahmen ohne Überlauf trägt weder Tabstopp noch Rolle. Die Region-Namen der
// Rahmen sind je Seite eindeutig (eigene Prüfung statt axe `landmark-unique`: diese
// Best-Practice-Regel trifft auch die internen Regionen von `wa-details`).

/** Öffnet alle `wa-details` (Eigenschaft statt Klick) und wartet, bis die Seite ruht. */
export async function oeffneAlleBereiche(page: Page): Promise<void> {
  await page.evaluate(async () => {
    for (const bereich of document.querySelectorAll('wa-details')) {
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
  // Das Layout der geöffneten Bereiche (verschachtelte Akkordeons auf /glossar) steht erst einen
  // Moment nach dem Öffnen; ohne Pause sähe die Messung noch den Zustand davor.
  await page.waitForTimeout(500)
}

/** Befunde zu den Tabellenrahmen der aktuellen Seite; leer, wenn alles stimmt. */
export function befundeTabellenrahmen(page: Page): Promise<string[]> {
  return page.evaluate(() => {
    const befunde: string[] = []
    const regionNamen = new Map<string, number>()

    const rahmenListe = [...document.querySelectorAll<HTMLElement>('.om-tabelle-rahmen')]
    rahmenListe.forEach((rahmen, nummer) => {
      if (!rahmen.checkVisibility({ checkVisibilityCSS: true })) {
        return
      }
      const ort = `Rahmen ${String(nummer + 1)} (${(rahmen.querySelector('caption')?.textContent ?? 'ohne Caption').replace(/\s+/g, ' ').trim()})`
      const hatTabelle = rahmen.querySelector('table') !== null
      const ueberlaeuft = hatTabelle && rahmen.scrollWidth > rahmen.clientWidth
      const tabindex = rahmen.getAttribute('tabindex')
      const rolle = rahmen.getAttribute('role')
      const bezug = rahmen.getAttribute('aria-labelledby')

      if (rahmen.hasAttribute('aria-label')) {
        befunde.push(`${ort}: aria-label am Rahmen (der Name kommt nur aus der Caption)`)
      }

      if (ueberlaeuft) {
        if (tabindex !== '0') {
          befunde.push(`${ort}: läuft über, tabindex ist ${String(tabindex)} statt 0`)
        }
        if (rolle !== 'region') {
          befunde.push(`${ort}: läuft über, role ist ${String(rolle)} statt region`)
        }
        const ziel = bezug === null ? null : document.getElementById(bezug)
        const name = (ziel?.textContent ?? '').replace(/\s+/g, ' ').trim()
        if (ziel === null || ziel.tagName !== 'CAPTION' || name === '') {
          befunde.push(
            `${ort}: aria-labelledby ${String(bezug)} zeigt nicht auf eine Caption mit Text`,
          )
        } else {
          regionNamen.set(name, (regionNamen.get(name) ?? 0) + 1)
        }
      } else {
        if (tabindex !== null) {
          befunde.push(`${ort}: läuft nicht über, trägt aber tabindex ${tabindex}`)
        }
        if (rolle !== null) {
          befunde.push(`${ort}: läuft nicht über, trägt aber role ${rolle}`)
        }
        if (bezug !== null) {
          befunde.push(`${ort}: läuft nicht über, trägt aber aria-labelledby ${bezug}`)
        }
      }
    })

    for (const [name, anzahl] of regionNamen) {
      if (anzahl > 1) {
        befunde.push(`Region-Name „${name}“ kommt ${String(anzahl)}-mal vor`)
      }
    }

    if (document.documentElement.scrollWidth > window.innerWidth) {
      befunde.push(
        `Seite scrollt waagerecht (scrollWidth ${String(document.documentElement.scrollWidth)} > innerWidth ${String(window.innerWidth)})`,
      )
    }
    return befunde
  })
}
