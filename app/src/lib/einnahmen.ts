// Ebene 2 der Einnahmen-Seite (EINN-02 bis EINN-04, EINN-06). Rein lesend: Werte kommen aus
// `haushalt.vorbericht`, `haushalt.meta` und `haushalt.finanzplan`; nichts wird neu berechnet
// außer den beiden gekennzeichneten Resten „Sonstige“ (Vorbericht, schon in den Daten) und
// „Sonstige (berechnet)“ (investive Einnahmen, hier). Fehlende Werte sind `null`, nie 0.
// Finanzplan-Werte (investive Einnahmen) und Ergebnisplan-Werte (Erträge) bleiben getrennt
// (Spez. 3.1): die investiven Builder lesen nur `finanzplan` und `vorbericht.investitionszuwendungen`.

import { haushalt, investitionen } from '@/data/daten'
import type { VorberichtPosten, VorberichtTabelle } from '@/data/typen'
import { zeilenName } from '@/lib/zeilen'

/** Ein Posten einer Aufschlüsselung (Vorbericht-Tabelle), bereits für ein Jahr gelesen. */
export interface PostenZeile {
  posten: string
  name: string
  /** Euro; `null` ohne Wert für das Jahr (die Seite zeigt „–“). */
  wert: number | null
  /** `true`, wenn der Wert aus einer in T€ geführten Tabelle stammt (Anzeige „rd.“). */
  gerundet: boolean
  /** `true` für einen hergeleiteten Rest (Anzeige mit „berechnet“-Etikett). */
  berechnet: boolean
  /** 1-basierte PDF-Seite; `null` für einen Posten ohne eigene Quellseite. */
  quelle: number | null
  /** `true` für die Auflösung von Sonderposten: Ertrag ohne Geldzufluss (EINN-03). */
  keinGeldfluss: boolean
}

export interface SteuerZeile extends PostenZeile {
  /** `true`, wenn die Gemeinde die Steuer selbst festlegt (EINN-02). */
  selbstFestgelegt: boolean
  /** Hebesatz in Prozentpunkten (nur Haushaltsjahr gedruckt), sonst `null`. */
  hebesatz: number | null
  /** PDF-Seite des Hebesatzes, `null` ohne Hebesatz. */
  hebesatzQuelle: number | null
}

export interface SonstigeErtragZeile extends PostenZeile {
  /** Schlüssel des Hauptpostens, wenn die Zeile ein Teil davon ist (Konzessionsabgaben nach Sparte). */
  teilVon: string | null
}

export type InvestiveGruppe = 'pauschale' | 'sonstige' | 'finanzplan'

export interface InvestiveZeile {
  schluessel: string
  name: string
  wert: number | null
  gerundet: boolean
  berechnet: boolean
  /** 1-basierte PDF-Seite (Vorbericht S. 52 bzw. Gesamtfinanzplan). */
  quelle: number | null
  gruppe: InvestiveGruppe
}

/**
 * Steuern, deren Höhe die Gemeinde selbst bestimmt: Hebesatz (Grundsteuer A/B, Gewerbesteuer) bzw.
 * örtliche Steuer (Hunde-, Vergnügungssteuer). Fachliche Regel (Spez. 6.4); die Anteile an
 * Einkommen- und Umsatzsteuer und die Kompensationszahlungen kommen von Bund und Land.
 */
export const SELBST_FESTGELEGTE_STEUERN: readonly string[] = [
  'grundsteuer_a',
  'grundsteuer_b',
  'gewerbesteuer',
  'hundesteuer',
  'vergnuegungssteuer',
]

/**
 * Posten, die die Auflösung eines Sonderpostens abbilden: ein Ertrag ohne Geldzufluss
 * (Spez. 6.4). Sie tragen das Etikett „kein Geldfluss“, damit sie nicht als Einnahme gelten.
 */
export const SONDERPOSTEN_POSTEN: readonly string[] = [
  'aufloesung_sonderposten',
  'aufloesung_sonstiger_sonderposten',
]

/**
 * Pauschalen, die als eigene Balken der investiven Einnahmen erscheinen (Posten-Schlüssel aus
 * `vorbericht.investitionszuwendungen`, S. 52). Alles Übrige von Zeile 18 steht in
 * „Sonstige (berechnet)“.
 */
export const GEZEIGTE_PAUSCHALEN: readonly string[] = [
  'investitionspauschale',
  'schulpauschale',
  'sportpauschale',
]

export type Aufschluesselung = 'steuern' | 'zuwendungen' | 'sonstige'

/**
 * Welche Ertragsart der Ebene 1 eine Aufschlüsselung (Ebene 2) hat. Nur diese drei bekommen
 * ein `wa-details`; die übrigen Ertragsarten haben im Vorbericht keine passende Tabelle.
 */
export const AUFSCHLUESSELUNG_FUER_ERTRAGSART: ReadonlyMap<string, Aufschluesselung> = new Map([
  ['steuern', 'steuern'],
  ['zuwendungen', 'zuwendungen'],
  ['sonstige_ordentliche_ertraege', 'sonstige'],
])

/** Konzessionsabgaben nach Sparte (Vorbericht 2.1.7, nur Haushaltsjahr): meta-Schlüssel und Name. */
const KONZESSIONSSPARTEN: readonly (readonly [string, string])[] = [
  ['konzessionsabgabe_strom', 'Konzessionsabgabe Strom'],
  ['konzessionsabgabe_gas', 'Konzessionsabgabe Gas'],
  ['konzessionsabgabe_wasser', 'Konzessionsabgabe Wasser'],
]

/** Finanzplan-Zeilen neben den Pauschalen: Zeilenschlüssel und Balkenname (UI-SPEC). */
const FINANZPLAN_BALKEN: readonly (readonly [string, string])[] = [
  ['veraeusserung_sachanlagen', 'Grundstücksverkäufe'],
  ['beitraege', 'Beiträge'],
  ['kreditaufnahme', 'Kredite'],
]

/** Finanzplan-Zeilen der Tabelle „Investive Einnahmen“, in der Reihenfolge des Gesamtfinanzplans. */
const FINANZPLAN_TABELLE: readonly string[] = [
  'investitionszuwendungen',
  'veraeusserung_sachanlagen',
  'beitraege',
  'kreditaufnahme',
]

const SONSTIGE_BERECHNET = 'sonstige_berechnet'
const SONSTIGE_BERECHNET_NAME = 'Sonstige (berechnet)'

function vorberichtTabelle(name: string): VorberichtTabelle {
  const tabelle = haushalt.vorbericht[name]
  if (tabelle === undefined) {
    throw new Error(`Vorberichtstabelle „${name}“ fehlt in haushalt.json`)
  }
  return tabelle
}

function wertAn(posten: VorberichtPosten, jahrIndex: number): number | null {
  return posten.werte[jahrIndex] ?? null
}

function postenZeile(posten: VorberichtPosten, jahrIndex: number): PostenZeile {
  return {
    posten: posten.posten,
    name: posten.name,
    wert: wertAn(posten, jahrIndex),
    gerundet: posten.gerundet,
    berechnet: posten.berechnet,
    quelle: posten.quelle,
    keinGeldfluss: SONDERPOSTEN_POSTEN.includes(posten.posten),
  }
}

/** Ein hergeleiteter Rest ohne Wert ist kein fehlender Wert, sondern gar keine Zeile. */
function istAnzeigbar(zeile: PostenZeile): boolean {
  return !(zeile.berechnet && zeile.wert === null)
}

function hebesatzFuer(posten: string): { wert: number | null; quelle: number | null } {
  if (!Object.hasOwn(haushalt.meta.hebesaetze, posten)) {
    return { wert: null, quelle: null }
  }
  const meta = haushalt.meta.hebesaetze[posten]
  if (meta === undefined || typeof meta.wert !== 'number') {
    throw new Error(`Hebesatz „${posten}“ in haushalt.meta ist keine Zahl`)
  }
  return { wert: meta.wert, quelle: meta.quelle }
}

/** Steuerarten des Jahres (EINN-02) mit Markierung „selbst festgelegt“ und Hebesatz. */
export function baueSteuern(jahrIndex: number): SteuerZeile[] {
  return vorberichtTabelle('steuerarten')
    .posten.map((posten) => {
      const hebesatz = hebesatzFuer(posten.posten)
      return {
        ...postenZeile(posten, jahrIndex),
        selbstFestgelegt: SELBST_FESTGELEGTE_STEUERN.includes(posten.posten),
        hebesatz: hebesatz.wert,
        hebesatzQuelle: hebesatz.quelle,
      }
    })
    .filter(istAnzeigbar)
}

/** Zuwendungen des Jahres (EINN-03) mit dem Etikett „kein Geldfluss“ für Sonderposten. */
export function baueZuwendungen(jahrIndex: number): PostenZeile[] {
  return vorberichtTabelle('zuwendungen')
    .posten.map((posten) => postenZeile(posten, jahrIndex))
    .filter(istAnzeigbar)
}

function konzessionsabgabeNachSparte(): SonstigeErtragZeile[] {
  return KONZESSIONSSPARTEN.map(([schluessel, name]) => {
    const meta = haushalt.meta.vorbericht_werte[schluessel]
    if (meta === undefined || typeof meta.wert !== 'number') {
      throw new Error(`Konzessionsabgabe „${schluessel}“ fehlt in haushalt.meta.vorbericht_werte`)
    }
    return {
      posten: schluessel,
      name,
      wert: meta.wert,
      gerundet: meta.gerundet === true,
      berechnet: false,
      quelle: meta.quelle,
      keinGeldfluss: false,
      teilVon: 'konzessionsabgaben',
    }
  })
}

/**
 * Sonstige ordentliche Erträge des Jahres (EINN-04, Vorbericht 2.1.7). Für das Haushaltsjahr
 * stehen die Konzessionsabgaben zusätzlich nach Sparte (Strom, Gas, Wasser) direkt hinter dem
 * Posten; andere Jahre nennt das PDF nicht.
 */
export function baueSonstigeErtraege(jahrIndex: number): SonstigeErtragZeile[] {
  const istHaushaltsjahr = haushalt.jahre.indexOf(haushalt.haushaltsjahr) === jahrIndex
  const zeilen: SonstigeErtragZeile[] = []
  for (const posten of vorberichtTabelle('sonstige_ertraege').posten) {
    const zeile = { ...postenZeile(posten, jahrIndex), teilVon: null }
    if (!istAnzeigbar(zeile)) {
      continue
    }
    zeilen.push(zeile)
    if (istHaushaltsjahr && posten.posten === 'konzessionsabgaben') {
      zeilen.push(...konzessionsabgabeNachSparte())
    }
  }
  return zeilen
}

/** Seite des Gesamtfinanzplans, auf dem die Finanzplan-Zeilen stehen. */
function finanzplanSeite(): number {
  return investitionen.finanzierung.quelle
}

function finanzplanWert(schluessel: string, jahrIndex: number): number {
  const wert = haushalt.finanzplan['GESAMT']?.zeilen[schluessel]?.[jahrIndex]
  if (wert === undefined) {
    throw new Error(`Gesamtfinanzplan: Zeile „${schluessel}“ fehlt für Jahresindex ${jahrIndex}`)
  }
  return wert
}

function investiveFinanzplanZeile(
  schluessel: string,
  name: string,
  jahrIndex: number,
): InvestiveZeile {
  return {
    schluessel,
    name,
    wert: finanzplanWert(schluessel, jahrIndex),
    gerundet: false,
    berechnet: false,
    quelle: finanzplanSeite(),
    gruppe: 'finanzplan',
  }
}

function pauschaleZeile(posten: VorberichtPosten, jahrIndex: number): InvestiveZeile {
  return {
    schluessel: posten.posten,
    name: posten.name,
    wert: wertAn(posten, jahrIndex),
    gerundet: posten.gerundet,
    berechnet: false,
    quelle: posten.quelle,
    gruppe: 'pauschale',
  }
}

/**
 * Investive Einnahmen des Jahres (EINN-06, D-03) in der Reihenfolge des UI-SPEC: die drei
 * Pauschalen, „Sonstige (berechnet)“ (= Zeile 18 des Gesamtfinanzplans minus die gezeigten
 * Pauschalen), dann Grundstücksverkäufe, Beiträge und Kredite aus dem Gesamtfinanzplan. Das PDF
 * druckt die Pauschalen nur für das Haushaltsjahr; in anderen Jahren sind sie `null` und
 * „Sonstige (berechnet)“ trägt die ganze Zeile 18.
 */
export function baueInvestiveEinnahmen(jahrIndex: number): InvestiveZeile[] {
  const tabelle = vorberichtTabelle('investitionszuwendungen')
  const pauschalen = GEZEIGTE_PAUSCHALEN.map((schluessel) => {
    const posten = tabelle.posten.find((p) => p.posten === schluessel)
    if (posten === undefined) {
      throw new Error(`Pauschale „${schluessel}“ fehlt in vorbericht.investitionszuwendungen`)
    }
    return pauschaleZeile(posten, jahrIndex)
  })

  const gezeigt = pauschalen.filter((zeile) => zeile.wert !== null)
  const summeGezeigt = gezeigt.reduce((summe, zeile) => summe + (zeile.wert ?? 0), 0)
  const sonstige: InvestiveZeile = {
    schluessel: SONSTIGE_BERECHNET,
    name: SONSTIGE_BERECHNET_NAME,
    wert: finanzplanWert('investitionszuwendungen', jahrIndex) - summeGezeigt,
    gerundet: gezeigt.some((zeile) => zeile.gerundet),
    berechnet: true,
    quelle: finanzplanSeite(),
    gruppe: 'sonstige',
  }

  return [
    ...pauschalen,
    sonstige,
    ...FINANZPLAN_BALKEN.map(([schluessel, name]) =>
      investiveFinanzplanZeile(schluessel, name, jahrIndex),
    ),
  ]
}

/**
 * Zeilen der Tabelle unter dem Diagramm: alle gedruckten Pauschalen und Förderungen des Jahres
 * (Vorbericht S. 52), dann die Finanzplan-Zeilen mit ihrem gedruckten Namen.
 */
export function baueInvestiveTabelle(jahrIndex: number): InvestiveZeile[] {
  const gedruckt = vorberichtTabelle('investitionszuwendungen')
    .posten.map((posten) => pauschaleZeile(posten, jahrIndex))
    .filter((zeile) => zeile.wert !== null)
  const finanzplan = FINANZPLAN_TABELLE.map((schluessel) =>
    investiveFinanzplanZeile(schluessel, zeilenName('finanzplan', schluessel), jahrIndex),
  )
  return [...gedruckt, ...finanzplan]
}

/** `true`, wenn mindestens eine Zeile einen Wert ungleich 0 hat; sonst gilt der Leerzustand. */
export function hatInvestiveWerte(zeilen: readonly InvestiveZeile[]): boolean {
  return zeilen.some((zeile) => zeile.wert !== null && zeile.wert !== 0)
}
