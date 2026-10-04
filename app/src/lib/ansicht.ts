// RED-Gerüst (TDD, Plan 05-04 Task 2): Signaturen ohne Verhalten, damit die Tests an
// Assertions scheitern und nicht am Import. Die Implementierung folgt im GREEN-Commit.
import type { Knoten, Produkt } from '@/data/typen'

export type Modus = 'aufwand' | 'zuschussbedarf'

export interface Ansicht {
  modus: Modus
  pb: string | null
  pg: string | null
  bereinigt: boolean
}

export function leseAnsicht(query: Readonly<Record<string, unknown>>): Ansicht {
  void query
  return { modus: 'aufwand', pb: null, pg: null, bereinigt: false }
}

export function bereinigteQuery(
  query: Readonly<Record<string, unknown>>,
  ansicht: Ansicht,
): Record<string, unknown> {
  void query
  void ansicht
  return {}
}

export function findeKnoten(code: unknown): Knoten | undefined {
  void code
  return undefined
}

export function findeProdukt(code: unknown): Produkt | undefined {
  void code
  return undefined
}
