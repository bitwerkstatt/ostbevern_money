import { describe, expect, it } from 'vitest'

import { euro } from '@/charts/format'
import { haushalt, texte } from '@/data/daten'
import {
  ABSCHREIBUNG_ZEILE,
  baueAufwandsarten,
  baueTransferaufwendungen,
  minderaufwandHinweis,
} from '@/lib/aufwandsarten'
import { findeBeleg } from '@/lib/quelle'
import { zeilenName } from '@/lib/zeilen'

const JAHRE = haushalt.jahre.map((jahr, index) => [jahr, index] as const)
const GESAMT = haushalt.ergebnisplan['GESAMT']
const TRANSFER_ZEILE = 'transferaufwendungen'
const KITA_POSTEN = 'zuschuesse_kindertageseinrichtungen'

function gep(zeile: string, index: number): number {
  const wert = GESAMT?.zeilen[zeile]?.[index]
  if (wert === undefined) {
    throw new Error(`Keine GEP-Zeile ${zeile} im Jahresindex ${String(index)}`)
  }
  return wert
}

function kitaWerte(index: number): number[] {
  const tabelle = haushalt.vorbericht['kita_zuschuesse']
  return (tabelle?.posten ?? []).flatMap((p) => {
    const wert = p.werte[index]
    return wert === null || wert === undefined ? [] : [wert]
  })
}

function aufwand(index: number): number {
  const wert = GESAMT?.berechnet.aufwand[index]
  if (wert === undefined) {
    throw new Error(`Kein Aufwand im Jahresindex ${String(index)}`)
  }
  return wert
}

describe('baueAufwandsarten (AUSG-04)', () => {
  it.each(JAHRE)(
    'Jahr %i: die Aufwandsarten ergeben den Gesamtaufwand (Druckrundung höchstens 1 €)',
    (_jahr, i) => {
      const summe = baueAufwandsarten(i).reduce((s, art) => s + art.wert, 0)
      // Z. 17 „Ordentliche Aufwendungen“ ist im PDF gedruckt; in einzelnen Jahren weicht die
      // Summe der Zeilen 11–16 wegen der Druckrundung um 1 € davon ab (2024).
      expect(Math.abs(summe - aufwand(i))).toBeLessThanOrEqual(1)
    },
  )

  it.each(JAHRE.filter(([jahr]) => jahr !== 2024))(
    'Jahr %i: die Summe stimmt auf den Euro mit dem Gesamtaufwand überein',
    (_jahr, i) => {
      const summe = baueAufwandsarten(i).reduce((s, art) => s + art.wert, 0)
      expect(summe).toBe(aufwand(i))
    },
  )

  it.each(JAHRE)(
    'Jahr %i: absteigend sortiert, keine Nullzeilen, Anteile summieren sich',
    (_j, i) => {
      const arten = baueAufwandsarten(i)
      expect(arten.length).toBeGreaterThan(0)
      for (let k = 1; k < arten.length; k += 1) {
        expect(arten[k - 1]?.wert ?? 0).toBeGreaterThanOrEqual(arten[k]?.wert ?? 0)
      }
      for (const art of arten) {
        expect(art.wert, art.schluessel).not.toBe(0)
        expect(art.anteil, art.schluessel).toBeGreaterThan(0)
      }
      const summeAnteile = arten.reduce((s, art) => s + art.anteil, 0)
      expect(summeAnteile).toBeCloseTo(1, 5)
    },
  )

  it.each(JAHRE)('Jahr %i: Namen stammen aus zeilen_namen', (_j, i) => {
    for (const art of baueAufwandsarten(i)) {
      expect(art.name, art.schluessel).toBe(zeilenName('ergebnisplan', art.schluessel))
      expect(art.name.length).toBeGreaterThan(0)
    }
  })

  it.each(JAHRE)('Jahr %i: nur die Abschreibungen sind „kein Geldfluss“', (_j, i) => {
    const arten = baueAufwandsarten(i)
    const markiert = arten.filter((art) => art.keinGeldfluss)
    expect(markiert.map((art) => art.schluessel)).toEqual([ABSCHREIBUNG_ZEILE])
  })

  it('wählt die Zeilen 11–16 und 20, keine Summenzeilen', () => {
    const schluessel = baueAufwandsarten(0).map((art) => art.schluessel)
    const erlaubt = new Set(
      haushalt.zeilen_namen.ergebnisplan
        .filter(
          (zeile) =>
            !zeile.ist_summe &&
            ((zeile.nummer >= '11' && zeile.nummer <= '16') || zeile.nummer === '20'),
        )
        .map((zeile) => zeile.schluessel),
    )
    expect(erlaubt.size).toBe(7)
    for (const eintrag of schluessel) {
      expect(erlaubt.has(eintrag), eintrag).toBe(true)
    }
  })

  it('wirft bei einem Jahresindex außerhalb der Jahre', () => {
    expect(() => baueAufwandsarten(haushalt.jahre.length)).toThrow()
  })
})

describe.runIf(haushalt.haushaltsjahr === 2026)('Aufwandsarten Haushalt 2026', () => {
  it('sieben Zeilen, Summe 30.455.569 €, größte Zeile sind die Transferaufwendungen', () => {
    const i = haushalt.jahre.indexOf(2026)
    const arten = baueAufwandsarten(i)
    expect(arten).toHaveLength(7)
    expect(arten.reduce((s, art) => s + art.wert, 0)).toBe(30455569)
    expect(arten[0]?.schluessel).toBe('transferaufwendungen')
  })
})

describe('baueTransferaufwendungen (AUSG-04)', () => {
  it.each(JAHRE)('Jahr %i: die Posten ergeben Z. 15 des GEP (T€-Toleranz je Posten)', (_j, i) => {
    const posten = baueTransferaufwendungen(i)
    expect(posten.length).toBeGreaterThan(0)
    const summe = posten.reduce((s, p) => s + p.wert, 0)
    expect(Math.abs(summe - gep(TRANSFER_ZEILE, i))).toBeLessThanOrEqual(posten.length * 1000)
  })

  it.each(JAHRE)('Jahr %i: jede Zeile ist „rd.“ und nennt ihre PDF-Seite', (_j, i) => {
    for (const p of baueTransferaufwendungen(i)) {
      expect(p.gerundet, p.posten).toBe(true)
      expect(p.quelle, p.posten).not.toBeNull()
      expect(p.name.length, p.posten).toBeGreaterThan(0)
      expect(Number.isFinite(p.wert), p.posten).toBe(true)
    }
  })

  it.each(JAHRE)('Jahr %i: absteigend sortiert', (_j, i) => {
    const posten = baueTransferaufwendungen(i)
    for (let k = 1; k < posten.length; k += 1) {
      expect(posten[k - 1]?.wert ?? 0).toBeGreaterThanOrEqual(posten[k]?.wert ?? 0)
    }
  })

  it.each(JAHRE)(
    'Jahr %i: Kita-Einrichtungen nur in Jahren, in denen sie gedruckt sind',
    (_j, i) => {
      const kita = baueTransferaufwendungen(i).find((p) => p.posten === KITA_POSTEN)
      const werte = kitaWerte(i)
      if (werte.length === 0) {
        expect(kita?.kinder).toBeUndefined()
        return
      }
      expect(kita?.kinder).toBeDefined()
      const kinder = kita?.kinder ?? []
      expect(kinder).toHaveLength(werte.length)
      const summe = kinder.reduce((s, k) => s + k.wert, 0)
      expect(Math.abs(summe - (kita?.wert ?? 0))).toBeLessThanOrEqual(kinder.length * 1000)
      for (const k of kinder) {
        expect(k.gerundet, k.posten).toBe(true)
        expect(k.quelle, k.posten).not.toBeNull()
      }
    },
  )

  it.each(JAHRE)('Jahr %i: kein Verweis auf eine Fußnote, die nicht gezeigt wird', (_j, i) => {
    for (const p of baueTransferaufwendungen(i)) {
      if (p.anmerkung === null) {
        expect(p.name, p.posten).not.toMatch(/Fußnote/)
      }
    }
  })

  it.each(JAHRE)(
    'Jahr %i: jede Zeile trägt vb:transferaufwendungen, jede Kita-Einrichtung vb:kita_zuschuesse',
    (_j, i) => {
      for (const p of baueTransferaufwendungen(i)) {
        expect(p.beleg, p.posten).toBe(`vb:transferaufwendungen:${p.posten}`)
        expect(findeBeleg(p.beleg ?? '')?.pdfSeite, p.posten).toBe(p.quelle)
        for (const k of p.kinder ?? []) {
          expect(k.beleg, k.posten).toBe(`vb:kita_zuschuesse:${k.posten}`)
          expect(findeBeleg(k.beleg ?? '')?.pdfSeite, k.posten).toBe(k.quelle)
        }
      }
    },
  )

  it('keine andere Zeile als die Kita-Zuschüsse hat Kinder', () => {
    for (const [, i] of JAHRE) {
      for (const p of baueTransferaufwendungen(i)) {
        if (p.posten !== KITA_POSTEN) {
          expect(p.kinder, p.posten).toBeUndefined()
        }
      }
    }
  })

  it('wirft bei einem Jahresindex außerhalb der Jahre', () => {
    expect(() => baueTransferaufwendungen(haushalt.jahre.length)).toThrow()
  })
})

describe.runIf(haushalt.haushaltsjahr === 2026)('Transferaufwendungen Haushalt 2026', () => {
  it('nennt die Kreisumlage als größten Posten und sieben Kita-Einrichtungen', () => {
    const i = haushalt.jahre.indexOf(2026)
    const posten = baueTransferaufwendungen(i)
    expect(posten[0]?.posten).toBe('kreisumlage')
    const kita = posten.find((p) => p.posten === KITA_POSTEN)
    expect(kita?.kinder).toHaveLength(7)
  })

  it('zeigt in 2025 keine Kita-Einrichtungen', () => {
    const i = haushalt.jahre.indexOf(2025)
    const kita = baueTransferaufwendungen(i).find((p) => p.posten === KITA_POSTEN)
    expect(kita).toBeDefined()
    expect(kita?.kinder).toBeUndefined()
  })
})

describe('minderaufwandHinweis (AUSG-02, Pitfall 6)', () => {
  it.each(JAHRE)('Jahr %i: Hinweis genau dann, wenn der Minderaufwand ≠ 0 ist', (_j, i) => {
    const wert = gep('globaler_minderaufwand', i)
    const hinweis = minderaufwandHinweis(i)
    if (wert === 0) {
      expect(hinweis).toBeNull()
      return
    }
    expect(hinweis).not.toBeNull()
    // Der GEP führt den Minderaufwand mit negativem Vorzeichen; der Hinweis nennt den Betrag.
    expect(wert).toBeLessThan(0)
    expect(hinweis?.betrag).toBe(-wert)
    expect(hinweis?.betrag ?? 0).toBeGreaterThan(0)
    expect(hinweis?.jahr).toBe(haushalt.jahre[i])
  })

  it.each(JAHRE)('Jahr %i: der Hinweis zeigt nie ein Minuszeichen (TXT-02)', (_j, i) => {
    const hinweis = minderaufwandHinweis(i)
    if (hinweis === null) {
      return
    }
    expect(hinweis.betrag).toBeGreaterThan(0)
    expect(hinweis.satz).not.toMatch(/[-−]\s?\d/)
    expect(hinweis.satz).toContain(`von ${euro(hinweis.betrag)}`)
  })

  it.each(JAHRE)('Jahr %i: geprüfter Text nur im Haushaltsjahr', (jahr, i) => {
    const hinweis = minderaufwandHinweis(i)
    if (hinweis === null) {
      return
    }
    expect(hinweis.textSchluessel).toBe(
      jahr === texte.haushaltsjahr ? 'globaler_minderaufwand' : null,
    )
  })

  it.each(JAHRE)(
    'Jahr %i: der zusammengesetzte Satz ist sauber und nennt Betrag und Jahr',
    (jahr, i) => {
      const hinweis = minderaufwandHinweis(i)
      if (hinweis === null) {
        return
      }
      expect(hinweis.satz).not.toMatch(/\{\{|\}\}|NaN|undefined|Infinity/)
      expect(hinweis.satz).toContain(euro(hinweis.betrag))
      expect(hinweis.satz).toContain(String(jahr))
      expect(hinweis.pdfSeite).not.toBeNull()
    },
  )

  it('wirft bei einem Jahresindex außerhalb der Jahre', () => {
    expect(() => minderaufwandHinweis(haushalt.jahre.length)).toThrow()
  })
})

describe.runIf(haushalt.haushaltsjahr === 2026)('Minderaufwand Haushalt 2026', () => {
  it('2024 ohne Hinweis, 2025 mit zusammengesetztem Satz, 2026 mit geprüftem Text', () => {
    expect(minderaufwandHinweis(haushalt.jahre.indexOf(2024))).toBeNull()
    const vorjahr = minderaufwandHinweis(haushalt.jahre.indexOf(2025))
    expect(vorjahr?.betrag).toBe(564600)
    expect(vorjahr?.textSchluessel).toBeNull()
    const jetzt = minderaufwandHinweis(haushalt.jahre.indexOf(2026))
    expect(jetzt?.betrag).toBe(600000)
    expect(jetzt?.textSchluessel).toBe('globaler_minderaufwand')
  })
})
