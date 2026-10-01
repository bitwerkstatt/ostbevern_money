---
status: testing
phase: 01-setup
source: [01-VERIFICATION.md]
started: 2026-10-01T09:55:36Z
updated: 2026-10-01T09:55:36Z
---

## Current Test

number: 1
name: BaseChart loading and error states render correctly
expected: |
  With `npm --prefix app run dev`, a BaseChart with `:laedt="true"` shows `<wa-skeleton effect="sheen">` filling the chart area, not the canvas; with `:fehler="true"` it shows the triangle-exclamation icon and the German fallback copy, not a broken/empty canvas.
awaiting: user response

## Tests

### 1. BaseChart loading and error states render correctly
expected: `:laedt="true"` shows `<wa-skeleton effect="sheen">` filling the chart area, not the canvas; `:fehler="true"` shows the triangle-exclamation icon and the German fallback copy, not a broken/empty canvas.
result: [pending]

### 2. DatenTabelle loading state renders skeleton rows
expected: Passing `:laedt="true"` renders three `<wa-skeleton effect="sheen">` rows in place of the table, not an empty or broken table.
result: [pending]

### 3. App shell at 360 px (header, nav, PageIntro, unknown route, network)
expected: Nav wraps, no horizontal page scroll, PageIntro heading wraps without overflow, active nav link is gold-brown, footer credit visible and working, `#/gibt-es-nicht` redirects to start, Network tab shows no third-party host.
result: [pending]

### 4. Beispieldaten chart and table at full width and 360 px
expected: First bars Ostbevern-Gold, negative "Bereich D" bar in the danger colour, German amount formatting in tooltip/axis, bars turn horizontal at 360 px, callout/table never overflow sideways, "Bereich" column stays sticky while scrolling, "Echte Haushaltszahlen" card shows "Noch keine Daten" instead of an empty chart.
result: [pending]

## Summary

total: 4
passed: 0
issues: 0
pending: 4
skipped: 0
blocked: 0

## Gaps
