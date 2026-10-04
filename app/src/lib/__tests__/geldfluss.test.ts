import { readFileSync } from 'node:fs'

import { describe, expect, it } from 'vitest'

import { euro, jahr as formatiereJahr } from '@/charts/format'
import { haushalt, texte } from '@/data/daten'
import {
  baueGeldfluss,
  baueGeldflussBalken,
  geldflussOption,
  lesehilfeSatz,
  welcheLesetexte,
  zielCodeAusKlick,
} from '@/lib/geldfluss'
import type { Geldfluss } from '@/lib/geldfluss'
import { findeKlKnoten } from '@/lib/kreisumlage'
import { findeText, textFuerJahr } from '@/lib/texte'

const GESAMT = haushalt.ergebnisplan.GESAMT
const ALLE_JAHRE = haushalt.jahre.map((jahr, index) => [jahr, index] as const)

function zeile(schluessel: string, index: number): number {
  const wert = GESAMT?.zeilen[schluessel]?.[index]
  if (wert === undefined) {
    throw new Error(`Zeile ${schluessel} fehlt im Jahresindex ${String(index)}`)
  }
  return wert
}

function summe(fluss: Geldfluss, seite: 'links' | 'rechts'): number {
  return fluss.knoten.filter((k) => k.seite === seite).reduce((s, k) => s + k.wert, 0)
}

describe('baueGeldfluss: Bilanz in jedem Jahr (D-11, D-19, FLUSS-02)', () => {
  it.each(ALLE_JAHRE)(
    'Jahr %i: linke und rechte Summe sind gleich (±2 €), kein Knoten mit Wert ≤ 0',
    (_jahr, index) => {
      const fluss = baueGeldfluss(index)
      expect(fluss.knoten.length).toBeGreaterThan(0)
      expect(Math.abs(summe(fluss, 'links') - summe(fluss, 'rechts'))).toBeLessThanOrEqual(2)
      expect(fluss.summeLinks).toBe(summe(fluss, 'links'))
      expect(fluss.summeRechts).toBe(summe(fluss, 'rechts'))
      for (const knoten of fluss.knoten) {
        expect(knoten.wert, knoten.id).toBeGreaterThan(0)
        expect(Number.isInteger(knoten.wert), knoten.id).toBe(true)
      }
    },
  )

  it.each(ALLE_JAHRE)(
    'Jahr %i: Defizit, Überschuss und Minderaufwand stehen genau dann da, wenn ihre Bedingung gilt',
    (_jahr, index) => {
      const fluss = baueGeldfluss(index)
      const nachAbzug = zeile('ergebnis_nach_minderaufwand', index)
      const minder = zeile('globaler_minderaufwand', index)
      const defizit = fluss.knoten.find((k) => k.art === 'defizit')
      const ueberschuss = fluss.knoten.find((k) => k.art === 'ueberschuss')
      const minderaufwand = fluss.knoten.find((k) => k.art === 'minderaufwand')

      expect(defizit !== undefined).toBe(nachAbzug < 0)
      expect(ueberschuss !== undefined).toBe(nachAbzug > 0)
      expect(minderaufwand !== undefined).toBe(minder !== 0)
      expect(defizit?.wert).toBe(nachAbzug < 0 ? -nachAbzug : undefined)
      expect(ueberschuss?.wert).toBe(nachAbzug > 0 ? nachAbzug : undefined)
      expect(minderaufwand?.wert).toBe(minder !== 0 ? -minder : undefined)
      // Defizit und Minderaufwand sind linke Quellen, der Überschuss steht rechts (D-19).
      expect(defizit?.seite ?? 'links').toBe('links')
      expect(minderaufwand?.seite ?? 'links').toBe('links')
      expect(ueberschuss?.seite ?? 'rechts').toBe('rechts')
    },
  )

  it.each(ALLE_JAHRE)(
    'Jahr %i: rechte Seite = KL, jeder Aufgabenbereich mit Z. 17 > 0 und Zinsen',
    (_jahr, index) => {
      const fluss = baueGeldfluss(index)
      const kl = findeKlKnoten()
      const erwartet = haushalt.knoten
        .filter((k) => k.ebene === 'PB' && k.eltern === 'GESAMT' && !k.synthetisch)
        .filter(
          (k) => (haushalt.ergebnisplan[k.code]?.zeilen.ordentliche_aufwendungen?.[index] ?? 0) > 0,
        )
        .map((k) => k.code)

      const pb = fluss.knoten.filter((k) => k.art === 'pb').map((k) => k.code)
      expect(pb).toEqual(erwartet)
      expect(fluss.knoten.filter((k) => k.art === 'kl').map((k) => k.code)).toEqual([kl.code])
      const zinsen = fluss.knoten.filter((k) => k.art === 'zinsen')
      expect(zinsen).toHaveLength(zeile('zinsaufwendungen', index) > 0 ? 1 : 0)
      expect(zinsen[0]?.wert).toBe(zeile('zinsaufwendungen', index))
      // Wert eines Aufgabenbereichs ist seine Z. 17, nicht sein Aufwand inklusive Zinsen.
      for (const knoten of fluss.knoten.filter((k) => k.art === 'pb' || k.art === 'kl')) {
        const z17 =
          haushalt.ergebnisplan[knoten.code ?? '']?.zeilen.ordentliche_aufwendungen?.[index]
        expect(knoten.wert, knoten.id).toBe(z17)
      }
    },
  )

  it.each(ALLE_JAHRE)(
    'Jahr %i: linke Ertragsknoten ergeben Erträge Z. 10 plus Finanzerträge Z. 19',
    (_jahr, index) => {
      const fluss = baueGeldfluss(index)
      const ertraege = fluss.knoten
        .filter((k) => k.art === 'steuer' || k.art === 'ertrag')
        .reduce((s, k) => s + k.wert, 0)
      expect(ertraege).toBe(zeile('ordentliche_ertraege', index) + zeile('finanzertraege', index))
    },
  )

  it.each(ALLE_JAHRE)(
    'Jahr %i: Kanten verbinden nur links→Mitte und Mitte→rechts',
    (_jahr, index) => {
      const fluss = baueGeldfluss(index)
      const nachId = new Map(fluss.knoten.map((k) => [k.id, k]))
      expect(nachId.size).toBe(fluss.knoten.length)

      const mitte = fluss.knoten.filter((k) => k.seite === 'mitte')
      expect(mitte).toHaveLength(1)
      const mitteId = mitte[0]?.id

      let hinein = 0
      let hinaus = 0
      for (const kante of fluss.kanten) {
        const quelle = nachId.get(kante.quelle)
        const ziel = nachId.get(kante.ziel)
        expect(quelle, kante.quelle).toBeDefined()
        expect(ziel, kante.ziel).toBeDefined()
        expect(kante.wert).toBeGreaterThan(0)
        if (quelle?.seite === 'links') {
          expect(ziel?.id).toBe(mitteId)
          expect(kante.wert).toBe(quelle.wert)
          hinein += kante.wert
        } else {
          expect(quelle?.id).toBe(mitteId)
          expect(ziel?.seite).toBe('rechts')
          expect(kante.wert).toBe(ziel?.wert)
          hinaus += kante.wert
        }
      }
      expect(Math.abs(hinein - hinaus)).toBeLessThanOrEqual(2)
    },
  )

  it.each(ALLE_JAHRE)(
    'Jahr %i: nur Aufgabenbereiche und KL tragen ein Klickziel (D-10)',
    (_jahr, index) => {
      const fluss = baueGeldfluss(index)
      const codes = new Set(haushalt.knoten.map((k) => k.code))
      for (const knoten of fluss.knoten) {
        if (knoten.art === 'pb' || knoten.art === 'kl') {
          expect(knoten.code, knoten.id).not.toBeNull()
          expect(codes.has(knoten.code ?? ''), knoten.id).toBe(true)
        } else {
          expect(knoten.code, knoten.id).toBeNull()
        }
      }
    },
  )
})

describe('zielCodeAusKlick', () => {
  const fluss = baueGeldfluss(haushalt.jahre.indexOf(haushalt.haushaltsjahr))

  it('liefert den Code eines Aufgabenbereichs- oder KL-Knotens', () => {
    for (const knoten of fluss.knoten.filter((k) => k.art === 'pb' || k.art === 'kl')) {
      expect(zielCodeAusKlick({ dataType: 'node', name: knoten.id }, fluss)).toBe(knoten.code)
    }
  })

  it('liefert null für Ertragsknoten, Kanten und unbrauchbare Eingaben', () => {
    for (const knoten of fluss.knoten.filter((k) => k.code === null)) {
      expect(zielCodeAusKlick({ dataType: 'node', name: knoten.id }, fluss), knoten.id).toBeNull()
    }
    const kante = fluss.kanten[0]
    expect(
      zielCodeAusKlick(
        { dataType: 'edge', name: 'x', data: { source: kante?.quelle, target: kante?.ziel } },
        fluss,
      ),
    ).toBeNull()
    for (const roh of [null, undefined, 'x', 7, [], {}, { dataType: 'node' }]) {
      expect(zielCodeAusKlick(roh, fluss)).toBeNull()
    }
    expect(zielCodeAusKlick({ dataType: 'node', name: '__proto__' }, fluss)).toBeNull()
    expect(zielCodeAusKlick({ dataType: 'node', name: 'constructor' }, fluss)).toBeNull()
  })
})

describe('geldflussOption', () => {
  const fluss = baueGeldfluss(haushalt.jahre.indexOf(haushalt.haushaltsjahr))
  const option = geldflussOption(fluss, { wertartText: 'Ansatz 2026' })
  const serie = (option.series as unknown[])[0] as Record<string, unknown>

  it('beschreibt einen Sankey mit den Maßen aus der UI-SPEC', () => {
    expect(serie.type).toBe('sankey')
    expect(serie.nodeWidth).toBe(16)
    expect(serie.nodeGap).toBe(8)
    expect(serie.draggable).toBe(false)
    expect(serie.emphasis).toMatchObject({ focus: 'adjacency' })
    expect(serie.lineStyle).toMatchObject({ color: 'source', opacity: 0.35 })
    expect(serie.label).toMatchObject({ width: 160, overflow: 'break' })
  })

  it('enthält je Knoten und Kante genau einen Eintrag mit eindeutigen Namen', () => {
    const data = serie.data as { name: string }[]
    const links = serie.links as { source: string; target: string; value: number }[]
    expect(data).toHaveLength(fluss.knoten.length)
    expect(new Set(data.map((d) => d.name)).size).toBe(data.length)
    expect(links).toHaveLength(fluss.kanten.length)
  })

  it('maskiert Namen im Tooltip (T-05-33)', () => {
    const boese: Geldfluss = {
      ...fluss,
      knoten: fluss.knoten.map((k, i) =>
        i === 0 ? { ...k, name: '<img src=x onerror=alert(1)>' } : k,
      ),
    }
    const tooltip = geldflussOption(boese, { wertartText: 'Ansatz 2026' }).tooltip as {
      formatter: (params: unknown) => string
    }
    const erster = boese.knoten[0]
    const html = tooltip.formatter({ dataType: 'node', name: erster?.id })
    expect(html).not.toContain('<img')
    expect(html).toContain('&lt;img')
    expect(html).toContain('Ansatz 2026')
    const kante = boese.kanten.find((k) => k.quelle === erster?.id)
    const kantenHtml = tooltip.formatter({
      dataType: 'edge',
      data: { source: kante?.quelle, target: kante?.ziel, value: kante?.wert },
    })
    expect(kantenHtml).not.toContain('<img')
  })

  it('liefert für leere Flüsse leere Daten, damit BaseChart den Leerzustand zeigt', () => {
    const leer: Geldfluss = { ...fluss, knoten: [], kanten: [], summeLinks: 0, summeRechts: 0 }
    const leereSerie = (geldflussOption(leer, { wertartText: '' }).series as unknown[])[0] as {
      data: unknown[]
      links: unknown[]
    }
    expect(leereSerie.data).toHaveLength(0)
    expect(leereSerie.links).toHaveLength(0)
  })
})

describe('geldfluss.ts: Verbote (T-05-32)', () => {
  const quelltext = readFileSync(new URL('../geldfluss.ts', import.meta.url), 'utf8')

  it('mischt keine Finanzplan-Werte ein (Sankey nur Ergebnisplan)', () => {
    expect(quelltext).not.toContain('finanzplan')
  })

  it('enthält kein Aufgabenbereichs-Code-Literal und kein Jahres-Sonderfall', () => {
    expect(quelltext).not.toMatch(/'(0[1-9]|1[0-6])'/)
    expect(quelltext).not.toMatch(/\b20[2-3]\d\b/)
  })
})

describe.runIf(haushalt.haushaltsjahr === 2026)('Geldfluss Haushalt 2026 (D-11, D-19)', () => {
  it('2026: Defizit 2.353.506 €, Minderaufwand 600.000 €, Summe 30.455.569 €', () => {
    const fluss = baueGeldfluss(haushalt.jahre.indexOf(2026))
    expect(fluss.knoten.find((k) => k.art === 'defizit')?.wert).toBe(2353506)
    expect(fluss.knoten.find((k) => k.art === 'minderaufwand')?.wert).toBe(600000)
    expect(fluss.knoten.find((k) => k.art === 'ueberschuss')).toBeUndefined()
    expect(summe(fluss, 'links')).toBe(30455569)
    expect(summe(fluss, 'rechts')).toBe(30455569)
  })

  it('2024: Überschuss 191.990 € rechts, kein Minderaufwand', () => {
    const fluss = baueGeldfluss(haushalt.jahre.indexOf(2024))
    const ueberschuss = fluss.knoten.find((k) => k.art === 'ueberschuss')
    expect(ueberschuss?.wert).toBe(191990)
    expect(ueberschuss?.seite).toBe('rechts')
    expect(fluss.knoten.find((k) => k.art === 'minderaufwand')).toBeUndefined()
    expect(fluss.knoten.find((k) => k.art === 'defizit')).toBeUndefined()
  })
})

describe('baueGeldflussBalken: Mobil-Alternative (D-12, D-19, FLUSS-04)', () => {
  it.each(ALLE_JAHRE)(
    'Jahr %i: beide Balken haben dieselbe Summe (±2 €), Segmente in den Knotenfarben',
    (_jahr, index) => {
      const fluss = baueGeldfluss(index)
      const balken = baueGeldflussBalken(fluss)

      expect(balken.woher.map((s) => s.id)).toEqual(
        fluss.knoten.filter((k) => k.seite === 'links').map((k) => k.id),
      )
      expect(balken.wohin.map((s) => s.id)).toEqual(
        fluss.knoten.filter((k) => k.seite === 'rechts').map((k) => k.id),
      )
      const summeWoher = balken.woher.reduce((s, x) => s + x.wert, 0)
      const summeWohin = balken.wohin.reduce((s, x) => s + x.wert, 0)
      expect(balken.summeWoher).toBe(summeWoher)
      expect(balken.summeWohin).toBe(summeWohin)
      expect(Math.abs(summeWoher - summeWohin)).toBeLessThanOrEqual(2)

      const nachId = new Map(fluss.knoten.map((k) => [k.id, k] as const))
      for (const segment of [...balken.woher, ...balken.wohin]) {
        const knoten = nachId.get(segment.id)
        expect(segment.farbe, segment.id).toBe(knoten?.farbe)
        expect(segment.decal, segment.id).toBe(knoten?.decal)
        expect(segment.code, segment.id).toBe(knoten?.code)
        expect(segment.wert, segment.id).toBeGreaterThan(0)
      }
      expect(balken.woher.reduce((s, x) => s + (x.anteil ?? 0), 0)).toBeCloseTo(1, 6)
      expect(balken.wohin.reduce((s, x) => s + (x.anteil ?? 0), 0)).toBeCloseTo(1, 6)
    },
  )

  it.each(ALLE_JAHRE)(
    'Jahr %i: Defizit und Minderaufwand stehen in „Woher“, der Überschuss in „Wohin“',
    (_jahr, index) => {
      const balken = baueGeldflussBalken(baueGeldfluss(index))
      expect(balken.wohin.some((s) => s.art === 'defizit' || s.art === 'minderaufwand')).toBe(false)
      expect(balken.woher.some((s) => s.art === 'ueberschuss')).toBe(false)
      const nachAbzug = zeile('ergebnis_nach_minderaufwand', index)
      expect(balken.wohin.some((s) => s.art === 'ueberschuss')).toBe(nachAbzug > 0)
      expect(balken.woher.some((s) => s.art === 'defizit')).toBe(nachAbzug < 0)
    },
  )
})

describe('lesehilfeSatz: Satz aus den Daten des gewählten Jahres (D-11, T-05-34)', () => {
  it.each(ALLE_JAHRE)('Jahr %i: nennt die Beträge des Jahres und die PDF-Seite', (jahr, index) => {
    const fluss = baueGeldfluss(index)
    const satz = lesehilfeSatz(fluss, jahr, 'Ansatz')
    expect(satz).not.toMatch(/NaN|undefined|\{\{|Infinity|null/)
    expect(satz).toContain(formatiereJahr(jahr))
    expect(satz).toContain(`PDF-Seite ${String(fluss.pdfSeite)}`)

    const defizit = fluss.knoten.find((k) => k.art === 'defizit')
    const ueberschuss = fluss.knoten.find((k) => k.art === 'ueberschuss')
    const minderaufwand = fluss.knoten.find((k) => k.art === 'minderaufwand')
    if (defizit) {
      expect(satz).toContain('Defizit')
      expect(satz).toContain(euro(defizit.wert))
    } else {
      expect(satz).not.toContain('Defizit')
    }
    if (ueberschuss) {
      expect(satz).toContain('Überschuss')
      expect(satz).toContain(euro(ueberschuss.wert))
    } else {
      expect(satz).not.toContain('Überschuss')
    }
    if (minderaufwand) {
      expect(satz).toContain('Minderaufwand')
      expect(satz).toContain(euro(minderaufwand.wert))
    } else {
      expect(satz).not.toContain('Minderaufwand')
    }
  })

  it('der Defizitbetrag eines Jahres erscheint nicht im Satz eines anderen Jahres', () => {
    const fluesse = ALLE_JAHRE.map(([jahr, index]) => ({ jahr, fluss: baueGeldfluss(index) }))
    for (const a of fluesse) {
      const defizit = a.fluss.knoten.find((k) => k.art === 'defizit')
      if (!defizit) {
        continue
      }
      for (const b of fluesse) {
        const andereDefizit = b.fluss.knoten.find((k) => k.art === 'defizit')?.wert
        if (b.jahr !== a.jahr && andereDefizit !== defizit.wert) {
          expect(lesehilfeSatz(b.fluss, b.jahr, 'Ansatz')).not.toContain(euro(defizit.wert))
        }
      }
    }
  })
})

describe('welcheLesetexte: jahrpassende Erklärtexte (D-11, Pitfall 6, T-05-34)', () => {
  it.each(ALLE_JAHRE)(
    'Jahr %i: wählt die Texte nach Defizit/Überschuss und Haushaltsjahr',
    (jahr, index) => {
      const fluss = baueGeldfluss(index)
      const schluessel = welcheLesetexte(jahr, fluss)
      const hatDefizit = fluss.knoten.some((k) => k.art === 'defizit')
      const hatUeberschuss = fluss.knoten.some((k) => k.art === 'ueberschuss')

      expect(schluessel[0]).toBe('geldfluss_lesehilfe')
      expect(schluessel.includes('defizit_ruecklagen')).toBe(
        hatDefizit && jahr === texte.haushaltsjahr,
      )
      expect(schluessel.includes('ueberschuss_ruecklage')).toBe(hatUeberschuss)
      for (const eintrag of schluessel) {
        expect(findeText(eintrag), eintrag).toBeDefined()
        expect(textFuerJahr(eintrag, jahr), eintrag).not.toBeNull()
      }
    },
  )
})
