// RED-Stand: Signaturen ohne Implementierung (wird im GREEN-Schritt ersetzt).

import type { VorberichtTabelle } from '@/data/typen'

export interface Zuschuss {
  schluessel: string
  name: string
  wert: number | null
  gerundet: boolean
  pdfSeite: number | null
}

export interface ZuschussGruppe {
  posten: Zuschuss[]
  gesamt: number | null
  pdfSeiten: number[]
}

export function vorberichtTabelle(name: string): VorberichtTabelle {
  throw new Error(`nicht implementiert: ${name}`)
}

export function kitaZuschuesse(): ZuschussGruppe {
  return { posten: [], gesamt: null, pdfSeiten: [] }
}

export function weitereZuschuesse(): { transfer: ZuschussGruppe; lfdZwecke: ZuschussGruppe } {
  return {
    transfer: { posten: [], gesamt: null, pdfSeiten: [] },
    lfdZwecke: { posten: [], gesamt: null, pdfSeiten: [] },
  }
}
