import { describe, expect, it } from 'vitest'

import { MENUE } from '@/lib/menue'

describe('MENUE (D-13)', () => {
  it('listet Start, Woher?, Wofür?, Geldfluss, Glossar in dieser Reihenfolge', () => {
    expect(MENUE.map((eintrag) => eintrag.name)).toEqual([
      'start',
      'einnahmen',
      'ausgaben',
      'geldfluss',
      'glossar',
    ])
    expect(MENUE.map((eintrag) => eintrag.text)).toEqual([
      'Start',
      'Woher?',
      'Wofür?',
      'Geldfluss',
      'Glossar',
    ])
  })

  it('behält das gewählte Jahr genau bei einnahmen, ausgaben und geldfluss (D-10)', () => {
    expect(MENUE.filter((eintrag) => eintrag.mitJahr).map((eintrag) => eintrag.name)).toEqual([
      'einnahmen',
      'ausgaben',
      'geldfluss',
    ])
  })

  it('führt jeden Eintrag nur einmal', () => {
    expect(new Set(MENUE.map((eintrag) => eintrag.name)).size).toBe(MENUE.length)
  })
})
