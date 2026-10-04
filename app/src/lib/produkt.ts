// Seitenmodell der Produktdetailseite `/produkt/:code` (D-09, AUSG-05). Reine Funktionen
// über den App-Daten; formatiert wird erst in der Seite und in `DatenTabelle` über
// `charts/format.ts` bzw. `wa-format-number`.

import type { RouteLocationNamedRaw } from 'vue-router'

import { jahr as formatiereJahr } from '@/charts/format'
import type { DatenSpalte, DatenZeile } from '@/components/datenTabelle'
import { haushalt, investitionen } from '@/data/daten'
import type { Grundzahl, KnotenWerte, Massnahme, Produkt } from '@/data/typen'
import { findeKnoten, findeProdukt, leseAnsicht } from '@/lib/ansicht'
import { proKopf } from '@/lib/berechnung'
import { wertartFuerJahr, wertartName } from '@/lib/jahr'

const BINDUNGSGRAD_TEXTE: ReadonlyMap<string, string> = new Map([
  ['pflichtig', 'pflichtig'],
  ['freiwillig', 'freiwillig'],
  ['teils', 'teils pflichtig, teils freiwillig'],
])

/** Ausgeschriebener Bindungsgrad; ein unbekannter Wert kommt unverändert zurück. */
export function bindungsgradText(wert: string): string {
  return BINDUNGSGRAD_TEXTE.get(wert) ?? wert
}

function normiere(text: string): string {
  return text.replaceAll(',', '').replaceAll(/\s+/g, ' ').trim().toLowerCase()
}

/** Kopfdaten der Produktseite: Namen der Ebenen darüber, Rücksprungziel und Quellseite. */
export interface ProduktKopf {
  produkt: Produkt
  /** Name des Aufgabenbereichs (PB) des Produkts. */
  pbName: string
  /** Name der Produktgruppe (PG) des Produkts. */
  pgName: string
  /** Ziel des Zurück-Links: die Ausgabenansicht, aus der das Produkt geöffnet wurde (ohne `jahr`). */
  zurueck: RouteLocationNamedRaw
  /** Name der Ebene, zu der der Zurück-Link führt (Produktgruppe, sonst Aufgabenbereich). */
  zurueckText: string
  /** Erste PDF-Seite des Produkts (1-basiert) für die Quellzeile. */
  quelleSeite: number | null
  /** Ausgeschriebener Bindungsgrad. */
  bindungsgrad: string
  /** Wortlaut des Plans, wenn er sich vom ausgeschriebenen Bindungsgrad unterscheidet. */
  bindungsgradOriginal: string | null
}

/**
 * Baut den Kopf eines Produkts (D-09); `null` für jeden unbekannten Code, auch für
 * Prototyp-Schlüssel (Nachschlagen nur über die Map in `findeProdukt`).
 *
 * `query` ist der gemerkte Zustand der Ausgabenansicht (`modus`, `pb`, `pg`). Er wird mit
 * `leseAnsicht` neu validiert und nur übernommen, wenn er zum Produkt passt (gleicher
 * Aufgabenbereich, gleiche oder keine Produktgruppe); sonst führt der Zurück-Link zu
 * Aufgabenbereich und Produktgruppe des Produkts. Das Jahr hängt die Seite über `jahrLink` an.
 */
export function baueProduktKopf(
  code: unknown,
  query: Readonly<Record<string, unknown>> = {},
): ProduktKopf | null {
  const produkt = findeProdukt(code)
  if (produkt === undefined) {
    return null
  }
  const pbName = findeKnoten(produkt.pb)?.name ?? produkt.pb
  const pgName = findeKnoten(produkt.pg)?.name ?? produkt.pg

  const gemerkt = leseAnsicht(query)
  const passt = gemerkt.pb === produkt.pb && (gemerkt.pg === null || gemerkt.pg === produkt.pg)
  const pb = passt ? gemerkt.pb : produkt.pb
  const pg = passt ? gemerkt.pg : produkt.pg

  const rueckQuery: Record<string, string> = {}
  if (gemerkt.modus !== 'aufwand') {
    rueckQuery.modus = gemerkt.modus
  }
  if (pb !== null) {
    rueckQuery.pb = pb
  }
  if (pg !== null) {
    rueckQuery.pg = pg
  }

  const bindungsgrad = bindungsgradText(produkt.bindungsgrad)
  const abweichend = normiere(produkt.bindungsgrad_original) !== normiere(bindungsgrad)

  return {
    produkt,
    pbName,
    pgName,
    zurueck: { name: 'ausgaben', query: rueckQuery },
    zurueckText: pg === null ? pbName : pgName,
    quelleSeite: produkt.pdf_seiten[0] ?? null,
    bindungsgrad,
    bindungsgradOriginal: abweichend ? produkt.bindungsgrad_original : null,
  }
}

// ---------------------------------------------------------------------------------------
// Tabellen
// ---------------------------------------------------------------------------------------

/** Spalten und Zeilen für `DatenTabelle`. */
export interface Tabelle {
  spalten: DatenSpalte[]
  zeilen: DatenZeile[]
}

/** Teilergebnisplan eines Produkts. */
export interface Teilergebnisplan extends Tabelle {
  /** Abschnittsüberschrift, z. B. „Teilergebnisplan 2024–2029“. */
  titel: string
}

/** Grundzahlen eines Produkts mit Hinweisen als Fußnote. */
export interface GrundzahlenTabelle extends Tabelle {
  fussnote: string | null
}

type ZeilenWerte = Record<string, string | number | null>

/** Schlüssel der Jahresspalte in den Tabellenzeilen. */
export function jahrSchluessel(jahr: number): string {
  return `j${jahr}`
}

/** Wert, der in `etikett` einer Tabellenzeile steht, wenn die Zeile berechnet ist. */
const BERECHNET = 'berechnet'

// Nachschlagetabellen als Map: URL-Codes und Zeilennummern erreichen nie ein einfaches
// Objekt als Schlüssel (Prototyp-Schlüssel wie `__proto__`, T-05-29).
const ERGEBNISPLAN: ReadonlyMap<string, KnotenWerte> = new Map(
  Object.entries(haushalt.ergebnisplan),
)
const ZEILEN_JE_NUMMER: ReadonlyMap<string, string> = new Map(
  haushalt.zeilen_namen.ergebnisplan.map((zeile) => [zeile.nummer, zeile.name] as const),
)
const MASSNAHMEN_JE_PRODUKT: ReadonlyMap<string, Massnahme[]> = (() => {
  const karte = new Map<string, Massnahme[]>()
  for (const massnahme of investitionen.massnahmen) {
    const liste = karte.get(massnahme.produkt) ?? []
    liste.push(massnahme)
    karte.set(massnahme.produkt, liste)
  }
  return karte
})()

/** Die Summenzeilen, die der Teilergebnisplan immer zeigt (Erträge, Aufwendungen, Ergebnis). */
const IMMER_ZEIGEN: ReadonlySet<string> = new Set([
  'ordentliche_ertraege',
  'ordentliche_aufwendungen',
  'jahresergebnis',
])

function einwohnerzahl(): number {
  const wert = haushalt.meta.einwohner.wert
  if (typeof wert !== 'number') {
    throw new TypeError('meta.einwohner.wert muss eine Zahl sein')
  }
  return wert
}

function jahrSpalte(jahr: number, wertart: string, art: DatenSpalte['art']): DatenSpalte {
  return {
    schluessel: jahrSchluessel(jahr),
    titel: `${wertartName(wertart)} ${formatiereJahr(jahr)}`,
    art,
  }
}

function produktMitErgebnisplan(code: unknown): { produkt: Produkt; werte: KnotenWerte } | null {
  const produkt = findeProdukt(code)
  const werte = produkt === undefined ? undefined : ERGEBNISPLAN.get(produkt.code)
  return produkt === undefined || werte === undefined ? null : { produkt, werte }
}

/**
 * Teilergebnisplan eines Produkts (AUSG-05): jede Zeile, die in irgendeinem Jahr einen Wert
 * hat, dazu die Summen Erträge, Aufwendungen und Ergebnis, benannt über
 * `haushalt.zeilen_namen`. Danach die gekennzeichneten berechneten Zeilen „Zuschussbedarf“
 * und „Zuschussbedarf je Einwohner“ (D-23, DATA-03). `null` für einen unbekannten Code.
 */
export function baueTeilergebnisplan(code: unknown): Teilergebnisplan | null {
  const treffer = produktMitErgebnisplan(code)
  if (treffer === null) {
    return null
  }
  const { werte } = treffer
  const jahre = haushalt.jahre

  const spalten: DatenSpalte[] = [
    { schluessel: 'name', titel: 'Zeile', art: 'text' },
    ...jahre.map((j) => jahrSpalte(j, wertartFuerJahr(j), 'euro')),
  ]

  const zeile = (
    schluessel: string,
    name: string,
    etikett: string | null,
    reihe: readonly (number | null)[],
  ): DatenZeile => {
    const eintrag: ZeilenWerte = { schluessel, name, etikett }
    jahre.forEach((j, index) => {
      eintrag[jahrSchluessel(j)] = reihe[index] ?? null
    })
    return eintrag
  }

  const zeilen: DatenZeile[] = []
  for (const gedruckt of haushalt.zeilen_namen.ergebnisplan) {
    const reihe = werte.zeilen[gedruckt.schluessel]
    if (reihe === undefined) {
      continue
    }
    if (reihe.some((wert) => wert !== 0) || IMMER_ZEIGEN.has(gedruckt.schluessel)) {
      zeilen.push(zeile(gedruckt.schluessel, gedruckt.name, null, reihe))
    }
  }

  const einwohner = einwohnerzahl()
  const zuschussbedarf = werte.berechnet.zuschussbedarf
  zeilen.push(
    zeile('zuschussbedarf', 'Zuschussbedarf (berechnet)', BERECHNET, zuschussbedarf),
    zeile(
      'zuschussbedarf_je_einwohner',
      'Zuschussbedarf je Einwohner (berechnet)',
      BERECHNET,
      zuschussbedarf.map((betrag) => proKopf(betrag, einwohner)),
    ),
  )

  const erstes = jahre[0]
  const letztes = jahre.at(-1)
  const titel =
    erstes === undefined || letztes === undefined
      ? 'Teilergebnisplan'
      : `Teilergebnisplan ${formatiereJahr(erstes)}–${formatiereJahr(letztes)}`
  return { titel, spalten, zeilen }
}

/** Ein Erläuterungsposten, aufgelöst für die Anzeige. */
export interface ErlaeuterungEintrag {
  /** Betrag in Euro, `null` für eine Freitextzeile. */
  betrag: number | null
  text: string
  /** Gedruckte Namen der Zeilen, auf die sich der Posten bezieht. */
  zeilenNamen: string[]
  /** `true`, wenn die Seite „zu: …“ zeigen soll (nicht leer und anders als beim Posten davor). */
  zuAnzeigen: boolean
}

/**
 * Erläuterungen eines Produkts (AUSG-05): Betrag, Text und die Namen der Zeilen, auf die sich
 * der Posten bezieht (zweistellige Nummern über `haushalt.zeilen_namen`). Ohne Erläuterungen
 * oder bei unbekanntem Code leer.
 */
export function baueErlaeuterungen(code: unknown): ErlaeuterungEintrag[] {
  const produkt = findeProdukt(code)
  if (produkt === undefined) {
    return []
  }
  const eintraege: ErlaeuterungEintrag[] = []
  let davor: string | null = null
  for (const erlaeuterung of produkt.erlaeuterungen) {
    const zeilenNamen = (erlaeuterung.zu_zeilen ?? []).map(
      (nummer) => ZEILEN_JE_NUMMER.get(nummer) ?? `Zeile ${nummer}`,
    )
    const schluessel = zeilenNamen.join('|')
    eintraege.push({
      betrag: erlaeuterung.betrag,
      text: erlaeuterung.text,
      zeilenNamen,
      zuAnzeigen: zeilenNamen.length > 0 && schluessel !== davor,
    })
    davor = schluessel
  }
  return eintraege
}

/**
 * Bezugsgröße, auf die sich „Zuschussbedarf je …“ eines Produkts bezieht. `bezeichnungen`
 * sind die gedruckten Namen der Grundzahlen, deren Jahreswerte summiert den Nenner bilden.
 */
export interface Bezugsgroesse {
  produkt: string
  bezeichnungen: readonly string[]
  /** Einheit im Zeilennamen: „Zuschussbedarf je {einheitText} (berechnet)“. */
  einheitText: string
}

/**
 * Die Produkte mit „Zuschussbedarf je Einheit“ (RESEARCH Open Question 6). Freigegeben in
 * Plan 05-03 („Entscheidungen aus der Abnahme“, Antwort „Vorschlag übernehmen“): Grundschulen
 * je Schüler/in, Musikschule je Musikschüler/in, Kindertagesstätten je betreutem Kind (Summe
 * aus „unter 3 Jahre“ und „3 - 6 Jahre“). Für jedes andere Produkt gibt es nur „je Einwohner“.
 * Eine falsche Bezugsgröße würde Bürgerinnen und Bürger in die Irre führen; deshalb nur diese
 * Liste, abgesichert durch einen Test.
 */
export const BEZUGSGROESSEN: readonly Bezugsgroesse[] = [
  { produkt: '030101', bezeichnungen: ['Schüler/innen'], einheitText: 'Schüler/in' },
  { produkt: '030102', bezeichnungen: ['Schüler/innen'], einheitText: 'Schüler/in' },
  { produkt: '040301', bezeichnungen: ['Musikschüler/innen'], einheitText: 'Musikschüler/in' },
  {
    produkt: '060101',
    bezeichnungen: ['Betreute Kinder unter 3 Jahre', 'Betreute Kinder von 3 - 6 Jahre'],
    einheitText: 'betreutem Kind',
  },
]

/** Hinweise ohne Dopplungen; ein Hinweis, der in einem längeren enthalten ist, entfällt. */
function fasseHinweiseZusammen(grundzahlen: readonly Grundzahl[]): string | null {
  const alle = new Set<string>()
  for (const grundzahl of grundzahlen) {
    for (const wert of grundzahl.werte) {
      if (wert.hinweis !== null && wert.hinweis !== '') {
        alle.add(wert.hinweis)
      }
    }
  }
  const eigene = [...alle].filter(
    (hinweis) => ![...alle].some((anderer) => anderer !== hinweis && anderer.includes(hinweis)),
  )
  return eigene.length === 0 ? null : eigene.join(' ')
}

/**
 * Grundzahlen eines Produkts: je Grundzahl eine Zeile mit Einheit und den Werten je
 * Grundzahl-Jahr, dazu die freigegebenen Zeilen „Zuschussbedarf je {Bezugsgröße}
 * (berechnet)“ und nur für Jahre, in denen es Grundzahl und Zuschussbedarf gibt. Hat eine
 * Grundzahl Nachkommastellen, zeigen alle Jahresspalten Dezimalzahlen. `null` ohne
 * Grundzahlen oder bei unbekanntem Code.
 */
export function baueGrundzahlen(code: unknown): GrundzahlenTabelle | null {
  const treffer = produktMitErgebnisplan(code)
  if (treffer === null || treffer.produkt.grundzahlen.length === 0) {
    return null
  }
  const { produkt, werte } = treffer
  const grundzahlen = produkt.grundzahlen

  const jahre = [...new Set(grundzahlen.flatMap((g) => g.werte.map((w) => w.jahr)))].sort(
    (a, b) => a - b,
  )
  const dezimal = grundzahlen.some((g) => g.nachkommastellen > 0)
  const spalten: DatenSpalte[] = [
    { schluessel: 'name', titel: 'Grundzahl', art: 'text' },
    { schluessel: 'einheit', titel: 'Einheit', art: 'text' },
    ...jahre.map((j): DatenSpalte => ({
      schluessel: jahrSchluessel(j),
      titel: formatiereJahr(j),
      art: dezimal ? 'dezimal' : 'zahl',
    })),
  ]

  const zeilen: DatenZeile[] = grundzahlen.map((grundzahl) => {
    const eintrag: ZeilenWerte = {
      schluessel: `grundzahl_${grundzahl.position}`,
      name:
        grundzahl.gruppe === null
          ? grundzahl.bezeichnung
          : `${grundzahl.gruppe}: ${grundzahl.bezeichnung}`,
      einheit: grundzahl.einheit,
      etikett: null,
    }
    for (const j of jahre) {
      eintrag[jahrSchluessel(j)] = grundzahl.werte.find((w) => w.jahr === j)?.wert ?? null
    }
    return eintrag
  })

  for (const bezug of BEZUGSGROESSEN.filter((b) => b.produkt === produkt.code)) {
    const nenner = bezug.bezeichnungen.map((bezeichnung) =>
      grundzahlen.find((g) => g.bezeichnung === bezeichnung),
    )
    const eintrag: ZeilenWerte = {
      schluessel: 'zuschussbedarf_je_einheit',
      name: `Zuschussbedarf je ${bezug.einheitText} (berechnet)`,
      einheit: 'EUR',
      etikett: BERECHNET,
    }
    for (const j of jahre) {
      const planIndex = haushalt.jahre.indexOf(j)
      const teile = nenner.map((g) => g?.werte.find((w) => w.jahr === j)?.wert)
      const zuschuss = planIndex < 0 ? undefined : werte.berechnet.zuschussbedarf[planIndex]
      const summe = teile.reduce<number | null>(
        (gesamt, teil) => (gesamt === null || teil === undefined ? null : gesamt + teil),
        0,
      )
      eintrag[jahrSchluessel(j)] =
        zuschuss === undefined || summe === null || summe === 0
          ? null
          : Math.round(zuschuss / summe)
    }
    zeilen.push(eintrag)
  }

  return { spalten, zeilen, fussnote: fasseHinweiseZusammen(grundzahlen) }
}

/** Investitionsmaßnahmen eines Produkts; leer ohne Maßnahmen oder bei unbekanntem Code. */
export function baueProduktInvestitionen(code: unknown): Massnahme[] {
  return typeof code === 'string' ? [...(MASSNAHMEN_JE_PRODUKT.get(code) ?? [])] : []
}

const RICHTUNG_TEXTE: ReadonlyMap<string, string> = new Map([
  ['einzahlung', 'Einzahlung'],
  ['auszahlung', 'Auszahlung'],
])

/** Tabelle der Investitionsmaßnahmen: Maßnahme, Konto, Richtung und ein Betrag je Jahr. */
export function baueInvestitionenTabelle(massnahmen: readonly Massnahme[]): Tabelle {
  const spalten: DatenSpalte[] = [
    { schluessel: 'name', titel: 'Maßnahme', art: 'text' },
    { schluessel: 'konto', titel: 'Konto', art: 'text' },
    { schluessel: 'richtung', titel: 'Richtung', art: 'text' },
    ...investitionen.jahre.map((j, index) =>
      jahrSpalte(j, investitionen.wertarten[index] ?? wertartFuerJahr(j), 'euro'),
    ),
  ]
  const zeilen: DatenZeile[] = massnahmen.map((massnahme) => {
    const eintrag: ZeilenWerte = {
      schluessel: `${massnahme.massnahme_id}-${massnahme.konto}`,
      name: massnahme.massnahme_name,
      konto: massnahme.konto_name,
      richtung: RICHTUNG_TEXTE.get(massnahme.richtung) ?? massnahme.richtung,
    }
    investitionen.jahre.forEach((j, index) => {
      eintrag[jahrSchluessel(j)] = massnahme.werte[index] ?? null
    })
    return eintrag
  })
  return { spalten, zeilen }
}
