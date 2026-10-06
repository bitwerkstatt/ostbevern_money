// Entwicklung (ENTW-01, ENTW-02): Jahresreihen für /entwicklung. Alle Werte werden aus `haushalt.json`
// gelesen, nichts wird neu berechnet; die Jahre kommen ausschließlich aus `haushalt.jahre`, nie aus
// dem Quelltext, und es gibt keine Grundzahl-Jahre vor dem ersten Planjahr (D-12). Fehlt ein
// Schlüssel in den Daten, wirft die Funktion mit dem Namen des Schlüssels statt still auf 0 oder
// eine Ersatzzahl zu fallen.

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
    minderaufwand: gepZeile('globaler_minderaufwand', (wert) => -wert),
    ergebnisNach: gepZeile('ergebnis_nach_minderaufwand'),
  }
}
