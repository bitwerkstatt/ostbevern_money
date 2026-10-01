---
phase: 01-setup
plan: 01
subsystem: setup
tags: [package-legitimacy, pypi, npm, supply-chain, checkpoint]

# Dependency graph
requires: []
provides:
  - "Human-approved list of all 5 PyPI packages (installed by 01-02) and all 21 npm packages (installed/scaffolded by 01-03)"
  - "Verbatim human approval verdict gating the Phase 1 package-legitimacy threat mitigation (T-01-SC)"
affects: [01-setup/01-02, 01-setup/01-03]

# Actuals (#2632)
actuals:
  tokens: 2800
  tasks: 1
  commits: 1

# Tech tracking
tech-stack:
  added: []
  patterns: ["Package legitimacy gate: blocking-human checkpoint verifies registry source + absence of postinstall scripts before any install task runs"]

key-files:
  created: [".planning/phases/01-setup/01-01-SUMMARY.md"]
  modified: []

key-decisions:
  - "Human approved the full 26-package list (5 PyPI + 21 npm) verbatim with no drops or replacements"
  - "Drift policy: patch/minor version drift within the same major is accepted without re-approval; a new major (e.g. typescript 7.x) is NOT accepted — the scaffold's pinned ~6.0.x stays"
  - "oxlint, eslint-plugin-oxlint, and vite-plugin-vue-devtools remain intentionally excluded — stripped from package.json by 01-03 before npm install"

patterns-established:
  - "Pattern: Package legitimacy gate — before any install/scaffold task in a phase, a gate="blocking-human" checkpoint refreshes registry evidence (npm view / pip index versions) read-only and requires explicit human approval of the exact package+version+repository list"

requirements-completed: [SETUP-02, SETUP-03]

coverage:
  - id: D1
    description: "Human verified every PyPI and npm package's source repository and absence of postinstall scripts before any install runs"
    requirement: "SETUP-02"
    verification:
      - kind: manual_procedural
        ref: "Human reply 'approved' recorded in this SUMMARY against the refreshed package table"
        status: pass
    human_judgment: true
    rationale: "Package-legitimacy verification is an irreversible trust decision (gate=blocking-human) that must be made by a human, not inferred from automated heuristics — this is the entire purpose of the gate."
  - id: D2
    description: "Approved package list (names, versions, registry URLs) recorded so plans 01-02 and 01-03 install exactly that list"
    requirement: "SETUP-03"
    verification:
      - kind: manual_procedural
        ref: "Full 26-row table (5 PyPI + 21 npm) present in this SUMMARY's Approved Package List section"
        status: pass
    human_judgment: false

# Metrics
duration: 5 min
completed: 2026-10-01
status: complete
---

# Phase 1 Plan 1: Package Legitimacy Gate Summary

**Human approved the full 26-package list (5 PyPI, 21 npm) for Phase 1 after read-only evidence refresh via `pip index versions` / PyPI JSON `project_urls` and `npm view NAME version repository.url scripts.postinstall` — no packages dropped or replaced.**

## Performance

- **Duration:** 5 min (checkpoint confirmation + summary finalization)
- **Started:** 2026-10-01T09:00:00Z
- **Completed:** 2026-10-01T09:08:08Z
- **Tasks:** 1
- **Files modified:** 1 (this SUMMARY.md)

## Accomplishments

- Refreshed package-legitimacy evidence read-only (no installs) for all 5 PyPI and 21 npm packages named in RESEARCH.md's Package Legitimacy Audit and the create-vue scaffold's additional dependencies
- Presented a single table (name, registry, current version, source repository URL, postinstall script) to the human for every package
- Human replied `approved` — verbatim verdict recorded below together with the final table
- Confirmed the three create-vue extras (oxlint, eslint-plugin-oxlint, vite-plugin-vue-devtools) remain intentionally excluded, to be stripped by 01-03 before `npm install`
- Nothing was installed; no repository files other than this SUMMARY.md changed

## Human Verdict (verbatim)

> approved

No packages were dropped or replaced. Plans 01-02 (PyPI, via `uv add`) and 01-03 (npm, via `npm create vue@3.24.0` + `npm install`) are authorized to install exactly the list below.

## Approved Package List

Evidence refreshed read-only on 2026-10-01 via `pip index versions` + PyPI JSON `project_urls`, and `npm view NAME version repository.url scripts.postinstall`.

| Package | Registry | Registry URL | Current version | Source repository | Postinstall |
|---|---|---|---|---|---|
| pdfplumber | PyPI | https://pypi.org/project/pdfplumber/ | 0.11.10 | github.com/jsvine/pdfplumber | n/a |
| polars | PyPI | https://pypi.org/project/polars/ | 1.44.2 | github.com/pola-rs/polars | n/a |
| typer | PyPI | https://pypi.org/project/typer/ | 0.27.2 | github.com/fastapi/typer | n/a |
| pytest | PyPI | https://pypi.org/project/pytest/ | 9.1.1 | github.com/pytest-dev/pytest | n/a |
| ruff | PyPI | https://pypi.org/project/ruff/ | 0.16.9 | github.com/astral-sh/ruff | n/a |
| create-vue | npm | https://www.npmjs.com/package/create-vue | 3.24.0 | github.com/vuejs/create-vue | none (executed via `npm create vue@3.24.0`) |
| vue | npm | https://www.npmjs.com/package/vue | 3.5.43 | github.com/vuejs/core | none |
| vue-router | npm | https://www.npmjs.com/package/vue-router | 5.3.1 | github.com/vuejs/router | none |
| vite | npm | https://www.npmjs.com/package/vite | 8.3.1 | github.com/vitejs/vite | none |
| @vitejs/plugin-vue | npm | https://www.npmjs.com/package/@vitejs/plugin-vue | 6.0.9 | github.com/vitejs/vite-plugin-vue | none |
| vue-tsc | npm | https://www.npmjs.com/package/vue-tsc | 3.3.11 | github.com/vuejs/language-tools | none |
| typescript | npm | https://www.npmjs.com/package/typescript | 7.0.2 latest; scaffold pin ~6.0.x is kept (new major 7.x NOT approved) | github.com/microsoft/TypeScript | none |
| eslint | npm | https://www.npmjs.com/package/eslint | 10.11.0 | github.com/eslint/eslint | none |
| eslint-plugin-vue | npm | https://www.npmjs.com/package/eslint-plugin-vue | 10.11.1 | github.com/vuejs/eslint-plugin-vue | none |
| vue-eslint-parser | npm | https://www.npmjs.com/package/vue-eslint-parser | 10.4.1 | github.com/vuejs/vue-eslint-parser | none |
| @vue/eslint-config-typescript | npm | https://www.npmjs.com/package/@vue/eslint-config-typescript | 14.9.0 | github.com/vuejs/eslint-config-typescript | none |
| eslint-config-prettier | npm | https://www.npmjs.com/package/eslint-config-prettier | 10.1.8 | github.com/prettier/eslint-config-prettier | none |
| prettier | npm | https://www.npmjs.com/package/prettier | 3.9.9 | github.com/prettier/prettier | none |
| @vue/tsconfig | npm | https://www.npmjs.com/package/@vue/tsconfig | 0.9.1 | github.com/vuejs/tsconfig | none |
| @tsconfig/node24 | npm | https://www.npmjs.com/package/@tsconfig/node24 | 24.0.5 | github.com/tsconfig/bases | none |
| @types/node | npm | https://www.npmjs.com/package/@types/node | 26.6.3 (version as chosen by the scaffold) | github.com/DefinitelyTyped/DefinitelyTyped | none |
| jiti | npm | https://www.npmjs.com/package/jiti | 2.7.0 | github.com/unjs/jiti | none |
| npm-run-all2 | npm | https://www.npmjs.com/package/npm-run-all2 | 9.0.3 | github.com/bcomnes/npm-run-all2 | none |
| echarts | npm | https://www.npmjs.com/package/echarts | 6.1.0 | github.com/apache/echarts | none |
| vue-echarts | npm | https://www.npmjs.com/package/vue-echarts | 8.3.1 | github.com/ecomfe/vue-echarts | none |
| @awesome.me/webawesome | npm | https://www.npmjs.com/package/@awesome.me/webawesome | 3.14.0 | github.com/shoelace-style/webawesome | none |

**Findings:** All 26 repositories match the plan's expected upstream. Zero npm postinstall scripts across all 21 npm packages. No look-alike or typo-squatted names found.

**Not installed on purpose:** oxlint, eslint-plugin-oxlint, vite-plugin-vue-devtools — these create-vue scaffold extras are stripped from `package.json` by 01-03 before `npm install` (per 01-03 decisions D-15/D-16, which name only ESLint; this also keeps unaudited packages out of the installed tree).

**Drift policy:** Patch/minor version drift within the same major is accepted without re-approval (registry versions move between planning time and install time). A new major version is NOT accepted under this approval — notably `typescript` stays pinned to the scaffold's `~6.0.x` even though `7.0.2` is the npm registry's current latest.

## Task Commits

This plan has a single task, which is the checkpoint itself. No code or dependency files were created or modified — the task's `<done>` criterion is "Human approval... is recorded in 01-01-SUMMARY.md; nothing has been installed," which this SUMMARY satisfies.

**Plan metadata:** commit created immediately after this SUMMARY (see below).

_Note: No `feat`/`fix`/`test` commits exist for this plan — it is a pure verification gate with no repository changes besides this SUMMARY.md._

## Files Created/Modified

- `.planning/phases/01-setup/01-01-SUMMARY.md` - This summary, recording the human-approved package list and verdict

## Decisions Made

- Human approved the complete 26-package list without changes
- Patch/minor drift accepted within the same major; a new major (typescript 7.x) is explicitly not approved
- The three create-vue scaffold extras (oxlint, eslint-plugin-oxlint, vite-plugin-vue-devtools) stay excluded, consistent with 01-03's plan

## Deviations from Plan

None - plan executed exactly as written. The checkpoint was presented with refreshed evidence as specified, and the human replied "approved" verbatim.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Plans 01-02 (PyPI pipeline dependencies via `uv add`) and 01-03 (npm app scaffold via `npm create vue@3.24.0`) are unblocked and authorized to install exactly the 26-package list recorded above
- No blockers or concerns

---
*Phase: 01-setup*
*Completed: 2026-10-01*
