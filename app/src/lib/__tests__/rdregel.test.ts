import { describe, expect, it } from 'vitest'

// Wächter gegen neue Kopien der „rd.“-Regel (D-22, TXT-04). Ob ein Betrag nur auf T€ genau ist
// und deshalb „rd.“ davor bekommt, entscheidet allein `charts/format.ts` (`RD_PRAEFIX`,
// `betragMitHinweis`, `kurzMitHinweis`). Jede Komponente und jede Hilfsfunktion nutzt diese
// Funktionen oder `EuroBetrag`, statt den Vorsatz selbst zu bauen. Der Test liest den
// Quelltext, weil das eine Konvention ist und kein Verhalten: Eine zweite Kopie liefert heute
// dieselbe Ausgabe wie die zentrale Regel und fällt erst auf, wenn die beiden auseinanderlaufen
// (so entstanden die Altkopien, die Phase 8 entfernt hat). Es gibt in der Testumgebung
// (`environment: 'node'`) kein DOM und kein DOM-Paket (D-14), das die gerenderte Seite prüfen
// könnte; die Quelltext-Prüfung ist deshalb der einzige Weg, die Konvention zu sichern.
const quelltexte = import.meta.glob<string>('/src/**/*.{ts,vue}', {
  query: '?raw',
  import: 'default',
  eager: true,
})

/** Die einzige Datei, die den Vorsatz bauen darf. */
const ERLAUBTE_DATEI = '/src/charts/format.ts'

/**
 * Kommentare entfernen, bevor gesucht wird: Doc-Kommentare nennen die Regel in typografischen
 * Anführungszeichen („rd.“) und müssen erlaubt bleiben. Blockkommentare und
 * Zeilenkommentare gelten nur am Zeilenanfang oder nach einem Leerraum, damit `https://` und
 * Glob-Muster wie `/src/**\/*.vue` in Zeichenketten nicht als Kommentar zählen. Grenze: Ein
 * `//` nach einem Leerraum innerhalb einer Zeichenkette gilt als Kommentar.
 */
function ohneKommentare(quelltext: string): string {
  return quelltext
    .replace(/<!--[\s\S]*?-->/g, '')
    .replace(/(^|\s)\/\*[\s\S]*?\*\//g, '$1')
    .replace(/(^|\s)\/\/.*$/gm, '$1')
}

/**
 * „rd.“ ohne Buchstaben oder Ziffer davor (kein „Standard.“, kein „Bord.“), danach ein
 * Leerzeichen, U+00A0, der Escape für U+00A0 (` `, `\xa0`), `&nbsp;` oder ein Anführungszeichen
 * (einfach, doppelt, Backtick). Das typografische Schlusszeichen U+201C gehört nicht dazu.
 */
const RD_KOPIE = /(?<![\p{L}\p{N}])rd\.(?: | |\\u00a0|\\u\{a0\}|\\xa0|&nbsp;|['"`])/giu

/** Die Fundstellen einer selbst gebauten „rd.“-Regel in einem Quelltext (mit etwas Umgebung). */
function rdKopien(quelltext: string): string[] {
  const text = ohneKommentare(quelltext)
  return Array.from(text.matchAll(RD_KOPIE), (treffer) => {
    const anfang = Math.max(0, treffer.index - 12)
    return text.slice(anfang, treffer.index + treffer[0].length + 20).replace(/\s+/g, ' ')
  })
}

describe('rdKopien erkennt selbst gebaute rd.-Vorsätze (Fail-first)', () => {
  it.each([
    [
      'Markup mit Span (Altform in SteuerZeitreihe.vue)',
      `<span v-if="zeile['gerundet'] === 1">rd. </span>{{ euro(wert) }}`,
    ],
    ['Template-Literal mit euro(wert)', 'const text = `rd. ${euro(wert)}`'],
    [
      'Callout-Markup mit euroKurz',
      '<p class="om-callout">rd. {{ euroKurz(wert) }} bleiben übrig</p>',
    ],
    ['Zeichenkette mit dem Escape für U+00A0', "const vorsatz = 'rd.\\u00a0'"],
    ["Zeichenkette 'rd. ' mit Leerzeichen", "const vorsatz = 'rd. '"],
    ['Zeichenkette mit echtem U+00A0', "const vorsatz = 'rd. '"],
    ['HTML-Entität &nbsp;', '<span>rd.&nbsp;{{ wert }}</span>'],
    [
      'rd. als eigene Zeichenkette, mit Leerzeichen verkettet',
      "const text = 'rd.' + ' ' + euro(wert)",
    ],
  ])('findet %s', (_name, quelltext) => {
    expect(rdKopien(quelltext)).toHaveLength(1)
  })

  it('findet die Kopie auch hinter einem Zeilenkommentar in der Zeile davor', () => {
    const quelltext = ['// Betrag mit „rd.“ davor', "const vorsatz = 'rd. '"].join('\n')
    expect(rdKopien(quelltext)).toHaveLength(1)
  })
})

describe('rdKopien lässt erlaubte Schreibweisen durch (Fail-first)', () => {
  it.each([
    ['Aufruf der zentralen Funktion', '{{ betragMitHinweis(wert, true) }}'],
    ['Komponente EuroBetrag', '<EuroBetrag :wert="wert" gerundet />'],
    [
      'Zeilenkommentar mit typografischem „rd.“',
      '// Betrag mit „rd.“ davor, wenn er nur auf T€ genau ist',
    ],
    [
      'JSDoc-Kommentar mit typografischem „rd.“',
      '/**\n * Zeigt „rd.“ vor dem Betrag.\n */\nexport const a = 1',
    ],
    [
      'Zeilenkommentar nach Code mit rd. und Leerzeichen',
      'const a = 1 // rd. davor, siehe format.ts',
    ],
    ['HTML-Kommentar mit rd.', '<!-- rd. {{ euro(wert) }} -->\n<p>x</p>'],
    ['Zeichenkette mit URL, die rd. enthält', "const url = 'https://example.org/rd.html'"],
    ['typografisches Schlusszeichen im Fließtext', "const text = 'Betrag mit „rd.“ davor'"],
    ['Wortende wie Standard.', "const text = 'Der Standard. Danach geht es weiter'"],
    ['Glob-Muster ohne Kommentar', "import.meta.glob('/src/**/*.vue', { query: '?raw' })"],
  ])('lässt %s durch', (_name, quelltext) => {
    expect(rdKopien(quelltext)).toEqual([])
  })
})

describe('Quelltext der App (D-22, TXT-04)', () => {
  const dateien = Object.entries(quelltexte)
    .filter(([pfad]) => !pfad.includes('/__tests__/') && pfad !== ERLAUBTE_DATEI)
    .sort(([a], [b]) => a.localeCompare(b))

  it('sieht den Quelltext der App und die einzige erlaubte Datei', () => {
    // Ein leerer oder verfehlter Glob würde sonst jede Prüfung unten trivial bestehen lassen.
    expect(Object.keys(quelltexte).length).toBeGreaterThan(100)
    expect(dateien.length).toBeGreaterThan(80)
    expect(Object.keys(quelltexte)).toContain(ERLAUBTE_DATEI)
  })

  it('hat in format.ts den Vorsatz, den dieser Wächter sonst überall verbietet', () => {
    expect(rdKopien(quelltexte[ERLAUBTE_DATEI] ?? '').length).toBeGreaterThan(0)
  })

  it.each(dateien)('%s baut den rd.-Vorsatz nicht selbst', (pfad, quelltext) => {
    expect(rdKopien(quelltext), pfad).toEqual([])
  })
})
