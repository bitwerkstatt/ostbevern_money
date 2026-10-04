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
