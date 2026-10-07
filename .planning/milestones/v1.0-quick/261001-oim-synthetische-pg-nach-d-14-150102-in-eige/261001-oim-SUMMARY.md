---
phase: quick-261001-oim
plan: 01
subsystem: pipeline
tags: [toml, polars, pytest, tdd, konfiguration, seiten, plaene, pruefung]

requires:
  - phase: 02-kernzahlen
    provides: alle.py Schritt 01/02/06 (seiten.py, plaene.py, pruefung.py), lade_jahrgang/lade_sollwerte
provides:
  - D-14 rule generalized to "every synthetic PG has exactly one product", enforced
    (SeitenFehler/PlaeneFehler) and validated against checked-in data
  - Jahrgangsdatei [synthetische_produktgruppen] section (declared code/name/pdf_seite
    overrides for assignments the four-digit-prefix default cannot express)
  - Sollwertdatei [haushaltsquerschnitt_pg] section for the Phase 3 Regel 7 Querschnitt check
  - PG 1502 "Tourismus" (product 150102) split out of PG 1501, matching Haushaltsquerschnitt S. 299/300
affects: [03-details]

actuals:
  tokens: 20952
  tasks: 3
  commits: 5
  plan_head_before: 339f5edc886ca648d345a98df15a04caf7f8905b
  plan_head_after: b5e2b266cc33e90fe9038513798fc8ebb64b27ac

tech-stack:
  added: []
  patterns:
    - "Declared config exceptions: a Jahrgangsdatei section (e.g. [synthetische_produktgruppen])
       holds only the entries that deviate from a code-derived default, validated in full by
       the loader plus a second semantic pass once the extracted hierarchy is known"

key-files:
  created: []
  modified:
    - pipeline/jahrgaenge/2026.toml
    - pipeline/jahrgaenge/2026_sollwerte.toml
    - pipeline/ostbevern/konfiguration.py
    - pipeline/ostbevern/seiten.py
    - pipeline/ostbevern/plaene.py
    - pipeline/tests/test_hierarchie.py
    - pipeline/tests/test_seiten.py
    - pipeline/tests/test_pruefung.py
    - pipeline/tests/test_konfiguration.py
    - daten/zwischen/seiten.csv
    - daten/aufbereitet/hierarchie.csv
    - daten/aufbereitet/ergebnisplan.csv
    - daten/aufbereitet/finanzplan.csv
    - daten/pruefberichte/konsistenz.md
    - daten/pruefberichte/befunde.md

key-decisions:
  - "Decision reconciliation (plan <decision_reconciliation>): the D-14 default stays
     'synthetic PG code = product's first four digits' and 'exactly one product per
     synthetic PG' (collision is now SeitenFehler, never silent summation). Because
     150102's first four digits are 1501 (not 1502), a purely digit-based rule can
     never place it in its own PG 1502 — so the Jahrgangsdatei gets a declared-exception
     section, [synthetische_produktgruppen], keyed by PG code with {produkt, name,
     pdf_seite}. PG 1502 'Tourismus' is declared there, sourced from the
     Haushaltsquerschnitt (S. 299 Ergebnisplan / S. 300 Finanzplan), which the Teilplanbereich
     (S. 66-282) never prints as its own PG header."
  - "pdf_seite_start of a declared synthetic PG in hierarchie.csv stays the product's own
     start page (D-14), not the Haushaltsquerschnitt source page. The config entry's
     pdf_seite (299) documents only where the assignment and name come from."
  - "New [haushaltsquerschnitt_pg] Sollwerte (PG 1501 = -118138, PG 1502 = -72554, S. 299)
     back every declared synthetic PG and are cross-checked against ergebnisplan.csv in
     test_hierarchie.py — not wired into Regel 4 (that belongs to Phase 3 Regel 7, PRUEF-07)."

requirements-completed: [EXTR-03, EXTR-04, EXTR-05, PRUEF-02]

coverage:
  - id: D1
    description: "Every synthetic PG holds exactly one product (D-14); collisions and
      invalid declarations fail loudly instead of silently summing"
    requirement: EXTR-03
    verification:
      - kind: unit
        ref: "pipeline/tests/test_hierarchie.py#test_synthetische_pg_markierung_und_namen"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_seiten.py#test_baue_hierarchie_kollision_ohne_deklaration_meldet_beide_produkte"
        status: pass
    human_judgment: false
  - id: D2
    description: "PG 1502 'Tourismus' (product 150102) is declared via the Jahrgangsdatei
      and regenerates with the Haushaltsquerschnitt S. 299/300 values"
    requirement: EXTR-04
    verification:
      - kind: unit
        ref: "pipeline/tests/test_hierarchie.py#test_haushaltsquerschnitt_pg_sollwerte"
        status: pass
      - kind: integration
        ref: "uv run --directory pipeline python alle.py --jahr 2026 (PG 1501/1502 Z. 29 Ansatz 2026 = -118138/-72554)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Synthetic PG rows in ergebnisplan.csv/finanzplan.csv are exact copies of
      their single product's rows (no more summation)"
    requirement: EXTR-05
    verification:
      - kind: unit
        ref: "pipeline/tests/test_hierarchie.py#test_synthetische_pg_ist_kopie_ihres_einzigen_produkts"
        status: pass
    human_judgment: false
  - id: D4
    description: "Malformed/orphaned [synthetische_produktgruppen] and
      [haushaltsquerschnitt_pg] declarations raise KonfigurationsFehler or SeitenFehler
      (D-08 fail-loud)"
    requirement: PRUEF-02
    verification:
      - kind: unit
        ref: "pipeline/tests/test_konfiguration.py (13 negative mutation tests)"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_seiten.py (3 semantic SeitenFehler cases: missing produkt,
          produkt in a printed PG, declared code is a printed PG)"
        status: pass
    human_judgment: false
  - id: D5
    description: "Pipeline CI green end-to-end and regeneration is byte-identical"
    verification:
      - kind: integration
        ref: "(cd pipeline && uv sync --locked && uv run ruff check . && uv run ruff format --check . && uv run pytest) — 152 passed"
        status: pass
      - kind: integration
        ref: "uv run --directory pipeline python alle.py --jahr 2026 && git diff --exit-code -- daten/"
        status: pass
    human_judgment: false

duration: 17min
completed: 2026-10-01
status: complete
---

# Quick Task 261001-oim: Synthetic PG per D-14, PG 1502 "Tourismus" Summary

**Generalized the synthetic-PG rule to "exactly one product per PG" (collisions now fail loudly instead of silently summing), and declared PG 1502 "Tourismus" (product 150102) via a new Jahrgangsdatei section so it matches the Haushaltsquerschnitt (S. 299/300) instead of being merged into PG 1501.**

## Performance

- **Duration:** ~17 min (first RED commit 18:10 → last GREEN commit 18:27, 2026-10-01)
- **Tasks:** 3 (1 tracer + 2 auto, two of them TDD with RED/GREEN commit pairs)
- **Files modified:** 15 (5 pipeline source/config, 4 test files, 5 regenerated `daten/` files, 1 `befunde.md`)

## Accomplishments

- **PG 1501/1502 split, matching the PDF.** `hierarchie.csv` now has PG 1501 "Wirtschaftsförderung" (product 150101 only) and a new PG 1502 "Tourismus" (product 150102 only). `ergebnisplan.csv` Z. 29 Ansatz 2026: PG 1501 = -118138, PG 1502 = -72554, exactly matching Haushaltsquerschnitt S. 299 (previously PG 1501 alone carried the summed -190692).
- **General rule, not a one-off fix.** `seiten.produktgruppe_fuer_produkt(produkt, jahrgang)` resolves a product's PG code (declared override or the D-14 four-digit-prefix default); `baue_hierarchie` now raises `SeitenFehler` if two products would collide on the same synthetic PG code instead of silently merging them. `plaene._synthetische_pg_datensaetze` determines each synthetic PG's single child from `hierarchie.eltern_code` and emits an exact row copy — no more summation.
- **Declared-exception config section.** `pipeline/jahrgaenge/2026.toml` gained `[synthetische_produktgruppen]`, fully validated by `lade_jahrgang` (key format, required/forbidden fields, six-digit produkt sharing the PG's PB prefix, non-empty name, pdf_seite range, no product declared twice, section must be a table). `2026_sollwerte.toml` gained the optional `[haushaltsquerschnitt_pg]` table, validated the same way, feeding the Phase 3 Regel 7 Querschnitt check.
- **Fail-loud semantic validation.** `baue_hierarchie` additionally checks every declaration against the extracted hierarchy: the declared product must exist, must not already belong to a printed PG, and the declared code must not itself be a printed PG — each raises `SeitenFehler` naming the PG code, the product, and the `[synthetische_produktgruppen]` section (D-08).
- **Existing tests adapted, not weakened.** `test_seiten.py`'s PG-from-product-code test now expects the declared code where one exists, the prefix default otherwise. `test_pruefung.py`'s Regel-1 count (6550 → 6593) is derived in-test from the checked-in CSVs as the 43-cell formula overlap between products 150101/150102, not a bare literal swap.
- **befunde.md cleaned up.** The now-resolved "PG 1501/1502 ... muss entschieden werden" open question is removed from "Beobachtungen ohne Prüfregel"; all 10 Schlüsseltabelle rows are byte-identical to the pre-change baseline.

## Task Commits

1. **Task 1: Tracer, config declaration → hierarchie.csv → both plan CSVs (TDD)**
   - `30c4571` `test(261001-oim): failing tests for one product per synthetic PG (D-14) and PG 1502` (RED)
   - `6d03683` `fix(261001-oim): one product per synthetic PG, PG 1502 Tourismus from Jahrgangsdatei (D-14)` (GREEN)
2. **Task 2: Adapt test_seiten.py/test_pruefung.py, drop resolved befunde.md observation**
   - `c511173` `test(261001-oim): adapt seiten/pruefung tests to D-14 one-product rule, drop resolved PG observation`
3. **Task 3: Fail-loud validation for config declarations and hierarchy assignment (D-08) (TDD)**
   - `9fbe6d6` `test(261001-oim): failing validation tests for synthetic PG declarations` (RED)
   - `b5e2b26` `fix(261001-oim): validate synthetic PG declarations and fail loudly (D-08)` (GREEN)

**Plan metadata:** this SUMMARY's own commit (docs, see below)

## TDD Gate Compliance

Both TDD tasks followed RED → GREEN (no REFACTOR commit needed — the GREEN implementation was already clean):

| Task | RED | GREEN | REFACTOR | Status |
|------|-----|-------|----------|--------|
| 1 (tracer, tdd) | ✓ `30c4571` (6/9 tests failed on real assertions: two P children, missing PG 1502, missing `synthetische_produktgruppen` attribute) | ✓ `6d03683` (9/9 pass) | — | Pass |
| 3 (auto, tdd) | ✓ `9fbe6d6` (16/54 failed, all "DID NOT RAISE" on the target negative assertion) | ✓ `b5e2b26` (all pass) | — | Pass |

**Note on `gsd_run check tdd-red-evidence`:** this repo's test runner is pytest, whose default output is neither TAP (`node --test`) nor Surefire/Failsafe XML — the two formats the RED-evidence classifier parses. The tool could not be used to machine-verify RED here; RED was instead confirmed by direct pytest output inspection against the plan's own `<action>`-specified failure criteria (named explicitly in both task actions), which is what the user-approved plan directs.

## Files Created/Modified

- `pipeline/jahrgaenge/2026.toml` - `[synthetische_produktgruppen."1502"]` declaration (produkt=150102, name=Tourismus, pdf_seite=299) with rationale comment
- `pipeline/jahrgaenge/2026_sollwerte.toml` - `[haushaltsquerschnitt_pg]` Sollwerte for PG 1501/1502 (S. 299)
- `pipeline/ostbevern/konfiguration.py` - `SynthetischeProduktgruppe` dataclass, `Jahrgang.synthetische_produktgruppen`, full loader validation for both new TOML sections
- `pipeline/ostbevern/seiten.py` - `produktgruppe_fuer_produkt` helper; `baue_hierarchie` enforces one-product-per-synthetic-PG and validates declarations against the extracted hierarchy
- `pipeline/ostbevern/plaene.py` - `_synthetische_pg_datensaetze` rewritten to copy (not sum) the single child's rows, membership via `hierarchie.eltern_code` only
- `pipeline/tests/test_hierarchie.py` - rewritten for the one-product rule, copy semantics, and the Haushaltsquerschnitt Sollwert cross-check
- `pipeline/tests/test_seiten.py` - updated PG-resolution test; 5 new constructed `baue_hierarchie` tests (fabricated PB "99", no PDF)
- `pipeline/tests/test_pruefung.py` - Regel-1 count updated with an in-test derivation of the delta
- `pipeline/tests/test_konfiguration.py` - 16 new tests (3 positive, 13 negative) for both config sections
- `daten/zwischen/seiten.csv`, `daten/aufbereitet/{hierarchie,ergebnisplan,finanzplan}.csv`, `daten/pruefberichte/konsistenz.md` - regenerated (49 PG, 41 synthetisch; Regel 1 = 6593 Werte, Regel 2 = 7994 Werte, Regel 3 = 114, Regel 4 = 194, alle grün)
- `daten/pruefberichte/befunde.md` - removed the resolved PG 1501/1502 open question; Schlüsseltabelle unchanged

## Decisions Made

See `key-decisions` in frontmatter. Summary: the D-14 default (code = product's first four digits, exactly one product per synthetic PG) stays the general rule; PG 1502 is a declared exception in the Jahrgangsdatei because a digit-only rule can never place product 150102 (prefix 1501) into its own PG 1502. The declaration's `pdf_seite` (299) documents the Haushaltsquerschnitt source of the assignment/name; the PG's `pdf_seite_start` in `hierarchie.csv` stays the product's own start page (D-14 unchanged). `[haushaltsquerschnitt_pg]` Sollwerte back every declared PG and are cross-checked by tests now, but intentionally not wired into Regel 4 — that belongs to Phase 3 Regel 7 (PRUEF-07).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed own RED-phase test fixture (TOML scalar landed in the wrong table)**
- **Found during:** Task 3 GREEN verification
- **Issue:** `test_synthetische_produktgruppen_falscher_typ_wird_abgelehnt` removed the `[synthetische_produktgruppen."1502"]` section and appended `synthetische_produktgruppen = "nicht-tabelle"` at the end of the file. Because the preceding `[kopfzeilen.seitentypen]` table was still "open" in TOML's sense (no later `[section]` header to close it), the appended line was parsed as `kopfzeilen.seitentypen.synthetische_produktgruppen`, not a top-level key — so the test never actually exercised the type check, before or after GREEN.
- **Fix:** Insert the override right after `haushaltsjahr = 2026`, before any `[section]` header opens, guaranteeing it parses as top-level.
- **Files modified:** `pipeline/tests/test_konfiguration.py`
- **Verification:** `uv run python3 -c 'import tomllib; ...'` confirmed the key lands at the top level; the test then correctly fails before GREEN and passes after.
- **Committed in:** `b5e2b26` (same commit as the GREEN implementation it tests)

---

**Total deviations:** 1 auto-fixed (1 bug in own test fixture, Rule 1)
**Impact on plan:** No scope creep — the fix only corrects a self-introduced test construction error so the negative test actually proves what it claims to prove.

## Known Stubs

None.

## Threat Flags

None — this plan's `<threat_model>` already covered the new config surface (T-261001-oim-01 through -05), and Task 3 implements exactly the mitigations it specifies (strict loader validation plus semantic `SeitenFehler` checks).

## Issues Encountered

None beyond the self-fixed test fixture above.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 3 Regel 7 (Haushaltsquerschnitt-Abgleich, PRUEF-07) can now read `[haushaltsquerschnitt_pg]` Sollwerte directly instead of re-deriving the PG 1501/1502 split.
- `.planning/STATE.md`'s Phase 3 blocker about PG 1501/1502 is resolved by this plan; the orchestrator should update/remove that blocker entry (the executor intentionally did not touch STATE.md or PROJECT.md per plan constraints).
- `produktgruppe_fuer_produkt` and the `[synthetische_produktgruppen]` pattern are reusable if any other product needs a declared PG assignment in a future Jahrgang.

---
*Phase: quick-261001-oim*
*Completed: 2026-10-01*

## Self-Check: PASSED

- All 15 files listed in `key-files.modified` verified present on disk (`[ -f ]`).
- All 5 commits (`30c4571`, `6d03683`, `c511173`, `9fbe6d6`, `b5e2b26`) verified present via `git log --oneline --all`.
- All task-level `<acceptance_criteria>` re-run and passing (see Task Commits / Accomplishments above).
- Plan-level `<verification>` re-run: repo-root CI line (`uv sync --locked && ruff check && ruff format --check && pytest`) — 152 passed; `alle.py --jahr 2026` exits 0 with `49 PG (41 synthetisch)`; a second run leaves `git diff --exit-code -- daten/` clean; `hierarchie.csv`/`ergebnisplan.csv` contain the required PG 1501/1502 rows and values; `.planning/STATE.md`/`.planning/PROJECT.md` untouched by any `(261001-oim)` commit.
