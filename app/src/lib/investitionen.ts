// Investitionsmaßnahmen der Planjahre für `/investitionen` (INV-01, D-06, D-07, D-08).
// Reine Funktionen über `investitionen.json`: Auszahlungen je Konto werden erst nach Art und
// Aufgabenbereich gefiltert und dann je Produkt und Maßnahme gebündelt. Nichts wird neu
// gerechnet außer der Summe der Kontozeilen; Einzahlungen kommen nie vor (D-08).
//
// Dokumentierte Abweichung von D-07: Der Bündelungsschlüssel ist `(produkt, massnahme_id)`
// statt `massnahme_id` allein, weil 11 Kennungen unter mehreren Produkten vorkommen (z. B.
// KLIMA1 mit verschiedenen Photovoltaikanlagen) und der Link auf `/produkt/:code` sonst
// mehrdeutig wäre (RESEARCH Pitfall 2, Entscheidung 2 des Nutzers).

import { computed, watch } from 'vue'
import { useRoute, useRouter, type LocationQueryRaw } from 'vue-router'

import { anzahlText, euroKurz, jahr as formatiereJahr } from '@/charts/format'
import type { DatenSpalte, DatenZeile } from '@/components/datenTabelle'
import { haushalt, investitionen } from '@/data/daten'
import type { Massnahme } from '@/data/typen'
import { findeKnoten } from '@/lib/ansicht'
import { wertartName } from '@/lib/jahr'
import { jahrSchluessel, type Tabelle } from '@/lib/produkt'
import { belegSchluessel } from '@/lib/quelle'

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
  /**
   * Belegschlüssel (`inv`): bei mehreren Konten der der Kontozeile mit der größten Auszahlung im
   * Haushaltsjahr (bei Gleichstand die erste), sonst der des einen Kontos.
   */
  beleg: string
  /** Anzahl der gebündelten Auszahlungszeilen (Konten); über 1 steht der Beleg nur für eine Zeile. */
  anzahlKonten: number
}

/** Herleitung für den Beleg einer Maßnahme, die mehrere Konten bündelt (D-03). */
export const HERLEITUNG_MEHRERE_KONTEN = 'Summe aller Konten dieser Maßnahme'

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
  /** Größte Auszahlung im Haushaltsjahr unter den bisherigen Zeilen; `null` ohne Wert. */
  belegWert: number | null
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
        beleg: belegSchluessel.inv(zeile.produkt, zeile.massnahme_id, zeile.konto, zeile.richtung),
        anzahlKonten: 0,
      },
      gesehen: new Set(),
      belegWert: zeile.werte[ab] ?? null,
    }
    if (sammler.has(schluessel)) {
      // Weitere Zeile derselben Maßnahme: der Beleg wechselt nur zu einer echt größeren Auszahlung.
      const wert = zeile.werte[ab] ?? null
      if (wert !== null && (eintrag.belegWert === null || wert > eintrag.belegWert)) {
        eintrag.belegWert = wert
        eintrag.vorhaben.beleg = belegSchluessel.inv(
          zeile.produkt,
          zeile.massnahme_id,
          zeile.konto,
          zeile.richtung,
        )
      }
    }
    eintrag.vorhaben.anzahlKonten += 1
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

/**
 * Text der aria-live-Ergebniszeile auf `/investitionen` (UI-SPEC Copywriting „Ergebniszeile
 * Filter“): Anzahl der Maßnahmen, im Singular bei genau einer (WR-02), und die Summe der
 * gezeigten Vorhaben als gekürzter Euro-Betrag.
 */
export function ergebnisText(vorhaben: readonly Vorhaben[]): string {
  const summe = vorhaben.reduce((gesamt, eintrag) => gesamt + eintrag.summe, 0)
  return `${anzahlText(vorhaben.length, 'Maßnahme', 'Maßnahmen')} · zusammen ${euroKurz(summe)}`
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
 * Summe und Quelle (Beleg der Kontozeile, bei mehreren Konten mit Herleitung). Fehlende
 * Jahreswerte bleiben `null` und erscheinen als „–“, nie als 0.
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
    { schluessel: 'quelle', titel: 'Quelle', art: 'quelle' },
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
    zeile.quelle = eintrag.beleg
    if (eintrag.anzahlKonten > 1) {
      zeile.quelleHerleitung = HERLEITUNG_MEHRERE_KONTEN
    }
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

/**
 * Die Aufgabenbereiche, die Auszahlungs-Maßnahmen haben, in Knotenreihenfolge. Nur echte
 * Aufgabenbereiche (Ebene PB unter GESAMT, nicht synthetisch): „Weitergabe an Kreis und Land“
 * (KL) ist auch ein PB-Knoten, hat aber keine Maßnahmen und ist nie ein Aufgabenbereich
 * dieser Liste (RESEARCH Pitfall 8).
 */
export const MASSNAHMEN_AUFGABENBEREICHE: readonly MassnahmenAufgabenbereich[] = (() => {
  const mitMassnahmen = new Set(baueVorhaben({ pb: null, art: null }).map((e) => e.pb))
  return haushalt.knoten
    .filter(
      (knoten) =>
        knoten.ebene === 'PB' &&
        knoten.eltern === 'GESAMT' &&
        !knoten.synthetisch &&
        mitMassnahmen.has(knoten.code),
    )
    .map((knoten) => ({ code: knoten.code, name: knoten.name }))
})()

// Allowlists als Set: URL-Werte werden nie als Schlüssel eines einfachen Objekts benutzt
// (Prototyp-Schlüssel wie `__proto__`, T-06-14).
const PB_CODES: ReadonlySet<string> = new Set(MASSNAHMEN_AUFGABENBEREICHE.map((b) => b.code))
const ART_CODES: ReadonlySet<string> = new Set(ARTEN.map((a) => a.art))
const FILTER_SCHLUESSEL: ReadonlySet<string> = new Set(['pb', 'art'])
const NUR_PB: ReadonlySet<string> = new Set(['pb'])
const NUR_ART: ReadonlySet<string> = new Set(['art'])

function istArt(wert: unknown): wert is Art {
  return typeof wert === 'string' && ART_CODES.has(wert)
}

function istPb(wert: unknown): wert is string {
  return typeof wert === 'string' && PB_CODES.has(wert)
}

function erster(roh: unknown): unknown {
  return Array.isArray(roh) ? roh[0] : roh
}

/** Validierter Filterzustand aus der URL. */
export interface MassnahmenFilter {
  pb: string | null
  art: Art | null
  /** `true`, wenn die URL unbrauchbare Teile trug, die entfernt werden sollen. */
  bereinigt: boolean
}

/**
 * Liest `pb` und `art` defensiv aus der Query (D-06, T-06-14): `pb` nur aus
 * `MASSNAHMEN_AUFGABENBEREICHE`, `art` nur aus den vier Filterarten, bei einem Array gilt das
 * erste Element. Fehlt ein Schlüssel, gilt „Alle“; ein vorhandener, aber unbrauchbarer Wert
 * (auch `?art` ohne Wert) fällt auf „Alle“ zurück und setzt `bereinigt`.
 */
export function leseMassnahmenFilter(query: Readonly<Record<string, unknown>>): MassnahmenFilter {
  let bereinigt = false

  let pb: string | null = null
  const rohPb = erster(query.pb)
  if (rohPb !== undefined) {
    if (istPb(rohPb)) {
      pb = rohPb
    } else {
      bereinigt = true
    }
  }

  let art: Art | null = null
  const rohArt = erster(query.art)
  if (rohArt !== undefined) {
    if (istArt(rohArt)) {
      art = rohArt
    } else {
      bereinigt = true
    }
  }

  return { pb, art, bereinigt }
}

/** Query ohne die genannten Schlüssel; `fromEntries` legt die Schlüssel als Datenfelder an. */
function ohne<W>(
  query: Readonly<Record<string, W>>,
  schluessel: ReadonlySet<string>,
): Record<string, W> {
  return Object.fromEntries(Object.entries(query).filter(([name]) => !schluessel.has(name)))
}

/**
 * Die Query mit nur den gültigen Filterteilen: ungültige `pb`/`art`-Werte entfallen, fremde
 * Schlüssel (z. B. `jahr`) und gültige Teile bleiben.
 */
export function bereinigteMassnahmenQuery<W>(
  query: Readonly<Record<string, W>>,
  filter: MassnahmenFilter,
): Record<string, W | string> {
  const ergebnis: Record<string, W | string> = ohne(query, FILTER_SCHLUESSEL)
  if (filter.pb !== null) {
    ergebnis.pb = filter.pb
  }
  if (filter.art !== null) {
    ergebnis.art = filter.art
  }
  return ergebnis
}

/**
 * Filterzustand der Maßnahmen in der URL (`pb`, `art`). Ungültige Teile werden mit
 * `router.replace` entfernt; jede Änderung nutzt `replace` (kein Verlaufseintrag), fremde
 * Query-Schlüssel und der Hash bleiben. Die Seite zeigt immer alle Planjahre, `?jahr=` gilt
 * hier nicht (D-07).
 */
export function useMassnahmenFilter() {
  const route = useRoute()
  const router = useRouter()
  // Beim Verlassen der Seite wechselt die Route vor dem Abbau der Komponente; dann darf der
  // Zustand der nächsten Seite nicht angefasst werden.
  const eigeneRoute = route.name

  const filter = computed(() => leseMassnahmenFilter(route.query))
  const vorhaben = computed(() => baueVorhaben({ pb: filter.value.pb, art: filter.value.art }))

  function ersetze(query: LocationQueryRaw) {
    if (route.name !== eigeneRoute) {
      return
    }
    void router.replace({ query, hash: route.hash })
  }

  watch(
    filter,
    (aktuell) => {
      if (aktuell.bereinigt) {
        ersetze(bereinigteMassnahmenQuery(route.query, aktuell))
      }
    },
    { immediate: true },
  )

  /** Wählt einen Aufgabenbereich; `null` bedeutet „Alle“, ein unbekannter Code wird ignoriert. */
  function setzePb(code: string | null) {
    if (code === null) {
      ersetze(ohne(route.query, NUR_PB))
    } else if (istPb(code)) {
      ersetze({ ...ohne(route.query, NUR_PB), pb: code })
    }
  }

  /** Wählt eine Art; `null` bedeutet „Alle“, ein unbekannter Wert wird ignoriert. */
  function setzeArt(art: Art | null) {
    if (art === null) {
      ersetze(ohne(route.query, NUR_ART))
    } else if (istArt(art)) {
      ersetze({ ...ohne(route.query, NUR_ART), art })
    }
  }

  /** Setzt beide Filter auf „Alle“. */
  function zuruecksetzen() {
    ersetze(ohne(route.query, FILTER_SCHLUESSEL))
  }

  return { filter, vorhaben, setzePb, setzeArt, zuruecksetzen }
}
