---
phase: 02-kernzahlen
reviewed: 2026-10-01T00:00:00Z
depth: standard
files_reviewed: 23
files_reviewed_list:
  - daten/pruefberichte/befunde.md
  - daten/pruefberichte/konsistenz.md
  - pipeline/01_seiten_klassifizieren.py
  - pipeline/02_plaene_extrahieren.py
  - pipeline/06_pruefen.py
  - pipeline/alle.py
  - pipeline/jahrgaenge/2026.toml
  - pipeline/jahrgaenge/2026_sollwerte.toml
  - pipeline/ostbevern/konfiguration.py
  - pipeline/ostbevern/pdf.py
  - pipeline/ostbevern/plaene.py
  - pipeline/ostbevern/pruefung.py
  - pipeline/ostbevern/schema.py
  - pipeline/ostbevern/seiten.py
  - pipeline/ostbevern/zahlen.py
  - pipeline/ostbevern/zeilen.py
  - pipeline/tests/test_alle.py
  - pipeline/tests/test_hierarchie.py
  - pipeline/tests/test_konfiguration.py
  - pipeline/tests/test_plaene.py
  - pipeline/tests/test_pruefung.py
  - pipeline/tests/test_seiten.py
  - pipeline/tests/test_zahlen.py
findings:
  critical: 0
  warning: 3
  info: 2
  total: 5
status: issues_found
---

# Phase 02: Code Review Report

**Reviewed:** 2026-10-01
**Depth:** standard
**Files Reviewed:** 23
**Status:** issues_found

## Summary

This phase implements the consistency-checking pipeline (Regel 1–4) that is the core-value
guarantor of the project: every budget figure shown in the app must be traceable to the PDF and
cross-checked against Anhang B / the Satzung. I read the full pipeline (`konfiguration.py`,
`pdf.py`, `seiten.py`, `plaene.py`, `pruefung.py`, `schema.py`, `zahlen.py`, `zeilen.py`), the
thin typer entry points, both generated/maintained report files, and all pipeline tests.

I specifically hunted for the failure modes called out in the brief: self-comparing checks,
mis-signed tolerances, swallowed exceptions, and `befunde.md` entries that could mask real
extraction bugs. I traced every `soll`/`ist` computation in `pruefung.py` by hand against the
actual numbers documented in `befunde.md`/`konsistenz.md` and confirmed the arithmetic
(`abweichung = ist − soll`) is applied correctly and consistently everywhere it matters — I did
not find a tautological check (a value compared against itself) and did not find a Befund whose
tolerance-matching logic could silently cover up a genuine extraction defect. `TOLERANZ_EURO = 1`
is applied with a strict `>` comparison everywhere, matching the ">1 €" rule from
`.claude/CLAUDE.md`, and `lies_befunde` actively rejects any documented Befund whose own
deviation falls inside that tolerance (so the file cannot be used to paper over sub-threshold
drift). No hardcoded secrets, `eval`, shell/SQL injection, or path-traversal issues were found;
`lade_jahrgang` explicitly rejects absolute or out-of-project `pdf_pfad` values.

I did find three Warning-level issues and two Info-level observations, detailed below. None of
them are things that are currently producing a wrong number in the checked-in data (the pipeline
is green and the data is self-consistent), but they are genuine defects in documentation
accuracy, defensive coding, and the independence of one specific check that should be fixed.

## Warnings

### WR-01: `befunde.md` header describes the Regel-1 deviation formula with the wrong sign

**File:** `daten/pruefberichte/befunde.md:11`
**Issue:** The machine-readable header states the general rule `abweichung = ist − soll` and then
spells out, per rule, what `ist`/`soll` are. For Regel 1 it says:

> „Regel 1: gedruckte Summe minus Formelkette"

i.e. it claims `abweichung = gedruckte_Summe − Formelkette`. But `pruefung.py::_pruefe_regel1`
actually computes `soll = zeile["betrag"]` (the **gedruckte** value) and `ist = Formelkette`
(the component sum), so the real formula is `abweichung = Formelkette − gedruckte_Summe` — the
opposite of what the sentence says. This is confirmed by the actual table row directly below it:
for PB 08 Zeile 17 2024, "gedruckt" is 186.499 and "Formelkette" (Zeilen 11, 13–16) is 186.501;
the documented `abweichung` is **+2**, which only matches `Formelkette − gedruckt`
(186.501 − 186.499 = +2), not the stated "gedruckte Summe minus Formelkette"
(186.499 − 186.501 = −2). The other three rule descriptions in the same sentence (Regel 2, 3, 4)
are correctly worded and match their code (verified against `_pruefe_regel2`,
`_pruefe_regel3`, `_pruefe_regel4_satzung`/`_b1`/`_b2`/`_b3`) — only the Regel-1 clause is
inverted.
**Fix:** Correct the sentence to read "Regel 1: Formelkette minus gedruckte Summe" so a future
maintainer transcribing a new Befund by hand computes the correct sign (otherwise they will
author an entry with the wrong sign, which `gleiche_befunde_ab`'s tolerance match will reject,
producing a confusing red build until someone re-derives the correct sign from first principles).
```diff
-berechnet (Regel 1: gedruckte Summe minus Formelkette; Regel 2: Summe der Kinder minus
+berechnet (Regel 1: Formelkette minus gedruckte Summe; Regel 2: Summe der Kinder minus
```

### WR-02: Anhang B.3 sollwerte for PB 09/15 Zeile 29 are derived via the same formula the pipeline itself uses, weakening that specific check's independence

**File:** `pipeline/jahrgaenge/2026_sollwerte.toml:75-99` (comment block and
`[teilergebnisplaene_pb]` entries `"09"`/`"15"`)
**Issue:** The project's stated core value is that every number is "durch automatische Prüfungen
… belegt" — Regel 4 B.3 is supposed to check the pipeline's extracted PB-level Zeile-29 value
against an independently-sourced reference number from Anhang B. For 13 of the 15 PB this is
true (Anhang B prints the value directly). For PB 09 and PB 15, however, Anhang B itself is
documented as containing a typo (it prints the first product group's value instead of the PB
total), so the comment explains that the sollwerte for these two PBs were **re-derived by hand
using the same formula chain that `Planwerte`/`FORMELN["teilergebnisplan"]` evaluates at
runtime** (`Z.18 = Z.10 − Z.17`, `Z.26 = Z.18` (Z.19-25 are 0), `Z.29 = Z.26 + Z.27 − Z.28`).
`test_regel4_b3_herleitet_fehlende_z29` then asserts that `Planwerte.wert(..., "29", ...)` equals
this manually-recomputed sollwert — i.e. it compares two independently-performed evaluations of
the *same* formula, not the pipeline's output against an independent PDF-printed ground truth.
Concretely: if `FORMELN["teilergebnisplan"]["29"]` or `["18"]`/`["26"]` in `zeilen.py` were
wrong, both the hand-derived sollwert *and* the pipeline's computed `ist` would be wrong in the
same way, and this specific check (2 of the 194 Regel-4 checks) would stay green. This risk is
substantially mitigated — the same `FORMELN` entries are exercised by hundreds of Regel-1 checks
against directly-printed Zeile 29 values on the other 13 PB pages — but it is still a real gap
for exactly these two data points, and it is the kind of "check that effectively compares a
derived value with itself" the project's accuracy guarantee is meant to rule out.
**Fix:** At minimum, add an explicit code comment at `_pruefe_regel4_b3` (or next to
`B3_ZEILEN`) cross-referencing this known limitation, so it isn't lost; better, if a later phase
can independently confirm these two PB totals from the Haushaltsquerschnitt pages (S. 296/299,
already referenced in the comment) via a *different* code path (e.g. Regel 7 mentioned in
`befunde.md`'s "Beobachtungen ohne Prüfregel"), do so to close the gap rather than relying on
re-derivation with the same formula.

### WR-03: `_pruefe_regel4_b1` can raise an unhandled `IndexError` instead of a clear `PruefungsFehler` if `spalten` and `jahre` ever go out of sync

**File:** `pipeline/ostbevern/pruefung.py:556-578`
**Issue:**
```python
for zeile, sollwerte_je_jahr in sorted(gesamtergebnisplan["zeilen"].items()):
    if len(sollwerte_je_jahr) != len(jahre):
        raise PruefungsFehler(...)
    for index, jahreszahl in enumerate(jahre):
        wertart, spalten_jahr = spalten_zu_wertart[index]   # <- indexes by len(jahre)
```
The code validates that each sollwert row has as many values as `jahre` (from the sollwerte TOML)
but never validates that `len(jahre) == len(spalten_zu_wertart)` (derived from the **jahrgang**
TOML's `spalten.ergebnisplan`). Today both are 6 for 2026, so this never triggers, but if a
future jahrgang file ever defines `gesamtergebnisplan.jahre` with more entries than
`spalten.ergebnisplan` has columns, `spalten_zu_wertart[index]` raises a bare `IndexError`
instead of the clear, actionable `PruefungsFehler` the rest of this module consistently produces
(e.g. the very next check three lines down, `spalten_jahr != jahreszahl`, correctly raises
`PruefungsFehler` for a *related* mismatch). This is purely a diagnostics/robustness gap — no
current data triggers it — but it breaks the project's "bricht sofort mit PDF-Seite und Zeile ab"
discipline for this one code path.
**Fix:**
```python
jahre = gesamtergebnisplan["jahre"]
pdf_seite = gesamtergebnisplan.get("pdf_seite")
spalten_zu_wertart = [zerlege_spaltenkopf(kopf) for kopf in spalten]
if len(spalten_zu_wertart) != len(jahre):
    raise PruefungsFehler(
        f"Regel 4: {len(spalten)} Spalten in jahrgang.spalten.ergebnisplan, "
        f"{len(jahre)} Jahre in gesamtergebnisplan.jahre"
    )
```

## Info

### IN-01: `REGEL3_ZEILEN` comment only explains a subset of the excluded lines

**File:** `pipeline/ostbevern/pruefung.py:45-49`
**Issue:** The comment says Regel 3 excludes "TP 27/28 … und der Minderaufwand (GEP 27, TP 30)"
plus Zeile 18. The actual excluded set (everything between 01–20 except 18, plus everything
21–33) is larger — Zeilen 21–26 and 29/31–33 are also silently excluded by only listing 01-17/19/20
in `REGEL3_ZEILEN`, but the comment doesn't mention them. The behaviour is correct and fully
covered by `test_regel3_gruen_auf_eingecheckten_daten`'s exact `geprueft == 114` assertion; this
is a documentation completeness nit, not a functional issue.
**Fix:** Expand the comment to state explicitly which lines are checked (`REGEL3_ZEILEN` itself
is the authoritative list) rather than only naming the two most notable exclusions, to save the
next reader from having to reverse-engineer the full exclusion set.

### IN-02: `lies_befunde`'s hand-rolled Markdown table parser has no defence against a `|` inside `begruendung`

**File:** `pipeline/ostbevern/pruefung.py:258-268`
**Issue:** `zellen = [zelle.strip() for zelle in text.strip("|").split("|")]` splits purely on the
pipe character. None of the current `begruendung` texts in `befunde.md` contain a literal `|`,
but if a future entry's free-text justification ever needs one (e.g. to show a formula like
`a|b`), the row would silently split into more than 10 cells and fail with the generic "hat N
Zellen, erwartet 10" error — a confusing message for what is actually a formatting footgun in
the authoring file, not a data problem. This fails loudly (not silently), so it's low risk, but
worth a one-line guard or comment.
**Fix:** Either document the `|`-free constraint on `begruendung` next to the module docstring,
or make the parser robust by capping the split (`text.strip("|").split("|", 9)`) so any `|`
inside the final `begruendung` cell doesn't corrupt the parse.

---

_Reviewed: 2026-10-01_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
