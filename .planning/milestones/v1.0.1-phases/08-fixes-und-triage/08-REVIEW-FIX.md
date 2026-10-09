---
phase: 08-fixes-und-triage
fixed_at: 2026-10-08T07:20:00Z
review_path: .planning/phases/08-fixes-und-triage/08-REVIEW.md
iteration: 1
findings_in_scope: 3
fixed: 3
skipped: 0
status: all_fixed
---

# Phase 08: Code Review Fix Report

**Fixed at:** 2026-10-08
**Source review:** .planning/phases/08-fixes-und-triage/08-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 3
- Fixed: 3
- Skipped: 0

Scope was `critical_warning` (no Critical findings, three Warnings). The seven Info findings (IN-01 to IN-07) were out of scope.

**Verification environment:** Fixes were edited and committed in an isolated worktree, which was fast-forwarded into `main` and removed afterwards. The worktree has no `node_modules`, so the app checks (`type-check`, `lint`, `prettier`, `vitest`) ran in a scratch copy of `app/` with its own `npm ci` (`/tmp/claude-1000/.../scratchpad/wt/app`). They are not reproducible from the main checkout, whose `node_modules` holds macOS binaries. The pipeline checks (`ruff`, `pytest`, `alle.py`) ran inside the worktree.

## Fixed Issues

### WR-01: Year label and value key are now decoupled; a new Jahrgang silently produces wrong statements

**Status:** fixed: requires human verification (logic check)
**Files modified:** `pipeline/ostbevern/texte.py`, `pipeline/tests/test_texte.py`, `daten/manuell/texte/glossar.md`, `app/src/data/texte.json`
**Commit:** e8e25d5
**Applied fix:** Took the pipeline-check variant of the suggested fix. `loese_auf` now calls a new `_pruefe_jahrbezug` for every paragraph. It raises `TexteFehler` when a paragraph uses a value key with a fixed year suffix (e.g. `schulden.gesamt.2025`) but contains no `jahr.*` placeholder (relative or `jahr.fest_JJJJ`) that resolves to that year in the current Jahrgang. A 2027 Jahrgang would therefore fail at pipeline step 07 instead of publishing "Ende 2026 ... {{schulden.gesamt.2025}}". The check found one existing violation: the glossar paragraph for the Schlüsselzuweisung said "im Vorjahr waren es {{...2025}}" without labelling the year. It now reads "im Vorjahr ({{jahr.vorjahr|jahr}}) waren es ...". `texte.json` was regenerated with `alle.py`; only that paragraph changed. Three new tests cover rejection, acceptance with a matching relative label, and acceptance with `jahr.fest_JJJJ`. `ruff format`, `ruff check` and `pytest` (679 passed, 1 skipped for missing `typescript`) are green after regeneration.
**Limitation:** This is a pairing check at paragraph level. It does not tie each value to its own label inside a paragraph that mentions several years. The review's alternative, fully relative value keys such as `schulden.gesamt.vorjahr`, was not implemented because it is a broader data-model change.

### WR-02: Drawer link click sets the "closes by navigation" flag even when no navigation happens

**Files modified:** `app/src/App.vue`
**Commit:** 13eb786
**Applied fix:** `beiDrawerLinkKlick` now takes the `MouseEvent`. It returns early for Ctrl/Cmd/Shift/Alt clicks and non-primary buttons, and when the drawer is no longer open (a second click during the close animation). `oeffneDrawer` resets `schliesstDurchSeitenwechsel`, so a stale flag cannot leak into the next drawer session. `vue-tsc`, `eslint`, `prettier --check` and `vitest` (49 files, 2153 tests) pass in the scratch copy. The Playwright e2e tests for the drawer were not run.

### WR-03: `DatenTabelle` accepts an empty `beschriftung`, producing an unnamed scroll region with no guard left

**Files modified:** `app/src/components/DatenTabelle.vue`
**Commit:** 98803c4
**Applied fix:** A new computed `hatBeschriftung` (`beschriftung.trim() !== ''`) is included in the condition passed to `rahmenAttribute`. A blank name no longer yields `role="region"`, `tabindex` or `aria-labelledby` on the scroll frame. A `watchEffect` guarded by `import.meta.env.DEV` logs a `console.warn` for a blank `beschriftung`. `vue-tsc`, `eslint`, `prettier` and `vitest` pass in the scratch copy.

## Skipped Issues

None.

---

_Fixed: 2026-10-08_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
