import { describe, expect, it } from 'vitest'

import { listenVersatz, randAusMaximalbreite } from '@/lib/menueVersatz'

// Der Quelltext der Menügruppe (wie in `menue.test.ts` über `?raw`): die Verdrahtung von
// `positioniere()` wird am Quelltext festgenagelt, weil vitest ohne DOM läuft.
const gruppenQuelltexte = import.meta.glob<string>('/src/components/MenueGruppe.vue', {
  query: '?raw',
  import: 'default',
  eager: true,
})
const gruppenQuelltext = gruppenQuelltexte['/src/components/MenueGruppe.vue'] ?? ''

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

describe('Verdrahtung in MenueGruppe.vue', () => {
  it('delegiert an listenVersatz und randAusMaximalbreite', () => {
    expect(gruppenQuelltext).toContain('listenVersatz(')
    expect(gruppenQuelltext).toContain('randAusMaximalbreite(')
  })

  it('setzt den reaktiven Versatz nicht mehr vor dem Messen auf 0', () => {
    expect(gruppenQuelltext).not.toMatch(/versatz\.value\s*=\s*0\s*$/m)
  })
})
