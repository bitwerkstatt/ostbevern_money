---
phase: 03-details
fixed_at: 2026-10-02T13:43:07+02:00
review_path: .planning/phases/03-details/03-REVIEW.md
iteration: 2
findings_in_scope: 1
fixed: 1
skipped: 0
status: all_fixed
---

# Phase 03: Code Review Fix Report

**Fixed at:** 2026-10-02T13:43:07+02:00
**Source review:** .planning/phases/03-details/03-REVIEW.md
**Iteration:** 2

**This report supersedes the previous iteration of `03-REVIEW-FIX.md`** (fix_scope: all,
WR-01/WR-02/IN-01/IN-02/IN-03, status `all_fixed`), which is preserved in git history at
commit `101a4e4`. That iteration fixed an incremental review of `git diff 69bcd19..HEAD`
over 9 files. The current review (`03-REVIEW.md`, reviewed `2026-10-02T11:27:49Z`) re-
examined that same diff and confirmed WR-01, WR-02, IN-01, and IN-02 are correct and
complete with no new findings, but found that the IN-03 fix itself (`strict=True` on
`schema.schreibe_csv`'s central `.cast()`) does not catch the exact precision-loss
scenario it was written to prevent. That gap is raised as the sole new finding, CR-01,
fixed in this iteration.

**Summary:**
- Findings in scope: 1 (fix_scope: critical_warning — CR-01; no WR/IN findings in this review)
- Fixed: 1
- Skipped: 0

**Verification environment:** all fixes and verification ran inside an isolated git
worktree (`.claude/worktrees/rf-03-365247-1790940861`, branch `gsd-reviewfix/03-365247`),
whose commits were fast-forwarded onto `main` and the worktree removed as part of this
agent's cleanup tail. The numbers below are reproducible from the main checkout after
that fast-forward.

## Fixed Issues

### CR-01: `strict=True` in `schema.schreibe_csv` does not catch the float->int precision-loss scenario it was added to prevent — IN-03 is not actually fixed

**Files modified:** `pipeline/ostbevern/schema.py`, `pipeline/tests/test_schema.py` (new file)
**Commit:** `a531fb6`
**Applied fix:** Kept `strict=True` on the central `.cast()` in `schreibe_csv` (it still
catches overflow/NaN/unparsable input), but added an explicit lossless round-trip check
run immediately after the cast: for every column whose source dtype (captured from the
pre-cast, column-selected frame) differs from its target schema dtype and is `Float32`
or `Float64`, the already-cast column is cast back to the source float dtype and
compared element-wise (`null_equal=True`) against the pre-cast values. Any mismatch
raises `SchemaFehler` naming the file path, the column, and both dtypes involved —
following the same `SchemaFehler` naming convention used elsewhere in the module (e.g.
`_pruefe_keine_leeren_strings`, `lies_csv`). Corrected the now-inaccurate comment above
the cast to document precisely what `strict=True` does and does not catch (verified
against the pinned `polars>=1.44.2`), rather than implying full precision-loss coverage.
Added `pipeline/tests/test_schema.py` with two regression tests, following this
project's existing test conventions (German identifiers without umlauts, `tmp_path`
fixtures, `pytest.raises(..., match=...)`):
- `test_schreibe_csv_lehnt_fraktionalen_float_bei_int_narrowing_ab`: a `Float64` column
  with a fractional value (`1234.5`) targeting an `Int64` schema column raises
  `SchemaFehler` matching `"betrag"`, and no file is written.
- `test_schreibe_csv_schreibt_ganzzahligen_float_bei_int_narrowing`: the same schema with
  an integral `Float64` value (`1234.0`) still writes successfully and round-trips to the
  expected `Int64` value, confirming the new check does not reject legitimate data.

Did not touch any `pl.DataFrame(...)` call site that feeds `schreibe_csv` — the review
confirmed by grep that every current call site already passes an explicit `schema=`
matching its target `*_SPALTEN` dtypes 1:1, and the only `Float64` schema column
(`GRUNDZAHLEN_SPALTEN.wert`) is cast to `Float64` (unchanged dtype, so the new check's
`quelle_dtype != ziel_dtype` guard correctly skips it). No currently-generated CSV
changes; the fix closes the latent gap for future columns computed via float arithmetic.

**Verification:**
- `uv run --directory pipeline ruff check .` — all checks passed.
- `uv run --directory pipeline ruff format --check .` — 35 files already formatted.
- `uv run --directory pipeline pytest -q tests/test_schema.py` — 2 passed.
- `uv run --directory pipeline pytest -q` (full suite) — 300 passed in 198.41s.
- `git status --short daten/` — empty; no generated data changed.

## Skipped Issues

None — the single in-scope finding was fixed.

---

_Fixed: 2026-10-02T13:43:07+02:00_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 2_
