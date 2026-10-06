// Ausgaben nach Aufwandsart (AUSG-04, Spez. 6.5 „Zweite Sicht“): die sieben Aufwandsarten des
// Gesamtergebnisplans. Werte werden gelesen, nie neu berechnet; nur der Anteil ist
// `wert / berechnet.aufwand`. Die Namen kommen aus `zeilen_namen`.

import { euro, jahr as formatiereJahr } from '@/charts/format'
import { haushalt } from '@/data/daten'
import { belegSchluessel } from '@/lib/quelle'
import { textFuerJahr } from '@/lib/texte'
import { zeilenName } from '@/lib/zeilen'

/** Schlüssel der GEP-Zeile 27 „Globaler Minderaufwand“. */
const MINDERAUFWAND_ZEILE = 'globaler_minderaufwand'

/** Die Zeile „Abschreibungen“: Wertverlust, kein Geldfluss (fachliche Regel, Spez. 3.6). */
export const ABSCHREIBUNG_ZEILE = 'abschreibungen'

export interface Aufwandsart {
  schluessel: string
  /** Gedruckte Zeilennummer im Gesamtergebnisplan, z. B. „15“. */
  nummer: string
  name: string
  wert: number
  /** Anteil am Gesamtaufwand des Jahres (0–1). */
  anteil: number
  /** `true` nur für die Abschreibungen. */
  keinGeldfluss: boolean
}

/** Zeilen 11–16 (ohne Summen) plus 20 Zinsaufwendungen: fachliche Regel, Spez. 6.5. */
function istAufwandsart(nummer: string, istSumme: boolean): boolean {
  if (istSumme) {
    return false
  }
  return (nummer >= '11' && nummer <= '16') || nummer === '20'
}

export function baueAufwandsarten(jahrIndex: number): Aufwandsart[] {
  const gesamt = haushalt.ergebnisplan.GESAMT
  if (gesamt === undefined) {
    throw new Error('Ergebnisplan GESAMT fehlt in haushalt.json')
  }
  const aufwand = gesamt.berechnet.aufwand[jahrIndex]
  if (aufwand === undefined) {
    throw new Error(`Jahresindex ${String(jahrIndex)} liegt außerhalb der Jahre`)
  }

  const reihen: Aufwandsart[] = []
  for (const zeile of haushalt.zeilen_namen.ergebnisplan) {
    if (!istAufwandsart(zeile.nummer, zeile.ist_summe)) {
      continue
    }
    const wert = gesamt.zeilen[zeile.schluessel]?.[jahrIndex] ?? 0
    if (wert === 0) {
      continue
    }
    reihen.push({
      schluessel: zeile.schluessel,
      nummer: zeile.nummer,
      name: zeilenName('ergebnisplan', zeile.schluessel),
      wert,
      anteil: aufwand === 0 ? 0 : wert / aufwand,
      keinGeldfluss: zeile.schluessel === ABSCHREIBUNG_ZEILE,
    })
  }
  return reihen.sort((a, b) => b.wert - a.wert)
}

/** Eine Zeile der Vorbericht-Tabelle „Transferaufwendungen“ (T€-Werte × 1000, daher gerundet). */
export interface TransferPosten {
  posten: string
  name: string
  wert: number
  /** Immer `true` für Vorbericht-Werte: die App zeigt „rd.“. */
  gerundet: boolean
  /** 1-basierte PDF-Seite; `null`, falls die Daten keine Seite nennen. */
  quelle: number | null
  /** Belegschlüssel der Zeile (`lib/quelle.ts`), `null` ohne Quellseite. */
  beleg: string | null
  anmerkung: string | null
  /** Einzelne Kita-Einrichtungen, nur bei der Zeile der Kita-Zuschüsse und nur in Jahren mit Werten. */
  kinder?: TransferPosten[]
}

/** Der Posten der Kita-Zuschüsse, unter dem die einzelnen Einrichtungen stehen (MANU-04). */
const KITA_ZEILE = 'zuschuesse_kindertageseinrichtungen'

function pruefeJahrIndex(jahrIndex: number): void {
  if (haushalt.jahre[jahrIndex] === undefined) {
    throw new Error(`Jahresindex ${String(jahrIndex)} liegt außerhalb der Jahre`)
  }
}

function tabelle(name: string) {
  const treffer = haushalt.vorbericht[name]
  if (treffer === undefined) {
    throw new Error(`Vorberichtstabelle „${name}“ fehlt in haushalt.json`)
  }
  return treffer
}

/** Verweis „(siehe Fußnote)“ am Ende eines gedruckten Postennamens. */
const FUSSNOTEN_VERWEIS = /\s*\(siehe Fußnote\)$/

/**
 * Posten der Tabelle mit Wert im Jahr; ein Posten ohne gedruckten Wert entfällt (nie als 0).
 * Trägt der Posten keine Anmerkung in den Daten, entfällt auch der Verweis „(siehe Fußnote)“ im
 * Namen, damit die Tabelle nicht auf eine Fußnote verweist, die sie nicht zeigt.
 */
function postenMitWert(tabellenName: string, jahrIndex: number): TransferPosten[] {
  return tabelle(tabellenName).posten.flatMap((p) => {
    const wert = p.werte[jahrIndex]
    if (wert === null || wert === undefined) {
      return []
    }
    return [
      {
        posten: p.posten,
        name: p.anmerkung === null ? p.name.replace(FUSSNOTEN_VERWEIS, '') : p.name,
        wert,
        gerundet: p.gerundet,
        quelle: p.quelle,
        beleg: p.quelle === null ? null : belegSchluessel.vb(tabellenName, p.posten),
        anmerkung: p.anmerkung,
      },
    ]
  })
}

function absteigend(posten: TransferPosten[]): TransferPosten[] {
  return posten.sort((a, b) => b.wert - a.wert)
}

/**
 * Die Vorbericht-Tabelle „Transferaufwendungen“ des Jahres (absteigend). Die einzelnen
 * Kita-Einrichtungen hängen an den Kita-Zuschüssen und erscheinen nur in Jahren, in denen der
 * Vorbericht sie druckt (nur im Haushaltsjahr). Alle Werte sind T€ × 1000, also „rd.“.
 */
export function baueTransferaufwendungen(jahrIndex: number): TransferPosten[] {
  pruefeJahrIndex(jahrIndex)
  const kinder = absteigend(postenMitWert('kita_zuschuesse', jahrIndex))
  return absteigend(
    postenMitWert('transferaufwendungen', jahrIndex).map((p) =>
      p.posten === KITA_ZEILE && kinder.length > 0 ? { ...p, kinder } : p,
    ),
  )
}

export interface MinderaufwandHinweis {
  /** Positiver Betrag: der Aufwand sinkt um diese Summe. */
  betrag: number
  jahr: number
  /** Schlüssel des geprüften Erklärtexts, nur im Haushaltsjahr (Pitfall 6), sonst `null`. */
  textSchluessel: string | null
  /** Aus den Daten des Jahres zusammengesetzter Satz (für Jahre ohne geprüften Text). */
  satz: string
  pdfSeite: number | null
}

/** Schlüssel des geprüften Erklärtexts zum globalen Minderaufwand. */
const MINDERAUFWAND_TEXT = 'globaler_minderaufwand'

/**
 * Der Hinweis „Globaler Minderaufwand“ des Jahres oder `null`, wenn der Gesamtergebnisplan
 * für das Jahr keinen Minderaufwand führt (2024). Der geprüfte Erklärtext nennt Zahlen des
 * Haushaltsjahrs und gilt nur dort (RESEARCH Pitfall 6); für andere Jahre entsteht ein Satz
 * aus dem Betrag und dem Jahr der Daten, ohne Behauptungen über andere Jahre.
 */
export function minderaufwandHinweis(jahrIndex: number): MinderaufwandHinweis | null {
  pruefeJahrIndex(jahrIndex)
  const jahr = haushalt.jahre[jahrIndex]
  const wert = haushalt.ergebnisplan.GESAMT?.zeilen[MINDERAUFWAND_ZEILE]?.[jahrIndex]
  if (jahr === undefined || wert === undefined || wert === 0) {
    return null
  }
  // Der Gesamtergebnisplan führt die Kürzung mit negativem Vorzeichen.
  const betrag = -wert
  const hatGepruefterText = textFuerJahr(MINDERAUFWAND_TEXT, jahr) !== null
  return {
    betrag,
    jahr,
    textSchluessel: hatGepruefterText ? MINDERAUFWAND_TEXT : null,
    satz: `Für ${formatiereJahr(jahr)} setzt der Plan einen globalen Minderaufwand von ${euro(betrag)} an. Das ist ein pauschaler Kürzungsbetrag auf die geplanten Ausgaben.`,
    pdfSeite: haushalt.knoten.find((k) => k.code === 'GESAMT')?.pdf_seite ?? null,
  }
}
