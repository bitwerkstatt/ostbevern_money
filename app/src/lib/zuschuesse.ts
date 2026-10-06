// Einzelzuschüsse des Haushaltsjahrs aus den Vorbericht-Tabellen (RAT-03, D-03): die
// Kindertageseinrichtungen (S. 46), das Kinder- und Jugendwerk und der Offene Ganztag
// (Transferaufwendungen, S. 46) sowie die acht Einzelposten der Zuschüsse für laufende Zwecke
// (S. 47). Werte werden aus `haushalt.json` gelesen, nie neu berechnet. Alle Beträge sind
// T€-Werte × 1000 und deshalb gerundet; die App zeigt sie als „rd.“.

import { haushalt } from '@/data/daten'
import type { VorberichtPosten, VorberichtTabelle } from '@/data/typen'

export interface Zuschuss {
  schluessel: string
  name: string
  /** Betrag in Euro; `null`, wenn der Vorbericht für das Haushaltsjahr keinen Wert nennt. */
  wert: number | null
  /** `true`, wenn der Betrag nur auf T€ genau ist (Vorbericht-Abschrift × 1000). */
  gerundet: boolean
  /** 1-basierte PDF-Seite des Postens; `null`, falls die Daten keine Seite nennen. */
  pdfSeite: number | null
}

export interface ZuschussGruppe {
  posten: Zuschuss[]
  /** Gedruckte Gesamtzeile der Tabelle im Haushaltsjahr; `null`, wenn keine gedruckt ist. */
  gesamt: number | null
  /** Sortierte, eindeutige PDF-Seiten, die die Gruppe belegen. */
  pdfSeiten: number[]
}

/** Tabellen der manuellen Vorbericht-Daten (Schlüssel in `haushalt.vorbericht`). */
const KITA_TABELLE = 'kita_zuschuesse'
const LFD_ZWECKE_TABELLE = 'zuschuesse_lfd_zwecke'
const TRANSFER_TABELLE = 'transferaufwendungen'

/** Die zwei eigenen Zuschüsse unter den Transferaufwendungen (Kinder- und Jugendwerk, OGS). */
const TRANSFER_ZUSCHUESSE = ['zuschuss_kinder_jugendwerk', 'zuschuss_ogs'] as const

/** Gesetzliche Sozialleistungen unter den Transferaufwendungen (D-02). */
export const SOZIALLEISTUNGEN_SCHLUESSEL = 'sozialleistungen'

function jahrIndex(): number {
  const index = haushalt.jahre.indexOf(haushalt.haushaltsjahr)
  if (index < 0) {
    throw new Error(`Haushaltsjahr ${String(haushalt.haushaltsjahr)} steht nicht in haushalt.jahre`)
  }
  return index
}

/** Eine Vorberichtstabelle; eine fehlende Tabelle ist ein Datenfehler und wirft. */
export function vorberichtTabelle(name: string): VorberichtTabelle {
  const tabelle = haushalt.vorbericht[name]
  if (tabelle === undefined) {
    throw new Error(`Die Vorberichtstabelle „${name}“ fehlt in haushalt.json`)
  }
  return tabelle
}

/** Ein Posten einer Vorberichtstabelle; ein fehlender Posten ist ein Datenfehler und wirft. */
export function vorberichtPosten(tabelle: string, schluessel: string): VorberichtPosten {
  const posten = vorberichtTabelle(tabelle).posten.find((p) => p.posten === schluessel)
  if (posten === undefined) {
    throw new Error(`Der Posten „${schluessel}“ fehlt in der Vorberichtstabelle „${tabelle}“`)
  }
  return posten
}

/** Der Posten im Haushaltsjahr als `Zuschuss`; ohne Wert bleibt `wert` `null` (nie 0). */
export function alsZuschuss(posten: VorberichtPosten, index: number = jahrIndex()): Zuschuss {
  return {
    schluessel: posten.posten,
    name: posten.name,
    wert: posten.werte[index] ?? null,
    gerundet: posten.gerundet,
    pdfSeite: posten.quelle,
  }
}

function seitenVon(posten: readonly Zuschuss[], weitere: readonly (number | null)[]): number[] {
  const seiten = new Set<number>()
  for (const seite of [...posten.map((p) => p.pdfSeite), ...weitere]) {
    if (seite !== null) {
      seiten.add(seite)
    }
  }
  return Array.from(seiten).sort((a, b) => a - b)
}

function gruppeAusTabelle(name: string, index: number): ZuschussGruppe {
  const tabelle = vorberichtTabelle(name)
  const posten = tabelle.posten.map((p) => alsZuschuss(p, index))
  return {
    posten,
    gesamt: tabelle.gesamt_vorbericht.werte[index] ?? null,
    pdfSeiten: seitenVon(posten, [tabelle.gesamt_vorbericht.quelle]),
  }
}

/** Die Kindertageseinrichtungen einzeln, mit der gedruckten Gesamtzeile (S. 46). */
export function kitaZuschuesse(): ZuschussGruppe {
  return gruppeAusTabelle(KITA_TABELLE, jahrIndex())
}

/**
 * Die weiteren Zuschüsse in zwei Quellgruppen: die eigenen Zuschüsse der Transferaufwendungen
 * (`transfer`) und die Einzelposten der Zuschüsse für laufende Zwecke (`lfdZwecke`).
 */
export function weitereZuschuesse(): { transfer: ZuschussGruppe; lfdZwecke: ZuschussGruppe } {
  const index = jahrIndex()
  const posten = TRANSFER_ZUSCHUESSE.map((schluessel) =>
    alsZuschuss(vorberichtPosten(TRANSFER_TABELLE, schluessel), index),
  )
  return {
    transfer: { posten, gesamt: null, pdfSeiten: seitenVon(posten, []) },
    lfdZwecke: gruppeAusTabelle(LFD_ZWECKE_TABELLE, index),
  }
}

/**
 * Die Summe einer Gruppe für die Zeile „zusammen“: die gedruckte Gesamtzeile, sonst die Summe der
 * vorhandenen Werte; ohne einen einzigen Wert `null` (kein erfundenes 0).
 */
export function zusammen(gruppe: ZuschussGruppe): number | null {
  if (gruppe.gesamt !== null) {
    return gruppe.gesamt
  }
  const werte = gruppe.posten.flatMap((p) => (p.wert === null ? [] : [p.wert]))
  return werte.length === 0 ? null : werte.reduce((summe, wert) => summe + wert, 0)
}

// RED-Stand (Task 2): Signaturen ohne Implementierung.
export const SOZIALLEISTUNGEN_BEZEICHNUNG = 'Gesetzliche Sozialleistungen'

export interface NichtBeeinflussbar {
  posten: Zuschuss[]
  klGesamt: number
  klName: string
}

export function ohneLeere(posten: readonly Zuschuss[]): Zuschuss[] {
  return [...posten]
}

export function nichtBeeinflussbar(): NichtBeeinflussbar {
  return { posten: [], klGesamt: 0, klName: '' }
}
