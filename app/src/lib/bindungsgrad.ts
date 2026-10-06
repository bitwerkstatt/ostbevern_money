// Zuschussbedarf des Haushaltsjahrs nach Bindungsgrad (RAT-01, D-01). Jeder Wert wird aus
// `ergebnisplan[code].berechnet.zuschussbedarf` gelesen und nie aus Aufwand und Erträgen neu
// gerechnet (Phase 5 D-05). Der Balken summiert nur Produkte mit Zuschussbedarf > 0; Produkte mit
// negativem Zuschussbedarf (Überschuss) stehen in einer eigenen Liste. Das Finanzierungsprodukt
// ist der einzige benannte Ausschluss und fehlt in beiden.

import { haushalt, produkte } from '@/data/daten'
import { bindungsgradText } from '@/lib/produkt'
import { ZEITREIHEN_PRODUKT } from '@/lib/zeitreihen'

/** Die Bindungsgrade in fester Reihenfolge, links nach rechts im Balken. */
export const BINDUNGSGRADE = ['pflichtig', 'teils', 'freiwillig'] as const

export type Bindungsgrad = (typeof BINDUNGSGRADE)[number]

/** Kurzer Anzeigename für Beschriftung, Legende und Aufklapper (UI-SPEC Copywriting). */
const BEZEICHNUNGEN: Readonly<Record<Bindungsgrad, string>> = {
  pflichtig: 'Pflichtig',
  teils: 'Teils pflichtig',
  freiwillig: 'Freiwillig',
}

/**
 * Das Finanzierungsprodukt: dort liegen Steuern und Schlüsselzuweisung, es bringt mehr ein, als
 * es kostet, und würde den Segmentwert „pflichtig“ ins Negative ziehen (D-01). Es steht weder im
 * Balken noch in der Überschuss-Liste. Dasselbe Produkt führt die Zeitreihen der Steuerarten,
 * deshalb gibt es hier kein zweites Codeliteral.
 */
export const FINANZIERUNGSPRODUKT = ZEITREIHEN_PRODUKT

/** Ein Produkt mit seinem Zuschussbedarf im Haushaltsjahr. */
export interface BindungsProdukt {
  code: string
  name: string
  /** Code des Aufgabenbereichs, für die Balkenfarbe. */
  pb: string
  /** Zuschussbedarf in Euro, wie in `berechnet.zuschussbedarf` (negativ beim Überschuss). */
  wert: number
}

export interface BindungsSegment {
  bindungsgrad: Bindungsgrad
  /** Ausgeschriebener Name aus `bindungsgradText`, wie auf der Produktseite. */
  name: string
  /** Kurzer Anzeigename: „Pflichtig“, „Teils pflichtig“, „Freiwillig“. */
  bezeichnung: string
  summe: number
  anzahl: number
  /** Anteil an der Summe aller Segmente (0–1). */
  anteil: number
  /** Absteigend nach Zuschussbedarf. */
  produkte: BindungsProdukt[]
}

export interface BindungsgradModell {
  /** Nur Bindungsgrade mit mindestens einem Produkt, in der Reihenfolge von `BINDUNGSGRADE`. */
  segmente: BindungsSegment[]
  /** Produkte mit negativem Zuschussbedarf, der größte Überschuss zuerst. */
  ueberschuss: BindungsProdukt[]
  /** Summe aller Segmente in Euro. */
  summe: number
}

function istBindungsgrad(wert: string): wert is Bindungsgrad {
  return (BINDUNGSGRADE as readonly string[]).includes(wert)
}

function jahrIndex(): number {
  const index = haushalt.jahre.indexOf(haushalt.haushaltsjahr)
  if (index < 0) {
    throw new Error(`Haushaltsjahr ${String(haushalt.haushaltsjahr)} steht nicht in haushalt.jahre`)
  }
  return index
}

/** Segmente, Produktlisten und Überschuss des Haushaltsjahrs (D-01). */
export function baueBindungsgrad(): BindungsgradModell {
  const index = jahrIndex()
  const jeBindungsgrad = new Map<Bindungsgrad, BindungsProdukt[]>(
    BINDUNGSGRADE.map((b) => [b, []] as const),
  )
  const ueberschuss: BindungsProdukt[] = []

  for (const produkt of produkte) {
    if (produkt.code === FINANZIERUNGSPRODUKT) {
      continue
    }
    const wert = haushalt.ergebnisplan[produkt.code]?.berechnet.zuschussbedarf[index]
    if (wert === undefined) {
      throw new Error(`Produkt ${produkt.code}: kein Zuschussbedarf in haushalt.json`)
    }
    const eintrag: BindungsProdukt = {
      code: produkt.code,
      name: produkt.name,
      pb: produkt.pb,
      wert,
    }
    if (wert < 0) {
      ueberschuss.push(eintrag)
    } else if (wert > 0) {
      if (!istBindungsgrad(produkt.bindungsgrad)) {
        throw new Error(
          `Produkt ${produkt.code}: unbekannter Bindungsgrad „${produkt.bindungsgrad}“`,
        )
      }
      jeBindungsgrad.get(produkt.bindungsgrad)?.push(eintrag)
    }
  }

  const gefuellt = BINDUNGSGRADE.flatMap((bindungsgrad) => {
    const liste = [...(jeBindungsgrad.get(bindungsgrad) ?? [])].sort((a, b) => b.wert - a.wert)
    return liste.length === 0 ? [] : [{ bindungsgrad, liste }]
  })
  const summe = gefuellt.reduce(
    (gesamt, { liste }) => gesamt + liste.reduce((s, p) => s + p.wert, 0),
    0,
  )
  const segmente = gefuellt.map(({ bindungsgrad, liste }): BindungsSegment => {
    const segmentSumme = liste.reduce((s, p) => s + p.wert, 0)
    return {
      bindungsgrad,
      name: bindungsgradText(bindungsgrad),
      bezeichnung: BEZEICHNUNGEN[bindungsgrad],
      summe: segmentSumme,
      anzahl: liste.length,
      anteil: segmentSumme / summe,
      produkte: liste,
    }
  })

  return { segmente, ueberschuss: ueberschuss.sort((a, b) => a.wert - b.wert), summe }
}
