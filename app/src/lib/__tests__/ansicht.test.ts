import { describe, expect, it } from 'vitest'

import { haushalt, produkte } from '@/data/daten'
import { bereinigteQuery, findeKnoten, findeProdukt, leseAnsicht } from '@/lib/ansicht'

// Testdaten kommen aus den App-Daten, nicht aus Literalen: PB = direktes Kind von GESAMT,
// PG = Kind eines PB.
const pbCodes = haushalt.knoten.filter((k) => k.eltern === 'GESAMT').map((k) => k.code)
const pgVon = (pb: string) => haushalt.knoten.find((k) => k.eltern === pb && k.ebene === 'PG')
const pbMitPg = pbCodes.filter((code) => pgVon(code) !== undefined)

const [pbA, pbB] = pbMitPg
const pgA = pbA === undefined ? undefined : pgVon(pbA)?.code
const pgB = pbB === undefined ? undefined : pgVon(pbB)?.code

describe('Testdaten', () => {
  it('liefern zwei PB mit je einer PG', () => {
    expect(pbA).toBeDefined()
    expect(pbB).toBeDefined()
    expect(pgA).toBeDefined()
    expect(pgB).toBeDefined()
  })
})

describe('leseAnsicht (D-06, D-09)', () => {
  it('liefert ohne Query die oberste Ebene im Modus Aufwand', () => {
    expect(leseAnsicht({})).toEqual({ modus: 'aufwand', pb: null, pg: null, bereinigt: false })
  })

  it('behält einen gültigen Modus und einen gültigen PB', () => {
    expect(leseAnsicht({ modus: 'zuschussbedarf', pb: pbA })).toEqual({
      modus: 'zuschussbedarf',
      pb: pbA,
      pg: null,
      bereinigt: false,
    })
  })

  it('behält eine PG, die zum gewählten PB gehört', () => {
    expect(leseAnsicht({ pb: pbA, pg: pgA })).toEqual({
      modus: 'aufwand',
      pb: pbA,
      pg: pgA,
      bereinigt: false,
    })
  })

  it('akzeptiert KL (Weitergabe an Kreis und Land) als PB', () => {
    expect(pbCodes).toContain('KL')
    expect(leseAnsicht({ pb: 'KL' })).toMatchObject({ pb: 'KL', bereinigt: false })
  })

  it.each(['__proto__', 'constructor', 'toString', 'GESAMT', '999999', ''])(
    'verwirft pb=%j und meldet bereinigt',
    (pb) => {
      expect(leseAnsicht({ pb })).toEqual({
        modus: 'aufwand',
        pb: null,
        pg: null,
        bereinigt: true,
      })
    },
  )

  it.each(['toString', '__proto__', 'Aufwand', ''])(
    'verwirft modus=%j und fällt auf Aufwand zurück',
    (modus) => {
      expect(leseAnsicht({ modus })).toEqual({
        modus: 'aufwand',
        pb: null,
        pg: null,
        bereinigt: true,
      })
    },
  )

  it('verwirft eine PG ohne PB', () => {
    expect(leseAnsicht({ pg: pgA })).toEqual({
      modus: 'aufwand',
      pb: null,
      pg: null,
      bereinigt: true,
    })
  })

  it('verwirft eine PG eines anderen PB und behält den PB', () => {
    expect(leseAnsicht({ pb: pbA, pg: pgB })).toEqual({
      modus: 'aufwand',
      pb: pbA,
      pg: null,
      bereinigt: true,
    })
  })

  it('verwirft die PG, wenn der PB ungültig ist', () => {
    expect(leseAnsicht({ pb: '__proto__', pg: pgA })).toMatchObject({
      pb: null,
      pg: null,
      bereinigt: true,
    })
  })

  it('nimmt bei Arrays das erste Element und behandelt null als ungültig', () => {
    expect(leseAnsicht({ pb: [pbA, pbB] })).toMatchObject({ pb: pbA, bereinigt: false })
    expect(leseAnsicht({ pb: null })).toMatchObject({ pb: null, bereinigt: true })
  })
})

describe('bereinigteQuery', () => {
  it('entfernt ungültige Teile und behält fremde Schlüssel sowie gültige Teile', () => {
    const query = { jahr: '2027', modus: 'toString', pb: pbA, pg: pgB }
    const ansicht = leseAnsicht(query)
    expect(bereinigteQuery(query, ansicht)).toEqual({ jahr: '2027', pb: pbA })
  })

  it('behält einen gültigen Modus', () => {
    const query = { modus: 'zuschussbedarf', pb: '__proto__' }
    expect(bereinigteQuery(query, leseAnsicht(query))).toEqual({ modus: 'zuschussbedarf' })
  })
})

describe('findeKnoten', () => {
  it('findet GESAMT und einen PB', () => {
    expect(findeKnoten('GESAMT')?.ebene).toBe('GESAMT')
    expect(findeKnoten(pbA ?? '')?.ebene).toBe('PB')
  })

  it.each(['__proto__', 'constructor', 'toString', '999999'])(
    'liefert für %j undefined',
    (code) => {
      expect(findeKnoten(code)).toBeUndefined()
    },
  )

  it('liefert für Nicht-Texte undefined', () => {
    expect(findeKnoten(123)).toBeUndefined()
    expect(findeKnoten(['GESAMT'])).toBeUndefined()
    expect(findeKnoten(undefined)).toBeUndefined()
  })
})

describe('findeProdukt (AUSG-05)', () => {
  it('findet jedes Produkt der Daten über seinen Code', () => {
    for (const produkt of produkte) {
      expect(findeProdukt(produkt.code)).toBe(produkt)
    }
  })

  it('liefert für unbekannte Codes und Prototyp-Schlüssel undefined', () => {
    expect(findeProdukt('__proto__')).toBeUndefined()
    expect(findeProdukt('constructor')).toBeUndefined()
    expect(findeProdukt('999999')).toBeUndefined()
    expect(findeProdukt('')).toBeUndefined()
  })
})
