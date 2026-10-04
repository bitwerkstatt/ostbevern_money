let region: HTMLElement | null = null

/**
 * Meldet einen Text höflich (`aria-live="polite"`) an Screenreader, ohne den Fokus zu
 * bewegen (D-13): Jahr-/Modus-Wechsel, Seitenwechsel, Ebenenwechsel. Die Region liegt
 * einmal unsichtbar im `body`. Sie wird erst geleert und im nächsten Animationsframe
 * befüllt, damit auch ein wiederholter, gleicher Text erneut angesagt wird. Ohne
 * `document` (vitest unter Node) passiert nichts.
 */
export function ansagen(text: string): void {
  if (typeof document === 'undefined') {
    return
  }
  if (region === null || !region.isConnected) {
    region = document.createElement('div')
    region.className = 'om-visually-hidden'
    region.setAttribute('aria-live', 'polite')
    region.setAttribute('aria-atomic', 'true')
    document.body.appendChild(region)
  }
  const ziel = region
  ziel.textContent = ''
  requestAnimationFrame(() => {
    ziel.textContent = text
  })
}
