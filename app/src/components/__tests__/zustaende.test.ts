import { createSSRApp, type Component } from 'vue'
import { renderToString } from 'vue/server-renderer'
import { describe, expect, it, vi } from 'vitest'

import BaseChart, { datenpunkte } from '@/components/BaseChart.vue'
import DatenTabelle from '@/components/DatenTabelle.vue'
import { KEIN_WERT } from '@/charts/format'
import type { DatenSpalte, DatenZeile } from '@/components/datenTabelle'

// Zustände von BaseChart und DatenTabelle (E6, QUAL-02): laden, Fehler, leer, teilweise leer.
// Gerendert wird serverseitig mit `vue/server-renderer` (Teil des vue-Pakets, kein neues
// Paket, kein DOM). VChart zeichnet in Node nichts; es wird durch eine leere Komponente
// ersetzt, geprüft wird der Rahmen, den BaseChart darum setzt.

vi.mock('vue-echarts', () => ({
  default: { name: 'VChart', render: () => null },
}))

function rendere(komponente: Component, props: Record<string, unknown>): Promise<string> {
  return renderToString(createSSRApp(komponente, props))
}

const MIT_DATEN = {
  series: [{ type: 'bar', data: [1, 2, 3] }],
}

describe('BaseChart Zustände', () => {
  it('laedt: zeigt wa-skeleton, weder Diagramm noch Leerzustand', async () => {
    const html = await rendere(BaseChart, { option: MIT_DATEN, laedt: true })
    expect(html).toContain('<wa-skeleton')
    expect(html).not.toContain('om-base-chart__chart')
    expect(html).not.toContain('Keine Einzelwerte')
  })

  it('fehler: zeigt den Fehlertext statt eines leeren Bereichs', async () => {
    const html = await rendere(BaseChart, { option: MIT_DATEN, fehler: true })
    expect(html).toContain('Diagramm kann nicht angezeigt werden')
    expect(html).not.toContain('om-base-chart__chart')
    expect(html).not.toContain('<wa-skeleton')
  })

  it('leer: eine Option ohne Serie zeigt Titel und Text des Leerzustands', async () => {
    const html = await rendere(BaseChart, { option: {} })
    expect(html).toContain('Keine Einzelwerte')
    expect(html).toContain('Der Haushaltsplan nennt hier keine Aufschlüsselung.')
    expect(html).not.toContain('om-base-chart__chart')
  })

  it('leer: Serien ohne Einträge zeigen den Leerzustand mit eigenem Titel und Text', async () => {
    const html = await rendere(BaseChart, {
      option: { series: [{ type: 'line', data: [] }] },
      leerTitel: 'Nichts da',
      leerText: 'Hier fehlen die Werte.',
    })
    expect(html).toContain('Nichts da')
    expect(html).toContain('Hier fehlen die Werte.')
    expect(html).not.toContain('om-base-chart__chart')
  })

  it('mit Daten: der Diagrammcontainer trägt die Zahl der Datenpunkte', async () => {
    const html = await rendere(BaseChart, { option: MIT_DATEN })
    expect(html).toContain('om-base-chart__chart')
    expect(html).toContain('data-om-datenpunkte="3"')
    expect(html).not.toContain('Keine Einzelwerte')
  })
})

describe('datenpunkte()', () => {
  it('zählt data einer einzelnen Serie', () => {
    expect(datenpunkte({ series: { type: 'bar', data: [1, 2, 3] } })).toBe(3)
  })

  it('zählt data, links und edges aller Serien zusammen', () => {
    expect(
      datenpunkte({
        series: [
          { type: 'bar', data: [1, 2] },
          { type: 'sankey', data: [{ name: 'a' }, { name: 'b' }], links: [{}, {}, {}] },
          { type: 'graph', edges: [{}] },
        ],
      }),
    ).toBe(2 + 2 + 3 + 1)
  })

  it('liefert 0 ohne Serie und bei leeren Serien', () => {
    expect(datenpunkte({})).toBe(0)
    expect(datenpunkte({ series: [] })).toBe(0)
    expect(datenpunkte({ series: [{ type: 'bar', data: [] }] })).toBe(0)
  })
})

const SPALTEN: readonly DatenSpalte[] = [
  { schluessel: 'name', titel: 'Name', art: 'text' },
  { schluessel: 'betrag', titel: 'Betrag', art: 'euro' },
]

describe('DatenTabelle Zustände', () => {
  it('laedt: zeigt wa-skeleton, keine Tabelle', async () => {
    const html = await rendere(DatenTabelle, { spalten: SPALTEN, zeilen: [], laedt: true })
    expect(html).toContain('<wa-skeleton')
    expect(html).not.toContain('<table')
    expect(html).not.toContain('Keine Einzelwerte')
  })

  it('leer: zeilen [] zeigt Titel und Text des Leerzustands, keine Tabelle', async () => {
    const html = await rendere(DatenTabelle, { spalten: SPALTEN, zeilen: [] })
    expect(html).toContain('Keine Einzelwerte')
    expect(html).toContain('Der Haushaltsplan nennt hier keine Aufschlüsselung.')
    expect(html).not.toContain('<table')
  })

  it('teilweise leer: eine Zelle ohne Wert zeigt „–“ mit dem verborgenen Text „kein Wert“, nie 0', async () => {
    const zeilen: DatenZeile[] = [
      { name: 'Posten A', betrag: null },
      { name: 'Posten B', betrag: 5 },
    ]
    const html = await rendere(DatenTabelle, { spalten: SPALTEN, zeilen })
    expect(html).toContain('<table')
    // Scoped-CSS-Attribute (data-v-…) stehen im Tag; geprüft wird Tag, Rolle und Inhalt.
    expect(html).toMatch(new RegExp(`<span aria-hidden="true"[^>]*>${KEIN_WERT}</span>`))
    expect(html).toContain('kein Wert')
    // Genau eine Zelle ist leer; die andere trägt ihren Wert an wa-format-number.
    expect(html.split('kein Wert').length - 1).toBe(1)
    expect(html).toContain('value="5"')
    expect(html).not.toContain('value="0"')
  })
})
