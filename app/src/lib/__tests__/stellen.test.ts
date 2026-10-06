import { describe, expect, it } from 'vitest'

import { stellenplan } from '@/data/daten'
import type { Stellenplan } from '@/data/typen'
import {
  alsVzae,
  differenzText,
  nachwuchs,
  stellenNachTeil,
  stellenSummen,
  TEILE,
} from '@/lib/stellen'

// Alle Summen laufen in Hundertstel (RESEARCH Pattern 6, Pitfall 5): Erwartungen stehen als
// ganze Hundertstel, nie als Fließkommazahl wie 62.91. Die für den Jahrgang festgehaltenen
// Werte stehen unter `describe.runIf`.

/** Kopie des Stellenplans mit den Zeilen, die `behalte` annimmt. */
function ohne(behalte: (zeile: Stellenplan['zeilen'][number]) => boolean): Stellenplan {
  return { ...stellenplan, zeilen: stellenplan.zeilen.filter(behalte) }
}

describe('TEILE', () => {
  it('nennt die drei Teile mit Namen und Gruppentitel in fester Reihenfolge', () => {
    expect(TEILE.map((t) => t.teil)).toEqual(['beamte', 'tarif', 'sozial_erziehungsdienst'])
    expect(TEILE.map((t) => t.name)).toEqual([
      'Beamtinnen und Beamte',
      'Tarifbeschäftigte',
      'Sozial- und Erziehungsdienst',
    ])
    expect(TEILE.map((t) => t.gruppenTitel)).toEqual([
      'Besoldung',
      'Entgelt',
      'Sozial- und Erziehungsdienst',
    ])
  })
})

describe('alsVzae', () => {
  it('teilt Hundertstel erst zur Anzeige durch 100', () => {
    expect(alsVzae(6291)).toBe(62.91)
    expect(alsVzae(0)).toBe(0)
  })
})

describe('differenzText', () => {
  it('setzt ein Vorzeichen und rechnet in Hundertstel', () => {
    expect(differenzText(6291, 6213)).toBe('+0,78')
    expect(differenzText(5663, 6291)).toBe('−6,28')
  })

  it('zeigt eine gleiche Größe ohne Vorzeichen', () => {
    expect(differenzText(6291, 6291)).toBe('0')
  })

  it('liefert null, wenn ein Wert fehlt (kein erfundenes 0)', () => {
    expect(differenzText(null, 6213)).toBeNull()
    expect(differenzText(6291, null)).toBeNull()
  })
})

describe('stellenSummen', () => {
  it('zählt nur Zeilen ohne Produktbereich mit den Merkmalen stellen und besetzt', () => {
    const summen = stellenSummen()
    const hundertstel = (f: (z: Stellenplan['zeilen'][number]) => boolean): number =>
      stellenplan.zeilen
        .filter(f)
        .reduce((summe, zeile) => summe + Math.round((zeile.stellen ?? 0) * 100), 0)
    const vorjahr = stellenplan.haushaltsjahr - 1
    expect(summen.haushaltsjahr).toBe(
      hundertstel(
        (z) =>
          z.produktbereich === null &&
          z.merkmal === 'stellen' &&
          z.jahr === stellenplan.haushaltsjahr,
      ),
    )
    expect(summen.vorjahr).toBe(
      hundertstel(
        (z) => z.produktbereich === null && z.merkmal === 'stellen' && z.jahr === vorjahr,
      ),
    )
    expect(summen.besetzt).toBe(
      hundertstel((z) => z.produktbereich === null && z.merkmal === 'besetzt'),
    )
  })

  it('nennt den Stichtag des besetzten Standes aus den Daten', () => {
    const stichtage = new Set(
      stellenplan.zeilen
        .filter((z) => z.merkmal === 'besetzt' && z.produktbereich === null)
        .map((z) => z.stichtag),
    )
    expect([...stichtage]).toEqual([stellenSummen().stichtag])
  })

  it('nennt die belegenden PDF-Seiten aufsteigend und ohne Doppelte', () => {
    const seiten = stellenSummen().pdfSeiten
    expect(seiten.length).toBeGreaterThan(0)
    expect(seiten).toEqual([...new Set(seiten)].sort((a, b) => a - b))
  })

  it('ändert sich nicht, wenn die davon_ausgesondert-Zeilen fehlen', () => {
    const ohneAusgesondert = ohne((z) => z.merkmal !== 'davon_ausgesondert')
    expect(stellenSummen(ohneAusgesondert)).toEqual(stellenSummen())
  })

  it('ändert sich nicht, wenn die Nachwuchszeilen fehlen', () => {
    const ohneNachwuchs = ohne((z) => z.teil !== 'nachwuchs')
    expect(stellenSummen(ohneNachwuchs)).toEqual(stellenSummen())
  })

  it('ändert sich nicht, wenn die Zeilen mit Produktbereich fehlen', () => {
    const ohnePb = ohne((z) => z.produktbereich === null)
    expect(stellenSummen(ohnePb)).toEqual(stellenSummen())
  })

  it('liefert null statt 0, wenn Vergleichswerte fehlen (UI-SPEC E10 empty)', () => {
    const vorjahr = stellenplan.haushaltsjahr - 1
    const summen = stellenSummen(ohne((z) => !(z.merkmal === 'stellen' && z.jahr === vorjahr)))
    expect(summen.vorjahr).toBeNull()
    expect(summen.haushaltsjahr).not.toBeNull()
    expect(stellenSummen(ohne((z) => z.merkmal !== 'besetzt')).besetzt).toBeNull()
  })

  it('wirft bei einer Summenzeile ohne Wert, statt 0 zu erfinden', () => {
    const ziel = stellenplan.zeilen.findIndex(
      (z) => z.merkmal === 'stellen' && z.produktbereich === null,
    )
    const kaputt: Stellenplan = {
      ...stellenplan,
      zeilen: stellenplan.zeilen.map((z, i) => (i === ziel ? { ...z, stellen: null } : z)),
    }
    expect(() => stellenSummen(kaputt)).toThrow()
  })

  describe.runIf(stellenplan.haushaltsjahr === 2026)('Jahrgang 2026', () => {
    it('Haushaltsjahr 6291, Vorjahr 6213, besetzt 5663, Stichtag 30.06.2025', () => {
      const summen = stellenSummen()
      expect(summen.haushaltsjahr).toBe(6291)
      expect(summen.vorjahr).toBe(6213)
      expect(summen.besetzt).toBe(5663)
      expect(summen.stichtag).toBe('2025-06-30')
    })

    it('Differenzen 78 und 628 Hundertstel', () => {
      const summen = stellenSummen()
      expect((summen.haushaltsjahr ?? 0) - (summen.vorjahr ?? 0)).toBe(78)
      expect((summen.haushaltsjahr ?? 0) - (summen.besetzt ?? 0)).toBe(628)
    })
  })
})

describe('stellenNachTeil', () => {
  it('liefert die drei Teile in der Reihenfolge von TEILE', () => {
    expect(stellenNachTeil().map((t) => t.teil)).toEqual(TEILE.map((t) => t.teil))
  })

  it('summiert über die Teile zur Gesamtsumme', () => {
    const teile = stellenNachTeil()
    const summen = stellenSummen()
    const gesamt = (feld: 'haushaltsjahr' | 'vorjahr' | 'besetzt'): number =>
      teile.reduce((summe, teil) => summe + (teil[feld] ?? 0), 0)
    expect(gesamt('haushaltsjahr')).toBe(summen.haushaltsjahr)
    expect(gesamt('vorjahr')).toBe(summen.vorjahr)
    expect(gesamt('besetzt')).toBe(summen.besetzt)
  })

  describe.runIf(stellenplan.haushaltsjahr === 2026)('Jahrgang 2026', () => {
    it('Beamte haben 800 Hundertstel im Haushaltsjahr (S. 34: 8,0 Stellen)', () => {
      const beamte = stellenNachTeil().find((t) => t.teil === 'beamte')
      expect(beamte).toBeDefined()
      expect(beamte?.haushaltsjahr).toBe(800)
    })

    it('Tarif und Sozial- und Erziehungsdienst summieren auf 5491 Hundertstel', () => {
      const teile = stellenNachTeil()
      const rest = teile
        .filter((t) => t.teil !== 'beamte')
        .reduce((summe, t) => summe + (t.haushaltsjahr ?? 0), 0)
      expect(rest).toBe(5491)
    })
  })
})

describe('nachwuchs', () => {
  it('zählt Personen je Jahr und nennt die PDF-Seite', () => {
    const n = nachwuchs()
    expect(n.pdfSeiten.length).toBeGreaterThan(0)
    const personen = (merkmal: string): number =>
      stellenplan.zeilen
        .filter((z) => z.teil === 'nachwuchs' && z.merkmal === merkmal)
        .reduce((summe, z) => summe + (z.personen ?? 0), 0)
    expect(n.vorjahr).toBe(personen('beschaeftigt'))
    expect(n.haushaltsjahr).toBe(personen('vorgesehen'))
  })

  it('nennt nur das vorhandene Jahr, wenn Personenzahlen fehlen (UI-SPEC E10 partial)', () => {
    const nurVorgesehen = ohne((z) => z.merkmal !== 'beschaeftigt')
    expect(nachwuchs(nurVorgesehen).vorjahr).toBeNull()
    expect(nachwuchs(nurVorgesehen).haushaltsjahr).not.toBeNull()
  })

  it('geht nie in eine Stellensumme ein', () => {
    const ohneNachwuchs = ohne((z) => z.teil !== 'nachwuchs')
    expect(stellenNachTeil(ohneNachwuchs)).toEqual(stellenNachTeil())
  })

  describe.runIf(stellenplan.haushaltsjahr === 2026)('Jahrgang 2026', () => {
    it('Vorjahr 5 Personen, Haushaltsjahr 6 Personen, S. 290', () => {
      const n = nachwuchs()
      expect(n.vorjahr).toBe(5)
      expect(n.haushaltsjahr).toBe(6)
      expect(n.pdfSeiten).toEqual([290])
    })
  })
})
