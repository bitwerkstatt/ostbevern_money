import { describe, expect, it } from 'vitest'

import { euroKurz } from '@/charts/format'
import { haushalt, produkte } from '@/data/daten'
import {
  baueBindungsgrad,
  BINDUNGSGRADE,
  FINANZIERUNGSPRODUKT,
  klAnteil,
  produkteText,
  segmentZusammenfassung,
  type BindungsSegment,
} from '@/lib/bindungsgrad'
import { bindungsgradText } from '@/lib/produkt'
import { ZEITREIHEN_PRODUKT } from '@/lib/zeitreihen'

const INDEX = haushalt.jahre.indexOf(haushalt.haushaltsjahr)

/** Zuschussbedarf eines Produkts im Haushaltsjahr, direkt aus den Daten gelesen. */
function zuschussbedarf(code: string): number {
  const wert = haushalt.ergebnisplan[code]?.berechnet.zuschussbedarf[INDEX]
  if (wert === undefined) {
    throw new Error(`Kein Zuschussbedarf für ${code}`)
  }
  return wert
}

describe('FINANZIERUNGSPRODUKT (D-01)', () => {
  it('ist die eine Konstante aus lib/zeitreihen.ts, kein zweites Literal', () => {
    expect(FINANZIERUNGSPRODUKT).toBe(ZEITREIHEN_PRODUKT)
  })

  it('hat im Haushaltsjahr einen negativen Zuschussbedarf', () => {
    expect(zuschussbedarf(FINANZIERUNGSPRODUKT)).toBeLessThan(0)
  })
})

describe('baueBindungsgrad', () => {
  const modell = baueBindungsgrad()

  it('führt die Segmente in der festen Reihenfolge pflichtig, teils, freiwillig', () => {
    const reihenfolge = modell.segmente.map((s) => s.bindungsgrad)
    const erwartet = BINDUNGSGRADE.filter((b) => reihenfolge.includes(b))
    expect(reihenfolge).toEqual(erwartet)
    expect(modell.segmente.length).toBeGreaterThan(0)
  })

  it('benennt die Segmente mit dem ausgeschriebenen Bindungsgrad', () => {
    for (const segment of modell.segmente) {
      expect(segment.name).toBe(bindungsgradText(segment.bindungsgrad))
    }
  })

  it('gibt den Segmenten die kurzen Bezeichnungen für Beschriftung und Aufklapper', () => {
    const bezeichnungen = new Map([
      ['pflichtig', 'Pflichtig'],
      ['teils', 'Teils pflichtig'],
      ['freiwillig', 'Freiwillig'],
    ])
    for (const segment of modell.segmente) {
      expect(segment.bezeichnung).toBe(bezeichnungen.get(segment.bindungsgrad))
    }
  })

  it('liest jeden Wert aus berechnet.zuschussbedarf, ohne neu zu rechnen', () => {
    const alle = [...modell.segmente.flatMap((s) => s.produkte), ...modell.ueberschuss]
    expect(alle.length).toBeGreaterThan(0)
    for (const eintrag of alle) {
      expect(eintrag.wert, eintrag.code).toBe(zuschussbedarf(eintrag.code))
    }
  })

  it('führt das Finanzierungsprodukt weder in einem Segment noch im Überschuss', () => {
    const codes = [
      ...modell.segmente.flatMap((s) => s.produkte.map((p) => p.code)),
      ...modell.ueberschuss.map((p) => p.code),
    ]
    expect(codes).not.toContain(FINANZIERUNGSPRODUKT)
  })

  it('summiert alle positiven Zuschussbedarfe außer dem Finanzierungsprodukt', () => {
    const erwartet = produkte
      .filter((p) => p.code !== FINANZIERUNGSPRODUKT)
      .map((p) => zuschussbedarf(p.code))
      .filter((wert) => wert > 0)
      .reduce((summe, wert) => summe + wert, 0)
    expect(modell.summe).toBe(erwartet)
    expect(modell.segmente.reduce((summe, s) => summe + s.summe, 0)).toBe(erwartet)
  })

  it('zählt je Segment die Produkte und teilt die Summe durch die Gesamtsumme', () => {
    for (const segment of modell.segmente) {
      expect(segment.anzahl).toBe(segment.produkte.length)
      expect(segment.summe).toBe(segment.produkte.reduce((s, p) => s + p.wert, 0))
      expect(segment.anteil).toBeCloseTo(segment.summe / modell.summe, 12)
    }
  })

  it('sortiert die Produkte absteigend nach Zuschussbedarf', () => {
    for (const segment of modell.segmente) {
      const werte = segment.produkte.map((p) => p.wert)
      expect(werte).toEqual([...werte].sort((a, b) => b - a))
    }
  })

  it('ordnet jedes Produkt dem Bindungsgrad aus produkte.json zu', () => {
    for (const segment of modell.segmente) {
      for (const eintrag of segment.produkte) {
        const produkt = produkte.find((p) => p.code === eintrag.code)
        expect(produkt?.bindungsgrad, eintrag.code).toBe(segment.bindungsgrad)
        expect(produkt?.pb, eintrag.code).toBe(eintrag.pb)
        expect(produkt?.name, eintrag.code).toBe(eintrag.name)
      }
    }
  })

  it('listet im Überschuss genau die negativen Produkte außer dem Finanzierungsprodukt', () => {
    const erwartet = produkte
      .filter((p) => p.code !== FINANZIERUNGSPRODUKT && zuschussbedarf(p.code) < 0)
      .map((p) => p.code)
      .sort()
    expect(modell.ueberschuss.map((p) => p.code).sort()).toEqual(erwartet)
    for (const eintrag of modell.ueberschuss) {
      expect(eintrag.wert, eintrag.code).toBeLessThan(0)
    }
  })

  it('hat keine Segmente ohne Produkte', () => {
    for (const segment of modell.segmente) {
      expect(segment.anzahl).toBeGreaterThan(0)
    }
  })
})

describe('klAnteil (RAT-02, D-02)', () => {
  it('teilt die Weitergabe an Kreis und Land durch die Summe im Balken', () => {
    expect(klAnteil(500, 2000)).toBe(0.25)
    expect(klAnteil(3000, 2000)).toBe(1.5)
  })

  it('liefert null, wenn die Summe im Balken 0 ist', () => {
    expect(klAnteil(500, 0)).toBeNull()
  })

  it('liefert 0 für eine Weitergabe von 0 €', () => {
    expect(klAnteil(0, 2000)).toBe(0)
  })
})

describe('produkteText und segmentZusammenfassung (WR-02, RAT-01)', () => {
  it('nutzt den Singular genau für ein Produkt', () => {
    expect(produkteText(1)).toBe('1 Produkt')
  })

  it('nutzt für 0 und für viele den Plural', () => {
    expect(produkteText(0)).toBe('0 Produkte')
    expect(produkteText(15)).toBe('15 Produkte')
  })

  it('schreibt die Zusammenfassung eines Segments mit genau einem Produkt im Singular', () => {
    const segment: BindungsSegment = {
      bindungsgrad: 'freiwillig',
      name: 'freiwillig',
      bezeichnung: 'Freiwillig',
      summe: 59900,
      anzahl: 1,
      anteil: 1,
      produkte: [{ code: '000000', name: 'Testprodukt', pb: '01', wert: 59900 }],
    }
    expect(segmentZusammenfassung(segment)).toBe(`Freiwillig · ${euroKurz(59900)} · 1 Produkt`)
  })

  it('setzt die Zusammenfassung jedes echten Segments aus Bezeichnung, Summe und Anzahl zusammen', () => {
    for (const segment of baueBindungsgrad().segmente) {
      expect(segmentZusammenfassung(segment)).toBe(
        `${segment.bezeichnung} · ${euroKurz(segment.summe)} · ${produkteText(segment.anzahl)}`,
      )
    }
  })

  describe.runIf(haushalt.haushaltsjahr === 2026)('Jahrgang 2026', () => {
    it('endet die Zusammenfassung von „Pflichtig“ auf 29 Produkte', () => {
      const pflichtig = baueBindungsgrad().segmente.find((s) => s.bindungsgrad === 'pflichtig')
      expect(pflichtig).toBeDefined()
      expect(segmentZusammenfassung(pflichtig as BindungsSegment)).toMatch(/ · 29 Produkte$/)
    })
  })
})

describe('Anzahltexte in den Komponenten (WR-02)', () => {
  const quelltexte = import.meta.glob<string>(
    [
      '/src/components/MassnahmenFilter.vue',
      '/src/components/ProduktBalkenListe.vue',
      '/src/components/BindungsgradBalken.vue',
    ],
    { query: '?raw', import: 'default', eager: true },
  )
  const quelltext = (name: string): string => {
    const treffer = Object.entries(quelltexte).find(([pfad]) => pfad.endsWith(`/${name}`))
    if (treffer === undefined) {
      throw new Error(`Quelltext ${name} nicht gefunden`)
    }
    return treffer[1]
  }

  it('findet alle drei Komponenten', () => {
    expect(Object.keys(quelltexte)).toHaveLength(3)
  })

  it.each(['MassnahmenFilter.vue', 'ProduktBalkenListe.vue', 'BindungsgradBalken.vue'])(
    'baut in %s keinen Anzahltext mit festem Plural',
    (name) => {
      expect(quelltext(name)).not.toMatch(/\$\{[^}]*\}\s+(Maßnahmen|Produkte)\b/)
    },
  )

  it('nutzt in ProduktBalkenListe.vue segmentZusammenfassung()', () => {
    expect(quelltext('ProduktBalkenListe.vue')).toContain('segmentZusammenfassung(')
  })

  it('nutzt in BindungsgradBalken.vue produkteText() und definiert es nicht selbst', () => {
    const text = quelltext('BindungsgradBalken.vue')
    expect(text).toContain('produkteText(')
    expect(text).not.toMatch(/function\s+produkteText/)
  })
})

describe.runIf(haushalt.haushaltsjahr === 2026)('Bindungsgrad Haushalt 2026', () => {
  const modell = baueBindungsgrad()

  it('summiert 6.358.143 €, 4.491.669 € und 2.436.628 € (13.286.440 €)', () => {
    expect(modell.segmente.map((s) => s.summe)).toEqual([6358143, 4491669, 2436628])
    expect(modell.summe).toBe(13286440)
  })

  it('zählt 29, 15 und 15 Produkte', () => {
    expect(modell.segmente.map((s) => s.anzahl)).toEqual([29, 15, 15])
  })

  it('führt im Überschuss genau 011202, 011204 und 110101', () => {
    expect(new Set(modell.ueberschuss.map((p) => p.code))).toEqual(
      new Set(['011202', '011204', '110101']),
    )
  })
})
