import { readFileSync } from 'node:fs'

import { FUSSZEILEN_ROUTEN, menueLinks } from '../src/lib/menue'

// Routenliste der Browser-Tests (D-12). Nichts davon ist von Hand getippt: die Menürouten
// kommen aus `menueLinks()`, die Fußzeilenrouten aus `FUSSZEILEN_ROUTEN`, die Produktseite
// aus den Daten (erstes Produkt nach Code mit mindestens einer Grundzahl, einer Erläuterung
// und einer Maßnahme).

export interface Route {
  /** Routenname in `router/index.ts`. */
  name: string
  /** Pfad mit führendem Schrägstrich, ohne `#`. */
  pfad: string
}

interface ProduktJson {
  code: string
  grundzahlen: unknown[]
  erlaeuterungen: unknown[]
}

interface InvestitionenJson {
  massnahmen: { produkt: string }[]
}

function lies<T>(datei: string): T {
  return JSON.parse(readFileSync(new URL(`../src/data/${datei}`, import.meta.url), 'utf-8')) as T
}

/** Pfad einer benannten Route; die Startseite ist die Wurzel, alle anderen heißen wie ihr Name. */
function pfadVon(name: string): string {
  return name === 'start' ? '/' : `/${name}`
}

/** Code des ersten Produkts (nach Code sortiert) mit Grundzahl, Erläuterung und Maßnahme. */
export function beispielProdukt(): string {
  const produkte = lies<ProduktJson[]>('produkte.json')
  const mitMassnahme = new Set(
    lies<InvestitionenJson>('investitionen.json').massnahmen.map((massnahme) => massnahme.produkt),
  )
  const treffer = produkte
    .filter(
      (produkt) =>
        produkt.grundzahlen.length > 0 &&
        produkt.erlaeuterungen.length > 0 &&
        mitMassnahme.has(produkt.code),
    )
    .map((produkt) => produkt.code)
    .sort()[0]
  if (treffer === undefined) {
    throw new Error('Kein Produkt mit Grundzahl, Erläuterung und Maßnahme in den App-Daten')
  }
  return treffer
}

/** Menürouten, Fußzeilenrouten und die Produktseite des Beispielprodukts. */
export function routen(): Route[] {
  const menue = menueLinks().map((link) => ({ name: link.name, pfad: pfadVon(link.name) }))
  const fusszeile = FUSSZEILEN_ROUTEN.map((name) => ({ name, pfad: pfadVon(name) }))
  return [...menue, ...fusszeile, { name: 'produkt', pfad: `/produkt/${beispielProdukt()}` }]
}
