import { describe, expect, it } from 'vitest'

import { haushalt, stellenplan } from '@/data/daten'
import type { Haushalt, Stellenplan } from '@/data/typen'
import {
  alsVzae,
  differenzText,
  nachwuchs,
  stellenNachBereich,
  stellenNachGruppe,
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

// ---------------------------------------------------------------------------------------------
// Stellen und Personalaufwand je Aufgabenbereich (STEL-02, STEL-03, D-16)
// ---------------------------------------------------------------------------------------------

const quelltexte = import.meta.glob<string>('/src/lib/stellen.ts', {
  query: '?raw',
  import: 'default',
  eager: true,
})

const jahrIndex = haushalt.jahre.indexOf(stellenplan.haushaltsjahr)

/** Kopie des Haushalts, in der der Personalaufwand des Aufgabenbereichs `pb` überschrieben ist. */
function mitPersonalaufwand(pb: string, werte: number[]): Haushalt {
  const knoten = haushalt.ergebnisplan[pb]
  if (knoten === undefined) {
    throw new Error(`Aufgabenbereich ${pb} fehlt`)
  }
  return {
    ...haushalt,
    ergebnisplan: {
      ...haushalt.ergebnisplan,
      [pb]: { ...knoten, zeilen: { ...knoten.zeilen, personalaufwendungen: werte } },
    },
  }
}

describe('stellenNachBereich', () => {
  const zeilen = stellenNachBereich()

  it('führt nur Aufgabenbereiche: ebene PB, eltern GESAMT, nicht synthetisch (kein KL)', () => {
    const erlaubt = new Set(
      haushalt.knoten
        .filter((k) => k.ebene === 'PB' && k.eltern === 'GESAMT' && !k.synthetisch)
        .map((k) => k.code),
    )
    expect(zeilen.length).toBeGreaterThan(0)
    for (const zeile of zeilen) {
      expect(erlaubt.has(zeile.pb)).toBe(true)
    }
    expect(zeilen.map((z) => z.pb)).not.toContain('KL')
  })

  it('sortiert absteigend nach Stellen, Zeilen ohne Stellen zuletzt', () => {
    const werte = zeilen.map((z) => z.stellen)
    const ersteLeere = werte.indexOf(null)
    const mitWert = ersteLeere === -1 ? werte : werte.slice(0, ersteLeere)
    expect(mitWert).toEqual([...mitWert].sort((a, b) => (b ?? 0) - (a ?? 0)))
    if (ersteLeere !== -1) {
      expect(werte.slice(ersteLeere).every((w) => w === null)).toBe(true)
    }
  })

  it('summiert die Stellen zur Gesamtsumme, ohne Zeilen doppelt zu zählen', () => {
    const gesamt = zeilen.reduce((summe, z) => summe + (z.stellen ?? 0), 0)
    expect(gesamt).toBe(stellenSummen().haushaltsjahr)
  })

  it('summiert den Personalaufwand zur Zeile personalaufwendungen des Gesamtplans', () => {
    const gesamt = zeilen.reduce((summe, z) => summe + (z.personalaufwand ?? 0), 0)
    expect(gesamt).toBe(
      haushalt.ergebnisplan['GESAMT']?.zeilen['personalaufwendungen']?.[jahrIndex],
    )
  })

  it('lässt Aufgabenbereiche ohne Stellen und ohne Personalaufwand weg', () => {
    const ohneStellen = ohne((z) => z.produktbereich !== '04')
    const ohneBeides = stellenNachBereich(ohneStellen, mitPersonalaufwand('04', [0, 0, 0, 0, 0, 0]))
    expect(ohneBeides.map((z) => z.pb)).not.toContain('04')
  })

  it('behält eine Zeile mit nur einer Seite und zeigt die andere als null (nie 0)', () => {
    const nurPersonal = stellenNachBereich(ohne((z) => z.produktbereich !== '04'))
    const zeile = nurPersonal.find((z) => z.pb === '04')
    expect(zeile).toBeDefined()
    expect(zeile?.stellen).toBeNull()
    expect(zeile?.personalaufwand).not.toBeNull()
    expect(nurPersonal[nurPersonal.length - 1]?.stellen).toBeNull()

    const nurStellen = stellenNachBereich(stellenplan, mitPersonalaufwand('04', []))
    expect(nurStellen.find((z) => z.pb === '04')?.personalaufwand).toBeNull()
    expect(nurStellen.find((z) => z.pb === '04')?.stellen).not.toBeNull()
  })

  it('ändert nichts, wenn die Zeilen ohne Produktbereich fehlen', () => {
    const nurPb = ohne((z) => z.produktbereich !== null)
    expect(stellenNachBereich(nurPb)).toEqual(zeilen)
  })

  it('nennt die belegenden PDF-Seiten aufsteigend und ohne Doppelte', () => {
    for (const zeile of zeilen) {
      expect(zeile.pdfSeiten.length).toBeGreaterThan(0)
      expect(zeile.pdfSeiten).toEqual([...new Set(zeile.pdfSeiten)].sort((a, b) => a - b))
    }
  })

  it('bildet keinen Aufwand je Stelle (D-16): kein Export und keine Division', () => {
    const quelltext = quelltexte['/src/lib/stellen.ts'] ?? ''
    const ohneKommentare = quelltext.replace(/\/\*[\s\S]*?\*\//g, '').replace(/\/\/.*$/gm, '')
    const exportNamen = Array.from(
      ohneKommentare.matchAll(/export\s+(?:function|const|interface|type)\s+(\w+)/g),
      (treffer) => treffer[1] ?? '',
    )
    const verdaechtig = exportNamen.filter((name) => /personal/i.test(name) && /stelle/i.test(name))
    expect(verdaechtig).toEqual([])
    expect(ohneKommentare).not.toMatch(/personalaufwand\w*\s*\/\s*\w*stelle/i)
    expect(ohneKommentare).not.toMatch(/stelle\w*\s*\/\s*\w*personalaufwand/i)
    expect(ohneKommentare).not.toMatch(/je\s*stelle/i)
  })

  describe.runIf(stellenplan.haushaltsjahr === 2026)('Jahrgang 2026', () => {
    it('Σ Stellen 6291 Hundertstel, Σ Personalaufwand 5.204.054 €', () => {
      expect(zeilen.reduce((summe, z) => summe + (z.stellen ?? 0), 0)).toBe(6291)
      expect(zeilen.reduce((summe, z) => summe + (z.personalaufwand ?? 0), 0)).toBe(5204054)
    })

    it('15 Aufgabenbereiche, Innere Verwaltung (01) mit 2187 Hundertstel vorn', () => {
      expect(zeilen).toHaveLength(15)
      expect(zeilen[0]?.pb).toBe('01')
      expect(zeilen[0]?.stellen).toBe(2187)
    })
  })
})

// ---------------------------------------------------------------------------------------------
// Stellen nach Besoldungs-, Entgelt- und S-Gruppe (STEL-02, D-17)
// ---------------------------------------------------------------------------------------------

describe('stellenNachGruppe', () => {
  it('liefert je Teil Zeilen {gruppe, stellen, pdfSeite} mit Stellen in Hundertstel', () => {
    for (const { teil } of TEILE) {
      const gruppen = stellenNachGruppe(teil)
      expect(gruppen.length).toBeGreaterThan(0)
      for (const zeile of gruppen) {
        expect(zeile.gruppe).not.toBe('')
        expect(Number.isInteger(zeile.stellen)).toBe(true)
        expect(zeile.pdfSeite).toBeGreaterThan(0)
      }
    }
  })

  it('sortiert absteigend nach der gedruckten Position (RESEARCH Pitfall 7)', () => {
    for (const { teil } of TEILE) {
      const positionen = new Map(
        stellenplan.zeilen
          .filter(
            (z) =>
              z.teil === teil &&
              z.produktbereich === null &&
              z.merkmal === 'stellen' &&
              z.jahr === stellenplan.haushaltsjahr,
          )
          .map((z) => [z.gruppe, z.position]),
      )
      const reihenfolge = stellenNachGruppe(teil).map((z) => positionen.get(z.gruppe) ?? Number.NaN)
      expect(reihenfolge).toEqual([...reihenfolge].sort((a, b) => b - a))
    }
  })

  it('summiert je Teil zur Teilsumme, über alle Teile zur Gesamtsumme und zur Summe je Bereich', () => {
    const teile = stellenNachTeil()
    for (const teil of teile) {
      const summe = stellenNachGruppe(teil.teil).reduce((gesamt, z) => gesamt + z.stellen, 0)
      expect(summe).toBe(teil.haushaltsjahr)
    }
    const ueberGruppen = TEILE.flatMap(({ teil }) => stellenNachGruppe(teil)).reduce(
      (gesamt, z) => gesamt + z.stellen,
      0,
    )
    const ueberBereiche = stellenNachBereich().reduce((gesamt, z) => gesamt + (z.stellen ?? 0), 0)
    expect(ueberGruppen).toBe(stellenSummen().haushaltsjahr)
    expect(ueberBereiche).toBe(ueberGruppen)
  })

  it('zählt keine Zeilen mit Produktbereich, kein Vorjahr und kein besetzt', () => {
    const nurTeilA = ohne((z) => z.produktbereich === null && z.merkmal === 'stellen')
    for (const { teil } of TEILE) {
      expect(stellenNachGruppe(teil, nurTeilA)).toEqual(stellenNachGruppe(teil))
    }
  })

  it('stellt Pauschal- und Sonderzeilen ans Ende der Achse (UI-SPEC)', () => {
    const vorlage = stellenplan.zeilen.find(
      (z) =>
        z.teil === 'tarif' &&
        z.produktbereich === null &&
        z.merkmal === 'stellen' &&
        z.jahr === stellenplan.haushaltsjahr,
    )
    if (vorlage === undefined) {
      throw new Error('Keine Tarifzeile gefunden')
    }
    // Die Sonderzeile erhält die höchste Position und stünde nach Position ganz vorn.
    const mit: Stellenplan = {
      ...stellenplan,
      zeilen: [...stellenplan.zeilen, { ...vorlage, gruppe: 'pauschal', position: 99, stellen: 1 }],
    }
    const gruppen = stellenNachGruppe('tarif', mit).map((z) => z.gruppe)
    expect(gruppen[gruppen.length - 1]).toBe('pauschal')
    expect(gruppen.slice(0, -1)).toEqual(stellenNachGruppe('tarif').map((z) => z.gruppe))
  })

  it('liefert eine leere Liste für einen Teil ohne Zeilen und für einen unbekannten Teil', () => {
    const ohneSozial = ohne((z) => z.teil !== 'sozial_erziehungsdienst')
    expect(stellenNachGruppe('sozial_erziehungsdienst', ohneSozial)).toEqual([])
    expect(stellenNachGruppe('gibt_es_nicht')).toEqual([])
  })

  it('zeigt einen Teil mit einer einzigen Gruppe als eine Zeile (UI-SPEC E10 zero-one-many)', () => {
    const eine = stellenNachGruppe(
      'sozial_erziehungsdienst',
      ohne((z) => z.teil !== 'sozial_erziehungsdienst' || z.gruppe === 'S 12'),
    )
    expect(eine.map((z) => z.gruppe)).toEqual(['S 12'])
  })

  describe.runIf(stellenplan.haushaltsjahr === 2026)('Jahrgang 2026', () => {
    it('Beamte A 8 → B 3', () => {
      expect(stellenNachGruppe('beamte').map((z) => z.gruppe)).toEqual([
        'A 8',
        'A 10',
        'A 12',
        'A 13',
        'A 14',
        'B 3',
      ])
    })

    it('Tarif 1 → 14 mit 9a, 9b, 9c in dieser Reihenfolge', () => {
      expect(stellenNachGruppe('tarif').map((z) => z.gruppe)).toEqual([
        '1',
        '5',
        '6',
        '7',
        '8',
        '9a',
        '9b',
        '9c',
        '11',
        '12',
        '14',
      ])
    })

    it('Sozial- und Erziehungsdienst S 11 → S 12', () => {
      expect(stellenNachGruppe('sozial_erziehungsdienst').map((z) => z.gruppe)).toEqual([
        'S 11',
        'S 12',
      ])
    })

    it('Einzelwerte: A 8 mit 200, Tarif 6 mit 1895, S 12 mit 214 Hundertstel', () => {
      const wert = (teil: string, gruppe: string): number | undefined =>
        stellenNachGruppe(teil).find((z) => z.gruppe === gruppe)?.stellen
      expect(wert('beamte', 'A 8')).toBe(200)
      expect(wert('tarif', '6')).toBe(1895)
      expect(wert('sozial_erziehungsdienst', 'S 12')).toBe(214)
    })
  })
})
