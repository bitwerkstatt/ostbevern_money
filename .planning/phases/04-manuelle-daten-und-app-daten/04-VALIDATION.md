---
phase: "4"
slug: "manuelle-daten-und-app-daten"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-10-02"
---

# Phase 4 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest ≥ 9.1.1 (installed in Phase 1); app side: `vue-tsc` type-check against `app/src/data/typen.ts` |
| **Config file** | `pipeline/pyproject.toml` `[tool.pytest.ini_options]` (`testpaths=["tests"]`, `pythonpath=["."]`) |
| **Quick run command** | `uv run --directory pipeline pytest tests/<datei>.py -x` (`test_manuell.py`, `test_stellenplan.py`, `test_texte.py`, `test_app_daten.py`) |
| **Full suite command** | `uv run --directory pipeline pytest` |
| **Estimated runtime** | ~90 seconds (some tests read real PDF pages) |

---

## Sampling Rate

- **After every task commit:** Run the targeted `pytest` file for the module just changed
- **After every plan wave:** Run `uv run --directory pipeline pytest`
- **Before `/gsd-verify-work`:** Full suite green, plus `uv run --directory pipeline python alle.py --jahr 2026` followed by `git diff --exit-code -- daten app/src/data` (simulates D-24), plus `npm --prefix app run type-check` (in a scratch copy on Linux, see STATE.md)
- **Max feedback latency:** 90 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| TBD | TBD | TBD | MANU-01..05 | — | N/A | unit | `uv run --directory pipeline pytest tests/test_manuell.py -k schema -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | MANU-06 | — | N/A | unit | `uv run --directory pipeline pytest tests/test_manuell.py -k meta -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | MANU-07 | — | N/A | unit | `uv run --directory pipeline pytest tests/test_manuell.py -k readme -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | MANU-08 | T-4 (placeholder injection) | Unknown placeholder key aborts step 07 | unit | `uv run --directory pipeline pytest tests/test_texte.py -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | PRUEF-05 | — | N/A | integration | `uv run --directory pipeline pytest tests/test_manuell.py -k regel5 -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | EXTR-10 | — | N/A | unit+integration | `uv run --directory pipeline pytest tests/test_stellenplan.py -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | DATA-01 | T-4 (name disclosure) | No person names in `app/src/data/*.json` | unit | `uv run --directory pipeline pytest tests/test_app_daten.py -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | DATA-02 | — | N/A | unit | `uv run --directory pipeline pytest tests/test_app_daten.py -k kl_knoten -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | DATA-03 | — | N/A | unit | `uv run --directory pipeline pytest tests/test_app_daten.py -k zuschussbedarf -x` | ❌ W0 | ⬜ pending |
| TBD | TBD | TBD | PRUEF-10 | — | N/A | integration | `uv run --directory pipeline python alle.py --jahr 2026 && git diff --exit-code -- daten app/src/data` | ✅ alle.py (05/07 missing) | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `pipeline/tests/test_manuell.py` — MANU-01..07, PRUEF-05
- [ ] `pipeline/tests/test_stellenplan.py` — EXTR-10
- [ ] `pipeline/tests/test_texte.py` — MANU-08
- [ ] `pipeline/tests/test_app_daten.py` — DATA-01..03, extended person-name scan over `app/src/data/`
- [ ] Optional `manuelle_daten` fixture in `pipeline/tests/conftest.py` if several test files read the same CSVs
- No framework install needed — pytest already present

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Erklärtexte are fachlich correct and in Du-Anrede | MANU-08 | D-17: user signs off on content before commit | Checkpoint in plan: user reads `texte/erklaerungen.md` against the cited Vorbericht pages |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 90s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
