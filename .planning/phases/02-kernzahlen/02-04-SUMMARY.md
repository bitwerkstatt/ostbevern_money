---
phase: 02-kernzahlen
plan: 04
subsystem: pipeline
tags: [pdfplumber, polars, pytest, teilplaene, formula-chain, synthetic-pg]

requires:
  - phase: 02-02
    provides: "seiten.csv (teilergebnisplan/teilfinanzplan page typing, D-17), hierarchie.csv (15 PB, 48 PG davon 40 synthetisch, 63 Produkte)"
  - phase: 02-03
    provides: "ZEILEN/FORMELN scaffolding for teilergebnisplan/teilfinanzplan (rows left to fill), pruefung.Planwerte formula-chain resolver, befunde.md policy (D-02 to D-05)"
provides:
  - "ostbevern/zeilen.py: ZEILEN['teilergebnisplan'] (01-31) and ZEILEN['teilfinanzplan'] (19 verified rows)"
  - "ostbevern/plaene.py: Abschnitt dataclass, lies_abschnitte (splits a Teilplan page into Teilergebnisplan-/Teilfinanzplan-Abschnitte by scanning for both section headers), lies_teilplaene (extracts PB/PG/P Teilpläne with completeness and duplicate-row checks), _synthetische_pg_datensaetze (D-14 aggregation), extrahiere_plaene now writes complete Gesamt+Teil CSVs in one pass"
  - "daten/aufbereitet/ergebnisplan.csv and finanzplan.csv: complete long-format CSVs with GESAMT, all 15 PB, 8 printed PG, 40 synthetic PG, and 63 Produkt Teilpläne"
  - "daten/pruefberichte/befunde.md: 3 Schlüsseltabelle rows (same PDF-printed 2€ rounding artifact on PB/PG/P level) + PG 1501/1502 observation"
affects: [02-05-weitere-pruefregeln, 04-app-json]

actuals:
  tokens: 10845
  tasks: 2
  commits: 3
  plan_head_before: 78266e06b837214cad89d597930e797f730d5f55
  plan_head_after: 152d99422331af3d5308e4fd3196a4b66f3a917f

tech-stack:
  added: []
  patterns:
    - "Section scanning by content, not page typ: lies_abschnitte scans a Teilplan page's full word stream for both Teilergebnisplan/Teilfinanzplan headers (title-line or bare continuation table-head, distinguished by the first word being 'Nr.') with a small state machine, instead of trusting seiten.csv's one-typ-per-page classification — PB/PG/Produkt pages routinely share one physical page for both plan types"
    - "lies_teilplaene is ebene-agnostic by construction: the same function handles PB, printed PG, and Produkt nodes via a collection parameter, with per-node completeness (exactly one Teilergebnisplan, at least one Teilfinanzplan section) and duplicate-row checks enforced generically — this is why Task 2 needed no changes to the extraction logic itself, only widening the ebenen argument and adding synthetic PG aggregation"
    - "Synthetic PG aggregation (D-14) sorts product rows by code ascending and groups by (zeile, jahr, wertart), taking betrag as the sum and pdf_seite/operator from the first (lowest-code) product that prints a given row — a single-product PG is therefore an exact copy without special-casing"

key-files:
  created: []
  modified:
    - pipeline/ostbevern/zeilen.py
    - pipeline/ostbevern/plaene.py
    - pipeline/tests/test_plaene.py
    - pipeline/tests/test_hierarchie.py
    - pipeline/tests/test_pruefung.py
    - daten/aufbereitet/ergebnisplan.csv
    - daten/aufbereitet/finanzplan.csv
    - daten/pruefberichte/konsistenz.md
    - daten/pruefberichte/befunde.md

key-decisions:
  - "lies_abschnitte distinguishes a Teilfinanzplan title from its own bare continuation table-head by checking whether the line's first word is 'Nr.' rather than by position — this also solves 'a title directly followed by its own head line opens one section, not two' for free: once a section is open, a later line matching the same pattern via its 'Nr.' alternative is just content, not a new section start"
  - "Synthetic PG rows are built from the already-extracted Produkt rows (teil_df, after lies_teilplaene), not re-derived from the PDF — this keeps D-14 aggregation a pure in-memory grouping step with no extra PDF access and guarantees synthetic PG betrag/operator/pdf_seite trace back to exactly the product rows the pipeline already validated"
  - "A genuine 2€ PDF-printed rounding discrepancy (PB 08 Teilergebnisplan Z. 17, Ergebnis 2024) was found and documented in befunde.md at all three levels it appears at (PB 08, PG 0801, P 080101) — PB 08 has only one product, so the same table is effectively reprinted on the PB-level and product-level pages, and the artifact is genuinely present on both pages (verified word-for-word against the PDF, not an extraction bug)"
  - "Deviation: test_pruefung.py's hardcoded Regel-1 geprueft count and known-befunde count (written in 02-03 before any Teilplan rows existed) needed updating twice — once after Task 1 added PB rows (592), again after Task 2 added PG/P rows (6550) — and the test_konsistenzbericht_listet_bekannten_befund fixture needed the new PB08/PG0801/P080101 known-befunde entries added so its manipulated-CSV scenario stays green against the now-complete dataset"

requirements-completed: [EXTR-04, EXTR-05, PRUEF-01]

coverage:
  - id: D1
    description: "ergebnisplan.csv and finanzplan.csv hold, besides GESAMT, the Teilergebnis- and Teilfinanzpläne of all 15 PB, all 8 printed PG, all 40 synthetic PG, and all 63 products, one line per printed value with zeile, zeile_kanonisch, ist_summe, operator and pdf_seite"
    requirement: "EXTR-04"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_plaene.py#test_alle_knoten_haben_teilplaene"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_hierarchie.py#test_jeder_knoten_hat_ergebnis_und_finanzplanzeilen"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_hierarchie.py#test_synthetische_pg_summieren_ihre_produkte"
        status: pass
      - kind: integration
        ref: "uv run --directory pipeline python 02_plaene_extrahieren.py --jahr 2026"
        status: pass
    human_judgment: false
  - id: D2
    description: "Teilfinanzplan continuation across pages (e.g. a product whose Teilfinanzplan continues on the next page) is extracted with correct pdf_seite per row, no duplicate row numbers, and includes the continuation's own rows (VE column included, EXTR-05)"
    requirement: "EXTR-05"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_plaene.py#test_teilfinanzplan_fortsetzung_auf_folgeseite"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_plaene.py#test_pb_teilfinanzplan_hat_sieben_spalten"
        status: pass
    human_judgment: false
  - id: D3
    description: "Regel 1 (zeilenformeln via the formula-chain resolver) is grün for every Gesamt- and Teilplan (PB, printed PG, synthetic PG, Produkt) — 6550 values checked"
    requirement: "PRUEF-01"
    verification:
      - kind: integration
        ref: "uv run --directory pipeline python 06_pruefen.py --jahr 2026 (Regel 1: grün)"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_regel1_sollwerte_gesamtplaene_gruen"
        status: pass
    human_judgment: false

duration: ~45min
completed: 2026-10-01
status: complete
---

# Phase 2 Plan 4: Teilergebnis- und Teilfinanzpläne (PB/PG/Produkt) Summary

**Section-scanning extraction of all 86 printed Teilergebnis-/Teilfinanzpläne plus 40 synthetic Produktgruppen into the long-format CSVs, with Regel 1 (formula-chain) grün across 6550 checked values.**

## Performance

- **Duration:** ~45 min
- **Tasks:** 2
- **Commits:** 3
- **Files modified:** 9

## Accomplishments
- `plaene.lies_abschnitte` splits a Teilplan page's own word stream into Teilergebnisplan-/Teilfinanzplan-Abschnitte by content (title vs. bare continuation table-head), replacing a 1:1 page→plantyp assumption that cannot represent PB/PG/Produkt pages sharing one physical page
- `plaene.lies_teilplaene` extracts any combination of PB/PG/Produkt nodes with per-node completeness (exactly one Teilergebnisplan, at least one Teilfinanzplan section) and duplicate-row checks (D-08); it needed no behavior change between Task 1 (PB only) and Task 2 (all ebenen) — only the caller's `ebenen` argument widened
- `plaene._synthetische_pg_datensaetze` builds the 40 synthetic PG rows (D-14) from already-extracted product rows, summing per zeile/jahr/wertart and tracing pdf_seite/operator to the lowest-code contributing product
- `ergebnisplan.csv`/`finanzplan.csv` now hold the complete long-format dataset: GESAMT, 15 PB, 8 printed PG, 40 synthetic PG, 63 Produkt — 10128 and 4697 rows respectively
- Regel 1 is grün for every Gesamt- and Teilplan (6550 values); the one genuine PDF-printed 2€ rounding artifact (PB 08 Z. 17, Ergebnis 2024 — PB 08 has only one product, so the figure appears verbatim on both the PB- and product-level pages) is documented in `befunde.md` at all three levels it surfaces at

## Task Commits

1. **Task 1: Tracer — PB-level Teilpläne end-to-end** - `e6cfbfd` (feat)
2. **Task 2: All PG and product Teilpläne, Teilfinanzplan continuation, synthetic PG rows** - `59d746c` (test, RED) + `152d994` (feat, GREEN)

_No REFACTOR commit — the GREEN implementation stayed minimal (widen `ebenen`, add the synthetic-PG aggregation function, no changes to the already-general section-scanning logic)._

## Files Created/Modified
- `pipeline/ostbevern/zeilen.py` - `ZEILEN["teilergebnisplan"]` (01-31, rows 01-26 reused from gesamtergebnisplan) and `ZEILEN["teilfinanzplan"]` (19 rows)
- `pipeline/ostbevern/plaene.py` - `Abschnitt`, `lies_abschnitte`, `lies_teilplaene`, `_synthetische_pg_datensaetze`, refactored `extrahiere_plaene`/`_gesamtplan_datensaetze`
- `pipeline/tests/test_plaene.py` - PB-level tests (Task 1) + module fixture `_alle_teilplaene` and all-ebenen tests (Task 2)
- `pipeline/tests/test_hierarchie.py` - node-completeness and synthetic-PG-summation tests (Task 2, RED→GREEN)
- `pipeline/tests/test_pruefung.py` - updated Regel-1 count assumptions and known-befunde fixtures twice as the dataset grew (deviation, see below)
- `daten/aufbereitet/ergebnisplan.csv`, `finanzplan.csv` - regenerated, complete
- `daten/pruefberichte/konsistenz.md` - regenerated (Regel 1/4 grün)
- `daten/pruefberichte/befunde.md` - 3 Schlüsseltabelle rows + PG 1501/1502 observation

## Decisions Made
- `lies_abschnitte` tells a Teilfinanzplan title from its own continuation table-head by the first word (`"Nr."` vs. not), not by page position — this incidentally also resolves "title directly followed by its own head line opens one section, not two" since the head line is recognized as ordinary content of the section already opened by the title
- Synthetic PG aggregation operates on the in-memory product rows already produced by `lies_teilplaene`, never re-reading the PDF
- The genuine 2€ PB 08 Z.17 2024 rounding artifact is documented at all three levels (PB, PG, P) it appears at, since PB 08 has exactly one product and the Teilergebnisplan table is effectively printed twice (PB-level page 203, product-level page 206) with the identical figure

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] befunde.md entry for a genuine 2€ PDF rounding discrepancy (PB 08 Z. 17, 2024)**
- **Found during:** Task 1 verification (`06_pruefen.py` reported Regel 1 rot)
- **Issue:** Teilergebnisplan PB 08's printed Z. 17 (186.499) differs by 2 € from the sum of its printed components (186.501); verified word-for-word against the PDF — not an extraction bug, a real printing artifact
- **Fix:** Documented in `befunde.md`'s Schlüsseltabelle (D-02/D-04/D-05); Task 2 added two more rows for the same artifact surfacing at PG 0801 and P 080101 (PB 08 has only one product)
- **Files modified:** `daten/pruefberichte/befunde.md`
- **Verification:** `06_pruefen.py` reports Regel 1 grün; `grep -Eq '^\| Regel 1 .*\| grün \|'` passes
- **Committed in:** `e6cfbfd` (PB level), `152d994` (PG/P levels)

**2. [Rule 1 - Bug] test_pruefung.py hardcoded GESAMT-era assumptions invalidated by new Teilplan rows**
- **Found during:** Task 1 and Task 2 full-suite runs
- **Issue:** `test_regel1_sollwerte_gesamtplaene_gruen` hardcoded `geprueft == 118` (GESAMT-only formula count, written in 02-03 before any Teilplan rows existed) and `test_konsistenzbericht_listet_bekannten_befund` wrote a fixed 2-entry `befunde.md` that no longer covered the Teilplan-level deviation — both broke as a direct, structural consequence of this plan's extraction expanding `ergebnisplan.csv`/`finanzplan.csv` (not test defects, not out-of-scope: the plan's own `<verification>` requires the full suite green)
- **Fix:** Updated the hardcoded counts (592 after Task 1, 6550 after Task 2) and added the matching known-befunde entries to the test's `befunde.md` fixture
- **Files modified:** `pipeline/tests/test_pruefung.py`
- **Verification:** `uv run --directory pipeline pytest -q` exits 0 (117 tests)
- **Committed in:** `e6cfbfd` (first pass), `152d994` (second pass)

---

**Total deviations:** 2 auto-fixed (2 bugs, one spanning both tasks)
**Impact on plan:** Both deviations were necessary consequences of correctly implementing the plan's own scope (complete Teilplan extraction) and were required to keep the plan's own `<verification>` (full pytest suite green) satisfied. No scope creep — `test_pruefung.py` was not in the plan's declared `files_modified`, but leaving it broken would have left the phase in a state its own verification contract forbids.

## Issues Encountered
None beyond the deviations above.

## User Setup Required
None - no external services required.

## Next Phase Readiness
- `ergebnisplan.csv`/`finanzplan.csv` are complete for all nodes (GESAMT, PB, PG printed+synthetic, Produkt) with `pdf_seite` and VE; Plan 02-05's aggregation rules (Produkte → PG → PB → Gesamt, B.3) and Regeln 2/3 can build directly on this data
- `Planwerte`'s formula-chain resolver (02-03) already covers Teilplan formulas at every ebene without changes; Regel 2/3 in 02-05 can reuse it the same way Regel 1 and Regel 4 already do
- The PG 1501/1502 naming question (D-14 vs. Haushaltsquerschnitt) is recorded in `befunde.md`'s "Beobachtungen ohne Prüfregel" for a decision before Phase 3's Regel 7
- No blockers for 02-05

---
*Phase: 02-kernzahlen*
*Completed: 2026-10-01*

## Self-Check: PASSED

All files claimed as modified verified present on disk (`pipeline/ostbevern/plaene.py`, `pipeline/ostbevern/zeilen.py`, `pipeline/tests/test_plaene.py`, `pipeline/tests/test_hierarchie.py`, `pipeline/tests/test_pruefung.py`, `daten/aufbereitet/ergebnisplan.csv`, `daten/aufbereitet/finanzplan.csv`, `daten/pruefberichte/konsistenz.md`, `daten/pruefberichte/befunde.md`). All 3 commit hashes (e6cfbfd, 59d746c, 152d994) verified present in `git log --oneline`. Full pipeline suite (117 tests) green; `06_pruefen.py --jahr 2026` reports Regel 1 grün (6550 Werte) and Regel 4 grün (147 Werte); `git status --porcelain daten/` is clean after the final extraction run (byte-identical regeneration); all 12 plan acceptance criteria across both tasks verified via direct grep/test commands.
