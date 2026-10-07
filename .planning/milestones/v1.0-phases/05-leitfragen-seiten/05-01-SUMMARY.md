---
phase: 05-leitfragen-seiten
plan: 01
subsystem: testing
tags: [vitest, vite, typescript, intl, format, ci]

requires:
  - phase: 04-manuelle-daten-und-app-daten
    provides: "app/src/charts/format.ts with formatiere(), Python port test_formatiere.py, review items WR-06/IN-01"
provides:
  - "vitest 5.0.3 test runner for the app (npm run test, environment node, alias @/)"
  - "tsconfig.vitest.json: type-check scope for src/**/__tests__"
  - "formatiere() with visible dash fallback (KEIN_WERT) and exhaustive Formatkuerzel guard"
  - "Python mirror formatiere_port with the same fallback/ValueError, node cross-check incl. null inputs"
  - "CI step Tests (vitest) and CLAUDE.md command entry"
affects: [05-02, 05-03, 05-04, 05-05, 05-06, 05-07, 05-08, 05-09, 05-10, 05-11, 05-12, 05-13, 05-14, 05-15]

actuals:
  tokens: 7000
  tasks: 3
  commits: 3
plan_head_before: b35812ee68903990dadca3e55bbb1501490164b0
plan_head_after: 65cd6d8954aac57a99bdf835e124e7f9c59fa19c

tech-stack:
  added: [vitest 5.0.3 (devDependency, exact pin)]
  patterns:
    - "Pure logic in app/src/**, tests in app/src/**/__tests__/*.test.ts, imports from 'vitest' (no globals), environment node"
    - "vitest.config.ts = mergeConfig(vite.config.ts, test block); test files type-checked via tsconfig.vitest.json"
    - "Missing number = KEIN_WERT ('–'), never 0/NaN/undefined; unknown format code throws"

key-files:
  created:
    - app/vitest.config.ts
    - app/tsconfig.vitest.json
    - app/src/charts/__tests__/format.test.ts
  modified:
    - app/package.json
    - app/package-lock.json
    - app/tsconfig.json
    - app/src/charts/format.ts
    - pipeline/tests/test_formatiere.py
    - .github/workflows/ci.yml
    - .claude/CLAUDE.md

key-decisions:
  - "vitest 5.0.3 installed with the sandbox npm 9.2.0; the approved npm 10.9.2 fallback installer was not needed"
  - "A real-data pair that renders as the dash is a violation in _verstoesse (texte.json values must never be missing); fallback is only expected for explicit None/NaN/inf inputs"
  - "RED/GREEN committed separately (test then feat) as the TDD protocol requires, instead of one commit for Task 3's five files"

patterns-established:
  - "Test-first for pure functions: failing vitest + pytest commit, then implementation commit"
  - "npm work only in a scratch copy of app/ (tar excluding node_modules), copy back package.json/package-lock.json"

requirements-completed: [UI-05]

coverage:
  - id: D1
    description: "vitest 5.0.3 installed (exact pin) after the blocking-human legitimacy checkpoint; npm run test runs the suites in CI-identical fashion from a clean npm ci"
    requirement: UI-05
    verification:
      - kind: integration
        ref: "scratch copy: npm ci && type-check && lint && format:check && test && build (all exit 0)"
        status: pass
    human_judgment: false
  - id: D2
    description: "formatiere() shows '–' for null/undefined/NaN/+-Infinity and throws for an unknown Formatkuerzel; existing outputs unchanged"
    requirement: UI-05
    verification:
      - kind: unit
        ref: "app/src/charts/__tests__/format.test.ts#formatiere: sichtbarer Fallback (UI-05, WR-06/IN-01)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Python port mirrors both behaviours and the node cross-check agrees on null inputs"
    requirement: UI-05
    verification:
      - kind: unit
        ref: "pipeline/tests/test_formatiere.py#test_port_fallback_fuer_fehlende_werte, test_port_unbekanntes_kuerzel_wirft_value_error, test_verstoesse_meldet_fehlenden_rohwert"
        status: pass
      - kind: integration
        ref: "pipeline/tests/test_formatiere.py#test_port_wie_format_ts (ran, not skipped; node_modules from a Linux scratch copy)"
        status: pass
    human_judgment: false
  - id: D4
    description: "CI app job runs 'Tests (vitest)' between Prettier and Build; CLAUDE.md lists the test command"
    requirement: UI-05
    verification:
      - kind: other
        ref: "grep -q 'npm run test' .github/workflows/ci.yml; grep -q 'npm --prefix app run test' .claude/CLAUDE.md"
        status: pass
    human_judgment: true
    rationale: "The CI workflow itself cannot run before a GitHub remote exists (D-18); a human sees it green on the first push"

duration: 40min
completed: 2026-10-04
status: complete
---

# Phase 5 Plan 01: Test runner and formatiere fallback Summary

**vitest 5.0.3 (human-approved, exact pin) as the app's test runner with a first format.ts suite, and formatiere() hardened so a missing number renders as "–" and an unknown format code throws (WR-06/IN-01), mirrored in the Python port and the node cross-check.**

## Performance

- **Duration:** ~40 min (after the Task-1 checkpoint answer)
- **Completed:** 2026-10-04
- **Tasks:** 3 (Task 1 checkpoint approved by the user; Task 2 tracer; Task 3 TDD)
- **Files modified:** 10 (3 created, 7 modified)

## Task-1 user reply (verbatim, acceptance criterion)

- Selected option: "Freigegeben + npm 10.9.2"
- Resume signal it stands for: "vitest 5.0.3 freigegeben + npm 10.9.2 als Installationshilfe freigegeben"
- Answered: 2026-10-04, via the orchestrator's checkpoint question.

The reply contains "freigegeben". The npm 10.9.2 fallback was **not used**: the sandbox npm 9.2.0 installed vitest 5.0.3 without the Arborist `edgesOut` crash, so nothing beyond vitest 5.0.3 and its transitive dependencies entered the lockfile.

## Accomplishments

- vitest 5.0.3 pinned exactly in `devDependencies`; `npm run test` (`vitest run`, environment node, include `src/**/__tests__/*.test.ts`, alias `@/` via merged `vite.config.ts`).
- `tsconfig.vitest.json` (extends tsconfig.app.json, types node) referenced from `tsconfig.json`; `vue-tsc --build` now type-checks test files (`node_modules/.tmp/tsconfig.vitest.tsbuildinfo` produced).
- `formatiere(wert: number | null | undefined, kuerzel)` returns `KEIN_WERT` ("–") for null/undefined/NaN/Infinity/-Infinity and throws `Error("Unbekanntes Formatkürzel: …")` for an unknown code (exhaustive `never` default). `format.ts` stays import-free; `FormatKuerzel` stays on one line (test_texte regex still passes).
- Python `formatiere_port` mirrors both (None/NaN/inf -> "–", unknown code -> ValueError); `_verstoesse` treats a dash-rendered real-data pair as a violation; `test_port_wie_format_ts` now sends `(None, "euro")` and `(None, "mio")` and both sides return "–".
- CI app job: step "Tests (vitest)" (`npm run test`) between Prettier and Build; CLAUDE.md "Befehle" lists `npm --prefix app run test` and the local CI replay includes `npm run test`.

## Task Commits

1. **Task 1: Paketprüfung vitest 5.0.3** - no commit (checkpoint, approved by the user)
2. **Task 2: Tracer vitest end-to-end** - `ed9798c` (chore) - six files exactly: package.json, package-lock.json, vitest.config.ts, tsconfig.vitest.json, tsconfig.json, format.test.ts
3. **Task 3 RED: failing tests for fallback and guard** - `18bd2a4` (test)
4. **Task 3 GREEN: formatiere fallback, port, CI, CLAUDE.md** - `65cd6d8` (feat)

**Plan metadata:** committed with this SUMMARY (docs).

## Files Created/Modified

- `app/vitest.config.ts` - mergeConfig(viteConfig, test block: node, include pattern)
- `app/tsconfig.vitest.json` - type-check scope for `src/**/__tests__`
- `app/tsconfig.json` - reference to tsconfig.vitest.json
- `app/package.json` / `app/package-lock.json` - vitest 5.0.3, script `test`
- `app/src/charts/__tests__/format.test.ts` - 14 tests (euro, euroKurz, jahr, formatiere, fallback, guard)
- `app/src/charts/format.ts` - `KEIN_WERT`, fallback, exhaustive guard, TSDoc
- `pipeline/tests/test_formatiere.py` - port fallback/ValueError, new tests, null pairs in the node cross-check
- `.github/workflows/ci.yml`, `.claude/CLAUDE.md` - test step / command

## package-lock.json diff (T-05-SC)

Added packages (18 `node_modules/` entries, all `dev: true`, none with an install script; the only `hasInstallScript` in the lockfile is the pre-existing optional `fsevents`):
`vitest` 5.0.3, `@vitest/mocker` 5.0.3, `@vitest/spy` 5.0.3, `@types/chai` 5.2.3, `@types/deep-eql` 4.0.2, `assertion-error` 2.0.1, `chai` 6.3.0, `es-module-lexer` 2.3.2, `expect-type` 1.4.0, `obug` 2.2.1, `std-env` 4.3.0, `tinybench` 6.2.0, `tinyexec` 1.3.1, `why-is-node-running`, plus nested `@vitest/mocker/node_modules/{estree-walker 3.0.3, magic-string 1.4.2}` and `vitest/node_modules/{magic-string, picomatch}`.

Besides the additions npm 9.2.0 also synchronised three stale root-entry lines of the lockfile with `package.json`: `"name": "app"` -> `"ostbevern-money-app"` (top level and `packages[""]`) and `engines.node` `"^22.18.0 || >=24.12.0"` -> `"^22.18.0"`. No other existing package entry changed (3 removed lines in total, all of these).

## Decisions Made

- Used the sandbox npm 9.2.0 (worked); npm 10.9.2 fallback unused and not added anywhere.
- A dash rendering of a real-data (texte.json / erklaerungen) pair is reported as a violation by `_verstoesse`: real data must never hit the fallback, only an explicit None/NaN/inf input may.
- TDD RED and GREEN as separate commits (the plan listed one commit for five files; the TDD protocol and the plan's own "see them fail" step require the split). The five Task-3 files are all covered (format.test.ts and test_formatiere.py in RED, the rest in GREEN).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking/consistency] Lockfile root metadata resynced by npm**
- **Found during:** Task 2
- **Issue:** `npm install -D vitest@5.0.3` rewrote the root `name` and `engines.node` lines of package-lock.json to match package.json (stale since Phase 1).
- **Fix:** Kept npm's output (copy back of the untouched file is what the plan prescribes); documented above.
- **Files modified:** app/package-lock.json
- **Verification:** `npm ci` from the committed lockfile succeeds in a fresh scratch copy.
- **Committed in:** ed9798c

**2. [Plan interpretation] Task 3 committed as RED + GREEN**
- **Found during:** Task 3 (tdd="true")
- **Issue:** Plan text says "commit the five files"; the TDD gate requires a failing-test commit before the implementation.
- **Fix:** `18bd2a4` (test) then `65cd6d8` (feat).
- **Committed in:** 18bd2a4, 65cd6d8

---

**Total deviations:** 1 auto-fixed (Rule 3), 1 interpretation note. **Impact:** none on scope or outcomes.

## TDD Gate Compliance

- **RED** `18bd2a4`: 6 new vitest cases failed on assertions (null/undefined/NaN/Infinity/-Infinity returned "0 €"-style strings or "NaN", unknown code did not throw); 8 pytest cases failed (TypeError for None in the port, KeyError instead of ValueError, `_verstoesse` crash, node cross-check failing on the None pair). Note: the Python failures are TypeError/KeyError of the not-yet-implemented behaviour, not assertion mismatches; each failing test is exactly a newly added target test. `gsd check tdd-red-evidence` was not run (no record file persisted).
- **GREEN** `65cd6d8`: all pass (vitest 14/14, pytest full suite 479 passed, 0 skipped).
- **REFACTOR:** none needed.

## Verification

- Scratch copy (`tar` excluding node_modules/dist, fresh `npm ci`): `type-check`, `lint`, `format:check`, `test` (14 passed), `build` all exit 0.
- `uv run --directory pipeline pytest tests/test_formatiere.py tests/test_texte.py` 57 passed; full pipeline suite 479 passed; `ruff check .` and `ruff format --check .` clean.
- **Node cross-check ran (not skipped):** `test_port_wie_format_ts` was run with the worktree's `app/node_modules` temporarily symlinked to the Linux scratch copy's `node_modules` (symlink removed again, nothing committed); the whole suite reported 479 passed with `-rs` showing no skips.
- Acceptance greps (KEIN_WERT export, 0 imports in format.ts, one `FormatKuerzel` line, `npm run test` in ci.yml, command in CLAUDE.md, `pytest -k port` 19 passed) all pass.
- Task-2 commit file list is exactly the six task files.

## Issues Encountered

- `npm install` printed EBADENGINE warnings (e.g. `which@7.0.0`, `read-package-json-fast@6.0.0` require node `^22.22.2 || ^24.15.0 || >=26.0.0`, the sandbox has node 22.22.1 and npm 9.2.0); warnings only, all commands pass. `app/.nvmrc` is `22`, so CI resolves the latest 22.x. `package.json` `engines.node` stays `^22.18.0`, unchanged.
- Tracer gate: vitest verify chain re-run end-to-end after Task 2 (passed) before expansion in Task 3.

## Known Stubs

None.

## Threat Flags

None. (T-05-01 mitigated by tests on TS and Python side; T-05-SC mitigated by the human gate, exact pin, devDependency only, scratch-copy install, lock diff above.)

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plans 05-02 onward can add `app/src/**/__tests__/*.test.ts` and run `npm --prefix app run test` (scratch copy in this sandbox).
- The orchestrator's post-merge gate should run `uv run --directory pipeline pytest tests/test_formatiere.py` against a checkout with installed `app/node_modules`.

## Self-Check: PASSED

- Created files exist: app/vitest.config.ts, app/tsconfig.vitest.json, app/src/charts/__tests__/format.test.ts.
- Commits exist: ed9798c, 18bd2a4, 65cd6d8 on branch worktree-agent-a7268c07ad37c44a7.

---
*Phase: 05-leitfragen-seiten*
*Completed: 2026-10-04*
