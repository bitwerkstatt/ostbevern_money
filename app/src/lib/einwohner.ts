// Die eine Prüfung der Einwohnerzahl (TXT-06, D-09). Datenfehler wirfen laut; auf der Seite
// steht kein Hinweis und keine Spalte voller „–“.

import { haushalt } from '@/data/daten'

/**
 * Einwohnerzahl aus `haushalt.json` für alle Pro-Kopf-Werte. Der Parameter existiert nur, damit
 * der Wurf ohne Änderung des statischen Imports prüfbar ist.
 */
export function einwohnerZahl(wert: unknown = haushalt.meta.einwohner.wert): number {
  return wert as number
}
