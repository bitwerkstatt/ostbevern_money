import type { EChartsOption } from 'echarts'
import { describe, expect, it } from 'vitest'

import { INVEST_FARBE } from '@/charts/echartsTheme'
import { haushalt, investitionen } from '@/data/daten'
import type { Massnahme, VeFaelligkeit } from '@/data/typen'
import {
  baueVeFaelligkeiten,
  veFaelligkeiten,
  veGesamt,
  veOption,
  vePdfSeiten,
  veTabelle,
} from '@/lib/finanzierung'

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

describe.runIf(haushalt.haushaltsjahr === 2026)('Jahrgang 2026 (ROADMAP SC 2)', () => {
  it('Verpflichtungsermächtigungen 11.600.000 €, fällig 2027 und 2028', () => {
    expect(veGesamt()).toBe(11_600_000)
    expect(veFaelligkeiten().map((eintrag) => [eintrag.jahr, eintrag.betrag])).toEqual([
      [2027, 9_400_000],
      [2028, 2_200_000],
    ])
  })
})
