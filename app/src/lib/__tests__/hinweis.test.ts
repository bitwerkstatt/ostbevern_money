import { describe, expect, it } from 'vitest'

import { texte } from '@/data/daten'
import { GLOSSAR_SCHLUESSEL } from '@/lib/glossar'
import { findeText } from '@/lib/texte'

// Strukturprüfung der Hinweisbox „Was nicht im Haushalt steht“ (UI-04, D-18). Die Quelltexte
// kommen wie in `quelltext.test.ts` über `import.meta.glob` mit `?raw`.
const quelltexte = import.meta.glob<string>('/src/**/*.vue', {
  query: '?raw',
  import: 'default',
  eager: true,
})

const KOMPONENTE = '/src/components/HinweisNichtImHaushalt.vue'

function quelltext(pfad: string): string {
  const text = quelltexte[pfad]
  if (text === undefined) {
    throw new Error(`${pfad} nicht gefunden`)
  }
  return text
}

/** Der Inhalt zwischen dem ersten `<template>` und dem letzten `</template>`. */
function templateTeil(text: string): string {
  const anfang = text.search(/^<template>/m)
  const ende = text.lastIndexOf('</template>')
  if (anfang === -1 || ende === -1 || ende <= anfang) {
    return ''
  }
  return text.slice(anfang + '<template>'.length, ende)
}

/** Der Inhalt des `<script setup>`-Blocks. */
function scriptTeil(text: string): string {
  const treffer = /<script setup[^>]*>([\s\S]*?)<\/script>/.exec(text)
  return treffer?.[1] ?? ''
}

describe('HinweisNichtImHaushalt auf /einnahmen und in der Kurzform (UI-04, D-18)', () => {
  it('EinnahmenPage bindet die Hinweisbox mit variante="einnahmen" ein', () => {
    const seite = quelltext('/src/pages/EinnahmenPage.vue')
    expect(seite).toContain('<HinweisNichtImHaushalt')
    expect(seite).toContain('variante="einnahmen"')
  })

  it('EinnahmenPage setzt die Hinweisbox hinter den Abschnitt Investive Einnahmen', () => {
    const template = templateTeil(quelltext('/src/pages/EinnahmenPage.vue'))
    expect(template.indexOf('<HinweisNichtImHaushalt')).toBeGreaterThan(
      template.indexOf('Investive Einnahmen'),
    )
  })

  it('die Komponente trägt die drei Leitsätze wörtlich', () => {
    const komponente = quelltext(KOMPONENTE)
    expect(komponente).toContain(
      'Nicht alles, was in Ostbevern Geld kostet, steht in diesem Haushalt. Das Hallenbad führt die BBO in eigenen Büchern. Im Haushalt siehst du nur die Verlustübernahme.',
    )
    expect(komponente).toContain(
      'Abwassergebühren findest du hier nicht. Die Abwasserentsorgung führt der TEO AöR in eigenen Büchern.',
    )
    expect(komponente).toContain(
      'Das Hallenbad (BBO) und die Abwasserentsorgung (TEO AöR) führen eigene Bücher und stehen nicht in diesem Haushalt.',
    )
  })

  it('die Kurzform verlinkt auf den Glossaranker nicht_im_haushalt', () => {
    const komponente = quelltext(KOMPONENTE)
    expect(komponente).toContain('#nicht_im_haushalt')
    expect(komponente).toContain('Mehr dazu im Glossar')
  })

  it('der Aufklapper „Was sind BBO und TEO?“ hängt am vorhandenen Pipeline-Text', () => {
    const komponente = quelltext(KOMPONENTE)
    expect(komponente).toContain('Was sind BBO und TEO?')
    expect(komponente).toContain("findeText('nicht_im_haushalt')")
  })
})

describe('HinweisNichtImHaushalt auf /rat-entscheidet (UI-04, D-18)', () => {
  const SEITE = '/src/pages/RatEntscheidetPage.vue'

  it('RatEntscheidetPage bindet die Hinweisbox mit variante="kurz" ein', () => {
    const seite = quelltext(SEITE)
    expect(seite).toContain('<HinweisNichtImHaushalt')
    expect(seite).toContain('variante="kurz"')
  })

  it('die Kurzform steht als letztes Element der Seite, hinter den Einzelzuschüssen', () => {
    const template = templateTeil(quelltext(SEITE))
    expect(template.indexOf('<ZuschussListe')).toBeGreaterThan(-1)
    expect(template.indexOf('<HinweisNichtImHaushalt')).toBeGreaterThan(
      template.indexOf('<ZuschussListe'),
    )
  })

  it('der Block „Was der Rat nicht beeinflussen kann“ steht vor den Einzelzuschüssen', () => {
    const template = templateTeil(quelltext(SEITE))
    expect(template.indexOf('<NichtBeeinflussbarBlock')).toBeGreaterThan(-1)
    expect(template.indexOf('<NichtBeeinflussbarBlock')).toBeLessThan(
      template.indexOf('<ZuschussListe'),
    )
  })
})

describe('HinweisNichtImHaushalt auf /ausgaben (UI-04, D-18)', () => {
  it('AusgabenPage bindet die Hinweisbox mit variante="ausgaben" ein', () => {
    const seite = quelltext('/src/pages/AusgabenPage.vue')
    expect(seite).toContain('<HinweisNichtImHaushalt')
    expect(seite).toContain('variante="ausgaben"')
  })

  it('der Pipeline-Text nicht_im_haushalt existiert und nennt mindestens eine PDF-Seite', () => {
    const text = findeText('nicht_im_haushalt')
    expect(text).toBeDefined()
    expect(text?.quelle_seiten.length ?? 0).toBeGreaterThan(0)
  })

  it('die Komponente trägt die Überschrift und zieht den Pipeline-Text über ErklaerText', () => {
    const komponente = quelltext(KOMPONENTE)
    expect(komponente).toContain('Was nicht im Haushalt steht')
    expect(komponente).toContain('schluessel="nicht_im_haushalt"')
  })

  it('der Text im Template der Komponente enthält keine Ziffer (UI-05, T-06-08)', () => {
    // Ohne Markup: Tag-Namen wie `h2` tragen Ziffern, sind aber keine Zahlen im Text.
    const text = templateTeil(quelltext(KOMPONENTE)).replace(/<[^>]*>/g, '')
    expect(text.trim().length).toBeGreaterThan(0)
    expect(text).not.toMatch(/\d/)
  })

  it('die Leitsätze im Skript enthalten keine Ziffer (UI-05, T-06-08)', () => {
    const saetze = [...scriptTeil(quelltext(KOMPONENTE)).matchAll(/'([^'\n]*\s[^'\n]*)'/g)].map(
      (treffer) => treffer[1] ?? '',
    )
    expect(saetze.length).toBeGreaterThan(0)
    expect(saetze.filter((satz) => /\d/.test(satz))).toEqual([])
  })
})

describe('Glossaranker nicht_im_haushalt (UI-04, D-18)', () => {
  it('steht im Tupel GLOSSAR_SCHLUESSEL', () => {
    const bekannt: readonly string[] = GLOSSAR_SCHLUESSEL
    expect(bekannt).toContain('nicht_im_haushalt')
  })

  it('steht als Begriff in texte.glossar und nennt mindestens eine PDF-Seite', () => {
    const begriff = texte.glossar.find((eintrag) => eintrag.schluessel === 'nicht_im_haushalt')
    expect(begriff).toBeDefined()
    expect(begriff?.quelle_seiten.length ?? 0).toBeGreaterThan(0)
  })

  it('die Kurzform und die langen Varianten der Seiten verlinken denselben Anker', () => {
    // Die drei Platzierungen (ausgaben, einnahmen, kurz) teilen sich eine Komponente und damit
    // einen Anker; die Seitenprüfungen oben belegen die Platzierung je Seite.
    const plaetze = [
      ['/src/pages/AusgabenPage.vue', 'variante="ausgaben"'],
      ['/src/pages/EinnahmenPage.vue', 'variante="einnahmen"'],
      ['/src/pages/RatEntscheidetPage.vue', 'variante="kurz"'],
    ] as const
    for (const [pfad, variante] of plaetze) {
      const seite = quelltext(pfad)
      expect(seite, pfad).toContain('<HinweisNichtImHaushalt')
      expect(seite, pfad).toContain(variante)
    }
    expect(quelltext(KOMPONENTE)).toContain('#nicht_im_haushalt')
  })
})
