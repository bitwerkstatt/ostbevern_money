---
phase: "2"
slug: "kernzahlen"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
created: "2026-10-01"
validated: "2026-10-01"
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
| 2-01-02 | 02-01 | 1 | EXTR-01 | — | N/A | unit | `uv run --directory pipeline pytest tests/test_zahlen.py -x` | ✅ | ✅ green (37 passed) |
| 2-02-01 | 02-02 | 2 | EXTR-02 | — | N/A | unit | `uv run --directory pipeline pytest tests/test_seiten.py tests/test_hierarchie.py -x` | ✅ | ✅ green (22 passed) |
| 2-02-02 | 02-02 | 2 | EXTR-03 | — | N/A | unit | `uv run --directory pipeline pytest tests/test_hierarchie.py -x` | ✅ | ✅ green (9 passed) |
| 2-01-01, 2-04-01, 2-04-02 | 02-01, 02-04 | 1, 3 | EXTR-04 | — | N/A | unit | `uv run --directory pipeline pytest tests/test_plaene.py -k ergebnisplan -x` | ✅ | ✅ green (8 passed) |
| 2-03-01, 2-04-02 | 02-03, 02-04 | 2, 3 | EXTR-05 | — | N/A | unit | `uv run --directory pipeline pytest tests/test_plaene.py -k finanzplan -x` | ✅ | ✅ green (5 passed) |
| 2-03-02, 2-04-01 | 02-03, 02-04 | 2, 3 | PRUEF-01 | — | N/A | unit | `uv run --directory pipeline pytest tests/test_pruefung.py -k regel1 -x` | ✅ | ✅ green (4 passed) |
| 2-05-02 | 02-05 | 4 | PRUEF-02 | — | N/A | unit | `uv run --directory pipeline pytest tests/test_pruefung.py -k regel2 -x` | ✅ | ✅ green (2 passed) |
| 2-05-02 | 02-05 | 4 | PRUEF-03 | — | N/A | unit | `uv run --directory pipeline pytest tests/test_pruefung.py -k regel3 -x` | ✅ | ✅ green (3 passed) |
| 2-01-01, 2-01-03, 2-03-01, 2-05-03 | 02-01, 02-03, 02-05 | 1, 2, 4 | PRUEF-04 | — | N/A | unit | `uv run --directory pipeline pytest tests/test_pruefung.py -k regel4 -x` | ✅ | ✅ green (6 passed) |
| 2-01-03, 2-03-03, 2-05-03 | 02-01, 02-03, 02-05 | 1, 2, 4 | PRUEF-09 | — | N/A | integration | `uv run --directory pipeline pytest tests/test_pruefung.py -k konsistenzbericht -x` | ✅ | ✅ green (6 passed) |
| 2-05-01 | 02-05 | 4 | PRUEF-09 (alle.py, D-09) | — | N/A | integration | `uv run --directory pipeline pytest tests/test_alle.py -x` | ✅ | ✅ green (4 passed) |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `pipeline/tests/test_zahlen.py` — EXTR-01 (pure string tests, D-07)
- [x] `pipeline/tests/test_seiten.py` — EXTR-02, reads real PDF pages (D-07)
- [x] `pipeline/tests/test_hierarchie.py` — EXTR-03, Anhang-A start pages vs. checked-in CSVs (D-06)
- [x] `pipeline/tests/test_plaene.py` — EXTR-04/05, reads real PDF pages (D-07)
- [x] `pipeline/tests/test_pruefung.py` — PRUEF-01 to PRUEF-09, reads checked-in CSVs (D-06), including the formula chain
- No framework install needed — pytest already present

---

## Manual-Only Verifications

All phase behaviors have automated verification.

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 60s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-10-01

---

## Validation Audit 2026-10-01

| Metric | Count |
|--------|-------|
| Gaps found | 0 |
| Resolved | 0 |
| Escalated | 0 |

All 10 phase requirements (EXTR-01..05, PRUEF-01..04, PRUEF-09) are COVERED by green automated tests. Full suite: 152 passed (`uv run --directory pipeline pytest`, ~43 s); `alle.py --jahr 2026` exits 0 and regenerates `daten/` byte-identically; Regeln 1–4 grün.
