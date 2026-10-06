import { createApp, nextTick } from 'vue'
import { createMemoryHistory, createRouter } from 'vue-router'
import { describe, expect, it } from 'vitest'

import { farbeFuerPb } from '@/charts/echartsTheme'
import { haushalt, investitionen, produkte } from '@/data/daten'
import type { Massnahme } from '@/data/typen'
import {
  ARTEN,
  baueGruppen,
  baueMassnahmenTabelle,
  baueVorhaben,
  bereinigteMassnahmenQuery,
  buendeln,
  filterArt,
  GROESSTE_ANZAHL,
  klickIndex,
  leseMassnahmenFilter,
  MASSNAHMEN_AUFGABENBEREICHE,
  planjahre,
  useMassnahmenFilter,
  type Art,
} from '@/lib/investitionen'

// Alle Erwartungen stammen aus den App-Daten (Finanzplan-Zeilen, Planjahre), nicht aus
// getippten Beträgen; nur die für den Jahrgang festgehaltenen Zählungen stehen unter
// `describe.runIf` (RESEARCH Pattern 1, Pitfall 2).
const planAb = haushalt.jahre.indexOf(haushalt.haushaltsjahr)
const finanzplan = haushalt.finanzplan['GESAMT']?.zeilen ?? {}

const GFP_JE_ART: ReadonlyMap<Art, readonly string[]> = new Map<Art, readonly string[]>([
  ['bau', ['baumassnahmen']],
  ['grundstuecke', ['erwerb_grundstuecke_gebaeude']],
  ['ausstattung', ['erwerb_bewegliches_anlagevermoegen']],
  [
    'sonstige',
    ['erwerb_finanzanlagen', 'aktivierbare_zuwendungen', 'sonstige_investitionsauszahlungen'],
  ],
])

/** Summe einer GFP-Zeile im Planjahr mit dem Index `i` (0 = Haushaltsjahr). */
function gfp(schluessel: string, i: number): number {
  return finanzplan[schluessel]?.[planAb + i] ?? Number.NaN
}

function massnahme(teil: Partial<Massnahme>): Massnahme {
  return {
    produkt: '000000',
    pb: '01',
    massnahme_id: 'TEST1',
    massnahme_name: 'Testmaßnahme',
    konto: '780000',
    konto_name: 'Testkonto',
    richtung: 'auszahlung',
    art: 'bau',
    werte: [null, null],
    ve: null,
    pdf_seite: 1,
    ...teil,
  }
}

describe('filterArt (D-06)', () => {
  it.each([
    ['bau', 'bau'],
    ['grundstuecke', 'grundstuecke'],
    ['ausstattung', 'ausstattung'],
    ['finanzanlagen', 'sonstige'],
    ['investitionszuschuesse', 'sonstige'],
    ['immaterielles', 'sonstige'],
    [null, 'sonstige'],
    ['__proto__', 'sonstige'],
  ] as const)('ordnet %s der Filterart %s zu', (art, erwartet) => {
    expect(filterArt(art)).toBe(erwartet)
  })

  it('bietet genau die vier Filterarten mit deutschen Texten an', () => {
    expect(ARTEN.map((a) => a.art)).toEqual(['bau', 'grundstuecke', 'ausstattung', 'sonstige'])
    expect(ARTEN.map((a) => a.text)).toEqual([
      'Bau',
      'Grundstücke',
      'Fahrzeuge und Ausstattung',
      'Sonstige',
    ])
  })
})

describe('planjahre', () => {
  it('liefert die Jahre ab dem Haushaltsjahr bis zum letzten Jahr', () => {
    expect(planjahre()).toEqual(haushalt.jahre.slice(planAb))
    expect(planjahre()[0]).toBe(haushalt.haushaltsjahr)
  })

  it('stimmt mit den Jahren der Investitionsdaten überein', () => {
    expect(investitionen.jahre).toEqual(haushalt.jahre)
  })
})

describe('buendeln (Schlüssel produkt/massnahme_id)', () => {
  it('fasst die Konten einer Maßnahme zusammen und summiert je Planjahr', () => {
    const zeilen = [
      massnahme({ konto: '1', werte: [100, 200] }),
      massnahme({ konto: '2', werte: [10, 20], art: 'grundstuecke' }),
    ]
    const [eintrag, ...rest] = buendeln(zeilen, 0)
    expect(rest).toEqual([])
    expect(eintrag).toMatchObject({
      schluessel: '000000/TEST1',
      jahre: [110, 220],
      summe: 330,
      arten: ['bau', 'grundstuecke'],
    })
  })

  it('hält gleiche massnahme_id unter verschiedenen Produkten getrennt', () => {
    const zeilen = [
      massnahme({ produkt: '010101', werte: [5, 5] }),
      massnahme({ produkt: '020202', werte: [7, 7] }),
    ]
    const eintraege = buendeln(zeilen, 0)
    expect(eintraege.map((e) => e.produkt).sort()).toEqual(['010101', '020202'])
  })

  it('zählt nur die Planjahre ab dem Index', () => {
    const [eintrag] = buendeln([massnahme({ werte: [1000, 5, 6] })], 1)
    expect(eintrag?.jahre).toEqual([5, 6])
    expect(eintrag?.summe).toBe(11)
  })

  it('lässt ein Jahr nur dann leer, wenn alle Beiträge fehlen', () => {
    const zeilen = [
      massnahme({ konto: '1', werte: [null, 5] }),
      massnahme({ konto: '2', werte: [null, null] }),
    ]
    const [eintrag] = buendeln(zeilen, 0)
    expect(eintrag?.jahre).toEqual([null, 5])
    expect(eintrag?.summe).toBe(5)
  })

  it('sortiert absteigend nach der Summe, bei Gleichstand nach dem Namen', () => {
    const zeilen = [
      massnahme({ massnahme_id: 'B', massnahme_name: 'Zebra', werte: [10, 0] }),
      massnahme({ massnahme_id: 'A', massnahme_name: 'Ärmel', werte: [10, 0] }),
      massnahme({ massnahme_id: 'C', massnahme_name: 'Groß', werte: [99, 0] }),
    ]
    expect(buendeln(zeilen, 0).map((e) => e.massnahmeId)).toEqual(['C', 'A', 'B'])
  })
})

describe('baueVorhaben ohne Filter (INV-01, D-07, D-08)', () => {
  const alle = baueVorhaben({ pb: null, art: null })

  it('führt nur Maßnahmen mit Summe ungleich 0, absteigend sortiert', () => {
    expect(alle.length).toBeGreaterThan(0)
    expect(alle.every((e) => e.summe !== 0)).toBe(true)
    const summen = alle.map((e) => e.summe)
    expect(summen).toEqual([...summen].sort((a, b) => b - a))
  })

  it('verweist jede Maßnahme auf ein Produkt aus produkte.json und kennt dessen Farbe', () => {
    const codes = new Set(produkte.map((p) => p.code))
    for (const eintrag of alle) {
      expect(codes.has(eintrag.produkt)).toBe(true)
      expect(() => farbeFuerPb(eintrag.pb)).not.toThrow()
    }
  })

  it('hat eindeutige Schlüssel', () => {
    expect(new Set(alle.map((e) => e.schluessel)).size).toBe(alle.length)
  })

  it('summiert über alle Maßnahmen auf die GFP-Zeile auszahlungen_investitionen', () => {
    const jahre = planjahre()
    jahre.forEach((_jahr, i) => {
      const summe = alle.reduce((s, e) => s + (e.jahre[i] ?? 0), 0)
      expect(summe).toBe(gfp('auszahlungen_investitionen', i))
    })
    const gesamt = alle.reduce((s, e) => s + e.summe, 0)
    expect(gesamt).toBe(jahre.reduce((s, _j, i) => s + gfp('auszahlungen_investitionen', i), 0))
  })

  it.each(ARTEN.map((a) => a.art))('trifft je Planjahr die GFP-Zeilen der Art %s (D-06)', (art) => {
    const eintraege = baueVorhaben({ pb: null, art })
    const zeilen = GFP_JE_ART.get(art) ?? []
    expect(zeilen.length).toBeGreaterThan(0)
    planjahre().forEach((_jahr, i) => {
      const summe = eintraege.reduce((s, e) => s + (e.jahre[i] ?? 0), 0)
      const erwartet = zeilen.reduce((s, zeile) => s + gfp(zeile, i), 0)
      expect(summe).toBe(erwartet)
    })
  })

  it('übernimmt keinen Wert aus Einzahlungs-Zeilen (D-08)', () => {
    const einzahlungen = investitionen.massnahmen.filter((m) => m.richtung === 'einzahlung')
    const ausSumme = (m: Massnahme) =>
      m.werte.slice(planAb).reduce<number>((s, w) => s + (w ?? 0), 0)
    // Die Daten enthalten Einzahlungen im Planzeitraum, sonst wäre die Prüfung wertlos.
    expect(einzahlungen.some((m) => ausSumme(m) !== 0)).toBe(true)

    const nurEinzahlung = new Set(
      einzahlungen
        .filter(
          (e) =>
            !investitionen.massnahmen.some(
              (m) =>
                m.richtung === 'auszahlung' &&
                m.produkt === e.produkt &&
                m.massnahme_id === e.massnahme_id,
            ),
        )
        .map((e) => `${e.produkt}/${e.massnahme_id}`),
    )
    expect(alle.some((e) => nurEinzahlung.has(e.schluessel))).toBe(false)

    // Mit einer Einzahlung ändert sich keine Summe: das Bündeln ignoriert sie.
    const eins = massnahme({ werte: [100, 100] })
    const mitEinzahlung = [eins, massnahme({ richtung: 'einzahlung', konto: '9', werte: [60, 60] })]
    expect(buendeln(mitEinzahlung, 0)[0]?.summe).toBe(200)
  })

  it('filtert nach Aufgabenbereich und Art auf Kontoebene', () => {
    const pb = alle[0]?.pb ?? ''
    const nurPb = baueVorhaben({ pb, art: null })
    expect(nurPb.length).toBeGreaterThan(0)
    expect(nurPb.every((e) => e.pb === pb)).toBe(true)

    const nurBau = baueVorhaben({ pb: null, art: 'bau' })
    expect(nurBau.every((e) => e.arten.length === 1 && e.arten[0] === 'bau')).toBe(true)
  })

  it('liefert für den Filter einen kleineren oder gleich großen Teil der Summe', () => {
    const gesamt = alle.reduce((s, e) => s + e.summe, 0)
    const teile = ARTEN.map((a) =>
      baueVorhaben({ pb: null, art: a.art }).reduce((s, e) => s + e.summe, 0),
    )
    expect(teile.reduce((s, t) => s + t, 0)).toBe(gesamt)
  })

  it('zeigt im Diagramm höchstens 15 Maßnahmen', () => {
    expect(GROESSTE_ANZAHL).toBe(15)
  })
})

describe('baueMassnahmenTabelle', () => {
  const alle = baueVorhaben({ pb: null, art: null })
  const tabelle = baueMassnahmenTabelle(alle)

  it('hat Maßnahme, Aufgabenbereich, Art, je Planjahr eine Spalte mit Wertart und die Summe', () => {
    const titel = tabelle.spalten.map((s) => s.titel)
    expect(titel.slice(0, 3)).toEqual(['Maßnahme', 'Aufgabenbereich', 'Art'])
    expect(titel).toContain('Summe')
    const jahresTitel = titel.slice(3, 3 + planjahre().length)
    jahresTitel.forEach((text, i) => {
      expect(text.startsWith(String(planjahre()[i]))).toBe(true)
      expect(text).toMatch(/Ist|Ansatz|Planung/)
    })
  })

  it('zeigt alle Maßnahmen, nicht nur die größten', () => {
    expect(tabelle.zeilen).toHaveLength(alle.length)
    expect(tabelle.zeilen.every((z) => typeof z['produkt'] === 'string')).toBe(true)
  })

  it('lässt fehlende Jahreswerte leer (null) statt 0', () => {
    const [eintrag] = buendeln([massnahme({ werte: [null, 5] })], 0)
    expect(eintrag).toBeDefined()
    const zeilen = baueMassnahmenTabelle(eintrag === undefined ? [] : [eintrag]).zeilen
    const jahresSchluessel = tabelle.spalten[3]?.schluessel ?? ''
    expect(zeilen[0]?.[jahresSchluessel]).toBeNull()
  })
})

describe('klickIndex', () => {
  it('liest den dataIndex und lehnt Unpassendes ab', () => {
    expect(klickIndex({ dataIndex: 2 }, 5)).toBe(2)
    expect(klickIndex({ dataIndex: 5 }, 5)).toBeNull()
    expect(klickIndex({ dataIndex: -1 }, 5)).toBeNull()
    expect(klickIndex({ dataIndex: '1' }, 5)).toBeNull()
    expect(klickIndex(null, 5)).toBeNull()
    expect(klickIndex({}, 5)).toBeNull()
  })
})

describe.runIf(haushalt.haushaltsjahr === 2026)(
  'Jahrgang 2026 (RESEARCH Pattern 1, Pitfall 2)',
  () => {
    it('bündelt 89 Auszahlungs-Gruppen, davon 59 mit Summe ungleich 0', () => {
      expect(baueGruppen({ pb: null, art: null })).toHaveLength(89)
      expect(baueVorhaben({ pb: null, art: null })).toHaveLength(59)
    })

    it('summiert die Planjahre auf 36.361.784 €', () => {
      const gesamt = baueVorhaben({ pb: null, art: null }).reduce((s, e) => s + e.summe, 0)
      expect(gesamt).toBe(36361784)
    })

    it('trennt KLIMA1 in mehrere Maßnahmen je Produkt', () => {
      const klima = baueVorhaben({ pb: null, art: null }).filter((e) => e.massnahmeId === 'KLIMA1')
      expect(klima.length).toBeGreaterThan(1)
      expect(new Set(klima.map((e) => e.produkt)).size).toBe(klima.length)
    })
  },
)

describe('MASSNAHMEN_AUFGABENBEREICHE (D-06, Pitfall 8)', () => {
  const codes = MASSNAHMEN_AUFGABENBEREICHE.map((b) => b.code)
  const pbMitMassnahmen = new Set(baueVorhaben({ pb: null, art: null }).map((e) => e.pb))

  it('nennt genau die Aufgabenbereiche mit Auszahlungs-Maßnahmen', () => {
    expect(codes.length).toBeGreaterThan(0)
    expect(new Set(codes)).toEqual(pbMitMassnahmen)
  })

  it('führt nur echte Aufgabenbereiche, nie KL oder synthetische Knoten', () => {
    for (const bereich of MASSNAHMEN_AUFGABENBEREICHE) {
      const knoten = haushalt.knoten.find((k) => k.code === bereich.code)
      expect(knoten).toMatchObject({ ebene: 'PB', eltern: 'GESAMT', synthetisch: false })
      expect(bereich.name).toBe(knoten?.name)
    }
    expect(codes).not.toContain('KL')
  })

  it('folgt der Reihenfolge der Knoten', () => {
    const reihenfolge = haushalt.knoten.map((k) => k.code)
    const positionen = codes.map((c) => reihenfolge.indexOf(c))
    expect(positionen).toEqual([...positionen].sort((a, b) => a - b))
  })

  describe.runIf(haushalt.haushaltsjahr === 2026)('Jahrgang 2026', () => {
    it('hat elf Aufgabenbereiche', () => {
      expect(codes).toEqual(['01', '02', '03', '04', '06', '08', '09', '10', '12', '13', '15'])
    })
  })
})

describe('leseMassnahmenFilter (D-06, T-06-14)', () => {
  const pb = MASSNAHMEN_AUFGABENBEREICHE[0]?.code ?? ''

  it('liefert ohne Query „Alle“ ohne Bereinigung', () => {
    expect(leseMassnahmenFilter({})).toEqual({ pb: null, art: null, bereinigt: false })
  })

  it('behält gültige Werte', () => {
    expect(pb).not.toBe('')
    expect(leseMassnahmenFilter({ art: 'bau', pb })).toEqual({ pb, art: 'bau', bereinigt: false })
  })

  it.each(['bau', 'grundstuecke', 'ausstattung', 'sonstige'] as const)(
    'akzeptiert die Art %s',
    (art) => {
      expect(leseMassnahmenFilter({ art })).toMatchObject({ art, bereinigt: false })
    },
  )

  it('verwirft eine unbekannte Art und meldet Bereinigung', () => {
    expect(leseMassnahmenFilter({ art: 'xyz' })).toEqual({ pb: null, art: null, bereinigt: true })
  })

  it.each(['__proto__', 'constructor', 'toString', 'KL', '16', '', 'xyz'])(
    'verwirft den Aufgabenbereich „%s“',
    (wert) => {
      expect(leseMassnahmenFilter({ pb: wert })).toEqual({ pb: null, art: null, bereinigt: true })
    },
  )

  it('verwirft Prototyp-Schlüssel auch bei der Art', () => {
    expect(leseMassnahmenFilter({ art: '__proto__' })).toMatchObject({ art: null, bereinigt: true })
    expect(leseMassnahmenFilter({ art: 'hasOwnProperty' })).toMatchObject({
      art: null,
      bereinigt: true,
    })
  })

  it('nimmt bei Arrays nur das erste Element', () => {
    expect(leseMassnahmenFilter({ art: ['grundstuecke', 'bau'] })).toMatchObject({
      art: 'grundstuecke',
      bereinigt: false,
    })
    expect(leseMassnahmenFilter({ art: ['xyz', 'bau'] })).toMatchObject({
      art: null,
      bereinigt: true,
    })
  })

  it('behandelt einen leeren Wert (?art ohne Wert) als ungültig', () => {
    expect(leseMassnahmenFilter({ art: null, pb: null })).toEqual({
      pb: null,
      art: null,
      bereinigt: true,
    })
  })

  it('ignoriert das globale jahr und andere fremde Schlüssel', () => {
    expect(leseMassnahmenFilter({ jahr: '1999', foo: 'bar' })).toEqual({
      pb: null,
      art: null,
      bereinigt: false,
    })
  })
})

describe('bereinigteMassnahmenQuery', () => {
  const pb = MASSNAHMEN_AUFGABENBEREICHE[0]?.code ?? ''

  it('behält fremde Schlüssel und gültige Filter und entfernt nur ungültige', () => {
    const query = { jahr: '2025', art: 'xyz', pb }
    expect(bereinigteMassnahmenQuery(query, leseMassnahmenFilter(query))).toEqual({
      jahr: '2025',
      pb,
    })
  })

  it('entfernt beide ungültigen Filter', () => {
    const query = { pb: '__proto__', art: 'xyz', jahr: '2025' }
    expect(bereinigteMassnahmenQuery(query, leseMassnahmenFilter(query))).toEqual({
      jahr: '2025',
    })
  })

  it('schreibt ein Array auf den ersten gültigen Wert zurück', () => {
    const query = { art: ['bau', 'grundstuecke'] }
    expect(bereinigteMassnahmenQuery(query, leseMassnahmenFilter(query))).toEqual({ art: 'bau' })
  })
})

describe('useMassnahmenFilter (D-06, Router-Zustand)', () => {
  const pb = MASSNAHMEN_AUFGABENBEREICHE[0]?.code ?? ''

  const abwarten = () => new Promise((fertig) => setTimeout(fertig, 0))

  async function aufbau(ziel: string) {
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/investitionen', name: 'investitionen', component: { render: () => null } },
        { path: '/anders', name: 'anders', component: { render: () => null } },
      ],
    })
    const app = createApp({ render: () => null })
    app.use(router)
    await router.push(ziel)
    const zustand = app.runWithContext(() => useMassnahmenFilter())
    await nextTick()
    await abwarten()
    return { router, zustand }
  }

  it('entfernt ungültige Werte per replace und behält fremde Schlüssel und den Hash', async () => {
    const { router } = await aufbau('/investitionen?art=xyz&jahr=2025#anker')
    expect(router.currentRoute.value.query).toEqual({ jahr: '2025' })
    expect(router.currentRoute.value.hash).toBe('#anker')
  })

  it('setzt Aufgabenbereich und Art per replace, ohne neuen Verlaufseintrag', async () => {
    const { router, zustand } = await aufbau('/investitionen?jahr=2025')
    const vorher = router.options.history.state.position
    zustand.setzePb(pb)
    await abwarten()
    zustand.setzeArt('bau')
    await abwarten()
    expect(router.currentRoute.value.query).toEqual({ jahr: '2025', pb, art: 'bau' })
    expect(zustand.filter.value).toEqual({ pb, art: 'bau', bereinigt: false })
    expect(router.options.history.state.position).toBe(vorher)
  })

  it('ignoriert ungültige Werte beim Setzen', async () => {
    const { router, zustand } = await aufbau('/investitionen')
    zustand.setzePb('__proto__')
    zustand.setzePb('KL')
    zustand.setzeArt('xyz' as never)
    await abwarten()
    expect(router.currentRoute.value.query).toEqual({})
  })

  it('setzt „Alle“ und mit zuruecksetzen beide Filter zurück', async () => {
    const { router, zustand } = await aufbau(`/investitionen?pb=${pb}&art=bau&jahr=2025`)
    zustand.setzeArt(null)
    await abwarten()
    expect(router.currentRoute.value.query).toEqual({ pb, jahr: '2025' })
    zustand.zuruecksetzen()
    await abwarten()
    expect(router.currentRoute.value.query).toEqual({ jahr: '2025' })
  })

  it('liefert die Maßnahmen der Auswahl', async () => {
    const { zustand } = await aufbau(`/investitionen?pb=${pb}&art=bau`)
    expect(zustand.vorhaben.value).toEqual(baueVorhaben({ pb, art: 'bau' }))
  })
})
