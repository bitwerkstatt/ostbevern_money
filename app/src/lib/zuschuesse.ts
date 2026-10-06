// Einzelzuschüsse des Haushaltsjahrs aus den Vorbericht-Tabellen (RAT-03, D-03): die
// Kindertageseinrichtungen (S. 46), das Kinder- und Jugendwerk und der Offene Ganztag
// (Transferaufwendungen, S. 46) sowie die acht Einzelposten der Zuschüsse für laufende Zwecke
// (S. 47). Dazu die großen Posten, die der Rat nicht beeinflussen kann (RAT-02, D-02): die
// Weitergabe an Kreis und Land (über `lib/kreisumlage.ts`, wie auf /ausgaben) und die gesetzlichen
// Sozialleistungen. Werte werden aus `haushalt.json` gelesen, nie neu berechnet. Alle Beträge
// sind T€-Werte × 1000 und deshalb gerundet; die App zeigt sie als „rd.“.

import { haushalt } from '@/data/daten'
import type { VorberichtPosten, VorberichtTabelle } from '@/data/typen'
import { baueKreisumlage } from '@/lib/kreisumlage'
import { belegSchluessel, findeBeleg } from '@/lib/quelle'

export interface Zuschuss {
  schluessel: string
  name: string
  /** Betrag in Euro; `null`, wenn der Vorbericht für das Haushaltsjahr keinen Wert nennt. */
  wert: number | null
  /** `true`, wenn der Betrag nur auf T€ genau ist (Vorbericht-Abschrift × 1000). */
  gerundet: boolean
  /** 1-basierte PDF-Seite des Postens; `null`, falls die Daten keine Seite nennen. */
  pdfSeite: number | null
  /** Belegschlüssel der Quelle (`lib/quelle.ts`); `null`, wenn der Posten keine Seite nennt. */
  beleg: string | null
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

/** Schlüssel der Sozialleistungen unter den Transferaufwendungen (D-02). */
const SOZIALLEISTUNGEN_SCHLUESSEL = 'sozialleistungen'

/** Name der Kachel; der Vorbericht nennt den Posten nur „Sozialleistungen“. */
export const SOZIALLEISTUNGEN_BEZEICHNUNG = 'Gesetzliche Sozialleistungen'

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

/**
 * Der Posten der Vorberichtstabelle `tabelle` im Haushaltsjahr als `Zuschuss`; ohne Wert bleibt
 * `wert` `null` (nie 0), ohne Seite der Beleg `null`.
 */
export function alsZuschuss(
  tabelle: string,
  posten: VorberichtPosten,
  index: number = jahrIndex(),
): Zuschuss {
  return {
    schluessel: posten.posten,
    name: posten.name,
    wert: posten.werte[index] ?? null,
    gerundet: posten.gerundet,
    pdfSeite: posten.quelle,
    beleg: posten.quelle === null ? null : belegSchluessel.vb(tabelle, posten.posten),
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
  const posten = tabelle.posten.map((p) => alsZuschuss(name, p, index))
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
    alsZuschuss(TRANSFER_TABELLE, vorberichtPosten(TRANSFER_TABELLE, schluessel), index),
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

export interface NichtBeeinflussbar {
  /** Kacheln: die KL-Unterposten, dann die Sozialleistungen; ohne Posten mit 0 oder ohne Wert. */
  posten: Zuschuss[]
  /** Eurogenauer Gesamtaufwand der Weitergabe an Kreis und Land im Haushaltsjahr. */
  klGesamt: number
  klName: string
}

/** Posten mit dem Wert 0 oder ohne Wert sind keine Kachel (UI-SPEC E6 partial). */
export function ohneLeere(posten: readonly Zuschuss[]): Zuschuss[] {
  return posten.filter((p) => p.wert !== null && p.wert !== 0)
}

/**
 * Belegschlüssel eines KL-Unterpostens: der Vorberichtsposten gleichen Namens unter den
 * Transferaufwendungen (`KL.kreisumlage` gehört zu `vb:transferaufwendungen:kreisumlage`), sonst
 * die Seite des Knotens; ohne Seite `null`.
 */
function klBeleg(code: string, pdfSeite: number | null): string | null {
  const posten = code.slice(code.lastIndexOf('.') + 1)
  const vorbericht = belegSchluessel.vb(TRANSFER_TABELLE, posten)
  if (findeBeleg(vorbericht) !== null) {
    return vorbericht
  }
  return pdfSeite === null ? null : belegSchluessel.seite(pdfSeite)
}

/**
 * Was der Rat nicht beeinflussen kann (D-02): die KL-Unterposten wie auf /ausgaben und die
 * gesetzlichen Sozialleistungen. KL erscheint nur hier, nie als Bindungsgrad-Segment.
 */
export function nichtBeeinflussbar(): NichtBeeinflussbar {
  const index = jahrIndex()
  const kl = baueKreisumlage(index)
  const klPosten: Zuschuss[] = kl.unterposten.map((u) => ({
    schluessel: u.code,
    name: u.name,
    wert: u.wert,
    gerundet: u.gerundet,
    pdfSeite: u.pdfSeite,
    beleg: klBeleg(u.code, u.pdfSeite),
  }))
  const sozialleistungen: Zuschuss = {
    ...alsZuschuss(
      TRANSFER_TABELLE,
      vorberichtPosten(TRANSFER_TABELLE, SOZIALLEISTUNGEN_SCHLUESSEL),
      index,
    ),
    name: SOZIALLEISTUNGEN_BEZEICHNUNG,
  }
  return {
    posten: ohneLeere([...klPosten, sozialleistungen]),
    klGesamt: kl.gesamt,
    klName: kl.name,
  }
}
