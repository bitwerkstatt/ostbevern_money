import { describe, expect, it } from 'vitest'

import { abstufung, farbeFuerPb, KL_DECAL, KL_FARBE, PUNKT_DECAL } from '@/charts/echartsTheme'
import { euroKurz } from '@/charts/format'
import { haushalt } from '@/data/daten'
import {
  baueBrotkrumen,
  baueEbene,
  codeAusParams,
  ebenenElternCode,
  eintragTooltip,
  kachelBeschriftet,
  kinderVon,
  klickZiel,
  ueberschussTextSchluessel,
  zuschussBalkenHoehe,
  zuschussBalkenOption,
  type EbenenEintrag,
} from '@/lib/drilldown'
import { findeProdukt } from '@/lib/ansicht'
import { findeText, rendereAbsatz } from '@/lib/texte'

const JAHRE = haushalt.jahre.map((j, i) => [j, i] as const)
const MIT_KINDERN = haushalt.knoten.filter((k) => haushalt.knoten.some((c) => c.eltern === k.code))

function aufwand(code: string, i: number): number {
  const wert = haushalt.ergebnisplan[code]?.berechnet.aufwand[i]
  if (wert === undefined) {
    throw new Error(`kein Aufwand für ${code}`)
  }
  return wert
}

function zuschuss(code: string, i: number): number {
  const wert = haushalt.ergebnisplan[code]?.berechnet.zuschussbedarf[i]
  if (wert === undefined) {
    throw new Error(`kein Zuschussbedarf für ${code}`)
  }
  return wert
}

describe('baueEbene: oberste Ebene (AUSG-01)', () => {
  it.each(JAHRE)(
    'Jahr %i: ein Eintrag je Kind von GESAMT, absteigend, Summe = Gesamtaufwand',
    (_j, i) => {
      const ebene = baueEbene('GESAMT', i, 'aufwand')
      const erwartet = haushalt.knoten.filter((k) => k.eltern === 'GESAMT')
      expect(ebene).toHaveLength(erwartet.length)
      expect(new Set(ebene.map((e) => e.code))).toEqual(new Set(erwartet.map((k) => k.code)))
      for (let n = 1; n < ebene.length; n++) {
        expect(ebene[n - 1]?.wert ?? 0).toBeGreaterThanOrEqual(ebene[n]?.wert ?? 0)
      }
      const summe = ebene.reduce((s, e) => s + e.wert, 0)
      expect(Math.abs(summe - aufwand('GESAMT', i))).toBeLessThanOrEqual(2)
    },
  )

  it('enthält die 15 Aufgabenbereiche und die Weitergabe an Kreis und Land', () => {
    const ebene = baueEbene('GESAMT', 0, 'aufwand')
    expect(ebene.filter((e) => e.istKl)).toHaveLength(1)
    expect(ebene.filter((e) => !e.istKl).length).toBe(ebene.length - 1)
  })
})

describe('baueEbene: Kinder summieren sich zum Elternknoten', () => {
  it.each(JAHRE)('Jahr %i: Σ Kinder = Eltern (±2 €, KL ±3.000 €)', (_j, i) => {
    for (const eltern of MIT_KINDERN) {
      const ebene = baueEbene(eltern.code, i, 'aufwand')
      const summe = ebene.reduce((s, e) => s + e.wert, 0)
      const toleranz = eltern.code === 'KL' ? 3000 : 2
      expect(Math.abs(summe - aufwand(eltern.code, i)), eltern.code).toBeLessThanOrEqual(toleranz)
    }
  })

  it('lässt Einträge mit Wert 0 weg', () => {
    for (const [, i] of JAHRE) {
      for (const eltern of MIT_KINDERN) {
        for (const modus of ['aufwand', 'zuschussbedarf'] as const) {
          expect(baueEbene(eltern.code, i, modus).every((e) => e.wert !== 0)).toBe(true)
        }
      }
    }
  })
})

describe('baueEbene: Modus Zuschussbedarf (AUSG-03, D-05)', () => {
  it.each(JAHRE)('Jahr %i: Wert und Überschuss stammen unverändert aus berechnet', (_j, i) => {
    for (const eltern of [{ code: 'GESAMT' }, ...MIT_KINDERN]) {
      for (const eintrag of baueEbene(eltern.code, i, 'zuschussbedarf')) {
        expect(eintrag.wert, eintrag.code).toBe(zuschuss(eintrag.code, i))
        expect(eintrag.ueberschuss, eintrag.code).toBe(
          haushalt.ergebnisplan[eintrag.code]?.berechnet.ueberschuss[i],
        )
        expect(eintrag.ueberschuss, eintrag.code).toBe(eintrag.wert < 0)
      }
    }
  })

  it('führt Überschüsse als negative Einträge ohne Anteil und rechnet den Anteil nur über positive Werte', () => {
    for (const [, i] of JAHRE) {
      const ebene = baueEbene('GESAMT', i, 'zuschussbedarf')
      const positive = ebene.filter((e) => e.wert > 0)
      const summe = positive.reduce((s, e) => s + e.wert, 0)
      for (const e of ebene) {
        if (e.ueberschuss) {
          expect(e.anteil, e.code).toBeNull()
        } else {
          expect(e.anteil, e.code).toBeCloseTo(e.wert / summe, 10)
        }
      }
      expect(positive.reduce((s, e) => s + (e.anteil ?? 0), 0)).toBeCloseTo(1, 10)
    }
  })

  it('markiert im Modus Aufwand nie einen Überschuss', () => {
    for (const [, i] of JAHRE) {
      expect(baueEbene('GESAMT', i, 'aufwand').some((e) => e.ueberschuss)).toBe(false)
    }
  })

  it('zeigt die Aufgabenbereiche mit Überschuss in den Daten als negative Einträge', () => {
    const i = haushalt.jahre.indexOf(haushalt.haushaltsjahr)
    const negativ = baueEbene('GESAMT', i, 'zuschussbedarf').filter((e) => e.wert < 0)
    expect(negativ.length).toBeGreaterThan(0)
    for (const e of negativ) {
      expect(haushalt.ergebnisplan[e.code]?.berechnet.zuschussbedarf[i]).toBeLessThan(0)
    }
  })
})

describe('baueEbene: Anteile im Modus Aufwand', () => {
  it('summieren sich je Ebene zu 100 %', () => {
    for (const [, i] of JAHRE) {
      for (const eltern of [{ code: 'GESAMT' }, ...MIT_KINDERN]) {
        const ebene = baueEbene(eltern.code, i, 'aufwand')
        if (ebene.length === 0) {
          continue
        }
        expect(
          ebene.reduce((s, e) => s + (e.anteil ?? 0), 0),
          eltern.code,
        ).toBeCloseTo(1, 10)
      }
    }
  })
})

describe('baueEbene: Farben (D-08)', () => {
  const i = haushalt.jahre.indexOf(haushalt.haushaltsjahr)

  it('Aufgabenbereiche tragen ihre Palettenfarbe', () => {
    for (const e of baueEbene('GESAMT', i, 'aufwand')) {
      expect(e.farbe, e.code).toBe(farbeFuerPb(e.code))
    }
  })

  it('Kinder nutzen die abgestufte Farbe ihres Aufgabenbereichs nach Rang', () => {
    for (const bereich of haushalt.knoten.filter((k) => k.eltern === 'GESAMT')) {
      baueEbene(bereich.code, i, 'aufwand').forEach((kind, rang) => {
        expect(kind.farbe, kind.code).toBe(abstufung(farbeFuerPb(bereich.code), rang))
      })
    }
  })

  it('KL und seine Unterposten tragen KL_DECAL, alle anderen keins', () => {
    for (const e of baueEbene('GESAMT', i, 'aufwand')) {
      expect(e.decal, e.code).toBe(e.istKl ? KL_DECAL : undefined)
    }
    const kinder = baueEbene('KL', i, 'aufwand')
    expect(kinder.length).toBeGreaterThan(0)
    for (const e of kinder) {
      expect(e.istKl).toBe(true)
      expect(e.decal).toBe(KL_DECAL)
    }
    const kl = baueEbene('GESAMT', i, 'aufwand').find((e) => e.istKl)
    expect(kl?.farbe).toBe(KL_FARBE)
  })
})

describe('klickZiel (D-06, D-08)', () => {
  const i = haushalt.jahre.indexOf(haushalt.haushaltsjahr)

  it('öffnet Knoten mit Kindern, auch KL', () => {
    for (const e of baueEbene('GESAMT', i, 'aufwand')) {
      expect(klickZiel(e), e.code).toBe('drill')
    }
  })

  it('verweist Produkte auf ihre Seite', () => {
    const produkte = haushalt.knoten.filter((k) => k.ebene === 'P' && k.eltern !== null)
    expect(produkte.length).toBeGreaterThan(0)
    for (const produkt of produkte) {
      const eintrag = baueEbene(produkt.eltern ?? '', i, 'aufwand').find(
        (e) => e.code === produkt.code,
      )
      if (eintrag !== undefined) {
        expect(klickZiel(eintrag), produkt.code).toBe('produkt')
      }
    }
  })

  it('führt aus KL-Unterposten nirgendwohin', () => {
    for (const e of baueEbene('KL', i, 'aufwand')) {
      expect(klickZiel(e), e.code).toBe('keins')
    }
  })

  it('zu jedem Produkt-Eintrag gibt es ein Produkt mit Seite', () => {
    for (const k of haushalt.knoten.filter((n) => n.ebene === 'P')) {
      expect(findeProdukt(k.code), k.code).toBeDefined()
    }
  })
})

describe('Eingabeschutz (T-05-26)', () => {
  it.each(['__proto__', 'constructor', 'toString', 'gibt-es-nicht', ''])(
    'baueEbene wirft für %j',
    (code) => {
      expect(() => baueEbene(code, 0, 'aufwand')).toThrow()
    },
  )

  it('kinderVon wirft für Prototyp-Schlüssel', () => {
    expect(() => kinderVon('__proto__')).toThrow()
  })

  it('wirft für einen Jahresindex außerhalb der Jahre', () => {
    expect(() => baueEbene('GESAMT', haushalt.jahre.length, 'aufwand')).toThrow()
  })
})

describe('ebenenElternCode', () => {
  it('nimmt Produktgruppe vor Aufgabenbereich vor Wurzel', () => {
    expect(ebenenElternCode(null, null)).toBe('GESAMT')
    expect(ebenenElternCode('01', null)).toBe('01')
    expect(ebenenElternCode('01', '0101')).toBe('0101')
  })
})

describe('Randfälle der Ebenen (UI-SPEC E7)', () => {
  const i = haushalt.jahre.indexOf(haushalt.haushaltsjahr)

  it('eine synthetische Produktgruppe mit einem Produkt ergibt genau einen Eintrag mit vollem Anteil', () => {
    const einzel = haushalt.knoten.filter(
      (k) =>
        k.ebene === 'PG' &&
        k.synthetisch &&
        haushalt.knoten.filter((c) => c.eltern === k.code).length === 1,
    )
    expect(einzel.length).toBeGreaterThan(0)
    for (const pg of einzel) {
      const ebene = baueEbene(pg.code, i, 'aufwand')
      if (ebene.length === 1) {
        expect(ebene[0]?.anteil).toBe(1)
      }
    }
  })

  it('ein Blatt hat keine Einträge', () => {
    const blatt = haushalt.knoten.find((k) => k.ebene === 'P')
    expect(blatt).toBeDefined()
    expect(baueEbene(blatt?.code ?? '', i, 'aufwand')).toEqual([])
  })
})

describe('baueBrotkrumen', () => {
  it('liefert nur die Wurzel ohne Auswahl', () => {
    expect(baueBrotkrumen(null, null)).toEqual([{ code: 'GESAMT', name: 'Alle Bereiche' }])
  })

  it('liefert drei Einträge für eine Produktgruppe, der letzte trägt deren Namen', () => {
    const pg = haushalt.knoten.find((k) => k.ebene === 'PG' && k.eltern !== 'KL')
    const pb = haushalt.knoten.find((k) => k.code === pg?.eltern)
    const krumen = baueBrotkrumen(pb?.code ?? null, pg?.code ?? null)
    expect(krumen).toHaveLength(3)
    expect(krumen.map((k) => k.code)).toEqual(['GESAMT', pb?.code, pg?.code])
    expect(krumen[2]?.name).toBe(pg?.name)
  })

  it('wirft bei unbekannten Codes', () => {
    expect(() => baueBrotkrumen('__proto__', null)).toThrow()
  })
})

describe('codeAusParams (Pitfall 16)', () => {
  it('liest den Code aus data.code', () => {
    expect(codeAusParams({ data: { code: '01', value: 1 } })).toBe('01')
  })

  it.each([null, undefined, 'x', 3, {}, { data: null }, { data: {} }, { data: { code: 7 } }])(
    'liefert null für %j',
    (params) => {
      expect(codeAusParams(params)).toBeNull()
    },
  )
})

describe('eintragTooltip (T-05-27)', () => {
  it('maskiert Namen und nennt Wertart und Klickhinweis', () => {
    const html = eintragTooltip(
      {
        code: 'x',
        name: '<img src=x onerror=alert(1)>',
        wert: 1500,
        anteil: 0.5,
        gerundet: false,
        ueberschuss: false,
        istKl: false,
        hatKinder: true,
        istProdukt: false,
        farbe: '#000000',
      },
      'Ansatz',
    )
    expect(html).not.toContain('<img')
    expect(html).toContain('&lt;img')
    expect(html).toContain('Ansatz')
    expect(html).toContain('Klicken, um die Unterteilung zu öffnen')
  })

  it('kennzeichnet gerundete Beträge mit „rd.“ und lässt bei KL-Unterposten den Klickhinweis weg', () => {
    const html = eintragTooltip(
      {
        code: 'KL.x',
        name: 'Kreisumlage',
        wert: 10147000,
        anteil: 0.9,
        gerundet: true,
        ueberschuss: false,
        istKl: true,
        hatKinder: false,
        istProdukt: false,
        farbe: '#000000',
      },
      'Ansatz',
    )
    expect(html).toContain('rd.')
    expect(html).not.toContain('Klicken')
  })
})

describe('kachelBeschriftet (RESEARCH A3)', () => {
  it('beschriftet große Kacheln und lässt kleine unbeschriftet', () => {
    expect(kachelBeschriftet(0.5, 900, 480)).toBe(true)
    expect(kachelBeschriftet(0.001, 900, 480)).toBe(false)
  })

  it('verlangt mehr als die Mindestfläche von 72 × 44 px (Sicherheitsfaktor)', () => {
    expect(kachelBeschriftet(72 * 44, 1, 1)).toBe(false)
    expect(kachelBeschriftet(72 * 44 * 2.5 - 1, 1, 1)).toBe(false)
    expect(kachelBeschriftet(72 * 44 * 2.5, 1, 1)).toBe(true)
  })
})

describe('ueberschussTextSchluessel (AUSG-03)', () => {
  it('nimmt den Text des Aufgabenbereichs, wenn es ihn gibt, sonst den allgemeinen', () => {
    expect(ueberschussTextSchluessel('11')).toBe('ueberschuss_pb_11')
    expect(ueberschussTextSchluessel('16')).toBe('ueberschuss_pb_16')
    // Produktgruppen und Produkte erben den Text ihres Aufgabenbereichs.
    expect(ueberschussTextSchluessel('1101')).toBe('ueberschuss_pb_11')
    expect(ueberschussTextSchluessel('110101')).toBe('ueberschuss_pb_11')
    // Aufgabenbereich 01 hat keinen eigenen Text.
    expect(ueberschussTextSchluessel('0112')).toBe('ueberschuss_allgemein')
    expect(ueberschussTextSchluessel('KL')).toBe('ueberschuss_allgemein')
  })

  it('findet für jeden Überschussknoten in jedem Jahr einen vorhandenen, platzhalterfreien Text', () => {
    let geprueft = 0
    for (const [, i] of JAHRE) {
      for (const k of haushalt.knoten.filter((n) => n.eltern !== null)) {
        if (haushalt.ergebnisplan[k.code]?.berechnet.ueberschuss[i] !== true) {
          continue
        }
        const schluessel = ueberschussTextSchluessel(k.code)
        const text = findeText(schluessel)
        expect(text, `${k.code} -> ${schluessel}`).toBeDefined()
        const absatz = text?.absaetze[0] ?? ''
        expect(absatz.length, schluessel).toBeGreaterThan(0)
        expect(rendereAbsatz(absatz), schluessel).not.toContain('{{')
        geprueft += 1
      }
    }
    expect(geprueft).toBeGreaterThan(0)
  })

  it('wirft für unbekannte Codes und für die Wurzel', () => {
    expect(() => ueberschussTextSchluessel('__proto__')).toThrow()
    expect(() => ueberschussTextSchluessel('GESAMT')).toThrow()
  })
})

function synthetisch(code: string, name: string, wert: number, extra?: Partial<EbenenEintrag>) {
  const eintrag: EbenenEintrag = {
    code,
    name,
    wert,
    anteil: wert > 0 ? 0.5 : null,
    gerundet: false,
    ueberschuss: wert < 0,
    istKl: false,
    hatKinder: true,
    istProdukt: false,
    farbe: '#123456',
    ...extra,
  }
  return eintrag
}

interface Achse {
  min: number
  max: number
  interval: number
}

function xAchse(option: ReturnType<typeof zuschussBalkenOption>): Achse {
  const x = option.xAxis
  if (typeof x !== 'object' || x === null || Array.isArray(x)) {
    throw new Error('xAxis ist kein einzelnes Objekt')
  }
  const { min, max, interval } = x as Record<string, unknown>
  if (typeof min !== 'number' || typeof max !== 'number' || typeof interval !== 'number') {
    throw new Error('xAxis trägt keine festen Grenzen')
  }
  return { min, max, interval }
}

function balkenDaten(option: ReturnType<typeof zuschussBalkenOption>) {
  const serie = Array.isArray(option.series) ? option.series[0] : option.series
  const daten = (serie as { data?: unknown }).data
  if (!Array.isArray(daten)) {
    throw new Error('Serie ohne Daten')
  }
  return daten as {
    value: number
    code: string
    itemStyle: { color: string; decal?: unknown }
    label: { formatter: string; show: boolean }
  }[]
}

describe('zuschussBalkenHoehe', () => {
  it('beträgt Zeilen × 40 px + 48 px (UI-SPEC)', () => {
    expect(zuschussBalkenHoehe(1)).toBe(88)
    expect(zuschussBalkenHoehe(16)).toBe(688)
  })
})

describe('zuschussBalkenOption (AUSG-03, D-05)', () => {
  const i = haushalt.jahre.indexOf(haushalt.haushaltsjahr)
  const ebene = baueEbene('GESAMT', i, 'zuschussbedarf')
  const option = zuschussBalkenOption(ebene, { wertartText: 'Ansatz' })

  it('zeichnet einen horizontalen Balken je Eintrag in der Reihenfolge der Ebene', () => {
    const daten = balkenDaten(option)
    expect(daten.map((d) => d.code)).toEqual(ebene.map((e) => e.code))
    expect(daten.map((d) => d.value)).toEqual(ebene.map((e) => e.wert))
  })

  it('behält die PB-Farbe aller Balken', () => {
    balkenDaten(option).forEach((d, n) => {
      expect(d.itemStyle.color).toBe(ebene[n]?.farbe)
    })
  })

  it('gibt Überschussbalken ein Punktmuster und die Beschriftung „Überschuss: {Betrag}“', () => {
    const daten = balkenDaten(option)
    const negativ = daten.filter((d) => d.value < 0)
    expect(negativ.length).toBeGreaterThan(0)
    for (const d of negativ) {
      expect(d.itemStyle.decal, d.code).toBe(PUNKT_DECAL)
      expect(d.label.formatter, d.code).toBe(`Überschuss: ${euroKurz(Math.abs(d.value))}`)
      expect(d.label.show).toBe(true)
    }
  })

  it('beschriftet positive Balken mit dem Betrag und ohne Punktmuster', () => {
    for (const d of balkenDaten(option).filter((n) => n.value > 0)) {
      expect(d.label.formatter, d.code).toBe(euroKurz(d.value))
      expect(d.itemStyle.decal, d.code).not.toBe(PUNKT_DECAL)
    }
  })

  it('kennzeichnet KL mit dem Streifenmuster', () => {
    const kl = balkenDaten(option).find((d) => d.code === 'KL')
    expect(kl?.itemStyle.decal).toBe(KL_DECAL)
  })

  it('zeigt die Nulllinie: eine Achse trägt die Namen am linken Rand, eine zweite die Linie bei 0', () => {
    const y = option.yAxis
    expect(Array.isArray(y)).toBe(true)
    const achsen = (Array.isArray(y) ? y : []) as {
      axisLine?: { onZero?: boolean; show?: boolean }
      axisLabel?: { show?: boolean; formatter?: (code: string) => string }
    }[]
    expect(achsen).toHaveLength(2)
    expect(achsen[0]?.axisLine?.onZero).toBe(false)
    expect(achsen[1]?.axisLine?.onZero).toBe(true)
    expect(achsen[1]?.axisLabel?.show).toBe(false)
    const erster = ebene[0]
    expect(achsen[0]?.axisLabel?.formatter?.(erster?.code ?? '')).toBe(erster?.name)
  })

  it('enthält die 0 auf der Wertachse (gemischte Vorzeichen)', () => {
    const { min, max } = xAchse(option)
    expect(min).toBeLessThan(0)
    expect(max).toBeGreaterThan(0)
    const werte = ebene.map((e) => e.wert)
    expect(min).toBeLessThanOrEqual(Math.min(...werte))
    expect(max).toBeGreaterThanOrEqual(Math.max(...werte))
  })

  it('enthält die 0 und Platz für Beschriftungen, wenn alle Werte positiv sind', () => {
    const nurPositiv = zuschussBalkenOption(
      [synthetisch('a', 'A', 5_000_000), synthetisch('b', 'B', 1_200_000)],
      { wertartText: 'Ansatz' },
    )
    const { min, max } = xAchse(nurPositiv)
    expect(min).toBe(0)
    expect(max).toBeGreaterThan(5_000_000)
  })

  it('lässt rechts der Nulllinie Platz für das Überschuss-Label, wenn alle Werte negativ sind', () => {
    const nurNegativ = zuschussBalkenOption([synthetisch('a', 'A', -60_540)], {
      wertartText: 'Ansatz',
    })
    const { min, max } = xAchse(nurNegativ)
    expect(min).toBeLessThanOrEqual(-60_540)
    expect(max).toBeGreaterThan(0)
  })

  it('wählt gleichmäßige Schritte, die die Grenzen treffen', () => {
    const { min, max, interval } = xAchse(option)
    expect(interval).toBeGreaterThan(0)
    expect(min / interval).toBeCloseTo(Math.round(min / interval), 6)
    expect(max / interval).toBeCloseTo(Math.round(max / interval), 6)
  })

  it('maskiert Namen im Tooltip (T-05-27)', () => {
    const boese = zuschussBalkenOption([synthetisch('x', '<b onmouseover=1>', 1000)], {
      wertartText: 'Ansatz',
    })
    const tooltip = boese.tooltip as { formatter?: (params: unknown) => string }
    const html = tooltip.formatter?.({ data: { code: 'x' } }) ?? ''
    expect(html).toContain('&lt;b')
    expect(html).not.toContain('<b ')
  })

  it('übernimmt das Zuschussbedarf-Jahr unverändert (keine Neuberechnung)', () => {
    for (const d of balkenDaten(option)) {
      expect(d.value).toBe(haushalt.ergebnisplan[d.code]?.berechnet.zuschussbedarf[i])
    }
  })
})
