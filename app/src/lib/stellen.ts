// Stellenplan-Seite (STEL-01 bis STEL-03): Summen aus `stellenplan.json`. Alle Summen laufen in
// ganzen Hundertstel VZÄ (`Math.round(stellen × 100)`) und werden erst zur Anzeige durch 100
// geteilt (`alsVzae`), damit kein Fließkommafehler wie 62,90999… entsteht (RESEARCH Pattern 6,
// Pitfall 5). Gezählt werden nur die Merkmale „stellen“ und „besetzt“; „davon_ausgesondert“ und
// die Nachwuchskräfte gehen nie ein. Zeilen mit Produktbereich (Stellenübersicht nach
// Aufgabenbereich) sind eine zweite Sicht auf dieselben Stellen und werden nie zu den Teil-
// Summen addiert (D-15). Jahre stammen aus den Daten, nie aus dem Code.

import { vzae } from '@/charts/format'
import { stellenplan } from '@/data/daten'
import type { Stellenplan, StellenplanZeile } from '@/data/typen'

export interface TeilInfo {
  /** Wert von `StellenplanZeile.teil`. */
  teil: string
  /** Anzeigename des Teils. */
  name: string
  /** Überschrift des Gruppenabschnitts (D-17). */
  gruppenTitel: string
}

/** Die drei Teile des Stellenplans in fester Reihenfolge (D-15, D-17). */
export const TEILE: readonly TeilInfo[] = [
  { teil: 'beamte', name: 'Beamtinnen und Beamte', gruppenTitel: 'Besoldung' },
  { teil: 'tarif', name: 'Tarifbeschäftigte', gruppenTitel: 'Entgelt' },
  {
    teil: 'sozial_erziehungsdienst',
    name: 'Sozial- und Erziehungsdienst',
    gruppenTitel: 'Sozial- und Erziehungsdienst',
  },
]

/** Hundertstel einer Stellenzeile; eine Zeile ohne Wert ist ein Datenfehler und wirft. */
function hundertstel(zeile: StellenplanZeile): number {
  if (zeile.stellen === null) {
    throw new Error(
      `Stellenzeile ohne Stellenwert: Teil ${zeile.teil}, Position ${String(zeile.position)}, Merkmal ${zeile.merkmal}`,
    )
  }
  return Math.round(zeile.stellen * 100)
}

/** Summe in Hundertstel oder `null`, wenn keine Zeile zählt (nie 0 erfinden). */
function summe(zeilen: readonly StellenplanZeile[]): number | null {
  if (zeilen.length === 0) {
    return null
  }
  return zeilen.reduce((gesamt, zeile) => gesamt + hundertstel(zeile), 0)
}

/** Eindeutige PDF-Seiten, aufsteigend. */
function seiten(zeilen: readonly StellenplanZeile[]): number[] {
  return [...new Set(zeilen.map((zeile) => zeile.pdf_seite))].sort((a, b) => a - b)
}

/** Teil-A/B-Zeilen (ohne Produktbereich) mit dem Merkmal „stellen“ des Jahres `jahr`. */
function stellenZeilen(daten: Stellenplan, jahr: number): StellenplanZeile[] {
  return daten.zeilen.filter(
    (zeile) => zeile.produktbereich === null && zeile.merkmal === 'stellen' && zeile.jahr === jahr,
  )
}

/** Teil-A/B-Zeilen (ohne Produktbereich) mit dem Merkmal „besetzt“. */
function besetztZeilen(daten: Stellenplan): StellenplanZeile[] {
  return daten.zeilen.filter(
    (zeile) => zeile.produktbereich === null && zeile.merkmal === 'besetzt',
  )
}

/** Das Jahr vor dem Haushaltsjahr der Daten. */
function vorjahrVon(daten: Stellenplan): number {
  return daten.haushaltsjahr - 1
}

/** Hundertstel VZÄ als VZÄ für die Anzeige über `vzae()`. */
export function alsVzae(hundertstelWert: number): number {
  return hundertstelWert / 100
}

/**
 * Differenz zweier Hundertstelwerte als Text mit Vorzeichen für die Anzeige, z. B. „+0,78“ oder
 * „−6,28“ (echtes Minuszeichen, UI-SPEC „{+/−}{Wert}“). Fehlt ein Wert, gibt es keine Differenz
 * (`null`), nie eine erfundene 0 (UI-SPEC E10 empty).
 */
export function differenzText(wert: number | null, vergleich: number | null): string | null {
  if (wert === null || vergleich === null) {
    return null
  }
  const differenz = wert - vergleich
  if (differenz === 0) {
    return vzae(0)
  }
  return `${differenz > 0 ? '+' : '−'}${vzae(alsVzae(Math.abs(differenz)))}`
}

export interface StellenSummen {
  /** Stellen des Haushaltsjahrs in Hundertstel, `null` ohne Zeilen. */
  haushaltsjahr: number | null
  /** Stellen des Vorjahrs in Hundertstel, `null` ohne Zeilen. */
  vorjahr: number | null
  /** Besetzte Stellen am Stichtag in Hundertstel, `null` ohne Zeilen. */
  besetzt: number | null
  /** ISO-Stichtag der besetzten Stellen, `null` ohne Zeilen. */
  stichtag: string | null
  /** Belegende PDF-Seiten, aufsteigend. */
  pdfSeiten: number[]
}

/** Der eine Stichtag des besetzten Standes; mehrere verschiedene Stichtage sind ein Datenfehler. */
function stichtagVon(zeilen: readonly StellenplanZeile[]): string | null {
  const stichtage = new Set(
    zeilen.flatMap((zeile) => (zeile.stichtag === null ? [] : [zeile.stichtag])),
  )
  if (stichtage.size > 1) {
    throw new Error(`Der besetzte Stand nennt mehrere Stichtage: ${[...stichtage].join(', ')}`)
  }
  return [...stichtage][0] ?? null
}

/** Gesamtsummen über alle Teile: Haushaltsjahr, Vorjahr und besetzt (STEL-01, D-15). */
export function stellenSummen(daten: Stellenplan = stellenplan): StellenSummen {
  const hj = stellenZeilen(daten, daten.haushaltsjahr)
  const vj = stellenZeilen(daten, vorjahrVon(daten))
  const besetzt = besetztZeilen(daten)
  return {
    haushaltsjahr: summe(hj),
    vorjahr: summe(vj),
    besetzt: summe(besetzt),
    stichtag: stichtagVon(besetzt),
    pdfSeiten: seiten([...hj, ...vj, ...besetzt]),
  }
}

export interface TeilSummen extends TeilInfo {
  haushaltsjahr: number | null
  vorjahr: number | null
  besetzt: number | null
}

/** Die drei Werte je Teil in Hundertstel, in der Reihenfolge von `TEILE` (STEL-01, D-15). */
export function stellenNachTeil(daten: Stellenplan = stellenplan): TeilSummen[] {
  const vorjahr = vorjahrVon(daten)
  return TEILE.map((info) => ({
    ...info,
    haushaltsjahr: summe(
      stellenZeilen(daten, daten.haushaltsjahr).filter((zeile) => zeile.teil === info.teil),
    ),
    vorjahr: summe(stellenZeilen(daten, vorjahr).filter((zeile) => zeile.teil === info.teil)),
    besetzt: summe(besetztZeilen(daten).filter((zeile) => zeile.teil === info.teil)),
  }))
}

export interface Nachwuchs {
  /** Personen im Vorjahr („beschäftigt“), `null` ohne Zeilen. */
  vorjahr: number | null
  /** Personen im Haushaltsjahr („vorgesehen“), `null` ohne Zeilen. */
  haushaltsjahr: number | null
  /** Belegende PDF-Seiten, aufsteigend. */
  pdfSeiten: number[]
}

function personen(zeilen: readonly StellenplanZeile[]): number | null {
  if (zeilen.length === 0) {
    return null
  }
  return zeilen.reduce((gesamt, zeile) => gesamt + (zeile.personen ?? 0), 0)
}

/**
 * Personenzahlen der Nachwuchskräfte (D-15): Vorjahr „beschäftigt“, Haushaltsjahr „vorgesehen“.
 * Sie sind Personen, nie Stellen, und gehen in keine Stellensumme ein.
 */
export function nachwuchs(daten: Stellenplan = stellenplan): Nachwuchs {
  const zeilen = daten.zeilen.filter((zeile) => zeile.teil === 'nachwuchs')
  const vorjahr = zeilen.filter(
    (zeile) => zeile.merkmal === 'beschaeftigt' && zeile.jahr === vorjahrVon(daten),
  )
  const haushaltsjahr = zeilen.filter(
    (zeile) => zeile.merkmal === 'vorgesehen' && zeile.jahr === daten.haushaltsjahr,
  )
  return {
    vorjahr: personen(vorjahr),
    haushaltsjahr: personen(haushaltsjahr),
    pdfSeiten: seiten([...vorjahr, ...haushaltsjahr]),
  }
}
