---
phase: 03-details
reviewed: 2026-10-02T11:27:49Z
depth: standard
files_reviewed: 9
files_reviewed_list:
  - pipeline/03_produktinfos.py
  - pipeline/04_investitionen.py
  - pipeline/alle.py
  - pipeline/ostbevern/schema.py
  - pipeline/ostbevern/spalten.py
  - pipeline/tests/test_alle.py
  - pipeline/tests/test_investitionen.py
  - pipeline/tests/test_produkte.py
  - pipeline/tests/test_spalten.py
findings:
  critical: 1
  warning: 0
  info: 0
  total: 1
status: issues_found
---

# Phase 03: Code Review Report

**Reviewed:** 2026-10-02T11:27:49Z
**Depth:** standard
**Files Reviewed:** 9
**Status:** issues_found

## Summary

**This review supersedes `03-REVIEW.md`'s prior iteration (base commit `69bcd19`, 32 files).** That
review raised WR-01, WR-02, IN-01, IN-02, IN-03; all five were fixed in commits `e842ff3`,
`20bab38`, `0a758a6`, `b590bdb`, `12e7b93` (see `03-REVIEW-FIX.md`). This incremental review
re-examined `git diff 69bcd19..HEAD` for the 9 files in scope — the five fix commits plus
`b857f29`, which added three Nyquist validation tests (two `test_finanzierungskonten_*` tests in
`test_investitionen.py`, one Schritt-03 byte-identity test in `test_produkte.py`) — with emphasis
on whether each fix actually delivers what it claims.

**Confirmed correct and complete, no new findings:**
- **WR-01** (`spalten.ordne_spalten`): the per-anchor-pair local tolerance is sound. I traced the
  tie-breaking, rank lookup and neighbour-selection logic by hand against several anchor
  configurations (duplicate pairs, 3-way ties, single/two-anchor edge cases) and against the new
  regression test (`test_ordne_spalten_doppelter_anker_bricht_nicht_die_ganze_zuordnung`); the fix
  genuinely isolates a degenerate anchor pair's zero-gap from unrelated anchors elsewhere in the
  same table, and the regression test genuinely fails against the pre-fix implementation (verified
  by hand-evaluating the old global-`min` formula against the test's exact anchor list).
- **WR-02** (`test_alle.py` mock arity): the 3-tuple fixture order
  `(produkte_ergebnis, grundzahlen_ergebnis, erlaeuterungen_ergebnis)` matches
  `produkte.extrahiere_produkte`'s actual `return` statement exactly (confirmed by reading
  `pipeline/ostbevern/produkte.py:1063-1067`).
- **IN-01** (`alle.py` step-label) and **IN-02** (CLI help text) are plain, accurate textual
  changes; both match what the called functions actually write.
- The two new `test_finanzierungskonten_*_bricht_ab` tests and the new Schritt-03 byte-identity
  test genuinely exercise their target checks — I ran all three in isolation (`pytest -k
  "finanzierungskonten_weichen or byte_identisch"`) against the real PDF and confirmed they pass
  for the right reason (the `match=` regex ties each test to the specific `InvestitionenFehler`
  message produced by `_pruefe_finanzierungskonten`, not an incidental earlier abort). I also ran
  the full pipeline suite (298 tests) — all green.

**New finding (not raised by the prior review):** the **IN-03** fix (`strict=True` on
`schema.schreibe_csv`'s central `.cast()`) does not actually catch the precision-loss scenario it
was written to prevent — see CR-01. I verified this empirically against the pinned polars version
(`polars>=1.44.2`), not just by reading the source, since this is exactly the kind of fix
correctness the orchestrator asked this pass to scrutinize.

## Critical Issues

### CR-01: `strict=True` in `schema.schreibe_csv` does not catch the float→int precision-loss scenario it was added to prevent — IN-03 is not actually fixed

**File:** `pipeline/ostbevern/schema.py:98-100`
**Issue:** The IN-03 fix added `strict=True` to the single central cast every generated CSV goes
through, with the comment "fail loud on precision loss/overflow instead of polars' default silent
coercion/truncation." The original review's own example of the defect class to close was
explicitly "a `Float64` column with a fractional value cast to `Int64`." I verified against the
project's pinned polars version that **polars' `DataFrame.cast(..., strict=True)` does not raise
on exactly this case** — it only raises on genuine overflow (value out of the target integer's
range) or unparsable input (e.g. a non-numeric string). Fractional truncation during a `Float64 ->
Int64` cast is silently accepted under `strict=True`, identically to the pre-fix behaviour:

```python
import polars as pl
df = pl.DataFrame({"betrag": [1234.5]})
df.select(["betrag"]).cast({"betrag": pl.Int64}, strict=True)
# shape: (1, 1)  ┌────────┐ │ betrag │ │ i64    │ ╞════════╡ │ 1234   │ └────────┘
# No exception. 1234.5 was silently truncated to 1234 — the exact defect IN-03 claimed to close.
```
I confirmed the contrast with genuine overflow/NaN, which *do* raise under `strict=True`
(`InvalidOperationError`), so the change is not a complete no-op — it just doesn't cover the
specific precision-loss example that motivated it. No new test was added for this fix (there is no
`test_schema.py` in the suite at all), so nothing would have caught the gap. Today this is latent
rather than active: every `pl.DataFrame(...)` construction site that feeds `schreibe_csv` (in
`produkte.py`, `plaene.py`, `seiten.py`, `investitionen.py`, `querschnitte.py`) already passes an
explicit `schema=` matching the target `*_SPALTEN` dtypes 1:1 (verified by grepping every
`pl.DataFrame(` call site), and the only `Float64` column in any schema (`GRUNDZAHLEN_SPALTEN.wert`)
is cast to `Float64`, not narrowed — so no currently-generated number is wrong. But this is the
single, central write path used by *every* generated CSV in a pipeline whose explicitly stated core
value is "Jede Zahl in der App ist korrekt" and whose accuracy bar is "Abweichungen über 1 €
gegenüber den Planwerten gelten als Fehler." A future change that computes a `betrag`-like column
via float arithmetic (an average, a rounding step, a division) would have its error silently
swallowed by this "fail loud" gate exactly as before IN-03 was filed — while the commit history,
the code comment, and the fix-report's verification notes all now assert the opposite. That
combination — a safety mechanism that doesn't do what its own documentation and verification claim
for its headline example — is a correctness risk in the project's main financial-accuracy
guarantee, not a style nit.
**Fix:** `strict=True` is still worth keeping (it does catch overflow/NaN/unparsable input), but it
must be paired with an explicit lossless-round-trip check for numeric columns, e.g.:
```python
def schreibe_csv(df, pfad, spalten, sortierung):
    _pruefe_keine_leeren_strings(df, spalten, pfad)
    sortiert = df.sort(sortierung, nulls_last=False)
    ausgewaehlt = sortiert.select(list(spalten.keys()))
    geordnet = ausgewaehlt.cast(spalten, strict=True)
    # strict=True alone does not catch Float64->Int64 fractional truncation (verified against
    # polars>=1.44.2) — round-trip every narrowed numeric column explicitly.
    for name, ziel_dtype in spalten.items():
        quelle_dtype = ausgewaehlt.schema[name]
        if quelle_dtype != ziel_dtype and quelle_dtype in (pl.Float32, pl.Float64):
            zurueck = geordnet[name].cast(quelle_dtype)
            if not zurueck.equals(ausgewaehlt[name], null_equal=True):
                raise SchemaFehler(f"{pfad}: Spalte {name!r} verliert Genauigkeit bei Int-Cast")
    ...
```
At minimum, add a `test_schema.py` regression test asserting that `schreibe_csv` raises
`SchemaFehler`/an exception for a `Float64` column with a fractional value targeting an `Int64`
schema column — the exact scenario the IN-03 commit message claims is now covered.

---

_Reviewed: 2026-10-02T11:27:49Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
