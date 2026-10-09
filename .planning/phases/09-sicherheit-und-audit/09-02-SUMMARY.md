---
phase: 09-sicherheit-und-audit
plan: 02
subsystem: ui
tags: [vue, a11y, wcag, vitest, playwright, review-ledger]

requires:
  - phase: 08-fixes-und-triage
    provides: DatenTabelle scroll frame guard (WR-03), review ledger 08, 08-VERIFICATION
provides:
  - "tabellenRahmen / ERSATZ_BESCHRIFTUNG: pure rule for caption text and scroll-frame attributes of DatenTabelle"
  - "Ledger 08-REVIEW-DISPOSITION.md on open: 0 (total 10)"
  - "08-VERIFICATION.md renewed after the D-20 code change (status passed, not stale)"
affects: [09-03 Basislauf, re-verifications of phases 5 to 7, audit]

actuals:
  tokens: 8146
  tasks: 2
  commits: 4

plan_head_before: 86c56dc24eb96193ca66031d67194f6472f8c196
plan_head_after: 14e973386f5d7a650e8f71bf8d7c95c8c5a8fa92

tech-stack:
  added: []
  patterns:
    - "Accessibility rule extracted into a pure function and tested at the function, not by source-text regex"

key-files:
  created: []
  modified:
    - app/src/components/datenTabelle.ts
    - app/src/components/DatenTabelle.vue
    - app/src/components/__tests__/zustaende.test.ts
    - app/src/lib/__tests__/quelltext.test.ts
    - .planning/phases/08-fixes-und-triage/08-REVIEW-DISPOSITION.md
    - .planning/phases/08-fixes-und-triage/08-VERIFICATION.md

key-decisions:
  - "A blank beschriftung falls back to the caption name „Tabelle“ instead of dropping tabindex and role, so keyboard access never depends on the caller (D-20, WCAG 2.1.1)"
  - "IN-01 recorded fixed because the WR-01 fix removed its subject; IN-02 to IN-07 deferred with a reason each"
  - "IN-05 deferred after checking every caller of quellenZeile: none can pass an empty page list with the shipped data"

patterns-established:
  - "Frame rule: tabellenRahmen(lage, captionId) returns { name, attribute }; beschriftung never gates the attributes"

requirements-completed: [AUD-01, AUD-03]

coverage:
  - id: D1
    description: "An overflowing DatenTabelle frame always carries tabindex 0, role region and aria-labelledby, with caption „Tabelle“ for a blank beschriftung"
    requirement: AUD-01
    verification:
      - kind: unit
        ref: "app/src/components/__tests__/zustaende.test.ts#tabellenRahmen (08/WR-01, 08/WR-02, A11Y-01)"
        status: pass
      - kind: unit
        ref: "app/src/components/__tests__/zustaende.test.ts#DatenTabelle Name und Rahmen (SSR fallback caption)"
        status: pass
      - kind: e2e
        ref: "scripts/e2e-wie-ci.sh app --project=mobil (Tabellenrahmen bei 360 px, 41 passed)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Ledger 08 stands at open: 0 with total 10, every row citing a commit or a reason"
    requirement: AUD-03
    verification:
      - kind: other
        ref: "grep and awk checks of 08-REVIEW-DISPOSITION.md (Task 2 automated command 1)"
        status: pass
    human_judgment: false
  - id: D3
    description: "08-VERIFICATION.md renewed with re_verification, fingerprint from verification.fingerprint, status passed"
    requirement: AUD-03
    verification:
      - kind: other
        ref: "gsd-tools query verification.status .planning/phases/08-fixes-und-triage --pick status prints passed"
        status: pass
    human_judgment: false

duration: 22min
completed: 2026-10-09
status: complete
---

# Phase 9 Plan 02: Tabellenrahmen-Regel, Ledger 08 und Re-Verifikation Summary

**Pure `tabellenRahmen` rule keeps every overflowing DatenTabelle frame focusable, role-bearing and named (blank `beschriftung` falls back to „Tabelle“), tests proven red first, ledger 08 on `open: 0`, 08-VERIFICATION renewed.**

## Performance

- **Duration:** 22 min
- **Started:** 2026-10-09T05:55:00Z
- **Completed:** 2026-10-09T06:08:00Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments

- 08/WR-02 closed: the scroll frame of an overflowing table no longer loses `tabindex`, `role` and `aria-labelledby` when `beschriftung` is empty or whitespace-only; the caption then reads „Tabelle“.
- 08/WR-01 closed: the rule lives in the pure function `tabellenRahmen` and is unit-tested (blank, whitespace, normal, no overflow, loading, empty state); the SSR test asserts the fallback caption. The two SSR tests that held with and without the old guard and the two source-text regex tests on it (08/IN-01) are removed.
- Ledger 08: WR-01, WR-02, IN-01 fixed with hashes, IN-02 to IN-07 deferred with a reason; `open: 0`, `total: 10`.
- 08-VERIFICATION renewed (D-15): `re_verification` with `gaps_closed` 08/WR-01 and 08/WR-02, `covered_files` and `covered_digest` copied from `verification.fingerprint`, `verification.status` prints `passed`.

## TDD Evidence

**RED** (commit `8b4ae20`, `test(09): 08/WR-01 ...`): 8 of 24 tests in `zustaende.test.ts` failed, 16 passed. Failing tests:

- `DatenTabelle Name und Rahmen ... > leere Beschriftung: die Caption trägt den Ersatznamen „Tabelle“` (empty caption)
- `... > aus Leerzeichen bestehende Beschriftung: die Caption trägt den Ersatznamen „Tabelle“` (empty caption)
- `tabellenRahmen ... > leere Beschriftung mit Überlauf: Rahmen bleibt erreichbar, Name ist „Tabelle“` (`TypeError: tabellenRahmen is not a function`)
- `tabellenRahmen ... > aus Leerzeichen bestehende Beschriftung mit Überlauf: wie die leere`
- `tabellenRahmen ... > normale Beschriftung mit Überlauf: der Name ist die gekürzte Beschriftung`
- `tabellenRahmen ... > ohne Überlauf / beim Laden / im Leerzustand: keine Attribute, für jede Beschriftung` (3 tests)

Machine check: the vitest TAP reporters (`tap`, `tap-flat`) were rejected by `gsd_run check tdd-red-evidence` as `invalid_record` (non-TAP data / malformed TAP in vitest's output). The same run through vitest's `junit` reporter, unchanged, returned `RED_EVIDENCE_OK` (`target_test_failed`, matched test `tabellenRahmen ... > leere Beschriftung mit Überlauf: Rahmen bleibt erreichbar, Name ist „Tabelle“`). Semantic assessment: the target executed and failed on the planned assertion for the intended reason (the export does not exist yet; the caption is empty instead of „Tabelle“); no syntax, load or fixture fault; the other 16 tests passed.

**GREEN** (commit `78744d4`, `fix(09): 08/WR-02 ... (08/WR-01)`): `zustaende.test.ts` plus `quelltext.test.ts`: 2 files, 178 tests passed; full vitest run: 2162 tests passed (2158 before: 8 added, 4 removed).

**REFACTOR:** none needed.

### TDD Gate Compliance

RED (`test(09-...)`-style commit `8b4ae20`) precedes GREEN (`78744d4`). The plan's own commit scope was `test(09)` and `fix(09)`, not `test(09-02)`/`feat(09-02)`; the sequence and content satisfy the gate.

## Task Commits

1. **Task 1: Tabellenrahmen-Regel (tracer, tdd)**
   - RED: `8b4ae20` (test)
   - GREEN: `78744d4` (fix)
2. **Task 2: Ledger 08 und 08-VERIFICATION**
   - Ledger: `46fc562` (docs)
   - Verification: `14e9733` (docs)

**Plan metadata:** the commit of this SUMMARY (docs: complete plan).

## Files Created/Modified

- `app/src/components/datenTabelle.ts` - `ERSATZ_BESCHRIFTUNG`, `RahmenLage`, `TabellenRahmen`, `tabellenRahmen`
- `app/src/components/DatenTabelle.vue` - caption text and frame attributes via `rahmenLage` (computed from `tabellenRahmen`); DEV warning keeps the prefix „DatenTabelle: `beschriftung` ist leer“
- `app/src/components/__tests__/zustaende.test.ts` - unit tests of `tabellenRahmen`, SSR fallback caption test
- `app/src/lib/__tests__/quelltext.test.ts` - old source-text guard block removed
- `.planning/phases/08-fixes-und-triage/08-REVIEW-DISPOSITION.md` - ledger on `open: 0`
- `.planning/phases/08-fixes-und-triage/08-VERIFICATION.md` - renewed (D-15)

## Decisions Made

- Fallback caption „Tabelle“ over throwing in DEV: keeps keyboard access independent of callers (review recommendation for WR-02, D-20).
- IN-05 checked before deferral: callers of `quellenZeile` pass `[kennzahlen.quelle]`, `[p.pdfSeite]`, `[e.einnahmen.pdfSeite]`, `[e.ausgaben.pdfSeite]`, two-element arrays from `kennzahlen.ts`/`schulden.ts`, and `vePdfSeiten()` (shipped data: pages 143, 153, 157, 160, 245). No empty list, so no D-10 fix.
- IN-07 checked: no hand-built „rund“-prefix copy outside `charts/format.ts` in `app/src`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] gsd-tools path in the Task 2 command**
- **Found during:** Task 2
- **Issue:** The plan calls `node .claude/gsd-core/bin/gsd-tools.cjs`; `.claude/gsd-core/` is untracked and exists only in the main checkout, not in the worktree.
- **Fix:** Called the same CLI by its absolute path in the main checkout (read-only use); the working directory stayed the worktree, so it read the worktree's phase files.
- **Files modified:** none
- **Verification:** `verification.status` printed `passed`; fingerprint output copied verbatim.

**2. [Rule 3 - Blocking] Task 1 `<automated>` command run in separate steps**
- **Found during:** Task 1
- **Issue:** The sandbox refused the single compound command with `S=$(mktemp -d)` and runtime-computed rsync targets.
- **Fix:** Ran the identical steps (rsync, `npm ci`, vitest, type-check, lint, format:check, build-only, `scripts/e2e-wie-ci.sh` for `--project=mobil` and for `e2e/interaktion.spec.ts e2e/smoke.spec.ts`) one by one in a fixed scratch copy; the whole `app/src` was re-synced from the worktree before the GREEN run.
- **Verification:** all steps green (see below).

**3. [Rule 3 - Blocking] RED evidence format**
- **Found during:** Task 1 (RED)
- **Issue:** vitest's `tap` and `tap-flat` reports are rejected by the classifier.
- **Fix:** Used the `junit` reporter for the machine check (unchanged report, real command); the plan's commit and test content are unchanged.

---

**Total deviations:** 3 auto-fixed (3 blocking, all tooling or path issues)
**Impact on plan:** None on scope or outcome.

## Verification Results

- vitest full: 2162 passed. `vue-tsc --build`, `eslint .`, `prettier --check src/ e2e/`: clean. `vite build`: success.
- Playwright: `--project=mobil` 41 passed; `ci` project with `e2e/interaktion.spec.ts` and `e2e/smoke.spec.ts` 62 passed.
- Task 1 grep checks: OK. `git diff --stat 8b4ae20^..78744d4 -- daten app/src/data pipeline`: empty.
- Task 2 ledger checks (open: 0, no `open` row, Source cells non-empty and not starting with „-“, total 10, WR-01/02 fixed): OK. Cited hashes accepted by `git cat-file -e`.
- Task 2 verification checks: status `passed`, `08/WR-02`, v3 digest, `datenTabelle.ts` in `covered_files`, `previous_score` contains `5/5`: OK.
- `commits: 4` counts the commits before this SUMMARY commit (`plan_head_before..plan_head_after`).

## Issues Encountered

None beyond the tooling items under Deviations.

## Known Stubs

None.

## Threat Flags

None. No new endpoint, auth path, file access or schema surface; T-09-04 to T-09-06 are mitigated as planned.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- DatenTabelle is in its final form, so the Basislauf (09-03) and the re-verifications of phases 5 to 7 see the same code and their digests do not go stale because of it.
- The screenreader announcement check (A11Y-03) stays open in `08-UAT.md`; it is not affected by this plan.

## Self-Check: PASSED

- Created/modified files exist; commits `8b4ae20`, `78744d4`, `46fc562`, `14e9733` are ancestors of HEAD.

---
*Phase: 09-sicherheit-und-audit*
*Completed: 2026-10-09*
