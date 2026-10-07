import { describe, expect, it } from 'vitest'

import { GLOSSAR_SCHLUESSEL, glossarVerwendungen } from '@/lib/glossar'

// Quelltext-Prüfungen über alle Vue-Dateien der App (GLOS-03, UI-05). Die Quelltexte kommen
// wie in `glossar.test.ts` über `import.meta.glob` mit `?raw`.
const quelltexte = import.meta.glob<string>('/src/**/*.vue', {
  query: '?raw',
  import: 'default',
  eager: true,
})

/**
 * Die neun Inhaltsseiten, auf denen Glossarbegriffe im Fließtext verlinkt sein müssen: die fünf
 * aus Phase 5 (D-16) und die vier aus Phase 6 (D-14, D-17).
 */
const INHALTSSEITEN = [
  'StartPage',
  'EinnahmenPage',
  'AusgabenPage',
  'GeldflussPage',
  'ProduktPage',
  'EntwicklungPage',
  'InvestitionenPage',
  'RatEntscheidetPage',
  'StellenplanPage',
] as const

/**
 * Schlüssel, die zusammen auf den Inhaltsseiten verlinkt sein müssen (GLOS-03, D-16, D-17): die
 * Pflichtbegriffe aus Phase 5, dann die vier aus Phase 6.
 */
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
  'haushaltssicherung',
  'verpflichtungsermaechtigung',
  'vzae',
  'entgeltgruppen',
] as const

/** Der Inhalt zwischen dem ersten `<template>` und dem letzten `</template>` einer Vue-Datei. */
function templateTeil(quelltext: string): string {
  const anfang = quelltext.search(/^<template>/m)
  const ende = quelltext.lastIndexOf('</template>')
  if (anfang === -1 || ende === -1 || ende <= anfang) {
    return ''
  }
  return quelltext.slice(anfang + '<template>'.length, ende)
}

/** Deutsche Tausendergruppen: 1 bis 3 Ziffern, dann Gruppen aus Punkt und drei Ziffern. */
const GRUPPIERTE_ZAHL = /(?<![\d.,])\d{1,3}(?:\.\d{3})+(?!\d)/g
/** Eine Ziffer, optional ein Leerzeichen, dann „Mio.“, „€“ oder „%“. */
const BETRAG_ODER_PROZENT = /\d\s*(?:Mio\.|€|%)/g
/** Die Roh-HTML-Direktive; aus zwei Teilen gebaut, damit diese Datei sich nicht selbst trifft. */
const ROH_HTML = new RegExp('\\bv-' + 'html\\b', 'g')

/** Die Fundstellen getippter Zahlen oder der Roh-HTML-Direktive im Template (UI-05, T-05-40/41). */
function getippteZahlen(template: string): string[] {
  return [GRUPPIERTE_ZAHL, BETRAG_ODER_PROZENT, ROH_HTML].flatMap((muster) =>
    Array.from(template.matchAll(muster), (treffer) => treffer[0]),
  )
}

function seitenQuelltext(seite: string): string {
  const quelltext = quelltexte[`/src/pages/${seite}.vue`]
  if (quelltext === undefined) {
    throw new Error(`Seite ${seite}.vue nicht gefunden`)
  }
  return quelltext
}

describe('Glossarverlinkung auf den Inhaltsseiten (GLOS-03, D-16, D-17)', () => {
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
    '<EuroBetrag :wert="wert" :gerundet="zeile[\'gerundet\'] === 1" />',
    '<wa-details :open="gruppe.id === \'steuern\'" class="om-a-1">',
    '<p>{{ euro(wert) }} und {{ prozent(anteil) }}</p>',
    '<h2 id="om-start-kennzahlen">Die wichtigsten Zahlen {{ jahrText }}</h2>',
    '<p>Hebesätze {{ haushaltsjahrText }}: {{ hebesatzText }}.</p>',
  ])('lässt %s unbeanstandet', (probe) => {
    expect(getippteZahlen(probe)).toEqual([])
  })
})

/** Ein öffnendes `<wa-…>`-Tag samt Attributen; Anführungszeichen dürfen ein `>` enthalten. */
const WA_ELEMENT = /<wa-[\w-]+(?:"[^"]*"|'[^']*'|[^>"'])*>/g
/** Das `size`-Attribut mit einem der drei langen Namen, die Web Awesome 3 als veraltet meldet. */
const VERALTETE_GROESSE = /\ssize\s*=\s*"(small|medium|large)"/g

/**
 * Die veralteten Größenangaben (`small`, `medium`, `large`) an `wa-*`-Elementen im Template.
 * Web Awesome 3.14 meldet sie als Konsolenwarnung (QUAL-02); erlaubt sind `xs`, `s`, `m`, `l`, `xl`.
 */
function veralteteGroessen(template: string): string[] {
  return Array.from(template.matchAll(WA_ELEMENT), (element) => element[0]).flatMap((element) =>
    Array.from(element.matchAll(VERALTETE_GROESSE), (treffer) => treffer[0].trim()),
  )
}

describe('veralteteGroessen (QUAL-02, Fail-first)', () => {
  it.each([
    ['<wa-tag size="small" variant="neutral">x</wa-tag>', 'size="small"'],
    ['<wa-tag size="medium">x</wa-tag>', 'size="medium"'],
    ['<wa-button size="large">x</wa-button>', 'size="large"'],
    [
      '<wa-button\n  variant="brand"\n  size="large"\n  @click="a => b()"\n>x</wa-button>',
      'size="large"',
    ],
  ])('meldet die veraltete Größe in %s', (probe, erwartet) => {
    expect(veralteteGroessen(probe)).toEqual([erwartet])
  })

  it.each([
    '<wa-tag size="s" variant="neutral">x</wa-tag>',
    '<wa-button size="l">x</wa-button>',
    '<wa-tag variant="neutral">x</wa-tag>',
    '<img size="large" alt="">',
    '<p>size="small" im Fließtext</p>',
  ])('lässt %s unbeanstandet', (probe) => {
    expect(veralteteGroessen(probe)).toEqual([])
  })
})

describe('Keine veralteten Web-Awesome-Größen in den Templates (QUAL-02)', () => {
  const dateien = Object.entries(quelltexte).sort(([a], [b]) => a.localeCompare(b))

  it.each(dateien)('%s benutzt nur die kurzen Größennamen', (_pfad, text) => {
    expect(veralteteGroessen(templateTeil(text))).toEqual([])
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
