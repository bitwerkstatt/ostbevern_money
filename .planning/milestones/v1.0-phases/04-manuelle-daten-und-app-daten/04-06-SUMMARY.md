---
phase: 04-manuelle-daten-und-app-daten
plan: 06
subsystem: data
tags: [formatting, intl, decimal, typescript-python-crosscheck, tdd, erklaertexte]

# Dependency graph
requires:
  - phase: 04-05
    provides: texte.json (D-17-approved Erklärtexte), erklaerungen.md, Schritt 07
provides:
  - "jahr" Formatkürzel in app/src/charts/format.ts (FormatKuerzel, formatiere()) and
    pipeline/ostbevern/texte.py (FORMATKUERZEL), kept in sync by test_formatkuerzel_wie_format_ts
  - Corrected erklaerungen.md/texte.json: all ten Haushaltsjahr placeholders render as a bare
    four-digit year instead of grouped ("2026" not "2.026", CR-01)
  - pipeline/tests/test_formatiere.py: a Python port of formatiere() that mechanically renders
    every (Rohwert, Formatkürzel) pair used by erklaerungen.md and texte.json, with a CR-01
    mutation test and an optional Node cross-check against the real format.ts
  - CR-01 recorded as fixed in 04-REVIEW-DISPOSITION.md
affects: [05-vue-app-grundgeruest, 06-seiten-und-visualisierungen]

# Actuals (#2632)
actuals:
  tokens: 12603
  tasks: 2
  commits: 3
  plan_head_before: e34d5a44aaf27f8af1c76d9034b1feb7b9027a91
  plan_head_after: 5e3292ed3a7190769a83f459b9fd0b0552ff47de

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Python Decimal-based port of Intl.NumberFormat('de-DE', ...) for a specific, enumerated set
      of options objects (maximumFractionDigits XOR maximumSignificantDigits, grouping on/off),
      used only inside pytest to mechanically verify citizen-facing number rendering without a
      JS runtime dependency in CI."
    - "Node subprocess cross-check (no shell, argument list only) that transpiles the app's own
      format.ts with the app's own node_modules/typescript devDependency and compares against the
      Python port — runs wherever Node + app/node_modules/typescript exist, skips with a named
      reason otherwise (e.g. the CI pipeline job, which sets up no Node)."

key-files:
  created:
    - pipeline/tests/test_formatiere.py
  modified:
    - app/src/charts/format.ts
    - pipeline/ostbevern/texte.py
    - daten/manuell/texte/erklaerungen.md
    - daten/manuell/README.md
    - app/src/data/texte.json
    - .planning/phases/04-manuelle-daten-und-app-daten/04-REVIEW-DISPOSITION.md

key-decisions:
  - "'jahr' placed directly after 'zahl' in both FormatKuerzel (TS) and FORMATKUERZEL (Python),
    same order, so the existing order-sensitive test_formatkuerzel_wie_format_ts stays the single
    sync check between the two languages (no new contract test needed)."
  - "The formatiere() Python port lives only in pipeline/tests/test_formatiere.py, never in
    pipeline/ostbevern/ — the pipeline never formats (D-15); the port exists purely as a test
    oracle."
  - "TDD RED/GREEN executed as two separate commits (test(04-06) then feat(04-06)) rather than
    the single test(04-06) commit the plan's action text suggested, to follow the canonical
    RED→GREEN commit-scope contract (tdd.md) the executor instructions require verbatim. No
    content difference — same final diff, just split so the RED (intentionally failing) state is
    independently inspectable in history."
  - "REQUIREMENTS.md is not touched by this worktree executor (MANU-08, DATA-01, PRUEF-10 marking
    is deferred to the orchestrator's centralized post-wave update), matching how STATE.md and
    ROADMAP.md are excluded in worktree mode — all three are shared, cross-plan bookkeeping files
    that multiple wave agents could touch concurrently."

patterns-established:
  - "Cross-language format verification: when a value is formatted in TypeScript for citizens and
    must also be checked in the Python test suite, port the formatter into pytest (never into the
    pipeline) and, where a JS runtime is available, cross-check the port against the real
    TypeScript source via a transpile-and-import subprocess rather than hand-copying examples."

requirements-completed: [MANU-08, DATA-01, PRUEF-10]

coverage:
  - id: D1
    description: "Ungrouped 'jahr' Formatkürzel added to format.ts and FORMATKUERZEL; all ten
      Haushaltsjahr placeholders in erklaerungen.md/texte.json switched to it; wording stays
      byte-identical to the D-17-approved 04-05 state"
    requirement: "MANU-08"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_texte.py#test_formatkuerzel_wie_format_ts"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_app_daten.py -k texte_json"
        status: pass
      - kind: integration
        ref: "scratch-copy app build: type-check, lint, format:check, build + real formatiere() render of all ten jahr.* placeholders"
        status: pass
    human_judgment: false
  - id: D2
    description: "Python port of formatiere() (pipeline/tests/test_formatiere.py) mechanically
      renders every placeholder of erklaerungen.md and texte.json; CR-01 mutation test proves a
      regression (grouped Haushaltsjahr) is caught; optional Node cross-check against the real
      format.ts"
    requirement: "PRUEF-10"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_formatiere.py#test_port_beispiele"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_formatiere.py#test_erklaerungen_rendern_korrekt"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_formatiere.py#test_texte_json_rendert_korrekt"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_formatiere.py#test_cr01_gruppiertes_haushaltsjahr_wird_erkannt"
        status: pass
      - kind: integration
        ref: "pipeline/tests/test_formatiere.py#test_port_wie_format_ts"
        status: pass
    human_judgment: false
  - id: D3
    description: "Full reproducibility gate stays green after the change: full pytest suite, ruff
      check/format, alle.py regeneration with a clean git diff and no untracked files under
      daten/ and app/src/data"
    requirement: "DATA-01"
    verification:
      - kind: integration
        ref: "uv run --directory pipeline pytest -q (471 passed, 1 skipped)"
        status: pass
      - kind: other
        ref: "uv run --directory pipeline ruff check . && ruff format --check ."
        status: pass
      - kind: integration
        ref: "uv run --directory pipeline python alle.py --jahr 2026 && git diff --stat --exit-code -- daten app/src/data"
        status: pass
    human_judgment: false

# Metrics
duration: 35min
completed: 2026-10-04
status: complete
---

# Phase 04 Plan 06: Formatkürzel "jahr" und formatiere()-Rendertest Summary

**Added an ungrouped "jahr" format kürzel to format.ts/texte.py and a Python port of formatiere() in pytest that mechanically proves every Erklärtext number — including all ten Haushaltsjahr placeholders — renders correctly, closing CR-01.**

## Performance

- **Duration:** 35 min
- **Started:** 2026-10-04T08:05:00Z
- **Completed:** 2026-10-04T08:22:23Z
- **Tasks:** 2 completed
- **Files modified:** 7 (1 created, 6 modified)

## Accomplishments

- `formatiere(wert, 'jahr')` in `app/src/charts/format.ts` now renders a year without thousands
  separator ("2026"), while `zahl()` stays grouped for counts like Einwohner ("11.741") — the
  CR-01 defect (Haushaltsjahr rendering as "2.026") is fixed.
- `FormatKuerzel` (TS) and `FORMATKUERZEL` (Python) both list `jahr` directly after `zahl`,
  keeping the existing order-sensitive `test_formatkuerzel_wie_format_ts` in sync.
- All ten Haushaltsjahr placeholders in `daten/manuell/texte/erklaerungen.md` carry the `jahr`
  kürzel; the approved D-17 wording stays byte-identical (verified by a suffix-normalized diff
  against the 04-05 base commit `f9e085d`).
- `app/src/data/texte.json` is regenerated via Schritt 07 and differs from the 04-05 base only in
  the same ten suffixes; `werte` stay raw numbers (the pipeline never formats, D-15).
- `pipeline/tests/test_formatiere.py` (new, 455 lines) ports `formatiere()` into Python
  (`_dezimal`, `_euro`, `_euro_kurz`, `_zahl`, `_jahr`, `_vzae`, `_prozent`, `formatiere_port`),
  renders every placeholder of `erklaerungen.md` and `texte.json` through it, proves the CR-01
  pattern is mechanically detected (`test_cr01_gruppiertes_haushaltsjahr_wird_erkannt`), and
  cross-checks the port against the real `format.ts` via a Node subprocess wherever Node and
  `app/node_modules/typescript` are available.
- The full pipeline test suite (471 tests), ruff, and the `alle.py` reproducibility gate stay
  green after the change; CR-01 is recorded as `fixed` in `04-REVIEW-DISPOSITION.md` while
  WR-01, WR-02, WR-03 and IN-01 remain `open` (out of scope by user decision).

## Task Commits

Each task was committed atomically; Task 2 (`tdd="true"`) produced two commits following the
canonical RED→GREEN commit-scope contract:

1. **Task 1: Formatkürzel jahr end-to-end — format.ts, FORMATKUERZEL, zehn Platzhalter,
   texte.json (CR-01)** — `52b3d3b` (fix)
2. **Task 2 RED: add failing test for Erklärtexte-Rendering via formatiere-Portierung** —
   `9a2af1b` (test)
3. **Task 2 GREEN: implement formatiere-Portierung für Erklärtext-Rendering (CR-01 behoben)** —
   `5e3292e` (feat)

_Note: the plan's action text suggested a single `test(04-06)` commit for Task 2; the executor's
TDD instructions require the canonical two-commit RED→GREEN split instead — see Deviations._

## Files Created/Modified

- `app/src/charts/format.ts` — `JAHR_FORMAT` constant, `jahr()` function, `'jahr'` added to
  `FormatKuerzel` and to the `formatiere()` switch
- `pipeline/ostbevern/texte.py` — `'jahr'` added to `FORMATKUERZEL` (same position as the TS union)
- `daten/manuell/texte/erklaerungen.md` — ten `{{jahr.haushaltsjahr|zahl}}` →
  `{{jahr.haushaltsjahr|jahr}}` (suffix only, wording unchanged)
- `daten/manuell/README.md` — format kürzel vocabulary sentence extended with `jahr`
- `app/src/data/texte.json` — regenerated via Schritt 07 with the corrected placeholders
- `pipeline/tests/test_formatiere.py` — new: Python port of `formatiere()` plus the six behavior
  tests (RED stub → GREEN implementation)
- `.planning/phases/04-manuelle-daten-und-app-daten/04-REVIEW-DISPOSITION.md` — CR-01 row set to
  `fixed`

## Decisions Made

- `jahr` kürzel placed directly after `zahl` in both languages, in the same order, so the existing
  `test_formatkuerzel_wie_format_ts` stays the single sync check (no new contract test needed).
- The Python port of `formatiere()` lives only in `pipeline/tests/test_formatiere.py` — never in
  `pipeline/ostbevern/` — because the pipeline never formats (D-15); it exists purely as a test
  oracle to mechanically catch a regression like CR-01.
- TDD RED/GREEN executed as two separate commits rather than the plan's suggested single commit
  (see Deviations below).
- `REQUIREMENTS.md` was deliberately **not** updated by this worktree executor; marking MANU-08,
  DATA-01 and PRUEF-10 complete is deferred to the orchestrator's centralized post-wave update
  (same treatment as STATE.md/ROADMAP.md — all three are shared, cross-plan bookkeeping files).

## Deviations from Plan

### Auto-fixed Issues

**1. [Process — TDD commit granularity] Split Task 2's single suggested commit into RED+GREEN**
- **Found during:** Task 2 (formatiere-Portierung, `tdd="true"`)
- **Issue:** The plan's action text (step 7) suggested committing the finished test file and the
  disposition-ledger update together as one `test(04-06): ...` commit. The executor's TDD
  instructions (canonical `tdd.md` reference) require the RED→GREEN commit-scope contract
  (`test({phase}-{plan})` for the intentionally-failing state, `feat({phase}-{plan})` for the
  passing implementation) to be followed "exactly ... do not improvise a variant."
- **Fix:** Committed the stubbed, intentionally-failing test file first (`test(04-06): add failing
  test for Erklärtexte-Rendering via formatiere-Portierung (RED)`, verified to fail for the right
  reason — `NotImplementedError` / a false `_PORT` assertion, 15 failed + 1 skipped), then restored
  the full implementation and committed it together with the `04-REVIEW-DISPOSITION.md` update
  (`feat(04-06): implement formatiere-Portierung für Erklärtext-Rendering (CR-01 behoben)`,
  verified green — 15 passed + 1 skipped without the Node cross-check available, 16 passed with it
  temporarily enabled via a gitignored symlink per the dispatch's environment notes).
- **Files modified:** `pipeline/tests/test_formatiere.py` (both commits),
  `.planning/phases/04-manuelle-daten-und-app-daten/04-REVIEW-DISPOSITION.md` (GREEN commit only)
- **Verification:** RED run showed 15 failed/1 skipped before implementation; GREEN run showed 15
  passed/1 skipped (16 passed/0 skipped with the temporary Node cross-check symlink); final
  diff-tree of HEAD after the GREEN commit holds exactly the two files the plan's acceptance
  criterion names.
- **Committed in:** `9a2af1b` (RED), `5e3292e` (GREEN)

---

**Total deviations:** 1 (process/commit-granularity only — no content, scope, or behavior change
from the plan).
**Impact on plan:** None on the delivered artifacts; the final tree state and every acceptance
criterion match the plan exactly. The only difference from the plan's literal instruction is that
the RED state is independently visible in git history as its own commit.

## Issues Encountered

None. The Node cross-check (`test_port_wie_format_ts`) correctly skips in this worktree by default
(`app/node_modules/typescript/package.json` is absent, as expected — the worktree has no
`app/node_modules` at all). Per the dispatch's environment notes, it was exercised once via a
temporary, gitignored symlink (`app/node_modules -> <main-checkout>/app/node_modules`), confirmed
to pass (port output byte-identical to the real `formatiere()` for all 31 pairs: 11 examples + 9
edge pairs + 11 distinct `texte.json` placeholder pairs minus 1 overlap), and the symlink was
removed again before the final reproducibility gate and before writing this summary — `app/`
is clean (`git status --short -- app` reports nothing).

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- The single verification gap recorded in `04-VERIFICATION.md` (CR-01) is closed; MANU-08, DATA-01
  and PRUEF-10 are fully satisfied for Phase 4's scope. WR-01, WR-02, WR-03 and IN-01 remain
  intentionally `open` in `04-REVIEW-DISPOSITION.md` (user decision 2026-10-03, out of scope for
  this plan).
- `app/src/data/texte.json` now carries the corrected `jahr` placeholders for Phase 5/6 to render;
  no further pipeline-side work is needed for the Erklärtexte's year formatting.
- **Orchestrator follow-up:** mark `MANU-08`, `DATA-01`, `PRUEF-10` complete in
  `REQUIREMENTS.md` and update `STATE.md`/`ROADMAP.md` centrally after this worktree merges (not
  done here per worktree-mode convention).

## Self-Check: PASSED

All eight files (five modified sources, the new test file, the disposition ledger, and this
summary) verified present on disk with `[ -f ]`. All four commits (`52b3d3b` fix, `9a2af1b` test
RED, `5e3292e` feat GREEN, `b799e99` docs summary) verified present via `git log --oneline --all`.

---
*Phase: 04-manuelle-daten-und-app-daten*
*Completed: 2026-10-04*
