// Projektkonfiguration, die nicht aus dem Haushalts-PDF stammt: Kontakt und Link zum
// Original-Haushaltsplan (D-17, D-18). Die Fußzeile in `App.vue` liest ausschließlich
// diese Konstanten; weder die Adresse noch die URL stehen in Komponenten.

/**
 * Kontaktadresse in der Fußzeile.
 *
 * Solange der Wert nicht festgelegt ist, steht hier ein Platzhalter auf der
 * reservierten Domain `.invalid` (RFC 2606). Phase 7 MUSS vor dem Deployment mit
 * `istPlatzhalter(KONTAKT_EMAIL)` prüfen und bei einem Platzhalter abbrechen (D-17).
 */
export const KONTAKT_EMAIL = 'kontakt-noch-nicht-festgelegt@example.invalid'

/**
 * Link zum Original-Haushaltsplan (PDF) der Gemeinde Ostbevern.
 *
 * Solange der Wert nicht festgelegt ist, steht hier ein Platzhalter auf der
 * reservierten Domain `.invalid` (RFC 2606). Phase 7 MUSS vor dem Deployment mit
 * `istPlatzhalter(ORIGINAL_PDF_URL)` prüfen und bei einem Platzhalter abbrechen (D-17).
 */
export const ORIGINAL_PDF_URL = 'https://haushaltsplan-noch-nicht-festgelegt.invalid/'

function istInvalidHost(host: string): boolean {
  const klein = host.toLowerCase()
  return klein === 'invalid' || klein.endsWith('.invalid')
}

/**
 * Ob eine Adresse (E-Mail) oder URL ein Platzhalter ist: ihr Host (URL) bzw. der
 * Domainteil (E-Mail) liegt auf `.invalid`. Leere oder unlesbare Werte gelten
 * ebenfalls als Platzhalter, damit nie ein unbrauchbarer Wert als echt durchgeht.
 * Phase 7 weist das Deployment ab, solange diese Funktion für eine der beiden
 * Konstanten `true` liefert (D-17).
 */
export function istPlatzhalter(wert: string): boolean {
  const text = wert.trim()
  if (text === '') {
    return true
  }
  if (text.includes('@')) {
    return istInvalidHost(text.slice(text.lastIndexOf('@') + 1))
  }
  try {
    return istInvalidHost(new URL(text).hostname)
  } catch {
    return true
  }
}
