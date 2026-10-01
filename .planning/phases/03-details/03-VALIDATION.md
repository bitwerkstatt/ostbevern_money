---
phase: "3"
slug: "details"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: draft
nyquist_compliant: false
wave_0_complete: false
created: "2026-10-01"
---

# Phase 3 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1 |
| **Config file** | `pipeline/pyproject.toml` |
| **Quick run command** | `uv run --directory pipeline pytest tests/test_produkte.py tests/test_investitionen.py tests/test_querschnitte.py -x` |
| **Full suite command** | `uv run --directory pipeline pytest` |
| **Estimated runtime** | ~60 seconds |

---

## Sampling Rate

- **After every task commit:** Run `uv run --directory pipeline pytest tests/test_<modul>.py -x`
- **After every plan wave:** Run `uv run --directory pipeline pytest`
- **Before `/gsd-verify-work`:** Full suite must be green, and `uv run --directory pipeline python alle.py --jahr 2026` must report Regeln 1–4 und 6–8 grün in `konsistenz.md`
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| (filled by planner) | | | EXTR-06 | — | 63 Produkte vollständig, Bindungsgrad normalisiert | integration | `uv run --directory pipeline pytest tests/test_produkte.py -x` | ❌ W0 | ⬜ pending |
| (filled by planner) | | | EXTR-06 | D-09 | Keine Personennamen unter `daten/` | integration | `uv run --directory pipeline pytest tests/test_produkte.py::test_keine_personennamen -x` | ❌ W0 | ⬜ pending |
| (filled by planner) | | | EXTR-07 | — | N/A | integration | `uv run --directory pipeline pytest tests/test_produkte.py::test_steuer_istwerte_160101 -x` | ❌ W0 | ⬜ pending |
| (filled by planner) | | | EXTR-08 | — | N/A | integration | `uv run --directory pipeline pytest tests/test_produkte.py::test_erlaeuterung_ohne_zu_nr -x` | ❌ W0 | ⬜ pending |
| (filled by planner) | | | EXTR-09 | — | N/A | integration | `uv run --directory pipeline pytest tests/test_investitionen.py -x` | ❌ W0 | ⬜ pending |
| (filled by planner) | | | PRUEF-06 | — | N/A | integration | `uv run --directory pipeline pytest tests/test_pruefung.py -k regel6 -x` | ❌ W0 | ⬜ pending |
| (filled by planner) | | | PRUEF-07 | — | N/A | integration | `uv run --directory pipeline pytest tests/test_pruefung.py -k regel7 -x` | ❌ W0 | ⬜ pending |
| (filled by planner) | | | PRUEF-08 | — | N/A | integration | `uv run --directory pipeline pytest tests/test_pruefung.py -k regel8 -x` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `pipeline/tests/test_freitext.py` — Silbentrennung, `(cid:15)`-Split, Leerzeichen-Rekonstruktion
- [ ] `pipeline/tests/test_produkte.py` — EXTR-06, EXTR-07, EXTR-08, D-09-Datenschutztest
- [ ] `pipeline/tests/test_investitionen.py` — EXTR-09, Maßnahmen-ID-Trennung, Kassenwirksamkeit
- [ ] `pipeline/tests/test_querschnitte.py` — Datenquelle für PRUEF-07
- [ ] `pipeline/tests/test_pruefung.py` (Erweiterung) — PRUEF-06, PRUEF-07, PRUEF-08

Framework-Installation nicht nötig, pytest ist vorhanden.

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
