// Ertragsarten der obersten Ebene (EINN-01): Start-Kachel und Einnahmen-Seite zeigen
// dieselben Zeilen mit demselben Betrag und Anteil. Werte werden gelesen, nie neu
// berechnet; nur der Anteil ist `wert / berechnet.ertraege`.

import { haushalt } from '@/data/daten'
import { zeilenName } from '@/lib/zeilen'

export interface Ertragsart {
  schluessel: string
  /** Gedruckte Zeilennummer im Gesamtergebnisplan, z. B. „01“. */
  nummer: string
  name: string
  wert: number
  /** Anteil an den Erträgen des Jahres (0–1). */
  anteil: number
}

/** Zeilen 01–09 (ohne Summen) plus 19 Finanzerträge: fachliche Regel, Spez. 3.2. */
function istErtragsart(nummer: string, istSumme: boolean): boolean {
  if (istSumme) {
    return false
  }
  return (nummer >= '01' && nummer <= '09') || nummer === '19'
}

export function baueErtragsarten(jahrIndex: number): Ertragsart[] {
  const gesamt = haushalt.ergebnisplan.GESAMT
  if (gesamt === undefined) {
    throw new Error('Ergebnisplan GESAMT fehlt in haushalt.json')
  }
  const ertraege = gesamt.berechnet.ertraege[jahrIndex]
  if (ertraege === undefined) {
    throw new Error(`Jahresindex ${String(jahrIndex)} liegt außerhalb der Jahre`)
  }

  const reihen: Ertragsart[] = []
  for (const zeile of haushalt.zeilen_namen.ergebnisplan) {
    if (!istErtragsart(zeile.nummer, zeile.ist_summe)) {
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
      anteil: ertraege === 0 ? 0 : wert / ertraege,
    })
  }
  return reihen.sort((a, b) => b.wert - a.wert)
}
