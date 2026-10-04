import { computed, watch } from 'vue'
import { useRoute, useRouter, type RouteLocationRaw } from 'vue-router'

import { haushalt } from '@/data/daten'

/**
 * Anzeigenamen der Wertarten aus `haushalt.wertarten` (UI-SPEC: ergebnis → Ist,
 * ansatz → Ansatz, planung → Planung). Eine `Map`, damit ein Schlüssel nie als
 * Objekteigenschaft (z. B. `__proto__`) aufgelöst wird.
 */
export const WERTART_NAMEN: ReadonlyMap<string, string> = new Map([
  ['ergebnis', 'Ist'],
  ['ansatz', 'Ansatz'],
  ['planung', 'Planung'],
])

/** Anzeigename einer Wertart; eine unbekannte Wertart ist ein Datenfehler und wirft. */
export function wertartName(wertart: string): string {
  const name = WERTART_NAMEN.get(wertart)
  if (name === undefined) {
    throw new Error(`Unbekannte Wertart: ${wertart}`)
  }
  return name
}

/** Wertart eines Jahres aus `haushalt.wertarten` (gleiche Position wie in `haushalt.jahre`). */
export function wertartFuerJahr(jahr: number): string {
  const index = haushalt.jahre.indexOf(jahr)
  const wertart = haushalt.wertarten[index]
  if (index < 0 || wertart === undefined) {
    throw new Error(`Jahr ${jahr} steht nicht in haushalt.jahre`)
  }
  return wertart
}

export interface GelesenesJahr {
  /** Das gültige Jahr, sonst der Standard. */
  jahr: number
  /** `false`, wenn die URL einen unbrauchbaren `jahr`-Wert trägt (dann bereinigen). */
  gueltig: boolean
}

/**
 * Liest `?jahr=` defensiv (D-10, Sicherheit V5): angenommen wird nur eine reine
 * Ziffernfolge, deren Zahl in `jahre` steht. Ein Array (mehrfaches `jahr`) liefert
 * sein erstes Element. Fehlt der Schlüssel, gilt der Standard als gültig; ein
 * vorhandener, aber unbrauchbarer Wert (auch `?jahr` ohne Wert) als ungültig.
 */
export function leseJahr(roh: unknown, jahre: readonly number[], standard: number): GelesenesJahr {
  const wert = Array.isArray(roh) ? roh[0] : roh
  if (wert === undefined) {
    return { jahr: standard, gueltig: true }
  }
  if (typeof wert === 'string' && /^\d+$/.test(wert)) {
    const zahl = Number(wert)
    if (jahre.includes(zahl)) {
      return { jahr: zahl, gueltig: true }
    }
  }
  return { jahr: standard, gueltig: false }
}

/**
 * Hängt das explizit gewählte Jahr an ein internes Linkziel (D-10). Ohne
 * explizites Jahr (`null`) und bei Textzielen bleibt das Ziel unverändert; die
 * Zielseite fällt dann selbst auf das Haushaltsjahr zurück.
 */
export function jahrLinkFuer(
  ziel: RouteLocationRaw,
  explizitesJahr: number | null,
): RouteLocationRaw {
  if (typeof ziel === 'string' || explizitesJahr === null) {
    return ziel
  }
  return { ...ziel, query: { ...ziel.query, jahr: String(explizitesJahr) } }
}

/**
 * Das gewählte Jahr als einzige Quelle der Wahrheit in der URL (`?jahr=`, D-10).
 * Ein ungültiger Wert wird mit `router.replace` aus der URL entfernt (kein
 * Verlaufseintrag); die Seite zeigt solange das Haushaltsjahr.
 */
export function useJahr() {
  const route = useRoute()
  const router = useRouter()

  const gelesen = computed(() => leseJahr(route.query.jahr, haushalt.jahre, haushalt.haushaltsjahr))
  const jahr = computed(() => gelesen.value.jahr)
  const index = computed(() => haushalt.jahre.indexOf(jahr.value))
  const wertart = computed(() => wertartFuerJahr(jahr.value))
  /** Das Jahr nur, wenn die URL ein gültiges `jahr` trägt (für `jahrLink`). */
  const explizitesJahr = computed(() =>
    route.query.jahr !== undefined && gelesen.value.gueltig ? gelesen.value.jahr : null,
  )

  watch(
    gelesen,
    (aktuell) => {
      if (!aktuell.gueltig) {
        const rest = Object.fromEntries(
          Object.entries(route.query).filter(([schluessel]) => schluessel !== 'jahr'),
        )
        void router.replace({ query: rest, hash: route.hash })
      }
    },
    { immediate: true },
  )

  /** Wechselt das Jahr per `router.replace` (kein Verlaufseintrag), andere Query-Schlüssel bleiben. */
  function setzeJahr(neu: number) {
    if (!haushalt.jahre.includes(neu)) {
      return
    }
    void router.replace({ query: { ...route.query, jahr: String(neu) }, hash: route.hash })
  }

  /** Linkziel mit dem aktuellen, explizit gewählten Jahr. */
  function jahrLink(ziel: RouteLocationRaw): RouteLocationRaw {
    return jahrLinkFuer(ziel, explizitesJahr.value)
  }

  return { jahr, index, wertart, setzeJahr, jahrLink }
}
