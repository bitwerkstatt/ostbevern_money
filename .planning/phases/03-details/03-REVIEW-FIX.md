---
phase: 03-details
fixed_at: 2026-10-02T08:50:00Z
review_path: .planning/phases/03-details/03-REVIEW.md
iteration: 1
findings_in_scope: 5
fixed: 5
skipped: 0
status: all_fixed
---

# Phase 03: Code Review Fix Report

**Fixed at:** 2026-10-02T08:50:00Z
**Source review:** .planning/phases/03-details/03-REVIEW.md
**Iteration:** 1

**Summary:**
- Findings in scope: 5 (fix_scope: all — WR-01, WR-02, IN-01, IN-02, IN-03)
- Fixed: 5
- Skipped: 0

Verification for all fixes ran both inside an isolated git worktree (full pipeline
test suite, ruff, and a full `alle.py --jahr 2026` run against the real PDF) and is
reproducible from the main checkout after the worktree's commits were fast-forwarded
onto `main`.

## Fixed Issues

### WR-01: `ordne_spalten` tolerance is computed globally, not per-anchor-pair — a single duplicate anchor breaks column assignment for the whole table

**Files modified:** `pipeline/ostbevern/spalten.py`, `pipeline/tests/test_spalten.py`
**Commit:** `e842ff3` (fixed in a prior run of this agent)
**Applied fix:** Replaced the single global tolerance (`min` over every gap between adjacent sorted anchors, computed once up front) with a per-word local tolerance computed from only the assigned anchor's immediate left/right neighbours (after sorting by x1). This matches the fix suggested in the review: a duplicate/zero-gap anchor pair elsewhere in the table no longer collapses the tolerance to 0 for unrelated, unambiguous words. Updated the function docstring to describe the new local-tolerance semantics. Added a regression test (`test_ordne_spalten_doppelter_anker_bricht_nicht_die_ganze_zuordnung`) reproducing the review's exact example (`anker_x1 = [100.0, 100.0, 500.0]`, word at `x1=500.0`) and asserting it is still assigned instead of raising `SpaltenFehler`.
Verification (from the prior run): all 5 existing `test_spalten.py` cases plus the new regression test pass unchanged; full pipeline test suite (295 tests) passes; `ruff check`/`ruff format --check` clean; no change to any file under `daten/`.

### WR-02: `test_alle.py` mocks `extrahiere_produkte` with a 2-tuple, but the real function returns a 3-tuple

**Files modified:** `pipeline/tests/test_alle.py`
**Commit:** `20bab38` (fixed in a prior run of this agent)
**Applied fix:** Updated `_produkte_ergebnisse()` to return a 3-tuple matching `produkte.extrahiere_produkte`'s actual return contract `(produkte_ergebnis, grundzahlen_ergebnis, erlaeuterungen_ergebnis)` — confirmed by reading `pipeline/ostbevern/produkte.py:941-1063`, which returns exactly this order. Added the missing middle `ProdukteErgebnis` for `grundzahlen.csv` (`zeilen_geschrieben=1234`, matching the review's suggested fixture) and a comment documenting the expected order so a future edit doesn't silently drop it again.
Verification (from the prior run): `tests/test_alle.py` (7 tests) passes; `ruff check`/`ruff format --check` clean; no change to any file under `daten/`.

### IN-01: `alle.py` reuses the "Schritt 06" label for two unrelated operations, inconsistent with `06_pruefen.py`'s own labeling of the same step

**Files modified:** `pipeline/alle.py`
**Commit:** `0a758a6`
**Applied fix:** Verified the code still matched the review's description exactly (the querschnitte-extraction line was prefixed `"Schritt 06: Querschnitte: ..."` while `06_pruefen.py` prints the equivalent line unprefixed as `"Querschnitte: ..."`). Dropped the `"Schritt 06: "` prefix from `alle.py`'s querschnitte line, matching `06_pruefen.py`'s own labeling. Grepped `test_alle.py` first to confirm no test asserts on the exact "Schritt 06: Querschnitte" string — none does, so this is a pure log-text change with no behavioural side effect.
Verification: full pipeline test suite (295 tests) passes; `ruff check`/`ruff format --check` clean; a full `uv run --directory pipeline python alle.py --jahr 2026` run against the real PDF prints `Querschnitte: 1152 Werte geschrieben.` as expected and produces no diff under `daten/`.

### IN-02: CLI help text for `03_produktinfos.py` / `04_investitionen.py` doesn't mention all artifacts the command actually writes

**Files modified:** `pipeline/03_produktinfos.py`, `pipeline/04_investitionen.py`
**Commit:** `b590bdb`
**Applied fix:** Extended `03_produktinfos.py`'s Typer help string to `"Extrahiert Produktinformationen, Grundzahlen und Erläuterungen aus den Produktseiten."` and `04_investitionen.py`'s to `"Extrahiert Investitionsmaßnahmen, VE-Fälligkeiten und die PB-Investitionslisten aus den Produktseiten."`, matching the review's suggested wording exactly. Confirmed both strings stay within the project's 100-char ruff line-length limit.
Verification: full pipeline test suite (295 tests) passes; `ruff check`/`ruff format --check` clean; no change to any file under `daten/`.

### IN-03: `schreibe_csv` relies on a blind `.cast(spalten)` that can silently coerce/truncate mismatched types instead of failing loud

**Files modified:** `pipeline/ostbevern/schema.py`
**Commit:** `12e7b93`
**Applied fix:** Added `strict=True` to the single central `.cast(spalten)` call in `schreibe_csv`, with a comment tying it to the project's D-08 fail-loud convention, per the review's suggested minimal fix. Before applying, audited every `pl.DataFrame(...)` construction site that feeds into `schreibe_csv` (via `schreibe_plan_csv`, `schreibe_seiten_csv`, `schreibe_hierarchie_csv`, `schreibe_querschnitte_csv`, `schreibe_investitionen_csv`, `schreibe_ve_faelligkeiten_csv`, `schreibe_erlaeuterungen_csv`, `schreibe_grundzahlen_csv`, `schreibe_investitionen_pb_csv` across `produkte.py`, `querschnitte.py`, `seiten.py`, `plaene.py`, `investitionen.py`) and confirmed each already builds its DataFrame with an explicit `schema=` dict identical to the target `*_SPALTEN` dtypes, so `strict=True` is a no-op for every current call site and only changes behaviour for a future type mismatch.
Verification: full pipeline test suite (295 tests) passes; `ruff check`/`ruff format --check` clean; a full `uv run --directory pipeline python alle.py --jahr 2026` run against the real PDF completes with all 7 consistency rules green and produces no diff under `daten/` (confirmed via `git status` after the run) — i.e. the stricter cast does not change any generated output.

## Skipped Issues

None — all five in-scope findings were fixed.

---

_Fixed: 2026-10-02T08:50:00Z_
_Fixer: Claude (gsd-code-fixer)_
_Iteration: 1_
