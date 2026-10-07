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
// - jede Kachel steht in einem Raster `.om-kachelraster` (G-04),
// - das `li` um jede Kachel hat Außenabstand 0 (07-14, Einzug aus Web Awesome),
// - je Route wird die Schrift der Beträge protokolliert und gegen die Kalibrierschrift geprüft
//   (`KALIBRIERSCHRIFT`): Weicht sie ab, bricht der Test mit einer klaren Meldung ab, bevor
//   Layoutbefunde entstehen, die nur an der Schrift liegen.
// Ein eigener Test hält die Routenliste geschlossen: Zeigt eine weitere Route Kacheln, schlägt er
// fehl, statt sie ungeprüft zu lassen.
// Alle Befunde einer Route werden gesammelt, damit ein Lauf jeden Überlauf mit Route, Breite und
// Betrag nennt.
//
// Messumgebung (Lücke G-07-2, Plan 07-14): Die gerenderten Breiten hängen von der Systemschrift
// hinter `system-ui` ab. GitHub Actions (ubuntu-24.04) rendert DejaVu Sans. Lokale Läufe und jede
// Kalibrierung gehen deshalb über `scripts/e2e-wie-ci.sh`. Das nackte Playwright-Image rendert
// WenQuanYi Zen Hei (rund 16 % schmaler) und ist keine gültige Kalibrierumgebung.

/** Schrift, gegen die die Mindestspur der Kacheln kalibriert ist (Familienname laut Chromium). */
const KALIBRIERSCHRIFT = 'DejaVu Sans'

// Grundbreiten des Sweeps. 720 und 952 px sind die Spaltensprünge der Mindestspur 13rem aus 07-13,
// die zuvor niemand testete (G-07-2).
const GRUNDBREITEN = [360, 400, 480, 560, 600, 700, 720, 768, 952, 1024, 1280, 1440] as const

// Spaltensprünge der aktuellen Mindestspur `--om-kachel-mindestbreite` (13,25rem = 212 px): Die
// Spur ist dort genau so breit wie die Mindestspur, also der ungünstigste Fall. Die Liste füllt den
// Inhaltsbereich der Seite (Breite = Viewport − 48 px durch das Seitenpolster `--wa-space-l` von
// 24 px links und rechts), die Lücke beträgt 16 px unter 700 px und 24 px ab 700 px. Der Sprung auf n
// Spalten liegt daher bei n·212 + (n−1)·Lücke + 48 px: n = 2: 488, n = 3: 732, n = 4: 968,
// n = 5: 1204, n = 6: 1440 (n = 7 läge bei 1676 px, jenseits des Sweeps). Ändert sich der Wert in
// basis.css, müssen diese Breiten folgen; der Selbsttest auf der Startseite meldet es, wenn nicht.
const SPALTENSPRUENGE: readonly number[] = [488, 732, 968, 1204, 1440]

/** Längste Wartezeit je Breite, bis die Seite nicht mehr über den Rand reicht (`warteAufLayout`). */
const LAYOUT_WARTEZEIT_MS = 2000

/** Alle Breiten des Sweeps: Grundbreiten und Spaltensprünge, aufsteigend und ohne Doppelte. */
const BREITEN: readonly number[] = [...new Set([...GRUNDBREITEN, ...SPALTENSPRUENGE])].sort(
  (a, b) => a - b,
)
const HOEHE = 800

/**
 * Zeitgrenze eines Routentests: Im Fehlerfall (dauerhafter Überlauf) wartet jede Breite die volle
 * `LAYOUT_WARTEZEIT_MS`. Die Grenze deckt das mit Reserve für Laden und Messung ab, sonst bricht
 * der Test mit einem Timeout ab, bevor die gesammelte Befundliste ausgegeben wird.
 */
const ROUTENTEST_ZEITGRENZE_MS = 60_000 + BREITEN.length * LAYOUT_WARTEZEIT_MS
const MINDESTMASS = 44
const TOLERANZ = 0.5

/** Routennamen (`routen()`), die Kennzahl-Kacheln zeigen; der Klassifikationstest hält sie vollständig. */
const KACHEL_ROUTEN: readonly string[] = [
  'start',
  'investitionen',
  'rat-entscheidet',
  'stellenplan',
]

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
  /** Aufgelöste `--om-kachel-mindestbreite` in px (kleinster Wert über die Kachellisten). */
  mindestspur: number
  /** Kleinste Spur (ohne 0) der `grid-template-columns` der Kachellisten in px. */
  engsteSpur: number
  /** Kleinster Abstand des Betrags zum Inhaltsrand in der schmalsten möglichen Spur in px. */
  spurreserve: number
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
  // Diagramme ziehen nach einer Größenänderung verzögert nach (ECharts-Resize). Beim Wechsel auf
  // das zweispaltige Layout ab 700 px steht ein Diagramm kurz noch in der alten, breiteren
  // Größe und schiebt die Seite über den Rand (auf /stellenplan: Leinwand 520 px in einer Spalte
  // von 302 px). Das ist kein Layoutfehler der Kacheln und nach wenigen Millisekunden vorbei.
  // Gewartet wird deshalb, bis die Seite nicht mehr über den Rand reicht, höchstens 2 s. Ein
  // dauerhafter Überlauf bleibt danach bestehen und wird von der Messung gemeldet.
  await page.evaluate(
    (grenze) =>
      new Promise<void>((fertig) => {
        const beginn = performance.now()
        const pruefe = () => {
          if (
            document.documentElement.scrollWidth <= window.innerWidth ||
            performance.now() - beginn > grenze
          ) {
            fertig()
          } else {
            setTimeout(pruefe, 50)
          }
        }
        pruefe()
      }),
    LAYOUT_WARTEZEIT_MS,
  )
}

/**
 * Die Plattformschrift, die die Beträge rendert (CDP `CSS.getPlatformFontsForNode`). Das Projekt
 * `ci` ist Chromium, CDP steht also zur Verfügung. Der Aufrufer prüft sie gegen
 * `KALIBRIERSCHRIFT`; die CI stellt sie im Workflow her (Schritt „Schrift der Kalibrierung
 * sicherstellen“), das Runner-Image allein garantiert sie nicht. Jeder Eintrag hat die Form
 * `Familienname (PostScript-Name)`, z. B. `DejaVu Sans (DejaVuSans-Bold)`.
 */
async function schriftDerBetraege(page: Page): Promise<string[]> {
  const sitzung = await page.context().newCDPSession(page)
  try {
    await sitzung.send('DOM.enable')
    await sitzung.send('CSS.enable')
    const dokument = await sitzung.send('DOM.getDocument', { depth: -1 })
    const knoten = await sitzung.send('DOM.querySelectorAll', {
      nodeId: dokument.root.nodeId,
      selector: '.om-kennzahl .om-zahl',
    })
    const schriften = new Set<string>()
    for (const nodeId of knoten.nodeIds) {
      const antwort = await sitzung.send('CSS.getPlatformFontsForNode', { nodeId })
      for (const eintrag of antwort.fonts) {
        schriften.add(`${eintrag.familyName} (${eintrag.postScriptName})`)
      }
    }
    return [...schriften]
  } finally {
    await sitzung.detach()
  }
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
      let spurreserve = Number.POSITIVE_INFINITY
      let mindestspur = Number.POSITIVE_INFINITY
      let engsteSpur = Number.POSITIVE_INFINITY
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
            .map(zahl)
            .filter((spur) => spur > 0)
          spalten = Math.max(spalten, spuren.length)
          engsteSpur = Math.min(engsteSpur, ...spuren)
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
              befunde.push(
                `„${name}“: ${bezeichnung} hat overflow-x ${overflowX}, erwartet visible`,
              )
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

        // (i) das li des Rasters hat keinen Außenabstand (Einzug aus Web Awesome native.css)
        const eintrag = kachel.closest('li')
        if (eintrag !== null) {
          const eintragStil = getComputedStyle(eintrag)
          const raender = [
            eintragStil.marginLeft,
            eintragStil.marginRight,
            eintragStil.marginTop,
            eintragStil.marginBottom,
          ]
          if (raender.some((rand) => Math.abs(zahl(rand)) > toleranz)) {
            befunde.push(
              `„${name}“: li hat Außenabstand links ${eintragStil.marginLeft}, rechts ${eintragStil.marginRight}, oben ${eintragStil.marginTop}, unten ${eintragStil.marginBottom}, erwartet 0 (Einzug des li aus Web Awesome (native.css) nicht zurückgesetzt)`,
            )
          }
        }

        // (j) der Betrag passt in die schmalste Spur, die das Raster erzeugen kann. Seine Breite
        // hängt nicht vom Viewport ab (nowrap, feste Größe), und die auto-fit-Spur wird nie schmaler
        // als die Mindestbreite, solange die Liste mindestens so breit ist (ab 360 px der Fall).
        // Der Check deckt damit jede Breite zwischen den getesteten Breiten ab.
        if (raster !== null && eintrag !== null && betrag !== null) {
          const roh = getComputedStyle(raster).getPropertyValue('--om-kachel-mindestbreite').trim()
          if (roh === '') {
            befunde.push(`„${name}“: Raster ohne --om-kachel-mindestbreite`)
          } else {
            const mindestSonde = document.createElement('div')
            mindestSonde.style.position = 'absolute'
            mindestSonde.style.visibility = 'hidden'
            mindestSonde.style.width = roh
            document.body.append(mindestSonde)
            const mindestPx = mindestSonde.getBoundingClientRect().width
            mindestSonde.remove()
            mindestspur = Math.min(mindestspur, mindestPx)
            const eintragStil = getComputedStyle(eintrag)
            const schmalsterInhalt =
              mindestPx -
              zahl(eintragStil.marginLeft) -
              zahl(eintragStil.marginRight) -
              zahl(stil.borderLeftWidth) -
              zahl(stil.borderRightWidth) -
              zahl(stil.paddingLeft) -
              zahl(stil.paddingRight)
            const betragsBreite = betrag.getBoundingClientRect().width
            spurreserve = Math.min(spurreserve, schmalsterInhalt - betragsBreite)
            if (betragsBreite > schmalsterInhalt + toleranz) {
              befunde.push(
                `„${name}“: Betrag „${(betrag.textContent ?? '').trim()}“ (${px(betragsBreite)} px) passt nicht in die schmalste Spur (Inhalt ${px(schmalsterInhalt)} px bei Mindestspur ${px(mindestPx)} px)`,
              )
            }
          }
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
              `${element.tagName.toLowerCase()}${klassen} reicht bis ${px(kasten.right)} px (links ${px(kasten.left)} px, Breite ${px(kasten.width)} px)`,
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
        mindestspur: Number.isFinite(mindestspur) ? mindestspur : 0,
        engsteSpur: Number.isFinite(engsteSpur) ? engsteSpur : 0,
        spurreserve: Number.isFinite(spurreserve) ? spurreserve : 0,
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
    eine(messung.engsteSpur),
    eine(messung.spurreserve),
    `${String(messung.scrollWidth)} |`,
  ].join(' | ')
}

test.describe('Kennzahl-Kacheln über alle Breiten (A11Y-03, 07-13)', () => {
  test.use({ viewport: { width: GRUNDBREITEN[0], height: HOEHE } })
  test.describe.configure({ timeout: ROUTENTEST_ZEITGRENZE_MS })

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
      const schriften = await schriftDerBetraege(page)
      const schrift = schriften.length > 0 ? schriften.join(', ') : '(keine)'
      console.log(`Schrift der Beträge auf ${pfad}: ${schrift}`)
      // Jeder gemeldete Eintrag muss die Familie selbst sein: `DejaVu Sans Mono` oder `DejaVu Sans
      // Condensed` haben andere Zeichenbreiten, und ein Ersatzglyph aus einer anderen Schrift
      // zeigt, dass der Betrag nicht vollständig in der Kalibrierschrift steht.
      expect(
        schriften.length > 0 &&
          schriften.every((eintrag) => eintrag.startsWith(`${KALIBRIERSCHRIFT} (`)),
        `Schrift weicht von der Kalibrierung ab: erwartet ausschließlich ${KALIBRIERSCHRIFT}, gerendert ${schrift}. ` +
          'Die Breitenmessung gilt nur mit dieser Schrift (Lauf über scripts/e2e-wie-ci.sh bzw. ' +
          'den Workflow-Schritt „Schrift der Kalibrierung sicherstellen“).',
      ).toBe(true)

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
        // Selbsttest: Auf der Startseite (sieben Kacheln) gibt es jeden Spaltensprung bis 1440 px.
        // Dort muss die engste Spur der Mindestspur entsprechen, sonst ist die Liste
        // SPALTENSPRUENGE nicht mehr an --om-kachel-mindestbreite ausgerichtet.
        if (name === 'start' && SPALTENSPRUENGE.includes(breite)) {
          if (Math.abs(messung.engsteSpur - messung.mindestspur) > TOLERANZ) {
            messung.befunde.push(
              `Breite ${String(breite)} ist kein Spaltensprung der Mindestspur (engste Spur ${messung.engsteSpur.toFixed(1)} px, Mindestspur ${messung.mindestspur.toFixed(1)} px): SPALTENSPRUENGE an --om-kachel-mindestbreite anpassen`,
            )
          }
        }
        for (const befund of messung.befunde) {
          befunde.push(`${pfad} @ ${String(breite)} px: ${befund}`)
        }
      }
      expect(befunde, befunde.join('\n')).toEqual([])
    })
  }

  // Hält die Routenliste geschlossen: Eine neue Route mit Kacheln schlägt hier fehl, statt
  // ungeprüft zu bleiben. Der Test zählt nur; über das Layout der übrigen Routen sagt er nichts
  // (D-12: der Smoke-Test bleibt Desktop-only).
  test('Kachelrouten: genau diese Routen zeigen Kennzahl-Kacheln', async ({ page }) => {
    const mitKacheln: string[] = []
    for (const route of routen()) {
      await page.goto(`/#${route.pfad}`)
      await expect(page.locator('h1')).toBeVisible()
      await page.waitForLoadState('networkidle')
      const anzahl = await page.locator('.om-kennzahl').count()
      console.log(`| ${route.pfad} | ${String(anzahl)} Kacheln |`)
      if (anzahl > 0) {
        mitKacheln.push(route.name)
      }
    }
    const erwartet = [...KACHEL_ROUTEN].sort()
    const gefunden = mitKacheln.sort()
    const fehlen = erwartet.filter((name) => !gefunden.includes(name))
    const zusaetzlich = gefunden.filter((name) => !erwartet.includes(name))
    const meldung =
      `Routen ohne Kacheln, aber in KACHEL_ROUTEN: ${fehlen.join(', ') || '(keine)'}; ` +
      `Routen mit Kacheln, aber nicht in KACHEL_ROUTEN: ${zusaetzlich.join(', ') || '(keine)'}`
    expect(gefunden, meldung).toEqual(erwartet)
  })
})
