import { describe, expect, it } from 'vitest'

import { haushalt } from '@/data/daten'
import { baueKreisumlage, findeKlKnoten } from '@/lib/kreisumlage'

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
