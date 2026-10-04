// Zeitreihe je Steuerart (EINN-05, D-01). Signatur-Stub für den RED-Schritt.

import type { Grundzahl, Produkt } from '@/data/typen'

export interface ZeitreihenPosten {
  posten: string
  tabelle: 'steuerarten' | 'zuwendungen'
  grundzahlPraefix: string
}

export interface Zeitpunkt {
  jahr: number
  wert: number | null
  wertart: string
  quelle: 'grundzahlen' | 'vorbericht'
  pdfSeite: number | null
  gerundet: boolean
}

export interface ZeitreihenSerie {
  wertart: string
  werte: (number | null)[]
  geteilt: boolean[]
}

export interface Zeitreihe {
  jahre: number[]
  serien: ZeitreihenSerie[]
}

export const ZEITREIHEN_PRODUKT = ''
export const STANDARD_ZEITREIHE = ''
export const ZEITREIHEN_POSTEN: readonly ZeitreihenPosten[] = []

export function findeGrundzahl(
  _eintrag: ZeitreihenPosten,
  _produkte?: readonly Produkt[],
): Grundzahl {
  throw new Error('nicht umgesetzt')
}

export function baueZeitreihe(_posten: string): Zeitpunkt[] {
  return []
}

export function zeitreihenSerien(_punkte: readonly Zeitpunkt[]): Zeitreihe {
  return { jahre: [], serien: [] }
}

export function zeitreihenOptionen(): { posten: string; name: string }[] {
  return []
}

export function zeitreihenSeite(_posten: string): number | null {
  return null
}

export function quellenFussnote(_punkte: readonly Zeitpunkt[]): string {
  return ''
}
