// Schlanke Hilfsfunktionen ohne Datenzugriff (06/IN-04); einzige Abhängigkeit ist charts/format.ts.
// Kleine Helfer, die mehrere Seiten und Komponenten brauchen, ohne dafür ein Datenmodul oder
// vue-router mitzuladen.

import { jahr as formatiereJahr } from '@/charts/format'

/** Index der Maßnahme, auf die ein Klick im Balkendiagramm zeigt (`dataIndex`); sonst `null`. */
export function klickIndex(params: unknown, anzahl: number): number | null {
  if (typeof params !== 'object' || params === null || !('dataIndex' in params)) {
    return null
  }
  const index = params.dataIndex
  return typeof index === 'number' && Number.isInteger(index) && index >= 0 && index < anzahl
    ? index
    : null
}

/** Jahreszahlen als Aufzählung: „2027“, „2027 und 2028“, „2027, 2028 und 2029“. */
export function jahreListe(jahre: readonly number[]): string {
  const texte = jahre.map(formatiereJahr)
  const letztes = texte.at(-1)
  if (letztes === undefined) {
    return ''
  }
  return texte.length === 1 ? letztes : `${texte.slice(0, -1).join(', ')} und ${letztes}`
}
