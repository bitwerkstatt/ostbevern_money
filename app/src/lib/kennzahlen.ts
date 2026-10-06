// Startseite: Kennzahlenband (START-01, sieben Kennzahlen des Haushaltsjahrs) und die
// Datensätze der beiden Einstiegskacheln (START-02, D-20). Alle Werte werden aus
// `haushalt.json` gelesen; nur die beiden Pro-Kopf-Werte sind berechnet (`proKopf`,
// gerundet). Die Seite zeigt die Zahlen über `charts/format.ts`.

import { jahr as formatJahr } from '@/charts/format'
import { haushalt, investitionen } from '@/data/daten'
import type { Knoten } from '@/data/typen'
import { proKopf } from '@/lib/berechnung'
import { baueErtragsarten } from '@/lib/ertragsarten'
import { wertartFuerJahr, wertartName } from '@/lib/jahr'
import { belegSchluessel } from '@/lib/quelle'

export interface Kennzahl {
  schluessel: string
  bezeichnung: string
  /** Betrag in Euro (mit Vorzeichen) bzw. Euro pro Einwohner. */
  wert: number
  /** `kurz` = `euroKurz` (Mio. €), `euro` = voller Betrag (Pro-Kopf-Werte). */
  anzeige: 'kurz' | 'euro'
  /** Anzeigename der Wertart des Jahres, z. B. „Ansatz“. */
  wertart: string
  jahr: number
  /** 1-basierte PDF-Seiten, die den Wert belegen. */
  pdfSeiten: number[]
  /** `true`, wenn der Wert nicht im PDF steht, sondern berechnet ist. */
  berechnet: boolean
  /** Belegschlüssel der Zeile, die der Wert belegt (`lib/quelle.ts`, Grammatik `ep:`/`fp:`). */
  quelle: string
  /**
   * Herleitung für die Quell-Seitenleiste (D-03), wenn der angezeigte Wert aus mehr als der
   * belegten Zeile besteht; sonst `null`. Namen, Zeilennummern und Seiten stammen aus den Daten.
   */
  herleitung: string | null
}

/** Zeile unter einem Wert: „{Wertart} {jahr} · PDF-Seite {n}“ (D-10, UI-SPEC KennzahlKachel). */
export function quellenZeile(wertart: string, jahr: number, pdfSeiten: readonly number[]): string {
  const seiten = pdfSeiten.join(', ')
  const wort = pdfSeiten.length === 1 ? 'PDF-Seite' : 'PDF-Seiten'
  return `${wertart} ${formatJahr(jahr)} · ${wort} ${seiten}`
}

function jahrIndex(): number {
  const index = haushalt.jahre.indexOf(haushalt.haushaltsjahr)
  if (index < 0) {
    throw new Error(`Haushaltsjahr ${String(haushalt.haushaltsjahr)} steht nicht in haushalt.jahre`)
  }
  return index
}

function wertAn(werte: readonly number[] | undefined, index: number, name: string): number {
  const wert = werte?.[index]
  if (wert === undefined) {
    throw new Error(`Kein Wert für ${name} im Jahresindex ${String(index)}`)
  }
  return wert
}

function einwohnerZahl(): number {
  const wert = haushalt.meta.einwohner.wert
  if (typeof wert !== 'number') {
    throw new Error('meta.einwohner.wert muss eine Zahl sein')
  }
  return wert
}

/** Gedruckte Seite des Gesamtergebnisplans (Knoten GESAMT). */
function ergebnisplanSeite(): number {
  const seite = haushalt.knoten.find((knoten) => knoten.code === 'GESAMT')?.pdf_seite
  if (seite === null || seite === undefined) {
    throw new Error('Der Knoten GESAMT nennt keine PDF-Seite')
  }
  return seite
}

/** Gedruckter Name und Zeilennummer einer Ergebnisplan-Zeile: „Ordentliche Erträge (Zeile 10)“. */
function zeilenBezug(schluessel: string): string {
  const eintrag = haushalt.zeilen_namen.ergebnisplan.find(
    (zeile) => zeile.schluessel === schluessel,
  )
  if (eintrag === undefined) {
    throw new Error(`Die Ergebnisplan-Zeile ${schluessel} fehlt in haushalt.zeilen_namen`)
  }
  return `${eintrag.name} (Zeile ${eintrag.nummer})`
}

export function baueKennzahlen(): Kennzahl[] {
  const index = jahrIndex()
  const jahr = haushalt.haushaltsjahr
  const wertart = wertartName(wertartFuerJahr(jahr))
  const gesamt = haushalt.ergebnisplan.GESAMT
  const finanzplan = haushalt.finanzplan.GESAMT
  if (gesamt === undefined || finanzplan === undefined) {
    throw new Error('Ergebnisplan oder Finanzplan GESAMT fehlt in haushalt.json')
  }

  const epSeite = ergebnisplanSeite()
  const fpSeite = investitionen.finanzierung.quelle
  const einwohnerSeite = haushalt.meta.einwohner.quelle

  const ertraege = wertAn(gesamt.berechnet.ertraege, index, 'Erträge')
  const aufwand = wertAn(gesamt.berechnet.aufwand, index, 'Aufwendungen')
  const ergebnis = wertAn(
    gesamt.zeilen.ergebnis_nach_minderaufwand,
    index,
    'Ergebnis nach Minderaufwand',
  )
  const steuern = wertAn(gesamt.zeilen.steuern, index, 'Steuern')
  const einwohner = einwohnerZahl()

  const basis = { wertart, jahr }
  const herleitungErtraege = `${zeilenBezug('ordentliche_ertraege')} plus ${zeilenBezug('finanzertraege')}`
  const herleitungAufwand = `${zeilenBezug('ordentliche_aufwendungen')} plus ${zeilenBezug('zinsaufwendungen')}`
  const durchEinwohner = `geteilt durch die Einwohnerzahl (PDF-Seite ${String(einwohnerSeite)})`
  return [
    {
      ...basis,
      schluessel: 'ertraege',
      bezeichnung: 'Erträge',
      wert: ertraege,
      anzeige: 'kurz',
      pdfSeiten: [epSeite],
      berechnet: false,
      quelle: belegSchluessel.ep('GESAMT', 'ordentliche_ertraege'),
      herleitung: herleitungErtraege,
    },
    {
      ...basis,
      schluessel: 'aufwendungen',
      bezeichnung: 'Aufwendungen',
      wert: aufwand,
      anzeige: 'kurz',
      pdfSeiten: [epSeite],
      berechnet: false,
      quelle: belegSchluessel.ep('GESAMT', 'ordentliche_aufwendungen'),
      herleitung: herleitungAufwand,
    },
    {
      ...basis,
      schluessel: 'ergebnis',
      bezeichnung: ergebnis < 0 ? 'Defizit nach Minderaufwand' : 'Überschuss nach Minderaufwand',
      wert: ergebnis,
      anzeige: 'kurz',
      pdfSeiten: [epSeite],
      berechnet: false,
      quelle: belegSchluessel.ep('GESAMT', 'ergebnis_nach_minderaufwand'),
      herleitung: null,
    },
    {
      ...basis,
      schluessel: 'investitionen',
      bezeichnung: 'Investitionen',
      wert: wertAn(finanzplan.zeilen.auszahlungen_investitionen, index, 'Investitionen'),
      anzeige: 'kurz',
      pdfSeiten: [fpSeite],
      berechnet: false,
      quelle: belegSchluessel.fp('GESAMT', 'auszahlungen_investitionen'),
      herleitung: null,
    },
    {
      ...basis,
      schluessel: 'kredite',
      bezeichnung: 'Neue Kredite',
      wert: wertAn(finanzplan.zeilen.kreditaufnahme, index, 'Kreditaufnahme'),
      anzeige: 'kurz',
      pdfSeiten: [fpSeite],
      berechnet: false,
      quelle: belegSchluessel.fp('GESAMT', 'kreditaufnahme'),
      herleitung: null,
    },
    {
      ...basis,
      schluessel: 'aufwand_pro_kopf',
      bezeichnung: 'Aufwand pro Einwohner',
      wert: proKopf(aufwand, einwohner),
      anzeige: 'euro',
      pdfSeiten: [epSeite, einwohnerSeite],
      berechnet: true,
      quelle: belegSchluessel.ep('GESAMT', 'ordentliche_aufwendungen'),
      herleitung: `(${herleitungAufwand}) ${durchEinwohner}`,
    },
    {
      ...basis,
      schluessel: 'steuern_pro_kopf',
      bezeichnung: 'Steuern pro Einwohner',
      wert: proKopf(steuern, einwohner),
      anzeige: 'euro',
      pdfSeiten: [epSeite, einwohnerSeite],
      berechnet: true,
      quelle: belegSchluessel.ep('GESAMT', 'steuern'),
      herleitung: `${zeilenBezug('steuern')} ${durchEinwohner}`,
    },
  ]
}

export interface Einstiege {
  wertart: string
  jahr: number
  /** Größte Ertragsart (EINN-01), z. B. „Steuern und ähnliche Abgaben“. */
  einnahmen: { name: string; wert: number; anteil: number; pdfSeite: number }
  /** Größter echter Aufgabenbereich, nie die synthetische „Weitergabe an Kreis und Land“ (D-20). */
  ausgaben: { code: string; name: string; wert: number; pdfSeite: number }
}

function seiteVon(code: string, name: string, pdfSeite: number | null): number {
  if (pdfSeite === null) {
    throw new Error(`Der Knoten „${name}“ (${code}) nennt keine PDF-Seite`)
  }
  return pdfSeite
}

/**
 * Datensätze der beiden Einstiegskacheln (START-02, D-20): größte Ertragsart und größter
 * Produktbereich unterhalb von GESAMT ohne synthetische Knoten. Die Auswahl folgt den
 * Daten; weder ein Produktbereichscode noch ein Name steht im Code.
 */
export function baueEinstiege(): Einstiege {
  const index = jahrIndex()
  const jahr = haushalt.haushaltsjahr
  const wertart = wertartName(wertartFuerJahr(jahr))

  const groesste = baueErtragsarten(index)[0]
  if (groesste === undefined) {
    throw new Error('Keine Ertragsart im Haushaltsjahr gefunden')
  }
  const gesamt = haushalt.knoten.find((knoten) => knoten.code === 'GESAMT')
  if (gesamt === undefined) {
    throw new Error('Der Knoten GESAMT fehlt in haushalt.json')
  }

  let bester: { knoten: Knoten; wert: number } | undefined
  for (const knoten of haushalt.knoten) {
    if (knoten.ebene !== 'PB' || knoten.eltern !== 'GESAMT' || knoten.synthetisch) {
      continue
    }
    const wert = wertAn(haushalt.ergebnisplan[knoten.code]?.berechnet.aufwand, index, knoten.name)
    if (bester === undefined || wert > bester.wert) {
      bester = { knoten, wert }
    }
  }
  if (bester === undefined) {
    throw new Error('Kein Aufgabenbereich unterhalb von GESAMT gefunden')
  }

  return {
    wertart,
    jahr,
    einnahmen: {
      name: groesste.name,
      wert: groesste.wert,
      anteil: groesste.anteil,
      pdfSeite: seiteVon(gesamt.code, gesamt.name, gesamt.pdf_seite),
    },
    ausgaben: {
      code: bester.knoten.code,
      name: bester.knoten.name,
      wert: bester.wert,
      pdfSeite: seiteVon(bester.knoten.code, bester.knoten.name, bester.knoten.pdf_seite),
    },
  }
}
