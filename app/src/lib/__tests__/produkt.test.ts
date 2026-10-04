import { describe, expect, it } from 'vitest'

import { haushalt, investitionen, produkte } from '@/data/daten'
import { proKopf } from '@/lib/berechnung'
import { wertartFuerJahr, wertartName } from '@/lib/jahr'
import {
  BEZUGSGROESSEN,
  baueErlaeuterungen,
  baueGrundzahlen,
  baueInvestitionenTabelle,
  baueProduktInvestitionen,
  baueProduktKopf,
  baueTeilergebnisplan,
  bindungsgradText,
  jahrSchluessel,
} from '@/lib/produkt'
import { zeilenName } from '@/lib/zeilen'

// Alle Testdaten kommen aus den App-Daten, nicht aus Literalen.
const erstes = produkte[0]

describe('Testdaten', () => {
  it('enthalten die 63 Produkte des Haushalts', () => {
    expect(produkte).toHaveLength(63)
    expect(erstes).toBeDefined()
  })
})

describe('bindungsgradText', () => {
  it('schreibt die drei Werte der Pipeline aus', () => {
    expect(bindungsgradText('pflichtig')).toBe('pflichtig')
    expect(bindungsgradText('freiwillig')).toBe('freiwillig')
    expect(bindungsgradText('teils')).toBe('teils pflichtig, teils freiwillig')
  })

  it('gibt einen unbekannten Wert unverändert zurück', () => {
    expect(bindungsgradText('unklar')).toBe('unklar')
  })

  it('löst Prototyp-Schlüssel nicht auf', () => {
    expect(bindungsgradText('__proto__')).toBe('__proto__')
    expect(bindungsgradText('constructor')).toBe('constructor')
  })
})

describe('baueProduktKopf (D-09)', () => {
  it.each(produkte.map((p) => p.code))('baut den Kopf von Produkt %s', (code) => {
    const kopf = baueProduktKopf(code)
    expect(kopf).not.toBeNull()
    if (kopf === null) {
      return
    }
    expect(kopf.produkt.code).toBe(code)
    expect(kopf.pbName).toBe(haushalt.knoten.find((k) => k.code === kopf.produkt.pb)?.name)
    expect(kopf.pgName).toBe(haushalt.knoten.find((k) => k.code === kopf.produkt.pg)?.name)
    expect(kopf.pbName).not.toBe('')
    expect(kopf.pgName).not.toBe('')
    expect(kopf.quelleSeite).toBe(kopf.produkt.pdf_seiten[0])
  })

  it('führt ohne gemerkten Zustand zur Produktgruppe des Produkts', () => {
    const kopf = baueProduktKopf(erstes?.code ?? '')
    expect(kopf?.zurueck).toEqual({
      name: 'ausgaben',
      query: { pb: erstes?.pb, pg: erstes?.pg },
    })
    expect(kopf?.zurueckText).toBe(kopf?.pgName)
  })

  it('behält Modus, Aufgabenbereich und Produktgruppe aus einer gültigen Query', () => {
    const kopf = baueProduktKopf(erstes?.code ?? '', {
      modus: 'zuschussbedarf',
      pb: erstes?.pb,
      pg: erstes?.pg,
    })
    expect(kopf?.zurueck).toEqual({
      name: 'ausgaben',
      query: { modus: 'zuschussbedarf', pb: erstes?.pb, pg: erstes?.pg },
    })
  })

  it('benennt den Aufgabenbereich, wenn die gemerkte Query keine Produktgruppe trägt', () => {
    const kopf = baueProduktKopf(erstes?.code ?? '', { pb: erstes?.pb })
    expect(kopf?.zurueck).toEqual({ name: 'ausgaben', query: { pb: erstes?.pb } })
    expect(kopf?.zurueckText).toBe(kopf?.pbName)
  })

  it('verwirft eine gemerkte Query, die zu einem anderen Aufgabenbereich gehört', () => {
    const fremd = haushalt.knoten.find(
      (k) => k.eltern === 'GESAMT' && k.code !== erstes?.pb && k.code !== 'KL',
    )
    expect(fremd).toBeDefined()
    const kopf = baueProduktKopf(erstes?.code ?? '', { pb: fremd?.code })
    expect(kopf?.zurueck).toEqual({
      name: 'ausgaben',
      query: { pb: erstes?.pb, pg: erstes?.pg },
    })
  })

  it('verwirft unbrauchbare Query-Werte, ohne sie weiterzureichen', () => {
    const kopf = baueProduktKopf(erstes?.code ?? '', {
      modus: '<script>',
      pb: '__proto__',
      pg: ['x'],
    })
    expect(kopf?.zurueck).toEqual({
      name: 'ausgaben',
      query: { pb: erstes?.pb, pg: erstes?.pg },
    })
  })

  it.each(['__proto__', 'constructor', 'toString', 'GESAMT', '999999', ''])(
    'liefert für den Code %j kein Produkt',
    (code) => {
      expect(baueProduktKopf(code)).toBeNull()
    },
  )

  it('nennt ein abweichendes Original des Bindungsgrads, sonst nicht', () => {
    for (const produkt of produkte) {
      const kopf = baueProduktKopf(produkt.code)
      expect(kopf?.bindungsgrad).toBe(bindungsgradText(produkt.bindungsgrad))
      if (kopf?.bindungsgradOriginal !== null) {
        expect(kopf?.bindungsgradOriginal).toBe(produkt.bindungsgrad_original)
      }
    }
    const rein = produkte.find((p) => p.bindungsgrad === 'pflichtig')
    expect(baueProduktKopf(rein?.code ?? '')?.bindungsgradOriginal).toBeNull()
  })
})

const einwohner = haushalt.meta.einwohner.wert
const ERLAUBTE_PRODUKT_FELDER: ReadonlySet<string> = new Set([
  'code',
  'name',
  'pb',
  'pg',
  'fachbereich',
  'gremium',
  'beschreibung',
  'leistungen',
  'auftragsgrundlage',
  'bindungsgrad',
  'bindungsgrad_original',
  'klassifizierung',
  'zielgruppe',
  'ziele',
  'erlaeuterungen',
  'pdf_seiten',
  'grundzahlen',
])
const SUMMENZEILEN = ['ordentliche_ertraege', 'ordentliche_aufwendungen', 'jahresergebnis']

function ergebnisplanVon(code: string) {
  const werte = haushalt.ergebnisplan[code]
  if (werte === undefined) {
    throw new Error(`Kein Ergebnisplan für ${code}`)
  }
  return werte
}

describe('baueTeilergebnisplan (AUSG-05, D-23)', () => {
  it('beschriftet die Spalten mit Wertart und Jahr aus den Daten', () => {
    const plan = baueTeilergebnisplan(erstes?.code ?? '')
    const erwartet = haushalt.jahre.map((j) => `${wertartName(wertartFuerJahr(j))} ${j}`)
    expect(plan?.spalten.slice(1).map((s) => s.titel)).toEqual(erwartet)
    expect(plan?.spalten[0]?.art).toBe('text')
    expect(plan?.spalten.slice(1).every((s) => s.art === 'euro')).toBe(true)
    const erstesJahr = haushalt.jahre[0]
    const letztesJahr = haushalt.jahre.at(-1)
    expect(plan?.titel).toBe(`Teilergebnisplan ${erstesJahr}–${letztesJahr}`)
  })

  it('liefert für unbekannte Codes null', () => {
    expect(baueTeilergebnisplan('__proto__')).toBeNull()
    expect(baueTeilergebnisplan('999999')).toBeNull()
  })

  it.each(produkte.map((p) => p.code))(
    'zeigt für %s jede Zeile mit Wert, die Summen und stimmt mit dem Ergebnisplan überein',
    (code) => {
      const plan = baueTeilergebnisplan(code)
      const werte = ergebnisplanVon(code)
      expect(plan).not.toBeNull()
      const zeilen = plan?.zeilen ?? []
      const einfache = zeilen.filter((z) => z.etikett === null)
      const gezeigt = einfache.map((z) => z.schluessel)

      for (const [schluessel, reihe] of Object.entries(werte.zeilen)) {
        const hatWert = reihe.some((wert) => wert !== 0)
        const istSumme = SUMMENZEILEN.includes(schluessel)
        expect(gezeigt.includes(schluessel)).toBe(hatWert || istSumme)
      }
      for (const zeile of einfache) {
        const reihe = werte.zeilen[String(zeile.schluessel)]
        expect(zeile.name).toBe(zeilenName('ergebnisplan', String(zeile.schluessel)))
        haushalt.jahre.forEach((j, i) => {
          expect(zeile[jahrSchluessel(j)]).toBe(reihe?.[i])
        })
      }
    },
  )

  it.each(produkte.map((p) => p.code))(
    'hängt für %s die berechneten Zeilen mit Etikett an',
    (code) => {
      const plan = baueTeilergebnisplan(code)
      const werte = ergebnisplanVon(code)
      const berechnet = (plan?.zeilen ?? []).filter((z) => z.etikett === 'berechnet')
      expect(berechnet.map((z) => z.schluessel)).toEqual([
        'zuschussbedarf',
        'zuschussbedarf_je_einwohner',
      ])
      expect(berechnet.map((z) => z.name)).toEqual([
        'Zuschussbedarf (berechnet)',
        'Zuschussbedarf je Einwohner (berechnet)',
      ])
      haushalt.jahre.forEach((j, i) => {
        const zuschuss = werte.berechnet.zuschussbedarf[i] ?? Number.NaN
        expect(berechnet[0]?.[jahrSchluessel(j)]).toBe(zuschuss)
        expect(berechnet[1]?.[jahrSchluessel(j)]).toBe(proKopf(zuschuss, Number(einwohner)))
      })
    },
  )
})

describe('BEZUGSGROESSEN (Freigabe 05-03, Open Question 6)', () => {
  it('enthält genau die freigegebenen Produkte', () => {
    expect(BEZUGSGROESSEN.map((b) => b.produkt)).toEqual(['030101', '030102', '040301', '060101'])
  })

  it.each(BEZUGSGROESSEN.map((b) => [b.produkt, b] as const))(
    'nennt für %s Grundzahlen, die im Produkt genau einmal vorkommen',
    (_code, bezug) => {
      const produkt = produkte.find((p) => p.code === bezug.produkt)
      expect(produkt).toBeDefined()
      expect(bezug.bezeichnungen.length).toBeGreaterThan(0)
      for (const bezeichnung of bezug.bezeichnungen) {
        expect(produkt?.grundzahlen.filter((g) => g.bezeichnung === bezeichnung)).toHaveLength(1)
      }
    },
  )
})

describe('baueGrundzahlen (AUSG-05)', () => {
  it('liefert null für Produkte ohne Grundzahlen', () => {
    const ohne = produkte.filter((p) => p.grundzahlen.length === 0)
    expect(ohne).toHaveLength(15)
    for (const produkt of ohne) {
      expect(baueGrundzahlen(produkt.code)).toBeNull()
    }
    expect(baueGrundzahlen('__proto__')).toBeNull()
  })

  it.each(produkte.filter((p) => p.grundzahlen.length > 0).map((p) => p.code))(
    'zeigt für %s jede Grundzahl mit ihren Werten und nur freigegebene Je-Einheit-Zeilen',
    (code) => {
      const tabelle = baueGrundzahlen(code)
      const produkt = produkte.find((p) => p.code === code)
      expect(tabelle).not.toBeNull()
      const zeilen = tabelle?.zeilen ?? []
      const einfache = zeilen.filter((z) => z.etikett === null)
      const berechnet = zeilen.filter((z) => z.etikett === 'berechnet')

      expect(einfache).toHaveLength(produkt?.grundzahlen.length ?? -1)
      produkt?.grundzahlen.forEach((grundzahl, index) => {
        const zeile = einfache[index]
        expect(zeile?.einheit).toBe(grundzahl.einheit)
        for (const wert of grundzahl.werte) {
          expect(zeile?.[jahrSchluessel(wert.jahr)]).toBe(wert.wert)
        }
      })

      const freigegeben = BEZUGSGROESSEN.filter((b) => b.produkt === code)
      expect(berechnet).toHaveLength(freigegeben.length)
      expect(zeilen.filter((z) => String(z.name).includes('Zuschussbedarf je'))).toHaveLength(
        freigegeben.length,
      )
    },
  )

  it('wählt dezimale Spalten genau dann, wenn eine Grundzahl Nachkommastellen hat', () => {
    for (const produkt of produkte.filter((p) => p.grundzahlen.length > 0)) {
      const mitKomma = produkt.grundzahlen.some((g) => g.nachkommastellen > 0)
      const jahrSpalten = baueGrundzahlen(produkt.code)?.spalten.slice(2) ?? []
      expect(jahrSpalten.length).toBeGreaterThan(0)
      expect(jahrSpalten.every((s) => s.art === (mitKomma ? 'dezimal' : 'zahl'))).toBe(true)
    }
    expect(produkte.some((p) => p.grundzahlen.some((g) => g.nachkommastellen > 0))).toBe(true)
  })

  it('rechnet Zuschussbedarf je Einheit nur für Jahre mit beiden Werten', () => {
    for (const bezug of BEZUGSGROESSEN) {
      const produkt = produkte.find((p) => p.code === bezug.produkt)
      const zuschuss = ergebnisplanVon(bezug.produkt).berechnet.zuschussbedarf
      const tabelle = baueGrundzahlen(bezug.produkt)
      const zeile = tabelle?.zeilen.find((z) => z.etikett === 'berechnet')
      expect(zeile?.name).toBe(`Zuschussbedarf je ${bezug.einheitText} (berechnet)`)
      const jahrSpalten = tabelle?.spalten.slice(2) ?? []
      for (const spalte of jahrSpalten) {
        const j = Number(spalte.schluessel.slice(1))
        const planIndex = haushalt.jahre.indexOf(j)
        const teile = bezug.bezeichnungen.map((bezeichnung) =>
          produkt?.grundzahlen
            .find((g) => g.bezeichnung === bezeichnung)
            ?.werte.find((w) => w.jahr === j),
        )
        const wert = zeile?.[spalte.schluessel]
        if (planIndex < 0 || teile.some((t) => t === undefined)) {
          expect(wert).toBeNull()
        } else {
          const summe = teile.reduce((gesamt, t) => gesamt + (t?.wert ?? 0), 0)
          expect(wert).toBe(Math.round((zuschuss[planIndex] ?? Number.NaN) / summe))
        }
      }
      // Mindestens ein Jahr hat beide Werte (2024/2025 liegen im Plan und bei den Grundzahlen).
      expect(jahrSpalten.some((s) => zeile?.[s.schluessel] !== null)).toBe(true)
    }
  })

  it('fasst die Hinweise der Grundzahlen als Fußnote zusammen', () => {
    const tabelle = baueGrundzahlen(erstes?.code ?? '')
    const hinweise = new Set(
      erstes?.grundzahlen.flatMap((g) => g.werte.map((w) => w.hinweis).filter((h) => h !== null)) ??
        [],
    )
    expect(hinweise.size).toBeGreaterThan(0)
    for (const hinweis of hinweise) {
      expect(tabelle?.fussnote).toContain(hinweis)
    }
  })
})

describe('baueProduktInvestitionen (AUSG-05)', () => {
  it('liefert genau die Maßnahmen mit dem Produktcode', () => {
    for (const produkt of produkte) {
      const liste = baueProduktInvestitionen(produkt.code)
      expect(liste).toEqual(investitionen.massnahmen.filter((m) => m.produkt === produkt.code))
    }
  })

  it('verteilt alle Maßnahmen auf Produkte und lässt andere Produkte leer', () => {
    const gesamt = produkte.reduce((n, p) => n + baueProduktInvestitionen(p.code).length, 0)
    expect(gesamt).toBe(investitionen.massnahmen.length)
    const ohne = produkte.find((p) => baueProduktInvestitionen(p.code).length === 0)
    expect(ohne).toBeDefined()
    expect(baueProduktInvestitionen('__proto__')).toEqual([])
  })

  it('baut die Tabelle mit Jahresspalten und Fehlwerten als null', () => {
    const mit = produkte.find((p) => baueProduktInvestitionen(p.code).length > 0)
    const liste = baueProduktInvestitionen(mit?.code ?? '')
    const tabelle = baueInvestitionenTabelle(liste)
    expect(tabelle.zeilen).toHaveLength(liste.length)
    expect(tabelle.spalten.map((s) => s.titel).slice(0, 3)).toEqual([
      'Maßnahme',
      'Konto',
      'Richtung',
    ])
    liste.forEach((massnahme, index) => {
      expect(tabelle.zeilen[index]?.name).toBe(massnahme.massnahme_name)
      expect(tabelle.zeilen[index]?.konto).toBe(massnahme.konto_name)
      investitionen.jahre.forEach((j, i) => {
        expect(tabelle.zeilen[index]?.[jahrSchluessel(j)]).toBe(massnahme.werte[i] ?? null)
      })
    })
    expect(baueInvestitionenTabelle([]).zeilen).toEqual([])
  })
})

describe('baueErlaeuterungen (AUSG-05)', () => {
  it('liefert für Produkte ohne Erläuterungen eine leere Liste', () => {
    const ohne = produkte.filter((p) => p.erlaeuterungen.length === 0)
    expect(ohne).toHaveLength(13)
    for (const produkt of ohne) {
      expect(baueErlaeuterungen(produkt.code)).toEqual([])
    }
    expect(baueErlaeuterungen('__proto__')).toEqual([])
  })

  it('löst zweistellige Zeilennummern zu gedruckten Zeilennamen auf', () => {
    const mit = produkte.find((p) =>
      p.erlaeuterungen.some((e) => e.zu_zeilen !== null && e.betrag !== null),
    )
    const liste = baueErlaeuterungen(mit?.code ?? '')
    expect(liste).toHaveLength(mit?.erlaeuterungen.length ?? -1)
    mit?.erlaeuterungen.forEach((erlaeuterung, index) => {
      const eintrag = liste[index]
      expect(eintrag?.betrag).toBe(erlaeuterung.betrag)
      expect(eintrag?.text).toBe(erlaeuterung.text)
      const erwartet = (erlaeuterung.zu_zeilen ?? []).map((nummer) => {
        const zeile = haushalt.zeilen_namen.ergebnisplan.find((z) => z.nummer === nummer)
        return zeile?.name
      })
      expect(eintrag?.zeilenNamen).toEqual(erwartet)
      expect(eintrag?.zeilenNamen.every((name) => name !== undefined)).toBe(true)
    })
  })

  it('nennt die Zeilen nur, wenn sie sich vom vorigen Posten unterscheiden', () => {
    for (const produkt of produkte) {
      const liste = baueErlaeuterungen(produkt.code)
      liste.forEach((eintrag, index) => {
        const davor = liste[index - 1]
        const gleich =
          davor !== undefined && davor.zeilenNamen.join('|') === eintrag.zeilenNamen.join('|')
        expect(eintrag.zuAnzeigen).toBe(eintrag.zeilenNamen.length > 0 && !gleich)
      })
    }
  })
})

describe('Probe AUSG-05: alle 63 Produkte', () => {
  it('baut jedes Seitenmodell ohne Fehler', () => {
    for (const produkt of produkte) {
      expect(() => {
        baueProduktKopf(produkt.code)
        baueTeilergebnisplan(produkt.code)
        baueErlaeuterungen(produkt.code)
        baueGrundzahlen(produkt.code)
        baueInvestitionenTabelle(baueProduktInvestitionen(produkt.code))
      }).not.toThrow()
    }
  })

  it('verwendet nur namenfreie Produktfelder (Datenschutz, Phase 3 D-09)', () => {
    for (const produkt of produkte) {
      for (const feld of Object.keys(produkt)) {
        expect(ERLAUBTE_PRODUKT_FELDER.has(feld)).toBe(true)
      }
    }
  })
})
