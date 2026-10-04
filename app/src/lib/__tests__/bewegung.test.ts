import { describe, expect, it } from 'vitest'
import type { EChartsOption } from 'echarts'

import { ohneAnimation, useReducedMotion } from '@/lib/bewegung'

describe('ohneAnimation', () => {
  it('liefert bei reduzierter Bewegung eine Kopie mit animation false', () => {
    const option: EChartsOption = { animation: true, series: [{ type: 'bar', data: [1] }] }
    const ergebnis = ohneAnimation(option, true)
    expect(ergebnis.animation).toBe(false)
    expect(ergebnis.series).toEqual(option.series)
    expect(ergebnis).not.toBe(option)
  })

  it('laesst das uebergebene Objekt unveraendert', () => {
    const option: EChartsOption = { animation: true }
    ohneAnimation(option, true)
    expect(option.animation).toBe(true)
  })

  it('gibt die Option ohne reduzierte Bewegung unveraendert zurueck', () => {
    const option: EChartsOption = { animation: true }
    expect(ohneAnimation(option, false)).toBe(option)
  })
})

describe('useReducedMotion', () => {
  it('liefert ohne window einen schreibgeschuetzten Ref mit false', () => {
    expect(typeof window).toBe('undefined')
    expect(useReducedMotion().value).toBe(false)
  })
})
