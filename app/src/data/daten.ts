// Typisierter Zugriff auf die von `pipeline/07_app_daten.py` erzeugten App-JSON-Dateien
// (D-21). Die Zuweisung erfolgt ohne Typumwandlung (kein `as`, kein `unknown`): weicht
// die JSON-Struktur vom Typ in `typen.ts` ab, schlägt `npm run type-check` fehl.

import haushaltJson from './haushalt.json'
import investitionenJson from './investitionen.json'
import produkteJson from './produkte.json'
import stellenplanJson from './stellenplan.json'
import type { Haushalt, Investitionen, Produkt, Stellenplan } from './typen'

export const haushalt: Haushalt = haushaltJson
export const stellenplan: Stellenplan = stellenplanJson
export const produkte: Produkt[] = produkteJson
export const investitionen: Investitionen = investitionenJson
