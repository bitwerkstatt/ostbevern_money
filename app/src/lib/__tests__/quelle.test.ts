import { afterEach, describe, expect, it, vi } from 'vitest'
import { createSSRApp } from 'vue'
import { renderToString } from 'vue/server-renderer'

import DatenTabelle from '@/components/DatenTabelle.vue'
import QuelleKnopf from '@/components/QuelleKnopf.vue'
import quelleKnopfQuelltext from '@/components/QuelleKnopf.vue?raw'
import quelleSeiteQuelltext from '@/components/QuelleSeite.vue?raw'
import quelleSeitenleisteQuelltext from '@/components/QuelleSeitenleiste.vue?raw'
import { sichtbareSpalten, type DatenSpalte } from '@/components/datenTabelle'
import { ORIGINAL_PDF_URL } from '@/config'
import { haushalt, quellen } from '@/data/daten'
import { baueKennzahlen } from '@/lib/kennzahlen'
import {
  bboxProzent,
  belegHinweis,
  belegSchluessel,
  bildUrl,
  findeBeleg,
  originalSeitenUrl,
  quellAltText,
} from '@/lib/quelle'

describe('belegSchluessel (Grammatik wie pipeline/ostbevern/quellen.py)', () => {
  it('baut jeden Schlüssel nach der Grammatik', () => {
    expect(belegSchluessel.ep('GESAMT', 'steuern')).toBe('ep:GESAMT:steuern')
    expect(belegSchluessel.fp('GESAMT', 'kreditaufnahme')).toBe('fp:GESAMT:kreditaufnahme')
    expect(belegSchluessel.vb('steuerarten', 'grundsteuer_a')).toBe('vb:steuerarten:grundsteuer_a')
    expect(belegSchluessel.vbGesamt('steuerarten')).toBe('vb:steuerarten:gesamt')
    expect(belegSchluessel.meta('hebesaetze.gewerbesteuer')).toBe('meta:hebesaetze.gewerbesteuer')
    expect(belegSchluessel.gz('020701', 3)).toBe('gz:020701:3')
    expect(belegSchluessel.pr('020701')).toBe('pr:020701')
    expect(belegSchluessel.inv('020701', 'M1', '785100', 'auszahlung')).toBe(
      'inv:020701:M1:785100:auszahlung',
    )
    expect(belegSchluessel.ve('020701', 'M1', '785100')).toBe('ve:020701:M1:785100')
    expect(belegSchluessel.sd('nrw_bank')).toBe('sd:nrw_bank')
    expect(belegSchluessel.seite(62)).toBe('seite:62')
  })

  it('schreibt einen fehlenden Produktbereich im Stellenplan als Strich', () => {
    expect(belegSchluessel.sp('tarif', 3, null)).toBe('sp:tarif:3:-')
    expect(belegSchluessel.sp('stellenuebersicht', 7, '04')).toBe('sp:stellenuebersicht:7:04')
  })
})

describe('findeBeleg', () => {
  it('löst alle sieben Schlüssel der Start-Kacheln auf', () => {
    for (const kennzahl of baueKennzahlen()) {
      const beleg = findeBeleg(kennzahl.quelle)
      expect(beleg, `${kennzahl.schluessel}: ${kennzahl.quelle}`).not.toBeNull()
    }
  })

  it('liefert für Ergebnis, Investitionen und Kredite ein Rechteck', () => {
    for (const schluessel of ['ergebnis', 'investitionen', 'kredite']) {
      const kennzahl = baueKennzahlen().find((k) => k.schluessel === schluessel)
      const beleg = findeBeleg(kennzahl?.quelle ?? '')
      expect(beleg?.bbox, schluessel).not.toBeNull()
      expect(beleg?.bbox).toHaveLength(4)
    }
  })

  it('löst jede Zeile des Gesamtergebnis- und Gesamtfinanzplans auf', () => {
    const gesamt = haushalt.ergebnisplan.GESAMT
    const finanzplan = haushalt.finanzplan.GESAMT
    expect(gesamt).toBeDefined()
    expect(finanzplan).toBeDefined()
    for (const zeile of Object.keys(gesamt?.zeilen ?? {})) {
      expect(findeBeleg(belegSchluessel.ep('GESAMT', zeile)), `ep ${zeile}`).not.toBeNull()
    }
    for (const zeile of Object.keys(finanzplan?.zeilen ?? {})) {
      expect(findeBeleg(belegSchluessel.fp('GESAMT', zeile)), `fp ${zeile}`).not.toBeNull()
    }
  })

  it('liefert Seitenmaß und Bildname der Seite', () => {
    const beleg = findeBeleg(belegSchluessel.ep('GESAMT', 'ordentliche_ertraege'))
    expect(beleg).not.toBeNull()
    const seite = quellen.seiten[String(beleg?.pdfSeite)]
    expect(seite).toBeDefined()
    expect(beleg?.breite).toBe(seite?.breite)
    expect(beleg?.hoehe).toBe(seite?.hoehe)
    expect(beleg?.bild).toBe(seite?.bild)
  })

  it('findet über Prototyp-Namen und unbekannte Schlüssel nichts', () => {
    expect(findeBeleg('__proto__')).toBeNull()
    expect(findeBeleg('constructor')).toBeNull()
    expect(findeBeleg('toString')).toBeNull()
    expect(findeBeleg('ep:GESAMT:gibt_es_nicht')).toBeNull()
    expect(findeBeleg('')).toBeNull()
  })
})

describe('bboxProzent', () => {
  it('rechnet ein Hochformat-Rechteck in Prozent der Seite um', () => {
    expect(bboxProzent([59.53, 84.19, 535.75, 92.61], 595.28, 841.89)).toEqual({
      links: 10,
      oben: 10,
      breite: 80,
      hoehe: 1,
    })
  })

  it('rechnet ein Querformat-Rechteck mit vertauschtem Seitenmaß um', () => {
    const querformat = bboxProzent([84.19, 59.53, 420.945, 118.0], 841.89, 595.28)
    expect(querformat).toEqual({ links: 10, oben: 10, breite: 40, hoehe: 9.8 })
    // Mit dem Hochformat-Maß wäre dieselbe Box eine andere (falsche) Stelle.
    expect(bboxProzent([84.19, 59.53, 420.945, 118.0], 595.28, 841.89)).not.toEqual(querformat)
  })

  it('rundet auf eine Nachkommastelle', () => {
    const p = bboxProzent([1, 1, 2, 2], 3, 7)
    expect(p.links).toBe(33.3)
    expect(p.oben).toBe(14.3)
  })
})

describe('bildUrl', () => {
  afterEach(() => {
    vi.unstubAllEnvs()
  })

  it('führt in den Ordner quellen unterhalb der App-Basis', () => {
    const url = bildUrl('s062.webp')
    expect(url).toBe(`${import.meta.env.BASE_URL}quellen/s062.webp`)
    expect(url.endsWith('quellen/s062.webp')).toBe(true)
  })

  it('beginnt mit der relativen Basis des Builds nie mit einem Schrägstrich', () => {
    // Vitest löst `base: './'` zu '/' auf; der Produktions-Build setzt './' (vite.config.ts).
    vi.stubEnv('BASE_URL', './')
    const url = bildUrl('s062.webp')
    expect(url.startsWith('/')).toBe(false)
    expect(url).toBe('./quellen/s062.webp')
  })
})

describe('keine Drittanbieter- oder Absolutpfade in den Beleg-Komponenten (D-05)', () => {
  it.each([
    ['QuelleKnopf', quelleKnopfQuelltext],
    ['QuelleSeite', quelleSeiteQuelltext],
  ])('%s lädt nichts von einem fremden Host', (_name, quelltext) => {
    expect(quelltext).not.toMatch(/https?:\/\//)
    expect(quelltext).not.toMatch(/src="\//)
  })

  it('die Seitenleiste nennt den Originallink nur über originalSeitenUrl', () => {
    expect(quelleSeitenleisteQuelltext).not.toMatch(/https?:\/\//)
    expect(quelleSeitenleisteQuelltext).toContain('originalSeitenUrl(')
  })
})

const HINWEIS_OHNE_MARKIERUNG =
  'Zeile nicht automatisch markiert. Der Wert steht auf dieser Seite, vielleicht in anderer Schreibweise, zum Beispiel gerundet in Tausend Euro.'

describe('belegHinweis (D-03)', () => {
  it('nennt bei vorhandenem Rechteck nur den Markierungshinweis', () => {
    expect(belegHinweis({ bbox: [1, 2, 3, 4] }, null)).toEqual({
      art: 'markiert',
      text: 'Die markierte Zeile ist umrandet.',
    })
  })

  it('erklärt bei fehlendem Rechteck, dass die Zeile nicht markiert ist', () => {
    expect(belegHinweis({ bbox: null }, null)).toEqual({
      art: 'ohne_markierung',
      text: HINWEIS_OHNE_MARKIERUNG,
    })
  })

  it('nennt bei berechneten Werten die Herleitung, mit und ohne Rechteck', () => {
    const erwartet = {
      art: 'berechnet',
      titel: 'Berechneter Wert',
      text: 'Dieser Wert steht nicht im PDF. Er wird berechnet: Steuern geteilt durch die Einwohnerzahl. Die Seite zeigt die Ausgangswerte.',
    }
    expect(belegHinweis({ bbox: [1, 2, 3, 4] }, 'Steuern geteilt durch die Einwohnerzahl')).toEqual(
      erwartet,
    )
    expect(belegHinweis({ bbox: null }, 'Steuern geteilt durch die Einwohnerzahl')).toEqual(
      erwartet,
    )
  })

  it('setzt ohne Herleitungstext „aus den Planwerten“ ein', () => {
    expect(belegHinweis({ bbox: [1, 2, 3, 4] }, '')).toEqual({
      art: 'berechnet',
      titel: 'Berechneter Wert',
      text: 'Dieser Wert steht nicht im PDF. Er wird berechnet: aus den Planwerten. Die Seite zeigt die Ausgangswerte.',
    })
  })
})

describe('originalSeitenUrl (D-06)', () => {
  it('hängt die 1-basierte Seite als #page an die Original-URL', () => {
    expect(originalSeitenUrl(62)).toBe(`${ORIGINAL_PDF_URL}#page=62`)
    expect(originalSeitenUrl(1)).toBe(`${ORIGINAL_PDF_URL}#page=1`)
  })

  it.each([0, -1, 1.5, Number.NaN, Number.POSITIVE_INFINITY])('lehnt %s ab', (seite) => {
    expect(() => originalSeitenUrl(seite)).toThrow()
  })
})

describe('quellAltText', () => {
  it('beschreibt die Seite und nennt mit Markierung die markierte Zeile', () => {
    expect(quellAltText(62, 'Erträge', true)).toBe(
      'Ausschnitt des Haushaltsplans, PDF-Seite 62. Die markierte Zeile gehört zu: Erträge.',
    )
  })

  it('beschreibt ohne Markierung nur die Seite', () => {
    expect(quellAltText(62, 'Erträge', false)).toBe('Ausschnitt des Haushaltsplans, PDF-Seite 62.')
  })
})

describe('sichtbareSpalten (Spalte „Quelle“ der DatenTabelle)', () => {
  const spalten: DatenSpalte[] = [
    { schluessel: 'name', titel: 'Name', art: 'text' },
    { schluessel: 'betrag', titel: 'Betrag', art: 'euro' },
    { schluessel: 'beleg', titel: 'Quelle', art: 'quelle' },
  ]
  const hatBeleg = (wert: string | number | null): boolean =>
    typeof wert === 'string' && findeBeleg(wert) !== null
  const gueltig = belegSchluessel.ep('GESAMT', 'steuern')

  it('behält die Quelle-Spalte, wenn mindestens eine Zeile einen Beleg hat', () => {
    const zeilen = [
      { name: 'a', betrag: 1, beleg: null },
      { name: 'b', betrag: 2, beleg: gueltig },
    ]
    expect(sichtbareSpalten(spalten, zeilen, hatBeleg)).toEqual(spalten)
  })

  it('lässt die Quelle-Spalte weg, wenn keine Zeile einen Beleg hat', () => {
    const zeilen = [
      { name: 'a', betrag: 1, beleg: null },
      { name: 'b', betrag: 2, beleg: 'ep:GESAMT:gibt_es_nicht' },
    ]
    expect(sichtbareSpalten(spalten, zeilen, hatBeleg).map((s) => s.schluessel)).toEqual([
      'name',
      'betrag',
    ])
  })

  it('lässt die Quelle-Spalte bei einer Tabelle ohne Zeilen weg und ändert andere Spalten nie', () => {
    expect(sichtbareSpalten(spalten, [], hatBeleg).map((s) => s.schluessel)).toEqual([
      'name',
      'betrag',
    ])
    const ohneQuelle = spalten.slice(0, 2)
    expect(sichtbareSpalten(ohneQuelle, [{ name: 'a', betrag: 1 }], hatBeleg)).toEqual(ohneQuelle)
  })
})

describe('QuelleKnopf und DatenTabelle-Spalte „Quelle“ (Server-Rendering ohne DOM)', () => {
  const gueltig = belegSchluessel.ep('GESAMT', 'steuern')
  const spalten: DatenSpalte[] = [
    { schluessel: 'name', titel: 'Name', art: 'text' },
    { schluessel: 'beleg', titel: 'Quelle', art: 'quelle' },
  ]

  async function rendere(komponente: object, props: Record<string, unknown>): Promise<string> {
    return renderToString(createSSRApp(komponente, props))
  }

  it('QuelleKnopf rendert für einen unbekannten Schlüssel nichts (kein toter Knopf)', async () => {
    const html = await rendere(QuelleKnopf, {
      schluessel: 'ep:GESAMT:gibt_es_nicht',
      bezeichnung: 'Erträge',
      variante: 'kachel',
    })
    expect(html).not.toContain('<button')
    expect(html).not.toContain('Quelle anzeigen')
    expect(html).not.toContain('>Quelle<')
  })

  it('QuelleKnopf zeigt in der Variante kachel den Text „Quelle“ und trägt den vollen Namen', async () => {
    const html = await rendere(QuelleKnopf, {
      schluessel: gueltig,
      bezeichnung: 'Erträge',
      variante: 'kachel',
    })
    expect(html).toContain('aria-label="Quelle anzeigen: Erträge, PDF-Seite 62"')
    expect(html).toContain('>Quelle<')
    expect(html).toContain('name="file-lines"')
  })

  it('QuelleKnopf zeigt in der Variante produkt den Text „Quelle“ und trägt den vollen Namen', async () => {
    const html = await rendere(QuelleKnopf, {
      schluessel: gueltig,
      bezeichnung: 'Erträge',
      variante: 'produkt',
    })
    expect(html).toContain('aria-label="Quelle anzeigen: Erträge, PDF-Seite 62"')
    expect(html).toContain('>Quelle<')
    expect(html).toContain('name="file-lines"')
  })

  it('QuelleKnopf zeigt in der Variante zeile „PDF-Seite {n}“ ohne Icon', async () => {
    const html = await rendere(QuelleKnopf, {
      schluessel: gueltig,
      bezeichnung: 'Steuern',
      variante: 'zeile',
    })
    expect(html).toContain('aria-label="Quelle anzeigen: Steuern, PDF-Seite 62"')
    expect(html).toMatch(/>PDF-Seite 62</)
    expect(html).not.toContain('file-lines')
  })

  it('DatenTabelle zeichnet je belegter Zeile einen Knopf und lässt andere Zellen leer', async () => {
    const html = await rendere(DatenTabelle, {
      beschriftung: 'Probe',
      spalten,
      zeilen: [
        { name: 'Steuern', beleg: gueltig },
        { name: 'Ohne Beleg', beleg: null },
        { name: 'Unbekannt', beleg: 'ep:GESAMT:gibt_es_nicht' },
      ],
    })
    expect(html.match(/<button/g)).toHaveLength(1)
    expect(html).toContain('aria-label="Quelle anzeigen: Steuern, PDF-Seite 62"')
    expect(html).toMatch(/<th scope="col"[^>]*>Quelle<\/th>/)
    expect(html).not.toContain('kein Wert')
    // Die beiden Zeilen ohne auflösbaren Beleg haben eine leere Zelle (ohne Strich, ohne Text).
    expect(html.match(/<td class="om-tabelle__quelle"[^>]*><!----><\/td>/g)).toHaveLength(2)
  })

  it('DatenTabelle zeigt ohne auflösbaren Beleg keine Quelle-Spalte', async () => {
    const html = await rendere(DatenTabelle, {
      beschriftung: 'Probe',
      spalten,
      zeilen: [
        { name: 'Ohne Beleg', beleg: null },
        { name: 'Unbekannt', beleg: 'ep:GESAMT:gibt_es_nicht' },
      ],
    })
    expect(html).not.toContain('Quelle')
    expect(html).not.toContain('<button')
    expect(html).not.toContain('om-tabelle__quelle')
  })
})
