---
phase: "3"
slug: "details"
# status lifecycle: draft (seeded by plan-phase) → validated (set by validate-phase §6)
# audit-milestone §5.5 distinguishes NOT-VALIDATED (draft) from PARTIAL (validated + nyquist_compliant: false) (#2117)
status: validated
nyquist_compliant: true
wave_0_complete: true
created: "2026-10-01"
validated: "2026-10-02"
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
| 03-01-T1 | 03-01 | 1 | PRUEF-07 | T-03-01, T-03-03 | Regel 7 reads only querschnitte.csv; pruefung.py imports no PDF module | integration | `uv run --directory pipeline pytest tests/test_spalten.py tests/test_querschnitte.py tests/test_pruefung.py -x -q` | ✅ | ✅ green |
| 03-01-T2 | 03-01 | 1 | PRUEF-07 | T-03-02 | malformed Querschnitt row/block/PG set aborts with PDF page | integration | `uv run --directory pipeline pytest tests/test_querschnitte.py -x -q` | ✅ | ✅ green |
| 03-01-T3 | 03-01 | 1 | PRUEF-07 | T-03-03 | alle.py exits 1 on QuerschnitteFehler; stale Regel-7 befund turns report rot | unit | `uv run --directory pipeline pytest tests/test_alle.py tests/test_konfiguration.py tests/test_pruefung.py -x -q` | ✅ | ✅ green |
| 03-02-T1 | 03-02 | 2 | EXTR-09 | T-03-05, T-03-06 | unknown Konto aborts; Finanzierungs-Konten 692/792 verified against TFP Z. 33/35 (P and PB level, `-k finanzierungskonten`, added by audit) and excluded | integration | `uv run --directory pipeline pytest tests/test_freitext.py tests/test_investitionen.py tests/test_plaene.py -x -q` | ✅ | ✅ green |
| 03-02-T2 | 03-02 | 2 | EXTR-09 | T-03-04 | Kassenwirksamkeit values only in ve_faelligkeiten.csv, never in sums | integration | `uv run --directory pipeline pytest tests/test_investitionen.py tests/test_alle.py -x -q` | ✅ | ✅ green |
| 03-02-T3 | 03-02 | 2 | PRUEF-06 | T-03-04 | Regel 6 product/total sums and VE = Σ Fälligkeiten | integration | `uv run --directory pipeline pytest tests/test_pruefung.py -x -q -k regel6` | ✅ | ✅ green |
| 03-03-T1 | 03-03 | 3 | EXTR-09 | T-03-08 | PB lists stored only under daten/zwischen/, investitionen.csv byte-identical | integration | `uv run --directory pipeline pytest tests/test_investitionen.py -x -q` | ✅ | ✅ green |
| 03-03-T2 | 03-03 | 3 | PRUEF-06 | T-03-07 | one-sided measure is a Lücke that befunde.md cannot cover | integration | `uv run --directory pipeline pytest tests/test_pruefung.py tests/test_alle.py -x -q` | ✅ | ✅ green |
| 03-04-T1 | 03-04 | 4 | EXTR-06 | T-03-09, T-03-10 | no personal name in any file under daten/, none printed in test output | integration | `uv run --directory pipeline pytest tests/test_produkte.py -q -k keine_personennamen` | ✅ | ✅ green |
| 03-04-T1 | 03-04 | 4 | EXTR-06 | — | 63 Produkte, Bindungsgrad normalisiert, D-11 field types | integration | `uv run --directory pipeline pytest tests/test_freitext.py tests/test_produkte.py tests/test_konfiguration.py -x -q` | ✅ | ✅ green |
| 03-04-T2 | 03-04 | 4 | EXTR-08 | T-03-12 | D-04 plausibility aborts; block without zu Nr. (S. 184) kept | integration | `uv run --directory pipeline pytest tests/test_produkte.py -x -q` | ✅ | ✅ green |
| 03-04-T3 | 03-04 | 4 | EXTR-06, EXTR-08 | — | alle.py runs Schritt 03 deterministically (byte-identity test added by audit) | unit | `uv run --directory pipeline pytest tests/test_alle.py tests/test_produkte.py -x -q -k "fehler or byte_identisch"` | ✅ | ✅ green |
| 03-05-T1 | 03-05 | 5 | EXTR-07 | T-03-13 | "–" never becomes a row; Steuer-Istwerte 160101; Stichtag hint per year | integration | `uv run --directory pipeline pytest tests/test_zahlen.py tests/test_produkte.py -x -q` | ✅ | ✅ green |
| 03-05-T2 | 03-05 | 5 | PRUEF-08 | T-03-14, T-03-15 | Regel 8 Lücken turn the report rot; final D-09 scan | integration | `uv run --directory pipeline pytest tests/test_pruefung.py -x -q -k regel8` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Die Testdateien entstehen test-first innerhalb der jeweiligen Tasks (tdd="true"); es gibt keinen separaten Wave-0-Plan.

- [x] `pipeline/tests/conftest.py` — Session-Fixtures `pdf_klassifikation`, `jahrgang` (03-01-T1)
- [x] `pipeline/tests/test_spalten.py` — x-Koordinaten-Zuordnung (03-01-T1)
- [x] `pipeline/tests/test_querschnitte.py` — Datenquelle für PRUEF-07 (03-01-T1/T2)
- [x] `pipeline/tests/test_freitext.py` — Silbentrennung, Eurozeichen, Leerzeichen vor Komma (03-02-T1, 03-04-T1)
- [x] `pipeline/tests/test_investitionen.py` — EXTR-09, Maßnahmen-ID-Trennung, Kassenwirksamkeit, PB-Listen (03-02-T1/T2, 03-03-T1)
- [x] `pipeline/tests/test_produkte.py` — EXTR-06, EXTR-07, EXTR-08, D-09-Datenschutztest (03-04-T1/T2, 03-05-T1)
- [x] `pipeline/tests/test_pruefung.py` (Erweiterung) — PRUEF-06, PRUEF-07, PRUEF-08 (03-01, 03-02-T3, 03-03-T2, 03-05-T2)

Framework-Installation nicht nötig, pytest ist vorhanden.

---

## Manual-Only Verifications

All phase behaviors have automated verification.

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 60s (targeted commands; full suite ~205 s)
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** validated 2026-10-02 (validate-phase audit)

---

## Validation Audit 2026-10-02

| Metric | Count |
|--------|-------|
| Gaps found | 2 |
| Resolved | 2 |
| Escalated | 0 |

- **G1 (03-02-T1, EXTR-09):** `_pruefe_finanzierungskonten` (692/792 vs Teilfinanzplan Z. 33/35) had no failing-path test; the PB-16 manipulation test aborts earlier in the Saldo check. Added `test_finanzierungskonten_weichen_vom_teilfinanzplan_ab_bricht_ab` (product level, Z. 33) and `test_finanzierungskonten_pb_weichen_vom_teilfinanzplan_ab_bricht_ab` (PB level, Z. 35).
- **G2 (03-04-T3, EXTR-06/08):** no test asserted deterministic Schritt 03 output. Added `test_produkte_json_erlaeuterungen_csv_grundzahlen_csv_byte_identisch` (~4 s).
- Full suite after audit: 298 passed; ruff check/format clean; `daten/` unchanged.
