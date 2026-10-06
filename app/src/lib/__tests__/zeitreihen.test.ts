import { describe, expect, it } from 'vitest'

import { euro } from '@/charts/format'
import { haushalt, produkte } from '@/data/daten'
import type { Produkt } from '@/data/typen'
import { findeBeleg } from '@/lib/quelle'
import {
  STANDARD_ZEITREIHE,
  ZEITREIHEN_POSTEN,
  ZEITREIHEN_PRODUKT,
  baueZeitreihe,
  betragText,
  findeGrundzahl,
  quellenFussnote,
  zeitreihenOptionen,
  zeitreihenSeite,
  zeitreihenSerien,
  type Zeitpunkt,
} from '@/lib/zeitreihen'

const ERSTES_PLANJAHR = haushalt.jahre[0] ?? 0
const POSTEN_SCHLUESSEL = ZEITREIHEN_POSTEN.map((eintrag) => eintrag.posten)

function punkt(jahr: number, wert: number | null, wertart: string): Zeitpunkt {
  return { jahr, wert, wertart, quelle: 'vorbericht', pdfSeite: 1, beleg: null, gerundet: true }
}

describe('ZEITREIHEN_POSTEN (RESEARCH Pitfall 8)', () => {
  it('umfasst die acht Steuerarten und die Schlüsselzuweisung', () => {
    expect([...POSTEN_SCHLUESSEL].sort()).toEqual(
      [
        'anteil_einkommensteuer',
        'anteil_umsatzsteuer',
        'gewerbesteuer',
        'grundsteuer_a',
        'grundsteuer_b',
        'hundesteuer',
        'kompensationszahlungen',
        'schluesselzuweisung',
        'vergnuegungssteuer',
      ].sort(),
    )
  })

  it('führt jeden Posten höchstens einmal', () => {
    expect(new Set(POSTEN_SCHLUESSEL).size).toBe(POSTEN_SCHLUESSEL.length)
  })

  it.each(POSTEN_SCHLUESSEL)('Posten %s steht in der zugeordneten Vorberichtstabelle', (posten) => {
    const eintrag = ZEITREIHEN_POSTEN.find((e) => e.posten === posten)
    const tabelle = eintrag === undefined ? undefined : haushalt.vorbericht[eintrag.tabelle]
    expect(tabelle?.posten.map((p) => p.posten)).toContain(posten)
  })

  it.each(ZEITREIHEN_POSTEN)(
    'Posten $posten löst auf genau eine Grundzahl in Euro auf (Bezeichnung beginnt mit dem Präfix)',
    (eintrag) => {
      const grundzahl = findeGrundzahl(eintrag)
      expect(grundzahl.einheit).toBe('EUR')
      expect(grundzahl.bezeichnung.startsWith(eintrag.grundzahlPraefix)).toBe(true)
    },
  )

  it('findeGrundzahl wirft mit dem Postennamen, wenn keine Grundzahl passt', () => {
    const eintrag = ZEITREIHEN_POSTEN[0]
    expect(eintrag).toBeDefined()
    if (eintrag === undefined) {
      return
    }
    const leer: Produkt[] = produkte.map((produkt) => ({ ...produkt, grundzahlen: [] }))
    expect(() => findeGrundzahl(eintrag, leer)).toThrow(eintrag.posten)
  })

  it('findeGrundzahl wirft mit dem Postennamen, wenn zwei Grundzahlen passen', () => {
    const eintrag = ZEITREIHEN_POSTEN[0]
    expect(eintrag).toBeDefined()
    if (eintrag === undefined) {
      return
    }
    const gezeigt = findeGrundzahl(eintrag)
    const doppelt: Produkt[] = produkte.map((p) =>
      p.grundzahlen.includes(gezeigt)
        ? { ...p, grundzahlen: [...p.grundzahlen, { ...gezeigt }] }
        : p,
    )
    expect(() => findeGrundzahl(eintrag, doppelt)).toThrow(eintrag.posten)
  })

  it('der Standard ist eine der Auswahlmöglichkeiten', () => {
    expect(POSTEN_SCHLUESSEL).toContain(STANDARD_ZEITREIHE)
  })
})

describe.each(POSTEN_SCHLUESSEL)('baueZeitreihe(%s)', (posten) => {
  const punkte = baueZeitreihe(posten)

  it('hat einen Punkt je Jahr, lückenlos bis zum letzten Planjahr', () => {
    const jahre = punkte.map((p) => p.jahr)
    for (let k = 1; k < jahre.length; k++) {
      expect(jahre[k]).toBe((jahre[k - 1] ?? 0) + 1)
    }
    expect(jahre.at(-1)).toBe(haushalt.jahre.at(-1))
    expect(jahre).toEqual(expect.arrayContaining([...haushalt.jahre]))
  })

  it('Jahre vor dem ersten Planjahr stammen aus den Grundzahlen (Ist)', () => {
    const davor = punkte.filter((p) => p.jahr < ERSTES_PLANJAHR)
    expect(davor.length).toBeGreaterThan(0)
    for (const p of davor) {
      expect(p.quelle).toBe('grundzahlen')
      expect(p.wertart).toBe('ergebnis')
      expect(p.gerundet).toBe(false)
    }
  })

  it('Planjahre stammen aus dem Vorbericht mit den Wertarten der Haushaltsdaten (D-01)', () => {
    haushalt.jahre.forEach((jahr, index) => {
      const p = punkte.find((x) => x.jahr === jahr)
      expect(p?.quelle, String(jahr)).toBe('vorbericht')
      expect(p?.wertart, String(jahr)).toBe(haushalt.wertarten[index])
    })
  })

  it('nutzt für kein Planjahr einen Grundzahl-Wert (D-01)', () => {
    const planPunkte = punkte.filter((p) => haushalt.jahre.includes(p.jahr))
    expect(planPunkte.length).toBe(haushalt.jahre.length)
    expect(planPunkte.some((p) => p.quelle === 'grundzahlen')).toBe(false)
  })

  it('liefert für fehlende Werte null, nie undefined', () => {
    for (const p of punkte) {
      expect(p.wert === null || typeof p.wert === 'number').toBe(true)
    }
  })
})

describe('baueZeitreihe: Fehlerfälle', () => {
  it('wirft bei einem unbekannten Posten und nennt ihn', () => {
    expect(() => baueZeitreihe('gibt_es_nicht')).toThrow('gibt_es_nicht')
  })

  it('wirft bei einem Prototyp-Schlüssel', () => {
    expect(() => baueZeitreihe('__proto__')).toThrow('__proto__')
  })
})

describe('zeitreihenSerien', () => {
  const punkte: Zeitpunkt[] = [
    punkt(1, 10, 'ergebnis'),
    punkt(2, 20, 'ergebnis'),
    punkt(3, 30, 'ansatz'),
    punkt(4, 40, 'ansatz'),
    punkt(5, 50, 'planung'),
    punkt(6, 60, 'planung'),
  ]

  it('liefert drei Serien in der Reihenfolge Ist, Ansatz, Planung über allen Jahren', () => {
    const { jahre, serien } = zeitreihenSerien(punkte)
    expect(jahre).toEqual([1, 2, 3, 4, 5, 6])
    expect(serien.map((s) => s.wertart)).toEqual(['ergebnis', 'ansatz', 'planung'])
    for (const serie of serien) {
      expect(serie.werte).toHaveLength(6)
      expect(serie.geteilt).toHaveLength(6)
    }
  })

  it('teilen sich Ist und Ansatz sowie Ansatz und Planung genau einen Punkt', () => {
    const [ist, ansatz, planung] = zeitreihenSerien(punkte).serien
    expect(ist?.werte).toEqual([10, 20, null, null, null, null])
    expect(ansatz?.werte).toEqual([null, 20, 30, 40, null, null])
    expect(planung?.werte).toEqual([null, null, null, 40, 50, 60])
  })

  it('der geteilte Punkt gehört nur der späteren Serie als „geteilt“ (symbol none)', () => {
    const [ist, ansatz, planung] = zeitreihenSerien(punkte).serien
    expect(ist?.geteilt.some(Boolean)).toBe(false)
    expect(ansatz?.geteilt).toEqual([false, true, false, false, false, false])
    expect(planung?.geteilt).toEqual([false, false, false, true, false, false])
  })

  it('der letzte Ist-Punkt ist der erste Ansatz-Punkt, der letzte Ansatz-Punkt der erste Planungs-Punkt', () => {
    const [ist, ansatz, planung] = zeitreihenSerien(punkte).serien
    const letzter = (werte: readonly (number | null)[]) =>
      werte
        .map((w, i) => (w === null ? -1 : i))
        .filter((i) => i >= 0)
        .at(-1)
    const erster = (werte: readonly (number | null)[]) => werte.findIndex((w) => w !== null)
    expect(letzter(ist?.werte ?? [])).toBe(erster(ansatz?.werte ?? []))
    expect(letzter(ansatz?.werte ?? [])).toBe(erster(planung?.werte ?? []))
  })

  it('fehlende Werte bleiben null (Lücke in der Linie), auch am Übergang', () => {
    const luecke: Zeitpunkt[] = [
      punkt(1, 10, 'ergebnis'),
      punkt(2, null, 'ergebnis'),
      punkt(3, 30, 'ansatz'),
      punkt(4, null, 'planung'),
      punkt(5, 50, 'planung'),
    ]
    const [ist, ansatz, planung] = zeitreihenSerien(luecke).serien
    expect(ist?.werte).toEqual([10, null, null, null, null])
    expect(ansatz?.werte).toEqual([null, null, 30, null, null])
    expect(planung?.werte).toEqual([null, null, 30, null, 50])
  })

  it('jeder Punkt liegt in genau einer Serie, außer den beiden geteilten', () => {
    const { serien } = zeitreihenSerien(punkte)
    const anzahl = punkte.map((_p, k) => serien.filter((s) => s.werte[k] !== null).length)
    expect(anzahl).toEqual([1, 2, 1, 2, 1, 1])
  })

  it('liefert für eine Reihe ohne Punkte leere Serien', () => {
    const { jahre, serien } = zeitreihenSerien([])
    expect(jahre).toEqual([])
    expect(serien).toHaveLength(3)
  })

  it('arbeitet mit den echten Daten: drei Serien über alle Jahre', () => {
    const echte = baueZeitreihe(STANDARD_ZEITREIHE)
    const { jahre, serien } = zeitreihenSerien(echte)
    expect(jahre).toEqual(echte.map((p) => p.jahr))
    expect(serien).toHaveLength(3)
    for (const serie of serien) {
      expect(serie.werte).toHaveLength(echte.length)
    }
  })
})

describe('betragText', () => {
  it('setzt „rd.“ vor einen in T€ gerundeten Betrag', () => {
    expect(betragText({ wert: 9_511_000, gerundet: true })).toBe(`rd. ${euro(9_511_000)}`)
  })

  it('lässt einen eurogenauen Betrag ohne „rd.“', () => {
    expect(betragText({ wert: 4_771_497, gerundet: false })).toBe(euro(4_771_497))
  })

  it('zeigt „–“ statt 0 ohne Wert, auch bei gerundeter Quelle', () => {
    expect(betragText({ wert: null, gerundet: true })).toBe('–')
  })
})

describe('Optionen und Quellen', () => {
  it('zeitreihenOptionen nennt jeden Posten mit dem gedruckten Namen', () => {
    const optionen = zeitreihenOptionen()
    expect(optionen.map((o) => o.posten)).toEqual(POSTEN_SCHLUESSEL)
    expect(optionen.every((o) => o.name.length > 0)).toBe(true)
    expect(optionen.find((o) => o.posten === 'gewerbesteuer')?.name).toBe('Gewerbesteuer')
  })

  it('zeitreihenSeite liefert die Vorberichtsseite der Tabelle des Postens', () => {
    expect(zeitreihenSeite('gewerbesteuer')).toBe(
      haushalt.vorbericht['steuerarten']?.posten[0]?.quelle,
    )
    expect(zeitreihenSeite('schluesselzuweisung')).toBe(
      haushalt.vorbericht['zuwendungen']?.posten[0]?.quelle,
    )
  })

  it('quellenFussnote nennt beide Quellen mit ihren Jahren', () => {
    const punkte: Zeitpunkt[] = [
      { ...punkt(2022, 1, 'ergebnis'), quelle: 'grundzahlen' },
      { ...punkt(2023, 2, 'ergebnis'), quelle: 'grundzahlen' },
      punkt(2024, 3, 'ergebnis'),
      punkt(2025, 4, 'ansatz'),
    ]
    expect(quellenFussnote(punkte)).toBe('Quelle: Grundzahlen (2022–2023), Vorbericht (ab 2024)')
  })

  it('quellenFussnote nennt ein einzelnes Grundzahl-Jahr ohne Spanne', () => {
    const punkte: Zeitpunkt[] = [
      { ...punkt(2023, 2, 'ergebnis'), quelle: 'grundzahlen' },
      punkt(2024, 3, 'ergebnis'),
    ]
    expect(quellenFussnote(punkte)).toBe('Quelle: Grundzahlen (2023), Vorbericht (ab 2024)')
  })

  it('quellenFussnote nennt ohne Grundzahlen nur den Vorbericht', () => {
    expect(quellenFussnote([punkt(2024, 3, 'ergebnis')])).toBe('Quelle: Vorbericht (ab 2024)')
  })
})

describe.runIf(haushalt.haushaltsjahr === 2026)(
  'Gewerbesteuer: Quellenwechsel (D-01, D-02)',
  () => {
    const punkte = baueZeitreihe('gewerbesteuer')
    const wert = (jahr: number) => punkte.find((p) => p.jahr === jahr)?.wert

    it('2022 und 2023 stammen aus den Grundzahlen (Ist)', () => {
      expect(wert(2022)).toBe(9_737_018)
      expect(wert(2023)).toBe(4_771_497)
    })

    it('2024 ist der vorläufige Ist-Wert des Vorberichts (9.511.000 €), nicht die Grundzahl 8.418.043 €', () => {
      expect(wert(2024)).toBe(9_511_000)
      expect(wert(2024)).not.toBe(8_418_043)
    })

    it('2026 ist der Ansatz 7.800.000 €, 2029 die Planung 9.300.000 €', () => {
      expect(wert(2026)).toBe(7_800_000)
      expect(wert(2029)).toBe(9_300_000)
    })

    it('Schlüsselzuweisung: 2023 Grundzahl, 2025 Vorbericht', () => {
      const schluessel = baueZeitreihe('schluesselzuweisung')
      expect(schluessel.find((p) => p.jahr === 2023)?.quelle).toBe('grundzahlen')
      expect(schluessel.find((p) => p.jahr === 2025)?.wert).toBe(2_807_000)
    })
  },
)

describe.each(POSTEN_SCHLUESSEL)('Belegschlüssel der Zeitreihe %s (D-01)', (posten) => {
  const eintrag = ZEITREIHEN_POSTEN.find((e) => e.posten === posten)
  const punkte = baueZeitreihe(posten)

  it('Grundzahl-Punkte tragen gz:{produkt}:{position}, Vorbericht-Punkte vb:{tabelle}:{posten}', () => {
    const grundzahl = eintrag === undefined ? undefined : findeGrundzahl(eintrag)
    for (const punkt of punkte) {
      const erwartet =
        punkt.quelle === 'grundzahlen'
          ? `gz:${ZEITREIHEN_PRODUKT}:${String(grundzahl?.position)}`
          : `vb:${eintrag?.tabelle ?? ''}:${posten}`
      expect(punkt.beleg, String(punkt.jahr)).toBe(erwartet)
    }
  })

  it('jeder Beleg löst auf und zeigt auf die Seite des Punkts', () => {
    for (const punkt of punkte) {
      const beleg = findeBeleg(punkt.beleg ?? '')
      expect(beleg, String(punkt.jahr)).not.toBeNull()
      expect(beleg?.pdfSeite, String(punkt.jahr)).toBe(punkt.pdfSeite)
    }
  })
})
