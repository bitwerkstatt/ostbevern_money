---
phase: 07-feinschliff-und-ver-ffentlichung
plan: 02
subsystem: pipeline
tags: [pipeline, code-review, fail-fast, pytest, polars]

requires:
  - phase: 02-kernzahlen
    provides: pruefung.py (Regeln 1-4, lies_befunde), Review-Ledger 02
  - phase: 04-manuelle-daten-und-app-daten
    provides: texte.py, app_daten.py, ve_uebersicht.csv, Review-Ledger 04
provides:
  - Fail-fast guards for the open Phase-2 and Phase-4 review warnings (D-20), no data change
  - Both review disposition ledgers without an open finding, each with a "Nachtrag Phase 7 (D-20)" section
affects: [07-01 Quellenbelege (reads the unchanged daten/), pipeline test suite]

actuals:
  tokens: 9700
  tasks: 2
  commits: 6
plan_head_before: e0a91c5c974c1469646175280212ef7f381d6931
plan_head_after: 03ae4bb4db0545e1b6e614e53a5803bc0cd91835

tech-stack:
  added: []
  patterns:
    - "Fail-fast validation that is not a Prüfpunkt, so konsistenz.md stays byte-identical"
    - "Formula table wrapped once (_mit_eingabepruefung) so every formula raises TexteFehler with formula name and missing key"

key-files:
  created: []
  modified:
    - pipeline/ostbevern/pruefung.py
    - pipeline/ostbevern/texte.py
    - pipeline/ostbevern/app_daten.py
    - pipeline/jahrgaenge/2026_sollwerte.toml
    - pipeline/tests/test_pruefung.py
    - pipeline/tests/test_texte.py
    - pipeline/tests/test_app_daten.py
    - pipeline/tests/test_manuell.py
    - .planning/phases/02-kernzahlen/02-REVIEW-DISPOSITION.md
    - .planning/phases/04-manuelle-daten-und-app-daten/04-REVIEW-DISPOSITION.md

key-decisions:
  - "lies_befunde splits cells on unescaped pipes only and accepts a backslash-escaped pipe inside begruendung; the consistency report escapes pipes on output so rows stay copyable"
  - "validiere_ve_uebersicht compares per-year summary rows with the single rows exactly in T€ (1 T€ = 1000 € is already above the Regel-5 tolerance of 1 €), independent of the TOLERANZ_EURO knob that tests monkeypatch"
  - "ABGELEITET is built from _ABGELEITET_ROH through one wrapper instead of editing every formula; textwerte lost its own try/except because the wrapper raises TexteFehler"
  - "WR-04 (Quelle ranges), WR-06/IN-01 (formatiere) and the textwerte level of WR-03 were already fixed in Phase 5; they are verified and recorded with the original commits, not re-implemented"

patterns-established:
  - "Triage of review findings is re-derived from review files and git history because IDs are reused across review runs"

requirements-completed: [DATA-04]

coverage:
  - id: D1
    description: "_pruefe_regel4_b1 raises PruefungsFehler naming both lengths when Spaltenköpfe and Jahre differ"
    requirement: DATA-04
    verification:
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_regel4_b1_laengenabweichung_bricht_mit_beiden_laengen_ab"
        status: pass
    human_judgment: false
  - id: D2
    description: "lies_befunde names the line for an unescaped pipe in begruendung and accepts an escaped pipe"
    requirement: DATA-04
    verification:
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_lies_befunde_unmaskierte_pipe_in_begruendung_nennt_zeilennummer"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_lies_befunde_maskierte_pipe_in_begruendung_ist_gueltig"
        status: pass
    human_judgment: false
  - id: D3
    description: "ve_uebersicht per-year summary rows are validated before any rule runs"
    requirement: DATA-04
    verification:
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_pruefe_alles_bricht_bei_abweichender_ve_jahressumme_ab"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_ve_uebersicht_jahressummen_stimmen_auf_eingecheckten_daten"
        status: pass
    human_judgment: false
  - id: D4
    description: "Schuldenstand-Fortschreibung raises AppDatenFehler without a preceding printed Stand"
    requirement: DATA-04
    verification:
      - kind: unit
        ref: "pipeline/tests/test_app_daten.py#test_schuldenstand_fortschreibung_ohne_gedruckten_stand_vor_dem_jahr_bricht_ab"
        status: pass
    human_judgment: false
  - id: D5
    description: "Every ABGELEITET formula raises TexteFehler naming formula and missing input key"
    requirement: DATA-04
    verification:
      - kind: unit
        ref: "pipeline/tests/test_texte.py#test_abgeleitete_formel_ohne_eingabewert_nennt_formel_und_schluessel"
        status: pass
    human_judgment: false
  - id: D6
    description: "pruefe_text requires the jahr kürzel for jahr.* placeholders; texte.json haushaltsjahr must equal werte jahr.haushaltsjahr"
    requirement: DATA-04
    verification:
      - kind: unit
        ref: "pipeline/tests/test_texte.py#test_pruefe_text_jahr_platzhalter_braucht_formatkuerzel_jahr"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_app_daten.py#test_texte_haushaltsjahr_muss_zu_jahr_wert_passen"
        status: pass
    human_judgment: false
  - id: D7
    description: "alle.py --jahr 2026 regenerates daten/ and app/src/data/ without any diff (D-20)"
    requirement: DATA-04
    verification:
      - kind: other
        ref: "uv run --directory pipeline python alle.py --jahr 2026, then git status shows no change under daten/ or app/src/data/"
        status: pass
    human_judgment: false
  - id: D8
    description: "Both review ledgers carry a disposition for every finding with the fixing commit"
    requirement: DATA-04
    verification: []
    human_judgment: true
    rationale: "Whether each cited commit really closes its finding is a reading judgment; the grep acceptance checks only prove that no open finding remains"

duration: 62min
completed: 2026-10-06
status: complete
---

# Phase 7 Plan 02: Review-Restpunkte der Phasen 2 und 4 als Guards Summary

**D-20 closed with fail-fast guards only: Regel-4-B1 length check, escaped-pipe parsing in lies_befunde, ve_uebersicht per-year validation, explicit Schuldenstand lookup, formula-input errors and a jahr-kürzel guard, with both review ledgers at zero open findings and daten/ plus app/src/data/ byte-identical after alle.py.**

## Performance

- **Duration:** 62 min
- **Started:** 2026-10-06T10:47:00Z
- **Completed:** 2026-10-06T11:49:00Z
- **Tasks:** 2
- **Files modified:** 10

## Accomplishments

- Phase-2 rest points: `_pruefe_regel4_b1` length guard (WR-03), cell parsing that honours escaped pipes with line number and hint on extra cells (IN-02), `REGEL3_ZEILEN` comment naming every excluded line, PB 09/15 Z. 29 comment citing PDF-Seite 296/299 as the independent source.
- Phase-4 rest points: `validiere_ve_uebersicht` (WR-01), `schreibe_schuldenstand_fort` (WR-02), formula wrapper (WR-03), `jahr.` kürzel guard in `pruefe_text` (WR-05), `pruefe_texte_haushaltsjahr` (IN-02).
- Triage re-derived from review files and git history: WR-01/WR-02 of Phase 2 verified fixed (39214cf, 1f5cfaa), WR-04, WR-06, IN-01 of Phase 4 verified fixed in Phase 5 (9d18267, 65cd6d8), Phase-2 IN-01 skipped with the review's own reason.
- Reproducibility gate: `alle.py --jahr 2026` ran green (Regeln 1-10 grün, 0 veraltete Befunde) and left `daten/` and `app/src/data/` unchanged and no untracked files.

## Task Commits

1. **Task 1: Phase-2-Restpunkte (WR-03, IN-02, frühere WR-02/IN-01), Ledger 02**
   - RED `050fbb8` (test), GREEN `ee7f4ae` (feat), ledger `41be048` (docs)
2. **Task 2: Phase-4-Restpunkte (WR-01...WR-05, IN-02), Ledger 04, Reproduzierbarkeits-Gate**
   - RED `9541954` (test), GREEN `d53ffc7` (feat), ledger `03ae4bb` (docs)

**Plan metadata:** the SUMMARY commit follows this file (docs).

## TDD Gate Compliance

RED and GREEN commits exist for both tasks (`test(07-02)` before `feat(07-02)`); no REFACTOR commit was needed. RED evidence was taken from the real pytest runs (not through `gsd_run check tdd-red-evidence`, pytest's console format is not one of its adapters).

- Task 1 RED: `test_regel4_b1_laengenabweichung_*` (2 cases) and the two `lies_befunde` pipe tests failed because the guard was missing (no PruefungsFehler for the length mismatch, a too-many-cells error without escape support and hint). Semantic assessment: the target tests executed and failed on the planned assertion. The one deviation: the unescaped-pipe case already raised a generic "N Zellen, erwartet 10" error with the line number, so its RED came from the missing hint (`Pipe`) and the missing escape support, not from a missing exception.
- Task 2 RED: 8 of 9 new tests failed with AttributeError (helpers not yet present) or on the missing behaviour; the ve_uebersicht `pruefe_alles` test failed with "DID NOT RAISE PruefungsFehler". Semantic assessment: the AttributeError failures are RED by absence of the new public helper the test names; the behavioural assertions (message contents, year named) are only reachable after GREEN.
- WR-04 needed no new RED test: the behaviour list's range-form tests already exist (`test_lies_erklaerungen_lehnt_seitenspannen_in_der_quelle_ab`, covers "S. 24/25" and "S. 309-311") and pass; the finding is recorded as fixed by 9d18267.

## Files Created/Modified

- `pipeline/ostbevern/pruefung.py` - length guard, escaped-pipe parsing, `_maskiere_pipe`, `validiere_ve_uebersicht`, extended `REGEL3_ZEILEN` comment
- `pipeline/ostbevern/texte.py` - `_mit_eingabepruefung` wrapper, `jahr.` kürzel guard in `pruefe_text`
- `pipeline/ostbevern/app_daten.py` - `schreibe_schuldenstand_fort`, `pruefe_texte_haushaltsjahr`
- `pipeline/jahrgaenge/2026_sollwerte.toml` - comment citing PDF-Seite 296/299, values unchanged
- `pipeline/tests/test_pruefung.py`, `test_texte.py`, `test_app_daten.py` - fail-first tests
- `pipeline/tests/test_manuell.py` - one test adapted (see Deviations)
- `.planning/phases/02-kernzahlen/02-REVIEW-DISPOSITION.md`, `.planning/phases/04-manuelle-daten-und-app-daten/04-REVIEW-DISPOSITION.md` - dispositions and "Nachtrag Phase 7 (D-20)"

## Decisions Made

See `key-decisions` in the frontmatter. In short: escaped pipes instead of forbidding pipes, exact T€ comparison for the VE sums, one wrapper for all formulas, and verified-not-reimplemented for findings already closed in Phase 5.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Existing tests collided with the new guards**
- **Found during:** Task 2 (full suite run)
- **Issue:** `test_regel5_ve_uebersicht_luecke_bei_fehlendem_paar` removes one single row from `ve_uebersicht.csv` to provoke a Regel-5 Lücke, which the new validation now rejects first. `test_texte_py_validiert_sich_selbst_gegen_echte_daten` used the `zahl` kürzel for `jahr.haushaltsjahr`, the very CR-01 pattern the new guard forbids. `test_regel5_lfd_zwecke_gleich_transferposten` monkeypatches `TOLERANZ_EURO = -1`, which made a tolerance-based sum check fail.
- **Fix:** the sum check compares exactly in T€ (no tolerance dependency); the Lücke test now also reduces the 2027 summary row by the removed amount; the self-test uses the `jahr` kürzel.
- **Files modified:** `pipeline/ostbevern/pruefung.py`, `pipeline/tests/test_manuell.py`, `pipeline/tests/test_texte.py` (test_manuell.py is not in the plan's file list)
- **Verification:** full pytest 558 passed, 1 skipped
- **Committed in:** d53ffc7

**2. [Rule 1 - Bug in plan assumption] IN-02 of Phase 2 already failed loudly**
- **Found during:** Task 1
- **Issue:** `lies_befunde` already raised an error with line number for too many cells, so "reject with line number" was not new. What was missing is the hint and a way to write a pipe.
- **Fix:** support for backslash-escaped pipes, a hint in the error, docstring, and escaping in the report writer so a copied row still parses.
- **Files modified:** `pipeline/ostbevern/pruefung.py`
- **Committed in:** ee7f4ae

---

**Total deviations:** 2 auto-fixed (1 blocking, 1 plan assumption corrected)
**Impact on plan:** No scope creep; the data and reports are unchanged.

## Issues Encountered

- The full pytest suite takes about 6 minutes, so it ran in the background; one test file (`test_formatiere.py`, 1 test) is skipped because `app/node_modules` is absent in the worktree (not touched by this plan).

## Befunde für den Nutzer

None. The reproducibility gate showed no diff, so no finding is `deferred`.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- The pipeline guards are in place and the data Plan 07-01 points its Quellenbelege at is unchanged.
- Both ledgers have no open findings.

## Self-Check: PASSED

- Files exist: `pipeline/ostbevern/pruefung.py`, `texte.py`, `app_daten.py`, both disposition files (checked below).
- Commits exist: 050fbb8, ee7f4ae, 41be048, 9541954, d53ffc7, 03ae4bb.
- Acceptance greps: `Nachtrag Phase 7` in both ledgers, `S. 296` in the sollwerte file, `disposition: open` count 0 in both ledgers, WR-03 of ledger 02 `disposition: fixed`.

---
*Phase: 07-feinschliff-und-ver-ffentlichung*
*Completed: 2026-10-06*
