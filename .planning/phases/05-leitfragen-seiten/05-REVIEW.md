---
phase: 05-leitfragen-seiten
reviewed: 2026-10-05T00:00:00Z
depth: standard
files_reviewed: 13
files_reviewed_list:
  - app/src/charts/__tests__/farben.test.ts
  - app/src/charts/echartsTheme.ts
  - app/src/components/DatenTabelle.vue
  - app/src/components/GeldflussBalken.vue
  - app/src/lib/__tests__/geldfluss.test.ts
  - app/src/lib/geldfluss.ts
  - app/src/pages/GeldflussPage.vue
  - app/src/pages/StartPage.vue
  - pipeline/ostbevern/app_daten.py
  - pipeline/ostbevern/pruefung.py
  - pipeline/ostbevern/texte.py
  - pipeline/tests/test_pruefung.py
  - pipeline/tests/test_texte.py
findings:
  critical: 0
  warning: 2
  info: 4
  total: 6
status: issues_found
---

# Phase 5: Code Review Report (incremental re-review of the fix commits)

**Reviewed:** 2026-10-05
**Depth:** standard
**Files Reviewed:** 13
**Status:** issues_found

## Summary

I re-reviewed the diff `ce51941..HEAD` for the seven fixes WR-01 to WR-07. I did not re-report the open Info items IN-01 to IN-11 from the previous round.

All seven fixes work in their main path. No regression and no security issue turned up.

- **WR-01 (rd. / berechnet):** The `gerundet` flags come from `haushalt.json` (`vorbericht.*.posten[].gerundet`). In the checked-in data, all four posten behind the flagged nodes are `true`. The edge-tooltip rule `von.seite === 'links' ? von.gerundet : nach.gerundet` is correct for every edge of the graph. The `zelle` slot overrides in `GeldflussPage` and `GeldflussBalken` return only comments for non-`wert` columns. Vue's `renderSlot` then falls back to the default cell content, so the name and share columns still render.
- **WR-02 (Start page wording):** `baueEinstiege` skips `synthetisch` nodes, which is what makes the new wording true.
- **WR-03 (`mitDeckkraft`):** The canvas resolution is correct for opaque colours. The fallback chain is sound.
- **WR-05 (Regel 5 without `meta`):** The test reaches the new branch, because the loop over the monkeypatched `REGEL5_TABELLEN_OHNE_GESAMT` skips the empty frame.
- **WR-06 (formulas):** The four `ABGELEITET` formulas read only from `werte`, never from each other. Skipping unused ones is therefore safe.

Two weaknesses remain in the fixes. They are listed below, followed by four Info items.

## Warnings

### WR-01: `Quelle:` page lists without a repeated `S.` are still silently truncated (incomplete fix of the old WR-04)

**File:** `pipeline/ostbevern/texte.py:55-58, 125-130`
**Issue:** `_SEITENSPANNE_MUSTER` only catches `S. a-b`, `S. a/b` and `S. a–b`. `_SEITENZAHL_MUSTER` (`S\.\s*(\d+)`) still reads just the first number after each `S.`, so these forms drop pages without any error:
- `Quelle: S. 24, 25` becomes `(24,)`
- `Quelle: S. 309 bis 311`
- `Quelle: S. 309 f.`
- `Quelle: S. 309—311` (em dash)
- `Quelle: S. 309 − 311` (minus sign)

Dropped pages mean a missing page reference next to a number in the app. That is the same failure class as the original finding. The new error message itself prescribes the `S. 309, S. 310` form, but nothing enforces it. The checked-in `.md` files use that form today, so no data is affected now. The next author who writes `S. 24, 25` gets no error.

**Fix:** Validate the whole line instead of blacklisting range spellings. After removing every `S. <n>`, the remainder may contain only separators.
```python
_QUELLE_ERLAUBT = re.compile(r"^(?:S\.\s*\d+)(?:\s*[,;]\s*S\.\s*\d+)*$")
if not _QUELLE_ERLAUBT.fullmatch(quelle_treffer.group(1).strip()):
    raise TexteFehler(
        f"{pfad}: Abschnitt {schluessel!r}: Quelle muss 'S. n, S. m' sein "
        "(jede Seite einzeln, keine Spannen oder Listen ohne 'S.')"
    )
```
Then `_SEITENSPANNE_MUSTER` is no longer needed. Add `"S. 24, 25"` and `"S. 309 bis 311"` to the parametrised test.

### WR-02: `DatenTabelle` overflow detection observes only the elements present at mount

**File:** `app/src/components/DatenTabelle.vue:55-84`
**Issue:** `onMounted` observes `rahmen` and its children as they exist at that moment. The template swaps the child with `v-if` / `v-else-if` between skeleton, empty state and table. A table that appears after a `laedt` phase, or after the empty state, is never observed.

`rahmen` itself keeps its width, so only a height change on `rahmen` triggers `pruefeUeberlauf`. If the table's width then changes without a height change, `ueberlaeuft` goes stale. Examples are `wa-format-number` upgrading after the custom elements are defined, a year switch that changes number widths, or new text in a column.

The consequence is that a horizontally scrolling table can have no `tabindex` and no name (WCAG 2.1.1 keyboard failure). The inverse also happens: a table that no longer overflows keeps a useless tab stop. The path is only taken for consumers that start with `laedt`. The current pages mount the table synchronously, so the bug is latent.

**Fix:** Re-observe whenever the content branch changes.
```ts
import { nextTick, watch } from 'vue'

function beobachteInhalt() {
  beobachter?.disconnect()
  if (rahmen.value === null) return
  beobachter?.observe(rahmen.value)
  for (const kind of Array.from(rahmen.value.children)) beobachter?.observe(kind)
  pruefeUeberlauf()
}
// in onMounted: create the observer, then beobachteInhalt()
watch([() => props.laedt, istLeer, istDatenModus], () => void nextTick(beobachteInhalt))
```

## Info

### IN-01: `alsRgb` turns an unparseable colour into black without a signal

**File:** `app/src/charts/echartsTheme.ts:141-158`
**Issue:** A canvas ignores an invalid `fillStyle` assignment and keeps its default `#000000`. If a token resolves to something the browser cannot parse (for example `light-dark(...)` in an older engine, or an unresolved `var(...)`), `getImageData` returns `0,0,0,255`. The `a !== 255` guard does not catch that. The decal then becomes black stripes at 45 % or 55 % opacity, which is a silent wrong result and the opposite of what the WR-03 fix intended. The colour is evaluated once at module load.
**Fix:** Detect the rejection by assigning a sentinel first, then comparing.
```ts
kontext.fillStyle = '#010203'
kontext.fillStyle = farbe
if (kontext.fillStyle === '#010203') return null // Browser hat die Farbe abgelehnt
```
Use it only when `farbe` is not itself `#010203`.

### IN-02: Scroll region without `beschriftung` is never keyboard-focusable; the new overflow logic has no test

**File:** `app/src/components/DatenTabelle.vue:84, 103-107`
**Issue:** `scrollbarBenannt` requires `beschriftung`. A table without a caption that overflows horizontally gets no `tabindex`, which axe reports as `scrollable-region-focusable`. `tabindex="0"` could be bound to `ueberlaeuft` alone, with `role` and `aria-label` kept conditional on `beschriftung`.

The fix report notes that the vitest suite has no DOM. The mount, `ResizeObserver` and attribute behaviour therefore have no automated coverage at all.

**Fix:** Bind `:tabindex="ueberlaeuft ? 0 : undefined"`. Add a test under happy-dom or jsdom, or accept the manual check and record it in the verification notes.

### IN-03: Regel 5 still skips the Kreisumlage check silently when `meta` is `None`

**File:** `pipeline/ostbevern/pruefung.py:1477`
**Issue:** WR-05 closed the silent skip for Konzessionsabgaben. The directly adjacent branch `if "transferaufwendungen" in vorbericht and meta is not None and eckwerte is not None:` keeps the old pattern. The production caller (`pruefe_alles`) always passes both arguments, so this only affects direct callers. Still, the two branches of one rule now behave differently.
**Fix:** Raise `PruefungsFehler` when `"transferaufwendungen"` is present and `meta` or `eckwerte` is `None`, as in the Konzessions branch. If `eckwerte=None` is meant to be legitimate, document that in the docstring.

### IN-04: The "rd." / "berechnet" cell template is copy-pasted three times; the space after "rd." can wrap

**File:** `app/src/pages/GeldflussPage.vue:77-83, 93-96`; `app/src/components/GeldflussBalken.vue:82-85`
**Issue:** The block `<span v-if="zeile['gerundet'] === 1">rd. </span>{{ euro(wert) }} <BerechnetEtikett .../>` appears three times. The next change to the display rule has to be made in three places. The separator is an ordinary space, so "rd." can end a line while the amount starts the next. `euro()` already uses a non-breaking space before "€", and `betragMitHinweis` in `geldfluss.ts` uses a plain space too, so the text rules are inconsistent.

Test coverage for the `von.seite === 'links'` edge rule in `tooltipInhalt` is also thin. The new tests cover node tooltips and segments but not an edge tooltip, so inheriting the flag from `von` or `nach` could silently break.
**Fix:** Extract a small `EuroBetrag` component with props `wert`, `gerundet` and `berechnet`. Use `rd. ` as the prefix in both the component and `betragMitHinweis`. Add an edge-tooltip test: a Gewerbesteuer to Gemeinde edge contains `rd. `, and a Gemeinde to KL edge does not.

---

_Reviewed: 2026-10-05_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
