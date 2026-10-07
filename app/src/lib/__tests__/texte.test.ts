import { describe, expect, it } from 'vitest'

import { formatiere } from '@/charts/format'
import { haushalt, texte } from '@/data/daten'
import { findeText, istJahrneutral, rendereAbsatz, textFuerJahr } from '@/lib/texte'

describe('rendereAbsatz', () => {
  it('ersetzt einen Platzhalter durch den formatierten Wert', () => {
    expect(rendereAbsatz('X {{a.b|mio}} Y', { 'a.b': 27502063 })).toBe(
      `X ${formatiere(27502063, 'mio')} Y`,
    )
    expect(rendereAbsatz('X {{a.b|mio}} Y', { 'a.b': 27502063 })).toBe('X 27,5 Mio. € Y')
  })

  it('ersetzt mehrere Platzhalter mit unterschiedlichen Kürzeln', () => {
    const werte = { a: 2026, b: 554 }
    expect(rendereAbsatz('{{a|jahr}}: {{b|prozent}}', werte)).toBe(
      `${formatiere(2026, 'jahr')}: ${formatiere(554, 'prozent')}`,
    )
  })

  it('zeigt einen Gedankenstrich, wenn der Schlüssel in werte fehlt', () => {
    expect(rendereAbsatz('X {{fehlt|euro}} Y', {})).toBe('X – Y')
  })

  it('vertraut keinen Prototyp-Schlüsseln', () => {
    expect(rendereAbsatz('{{constructor|zahl}}', {})).toBe('–')
    expect(rendereAbsatz('{{__proto__|zahl}}', {})).toBe('–')
  })

  it('wirft bei unbekanntem Formatkürzel und nennt es', () => {
    expect(() => rendereAbsatz('{{a|nix}}', { a: 1 })).toThrow(/nix/)
  })

  it('lässt Text ohne Platzhalter unverändert', () => {
    expect(rendereAbsatz('Nur Text.', {})).toBe('Nur Text.')
  })

  it('liefert reinen Text: Markup im Absatz bleibt unverändert (keine HTML-Auswertung)', () => {
    expect(rendereAbsatz('<b>{{a|zahl}}</b>', { a: 5 })).toBe('<b>5</b>')
  })
})

describe('Texte aus texte.json', () => {
  it('rendert jeden Absatz jedes Textes ohne Platzhalterrest, NaN, undefined oder Infinity', () => {
    expect(texte.texte.length).toBeGreaterThan(0)
    for (const text of texte.texte) {
      for (const absatz of text.absaetze) {
        const gerendert = rendereAbsatz(absatz)
        expect(gerendert, text.schluessel).not.toContain('{{')
        expect(gerendert, text.schluessel).not.toContain('}}')
        expect(gerendert, text.schluessel).not.toContain('NaN')
        expect(gerendert, text.schluessel).not.toContain('undefined')
        expect(gerendert, text.schluessel).not.toContain('Infinity')
      }
    }
  })

  it('nennt zu jedem Text mindestens eine PDF-Seite', () => {
    for (const text of texte.texte) {
      expect(text.quelle_seiten.length, text.schluessel).toBeGreaterThan(0)
    }
  })
})

describe('findeText', () => {
  it('findet einen vorhandenen Text', () => {
    const erster = texte.texte[0]
    expect(erster).toBeDefined()
    if (erster === undefined) return
    expect(findeText(erster.schluessel)).toBe(erster)
  })

  it('liefert undefined für unbekannte und Prototyp-Schlüssel', () => {
    expect(findeText('__proto__')).toBeUndefined()
    expect(findeText('constructor')).toBeUndefined()
    expect(findeText('gibt_es_nicht')).toBeUndefined()
  })
})

describe('textFuerJahr', () => {
  const mitPlatzhalter = texte.texte.find((t) => !istJahrneutral(t))
  const andereJahre = haushalt.jahre.filter((j) => j !== texte.haushaltsjahr)

  it('gibt einen Text mit Platzhaltern für das Haushaltsjahr zurück', () => {
    expect(mitPlatzhalter).toBeDefined()
    if (mitPlatzhalter === undefined) return
    expect(textFuerJahr(mitPlatzhalter.schluessel, texte.haushaltsjahr)).toBe(mitPlatzhalter)
  })

  it('gibt einen Text mit Platzhaltern für jedes andere Jahr nicht zurück (Pitfall 6)', () => {
    expect(andereJahre.length).toBeGreaterThan(0)
    for (const text of texte.texte.filter((t) => !istJahrneutral(t))) {
      for (const jahr of andereJahre) {
        expect(textFuerJahr(text.schluessel, jahr), `${text.schluessel} ${jahr}`).toBeNull()
      }
    }
  })

  it('gibt einen jahrneutralen Text für jedes Jahr zurück', () => {
    const neutral = texte.texte.find((t) => istJahrneutral(t))
    if (neutral === undefined) {
      // Der aktuelle Datenbestand enthält nur Texte mit Platzhaltern; die Jahrneutralität
      // wird dann über die Funktion selbst geprüft.
      expect(
        istJahrneutral({ schluessel: 'x', titel: 'x', quelle_seiten: [1], absaetze: ['a'] }),
      ).toBe(true)
      return
    }
    for (const jahr of haushalt.jahre) {
      expect(textFuerJahr(neutral.schluessel, jahr)).toBe(neutral)
    }
  })

  it('gibt null für einen unbekannten Schlüssel zurück', () => {
    expect(textFuerJahr('gibt_es_nicht', texte.haushaltsjahr)).toBeNull()
  })
})

describe('istJahrneutral', () => {
  it('erkennt Platzhalter in irgendeinem Absatz', () => {
    expect(
      istJahrneutral({
        schluessel: 'a',
        titel: 'a',
        quelle_seiten: [1],
        absaetze: ['x', 'y {{k|zahl}}'],
      }),
    ).toBe(false)
    expect(
      istJahrneutral({ schluessel: 'a', titel: 'a', quelle_seiten: [1], absaetze: ['x', 'y'] }),
    ).toBe(true)
  })

  it('ignoriert jahr.*-Platzhalter: nur feste Jahre machen den Text nicht jahrgebunden', () => {
    expect(
      istJahrneutral({
        schluessel: 'a',
        titel: 'a',
        quelle_seiten: [1],
        absaetze: ['Von {{jahr.fest_2020|jahr}} bis {{jahr.fest_2024|jahr}}.'],
      }),
    ).toBe(true)
  })

  it('bindet einen Text an das Haushaltsjahr, sobald ein Betrags-Platzhalter vorkommt', () => {
    expect(
      istJahrneutral({
        schluessel: 'a',
        titel: 'a',
        quelle_seiten: [1],
        absaetze: ['Im Jahr {{jahr.fest_2020|jahr}} waren es {{a.b|mio}}.'],
      }),
    ).toBe(false)
  })

  it('hält ueberschuss_ruecklage für jedes Jahr sichtbar (jahr.fest_*-Platzhalter)', () => {
    expect(findeText('ueberschuss_ruecklage')).toBeDefined()
    for (const jahr of haushalt.jahre) {
      expect(textFuerJahr('ueberschuss_ruecklage', jahr), `${jahr}`).not.toBeNull()
    }
  })

  it('hält ueberschuss_pb_11 für jedes Jahr sichtbar (jahr.fest_*-Platzhalter)', () => {
    expect(findeText('ueberschuss_pb_11')).toBeDefined()
    for (const jahr of haushalt.jahre) {
      expect(textFuerJahr('ueberschuss_pb_11', jahr), `${jahr}`).not.toBeNull()
    }
  })

  it('jahrneutrale Texte nennen nur feste Jahre (jahr.fest_*), nie relative Schlüssel (D-04)', () => {
    const neutrale = texte.texte.filter((t) => istJahrneutral(t))
    expect(neutrale.length).toBeGreaterThan(0)
    for (const text of neutrale) {
      for (const absatz of text.absaetze) {
        for (const treffer of absatz.matchAll(/\{\{([a-z0-9_.]+)\|[a-z]+\}\}/g)) {
          expect(treffer[1], text.schluessel).toMatch(/^jahr\.fest_/)
        }
      }
    }
  })
})
