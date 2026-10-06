// Globale Abdeckung der Quelle-Knöpfe (Phase 7, UI-02, D-01): kein `.vue`-Template rendert eine
// `KennzahlKachel` ohne `:quelle`, und keine Tabellenspalte mit dem Titel „Quelle“ oder
// „PDF-Seite“ ist ein bloßer Text statt der Spaltenart `quelle`. Die Pläne 07-05 bis 07-08 haben
// jede Seite einzeln geprüft (`quelle-kacheln.test.ts`, `quelle-kontext.test.ts`); dieser Test
// fängt eine später ergänzte Kachel oder Spalte an beliebiger Stelle von `src/` ab.

import { describe, expect, it } from 'vitest'

const vueDateien = import.meta.glob<string>('/src/**/*.vue', {
  query: '?raw',
  import: 'default',
  eager: true,
})

const tsDateien = import.meta.glob<string>(['/src/**/*.ts', '!/src/**/__tests__/**'], {
  query: '?raw',
  import: 'default',
  eager: true,
})

const KACHEL_ELEMENT = /<KennzahlKachel\b[\s\S]*?\/>/g
const KACHEL_ANFANG = /<KennzahlKachel\b/g

/** Alle selbstschließenden `<KennzahlKachel … />`-Elemente eines Quelltexts. */
function kachelElemente(quelltext: string): string[] {
  return Array.from(quelltext.matchAll(KACHEL_ELEMENT), (treffer) => treffer[0])
}

/** Anzahl aller `<KennzahlKachel`-Anfänge, auch ohne selbstschließendes Ende. */
function kachelAnfaenge(quelltext: string): number {
  return Array.from(quelltext.matchAll(KACHEL_ANFANG)).length
}

/** Kacheln ohne gebundenes `:quelle` (jede Kachel braucht den Belegschlüssel, D-01). */
function kachelnOhneQuelle(quelltext: string): string[] {
  return kachelElemente(quelltext).filter((element) => !/\s:quelle="/.test(element))
}

/** Objektliteral-Spalten mit Titel „Quelle“ oder „PDF-Seite“. */
const QUELL_SPALTE = /\{[^{}]*(?<!\w)titel:\s*(['"`])(?:Quelle|PDF-Seite)\1[^{}]*\}/g

/** Spalten mit Titel „Quelle“/„PDF-Seite“, deren Art nicht `quelle` ist. */
function spaltenMitFalscherArt(quelltext: string): string[] {
  return Array.from(quelltext.matchAll(QUELL_SPALTE), (treffer) => treffer[0]).filter(
    (spalte) => !/(?<!\w)art:\s*(['"`])quelle\1/.test(spalte),
  )
}

describe('D-01 global: jede KennzahlKachel bindet :quelle', () => {
  it('findet in src/ mindestens eine Kachel (der Scan läuft nicht ins Leere)', () => {
    const alle = Object.values(vueDateien).flatMap(kachelElemente)
    expect(alle.length).toBeGreaterThan(0)
  })

  it('jedes <KennzahlKachel> ist selbstschließend, damit der Scan es vollständig sieht', () => {
    for (const [pfad, quelltext] of Object.entries(vueDateien)) {
      expect(kachelAnfaenge(quelltext), pfad).toBe(kachelElemente(quelltext).length)
    }
  })

  it('keine .vue-Datei rendert eine KennzahlKachel ohne :quelle', () => {
    const ohne = Object.entries(vueDateien).flatMap(([pfad, quelltext]) =>
      kachelnOhneQuelle(quelltext).map((element) => `${pfad}: ${element.slice(0, 80)}`),
    )
    expect(ohne).toEqual([])
  })

  it('das Prüfmuster erkennt eine Kachel ohne :quelle und akzeptiert eine mit', () => {
    expect(kachelnOhneQuelle('<KennzahlKachel bezeichnung="x" wert="1" zeile="z" />')).toHaveLength(
      1,
    )
    expect(
      kachelnOhneQuelle('<KennzahlKachel bezeichnung="x" :quelle="k.quelle" zeile="z" />'),
    ).toHaveLength(0)
    // `:quelle` im Wert eines anderen Attributs zählt nicht als gebunden.
    expect(kachelnOhneQuelle('<KennzahlKachel zeile=" :quelle=&quot;x&quot;" />')).toHaveLength(1)
  })
})

describe('D-01 global: Spalten „Quelle“ und „PDF-Seite“ haben die Art quelle', () => {
  const quelltexte = [...Object.entries(vueDateien), ...Object.entries(tsDateien)]

  it('findet in src/ Quelle-Spalten (der Scan läuft nicht ins Leere)', () => {
    const treffer = quelltexte.flatMap(([, quelltext]) =>
      Array.from(quelltext.matchAll(QUELL_SPALTE)),
    )
    expect(treffer.length).toBeGreaterThan(0)
  })

  it('keine DatenSpalte mit Titel „Quelle“ oder „PDF-Seite“ nutzt eine andere Art als quelle', () => {
    const falsch = quelltexte.flatMap(([pfad, quelltext]) =>
      spaltenMitFalscherArt(quelltext).map((spalte) => `${pfad}: ${spalte}`),
    )
    expect(falsch).toEqual([])
  })

  it('das Prüfmuster erkennt eine Textspalte und akzeptiert die Spaltenart quelle', () => {
    expect(
      spaltenMitFalscherArt("{ schluessel: 'seite', titel: 'PDF-Seite', art: 'text' }"),
    ).toHaveLength(1)
    expect(
      spaltenMitFalscherArt("{ schluessel: 'quelle', titel: 'Quelle', art: 'zahl' }"),
    ).toHaveLength(1)
    expect(
      spaltenMitFalscherArt("{ schluessel: 'quelle', titel: 'Quelle', art: 'quelle' }"),
    ).toHaveLength(0)
    expect(spaltenMitFalscherArt("{ schluessel: 'x', titel: 'Betrag', art: 'euro' }")).toHaveLength(
      0,
    )
  })
})
