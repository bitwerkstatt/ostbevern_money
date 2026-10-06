import { describe, expect, it } from 'vitest'

import { haushalt } from '@/data/daten'
import { baueKreisumlage, findeKlKnoten } from '@/lib/kreisumlage'
import {
  kitaZuschuesse,
  nichtBeeinflussbar,
  ohneLeere,
  SOZIALLEISTUNGEN_BEZEICHNUNG,
  vorberichtTabelle,
  weitereZuschuesse,
  zusammen,
} from '@/lib/zuschuesse'

const INDEX = haushalt.jahre.indexOf(haushalt.haushaltsjahr)

function transferWert(schluessel: string): number | null | undefined {
  return haushalt.vorbericht.transferaufwendungen?.posten.find((p) => p.posten === schluessel)
    ?.werte[INDEX]
}

function summe(posten: readonly { wert: number | null }[]): number {
  return posten.reduce((s, p) => s + (p.wert ?? 0), 0)
}

describe('vorberichtTabelle', () => {
  it('liefert eine vorhandene Vorberichtstabelle', () => {
    expect(vorberichtTabelle('kita_zuschuesse').tabelle).toBe('kita_zuschuesse')
  })

  it('wirft bei einer fehlenden Tabelle mit dem Namen der Tabelle', () => {
    expect(() => vorberichtTabelle('gibt_es_nicht')).toThrow(/gibt_es_nicht/)
  })
})

describe('kitaZuschuesse', () => {
  it('liefert die Einrichtungen einzeln, gerundet und mit PDF-Seite', () => {
    const kita = kitaZuschuesse()
    expect(kita.posten.length).toBeGreaterThan(0)
    for (const p of kita.posten) {
      expect(p.gerundet, p.schluessel).toBe(true)
      expect(p.pdfSeite, p.schluessel).not.toBeNull()
      expect(p.name.length, p.schluessel).toBeGreaterThan(0)
    }
    expect(kita.pdfSeiten.length).toBeGreaterThan(0)
  })

  it('die Einzelposten ergeben die gedruckte Gesamtzeile', () => {
    const kita = kitaZuschuesse()
    expect(kita.gesamt).not.toBeNull()
    expect(summe(kita.posten)).toBe(kita.gesamt)
  })

  it('die Gesamtzeile entspricht dem Transferposten für Kindertageseinrichtungen', () => {
    expect(kitaZuschuesse().gesamt).toBe(transferWert('zuschuesse_kindertageseinrichtungen'))
  })
})

describe('weitereZuschuesse', () => {
  it('liefert die beiden Gruppen mit Zeilen und PDF-Seiten', () => {
    const { transfer, lfdZwecke } = weitereZuschuesse()
    expect(transfer.posten.length).toBe(2)
    expect(lfdZwecke.posten.length).toBeGreaterThan(0)
    expect(transfer.pdfSeiten.length).toBeGreaterThan(0)
    expect(lfdZwecke.pdfSeiten.length).toBeGreaterThan(0)
    for (const p of [...transfer.posten, ...lfdZwecke.posten]) {
      expect(p.gerundet, p.schluessel).toBe(true)
      expect(p.pdfSeite, p.schluessel).not.toBeNull()
    }
  })

  it('die Transferposten tragen die Werte der Transferaufwendungen', () => {
    const { transfer } = weitereZuschuesse()
    const werte = Object.fromEntries(transfer.posten.map((p) => [p.schluessel, p.wert]))
    expect(werte.zuschuss_kinder_jugendwerk).toBe(transferWert('zuschuss_kinder_jugendwerk'))
    expect(werte.zuschuss_ogs).toBe(transferWert('zuschuss_ogs'))
  })

  it('die Einzelposten der laufenden Zwecke ergeben den Transferposten', () => {
    const { lfdZwecke } = weitereZuschuesse()
    expect(summe(lfdZwecke.posten)).toBe(transferWert('zuschuesse_laufende_zwecke'))
    expect(lfdZwecke.gesamt).toBe(transferWert('zuschuesse_laufende_zwecke'))
  })
})

describe('zusammen', () => {
  const posten = (wert: number | null) => ({
    schluessel: 'x',
    name: 'X',
    wert,
    gerundet: true,
    pdfSeite: 1,
  })

  it('nimmt die gedruckte Gesamtzeile, wenn es sie gibt', () => {
    expect(zusammen({ posten: [posten(1000)], gesamt: 5000, pdfSeiten: [1] })).toBe(5000)
  })

  it('summiert ohne Gesamtzeile nur vorhandene Werte', () => {
    expect(
      zusammen({
        posten: [posten(1000), posten(null), posten(2000)],
        gesamt: null,
        pdfSeiten: [1],
      }),
    ).toBe(3000)
  })

  it('liefert null, wenn kein einziger Wert vorhanden ist', () => {
    expect(zusammen({ posten: [posten(null)], gesamt: null, pdfSeiten: [1] })).toBeNull()
    expect(zusammen({ posten: [], gesamt: null, pdfSeiten: [] })).toBeNull()
  })
})

describe.runIf(haushalt.haushaltsjahr === 2026)('Einzelzuschüsse Haushalt 2026', () => {
  it('die acht Posten der laufenden Zwecke ergeben 120.000 €', () => {
    const { lfdZwecke } = weitereZuschuesse()
    expect(lfdZwecke.posten).toHaveLength(8)
    expect(summe(lfdZwecke.posten)).toBe(120000)
  })

  it('die sieben Kitas ergeben 559.000 €', () => {
    const kita = kitaZuschuesse()
    expect(kita.posten).toHaveLength(7)
    expect(kita.gesamt).toBe(559000)
  })
})

describe('ohneLeere', () => {
  const posten = (schluessel: string, wert: number | null) => ({
    schluessel,
    name: schluessel,
    wert,
    gerundet: true,
    pdfSeite: 1,
  })

  it('lässt Posten mit dem Wert 0 oder ohne Wert weg', () => {
    const rest = ohneLeere([posten('a', 0), posten('b', null), posten('c', 5000)])
    expect(rest.map((p) => p.schluessel)).toEqual(['c'])
  })
})

describe('nichtBeeinflussbar', () => {
  const ergebnis = nichtBeeinflussbar()

  it('enthält jeden Unterposten der Weitergabe an Kreis und Land mit denselben Werten wie /ausgaben', () => {
    const kreisumlage = baueKreisumlage(INDEX)
    expect(kreisumlage.unterposten.length).toBeGreaterThan(0)
    for (const u of kreisumlage.unterposten) {
      const kachel = ergebnis.posten.find((p) => p.schluessel === u.code)
      expect(kachel?.wert, u.code).toBe(u.wert)
      expect(kachel?.name, u.code).toBe(u.name)
      expect(kachel?.pdfSeite, u.code).toBe(u.pdfSeite)
    }
  })

  it('enthält die gesetzlichen Sozialleistungen aus den Transferaufwendungen', () => {
    const kachel = ergebnis.posten.find((p) => p.name === SOZIALLEISTUNGEN_BEZEICHNUNG)
    const wert = transferWert('sozialleistungen')
    if (wert === null || wert === undefined || wert === 0) {
      expect(kachel).toBeUndefined()
    } else {
      expect(kachel?.wert).toBe(wert)
    }
  })

  it('zeigt keinen Posten ohne Wert oder mit dem Wert 0 und belegt jeden mit einer PDF-Seite', () => {
    expect(ergebnis.posten.length).toBeGreaterThan(0)
    for (const p of ergebnis.posten) {
      expect(p.wert, p.schluessel).not.toBeNull()
      expect(p.wert, p.schluessel).not.toBe(0)
      expect(p.pdfSeite, p.schluessel).not.toBeNull()
      expect(p.gerundet, p.schluessel).toBe(true)
    }
  })

  it('liefert Gesamtbetrag und Namen der Weitergabe an Kreis und Land', () => {
    expect(ergebnis.klGesamt).toBe(baueKreisumlage(INDEX).gesamt)
    expect(ergebnis.klName).toBe(findeKlKnoten().name)
  })
})

describe.runIf(haushalt.haushaltsjahr === 2026)('Nicht beeinflussbare Posten Haushalt 2026', () => {
  const werte = Object.fromEntries(nichtBeeinflussbar().posten.map((p) => [p.name, p.wert]))

  it('Kreisumlage 10.147.000 €, Gewerbesteuerumlage 654.000 €, Krankenhausinvestitionsumlage 200.000 €', () => {
    expect(werte.Kreisumlage).toBe(10147000)
    expect(werte.Gewerbesteuerumlage).toBe(654000)
    expect(werte.Krankenhausinvestitionsumlage).toBe(200000)
  })

  it('Gesetzliche Sozialleistungen 491.000 €', () => {
    expect(werte[SOZIALLEISTUNGEN_BEZEICHNUNG]).toBe(491000)
  })
})
