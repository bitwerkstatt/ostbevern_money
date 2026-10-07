import { describe, expect, it } from 'vitest'

import { listenVersatz, randAusMaximalbreite } from '@/lib/menueVersatz'

// Reine Rechnung der Listenlage. Die Verdrahtung in `MenueGruppe.vue` (Öffnen, Resize,
// `style.left`) prüft `e2e/interaktion.spec.ts` im Browser (D-14, 06/IN-09), nicht der Quelltext.

describe('listenVersatz (WR-01, UI-SPEC E12)', () => {
  it('verschiebt die Liste beim ersten Öffnen nach links, wenn sie rechts überläuft', () => {
    expect(
      listenVersatz({
        links: 600,
        rechts: 800,
        angewandterVersatz: 0,
        fensterbreite: 780,
        rand: 16,
      }),
    ).toBe(-36)
  })

  it('liefert beim zweiten Öffnen mit veraltetem Versatz denselben Versatz (Review-Spur)', () => {
    // Der alte Algorithmus lieferte hier 0, weil das Rechteck noch den Versatz des ersten
    // Öffnens trug und deshalb „passte“.
    expect(
      listenVersatz({
        links: 564,
        rechts: 764,
        angewandterVersatz: -36,
        fensterbreite: 780,
        rand: 16,
      }),
    ).toBe(-36)
  })

  it('liefert 0, wenn die Liste ins Fenster passt', () => {
    expect(
      listenVersatz({
        links: 600,
        rechts: 800,
        angewandterVersatz: 0,
        fensterbreite: 1200,
        rand: 16,
      }),
    ).toBe(0)
  })

  it('korrigiert einen Überlauf links auf den Rand', () => {
    expect(
      listenVersatz({
        links: 4,
        rechts: 300,
        angewandterVersatz: 0,
        fensterbreite: 780,
        rand: 16,
      }),
    ).toBe(12)
  })

  it('setzt eine zu breite Liste mit der linken Kante auf den Rand', () => {
    expect(
      listenVersatz({
        links: 600,
        rechts: 1100,
        angewandterVersatz: 0,
        fensterbreite: 520,
        rand: 16,
      }),
    ).toBe(-584)
  })
})

describe('randAusMaximalbreite', () => {
  it('leitet den Rand aus der berechneten max-width ab', () => {
    expect(randAusMaximalbreite(780, '748px')).toBe(16)
  })

  it('liefert 0 ohne Pixelwert', () => {
    expect(randAusMaximalbreite(780, 'none')).toBe(0)
  })

  it('begrenzt einen negativen Rand auf 0', () => {
    expect(randAusMaximalbreite(780, '900px')).toBe(0)
  })
})

interface Basis {
  links: number
  rechts: number
}

/** Messung einer Liste, die mit `versatz` verschoben ist: das Rechteck trägt den Versatz. */
function gemessen(basis: Basis, versatz: number, fensterbreite: number) {
  return {
    links: basis.links + versatz,
    rechts: basis.rechts + versatz,
    angewandterVersatz: versatz,
    fensterbreite,
    rand: 16,
  }
}

describe('Resize und Fixpunkt (WR-01)', () => {
  const liste: Basis = { links: 600, rechts: 800 }

  it('Resize-Spur: Fenster wird breiter, der Versatz fällt auf 0', () => {
    expect(listenVersatz(gemessen(liste, -36, 780))).toBe(-36)
    expect(listenVersatz(gemessen(liste, -36, 1200))).toBe(0)
  })

  it('Resize-Spur: Fenster wird schmaler, die rechte Kante landet am Rand', () => {
    expect(listenVersatz(gemessen(liste, -36, 700))).toBe(700 - 16 - 800)
  })

  const rechtecke: Basis[] = [
    { links: 600, rechts: 800 },
    { links: 4, rechts: 300 },
    { links: 600, rechts: 1100 },
  ]
  const veralteteVersaetze = [-584, -200, -36, 0, 12, 50, 300]
  const fensterbreiten = [520, 780, 1200]

  const faelle = rechtecke.flatMap((basis) =>
    veralteteVersaetze.flatMap((versatz) =>
      fensterbreiten.map((breite) => ({ basis, versatz, breite })),
    ),
  )

  it.each(faelle)(
    'Fixpunkt: Rechteck $basis.links/$basis.rechts, veralteter Versatz $versatz, Fenster $breite',
    ({ basis, versatz, breite }) => {
      const frisch = listenVersatz(gemessen(basis, 0, breite))
      expect(listenVersatz(gemessen(basis, versatz, breite))).toBe(frisch)
    },
  )

  it.each(faelle)(
    'Idempotenz: Rechteck $basis.links/$basis.rechts, Fenster $breite (Start $versatz)',
    ({ basis, versatz, breite }) => {
      const ergebnis = listenVersatz(gemessen(basis, versatz, breite))
      expect(listenVersatz(gemessen(basis, ergebnis, breite))).toBe(ergebnis)
    },
  )
})
