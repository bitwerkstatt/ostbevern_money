import { readdirSync, readFileSync } from 'node:fs'

import { describe, expect, it } from 'vitest'

// Wächter gegen undefinierte Web-Awesome-Tokens (G-05-6): Ein `var(--wa-…)` mit einem Namen,
// den es nicht gibt, macht die ganze CSS-Deklaration stillschweigend ungültig (so verlor
// `scroll-margin-top` im Glossar seinen Kopfzeilen-Versatz). Die Quelltexte kommen wie in
// `quelltext.test.ts` über `import.meta.glob` mit `?raw`.
const quelltexte = import.meta.glob<string>(['/src/**/*.vue', '/src/**/*.css', '/src/**/*.ts'], {
  query: '?raw',
  import: 'default',
  eager: true,
})

/** Alle `--wa-…`-Namen, die als `var(--wa-…)` benutzt werden (nicht `--scroll-margin-top` o. Ä.). */
function verwendeteTokens(text: string): string[] {
  return Array.from(text.matchAll(/var\(\s*(--wa-[a-z0-9-]+)/g), (treffer) => treffer[1]!)
}

/** Alle `--wa-…`-Namen, die als Custom Property deklariert werden (Name, dann Doppelpunkt). */
function definierteTokens(text: string): string[] {
  return Array.from(text.matchAll(/(--wa-[a-z0-9-]+)\s*:/g), (treffer) => treffer[1]!)
}

/** Die benutzten Tokens, die nirgends definiert sind (sortiert, ohne Doppelte). */
function fehlendeTokens(verwendet: Iterable<string>, definiert: ReadonlySet<string>): string[] {
  return Array.from(new Set(verwendet))
    .filter((name) => !definiert.has(name))
    .sort()
}

const WEBAWESOME_STILE = new URL(
  '../../../node_modules/@awesome.me/webawesome/dist/styles/',
  import.meta.url,
)

/** Alle Tokens, die Web Awesome in seinen mitgelieferten Stylesheets definiert. */
function webAwesomeTokens(): string[] {
  return readdirSync(WEBAWESOME_STILE, { recursive: true, encoding: 'utf8' })
    .filter((pfad) => pfad.endsWith('.css'))
    .flatMap((pfad) => definierteTokens(readFileSync(new URL(pfad, WEBAWESOME_STILE), 'utf8')))
}

// Die Tests dieser Datei enthalten das falsche Beispiel mit Absicht und zählen nicht mit.
const appDateien = Object.entries(quelltexte).filter(([pfad]) => !pfad.includes('/__tests__/'))

describe('verwendeteTokens und definierteTokens (Fail-first)', () => {
  it('findet nur --wa-Namen in var(), nicht --scroll-margin-top von wa-page', () => {
    const text = 'calc(var(--scroll-margin-top, 0px) + var(--wa-space-md))'
    expect(verwendeteTokens(text)).toEqual(['--wa-space-md'])
  })

  it('findet deklarierte --wa-Tokens', () => {
    expect(definierteTokens(':root { --wa-space-m: 1rem; --wa-space-l: 1.5rem }')).toEqual([
      '--wa-space-m',
      '--wa-space-l',
    ])
  })

  it('meldet den Tippfehler --wa-space-md als undefiniert', () => {
    const verwendet = verwendeteTokens('calc(var(--scroll-margin-top, 0px) + var(--wa-space-md))')
    const definiert = new Set(
      definierteTokens(':root { --wa-space-m: 1rem; --wa-space-l: 1.5rem }'),
    )
    expect(fehlendeTokens(verwendet, definiert)).toEqual(['--wa-space-md'])
  })
})

// Typografie-Vertrag der Phase 6: UI-SPEC 06 §Typography erlaubt nur vier Schriftgrößen und zwei
// Gewichte (Befund aus 06-UI-REVIEW, Säule 4). Die Phase-5-Dateien GlossarPage.vue,
// GlossarListe.vue und EinnahmenPage.vue fehlen hier mit Absicht, ihre Bereinigung ist Phase 7.
const PHASE_6_TYPOGRAFIE_DATEIEN = [
  '/src/pages/EntwicklungPage.vue',
  '/src/pages/InvestitionenPage.vue',
  '/src/pages/RatEntscheidetPage.vue',
  '/src/components/ZuschussListe.vue',
  '/src/components/UeberschussListe.vue',
  '/src/components/NichtBeeinflussbarBlock.vue',
] as const

const VERBOTENE_TYPOGRAFIE_TOKENS: ReadonlySet<string> = new Set([
  '--wa-font-size-xl',
  '--wa-font-weight-semibold',
])

/** Die verbotenen Größen- und Gewichts-Tokens, die der Text benutzt (sortiert, ohne Doppelte). */
function verboteneTypografieTokens(text: string): string[] {
  return Array.from(new Set(verwendeteTokens(text)))
    .filter((name) => VERBOTENE_TYPOGRAFIE_TOKENS.has(name))
    .sort()
}

describe('verboteneTypografieTokens (Fail-first)', () => {
  it('meldet die verbotene Größe und das verbotene Gewicht', () => {
    const text = 'font-size: var(--wa-font-size-xl); font-weight: var(--wa-font-weight-semibold)'
    expect(verboteneTypografieTokens(text)).toEqual([
      '--wa-font-size-xl',
      '--wa-font-weight-semibold',
    ])
  })

  it('lässt die erlaubten Tokens durch, auch --wa-font-size-2xl', () => {
    const text = [
      'font-size: var(--wa-font-size-2xl)',
      'font-size: var(--wa-font-size-l)',
      'font-size: var(--wa-font-size-m)',
      'font-weight: var(--wa-font-weight-bold)',
    ].join('; ')
    expect(verboteneTypografieTokens(text)).toEqual([])
  })
})

describe('Typografie der Phase-6-Dateien (UI-SPEC 06)', () => {
  it('findet alle sechs Phase-6-Dateien in den Quelltexten', () => {
    expect(Object.keys(quelltexte)).toEqual(expect.arrayContaining([...PHASE_6_TYPOGRAFIE_DATEIEN]))
  })

  it.each(PHASE_6_TYPOGRAFIE_DATEIEN)(
    '%s benutzt nur erlaubte Schriftgrößen und Gewichte',
    (pfad) => {
      expect(verboteneTypografieTokens(quelltexte[pfad] ?? '')).toEqual([])
    },
  )
})

describe('Stiltokens der App (G-05-6)', () => {
  const definiert = new Set([
    ...webAwesomeTokens(),
    ...appDateien.flatMap(([, text]) => definierteTokens(text)),
  ])

  it('sieht die App-Quelltexte und die Web-Awesome-Definitionen', () => {
    expect(appDateien.length).toBeGreaterThan(20)
    expect(definiert.size).toBeGreaterThan(100)
  })

  it('benutzt kein var(--wa-*), das weder Web Awesome noch die App definiert', () => {
    const verwendet = appDateien.flatMap(([, text]) => verwendeteTokens(text))
    expect(fehlendeTokens(verwendet, definiert)).toEqual([])
  })
})
