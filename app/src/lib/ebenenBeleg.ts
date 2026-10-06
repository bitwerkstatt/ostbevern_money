// Belegschlüssel der Drilldown-Tabelle auf /ausgaben (Phase 7, D-01, T-07-18). Schlüssel entstehen
// nur über `belegSchluessel`; ein berechneter Wert nennt seine Herleitung (D-03).
//
//   Knoten außerhalb von KL   ep:{code}:ordentliche_aufwendungen (Z. 17 im Teilergebnisplan)
//   KL-Unterposten            vb:transferaufwendungen:{posten} (Vorbericht, T€)
//   KL selbst                 seite:{pdf_seite des Knotens}; sein Wert steht als Z. 15 im
//                             Teilergebnisplan des Produkts, dessen Seite der Knoten nennt.
//                             Die Gesamtzeile der Transferaufwendungen (vb:…:gesamt) wäre falsche
//                             Evidenz: sie umfasst alle Transferaufwendungen, nicht nur KL.

import { haushalt } from '@/data/daten'
import type { Modus } from '@/lib/ansicht'
import type { EbenenEintrag } from '@/lib/drilldown'
import { findeKlKnoten } from '@/lib/kreisumlage'
import { belegSchluessel, findeBeleg } from '@/lib/quelle'
import { zeilenName } from '@/lib/zeilen'

export interface EbenenBeleg {
  /** Belegschlüssel (`lib/quelle.ts`). */
  schluessel: string
  /** Herleitung eines berechneten Werts (D-03), sonst `null`. */
  herleitung: string | null
}

const AUFWAND_ZEILE = 'ordentliche_aufwendungen'
const ZINS_ZEILE = 'zinsaufwendungen'
const TRANSFER_TABELLE = 'transferaufwendungen'

/** Herleitung des Zuschussbedarfs (Spez. 3.6). */
const HERLEITUNG_ZUSCHUSSBEDARF = 'Aufwendungen minus Erträge'

function seitenBeleg(code: string): string | null {
  const seite = haushalt.knoten.find((k) => k.code === code)?.pdf_seite
  return seite === null || seite === undefined ? null : belegSchluessel.seite(seite)
}

function klSchluessel(code: string): string | null {
  const kl = findeKlKnoten()
  if (code === kl.code) {
    return seitenBeleg(code)
  }
  const posten = belegSchluessel.vb(TRANSFER_TABELLE, code.slice(kl.code.length + 1))
  return findeBeleg(posten) === null ? seitenBeleg(code) : posten
}

/**
 * Der Beleg einer Zeile der Drilldown-Tabelle, oder `null` ohne Beleg (die Zelle bleibt leer).
 * Der Aufwand eines Knotens ist Z. 17 plus Z. 20; weicht er von der gedruckten Z. 17 ab (nur
 * dort, wo Zinsaufwendungen anfallen), nennt der Beleg diese Summe als Herleitung. Der
 * Zuschussbedarf ist immer berechnet.
 */
export function ebenenBeleg(
  eintrag: Pick<EbenenEintrag, 'code' | 'istKl'>,
  jahrIndex: number,
  modus: Modus,
): EbenenBeleg | null {
  const schluessel = eintrag.istKl
    ? klSchluessel(eintrag.code)
    : belegSchluessel.ep(eintrag.code, AUFWAND_ZEILE)
  if (schluessel === null) {
    return null
  }
  if (modus === 'zuschussbedarf') {
    return { schluessel, herleitung: HERLEITUNG_ZUSCHUSSBEDARF }
  }
  const werte = haushalt.ergebnisplan[eintrag.code]
  const mitZinsen =
    !eintrag.istKl &&
    werte !== undefined &&
    werte.berechnet.aufwand[jahrIndex] !== werte.zeilen[AUFWAND_ZEILE]?.[jahrIndex]
  return {
    schluessel,
    herleitung: mitZinsen
      ? `${zeilenName('ergebnisplan', AUFWAND_ZEILE)} plus ${zeilenName('ergebnisplan', ZINS_ZEILE)}`
      : null,
  }
}
