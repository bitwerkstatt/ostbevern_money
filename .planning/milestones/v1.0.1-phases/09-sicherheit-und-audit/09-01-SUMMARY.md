---
phase: 09-sicherheit-und-audit
plan: 01
subsystem: security
tags: [security-register, stride, pytest, vitest, name-scan, meta-json]

requires:
  - phase: 04-manuelle-daten-und-app-daten
    provides: threat models of 04-01..04-06-PLAN.md (21 threats)
  - phase: 08-fixes-und-triage
    provides: changed code under T-04-15, T-04-16, T-04-18, T-04-03 (commit notes in the rows)
provides:
  - 04-SECURITY.md for phase 4, status verified, threats_open 0, 21 of 21 threats closed
  - AR-04-01 (T-04-11) and AR-04-02 (T-04-20) confirmed as accepted risks
affects: [09-15 re-verification, 09 audit report, SEC-01]

actuals:
  tokens: 5256
  tasks: 3
  commits: 3

plan_head_before: 86c56dc24eb96193ca66031d67194f6472f8c196
plan_head_after: cafa251443c39a3bc7a243632c5754758fbfd366

tech-stack:
  added: []
  patterns:
    - "Register rows cite file:line read in the plan and test names from a -rs run without skips"

key-files:
  created:
    - .planning/milestones/v1.0-phases/04-manuelle-daten-und-app-daten/04-SECURITY.md
  modified: []

key-decisions:
  - "T-04-05 (meta.json) rests on the strict allowlist plus test_meta_json_bricht_ab; the name scan only complements it"
  - "T-04-19 is closed historically at 52b3d3b by a reproduced normalized diff, T-04-SC by an empty dependency-file log"
  - "T-04-11 and T-04-20 keep disposition accept (D-03), no upgrade"

patterns-established:
  - "Evidence run first, register rows second: every cited test ran green in this plan with zero skips"

requirements-completed: [SEC-01]

coverage:
  - id: D1
    description: "04-SECURITY.md with 21 closed threats, file:line references and green tests, status verified, threats_open 0"
    requirement: SEC-01
    verification:
      - kind: unit
        ref: "pipeline pytest runs 1 to 3 of 09-01 (142, 40 and 142 passed, no SKIPPED line)"
        status: pass
      - kind: other
        ref: "awk and grep checks of the Task 1, 2 and 3 verify blocks on 04-SECURITY.md"
        status: pass
    human_judgment: false
  - id: D2
    description: "Name tests for app/src/data/*.json and daten/manuell/meta.json ran green without a skip (ROADMAP criterion 1)"
    requirement: SEC-01
    verification:
      - kind: unit
        ref: "pipeline/tests/test_app_daten.py#test_keine_personennamen_in_app_daten, test_produkte.py#test_keine_personennamen, test_manuell.py#test_meta_json_gueltig, test_meta_json_bricht_ab"
        status: pass
    human_judgment: false

duration: 35min
completed: 2026-10-09
status: complete
---

# Phase 9 Plan 01: 04-SECURITY.md Summary

**Security register of phase 4 with all 21 threats closed against the code after phase 8, each row backed by a file:line read in this plan and tests that ran green with zero skips**

## Performance

- **Duration:** about 35 min (start time not recorded, estimate)
- **Completed:** 2026-10-09T06:04Z
- **Tasks:** 3
- **Files modified:** 1 (created)

## Accomplishments

- `04-SECURITY.md` created in the section order of 08-SECURITY.md (Trust Boundaries, Threat Register, Accepted Risks Log, Security Audit Trail, Sign-Off) plus the appended `Security Audit 2026-10-09` block from `verification.append-audit`. Frontmatter: `phase: "4"`, `status: verified`, `threats_open: 0`, `asvs_level: 1`, `block_on: high`, `register_authored_at_plan_time: true`.
- 21 register rows (T-04-01 to T-04-20, T-04-SC once), Severity and Disposition copied from the plan threat models, all `closed`.
- Phase-8 notes with commit hashes on T-04-16 (27e0be7, 7d4be31, 57063a0, c1da62e), T-04-15 and T-04-18 (7d4be31, e8e25d5, c27904b, dde7341) and T-04-03 (96a23de).
- T-04-19 closed historically: normalized diff of `erklaerungen.md` and `texte.json` at 52b3d3b against f9e085d is empty (reproduced). T-04-SC closed: `git log 3973d86..7f605fd` over the four dependency files is empty (reproduced).
- Accepted risks AR-04-01 (T-04-11) and AR-04-02 (T-04-20) confirmed with the D-03 checks, not upgraded.

## D-04 statement

**Keine offene Bedrohung unter T-04-01 bis T-04-20 und T-04-SC.** All mitigations were present in the code after phase 8 and every named test ran green, so no failing test and no code fix was needed. No code, no generated data and no check was changed in this plan; `alle.py` was not run. The only file touched is `04-SECURITY.md`, so `08-VERIFICATION.md` is not made stale by this plan.

## Test runs (all with `-p no:cacheprovider -rs -q`, logs kept in the scratch directory)

| Run | Scope | Summary line | SKIPPED lines |
|-----|-------|--------------|---------------|
| 1 (Task 1) | `test_texte.py`, `test_formatiere.py`, the two name tests, `test_meta_json_gueltig`, `test_meta_json_bricht_ab` | `142 passed in 7.36s` | 0 |
| 2 (Task 2) | 24 node ids of T-04-01 to T-04-10 | `40 passed in 23.91s` | 0 |
| 3 (Task 3) | 12 node ids of T-04-11 to T-04-18 plus `test_texte.py` and `test_formatiere.py` | `142 passed in 10.37s` | 0 |
| vitest | `src/lib/__tests__/quelltext.test.ts` (T-04-17) | `Tests 156 passed (156)`, 1 file | none |

`test_port_wie_format_ts` ran and was not skipped because `app/node_modules` was installed with `npm ci` from the committed `package-lock.json` (directory is gitignored, no tracked file changed).

Name tests that ran green and not skipped (D-05): `test_keine_personennamen_in_app_daten`, `test_keine_personennamen`, `test_meta_json_gueltig`, `test_meta_json_bricht_ab`.

### Reproduced commands

- T-04-19: for `daten/manuell/texte/erklaerungen.md` and `app/src/data/texte.json`, `diff` of `git show 52b3d3b:<datei>` (with the Haushaltsjahr placeholder suffix `jahr` replaced by `zahl` via sed) against `git show f9e085d:<datei>` printed no difference for either file.
- T-04-SC: `git log --oneline 3973d86..7f605fd -- pipeline/pyproject.toml pipeline/uv.lock app/package.json app/package-lock.json` printed nothing.
- T-04-05 probe (not committed): adding `satzung.kaemmerin` to a copy of `meta.json` made `lies_meta_json` abort with `satzung hat unbekannte Felder: ['kaemmerin']`.
- Phase-8 code touch check: `git diff --stat 93b0a61..HEAD` over `pruefung.py`, `stellenplan.py`, `manuell.py`, `schema.py` is empty; `app_daten.py` changed 4 lines (`pruefe_titel` call, 27e0be7), `ci.yml` only comment lines.

## Task Commits

1. **Task 1: Gerüst, 21 Bedrohungen, T-04-16 geschlossen** - `9421304` (docs)
2. **Task 2: T-04-01 bis T-04-10** - `c8bec91` (docs)
3. **Task 3: T-04-11 bis T-04-SC, Accepted Risks, Audit, Sign-Off** - `cafa251` (docs)

**Plan metadata:** this SUMMARY is committed separately after the task commits (docs: complete plan).

## Files Created/Modified

- `.planning/milestones/v1.0-phases/04-manuelle-daten-und-app-daten/04-SECURITY.md` - security register of phase 4, verified

## Decisions Made

- T-04-05: the evidence is the allowlist (`_META_TOP_SCHLUESSEL`, `_META_SATZUNG_SCHLUESSEL`) plus `test_meta_json_bricht_ab`; the PDF name scan only complements it because its needles come from the product person fields (RESEARCH Pitfall 5).
- T-04-13: the plan promised a conservation test and a Satzung-total test; both live in `test_zuschussbedarf_summe_top_knoten`, so the row cites four KL tests plus `test_hierarchie_csv_unveraendert` and says so.
- T-04-14: the worksheet named `schuldenstand_euro` as the app-side formula; in the code the app uses the shared `investitionskredite_ende` and `pro_kopf_euro`, while `schuldenstand_euro` feeds Regel 9. The row states this.
- Two non-blocking audit notes (word-pair name scan from the research, missing `satzung` case in `test_meta_json_bricht_ab`) are recorded in the Audit Trail without changing a status.

## Deviations from Plan

None - plan executed exactly as written. Two evidence details differ from the research worksheet and were written as found: the line of the haushalt writer is `app_daten.py:707-720` (`schreibe_app_json`) rather than `schema.py`, and `manuell.py:128-135` holds the top-level key check.

## Issues Encountered

- `app/node_modules` was absent in the worktree, so `test_port_wie_format_ts` would have skipped. Resolved with `npm ci` from the lockfile (gitignored output), then the test ran.

## Known Stubs

None.

## Threat Flags

None - no new network endpoint, auth path or schema change; only a planning document was added.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- SEC-01 is evidenced; ROADMAP Phase 9 criterion 1 holds, including the green name tests.
- No code or generated data was touched, so plan 09-15 has nothing to re-fingerprint on account of this plan.

---
*Phase: 09-sicherheit-und-audit*
*Completed: 2026-10-09*

## Self-Check: PASSED

- FOUND: `.planning/milestones/v1.0-phases/04-manuelle-daten-und-app-daten/04-SECURITY.md`
- FOUND commits: 9421304, c8bec91, cafa251 (ancestors of HEAD)
- Verify blocks of Tasks 1 to 3 re-run: all pass (21 rows, 21 closed, 20 with test names, AR-04-01 and AR-04-02 present)
