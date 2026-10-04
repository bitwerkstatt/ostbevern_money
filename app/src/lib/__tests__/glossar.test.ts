import { describe, expect, it } from 'vitest'

import { texte } from '@/data/daten'
import { GLOSSAR_SCHLUESSEL, ersterSatz, findeBegriff, glossarBegriffe } from '@/lib/glossar'
import { rendereAbsatz } from '@/lib/texte'

const DATEN_SCHLUESSEL = texte.glossar.map((begriff) => begriff.schluessel)

describe('GLOSSAR_SCHLUESSEL', () => {
  it('enthält genau die Schlüssel von texte.glossar (Daten -> Tupel)', () => {
    const tupel: ReadonlySet<string> = new Set(GLOSSAR_SCHLUESSEL)
    const fehlend = DATEN_SCHLUESSEL.filter((schluessel) => !tupel.has(schluessel))
    expect(fehlend).toEqual([])
  })

  it('enthält keinen Schlüssel ohne Glossarbegriff (Tupel -> Daten)', () => {
    const daten: ReadonlySet<string> = new Set(DATEN_SCHLUESSEL)
    const ueberzaehlig = GLOSSAR_SCHLUESSEL.filter((schluessel) => !daten.has(schluessel))
    expect(ueberzaehlig).toEqual([])
  })

  it('enthält keine doppelten Schlüssel', () => {
    expect(new Set(GLOSSAR_SCHLUESSEL).size).toBe(GLOSSAR_SCHLUESSEL.length)
    expect(new Set(DATEN_SCHLUESSEL).size).toBe(DATEN_SCHLUESSEL.length)
  })
})

describe('glossarBegriffe', () => {
  const begriffe = glossarBegriffe()

  it('liefert mindestens 22 Begriffe (Spez. 6.14)', () => {
    expect(begriffe.length).toBeGreaterThanOrEqual(22)
    expect(begriffe).toHaveLength(texte.glossar.length)
  })

  it('sortiert nach deutscher Kollation auf dem Begriff', () => {
    const kollator = new Intl.Collator('de')
    for (let i = 1; i < begriffe.length; i++) {
      const vorher = begriffe[i - 1]?.begriff ?? ''
      const nachher = begriffe[i]?.begriff ?? ''
      expect(kollator.compare(vorher, nachher), `${vorher} vor ${nachher}`).toBeLessThanOrEqual(0)
    }
  })

  it('stellt einen Umlaut neben seinen Grundbuchstaben (Ä wie A)', () => {
    const kollator = new Intl.Collator('de')
    // Reiner Codepunktvergleich stellte Ä hinter Z; die deutsche Kollation ordnet es bei A ein.
    expect('Äpfel' < 'Zebra').toBe(false)
    expect(kollator.compare('Äpfel', 'Zebra')).toBeLessThan(0)
    expect(kollator.compare('Äpfel', 'Birne')).toBeLessThan(0)
    expect(kollator.compare('Ärger', 'Arbeit')).toBeGreaterThan(0)
  })

  it('verändert die Eingangsdaten nicht', () => {
    const vorher = texte.glossar.map((begriff) => begriff.schluessel)
    glossarBegriffe()
    expect(texte.glossar.map((begriff) => begriff.schluessel)).toEqual(vorher)
  })
})

describe('Glossardaten (UI-SPEC E13 partial)', () => {
  it('jeder Begriff hat mindestens einen nicht leeren Absatz', () => {
    for (const begriff of texte.glossar) {
      expect(begriff.absaetze.length, begriff.schluessel).toBeGreaterThan(0)
      for (const absatz of begriff.absaetze) {
        expect(absatz.trim(), begriff.schluessel).not.toBe('')
      }
    }
  })

  it('jeder Absatz mit Platzhalter gehört zu einem Begriff mit PDF-Seitenverweis', () => {
    for (const begriff of texte.glossar) {
      const hatPlatzhalter = begriff.absaetze.some((absatz) => absatz.includes('{{'))
      if (hatPlatzhalter) {
        expect(begriff.quelle_seiten.length, begriff.schluessel).toBeGreaterThan(0)
      }
    }
  })

  it('jeder Platzhalter ist auflösbar (kein verbliebenes {{ nach dem Rendern)', () => {
    for (const begriff of texte.glossar) {
      for (const absatz of begriff.absaetze) {
        expect(rendereAbsatz(absatz), begriff.schluessel).not.toContain('{{')
      }
    }
  })
})

describe('findeBegriff', () => {
  it('findet jeden Schlüssel des Tupels', () => {
    for (const schluessel of GLOSSAR_SCHLUESSEL) {
      expect(findeBegriff(schluessel)?.schluessel).toBe(schluessel)
    }
  })

  it('liefert undefined für Unbekanntes und Prototyp-Schlüssel', () => {
    expect(findeBegriff('gibtesnicht')).toBeUndefined()
    expect(findeBegriff('constructor')).toBeUndefined()
    expect(findeBegriff('__proto__')).toBeUndefined()
  })
})

describe('ersterSatz', () => {
  it('ist für jeden Begriff nicht leer, endet mit Satzzeichen und enthält keinen Platzhalter', () => {
    for (const schluessel of GLOSSAR_SCHLUESSEL) {
      const satz = ersterSatz(schluessel)
      expect(satz, schluessel).not.toBe('')
      expect(satz, schluessel).toMatch(/[.!?]$/)
      expect(satz, schluessel).not.toContain('{{')
    }
  })

  it('ist der erste Satz des ersten Absatzes und nicht länger als dieser', () => {
    for (const schluessel of GLOSSAR_SCHLUESSEL) {
      const erster = rendereAbsatz(findeBegriff(schluessel)?.absaetze[0] ?? '')
      expect(erster.startsWith(ersterSatz(schluessel)), schluessel).toBe(true)
    }
  })
})
