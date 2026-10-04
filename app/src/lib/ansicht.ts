import { computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { haushalt, produkte } from '@/data/daten'
import type { Knoten, Produkt } from '@/data/typen'

/** Darstellungsmodus der Ausgabenseite (D-05). */
export type Modus = 'aufwand' | 'zuschussbedarf'

/** Validierter Zustand der Ausgabenansicht aus der URL (D-06, D-09). */
export interface Ansicht {
  modus: Modus
  /** Code eines Aufgabenbereichs (direktes Kind von GESAMT, auch KL) oder `null` (oberste Ebene). */
  pb: string | null
  /** Code einer Produktgruppe unter `pb` oder `null`. */
  pg: string | null
  /** `true`, wenn die URL unbrauchbare Teile trug, die entfernt werden sollen. */
  bereinigt: boolean
}

const WURZEL = 'GESAMT'
const ANSICHTS_SCHLUESSEL: ReadonlySet<string> = new Set(['modus', 'pb', 'pg'])
const NUR_PG: ReadonlySet<string> = new Set(['pg'])
const PB_UND_PG: ReadonlySet<string> = new Set(['pb', 'pg'])

// Allowlists aus den Daten. URL-Werte werden nur über Map/Set nachgeschlagen, nie als
// Schlüssel eines einfachen Objekts (Sicherheit V5, Prototyp-Schlüssel wie `__proto__`).
const KNOTEN: ReadonlyMap<string, Knoten> = new Map(
  haushalt.knoten.map((k) => [k.code, k] as const),
)
const PRODUKTE: ReadonlyMap<string, Produkt> = new Map(produkte.map((p) => [p.code, p] as const))
const MODI: ReadonlySet<string> = new Set<Modus>(['aufwand', 'zuschussbedarf'])

function istModus(wert: unknown): wert is Modus {
  return typeof wert === 'string' && MODI.has(wert)
}

function erster(roh: unknown): unknown {
  return Array.isArray(roh) ? roh[0] : roh
}

/** Knoten der Haushaltshierarchie zu einem Code; `undefined` für alles Unbekannte. */
export function findeKnoten(code: unknown): Knoten | undefined {
  return typeof code === 'string' ? KNOTEN.get(code) : undefined
}

/** Produkt zu einem Code (Route `/produkt/:code`); `undefined` für alles Unbekannte. */
export function findeProdukt(code: unknown): Produkt | undefined {
  return typeof code === 'string' ? PRODUKTE.get(code) : undefined
}

/**
 * Liest `modus`, `pb` und `pg` defensiv aus der Query (D-06, D-09): `modus` nur aus
 * {aufwand, zuschussbedarf}, `pb` nur als direktes Kind von GESAMT (inkl. KL), `pg` nur,
 * wenn `pb` gültig ist und die Gruppe unter ihm hängt. Unbrauchbare Teile fallen auf den
 * Standard zurück und setzen `bereinigt`.
 */
export function leseAnsicht(query: Readonly<Record<string, unknown>>): Ansicht {
  let bereinigt = false

  let modus: Modus = 'aufwand'
  const rohModus = erster(query.modus)
  if (rohModus !== undefined) {
    if (istModus(rohModus)) {
      modus = rohModus
    } else {
      bereinigt = true
    }
  }

  let pb: string | null = null
  const rohPb = erster(query.pb)
  if (rohPb !== undefined) {
    const knoten = findeKnoten(rohPb)
    if (knoten !== undefined && knoten.eltern === WURZEL) {
      pb = knoten.code
    } else {
      bereinigt = true
    }
  }

  let pg: string | null = null
  const rohPg = erster(query.pg)
  if (rohPg !== undefined) {
    const knoten = findeKnoten(rohPg)
    if (pb !== null && knoten !== undefined && knoten.eltern === pb) {
      pg = knoten.code
    } else {
      bereinigt = true
    }
  }

  return { modus, pb, pg, bereinigt }
}

/** Query ohne die genannten Schlüssel (alle anderen bleiben). `fromEntries` legt die Schlüssel als Datenfelder an. */
function ohne<W>(
  query: Readonly<Record<string, W>>,
  schluessel: ReadonlySet<string>,
): Record<string, W> {
  return Object.fromEntries(Object.entries(query).filter(([name]) => !schluessel.has(name)))
}

/**
 * Die Query mit nur den gültigen Ansichtsteilen: ungültige `modus`/`pb`/`pg`-Werte
 * entfallen, fremde Schlüssel (z. B. `jahr`) und gültige Teile bleiben.
 */
export function bereinigteQuery<W>(
  query: Readonly<Record<string, W>>,
  ansicht: Ansicht,
): Record<string, W | string> {
  const ergebnis: Record<string, W | string> = ohne(query, ANSICHTS_SCHLUESSEL)
  if (istModus(erster(query.modus))) {
    ergebnis.modus = ansicht.modus
  }
  if (ansicht.pb !== null) {
    ergebnis.pb = ansicht.pb
  }
  if (ansicht.pg !== null) {
    ergebnis.pg = ansicht.pg
  }
  return ergebnis
}

/**
 * Validierter Ansichtszustand der Ausgabenseite in der URL (`modus`, `pb`, `pg`).
 * Ungültige Teile werden mit `router.replace` entfernt; Modus-Wechsel nutzen `replace`,
 * Drilldown-Schritte `push` (Zurück-Taste geht eine Ebene hoch, UI-SPEC).
 */
export function useAnsicht() {
  const route = useRoute()
  const router = useRouter()

  const ansicht = computed(() => leseAnsicht(route.query))

  watch(
    ansicht,
    (aktuell) => {
      if (aktuell.bereinigt) {
        void router.replace({ query: bereinigteQuery(route.query, aktuell), hash: route.hash })
      }
    },
    { immediate: true },
  )

  function setzeModus(modus: Modus) {
    if (!istModus(modus)) {
      return
    }
    void router.replace({ query: { ...route.query, modus }, hash: route.hash })
  }

  /**
   * Öffnet die nächste Ebene: ein direktes Kind von GESAMT setzt `pb` und löscht `pg`,
   * ein Kind des aktuellen `pb` setzt `pg`. Alles andere wird ignoriert.
   */
  function oeffne(code: string) {
    const knoten = findeKnoten(code)
    if (knoten === undefined) {
      return
    }
    if (knoten.eltern === WURZEL) {
      void router.push({
        query: { ...ohne(route.query, NUR_PG), pb: knoten.code },
        hash: route.hash,
      })
    } else if (ansicht.value.pb !== null && knoten.eltern === ansicht.value.pb) {
      void router.push({ query: { ...route.query, pg: knoten.code }, hash: route.hash })
    }
  }

  /**
   * Geht zu einer höheren Ebene zurück (Brotkrumen). `ebene` ist der Code des Ziels:
   * GESAMT leert `pb` und `pg`, der aktuelle `pb` leert nur `pg`; alles andere ändert nichts.
   */
  function zurueck(ebene: string) {
    if (ebene === WURZEL) {
      void router.push({ query: ohne(route.query, PB_UND_PG), hash: route.hash })
    } else if (ansicht.value.pb !== null && ebene === ansicht.value.pb) {
      void router.push({ query: ohne(route.query, NUR_PG), hash: route.hash })
    }
  }

  /** Ansichtsteile für Links, die später hierher zurückführen (z. B. von `/produkt/:code`). */
  function ansichtsQuery(): Record<string, string> {
    const query: Record<string, string> = {}
    if (ansicht.value.modus !== 'aufwand') {
      query.modus = ansicht.value.modus
    }
    if (ansicht.value.pb !== null) {
      query.pb = ansicht.value.pb
    }
    if (ansicht.value.pg !== null) {
      query.pg = ansicht.value.pg
    }
    return query
  }

  return { ansicht, setzeModus, oeffne, zurueck, ansichtsQuery }
}
