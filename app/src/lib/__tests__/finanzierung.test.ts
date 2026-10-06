import type { EChartsOption } from 'echarts'
import { describe, expect, it } from 'vitest'

import { INVEST_FARBE, KATEGORIE_FARBEN } from '@/charts/echartsTheme'
import { haushalt, investitionen } from '@/data/daten'
import type { Massnahme, VeFaelligkeit } from '@/data/typen'
import {
  baueVeFaelligkeiten,
  einzahlungsAbweichungen,
  einzahlungsAufteilung,
  einzahlungsTabelle,
  finanzierungsLegende,
  finanzierungsOption,
  finanzierungsReihen,
  finanzierungsTabelle,
  veFaelligkeiten,
  veGesamt,
  veOption,
  vePdfSeiten,
  veTabelle,
  type FinanzierungsVariante,
  type Finanzierungsreihen,
} from '@/lib/finanzierung'
import { jahrSchluessel } from '@/lib/produkt'

// Alle Erwartungen stammen aus den Daten (Identitäten gegen den Gesamtfinanzplan); nur die für
// den Jahrgang festgehaltenen Werte stehen unter `describe.runIf` (RESEARCH Pattern 1).
const finanzplanVe = haushalt.finanzplan['GESAMT']?.ve ?? {}

function ve(teil: Partial<VeFaelligkeit>): VeFaelligkeit {
  return {
    produkt: '000001',
    massnahme_id: 'TEST1',
    konto: '785111',
    jahr: 2030,
    betrag: 100,
    pdf_seite: 7,
    ...teil,
  }
}

function massnahme(teil: Partial<Massnahme>): Massnahme {
  return {
    produkt: '000001',
    pb: '01',
    massnahme_id: 'TEST1',
    massnahme_name: 'Testmaßnahme',
    konto: '785111',
    konto_name: 'Testkonto',
    richtung: 'auszahlung',
    art: 'bau',
    werte: [null],
    ve: null,
    pdf_seite: 1,
    ...teil,
  }
}

/** Die Datenpunkte (Zahlen) der ersten Serie einer Säulenoption. */
function saeulenWerte(option: EChartsOption): number[] {
  const serien = option.series
  if (!Array.isArray(serien)) {
    throw new Error('series ist kein Array')
  }
  const serie = serien[0]
  if (serie === undefined || serie.type !== 'bar' || !Array.isArray(serie.data)) {
    throw new Error('keine Säulenserie mit Daten')
  }
  return serie.data.map((eintrag) => {
    const wert = typeof eintrag === 'number' ? eintrag : undefined
    if (wert === undefined) {
      throw new Error('Datenpunkt ist keine Zahl')
    }
    return wert
  })
}

describe('baueVeFaelligkeiten (INV-02, D-10)', () => {
  it('fasst die Zeilen je Fälligkeitsjahr aufsteigend zusammen', () => {
    const ergebnis = baueVeFaelligkeiten(
      [
        ve({ jahr: 2032, betrag: 300 }),
        ve({ jahr: 2031, betrag: 200 }),
        ve({ jahr: 2031, massnahme_id: 'TEST2', betrag: 50 }),
      ],
      [massnahme({}), massnahme({ massnahme_id: 'TEST2', massnahme_name: 'Zweite' })],
    )
    expect(ergebnis.map((eintrag) => eintrag.jahr)).toEqual([2031, 2032])
    expect(ergebnis.map((eintrag) => eintrag.betrag)).toEqual([250, 300])
  })

  it('bündelt dieselbe Maßnahme mehrerer Konten im selben Jahr und ordnet absteigend', () => {
    const ergebnis = baueVeFaelligkeiten(
      [
        ve({ jahr: 2031, konto: '785111', betrag: 200 }),
        ve({ jahr: 2031, konto: '785311', betrag: 100 }),
        ve({ jahr: 2031, massnahme_id: 'TEST2', betrag: 500 }),
      ],
      [massnahme({}), massnahme({ massnahme_id: 'TEST2', massnahme_name: 'Zweite' })],
    )
    expect(ergebnis).toHaveLength(1)
    expect(ergebnis[0]?.massnahmen).toEqual([
      { produkt: '000001', massnahmeId: 'TEST2', name: 'Zweite', betrag: 500, pdfSeite: 7 },
      { produkt: '000001', massnahmeId: 'TEST1', name: 'Testmaßnahme', betrag: 300, pdfSeite: 7 },
    ])
  })

  it('unterscheidet dieselbe Maßnahmenkennung unter verschiedenen Produkten', () => {
    const ergebnis = baueVeFaelligkeiten(
      [ve({ produkt: '000001', betrag: 100 }), ve({ produkt: '000002', betrag: 40 })],
      [
        massnahme({ produkt: '000001', massnahme_name: 'Eins' }),
        massnahme({ produkt: '000002', massnahme_name: 'Zwei' }),
      ],
    )
    expect(ergebnis[0]?.massnahmen.map((m) => [m.produkt, m.name])).toEqual([
      ['000001', 'Eins'],
      ['000002', 'Zwei'],
    ])
  })

  it('zeigt bei einem einzigen Fälligkeitsjahr genau einen Eintrag (zero-one-many)', () => {
    const ergebnis = baueVeFaelligkeiten([ve({ jahr: 2031 })], [massnahme({})])
    expect(ergebnis).toHaveLength(1)
  })

  it('ohne Zeilen gibt es keinen Eintrag (kein Jahr ohne Fälligkeit)', () => {
    expect(baueVeFaelligkeiten([], [massnahme({})])).toEqual([])
  })

  it('wirft mit Produkt und Kennung, wenn die Maßnahme fehlt (T-06-23)', () => {
    expect(() => baueVeFaelligkeiten([ve({ massnahme_id: 'FEHLT' })], [massnahme({})])).toThrow(
      /000001.*FEHLT/,
    )
  })
})

describe('veFaelligkeiten und veGesamt (INV-02, D-10, T-06-23)', () => {
  it('ist aufsteigend nach Fälligkeitsjahr sortiert, ohne doppeltes Jahr', () => {
    const jahre = veFaelligkeiten().map((eintrag) => eintrag.jahr)
    expect(jahre).toEqual([...new Set(jahre)].sort((a, b) => a - b))
    expect(jahre.length).toBeGreaterThan(0)
  })

  it('betrag je Jahr ist die Summe der Datenzeilen dieses Jahres', () => {
    for (const eintrag of veFaelligkeiten()) {
      const summe = investitionen.ve_faelligkeiten
        .filter((zeile) => zeile.jahr === eintrag.jahr)
        .reduce((s, zeile) => s + zeile.betrag, 0)
      expect(eintrag.betrag).toBe(summe)
      expect(eintrag.massnahmen.reduce((s, m) => s + m.betrag, 0)).toBe(summe)
    }
  })

  it('veGesamt = Summe aller Zeilen = Verpflichtungsermächtigung im Gesamtfinanzplan', () => {
    const summe = investitionen.ve_faelligkeiten.reduce((s, zeile) => s + zeile.betrag, 0)
    expect(veGesamt()).toBe(summe)
    expect(veGesamt()).toBe(finanzplanVe['auszahlungen_investitionen'])
  })

  it('jede VE-Zeile findet ihre Maßnahme (Produkt und Kennung) in den Maßnahmen', () => {
    const bekannt = new Set(
      investitionen.massnahmen.map((zeile) => `${zeile.produkt}/${zeile.massnahme_id}`),
    )
    for (const zeile of investitionen.ve_faelligkeiten) {
      expect(bekannt.has(`${zeile.produkt}/${zeile.massnahme_id}`)).toBe(true)
    }
    for (const eintrag of veFaelligkeiten()) {
      for (const massnahmeEintrag of eintrag.massnahmen) {
        const treffer = investitionen.massnahmen.find(
          (zeile) =>
            zeile.produkt === massnahmeEintrag.produkt &&
            zeile.massnahme_id === massnahmeEintrag.massnahmeId,
        )
        expect(treffer?.massnahme_name).toBe(massnahmeEintrag.name)
      }
    }
  })

  it('vePdfSeiten nennt die Seiten der VE-Zeilen aufsteigend ohne Wiederholung', () => {
    const erwartet = [
      ...new Set(investitionen.ve_faelligkeiten.map((zeile) => zeile.pdf_seite)),
    ].sort((a, b) => a - b)
    expect(vePdfSeiten()).toEqual(erwartet)
  })
})

describe('veOption (INV-02, D-10)', () => {
  it('zeigt eine Säule je Fälligkeitsjahr mit dem Betrag, in INVEST_FARBE', () => {
    const eintraege = veFaelligkeiten()
    const option = veOption()
    expect(saeulenWerte(option)).toEqual(eintraege.map((eintrag) => eintrag.betrag))
    expect(JSON.stringify(option)).toContain(INVEST_FARBE)
    const achse = option.xAxis
    if (Array.isArray(achse) || achse === undefined || !('data' in achse)) {
      throw new Error('xAxis ohne data')
    }
    expect(achse.data).toEqual(eintraege.map((eintrag) => String(eintrag.jahr)))
  })

  it('bei einem einzigen Fälligkeitsjahr genau eine Säule (zero-one-many)', () => {
    const einzel = baueVeFaelligkeiten([ve({ jahr: 2031 })], [massnahme({})])
    expect(saeulenWerte(veOption(einzel))).toEqual([100])
  })

  it('ohne Fälligkeit keine Datenpunkte (BaseChart zeigt den Leerzustand)', () => {
    expect(veOption([]).series).toEqual([])
  })
})

describe('veTabelle (INV-02, D-10)', () => {
  it('hat je Fälligkeitsjahr eine Zeile mit Jahr, Betrag und Maßnahmen', () => {
    const eintraege = veFaelligkeiten()
    const tabelle = veTabelle()
    expect(tabelle.spalten.map((spalte) => spalte.schluessel)).toEqual([
      'jahr',
      'betrag',
      'massnahmen',
    ])
    expect(tabelle.zeilen).toHaveLength(eintraege.length)
    tabelle.zeilen.forEach((zeile, i) => {
      expect(zeile['faelligkeitsjahr']).toBe(eintraege[i]?.jahr)
      expect(zeile['betrag']).toBe(eintraege[i]?.betrag)
      expect(zeile['massnahmen']).toBe(eintraege[i]?.massnahmen.map((m) => m.name).join(', '))
    })
  })
})

// ---------------------------------------------------------------------------------------
// Finanzierung (INV-03, D-08)
// ---------------------------------------------------------------------------------------

const GFP = haushalt.finanzplan['GESAMT']?.zeilen ?? {}
const EINZAHLUNGS_SCHLUESSEL = [
  'investitionszuwendungen',
  'veraeusserung_sachanlagen',
  'veraeusserung_finanzanlagen',
  'beitraege',
  'sonstige_investitionseinzahlungen',
]
const VARIANTEN: readonly FinanzierungsVariante[] = ['investitionen', 'kredite']

function reihen(teil: Partial<Finanzierungsreihen>): Finanzierungsreihen {
  return {
    jahre: [2030, 2031],
    wertarten: ['planung', 'planung'],
    einzahlungen: [10, 50],
    auszahlungen: [30, 20],
    kreditaufnahme: [5, null],
    tilgung: [1, 2],
    ...teil,
  }
}

/** Die Säulenserien einer Option; wirft, wenn es keine Säulen sind. */
function serienVon(option: EChartsOption) {
  const serien = option.series
  if (!Array.isArray(serien)) {
    throw new Error('series ist kein Array')
  }
  return serien.map((serie) => {
    if (serie.type !== 'bar' || !Array.isArray(serie.data)) {
      throw new Error('keine Säulenserie mit Daten')
    }
    return { name: String(serie.name ?? ''), daten: serie.data, label: serie.label }
  })
}

/** Der Beschriftungstext von Serie `serie` im Datenpunkt `index`. */
function beschriftung(option: EChartsOption, serie: number, index: number): string {
  const label = serienVon(option)[serie]?.label
  const formatter = label?.formatter
  if (typeof formatter !== 'function') {
    throw new Error('Serie ohne Beschriftungsfunktion')
  }
  return String(
    formatter({ dataIndex: index, seriesIndex: serie } as Parameters<typeof formatter>[0]),
  )
}

describe('finanzierungsReihen (INV-03, D-08)', () => {
  it('liefert je Eintrag von haushalt.jahre einen Wert in jeder Reihe', () => {
    const r = finanzierungsReihen()
    expect(r.jahre).toEqual(haushalt.jahre)
    expect(r.wertarten).toEqual(haushalt.wertarten)
    for (const reihe of [r.einzahlungen, r.auszahlungen, r.kreditaufnahme, r.tilgung]) {
      expect(reihe).toHaveLength(haushalt.jahre.length)
    }
  })

  it('entspricht den Zeilen des Gesamtfinanzplans (T-06-23)', () => {
    const r = finanzierungsReihen()
    expect(r.einzahlungen).toEqual(GFP['einzahlungen_investitionen'])
    expect(r.auszahlungen).toEqual(GFP['auszahlungen_investitionen'])
    expect(r.kreditaufnahme).toEqual(GFP['kreditaufnahme'])
    expect(r.tilgung).toEqual(GFP['tilgung'])
  })

  it('entspricht investitionen.finanzierung.zeilen', () => {
    const r = finanzierungsReihen()
    const zeilen = investitionen.finanzierung.zeilen
    expect(r.einzahlungen).toEqual(zeilen.einzahlungen_investitionen)
    expect(r.auszahlungen).toEqual(zeilen.auszahlungen_investitionen)
    expect(r.kreditaufnahme).toEqual(zeilen.kreditaufnahme)
    expect(r.tilgung).toEqual(zeilen.tilgung)
  })
})

describe('einzahlungsAufteilung (INV-03, D-08)', () => {
  it('liefert die GFP-Zeilen 18 bis 22 mit den gedruckten Namen', () => {
    const zeilen = einzahlungsAufteilung()
    expect(zeilen.map((zeile) => zeile.schluessel)).toEqual(EINZAHLUNGS_SCHLUESSEL)
    expect(zeilen.map((zeile) => zeile.nummer)).toEqual(['18', '19', '20', '21', '22'])
    for (const zeile of zeilen) {
      const name = haushalt.zeilen_namen.finanzplan.find((n) => n.schluessel === zeile.schluessel)
      expect(zeile.name).toBe(name?.name)
      expect(zeile.werte).toEqual(GFP[zeile.schluessel])
    }
  })

  it('Σ der Zeilen 18 bis 22 = Einzahlungen aus Investitionstätigkeit, höchstens 1 € Abweichung', () => {
    const zeilen = einzahlungsAufteilung()
    const gesamt = GFP['einzahlungen_investitionen'] ?? []
    expect(gesamt.length).toBeGreaterThan(0)
    gesamt.forEach((wert, i) => {
      const summe = zeilen.reduce((s, zeile) => s + (zeile.werte[i] ?? 0), 0)
      expect(Math.abs(summe - wert)).toBeLessThanOrEqual(1)
    })
  })

  it('ab dem zweiten Jahr der Daten ist die Summe exakt', () => {
    const zeilen = einzahlungsAufteilung()
    const gesamt = GFP['einzahlungen_investitionen'] ?? []
    gesamt.forEach((wert, i) => {
      if (i === 0) {
        return
      }
      expect(zeilen.reduce((s, zeile) => s + (zeile.werte[i] ?? 0), 0)).toBe(wert)
    })
  })

  it('einzahlungsAbweichungen nennt genau die Jahre mit abweichender Summe', () => {
    const zeilen = einzahlungsAufteilung()
    const gesamt = GFP['einzahlungen_investitionen'] ?? []
    const erwartet = haushalt.jahre.flatMap((jahr, i) => {
      const differenz = zeilen.reduce((s, zeile) => s + (zeile.werte[i] ?? 0), 0) - (gesamt[i] ?? 0)
      return differenz === 0 ? [] : [{ jahr, differenz }]
    })
    expect(einzahlungsAbweichungen()).toEqual(erwartet)
  })
})

describe('finanzierungsLegende', () => {
  it('benennt dunkle und helle Serie', () => {
    expect(finanzierungsLegende('investitionen')).toBe('dunkel: Auszahlungen, hell: Einzahlungen')
    expect(finanzierungsLegende('kredite')).toBe('dunkel: Kreditaufnahme, hell: Tilgung')
  })
})

describe('finanzierungsOption (INV-03, D-08, UI-SPEC E8)', () => {
  it.each([false, true])(
    'investitionen: zwei Säulenserien aus den Finanzplan-Reihen (schmal: %s)',
    (schmal) => {
      const r = finanzierungsReihen()
      const serien = serienVon(finanzierungsOption('investitionen', schmal))
      expect(serien.map((serie) => serie.name)).toEqual(['Auszahlungen', 'Einzahlungen'])
      expect(serien[0]?.daten).toEqual(r.auszahlungen)
      expect(serien[1]?.daten).toEqual(r.einzahlungen)
    },
  )

  it.each([false, true])(
    'kredite: zwei Säulenserien aus den Finanzplan-Reihen (schmal: %s)',
    (schmal) => {
      const r = finanzierungsReihen()
      const serien = serienVon(finanzierungsOption('kredite', schmal))
      expect(serien.map((serie) => serie.name)).toEqual(['Kreditaufnahme', 'Tilgung'])
      expect(serien[0]?.daten).toEqual(r.kreditaufnahme)
      expect(serien[1]?.daten).toEqual(r.tilgung)
    },
  )

  it('färbt die erste Serie in INVEST_FARBE und die zweite in KATEGORIE_FARBEN[2]', () => {
    for (const variante of VARIANTEN) {
      const serien = finanzierungsOption(variante, false).series
      if (!Array.isArray(serien) || serien.length !== 2) {
        throw new Error('zwei Serien erwartet')
      }
      expect(JSON.stringify(serien[0])).toContain(INVEST_FARBE)
      expect(JSON.stringify(serien[1])).toContain(KATEGORIE_FARBEN[2])
    }
  })

  it('die x-Achse trägt je Jahr zwei Zeilen: Jahr und Wertart', () => {
    const achse = finanzierungsOption('investitionen', false).xAxis
    if (Array.isArray(achse) || achse === undefined || !('data' in achse)) {
      throw new Error('xAxis ohne data')
    }
    expect(achse.data).toHaveLength(haushalt.jahre.length)
    for (const beschriftungText of achse.data ?? []) {
      expect(String(beschriftungText).split('\n')).toHaveLength(2)
    }
  })

  it('ein fehlender Wert bleibt null und wird nie zu 0', () => {
    const serien = serienVon(finanzierungsOption('kredite', false, reihen({})))
    expect(serien[0]?.daten).toEqual([5, null])
  })

  it('breit: beide Werte je Jahr tragen eine Beschriftung', () => {
    const option = finanzierungsOption('investitionen', false, reihen({}))
    for (const index of [0, 1]) {
      expect(beschriftung(option, 0, index)).not.toBe('')
      expect(beschriftung(option, 1, index)).not.toBe('')
    }
  })

  it('schmal: nur der größte Wert je Jahr trägt eine Beschriftung (UI-SPEC E8 overflow)', () => {
    // Jahr 0: Auszahlungen 30 > Einzahlungen 10; Jahr 1: Einzahlungen 50 > Auszahlungen 20.
    const option = finanzierungsOption('investitionen', true, reihen({}))
    expect(beschriftung(option, 0, 0)).not.toBe('')
    expect(beschriftung(option, 1, 0)).toBe('')
    expect(beschriftung(option, 0, 1)).toBe('')
    expect(beschriftung(option, 1, 1)).not.toBe('')
  })

  it('schmal: bei Gleichstand trägt nur die erste Serie die Beschriftung', () => {
    const option = finanzierungsOption(
      'investitionen',
      true,
      reihen({ auszahlungen: [40, 1], einzahlungen: [40, 2] }),
    )
    expect(beschriftung(option, 0, 0)).not.toBe('')
    expect(beschriftung(option, 1, 0)).toBe('')
  })

  it('enthält keinen Ergebnisplan-Wert: alle Datenpunkte stammen aus Finanzplan-Zeilen', () => {
    const erlaubt = new Set(
      [
        'einzahlungen_investitionen',
        'auszahlungen_investitionen',
        'kreditaufnahme',
        'tilgung',
      ].flatMap((schluessel) => GFP[schluessel] ?? []),
    )
    for (const variante of VARIANTEN) {
      for (const serie of serienVon(finanzierungsOption(variante, false))) {
        for (const wert of serie.daten) {
          expect(erlaubt.has(Number(wert))).toBe(true)
        }
      }
    }
  })
})

describe('finanzierungsTabelle (INV-03, D-08)', () => {
  it.each(VARIANTEN)(
    '%s: je Jahr eine Zeile mit den beiden Werten, null bleibt null',
    (variante) => {
      const tabelle = finanzierungsTabelle(variante, reihen({}))
      expect(tabelle.spalten).toHaveLength(3)
      expect(tabelle.zeilen).toHaveLength(2)
      const [dunkel, hell] = tabelle.spalten.slice(1).map((spalte) => spalte.schluessel)
      if (dunkel === undefined || hell === undefined) {
        throw new Error('zwei Wertspalten erwartet')
      }
      if (variante === 'kredite') {
        expect(tabelle.zeilen.map((zeile) => zeile[dunkel])).toEqual([5, null])
        expect(tabelle.zeilen.map((zeile) => zeile[hell])).toEqual([1, 2])
      } else {
        expect(tabelle.zeilen.map((zeile) => zeile[dunkel])).toEqual([30, 20])
        expect(tabelle.zeilen.map((zeile) => zeile[hell])).toEqual([10, 50])
      }
    },
  )

  it('nutzt ohne Angabe die Finanzplan-Reihen aller Jahre', () => {
    expect(finanzierungsTabelle('investitionen').zeilen).toHaveLength(haushalt.jahre.length)
  })
})

describe('einzahlungsTabelle (INV-03, D-08)', () => {
  it('hat je Zeile 18 bis 22 eine Tabellenzeile und die Summenzeile, je Jahr eine Spalte', () => {
    const tabelle = einzahlungsTabelle()
    expect(tabelle.spalten).toHaveLength(1 + haushalt.jahre.length)
    expect(tabelle.zeilen).toHaveLength(EINZAHLUNGS_SCHLUESSEL.length + 1)
    const aufteilung = einzahlungsAufteilung()
    aufteilung.forEach((zeile, i) => {
      haushalt.jahre.forEach((jahr, j) => {
        expect(tabelle.zeilen[i]?.[jahrSchluessel(jahr)]).toBe(zeile.werte[j])
      })
    })
    const summenzeile = tabelle.zeilen.at(-1)
    haushalt.jahre.forEach((jahr, j) => {
      expect(summenzeile?.[jahrSchluessel(jahr)]).toBe(GFP['einzahlungen_investitionen']?.[j])
    })
  })
})

describe.runIf(haushalt.haushaltsjahr === 2026)('Jahrgang 2026 (ROADMAP SC 2)', () => {
  it('Verpflichtungsermächtigungen 11.600.000 €, fällig 2027 und 2028', () => {
    expect(veGesamt()).toBe(11_600_000)
    expect(veFaelligkeiten().map((eintrag) => [eintrag.jahr, eintrag.betrag])).toEqual([
      [2027, 9_400_000],
      [2028, 2_200_000],
    ])
  })
})
