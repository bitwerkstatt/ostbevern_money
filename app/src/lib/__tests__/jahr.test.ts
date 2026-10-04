import { describe, expect, it } from 'vitest'

import { haushalt } from '@/data/daten'
import { jahrLinkFuer, leseJahr, wertartFuerJahr, wertartName } from '@/lib/jahr'

const { jahre, haushaltsjahr } = haushalt

describe('leseJahr (UI-01, D-10)', () => {
  it('liefert das Haushaltsjahr als gültigen Standard, wenn kein jahr in der URL steht', () => {
    expect(leseJahr(undefined, jahre, haushaltsjahr)).toEqual({
      jahr: haushaltsjahr,
      gueltig: true,
    })
  })

  it.each(jahre)('akzeptiert das Jahr %i aus haushalt.jahre', (j) => {
    expect(leseJahr(String(j), jahre, haushaltsjahr)).toEqual({ jahr: j, gueltig: true })
  })

  // Absichtlich ungültige Eingaben: Text, Jahre außerhalb von haushalt.jahre, leer, Prototyp-Schlüssel.
  it.each(['abc', '2023', '2030', '', '__proto__', 'constructor', '2026.5', '-2026', '0x7EA'])(
    'fällt bei %j auf das Haushaltsjahr zurück und meldet die Query als ungültig',
    (roh) => {
      expect(leseJahr(roh, jahre, haushaltsjahr)).toEqual({ jahr: haushaltsjahr, gueltig: false })
    },
  )

  it('behandelt einen Schlüssel ohne Wert (?jahr) als ungültig', () => {
    expect(leseJahr(null, jahre, haushaltsjahr)).toEqual({ jahr: haushaltsjahr, gueltig: false })
  })

  it('nimmt bei einem Array das erste Element', () => {
    const [erstes, zweites] = jahre
    expect(leseJahr([String(erstes), String(zweites)], jahre, haushaltsjahr)).toEqual({
      jahr: erstes,
      gueltig: true,
    })
    expect(leseJahr(['abc', String(zweites)], jahre, haushaltsjahr)).toEqual({
      jahr: haushaltsjahr,
      gueltig: false,
    })
  })
})

describe('wertartName', () => {
  it('übersetzt die Wertarten aus der Pipeline in Anzeigenamen', () => {
    expect(wertartName('ergebnis')).toBe('Ist')
    expect(wertartName('ansatz')).toBe('Ansatz')
    expect(wertartName('planung')).toBe('Planung')
  })

  it('wirft bei einer unbekannten Wertart', () => {
    expect(() => wertartName('unbekannt')).toThrow()
    expect(() => wertartName('__proto__')).toThrow()
  })
})

describe('wertartFuerJahr', () => {
  it.each(jahre)('liefert für %i die Wertart an der Position in haushalt.wertarten', (j) => {
    expect(wertartFuerJahr(j)).toBe(haushalt.wertarten[jahre.indexOf(j)])
  })

  it('wirft für ein Jahr außerhalb von haushalt.jahre', () => {
    expect(() => wertartFuerJahr(Math.max(...jahre) + 1)).toThrow()
  })

  it('benennt jede Wertart der Daten', () => {
    for (const j of jahre) {
      expect(() => wertartName(wertartFuerJahr(j))).not.toThrow()
    }
  })
})

describe('jahrLinkFuer (D-10)', () => {
  it('ergänzt die Query um das explizit gewählte Jahr', () => {
    expect(jahrLinkFuer({ name: 'ausgaben' }, 2027)).toEqual({
      name: 'ausgaben',
      query: { jahr: '2027' },
    })
  })

  it('behält andere Query-Schlüssel des Ziels', () => {
    expect(jahrLinkFuer({ name: 'ausgaben', query: { modus: 'zuschussbedarf' } }, 2027)).toEqual({
      name: 'ausgaben',
      query: { modus: 'zuschussbedarf', jahr: '2027' },
    })
  })

  it('lässt das Ziel ohne explizites Jahr unverändert', () => {
    expect(jahrLinkFuer({ name: 'ausgaben' }, null)).toEqual({ name: 'ausgaben' })
  })

  it('lässt Textziele unverändert', () => {
    expect(jahrLinkFuer('/glossar', 2027)).toBe('/glossar')
  })
})
