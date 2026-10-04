// Gedruckte Zeilennamen und -nummern der Plan-Zeilen. Einzige Namensquelle ist
// `haushalt.zeilen_namen` (erzeugt aus `ostbevern/zeilen.py`); die App führt keine
// zweite Namenstabelle (RESEARCH Pitfall 9).

import { haushalt } from '@/data/daten'
import type { ZeilenName } from '@/data/typen'

export type Plan = 'ergebnisplan' | 'finanzplan'

function baueTabelle(zeilen: readonly ZeilenName[]): ReadonlyMap<string, ZeilenName> {
  return new Map(zeilen.map((zeile) => [zeile.schluessel, zeile]))
}

const TABELLEN: Readonly<Record<Plan, ReadonlyMap<string, ZeilenName>>> = {
  ergebnisplan: baueTabelle(haushalt.zeilen_namen.ergebnisplan),
  finanzplan: baueTabelle(haushalt.zeilen_namen.finanzplan),
}

function eintrag(plan: Plan, schluessel: string): ZeilenName {
  const treffer = TABELLEN[plan].get(schluessel)
  if (treffer === undefined) {
    throw new Error(`Unbekannte Zeile im ${plan}: „${schluessel}“`)
  }
  return treffer
}

/** Gedruckter Zeilenname, z. B. „Steuern und ähnliche Abgaben“. */
export function zeilenName(plan: Plan, schluessel: string): string {
  return eintrag(plan, schluessel).name
}

/** Gedruckte zweistellige Zeilennummer, z. B. „01“. */
export function zeilenNummer(plan: Plan, schluessel: string): string {
  return eintrag(plan, schluessel).nummer
}
