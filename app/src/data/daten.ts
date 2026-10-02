// Typisierter Zugriff auf die von `pipeline/07_app_daten.py` erzeugte haushalt.json
// (D-21). Die Zuweisung erfolgt ohne Typumwandlung (kein `as`, kein `unknown`): weicht
// die JSON-Struktur vom Typ in `typen.ts` ab, schlägt `npm run type-check` fehl.

import haushaltJson from './haushalt.json'
import type { Haushalt } from './typen'

export const haushalt: Haushalt = haushaltJson
