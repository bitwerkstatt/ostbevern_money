import { describe, expect, it } from 'vitest'

import { haushalt } from '@/data/daten'
import { kitaZuschuesse, vorberichtTabelle, weitereZuschuesse } from '@/lib/zuschuesse'

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
