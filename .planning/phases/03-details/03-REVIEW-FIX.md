---
phase: 03-details
fixed_at: 2026-10-02T08:10:00Z
review_path: .planning/phases/03-details/03-REVIEW.md
iteration: 1
findings_in_scope: 2
fixed: 2
skipped: 0
status: all_fixed
---

# Phase 03: Code Review Fix Report

**Fixed at:** 2026-10-02T08:10:00Z
**Source review:** .planning/phases/03-details/03-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 2 (fix_scope: critical_warning — WR-01, WR-02; no critical findings were reported; IN-01, IN-02, IN-03 were out of scope)
- Fixed: 2
- Skipped: 0

## Fixed Issues

### WR-01: `ordne_spalten` tolerance is computed globally, not per-anchor-pair — a single duplicate anchor breaks column assignment for the whole table

**Files modified:** `pipeline/ostbevern/spalten.py`, `pipeline/tests/test_spalten.py`
**Commit:** `e842ff3`
**Applied fix:** Replaced the single global tolerance (`min` over every gap between adjacent sorted anchors, computed once up front) with a per-word local tolerance computed from only the assigned anchor's immediate left/right neighbours (after sorting by x1). This matches the fix suggested in the review: a duplicate/zero-gap anchor pair elsewhere in the table no longer collapses the tolerance to 0 for unrelated, unambiguous words. Updated the function docstring to describe the new local-tolerance semantics. Added a regression test (`test_ordne_spalten_doppelter_anker_bricht_nicht_die_ganze_zuordnung`) reproducing the review's exact example (`anker_x1 = [100.0, 100.0, 500.0]`, word at `x1=500.0`) and asserting it is still assigned instead of raising `SpaltenFehler`.
Verification: all 5 existing `test_spalten.py` cases plus the new regression test pass unchanged; full pipeline test suite (295 tests) passes; `ruff check`/`ruff format --check` clean; no change to any file under `daten/` (confirmed via `git status` after running the test suite — this fix does not affect current 2026 extraction output, consistent with the review's note that it is a latent, not currently-triggered, defect).

### WR-02: `test_alle.py` mocks `extrahiere_produkte` with a 2-tuple, but the real function returns a 3-tuple

**Files modified:** `pipeline/tests/test_alle.py`
**Commit:** `20bab38`
**Applied fix:** Updated `_produkte_ergebnisse()` to return a 3-tuple matching `produkte.extrahiere_produkte`'s actual return contract `(produkte_ergebnis, grundzahlen_ergebnis, erlaeuterungen_ergebnis)` — confirmed by reading `pipeline/ostbevern/produkte.py:941-1063`, which returns exactly this order. Added the missing middle `ProdukteErgebnis` for `grundzahlen.csv` (`zeilen_geschrieben=1234`, matching the review's suggested fixture) and a comment documenting the expected order so a future edit doesn't silently drop it again. Updated the type annotation accordingly.
Verification: `tests/test_alle.py` (7 tests) passes; `alle.py`'s current generic `for ergebnis in ergebnisse_produkte:` loop (confirmed via grep) means no other assertion depended on exactly 2 items, so this change is a pure contract fix with no behavioural side effect on `alle.py` itself. `ruff check`/`ruff format --check` clean; no change to any file under `daten/`.

## Skipped Issues

None — both in-scope findings were fixed.

---

_Fixed: 2026-10-02T08:10:00Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
