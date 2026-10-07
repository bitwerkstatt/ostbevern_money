import { expect, test, type Page } from '@playwright/test'

import { routen } from './routen'

// Kennzahl-Kacheln über alle Breiten (Lücke A11Y-03 aus 07-VERIFICATION, Entscheidungen G-01 bis
// G-05 des Plans 07-13). Die Spec liegt im Projekt `ci`: Sie läuft damit in GitHub Actions
// (`npm run test:e2e`), sodass der Überlauf nicht unbemerkt zurückkehrt. Sie ist nicht der
// zurückgestellte 360-px-Smoke-Test (D-12): Geprüft werden nur die Routen mit Kacheln, und nur das
// Layout.
//
// Geprüft wird je Route und je Breite aus `BREITEN`:
// - jeder Betrag (`.om-zahl`) und jeder Quelle-Knopf der Kachel liegt im Inhaltsbereich der Kachel
//   (Innenabstand eingehalten, 0,5 px Toleranz), jedes andere sichtbare Nachfahrenelement im
//   Rahmen der Kachel,
// - `scrollWidth <= clientWidth` der Kachel und `scrollWidth <= innerWidth` der Seite,
// - jeder Betrag steht in genau einer Zeile und nichts wird abgeschnitten (`overflow-x: visible`),
// - die Betragsgröße ist `--wa-font-size-l` bei jeder Breite (G-02),
// - der Knopf zeigt „Quelle“, behält den zugänglichen Namen „Quelle anzeigen: …, PDF-Seite {n}“
//   und ist mindestens 44 × 44 px groß (G-03),
// - jede Kachel steht in einem Raster `.om-kachelraster` (G-04).
// Ein eigener Test hält die Routenliste geschlossen: Zeigt eine weitere Route Kacheln, schlägt er
// fehl, statt sie ungeprüft zu lassen.
// Alle Befunde einer Route werden gesammelt, damit ein Lauf jeden Überlauf mit Route, Breite und
// Betrag nennt.

const BREITEN = [360, 400, 480, 560, 600, 700, 768, 1024, 1280, 1440] as const
const HOEHE = 800
const MINDESTMASS = 44
const TOLERANZ = 0.5

/** Routennamen (`routen()`), die Kennzahl-Kacheln zeigen; der Klassifikationstest hält sie vollständig. */
const KACHEL_ROUTEN: readonly string[] = ['start']

interface KachelMessung {
  innerWidth: number
  scrollWidth: number
  /** Anzahl sichtbarer `.om-kennzahl`. */
  kacheln: number
  /** Größte Spaltenzahl der Raster, in denen die Kacheln stehen. */
  spalten: number
  breitesterBetrag: string
  /** Breite des breitesten Betrags in px. */
  betragBreite: number
  /** Kleinste Breite des Inhaltsbereichs einer Kachel in px. */
  engsteInnenbreite: number
  /** Kleinster Abstand zwischen rechter Betragskante und rechter Inhaltskante in px. */
  reserve: number
  befunde: string[]
}

async function warteAufLayout(page: Page): Promise<void> {
  await page.evaluate(
    () =>
      new Promise<void>((fertig) => {
        requestAnimationFrame(() => {
          requestAnimationFrame(() => {
            fertig()
          })
        })
      }),
  )
  await page.evaluate(() =>
    Promise.all(
      document
        .getAnimations()
        .filter((animation) => animation.effect?.getTiming().iterations !== Infinity)
        .map((animation) => animation.finished.catch(() => undefined)),
    ),
  )
}

/** Misst alle sichtbaren Kacheln der Seite im aktuellen Zustand (eine Auswertung im Browser). */
function messeKacheln(page: Page): Promise<KachelMessung> {
  return page.evaluate(
    ([mindest, toleranz]) => {
      const zahl = (wert: string): number => {
        const gelesen = Number.parseFloat(wert)
        return Number.isNaN(gelesen) ? 0 : gelesen
      }
      const sichtbar = (element: Element): boolean =>
        element.checkVisibility({ checkVisibilityCSS: true })
      const px = (wert: number): string => wert.toFixed(1)

      // Sollgröße des Betrags: der aufgelöste Wert von `--wa-font-size-l`.
      const sonde = document.createElement('span')
      sonde.style.fontSize = 'var(--wa-font-size-l)'
      document.body.append(sonde)
      const sollGroesse = getComputedStyle(sonde).fontSize
      sonde.remove()

      const befunde: string[] = []
      let breitesterBetrag = ''
      let betragBreite = 0
      let engsteInnenbreite = Number.POSITIVE_INFINITY
      let reserve = Number.POSITIVE_INFINITY
      let spalten = 0

      const kacheln = [...document.querySelectorAll('.om-kennzahl')].filter(
        (kachel) => sichtbar(kachel) && kachel.getBoundingClientRect().width > 0,
      )

      for (const kachel of kacheln) {
        const name =
          kachel.querySelector('.om-kennzahl__bezeichnung')?.textContent.trim() ?? '(ohne Name)'
        const rahmen = kachel.getBoundingClientRect()
        const stil = getComputedStyle(kachel)
        const innenLinks = rahmen.left + zahl(stil.borderLeftWidth) + zahl(stil.paddingLeft)
        const innenRechts = rahmen.right - zahl(stil.borderRightWidth) - zahl(stil.paddingRight)
        engsteInnenbreite = Math.min(engsteInnenbreite, innenRechts - innenLinks)

        // (a) gemeinsames Raster
        const raster = kachel.closest('.om-kachelraster')
        if (raster === null) {
          befunde.push(`„${name}“: Kachel steht in keinem .om-kachelraster`)
        }
        const liste = kachel.closest('li')?.parentElement
        if (liste !== null && liste !== undefined) {
          const spuren = getComputedStyle(liste)
            .gridTemplateColumns.split(/\s+/)
            .filter((spur) => zahl(spur) > 0).length
          spalten = Math.max(spalten, spuren)
        }

        // (b) nichts wird abgeschnitten
        const wert = kachel.querySelector('.om-kennzahl__wert')
        const betrag = kachel.querySelector('.om-zahl')
        const abgeschnitten: [string, Element | null | undefined][] = [
          ['Kachel', kachel],
          ['li', kachel.closest('li')],
          ['.om-kennzahl__wert', wert],
          ['.om-zahl', betrag],
        ]
        for (const [bezeichnung, element] of abgeschnitten) {
          if (element !== null && element !== undefined) {
            const overflowX = getComputedStyle(element).overflowX
            if (overflowX !== 'visible') {
              befunde.push(`„${name}“: ${bezeichnung} hat overflow-x ${overflowX}, erwartet visible`)
            }
          }
        }

        // (c) Betragsgröße, (d) eine Zeile, (e) Betrag im Inhaltsbereich
        if (wert !== null) {
          const groesse = getComputedStyle(wert).fontSize
          if (groesse !== sollGroesse) {
            befunde.push(
              `„${name}“: Betragsgröße ${groesse}, erwartet ${sollGroesse} (--wa-font-size-l)`,
            )
          }
        }
        if (betrag === null) {
          befunde.push(`„${name}“: kein .om-zahl in der Kachel`)
        } else {
          const text = (betrag.textContent ?? '').trim()
          const zeilen = betrag.getClientRects().length
          if (zeilen !== 1) {
            befunde.push(`„${name}“: Betrag „${text}“ steht in ${String(zeilen)} Zeilen`)
          }
          const kasten = betrag.getBoundingClientRect()
          if (kasten.width > betragBreite) {
            betragBreite = kasten.width
            breitesterBetrag = text
          }
          reserve = Math.min(reserve, innenRechts - kasten.right)
          if (kasten.right > innenRechts + toleranz) {
            befunde.push(
              `„${name}“: Betrag „${text}“ ragt ${px(kasten.right - innenRechts)} px über den Inhaltsbereich (Betrag ${px(kasten.width)} px, Inhalt ${px(innenRechts - innenLinks)} px)`,
            )
          }
          if (kasten.left < innenLinks - toleranz) {
            befunde.push(
              `„${name}“: Betrag „${text}“ ragt ${px(innenLinks - kasten.left)} px links über den Inhaltsbereich`,
            )
          }
        }

        // (f) Knopf „Quelle“
        for (const knopf of kachel.querySelectorAll('.om-quelle-knopf')) {
          const kasten = knopf.getBoundingClientRect()
          if (!sichtbar(knopf)) {
            befunde.push(`„${name}“: Quelle-Knopf nicht sichtbar`)
            continue
          }
          if (kasten.width < mindest - toleranz || kasten.height < mindest - toleranz) {
            befunde.push(
              `„${name}“: Quelle-Knopf ${px(kasten.width)} × ${px(kasten.height)} px, unter ${String(mindest)} px`,
            )
          }
          if (kasten.right > innenRechts + toleranz || kasten.left < innenLinks - toleranz) {
            befunde.push(
              `„${name}“: Quelle-Knopf liegt bei ${px(kasten.left)} bis ${px(kasten.right)} px, Inhaltsbereich ${px(innenLinks)} bis ${px(innenRechts)} px`,
            )
          }
          const sichtbarerText = (knopf as HTMLElement).innerText.trim()
          if (sichtbarerText !== 'Quelle') {
            befunde.push(`„${name}“: Quelle-Knopf zeigt „${sichtbarerText}“, erwartet „Quelle“`)
          }
          const zugaenglich = knopf.getAttribute('aria-label') ?? ''
          if (!zugaenglich.startsWith(sichtbarerText)) {
            befunde.push(
              `„${name}“: Name „${zugaenglich}“ beginnt nicht mit dem sichtbaren Text „${sichtbarerText}“`,
            )
          }
          if (!/^Quelle anzeigen: .+, PDF-Seite \d+$/.test(zugaenglich)) {
            befunde.push(`„${name}“: zugänglicher Name „${zugaenglich}“ weicht vom Muster ab`)
          }
        }

        // (g) jedes andere sichtbare Nachfahrenelement liegt im Rahmen der Kachel
        for (const kind of kachel.querySelectorAll('*')) {
          if (kind.closest('.om-visually-hidden, wa-tooltip') !== null || !sichtbar(kind)) {
            continue
          }
          const kasten = kind.getBoundingClientRect()
          if (kasten.width === 0 || kasten.height === 0) {
            continue
          }
          if (kasten.right > rahmen.right + toleranz || kasten.left < rahmen.left - toleranz) {
            const klassen = [...kind.classList].map((klasse) => `.${klasse}`).join('')
            befunde.push(
              `„${name}“: ${kind.tagName.toLowerCase()}${klassen} liegt bei ${px(kasten.left)} bis ${px(kasten.right)} px, Kachel ${px(rahmen.left)} bis ${px(rahmen.right)} px`,
            )
          }
        }

        // (h) Kachel scrollt nicht
        if (kachel.scrollWidth > kachel.clientWidth) {
          befunde.push(
            `„${name}“: Kachel scrollWidth ${String(kachel.scrollWidth)} > clientWidth ${String(kachel.clientWidth)}`,
          )
        }
      }

      // Seite: kein waagerechtes Scrollen, die breitesten Verursacher nennen.
      const sichtbareBreite = document.documentElement.clientWidth
      if (document.documentElement.scrollWidth > window.innerWidth) {
        const verursacher: string[] = []
        for (const element of document.body.querySelectorAll('*')) {
          const kasten = element.getBoundingClientRect()
          if (kasten.right > sichtbareBreite + toleranz && kasten.width > 0) {
            const klassen = [...element.classList].map((klasse) => `.${klasse}`).join('')
            verursacher.push(
              `${element.tagName.toLowerCase()}${klassen} reicht bis ${px(kasten.right)} px`,
            )
          }
          if (verursacher.length >= 5) {
            break
          }
        }
        befunde.push(
          `Seite scrollt waagerecht (scrollWidth ${String(document.documentElement.scrollWidth)} > innerWidth ${String(window.innerWidth)}): ${verursacher.join('; ')}`,
        )
      }

      return {
        innerWidth: window.innerWidth,
        scrollWidth: document.documentElement.scrollWidth,
        kacheln: kacheln.length,
        spalten,
        breitesterBetrag,
        betragBreite,
        engsteInnenbreite: Number.isFinite(engsteInnenbreite) ? engsteInnenbreite : 0,
        reserve: Number.isFinite(reserve) ? reserve : 0,
        befunde,
      }
    },
    [MINDESTMASS, TOLERANZ] as const,
  )
}

function tabellenzeile(pfad: string, breite: number, messung: KachelMessung): string {
  const eine = (wert: number): string => wert.toFixed(1)
  return [
    `| ${pfad}`,
    String(breite),
    String(messung.kacheln),
    String(messung.spalten),
    messung.breitesterBetrag,
    eine(messung.betragBreite),
    eine(messung.engsteInnenbreite),
    eine(messung.reserve),
    `${String(messung.scrollWidth)} |`,
  ].join(' | ')
}

test.describe('Kennzahl-Kacheln über alle Breiten (A11Y-03, 07-13)', () => {
  test.use({ viewport: { width: BREITEN[0], height: HOEHE } })

  for (const name of KACHEL_ROUTEN) {
    const route = routen().find((eintrag) => eintrag.name === name)
    if (route === undefined) {
      throw new Error(`Kachelroute „${name}“ fehlt in routen()`)
    }
    const pfad = route.pfad

    test(`Kacheln und Seitenbreite: ${pfad}`, async ({ page }) => {
      await page.goto(`/#${pfad}`)
      await expect(page.locator('h1')).toBeVisible()
      await page.waitForLoadState('networkidle')

      // Aufsteigende Breiten: Diagramme ziehen nach dem Viewport nach, sie sind nie breiter.
      const befunde: string[] = []
      for (const breite of BREITEN) {
        await page.setViewportSize({ width: breite, height: HOEHE })
        await warteAufLayout(page)
        const messung = await messeKacheln(page)
        console.log(tabellenzeile(pfad, breite, messung))
        if (messung.kacheln === 0) {
          messung.befunde.push('keine sichtbare Kennzahl-Kachel gefunden')
        }
        for (const befund of messung.befunde) {
          befunde.push(`${pfad} @ ${String(breite)} px: ${befund}`)
        }
      }
      expect(befunde, befunde.join('\n')).toEqual([])
    })
  }
})
