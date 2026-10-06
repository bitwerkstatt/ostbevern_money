// Vertragstest zwischen `quellen.json` (Schritt 08, Python) und den TypeScript-Schlüsselbauern
// (`belegSchluessel`, `findeBeleg`) in `lib/quelle.ts` (Phase 7, DATA-04, UI-SPEC E1 „error“):
//   1. Jeder Datensatz mit Seitenfeld der App-JSONs hat einen auflösbaren Beleg.
//   2. Jeder Schlüssel in `quellen.json` folgt der Grammatik und zeigt auf einen Datensatz.
//   3. Bild und Seite jedes Belegs stimmen mit der `seiten`-Karte überein.
// Die Fehlermeldungen listen die fehlenden bzw. fehlerhaften Schlüssel.

import { describe, expect, it } from 'vitest'

import { haushalt, investitionen, produkte, quellen, stellenplan, texte } from '@/data/daten'
import type { MetaWert, VorberichtTabelle } from '@/data/typen'
import { belegSchluessel, findeBeleg } from '@/lib/quelle'

/** Seitenfelder der App-JSONs: eine Seitenzahl oder eine Liste von Seitenzahlen. */
const SEITENFELD = ['pdf_seite', 'quelle']
const SEITENLISTENFELD = ['pdf_seiten', 'quelle_seiten']

function sammleSeiten(daten: unknown, ziel: Set<number>): void {
  if (Array.isArray(daten)) {
    for (const eintrag of daten) {
      sammleSeiten(eintrag, ziel)
    }
    return
  }
  if (typeof daten !== 'object' || daten === null) {
    return
  }
  for (const [name, wert] of Object.entries(daten)) {
    if (SEITENFELD.includes(name) && typeof wert === 'number') {
      ziel.add(wert)
    } else if (SEITENLISTENFELD.includes(name) && Array.isArray(wert)) {
      for (const seite of wert) {
        if (typeof seite === 'number') {
          ziel.add(seite)
        }
      }
    } else {
      sammleSeiten(wert, ziel)
    }
  }
}

const SEITEN_DER_DATEN = new Set<number>()
for (const daten of [haushalt, produkte, investitionen, stellenplan, texte]) {
  sammleSeiten(daten, SEITEN_DER_DATEN)
}

const META_GRUPPEN = ['hebesaetze', 'kreisumlage', 'satzung', 'vorbericht_werte'] as const
const SCHULDENSTAND_REIHEN = ['investitionskredite', 'nrw_bank', 'liquiditaetskredite'] as const

const VORBERICHT_TABELLEN: [string, VorberichtTabelle][] = [
  ...Object.entries(haushalt.vorbericht),
  ['eigenkapital', haushalt.eigenkapital],
]

function metaEintrag(pfad: string): MetaWert | undefined {
  const [kopf, unter, rest] = pfad.split('.')
  if (kopf === undefined || rest !== undefined) {
    return undefined
  }
  if (unter === undefined) {
    return kopf === 'einwohner'
      ? haushalt.meta.einwohner
      : kopf === 'flaeche'
        ? haushalt.meta.flaeche
        : undefined
  }
  const gruppe = META_GRUPPEN.find((name) => name === kopf)
  return gruppe === undefined ? undefined : haushalt.meta[gruppe][unter]
}

function alleMetaPfade(): string[] {
  const pfade = ['einwohner', 'flaeche']
  for (const gruppe of META_GRUPPEN) {
    for (const name of Object.keys(haushalt.meta[gruppe])) {
      pfade.push(`${gruppe}.${name}`)
    }
  }
  return pfade
}

/** Schlüssel jedes Datensatzes mit Seitenfeld, den die App mit „Quelle anzeigen“ belegen kann. */
function erwarteteSchluessel(): string[] {
  const schluessel: string[] = []

  for (const [tabelle, daten] of VORBERICHT_TABELLEN) {
    for (const posten of daten.posten) {
      if (posten.quelle !== null) {
        schluessel.push(belegSchluessel.vb(tabelle, posten.posten))
      }
    }
    if (daten.gesamt_vorbericht.quelle !== null) {
      schluessel.push(belegSchluessel.vbGesamt(tabelle))
    }
  }

  for (const pfad of alleMetaPfade()) {
    schluessel.push(belegSchluessel.meta(pfad))
  }

  for (const produkt of produkte) {
    schluessel.push(belegSchluessel.pr(produkt.code))
    for (const grundzahl of produkt.grundzahlen) {
      schluessel.push(belegSchluessel.gz(produkt.code, grundzahl.position))
    }
  }

  for (const massnahme of investitionen.massnahmen) {
    schluessel.push(
      belegSchluessel.inv(
        massnahme.produkt,
        massnahme.massnahme_id,
        massnahme.konto,
        massnahme.richtung,
      ),
    )
  }
  for (const ve of investitionen.ve_faelligkeiten) {
    schluessel.push(belegSchluessel.ve(ve.produkt, ve.massnahme_id, ve.konto))
  }
  for (const reihe of SCHULDENSTAND_REIHEN) {
    schluessel.push(belegSchluessel.sd(reihe))
  }

  for (const zeile of stellenplan.zeilen) {
    schluessel.push(belegSchluessel.sp(zeile.teil, zeile.position, zeile.produktbereich))
  }

  for (const seite of SEITEN_DER_DATEN) {
    schluessel.push(belegSchluessel.seite(seite))
  }

  // Gesamtpläne: jede gedruckte GESAMT-Zeile, die die App als Datensatz kennt.
  for (const zeile of Object.keys(haushalt.ergebnisplan['GESAMT']?.zeilen ?? {})) {
    schluessel.push(belegSchluessel.ep('GESAMT', zeile))
  }
  for (const zeile of Object.keys(haushalt.finanzplan['GESAMT']?.zeilen ?? {})) {
    schluessel.push(belegSchluessel.fp('GESAMT', zeile))
  }
  return schluessel
}

/** Prüft einen Schlüssel gegen Grammatik und Datensätze; liefert den Fehlergrund oder `null`. */
function pruefeSchluessel(schluessel: string): string | null {
  const teile = schluessel.split(':')
  const art = teile[0]
  const gruppe = (muster: RegExp): RegExpExecArray | null => muster.exec(schluessel)

  switch (art) {
    case 'ep': {
      const treffer = gruppe(/^ep:([A-Za-z0-9.]+):([a-z0-9_]+)$/)
      const code = treffer?.[1]
      const zeile = treffer?.[2]
      if (code === undefined || zeile === undefined) return 'Grammatik ep:{code}:{zeile}'
      if (code.startsWith('KL')) return 'KL-Knoten haben keinen Beleg'
      return haushalt.ergebnisplan[code]?.zeilen[zeile] === undefined ? 'kein Datensatz' : null
    }
    case 'fp': {
      const treffer = gruppe(/^fp:([A-Za-z0-9.]+):([a-z0-9_]+)$/)
      const code = treffer?.[1]
      const zeile = treffer?.[2]
      if (code === undefined || zeile === undefined) return 'Grammatik fp:{code}:{zeile}'
      return haushalt.finanzplan[code]?.zeilen[zeile] === undefined ? 'kein Datensatz' : null
    }
    case 'vb': {
      const treffer = gruppe(/^vb:([a-z_]+):([a-z0-9_]+)$/)
      const tabelle = treffer?.[1]
      const posten = treffer?.[2]
      if (tabelle === undefined || posten === undefined) return 'Grammatik vb:{tabelle}:{posten}'
      const daten = VORBERICHT_TABELLEN.find(([name]) => name === tabelle)?.[1]
      if (daten === undefined) return 'keine Tabelle'
      if (posten === 'gesamt') {
        return daten.gesamt_vorbericht.quelle === null ? 'Gesamtzeile ohne Quelle' : null
      }
      const eintrag = daten.posten.find((p) => p.posten === posten)
      return eintrag === undefined || eintrag.quelle === null ? 'kein Datensatz' : null
    }
    case 'meta': {
      const treffer = gruppe(/^meta:([a-z_]+(?:\.[a-z_]+)?)$/)
      const pfad = treffer?.[1]
      if (pfad === undefined) return 'Grammatik meta:{pfad}'
      return metaEintrag(pfad) === undefined ? 'kein Datensatz' : null
    }
    case 'gz': {
      const treffer = gruppe(/^gz:(\d{6}):(\d+)$/)
      const code = treffer?.[1]
      const position = Number(treffer?.[2])
      if (code === undefined) return 'Grammatik gz:{produkt}:{position}'
      const produkt = produkte.find((p) => p.code === code)
      return produkt?.grundzahlen.some((g) => g.position === position) === true
        ? null
        : 'kein Datensatz'
    }
    case 'pr': {
      const treffer = gruppe(/^pr:(\d{6})$/)
      const code = treffer?.[1]
      if (code === undefined) return 'Grammatik pr:{produkt}'
      return produkte.some((p) => p.code === code) ? null : 'kein Datensatz'
    }
    case 'inv': {
      const treffer = gruppe(/^inv:(\d{6}):([^:]+):(\d{6}):(einzahlung|auszahlung)$/)
      if (treffer === null) return 'Grammatik inv:{produkt}:{massnahme}:{konto}:{richtung}'
      const [, produkt, massnahme, konto, richtung] = treffer
      return investitionen.massnahmen.some(
        (m) =>
          m.produkt === produkt &&
          m.massnahme_id === massnahme &&
          m.konto === konto &&
          m.richtung === richtung,
      )
        ? null
        : 'kein Datensatz'
    }
    case 've': {
      const treffer = gruppe(/^ve:(\d{6}):([^:]+):(\d{6})$/)
      if (treffer === null) return 'Grammatik ve:{produkt}:{massnahme}:{konto}'
      const [, produkt, massnahme, konto] = treffer
      return investitionen.ve_faelligkeiten.some(
        (v) => v.produkt === produkt && v.massnahme_id === massnahme && v.konto === konto,
      )
        ? null
        : 'kein Datensatz'
    }
    case 'sd': {
      const treffer = gruppe(/^sd:([a-z_]+)$/)
      const reihe = SCHULDENSTAND_REIHEN.find((name) => name === treffer?.[1])
      return reihe === undefined ? 'Grammatik/Reihe sd:{reihe}' : null
    }
    case 'sp': {
      const treffer = gruppe(
        /^sp:(beamte|tarif|sozial_erziehungsdienst|nachwuchs):(\d+):(\d{2}|-)$/,
      )
      if (treffer === null) return 'Grammatik sp:{teil}:{position}:{produktbereich oder -}'
      const [, teil, position, produktbereich] = treffer
      return stellenplan.zeilen.some(
        (z) =>
          z.teil === teil &&
          z.position === Number(position) &&
          (z.produktbereich ?? '-') === produktbereich,
      )
        ? null
        : 'kein Datensatz'
    }
    case 'seite': {
      const treffer = gruppe(/^seite:(\d+)$/)
      if (treffer === null) return 'Grammatik seite:{n}'
      return SEITEN_DER_DATEN.has(Number(treffer[1])) ? null : 'Seite in keinem Seitenfeld'
    }
    default:
      return 'unbekannte Belegart'
  }
}

describe('Abdeckung: jeder Datensatz mit Seitenfeld hat einen Beleg', () => {
  it('löst jeden erwarteten Schlüssel über findeBeleg auf (E1)', () => {
    const erwartet = erwarteteSchluessel()
    expect(erwartet.length).toBeGreaterThan(700)
    const fehlend = erwartet.filter((schluessel) => findeBeleg(schluessel) === null)
    expect(fehlend, `Belege fehlen in quellen.json: ${fehlend.join(', ')}`).toEqual([])
  })

  it('belegt die Vereinigung aller Seitenfelder mit je einem Seitenbeleg', () => {
    expect(SEITEN_DER_DATEN.size).toBeGreaterThan(150)
    const fehlend = [...SEITEN_DER_DATEN]
      .sort((a, b) => a - b)
      .filter((seite) => findeBeleg(belegSchluessel.seite(seite)) === null)
    expect(fehlend, `Seitenbelege fehlen: ${fehlend.join(', ')}`).toEqual([])
  })
})

describe('Vertrag: jeder Schlüssel in quellen.json folgt der Grammatik und zeigt auf einen Datensatz', () => {
  it('hat keinen Schlüssel ohne Grammatik oder ohne Datensatz', () => {
    const schluessel = Object.keys(quellen.belege)
    expect(schluessel.length).toBeGreaterThan(2000)
    const fehler = schluessel
      .map((name) => ({ name, grund: pruefeSchluessel(name) }))
      .filter((eintrag) => eintrag.grund !== null)
      .map((eintrag) => `${eintrag.name} (${eintrag.grund})`)
    expect(fehler, `Ungültige Belegschlüssel: ${fehler.join('; ')}`).toEqual([])
  })

  it('führt die Belegarten ep, fp, vb, meta, gz, pr, inv, ve, sd, sp und seite', () => {
    const arten = new Set(Object.keys(quellen.belege).map((name) => name.split(':')[0]))
    for (const art of ['ep', 'fp', 'vb', 'meta', 'gz', 'pr', 'inv', 've', 'sd', 'sp', 'seite']) {
      expect(arten.has(art), `Belegart ${art} fehlt`).toBe(true)
    }
  })

  it('lehnt einen frei erfundenen Schlüssel ab (der Test prüft wirklich)', () => {
    expect(pruefeSchluessel('ep:KL:steuern')).not.toBeNull()
    expect(pruefeSchluessel('gz:000000:1')).not.toBeNull()
    expect(pruefeSchluessel('xx:1')).not.toBeNull()
    expect(pruefeSchluessel('seite:99999')).not.toBeNull()
  })
})

describe('Vertrag: Bild und Seite jedes Belegs stimmen mit der seiten-Karte überein', () => {
  it('gibt jedem Beleg ein Seitenbild gleichen Namens', () => {
    const fehler: string[] = []
    for (const [name, beleg] of Object.entries(quellen.belege)) {
      const seite = quellen.seiten[String(beleg.pdf_seite)]
      if (seite === undefined) {
        fehler.push(`${name}: Seite ${String(beleg.pdf_seite)} fehlt in seiten`)
      } else if (seite.bild !== beleg.bild) {
        fehler.push(`${name}: bild ${beleg.bild} statt ${seite.bild}`)
      }
      const seitenschluessel = /^seite:(\d+)$/.exec(name)
      if (seitenschluessel !== null) {
        if (Number(seitenschluessel[1]) !== beleg.pdf_seite) {
          fehler.push(`${name}: pdf_seite ${String(beleg.pdf_seite)}`)
        }
        if (beleg.bbox !== null) {
          fehler.push(`${name}: Seitenbelege haben nie ein Rechteck`)
        }
      }
    }
    expect(fehler, fehler.join('; ')).toEqual([])
  })

  it('führt zu jeder Seite der seiten-Karte mindestens einen Beleg', () => {
    const belegSeiten = new Set(
      Object.values(quellen.belege).map((beleg) => String(beleg.pdf_seite)),
    )
    const ohneBeleg = Object.keys(quellen.seiten).filter((seite) => !belegSeiten.has(seite))
    expect(ohneBeleg, `Seiten ohne Beleg: ${ohneBeleg.join(', ')}`).toEqual([])
  })
})
