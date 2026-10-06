// Entwicklung (ENTW-01, ENTW-02): Jahresreihen für /entwicklung. Alle Werte werden aus `haushalt.json`
// gelesen, nichts wird neu berechnet; die Jahre kommen ausschließlich aus `haushalt.jahre`, nie aus
// dem Quelltext, und es gibt keine Grundzahl-Jahre vor dem ersten Planjahr (D-12). Fehlt ein
// Schlüssel in den Daten, wirft die Funktion mit dem Namen des Schlüssels statt still auf 0 oder
// eine Ersatzzahl zu fallen.

import { euro, euroKurz, KEIN_WERT } from '@/charts/format'
import { haushalt } from '@/data/daten'

/** Ein Wert je Jahr mit Wertart und Quellseite; die Reihen liegen in der Reihenfolge von `haushalt.jahre`. */
export interface Jahreswert {
  jahr: number
  /** Euro; `null`, wenn die Quelle für das Jahr keinen Wert nennt (nie 0). */
  wert: number | null
  /** `ergebnis`, `ansatz` oder `planung` (aus `haushalt.wertarten`). */
  wertart: string
  /** 1-basierte PDF-Seite der Quelle; `null`, wenn die Daten keine nennen. */
  pdfSeite: number | null
  /** `true`, wenn der Wert aus einer in T€ geführten Quelle stammt (Anzeige „rd.“). */
  gerundet: boolean
}

export interface ErgebnisReihen {
  /** Erträge des Gesamtergebnisplans vor dem globalen Minderaufwand. */
  ertraege: Jahreswert[]
  /** Aufwendungen des Gesamtergebnisplans vor dem globalen Minderaufwand. */
  aufwendungen: Jahreswert[]
  /** Jahresergebnis laut Ergebnisplan, vor globalem Minderaufwand. */
  ergebnisVor: Jahreswert[]
  /** Globaler Minderaufwand als positive Kürzung des Aufwands (die GEP-Zeile trägt ein negatives Vorzeichen). */
  minderaufwand: Jahreswert[]
  /** Ergebnis nach globalem Minderaufwand, wie in der Haushaltssatzung und auf der Startseite. */
  ergebnisNach: Jahreswert[]
}

/** Schlüssel des Gesamtknotens in `haushalt.ergebnisplan` und `haushalt.knoten`. */
const GESAMT = 'GESAMT'

function gesamtPdfSeite(): number | null {
  const knoten = haushalt.knoten.find((eintrag) => eintrag.code === GESAMT)
  if (knoten === undefined) {
    throw new Error(`Der Knoten ${GESAMT} fehlt in haushalt.json`)
  }
  return knoten.pdf_seite
}

function gesamtWerte() {
  const gesamt = haushalt.ergebnisplan[GESAMT]
  if (gesamt === undefined) {
    throw new Error(`ergebnisplan.${GESAMT} fehlt in haushalt.json`)
  }
  return gesamt
}

/** Wertart je Jahr aus `haushalt.wertarten`; ein fehlender Eintrag ist ein Datenfehler. */
function wertartAn(index: number): string {
  const wertart = haushalt.wertarten[index]
  if (wertart === undefined) {
    throw new Error(`haushalt.wertarten hat keinen Eintrag für den Jahresindex ${String(index)}`)
  }
  return wertart
}

/** Je Jahr aus `haushalt.jahre` einen Wert; `werte` kommt aus den Daten, `name` steht in der Fehlermeldung. */
function jahresreihe(
  name: string,
  werte: readonly (number | null)[] | undefined,
  pdfSeite: number | null,
  gerundet: boolean,
  umrechnung: (wert: number) => number = (wert) => wert,
): Jahreswert[] {
  if (werte === undefined) {
    throw new Error(`${name} fehlt in haushalt.json`)
  }
  return haushalt.jahre.map((jahr, index) => {
    const wert = werte[index]
    return {
      jahr,
      wert: wert === undefined || wert === null ? null : umrechnung(wert),
      wertart: wertartAn(index),
      pdfSeite,
      gerundet,
    }
  })
}

/** Zeile des Gesamtergebnisplans als Jahresreihe. */
function gepZeile(schluessel: string, umrechnung?: (wert: number) => number): Jahreswert[] {
  return jahresreihe(
    `ergebnisplan.${GESAMT}.zeilen.${schluessel}`,
    gesamtWerte().zeilen[schluessel],
    gesamtPdfSeite(),
    false,
    umrechnung,
  )
}

/**
 * Die Reihen für Linien (Erträge, Aufwendungen), Säulen (Ergebnis nach Minderaufwand) und
 * Tabelle. Alle Werte stammen aus den GEP-Zeilen; die Identitäten (Erträge − Aufwendungen =
 * Ergebnis vor Minderaufwand, Ergebnis vor + Minderaufwand = Ergebnis nach Minderaufwand) prüft
 * der Test.
 */
export function baueErgebnisReihen(): ErgebnisReihen {
  const gesamt = gesamtWerte()
  const seite = gesamtPdfSeite()
  return {
    ertraege: jahresreihe(
      `ergebnisplan.${GESAMT}.berechnet.ertraege`,
      gesamt.berechnet.ertraege,
      seite,
      false,
    ),
    aufwendungen: jahresreihe(
      `ergebnisplan.${GESAMT}.berechnet.aufwand`,
      gesamt.berechnet.aufwand,
      seite,
      false,
    ),
    ergebnisVor: gepZeile('jahresergebnis'),
    // Die GEP-Zeile trägt die Kürzung negativ; `wert === 0` verhindert ein negatives Null („-0 €“).
    minderaufwand: gepZeile('globaler_minderaufwand', (wert) => (wert === 0 ? 0 : -wert)),
    ergebnisNach: gepZeile('ergebnis_nach_minderaufwand'),
  }
}

/**
 * Beschriftung einer Ergebnissäule: „Defizit {Betrag}“ unter der Nulllinie, „Überschuss {Betrag}“
 * darüber, jeweils ohne Vorzeichen. Ohne Wert steht „–“, bei genau 0 nur der Betrag. Der Betrag
 * steht gekürzt (`euroKurz`, für die Säule) oder mit `genau` auf den Euro genau (Tooltip).
 */
export function ergebnisBeschriftung(wert: number | null, genau = false): string {
  if (wert === null) {
    return KEIN_WERT
  }
  const betrag = genau ? euro : euroKurz
  if (wert < 0) {
    return `Defizit ${betrag(Math.abs(wert))}`
  }
  if (wert > 0) {
    return `Überschuss ${betrag(wert)}`
  }
  return betrag(wert)
}

export interface ErgebnisZeile {
  jahr: number
  wertart: string
  ertraege: number | null
  aufwendungen: number | null
  ergebnisVor: number | null
  minderaufwand: number | null
  ergebnisNach: number | null
}

/**
 * Eine Zeile je Jahr aus `haushalt.jahre`: Erträge, Aufwendungen, Ergebnis vor Minderaufwand, der
 * globale Minderaufwand (positive Kürzung) und das Ergebnis nach Minderaufwand. Fehlende Werte
 * bleiben `null`.
 */
export function ergebnisTabelle(): ErgebnisZeile[] {
  const reihen = baueErgebnisReihen()
  return haushalt.jahre.map((jahr, index) => ({
    jahr,
    wertart: wertartAn(index),
    ertraege: reihen.ertraege[index]?.wert ?? null,
    aufwendungen: reihen.aufwendungen[index]?.wert ?? null,
    ergebnisVor: reihen.ergebnisVor[index]?.wert ?? null,
    minderaufwand: reihen.minderaufwand[index]?.wert ?? null,
    ergebnisNach: reihen.ergebnisNach[index]?.wert ?? null,
  }))
}

/** Woher die Jahreswerte eines Postens stammen: eine Vorberichtstabelle oder eine GEP-Zeile. */
export type PostenQuelle =
  { art: 'vorbericht'; tabelle: string; posten: string } | { art: 'gep'; zeile: string }

export interface EntwicklungPosten {
  schluessel: string
  titel: string
  quelle: PostenQuelle
  /** Schlüssel eines geprüften Erklärtexts in `texte.json`, `null` ohne Text. */
  erklaertext: string | null
}

/** Die fünf Posten (Gerüst, folgt im GREEN-Commit). */
export const ENTWICKLUNG_POSTEN: readonly EntwicklungPosten[] = []

/** Jahresreihe eines Postens (Gerüst, folgt im GREEN-Commit). */
export function bauePostenReihe(_schluessel: string): Jahreswert[] {
  return []
}

/** Relative Veränderung erstes zu letztes Jahr (Gerüst, folgt im GREEN-Commit). */
export function veraenderung(_reihe: readonly Jahreswert[]): number | null {
  return Number.NaN
}

/** Anzeige der Veränderung (Gerüst, folgt im GREEN-Commit). */
export function veraenderungText(_wert: number | null): string {
  return ''
}

/** Quellenzeile eines Postens (Gerüst, folgt im GREEN-Commit). */
export function postenFussnote(_posten: EntwicklungPosten, _reihe: readonly Jahreswert[]): string {
  return ''
}
