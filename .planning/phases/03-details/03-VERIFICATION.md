---
phase: 03-details
verified: 2026-10-02T12:30:00Z
status: passed
score: 11/11 must-haves verified
covered_files: [".planning/phases/03-details/03-01-PLAN.md", ".planning/phases/03-details/03-01-SUMMARY.md", ".planning/phases/03-details/03-02-PLAN.md", ".planning/phases/03-details/03-02-SUMMARY.md", ".planning/phases/03-details/03-03-PLAN.md", ".planning/phases/03-details/03-03-SUMMARY.md", ".planning/phases/03-details/03-04-PLAN.md", ".planning/phases/03-details/03-04-SUMMARY.md", ".planning/phases/03-details/03-05-PLAN.md", ".planning/phases/03-details/03-05-SUMMARY.md", ".planning/phases/03-details/03-REVIEW-DISPOSITION.md", ".planning/phases/03-details/03-REVIEW-FIX.md", ".planning/phases/03-details/03-REVIEW.md", ".planning/phases/03-details/03-SECURITY.md", ".planning/phases/03-details/03-VALIDATION.md", "daten/aufbereitet/erlaeuterungen.csv", "daten/aufbereitet/grundzahlen.csv", "daten/aufbereitet/investitionen.csv", "daten/aufbereitet/produkte.json", "daten/aufbereitet/ve_faelligkeiten.csv", "daten/pruefberichte/befunde.md", "daten/pruefberichte/konsistenz.md", "daten/zwischen/investitionen_pb.csv", "daten/zwischen/querschnitte.csv", "pipeline/03_produktinfos.py", "pipeline/04_investitionen.py", "pipeline/06_pruefen.py", "pipeline/alle.py", "pipeline/jahrgaenge/2026.toml", "pipeline/jahrgaenge/2026_sollwerte.toml", "pipeline/ostbevern/freitext.py", "pipeline/ostbevern/investitionen.py", "pipeline/ostbevern/konfiguration.py", "pipeline/ostbevern/pdf.py", "pipeline/ostbevern/produkte.py", "pipeline/ostbevern/pruefung.py", "pipeline/ostbevern/querschnitte.py", "pipeline/ostbevern/schema.py", "pipeline/ostbevern/spalten.py", "pipeline/ostbevern/zahlen.py", "pipeline/tests/conftest.py", "pipeline/tests/test_alle.py", "pipeline/tests/test_freitext.py", "pipeline/tests/test_investitionen.py", "pipeline/tests/test_konfiguration.py", "pipeline/tests/test_produkte.py", "pipeline/tests/test_pruefung.py", "pipeline/tests/test_querschnitte.py", "pipeline/tests/test_schema.py", "pipeline/tests/test_spalten.py", "pipeline/tests/test_zahlen.py"]
covered_digest: "v2:sha256:5a725f5228a3f93b995a27e3f2dfdd5dfab252817ba3a2966f15931089726476"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: passed
  previous_score: 11/11
  gaps_closed: []
  gaps_remaining: []
  regressions: []
---

# Phase 3: Details — Verification Report (Re-verification)

**Phase Goal:** Alle 63 Produkte sind inhaltlich vollständig beschrieben (Produktinformationen, Bindungsgrad, Grundzahlen, Erläuterungen), und die Investitionsmaßnahmen stimmen mit den Finanzplänen überein.
**Verified:** 2026-10-02T12:30:00Z
**Status:** passed
**Re-verification:** Yes — after code-review fix round and Nyquist-validation test additions (stale prior verification at commit b538ea9; current HEAD 87f0580)

## Why Re-verification Was Needed

The prior VERIFICATION.md (status: passed, 11/11, verified at commit b538ea9) covered a fingerprint that predates seven commits touching `pipeline/`:

- `e842ff3` WR-01 — `ordne_spalten` tolerance computed per-anchor-pair instead of globally
- `20bab38` WR-02 — `test_alle.py` produkte mock corrected to the real 3-tuple contract
- `0a758a6` IN-01 — `alle.py` Querschnitte label de-duplicated from "Schritt 06"
- `b590bdb` IN-02 — CLI help text documents all written artifacts
- `12e7b93` IN-03 — `schema.schreibe_csv` casts with `strict=True`
- `b857f29` — Nyquist validation tests added (Finanzierungskonten G1 tests, byte-identity G2 test); `03-VALIDATION.md` set to `validated` / `nyquist_compliant: true`
- `a531fb6` CR-01 — round-trip check added to `schreibe_csv` closing the gap IN-03's `strict=True` alone did not cover (Float→Int truncation)

All 6 findings in `03-REVIEW-DISPOSITION.md` are recorded `disposition: fixed`, `open: 0`. This re-verification re-checks every roadmap Success Criterion and plan-level must-have against the current HEAD (`87f0580`), independently re-derives the data values (not trusting SUMMARY/REVIEW-FIX narrative), and confirms the `ordne_spalten`/`schreibe_csv` changes did not alter any generated data.

## Goal Achievement

### Observable Truths (Roadmap Success Criteria)

| # | Truth (ROADMAP.md Success Criterion) | Status | Evidence |
|---|---------------------------------------|--------|----------|
| 1 | `produkte.json` enthält alle 63 Produkte mit Fachbereich, Gremium, Beschreibung, Leistungen, Auftragsgrundlage, Klassifizierung, Zielgruppe, Zielen, PDF-Seiten und Bindungsgrad (normalisiert + original); Regel 8 grün | ✓ VERIFIED | Directly parsed `daten/aufbereitet/produkte.json` in this session: 63 records. Sample `030101`: `bindungsgrad="teils"`, `bindungsgrad_original="teils pflichtig teils freiwillig"`, `gremium="Bildungs-, Generationen- und Sozialausschuss"`, `leistungen[0]="Betrieb der Ambrosius-Grundschule"`, `pdf_seiten=[151,152,153,154]` — matches Spez. 4.2. `konsistenz.md` (current HEAD): `Regel 8 – Vollständigkeit der Produkte \| grün \| 820 \| 0 \| 0 \| 0`. |
| 2 | `grundzahlen.csv` führt Kennzahlen je Produkt mit Einheit, Jahr, Stichtagshinweis, inkl. Steuer-Istwerte 2022–2025 aus 160101 (Gewerbesteuer 2023 = 4.771.497 €); Erläuterungsposten je Produkt mit Betrag, Text, Zeilenbezug | ✓ VERIFIED | Direct `grep` on current file: `160101,1,,Gewerbesteuer (Im Teilplan Zeile 01),EUR,2023,4771497.0,0,,280` present, plus 2022/2024/2025 sibling rows with the `Ist-Wert 2025: Stand Ende 2025.` hint. `erlaeuterungen.csv` unchanged from prior verification (not touched by the review-fix diff — confirmed via `git diff b538ea9..HEAD -- daten/` showing zero changes to any `daten/` file). |
| 3 | `investitionen.csv` stammt nur aus Produktseiten; Summe je Produkt = TFP Z. 23/30; Summe aller Maßnahmen 2026 = 7.224.830 € / 12.280.484 € (Regel 6); „(Kassenwirksamkeit)" nur in `ve_faelligkeiten.csv`, nicht in Summen | ✓ VERIFIED | Recomputed directly via polars in this session on current `investitionen.csv`: Ansatz 2026 `einzahlung` sum = 7224830, `auszahlung` sum = 12280484 — exact match. 0 rows with Konto prefix 692/792. `konsistenz.md`: `Regel 6 \| grün \| 1964 \| 0 \| 0 \| 8`. |
| 4 | Querschnitte ab S. 291 stimmen mit eigenen PG-Aggregaten überein (Regel 7); `konsistenz.md` meldet Regeln 1–4 und 6–8 als grün | ✓ VERIFIED | `konsistenz.md` at current HEAD: `Gesamtstatus: grün`; `Regel 7 \| grün \| 1152 \| 0 \| 0 \| 18`; all of Regeln 1,2,3,4,6,7,8 read `grün` in the overview table (re-checked by direct grep this session). Orchestrator's fresh `alle.py --jahr 2026` run (reported in task context) reproduced this with `git status --short daten/` empty afterward — confirms determinism holds after the code-review fixes. |

**Score:** 4/4 roadmap success criteria verified; 7/7 plan-level must-have clusters verified. No regressions, no gaps, no new human-verification items.

### Plan-Level Must-Have Highlights (focused re-check of changed code)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 5 | WR-01 fix: `ordne_spalten` tolerance is now computed per-anchor-pair (local neighbours), not globally, so a duplicate/zero-distance anchor pair no longer zeroes tolerance for the whole table | ✓ VERIFIED | Read `pipeline/ostbevern/spalten.py` diff directly: `toleranz` is now computed inside the per-word loop from the two sorted neighbours of the matched anchor's rank, not from a single table-wide `min(abstaende)`. New regression test `test_ordne_spalten_doppelter_anker_bricht_nicht_die_ganze_zuordnung` (anchors `[100.0, 100.0, 500.0]`, word at `500.0`) — ran this exact test in this session: `1 passed`. Confirmed the fix does not change parsing of the real PDF (no `daten/` changes since b538ea9; `querschnitte.csv`/`investitionen*.csv` which depend on `ordne_spalten` are byte-identical). |
| 6 | CR-01 fix: `schema.schreibe_csv`'s `strict=True` cast is supplemented with a round-trip check that catches Float→Int precision loss `strict=True` alone misses | ✓ VERIFIED | Read `pipeline/ostbevern/schema.py` diff: after `cast(spalten, strict=True)`, every Float-sourced column is cast back to its original dtype and compared with `.equals(null_equal=True)`; mismatch raises `SchemaFehler`. New `pipeline/tests/test_schema.py` — ran both tests directly in this session: `test_schreibe_csv_lehnt_fraktionalen_float_bei_int_narrowing_ab` and `test_schreibe_csv_schreibt_ganzzahligen_float_bei_int_narrowing` → `2 passed`. This closes the gap the prior review (`ced6db8`) found in IN-03's original `strict=True`-only fix. |
| 7 | WR-02/IN-01/IN-02 fixes: test fixture now matches the real 3-tuple return of `extrahiere_produkte`; "Schritt 06" label de-duplicated; CLI help text documents all written artifacts | ✓ VERIFIED | Read diffs directly: `test_alle.py`'s `_produkte_ergebnisse()` now returns a 3-tuple (produkte/grundzahlen/erlaeuterungen) matching production; `alle.py`'s Querschnitte line dropped the duplicated "Schritt 06:" prefix (now reads "Querschnitte: N Werte geschrieben." standalone, "Schritt 06:" reserved for the Prüfung step that follows); `03_produktinfos.py`/`04_investitionen.py` help strings now list Grundzahlen/PB-Investitionslisten. None of these are behavior-affecting for generated data (cosmetic label + test-fixture correctness only). |
| 8 | Nyquist validation additions (G1/G2): Finanzierungskonten cross-check against Teilfinanzplan Z.33/35 is exercised by a failing-path test at both P and PB level; Schritt 03 output (produkte.json/erlaeuterungen.csv/grundzahlen.csv) is proven byte-deterministic by regenerating into a tmp dir and diffing against checked-in files | ✓ VERIFIED | Read `test_investitionen.py`'s two new tests (`test_finanzierungskonten_weichen_vom_teilfinanzplan_ab_bricht_ab`, `..._pb_...`): each manipulates a copied `finanzplan.csv` by +1,000,000 on the relevant Zeile/Jahr/Wertart cell and asserts `InvestitionenFehler` with the matching "Teilfinanzplan Zeile 33/35" message. Read `test_produkte.py`'s new `test_produkte_json_erlaeuterungen_csv_grundzahlen_csv_byte_identisch`: copies seiten/hierarchie/ergebnisplan CSVs into `tmp_path`, re-runs `extrahiere_produkte`, asserts byte-for-byte equality against `daten/aufbereitet/`. `03-VALIDATION.md` frontmatter confirms `status: validated`, `nyquist_compliant: true`. |
| 9 | 03-04: No personal name (`Verantwortliche/r`, `Sachbearbeiter/innen`) reaches any file under `daten/` (D-09) — unaffected by the review-fix round | ✓ VERIFIED | `grep -rn "verantwortlich\|sachbearbeiter" daten/` (case-sensitive-safe check re-run this session) returns no hits; `daten/` has zero diff vs b538ea9, so this guarantee is unchanged. |
| 10 | 03-05: Grundzahlen units/hints/groups normalised (D-12/D-13) — unaffected by the review-fix round | ✓ VERIFIED | `grundzahlen.csv` byte-identical to prior verification (confirmed via empty `git diff b538ea9..HEAD -- daten/`); spot-checked rows above match Spez. values exactly. |
| 11 | Phase gate: `alle.py --jahr 2026` leaves `git status --porcelain daten/` empty; full pytest suite and ruff/CI-replay green at current HEAD | ✓ VERIFIED | Orchestrator evidence (this verification round): `uv sync --locked && ruff check . && ruff format --check . && pytest -q` → ruff clean, `300 passed` (up from 294 — the 6 new Nyquist/regression tests); `git status --short daten/` empty after the full `alle.py --jahr 2026` run. Independently re-confirmed in this session: `git status --short` on the whole repo shows no changes to `pipeline/` or `daten/`; targeted re-runs of the two touched test files (`test_schema.py`, `test_spalten.py`) → `8 passed`. |

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `daten/aufbereitet/produkte.json` | 63 products, no person names | ✓ VERIFIED | Unchanged since b538ea9 (no `daten/` diff); re-parsed directly, 63 records, sample matches spec |
| `daten/aufbereitet/grundzahlen.csv` | Grundzahlen incl. Steuer-Istwerte | ✓ VERIFIED | Unchanged; 160101 Gewerbesteuer 2023 row confirmed exact |
| `daten/aufbereitet/erlaeuterungen.csv` | Erläuterungsposten | ✓ VERIFIED | Unchanged since prior verification |
| `daten/aufbereitet/investitionen.csv` | Product-page investment measures | ✓ VERIFIED | Unchanged; sums recomputed directly = 7.224.830 € / 12.280.484 €, 0 rows with 692/792 |
| `daten/aufbereitet/ve_faelligkeiten.csv` | Kassenwirksamkeit maturities | ✓ VERIFIED | Unchanged since prior verification |
| `daten/zwischen/querschnitte.csv` | Control source for Regel 7 | ✓ VERIFIED | Unchanged; Regel 7 grün with 1152 Werte |
| `daten/zwischen/investitionen_pb.csv` | Control source for Regel 6 PB check | ✓ VERIFIED | Unchanged since prior verification |
| `daten/pruefberichte/konsistenz.md` | Regeln 1-4, 6-8 grün | ✓ VERIFIED | Gesamtstatus grün; all 7 rules grün (re-grepped directly this session) |
| `pipeline/ostbevern/schema.py` (CR-01 fix) | round-trip check on Float→Int narrowing | ✓ VERIFIED | Diff read directly; 2 named tests in `test_schema.py` pass |
| `pipeline/ostbevern/spalten.py` (WR-01 fix) | per-anchor-pair tolerance | ✓ VERIFIED | Diff read directly; 1 named regression test passes |
| `pipeline/tests/test_investitionen.py` (G1) | Finanzierungskonten Z.33/35 negative-path tests | ✓ VERIFIED | Both new tests read directly, assert `InvestitionenFehler` on manipulated data |
| `pipeline/tests/test_produkte.py` (G2) | byte-identity regeneration test | ✓ VERIFIED | New test read directly, compares tmp-regenerated vs checked-in bytes |

### Key Link Verification

| From | To | Via | Status |
|------|----|----|--------|
| `pipeline/alle.py` | `produkte.extrahiere_produkte` | module-attribute call, Schritt 03 (3-tuple contract, fixed in `test_alle.py`) | ✓ WIRED |
| `pipeline/ostbevern/schema.py` | all CSV writers across the pipeline | `schreibe_csv` round-trip guard applies to every caller uniformly | ✓ WIRED (single choke point, confirmed by reading call sites — no caller bypasses `schreibe_csv`) |
| `pipeline/ostbevern/spalten.py` | `querschnitte.py`, `investitionen.py` | `ordne_spalten` consumed by both PDF-column parsers | ✓ WIRED (both modules' generated CSVs are byte-identical post-fix, confirming the tolerance change is either a no-op on real data or strictly more permissive without breaking it) |
| `pipeline/ostbevern/pruefung.py` | `daten/aufbereitet/investitionen.csv` + Teilfinanzplan | Finanzierungskonten G1 cross-check, now test-covered on the failure path | ✓ WIRED |

### Data-Flow Trace (Level 4)

No regenerate-and-diff was performed independently in this verification pass (the orchestrator already ran `alle.py --jahr 2026` and reported an empty `git status --short daten/`, and this session's direct `git diff b538ea9..HEAD -- daten/` is empty, which is the stronger claim: the checked-in artifacts are provably untouched by the review-fix commits). All five generated artifacts trace to the same PDF→pipeline chain established in the initial verification; the round-trip/tolerance fixes touch guard logic, not the data-producing code paths that write the compared values.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| CR-01 round-trip guard rejects fractional Float→Int narrowing | `pytest tests/test_schema.py -q` (run this session) | `2 passed` | ✓ PASS |
| WR-01 per-anchor-pair tolerance regression | `pytest tests/test_spalten.py -q` (run this session) | `6 passed` (incl. new regression test) | ✓ PASS |
| Investitionssummen 2026 unchanged | direct polars recomputation on current `investitionen.csv` (this session) | `einzahlung=7224830, auszahlung=12280484, 692/792 rows=0` | ✓ PASS |
| Full workspace suite + lint (orchestrator, this round) | `uv sync --locked && ruff check . && ruff format --check . && pytest -q` | ruff clean; `300 passed in ~200s` | ✓ PASS |
| Working tree clean after full pipeline run | `git status --short daten/` (orchestrator, this round) | empty | ✓ PASS |
| No debt markers in changed files | `grep -nE "TBD\|FIXME\|XXX\|TODO\|HACK\|PLACEHOLDER"` over `spalten.py`, `schema.py`, `alle.py`, `03_produktinfos.py`, `04_investitionen.py`, and all 5 changed/added test files (this session) | no matches | ✓ PASS |

### Probe Execution

No `scripts/*/tests/probe-*.sh` convention exists in this project. N/A (unchanged from prior verification).

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|---|---|---|---|---|
| EXTR-06 | 03-04 | Produktinformationen aller 63 Produkte in `produkte.json` | ✓ SATISFIED | Unchanged data, 63 records, exact field set, re-confirmed this session |
| EXTR-07 | 03-05 | Grundzahlen je Produkt, Steuer-Istwerte 160101 | ✓ SATISFIED | Unchanged data, Gewerbesteuer 2023 = 4.771.497 confirmed directly |
| EXTR-08 | 03-04 | Erläuterungsposten je Produkt | ✓ SATISFIED | Unchanged data since prior verification |
| EXTR-09 | 03-02, 03-03 | Investitionsmaßnahmen nur aus Produktseiten; Kassenwirksamkeit separat | ✓ SATISFIED | Unchanged data, sums recomputed directly, 0 Finanzierungskonten rows |
| PRUEF-06 | 03-02, 03-03 | Investitionssummen je Produkt/Gesamt stimmen (7.224.830 €/12.280.484 €) | ✓ SATISFIED | Recomputed directly, exact match; Regel 6 grün |
| PRUEF-07 | 03-01 | Querschnitte S.291ff stimmen mit PG-Aggregaten | ✓ SATISFIED | Regel 7 grün, 1152 Werte |
| PRUEF-08 | 03-05 | Vollständigkeit: 63 Produkte mit allen Pflichtfeldern | ✓ SATISFIED | Regel 8 grün, 820 geprüfte Werte, 0 Lücken |

All 7 phase requirement IDs are marked `Complete` and mapped to `Phase 3` in `.planning/REQUIREMENTS.md`. No orphaned requirements (grep for "Phase 3" returns exactly these 7 IDs).

### Code Review Disposition (closed since prior verification)

`03-REVIEW-DISPOSITION.md` at current HEAD: `open: 0`, `total: 6`, all 6 findings (CR-01 critical, WR-01/WR-02 warning, IN-01/IN-02/IN-03 info) `disposition: fixed`. This supersedes the prior verification's note of "5 open findings, 0 critical, 0 blocking" — the incremental re-review (`ced6db8`) found that IN-03's original fix (bare `strict=True`) did not actually close the Float→Int truncation gap it targeted (CR-01, severity critical), and `a531fb6` closed it with the round-trip check verified above. No findings remain open.

### Anti-Patterns Found

None. Re-scanned all files changed since the prior verification (`spalten.py`, `schema.py`, `alle.py`, `03_produktinfos.py`, `04_investitionen.py`, and the 5 touched/added test files) for `TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER` and stub patterns — zero matches.

### Human Verification Required

None. Pipeline/backend phase, no user-facing UI. All re-checked items are verifiable programmatically and were verified directly against current-HEAD code and data in this session (not SUMMARY/REVIEW-FIX narrative).

### Gaps Summary

No gaps, no regressions. All 4 roadmap Success Criteria and all 7 plan-level must-have clusters remain verified at current HEAD (`87f0580`). The code-review fix round (CR-01, WR-01, WR-02, IN-01–03) and the Nyquist validation test additions did not alter any file under `daten/` — confirmed by an empty `git diff b538ea9..HEAD -- daten/` and by independently recomputing the key figures (Investitionssummen, Gewerbesteuer, product/field counts) directly from the current checked-in files rather than trusting prior claims. The two most consequential fixes (CR-01's round-trip check, WR-01's per-anchor-pair tolerance) are each backed by a newly added, directly-run passing test exercising the exact scenario they were meant to catch. The review disposition ledger shows 0 open findings. Full workspace suite (300 tests, up from 294) and ruff checks are green per the orchestrator's fresh run this round, and the working tree is clean.

---

_Verified: 2026-10-02T12:30:00Z_
_Verifier: Claude (gsd-verifier)_
