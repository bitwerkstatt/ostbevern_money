// Platzhalter-Renderer für die Erklärtexte aus `texte.json` (D-15, UI-05). Die Pipeline
// liefert nur Rohtexte mit `{{schluessel|kuerzel}}`-Platzhaltern und Rohwerte; erst
// diese Datei macht daraus Anzeigetext, und zwar ausschließlich über `formatiere()`.
// Das Ergebnis ist reiner Text: Komponenten geben ihn per Textinterpolation aus.

import { formatiere, type FormatKuerzel } from '@/charts/format'
import { texte } from '@/data/daten'
import type { Erklaertext } from '@/data/typen'

/**
 * Muss `ostbevern.texte.PLATZHALTER_MUSTER` entsprechen. Das globale Flag wirkt nur in
 * `String.replace`; dort wird `lastIndex` je Aufruf zurückgesetzt.
 */
const PLATZHALTER_MUSTER = /\{\{([a-z0-9_.]+)\|([a-z]+)\}\}/g

/**
 * Alle Formatkürzel genau einmal als Objektschlüssel: Der Typ `Record<FormatKuerzel, true>`
 * lässt TypeScript fehlschlagen, sobald `format.ts` ein Kürzel hinzufügt oder entfernt.
 */
const KUERZEL: Record<FormatKuerzel, true> = {
  euro: true,
  mio: true,
  zahl: true,
  jahr: true,
  prozent: true,
  promille: true,
  vzae: true,
}

export function istFormatKuerzel(kuerzel: string): kuerzel is FormatKuerzel {
  return Object.hasOwn(KUERZEL, kuerzel)
}

/**
 * Ersetzt jeden Platzhalter des Absatzes durch `formatiere(werte[schluessel], kuerzel)`.
 * Ein in `werte` fehlender Schlüssel erscheint als „–“ (Pipeline lehnt unbekannte
 * Schlüssel schon ab; hier nur zweite Absicherung), ein unbekanntes Kürzel wirft.
 */
export function rendereAbsatz(
  absatz: string,
  werte: Readonly<Record<string, number>> = texte.werte,
): string {
  return absatz.replace(PLATZHALTER_MUSTER, (_treffer, schluessel: string, kuerzel: string) => {
    if (!istFormatKuerzel(kuerzel)) {
      throw new Error(`Unbekanntes Formatkürzel „${kuerzel}“ im Platzhalter „${schluessel}“`)
    }
    const wert = Object.hasOwn(werte, schluessel) ? werte[schluessel] : undefined
    return formatiere(wert, kuerzel)
  })
}

const TEXTE_NACH_SCHLUESSEL: ReadonlyMap<string, Erklaertext> = new Map(
  texte.texte.map((text) => [text.schluessel, text]),
)

/** Der Erklärtext zum Schlüssel oder `undefined`; Prototyp-Schlüssel treffen nichts. */
export function findeText(schluessel: string): Erklaertext | undefined {
  return TEXTE_NACH_SCHLUESSEL.get(schluessel)
}

/**
 * `true`, wenn der Text für jedes Jahr gilt. `jahr.*`-Platzhalter hängen am Haushaltsjahr,
 * nicht am gewählten Jahr; nur Betrags-Platzhalter binden einen Text an ein Jahr (D-04).
 * Jahrneutrale Texte dürfen deshalb nur feste Jahre (`jahr.fest_JJJJ`) nennen.
 */
export function istJahrneutral(text: Erklaertext): boolean {
  return text.absaetze.every((absatz) =>
    [...absatz.matchAll(PLATZHALTER_MUSTER)].every((treffer) => treffer[1]?.startsWith('jahr.')),
  )
}

/**
 * Der Text zum Schlüssel, wenn er zum gewählten Jahr passt. Ein Text mit Platzhaltern
 * nennt Zahlen des Haushaltsjahrs und darf nie neben den Zahlen eines anderen Jahres
 * stehen (RESEARCH Pitfall 6); dann ist das Ergebnis `null`. Jahrneutrale Texte gelten
 * für jedes Jahr.
 */
export function textFuerJahr(schluessel: string, jahr: number): Erklaertext | null {
  const text = findeText(schluessel)
  if (text === undefined) {
    return null
  }
  if (istJahrneutral(text) || jahr === texte.haushaltsjahr) {
    return text
  }
  return null
}
