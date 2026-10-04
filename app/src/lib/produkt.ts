// Seitenmodell der Produktdetailseite `/produkt/:code` (D-09, AUSG-05). Reine Funktionen
// über den App-Daten; formatiert wird erst in der Seite über `charts/format.ts`.

import type { RouteLocationNamedRaw } from 'vue-router'

import type { Produkt } from '@/data/typen'
import { findeKnoten, findeProdukt, leseAnsicht } from '@/lib/ansicht'

const BINDUNGSGRAD_TEXTE: ReadonlyMap<string, string> = new Map([
  ['pflichtig', 'pflichtig'],
  ['freiwillig', 'freiwillig'],
  ['teils', 'teils pflichtig, teils freiwillig'],
])

/** Ausgeschriebener Bindungsgrad; ein unbekannter Wert kommt unverändert zurück. */
export function bindungsgradText(wert: string): string {
  return BINDUNGSGRAD_TEXTE.get(wert) ?? wert
}

function normiere(text: string): string {
  return text.replaceAll(',', '').replaceAll(/\s+/g, ' ').trim().toLowerCase()
}

/** Kopfdaten der Produktseite: Namen der Ebenen darüber, Rücksprungziel und Quellseite. */
export interface ProduktKopf {
  produkt: Produkt
  /** Name des Aufgabenbereichs (PB) des Produkts. */
  pbName: string
  /** Name der Produktgruppe (PG) des Produkts. */
  pgName: string
  /** Ziel des Zurück-Links: die Ausgabenansicht, aus der das Produkt geöffnet wurde (ohne `jahr`). */
  zurueck: RouteLocationNamedRaw
  /** Name der Ebene, zu der der Zurück-Link führt (Produktgruppe, sonst Aufgabenbereich). */
  zurueckText: string
  /** Erste PDF-Seite des Produkts (1-basiert) für die Quellzeile. */
  quelleSeite: number | null
  /** Ausgeschriebener Bindungsgrad. */
  bindungsgrad: string
  /** Wortlaut des Plans, wenn er sich vom ausgeschriebenen Bindungsgrad unterscheidet. */
  bindungsgradOriginal: string | null
}

/**
 * Baut den Kopf eines Produkts (D-09); `null` für jeden unbekannten Code, auch für
 * Prototyp-Schlüssel (Nachschlagen nur über die Map in `findeProdukt`).
 *
 * `query` ist der gemerkte Zustand der Ausgabenansicht (`modus`, `pb`, `pg`). Er wird mit
 * `leseAnsicht` neu validiert und nur übernommen, wenn er zum Produkt passt (gleicher
 * Aufgabenbereich, gleiche oder keine Produktgruppe); sonst führt der Zurück-Link zu
 * Aufgabenbereich und Produktgruppe des Produkts. Das Jahr hängt die Seite über `jahrLink` an.
 */
export function baueProduktKopf(
  code: unknown,
  query: Readonly<Record<string, unknown>> = {},
): ProduktKopf | null {
  const produkt = findeProdukt(code)
  if (produkt === undefined) {
    return null
  }
  const pbName = findeKnoten(produkt.pb)?.name ?? produkt.pb
  const pgName = findeKnoten(produkt.pg)?.name ?? produkt.pg

  const gemerkt = leseAnsicht(query)
  const passt = gemerkt.pb === produkt.pb && (gemerkt.pg === null || gemerkt.pg === produkt.pg)
  const pb = passt ? gemerkt.pb : produkt.pb
  const pg = passt ? gemerkt.pg : produkt.pg

  const rueckQuery: Record<string, string> = {}
  if (gemerkt.modus !== 'aufwand') {
    rueckQuery.modus = gemerkt.modus
  }
  if (pb !== null) {
    rueckQuery.pb = pb
  }
  if (pg !== null) {
    rueckQuery.pg = pg
  }

  const bindungsgrad = bindungsgradText(produkt.bindungsgrad)
  const abweichend = normiere(produkt.bindungsgrad_original) !== normiere(bindungsgrad)

  return {
    produkt,
    pbName,
    pgName,
    zurueck: { name: 'ausgaben', query: rueckQuery },
    zurueckText: pg === null ? pbName : pgName,
    quelleSeite: produkt.pdf_seiten[0] ?? null,
    bindungsgrad,
    bindungsgradOriginal: abweichend ? produkt.bindungsgrad_original : null,
  }
}

// --- RED-Gerüst (wird im GREEN-Schritt ersetzt) ---
import type { DatenSpalte, DatenZeile } from '@/components/datenTabelle'
import type { Massnahme } from '@/data/typen'

export interface Tabelle {
  spalten: DatenSpalte[]
  zeilen: DatenZeile[]
}
export interface Teilergebnisplan extends Tabelle {
  titel: string
}
export interface GrundzahlenTabelle extends Tabelle {
  fussnote: string | null
}
export interface Bezugsgroesse {
  produkt: string
  bezeichnungen: readonly string[]
  einheitText: string
}
export interface ErlaeuterungEintrag {
  betrag: number | null
  text: string
  zeilenNamen: string[]
  zuAnzeigen: boolean
}
export const BEZUGSGROESSEN: readonly Bezugsgroesse[] = []
export function jahrSchluessel(jahr: number): string {
  return String(jahr)
}
export function baueTeilergebnisplan(_code: unknown): Teilergebnisplan | null {
  return null
}
export function baueErlaeuterungen(_code: unknown): ErlaeuterungEintrag[] {
  return []
}
export function baueGrundzahlen(_code: unknown): GrundzahlenTabelle | null {
  return null
}
export function baueProduktInvestitionen(_code: unknown): Massnahme[] {
  return []
}
export function baueInvestitionenTabelle(_liste: readonly Massnahme[]): Tabelle {
  return { spalten: [], zeilen: [] }
}
