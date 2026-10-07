---
phase: 02-kernzahlen
reviewed: 2026-10-01T16:48:56Z
depth: standard
files_reviewed: 15
files_reviewed_list:
  - daten/aufbereitet/ergebnisplan.csv
  - daten/aufbereitet/finanzplan.csv
  - daten/aufbereitet/hierarchie.csv
  - daten/pruefberichte/befunde.md
  - daten/pruefberichte/konsistenz.md
  - daten/zwischen/seiten.csv
  - pipeline/jahrgaenge/2026.toml
  - pipeline/jahrgaenge/2026_sollwerte.toml
  - pipeline/ostbevern/konfiguration.py
  - pipeline/ostbevern/plaene.py
  - pipeline/ostbevern/seiten.py
  - pipeline/tests/test_hierarchie.py
  - pipeline/tests/test_konfiguration.py
  - pipeline/tests/test_pruefung.py
  - pipeline/tests/test_seiten.py
findings:
  critical: 0
  warning: 2
  info: 1
  total: 3
status: issues_found
---

# Phase 02: Code Review Report

**Reviewed:** 2026-10-01
**Depth:** standard
**Files Reviewed:** 15
**Status:** issues_found

## Summary

This is an incremental re-review of the D-14 change (261001-oim): synthetic product groups
(`PG`) now carry at most one child product each, resolved either by the standard rule
(code = first four digits of the product code) or by an explicit declaration in
`[synthetische_produktgruppen]` (new in `pipeline/jahrgaenge/2026.toml`), with a matching
Haushaltsquerschnitt sollwert table `[haushaltsquerschnitt_pg]` added to
`pipeline/jahrgaenge/2026_sollwerte.toml`. This resolves the previously open "Beobachtung ohne
Prüfregel" in `befunde.md` about PG 1501/1502 (that paragraph has correctly been deleted), and
the regenerated `daten/aufbereitet/hierarchie.csv` / `ergebnisplan.csv` / `finanzplan.csv` /
`daten/zwischen/seiten.csv` now show PG 1501 as an exact copy of product 150101 and the new PG
1502 as an exact copy of product 150102, matching the new Haushaltsquerschnitt sollwerte
(-118138 / -72554, PDF S. 299) exactly — I spot-checked this by extracting the relevant rows
from the generated CSVs and comparing them byte-for-byte against the new sollwert table.

I traced `konfiguration.py`'s new validation for `[synthetische_produktgruppen]` and
`[haushaltsquerschnitt_pg]` (format, PB-prefix match, duplicate-product detection, pdf_seite
bounds) against all of `test_konfiguration.py`'s new negative tests, and `seiten.py`'s new
`produktgruppe_fuer_produkt` resolution plus the `baue_hierarchie` cross-validation (declared
product must exist, must not already belong to a printed PG, declared code must not already be
a printed PG, and two products may never collide on the same synthetic code) against all of
`test_seiten.py`'s new constructed-hierarchy tests. All 94 tests in the reviewed test files pass
(`uv run pytest tests/test_hierarchie.py tests/test_konfiguration.py tests/test_pruefung.py
tests/test_seiten.py`), and `ruff check .` is clean. I did not find a tautological check, a
mis-signed tolerance, or a case where a declared mapping could silently fail to apply (the
"product not found" / "already printed" guards in `baue_hierarchie` close the gap that a typo'd
`produkt` value in the declaration would otherwise leave open).

I found two Warnings and one Info item, none of which are incorrect numbers in the shipped data
— the pipeline is green and self-consistent — but they are genuine defects in code hygiene and
documentation accuracy that should be fixed.

## Warnings

### WR-01: `_synthetische_pg_datensaetze` keeps a `plantyp` parameter that is now dead code

**File:** `pipeline/ostbevern/plaene.py:481-518`
**Issue:** Before this change, `_synthetische_pg_datensaetze(teil_df, hierarchie, plantyp)` used
`plantyp` to look up `ZEILEN[plantyp]` for the row definition needed when building a summed row
from scratch. The D-14 rewrite replaced the summation with a verbatim copy of the single child
product's rows (`datensatz = dict(zeile)` at line 512), so `zeile_kanonisch`/`zeile_name`/
`ist_summe` etc. are now taken directly from the already-fully-populated child row — `plantyp`
is no longer read anywhere in the function body. The two call sites
(`pipeline/ostbevern/plaene.py:540-545`) still pass `"teilergebnisplan"` / `"teilfinanzplan"`
literals, which now do nothing and could mislead a future maintainer into thinking the function's
behavior depends on which plan is being processed (e.g. that it still looks up a per-plantyp row
definition). `ruff` does not flag this because the project's lint `select` list
(`pipeline/pyproject.toml`: `["E", "F", "I", "UP", "B"]`) does not include the unused-argument
rule family (`ARG`).
**Fix:** Drop the now-unused parameter and update both call sites:
```python
def _synthetische_pg_datensaetze(
    teil_df: pl.DataFrame, hierarchie: pl.DataFrame
) -> list[dict[str, object]]:
    ...

synthetisch_ergebnisplan = _synthetische_pg_datensaetze(teil_ergebnisplan, hierarchie)
synthetisch_finanzplan = _synthetische_pg_datensaetze(teil_finanzplan, hierarchie)
```

### WR-02: `befunde.md`'s Regel-1 sign description is still inverted relative to the code

**File:** `daten/pruefberichte/befunde.md:11`
**Issue:** Carried over from the prior review (previously WR-01, not touched by this phase's
diff but still live in a file that is in this review's scope). The machine-readable header
states "Regel 1: gedruckte Summe minus Formelkette", i.e.
`abweichung = gedruckte_Summe − Formelkette`. The actual implementation
(`pipeline/ostbevern/pruefung.py::_pruefe_regel1`, verified again in this pass) computes
`soll = zeile["betrag"]` (the gedruckte value) and `ist = Formelkette` (the component sum), so
`abweichung = ist − soll = Formelkette − gedruckte_Summe` — the opposite of the stated sentence.
The table row immediately below (PB 08 Z. 17 2024: gedruckt 186.499, Formelkette 186.501,
documented `abweichung = +2`) only matches `Formelkette − gedruckt`, confirming the sentence is
still wrong. This file is directly in this phase's review scope and was edited in this diff (the
PG 1501/1502 "Beobachtung" paragraph was correctly removed), so the stale sentence should have
been caught during that edit.
**Fix:**
```diff
-berechnet (Regel 1: gedruckte Summe minus Formelkette; Regel 2: Summe der Kinder minus
+berechnet (Regel 1: Formelkette minus gedruckte Summe; Regel 2: Summe der Kinder minus
```

## Info

### IN-01: Duplicate derivation of the D-14 PG-resolution rule in tests vs. production code

**File:** `pipeline/tests/test_hierarchie.py:37-44`, `pipeline/tests/test_seiten.py:94-104`
**Issue:** Both test files re-implement `produktgruppe_fuer_produkt`'s logic by hand
(`_resolved_pg_code` / the inline `deklarierte_produkte` dict comprehension) with a comment
explicitly stating this is deliberate ("unabhängig von der Produktionslogik"/"nicht über den
Helfer selbst") to avoid a tautological test. That rationale is sound and I agree with it, but
it does mean the *same* two-line resolution rule is now written out three times across
`seiten.py` (production), `test_hierarchie.py`, and `test_seiten.py` — if the D-14 resolution
rule ever grows a third case (e.g. a second declared product per PB), all three copies need
updating in lock-step and only two of them have test coverage protecting the production
implementation from drifting away from the copies. Not a bug today; flagging so a future change
to the resolution rule doesn't silently desync the two independent test derivations from each
other.
**Fix:** No action required now. If the resolution rule gains more cases, consider factoring the
test-side derivation into a single shared test helper (e.g. `pipeline/tests/conftest.py`) so the
two test files can't independently drift from each other, while still keeping it independent of
`ostbevern.seiten.produktgruppe_fuer_produkt`.

---

_Reviewed: 2026-10-01T16:48:56Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
