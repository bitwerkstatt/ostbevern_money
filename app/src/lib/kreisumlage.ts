// „Weitergabe an Kreis und Land“ (KL): Gesamtbetrag und die drei Unterposten für den
// Kreisumlage-Hinweis (D-07, START-02, AUSG-02). Werte werden aus `haushalt.json`
// gelesen, nie neu berechnet. Der Gesamtbetrag ist eurogenau (Teilergebnisplan), die
// Unterposten sind aus T€-Werten des Vorberichts abgeleitet und deshalb gerundet (P4 D-02).

import { haushalt } from '@/data/daten'
import type { Knoten } from '@/data/typen'

export interface Unterposten {
  code: string
  name: string
  wert: number
  /** Immer `true`: Betrag nur auf T€ genau, die App zeigt ihn als „rd.“. */
  gerundet: boolean
  /** 1-basierte PDF-Seite; `null`, falls die Daten keine Seite nennen. */
  pdfSeite: number | null
}

export interface Kreisumlage {
  name: string
  /** Eurogenauer Gesamtaufwand des KL-Knotens im gewählten Jahr. */
  gesamt: number
  unterposten: Unterposten[]
  pdfSeite: number | null
}

/**
 * Der eine synthetische Knoten unterhalb von GESAMT. Kein Code im Quelltext: wer den
 * Jahrgang wechselt, ändert nur die Daten (Konvention „keine Jahrgangswerte im Code“).
 */
export function findeKlKnoten(): Knoten {
  const treffer = haushalt.knoten.filter((k) => k.eltern === 'GESAMT' && k.synthetisch)
  const kl = treffer[0]
  if (treffer.length !== 1 || kl === undefined) {
    throw new Error(
      `Erwartet genau einen synthetischen Knoten unterhalb von GESAMT, gefunden: ${String(treffer.length)}`,
    )
  }
  return kl
}

function aufwand(code: string, jahrIndex: number): number {
  const wert = haushalt.ergebnisplan[code]?.berechnet.aufwand[jahrIndex]
  if (wert === undefined) {
    throw new Error(`Kein Aufwand für Knoten „${code}“ im Jahresindex ${String(jahrIndex)}`)
  }
  return wert
}

export function baueKreisumlage(jahrIndex: number): Kreisumlage {
  const kl = findeKlKnoten()
  const unterposten: Unterposten[] = []
  for (const knoten of haushalt.knoten) {
    if (knoten.eltern !== kl.code) {
      continue
    }
    const wert = aufwand(knoten.code, jahrIndex)
    if (wert === 0) {
      continue
    }
    unterposten.push({
      code: knoten.code,
      name: knoten.name,
      wert,
      gerundet: knoten.gerundet,
      pdfSeite: knoten.pdf_seite,
    })
  }
  return {
    name: kl.name,
    gesamt: aufwand(kl.code, jahrIndex),
    unterposten,
    pdfSeite: kl.pdf_seite,
  }
}
