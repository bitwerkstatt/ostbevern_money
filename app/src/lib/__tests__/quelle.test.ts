import { afterEach, describe, expect, it, vi } from 'vitest'

import quelleKnopfQuelltext from '@/components/QuelleKnopf.vue?raw'
import quelleSeiteQuelltext from '@/components/QuelleSeite.vue?raw'
import quelleSeitenleisteQuelltext from '@/components/QuelleSeitenleiste.vue?raw'
import { haushalt, quellen } from '@/data/daten'
import { baueKennzahlen } from '@/lib/kennzahlen'
import { bboxProzent, belegSchluessel, bildUrl, findeBeleg } from '@/lib/quelle'

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

  it('die Seitenleiste nennt den Originallink nur über ORIGINAL_PDF_URL', () => {
    expect(quelleSeitenleisteQuelltext).not.toMatch(/https?:\/\//)
    expect(quelleSeitenleisteQuelltext).toContain('ORIGINAL_PDF_URL')
  })
})
