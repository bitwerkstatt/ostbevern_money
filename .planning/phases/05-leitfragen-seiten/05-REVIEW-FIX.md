---
phase: 05-leitfragen-seiten
fixed_at: 2026-10-05T07:25:00Z
review_path: .planning/phases/05-leitfragen-seiten/05-REVIEW.md
iteration: 1
findings_in_scope: 6
fixed: 6
skipped: 0
status: all_fixed
---

# Phase 5: Code Review Fix Report

**Fixed at:** 2026-10-05
**Source review:** .planning/phases/05-leitfragen-seiten/05-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 6 (WR-01, WR-02, IN-01 to IN-04; fix_scope `all`)
- Fixed: 6
- Skipped: 0

All fixes were made in an isolated git worktree and fast-forwarded onto `main`.

## Fixed Issues

### WR-01: `Quelle:` page lists without a repeated `S.` are silently truncated

**Files modified:** `pipeline/ostbevern/texte.py`, `pipeline/tests/test_texte.py`
**Commit:** 9d18267
**Applied fix:** Replaced the blacklist `_SEITENSPANNE_MUSTER` with a whole-line whitelist `_QUELLE_ERLAUBT_MUSTER` (`S. n` entries separated by `,` or `;`). Anything else raises `TexteFehler` ("Quelle muss 'S. n, S. m' sein"). A Quelle without any `S. n` still raises the existing "Quelle ohne Seitenzahl" error. The parametrised test now also covers `S. 24, 25`, `S. 309 bis 311`, `S. 309 f.`, em dash and minus sign. All checked-in text files still parse.

### WR-02: `DatenTabelle` overflow detection observes only the elements present at mount

**Files modified:** `app/src/components/DatenTabelle.vue`
**Commit:** fdef6a9
**Applied fix:** Extracted `beobachteInhalt()` (disconnect, re-observe `rahmen` and its children, re-check overflow). It runs on mount and, via `watch([laedt, istLeer, istDatenModus])` plus `nextTick`, on every change of the skeleton/empty/table branch. Requires human verification in a browser: the Vitest setup has no DOM, so the observer path is not covered by an automated test (see IN-02).

### IN-01: `alsRgb` turns an unparseable colour into black without a signal

**Files modified:** `app/src/charts/echartsTheme.ts`
**Commit:** 20b7fc2
**Applied fix:** Before assigning `farbe`, `fillStyle` is set to the marker `#010203`. If the marker is still there afterwards (the canvas rejected the colour) and `farbe` is not the marker itself, `alsRgb` returns `null`, so `mitDeckkraft` falls back to `color-mix` instead of producing black stripes. Browser-only code path, not covered by Vitest (no DOM); requires human verification: fixed, requires human verification.

### IN-02: Scroll region without `beschriftung` is never keyboard-focusable

**Files modified:** `app/src/components/DatenTabelle.vue`
**Commit:** 52491a7
**Applied fix:** `tabindex` is now bound to `ueberlaeuft` alone. `role="region"` and `aria-label` stay tied to `beschriftung` (an `aria-label` without a role would be invalid). The DOM test the review suggests was not added: neither `happy-dom`/`jsdom` nor `@vue/test-utils` is installed, and the vitest environment is `node`. Adding them means new dependencies, which I did not do inside a fix pass. The behaviour needs a manual or Lighthouse check.

### IN-03: Regel 5 still skips the Kreisumlage check silently when `meta` is `None`

**Files modified:** `pipeline/ostbevern/pruefung.py`, `pipeline/tests/test_pruefung.py`
**Commit:** 8a64bef
**Applied fix:** When `transferaufwendungen` is present and `meta` or `eckwerte` is `None`, `_pruefe_regel5` now raises `PruefungsFehler`, like the Konzessionsabgaben branch. The docstring is updated. A parametrised test covers both missing arguments. The production caller `pruefe_alles` always passes both, and the full pipeline suite stays green.

### IN-04: The "rd." / "berechnet" cell template is copy-pasted three times; the space after "rd." can wrap

**Files modified:** `app/src/components/EuroBetrag.vue` (new), `app/src/pages/GeldflussPage.vue`, `app/src/components/GeldflussBalken.vue`, `app/src/lib/geldfluss.ts`, `app/src/lib/__tests__/geldfluss.test.ts`
**Commit:** 58adf28
**Applied fix:** New component `EuroBetrag` (props `wert`, `gerundet`, `berechnet`) replaces the three copies; it renders `betragMitHinweis(...)` plus `BerechnetEtikett`. `geldfluss.ts` exports `RD_PRAEFIX = 'rd. '` (non-breaking space), used by `betragMitHinweis` and the Sankey node label. Unused `euro` imports were removed. Existing tests now use `RD_PRAEFIX`. A new test checks edge tooltips: Gewerbesteuer to Gemeinde contains the prefix, Gemeinde to KL does not. Scope note: `zeitreihen.ts` and `drilldown.ts` still build `rd. ` with a plain space; the finding named only the Geldfluss files, so I left them alone.

## Skipped Issues

None.

## Verification

Gates ran in the isolated worktree (with `app/node_modules` and `pipeline/.venv` symlinked from the main checkout side; the symlinks were removed before cleanup). The worktree was fast-forwarded into `main` and then removed, so the numbers are not reproducible from a leftover worktree, but they are from `main` at 58adf28.

- `uv run --directory pipeline ruff check .`: passed
- `uv run --directory pipeline ruff format --check .`: passed (46 files)
- `uv run --directory pipeline pytest`: 528 passed (320 s)
- `npm --prefix app run type-check`: passed
- `npm --prefix app run lint`: passed
- `npm --prefix app run format:check`: passed
- `npm --prefix app run test`: 23 files, 1015 tests passed

Note: `app/node_modules` in the main checkout has no `vitest`; the app checks used the installed copy from the scratchpad working directory.

---

_Fixed: 2026-10-05_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
