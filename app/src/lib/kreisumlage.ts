// „Weitergabe an Kreis und Land“ (KL): Gesamtbetrag und die drei Unterposten für den
// Kreisumlage-Hinweis (D-07, START-02, AUSG-02). Werte werden aus `haushalt.json`
// gelesen, nie neu berechnet. Der Gesamtbetrag ist eurogenau (Teilergebnisplan), die
// Unterposten sind aus T€-Werten des Vorberichts abgeleitet und deshalb gerundet (P4 D-02).

import { haushalt } from '@/data/daten'
import type { Knoten } from '@/data/typen'
import { baueAufwandsarten } from '@/lib/aufwandsarten'

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

/** Posten der Vorbericht-Tabelle „Transferaufwendungen“, der die Kreisumlage trägt. */
const KREISUMLAGE_POSTEN = 'kreisumlage'

/** Schlüssel der Aufwandsart „Transferaufwendungen“, in der die Kreisumlage selbst liegt. */
const TRANSFER_ART = 'transferaufwendungen'

/**
 * Die Kreisumlage allein (Vorbericht, Tabelle „Transferaufwendungen“, T€ × 1000, also „rd.“)
 * im gewählten Jahr. Wirft, wenn die Daten den Posten oder das Jahr nicht nennen.
 */
export function kreisumlageWert(jahrIndex: number): number {
  const posten = haushalt.vorbericht.transferaufwendungen?.posten.find(
    (p) => p.posten === KREISUMLAGE_POSTEN,
  )
  const wert = posten?.werte[jahrIndex]
  if (wert === null || wert === undefined) {
    throw new Error(`Keine Kreisumlage im Jahresindex ${String(jahrIndex)}`)
  }
  return wert
}

/** Die Beträge, aus denen sich der Superlativ „größter Einzelposten“ ergibt. */
export interface EinzelpostenVergleich {
  /** Aufwand der „Weitergabe an Kreis und Land“. */
  gesamt: number
  /** Aufwand aller übrigen Aufgabenbereiche. */
  bereiche: readonly number[]
  /** Die Kreisumlage allein. */
  kreisumlage: number
  /** Alle Aufwandsarten außer den Transferaufwendungen. */
  aufwandsarten: readonly number[]
}

/**
 * Reine Prüfung (G-09-01): „Weitergabe an Kreis und Land“ ist nur dann der größte Einzelposten,
 * wenn sie größer ist als jeder andere Aufgabenbereich und die Kreisumlage größer als jede
 * Aufwandsart ohne die Transferaufwendungen. Gleichstand ist kein „größter“ Posten.
 */
export function pruefeGroessterEinzelposten(vergleich: EinzelpostenVergleich): boolean {
  return (
    vergleich.bereiche.every((wert) => vergleich.gesamt > wert) &&
    vergleich.aufwandsarten.every((wert) => vergleich.kreisumlage > wert)
  )
}

/**
 * Gilt der Superlativ „größter Einzelposten“ für die Weitergabe an Kreis und Land im Jahr? Die
 * Startseite nennt ihn nur, wenn die Daten ihn tragen; kippt er mit einem Jahrgang, fällt der
 * Satz auf die neutrale Fassung zurück (G-09-01).
 */
export function istGroessterEinzelposten(jahrIndex: number): boolean {
  const kl = findeKlKnoten()
  return pruefeGroessterEinzelposten({
    gesamt: aufwand(kl.code, jahrIndex),
    bereiche: haushalt.knoten
      .filter((k) => k.eltern === 'GESAMT' && k.code !== kl.code)
      .map((k) => aufwand(k.code, jahrIndex)),
    kreisumlage: kreisumlageWert(jahrIndex),
    aufwandsarten: baueAufwandsarten(jahrIndex)
      .filter((a) => a.schluessel !== TRANSFER_ART)
      .map((a) => a.wert),
  })
}
