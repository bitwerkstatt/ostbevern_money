---
phase: 02-kernzahlen
verified: 2026-10-01T17:11:17Z
status: passed
score: 5/5 must-haves verified (roadmap Success Criteria); 10/10 requirement IDs satisfied
covered_files: [".planning/phases/02-kernzahlen/02-01-PLAN.md", ".planning/phases/02-kernzahlen/02-01-SUMMARY.md", ".planning/phases/02-kernzahlen/02-02-PLAN.md", ".planning/phases/02-kernzahlen/02-02-SUMMARY.md", ".planning/phases/02-kernzahlen/02-03-PLAN.md", ".planning/phases/02-kernzahlen/02-03-SUMMARY.md", ".planning/phases/02-kernzahlen/02-04-PLAN.md", ".planning/phases/02-kernzahlen/02-04-SUMMARY.md", ".planning/phases/02-kernzahlen/02-05-PLAN.md", ".planning/phases/02-kernzahlen/02-05-SUMMARY.md", ".planning/quick/261001-oim-synthetische-pg-nach-d-14-150102-in-eige/261001-oim-PLAN.md", ".planning/quick/261001-oim-synthetische-pg-nach-d-14-150102-in-eige/261001-oim-SUMMARY.md", "daten/aufbereitet/ergebnisplan.csv", "daten/aufbereitet/finanzplan.csv", "daten/aufbereitet/hierarchie.csv", "daten/pruefberichte/befunde.md", "daten/pruefberichte/konsistenz.md", "daten/zwischen/seiten.csv", "pipeline/01_seiten_klassifizieren.py", "pipeline/02_plaene_extrahieren.py", "pipeline/06_pruefen.py", "pipeline/alle.py", "pipeline/jahrgaenge/2026.toml", "pipeline/jahrgaenge/2026_sollwerte.toml", "pipeline/ostbevern/konfiguration.py", "pipeline/ostbevern/pdf.py", "pipeline/ostbevern/plaene.py", "pipeline/ostbevern/pruefung.py", "pipeline/ostbevern/schema.py", "pipeline/ostbevern/seiten.py", "pipeline/ostbevern/zahlen.py", "pipeline/ostbevern/zeilen.py", "pipeline/tests/test_alle.py", "pipeline/tests/test_hierarchie.py", "pipeline/tests/test_konfiguration.py", "pipeline/tests/test_plaene.py", "pipeline/tests/test_pruefung.py", "pipeline/tests/test_seiten.py", "pipeline/tests/test_zahlen.py"]
covered_digest: "v2:sha256:664f45dfa6c835f30e40e4c257cbafca79c6b328d0dc1c44deb3d818cf9278fc"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: passed
  previous_score: "5/5 roadmap Success Criteria; 28/28 plan-level must_have truths"
  gaps_closed: []
  gaps_remaining: []
  regressions: []
---

# Phase 2: Kernzahlen Verification Report

**Phase Goal:** Alle Ergebnis- und Finanzpläne (Gesamt, PB, Produkt) liegen korrekt im Langformat vor. Die Pipeline weist das durch automatische Prüfungen und Anhang-B-Sollwerte nach.
**Verified:** 2026-10-01T17:11:17Z
**Status:** passed
**Re-verification:** Yes — after quick task 261001-oim (synthetic PG 1502 "Tourismus" per D-14) and two code-review fixes (39214cf WR-01, 1f5cfaa WR-02)

## Why This Re-Verification Was Needed

The previous VERIFICATION.md (`verified: 2026-10-01T15:31:01Z`, `status: passed`) covered the codebase at the Phase-2 plan baseline. Three commits landed afterward that touch files in `covered_files`:

- `39214cf` `fix(02): WR-01 drop dead plantyp parameter from _synthetische_pg_datensaetze` (`pipeline/ostbevern/plaene.py`)
- `1f5cfaa` `fix(02): WR-02 correct inverted Regel-1 sign description in befunde.md` (`daten/pruefberichte/befunde.md`)
- Quick task `261001-oim` (5 commits `30c4571`..`b5e2b26`): generalized the synthetic-PG rule to "exactly one product per PG" and split product 150102 into its own synthetic PG 1502 "Tourismus", changing `pipeline/jahrgaenge/2026.toml`, `2026_sollwerte.toml`, `konfiguration.py`, `seiten.py`, `plaene.py`, four test files, and five `daten/` outputs.

This re-verification re-runs the full goal-backward check against the current `HEAD`, not the prior snapshot, and regenerates the digest.

## Goal Achievement

### Observable Truths (Roadmap Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `seiten.csv` maps every PDF page to typ/PB/PG/Produkt with continuation-page inheritance; Anhang-A start-page test for all 63 products; `hierarchie.csv` has 15 PB, all PG (synthetic flagged) and 63 named products | ✓ VERIFIED | Live `alle.py --jahr 2026` run: "400 Seiten klassifiziert, 0 unbekannt, 15 PB, 49 PG (41 synthetisch), 63 Produkte." Independently re-parsed `hierarchie.csv` with `csv.DictReader`: PB=15, PG=49 (41 synthetic), P=63 — matches live run exactly. Product 150102 now correctly carries `pg=1502` in `seiten.csv` (`grep ',15,1502,150102$'` finds its product-info and Teilergebnisplan pages; `grep ',15,1501,150102$'` returns 0 rows). `pipeline/tests/test_hierarchie.py` (rewritten for the one-product-per-PG rule) passes in the full 152-test run. |
| 2 | Zahlenparser unit tests green: German thousands format, minus (ASCII + U+2212), „–" as no-value, glued amounts, `C`/`€` as Euro sign | ✓ VERIFIED | `pipeline/ostbevern/zahlen.py` unchanged by the post-verification commits. `pipeline/tests/test_zahlen.py` (21 tests) passes in the live full-suite run (152 passed, see below). |
| 3 | `ergebnisplan.csv`/`finanzplan.csv` (incl. VE) hold Gesamt/PB/Produkt plans with `zeile`, `zeile_kanonisch`, `ist_summe`, `pdf_seite`; Regel 1 (Zeilenformeln) green for every plan; Regel 2 (Produkt→PG→PB) green; Regel 3 (15 PB → Gesamt, excl. TP 27/28) green | ✓ VERIFIED | Live `alle.py --jahr 2026`: "Regel 1: grün (6593 Werte)", "Regel 2: grün (7994 Werte)", "Regel 3: grün (114 Werte)" — all 0 Abweichungen. Counts rose from the prior verification's 6550/7920 to 6593/7994 because PG 1501 and PG 1502 are now each counted separately instead of merged into one PG (documented and derived in-test in `test_pruefung.py`, not a bare literal). `ergebnisplan.csv` row `PG,1501,true,29,...,2026,ansatz,-118138,274` and `PG,1502,true,29,...,2026,ansatz,-72554,277` directly confirmed via `grep`. Manipulation tests (`test_regel2_erkennt_manipulierte_produktzeile`, `test_regel3_erkennt_manipulierte_pb_zeile`) still pass, confirmed in the targeted `pytest -k manipul` run (2/2 passed). |
| 4 | Anhang-B Sollwerte matched to the Euro: B.1 Z.28 2026 = −2.353.506 €; B.2 Z.23/30/33/41; B.3 PB sums 27.042.063 €/30.255.569 €; Satzung § 1 27.502.063 €/30.455.569 € | ✓ VERIFIED | Not touched by the post-verification commits; Regel 4 live run still reports "grün (194 Werte)", 0 Abweichungen. The B.3 Anhang-B.3 correction for PB 09/15 documented in the prior verification is unaffected by the PG 1501/1502 split (PG-level is a different granularity from PB-level Sollwerte). |
| 5 | `uv run pytest` produces `daten/pruefberichte/konsistenz.md`; an undocumented >1€ deviation fails the run | ✓ VERIFIED | `uv run --directory pipeline pytest -q`: **152 passed** (live run, this session). Live `alle.py` run regenerates `konsistenz.md`; `git status --porcelain daten/` is empty afterward (deterministic). `pytest -k "abweichung_ueber_einem_euro or toleriert_einen_euro"` (2/2 passed, live run) confirms the >1€ gate is still live. `konsistenz.md`/live output both show "Veraltete Befunde: 0". |

**Score:** 5/5 roadmap Success Criteria verified.

### Quick-Task Must-Haves (261001-oim, re-verified against current HEAD)

All 8 `must_haves.truths` and 6 `artifacts`/`key_links` entries from the quick-task PLAN frontmatter were independently re-checked, not read from its SUMMARY:

| Must-have | Status | Evidence |
|---|---|---|
| Every synthetic PG has exactly one P child via `eltern_code`; code = product's first four digits unless declared in `[synthetische_produktgruppen]` | ✓ VERIFIED | `hierarchie.csv`: PG 1501 → only P 150101; PG 1502 → only P 150102 (direct grep). `baue_hierarchie` raises `SeitenFehler` on collision (`pipeline/tests/test_seiten.py::test_baue_hierarchie_kollision_ohne_deklaration_meldet_beide_produkte`, in the 152-test pass). |
| PG 1501 (Wirtschaftsförderung, pdf_seite_start 273) has exactly one child 150101; PG 1502 (Tourismus, pdf_seite_start 276) has exactly one child 150102, `eltern_code`=1502 | ✓ VERIFIED | `grep` confirms `PG,1501,Wirtschaftsförderung,15,273,true` / `P,150101,Wirtschaftsförderung,1501,273,false` / `PG,1502,Tourismus,15,276,true` / `P,150102,Touristische Öffentlichkeitsarbeit,1502,276,false` in `hierarchie.csv`. |
| `ergebnisplan.csv`: PG 1501 Z.29 Ansatz 2026 = -118138, PG 1502 Z.29 Ansatz 2026 = -72554 | ✓ VERIFIED | Direct `grep` on `ergebnisplan.csv`: both values present exactly. |
| Synthetic PG rows are exact copies of their single product's rows (ebene=PG, synthetisch=true), not sums | ✓ VERIFIED | `plaene.py::_synthetische_pg_datensaetze` rewritten to copy via `hierarchie.eltern_code`, no prefix slicing (`! grep -v '^\s*#' pipeline/ostbevern/plaene.py \| grep -q '\[:4\]'` pattern confirmed absent). `test_synthetische_pg_ist_kopie_ihres_einzigen_produkts` passes. |
| `seiten.csv`: pages of product 150102 carry `pg=1502` | ✓ VERIFIED | Direct grep: `276,produktinformationen,15,1502,150102` and `277,teilergebnisplan,15,1502,150102` present; 0 rows with `,15,1501,150102$`. |
| Fail-loud (D-08): malformed config or hierarchy-level declaration raises `KonfigurationsFehler`/`SeitenFehler` | ✓ VERIFIED | `grep` confirms `synthetische_produktgruppen`/`haushaltsquerschnitt_pg` validation blocks in `konfiguration.py` (13+ distinct error messages) and `produktgruppe_fuer_produkt` wired into both `klassifiziere_dokument` and `baue_hierarchie` in `seiten.py`. Targeted `pytest -q -k "konfiguration or test_seiten"` → 51 passed (live run). |
| `alle.py --jahr 2026` exits 0 (Regeln 1–4 grün, no veraltete Befunde); second run byte-identical | ✓ VERIFIED | Live run, this session: exit 0, Regeln 1–4 grün, "Veraltete Befunde: 0"; `git status --porcelain daten/` empty after. |
| `befunde.md` no longer contains the open PG question about 150102; all 10 Schlüsseltabelle rows unchanged | ✓ VERIFIED | `grep -n "150102\|Haushaltsquerschnitt-Seiten 299"` on `befunde.md` returns nothing (open question removed). `grep -c '^| [0-9]* |'` returns 10 (Schlüsseltabelle row count unchanged from baseline). |

### Code-Review Fix Commits (39214cf, 1f5cfaa), re-verified

| Commit | Finding | Status | Evidence |
|---|---|---|---|
| `39214cf` | WR-01: dead `plantyp` parameter in `_synthetische_pg_datensaetze` | ✓ VERIFIED FIXED | Current `plaene.py` signature is `_synthetische_pg_datensaetze(teil_df, hierarchie)` (no `plantyp`); both call sites in `extrahiere_plaene` updated accordingly (confirmed by reading the diff and current file). |
| `1f5cfaa` | WR-02: inverted Regel-1 sign description in `befunde.md` | ✓ VERIFIED FIXED | `befunde.md` now reads "Regel 1: Formelkette minus gedruckte Summe", matching `pruefung.py::_pruefe_regel1`'s actual `abweichung = ist − soll` computation (confirmed by reading the diff and current file). |

### Requirements Coverage

| Requirement | Source Plan(s) | Description | Status | Evidence |
|---|---|---|---|---|
| EXTR-01 | 02-01 | Zahlenparser mit Unit-Tests | ✓ SATISFIED | `zahlen.py` unchanged; 21 passing tests in the live 152-test run. `.planning/REQUIREMENTS.md` line 20 now correctly shows `- [x]` (the stale-checkbox discrepancy flagged in the prior verification has since been corrected). |
| EXTR-02 | 02-02 | `seiten.csv` mit Seite/Typ/PB/PG/Produkt, Fortsetzungsseiten, Anhang-A-Startseiten | ✓ SATISFIED | `seiten.csv` 400 rows; product 150102 correctly reassigned to `pg=1502`; Anhang-A test green. |
| EXTR-03 | 02-02 | `hierarchie.csv`: 15 PB, alle PG (synthetisch markiert), 63 Produkte | ✓ SATISFIED | Live run + direct CSV parse: 15 PB / 49 PG (41 synthetic) / 63 P — the count rose from 48/40 to 49/41 because PG 1501/1502 is now two PGs, both correctly flagged `synthetisch=true`. |
| EXTR-04 | 02-01, 02-04 | Gesamtergebnisplan + alle Teilergebnispläne im Langformat | ✓ SATISFIED | `ergebnisplan.csv` GESAMT/PB/PG/P rows with required columns intact; PG-level row count rose (3702→3745-ish per the +43-row Regel-1 delta) consistent with the PG split, still a correct long-format representation. |
| EXTR-05 | 02-03, 02-04 | Gesamtfinanzplan + alle Teilfinanzpläne inkl. VE | ✓ SATISFIED | `finanzplan.csv` retains `wertart=ve` rows across all ebenen; `PG,1502,true,` row confirmed present (acceptance-criteria grep from the quick-task plan). |
| PRUEF-01 | 02-03, 02-04 | Zeilenformeln aller Pläne stimmen (Regel 1) | ✓ SATISFIED | Regel 1 grün, 6593 Werte (live run), count increase derived and documented in `test_pruefung.py`. |
| PRUEF-02 | 02-05 | Produkt-Teilpläne = PG = PB-Teilplan (Regel 2) | ✓ SATISFIED | Regel 2 grün, 7994 Werte (live run); manipulation tests still pass (targeted run, 2/2). |
| PRUEF-03 | 02-05 | 15 PB = Gesamtergebnisplan (Regel 3) | ✓ SATISFIED | Regel 3 grün, 114 Werte (live run, unchanged — PG-level split does not affect the PB→Gesamt rollup). |
| PRUEF-04 | 02-01, 02-03, 02-05 | Anhang-B-Sollwerte getroffen (Regel 4) | ✓ SATISFIED | Regel 4 grün, 194 Werte, 0 Abweichungen (live run, unchanged). |
| PRUEF-09 | 02-01, 02-03, 02-05 | Alle Prüfungen in pytest, `konsistenz.md`, >1€-Gate | ✓ SATISFIED | 152/152 pytest green (live run); >1€ gate re-confirmed live. |

No orphaned requirements: all 10 IDs declared across the five Phase-2 plans (`EXTR-01..05`, `PRUEF-01,02,03,04,09`) match the 10 IDs this task lists and the ROADMAP.md traceability table (all marked "Complete").

### Determinism / Reproducibility (live, this session)

```
$ uv run --directory pipeline python alle.py --jahr 2026
Jahrgang 2026: raw_data/haushalt-2026.pdf (400 Seiten erwartet), 15 Seitenbereiche, Sollwerte geladen.
Schritt 01: 400 Seiten klassifiziert, 0 unbekannt, 15 PB, 49 PG (41 synthetisch), 63 Produkte.
Schritt 02: 14899 Planzeilen geschrieben.
Schritt 06: Regel 1: grün (6593 Werte)
Schritt 06: Regel 2: grün (7994 Werte)
Schritt 06: Regel 3: grün (114 Werte)
Schritt 06: Regel 4: grün (194 Werte)
Schritt 06: Veraltete Befunde: 0

$ git status --porcelain daten/
(empty)

$ uv run --directory pipeline pytest -q
152 passed in 43.15s

$ uv run --directory pipeline ruff check .
All checks passed!

$ uv run --directory pipeline ruff format --check .
21 files already formatted
```

### Anti-Patterns Found

No debt markers (`TBD`/`FIXME`/`XXX`/`TODO`/`HACK`/`PLACEHOLDER`) in any `pipeline/ostbevern/*.py` or `pipeline/*.py` file (scanned live, this session, across all 12 Phase-2 pipeline source files). `ruff check .` and `ruff format --check .` both pass clean.

### Open Code-Review Findings (carried forward, non-blocking)

Per `02-REVIEW-DISPOSITION.md`, 3 findings remain open (unchanged status from the prior verification — none are in files altered by the post-verification commits, and none block the Phase 2 goal):

| ID | Severity | Summary | Why non-blocking |
|---|---|---|---|
| WR-03 | warning | `_pruefe_regel4_b1` could raise a bare `IndexError` instead of `PruefungsFehler` if `jahre`/`spalten` ever go out of sync | Still present at `pruefung.py:556` (confirmed live); defensive-coding gap for a hypothetical future Jahrgang mismatch, not triggered by 2026 data. |
| IN-01 | info | Duplicate derivation of the D-14 PG-resolution rule in tests vs. production code | Cosmetic; reviewer's own disposition says "No action required now". |
| IN-02 | info | `lies_befunde`'s table parser has no guard against `\|` inside free text | Fails loudly if ever triggered; no current data triggers it. |

WR-01 and WR-02 (both warning-severity, both in this re-verification's scope) are now `fixed` per `02-REVIEW-DISPOSITION.md` and independently confirmed above.

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Full pipeline run succeeds and is deterministic | `uv run --directory pipeline python alle.py --jahr 2026` then `git status --porcelain daten/` | exit 0, 49 PG (41 synthetisch), empty diff | ✓ PASS |
| Full test suite green | `uv run --directory pipeline pytest -q` | 152 passed | ✓ PASS |
| Lint/format clean (CI parity) | `uv run --directory pipeline ruff check .` / `ruff format --check .` | clean | ✓ PASS |
| 2€ injected deviation turns Regel 4 red / 1€ stays green | `pytest -k "abweichung_ueber_einem_euro or toleriert_einen_euro"` | 2 passed | ✓ PASS |
| Manipulated product/PB row caught at correct hierarchy level | `pytest -k manipul` | 2 passed | ✓ PASS |
| Config/hierarchy validation tests (konfiguration + seiten) | `pytest -k "konfiguration or test_seiten"` | 51 passed | ✓ PASS |
| PG 1501/1502 split present in hierarchie.csv, ergebnisplan.csv, seiten.csv | direct `grep` (5 checks, see tables above) | all matched | ✓ PASS |

### Human Verification Required

None. This is a deterministic, headless Python pipeline with comprehensive automated test coverage; all observable truths were verified programmatically against the live `HEAD`, not SUMMARY.md claims. (The project's own `02-UAT.md` additionally records 19/19 user-confirmed deliverables from the original Phase-2 UAT round, orthogonal to this automated re-verification.)

### Gaps Summary

No gaps found. All five roadmap Success Criteria, all 10 declared requirement IDs, all 8 quick-task must-have truths, and both code-review fix commits were re-verified against the current `HEAD` with live command execution — not inferred from any SUMMARY.md. The digest in this report's frontmatter (`covered_digest`) is fresh as of this verification run and supersedes the prior report's now-stale digest.

---

_Verified: 2026-10-01T17:11:17Z_
_Verifier: Claude (gsd-verifier)_
