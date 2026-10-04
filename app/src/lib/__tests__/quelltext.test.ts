import { describe, expect, it } from 'vitest'

import { GLOSSAR_SCHLUESSEL, glossarVerwendungen } from '@/lib/glossar'

// Quelltext-Prüfungen über alle Vue-Dateien der App (GLOS-03, UI-05). Die Quelltexte kommen
// wie in `glossar.test.ts` über `import.meta.glob` mit `?raw`.
const quelltexte = import.meta.glob<string>('/src/**/*.vue', {
  query: '?raw',
  import: 'default',
  eager: true,
})

/** Die fünf Inhaltsseiten, auf denen Glossarbegriffe im Fließtext verlinkt sein müssen (D-16). */
const INHALTSSEITEN = [
  'StartPage',
  'EinnahmenPage',
  'AusgabenPage',
  'GeldflussPage',
  'ProduktPage',
] as const

/** Schlüssel, die zusammen auf den Inhaltsseiten verlinkt sein müssen (GLOS-03, D-16). */
const PFLICHT_SCHLUESSEL = [
  'ergebnisplan',
  'finanzplan',
  'ertrag_aufwand',
  'hebesatz',
  'schluesselzuweisung',
  'sonderposten',
  'zuschussbedarf',
  'transferaufwendungen',
  'abschreibungen',
  'kreisumlage',
  'globaler_minderaufwand',
  'bindungsgrad',
  'produkt',
] as const

/** Der Inhalt zwischen dem ersten `<template>` und dem letzten `</template>` einer Vue-Datei. */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
function templateTeil(quelltext: string): string {
  return ''
}

/** Die Fundstellen getippter Zahlen oder der Roh-HTML-Direktive im Template (UI-05, T-05-40/41). */
// eslint-disable-next-line @typescript-eslint/no-unused-vars
function getippteZahlen(template: string): string[] {
  return []
}

function seitenQuelltext(seite: string): string {
  const quelltext = quelltexte[`/src/pages/${seite}.vue`]
  if (quelltext === undefined) {
    throw new Error(`Seite ${seite}.vue nicht gefunden`)
  }
  return quelltext
}

describe('Glossarverlinkung auf den Inhaltsseiten (GLOS-03, D-16)', () => {
  it.each(INHALTSSEITEN)('%s enthält mindestens einen GlossarBegriff im Fließtext', (seite) => {
    expect(glossarVerwendungen(seitenQuelltext(seite)).length).toBeGreaterThan(0)
  })

  it('verlinkt über alle Inhaltsseiten die Pflichtbegriffe', () => {
    const verwendet = new Set(
      INHALTSSEITEN.flatMap((seite) => glossarVerwendungen(seitenQuelltext(seite))),
    )
    const fehlend = PFLICHT_SCHLUESSEL.filter((schluessel) => !verwendet.has(schluessel))
    expect(fehlend).toEqual([])
  })

  it('kennt jeden Pflichtbegriff im Glossar (kein Tippfehler in der Liste)', () => {
    const bekannt: ReadonlySet<string> = new Set(GLOSSAR_SCHLUESSEL)
    expect(PFLICHT_SCHLUESSEL.filter((schluessel) => !bekannt.has(schluessel))).toEqual([])
  })
})

describe('templateTeil', () => {
  it('liefert den Inhalt zwischen erstem <template> und letztem </template>', () => {
    const quelltext = [
      '<script setup lang="ts">',
      'const x = 1',
      '</script>',
      '',
      '<template>',
      '  <p>Hallo</p>',
      '  <template v-if="x"><b>innen</b></template>',
      '</template>',
      '',
      '<style scoped>',
      '.a { width: 50%; }',
      '</style>',
    ].join('\n')
    const teil = templateTeil(quelltext)
    expect(teil).toContain('<p>Hallo</p>')
    expect(teil).toContain('<b>innen</b>')
    expect(teil).not.toContain('const x')
    expect(teil).not.toContain('width: 50%')
  })

  it('liefert für eine Datei ohne Template einen leeren Text', () => {
    expect(templateTeil('<script setup lang="ts">const x = 1</script>')).toBe('')
  })
})

describe('getippteZahlen (UI-05, Fail-first)', () => {
  it.each([
    '<p>Wir bekommen 4,5 Mio. € vom Land.</p>',
    '<p>Das sind 2.594 Euro je Person.</p>',
    '<p>1.234.567 Euro</p>',
    '<p>Rund 12 % der Erträge.</p>',
    '<p>Rund 12% der Erträge.</p>',
    '<p>Zusammen 3€.</p>',
    '<p>Insgesamt 27 Mio.</p>',
  ])('erkennt eine getippte Zahl in %s', (probe) => {
    expect(getippteZahlen(probe).length).toBeGreaterThan(0)
  })

  it('erkennt die Roh-HTML-Direktive', () => {
    const direktive = 'v-' + 'html'
    expect(getippteZahlen(`<div ${direktive}="text"></div>`).length).toBeGreaterThan(0)
  })

  it.each([
    '<span v-if="zeile[\'gerundet\'] === 1">rd. </span>',
    '<wa-details :open="gruppe.id === \'steuern\'" class="om-a-1">',
    '<p>{{ euro(wert) }} und {{ prozent(anteil) }}</p>',
    '<h2 id="om-start-kennzahlen">Die wichtigsten Zahlen {{ jahrText }}</h2>',
    '<p>Hebesätze {{ haushaltsjahrText }}: {{ hebesatzText }}.</p>',
  ])('lässt %s unbeanstandet', (probe) => {
    expect(getippteZahlen(probe)).toEqual([])
  })
})

describe('Keine getippten Zahlen in den Templates (UI-05, T-05-40, T-05-41)', () => {
  const dateien = Object.entries(quelltexte).sort(([a], [b]) => a.localeCompare(b))

  it('sieht die Vue-Dateien der App', () => {
    expect(dateien.length).toBeGreaterThan(20)
  })

  it.each(dateien)('%s enthält keine getippte Zahl und keine Roh-HTML-Direktive', (_pfad, text) => {
    expect(getippteZahlen(templateTeil(text))).toEqual([])
  })
})
