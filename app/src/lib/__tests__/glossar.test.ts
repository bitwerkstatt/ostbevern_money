import { describe, expect, it } from 'vitest'

import { haushalt, produkte, texte } from '@/data/daten'
import {
  GLOSSAR_SCHLUESSEL,
  ersterSatz,
  findeBegriff,
  glossarBegriffe,
  glossarVerwendungen,
  produktGruppen,
} from '@/lib/glossar'
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

describe('produktGruppen', () => {
  const gruppen = produktGruppen()
  const pbKnoten = haushalt.knoten.filter((k) => k.eltern === 'GESAMT')

  it('zeigt jedes Produkt genau einmal', () => {
    const codes = gruppen.flatMap((gruppe) => gruppe.produkte.map((produkt) => produkt.code))
    expect(codes).toHaveLength(produkte.length)
    expect(new Set(codes).size).toBe(produkte.length)
    expect([...codes].sort()).toEqual(produkte.map((produkt) => produkt.code).sort())
  })

  it('bildet eine Gruppe je verschiedenem Produktbereich der Produkte', () => {
    const verschiedene = new Set(produkte.map((produkt) => produkt.pb))
    expect(gruppen).toHaveLength(verschiedene.size)
    expect(new Set(gruppen.map((gruppe) => gruppe.pb))).toEqual(verschiedene)
  })

  it('enthält keine leere Gruppe (ein Bereich ohne Produkte erscheint nicht)', () => {
    for (const gruppe of gruppen) {
      expect(gruppe.produkte.length, gruppe.pb).toBeGreaterThan(0)
    }
    const mitProdukten = new Set(produkte.map((produkt) => produkt.pb))
    const ohneProdukte = pbKnoten.filter((k) => !mitProdukten.has(k.code))
    for (const knoten of ohneProdukte) {
      expect(
        gruppen.some((gruppe) => gruppe.pb === knoten.code),
        knoten.code,
      ).toBe(false)
    }
  })

  it('folgt der Reihenfolge der Produktbereiche und nennt sie wie die Hierarchie', () => {
    const erwartet = pbKnoten
      .filter((k) => produkte.some((produkt) => produkt.pb === k.code))
      .map((k) => k.code)
    expect(gruppen.map((gruppe) => gruppe.pb)).toEqual(erwartet)
    for (const gruppe of gruppen) {
      expect(gruppe.name, gruppe.pb).toBe(pbKnoten.find((k) => k.code === gruppe.pb)?.name)
    }
  })

  it('ordnet jedes Produkt der Gruppe seines Produktbereichs zu', () => {
    for (const gruppe of gruppen) {
      for (const produkt of gruppe.produkte) {
        expect(produkt.pb).toBe(gruppe.pb)
      }
    }
  })
})

describe('glossarVerwendungen', () => {
  it('liest den Schlüssel einer Verwendung, auch über mehrere Zeilen', () => {
    expect(
      glossarVerwendungen('<GlossarBegriff schluessel="hebesatz">Hebesatz</GlossarBegriff>'),
    ).toEqual(['hebesatz'])
    expect(
      glossarVerwendungen('<GlossarBegriff\n  class="x"\n  schluessel="kreisumlage"\n/>'),
    ).toEqual(['kreisumlage'])
  })

  it('findet mehrere Verwendungen und ignoriert andere Komponenten', () => {
    const quelltext = `
      <GlossarBegriff schluessel="hebesatz" />
      <GlossarListe />
      <p>Text <GlossarBegriff schluessel="nkf">NKF</GlossarBegriff></p>`
    expect(glossarVerwendungen(quelltext)).toEqual(['hebesatz', 'nkf'])
  })

  it('liefert nichts ohne Verwendung', () => {
    expect(glossarVerwendungen('<p>kein Begriff</p>')).toEqual([])
  })
})

describe('Verwendungsprüfung aller .vue-Dateien (D-16, GLOS-03)', () => {
  // Warum Quelltext: Geprüft wird die Glossarverlinkung, also welche `GlossarBegriff`-Schlüssel die
  // Templates der Seiten verwenden. Ohne DOM in der Testumgebung (`environment: 'node'`) und ohne
  // DOM-Paket lässt sich das nicht an der gerenderten Seite prüfen, nur am Quelltext (D-14).
  const quelltexte = import.meta.glob<string>('/src/**/*.vue', {
    query: '?raw',
    import: 'default',
    eager: true,
  })
  const erlaubt: ReadonlySet<string> = new Set(GLOSSAR_SCHLUESSEL)

  it('sieht die Vue-Dateien der App', () => {
    expect(Object.keys(quelltexte).length).toBeGreaterThan(0)
  })

  it('verwendet GlossarBegriff nur mit bekannten Schlüsseln', () => {
    const unbekannt: string[] = []
    for (const [datei, quelltext] of Object.entries(quelltexte)) {
      for (const schluessel of glossarVerwendungen(quelltext)) {
        if (!erlaubt.has(schluessel)) {
          unbekannt.push(`${datei}: ${schluessel}`)
        }
      }
    }
    expect(unbekannt).toEqual([])
  })

  it('schlägt bei einem untergeschobenen unbekannten Schlüssel an', () => {
    const probe = '<GlossarBegriff schluessel="gibtesnicht">x</GlossarBegriff>'
    const unbekannt = glossarVerwendungen(probe).filter((schluessel) => !erlaubt.has(schluessel))
    expect(unbekannt).toEqual(['gibtesnicht'])
  })
})
