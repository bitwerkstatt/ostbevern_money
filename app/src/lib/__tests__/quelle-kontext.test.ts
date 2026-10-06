// Quellenbelege der Kontextseiten (Phase 7, D-01, UI-02): die Tabellen und Kacheln von
// /rat-entscheidet (Einzelzuschüsse, „Was der Rat nicht beeinflussen kann“), /investitionen
// (Maßnahmen) und /stellenplan (Stellen nach Gruppe). Jeder Schlüssel, den diese Stellen
// aussenden, muss in `quellen.json` aufgelöst werden; keine dieser Dateien darf noch eine
// Seitenspalte mit Art `text` definieren.

import { describe, expect, it } from 'vitest'

import { baueMassnahmenTabelle, baueVorhaben } from '@/lib/investitionen'
import { findeBeleg } from '@/lib/quelle'
import { stellenNachGruppe, TEILE } from '@/lib/stellen'
import { kitaZuschuesse, nichtBeeinflussbar, weitereZuschuesse } from '@/lib/zuschuesse'

const quelltexte = import.meta.glob<string>('/src/**/*.vue', {
  query: '?raw',
  import: 'default',
  eager: true,
})

const tsQuelltexte = import.meta.glob<string>('/src/lib/*.ts', {
  query: '?raw',
  import: 'default',
  eager: true,
})

function quelltext(name: string): string {
  const treffer = Object.entries({ ...quelltexte, ...tsQuelltexte }).find(([pfad]) =>
    pfad.endsWith(`/${name}`),
  )
  if (treffer === undefined) {
    throw new Error(`Quelltext ${name} nicht gefunden`)
  }
  return treffer[1]
}

/** Eine Spaltendefinition `{ … titel: 'Quelle' | 'PDF-Seite' … art: 'text' … }` in einer Zeile. */
const SEITENSPALTE_ALS_TEXT =
  /\{[^{}]*titel:\s*['"`](?:Quelle|PDF-Seite)['"`][^{}]*art:\s*['"`]text['"`][^{}]*\}/

describe('Prüfmuster Seitenspalte als Text', () => {
  it('erkennt eine Seitenspalte mit Art text', () => {
    expect(
      SEITENSPALTE_ALS_TEXT.test("{ schluessel: 'seite', titel: 'Quelle', art: 'text' }"),
    ).toBe(true)
    expect(
      SEITENSPALTE_ALS_TEXT.test("{ schluessel: 'seite', titel: 'PDF-Seite', art: 'text' }"),
    ).toBe(true)
  })

  it('lässt eine Quelle-Spalte mit Art quelle und eine Textspalte anderen Titels zu', () => {
    expect(
      SEITENSPALTE_ALS_TEXT.test("{ schluessel: 'quelle', titel: 'Quelle', art: 'quelle' }"),
    ).toBe(false)
    expect(
      SEITENSPALTE_ALS_TEXT.test("{ schluessel: 'name', titel: 'Empfänger', art: 'text' }"),
    ).toBe(false)
  })
})

describe('/rat-entscheidet: Einzelzuschüsse', () => {
  const kita = kitaZuschuesse().posten
  const weitere = weitereZuschuesse()
  const alle = [...kita, ...weitere.transfer.posten, ...weitere.lfdZwecke.posten]

  it('jeder Zuschuss mit Seite trägt einen auflösbaren Vorberichtsschlüssel', () => {
    expect(alle.length).toBeGreaterThan(0)
    for (const z of alle) {
      expect(z.pdfSeite, z.schluessel).not.toBeNull()
      expect(z.beleg, z.schluessel).not.toBeNull()
      const beleg = findeBeleg(z.beleg ?? '')
      expect(beleg, `${z.schluessel}: ${String(z.beleg)}`).not.toBeNull()
      expect(beleg?.pdfSeite, z.schluessel).toBe(z.pdfSeite)
    }
  })

  it('die Schlüssel stammen aus der Tabelle der Gruppe', () => {
    for (const z of kita) {
      expect(z.beleg).toBe(`vb:kita_zuschuesse:${z.schluessel}`)
    }
    for (const z of weitere.transfer.posten) {
      expect(z.beleg).toBe(`vb:transferaufwendungen:${z.schluessel}`)
    }
    for (const z of weitere.lfdZwecke.posten) {
      expect(z.beleg).toBe(`vb:zuschuesse_lfd_zwecke:${z.schluessel}`)
    }
  })

  it('ZuschussListe hat eine Quelle-Spalte der Art quelle und keine Seitenspalte als Text', () => {
    const text = quelltext('ZuschussListe.vue')
    expect(text).toContain("art: 'quelle'")
    expect(SEITENSPALTE_ALS_TEXT.test(text)).toBe(false)
  })
})

describe('/rat-entscheidet: Was der Rat nicht beeinflussen kann', () => {
  const posten = nichtBeeinflussbar().posten

  it('jede Kachel trägt einen auflösbaren Schlüssel', () => {
    expect(posten.length).toBeGreaterThan(0)
    for (const p of posten) {
      expect(p.beleg, p.schluessel).not.toBeNull()
      expect(findeBeleg(p.beleg ?? ''), `${p.schluessel}: ${String(p.beleg)}`).not.toBeNull()
    }
  })

  it('die Unterposten der Weitergabe an Kreis und Land nutzen den Vorberichtsschlüssel ihres Postens', () => {
    const kl = posten.filter((p) => p.schluessel.startsWith('KL.'))
    expect(kl.length).toBeGreaterThan(0)
    for (const p of kl) {
      const vorbericht = `vb:transferaufwendungen:${p.schluessel.slice('KL.'.length)}`
      const erwartet = findeBeleg(vorbericht) === null ? `seite:${String(p.pdfSeite)}` : vorbericht
      expect(p.beleg, p.schluessel).toBe(erwartet)
    }
  })

  it('die Sozialleistungen nutzen ihren Vorberichtsschlüssel', () => {
    const sozial = posten.find((p) => p.schluessel === 'sozialleistungen')
    if (sozial !== undefined) {
      expect(sozial.beleg).toBe('vb:transferaufwendungen:sozialleistungen')
    }
  })

  it('NichtBeeinflussbarBlock bindet :quelle an die Kacheln', () => {
    expect(quelltext('NichtBeeinflussbarBlock.vue')).toContain(':quelle=')
  })
})

describe('/investitionen: Maßnahmen', () => {
  const tabelle = baueMassnahmenTabelle(baueVorhaben({ pb: null, art: null }))

  it('jede Zeile der Maßnahmentabelle trägt einen auflösbaren inv-Schlüssel', () => {
    expect(tabelle.zeilen.length).toBeGreaterThan(0)
    for (const zeile of tabelle.zeilen) {
      expect(findeBeleg(String(zeile['quelle'])), String(zeile['quelle'])).not.toBeNull()
    }
  })

  it('lib/investitionen.ts hat keine Seitenspalte mit Art text', () => {
    const text = quelltext('investitionen.ts')
    expect(text).toContain('belegSchluessel.inv')
    expect(SEITENSPALTE_ALS_TEXT.test(text)).toBe(false)
  })
})

describe('/stellenplan: Stellen nach Gruppe', () => {
  it('jede Gruppenzeile trägt einen auflösbaren sp-Schlüssel', () => {
    for (const { teil } of TEILE) {
      const zeilen = stellenNachGruppe(teil)
      expect(zeilen.length, teil).toBeGreaterThan(0)
      for (const zeile of zeilen) {
        expect(findeBeleg(zeile.beleg), zeile.beleg).not.toBeNull()
      }
    }
  })

  it('StellenNachGruppe hat eine Quelle-Spalte der Art quelle und keine Seitenspalte als Text', () => {
    const text = quelltext('StellenNachGruppe.vue')
    expect(text).toContain("art: 'quelle'")
    expect(SEITENSPALTE_ALS_TEXT.test(text)).toBe(false)
  })

  it('lib/stellen.ts baut die Schlüssel über belegSchluessel.sp', () => {
    expect(quelltext('stellen.ts')).toContain('belegSchluessel.sp')
  })
})
