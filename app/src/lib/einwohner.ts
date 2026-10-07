// Die eine Prüfung der Einwohnerzahl (TXT-06, D-09). Datenfehler wirfen laut; auf der Seite
// steht kein sichtbarer Hinweis und keine Spalte voller „–“.

import { haushalt } from '@/data/daten'

/**
 * Einwohnerzahl aus `haushalt.json` für alle Pro-Kopf-Werte. Eine fehlende oder ungültige Zahl ist
 * ein Datenfehler und wirft. Das optionale Argument existiert nur, damit der Wurf ohne Änderung
 * des statischen Imports prüfbar ist; ein ausdrücklich übergebenes `undefined` zählt als fehlender
 * Wert (ein Standardparameter würde es stillschweigend durch den echten Wert ersetzen).
 */
export function einwohnerZahl(...pruefwert: [wert?: unknown]): number {
  const wert = pruefwert.length === 0 ? haushalt.meta.einwohner.wert : pruefwert[0]
  if (typeof wert !== 'number' || !Number.isFinite(wert) || wert <= 0) {
    throw new Error(
      `Einwohnerzahl fehlt in haushalt.json: meta.einwohner.wert muss eine Zahl größer als 0 sein, war ${String(wert)}`,
    )
  }
  return wert
}
