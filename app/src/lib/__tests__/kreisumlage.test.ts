import { describe, expect, it } from 'vitest'

import { haushalt } from '@/data/daten'
import { baueAufwandsarten } from '@/lib/aufwandsarten'
import {
  baueKreisumlage,
  findeKlKnoten,
  istGroessterEinzelposten,
  kreisumlageWert,
  pruefeGroessterEinzelposten,
} from '@/lib/kreisumlage'

const JAHRE = haushalt.jahre.map((j, i) => [j, i] as const)

describe('findeKlKnoten', () => {
  it('findet den einen synthetischen Knoten unterhalb von GESAMT', () => {
    const kl = findeKlKnoten()
    expect(kl.eltern).toBe('GESAMT')
    expect(kl.synthetisch).toBe(true)
    expect(haushalt.knoten.filter((k) => k.eltern === 'GESAMT' && k.synthetisch)).toHaveLength(1)
  })
})

describe('baueKreisumlage', () => {
  it.each(JAHRE)(
    'Jahr %i: Unterposten stimmen mit dem Gesamtbetrag überein (±3.000 €)',
    (_jahr, i) => {
      const kreisumlage = baueKreisumlage(i)
      const kl = findeKlKnoten()
      expect(kreisumlage.gesamt).toBe(haushalt.ergebnisplan[kl.code]?.berechnet.aufwand[i])
      expect(kreisumlage.unterposten.length).toBeGreaterThan(0)

      const summeUnterposten = kreisumlage.unterposten.reduce((s, u) => s + u.wert, 0)
      expect(Math.abs(summeUnterposten - kreisumlage.gesamt)).toBeLessThanOrEqual(3000)

      for (const u of kreisumlage.unterposten) {
        expect(u.gerundet, u.code).toBe(true)
        expect(u.pdfSeite, u.code).not.toBeNull()
        expect(u.wert, u.code).not.toBe(0)
        expect(u.name.length, u.code).toBeGreaterThan(0)
      }
    },
  )

  it('liefert Namen und PDF-Seite des Gesamtknotens', () => {
    const kreisumlage = baueKreisumlage(0)
    expect(kreisumlage.name).toBe(findeKlKnoten().name)
    expect(kreisumlage.pdfSeite).toBe(findeKlKnoten().pdf_seite)
  })

  it('wirft bei einem Jahresindex außerhalb der Jahre', () => {
    expect(() => baueKreisumlage(haushalt.jahre.length)).toThrow()
  })
})

describe.runIf(haushalt.haushaltsjahr === 2026)('Kreisumlage Haushalt 2026', () => {
  it('beträgt 11.001.181 € und ist der größte oberste Knoten nach Aufwand', () => {
    const i = haushalt.jahre.indexOf(2026)
    expect(baueKreisumlage(i).gesamt).toBe(11001181)

    const oberste = haushalt.knoten.filter((k) => k.eltern === 'GESAMT')
    const aufwand = (code: string) => haushalt.ergebnisplan[code]?.berechnet.aufwand[i] ?? 0
    const groesster = oberste.reduce((a, b) => (aufwand(b.code) > aufwand(a.code) ? b : a))
    expect(groesster.code).toBe(findeKlKnoten().code)
  })
})

describe('G-09-01: Superlativ „größter Einzelposten“ nur aus den Daten', () => {
  it.each(JAHRE)(
    'G-09-01: Weitergabe an Kreis und Land ist im Jahr %i der größte Einzelposten',
    (_jahr, i) => {
      expect(istGroessterEinzelposten(i)).toBe(true)
    },
  )

  it.each(JAHRE)(
    'G-09-01: Kreisumlage ist im Jahr %i größer als jede Aufwandsart ohne Transferaufwendungen',
    (_jahr, i) => {
      const kreisumlage = kreisumlageWert(i)
      const andere = baueAufwandsarten(i).filter((a) => a.schluessel !== 'transferaufwendungen')
      expect(andere.length).toBeGreaterThan(0)
      for (const art of andere) {
        expect(kreisumlage, art.name).toBeGreaterThan(art.wert)
      }
    },
  )

  it('G-09-01: ein Datensatz, in dem ein Aufgabenbereich größer ist, liefert falsch', () => {
    const basis = { gesamt: 11_000_000, kreisumlage: 10_000_000, aufwandsarten: [7_000_000] }
    expect(pruefeGroessterEinzelposten({ ...basis, bereiche: [4_500_000, 3_000_000] })).toBe(true)
    expect(pruefeGroessterEinzelposten({ ...basis, bereiche: [11_000_001] })).toBe(false)
  })

  it('G-09-01: ein Datensatz, in dem eine Aufwandsart größer ist als die Kreisumlage, liefert falsch', () => {
    const eingabe = {
      gesamt: 11_000_000,
      bereiche: [4_500_000],
      kreisumlage: 10_000_000,
      aufwandsarten: [10_000_001],
    }
    expect(pruefeGroessterEinzelposten(eingabe)).toBe(false)
  })

  it('G-09-01: gleich große Posten sind kein „größter“ Posten', () => {
    const eingabe = {
      gesamt: 5_000_000,
      bereiche: [5_000_000],
      kreisumlage: 4_000_000,
      aufwandsarten: [3_000_000],
    }
    expect(pruefeGroessterEinzelposten(eingabe)).toBe(false)
  })
})
