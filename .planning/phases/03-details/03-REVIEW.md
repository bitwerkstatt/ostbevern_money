---
phase: 03-details
reviewed: 2026-10-02T00:00:00Z
depth: standard
files_reviewed: 32
files_reviewed_list:
  - pipeline/03_produktinfos.py
  - pipeline/04_investitionen.py
  - pipeline/06_pruefen.py
  - pipeline/alle.py
  - pipeline/jahrgaenge/2026.toml
  - pipeline/jahrgaenge/2026_sollwerte.toml
  - pipeline/ostbevern/freitext.py
  - pipeline/ostbevern/investitionen.py
  - pipeline/ostbevern/konfiguration.py
  - pipeline/ostbevern/pdf.py
  - pipeline/ostbevern/produkte.py
  - pipeline/ostbevern/pruefung.py
  - pipeline/ostbevern/querschnitte.py
  - pipeline/ostbevern/schema.py
  - pipeline/ostbevern/spalten.py
  - pipeline/ostbevern/zahlen.py
  - pipeline/tests/conftest.py
  - pipeline/tests/test_alle.py
  - pipeline/tests/test_freitext.py
  - pipeline/tests/test_investitionen.py
  - pipeline/tests/test_konfiguration.py
  - pipeline/tests/test_produkte.py
  - pipeline/tests/test_pruefung.py
  - pipeline/tests/test_querschnitte.py
  - pipeline/tests/test_spalten.py
  - pipeline/tests/test_zahlen.py
  - daten/pruefberichte/befunde.md
  - daten/pruefberichte/konsistenz.md
  - daten/aufbereitet/produkte.json
  - daten/aufbereitet/erlaeuterungen.csv
  - daten/aufbereitet/grundzahlen.csv
  - daten/aufbereitet/investitionen.csv
  - daten/aufbereitet/ve_faelligkeiten.csv
  - daten/zwischen/investitionen_pb.csv
  - daten/zwischen/querschnitte.csv
findings:
  critical: 0
  warning: 2
  info: 3
  total: 5
status: issues_found
---

# Phase 03: Code Review Report

**Reviewed:** 2026-10-02T00:00:00Z
**Depth:** standard
**Files Reviewed:** 32 (+ 9 generated data files sampled)
**Status:** issues_found

## Summary

Reviewed the Phase 3 pipeline (Produktinformationen/Erläuterungen/Grundzahlen, Investitionsmaßnahmen/VE-Fälligkeiten, Haushaltsquerschnitte, Konsistenzprüfung) and its full test suite, plus the year/sollwerte TOML configs and the generated CSV/JSON/markdown outputs they produce.

This is an unusually mature, heavily cross-checked codebase: every extraction module fails loudly on unexpected input (no silent defaults), the D-09 privacy rule (no staff names in `produkte.json`) is enforced both structurally (field is dropped before a dataclass is ever built) and by a dedicated test that greps the entire `daten/` tree for leaked name strings, and `befunde.md`/`konsistenz.md` are internally consistent and both green. I traced the full call chain for `spalten.ordne_spalten` (shared by `querschnitte.py`, `investitionen.py`, `produkte.py`) and found one latent robustness defect (WR-01). I did not find any security vulnerability, data-loss risk, or incorrect-output bug that would currently cause wrong figures to reach `daten/aufbereitet/` — all findings below are robustness/maintainability issues.

No `TODO`/`FIXME`/`console.log`/bare-`except`/hardcoded-secret patterns were found anywhere in the reviewed file set (verified via grep across all 16 Python source files).

## Warnings

### WR-01: `ordne_spalten` tolerance is computed globally, not per-anchor-pair — a single duplicate anchor breaks column assignment for the whole table

**File:** `pipeline/ostbevern/spalten.py:29-50`
**Issue:** `ordne_spalten` computes one global tolerance as `min(abstaende) / 2`, where `abstaende` is the list of gaps between *every* pair of adjacent sorted anchors. If any two anchors in `anker_x1` happen to coincide (gap 0 — e.g. a column that is empty/merged on a given PDF page, or a future jahrgang whose spalten configuration/extracted x1 values collide), `toleranz` becomes `0`, and the check `abstand >= toleranz` (line 40) then rejects **every** word for **every** column in that call — including a word whose `x1` exactly matches an unrelated, unambiguous anchor elsewhere in the row. For example, with `anker_x1 = [100.0, 100.0, 500.0]`, `toleranz = min(0, 400) / 2 = 0`, so a word at `x1=500.0` (an exact, unambiguous match to the third anchor) is also rejected with `SpaltenFehler`, even though it has nothing to do with the duplicate pair. This is shared code used by `querschnitte.py`, `investitionen.py`, and `produkte.py` (Grundzahlen), so the blast radius of a single degenerate anchor pair is large. Current `2026` data happens not to trigger this (full test suite is green), but it is a real latent defect in a widely-shared utility, not merely a theoretical one — the failure mode is an unconditional `SpaltenFehler` for an entire table/page rather than a precise error about the actual ambiguous word.
**Fix:**
```python
def ordne_spalten(woerter: Sequence[Wort], anker_x1: Sequence[float]) -> dict[int, Wort]:
    sortierte_indices = sorted(range(len(anker_x1)), key=lambda i: anker_x1[i])
    ergebnis: dict[int, Wort] = {}
    for wort in woerter:
        index = min(range(len(anker_x1)), key=lambda i: abs(wort.x1 - anker_x1[i]))
        abstand = abs(wort.x1 - anker_x1[index])
        # Local tolerance: only the gap to this word's two nearest neighbouring
        # anchors, not the smallest gap anywhere in the table.
        rang = sortierte_indices.index(index)
        nachbarn = [
            abs(anker_x1[index] - anker_x1[sortierte_indices[i]])
            for i in (rang - 1, rang + 1)
            if 0 <= i < len(sortierte_indices)
        ]
        toleranz = min(nachbarn) / 2 if nachbarn else float("inf")
        if abstand >= toleranz:
            raise SpaltenFehler(...)
        ...
```
At minimum, add a regression test with a duplicate/zero-gap anchor pair documenting the intended behaviour (reject only the genuinely ambiguous word(s), not the whole row).

### WR-02: `test_alle.py` mocks `extrahiere_produkte` with a 2-tuple, but the real function returns a 3-tuple

**File:** `pipeline/tests/test_alle.py:57-68` (compare `pipeline/ostbevern/produkte.py:942-1063`, which returns `(produkte_ergebnis, grundzahlen_ergebnis, erlaeuterungen_ergebnis)`)
**Issue:** `_produkte_ergebnisse()` in the `aufrufe` fixture returns only two `ExtraktionsErgebnis` objects (produkte.json, erlaeuterungen.csv), omitting the grundzahlen.csv result that `produkte.extrahiere_produkte` actually returns as its middle element. The test currently passes only because `alle.py`'s `main()` iterates the returned sequence generically (`for ergebnis in ergebnisse_produkte`) rather than unpacking it positionally, so the mock's arity never gets checked. If `alle.py` is ever changed to unpack `produkte_ergebnis, grundzahlen_ergebnis, erlaeuterungen_ergebnis = produkte.extrahiere_produkte(...)` (a natural refactor once grundzahlen.csv needs its own log line), this test suite would not catch an arity mismatch, and a real regression (e.g. silently dropping the grundzahlen step) could ship undetected through this integration test.
**Fix:** Make the test double match the real contract so it stays a meaningful regression guard:
```python
def _produkte_ergebnisse() -> tuple[ProdukteErgebnis, ProdukteErgebnis, ProdukteErgebnis]:
    return (
        ProdukteErgebnis(zeilen_geschrieben=63, pfad=PROJEKT_WURZEL / "daten/aufbereitet/produkte.json"),
        ProdukteErgebnis(zeilen_geschrieben=1234, pfad=PROJEKT_WURZEL / "daten/aufbereitet/grundzahlen.csv"),
        ProdukteErgebnis(zeilen_geschrieben=229, pfad=PROJEKT_WURZEL / "daten/aufbereitet/erlaeuterungen.csv"),
    )
```

## Info

### IN-01: `alle.py` reuses the "Schritt 06" label for two unrelated operations, inconsistent with `06_pruefen.py`'s own labeling of the same step

**File:** `pipeline/alle.py:107-125` (compare `pipeline/06_pruefen.py:46-51`, which prints the querschnitte-extraction line with no step prefix at all)
**Issue:** `alle.py` prints `"Schritt 06: Querschnitte: ... Werte geschrieben."` for the querschnitte extraction (which the module docstring explicitly calls a separate "Kontrollquelle"-step that runs *before* Schritt 06), and then separately prints `"Schritt 06: {titel}: ..."` once per rule for the actual consistency check. Both outputs share the "Schritt 06:" prefix even though they are two different operations, and `06_pruefen.py` (the other entry point for the same underlying calls) doesn't prefix the querschnitte line with any step number at all — the same logical step is labeled inconsistently depending on which CLI entry point ran it. This is purely a user-facing/log clarity issue, not a functional bug.
**Fix:** Give the querschnitte-extraction line in `alle.py` its own, unprefixed label (matching `06_pruefen.py`), e.g. `f"Querschnitte: {ergebnis_querschnitte.zeilen_geschrieben} Werte geschrieben."`.

### IN-02: CLI help text for `03_produktinfos.py` / `04_investitionen.py` doesn't mention all artifacts the command actually writes

**File:** `pipeline/03_produktinfos.py:22-25`, `pipeline/04_investitionen.py:22-25`
**Issue:** `03_produktinfos.py`'s Typer help string says "Extrahiert Produktinformationen und Erläuterungen aus den Produktseiten," but `extrahiere_produkte` also writes `grundzahlen.csv` (confirmed by its own return tuple and by `pipeline/ostbevern/schema.py`'s `GRUNDZAHLEN_CSV`). Similarly `04_investitionen.py`'s help string omits that the same call also writes `investitionen_pb.csv` (the PB control-source list). A user running `--help` gets an incomplete picture of what the command produces.
**Fix:** Extend both help strings, e.g. `"Extrahiert Produktinformationen, Grundzahlen und Erläuterungen aus den Produktseiten."` and `"Extrahiert Investitionsmaßnahmen, VE-Fälligkeiten und die PB-Investitionslisten aus den Produktseiten."`.

### IN-03: `schreibe_csv` relies on a blind `.cast(spalten)` that can silently coerce/truncate mismatched types instead of failing loud

**File:** `pipeline/ostbevern/schema.py:89-101`
**Issue:** `schreibe_csv` does `geordnet = sortiert.select(list(spalten.keys())).cast(spalten)` with no validation that the cast is lossless. Polars' `.cast()` silently truncates (e.g. a `Float64` column with a fractional value cast to `Int64`, or an out-of-range value) rather than raising, which runs counter to the project's explicit "fail loud, no silent defaults" convention (D-08, documented repeatedly throughout `pruefung.py`/`investitionen.py`/`konfiguration.py`). Nothing in the currently reviewed code path exercises this (all betrag values originate from `lies_betrag`, which is already `int`), so this is not an active bug today, but it is an inconsistency between the stated project philosophy and the one central write path every generated CSV goes through.
**Fix:** Either pass `strict=True` to `.cast()` (polars will raise on precision loss / overflow instead of silently coercing) or add an explicit round-trip equality check before writing:
```python
geordnet = sortiert.select(list(spalten.keys())).cast(spalten, strict=True)
```

---

_Reviewed: 2026-10-02T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
