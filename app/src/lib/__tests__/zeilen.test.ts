import { describe, expect, it } from 'vitest'

import { haushalt } from '@/data/daten'
import { zeilenName, zeilenNummer } from '@/lib/zeilen'

describe('zeilenName', () => {
  it('liefert für jede Ergebnisplan-Zeile einen nicht leeren Namen', () => {
    const zeilen = haushalt.ergebnisplan.GESAMT?.zeilen ?? {}
    expect(Object.keys(zeilen).length).toBeGreaterThan(0)
    for (const schluessel of Object.keys(zeilen)) {
      expect(zeilenName('ergebnisplan', schluessel).length, schluessel).toBeGreaterThan(0)
    }
  })

  it('stimmt für den Finanzplan mit zeilen_namen überein', () => {
    const eintrag = haushalt.zeilen_namen.finanzplan.find(
      (z) => z.schluessel === 'investitionszuwendungen',
    )
    expect(eintrag).toBeDefined()
    expect(zeilenName('finanzplan', 'investitionszuwendungen')).toBe(eintrag?.name)
  })

  it('wirft für unbekannte und Prototyp-Schlüssel und nennt Plan und Schlüssel', () => {
    expect(() => zeilenName('ergebnisplan', '__proto__')).toThrow(/ergebnisplan.*__proto__/)
    expect(() => zeilenName('finanzplan', 'gibt_es_nicht')).toThrow(/gibt_es_nicht/)
  })
})

describe('zeilenNummer', () => {
  it('liefert die gedruckte Zeilennummer', () => {
    const eintrag = haushalt.zeilen_namen.ergebnisplan[0]
    expect(eintrag).toBeDefined()
    if (eintrag === undefined) return
    expect(zeilenNummer('ergebnisplan', eintrag.schluessel)).toBe(eintrag.nummer)
  })

  it('wirft für unbekannte Schlüssel', () => {
    expect(() => zeilenNummer('ergebnisplan', 'constructor')).toThrow(/constructor/)
  })
})
