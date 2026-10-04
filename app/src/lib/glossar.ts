// Glossar-Logik (D-14, D-16, GLOS-01): Schlüsselunion, deutsche Sortierung, Nachschlagen
// und der erste Definitionssatz für den Tooltip. Die Begriffe selbst stammen aus
// `texte.json` (Pipeline); hier liegt nur, was die App daraus ableitet.

import { texte } from '@/data/daten'
import type { Glossarbegriff, Produkt } from '@/data/typen'
import { rendereAbsatz } from '@/lib/texte'

/**
 * Alle Glossarschlüssel als Tupel. Daraus entsteht der Union-Typ `GlossarSchluessel`,
 * mit dem `GlossarBegriff` einen unbekannten Schlüssel zum Typfehler macht (D-16). Das
 * Tupel muss genau die Schlüssel von `texte.glossar` enthalten; `glossar.test.ts`
 * prüft beide Richtungen, eine Abweichung fällt dort sofort auf.
 */
export const GLOSSAR_SCHLUESSEL = [
  'ergebnisplan',
  'finanzplan',
  'ertrag_aufwand',
  'einzahlung_auszahlung',
  'produkt',
  'produktgruppe',
  'produktbereich',
  'transferaufwendungen',
  'kreisumlage',
  'jugendamtsumlage',
  'gewerbesteuerumlage',
  'schluesselzuweisung',
  'hebesatz',
  'sonderposten',
  'abschreibungen',
  'globaler_minderaufwand',
  'ausgleichsruecklage',
  'allgemeine_ruecklage',
  'verpflichtungsermaechtigung',
  'bindungsgrad',
  'zuschussbedarf',
  'nkf',
  'haushaltssicherung',
  'wertart',
] as const

export type GlossarSchluessel = (typeof GLOSSAR_SCHLUESSEL)[number]

// Nachschlagen nur über Map (URL-Fragmente und Prototyp-Schlüssel treffen nichts).
const BEGRIFFE_NACH_SCHLUESSEL: ReadonlyMap<string, Glossarbegriff> = new Map(
  texte.glossar.map((begriff) => [begriff.schluessel, begriff] as const),
)

const KOLLATOR = new Intl.Collator('de')

const SORTIERTE_BEGRIFFE: readonly Glossarbegriff[] = [...texte.glossar].sort((a, b) =>
  KOLLATOR.compare(a.begriff, b.begriff),
)

/** Alle Begriffe, alphabetisch nach deutscher Kollation auf dem angezeigten Begriff. */
export function glossarBegriffe(): readonly Glossarbegriff[] {
  return SORTIERTE_BEGRIFFE
}

/** Der Begriff zum Schlüssel oder `undefined`; Prototyp-Schlüssel treffen nichts. */
export function findeBegriff(schluessel: string): Glossarbegriff | undefined {
  return BEGRIFFE_NACH_SCHLUESSEL.get(schluessel)
}

/** Abkürzungen, nach denen ein Punkt keinen Satz beendet. */
const ABKUERZUNGEN: readonly string[] = ['z. B.', 'd. h.', 'u. a.', 'bzw.', 'ca.', 'Nr.', 'vgl.']

/** Ende des ersten Satzes: Satzzeichen vor Leerraum oder Textende, außer nach Abkürzungen. */
function ersterSatzVon(text: string): string {
  const muster = /[.!?](?=\s|$)/g
  for (const treffer of text.matchAll(muster)) {
    const ende = treffer.index + 1
    const bisher = text.slice(0, ende)
    if (!ABKUERZUNGEN.some((kurz) => bisher.endsWith(kurz))) {
      return bisher
    }
  }
  return text
}

/**
 * Der erste Satz des ersten Absatzes, nach dem Auflösen der Platzhalter: der Text des
 * Tooltips von `GlossarBegriff` (D-16). Der erste Absatz trägt nie einen Platzhalter.
 */
export function ersterSatz(schluessel: GlossarSchluessel): string {
  const erster = findeBegriff(schluessel)?.absaetze[0]
  return erster === undefined ? '' : ersterSatzVon(rendereAbsatz(erster).trim())
}

/** Ein Aufgabenbereich mit seinen Produkten für das Produktakkordeon (D-16). */
export interface ProduktGruppe {
  pb: string
  name: string
  produkte: readonly Produkt[]
}

// RED-Stand: leere Rümpfe, damit die Tests an Behauptungen scheitern, nicht am Import.
export function produktGruppen(): readonly ProduktGruppe[] {
  return []
}

export function glossarVerwendungen(_quelltext: string): string[] {
  return []
}
