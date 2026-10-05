/**
 * Das Element zu einem URL-Fragment, ausschließlich per `getElementById` (der Hash ist nur
 * eine Element-ID, nie ein Selektor oder Ziel einer Weiterleitung). Unbekannt, ohne
 * `document` (vitest unter Node) oder bei fehlerhafter Prozentkodierung: `null`.
 */
export function elementFuerHash(hash: string): HTMLElement | null {
  if (typeof document === 'undefined' || hash.length < 2) {
    return null
  }
  try {
    return document.getElementById(decodeURIComponent(hash.slice(1)))
  } catch {
    return null // fehlerhafte Prozentkodierung
  }
}

/**
 * Wandelt eine berechnete CSS-Länge (z. B. `96px` aus `scrollMarginTop`) in Pixel um.
 * Nur endliche Werte größer 0 zählen; alles andere (leer, `auto`, negativ) ergibt 0,
 * damit nie über das Ziel hinaus gescrollt wird.
 */
export function versatzAusScrollMargin(wert: string): number {
  const zahl = parseFloat(wert)
  return Number.isFinite(zahl) && zahl > 0 ? zahl : 0
}

/**
 * Der Scroll-Versatz eines Sprungziels: sein berechnetes `scroll-margin-top` in Pixel.
 * Ohne `getComputedStyle` (vitest unter Node) ist der Versatz 0.
 */
export function scrollVersatz(ziel: Element): number {
  if (typeof getComputedStyle === 'undefined') {
    return 0
  }
  return versatzAusScrollMargin(getComputedStyle(ziel).scrollMarginTop)
}

/**
 * Die Scrollposition nach einem Seiten- oder Fragmentwechsel (Logik von `scrollBehavior`):
 * Mit Fragment zum Element, sonst die gespeicherte Position, bei reinem Query-Wechsel
 * (gleicher Pfad) nichts, sonst nach oben.
 *
 * Warum der Versatz: vue-router scrollt mit `window.scrollTo` und ignoriert das
 * CSS-`scroll-margin-top`. Deshalb wird das berechnete `scroll-margin-top` des Ziels als
 * `top`-Versatz an vue-router übergeben; ohne ihn landet das Ziel unter der festen
 * `wa-page`-Kopfzeile. Der Sprung bleibt ein Sofortsprung (kein `behavior`), so dass
 * `prefers-reduced-motion` keine zusätzliche Behandlung braucht.
 *
 * @param finde Sucht das Zielelement zum Fragment (injizierbar für Tests).
 * @param versatz Liefert den Versatz in Pixel für ein Ziel (injizierbar für Tests).
 */
export function sprungPosition(
  nach: { path: string; hash: string },
  von: { path: string },
  gespeichert: { left: number; top: number } | null,
  finde: (hash: string) => HTMLElement | null = elementFuerHash,
  versatz: (ziel: Element) => number = scrollVersatz,
): { el: HTMLElement; top: number } | { left?: number; top: number } | false {
  const ziel = finde(nach.hash)
  if (ziel !== null) {
    return { el: ziel, top: versatz(ziel) }
  }
  if (gespeichert) {
    return gespeichert
  }
  if (nach.path === von.path) {
    return false
  }
  return { top: 0 }
}
