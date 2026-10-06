// Quellenbelege (Phase 7, UI-02, DATA-04): Schlüsselgrammatik, Beleg-Lookup, Umrechnung des
// Zeilenrechtecks und der Zustand der einen globalen Quell-Seitenleiste.
//
// Die Schlüsselgrammatik ist identisch mit `pipeline/ostbevern/quellen.py` (Modul-Docstring):
//   ep:{code}:{zeile}                                  Ergebnisplanzeile
//   fp:{code}:{zeile}                                  Finanzplanzeile
//   vb:{tabelle}:{posten} | vb:{tabelle}:gesamt        Vorberichtsposten
//   meta:{pfad}                                        MetaWert (Pfad gepunktet)
//   gz:{produkt}:{position}                            Grundzahl
//   pr:{produkt}                                       Produktseite
//   inv:{produkt}:{massnahme_id}:{konto}:{richtung}    Investitionsmaßnahme
//   ve:{produkt}:{massnahme_id}:{konto}                VE-Fälligkeiten einer Kontozeile
//   sd:{reihe}                                         Schuldenstandsreihe
//   sp:{teil}:{position}:{produktbereich oder -}       Stellenplanzeile
//   seite:{n}                                          Seitenbeleg ohne Zeile

import { reactive, readonly } from 'vue'

import { quellen } from '@/data/daten'
import type { Beleg } from '@/data/typen'

type Teil = string | number

export const belegSchluessel = {
  ep: (code: string, zeile: string): string => `ep:${code}:${zeile}`,
  fp: (code: string, zeile: string): string => `fp:${code}:${zeile}`,
  vb: (tabelle: string, posten: string): string => `vb:${tabelle}:${posten}`,
  vbGesamt: (tabelle: string): string => `vb:${tabelle}:gesamt`,
  meta: (pfad: string): string => `meta:${pfad}`,
  gz: (produkt: string, position: Teil): string => `gz:${produkt}:${String(position)}`,
  pr: (produkt: string): string => `pr:${produkt}`,
  inv: (produkt: string, massnahmeId: string, konto: string, richtung: string): string =>
    `inv:${produkt}:${massnahmeId}:${konto}:${richtung}`,
  ve: (produkt: string, massnahmeId: string, konto: string): string =>
    `ve:${produkt}:${massnahmeId}:${konto}`,
  sd: (reihe: string): string => `sd:${reihe}`,
  sp: (teil: string, position: Teil, produktbereich: string | null): string =>
    `sp:${teil}:${String(position)}:${produktbereich ?? '-'}`,
  seite: (nummer: number): string => `seite:${String(nummer)}`,
} as const

/** Ein aufgelöster Beleg mit allem, was die Seitenleiste zum Zeichnen braucht. */
export interface AufgeloesterBeleg {
  schluessel: string
  /** 1-basierte PDF-Seite. */
  pdfSeite: number
  /** Dateiname des Belegbilds, z. B. "s062.webp". */
  bild: string
  /** `[x0, top, x1, bottom]` in PDF-Punkten (Ursprung oben links) oder `null` (D-03). */
  bbox: readonly [number, number, number, number] | null
  /** Seitenbreite in PDF-Punkten. */
  breite: number
  /** Seitenhöhe in PDF-Punkten. */
  hoehe: number
}

// Eine Map statt eines Objektzugriffs: `findeBeleg('__proto__')` und `findeBeleg('constructor')`
// dürfen keinen Beleg liefern (wie ERGEBNISPLAN in `lib/produkt.ts`).
const BELEGE: ReadonlyMap<string, Beleg> = new Map(Object.entries(quellen.belege))
const SEITEN = new Map(Object.entries(quellen.seiten))

function alsRechteck(
  bbox: readonly number[] | null,
): readonly [number, number, number, number] | null | undefined {
  if (bbox === null) {
    return null
  }
  const [x0, top, x1, bottom] = bbox
  if (
    bbox.length !== 4 ||
    x0 === undefined ||
    top === undefined ||
    x1 === undefined ||
    bottom === undefined
  ) {
    return undefined
  }
  return [x0, top, x1, bottom]
}

/**
 * Löst einen Belegschlüssel auf. `null`, wenn es keinen Beleg gibt, die `bbox` weder `null`
 * noch vier Zahlen ist oder die Seite nicht in `seiten` steht; der `QuelleKnopf` wird dann
 * nicht gerendert (kein toter Knopf).
 */
export function findeBeleg(schluessel: string): AufgeloesterBeleg | null {
  const beleg = BELEGE.get(schluessel)
  if (beleg === undefined) {
    return null
  }
  const seite = SEITEN.get(String(beleg.pdf_seite))
  const bbox = alsRechteck(beleg.bbox)
  if (seite === undefined || bbox === undefined) {
    return null
  }
  return {
    schluessel,
    pdfSeite: beleg.pdf_seite,
    bild: beleg.bild,
    bbox,
    breite: seite.breite,
    hoehe: seite.hoehe,
  }
}

export interface BboxProzent {
  links: number
  oben: number
  breite: number
  hoehe: number
}

function aufEineStelle(wert: number): number {
  return Math.round(wert * 10) / 10
}

/**
 * Rechnet das Zeilenrechteck (PDF-Punkte) in Prozent der Seitengröße um, auf eine
 * Nachkommastelle gerundet. Hoch- und Querformat nutzen dieselbe Formel mit der jeweiligen
 * Seitenbreite und -höhe.
 */
export function bboxProzent(
  bbox: readonly [number, number, number, number],
  breite: number,
  hoehe: number,
): BboxProzent {
  const [x0, top, x1, bottom] = bbox
  return {
    links: aufEineStelle((x0 / breite) * 100),
    oben: aufEineStelle((top / hoehe) * 100),
    breite: aufEineStelle(((x1 - x0) / breite) * 100),
    hoehe: aufEineStelle(((bottom - top) / hoehe) * 100),
  }
}

/** URL eines Belegbilds relativ zur App-Basis; nie ein Pfad mit führendem `/` (D-05). */
export function bildUrl(bild: string): string {
  return `${import.meta.env.BASE_URL}quellen/${bild}`
}

/** Was der Auslöser der Seitenleiste mitgibt (Wertzeile und Hinweis). */
export interface QuelleAnfrage {
  schluessel: string
  /** Bezeichnung des Werts, z. B. „Erträge“. */
  bezeichnung: string
  /** Bereits formatierter Wert. */
  wert?: string
  /** Zeile „{Wertart} {jahr}“. */
  wertart?: string
  /** Herleitung eines berechneten Werts (D-03); `null`/fehlend für gedruckte Werte. */
  herleitung?: string | null
}

interface QuelleZustand {
  offen: boolean
  anfrage: QuelleAnfrage | null
}

const zustand = reactive<QuelleZustand>({ offen: false, anfrage: null })

// Der Auslöser liegt bewusst außerhalb des reaktiven Zustands: ein DOM-Element braucht keinen
// Proxy, und er wird aus dem Klick (`event.currentTarget`) gemerkt, nicht aus
// `document.activeElement` (Safari und Firefox/macOS fokussieren einen Knopf beim Klick nicht).
let ausloeser: HTMLElement | null = null
let fokusZurueckgeben = true

/** Reaktiver, schreibgeschützter Zustand der Quell-Seitenleiste. */
export function useQuelle(): Readonly<QuelleZustand> {
  return readonly(zustand)
}

/**
 * Öffnet die Seitenleiste für einen Beleg. Ohne Beleg zum Schlüssel passiert nichts.
 * `ausloeser` ist das Element, das nach dem Schließen den Fokus zurückbekommt.
 */
export function oeffneQuelle(anfrage: QuelleAnfrage & { ausloeser: HTMLElement | null }): void {
  if (findeBeleg(anfrage.schluessel) === null) {
    return
  }
  const { ausloeser: knopf, ...rest } = anfrage
  ausloeser = knopf
  fokusZurueckgeben = true
  zustand.anfrage = rest
  zustand.offen = true
}

/**
 * Schließt die Seitenleiste (der Inhalt bleibt bis `fokusNachSchliessen` stehen, damit die
 * Ausblendanimation nicht in eine leere Leiste läuft). `ohneFokus` für einen Seitenwechsel:
 * dann gehört der Fokus der neuen Seite (Router: Überschrift).
 */
export function schliesseQuelle(optionen: { ohneFokus?: boolean } = {}): void {
  if (optionen.ohneFokus === true) {
    fokusZurueckgeben = false
  }
  zustand.offen = false
}

function fokussiere(element: HTMLElement): void {
  if (!element.hasAttribute('tabindex')) {
    element.setAttribute('tabindex', '-1')
  }
  element.focus()
}

/**
 * Nach dem Schließen (`wa-after-hide`): Inhalt abräumen und den Fokus zurückgeben, an den
 * Auslöser, oder an die Überschrift der Seite, wenn der Auslöser nicht mehr im DOM steht.
 */
export function fokusNachSchliessen(): void {
  const knopf = ausloeser
  const zurueckgeben = fokusZurueckgeben
  ausloeser = null
  fokusZurueckgeben = true
  zustand.offen = false
  zustand.anfrage = null
  if (!zurueckgeben) {
    return
  }
  if (knopf?.isConnected === true) {
    knopf.focus()
    return
  }
  const ueberschrift = document.querySelector<HTMLElement>('h1')
  if (ueberschrift !== null) {
    fokussiere(ueberschrift)
  }
}
