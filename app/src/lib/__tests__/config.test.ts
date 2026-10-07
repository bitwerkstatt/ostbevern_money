import { readFileSync } from 'node:fs'

import { describe, expect, it } from 'vitest'

import {
  IMPRESSUM_ANSCHRIFT,
  IMPRESSUM_NAME,
  KONTAKT_EMAIL,
  ORIGINAL_PDF_URL,
  istAnschriftPlatzhalter,
  istImpressumPlatzhalter,
  istPlatzhalter,
} from '@/config'

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

describe('Konfiguration (D-06, D-07)', () => {
  it('setzt die Kontaktadresse aus D-07', () => {
    expect(KONTAKT_EMAIL).toBe('mail@thomas-manthey.de')
    expect(KONTAKT_EMAIL).toMatch(/^[^@\s]+@[^@\s]+$/)
  })

  it('verweist auf die offizielle PDF-Datei der Gemeinde (D-06)', () => {
    expect(ORIGINAL_PDF_URL.startsWith('https://www.ostbevern.de/')).toBe(true)
    expect(ORIGINAL_PDF_URL.endsWith('.pdf')).toBe(true)
  })

  it('hält weder die Kontaktadresse noch die PDF-URL für einen Platzhalter', () => {
    expect(istPlatzhalter(KONTAKT_EMAIL)).toBe(false)
    expect(istPlatzhalter(ORIGINAL_PDF_URL)).toBe(false)
  })
})

describe('istImpressumPlatzhalter (E4, D-08)', () => {
  it.each(['', '   ', 'name-noch-nicht-festgelegt.invalid', 'Name.INVALID'])(
    'erkennt %j als Platzhalter',
    (wert) => {
      expect(istImpressumPlatzhalter(wert)).toBe(true)
    },
  )

  it.each(['Erika Musterfrau', 'Hauptstraße 1', '59227 Ostbevern'])(
    'lässt %j als echten Wert gelten',
    (wert) => {
      expect(istImpressumPlatzhalter(wert)).toBe(false)
    },
  )
})

describe('istAnschriftPlatzhalter (E4 partial, zero-one-many)', () => {
  it('erkennt eine leere Anschrift als Platzhalter', () => {
    expect(istAnschriftPlatzhalter([])).toBe(true)
  })

  it('erkennt eine halb gefüllte Anschrift als Platzhalter', () => {
    expect(
      istAnschriftPlatzhalter(['Hauptstraße 1', 'anschrift-noch-nicht-festgelegt.invalid']),
    ).toBe(true)
    expect(istAnschriftPlatzhalter(['Hauptstraße 1', ''])).toBe(true)
  })

  it('lässt eine vollständige Anschrift mit einer oder mehreren Zeilen gelten', () => {
    expect(istAnschriftPlatzhalter(['Hauptstraße 1'])).toBe(false)
    expect(istAnschriftPlatzhalter(['Hauptstraße 1', '59227 Ostbevern'])).toBe(false)
  })
})

describe('veröffentlichungsbereit (E4, D-07, D-08, T-07-23)', () => {
  it('hält keine der vier Konfigurationswerte für einen Platzhalter', () => {
    expect(istPlatzhalter(KONTAKT_EMAIL)).toBe(false)
    expect(istPlatzhalter(ORIGINAL_PDF_URL)).toBe(false)
    expect(istImpressumPlatzhalter(IMPRESSUM_NAME)).toBe(false)
    expect(istAnschriftPlatzhalter(IMPRESSUM_ANSCHRIFT)).toBe(false)
  })

  it('führt mindestens eine Anschriftzeile und keine leere Zeile', () => {
    expect(IMPRESSUM_ANSCHRIFT.length).toBeGreaterThan(0)
    for (const zeile of IMPRESSUM_ANSCHRIFT) {
      expect(istImpressumPlatzhalter(zeile)).toBe(false)
    }
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

  it('zeigt alle fünf Fußzeilen-Zeilen ohne Build-Datum', () => {
    expect(quelle).toContain('Datenstand: Haushalt')
    expect(quelle).toContain('Original-Haushaltsplan (PDF) der Gemeinde Ostbevern')
    expect(quelle).toContain(
      'Inoffizielles Projekt, keine Veröffentlichung der Gemeinde Ostbevern.',
    )
    expect(quelle).toContain('Kontakt:')
    expect(quelle).toContain('Über dieses Projekt, Impressum und Datenschutz')
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

describe('App.vue (Fußzeilenlink auf Über dieses Projekt, D-08)', () => {
  const quelle = readFileSync(new URL('../../App.vue', import.meta.url), 'utf8')

  it('verlinkt die Seite ueber per RouterLink auf den benannten Pfad', () => {
    expect(quelle).toMatch(/<RouterLink\s+:to="\{ name: 'ueber' \}"/)
  })

  it('setzt den Link zwischen die Kontaktzeile und „Inspiriert von“', () => {
    const kontakt = quelle.indexOf('Kontakt:')
    const ueber = quelle.indexOf('Über dieses Projekt, Impressum und Datenschutz')
    const inspiriert = quelle.indexOf('Inspiriert von')
    expect(kontakt).toBeGreaterThan(-1)
    expect(ueber).toBeGreaterThan(kontakt)
    expect(inspiriert).toBeGreaterThan(ueber)
  })
})

describe('UeberPage.vue (Über dieses Projekt, D-08, T-07-14, T-07-16)', () => {
  const quelle = readFileSync(new URL('../../pages/UeberPage.vue', import.meta.url), 'utf8')

  it('liest Name, Anschrift, Kontakt und PDF-URL aus der Konfiguration', () => {
    expect(quelle).toContain('IMPRESSUM_NAME')
    expect(quelle).toContain('IMPRESSUM_ANSCHRIFT')
    expect(quelle).toContain('KONTAKT_EMAIL')
    expect(quelle).toContain('ORIGINAL_PDF_URL')
  })

  it('trägt weder die Kontaktadresse noch die PDF-URL fest ein', () => {
    expect(quelle).not.toContain(KONTAKT_EMAIL)
    expect(quelle).not.toContain(ORIGINAL_PDF_URL)
    expect(quelle).not.toMatch(/@[a-z0-9.-]+\.(de|com|org|invalid)/i)
  })

  it('stellt das Projekt nie als offizielle Veröffentlichung der Gemeinde dar', () => {
    expect(quelle).not.toMatch(/offizielle[rs]? (Seite|Angebot|Veröffentlichung|Website)/i)
    expect(quelle).toContain('Ein inoffizielles Projekt')
  })

  it('führt die vier Abschnitte in der Reihenfolge von D-08', () => {
    const stellen = [
      'Ein inoffizielles Projekt',
      'Dank und Informationen',
      'Impressum',
      'Datenschutz',
    ].map((titel) => quelle.indexOf(`>${titel}</h2>`))
    for (const stelle of stellen) {
      expect(stelle).toBeGreaterThan(-1)
    }
    expect([...stellen].sort((a, b) => a - b)).toEqual(stellen)
  })

  it('nennt die Datenschutzaussage von D-08', () => {
    // Prettier bricht den Fließtext um; der Vergleich ignoriert Zeilenumbrüche und Einrückung.
    expect(quelle.replace(/\s+/g, ' ')).toContain(
      'Diese Seite setzt keine Cookies und verwendet kein Tracking. Beim Aufruf werden keine Daten an Drittanbieter geschickt. Die Seite wird bei GitHub Pages gehostet.',
    )
  })

  it('nennt die IP-Verarbeitung durch GitHub Pages (Abnahme 07-10)', () => {
    expect(quelle.replace(/\s+/g, ' ')).toContain(
      'Beim Aufruf verarbeitet GitHub Pages technisch bedingt deine IP-Adresse; mehr dazu in der Datenschutzerklärung von GitHub.',
    )
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
