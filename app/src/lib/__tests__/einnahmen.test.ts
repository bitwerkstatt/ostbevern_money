import { describe, expect, it } from 'vitest'

import { haushalt } from '@/data/daten'
import {
  AUFSCHLUESSELUNG_FUER_ERTRAGSART,
  GEZEIGTE_PAUSCHALEN,
  SELBST_FESTGELEGTE_STEUERN,
  SONDERPOSTEN_POSTEN,
  baueInvestiveEinnahmen,
  baueInvestiveTabelle,
  baueSonstigeErtraege,
  baueSteuern,
  baueZuwendungen,
  hatInvestiveWerte,
  quellenText,
} from '@/lib/einnahmen'

const JAHRE = haushalt.jahre.map((jahr, index) => [jahr, index] as const)
const GEP = haushalt.ergebnisplan['GESAMT']?.zeilen
const GFP = haushalt.finanzplan['GESAMT']?.zeilen

function tabelle(name: string) {
  const treffer = haushalt.vorbericht[name]
  if (treffer === undefined) {
    throw new Error(`Vorberichtstabelle ${name} fehlt`)
  }
  return treffer
}

function postenSchluessel(name: string): string[] {
  return tabelle(name).posten.map((p) => p.posten)
}

function summe(werte: readonly (number | null)[]): number {
  return werte.reduce<number>((s, w) => s + (w ?? 0), 0)
}

/** Sucht rekursiv nach `undefined`: Builder liefern `null` für fehlende Werte (Pitfall 7). */
function enthaeltUndefined(wert: unknown): boolean {
  if (wert === undefined) {
    return true
  }
  if (Array.isArray(wert)) {
    return wert.some(enthaeltUndefined)
  }
  if (typeof wert === 'object' && wert !== null) {
    return Object.values(wert).some(enthaeltUndefined)
  }
  return false
}

describe('fachliche Konstanten (Spez. 6.4)', () => {
  it('SELBST_FESTGELEGTE_STEUERN nennt Grund-, Gewerbe-, Hunde- und Vergnügungssteuer', () => {
    expect([...SELBST_FESTGELEGTE_STEUERN].sort()).toEqual(
      [
        'grundsteuer_a',
        'grundsteuer_b',
        'gewerbesteuer',
        'hundesteuer',
        'vergnuegungssteuer',
      ].sort(),
    )
  })

  it.each([...SELBST_FESTGELEGTE_STEUERN])(
    'Steuer %s steht in vorbericht.steuerarten',
    (posten) => {
      expect(postenSchluessel('steuerarten')).toContain(posten)
    },
  )

  it('SONDERPOSTEN_POSTEN nennt die Auflösung von Sonderposten (Zuwendungen und sonstige Erträge)', () => {
    expect([...SONDERPOSTEN_POSTEN].sort()).toEqual(
      ['aufloesung_sonderposten', 'aufloesung_sonstiger_sonderposten'].sort(),
    )
  })

  it.each([...SONDERPOSTEN_POSTEN])(
    'Sonderposten %s steht in einer Vorberichtstabelle',
    (posten) => {
      const vorhanden = [
        ...postenSchluessel('zuwendungen'),
        ...postenSchluessel('sonstige_ertraege'),
      ]
      expect(vorhanden).toContain(posten)
    },
  )

  it('GEZEIGTE_PAUSCHALEN nennt Investitions-, Schul- und Sportpauschale', () => {
    expect([...GEZEIGTE_PAUSCHALEN]).toEqual([
      'investitionspauschale',
      'schulpauschale',
      'sportpauschale',
    ])
  })

  it.each([...GEZEIGTE_PAUSCHALEN])(
    'Pauschale %s steht in vorbericht.investitionszuwendungen',
    (posten) => {
      expect(postenSchluessel('investitionszuwendungen')).toContain(posten)
    },
  )

  it('AUFSCHLUESSELUNG_FUER_ERTRAGSART verknüpft nur Ertragsarten des Gesamtergebnisplans', () => {
    expect(AUFSCHLUESSELUNG_FUER_ERTRAGSART.get('steuern')).toBe('steuern')
    expect(AUFSCHLUESSELUNG_FUER_ERTRAGSART.get('zuwendungen')).toBe('zuwendungen')
    expect(AUFSCHLUESSELUNG_FUER_ERTRAGSART.get('sonstige_ordentliche_ertraege')).toBe('sonstige')
    expect(AUFSCHLUESSELUNG_FUER_ERTRAGSART.get('kostenerstattungen')).toBeUndefined()
    expect(AUFSCHLUESSELUNG_FUER_ERTRAGSART.get('__proto__')).toBeUndefined()
  })
})

describe.each(JAHRE)('Aufschlüsselung Jahr %i', (_jahr, index) => {
  it('baueSteuern: acht Steuerarten, Summe weicht um höchstens acht T€ vom Gesamtergebnisplan ab (EINN-02)', () => {
    const zeilen = baueSteuern(index)
    expect(zeilen).toHaveLength(8)
    const plan = GEP?.['steuern']?.[index]
    expect(plan).toBeDefined()
    expect(Math.abs(summe(zeilen.map((z) => z.wert)) - (plan ?? 0))).toBeLessThanOrEqual(8000)
  })

  it('baueSteuern: genau die selbst festgelegten Steuern tragen die Markierung', () => {
    const markiert = baueSteuern(index)
      .filter((z) => z.selbstFestgelegt)
      .map((z) => z.posten)
      .sort()
    expect(markiert).toEqual([...SELBST_FESTGELEGTE_STEUERN].sort())
  })

  it('baueSteuern: Hebesätze nur für Grundsteuer A/B und Gewerbesteuer, mit PDF-Seite', () => {
    for (const zeile of baueSteuern(index)) {
      const hat = ['grundsteuer_a', 'grundsteuer_b', 'gewerbesteuer'].includes(zeile.posten)
      expect(zeile.hebesatz !== null, zeile.posten).toBe(hat)
      expect(zeile.hebesatzQuelle !== null, zeile.posten).toBe(hat)
    }
  })

  it('baueZuwendungen: Summe weicht um höchstens vier T€ vom Gesamtergebnisplan ab', () => {
    const plan = GEP?.['zuwendungen']?.[index]
    expect(plan).toBeDefined()
    const zeilen = baueZuwendungen(index)
    expect(Math.abs(summe(zeilen.map((z) => z.wert)) - (plan ?? 0))).toBeLessThanOrEqual(4000)
  })

  it('baueZuwendungen: nur Sonderposten tragen „kein Geldfluss“ (EINN-03)', () => {
    const zeilen = baueZuwendungen(index)
    const sonderposten = zeilen.find((z) => z.posten === 'aufloesung_sonderposten')
    expect(sonderposten?.keinGeldfluss).toBe(true)
    for (const zeile of zeilen.filter((z) => z.posten !== 'aufloesung_sonderposten')) {
      expect(zeile.keinGeldfluss, zeile.posten).toBe(false)
    }
  })

  it('baueZuwendungen: ein berechneter Rest „Sonstige“ erscheint nur mit Wert', () => {
    for (const zeile of baueZuwendungen(index).filter((z) => z.berechnet)) {
      expect(zeile.posten).toBe('sonstige')
      expect(zeile.wert).not.toBeNull()
      expect(zeile.quelle).not.toBeNull()
    }
  })

  it('baueSonstigeErtraege: Summe der Hauptposten weicht um höchstens drei T€ vom Gesamtergebnisplan ab (EINN-04)', () => {
    const plan = GEP?.['sonstige_ordentliche_ertraege']?.[index]
    expect(plan).toBeDefined()
    const hauptposten = baueSonstigeErtraege(index).filter((z) => z.teilVon === null)
    expect(hauptposten.length).toBeGreaterThan(0)
    expect(Math.abs(summe(hauptposten.map((z) => z.wert)) - (plan ?? 0))).toBeLessThanOrEqual(3000)
  })

  it('baueSonstigeErtraege: die Konzessionsabgaben stehen unter den 2.1.7-Posten', () => {
    expect(baueSonstigeErtraege(index).map((z) => z.posten)).toContain('konzessionsabgaben')
  })

  it('baueSonstigeErtraege: Sonderposten-Auflösung trägt „kein Geldfluss“', () => {
    const zeile = baueSonstigeErtraege(index).find(
      (z) => z.posten === 'aufloesung_sonstiger_sonderposten',
    )
    expect(zeile?.keinGeldfluss).toBe(true)
  })

  it('kein Builder liefert undefined (fehlende Werte sind null)', () => {
    expect(enthaeltUndefined(baueSteuern(index))).toBe(false)
    expect(enthaeltUndefined(baueZuwendungen(index))).toBe(false)
    expect(enthaeltUndefined(baueSonstigeErtraege(index))).toBe(false)
    expect(enthaeltUndefined(baueInvestiveEinnahmen(index))).toBe(false)
    expect(enthaeltUndefined(baueInvestiveTabelle(index))).toBe(false)
  })
})

describe('Konzessionsabgaben nach Sparte', () => {
  it('Unterzeilen erscheinen nur im Haushaltsjahr', () => {
    for (const [jahr, index] of JAHRE) {
      const unterzeilen = baueSonstigeErtraege(index).filter(
        (z) => z.teilVon === 'konzessionsabgaben',
      )
      expect(unterzeilen.length > 0, String(jahr)).toBe(jahr === haushalt.haushaltsjahr)
    }
  })

  it('Strom, Gas und Wasser ergeben im Haushaltsjahr den Posten Konzessionsabgaben', () => {
    const index = haushalt.jahre.indexOf(haushalt.haushaltsjahr)
    const zeilen = baueSonstigeErtraege(index)
    const gesamt = zeilen.find((z) => z.posten === 'konzessionsabgaben')?.wert
    const teile = zeilen.filter((z) => z.teilVon === 'konzessionsabgaben')
    expect(teile.map((z) => z.posten).sort()).toEqual([
      'konzessionsabgabe_gas',
      'konzessionsabgabe_strom',
      'konzessionsabgabe_wasser',
    ])
    expect(gesamt).toBeDefined()
    expect(summe(teile.map((z) => z.wert))).toBe(gesamt)
    for (const teil of teile) {
      expect(teil.gerundet, teil.posten).toBe(true)
      expect(teil.quelle, teil.posten).not.toBeNull()
    }
  })

  it('die Unterzeilen stehen direkt hinter den Konzessionsabgaben', () => {
    const index = haushalt.jahre.indexOf(haushalt.haushaltsjahr)
    const posten = baueSonstigeErtraege(index).map((z) => z.posten)
    const start = posten.indexOf('konzessionsabgaben')
    expect(
      posten.slice(start + 1, start + 4).every((p) => p.startsWith('konzessionsabgabe_')),
    ).toBe(true)
  })
})

describe('Hebesätze (EINN-02)', () => {
  it('stammen aus meta.hebesaetze', () => {
    const index = haushalt.jahre.indexOf(haushalt.haushaltsjahr)
    for (const zeile of baueSteuern(index)) {
      const meta = haushalt.meta.hebesaetze[zeile.posten]
      if (meta === undefined) {
        expect(zeile.hebesatz).toBeNull()
      } else {
        expect(zeile.hebesatz).toBe(meta.wert)
        expect(zeile.hebesatzQuelle).toBe(meta.quelle)
      }
    }
  })
})

describe.each(JAHRE)('investive Einnahmen Jahr %i (EINN-06, D-03)', (_jahr, index) => {
  const gfp = (schluessel: string): number | undefined => GFP?.[schluessel]?.[index]
  const hatAufschluesselung = tabelle('investitionszuwendungen').posten.some(
    (p) => p.werte[index] != null,
  )

  it('Pauschalen plus „Sonstige (berechnet)“ ergeben die Zeile 18 des Gesamtfinanzplans', () => {
    const zeilen = baueInvestiveEinnahmen(index)
    const teile = zeilen.filter((z) => z.gruppe === 'pauschale' || z.gruppe === 'sonstige')
    expect(summe(teile.map((z) => z.wert))).toBe(gfp('investitionszuwendungen'))
  })

  it('Grundstücksverkäufe, Beiträge und Kredite sind die Finanzplan-Zeilen', () => {
    const zeilen = baueInvestiveEinnahmen(index)
    const wert = (schluessel: string) => zeilen.find((z) => z.schluessel === schluessel)?.wert
    expect(wert('veraeusserung_sachanlagen')).toBe(gfp('veraeusserung_sachanlagen'))
    expect(wert('beitraege')).toBe(gfp('beitraege'))
    expect(wert('kreditaufnahme')).toBe(gfp('kreditaufnahme'))
  })

  it('die Reihenfolge folgt dem UI-SPEC', () => {
    expect(baueInvestiveEinnahmen(index).map((z) => z.schluessel)).toEqual([
      'investitionspauschale',
      'schulpauschale',
      'sportpauschale',
      'sonstige_berechnet',
      'veraeusserung_sachanlagen',
      'beitraege',
      'kreditaufnahme',
    ])
  })

  it('„Sonstige (berechnet)“ ist als berechnet gekennzeichnet, die übrigen Zeilen nicht', () => {
    for (const zeile of baueInvestiveEinnahmen(index)) {
      expect(zeile.berechnet, zeile.schluessel).toBe(zeile.schluessel === 'sonstige_berechnet')
    }
  })

  it('jede Zeile kennt ihre PDF-Seite', () => {
    for (const zeile of baueInvestiveEinnahmen(index)) {
      expect(zeile.quelle, zeile.schluessel).not.toBeNull()
    }
  })

  it(
    hatAufschluesselung
      ? 'mit gedruckter Aufschlüsselung tragen die Pauschalen Werte'
      : 'ohne gedruckte Aufschlüsselung sind alle Pauschalen null und „Sonstige“ trägt die ganze Zeile 18',
    () => {
      const zeilen = baueInvestiveEinnahmen(index)
      const pauschalen = zeilen.filter((z) => z.gruppe === 'pauschale')
      const sonstige = zeilen.find((z) => z.schluessel === 'sonstige_berechnet')
      if (hatAufschluesselung) {
        expect(pauschalen.some((z) => z.wert !== null)).toBe(true)
      } else {
        expect(pauschalen.every((z) => z.wert === null)).toBe(true)
        expect(sonstige?.wert).toBe(gfp('investitionszuwendungen'))
      }
    },
  )

  it('die Tabelle nennt die Finanzplan-Zeilen mit ihrem gedruckten Namen', () => {
    const tabellenzeilen = baueInvestiveTabelle(index)
    const finanzplan = tabellenzeilen.filter((z) => z.gruppe === 'finanzplan')
    expect(finanzplan.map((z) => z.schluessel)).toEqual([
      'investitionszuwendungen',
      'veraeusserung_sachanlagen',
      'beitraege',
      'kreditaufnahme',
    ])
    for (const zeile of finanzplan) {
      expect(zeile.name.length, zeile.schluessel).toBeGreaterThan(0)
      expect(zeile.wert, zeile.schluessel).toBe(gfp(zeile.schluessel))
    }
  })

  it('die Tabelle listet alle gedruckten Pauschalen und Förderungen des Jahres', () => {
    const gedruckt = tabelle('investitionszuwendungen').posten.filter((p) => p.werte[index] != null)
    const tabellenzeilen = baueInvestiveTabelle(index).filter((z) => z.gruppe === 'pauschale')
    expect(tabellenzeilen.map((z) => z.schluessel)).toEqual(gedruckt.map((p) => p.posten))
    expect(tabellenzeilen.every((z) => z.gerundet)).toBe(true)
  })
})

describe('quellenText', () => {
  it('nennt eine einzelne Seite im Singular', () => {
    expect(quellenText([27, 27, null])).toBe('Quelle: PDF-Seite 27')
  })

  it('nennt mehrere Seiten aufsteigend und ohne Doppelte', () => {
    expect(quellenText([29, 28, 28])).toBe('Quelle: PDF-Seiten 28, 29')
  })

  it('liefert ohne Seite keine Zeile', () => {
    expect(quellenText([])).toBeUndefined()
    expect(quellenText([null])).toBeUndefined()
  })
})

describe('hatInvestiveWerte', () => {
  it('ist falsch ohne Zeilen und bei lauter Nullen oder fehlenden Werten', () => {
    expect(hatInvestiveWerte([])).toBe(false)
    expect(
      hatInvestiveWerte([
        {
          schluessel: 'a',
          name: 'A',
          wert: 0,
          gerundet: false,
          berechnet: false,
          quelle: 1,
          gruppe: 'finanzplan',
        },
        {
          schluessel: 'b',
          name: 'B',
          wert: null,
          gerundet: false,
          berechnet: false,
          quelle: 1,
          gruppe: 'pauschale',
        },
      ]),
    ).toBe(false)
  })

  it('ist wahr, sobald eine Zeile einen Wert ungleich 0 hat', () => {
    expect(
      hatInvestiveWerte([
        {
          schluessel: 'a',
          name: 'A',
          wert: 5,
          gerundet: false,
          berechnet: false,
          quelle: 1,
          gruppe: 'finanzplan',
        },
      ]),
    ).toBe(true)
  })

  it('jedes Jahr der Daten hat investive Einnahmen', () => {
    for (const [, index] of JAHRE) {
      expect(hatInvestiveWerte(baueInvestiveEinnahmen(index))).toBe(true)
    }
  })
})

describe.runIf(haushalt.haushaltsjahr === 2026)(
  'Haushalt 2026: Werte aus dem PDF (S. 27, 28, 33, 52)',
  () => {
    const index = haushalt.jahre.indexOf(2026)

    it('Steuerarten: Gewerbesteuer 7.800.000 €, Hebesatz 418', () => {
      const gewerbe = baueSteuern(index).find((z) => z.posten === 'gewerbesteuer')
      expect(gewerbe?.wert).toBe(7_800_000)
      expect(gewerbe?.gerundet).toBe(true)
      expect(gewerbe?.hebesatz).toBe(418)
    })

    it('Zuwendungen: Schlüsselzuweisung 890.000 €, Sonstige 5.200 € berechnet', () => {
      const zeilen = baueZuwendungen(index)
      expect(zeilen.find((z) => z.posten === 'schluesselzuweisung')?.wert).toBe(890_000)
      const rest = zeilen.find((z) => z.posten === 'sonstige')
      expect(rest?.wert).toBe(5200)
      expect(rest?.berechnet).toBe(true)
    })

    it('Investive Einnahmen: Pauschalen 1.525.000 / 406.000 / 60.000 €, Sonstige (berechnet) 1.751.000 €', () => {
      const zeilen = baueInvestiveEinnahmen(index)
      const wert = (schluessel: string) => zeilen.find((z) => z.schluessel === schluessel)?.wert
      expect(wert('investitionspauschale')).toBe(1_525_000)
      expect(wert('schulpauschale')).toBe(406_000)
      expect(wert('sportpauschale')).toBe(60_000)
      expect(wert('sonstige_berechnet')).toBe(1_751_000)
    })

    it('„Sonstige (berechnet)“ entspricht der Summe der übrigen gedruckten Posten von S. 52', () => {
      const uebrige = tabelle('investitionszuwendungen').posten.filter(
        (p) => !GEZEIGTE_PAUSCHALEN.includes(p.posten),
      )
      const erwartet = summe(uebrige.map((p) => p.werte[index] ?? null))
      const sonstige = baueInvestiveEinnahmen(index).find(
        (z) => z.schluessel === 'sonstige_berechnet',
      )
      expect(sonstige?.wert).toBe(erwartet)
    })
  },
)
