import { readFileSync } from 'node:fs'

import { describe, expect, it } from 'vitest'

import {
  betragMitHinweis,
  euro,
  euroKurz,
  jahr as formatiereJahr,
  RD_PRAEFIX,
  RUND_PRAEFIX,
} from '@/charts/format'
import { haushalt, texte } from '@/data/daten'
import {
  baueGeldfluss,
  baueGeldflussBalken,
  geldflussOption,
  lesehilfeSatz,
  welcheLesetexte,
  zielCodeAusKlick,
} from '@/lib/geldfluss'
import type { Geldfluss, GeldflussKnoten } from '@/lib/geldfluss'
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

describe('Vorbericht-Beträge im Geldfluss (WR-01: „rd.“ und „berechnet“)', () => {
  const index = haushalt.jahre.indexOf(haushalt.haushaltsjahr)
  const fluss = baueGeldfluss(index)
  const nachId = (id: string) => fluss.knoten.find((k) => k.id === id)

  it('markiert die Vorbericht-Knoten als gerundet und die Reste zusätzlich als berechnet', () => {
    for (const id of ['gewerbesteuer', 'einkommensteuer', 'grundsteuer', 'schluesselzuweisung']) {
      const knoten = nachId(`ertrag:${id}`)
      expect(knoten?.gerundet, id).toBe(true)
      expect(knoten?.berechnet, id).toBe(false)
    }
    for (const id of ['uebrige_steuern', 'sonstige_zuwendungen']) {
      const knoten = nachId(`ertrag:${id}`)
      expect(knoten?.gerundet, id).toBe(true)
      expect(knoten?.berechnet, id).toBe(true)
    }
  })

  it('lässt Ergebnisplan-Knoten ohne Hinweis', () => {
    for (const knoten of fluss.knoten) {
      if (['entgelte', 'sonstige_ertraege', 'finanzertraege'].some((i) => knoten.id.endsWith(i))) {
        expect(knoten.gerundet, knoten.id).toBe(false)
      }
      if (knoten.seite === 'rechts' || knoten.seite === 'mitte') {
        expect(knoten.gerundet, knoten.id).toBe(false)
      }
    }
  })

  it('zeigt gerundete Beträge im Tooltip mit „rd.“', () => {
    const option = geldflussOption(fluss, { wertartText: 'Ansatz 2026' })
    const tooltip = option.tooltip as { formatter: (params: unknown) => string }
    const knoten = nachId('ertrag:gewerbesteuer')
    expect(tooltip.formatter({ dataType: 'node', name: knoten?.id })).toContain(RD_PRAEFIX)
    const ziel = fluss.knoten.find((k) => k.art === 'kl')
    expect(tooltip.formatter({ dataType: 'node', name: ziel?.id })).not.toContain(RD_PRAEFIX)
  })

  it('zeigt Kanten mit „rd.“, wenn der Ertragsknoten gerundet ist, und sonst ohne', () => {
    const option = geldflussOption(fluss, { wertartText: 'Ansatz 2026' })
    const tooltip = option.tooltip as { formatter: (params: unknown) => string }
    const kantenTooltip = (quelle: string, ziel: string) => {
      const kante = fluss.kanten.find((k) => k.quelle === quelle && k.ziel === ziel)
      expect(kante, `${quelle} → ${ziel}`).toBeDefined()
      return {
        html: tooltip.formatter({
          dataType: 'edge',
          data: { source: kante?.quelle, target: kante?.ziel, value: kante?.wert },
        }),
        wert: kante?.wert ?? Number.NaN,
      }
    }
    // Ertrag (gerundet) → Gemeinde: Kante erbt das Flag des Ertragsknotens (links).
    expect(kantenTooltip('ertrag:gewerbesteuer', 'mitte:gemeinde').html).toContain(RD_PRAEFIX)
    // Gemeinde → Kreisumlage (Ergebnisplan-Wert): Kante erbt das Flag des Zielknotens (rechts).
    const kl = fluss.knoten.find((k) => k.art === 'kl')
    expect(kl?.gerundet).toBe(false)
    const klKante = kantenTooltip('mitte:gemeinde', kl?.id ?? '')
    expect(klKante.html).not.toContain(RD_PRAEFIX)
    // 05/IN-03: nicht nur „kein rd.“, sondern positiv der Betrag der Kante im Tooltip.
    expect(klKante.wert).toBeGreaterThan(0)
    expect(klKante.html).toContain(euro(klKante.wert))
  })

  it('übernimmt die Flags in die Balkensegmente', () => {
    const balken = baueGeldflussBalken(fluss)
    const segment = balken.woher.find((s) => s.id === 'ertrag:uebrige_steuern')
    expect(segment?.gerundet).toBe(true)
    expect(segment?.berechnet).toBe(true)
  })

  it('betragMitHinweis (aus charts/format) setzt „rd.“ nur bei gerundeten Beträgen', () => {
    expect(betragMitHinweis(7_800_000, true)).toBe(`${RD_PRAEFIX}${euro(7_800_000)}`)
    expect(betragMitHinweis(7_800_000, false)).toBe(euro(7_800_000))
  })

  it('beschriftet gerundete Knoten im Diagramm mit „rd.“ vor dem gekürzten Betrag', () => {
    const option = geldflussOption(fluss, { wertartText: 'Ansatz 2026' })
    const serie = (option.series as unknown[])[0] as {
      label: { formatter: (params: unknown) => string }
    }
    const knoten = nachId('ertrag:gewerbesteuer')
    expect(serie.label.formatter({ name: knoten?.id })).toContain(RD_PRAEFIX)
    const ziel = fluss.knoten.find((k) => k.art === 'kl')
    expect(serie.label.formatter({ name: ziel?.id })).not.toContain(RD_PRAEFIX)
  })
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

// Echte Jahre erreichen nur die Fälle A und B; C und D entstehen hier aus konstruierten Flüssen
// (CONTEXT-Datentabelle). `genau` darf nur in Fall D stehen (TXT-01, 05/IN-06).
describe('lesehilfeSatz: vier Fälle der Bilanz (D-06, TXT-01, 05/IN-06)', () => {
  function knoten(
    art: GeldflussKnoten['art'],
    wert: number,
    seite: GeldflussKnoten['seite'],
    gerundet = false,
  ): GeldflussKnoten {
    return {
      id: `test:${art}`,
      name: art,
      wert,
      seite,
      art,
      code: null,
      farbe: '#000',
      gerundet,
      berechnet: false,
    }
  }

  function fluss(knotenListe: GeldflussKnoten[], pdfSeite: number | null = 51): Geldfluss {
    const links = knotenListe.filter((k) => k.seite === 'links').reduce((s, k) => s + k.wert, 0)
    const rechts = knotenListe.filter((k) => k.seite === 'rechts').reduce((s, k) => s + k.wert, 0)
    return { knoten: knotenListe, kanten: [], summeLinks: links, summeRechts: rechts, pdfSeite }
  }

  const ERTRAG = knoten('ertrag', 29_855_569, 'links')

  it('Fall A: Defizit und Minderaufwand links, ohne „genau“', () => {
    const satz = lesehilfeSatz(
      fluss([
        ERTRAG,
        knoten('defizit', 1_000_000, 'links'),
        knoten('minderaufwand', 600_000, 'links'),
      ]),
      2026,
      'Ansatz',
    )
    expect(satz).toContain(`Das Defizit von ${euro(1_000_000)}`)
    expect(satz).toContain('steht ebenfalls links')
    expect(satz).toContain(`Der globale Minderaufwand von ${euro(600_000)}`)
    expect(satz).not.toContain('genau')
  })

  it('Fall B: Überschuss rechts und Minderaufwand links, Minderaufwand-Satz ohne „ebenfalls“', () => {
    const satz = lesehilfeSatz(
      fluss([
        ERTRAG,
        knoten('minderaufwand', 600_000, 'links'),
        knoten('ueberschuss', 200_000, 'rechts'),
      ]),
      2026,
      'Ansatz',
    )
    expect(satz).toContain(`Der globale Minderaufwand von ${euro(600_000)}`)
    expect(satz).toContain(`Der Überschuss von ${euro(200_000)}`)
    expect(satz).not.toContain('ebenfalls')
    expect(satz).not.toContain('genau')
  })

  it('Fall C: nur der Minderaufwand gleicht aus, die Lesehilfe sagt nicht „genau“', () => {
    const satz = lesehilfeSatz(
      fluss([ERTRAG, knoten('minderaufwand', 600_000, 'links')]),
      2026,
      'Ansatz',
    )
    expect(satz).toContain(
      `Die Aufwendungen sind höher als die Erträge. Erst der globale Minderaufwand von ${euro(600_000)} gleicht beide Seiten aus.`,
    )
    expect(satz).toContain('Er steht links und senkt die geplanten Aufwendungen rechnerisch')
    expect(satz).not.toContain('genau')
    expect(satz).not.toContain('ebenfalls')
    expect(satz).not.toContain(`${RUND_PRAEFIX}${euro(600_000)}`)
  })

  it('Fall C: „rund“ steht vor dem Minderaufwand nur bei einem gerundeten Betrag', () => {
    const satz = lesehilfeSatz(
      fluss([ERTRAG, knoten('minderaufwand', 600_000, 'links', true)]),
      2026,
      'Ansatz',
    )
    expect(satz).toContain(
      `Erst der globale Minderaufwand von ${RUND_PRAEFIX}${euro(600_000)} gleicht`,
    )
  })

  it('Fall D: nur hier „genau“', () => {
    const satz = lesehilfeSatz(fluss([ERTRAG]), 2026, 'Ansatz')
    expect(satz).toContain('Erträge und Aufwendungen gleichen sich in diesem Jahr genau aus.')
    expect(satz).not.toContain('Minderaufwand')
  })

  it.each([
    [
      'A',
      [ERTRAG, knoten('defizit', 1_000_000, 'links'), knoten('minderaufwand', 600_000, 'links')],
    ],
    ['B', [ERTRAG, knoten('minderaufwand', 600_000, 'links'), knoten('ueberschuss', 1, 'rechts')]],
    ['C', [ERTRAG, knoten('minderaufwand', 600_000, 'links')]],
    ['D', [ERTRAG]],
  ])(
    'Fall %s: Satz 1 nennt „rund“ mit geschütztem Leerzeichen, am Ende die Quelle',
    (_fall, liste) => {
      const modell = fluss(liste)
      const satz = lesehilfeSatz(modell, 2026, 'Ansatz')
      expect(satz).toContain(`${RUND_PRAEFIX}${euroKurz(modell.summeLinks)}`)
      expect(satz.endsWith('Quelle: PDF-Seite 51.')).toBe(true)
    },
  )

  it('„genau“ steht in keinem echten Jahr', () => {
    for (const [jahr, index] of ALLE_JAHRE) {
      expect(lesehilfeSatz(baueGeldfluss(index), jahr, 'Ansatz'), String(jahr)).not.toContain(
        'genau',
      )
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
