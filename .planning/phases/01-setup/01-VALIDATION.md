---
phase: "1"
slug: "setup"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-10-01"
---

# Phase 1 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.x (pipeline); app side: `vue-tsc` + ESLint + Prettier check (no app unit-test framework in Phase 1 — Playwright smoke test is QUAL-02, Phase 7) |
| **Config file** | `pipeline/pyproject.toml` (none yet — Wave 0 installs); `app/package.json`, `app/eslint.config.ts` (none yet — Wave 0 scaffolds) |
| **Quick run command** | `cd pipeline && uv run pytest -q` / `cd app && npm run build` |
| **Full suite command** | `cd pipeline && uv run pytest` + `cd app && npm run build && npm run lint && npm run format:check` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run the quick command for the side the task touched (pipeline or app)
- **After every plan wave:** Run the full suite command (both sides)
- **Before `/gsd-verify-work`:** Full suite must be green, plus a local dry-run of the `ci.yml` command sequence (no remote CI run yet — D-18)
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 1-01-01 | 01-01 | 1 | SETUP-02, SETUP-03 | T-01-01, T-01-SC | Every package approved by a human before any install | manual (blocking-human checkpoint) | — (approval recorded in 01-01-SUMMARY.md) | n/a | ⬜ pending |
| 1-02-01 | 01-02 | 2 | SETUP-01, SETUP-02, D-12 | T-01-SC | Single tracked PDF; deps from uv.lock | smoke (tracer) | `uv run --directory pipeline pytest -q` | ❌ W0 (task creates `pipeline/tests/test_rauchtest.py`) | ⬜ pending |
| 1-02-02 | 01-02 | 2 | SETUP-05, D-12 | T-01-02, T-01-03 | pdf_pfad outside project root rejected; incomplete/malformed TOML rejected with named KonfigurationsFehler | unit (TDD) | `uv run --directory pipeline pytest -q` | ❌ W0 (task creates `pipeline/tests/test_konfiguration.py`) | ⬜ pending |
| 1-02-03 | 01-02 | 2 | SETUP-01, SETUP-02, SETUP-05 | T-01-04, T-01-05 | Unknown `--jahr` exits 1 with German error | cli/lint | `uv run --directory pipeline ruff check .` + `uv run --directory pipeline ruff format --check .` + `uv run --directory pipeline pytest -q` + `uv run --directory pipeline python alle.py --jahr 2026` | ❌ W0 (task creates `pipeline/tests/test_alle.py`) | ⬜ pending |
| 1-03-01 | 01-03 | 2 | SETUP-03 | T-01-07, T-01-SC | Unaudited scaffold extras stripped before install | build (tracer) | `npm --prefix app run build` | ❌ W0 (task scaffolds `app/`) | ⬜ pending |
| 1-03-02 | 01-03 | 2 | SETUP-03, QUAL-01 | T-01-06 | No third-party host referenced; icons self-hosted | typecheck/lint/format/build | `npm --prefix app run type-check` + `npm --prefix app run lint` + `npm --prefix app run format:check` + `npm --prefix app run build` | ✅ after 1-03-01 | ⬜ pending |
| 1-04-01 | 01-04 | 3 | SETUP-03 | T-01-08 | Demo figures always show the Beispieldaten notice | build + format check (tracer) | `npm --prefix app run build` + node transpile check of `app/src/charts/format.ts` (see 01-04 Task 1 verify) | ✅ after 01-03 | ⬜ pending |
| 1-04-02 | 01-04 | 3 | SETUP-03 | T-01-08 | ChartCard renders the notice itself when `beispieldaten` is set | build + grep | `npm --prefix app run build` | ✅ | ⬜ pending |
| 1-04-03 | 01-04 | 3 | SETUP-03, QUAL-01 | T-01-09 | No raw-HTML directive in app/src | typecheck/lint/format/build | `npm --prefix app run type-check` + `npm --prefix app run lint` + `npm --prefix app run format:check` + `npm --prefix app run build` | ✅ | ⬜ pending |
| 1-05-01 | 01-05 | 4 | QUAL-01 | T-01-10, T-01-11, T-01-SC | Actions SHA-pinned; token `contents: read`; installs only from lockfiles | CI replay (tracer) | `(cd pipeline && uv sync --locked && uv run ruff check . && uv run ruff format --check . && uv run pytest)` + `(cd app && npm ci && npm run type-check && npm run lint && npm run format:check && npm run build)` | ❌ W0 (task creates `.github/workflows/ci.yml`) | ⬜ pending |
| 1-05-02 | 01-05 | 4 | SETUP-04 | — | N/A | doc grep | phrase checks + GSD block equality on `.claude/CLAUDE.md` (see 01-05 Task 2 verify) | ✅ | ⬜ pending |
| 1-05-03 | 01-05 | 4 | SETUP-01 (D-05) | — | N/A | doc grep | `head -n 1 LICENSE` = `MIT License` + README phrase checks | ❌ W0 (task creates README.md, LICENSE) | ⬜ pending |

*Task IDs filled in by the planner. Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `pipeline/tests/test_rauchtest.py` — covers SETUP-02, SETUP-05, D-12 (created by task 1-02-01, extended by 1-02-02)
- [ ] `pipeline/jahrgaenge/2026.toml` + `2026_sollwerte.toml` — data files the tests load (1-02-01 minimal, 1-02-02 complete)
- [ ] `pipeline/ostbevern/konfiguration.py` — loader used by tests and scripts, D-09 (1-02-01, 1-02-02)
- [ ] `app/` scaffold via `npm create vue@3.24.0` (SETUP-03; task 1-03-01)
- [ ] `app/package.json` script `format:check` (`prettier --check src/`; task 1-03-02)
- [ ] `uv add --dev pytest ruff` — framework install (task 1-02-01, after the 1-01-01 package approval)

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| GitHub Actions workflow runs green on push | QUAL-01 | No GitHub remote exists yet (D-18) | After the remote is created, push and check the Actions tab |
| CLAUDE.md lists commands and conventions | SETUP-04 | Documentation content | Read `CLAUDE.md`; grep checks cover presence of key terms |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
