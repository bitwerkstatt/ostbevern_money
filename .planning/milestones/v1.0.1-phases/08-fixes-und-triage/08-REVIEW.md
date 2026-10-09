---
phase: 08-fixes-und-triage
reviewed: 2026-10-08T00:00:00Z
depth: standard
files_reviewed: 11
files_reviewed_list:
  - app/e2e/interaktion.spec.ts
  - app/e2e/menueDrawer.ts
  - app/e2e/mobil.spec.ts
  - app/src/App.vue
  - app/src/components/DatenTabelle.vue
  - app/src/components/__tests__/zustaende.test.ts
  - app/src/data/texte.json
  - app/src/lib/__tests__/quelltext.test.ts
  - daten/manuell/texte/glossar.md
  - pipeline/ostbevern/texte.py
  - pipeline/tests/test_texte.py
findings:
  critical: 0
  warning: 2
  info: 3
  total: 5
status: issues_found
---

# Phase 08: Code Review Report (Re-Review der Review-Fixes)

**Reviewed:** 2026-10-08
**Depth:** standard
**Files Reviewed:** 11
**Status:** issues_found

## Summary

Incremental re-review of `3e563056..HEAD`: the fixes for WR-01 (`_pruefe_jahrbezug` in `texte.py`), WR-02 (modifier-click guard and flag reset in `App.vue`), WR-03 (`hatBeschriftung` guard in `DatenTabelle.vue`) and the Nyquist tests from commit 7b9f0a6.

The production fixes themselves are sound:

- `_pruefe_jahrbezug` is wired into `loese_auf`. The real `erklaerungen.md` and `glossar.md` pass it (`pytest tests/test_texte.py`: 107 passed). The `glossar.md` edit that adds `({{jahr.vorjahr|jahr}})` is mirrored byte-consistently in `texte.json`.
- The `App.vue` guard covers ctrl, meta, shift, alt and non-primary buttons. `drawerOffen` is checked before the flag is set. `oeffneDrawer` resets the flag. Keyboard activation (Enter) still reports `button === 0`, so it is unaffected.
- The `DatenTabelle` guard removes role, tabindex and aria-labelledby together when the caption is blank.

There are no security findings and no crash or data-loss defects. The remaining problems are in the test coverage of the WR-03 fix and in a side effect of that fix.

## Warnings

### WR-01: The new WR-03 render tests cannot fail, because SSR never produces an overflowing frame

**File:** `app/src/components/__tests__/zustaende.test.ts:165-189`
**Issue:** Tests "leere Beschriftung" and "Whitespace-only Beschriftung" assert `not.toContain('tabindex' | 'role="region"' | 'aria-labelledby')`. They render via `renderToString`. There `ueberlaeuft` is only set in `onMounted` (`pruefeUeberlauf`), which does not run in SSR, so it is always `false` and `rahmenAttribute(false, …)` returns `{}`. The assertions therefore hold with or without the `hatBeschriftung` guard. Reverting the fix leaves both tests green. The existing test at line 154 ("ohne Überlauf weder role region noch tabindex") already covers exactly this path. The comments claim the tests protect the A11Y-01 guard, which they do not. The only effective protection is the DEV-warning test and the two source-text regex tests in `quelltext.test.ts`.
**Fix:** Test the guard where it can actually be observed. Either mount the component in jsdom/happy-dom with `scrollWidth`/`clientWidth` stubbed so `ueberlaeuft` becomes true, or extract the condition into a pure function in `datenTabelle.ts`, for example `rahmenSichtbar({ ueberlaeuft, laedt, leer, beschriftung })`, and unit-test it. Then drop or mark the two vacuous render tests:
```ts
expect(rahmenAttribute(rahmenSollNamenTragen(true, false, false, '  '), 'c')).toEqual({})
```

### WR-02: Blank `beschriftung` silently trades the unnamed region for a keyboard-inaccessible scroll area

**File:** `app/src/components/DatenTabelle.vue:127-144`
**Issue:** If `hatBeschriftung` is false and the table overflows, the frame loses `tabindex="0"`. A horizontally scrolling region that cannot take focus cannot be scrolled by keyboard users (WCAG 2.1.1, axe `scrollable-region-focusable`). The guard removes the A11Y-01 defect (unnamed region) and introduces the A11Y-03 defect (unreachable content). In a production build the `console.warn` is compiled out (`import.meta.env.DEV`), so the regression is invisible there. The caption element is also still rendered with empty text.
**Fix:** Keep the table reachable and make the empty case fail loudly instead of degrading silently. Options:
- Throw in DEV and in tests, as `alsZahl` already does for bad cell types, instead of only warning.
- Fall back to a non-empty generic name, for example `props.beschriftung.trim() || 'Tabelle'`, for both the caption and the frame.

## Info

### IN-01: Source-text regex tests are fragile against formatting

**File:** `app/src/lib/__tests__/quelltext.test.ts:238-250`
**Issue:** `/hatBeschriftung.*computed.*\.trim\(\)\s*!==\s*''/` relies on `.` not crossing newlines. It breaks as soon as Prettier wraps the `computed(() => …)` line. The first regex, `rahmenAttribute\([^)]*hatBeschriftung\.value[^)]*\)`, breaks as soon as a call with parentheses is added before `hatBeschriftung.value` in the argument list. The `D-14 Justification` comment says "nicht testbar ohne DOM", but WR-01 shows the logic can be extracted and tested without a DOM. Test titles and comments in `zustaende.test.ts` also mix English into German ("no role region", "no aria-labelledby").
**Fix:** Replace both regex tests with the pure-function unit test from WR-01. Keep the German wording in the titles.

### IN-02: `pruefeLinkMitZusatztaste` asserts the h1 focus before the code under test could have moved it

**File:** `app/e2e/menueDrawer.ts:98-106`
**Issue:** The bug being guarded against moves focus via `setTimeout(fokussiereUeberschrift)` after `wa-after-hide`. The `activeElement` check runs once, directly after the new page is closed, with no polling. It would pass before a delayed focus move. The regression is caught only indirectly, by the `aria-expanded === 'true'` assertion. Also, `tag` is read but never asserted.
**Fix:** Poll for a negative result over the close animation, or drop the redundant check and the unused `tag` field:
```ts
await page.waitForTimeout(0) // not wanted; prefer:
await expect.poll(() => page.evaluate(() => document.activeElement === document.querySelector('h1')), { timeout: 1000 }).toBe(false)
```
Since `expect.poll(...).toBe(false)` passes on the first try, the stronger form is to assert the dialog is still open after the drawer animation time (`toBeVisible` with `{ timeout }` after a short settle) and then check focus.

### IN-03: `_pruefe_jahrbezug` checks a paragraph as a set, not pair by pair; `Titel` is not covered

**File:** `pipeline/ostbevern/texte.py:581-617`, `pipeline/tests/test_texte.py:1042-1071`
**Issue:** The check passes whenever any `jahr.*` placeholder in the paragraph resolves to J. A paragraph with swapped labels, such as "Für {{jahr.vorjahr}} plant … {{x.2026}}, im Vorjahr ({{jahr.haushaltsjahr}}) … {{x.2025}}", is accepted, because both years appear somewhere. That is acceptable as a cheap guard, but the docstring ("dürfen nicht auseinanderlaufen") promises more than it enforces. The tests omit two cases: a paragraph that uses a year-suffixed key with no `jahr.*` placeholder at all (the strictest branch, currently raising), and a paragraph with two keys of different years where only one is labelled.
**Fix:** State the set-based semantics in the docstring. Add the two missing tests. If pairwise enforcement is wanted later, compare the placeholder order within a sentence.

---

_Reviewed: 2026-10-08_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
