import { describe, expect, it } from 'vitest'
import type { BarSeriesOption, EChartsOption } from 'echarts'

import {
  balkenBeschriftung,
  balkenHoehe,
  balkenTooltip,
  horizontaleBalkenOption,
  type BalkenZeile,
} from '@/charts/balken'

const ZEILEN: readonly BalkenZeile[] = [
  { schluessel: 'a', name: 'Steuern', wert: 1000, label: '1.000 € · 50 %' },
  { schluessel: 'b', name: 'Entgelte', wert: 600, label: '600 € · 30 %' },
  { schluessel: 'c', name: 'Sonstige', wert: 400, label: '400 € · 20 %' },
]

const OPTIONEN = { farbe: '#da7e00', wertartText: 'Ansatz 2026' }

function ersteSerie(option: EChartsOption): BarSeriesOption {
  const serie = Array.isArray(option.series) ? option.series[0] : option.series
  if (serie === undefined || serie.type !== 'bar') {
    throw new Error('Keine Balkenserie in der Option')
  }
  return serie
}

function datenNamen(serie: BarSeriesOption): string[] {
  return (serie.data ?? []).map((eintrag) => {
    if (typeof eintrag === 'object' && eintrag !== null && 'name' in eintrag) {
      return String(eintrag.name)
    }
    throw new Error('Datenpunkt ohne Namen')
  })
}

describe('balkenHoehe', () => {
  it('rechnet Zeilen × 40 px + 48 px', () => {
    expect(balkenHoehe(7)).toBe('328px')
  })

  it('liefert ohne Zeilen die Mindesthöhe 48 px', () => {
    expect(balkenHoehe(0)).toBe('48px')
  })

  it('wächst mit einer einzelnen Zeile gleichartig', () => {
    expect(balkenHoehe(1)).toBe('88px')
  })
})

describe('horizontaleBalkenOption', () => {
  it('liefert eine Balkenserie mit einem Balken je Zeile in der übergebenen Reihenfolge', () => {
    const serie = ersteSerie(horizontaleBalkenOption(ZEILEN, OPTIONEN))
    expect(datenNamen(serie)).toEqual(['Steuern', 'Entgelte', 'Sonstige'])
  })

  it('setzt die größte Zeile nach oben (invertierte Kategorienachse)', () => {
    const option = horizontaleBalkenOption(ZEILEN, OPTIONEN)
    const y = Array.isArray(option.yAxis) ? option.yAxis[0] : option.yAxis
    expect(y?.type).toBe('category')
    expect(y?.inverse).toBe(true)
  })

  it('bricht Kategoriebeschriftungen bei 160 px um statt sie abzuschneiden', () => {
    const option = horizontaleBalkenOption(ZEILEN, OPTIONEN)
    const y = Array.isArray(option.yAxis) ? option.yAxis[0] : option.yAxis
    expect(y?.axisLabel).toMatchObject({ width: 160, overflow: 'break' })
  })

  it('beginnt die Wertachse bei 0', () => {
    const option = horizontaleBalkenOption(ZEILEN, OPTIONEN)
    const x = Array.isArray(option.xAxis) ? option.xAxis[0] : option.xAxis
    expect(x?.type).toBe('value')
    expect(x?.min).toBe(0)
  })

  it('färbt jeden Balken in der Standardfarbe oder in der Farbe der Zeile', () => {
    const mitFarbe: BalkenZeile[] = [
      { schluessel: 'a', name: 'A', wert: 5, label: '5' },
      { schluessel: 'b', name: 'B', wert: 4, label: '4', farbe: '#112233' },
    ]
    const serie = ersteSerie(horizontaleBalkenOption(mitFarbe, OPTIONEN))
    const farben = (serie.data ?? []).map((eintrag) =>
      typeof eintrag === 'object' && eintrag !== null && 'itemStyle' in eintrag
        ? (eintrag.itemStyle as { color?: string }).color
        : undefined,
    )
    expect(farben).toEqual(['#da7e00', '#112233'])
  })

  it('beschriftet jede Zeile mit dem Label der Zeile', () => {
    const option = horizontaleBalkenOption(ZEILEN, OPTIONEN)
    const formatter = ersteSerie(option).label?.formatter
    expect(typeof formatter).toBe('function')
    if (typeof formatter !== 'function') {
      return
    }
    const texte = ZEILEN.map((_zeile, index) =>
      formatter({ dataIndex: index } as Parameters<typeof formatter>[0]),
    )
    expect(texte).toEqual(['1.000 € · 50 %', '600 € · 30 %', '400 € · 20 %'])
  })

  it('behält eine Zeile ohne Wert und beschriftet sie mit „–“', () => {
    const teilweise: BalkenZeile[] = [
      { schluessel: 'a', name: 'A', wert: 5, label: '5 € · 100 %' },
      { schluessel: 'b', name: 'B', wert: null, label: 'darf nicht erscheinen' },
    ]
    const option = horizontaleBalkenOption(teilweise, OPTIONEN)
    const serie = ersteSerie(option)
    expect(datenNamen(serie)).toEqual(['A', 'B'])
    expect(balkenBeschriftung(teilweise[1]!)).toBe('–')
  })

  it('liefert ohne Zeilen eine leere Datenreihe (BaseChart zeigt den Leerzustand)', () => {
    const serie = ersteSerie(horizontaleBalkenOption([], OPTIONEN))
    expect(serie.data).toEqual([])
  })

  it('reserviert rechts so viel Platz, wie die längste Beschriftung braucht', () => {
    const lang: BalkenZeile[] = [
      { schluessel: 'a', name: 'A', wert: 5, label: '27,5 Mio. € · 54,5 %' },
    ]
    const kurz: BalkenZeile[] = [{ schluessel: 'a', name: 'A', wert: 5, label: '5 € · 1 %' }]
    const rechts = (zeilen: BalkenZeile[]) => {
      const grid = horizontaleBalkenOption(zeilen, OPTIONEN).grid
      const eins = Array.isArray(grid) ? grid[0] : grid
      return Number(eins?.right)
    }
    expect(rechts(lang)).toBeGreaterThan(rechts(kurz))
  })

  it('bricht die Beschriftung auf schmalen Bildschirmen in zwei Zeilen und verkleinert den Namensbereich', () => {
    const schmal = horizontaleBalkenOption(ZEILEN, { ...OPTIONEN, schmal: true })
    const y = Array.isArray(schmal.yAxis) ? schmal.yAxis[0] : schmal.yAxis
    expect(y?.axisLabel).toMatchObject({ width: 120, overflow: 'break' })
    const formatter = ersteSerie(schmal).label?.formatter
    expect(typeof formatter).toBe('function')
    if (typeof formatter === 'function') {
      expect(formatter({ dataIndex: 0 } as Parameters<typeof formatter>[0])).toBe('1.000 €\n50 %')
    }
  })
})

describe('balkenTooltip (T-05-25)', () => {
  it('maskiert HTML im Zeilennamen', () => {
    const zeile: BalkenZeile = { schluessel: 'x', name: '<b>X</b>', wert: 1, label: '1 € · 100 %' }
    const html = balkenTooltip(zeile, 'Ansatz 2026')
    expect(html).toContain('&lt;b&gt;X&lt;/b&gt;')
    expect(html).not.toContain('<b>')
  })

  it('nennt Name, Betrag mit Anteil und die Wertart mit Jahr', () => {
    const html = balkenTooltip(ZEILEN[0]!, 'Ansatz 2026')
    expect(html).toBe('Steuern<br>1.000 € · 50 %<br>Ansatz 2026')
  })

  it('zeigt für eine Zeile ohne Wert „–“ statt eines Betrags', () => {
    const zeile: BalkenZeile = { schluessel: 'x', name: 'X', wert: null, label: 'egal' }
    expect(balkenTooltip(zeile, 'Ansatz 2026')).toBe('X<br>–<br>Ansatz 2026')
  })

  it('hängt der Option an: der Tooltip-Formatter liest die Zeile über dataIndex', () => {
    const zeilen: BalkenZeile[] = [
      { schluessel: 'x', name: '<i>X</i>', wert: 1, label: '1 € · 100 %' },
    ]
    const option = horizontaleBalkenOption(zeilen, OPTIONEN)
    const tooltip = Array.isArray(option.tooltip) ? option.tooltip[0] : option.tooltip
    const formatter = tooltip?.formatter
    expect(typeof formatter).toBe('function')
    if (typeof formatter === 'function') {
      const html = formatter({ dataIndex: 0 } as Parameters<typeof formatter>[0], '', () => {})
      expect(html).toContain('&lt;i&gt;X&lt;/i&gt;')
    }
  })
})
