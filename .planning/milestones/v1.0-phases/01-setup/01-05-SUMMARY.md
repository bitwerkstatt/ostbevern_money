---
phase: 01-setup
plan: 05
subsystem: infra
tags: [github-actions, ci, uv, npm, claude-md, readme, license, mit]

# Dependency graph
requires:
  - phase: 01-setup/01-02
    provides: "pipeline/ uv project with proven uv sync --locked / ruff check / ruff format --check / pytest commands"
  - phase: 01-setup/01-03
    provides: "app/ Vue 3 scaffold with proven npm ci / type-check / lint / format:check / build commands"
  - phase: 01-setup/01-04
    provides: "Münster base components (did not change this plan's deliverables, but completed D-03 before CLAUDE.md documents the component set)"
provides:
  - ".github/workflows/ci.yml: two parallel jobs (pipeline, app) replaying exactly the command lines proven locally, SHA-pinned actions, contents: read token"
  - ".claude/CLAUDE.md Technology Stack/Conventions/Architecture blocks filled with commands and the six D-17 conventions"
  - "README.md and LICENSE (MIT) completing the Spez. 7 repository structure"
affects: []

# Actuals (#2632)
actuals:
  tokens: 2392
  tasks: 3
  commits: 3
  plan_head_before: 0ca7035d120904f6371a0eb5360cc60d10c2c4c5
  plan_head_after: e90bb698b58f1c2f21fd42f002d308c2ab92c530

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "CI replays locally-proven command lines verbatim: ci.yml's run: lines are byte-identical to the commands executed and verified in pipeline/ and app/ during this plan, not independently re-derived"
    - "SHA-pinned GitHub Actions: every uses: is a full 40-hex commit SHA resolved via git ls-remote, with the version tag kept as a trailing comment for human readability"

key-files:
  created:
    - ".github/workflows/ci.yml"
    - "README.md"
    - "LICENSE"
  modified:
    - ".claude/CLAUDE.md"

key-decisions:
  - "actions/checkout@v7.0.1 is a lightweight tag with no peeled ^{} ref in git ls-remote output, so the tag SHA itself (3d3c42e...) was used directly, per the task's own fallback rule"
  - "Task 1 shipped as type=tracer; the tracer feedback gate re-ran all four pipeline <verify> commands and all five app <verify> commands after the commit (interactive, human_verify_mode=end-of-phase, automated-only verify — no checkpoint per the precedence chain), both chains passed, so Tasks 2-3 proceeded without a checkpoint"
  - "A transient ENOTEMPTY rmdir error during the post-commit npm ci re-run (node_modules/@typescript-eslint/utils/dist/ts-eslint/ESLint) was a filesystem race, not a code defect; a bare retry of npm ci succeeded cleanly"

patterns-established:
  - "Pattern: .claude/CLAUDE.md as the single commands-and-conventions reference — README.md points to it instead of duplicating the command list"

requirements-completed: [QUAL-01, SETUP-04, SETUP-01]

coverage:
  - id: D1
    description: "ci.yml exists with exactly the two parallel jobs pipeline/app, no needs, no path filters, contents: read, every action SHA-pinned, replaying command-for-command what was proven locally"
    requirement: "QUAL-01"
    verification:
      - kind: other
        ref: "(cd pipeline && uv sync --locked && uv run ruff check . && uv run ruff format --check . && uv run pytest)"
        status: pass
      - kind: other
        ref: "(cd app && npm ci && npm run type-check && npm run lint && npm run format:check && npm run build)"
        status: pass
      - kind: other
        ref: "app/node_modules/.bin/prettier --parser yaml .github/workflows/ci.yml (ci.yml is valid YAML)"
        status: pass
      - kind: other
        ref: "Task 1 acceptance criteria: job-name awk check, no needs:, no paths:, contents: read present, every uses: SHA-pinned, node-version-file/setup-uv version present, git remote empty"
        status: pass
    human_judgment: false
  - id: D2
    description: ".claude/CLAUDE.md documents commands and the six D-17 conventions in its Technology Stack/Conventions/Architecture blocks; GSD-managed blocks (project, skills, workflow, profile) stay byte-identical; no root CLAUDE.md exists"
    requirement: "SETUP-04"
    verification:
      - kind: other
        ref: "Task 2 <verify>: GSD-block-equality script (project/skills/workflow/profile sed ranges compared against git show HEAD) and the 11-phrase presence grep"
        status: pass
      - kind: other
        ref: "Task 2 acceptance criteria: all 7 marker pairs present, 'not yet documented'/'not yet established' placeholders gone, no root CLAUDE.md"
        status: pass
    human_judgment: false
  - id: D3
    description: "README.md and LICENSE complete the repo structure: MIT license text with the 2026 Thomas Manthey copyright line, README with the Münster Money credit link and quick-start commands, nothing pushed to any remote"
    requirement: "SETUP-01"
    verification:
      - kind: other
        ref: "Task 3 <verify>: LICENSE head/permission/copyright greps, 7-phrase README presence grep"
        status: pass
      - kind: other
        ref: "Task 3 acceptance criteria: head -n 1 LICENSE, git ls-files --error-unmatch README.md LICENSE, git remote empty"
        status: pass
    human_judgment: false

# Metrics
duration: 32 min
completed: 2026-10-01
status: complete
---

# Phase 1 Plan 5: CI, CLAUDE.md, README/LICENSE Summary

**Two-job GitHub Actions workflow (`pipeline`, `app`) that replays every command already proven locally, SHA-pinned to full commit hashes; `.claude/CLAUDE.md` filled with commands and the six D-17 conventions; README.md and MIT LICENSE closing out the Spez. 7 repository structure with the Münster Money credit — nothing pushed, no remote configured (D-18).**

## Performance

- **Duration:** 32 min
- **Started:** 2026-10-01T09:28:00Z (approx.)
- **Completed:** 2026-10-01T10:00:00Z (approx.)
- **Tasks:** 3
- **Files modified:** 4 (3 created, 1 modified)

## Accomplishments

- `.github/workflows/ci.yml`: `name: CI`, triggers on every `push`/`pull_request` with no path filter, top-level `permissions: contents: read`, exactly two parallel jobs with no `needs:` between them
  - `pipeline` job: `actions/checkout@3d3c42e...` (v7.0.1), `astral-sh/setup-uv@c18668a...` (v10.2.0, `version: "0.9.26"`), then `uv sync --locked`, `uv run ruff check .`, `uv run ruff format --check .`, `uv run pytest` — each a single-line `run:` step with a German `name:`
  - `app` job: `actions/checkout@3d3c42e...`, `actions/setup-node@8207627...` (v7.0.0, `node-version-file: app/.nvmrc`, `cache: npm`, `cache-dependency-path: app/package-lock.json`), then `npm ci`, `npm run type-check`, `npm run lint`, `npm run format:check`, `npm run build`
  - Every action pinned to a full 40-hex commit SHA resolved read-only via `git ls-remote`, version tag kept as a trailing comment
- Both local replays run twice (once while authoring the file, once as the post-commit tracer feedback gate) — all nine commands exit 0, `ci.yml` parses as valid YAML via Prettier
- `.claude/CLAUDE.md`: Technology Stack block (pipeline/app/CI summary plus a "### Befehle" subsection with every repo-root command and the two CI replay command chains), Conventions block (the six D-17 conventions with exact lead phrases, plus this phase's established conventions), Architecture block (the data-flow diagram in prose) — only these three GSD-managed blocks touched, verified byte-identical elsewhere against `git show HEAD`
- `README.md` (German, Du-Anrede): project description with the two Leitfragen and the "inoffizielles Projekt" disclosure, Stand, Aufbau, Schnellstart (pointing to `.claude/CLAUDE.md` for the full command list), Lizenz, and a Dank section crediting Münster Money with a link plus the Font Awesome Free (CC BY 4.0) icon credit
- `LICENSE`: standard MIT text with `Copyright (c) 2026 Thomas Manthey`
- No GitHub repository created, no remote added, no push — `git remote` prints nothing throughout

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — ci.yml with jobs pipeline and app, replayed locally command for command** - `ce193be` (feat)
2. **Task 2: Commands and conventions in .claude/CLAUDE.md (D-17)** - `39bc849` (docs)
3. **Task 3: README.md and MIT LICENSE with the Münster credit (D-05)** - `e90bb69` (docs)

**Plan metadata:** commit created immediately after this SUMMARY (see below).

_Note: Task 1 (`type="tracer"`) is production-quality, not a throwaway — it was followed by the tracer feedback gate (all nine local-replay commands re-run after the commit, all passed) before Tasks 2-3 proceeded._

## Resolved Action SHAs

| Action | Tag | Commit SHA |
|--------|-----|------------|
| `actions/checkout` | v7.0.1 | `3d3c42e5aac5ba805825da76410c181273ba90b1` |
| `actions/setup-node` | v7.0.0 | `820762786026740c76f36085b0efc47a31fe5020` |
| `astral-sh/setup-uv` | v10.2.0 | `c18668ad3cf93ea998bef934396af7bb5c839dc7` |

`actions/checkout@v7.0.1` has no peeled `^{}` ref in `git ls-remote` output (lightweight tag), so the tag SHA itself was used, per the task's own fallback instruction.

## Local CI Replay (tails)

**Pipeline** (`cd pipeline && uv sync --locked && uv run ruff check . && uv run ruff format --check . && uv run pytest`):
```
Resolved 24 packages in 1ms
Audited 22 packages in 1ms
All checks passed!
6 files already formatted
============================== 17 passed in 0.14s ==============================
```

**App** (`cd app && npm ci && npm run type-check && npm run lint && npm run format:check && npm run build`):
```
> type-check
> vue-tsc --build

> lint
> eslint .

> format:check
> prettier --check src/
Checking formatting...
All matched files use Prettier code style!

> build
...
✓ 828 modules transformed.
dist/index.html                   0.61 kB │ gzip:   0.39 kB
dist/assets/index-k_jdHlou.css  109.17 kB │ gzip:  15.74 kB
dist/assets/index-CuvKOEC4.js   782.06 kB │ gzip: 254.84 kB
✓ built in 316ms
```
(`npm run build` warns about a >500 kB chunk — expected, not a failure; no code-splitting work is in scope for this plan.)

## Files Created/Modified

- `.github/workflows/ci.yml` — CI workflow, two parallel jobs `pipeline`/`app`
- `.claude/CLAUDE.md` — Technology Stack, Conventions, Architecture blocks filled (project/skills/workflow/profile blocks untouched)
- `README.md` — project overview, Stand, Aufbau, Schnellstart, Lizenz, Dank
- `LICENSE` — MIT License, Copyright (c) 2026 Thomas Manthey

## Decisions Made

- `actions/checkout@v7.0.1`'s tag SHA was used directly (no peeled `^{}` ref existed), matching the task's documented fallback
- The tracer feedback gate's automated re-run doubled as the SUMMARY's authoritative "both local replays exit 0" evidence, so the tails above are from the post-commit run, not the pre-commit authoring run
- A transient `ENOTEMPTY` filesystem race during the post-commit `npm ci` was diagnosed as an environment flake (not a code or dependency issue) and resolved by a bare retry, which installed cleanly

## Deviations from Plan

None - plan executed exactly as written. The transient `npm ci` `ENOTEMPTY` rmdir error during the tracer feedback gate's re-run is not tracked as a deviation under the Rule 1-3 framework (it's an infrastructure flake with no code fix — a bare retry resolved it, no files changed).

## Issues Encountered

- One transient `ENOTEMPTY` error on `npm ci`'s rmdir of a stale `node_modules/@typescript-eslint/utils/dist/ts-eslint/ESLint` directory during the post-commit tracer-gate re-run — resolved by retrying `npm ci`, which succeeded cleanly on the second attempt. Not reproducible, not a code issue.

## User Setup Required

None - no external service configuration required. D-18 is explicit: the executor does not create a GitHub repository, add a remote, or push — the user does this themselves. Once pushed, the Actions tab should show both `pipeline` and `app` jobs green (flagged as a manual follow-up in the plan's "Flagged assumptions").

## Next Phase Readiness

- Phase 1 (Setup) is now complete: pipeline scaffold (01-02), app scaffold (01-03), Münster base components (01-04), and CI/docs/license (01-05) all have green SUMMARYs
- `.claude/CLAUDE.md` is the single, complete commands-and-conventions reference for Phase 2 onward — no script should re-derive or duplicate what it documents
- CI (`ci.yml`) is ready to run the moment the user creates the GitHub repository and pushes; until then it only exists as code, verified via local replay (D-18)
- No blockers or concerns

---
*Phase: 01-setup*
*Completed: 2026-10-01*

## Self-Check: PASSED

- `FOUND: .github/workflows/ci.yml`
- `FOUND: README.md`
- `FOUND: LICENSE`
- `FOUND: .claude/CLAUDE.md` (modified)
- Commits verified in `git log --oneline -5`: `ce193be` (Task 1), `39bc849` (Task 2), `e90bb69` (Task 3)
- Re-ran `(cd pipeline && uv sync --locked && uv run ruff check . && uv run ruff format --check . && uv run pytest)`: 17 passed, both ruff checks clean
- Re-ran `(cd app && npm ci && npm run type-check && npm run lint && npm run format:check && npm run build)`: all green (one transient `ENOTEMPTY` on the first `npm ci` attempt, resolved on retry — see Issues Encountered)
- Re-ran `app/node_modules/.bin/prettier --parser yaml .github/workflows/ci.yml`: valid YAML, exit 0
- Re-ran all acceptance-criteria greps for Tasks 1-3: all pass (job names, no `needs:`/path-filter, `contents: read`, SHA-pinned `uses:`, `node-version-file`/`version` pins, GSD-block equality, placeholder removal, no root `CLAUDE.md`, LICENSE head/copyright, README phrase set, `git ls-files`, `git remote` empty)
- Commit ledger: `plan_head_before=0ca7035d120904f6371a0eb5360cc60d10c2c4c5`, `plan_head_after=e90bb698b58f1c2f21fd42f002d308c2ab92c530`, `git rev-list --count` = 3 (matches `actuals.commits: 3`)
