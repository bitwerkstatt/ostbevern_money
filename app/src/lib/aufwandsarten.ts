// Ausgaben nach Aufwandsart (AUSG-04, Spez. 6.5 „Zweite Sicht“): die sieben Aufwandsarten des
// Gesamtergebnisplans. Werte werden gelesen, nie neu berechnet; nur der Anteil ist
// `wert / berechnet.aufwand`. Die Namen kommen aus `zeilen_namen`.

import { haushalt } from '@/data/daten'
import { zeilenName } from '@/lib/zeilen'

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
  anmerkung: string | null
  /** Einzelne Kita-Einrichtungen, nur bei der Zeile der Kita-Zuschüsse und nur in Jahren mit Werten. */
  kinder?: TransferPosten[]
}

export function baueTransferaufwendungen(_jahrIndex: number): TransferPosten[] {
  return []
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

export function minderaufwandHinweis(_jahrIndex: number): MinderaufwandHinweis | null {
  return null
}
