import { describe, expect, it } from 'vitest'

import { euroKurz } from '@/charts/format'
import kennzahlKachelQuelle from '@/components/KennzahlKachel.vue?raw'
import { haushalt, investitionen } from '@/data/daten'
import { baueKennzahlen, quellenZeile } from '@/lib/kennzahlen'
import startSeiteQuelle from '@/pages/StartPage.vue?raw'

const GESAMT = haushalt.ergebnisplan.GESAMT
const FINANZPLAN = haushalt.finanzplan.GESAMT
const INDEX = haushalt.jahre.indexOf(haushalt.haushaltsjahr)
const EINWOHNER = Number(haushalt.meta.einwohner.wert)

function kennzahl(schluessel: string) {
  const treffer = baueKennzahlen().find((k) => k.schluessel === schluessel)
  if (treffer === undefined) {
    throw new Error(`Kennzahl ${schluessel} fehlt`)
  }
  return treffer
}

describe('baueKennzahlen', () => {
  it('liefert sieben Kennzahlen in der festen Reihenfolge der UI-SPEC', () => {
    expect(baueKennzahlen().map((k) => k.schluessel)).toEqual([
      'ertraege',
      'aufwendungen',
      'ergebnis',
      'investitionen',
      'kredite',
      'aufwand_pro_kopf',
      'steuern_pro_kopf',
    ])
  })

  it('jeder Wert entspricht seinem Quellfeld im Haushaltsjahr (Probe START-01)', () => {
    expect(GESAMT).toBeDefined()
    expect(FINANZPLAN).toBeDefined()
    expect(INDEX).toBeGreaterThanOrEqual(0)
    expect(kennzahl('ertraege').wert).toBe(GESAMT?.berechnet.ertraege[INDEX])
    expect(kennzahl('aufwendungen').wert).toBe(GESAMT?.berechnet.aufwand[INDEX])
    expect(kennzahl('ergebnis').wert).toBe(GESAMT?.zeilen.ergebnis_nach_minderaufwand?.[INDEX])
    expect(kennzahl('investitionen').wert).toBe(
      FINANZPLAN?.zeilen.auszahlungen_investitionen?.[INDEX],
    )
    expect(kennzahl('kredite').wert).toBe(FINANZPLAN?.zeilen.kreditaufnahme?.[INDEX])
  })

  it('Pro-Kopf-Werte sind gerundet, nicht abgerundet (Probe START-01)', () => {
    const aufwand = GESAMT?.berechnet.aufwand[INDEX] ?? Number.NaN
    const steuern = GESAMT?.zeilen.steuern?.[INDEX] ?? Number.NaN
    expect(kennzahl('aufwand_pro_kopf').wert).toBe(Math.round(aufwand / EINWOHNER))
    expect(kennzahl('steuern_pro_kopf').wert).toBe(Math.round(steuern / EINWOHNER))
  })

  it('nur die beiden Pro-Kopf-Werte sind berechnet', () => {
    const berechnet = baueKennzahlen()
      .filter((k) => k.berechnet)
      .map((k) => k.schluessel)
    expect(berechnet).toEqual(['aufwand_pro_kopf', 'steuern_pro_kopf'])
  })

  it('Defizit trägt das Wort „Defizit“, ein Überschuss das Wort „Überschuss“', () => {
    const ergebnis = kennzahl('ergebnis')
    expect(ergebnis.bezeichnung).toBe(
      ergebnis.wert < 0 ? 'Defizit nach Minderaufwand' : 'Überschuss nach Minderaufwand',
    )
  })

  it('jede Kennzahl nennt Wertart, Jahr und mindestens eine PDF-Seite', () => {
    for (const k of baueKennzahlen()) {
      expect(k.jahr, k.schluessel).toBe(haushalt.haushaltsjahr)
      expect(k.wertart.length, k.schluessel).toBeGreaterThan(0)
      expect(k.pdfSeiten.length, k.schluessel).toBeGreaterThan(0)
      for (const seite of k.pdfSeiten) {
        expect(Number.isInteger(seite) && seite >= 1, k.schluessel).toBe(true)
      }
    }
  })

  it('Seitenverweise: Ergebnisplan-Werte nennen GESAMT, Finanzplan-Werte die Finanzierung', () => {
    const gesamtSeite = haushalt.knoten.find((n) => n.code === 'GESAMT')?.pdf_seite
    expect(gesamtSeite).toBeDefined()
    expect(kennzahl('ertraege').pdfSeiten).toEqual([gesamtSeite])
    expect(kennzahl('aufwendungen').pdfSeiten).toEqual([gesamtSeite])
    expect(kennzahl('ergebnis').pdfSeiten).toEqual([gesamtSeite])
    expect(kennzahl('investitionen').pdfSeiten).toEqual([investitionen.finanzierung.quelle])
    expect(kennzahl('kredite').pdfSeiten).toEqual([investitionen.finanzierung.quelle])
    expect(kennzahl('aufwand_pro_kopf').pdfSeiten).toEqual([
      gesamtSeite,
      haushalt.meta.einwohner.quelle,
    ])
  })
})

describe('quellenZeile', () => {
  it('nennt Wertart, Jahr ohne Tausenderpunkt und die Seite im Singular', () => {
    expect(quellenZeile('Ansatz', 2026, [62])).toBe('Ansatz 2026 · PDF-Seite 62')
  })

  it('nennt mehrere Seiten im Plural, getrennt durch Komma', () => {
    expect(quellenZeile('Ansatz', 2026, [62, 25])).toBe('Ansatz 2026 · PDF-Seiten 62, 25')
  })
})

describe.runIf(haushalt.haushaltsjahr === 2026)('Kennzahlen Haushalt 2026', () => {
  it('die fünf Betragskacheln lesen 27,5 / 30,5 / -2,35 / 12,3 / 5,2 Mio. €', () => {
    const kurz = baueKennzahlen()
      .slice(0, 5)
      .map((k) => euroKurz(k.wert))
    expect(kurz).toEqual([
      '27,5 Mio. €',
      '30,5 Mio. €',
      '-2,35 Mio. €',
      '12,3 Mio. €',
      '5,2 Mio. €',
    ])
  })

  it('Pro-Kopf-Werte sind 2594 € und 1571 € (aufgerundet, nicht abgerundet)', () => {
    expect(kennzahl('aufwand_pro_kopf').wert).toBe(2594)
    expect(kennzahl('steuern_pro_kopf').wert).toBe(1571)
  })

  it('das Ergebnis heißt „Defizit nach Minderaufwand“', () => {
    expect(kennzahl('ergebnis').bezeichnung).toBe('Defizit nach Minderaufwand')
  })
})

describe('Vorlagen ohne eingetippte Beträge (Probe: Kennzahlwert nie im Template)', () => {
  it.each([
    ['StartPage.vue', startSeiteQuelle],
    ['KennzahlKachel.vue', kennzahlKachelQuelle],
  ])('%s enthält keinen Betrag wie „27,5 Mio.“', (_name, quelle) => {
    expect(quelle).not.toMatch(/\d+,\d+ Mio/)
  })
})
