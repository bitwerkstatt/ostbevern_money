---
phase: 02-kernzahlen
verified: 2026-10-02T12:10:21Z
status: passed
score: 5/5 must-haves verified (roadmap Success Criteria); 10/10 requirement IDs satisfied
covered_files: [".planning/phases/02-kernzahlen/02-01-PLAN.md", ".planning/phases/02-kernzahlen/02-01-SUMMARY.md", ".planning/phases/02-kernzahlen/02-02-PLAN.md", ".planning/phases/02-kernzahlen/02-02-SUMMARY.md", ".planning/phases/02-kernzahlen/02-03-PLAN.md", ".planning/phases/02-kernzahlen/02-03-SUMMARY.md", ".planning/phases/02-kernzahlen/02-04-PLAN.md", ".planning/phases/02-kernzahlen/02-04-SUMMARY.md", ".planning/phases/02-kernzahlen/02-05-PLAN.md", ".planning/phases/02-kernzahlen/02-05-SUMMARY.md", ".planning/quick/261001-oim-synthetische-pg-nach-d-14-150102-in-eige/261001-oim-PLAN.md", ".planning/quick/261001-oim-synthetische-pg-nach-d-14-150102-in-eige/261001-oim-SUMMARY.md", "daten/aufbereitet/ergebnisplan.csv", "daten/aufbereitet/finanzplan.csv", "daten/aufbereitet/hierarchie.csv", "daten/pruefberichte/befunde.md", "daten/pruefberichte/konsistenz.md", "daten/zwischen/seiten.csv", "pipeline/01_seiten_klassifizieren.py", "pipeline/02_plaene_extrahieren.py", "pipeline/06_pruefen.py", "pipeline/alle.py", "pipeline/jahrgaenge/2026.toml", "pipeline/jahrgaenge/2026_sollwerte.toml", "pipeline/ostbevern/konfiguration.py", "pipeline/ostbevern/pdf.py", "pipeline/ostbevern/plaene.py", "pipeline/ostbevern/pruefung.py", "pipeline/ostbevern/schema.py", "pipeline/ostbevern/seiten.py", "pipeline/ostbevern/zahlen.py", "pipeline/ostbevern/zeilen.py", "pipeline/tests/test_alle.py", "pipeline/tests/test_hierarchie.py", "pipeline/tests/test_konfiguration.py", "pipeline/tests/test_plaene.py", "pipeline/tests/test_pruefung.py", "pipeline/tests/test_schema.py", "pipeline/tests/test_seiten.py", "pipeline/tests/test_zahlen.py"]
covered_digest: "v2:sha256:42effab33ef372e4df26670809d185a981d752a6bd3c98a7024bf1461edfce03"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: passed
  previous_score: "5/5 roadmap Success Criteria; 10/10 requirement IDs"
  gaps_closed: []
  gaps_remaining: []
  regressions: []
---

# Phase 2: Kernzahlen Verification Report

**Phase Goal:** Alle Ergebnis- und Finanzpläne (Gesamt, PB, Produkt) liegen korrekt im Langformat vor. Die Pipeline weist das durch automatische Prüfungen und Anhang-B-Sollwerte nach.
**Verified:** 2026-10-02T12:10:21Z
**Status:** passed
**Re-verification:** Yes — the prior `02-VERIFICATION.md` (verified `2026-10-02T00:00:00Z`, baseline `12e7b93`) went stale because `pipeline/ostbevern/schema.py` (a Phase 2-covered file) changed afterward in commit `a531fb6` ("fix(03): CR-01 round-trip check for Float->Int narrowing in schreibe_csv", +19/−3 in `schema.py`, part of Phase 3's code-review fix round). `gsd_run query verification.status` confirmed `"status": "stale"` before this re-verification ran.

## Why This Re-Verification Was Needed

`schema.py`'s `schreibe_csv` function is the single CSV writer used by every Phase 2 artifact (`ergebnisplan.csv`, `finanzplan.csv`, `hierarchie.csv`, `seiten.csv`). Commit `a531fb6` changed its cast logic, so this re-verification independently re-inspected the diff and re-ran the pipeline and targeted tests at HEAD (`189c481`) rather than trusting the prior report or any SUMMARY.md.

### Diff Inspection Result (`git show a531fb6 -- pipeline/ostbevern/schema.py`)

The existing `cast(spalten, strict=True)` call (itself a Phase 3 hardening fix, `12e7b93`, already covered by the prior re-verification) is unchanged in spirit — it still runs first and still rejects overflow/NaN/unparsable input exactly as before. The new code adds, strictly after that cast, an additional **round-trip check**: for every column being narrowed from `Float32`/`Float64` to a non-float type, it casts the result back to the original float type and compares it against the pre-cast value (`null_equal=True`); a mismatch raises `SchemaFehler` naming the column and the cast. This closes a gap the prior Phase 3 fix did not cover (`strict=True` alone does not catch fractional-truncation on Float→Int narrowing, per the commit message and the new `test_schreibe_csv_lehnt_fraktionalen_float_bei_int_narrowing_ab` regression test).

This is strictly additive tightening of the existing write path: a value that previously wrote successfully only fails now if it genuinely loses precision in the Float→Int cast. Phase 2's plan values are integer-Euro amounts (`schema.py`'s `ergebnisplan.csv`/`finanzplan.csv` schemas type `betrag`/`ve` as `Int64`, sourced from `zahlen.lies_betrag`, which parses to whole Euro); a round-trip mismatch would only occur if an upstream value already carried a fractional component that the prior `strict=True` cast had failed to catch. Live re-run below confirms no such value exists in the current data: the pipeline completes and `daten/` is byte-identical to the previously committed state.

### Live Verification (this session, HEAD `189c481`)

```
$ git status --short daten/ pipeline/
(clean before run)

$ uv run --directory pipeline python alle.py --jahr 2026
Jahrgang 2026: raw_data/haushalt-2026.pdf (400 Seiten erwartet), 15 Seitenbereiche, Sollwerte geladen.
Schritt 01: 400 Seiten klassifiziert, 0 unbekannt, 15 PB, 49 PG (41 synthetisch), 63 Produkte.
Schritt 02: 14899 Planzeilen geschrieben.
Schritt 03: 63 Einträge geschrieben: daten/aufbereitet/produkte.json
Schritt 03: 827 Einträge geschrieben: daten/aufbereitet/grundzahlen.csv
Schritt 03: 229 Einträge geschrieben: daten/aufbereitet/erlaeuterungen.csv
Schritt 04: 959 Zeilen geschrieben: daten/aufbereitet/investitionen.csv
Schritt 04: 8 Zeilen geschrieben: daten/aufbereitet/ve_faelligkeiten.csv
Schritt 04: 959 Zeilen geschrieben: daten/zwischen/investitionen_pb.csv
Querschnitte: 1152 Werte geschrieben.
Schritt 06: Regel 1: grün (6593 Werte)
Schritt 06: Regel 2: grün (7994 Werte)
Schritt 06: Regel 3: grün (114 Werte)
Schritt 06: Regel 4: grün (194 Werte)
Schritt 06: Regel 6: grün (1964 Werte)
Schritt 06: Regel 7: grün (1152 Werte)
Schritt 06: Regel 8: grün (820 Werte)
Schritt 06: Veraltete Befunde: 0

$ git status --short daten/
(empty — byte-identical regeneration; ergebnisplan.csv/finanzplan.csv unaffected by the new round-trip check)

$ uv run --directory pipeline pytest -q -k "test_schema"
2 passed in 0.05s
  (test_schreibe_csv_lehnt_fraktionalen_float_bei_int_narrowing_ab — rejects a 1234.5 Float->Int narrowing)
  (test_schreibe_csv_schreibt_ganzzahligen_float_bei_int_narrowing — accepts a 1234.0 Float->Int narrowing)

$ uv run --directory pipeline pytest -q -k "abweichung_ueber_einem_euro or toleriert_einen_euro or manipul or test_zahlen or test_konfiguration or test_hierarchie or test_seiten or test_plaene or test_pruefung or test_alle or test_schema"
212 passed, 88 deselected in 139.30s
```

Orchestrator-gathered full-suite run at this same HEAD (`189c481`), relied upon per the evidence-gate instructions — not re-run a second time to avoid redundant full-suite execution:

```
$ uv run --directory pipeline pytest -q
300 passed in ~202s
```

**Conclusion: no regression.** The counts for Regeln 1–4 (6593/7994/114/194) are byte-identical to both the original verification and the prior re-verification; `daten/` regenerates with an empty `git status` diff; the new round-trip check's own regression tests pass; and the full 300-test suite (up from 295 — the two new `test_schema.py` cases) is green.

## Goal Achievement

### Observable Truths (Roadmap Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `seiten.csv` maps every PDF page to typ/PB/PG/Produkt with continuation-page inheritance; Anhang-A start-page test for all 63 products; `hierarchie.csv` has 15 PB, all PG (synthetic flagged) and 63 named products | ✓ VERIFIED | Live `uv run --directory pipeline python alle.py --jahr 2026` run (this session): "Schritt 01: 400 Seiten klassifiziert, 0 unbekannt, 15 PB, 49 PG (41 synthetisch), 63 Produkte." Unaffected by `schema.py`'s change (seiten.py/klassifikation logic untouched). |
| 2 | Zahlenparser unit tests green: German thousands format, minus (ASCII + U+2212), „–" as no-value, glued amounts, `C`/`€` as Euro sign | ✓ VERIFIED | `zahlen.py`'s `lies_betrag`/`_BETRAG_MUSTER` untouched by commit `a531fb6`. Targeted run (this session) includes `test_zahlen` — part of the 212-passed run above. |
| 3 | `ergebnisplan.csv`/`finanzplan.csv` (incl. VE) hold Gesamt/PB/Produkt plans with `zeile`, `zeile_kanonisch`, `ist_summe`, `pdf_seite`; Regel 1 (Zeilenformeln) green for every plan; Regel 2 (Produkt→PG→PB) green; Regel 3 (15 PB → Gesamt, excl. TP 27/28) green | ✓ VERIFIED | Live run (this session): "Regel 1: grün (6593 Werte)", "Regel 2: grün (7994 Werte)", "Regel 3: grün (114 Werte)" — identical counts to both prior verifications. `git status --short daten/` empty after the run, confirming `schema.py`'s new round-trip check does not alter these CSVs. |
| 4 | Anhang-B Sollwerte matched to the Euro: B.1 Z.28 2026 = −2.353.506 €; B.2 Z.23/30/33/41; B.3 PB sums 27.042.063 €/30.255.569 €; Satzung § 1 27.502.063 €/30.455.569 € | ✓ VERIFIED | Live run (this session): "Regel 4: grün (194 Werte)", 0 Abweichungen — identical count to both prior verifications. |
| 5 | `uv run pytest` produces `daten/pruefberichte/konsistenz.md`; an undocumented >1€ deviation fails the run | ✓ VERIFIED | Orchestrator-reported full suite at HEAD `189c481`: 300 passed. Live `alle.py` run (this session) regenerates `konsistenz.md`; `git status --porcelain daten/` empty afterward. Targeted `pytest -k "abweichung_ueber_einem_euro or toleriert_einen_euro"` (part of the 212-passed run, this session) confirms the >1€ gate is still live. |

**Score:** 5/5 roadmap Success Criteria verified.

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|---|---|---|---|---|
| EXTR-01 | 02-01 | Zahlenparser mit Unit-Tests | ✓ SATISFIED | `zahlen.py`'s `lies_betrag` untouched by `a531fb6`; `.planning/REQUIREMENTS.md:20` shows `- [x]`; targeted `test_zahlen` passed (this session). |
| EXTR-02 | 02-02 | `seiten.csv` mit Seite/Typ/PB/PG/Produkt, Fortsetzungsseiten, Anhang-A-Startseiten | ✓ SATISFIED | `seiten.csv` 400 rows (live run); `seiten.py` untouched by `a531fb6`. |
| EXTR-03 | 02-02 | `hierarchie.csv`: 15 PB, alle PG (synthetisch markiert), 63 Produkte | ✓ SATISFIED | Live run: 15 PB / 49 PG (41 synthetic) / 63 P, unchanged. |
| EXTR-04 | 02-01, 02-04 | Gesamtergebnisplan + alle Teilergebnispläne im Langformat | ✓ SATISFIED | `ergebnisplan.csv` regenerated byte-identically (empty `git status` diff) despite `schema.py`'s new round-trip check — confirms no Phase 2 value triggers the stricter guard. |
| EXTR-05 | 02-03, 02-04 | Gesamtfinanzplan + alle Teilfinanzpläne inkl. VE | ✓ SATISFIED | `finanzplan.csv` retains `wertart=ve` rows across all ebenen (live run, byte-identical). |
| PRUEF-01 | 02-03, 02-04 | Zeilenformeln aller Pläne stimmen (Regel 1) | ✓ SATISFIED | Regel 1 grün, 6593 Werte (live run, this session) — identical to both prior verifications. |
| PRUEF-02 | 02-05 | Produkt-Teilpläne = PG = PB-Teilplan (Regel 2) | ✓ SATISFIED | Regel 2 grün, 7994 Werte (live run, this session) — identical. |
| PRUEF-03 | 02-05 | 15 PB = Gesamtergebnisplan (Regel 3) | ✓ SATISFIED | Regel 3 grün, 114 Werte (live run, this session) — identical. |
| PRUEF-04 | 02-01, 02-03, 02-05 | Anhang-B-Sollwerte getroffen (Regel 4) | ✓ SATISFIED | Regel 4 grün, 194 Werte, 0 Abweichungen (live run, this session) — identical. |
| PRUEF-09 | 02-01, 02-03, 02-05 | Alle Prüfungen in pytest, `konsistenz.md`, >1€-Gate | ✓ SATISFIED | 300/300 pytest green (orchestrator-reported, this session, full suite including the two new `test_schema.py` regression tests); >1€ gate re-confirmed live via targeted run. |

No orphaned requirements: all 10 IDs declared across the five Phase-2 plans (`EXTR-01..05`, `PRUEF-01,02,03,04,09`) match the 10 IDs this task lists, and `.planning/REQUIREMENTS.md`'s traceability table marks all 10 "Phase 2 / Complete".

### Anti-Patterns Found

No debt markers (`TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER`) found in `pipeline/ostbevern/schema.py` (the one file that changed since the prior verification; scanned live, this session). The new code is a focused, well-documented guard (docstring cites the exact polars behavior it works around and the originating review finding, `03-REVIEW.md CR-01`).

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Full pipeline run succeeds and is deterministic at HEAD (post CR-01 fix) | `uv run --directory pipeline python alle.py --jahr 2026` then `git status --short daten/` | exit 0, Regeln 1-4 grün with unchanged counts, empty diff | ✓ PASS |
| CR-01 round-trip check rejects fractional Float->Int narrowing | `pytest -k test_schema` (this session) | 2 passed — reject 1234.5, accept 1234.0 | ✓ PASS |
| >1€ injected deviation turns Regel 4 red / 1€ stays green | `pytest -k "abweichung_ueber_einem_euro or toleriert_einen_euro"` (this session, part of 212-passed targeted run) | passed | ✓ PASS |
| Full test suite green at HEAD | `uv run --directory pipeline pytest` (orchestrator) | 300 passed | ✓ PASS |

### Human Verification Required

None. This is a deterministic, headless Python pipeline with comprehensive automated test coverage. The single changed file since the last verification (`schema.py`) was independently diff-inspected and live-tested against this session's own pipeline run and targeted pytest invocations — not inferred from any SUMMARY.md or from the prior (now-stale) VERIFICATION.md.

### Gaps Summary

No gaps found. The one change to Phase 2's covered files since the last verification — `schema.py`'s CR-01 round-trip check for Float→Int narrowing — is a strictly additive tightening of the existing `schreibe_csv` cast guard. It adds its own regression test (`test_schema.py`, 2 new tests, both passing) and does not reject any value in the current Phase 2 data: a live pipeline re-run regenerates `ergebnisplan.csv`/`finanzplan.csv`/`hierarchie.csv`/`seiten.csv` byte-identically (empty `git status --short daten/` diff), Regeln 1-4's checked-value counts (6593/7994/114/194) are unchanged, and the full pytest suite (300, up from 295 due to the two new CR-01 tests) is green. The `covered_digest` in this report's frontmatter is fresh as of this verification run and supersedes the prior report's stale digest.

---

_Verified: 2026-10-02T12:10:21Z_
_Verifier: Claude (gsd-verifier)_
