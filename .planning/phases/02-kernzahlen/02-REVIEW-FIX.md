---
phase: 02-kernzahlen
fixed_at: 2026-10-01T16:52:15Z
review_path: .planning/phases/02-kernzahlen/02-REVIEW.md
iteration: 1
findings_in_scope: 2
fixed: 2
skipped: 0
status: all_fixed
---

# Phase 02: Code Review Fix Report

**Fixed at:** 2026-10-01T16:52:15Z
**Source review:** .planning/phases/02-kernzahlen/02-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 2 (fix_scope = critical_warning; WR-01, WR-02. IN-01 excluded by scope, no critical findings in this review.)
- Fixed: 2
- Skipped: 0

## Fixed Issues

### WR-01: `_synthetische_pg_datensaetze` keeps a `plantyp` parameter that is now dead code

**Files modified:** `pipeline/ostbevern/plaene.py`
**Commit:** 39214cf
**Applied fix:** Dropped the unused `plantyp: str` parameter from `_synthetische_pg_datensaetze`
(line 481) and updated both call sites in `extrahiere_plaene` (previously lines 540-545) to call
`_synthetische_pg_datensaetze(teil_ergebnisplan, hierarchie)` and
`_synthetische_pg_datensaetze(teil_finanzplan, hierarchie)` without the now-meaningless
`"teilergebnisplan"` / `"teilfinanzplan"` literals. Verified no other call sites or tests
reference the function's old signature. `ruff check .` and `ruff format --check .` pass on the
modified file, and the full pipeline test suite (152 tests) passes.

### WR-02: `befunde.md`'s Regel-1 sign description is still inverted relative to the code

**Files modified:** `daten/pruefberichte/befunde.md`
**Commit:** 1f5cfaa
**Applied fix:** Corrected the prose sentence from "Regel 1: gedruckte Summe minus Formelkette"
to "Regel 1: Formelkette minus gedruckte Summe", matching the actual implementation in
`pipeline/ostbevern/pruefung.py::_pruefe_regel1` (`abweichung = ist − soll` where `ist` =
Formelkette, `soll` = gedruckte Summe) and matching the documented example row (PB 08 Z. 17 2024:
gedruckt 186.499, Formelkette 186.501, `abweichung = +2` = Formelkette − gedruckt). This file is
hand-authored documentation (read/parsed by `pruefung.py`, not generated/written by any pipeline
script), so it was edited directly rather than via pipeline regeneration.

## Skipped Issues

None — all in-scope findings were fixed.

**Note:** IN-01 (duplicate derivation of the D-14 PG-resolution rule in tests vs. production code)
was excluded from this run by `fix_scope: critical_warning` — it is an Info-level finding with no
required action per the reviewer's own "No action required now" guidance. No critical findings
were reported in this review.

## Verification

- `uv run --directory pipeline ruff check .`: clean
- `uv run --directory pipeline ruff format --check .`: clean (file already formatted)
- `uv run --directory pipeline pytest`: 152 passed
- Verification ran inside the isolated git worktree (`.claude/worktrees/rf-02-*`, branch
  `gsd-reviewfix/02-*`) created for this fix run; the worktree's fast-forward merge back onto
  `main` and subsequent removal completed cleanly before this report was written, so the same
  results are reproducible by re-running the commands above directly in the main checkout at
  commit `1f5cfaa`.

---

_Fixed: 2026-10-01T16:52:15Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
