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
| 1-xx-xx | TBD | TBD | SETUP-02 | — | N/A | smoke | `cd pipeline && uv run pytest -q` | ❌ W0 | ⬜ pending |
| 1-xx-xx | TBD | TBD | SETUP-05 | — | N/A | unit | `cd pipeline && uv run pytest -q -k jahrgangsdatei` | ❌ W0 | ⬜ pending |
| 1-xx-xx | TBD | TBD | D-12 | — | N/A | unit/smoke | `cd pipeline && uv run pytest -q -k "sollwertdatei or pdf"` | ❌ W0 | ⬜ pending |
| 1-xx-xx | TBD | TBD | SETUP-03 | — | N/A | build | `cd app && npm run build` | ❌ W0 | ⬜ pending |
| 1-xx-xx | TBD | TBD | QUAL-01 | — | N/A | typecheck/lint | `cd app && npm run type-check && npm run lint` | ❌ W0 | ⬜ pending |

*Task IDs filled in by the planner. Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `pipeline/tests/test_rauchtest.py` — covers SETUP-02, SETUP-05, D-12
- [ ] `pipeline/jahrgaenge/2026.toml` + `2026_sollwerte.toml` — data files the tests load
- [ ] `pipeline/ostbevern/konfiguration.py` — loader used by tests and scripts (D-09)
- [ ] `app/` scaffold via `npm create vue@latest` (SETUP-03)
- [ ] `app/package.json` script `format:check` (`prettier --check src/`)
- [ ] `cd pipeline && uv add --dev pytest` — framework install

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
