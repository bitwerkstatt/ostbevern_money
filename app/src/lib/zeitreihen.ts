// Zeitreihe je Steuerart (EINN-05, D-01). Jahre vor dem ersten Planjahr stammen als Ist aus den
// Grundzahlen des Produkts 160101, alle Planjahre aus dem Vorbericht. Die Grundzahlen für 2024 und
// 2025 weichen vom Vorbericht ab (Gewerbesteuer 2024: 8.418.043 € gegen 9.511.000 €) und werden
// deshalb für Steuerreihen nie verwendet. Die Wertart je Planjahr kommt aus `haushalt.wertarten`.

import { formatiere, jahr as formatiereJahr } from '@/charts/format'
import { haushalt, produkte } from '@/data/daten'
import type { Grundzahl, Produkt } from '@/data/typen'
import { WERTART_NAMEN } from '@/lib/jahr'
import { belegSchluessel } from '@/lib/quelle'

/** Eine Auswahlmöglichkeit der Zeitreihe und ihre Herkunft in beiden Quellen. */
export interface ZeitreihenPosten {
  /** Posten-Schlüssel in der Vorberichtstabelle, z. B. „gewerbesteuer“. */
  posten: string
  /** Vorberichtstabelle, in der der Posten steht. */
  tabelle: 'steuerarten' | 'zuwendungen'
  /** Anfang der Grundzahl-Bezeichnung im Produkt 160101, inklusive der öffnenden Klammer. */
  grundzahlPraefix: string
}

export interface Zeitpunkt {
  jahr: number
  /** Euro; `null`, wenn die Quelle für das Jahr keinen Wert nennt. */
  wert: number | null
  /** `ergebnis`, `ansatz` oder `planung`. */
  wertart: string
  quelle: 'grundzahlen' | 'vorbericht'
  /** 1-basierte PDF-Seite der Quelle. */
  pdfSeite: number | null
  /** Belegschlüssel des Punkts (`gz:…` bzw. `vb:…`), `null` ohne PDF-Seite. */
  beleg: string | null
  /** `true` für Vorbericht-Werte, die in T€ geführt und × 1000 genommen wurden (Anzeige „rd.“). */
  gerundet: boolean
}

export interface ZeitreihenSerie {
  wertart: string
  /** Je Jahr der Zeitreihe; `null` außerhalb der Serie und für fehlende Werte. */
  werte: (number | null)[]
  /** `true` am Punkt, den die Serie von der vorigen übernimmt (wird dort nicht erneut gezeichnet). */
  geteilt: boolean[]
}

export interface Zeitreihe {
  jahre: number[]
  serien: ZeitreihenSerie[]
}

/** Das Produkt, dessen Grundzahlen die Steuerarten und die Schlüsselzuweisung führen (Teilplan 16 01 01). */
export const ZEITREIHEN_PRODUKT = '160101'

/** Vorauswahl der Zeitreihe. */
export const STANDARD_ZEITREIHE = 'gewerbesteuer'

/**
 * Die einzige Zuordnungstabelle Vorbericht-Posten zu Grundzahl (RESEARCH Pitfall 8). Das Präfix
 * enthält die öffnende Klammer, weil „Gewerbesteuer“ sonst auch „Gewerbesteuerumlage (Zeile 15)“
 * träfe. Schlägt eine Zuordnung fehl, wirft `findeGrundzahl` mit dem Postennamen.
 */
export const ZEITREIHEN_POSTEN: readonly ZeitreihenPosten[] = [
  { posten: 'gewerbesteuer', tabelle: 'steuerarten', grundzahlPraefix: 'Gewerbesteuer (' },
  { posten: 'grundsteuer_a', tabelle: 'steuerarten', grundzahlPraefix: 'Grundsteuer A (' },
  { posten: 'grundsteuer_b', tabelle: 'steuerarten', grundzahlPraefix: 'Grundsteuer B (' },
  {
    posten: 'anteil_einkommensteuer',
    tabelle: 'steuerarten',
    grundzahlPraefix: 'Anteil an der Einkommenssteuer (',
  },
  {
    posten: 'anteil_umsatzsteuer',
    tabelle: 'steuerarten',
    grundzahlPraefix: 'Anteil an der Umsatzsteuer (',
  },
  { posten: 'vergnuegungssteuer', tabelle: 'steuerarten', grundzahlPraefix: 'Vergnügungssteuer (' },
  { posten: 'hundesteuer', tabelle: 'steuerarten', grundzahlPraefix: 'Hundesteuer (' },
  {
    posten: 'kompensationszahlungen',
    tabelle: 'steuerarten',
    grundzahlPraefix: 'Kompensationsleistung (',
  },
  {
    posten: 'schluesselzuweisung',
    tabelle: 'zuwendungen',
    grundzahlPraefix: 'Schlüsselzuweisung (',
  },
]

function zeitreihenPosten(posten: string): ZeitreihenPosten {
  const eintrag = ZEITREIHEN_POSTEN.find((e) => e.posten === posten)
  if (eintrag === undefined) {
    throw new Error(`Unbekannter Zeitreihen-Posten: ${posten}`)
  }
  return eintrag
}

function vorberichtPosten(eintrag: ZeitreihenPosten) {
  const posten = haushalt.vorbericht[eintrag.tabelle]?.posten.find(
    (p) => p.posten === eintrag.posten,
  )
  if (posten === undefined) {
    throw new Error(
      `Zeitreihen-Posten ${eintrag.posten}: nicht in vorbericht.${eintrag.tabelle} enthalten`,
    )
  }
  return posten
}

/** Die eine Grundzahl in Euro, die zum Posten gehört; sonst Fehler mit Postennamen. */
export function findeGrundzahl(
  eintrag: ZeitreihenPosten,
  produktliste: readonly Produkt[] = produkte,
): Grundzahl {
  const treffer = produktliste
    .filter((produkt) => produkt.code === ZEITREIHEN_PRODUKT)
    .flatMap((produkt) => produkt.grundzahlen)
    .filter(
      (grundzahl) =>
        grundzahl.einheit === 'EUR' && grundzahl.bezeichnung.startsWith(eintrag.grundzahlPraefix),
    )
  const [erster] = treffer
  if (treffer.length !== 1 || erster === undefined) {
    throw new Error(
      `Zeitreihen-Posten ${eintrag.posten}: ${String(treffer.length)} Grundzahlen im Produkt ${ZEITREIHEN_PRODUKT} beginnen mit „${eintrag.grundzahlPraefix}“ (erwartet: genau eine)`,
    )
  }
  return erster
}

/**
 * Alle Punkte eines Postens: Jahr für Jahr vom ersten Grundzahl-Jahr vor dem ersten Planjahr bis
 * zum letzten Planjahr. Jahre davor sind Ist aus den Grundzahlen, Planjahre kommen aus dem
 * Vorbericht (D-01).
 */
export function baueZeitreihe(posten: string): Zeitpunkt[] {
  const eintrag = zeitreihenPosten(posten)
  const vorbericht = vorberichtPosten(eintrag)
  const grundzahl = findeGrundzahl(eintrag)
  const ersteresPlanjahr = haushalt.jahre[0]
  if (ersteresPlanjahr === undefined) {
    throw new Error('haushalt.jahre ist leer')
  }

  const punkte: Zeitpunkt[] = []
  const grundzahlJahre = grundzahl.werte.map((w) => w.jahr).filter((j) => j < ersteresPlanjahr)
  if (grundzahlJahre.length > 0) {
    for (let jahr = Math.min(...grundzahlJahre); jahr < ersteresPlanjahr; jahr++) {
      punkte.push({
        jahr,
        wert: grundzahl.werte.find((w) => w.jahr === jahr)?.wert ?? null,
        wertart: 'ergebnis',
        quelle: 'grundzahlen',
        pdfSeite: grundzahl.pdf_seite,
        beleg: belegSchluessel.gz(ZEITREIHEN_PRODUKT, grundzahl.position),
        gerundet: false,
      })
    }
  }

  haushalt.jahre.forEach((jahr, index) => {
    const wertart = haushalt.wertarten[index]
    if (wertart === undefined) {
      throw new Error(`haushalt.wertarten hat keinen Eintrag für ${String(jahr)}`)
    }
    punkte.push({
      jahr,
      wert: vorbericht.werte[index] ?? null,
      wertart,
      quelle: 'vorbericht',
      pdfSeite: vorbericht.quelle,
      beleg:
        vorbericht.quelle === null ? null : belegSchluessel.vb(eintrag.tabelle, eintrag.posten),
      gerundet: vorbericht.gerundet,
    })
  })
  return punkte
}

/**
 * Teilt die Punkte in eine Serie je Wertart (Ist, Ansatz, Planung). Der letzte Punkt einer Wertart
 * gehört zusätzlich zur Serie der nächsten, damit die Linie ohne Sprung weiterläuft; dort ist
 * `geteilt` gesetzt, damit die spätere Serie den Punkt nicht noch einmal zeichnet.
 */
export function zeitreihenSerien(
  punkte: readonly Pick<Zeitpunkt, 'jahr' | 'wert' | 'wertart'>[],
): Zeitreihe {
  const reihenfolge = [...WERTART_NAMEN.keys()]
  const serien = reihenfolge.map((wertart): ZeitreihenSerie => {
    const werte: (number | null)[] = punkte.map(() => null)
    const geteilt: boolean[] = punkte.map(() => false)
    const ersterIndex = punkte.findIndex((p) => p.wertart === wertart)
    punkte.forEach((p, k) => {
      if (p.wertart === wertart) {
        werte[k] = p.wert
      }
    })
    const davor = ersterIndex - 1
    if (ersterIndex > 0 && punkte[davor]?.wertart !== wertart) {
      werte[davor] = punkte[davor]?.wert ?? null
      geteilt[davor] = true
    }
    return { wertart, werte, geteilt }
  })
  return { jahre: punkte.map((p) => p.jahr), serien }
}

/** Auswahlliste der Zeitreihe mit den gedruckten Postennamen aus dem Vorbericht. */
export function zeitreihenOptionen(): { posten: string; name: string }[] {
  return ZEITREIHEN_POSTEN.map((eintrag) => ({
    posten: eintrag.posten,
    name: vorberichtPosten(eintrag).name,
  }))
}

/** PDF-Seite der Vorberichtstabelle, aus der die Planjahre des Postens stammen. */
export function zeitreihenSeite(posten: string): number | null {
  return vorberichtPosten(zeitreihenPosten(posten)).quelle
}

/**
 * Quellenzeile unter der Tabelle, z. B. „Quelle: Grundzahlen (2022–2023), Vorbericht (ab 2024)“.
 * Die Jahre kommen aus den Punkten, nicht aus dem Code.
 */
export function quellenFussnote(punkte: readonly Zeitpunkt[]): string {
  const grundzahlJahre = punkte.filter((p) => p.quelle === 'grundzahlen').map((p) => p.jahr)
  const vorberichtJahre = punkte.filter((p) => p.quelle === 'vorbericht').map((p) => p.jahr)
  const teile: string[] = []
  if (grundzahlJahre.length > 0) {
    const von = Math.min(...grundzahlJahre)
    const bis = Math.max(...grundzahlJahre)
    teile.push(
      von === bis
        ? `Grundzahlen (${formatiereJahr(von)})`
        : `Grundzahlen (${formatiereJahr(von)}–${formatiereJahr(bis)})`,
    )
  }
  if (vorberichtJahre.length > 0) {
    teile.push(`Vorbericht (ab ${formatiereJahr(Math.min(...vorberichtJahre))})`)
  }
  return `Quelle: ${teile.join(', ')}`
}

/** Betrag einer Reihe für Tooltip und Tabelle: „rd. “ vor einem in T€ gerundeten Wert, „–“ ohne Wert. */
export function betragText(punkt: Pick<Zeitpunkt, 'wert' | 'gerundet'>): string {
  const text = formatiere(punkt.wert, 'euro')
  return punkt.wert !== null && punkt.gerundet ? `rd. ${text}` : text
}
