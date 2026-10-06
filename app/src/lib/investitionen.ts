// Investitionsmaßnahmen der Planjahre für `/investitionen` (INV-01, D-06, D-07, D-08).
// Reine Funktionen über `investitionen.json`: Auszahlungen je Konto werden erst nach Art und
// Aufgabenbereich gefiltert und dann je Produkt und Maßnahme gebündelt. Nichts wird neu
// gerechnet außer der Summe der Kontozeilen; Einzahlungen kommen nie vor (D-08).
//
// Dokumentierte Abweichung von D-07: Der Bündelungsschlüssel ist `(produkt, massnahme_id)`
// statt `massnahme_id` allein, weil 11 Kennungen unter mehreren Produkten vorkommen (z. B.
// KLIMA1 mit verschiedenen Photovoltaikanlagen) und der Link auf `/produkt/:code` sonst
// mehrdeutig wäre (RESEARCH Pitfall 2, Entscheidung 2 des Nutzers).

import { jahr as formatiereJahr } from '@/charts/format'
import type { DatenSpalte, DatenZeile } from '@/components/datenTabelle'
import { haushalt, investitionen } from '@/data/daten'
import type { Massnahme } from '@/data/typen'
import { findeKnoten } from '@/lib/ansicht'
import { wertartName } from '@/lib/jahr'
import { jahrSchluessel, type Tabelle } from '@/lib/produkt'

/** Filterart der Maßnahmen (D-06). */
export type Art = 'bau' | 'grundstuecke' | 'ausstattung' | 'sonstige'

/** Die vier Filterarten in Anzeigereihenfolge mit ihrem Text. */
export const ARTEN: readonly { art: Art; text: string }[] = [
  { art: 'bau', text: 'Bau' },
  { art: 'grundstuecke', text: 'Grundstücke' },
  { art: 'ausstattung', text: 'Fahrzeuge und Ausstattung' },
  { art: 'sonstige', text: 'Sonstige' },
]

const ART_TEXTE: ReadonlyMap<Art, string> = new Map(ARTEN.map((a) => [a.art, a.text] as const))

/** Anzeigetext einer Filterart. */
export function artText(art: Art): string {
  return ART_TEXTE.get(art) ?? art
}

/** Einzige Zuordnung Konto-Art zu Filterart (D-06); jede nicht genannte Art ist „sonstige“. */
const ART_FILTER: ReadonlyMap<string, Art> = new Map<string, Art>([
  ['bau', 'bau'],
  ['grundstuecke', 'grundstuecke'],
  ['ausstattung', 'ausstattung'],
])

/**
 * Filterart eines Kontos: Bau, Grundstücke und Ausstattung bleiben, alles andere
 * (Finanzanlagen, Investitionszuschüsse, Immaterielles, Konten ohne Art) ist „sonstige“,
 * damit keine Auszahlung fehlt und die Summe die GFP-Zeile trifft.
 */
export function filterArt(art: string | null): Art {
  return (art === null ? undefined : ART_FILTER.get(art)) ?? 'sonstige'
}

/** Index des Haushaltsjahrs in `haushalt.jahre`; die Planjahre beginnen dort. */
function planAb(): number {
  const index = haushalt.jahre.indexOf(haushalt.haushaltsjahr)
  if (index < 0) {
    throw new Error('haushaltsjahr steht nicht in haushalt.jahre')
  }
  return index
}

/** Die Planjahre: vom Haushaltsjahr bis zum letzten Jahr der Daten. */
export function planjahre(): number[] {
  return haushalt.jahre.slice(planAb())
}

/** Eine gebündelte Investitionsmaßnahme der Planjahre. */
export interface Vorhaben {
  /** `produkt/massnahme_id`, eindeutig. */
  schluessel: string
  produkt: string
  massnahmeId: string
  name: string
  /** Aufgabenbereich (PB-Code) des Produkts. */
  pb: string
  /** Filterarten der gebündelten Konten, in Anzeigereihenfolge. */
  arten: Art[]
  /** Auszahlung je Planjahr; `null`, wenn kein Konto für das Jahr einen Wert hat. */
  jahre: (number | null)[]
  /** Summe der vorhandenen Jahreswerte. */
  summe: number
  /** 1-basierte PDF-Seite der Maßnahme. */
  pdfSeite: number
}

/** Auswahl der Filter; `null` bedeutet „Alle“. */
export interface Auswahl {
  pb: string | null
  art: Art | null
}

/** Anzahl der Maßnahmen im Balkendiagramm (UI-SPEC E7 overflow). */
export const GROESSTE_ANZAHL = 15

const SORTIERUNG = new Intl.Collator('de')

interface Sammler {
  vorhaben: Vorhaben
  gesehen: Set<Art>
}

/**
 * Bündelt Auszahlungszeilen je `(produkt, massnahme_id)` über ihre Konten. Das Jahr eines
 * Vorhabens ist `null`, wenn alle beitragenden Zeilen dort leer sind; sonst die Summe der
 * vorhandenen Werte. Einzahlungszeilen werden übersprungen (D-08). Das Ergebnis enthält auch
 * Gruppen mit Summe 0, absteigend nach Summe, bei Gleichstand nach Name und Schlüssel.
 */
export function buendeln(zeilen: readonly Massnahme[], ab: number): Vorhaben[] {
  const sammler = new Map<string, Sammler>()
  for (const zeile of zeilen) {
    if (zeile.richtung !== 'auszahlung') {
      continue
    }
    const schluessel = `${zeile.produkt}/${zeile.massnahme_id}`
    const eintrag: Sammler = sammler.get(schluessel) ?? {
      vorhaben: {
        schluessel,
        produkt: zeile.produkt,
        massnahmeId: zeile.massnahme_id,
        name: zeile.massnahme_name,
        pb: zeile.pb,
        arten: [],
        jahre: zeile.werte.slice(ab).map(() => null),
        summe: 0,
        pdfSeite: zeile.pdf_seite,
      },
      gesehen: new Set(),
    }
    sammler.set(schluessel, eintrag)
    eintrag.gesehen.add(filterArt(zeile.art))
    zeile.werte.slice(ab).forEach((wert, i) => {
      if (wert === null) {
        return
      }
      eintrag.vorhaben.jahre[i] = (eintrag.vorhaben.jahre[i] ?? 0) + wert
    })
  }

  const ergebnis = [...sammler.values()].map(({ vorhaben, gesehen }) => ({
    ...vorhaben,
    arten: ARTEN.map((a) => a.art).filter((art) => gesehen.has(art)),
    summe: vorhaben.jahre.reduce<number>((s, wert) => s + (wert ?? 0), 0),
  }))
  return ergebnis.sort(
    (a, b) =>
      b.summe - a.summe ||
      SORTIERUNG.compare(a.name, b.name) ||
      SORTIERUNG.compare(a.schluessel, b.schluessel),
  )
}

/** Auszahlungszeilen nach Aufgabenbereich und Filterart (auf Kontoebene). */
function gefilterteZeilen(auswahl: Auswahl): Massnahme[] {
  return investitionen.massnahmen.filter(
    (zeile) =>
      zeile.richtung === 'auszahlung' &&
      (auswahl.pb === null || zeile.pb === auswahl.pb) &&
      (auswahl.art === null || filterArt(zeile.art) === auswahl.art),
  )
}

/** Alle gebündelten Gruppen der Auswahl, auch die mit Summe 0. */
export function baueGruppen(auswahl: Auswahl): Vorhaben[] {
  return buendeln(gefilterteZeilen(auswahl), planAb())
}

/**
 * Die Maßnahmen der Planjahre für die Auswahl (D-06, D-07): erst nach Art und Aufgabenbereich
 * filtern, dann bündeln, Gruppen mit Summe 0 entfallen, absteigend nach Summe.
 */
export function baueVorhaben(auswahl: Auswahl): Vorhaben[] {
  return baueGruppen(auswahl).filter((eintrag) => eintrag.summe !== 0)
}

/** Name des Aufgabenbereichs (PB) einer Maßnahme; ohne Knoten der Code. */
export function aufgabenbereichName(pb: string): string {
  return findeKnoten(pb)?.name ?? pb
}

/** Index der Maßnahme, auf die ein Klick im Balkendiagramm zeigt (`dataIndex`); sonst `null`. */
export function klickIndex(params: unknown, anzahl: number): number | null {
  if (typeof params !== 'object' || params === null || !('dataIndex' in params)) {
    return null
  }
  const index = params.dataIndex
  return typeof index === 'number' && Number.isInteger(index) && index >= 0 && index < anzahl
    ? index
    : null
}

/**
 * Tabelle aller Maßnahmen der Auswahl: Maßnahme (die Seite macht daraus den Link auf das
 * Produkt), Aufgabenbereich, Art(en), je Planjahr ein Betrag (Kopf: „{Jahr} {Wertart}“),
 * Summe und PDF-Seite. Fehlende Jahreswerte bleiben `null` und erscheinen als „–“, nie als 0.
 */
export function baueMassnahmenTabelle(vorhaben: readonly Vorhaben[]): Tabelle {
  const ab = planAb()
  const jahre = planjahre()
  const spalten: DatenSpalte[] = [
    { schluessel: 'name', titel: 'Maßnahme', art: 'text' },
    { schluessel: 'aufgabenbereich', titel: 'Aufgabenbereich', art: 'text' },
    { schluessel: 'art', titel: 'Art', art: 'text' },
    ...jahre.map((j, i): DatenSpalte => {
      const wertart = investitionen.wertarten[ab + i]
      return {
        schluessel: jahrSchluessel(j),
        titel:
          wertart === undefined
            ? formatiereJahr(j)
            : `${formatiereJahr(j)} ${wertartName(wertart)}`,
        art: 'euro',
      }
    }),
    { schluessel: 'summe', titel: 'Summe', art: 'euro' },
    { schluessel: 'seite', titel: 'PDF-Seite', art: 'text' },
  ]
  const zeilen: DatenZeile[] = vorhaben.map((eintrag) => {
    const zeile: Record<string, string | number | null> = {
      schluessel: eintrag.schluessel,
      produkt: eintrag.produkt,
      name: eintrag.name,
      aufgabenbereich: aufgabenbereichName(eintrag.pb),
      art: eintrag.arten.map(artText).join(', '),
    }
    jahre.forEach((j, i) => {
      zeile[jahrSchluessel(j)] = eintrag.jahre[i] ?? null
    })
    zeile.summe = eintrag.summe
    zeile.seite = String(eintrag.pdfSeite)
    return zeile
  })
  return { spalten, zeilen }
}

// ---------------------------------------------------------------------------------------
// Filter und URL-Zustand (D-06)
// ---------------------------------------------------------------------------------------

/** Ein Aufgabenbereich, der Auszahlungs-Maßnahmen hat. */
export interface MassnahmenAufgabenbereich {
  code: string
  name: string
}

/** Gerüst, wird mit der Implementierung ersetzt. */
export const MASSNAHMEN_AUFGABENBEREICHE: readonly MassnahmenAufgabenbereich[] = []

/** Validierter Filterzustand aus der URL. */
export interface MassnahmenFilter {
  pb: string | null
  art: Art | null
  /** `true`, wenn die URL unbrauchbare Teile trug, die entfernt werden sollen. */
  bereinigt: boolean
}

export function leseMassnahmenFilter(_query: Readonly<Record<string, unknown>>): MassnahmenFilter {
  return { pb: null, art: null, bereinigt: false }
}

export function bereinigteMassnahmenQuery<W>(
  query: Readonly<Record<string, W>>,
  _filter: MassnahmenFilter,
): Record<string, W | string> {
  return { ...query }
}

export function useMassnahmenFilter(): never {
  throw new Error('nicht implementiert')
}
