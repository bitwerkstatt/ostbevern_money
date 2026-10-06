import { describe, expect, it } from 'vitest'

import { texte } from '@/data/daten'

// Dauerhafte Prüfung der Du-Anrede (UI-06, D-15). Gescannt werden alle Texte, die ein Mensch
// in der App lesen oder vorgelesen bekommen kann: `texte.json`, die Templates aller Vue-Dateien
// samt Attributwerten (`aria-label`, `title`, `alt`, `summary`, `label`, Props wie `titel`),
// versteckte Texte, außerdem Zeichenketten in den Skriptblöcken der Vue-Dateien und in
// `src/**/*.ts` außerhalb von `__tests__` (Kommentare zählen nicht).
//
// Regel: Eine Höflichkeitsform (Sie, Ihnen, Ihr, Ihre, Ihrem, Ihren, Ihrer, Ihres) innerhalb
// eines Satzes ist immer ein Fehler. Am Satzanfang sind sie dritte Person oder Possessiv und
// nur zulässig, wenn die Stelle in der geschlossenen Liste `AUSNAHMEN` steht (Fundort, die
// ersten 40 Zeichen des Satzes, Grund). Ein satzinitiales „Sie“ vor einem Höflichkeitsverb
// (können, müssen, sollten, …) fällt immer durch, auch mit Eintrag. Eine neue, nicht gelistete
// Stelle lässt den Test scheitern und geht in den Text-Checkpoint (RESEARCH Pitfall 6).

const quelltexte = import.meta.glob<string>(
  ['/src/**/*.vue', '/src/**/*.ts', '!/src/**/__tests__/**'],
  { query: '?raw', import: 'default', eager: true },
)

type Grund = '3. Person' | 'Possessiv'

interface Ausnahme {
  /** Fundort: `texte.json` oder der Pfad der Quelldatei ohne führenden Schrägstrich. */
  quelle: string
  /** Die ersten 40 Zeichen des Satzes (Leerraum zu einem Leerzeichen zusammengefasst). */
  anfang: string
  grund: Grund
}

/**
 * Die geschlossene Liste der satzinitialen „Sie“ und „Ihre“, die keine Höflichkeitsform sind.
 * Jeder Eintrag braucht einen Grund; die Liste wächst nur mit Zustimmung im Text-Checkpoint.
 */
const AUSNAHMEN: readonly Ausnahme[] = [
  {
    quelle: 'texte.json',
    anfang: 'Sie brauchen keinen Zuschuss aus Steuern',
    grund: '3. Person',
  },
  {
    quelle: 'texte.json',
    anfang: 'Sie zeigt auch nichts über die Zeit nach',
    grund: '3. Person',
  },
  {
    quelle: 'texte.json',
    anfang: 'Sie stehen im Finanzplan.',
    grund: '3. Person',
  },
  {
    quelle: 'texte.json',
    anfang: 'Ihre Höhe richtet sich nach einem Hebesa',
    grund: 'Possessiv',
  },
  {
    quelle: 'texte.json',
    anfang: 'Sie wird zusätzlich zur allgemeinen Krei',
    grund: '3. Person',
  },
  {
    quelle: 'texte.json',
    anfang: 'Sie richtet sich nach den Einnahmen aus ',
    grund: '3. Person',
  },
  {
    quelle: 'texte.json',
    anfang: 'Sie wird nicht für einen bestimmten Zwec',
    grund: '3. Person',
  },
  {
    quelle: 'texte.json',
    anfang: 'Sie bilden den Werteverbrauch des Anlage',
    grund: '3. Person',
  },
  {
    quelle: 'texte.json',
    anfang: 'Sie sind Aufwand im Ergebnisplan, aber k',
    grund: '3. Person',
  },
  {
    quelle: 'src/pages/EinnahmenPage.vue',
    anfang: 'Sie bezahlen Investitionen wie Gebäude, ',
    grund: '3. Person',
  },
]

const HOEFLICHKEITSFORM = /\b(?:Sie|Ihnen|Ihr|Ihre|Ihrem|Ihren|Ihrer|Ihres)\b/g
const HOEFLICHKEITSVERB =
  /^Sie\s+(?:können|müssen|sollten|möchten|finden|sehen|erhalten|klicken|wählen)\b/
/** Zeichen, die vor einem Satzanfang stehen dürfen, ohne ihn zu verschieben. */
const SATZANFANG_VORLAUF = /^[\s„“"'‚‘(\[–—-]*$/
/** Platzhalter für einen Ausdruck im Template; enthält weder Satzzeichen noch Buchstaben. */
const PLATZHALTER = '◊'

function gleichmaessig(text: string): string {
  return text.replace(/\s+/g, ' ').trim()
}

function saetze(text: string): string[] {
  return gleichmaessig(text)
    .split(/(?<=[.!?])\s+/)
    .filter((satz) => satz !== '')
}

interface Befund {
  verstoesse: string[]
  genutzt: Ausnahme[]
}

/** Prüft einen Text gegen die Du-Regel; `ausnahmen` ist die Liste der zulässigen Stellen. */
function pruefeText(quelle: string, text: string, ausnahmen: readonly Ausnahme[]): Befund {
  const befund: Befund = { verstoesse: [], genutzt: [] }
  for (const satz of saetze(text)) {
    for (const treffer of satz.matchAll(HOEFLICHKEITSFORM)) {
      const vorlauf = satz.slice(0, treffer.index)
      const kurz = satz.slice(0, 70)
      if (!SATZANFANG_VORLAUF.test(vorlauf)) {
        befund.verstoesse.push(`${quelle}: Höflichkeitsform im Satz „${kurz}“`)
        continue
      }
      if (HOEFLICHKEITSVERB.test(satz.slice(vorlauf.length))) {
        befund.verstoesse.push(`${quelle}: „Sie“ mit Höflichkeitsverb in „${kurz}“`)
        continue
      }
      const ausnahme = ausnahmen.find(
        (eintrag) => eintrag.quelle === quelle && eintrag.anfang === satz.slice(0, 40),
      )
      if (ausnahme === undefined) {
        befund.verstoesse.push(`${quelle}: satzinitial und nicht in AUSNAHMEN: „${kurz}“`)
      } else {
        befund.genutzt.push(ausnahme)
      }
    }
  }
  return befund
}

/** Die Zeichenketten eines Skripts; Kommentare und Regex-Literale werden übersprungen. */
function stringLiterale(code: string): string[] {
  const funde: string[] = []
  const regexVorher = new Set('(,=:[!&|?{};+-*%<>~^')
  let letztes = ''
  let i = 0
  while (i < code.length) {
    const zeichen = code.charAt(i)
    const naechstes = code.charAt(i + 1)
    if (zeichen === '/' && naechstes === '/') {
      const ende = code.indexOf('\n', i)
      i = ende === -1 ? code.length : ende
      continue
    }
    if (zeichen === '/' && naechstes === '*') {
      const ende = code.indexOf('*/', i + 2)
      i = ende === -1 ? code.length : ende + 2
      continue
    }
    if (zeichen === "'" || zeichen === '"') {
      let j = i + 1
      let inhalt = ''
      while (j < code.length && code.charAt(j) !== zeichen && code.charAt(j) !== '\n') {
        if (code.charAt(j) === '\\') {
          j += 1
          inhalt += code.charAt(j) === 'n' ? ' ' : code.charAt(j)
        } else {
          inhalt += code.charAt(j)
        }
        j += 1
      }
      funde.push(inhalt)
      letztes = zeichen
      i = j + 1
      continue
    }
    if (zeichen === '`') {
      let j = i + 1
      let inhalt = ''
      while (j < code.length && code.charAt(j) !== '`') {
        if (code.charAt(j) === '\\') {
          j += 1
          inhalt += code.charAt(j) === 'n' ? ' ' : code.charAt(j)
          j += 1
        } else if (code.charAt(j) === '$' && code.charAt(j + 1) === '{') {
          let tiefe = 1
          let k = j + 2
          while (k < code.length && tiefe > 0) {
            if (code.charAt(k) === '{') tiefe += 1
            if (code.charAt(k) === '}') tiefe -= 1
            k += 1
          }
          funde.push(...stringLiterale(code.slice(j + 2, k - 1)))
          inhalt += PLATZHALTER
          j = k
        } else {
          inhalt += code.charAt(j)
          j += 1
        }
      }
      funde.push(inhalt)
      letztes = '`'
      i = j + 1
      continue
    }
    if (zeichen === '/' && (letztes === '' || regexVorher.has(letztes))) {
      let j = i + 1
      let inKlasse = false
      while (j < code.length && code.charAt(j) !== '\n') {
        const c = code.charAt(j)
        if (c === '\\') {
          j += 1
        } else if (c === '[') {
          inKlasse = true
        } else if (c === ']') {
          inKlasse = false
        } else if (c === '/' && !inKlasse) {
          break
        }
        j += 1
      }
      letztes = '/'
      i = j + 1
      continue
    }
    if (!/\s/.test(zeichen)) {
      letztes = zeichen
    }
    i += 1
  }
  return funde
}

/** Der Inhalt zwischen dem ersten `<template>` und dem letzten `</template>` einer Vue-Datei. */
function templateTeil(quelltext: string): string {
  const anfang = quelltext.search(/^<template>/m)
  const ende = quelltext.lastIndexOf('</template>')
  if (anfang === -1 || ende === -1 || ende <= anfang) {
    return ''
  }
  return quelltext.slice(anfang + '<template>'.length, ende)
}

/** Die Skriptblöcke einer Vue-Datei. */
function skriptTeile(quelltext: string): string[] {
  return Array.from(
    quelltext.matchAll(/<script[^>]*>([\s\S]*?)<\/script>/g),
    (treffer) => treffer[1] ?? '',
  )
}

const TAG = /<\/?[A-Za-z][\w-]*(?:"[^"]*"|'[^']*'|[^>"'])*>/g
const ATTRIBUT = /([:@#\w.-]+)(?:\s*=\s*(?:"([^"]*)"|'([^']*)'))?/g

/** Text eines Templates: Textknoten, statische Attributwerte, Zeichenketten in Ausdrücken. */
function templateTexte(template: string): string[] {
  const funde: string[] = []
  const ohneKommentare = template.replace(/<!--[\s\S]*?-->/g, '')

  function textKnoten(text: string): void {
    const ersetzt = text.replace(/\{\{([\s\S]*?)\}\}/g, (_gesamt, ausdruck: string) => {
      funde.push(...stringLiterale(ausdruck))
      return PLATZHALTER
    })
    if (gleichmaessig(ersetzt) !== '') {
      funde.push(ersetzt)
    }
  }

  let position = 0
  for (const tag of ohneKommentare.matchAll(TAG)) {
    textKnoten(ohneKommentare.slice(position, tag.index))
    position = tag.index + tag[0].length
    const attribute = tag[0].replace(/^<\/?[\w-]+/, '')
    for (const attribut of attribute.matchAll(ATTRIBUT)) {
      const name = attribut[1] ?? ''
      const wert = attribut[2] ?? attribut[3]
      if (wert === undefined) {
        continue
      }
      if (/^[:@#]|^v-/.test(name)) {
        funde.push(...stringLiterale(wert))
      } else {
        funde.push(wert)
      }
    }
  }
  textKnoten(ohneKommentare.slice(position))
  return funde
}

/** Alle Texte eines Quelltextes (Vue-Datei oder TypeScript-Modul). */
function quellTexte(pfad: string, quelltext: string): string[] {
  if (pfad.endsWith('.vue')) {
    return [
      ...templateTexte(templateTeil(quelltext)),
      ...skriptTeile(quelltext).flatMap((skript) => stringLiterale(skript)),
    ]
  }
  return stringLiterale(quelltext)
}

/** Alle kuratierten Texte aus `texte.json`: Titel, Begriffe und Absätze. */
function jsonTexte(): string[] {
  return [
    ...texte.texte.flatMap((eintrag) => [eintrag.titel, ...eintrag.absaetze]),
    ...texte.glossar.flatMap((eintrag) => [eintrag.begriff, ...eintrag.absaetze]),
  ]
}

interface Fundort {
  quelle: string
  text: string
}

function alleTexte(): Fundort[] {
  const aus: Fundort[] = jsonTexte().map((text) => ({ quelle: 'texte.json', text }))
  for (const [pfad, quelltext] of Object.entries(quelltexte)) {
    const quelle = pfad.replace(/^\//, '')
    for (const text of quellTexte(pfad, quelltext)) {
      aus.push({ quelle, text })
    }
  }
  return aus
}

const PROBE: Ausnahme = {
  quelle: 'probe',
  anfang: 'Sie stehen im Finanzplan.',
  grund: '3. Person',
}

describe('pruefeText (UI-06, Fail-first)', () => {
  it.each([
    ['Wenn Sie hier klicken, öffnet sich die Seite.', 'im Satz'],
    ['Das zeigt Ihnen die Tabelle.', 'im Satz'],
    ['Haben Sie Fragen?', 'im Satz'],
    ['Schreib uns, wenn Ihr Anliegen offen bleibt.', 'im Satz'],
    ['Die Seite ist für Sie da. Ihre Fragen sind willkommen.', 'nicht in AUSNAHMEN'],
    ['Sie können die Zahlen im Original nachlesen.', 'Höflichkeitsverb'],
    ['Sie müssen nichts tun.', 'Höflichkeitsverb'],
    ['Sie wählen eine Zeile.', 'Höflichkeitsverb'],
    ['Sie klicken auf den Knopf.', 'Höflichkeitsverb'],
  ])('meldet %s', (text, grund) => {
    const befund = pruefeText('probe', text, [])
    expect(befund.verstoesse.length).toBeGreaterThan(0)
    expect(befund.verstoesse.join('\n')).toContain(grund)
  })

  it('lässt ein satzinitiales „Sie“ nur mit Eintrag in der Ausnahmeliste zu', () => {
    const text = 'Sie stehen im Finanzplan. Du siehst sie dort.'
    expect(pruefeText('probe', text, [PROBE]).verstoesse).toEqual([])
    expect(pruefeText('probe', text, [PROBE]).genutzt).toEqual([PROBE])
    expect(pruefeText('probe', text, []).verstoesse).toHaveLength(1)
  })

  it('bindet einen Eintrag an Fundort und Satzanfang', () => {
    const text = 'Sie stehen im Finanzplan.'
    expect(pruefeText('andere-quelle', text, [PROBE]).verstoesse).toHaveLength(1)
    expect(pruefeText('probe', 'Sie stehen im Haushalt.', [PROBE]).verstoesse).toHaveLength(1)
  })

  it('lässt auch mit Eintrag ein „Sie“ vor einem Höflichkeitsverb nicht durch', () => {
    const ausnahme: Ausnahme = { ...PROBE, anfang: 'Sie können die Seite öffnen.' }
    expect(pruefeText('probe', 'Sie können die Seite öffnen.', [ausnahme]).verstoesse).toHaveLength(
      1,
    )
  })

  it('erkennt ein satzinitiales „Sie“ nach einem Anführungszeichen als Satzanfang', () => {
    expect(pruefeText('probe', '„Sie stehen im Finanzplan.“', []).verstoesse).toHaveLength(1)
  })

  it.each([
    'Du kannst die Zahlen im Original nachlesen.',
    'Schau dir die Entwicklung an: Dein Anteil steigt.',
    'Die Gemeinde zahlt, wenn sie es kann.',
    'Die Hauptstraße ist wichtig, ihre Kosten steigen.',
  ])('lässt %s unbeanstandet', (text) => {
    expect(pruefeText('probe', text, []).verstoesse).toEqual([])
  })
})

describe('stringLiterale', () => {
  it('ignoriert Kommentare, auch mit „Sie“ darin', () => {
    const code = [
      '// Sie im Kommentar',
      "const a = 'Du'",
      '/* Sie im Blockkommentar',
      '   über Zeilen */',
      'const b = "Dir"',
      'const c = `Hallo ${a} und ${"Du"}`',
    ].join('\n')
    expect(stringLiterale(code)).toEqual(['Du', 'Dir', 'Du', 'Hallo ◊ und ◊'])
  })

  it('findet „Sie“ in einer Zeichenkette', () => {
    const funde = stringLiterale("const t = 'Wenn Sie hier klicken'")
    expect(pruefeText('probe', funde.join(' '), []).verstoesse).toHaveLength(1)
  })

  it('verwechselt ein Regex-Literal mit Anführungszeichen nicht mit einer Zeichenkette', () => {
    const code = "const r = /['\"]/g\nconst t = 'Du'"
    expect(stringLiterale(code)).toEqual(['Du'])
  })

  it('beachtet Escapes in Zeichenketten', () => {
    expect(stringLiterale("const t = 'Dir gehört\\'s'")).toEqual(["Dir gehört's"])
  })
})

describe('templateTexte', () => {
  it('liefert Textknoten, Attributwerte und Zeichenketten in Ausdrücken', () => {
    const template = [
      '<PageIntro titel="Titel" :beschreibung="ok ? \'Dein Weg\' : \'Haben Sie Fragen?\'" />',
      '<button aria-label="Quelle anzeigen" title="Hinweis">Weiter {{ wert }} so</button>',
      '<span class="om-visually-hidden"> (öffnet in neuem Tab)</span>',
      '<!-- Sie im Kommentar -->',
    ].join('\n')
    const funde = templateTexte(template)
    expect(funde).toContain('Titel')
    expect(funde).toContain('Dein Weg')
    expect(funde).toContain('Haben Sie Fragen?')
    expect(funde).toContain('Quelle anzeigen')
    expect(funde).toContain('Hinweis')
    expect(funde).toContain('Weiter ◊ so')
    expect(funde).toContain(' (öffnet in neuem Tab)')
    expect(funde.join('\n')).not.toContain('Kommentar')
  })

  it.each([
    '<img alt="Haben Sie das Bild gesehen?">',
    '<wa-icon label="Dort können Sie klicken"></wa-icon>',
    '<p aria-label="Schließen Sie das Fenster"></p>',
    '<details summary="Wenn Sie mehr wissen wollen"></details>',
    '<span class="om-visually-hidden">Öffnen Sie den Link</span>',
    '<p>{{ x ? "Wenn Sie wollen" : "" }}</p>',
  ])('führt eine Höflichkeitsform in %s zu einem Fehler', (template) => {
    const text = templateTexte(template).join(' ')
    expect(pruefeText('probe', text, []).verstoesse.length).toBeGreaterThan(0)
  })
})

describe('Du-Anrede in allen App-Texten (UI-06, D-15)', () => {
  const fundorte = alleTexte()
  const befund = fundorte.map((fundort) => pruefeText(fundort.quelle, fundort.text, AUSNAHMEN))

  it('sieht texte.json, Vue-Dateien und TypeScript-Module', () => {
    const quellen = new Set(fundorte.map((fundort) => fundort.quelle))
    expect(quellen.has('texte.json')).toBe(true)
    expect(Array.from(quellen).filter((q) => q.endsWith('.vue')).length).toBeGreaterThan(20)
    expect(Array.from(quellen).filter((q) => q.endsWith('.ts')).length).toBeGreaterThan(5)
    expect(Array.from(quellen).some((q) => q.includes('__tests__'))).toBe(false)
    expect(fundorte.length).toBeGreaterThan(500)
  })

  it('findet in keiner Quelle eine Höflichkeitsform außerhalb der Ausnahmeliste', () => {
    expect(befund.flatMap((eintrag) => eintrag.verstoesse)).toEqual([])
  })

  it('führt nur Ausnahmen, die der Scan wirklich trifft (keine Karteileichen)', () => {
    const genutzt = new Set(befund.flatMap((eintrag) => eintrag.genutzt))
    expect(AUSNAHMEN.filter((eintrag) => !genutzt.has(eintrag))).toEqual([])
  })

  it('begründet jede Ausnahme und hält sie eindeutig', () => {
    for (const eintrag of AUSNAHMEN) {
      expect(['3. Person', 'Possessiv']).toContain(eintrag.grund)
      expect(eintrag.anfang.length).toBeLessThanOrEqual(40)
    }
    const schluessel = AUSNAHMEN.map((eintrag) => `${eintrag.quelle}|${eintrag.anfang}`)
    expect(new Set(schluessel).size).toBe(schluessel.length)
  })
})
