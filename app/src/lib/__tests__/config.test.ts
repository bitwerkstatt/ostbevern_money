import { readFileSync } from 'node:fs'

import { describe, expect, it } from 'vitest'

import { KONTAKT_EMAIL, ORIGINAL_PDF_URL, istPlatzhalter } from '@/config'

describe('istPlatzhalter (UI-03, D-17)', () => {
  it.each([
    'kontakt-noch-nicht-festgelegt@example.invalid',
    'https://haushaltsplan-noch-nicht-festgelegt.invalid/',
    'https://haushaltsplan.INVALID/pfad.pdf',
    'Name@Beispiel.Invalid',
  ])('erkennt %s als Platzhalter', (wert) => {
    expect(istPlatzhalter(wert)).toBe(true)
  })

  it.each([
    'kontakt@beispiel.de',
    'https://www.ostbevern.de/haushalt.pdf',
    'https://invalid.example.org/plan.pdf',
    'kontakt@invalid.de',
  ])('lässt %s als echten Wert gelten', (wert) => {
    expect(istPlatzhalter(wert)).toBe(false)
  })

  it('behandelt leere oder unlesbare Werte als Platzhalter', () => {
    expect(istPlatzhalter('')).toBe(true)
    expect(istPlatzhalter('   ')).toBe(true)
    expect(istPlatzhalter('kein-ziel')).toBe(true)
  })
})

describe('Konfiguration', () => {
  it('liefert eine gültige E-Mail-Adresse und eine https-URL', () => {
    expect(KONTAKT_EMAIL).toMatch(/^[^@\s]+@[^@\s]+$/)
    expect(ORIGINAL_PDF_URL).toMatch(/^https:\/\//)
  })
})

describe('App.vue (Fußzeile, D-17, D-18)', () => {
  const quelle = readFileSync(new URL('../../App.vue', import.meta.url), 'utf8')

  it('liest Kontakt und PDF-URL aus der Konfiguration, ohne sie fest einzutragen', () => {
    expect(quelle).toContain('KONTAKT_EMAIL')
    expect(quelle).toContain('ORIGINAL_PDF_URL')
    expect(quelle).not.toMatch(/@[a-z0-9.-]+\.(de|com|org|invalid)/i)
    expect(quelle).not.toContain(KONTAKT_EMAIL)
    expect(quelle).not.toContain(ORIGINAL_PDF_URL)
  })

  it('zeigt alle vier Fußzeilen-Zeilen ohne Build-Datum', () => {
    expect(quelle).toContain('Datenstand: Haushalt')
    expect(quelle).toContain('Original-Haushaltsplan (PDF) der Gemeinde Ostbevern')
    expect(quelle).toContain(
      'Inoffizielles Projekt, keine Veröffentlichung der Gemeinde Ostbevern.',
    )
    expect(quelle).toContain('Kontakt:')
    expect(quelle).toContain('Inspiriert von')
    expect(quelle).not.toMatch(/build|Stand vom/i)
  })

  it('stellt das Projekt nie als offizielle Veröffentlichung der Gemeinde dar', () => {
    expect(quelle).not.toMatch(/offizielle[rs]? (Seite|Angebot|Veröffentlichung|Website)/i)
  })

  it('öffnet jeden externen Link mit noopener noreferrer und Hinweis auf den neuen Tab', () => {
    const externe = quelle.match(/target="_blank"/g) ?? []
    const gesichert = quelle.match(/rel="noopener noreferrer"/g) ?? []
    const hinweise = quelle.match(/\(öffnet in neuem Tab\)/g) ?? []
    expect(externe.length).toBeGreaterThan(0)
    expect(gesichert.length).toBe(externe.length)
    expect(hinweise.length).toBe(externe.length)
  })
})
