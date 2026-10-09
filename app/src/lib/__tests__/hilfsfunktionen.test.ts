import { describe, expect, it } from 'vitest'

import { texte } from '@/data/daten'
import { seitenText } from '@/lib/hilfsfunktionen'

// G-09-02: „PDF-Seite“ steht im Singular nur bei genau einer Seite, sonst „PDF-Seiten“.

describe('seitenText', () => {
  it('G-09-02: PDF-Seite im Singular nur bei genau einer Seite', () => {
    expect(seitenText([12])).toBe('PDF-Seite 12')
    expect(seitenText([12, 13])).toBe('PDF-Seiten 12, 13')
    expect(seitenText([46, 47, 48])).toBe('PDF-Seiten 46, 47, 48')
  })

  it('G-09-02: ohne Seite entsteht kein Text', () => {
    expect(seitenText([])).toBe('')
  })

  it('G-09-02: kein Erklärtext aus texte.json steht mit mehreren Seiten im Singular', () => {
    expect(texte.texte.length).toBeGreaterThan(0)
    for (const text of texte.texte) {
      const zeile = seitenText(text.quelle_seiten)
      const erwartet =
        text.quelle_seiten.length === 1 ? /^PDF-Seite \d+$/ : /^PDF-Seiten \d+(, \d+)+$/
      expect(zeile, text.schluessel).toMatch(erwartet)
    }
  })
})
