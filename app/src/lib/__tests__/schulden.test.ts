import type { EChartsOption } from 'echarts'
import { describe, expect, it } from 'vitest'

import { BERECHNET_DECAL, SCHULDEN_FARBEN } from '@/charts/echartsTheme'
import { euro, euroKurz, jahr as formatiereJahr } from '@/charts/format'
import { haushalt, investitionen } from '@/data/daten'
import { jahreListe, quellenZeile } from '@/lib/hilfsfunktionen'
import { belegSchluessel, findeBeleg } from '@/lib/quelle'
// Warum Quelltext: Der Block „die Seite rendert die Kacheln“ unten pinnt bewusst die Verdrahtung
// (06/IN-09): Die Seite ruft `schuldenKacheln()` auf und baut sie nicht selbst. Er beschränkt sich
// auf diese beiden stabilen Aussagen. Ohne DOM in der Testumgebung (`environment: 'node'`, kein
// DOM-Paket) lässt sich das nicht an der gerenderten Seite prüfen (D-14).
import investitionenSeiteQuelle from '@/pages/InvestitionenPage.vue?raw'
import {
  achsenZusatz,
  baueSchuldenstand,
  hatBerechneteJahre,
  jahreOhneLiquiditaetskredite,
  liquiditaetsSatz,
  schuldenKacheln,
  schuldenKennzahlen,
  schuldenstandOption,
  schuldenTabelle,
} from '@/lib/schulden'

// Alle Erwartungen stammen aus den Daten (Identitäten, Datenfelder); nur die für den Jahrgang
// festgehaltenen Werte stehen unter `describe.runIf` (RESEARCH Pitfall 3).
const stand = investitionen.schuldenstand
const vorjahrIndex = haushalt.jahre.indexOf(haushalt.haushaltsjahr) - 1

interface Datenpunkt {
  value: number
  decal: unknown
}

/** Die Datenpunkte der Serie `index` mit ihrem Decal; wirft bei einer unerwarteten Form. */
function datenpunkte(option: EChartsOption, index: number): Datenpunkt[] {
  const serien = option.series
  if (!Array.isArray(serien)) {
    throw new Error('series ist kein Array')
  }
  const serie = serien[index]
  if (serie === undefined || serie.type !== 'bar' || !Array.isArray(serie.data)) {
    throw new Error(`Serie ${String(index)} ist keine Säulenserie mit Daten`)
  }
  return serie.data.map((eintrag) => {
    if (
      typeof eintrag !== 'object' ||
      eintrag === null ||
      Array.isArray(eintrag) ||
      eintrag instanceof Date
    ) {
      throw new Error('Datenpunkt ist kein Objekt')
    }
    const wert = eintrag.value
    if (typeof wert !== 'number') {
      throw new Error('Datenpunkt ohne Zahl')
    }
    const itemStyle = eintrag.itemStyle
    return { value: wert, decal: itemStyle?.decal }
  })
}

function serienNamen(option: EChartsOption): string[] {
  const serien = option.series
  if (!Array.isArray(serien)) {
    throw new Error('series ist kein Array')
  }
  return serien.map((serie) => String(serie.name ?? ''))
}

describe('baueSchuldenstand (INV-04, D-09)', () => {
  it('liefert die Reihen unverändert aus den Daten (null bleibt null)', () => {
    const reihen = baueSchuldenstand()
    expect(reihen.jahre).toEqual(investitionen.jahre)
    expect(reihen.wertarten).toEqual(investitionen.wertarten)
    expect(reihen.investitionskredite).toEqual(stand.investitionskredite)
    expect(reihen.nrwBank).toEqual(stand.nrw_bank)
    expect(reihen.liquiditaetskredite).toEqual(stand.liquiditaetskredite)
    expect(reihen.gesamt).toEqual(stand.gesamt)
    expect(reihen.proKopf).toEqual(stand.pro_kopf)
    expect(reihen.berechnet).toEqual(stand.berechnet)
    expect(reihen.formel).toBe(stand.formel)
    expect(reihen.pdfSeite).toBe(stand.quelle)
  })

  it('hat für jedes Jahr einen Eintrag in jeder Reihe', () => {
    const reihen = baueSchuldenstand()
    for (const reihe of [
      reihen.wertarten,
      reihen.investitionskredite,
      reihen.nrwBank,
      reihen.liquiditaetskredite,
      reihen.gesamt,
      reihen.proKopf,
      reihen.berechnet,
    ]) {
      expect(reihe).toHaveLength(reihen.jahre.length)
    }
  })

  it('gesamt = Investitionskredite + NRW.Bank in jedem Jahr, ohne Liquiditätskredite (T-06-23)', () => {
    const reihen = baueSchuldenstand()
    reihen.jahre.forEach((_jahr, i) => {
      expect(reihen.gesamt[i]).toBe((reihen.investitionskredite[i] ?? 0) + (reihen.nrwBank[i] ?? 0))
    })
  })

  it('pro_kopf ist gesamt geteilt durch die Einwohner, abgerundet (T-06-23)', () => {
    const reihen = baueSchuldenstand()
    reihen.jahre.forEach((_jahr, i) => {
      expect(reihen.proKopf[i]).toBe(Math.floor((reihen.gesamt[i] ?? 0) / stand.einwohner))
    })
  })
})

describe('jahreOhneLiquiditaetskredite (D-09, Pitfall 3)', () => {
  it('nennt genau die Jahre, deren Liquiditätskredit null ist', () => {
    const erwartet = investitionen.jahre.filter((_jahr, i) => stand.liquiditaetskredite[i] === null)
    expect(jahreOhneLiquiditaetskredite()).toEqual(erwartet)
  })

  it('liquiditaetsSatz nennt diese Jahre aus den Daten, sonst null', () => {
    const jahre = jahreOhneLiquiditaetskredite()
    const satz = liquiditaetsSatz()
    if (jahre.length === 0) {
      expect(satz).toBeNull()
    } else {
      expect(satz).toBe(
        `Für ${jahreListe(jahre)} nennt der Haushaltsplan keine Liquiditätskredite.`,
      )
    }
  })
})

describe('jahreListe', () => {
  it.each([
    [[], ''],
    [[2027], '2027'],
    [[2027, 2028], '2027 und 2028'],
    [[2027, 2028, 2029], '2027, 2028 und 2029'],
  ])('formatiert %j als „%s“ (Jahreszahl ohne Tausenderpunkt)', (jahre, erwartet) => {
    expect(jahreListe(jahre)).toBe(erwartet)
  })
})

describe('schuldenKennzahlen (D-09, D-10, Nutzerentscheidung 4)', () => {
  it('liefert die Werte des Vorjahrs mit den beiden Belegseiten', () => {
    const kennzahlen = schuldenKennzahlen()
    expect(vorjahrIndex).toBeGreaterThanOrEqual(0)
    expect(kennzahlen.jahr).toBe(haushalt.haushaltsjahr - 1)
    expect(kennzahlen.gesamt).toBe(stand.gesamt[vorjahrIndex])
    expect(kennzahlen.proKopf).toBe(stand.pro_kopf[vorjahrIndex])
    expect(kennzahlen.quelle).toBe(stand.quelle)
    expect(kennzahlen.einwohnerQuelle).toBe(haushalt.meta.einwohner.quelle)
    expect(kennzahlen.pdfSeiten).toEqual([stand.quelle, haushalt.meta.einwohner.quelle])
  })

  it('trägt berechnet nur, wenn das Datenfeld des Vorjahrs wahr ist', () => {
    expect(schuldenKennzahlen().berechnet).toBe(stand.berechnet[vorjahrIndex])
  })
})

describe('schuldenKacheln (WR-03, D-09, D-10)', () => {
  it('liefert genau die beiden Kacheln in dieser Reihenfolge', () => {
    expect(schuldenKacheln().map((kachel) => kachel.schluessel)).toEqual([
      'schuldenstand',
      'schulden_je_einwohner',
    ])
  })

  it('baut Bezeichnung, Wert und Quellenzeile aus den Kennzahlen des Vorjahrs', () => {
    const kennzahlen = schuldenKennzahlen()
    const [gesamt, proKopf] = schuldenKacheln(kennzahlen)
    expect(gesamt?.bezeichnung).toBe(`Schuldenstand Ende ${formatiereJahr(kennzahlen.jahr)}`)
    expect(gesamt?.wert).toBe(euroKurz(kennzahlen.gesamt))
    expect(gesamt?.zeile).toBe(
      quellenZeile(kennzahlen.wertart, kennzahlen.jahr, [kennzahlen.quelle]),
    )
    expect(proKopf?.bezeichnung).toBe('Schulden je Einwohner')
    expect(proKopf?.wert).toBe(euro(kennzahlen.proKopf))
    expect(proKopf?.zeile).toBe(
      quellenZeile(kennzahlen.wertart, kennzahlen.jahr, kennzahlen.pdfSeiten),
    )
  })

  it.each([true, false])('markiert beide Kacheln gleich, wenn berechnet %s ist', (berechnet) => {
    const kacheln = schuldenKacheln({ ...schuldenKennzahlen(), berechnet })
    expect(kacheln).toHaveLength(2)
    expect(kacheln.map((kachel) => kachel.berechnet)).toEqual([berechnet, berechnet])
  })

  it('folgt auf den echten Daten dem Datenfeld des Vorjahrs', () => {
    const erwartet = stand.berechnet[vorjahrIndex]
    expect(schuldenKacheln().map((kachel) => kachel.berechnet)).toEqual([erwartet, erwartet])
  })

  it('belegt beide Kacheln mit der Schuldenstandsreihe der Investitionskredite (D-01)', () => {
    for (const kachel of schuldenKacheln()) {
      expect(kachel.quelle).toBe(belegSchluessel.sd('investitionskredite'))
      expect(findeBeleg(kachel.quelle)).not.toBeNull()
    }
  })

  it('nennt die Herleitung aus den Namen der Reihen (Schuldenstand) und der Einwohnerzahl (je Einwohner)', () => {
    const [gesamt, proKopf] = schuldenKacheln()
    expect(gesamt?.herleitung).toBe('Investitionskredite plus NRW.Bank')
    expect(proKopf?.herleitung).toContain('Investitionskredite plus NRW.Bank')
    expect(proKopf?.herleitung).toContain('geteilt durch die Einwohnerzahl')
  })

  it('gibt die Wertart der Seitenleiste als „{Wertart} {Jahr}“ mit', () => {
    const kennzahlen = schuldenKennzahlen()
    const erwartet = `${kennzahlen.wertart} ${formatiereJahr(kennzahlen.jahr)}`
    expect(schuldenKacheln().map((kachel) => kachel.wertart)).toEqual([erwartet, erwartet])
  })

  it('die Seite rendert die Kacheln, sie baut sie nicht selbst (Quelltext)', () => {
    expect(investitionenSeiteQuelle).toContain('schuldenKacheln()')
    expect(investitionenSeiteQuelle).not.toContain('schuldenKennzahlen(')
  })
})

describe('achsenZusatz (T-06-24)', () => {
  it('trägt „berechnet“ genau dort, wo berechnet[i] wahr ist', () => {
    const achse = achsenZusatz()
    expect(achse).toHaveLength(stand.berechnet.length)
    stand.berechnet.forEach((berechnet, i) => {
      expect(achse[i]?.split('\n').includes('berechnet')).toBe(berechnet)
    })
  })

  it('nennt in der ersten Zeile das Jahr', () => {
    achsenZusatz().forEach((beschriftung, i) => {
      expect(beschriftung.split('\n')[0]).toBe(String(investitionen.jahre[i]))
    })
  })

  it('hatBerechneteJahre folgt dem Datenfeld', () => {
    expect(hatBerechneteJahre()).toBe(stand.berechnet.some(Boolean))
  })
})

describe('schuldenstandOption (D-09, INV-04)', () => {
  it.each([false, true])('stapelt nur Investitionskredite und NRW.Bank (schmal: %s)', (schmal) => {
    const option = schuldenstandOption(schmal)
    expect(serienNamen(option)).toEqual(['Investitionskredite', 'NRW.Bank'])
    const ik = datenpunkte(option, 0).map((punkt) => punkt.value)
    const nrw = datenpunkte(option, 1).map((punkt) => punkt.value)
    expect(ik).toEqual(stand.investitionskredite)
    expect(nrw).toEqual(stand.nrw_bank)
    // Die Summe des Stapels ist der gedruckte bzw. fortgeschriebene Schuldenstand, ohne Liquiditätskredite.
    expect(ik.map((wert, i) => wert + (nrw[i] ?? 0))).toEqual(stand.gesamt)
  })

  it('enthält keine Liquiditätskredite-Serie und keine Farbe dafür', () => {
    const namen = serienNamen(schuldenstandOption(false)).join(' ')
    expect(namen).not.toContain('Liquidität')
    expect(JSON.stringify(schuldenstandOption(false))).not.toContain(
      SCHULDEN_FARBEN.liquiditaetskredite,
    )
  })

  it('setzt BERECHNET_DECAL genau an den Jahren mit berechnet === true (T-06-24)', () => {
    const option = schuldenstandOption(false)
    for (const serie of [0, 1]) {
      datenpunkte(option, serie).forEach((punkt, i) => {
        if (stand.berechnet[i] === true) {
          expect(punkt.decal).toBe(BERECHNET_DECAL)
        } else {
          expect(punkt.decal).toBeUndefined()
        }
      })
    }
  })

  it('die x-Achse ist die Achse von achsenZusatz', () => {
    const achse = schuldenstandOption(false).xAxis
    if (Array.isArray(achse) || achse === undefined || !('data' in achse)) {
      throw new Error('xAxis ohne data')
    }
    expect(achse.data).toEqual(achsenZusatz())
  })
})

describe('schuldenTabelle (D-09, Pitfall 3)', () => {
  it('zeigt einen fehlenden Liquiditätskredit als null (nie 0)', () => {
    const tabelle = schuldenTabelle()
    expect(tabelle.zeilen.map((zeile) => zeile['liquiditaetskredite'])).toEqual(
      stand.liquiditaetskredite,
    )
  })

  it('hat je Jahr eine Zeile und kennzeichnet nur berechnete Jahre', () => {
    const tabelle = schuldenTabelle()
    expect(tabelle.zeilen).toHaveLength(investitionen.jahre.length)
    tabelle.zeilen.forEach((zeile, i) => {
      expect(zeile['etikett']).toBe(stand.berechnet[i] === true ? 'berechnet' : null)
      expect(zeile['gesamt']).toBe(stand.gesamt[i])
      expect(zeile['proKopf']).toBe(stand.pro_kopf[i])
    })
  })

  it('enthält die Spalten Jahr, Investitionskredite, NRW.Bank, Schuldenstand, Liquiditätskredite, Je Einwohner', () => {
    expect(schuldenTabelle().spalten.map((spalte) => spalte.schluessel)).toEqual([
      'jahr',
      'investitionskredite',
      'nrwBank',
      'gesamt',
      'liquiditaetskredite',
      'proKopf',
    ])
  })
})

describe.runIf(haushalt.haushaltsjahr === 2026)('Jahrgang 2026 (ROADMAP SC 2)', () => {
  it('Schuldenstand Ende des Vorjahrs 7.710.000 €, je Einwohner 656 €, gedruckt', () => {
    const kennzahlen = schuldenKennzahlen()
    expect(kennzahlen.gesamt).toBe(7_710_000)
    expect(kennzahlen.proKopf).toBe(656)
    expect(kennzahlen.berechnet).toBe(false)
  })

  it('beide Schuldenkacheln: Ende 2025 mit 7,71 Mio. € und 656 €, ohne „berechnet“', () => {
    const [gesamt, proKopf] = schuldenKacheln()
    expect(gesamt?.bezeichnung).toBe('Schuldenstand Ende 2025')
    expect(gesamt?.wert).toBe(euroKurz(7_710_000))
    expect(proKopf?.wert).toBe(euro(656))
    expect(gesamt?.berechnet).toBe(false)
    expect(proKopf?.berechnet).toBe(false)
  })

  it('berechnet = [false, false, false, true, true, true]', () => {
    expect(baueSchuldenstand().berechnet).toEqual([false, false, false, true, true, true])
  })

  it('Liquiditätskredite fehlen in den drei letzten Jahren', () => {
    expect(jahreOhneLiquiditaetskredite()).toEqual([2027, 2028, 2029])
    expect(liquiditaetsSatz()).toBe(
      'Für 2027, 2028 und 2029 nennt der Haushaltsplan keine Liquiditätskredite.',
    )
  })
})
