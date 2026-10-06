import { describe, expect, it } from 'vitest'

import { zweizeilig } from '@/charts/beschriftung'
import { euroKurz } from '@/charts/format'

describe('zweizeilig', () => {
  it('trennt einen Betrag in Mio. € am ersten Leerzeichen', () => {
    expect(zweizeilig(euroKurz(21_305_000))).toBe('21,3\nMio. €')
  })

  it('trennt einen vollen Euro-Betrag vor dem Euro-Zeichen', () => {
    expect(zweizeilig(euroKurz(712_600))).toBe('712.600\n€')
  })

  it('lässt einen Text ohne Leerzeichen einzeilig', () => {
    expect(zweizeilig('–')).toBe('–')
  })
})
