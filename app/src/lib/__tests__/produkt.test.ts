import { describe, expect, it } from 'vitest'

import { haushalt, produkte } from '@/data/daten'
import { baueProduktKopf, bindungsgradText } from '@/lib/produkt'

// Alle Testdaten kommen aus den App-Daten, nicht aus Literalen.
const erstes = produkte[0]

describe('Testdaten', () => {
  it('enthalten die 63 Produkte des Haushalts', () => {
    expect(produkte).toHaveLength(63)
    expect(erstes).toBeDefined()
  })
})

describe('bindungsgradText', () => {
  it('schreibt die drei Werte der Pipeline aus', () => {
    expect(bindungsgradText('pflichtig')).toBe('pflichtig')
    expect(bindungsgradText('freiwillig')).toBe('freiwillig')
    expect(bindungsgradText('teils')).toBe('teils pflichtig, teils freiwillig')
  })

  it('gibt einen unbekannten Wert unverändert zurück', () => {
    expect(bindungsgradText('unklar')).toBe('unklar')
  })

  it('löst Prototyp-Schlüssel nicht auf', () => {
    expect(bindungsgradText('__proto__')).toBe('__proto__')
    expect(bindungsgradText('constructor')).toBe('constructor')
  })
})

describe('baueProduktKopf (D-09)', () => {
  it.each(produkte.map((p) => p.code))('baut den Kopf von Produkt %s', (code) => {
    const kopf = baueProduktKopf(code)
    expect(kopf).not.toBeNull()
    if (kopf === null) {
      return
    }
    expect(kopf.produkt.code).toBe(code)
    expect(kopf.pbName).toBe(haushalt.knoten.find((k) => k.code === kopf.produkt.pb)?.name)
    expect(kopf.pgName).toBe(haushalt.knoten.find((k) => k.code === kopf.produkt.pg)?.name)
    expect(kopf.pbName).not.toBe('')
    expect(kopf.pgName).not.toBe('')
    expect(kopf.quelleSeite).toBe(kopf.produkt.pdf_seiten[0])
  })

  it('führt ohne gemerkten Zustand zur Produktgruppe des Produkts', () => {
    const kopf = baueProduktKopf(erstes?.code ?? '')
    expect(kopf?.zurueck).toEqual({
      name: 'ausgaben',
      query: { pb: erstes?.pb, pg: erstes?.pg },
    })
    expect(kopf?.zurueckText).toBe(kopf?.pgName)
  })

  it('behält Modus, Aufgabenbereich und Produktgruppe aus einer gültigen Query', () => {
    const kopf = baueProduktKopf(erstes?.code ?? '', {
      modus: 'zuschussbedarf',
      pb: erstes?.pb,
      pg: erstes?.pg,
    })
    expect(kopf?.zurueck).toEqual({
      name: 'ausgaben',
      query: { modus: 'zuschussbedarf', pb: erstes?.pb, pg: erstes?.pg },
    })
  })

  it('benennt den Aufgabenbereich, wenn die gemerkte Query keine Produktgruppe trägt', () => {
    const kopf = baueProduktKopf(erstes?.code ?? '', { pb: erstes?.pb })
    expect(kopf?.zurueck).toEqual({ name: 'ausgaben', query: { pb: erstes?.pb } })
    expect(kopf?.zurueckText).toBe(kopf?.pbName)
  })

  it('verwirft eine gemerkte Query, die zu einem anderen Aufgabenbereich gehört', () => {
    const fremd = haushalt.knoten.find(
      (k) => k.eltern === 'GESAMT' && k.code !== erstes?.pb && k.code !== 'KL',
    )
    expect(fremd).toBeDefined()
    const kopf = baueProduktKopf(erstes?.code ?? '', { pb: fremd?.code })
    expect(kopf?.zurueck).toEqual({
      name: 'ausgaben',
      query: { pb: erstes?.pb, pg: erstes?.pg },
    })
  })

  it('verwirft unbrauchbare Query-Werte, ohne sie weiterzureichen', () => {
    const kopf = baueProduktKopf(erstes?.code ?? '', {
      modus: '<script>',
      pb: '__proto__',
      pg: ['x'],
    })
    expect(kopf?.zurueck).toEqual({
      name: 'ausgaben',
      query: { pb: erstes?.pb, pg: erstes?.pg },
    })
  })

  it.each(['__proto__', 'constructor', 'toString', 'GESAMT', '999999', ''])(
    'liefert für den Code %j kein Produkt',
    (code) => {
      expect(baueProduktKopf(code)).toBeNull()
    },
  )

  it('nennt ein abweichendes Original des Bindungsgrads, sonst nicht', () => {
    for (const produkt of produkte) {
      const kopf = baueProduktKopf(produkt.code)
      expect(kopf?.bindungsgrad).toBe(bindungsgradText(produkt.bindungsgrad))
      if (kopf?.bindungsgradOriginal !== null) {
        expect(kopf?.bindungsgradOriginal).toBe(produkt.bindungsgrad_original)
      }
    }
    const rein = produkte.find((p) => p.bindungsgrad === 'pflichtig')
    expect(baueProduktKopf(rein?.code ?? '')?.bindungsgradOriginal).toBeNull()
  })
})
