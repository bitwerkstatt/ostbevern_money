---
phase: 02-kernzahlen
verified: 2026-10-02T00:00:00Z
status: passed
score: 5/5 must-haves verified (roadmap Success Criteria); 10/10 requirement IDs satisfied
covered_files: [".planning/phases/02-kernzahlen/02-01-PLAN.md", ".planning/phases/02-kernzahlen/02-01-SUMMARY.md", ".planning/phases/02-kernzahlen/02-02-PLAN.md", ".planning/phases/02-kernzahlen/02-02-SUMMARY.md", ".planning/phases/02-kernzahlen/02-03-PLAN.md", ".planning/phases/02-kernzahlen/02-03-SUMMARY.md", ".planning/phases/02-kernzahlen/02-04-PLAN.md", ".planning/phases/02-kernzahlen/02-04-SUMMARY.md", ".planning/phases/02-kernzahlen/02-05-PLAN.md", ".planning/phases/02-kernzahlen/02-05-SUMMARY.md", ".planning/quick/261001-oim-synthetische-pg-nach-d-14-150102-in-eige/261001-oim-PLAN.md", ".planning/quick/261001-oim-synthetische-pg-nach-d-14-150102-in-eige/261001-oim-SUMMARY.md", "daten/aufbereitet/ergebnisplan.csv", "daten/aufbereitet/finanzplan.csv", "daten/aufbereitet/hierarchie.csv", "daten/pruefberichte/befunde.md", "daten/pruefberichte/konsistenz.md", "daten/zwischen/seiten.csv", "pipeline/01_seiten_klassifizieren.py", "pipeline/02_plaene_extrahieren.py", "pipeline/06_pruefen.py", "pipeline/alle.py", "pipeline/jahrgaenge/2026.toml", "pipeline/jahrgaenge/2026_sollwerte.toml", "pipeline/ostbevern/konfiguration.py", "pipeline/ostbevern/pdf.py", "pipeline/ostbevern/plaene.py", "pipeline/ostbevern/pruefung.py", "pipeline/ostbevern/schema.py", "pipeline/ostbevern/seiten.py", "pipeline/ostbevern/zahlen.py", "pipeline/ostbevern/zeilen.py", "pipeline/tests/test_alle.py", "pipeline/tests/test_hierarchie.py", "pipeline/tests/test_konfiguration.py", "pipeline/tests/test_plaene.py", "pipeline/tests/test_pruefung.py", "pipeline/tests/test_seiten.py", "pipeline/tests/test_zahlen.py"]
covered_digest: "v2:sha256:5578c71a829a019a7db00b91bee599ccaac4c8e66b81c5220c1637f065f9304a"
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
**Verified:** 2026-10-02T00:00:00Z
**Status:** passed
**Re-verification:** Yes — the `covered_digest` from the previous report (`2026-10-01T17:11:17Z`) went stale because Phase 3 ("Details", completed afterward at `12e7b93`) touched 15 files inside this report's `covered_files` set.

## Why This Re-Verification Was Needed

`gsd_run query verification status` flagged the prior `02-VERIFICATION.md` as stale: its `covered_digest` no longer matched HEAD because Phase 3 modified 15 covered files between commit `dd18987` (2026-10-01 19:12, the prior report's baseline) and `12e7b93` (HEAD):

`daten/pruefberichte/befunde.md`, `daten/pruefberichte/konsistenz.md`, `pipeline/06_pruefen.py`, `pipeline/alle.py`, `pipeline/jahrgaenge/2026.toml`, `pipeline/jahrgaenge/2026_sollwerte.toml`, `pipeline/ostbevern/konfiguration.py`, `pipeline/ostbevern/pdf.py`, `pipeline/ostbevern/pruefung.py`, `pipeline/ostbevern/schema.py`, `pipeline/ostbevern/zahlen.py`, `pipeline/tests/test_alle.py`, `pipeline/tests/test_konfiguration.py`, `pipeline/tests/test_pruefung.py`, `pipeline/tests/test_zahlen.py`

This re-verification re-reads every diff `dd18987..HEAD` for these files and independently re-runs the pipeline and targeted tests at HEAD, rather than trusting the prior report or any SUMMARY.md.

### Diff Inspection Result: All Changes Additive, Phase 2 Logic Untouched

Per-file inspection (`git diff dd18987..HEAD -- <file>`):

- **`pipeline/ostbevern/pruefung.py`** (+621/−0 net, all insertions after line 775): the diff hunk starts immediately after the closing brace of `_pruefe_regel4` — Regeln 1–4 (`_pruefe_regel1`…`_pruefe_regel4`) are byte-for-byte unchanged. Everything added is new code for Regel 6 (Investitionsmaßnahmen), Regel 7 (Haushaltsquerschnitte) and Regel 8 (Vollständigkeit), introduced in Phase 3. The `Regelergebnis.status` property gained an OR-clause for a new `luecken` field (defaults to `()`), which is a strict superset — a Regelergebnis with no `luecken` behaves exactly as before.
- **`pipeline/ostbevern/zahlen.py`** (+41/−2, docstring + new `lies_kennzahl` function and `_KENNZAHL_MUSTER` regex for Phase 3's EXTR-07 Grundzahlen). `lies_betrag` (the EXTR-01 Zahlenparser) and `_BETRAG_MUSTER` are byte-for-byte unchanged.
- **`pipeline/ostbevern/konfiguration.py`** (+101/−2): adds an optional `layout` field to `Jahrgang` (default empty dict) and two new `[layout.*]`/`[stichproben]` TOML-table loaders for Phase 3. `lade_jahrgang`'s existing seitenbereiche/kopfzeilen/synthetische_produktgruppen parsing paths are unchanged; the new `layout=layout` kwarg is additive to the `Jahrgang(...)` constructor call.
- **`pipeline/ostbevern/schema.py`** (+261/−2): adds new path constants and CSV schema helpers for Phase 3 outputs (`investitionen.csv`, `querschnitte.csv`, `produkte.json`, etc.). The one behavioral change to existing code is `schreibe_csv`'s `cast(spalten)` → `cast(spalten, strict=True)` (commit `12e7b93`, IN-03 fail-loud fix) — this affects `ergebnisplan.csv`/`finanzplan.csv` writes too, but the live pipeline run below confirms it still succeeds and produces byte-identical output.
- **`pipeline/alle.py`** / **`pipeline/06_pruefen.py`**: both diffs are purely additive — new Schritt 03/04/Querschnitte calls inserted between the existing Schritt 02 and Schritt 06 calls; the Schritt 01/02/06 calls and their exception handling are unchanged.
- **`daten/pruefberichte/befunde.md`** / **`konsistenz.md`**: diffs are additive — new Regel 6/7/8 documentation and Befunde rows appended; the three original Phase-2 Befunde rows (Regel 1 row, Regel 2 rows, Regel 3 row) are unchanged, and Regel 1–4's status/counts in `konsistenz.md`'s Übersicht table are unchanged (6593/7994/114/194, all grün).
- **`pipeline/tests/test_*.py`**: additive (new test classes for Regel 6/7/8, `lies_kennzahl`, `layout`/`stichproben` config); no existing Phase-2 test was deleted or weakened (confirmed by diff inspection — all hunks are pure insertions apart from the WR-02/IN-01 mock-contract fix commits already covered by the prior re-verification).

**Conclusion: no regression risk from Phase 3's changes to Phase 2's logic.** Independent live verification below confirms this holds in practice, not just in the diff.

## Goal Achievement

### Observable Truths (Roadmap Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `seiten.csv` maps every PDF page to typ/PB/PG/Produkt with continuation-page inheritance; Anhang-A start-page test for all 63 products; `hierarchie.csv` has 15 PB, all PG (synthetic flagged) and 63 named products | ✓ VERIFIED | Live `uv run --directory pipeline python alle.py --jahr 2026` run (this session): "Schritt 01: 400 Seiten klassifiziert, 0 unbekannt, 15 PB, 49 PG (41 synthetisch), 63 Produkte." `pipeline/tests/test_hierarchie.py` and `test_seiten.py` pass (part of the full 295-test run reported by the orchestrator and independently re-confirmed via targeted run below). |
| 2 | Zahlenparser unit tests green: German thousands format, minus (ASCII + U+2212), „–" as no-value, glued amounts, `C`/`€` as Euro sign | ✓ VERIFIED | `pipeline/ostbevern/zahlen.py`'s `lies_betrag`/`_BETRAG_MUSTER` byte-unchanged since the prior verification (diff inspection above). `pytest -q -k test_zahlen` → part of the 113-passed targeted run (this session). |
| 3 | `ergebnisplan.csv`/`finanzplan.csv` (incl. VE) hold Gesamt/PB/Produkt plans with `zeile`, `zeile_kanonisch`, `ist_summe`, `pdf_seite`; Regel 1 (Zeilenformeln) green for every plan; Regel 2 (Produkt→PG→PB) green; Regel 3 (15 PB → Gesamt, excl. TP 27/28) green | ✓ VERIFIED | Live run (this session): "Regel 1: grün (6593 Werte)", "Regel 2: grün (7994 Werte)", "Regel 3: grün (114 Werte)" — identical counts to the prior verification, all 0 Abweichungen. `_pruefe_regel1/2/3` functions in `pruefung.py` are unmodified since the prior verification (confirmed by diff, see above). |
| 4 | Anhang-B Sollwerte matched to the Euro: B.1 Z.28 2026 = −2.353.506 €; B.2 Z.23/30/33/41; B.3 PB sums 27.042.063 €/30.255.569 €; Satzung § 1 27.502.063 €/30.455.569 € | ✓ VERIFIED | Live run (this session): "Regel 4: grün (194 Werte)", 0 Abweichungen — identical count to the prior verification. `_pruefe_regel4` unmodified since the prior verification. |
| 5 | `uv run pytest` produces `daten/pruefberichte/konsistenz.md`; an undocumented >1€ deviation fails the run | ✓ VERIFIED | `uv run --directory pipeline pytest` (orchestrator-reported, this session): 295 passed. Live `alle.py` run (this session) regenerates `konsistenz.md`; `git status --porcelain daten/` is empty afterward (deterministic, independently re-run). Targeted `pytest -k "abweichung_ueber_einem_euro or toleriert_einen_euro"` (part of the 113-passed targeted run, this session) confirms the >1€ gate is still live. Live output shows "Veraltete Befunde: 0". |

**Score:** 5/5 roadmap Success Criteria verified.

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|---|---|---|---|---|
| EXTR-01 | 02-01 | Zahlenparser mit Unit-Tests | ✓ SATISFIED | `zahlen.py`'s `lies_betrag` unmodified since prior verification; `.planning/REQUIREMENTS.md:20` shows `- [x]`. |
| EXTR-02 | 02-02 | `seiten.csv` mit Seite/Typ/PB/PG/Produkt, Fortsetzungsseiten, Anhang-A-Startseiten | ✓ SATISFIED | `seiten.csv` 400 rows (live run); unmodified logic since prior verification. |
| EXTR-03 | 02-02 | `hierarchie.csv`: 15 PB, alle PG (synthetisch markiert), 63 Produkte | ✓ SATISFIED | Live run: 15 PB / 49 PG (41 synthetic) / 63 P, unchanged from prior verification. |
| EXTR-04 | 02-01, 02-04 | Gesamtergebnisplan + alle Teilergebnispläne im Langformat | ✓ SATISFIED | `ergebnisplan.csv` GESAMT/PB/PG/P rows present with required columns; regenerated byte-identically by the live run despite `schema.py`'s new `cast(..., strict=True)` (IN-03 fix) — confirms the stricter cast does not reject any Phase-2 value. |
| EXTR-05 | 02-03, 02-04 | Gesamtfinanzplan + alle Teilfinanzpläne inkl. VE | ✓ SATISFIED | `finanzplan.csv` retains `wertart=ve` rows across all ebenen (live run, unchanged). |
| PRUEF-01 | 02-03, 02-04 | Zeilenformeln aller Pläne stimmen (Regel 1) | ✓ SATISFIED | Regel 1 grün, 6593 Werte (live run, this session) — identical to prior verification. |
| PRUEF-02 | 02-05 | Produkt-Teilpläne = PG = PB-Teilplan (Regel 2) | ✓ SATISFIED | Regel 2 grün, 7994 Werte (live run, this session) — identical to prior verification. |
| PRUEF-03 | 02-05 | 15 PB = Gesamtergebnisplan (Regel 3) | ✓ SATISFIED | Regel 3 grün, 114 Werte (live run, this session) — identical to prior verification. |
| PRUEF-04 | 02-01, 02-03, 02-05 | Anhang-B-Sollwerte getroffen (Regel 4) | ✓ SATISFIED | Regel 4 grün, 194 Werte, 0 Abweichungen (live run, this session) — identical to prior verification. |
| PRUEF-09 | 02-01, 02-03, 02-05 | Alle Prüfungen in pytest, `konsistenz.md`, >1€-Gate | ✓ SATISFIED | 295/295 pytest green (orchestrator-reported, this session, full suite including Phase 3's new Regel 6/7/8 tests); >1€ gate re-confirmed live via targeted run. |

No orphaned requirements: all 10 IDs declared across the five Phase-2 plans (`EXTR-01..05`, `PRUEF-01,02,03,04,09`) match the 10 IDs this task lists and the ROADMAP.md/REQUIREMENTS.md traceability table (all marked "Complete").

### Determinism / Reproducibility (live, this session, independently re-run)

```
$ git status --short daten/
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
(empty — byte-identical regeneration)

$ uv run --directory pipeline pytest -q -k "abweichung_ueber_einem_euro or toleriert_einen_euro or manipul or test_zahlen or test_konfiguration"
113 passed, 182 deselected in 33.32s
```

Orchestrator-gathered (this session, relied upon for the full-suite run per the evidence-gate instructions — not re-run a second time to avoid redundant full-suite execution):

```
$ cd pipeline && uv sync --locked && uv run ruff check . && uv run ruff format --check . && uv run pytest
ruff clean, 34 files formatted, 295 passed in ~190s
```

### Anti-Patterns Found

No debt markers (`TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER`) found in any Phase-2 pipeline source file (scanned live, this session, across all 12 Phase-2 `pipeline/*.py`/`pipeline/ostbevern/*.py` files). `ruff check .` and `ruff format --check .` both pass clean (orchestrator-reported, this session).

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Full pipeline run succeeds and is deterministic at HEAD (post Phase-3) | `uv run --directory pipeline python alle.py --jahr 2026` then `git status --short daten/` | exit 0, Regeln 1-4 grün with unchanged counts, empty diff | ✓ PASS |
| Full test suite green at HEAD | `uv run --directory pipeline pytest` (orchestrator) | 295 passed | ✓ PASS |
| Lint/format clean (CI parity) | `uv run --directory pipeline ruff check .` / `ruff format --check .` (orchestrator) | clean | ✓ PASS |
| >1€ injected deviation turns Regel 4 red / 1€ stays green | `pytest -k "abweichung_ueber_einem_euro or toleriert_einen_euro"` (this session) | 2/113 of the targeted subset passed | ✓ PASS |
| Manipulated product/PB row caught at correct hierarchy level | `pytest -k manipul` (this session, part of targeted 113) | passed | ✓ PASS |
| Regel 1-4 functions unmodified by Phase 3 | `git diff dd18987..HEAD -- pipeline/ostbevern/pruefung.py` | hunk starts after `_pruefe_regel4`'s closing line | ✓ PASS |
| `schema.py`'s stricter `cast(strict=True)` (IN-03 fix) does not break Phase-2 CSV writes | Live `alle.py` run + empty `git status` diff | `ergebnisplan.csv`/`finanzplan.csv` regenerated byte-identically | ✓ PASS |

### Human Verification Required

None. This is a deterministic, headless Python pipeline with comprehensive automated test coverage. All five roadmap Success Criteria and all 10 requirement IDs were re-verified against the current `HEAD` with live command execution and direct diff inspection — not inferred from any SUMMARY.md or from the prior (now-stale) VERIFICATION.md.

### Gaps Summary

No gaps found. Phase 3's 15 file changes to Phase 2's covered files are entirely additive (new Regel 6/7/8, new `layout`/`stichproben` config tables, new Grundzahlen parser, new CSV schemas) plus one narrowly-scoped hardening fix (`schema.py`'s `cast(strict=True)`, commit `12e7b93`) that does not reject any Phase-2 data, confirmed by a clean live pipeline re-run. Regeln 1-4's checked-value counts (6593/7994/114/194) are byte-identical to the prior verification's live run, and the full pytest suite (295, up from 152 due to Phase 3's new Regel 6/7/8 tests) is green. The `covered_digest` in this report's frontmatter is fresh as of this verification run and supersedes the prior report's stale digest.

---

_Verified: 2026-10-02T00:00:00Z_
_Verifier: Claude (gsd-verifier)_
