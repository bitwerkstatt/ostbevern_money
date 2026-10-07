---
phase: 02-kernzahlen
plan: 05
subsystem: pipeline
tags: [pdfplumber, polars, pytest, pruefregeln, konsistenzbericht, alle.py]

requires:
  - phase: 02-04
    provides: "ergebnisplan.csv/finanzplan.csv complete for all nodes (GESAMT, PB, PG printed+synthetic, Produkt) with pdf_seite; Planwerte formula-chain resolver covering Teilplan formulas at every ebene"
provides:
  - "pipeline/alle.py: main(jahr) chains Schritt 01 (seiten.klassifiziere_seiten) -> 02 (plaene.extrahiere_plaene) -> 06 (pruefung.pruefe_alles + schreibe_konsistenzbericht) via module attributes, D-09; exits 1 on step exceptions or a red/veraltet report (report still written first)"
  - "ostbevern/pruefung.py: Regel 2 (two-level Produkte->PG->PB, teilergebnisplan+teilfinanzplan), REGEL3_ZEILEN and Regel 3 (15 PB -> Gesamtergebnisplan, no TP 27/28), B3_ZEILEN and Regel 4's Anhang B.3 (194 Werte total), Bericht.unbekannte_seiten and the '## Seiten mit typ=unbekannt' report section (D-17)"
  - "pipeline/06_pruefen.py: echoes Regel 1-4 status/counts and the unbekannt-Seiten count"
  - "daten/pruefberichte/konsistenz.md: final Phase 2 report, Regel 1-4 gruen (6550/7920/114/194 Werte), Gesamtstatus gruen"
  - "daten/pruefberichte/befunde.md: 7 new Schluesseltabelle rows for genuine PDF-printed cross-node rounding differences (Regel 2/3), each verified word-for-word against raw_data/haushalt-2026.pdf"
affects: [03-produktinformationen, 04-app-json]

actuals:
  tokens: 14137
  tasks: 3
  commits: 5
  plan_head_before: fa7857561621df22fa980ddefa6c802a05346017
  plan_head_after: fb0f15a07a691954dbe3e3972d4c085efd0a1fd0

tech-stack:
  added: []
  patterns:
    - "Regel 2's two-level aggregation (_pruefe_regel2_ebene) compares the PARENT's own stored/formula value against the SUM of children's own stored/formula values -- never a recursive re-derivation through the whole subtree -- so a deviation surfaces at exactly the hierarchy level where the parent and child figures disagree, with sibling levels unaffected (verified by the +2 EUR product-level manipulation test, which produces exactly one deviation at the PG level and leaves the PB level green)"
    - "Every Prüfregel now shares _spalten_zu_wertart (spalten -> (wertart, jahr) pairs) and reads hierarchie.csv once per pruefe_alles() call for the PG/P and PB/PG child-lookups Regel 2/3/4-B.3 all need"
    - "Genuine PDF-printed rounding differences (where the sum of printed child figures differs by 1-3 EUR from the printed parent figure, in the same table on the same page) are documented in befunde.md with page citations after direct pdfplumber verification against raw_data/haushalt-2026.pdf -- never assumed from the deviation's magnitude alone"

key-files:
  created: []
  modified:
    - pipeline/alle.py
    - pipeline/tests/test_alle.py
    - pipeline/ostbevern/pruefung.py
    - pipeline/06_pruefen.py
    - pipeline/tests/test_pruefung.py
    - pipeline/jahrgaenge/2026_sollwerte.toml
    - daten/pruefberichte/konsistenz.md
    - daten/pruefberichte/befunde.md

key-decisions:
  - "alle.py chains the three Schritt functions via `from ostbevern import plaene, pruefung, seiten` module attributes (not direct function imports), so test_alle.py's monkeypatch.setattr on the module works identically to the real call path"
  - "Regel 3's REGEL3_ZEILEN deliberately excludes Z.18 (Ordentliches Ergebnis) even though it's an additive-looking row: Z.18 is fully determined by Z.10/Z.17 (both in REGEL3_ZEILEN) via the Regel-1-validated formula chain, so checking it separately at the PB-sum level would be redundant, not a gap"
  - "Fixed two Anhang B.3 Sollwerte in 2026_sollwerte.toml (PB 09/15 'ergebnis_mit_internen_verrechnungen') that discussion/SPEZIFIKATION.md had mistranscribed from the Haushaltsquerschnitt's FIRST Produktgruppe row instead of the PB-level total (D-20 'Tippfehler fallen über die Konsistenzregeln auf') -- caught by this plan's own new Regel 4 B.3 check, confirmed via two independent arithmetic paths on the PDF's own printed figures before touching the sollwerte file"

patterns-established:
  - "Prüfregel functions that need both ergebnisplan/finanzplan and hierarchie.csv take `hierarchie: pl.DataFrame` as an explicit parameter rather than re-reading it, keeping pruefe_alles() the single CSV-IO entry point"

requirements-completed: [PRUEF-02, PRUEF-03, PRUEF-04, PRUEF-09]

coverage:
  - id: D1
    description: "alle.py runs Schritt 01 -> 02 -> 06 in order (D-09), exits 1 on any step exception or a red/veraltet Konsistenzbericht (the report is still written first), and regenerates daten/ byte-identically on the committed state"
    requirement: "PRUEF-09"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_alle.py#test_ohne_jahr_nutzt_standardjahr"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_alle.py#test_roter_bericht_beendet_mit_fehler"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_alle.py#test_schrittfehler_beendet_mit_fehler"
        status: pass
      - kind: integration
        ref: "uv run --directory pipeline python alle.py --jahr 2026 (exit 0, git status --porcelain daten/ empty)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Regel 2 (two-level: Produkte->PG and PG->PB, printed and synthetic PG, both Teilplan types) is grün on the extracted data and proven to catch a 2 EUR manipulation at exactly the right hierarchy level"
    requirement: "PRUEF-02"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_regel2_gruen_auf_eingecheckten_daten"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_regel2_erkennt_manipulierte_produktzeile"
        status: pass
      - kind: integration
        ref: "uv run --directory pipeline python 06_pruefen.py --jahr 2026 (Regel 2: grün, 7920 Werte)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Regel 3 (15 PB -> Gesamtergebnisplan, Z. 01-17/19/20, no TP 27/28) is grün with 114 checked values and proven to ignore TP 27/28 and catch a 2 EUR PB-level manipulation"
    requirement: "PRUEF-03"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_regel3_gruen_auf_eingecheckten_daten"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_regel3_ignoriert_tp_27_28"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_regel3_erkennt_manipulierte_pb_zeile"
        status: pass
    human_judgment: false
  - id: D4
    description: "Regel 4 covers Anhang B.3 (194 Werte total: 126 B.1 + 9 B.2 + 12 Satzung + 45 B.3 + 2 PB-Summen), derives a missing PB Z.29 through the formula chain, and raises PruefungsFehler naming an unknown PB key instead of skipping it silently"
    requirement: "PRUEF-04"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_regel4_b3_gruen_auf_eingecheckten_daten"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_regel4_b3_herleitet_fehlende_z29"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_regel4_b3_unbekannte_pb_bricht_ab"
        status: pass
      - kind: integration
        ref: "uv run --directory pipeline python alle.py --jahr 2026 (Regel 4: grün, 194 Werte)"
        status: pass
    human_judgment: false
  - id: D5
    description: "konsistenz.md lists Regel 1-4 in order with Gesamtstatus grün, a '## Seiten mit typ=unbekannt' section (D-17, listed pages do not turn the report rot), and pytest regenerates it byte-identically"
    requirement: "PRUEF-09"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_konsistenzbericht_unbekannte_seiten_keine_auf_echten_daten"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_konsistenzbericht_unbekannte_seiten_gelistet"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_konsistenzbericht_wird_geschrieben"
        status: pass
      - kind: integration
        ref: "(cd pipeline && uv sync --locked && uv run ruff check . && uv run ruff format --check . && uv run pytest) -- CI replay"
        status: pass
    human_judgment: false

duration: ~55min
completed: 2026-10-01
status: complete
---

# Phase 2 Plan 5: Alle Prüfregeln (Regel 1-4), alle.py-Kette und Phase-2-Abschluss Summary

**alle.py chains Schritt 01→02→06 end-to-end; Regel 2 (two-level Produkte→PG→PB), Regel 3 (15 PB→Gesamtergebnisplan) and Regel 4's Anhang B.3 close the Phase 2 consistency check at 194 values, with 7 genuine PDF-printed rounding differences documented and 2 sollwerte.toml transcription bugs fixed.**

## Performance

- **Duration:** ~55 min
- **Tasks:** 3
- **Commits:** 5
- **Files modified:** 8

## Accomplishments
- `alle.py` now runs the full Phase 2 pipeline (Schritt 01 → 02 → 06) in order via module-attribute calls, exits 1 loudly on any step exception or a red/veraltet Konsistenzbericht (writing the report first), and regenerates `daten/` byte-identically on the committed state
- Regel 2 checks both hierarchy levels (Σ Produkte = PG, Σ PG = PB, printed and synthetic PG alike) for both Teilergebnis- and Teilfinanzpläne, over every zeile printed by a parent or any child and every configured column — 7920 values, grün
- Regel 3 sums the 15 Produktbereiche against the Gesamtergebnisplan for Z. 01-17/19/20 (never TP 27/28) — 114 values, grün
- Regel 4 now covers Anhang B.3 in full (194 values total), deriving a PB's missing Z.29 through the same formula-chain resolver Regel 1 already validates, and raising `PruefungsFehler` for an unknown PB key instead of skipping it
- `konsistenz.md` lists a new `## Seiten mit typ=unbekannt` section (D-17); an unbekannt page is listed but does not turn Gesamtstatus rot
- Investigated 7 new cross-node deviations that Regel 2/3 surfaced on the already-committed data (none present before this plan, since Regel 1 only validates a single node's own formula internally) — all 7 verified word-for-word against `raw_data/haushalt-2026.pdf` as genuine PDF-printed rounding artifacts (same class as the pre-existing PB08 Z.17 2024 finding) and documented in `befunde.md` with page citations
- Found and fixed two genuine transcription bugs in `2026_sollwerte.toml`'s Anhang B.3 (PB 09/15), where `discussion/SPEZIFIKATION.md` had copied the first Produktgruppe's Haushaltsquerschnitt row instead of the PB-level total — caught by this plan's own new Regel 4 B.3 check, exactly the "Tippfehler fallen über die Konsistenzregeln auf" scenario D-20 anticipates

## Task Commits

1. **Task 1: Tracer — alle.py chains 01 -> 02 -> 06 end-to-end** - `87a30de` (feat)
2. **Task 2: Regel 2 and Regel 3** - `1095d2c` (test, RED) + `1f65b9b` (feat, GREEN)
3. **Task 3: Anhang B.3 in Regel 4, unbekannt-Seiten, final gate** - `81a2385` (test, RED) + `fb0f15a` (feat, GREEN)

_No REFACTOR commits — each GREEN implementation stayed minimal; the tracer feedback gate after Task 1 re-ran `<verify>` and passed before Task 2 started._

## Files Created/Modified
- `pipeline/alle.py` — chains `seiten.klassifiziere_seiten` → `plaene.extrahiere_plaene` → `pruefung.pruefe_alles`/`schreibe_konsistenzbericht`
- `pipeline/tests/test_alle.py` — monkeypatched fixture + 4 tests for step order, red-report and step-exception failure
- `pipeline/ostbevern/pruefung.py` — `REGEL3_ZEILEN`, `B3_ZEILEN`, `_pruefe_regel2`/`_pruefe_regel2_ebene`, `_pruefe_regel3`, `_pruefe_regel4_b3`, `Bericht.unbekannte_seiten`, new report section
- `pipeline/06_pruefen.py` — echoes the unbekannt-Seiten count
- `pipeline/tests/test_pruefung.py` — 13 new tests across Regel 2/3/4-B.3 and unbekannt-Seiten; `_kopiere_hierarchie_nach`/`_kopiere_seiten_nach`/`_manipuliere_eine_zeile`/`_erste_zeile`/`_lies_schluesseltabelle_markdown_zeilen` helpers
- `pipeline/jahrgaenge/2026_sollwerte.toml` — corrected PB 09/15 Anhang B.3 Z.29 Sollwerte
- `daten/pruefberichte/konsistenz.md` — regenerated, Regel 1-4 grün (6550/7920/114/194 Werte)
- `daten/pruefberichte/befunde.md` — 7 new Schlüsseltabelle rows for Regel 2/3 PDF-printed rounding differences

## Decisions Made
- `alle.py` imports step modules (`from ostbevern import plaene, pruefung, seiten`) rather than their functions directly, so tests can `monkeypatch.setattr` the module attribute exactly as the real call path uses it
- Regel 2's two-level check compares a parent's own value against the sum of its children's own values (never recursing through the whole subtree), so a manipulation at one level surfaces exactly there and nowhere else
- REGEL3_ZEILEN excludes Z.18 deliberately: it's fully covered transitively via Z.10/Z.17 (both in REGEL3_ZEILEN) through the already-Regel-1-validated formula chain
- Sollwerte transcription bugs (PB 09/15) were corrected in `2026_sollwerte.toml` itself, not worked around with a befunde.md entry or widened tolerance, per D-20's explicit guidance that Prüfregel fallout on a Sollwert is the expected mechanism for catching such typos

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Anhang B.3 Sollwerte for PB 09/15 were mistranscribed in 2026_sollwerte.toml**
- **Found during:** Task 3 verification (Regel 4 B.3 reported two large deviations: PB 09 off by -17.700, PB 15 off by -72.554 — far beyond any plausible rounding artifact)
- **Issue:** `discussion/SPEZIFIKATION.md` Anhang B.3 lists PB 09/15's "Ergebnis mit inneren Verrechnungen (TP Z. 29)" as -115.550 and -118.138. Cross-checked against `raw_data/haushalt-2026.pdf`: these are the FIRST Produktgruppe's own figure from the Haushaltsquerschnitt table (PDF S. 296 PG 0901, S. 299 PG 1501) — not the PB-level total. PB 09/15 print no Z.27-29 (PB 15) or only Z.30/31 (PB 09) on their own Teilergebnisplan page (S. 208/271); the pipeline correctly derives Z.29 via the already-Regel-1-validated formula chain from the printed Z.10/17 (and for PB 09, independently confirmed against the printed Z.30/Z.31 on the same page: Z.31=Z.29-Z.30 → Z.29=-123.250-(-10.000)=-133.250, exactly matching Z.10-Z.17=0-133.250)
- **Fix:** Corrected `2026_sollwerte.toml`'s PB 09 Z.29 to -133250 and PB 15 Z.29 to -190692 (= PG1501 -118.138 + PG1502 -72.554, the Haushaltsquerschnitt GESAMTSUMME on S. 299), with a comment explaining the source discrepancy (D-20)
- **Files modified:** `pipeline/jahrgaenge/2026_sollwerte.toml`
- **Verification:** `06_pruefen.py` reports Regel 4 grün (194 Werte); `pytest -q` green
- **Committed in:** `fb0f15a` (Task 3 GREEN)

**2. [Rule 1 - Bug] 7 genuine PDF-printed cross-node rounding differences surfaced by Regel 2/3**
- **Found during:** Task 2 GREEN implementation (Regel 2/3 against the already-committed, unmanipulated CSVs)
- **Issue:** Regel 1 only validates each node's own formula internally; it never checked that a parent's printed figure equals the sum of its children's printed figures. Once Regel 2/3 added that check, 6 Regel-2 and 1 Regel-3 deviation appeared (1-3 EUR each) — all independently verified word-for-word against `raw_data/haushalt-2026.pdf` (e.g. PB 02's printed Z.10 "334.222" vs. its 7 products' printed Z.10 summing to "334.224") as genuine PDF rounding artifacts, not extraction bugs
- **Fix:** Documented all 7 in `daten/pruefberichte/befunde.md`'s Schlüsseltabelle with page citations, following the existing PB08-pattern (D-02/D-04/D-05)
- **Files modified:** `daten/pruefberichte/befunde.md`
- **Verification:** `06_pruefen.py` reports Regel 2/3 grün; both are listed as "Bekannte Befunde" (not open) in `konsistenz.md`
- **Committed in:** `1f65b9b` (Task 2 GREEN)

**3. [Rule 1 - Bug] `400` literal in a Task-1 test_alle.py mock violated the pipeline/tests literal-scan convention**
- **Found during:** Task 3 verification (`grep -rnwE '2026|400|2353506|18443000' pipeline/tests`, an acceptance criterion that scans the whole tests/ tree, not just this task's own files)
- **Issue:** Task 1's `_klassifizierungs_ergebnis()` mock used `anzahl_seiten=400` as an arbitrary placeholder, coincidentally matching the real 2026 PDF page count — tripping the Research convention that forbids these specific literals anywhere in `pipeline/tests`
- **Fix:** Changed the placeholder to `42` (an unrelated, clearly-arbitrary value); the test never asserts on this field's value, so the change is behavior-neutral
- **Files modified:** `pipeline/tests/test_alle.py`
- **Verification:** `grep -rnwE '2026|400|2353506|18443000' pipeline/tests` prints nothing; full suite green
- **Committed in:** `fb0f15a` (Task 3 GREEN)

**4. [Rule 1 - Bug] Regel 2/3's new real deviations broke `test_konsistenzbericht_listet_bekannten_befund`**
- **Found during:** Task 2 GREEN full-suite run
- **Issue:** This existing test writes its own minimal `befunde.md` (only its 2 test-specific entries plus the 3 pre-existing PB08-pattern rows); once Regel 2/3 were wired in, the 7 new genuine deviations above had no matching entry in that minimal file and turned `bericht.ist_gruen` false. Separately, the test's own GESAMT-level manipulation (always on zeile "01", the first sorted sollwerte row) also lands inside `REGEL3_ZEILEN`, introducing a new Regel-3 side effect the test didn't anticipate
- **Fix:** Added `_lies_schluesseltabelle_markdown_zeilen` to layer the test's own entries on top of the real committed `befunde.md` instead of hand-duplicating its rows; added a conditional Regel-3 befund computed from the baseline Σ-PB-vs-GESAMT values whenever `zeile_sollwert` falls inside `REGEL3_ZEILEN`
- **Files modified:** `pipeline/tests/test_pruefung.py`
- **Verification:** `test_konsistenzbericht_listet_bekannten_befund` passes; full suite green
- **Committed in:** `1f65b9b` (Task 2 GREEN)

---

**Total deviations:** 4 auto-fixed (2 Sollwerte/convention bugs, 1 batch of 7 genuine PDF-printed deviations documented, 1 test-fixture fix made necessary by the new rules)
**Impact on plan:** All four were necessary consequences of correctly implementing Regel 2/3/4-B.3 as specified and were required to keep the plan's own `<verification>` (full pytest suite green, `alle.py` byte-identical regeneration) satisfied. No scope creep — `plaene.py`/`seiten.py`/`zeilen.py` were never touched, per the plan's explicit instruction that a rule turning red because of an extraction error is reported back, not patched around; all 4 fixes are in sollwerte data, befunde documentation, or test fixtures.

## Issues Encountered
None beyond the deviations above.

## User Setup Required
None - no external services required.

## Next Phase Readiness
- Phase 2 is complete: Prüfregeln 1-4 are grün (6550/7920/114/194 Werte), `alle.py` runs the full Schritt 01→02→06 chain and regenerates `daten/` byte-identically, CI replay passes
- `pipeline/jahrgaenge/2026_sollwerte.toml` now holds Anhang B.1-B.3 and Satzung § 1-3 fully and correctly (D-18, with the two PB 09/15 corrections documented above)
- Phase 3 (Produktinformationen, Grundzahlen, Erläuterungen, Investitionsmaßnahmen) can build on the complete `hierarchie.csv`/`ergebnisplan.csv`/`finanzplan.csv`/`seiten.csv` dataset and the `Planwerte` formula-chain resolver without changes
- The PG 1501/1502 naming question (recorded in `befunde.md`'s "Beobachtungen ohne Prüfregel" since 02-04) is still open for Phase 3's Prüfregel 7 (Haushaltsquerschnitt-based Produkt→PG→PB sums) — this plan's Regel 2/3 do not touch the Haushaltsquerschnitt pages at all, only the per-PB/PG/Produkt Teilplan pages
- No blockers for Phase 3

---
*Phase: 02-kernzahlen*
*Completed: 2026-10-01*

## Self-Check: PASSED

All 8 claimed files verified present on disk (`pipeline/alle.py`, `pipeline/tests/test_alle.py`, `pipeline/ostbevern/pruefung.py`, `pipeline/06_pruefen.py`, `pipeline/tests/test_pruefung.py`, `pipeline/jahrgaenge/2026_sollwerte.toml`, `daten/pruefberichte/konsistenz.md`, `daten/pruefberichte/befunde.md`). All 5 commit hashes (87a30de, 1095d2c, 1f65b9b, 81a2385, fb0f15a) verified present in `git log --oneline --all`. Full pipeline suite (129 tests) green; `06_pruefen.py --jahr 2026` reports Regel 1-4 grün (6550/7920/114/194 Werte) and 0 veraltete Befunde/unbekannte Seiten; CI replay (`uv sync --locked && ruff check . && ruff format --check . && pytest`) passes; `alle.py --jahr 2026` exits 0 and `git status --porcelain daten/` is empty afterward (byte-identical regeneration), re-verified after the final commit; `git diff --exit-code pipeline/pyproject.toml pipeline/uv.lock` clean; all acceptance criteria across all three tasks verified via direct grep/test commands.
