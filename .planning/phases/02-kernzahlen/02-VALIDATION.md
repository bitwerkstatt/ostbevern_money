---
phase: "2"
slug: "kernzahlen"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-10-01"
---

# Phase 2 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest ≥ 9.1.1 (installed in Phase 1) |
| **Config file** | `pipeline/pyproject.toml` `[tool.pytest.ini_options]` (`testpaths=["tests"]`, `pythonpath=["."]`) |
| **Quick run command** | `uv run --directory pipeline pytest tests/<datei>.py -x` (the file for the module being worked on) |
| **Full suite command** | `uv run --directory pipeline pytest` |
| **Estimated runtime** | ~60 seconds (real PDF pages are read in some tests) |

---

## Sampling Rate

- **After every task commit:** Run the targeted `pytest` file for the module just changed
- **After every plan wave:** Run `uv run --directory pipeline pytest`
- **Before `/gsd-verify-work`:** Full suite must be green, plus `uv run --directory pipeline ruff check .` and `ruff format --check .`
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 2-xx-xx | tbd | tbd | EXTR-01 | — | N/A | unit | `uv run --directory pipeline pytest tests/test_zahlen.py -x` | ❌ W0 | ⬜ pending |
| 2-xx-xx | tbd | tbd | EXTR-02 | — | N/A | unit | `uv run --directory pipeline pytest tests/test_seiten.py tests/test_hierarchie.py -x` | ❌ W0 | ⬜ pending |
| 2-xx-xx | tbd | tbd | EXTR-03 | — | N/A | unit | `uv run --directory pipeline pytest tests/test_hierarchie.py -x` | ❌ W0 | ⬜ pending |
| 2-xx-xx | tbd | tbd | EXTR-04 | — | N/A | unit | `uv run --directory pipeline pytest tests/test_plaene.py -k ergebnisplan -x` | ❌ W0 | ⬜ pending |
| 2-xx-xx | tbd | tbd | EXTR-05 | — | N/A | unit | `uv run --directory pipeline pytest tests/test_plaene.py -k finanzplan -x` | ❌ W0 | ⬜ pending |
| 2-xx-xx | tbd | tbd | PRUEF-01 | — | N/A | unit | `uv run --directory pipeline pytest tests/test_pruefung.py -k regel1 -x` | ❌ W0 | ⬜ pending |
| 2-xx-xx | tbd | tbd | PRUEF-02 | — | N/A | unit | `uv run --directory pipeline pytest tests/test_pruefung.py -k regel2 -x` | ❌ W0 | ⬜ pending |
| 2-xx-xx | tbd | tbd | PRUEF-03 | — | N/A | unit | `uv run --directory pipeline pytest tests/test_pruefung.py -k regel3 -x` | ❌ W0 | ⬜ pending |
| 2-xx-xx | tbd | tbd | PRUEF-04 | — | N/A | unit | `uv run --directory pipeline pytest tests/test_pruefung.py -k regel4 -x` | ❌ W0 | ⬜ pending |
| 2-xx-xx | tbd | tbd | PRUEF-09 | — | N/A | integration | `uv run --directory pipeline pytest tests/test_pruefung.py -k konsistenzbericht -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `pipeline/tests/test_zahlen.py` — EXTR-01 (pure string tests, D-07)
- [ ] `pipeline/tests/test_seiten.py` — EXTR-02, reads real PDF pages (D-07)
- [ ] `pipeline/tests/test_hierarchie.py` — EXTR-03, Anhang-A start pages vs. checked-in CSVs (D-06)
- [ ] `pipeline/tests/test_plaene.py` — EXTR-04/05, reads real PDF pages (D-07)
- [ ] `pipeline/tests/test_pruefung.py` — PRUEF-01 to PRUEF-09, reads checked-in CSVs (D-06), including the formula chain
- No framework install needed — pytest already present

---

## Manual-Only Verifications

All phase behaviors have automated verification.

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 60s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
