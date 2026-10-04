---
phase: 05-leitfragen-seiten
fixed_at: 2026-10-04T23:20:00Z
review_path: .planning/phases/05-leitfragen-seiten/05-REVIEW.md
iteration: 1
findings_in_scope: 7
fixed: 7
skipped: 0
status: all_fixed
---

# Phase 5: Code Review Fix Report

**Fixed at:** 2026-10-04T23:20:00Z
**Source review:** .planning/phases/05-leitfragen-seiten/05-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 7 (0 Critical, 7 Warning; Info excluded by `fix_scope: critical_warning`)
- Fixed: 7
- Skipped: 0

**Verification environment:** The fixes ran in an isolated git worktree under `.claude/worktrees/`. The worktree has no `node_modules` of its own. The app gates (`type-check`, `lint`, `format:check`, `test`, `build`) therefore ran against the dependency set in the scratchpad copy, because the main checkout's `app/node_modules` has no `vitest`. The gates are not reproducible from the main checkout until `npm --prefix app ci` has been run there. After the final fix, the app gates were green: 23 test files with 1013 tests passed, and lint, type-check, prettier and build were clean. On the pipeline side, `ruff check` and `ruff format --check` were clean. These pipeline tests passed: `test_texte.py`, `test_formatiere.py`, `test_app_daten.py`, and the `-k regel5` selection of `test_pruefung.py`. The complete `tests/test_pruefung.py` was not run to completion, because it is very slow (over 10 minutes at about 400 % CPU) and was stopped. CI runs it in full.

No pipeline change altered generated data (`texte.json` only carries used values), so no regeneration of `daten/` or `app/src/data/` was needed.

## Fixed Issues

### WR-01: Geldfluss shows Vorbericht-derived amounts as exact euros, without "rd." or "berechnet"

**Files modified:** `app/src/lib/geldfluss.ts`, `app/src/pages/GeldflussPage.vue`, `app/src/components/GeldflussBalken.vue`, `app/src/lib/__tests__/geldfluss.test.ts`
**Commit:** 0c8204c
**Applied fix:** Added `gerundet` and `berechnet` to `GeldflussKnoten`, `GeldflussZeile` and `BalkenSegment`. The `gerundet` flag is derived from the Vorbericht posten (`postenGerundet`), not hard-coded. Gewerbesteuer, Einkommensteuer, Grundsteuer and Schlüsselzuweisung are `gerundet`. "Übrige Steuern" and "Sonstige Zuwendungen" are `gerundet` and `berechnet`. New exported helper `betragMitHinweis` prefixes "rd." and is used in the node, edge and mobile-bar tooltips and in the Sankey labels. The Woher/Wohin tables and the mobile legend tables show "rd." and the `BerechnetEtikett`. Five new tests cover the flags, the tooltip and the segments.

### WR-02: Start page says "Den größten Anteil bekommt Innere Verwaltung", but Weitergabe an Kreis und Land is more than twice as large

**Files modified:** `app/src/pages/StartPage.vue`
**Commit:** d5206e1
**Applied fix:** Reworded the tile to "Ohne die Weitergabe an Kreis und Land bekommt {Name} den größten Anteil: {Betrag}." The wording is a copy decision. The UI-SPEC and VERIFICATION still quote the old sentence, and the Phase-7 text pass should confirm the new wording.

### WR-03: `mitDeckkraft` silently ignores every non-hex colour, so the decal opacity from the design never applies

**Files modified:** `app/src/charts/echartsTheme.ts`, `app/src/charts/__tests__/farben.test.ts`
**Commit:** 87d845a
**Applied fix:** `mitDeckkraft` is now exported. It converts hex directly. It resolves any other CSS colour (such as the keyword `white`) to RGB through a 1x1 canvas (`alsRgb`). If no resolution is possible, it falls back to `color-mix(in srgb, <farbe> N%, transparent)`, so the opacity is never silently dropped. Three tests cover hex, the stubbed canvas path with `white`, and the fallback. Whether the stripes and dots now look right in a real browser has not been checked visually. The change is code-verified only.

### WR-04: `lies_erklaerungen` / `lies_glossar` silently drop page ranges in `Quelle:` lines

**Files modified:** `pipeline/ostbevern/texte.py`, `pipeline/tests/test_texte.py`
**Commit:** e3a2122
**Applied fix:** Took the review's second option. A `Quelle:` line with a page range (`S. 309-311`, `S. 24/25`, including an en dash) now raises `TexteFehler` ("Seitenspannen in der Quelle sind nicht erlaubt, jede Seite einzeln auflisten"). The checked-in `.md` files contain no ranges. A parametrised test covers the rejection.

### WR-05: Konzessionsabgaben check is silently skipped when `meta` is absent; Regel 5 then reports a clean pass

**Files modified:** `pipeline/ostbevern/pruefung.py`, `pipeline/tests/test_pruefung.py`
**Commit:** 32dc5d1
**Applied fix:** The `sonstige_ertraege` branch no longer requires `meta is not None` to run. If `meta` is missing, it raises `PruefungsFehler`. The docstring is updated, and a new test calls `_pruefe_regel5` without `meta`.

### WR-06: Fixed-year shape in `texte.py` formulas: KeyError instead of `TexteFehler`, and every formula runs even when unused

**Files modified:** `pipeline/ostbevern/texte.py`, `pipeline/ostbevern/app_daten.py`, `pipeline/tests/test_texte.py`
**Commit:** 7587fd5
**Applied fix:** `textwerte` takes an optional `texte` argument. When given, only the `abgeleitet.*` formulas that a text references are evaluated. `app_daten` passes the Erklärtexte and the Glossar. A `KeyError` inside a formula becomes `TexteFehler("Formel '<name>': Eingabewert ... fehlt")`. Without `texte`, all formulas run as before, so existing callers and tests are unchanged. Two new tests cover the error conversion and the "unused formula is skipped" behaviour.

### WR-07: `DatenTabelle` makes every captioned table a tab stop and duplicates its name for screen readers

**Files modified:** `app/src/components/DatenTabelle.vue`
**Commit:** e1e1901
**Applied fix:** The wrapper gets `role="region"`, `aria-label` and `tabindex="0"` only while its content overflows horizontally. A `ResizeObserver` plus an initial `scrollWidth > clientWidth` check at mount decide this. Non-scrolling tables lose the extra tab stop and the doubled name. This differs slightly from the review's wording, which dropped `role` and `aria-label` altogether. A scrolling region needs a keyboard-reachable, named wrapper (the recommended pattern), so I kept them for that case. Status: fixed, requires human verification. The behaviour is a runtime layout check and was not exercised in a real browser. The existing vitest suite runs without a DOM and does not cover it.

---

_Fixed: 2026-10-04T23:20:00Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
