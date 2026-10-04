import { describe, expect, it } from 'vitest'

import { htmlSicher, tooltipZeilen } from '@/charts/tooltip'

describe('htmlSicher (T-05-12)', () => {
  it('maskiert HTML-Sonderzeichen', () => {
    expect(htmlSicher('<b>A & B</b>')).toBe('&lt;b&gt;A &amp; B&lt;/b&gt;')
  })

  it('maskiert Anfuehrungszeichen, damit keine Attribute ausbrechen', () => {
    expect(htmlSicher('"x" onmouseover=\'y\'')).not.toMatch(/["']/)
  })
})

describe('tooltipZeilen', () => {
  it('maskiert jede Zeile und verbindet sie mit einem Zeilenumbruch-Element', () => {
    expect(tooltipZeilen(['A<', 'B'])).toBe('A&lt;<br>B')
  })

  it('liefert fuer keine Zeilen einen leeren String', () => {
    expect(tooltipZeilen([])).toBe('')
  })
})
