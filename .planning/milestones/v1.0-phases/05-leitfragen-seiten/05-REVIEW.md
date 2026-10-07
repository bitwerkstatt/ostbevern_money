---
phase: 05-leitfragen-seiten
reviewed: 2026-10-05T00:00:00Z
depth: standard
files_reviewed: 18
files_reviewed_list:
  - app/src/charts/echartsTheme.ts
  - app/src/components/DatenTabelle.vue
  - app/src/components/EuroBetrag.vue
  - app/src/components/GeldflussBalken.vue
  - app/src/components/GlossarListe.vue
  - app/src/lib/__tests__/geldfluss.test.ts
  - app/src/lib/__tests__/sprungziel.test.ts
  - app/src/lib/__tests__/stiltokens.test.ts
  - app/src/lib/geldfluss.ts
  - app/src/lib/sprungziel.ts
  - app/src/pages/EinnahmenPage.vue
  - app/src/pages/GeldflussPage.vue
  - app/src/pages/ProduktPage.vue
  - app/src/router/index.ts
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

# Phase 5: Code Review Report (incremental re-review since e70324d)

**Reviewed:** 2026-10-05
**Depth:** standard
**Files Reviewed:** 18
**Status:** issues_found

## Summary

I re-reviewed the diff `e70324d..HEAD`. It contains the fixes for the previous WR-01 (Quelle-Zeile), WR-02 (`DatenTabelle` observer), IN-03 (Regel 5 without `meta`/`eckwerte`), the `scroll-margin-top` gap closures (G-05-4, G-05-6), and the new `EuroBetrag` component. I did not re-report the old open Info items.

The previous findings are fixed:

- **Quelle-Zeile (texte.py):** The whole line is now validated with `fullmatch`, so every spelling that is not `S. n[, S. m]*` is rejected. I checked the checked-in `.md` sources and none uses a different form. All 145 tests in `test_texte.py` and `test_pruefung.py` pass (`uv run pytest`).
- **`DatenTabelle`:** `beobachteInhalt` now re-observes after every `v-if` branch change. The watcher runs `nextTick` after the pre-flush, so the new element exists by then.
- **Regel 5 (pruefung.py):** The Kreisumlage check now raises instead of skipping silently.
- **Scroll offset (sprungziel.ts):** I checked vue-router's `getElementPosition`. It computes `elRect.top - docRect.top - (offset.top || 0)`, so passing `{ el, top: scroll-margin-top }` is the right way to apply the offset. `--scroll-margin-top` is defined by Web Awesome (`chunk.FFR4H3XU.js`).

I could not run the vitest suite in this sandbox. The rolldown native binding is missing, which is an environment problem. The app-side findings come from reading the code only.

No bugs and no security issues in the diff. There are two consistency and quality warnings, and four Info items.

## Warnings

### WR-01: `rd.` rule is only half migrated; the new non-breaking space and `EuroBetrag` coexist with five older copies

**File:** `app/src/lib/geldfluss.ts:123-129`, `app/src/components/EuroBetrag.vue:5-8`
**Issue:** The diff introduces `RD_PRAEFIX = 'rd. '` so that "rd." never stands alone at the end of a line. The comment in `EuroBetrag.vue` says the rule lives "nur hier (und in `betragMitHinweis`)". That is not true. These places still build the prefix with a plain space:
- `app/src/components/SteuerZeitreihe.vue:183` (`<span v-if="zeile['gerundet'] === 1">rd. </span>{{ euro(wert) }}`, the same markup that `EuroBetrag` replaced in two other files)
- `app/src/lib/drilldown.ts:201` and `:360`
- `app/src/lib/zeitreihen.ts:238`
- `app/src/components/AufwandTreemap.vue:53`
- `app/src/components/EbenenTabelle.vue:71`

The same amount can therefore wrap as "rd." / "7.800.000 €" in one view and stay together in another. If someone later changes the wording or spacing in `RD_PRAEFIX`, these sites diverge. `quelltext.test.ts:137` even whitelists the old markup as acceptable, so the test suite does not catch it.
**Fix:** Use `betragMitHinweis` in the `.ts` files and `EuroBetrag` in `SteuerZeitreihe.vue`. For example in `zeitreihen.ts`: `return punkt.wert !== null ? betragMitHinweis(punkt.wert, punkt.gerundet) : KEIN_WERT`, and adapt `zeitreihen.test.ts:230` to `RD_PRAEFIX`. For the `euroKurz` variants (`drilldown.ts:360`, `AufwandTreemap.vue:53`), prefix with `RD_PRAEFIX`. Alternatively, correct the `EuroBetrag` comment so it does not claim a single source of truth, and finish the migration in a follow-up task.

### WR-02: `DatenTabelle` makes the scroll container focusable without a role or name when `beschriftung` is missing

**File:** `app/src/components/DatenTabelle.vue:117-122`
**Issue:** `tabindex` is now bound to `ueberlaeuft` alone, while `role="region"` and `aria-label` still need `beschriftung` (`scrollbarBenannt`). If a table overflows and no `beschriftung` is passed, the frame becomes a tab stop with no role and no accessible name. A keyboard user lands on an anonymous `div`. The project requires Lighthouse a11y of at least 95 and focus control. The comment in the script says a `aria-label` without role would be invalid, but it does not address the opposite case, a tab stop without a name. Today every call site passes `beschriftung`, so nothing is visible yet.
**Fix:** Either bind `tabindex` to `scrollbarBenannt` again (a table without a name is then not keyboard-scrollable, which `beschriftung` being required would solve), or make `beschriftung` required in `defineProps` and keep the current binding:
```ts
beschriftung: string
```
At minimum, add a dev warning like the existing `watchEffect` one for `zeilen` without `spalten`.

## Info

### IN-01: `alsRgb` rejects a valid colour that happens to normalise to the marker

**File:** `app/src/charts/echartsTheme.ts:136-160`
**Issue:** The rejection check compares the normalised `fillStyle` with `#010203` and then excludes the case where the trimmed input string equals the marker. An input such as `rgb(1, 2, 3)` or `#010203` written in upper case is not caught by the string comparison for `rgb(...)`, because the browser reads back `#010203`. The function then returns `null` for a legal colour and the caller falls back silently. The practical risk is near zero, but the exclusion only handles one spelling.
**Fix:** Use two different markers and set the second one only if the first read-back is unchanged, or compare after normalising the input through a second canvas assignment:
```ts
kontext.fillStyle = MARKER_A
kontext.fillStyle = farbe
const erstes = kontext.fillStyle
kontext.fillStyle = MARKER_B
kontext.fillStyle = farbe
if (erstes === MARKER_A && kontext.fillStyle === MARKER_B) return null
```

### IN-02: `DatenTabelle` only re-observes on `laedt` / `istLeer` / `istDatenModus` changes, not on slot-mode content swaps

**File:** `app/src/components/DatenTabelle.vue:69-92`
**Issue:** In slot mode (default slot, no `zeilen`), a parent can replace the slotted element. The watcher does not fire for that, so the new element is never observed. No call site does this today, and the `rahmen` itself is still observed, so the effect is limited to a stale `ueberlaeuft` when only the child's width changes.
**Fix:** Either document that slot-mode content must be stable, or use a `MutationObserver({ childList: true })` on `rahmen` that calls `beobachteInhalt`.

### IN-03: Edge-tooltip test has a vacuous negative assertion

**File:** `app/src/lib/__tests__/geldfluss.test.ts:215-218`
**Issue:** The case "Gemeinde → Kreisumlage ... `not.toContain(RD_PRAEFIX)`" would also pass if the formatter returned an empty string for that edge, for example after a renamed node id. Only the positive Ertrag edge proves that the formatter runs at all. The "right-hand node inherits the flag" half of the rule is therefore not tested with a case that would flip to `true`.
**Fix:** Also assert a positive marker for the same edge (for example that the result contains `euro(kante.wert)`), or add a right-hand node with `gerundet: true` to the fixture.

### IN-04: The token guard cannot see dynamic token names and only reads Web Awesome's global stylesheets

**File:** `app/src/lib/__tests__/stiltokens.test.ts:15-36`
**Issue:** `verwendeteTokens` matches `var(--wa-[a-z0-9-]+`. A template string such as `` var(--wa-color-${farbe}) `` yields the truncated name `--wa-color-` and fails as undefined, a false positive. Tokens that Web Awesome defines only inside component CSS (Lit `css` in JS chunks) are not collected, because `webAwesomeTokens` reads only `dist/styles/**/*.css`. Neither case occurs today, so the guard is correct for the current code, but the next author gets a confusing failure.
**Fix:** Add one sentence to the file header comment naming both limits, and skip names ending in `-` in `verwendeteTokens` with a clear message instead.

---

_Reviewed: 2026-10-05_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
