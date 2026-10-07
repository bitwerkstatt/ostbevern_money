import { readdirSync, readFileSync } from 'node:fs'

import { describe, expect, it } from 'vitest'

// Wächter gegen undefinierte Web-Awesome-Tokens (G-05-6): Ein `var(--wa-…)` mit einem Namen,
// den es nicht gibt, macht die ganze CSS-Deklaration stillschweigend ungültig (so verlor
// `scroll-margin-top` im Glossar seinen Kopfzeilen-Versatz). Die Quelltexte kommen wie in
// `quelltext.test.ts` über `import.meta.glob` mit `?raw`.
// Warum Quelltext: Gesichert werden Stil-Konventionen (nur definierte Tokens, vier Schriftgrößen,
// zwei Gewichte), die im CSS der Dateien stehen. Die Testumgebung (`environment: 'node'`) berechnet
// keine Stile und hat weder ein DOM noch ein DOM-Paket (D-14).
// Grenzen des Wächters (05/IN-04): Er kann keine dynamischen Tokennamen auflösen, etwa
// `var(--wa-color-${name})` in einer Vorlagenzeichenkette. Solche Namen enden nach dem
// festen Teil auf „-“ und werden übersprungen und gemeldet, statt als fehlend zu gelten.
// Und er kennt nur die globalen Web-Awesome-Stylesheets (`dist/styles/**/*.css`): Ein Token,
// das nur im CSS einer einzelnen Komponente innerhalb ihres JavaScript-Chunks steht, wird
// nicht eingesammelt, ein `var()` darauf würde fälschlich als undefiniert gemeldet.
const quelltexte = import.meta.glob<string>(['/src/**/*.vue', '/src/**/*.css', '/src/**/*.ts'], {
  query: '?raw',
  import: 'default',
  eager: true,
})

/** Alle `--wa-…`-Namen aus `var(--wa-…)`, auch unvollständige Namen auf „-“ (dynamischer Rest). */
function benannteTokens(text: string): string[] {
  return Array.from(text.matchAll(/var\(\s*(--wa-[a-z0-9-]+)/g), (treffer) => treffer[1]!)
}

/**
 * Alle vollständigen `--wa-…`-Namen, die als `var(--wa-…)` benutzt werden (nicht
 * `--scroll-margin-top` o. Ä.). Ein Name auf „-“ ist der feste Teil eines dynamischen Namens
 * wie `var(--wa-color-${name})` und nicht auflösbar; er steht in `dynamischeTokens`.
 */
function verwendeteTokens(text: string): string[] {
  return benannteTokens(text).filter((name) => !name.endsWith('-'))
}

/** Die festen Teile dynamischer Namen (enden auf „-“), die `verwendeteTokens` überspringt. */
function dynamischeTokens(text: string): string[] {
  return benannteTokens(text).filter((name) => name.endsWith('-'))
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

  it('überspringt Namen auf „-“ aus dynamischen var()-Namen und meldet sie als dynamisch', () => {
    const text = 'color: var(--wa-color-${name}); gap: var(--wa-space-m)'
    expect(verwendeteTokens(text)).toEqual(['--wa-space-m'])
    expect(dynamischeTokens(text)).toEqual(['--wa-color-'])
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

// Typografie- und Abstandsvertrag (UI-SPEC 06 und 07, Befund aus 05-/06-UI-REVIEW, D-17): Die
// App kennt vier Schriftgrößen und zwei Gewichte. Der Wächter prüft die Style-Blöcke jeder
// .vue-Datei und jede .css-Datei unter src/, nicht eine Liste benannter Dateien. .ts-Dateien
// bleiben draußen: Die ECharts-Option `fontSize` ist kein CSS.
const ERLAUBTE_SCHRIFTGROESSEN: readonly string[] = ['s', 'm', 'l', '2xl']
const ERLAUBTE_GEWICHTE: readonly string[] = ['normal', 'bold']
const VERBOTENE_SPACING_TOKENS: readonly string[] = [
  '--wa-space-3xs',
  '--wa-space-2xl',
  '--wa-space-5xl',
]

/** Der Inhalt aller `<style>`-Blöcke einer Vue-Datei (Template und Script bleiben unberücksichtigt). */
function styleBloecke(vueText: string): string {
  return Array.from(
    vueText.matchAll(/<style\b[^>]*>([\s\S]*?)<\/style>/g),
    (treffer) => treffer[1]!,
  ).join('\n')
}

/** Die CSS-Teile einer Datei: bei .vue die Style-Blöcke, bei .css der ganze Text. */
function cssTeil(pfad: string, text: string): string {
  return pfad.endsWith('.vue') ? styleBloecke(text) : text
}

/** Die Deklarationswerte einer Eigenschaft (`font-size`, nicht `--x-font-size`). */
function deklarationen(css: string, eigenschaft: string): string[] {
  const muster = new RegExp(`(?<![-\\w])${eigenschaft}\\s*:\\s*([^;}]+)`, 'g')
  return Array.from(css.matchAll(muster), (treffer) => treffer[1]!.trim())
}

/** Ob der Wert genau `var(--wa-<familie>-<stufe>)` mit einer erlaubten Stufe ist. */
function istErlaubterToken(wert: string, familie: string, erlaubt: readonly string[]): boolean {
  const treffer = new RegExp(`^var\\(\\s*--wa-${familie}-([a-z0-9]+)\\s*\\)$`).exec(wert)
  return treffer !== null && erlaubt.includes(treffer[1]!)
}

/** Alle Verstöße gegen den Typografie- und Abstandsvertrag in einem CSS-Text. */
function verstoesse(css: string): string[] {
  const meldungen: string[] = []
  for (const wert of deklarationen(css, 'font-size')) {
    if (!istErlaubterToken(wert, 'font-size', ERLAUBTE_SCHRIFTGROESSEN)) {
      meldungen.push(`font-size: ${wert}`)
    }
  }
  for (const wert of deklarationen(css, 'font-weight')) {
    if (!istErlaubterToken(wert, 'font-weight', ERLAUBTE_GEWICHTE)) {
      meldungen.push(`font-weight: ${wert}`)
    }
  }
  for (const token of VERBOTENE_SPACING_TOKENS) {
    if (new RegExp(`var\\(\\s*${token}(?![a-z0-9-])`).test(css)) {
      meldungen.push(token)
    }
  }
  return meldungen
}

describe('styleBloecke (Fail-first)', () => {
  it('liefert nur den Inhalt der Style-Blöcke', () => {
    const text = [
      '<script setup lang="ts">const a = "font-size: 18px"</script>',
      '<template><p style="font-size: 18px">x</p></template>',
      '<style scoped>.a { gap: var(--wa-space-s); }</style>',
      '<style>.b { color: red; }</style>',
    ].join('\n')
    const css = styleBloecke(text)
    expect(css).toContain('gap: var(--wa-space-s)')
    expect(css).toContain('color: red')
    expect(css).not.toContain('18px')
  })

  it('liefert für eine Datei ohne Style-Block einen leeren Text', () => {
    expect(styleBloecke('<template><p>x</p></template>')).toBe('')
  })
})

describe('verstoesse (Fail-first)', () => {
  it('meldet ein Schriftgrößen-Literal', () => {
    expect(verstoesse('font-size: 18px')).toEqual(['font-size: 18px'])
  })

  it('meldet ein Gewichts-Literal', () => {
    expect(verstoesse('font-weight: 600')).toEqual(['font-weight: 600'])
  })

  it('meldet das Schlüsselwort bold als Gewichts-Literal', () => {
    expect(verstoesse('font-weight: bold')).toEqual(['font-weight: bold'])
  })

  it.each([
    ['font-size: var(--wa-font-size-xl)', 'font-size: var(--wa-font-size-xl)'],
    ['font-weight: var(--wa-font-weight-semibold)', 'font-weight: var(--wa-font-weight-semibold)'],
    ['font-weight: var(--wa-font-weight-body)', 'font-weight: var(--wa-font-weight-body)'],
  ])('meldet den nicht erlaubten Token in %s', (css, meldung) => {
    expect(verstoesse(css)).toEqual([meldung])
  })

  it.each(['--wa-space-2xl', '--wa-space-3xs', '--wa-space-5xl'])(
    'meldet den Abstands-Token %s',
    (token) => {
      expect(verstoesse(`gap: var(${token})`)).toEqual([token])
    },
  )

  it('lässt die erlaubten Tokens durch, auch --wa-font-size-2xl und --wa-space-s', () => {
    const css =
      'font-size: var(--wa-font-size-2xl); font-weight: var(--wa-font-weight-bold); gap: var(--wa-space-s)'
    expect(verstoesse(css)).toEqual([])
  })

  it('hält eine Custom Property mit font-size im Namen nicht für die Eigenschaft', () => {
    expect(verstoesse('--om-font-size: 18px')).toEqual([])
  })
})

describe('Typografie und Abstände aller Dateien (D-17, UI-SPEC 07)', () => {
  const cssDateien = appDateien
    .filter(([pfad]) => pfad.endsWith('.vue') || pfad.endsWith('.css'))
    .map(([pfad, text]) => [pfad, cssTeil(pfad, text)] as const)
    .sort(([a], [b]) => a.localeCompare(b))

  it('sieht alle .vue- und .css-Dateien der App', () => {
    expect(cssDateien.length).toBeGreaterThan(40)
  })

  it.each(cssDateien)('%s hält Schriftgrößen, Gewichte und Abstände ein', (_pfad, css) => {
    expect(verstoesse(css)).toEqual([])
  })
})

describe('Überschriften-Rolle der Unterüberschriften (D-18)', () => {
  /** Der Regelrumpf zu einem Selektor in einem CSS-Text. */
  function regelrumpf(css: string, selektor: string): string {
    const anfang = css.indexOf(`${selektor} {`)
    return anfang === -1 ? '' : css.slice(anfang, css.indexOf('}', anfang))
  }

  it.each([
    ['/src/pages/StellenplanPage.vue', '.om-stellenplan__gruppe h3'],
    ['/src/components/ZuschussListe.vue', '.om-zuschuesse__untertitel'],
  ])('%s: %s hat die Überschriften-Rolle', (pfad, selektor) => {
    const regel = regelrumpf(styleBloecke(quelltexte[pfad] ?? ''), selektor)
    expect(regel).toContain('font-size: var(--wa-font-size-l)')
    expect(regel).toContain('font-weight: var(--wa-font-weight-bold)')
    expect(regel).toContain('line-height: var(--wa-line-height-condensed)')
  })
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

  it('meldet Namen auf „-“ als dynamisch, statt sie als fehlend zu zählen', ({ skip }) => {
    const dynamisch = Array.from(
      new Set(appDateien.flatMap(([, text]) => dynamischeTokens(text))),
    ).sort()
    if (dynamisch.length > 0) {
      skip(
        `Nicht prüfbar (dynamische Tokennamen, nur der feste Teil steht im Quelltext): ${dynamisch.join(', ')}`,
      )
    }
  })

  it('benutzt kein var(--wa-*), das weder Web Awesome noch die App definiert', () => {
    const verwendet = appDateien.flatMap(([, text]) => verwendeteTokens(text))
    expect(fehlendeTokens(verwendet, definiert)).toEqual([])
  })
})
