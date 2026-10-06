// Belegschlüssel der Drilldown-Tabelle auf /ausgaben (Phase 7, D-01). Gerüst: Die Umsetzung
// folgt im nächsten Schritt.

import type { Modus } from '@/lib/ansicht'
import type { EbenenEintrag } from '@/lib/drilldown'

export interface EbenenBeleg {
  /** Belegschlüssel (`lib/quelle.ts`). */
  schluessel: string
  /** Herleitung eines berechneten Werts (D-03), sonst `null`. */
  herleitung: string | null
}

export function ebenenBeleg(
  _eintrag: Pick<EbenenEintrag, 'code' | 'istKl'>,
  _jahrIndex: number,
  _modus: Modus,
): EbenenBeleg | null {
  return null
}
