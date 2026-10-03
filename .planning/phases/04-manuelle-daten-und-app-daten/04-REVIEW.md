---
phase: 04-manuelle-daten-und-app-daten
reviewed: 2026-10-03T20:06:13Z
depth: standard
files_reviewed: 41
files_reviewed_list:
  - .github/workflows/ci.yml
  - app/.prettierignore
  - app/src/charts/format.ts
  - app/src/data/daten.ts
  - app/src/data/haushalt.json
  - app/src/data/investitionen.json
  - app/src/data/produkte.json
  - app/src/data/stellenplan.json
  - app/src/data/texte.json
  - app/src/data/typen.ts
  - daten/aufbereitet/stellenplan.csv
  - daten/manuell/README.md
  - daten/manuell/eigenkapital.csv
  - daten/manuell/kita_zuschuesse.csv
  - daten/manuell/meta.json
  - daten/manuell/steuerarten.csv
  - daten/manuell/texte/erklaerungen.md
  - daten/manuell/transferaufwendungen.csv
  - daten/manuell/ve_uebersicht.csv
  - daten/manuell/verbindlichkeiten.csv
  - daten/manuell/weitere_vorberichtstabellen.csv
  - daten/manuell/zuwendungen.csv
  - daten/pruefberichte/befunde.md
  - daten/pruefberichte/konsistenz.md
  - pipeline/05_stellenplan.py
  - pipeline/07_app_daten.py
  - pipeline/alle.py
  - pipeline/jahrgaenge/2026.toml
  - pipeline/jahrgaenge/2026_sollwerte.toml
  - pipeline/ostbevern/app_daten.py
  - pipeline/ostbevern/konfiguration.py
  - pipeline/ostbevern/manuell.py
  - pipeline/ostbevern/pruefung.py
  - pipeline/ostbevern/schema.py
  - pipeline/ostbevern/stellenplan.py
  - pipeline/ostbevern/texte.py
  - pipeline/tests/test_alle.py
  - pipeline/tests/test_app_daten.py
  - pipeline/tests/test_konfiguration.py
  - pipeline/tests/test_manuell.py
  - pipeline/tests/test_pruefung.py
  - pipeline/tests/test_stellenplan.py
  - pipeline/tests/test_texte.py
findings:
  critical: 1
  warning: 3
  info: 1
  total: 5
status: issues_found
---

# Phase 04: Code Review Report

**Reviewed:** 2026-10-03T20:06:13Z
**Depth:** standard
**Files Reviewed:** 41
**Status:** issues_found

## Summary

Phase 4 (manuelle Vorberichtstabellen, `meta.json`, Stellenplan-Extraktion, Regel 5/9/10
und die App-JSON-Erzeugung in `app_daten.py`/`texte.py`) is an unusually well-tested
slice of the pipeline: every new CSV/JSON shape has a round-trip ("read → rewrite →
byte-identical") test, the KL-Herauslösung (D-01 bis D-04) and Schuldenstand-Fortschreibung
(D-14) each have dedicated mutation tests, and `test_keine_personennamen_in_app_daten`
actively greps the generated JSON for personnel names extracted elsewhere in the pipeline.
No hardcoded secrets, `eval`, shell/SQL injection, or empty `except`/`catch` blocks were
found, and no person names leak into the generated `app/src/data/*.json` or
`daten/aufbereitet/stellenplan.csv` (job titles only, e.g. `amtsbezeichnung`).

The one critical defect found is a genuine, reproducible number-formatting bug: all ten
uses of `{{jahr.haushaltsjahr|zahl}}` in `erklaerungen.md` will render the haushaltsjahr
with German thousands-grouping ("2.026" instead of "2026") once the app renders
`texte.json` through `format.ts::formatiere`, because the `zahl` format kuerzel is (by
design, and correctly for `meta.einwohner`) always grouped, and `FORMATKUERZEL` has no
ungrouped/"year" variant. This directly contradicts the project's core value ("Jede Zahl
in der App ist korrekt... Bürgerinformation muss stimmen") and is not caught by any test
in this phase, because the test suite only validates the placeholder *contract*
(key exists, format kuerzel is in the vocabulary), never the rendered output.

Three further warnings concern verification/robustness gaps that are consistent with, but
slightly undercut, this project's "every number is backed by an automatic check" guarantee
(the VE-Übersicht per-year summary rows are never cross-checked) and defensive coding gaps
that would surface as unclear `IndexError`/`KeyError` instead of domain errors if a future
jahrgang's data shape deviates slightly from 2026's.

## Critical Issues

### CR-01: `zahl` format kuerzel mis-renders the Haushaltsjahr with thousands-grouping

**File:** `app/src/charts/format.ts:39-42`, `pipeline/ostbevern/texte.py:28-30`, `daten/manuell/texte/erklaerungen.md` (10 occurrences, e.g. lines 7, 13, 19, 25, 31, 37, 43, 49, 55, 61)

**Issue:** `zahl()` in `format.ts` is `Intl.NumberFormat('de-DE', { maximumFractionDigits: 0 })`,
which uses grouping by default — correct for `meta.einwohner` ("11.741"), but wrong for a
bare 4-digit year. All ten uses of `{{jahr.haushaltsjahr|zahl}}` in
`daten/manuell/texte/erklaerungen.md` (and therefore in the committed
`app/src/data/texte.json`) will render the Haushaltsjahr as **"2.026"** instead of
**"2026"** once a future phase wires `formatiere()` into the Vue templates — e.g. "Für
2.026 rechnet die Gemeinde nur noch mit 3,11 Mio. €" instead of "Für 2026…". Verified
directly:

```
$ node -e "console.log(new Intl.NumberFormat('de-DE',{maximumFractionDigits:0}).format(2026))"
2.026
```

`FORMATKUERZEL` (`euro`, `mio`, `zahl`, `prozent`, `promille`, `vzae`) has no ungrouped
integer/year variant, so there is currently no correct way to express "render this raw
int as a bare year" through the existing placeholder vocabulary — the content author had
to misuse `zahl`. Neither `ostbevern.texte.pruefe_text` (which only checks the
*syntactic* placeholder contract) nor any test in `test_texte.py`/`test_app_daten.py`
renders the resolved value through `formatiere()`, so this ships silently.

**Fix:** Add a dedicated ungrouped kuerzel (e.g. `jahr`) to both
`app/src/charts/format.ts::FormatKuerzel`/`formatiere()` and
`pipeline/ostbevern/texte.py::FORMATKUERZEL`, and switch all ten
`{{jahr.haushaltsjahr|zahl}}` placeholders in `erklaerungen.md` to the new kuerzel:

```ts
// format.ts
export type FormatKuerzel = 'euro' | 'mio' | 'zahl' | 'jahr' | 'prozent' | 'promille' | 'vzae'
const JAHR_FORMAT = new Intl.NumberFormat(LOCALE, { useGrouping: false })
...
case 'jahr':
  return JAHR_FORMAT.format(wert)
```
```python
# texte.py
FORMATKUERZEL: tuple[str, ...] = ("euro", "mio", "zahl", "jahr", "prozent", "promille", "vzae")
```
At minimum, add a test that renders every resolved `(wert, format)` pair from
`loese_auf()` through a reimplementation/port of `formatiere()` (or snapshot-tests the
expected rendered string) so a future regression is caught mechanically, not by eyeballing
the PDF.

## Warnings

### WR-01: `ve_uebersicht.csv` per-year summary rows are never cross-checked

**File:** `pipeline/ostbevern/pruefung.py:1555-1656` (`_pruefe_regel5_ve_uebersicht`), `daten/manuell/ve_uebersicht.csv`

**Issue:** `ve_uebersicht.csv` carries three `ist_gesamt=true` rows: the VE-Gesamtbetrag
(`faellig_jahr` null, 11.600 T€) and two per-year summary rows, "Summe (fällig 2027)"
(9.400 T€) and "Summe (fällig 2028)" (2.200 T€). `_pruefe_regel5_ve_uebersicht` only
selects `ist_gesamt & faellig_jahr.is_null()` for the Regel-5 `summe_gfp_ve` check and
filters `~ist_gesamt` for the per-(produkt, jahr) comparison against
`ve_faelligkeiten.csv` — the two per-year summary rows are excluded from *both* checks and
are never compared against anything (not even against the sum of the non-summary rows of
the same `faellig_jahr`). On the currently checked-in data they happen to be arithmetically
correct (2.000+2.000+1.700+1.000+1.700=9.400 for 2027; 1.200+1.000=2.200 for 2028), but a
future transcription typo in either cell would pass Regel 5, `pruefe_alles`, and every test
in `test_manuell.py`/`test_pruefung.py` silently — contradicting the project's stated
"jede Zahl … ist durch automatische Prüfungen … belegt" guarantee.

**Fix:** Add a check (either inside `_pruefe_regel5_ve_uebersicht` or as a dedicated
`Pruefpunkt`) that each `ist_gesamt` row with a non-null `faellig_jahr` equals the sum of
the `~ist_gesamt` rows for that same `faellig_jahr`:

```python
for jahr, betrag in (
    (z["faellig_jahr"], z["betrag_teur"])
    for z in ve_uebersicht.filter(
        pl.col("ist_gesamt") & pl.col("faellig_jahr").is_not_null()
    ).iter_rows(named=True)
):
    soll = einzel.filter(pl.col("faellig_jahr") == jahr)["betrag_teur"].sum()
    # ... Pruefpunkt soll vs. betrag*1000 ...
```

### WR-02: Fragile negative-index fallback in Schuldenstand-Fortschreibung

**File:** `pipeline/ostbevern/app_daten.py:570-586` (`baue_investitionen_json`)

**Issue:**

```python
for index, jahr in enumerate(jahre):
    if jahr in investitionskredite_gedruckt:
        ...
    else:
        vorjahr_euro = investitionskredite[index - 1]
```

If `jahre[0]` were ever *not* present in `investitionskredite_gedruckt` (e.g. a future
jahrgang where `verbindlichkeiten.csv` starts one year later than the Ergebnisplan
column range), `index == 0` would evaluate `investitionskredite[-1]` on a still-empty
list, raising a raw `IndexError` instead of a clear `AppDatenFehler`. This holds only by
coincidence of the current 2026 configuration (jahre[0]=2024 is always printed), and is
not guarded by any validation or `KonfigurationsFehler`/`AppDatenFehler`.

**Fix:** Validate the precondition explicitly before the loop:

```python
if jahre[0] not in investitionskredite_gedruckt:
    raise AppDatenFehler(
        "investitionen.json: erstes Jahr hat keinen gedruckten Schuldenstand "
        f"({jahre[0]!r})"
    )
```

### WR-03: `ABGELEITET`-Formeln in `texte.py` nehmen Nachbarjahre ungeprüft an

**File:** `pipeline/ostbevern/texte.py:218-227` (`_ausgleichsruecklage_minderung_haushaltsjahr`), `:204-210`, `:213-215`

**Issue:** `_ausgleichsruecklage_minderung_haushaltsjahr` reads
`w[f"eigenkapital.ausgleichsruecklage.{hh + 1}"]`, and
`_schluesselzuweisung_rueckgang_haushaltsjahr` reads `...{vj}` where `vj = hh - 1` — both
assume the neighbouring year is present in the computed `werte` dict (i.e. is one of the
configured Ergebnisplan columns). For the 2026 jahrgang this holds (`jahre` spans
2024–2029, haushaltsjahr=2026), but nothing enforces it structurally: a future jahrgang
whose `haushaltsjahr` is the *last* configured year would make `hh + 1` raise a raw
`KeyError` deep inside `textwerte()`'s `ABGELEITET` loop, rather than the domain-specific
`TexteFehler` every other failure mode in this module produces.

**Fix:** Either validate in `textwerte()`/`erzeuge_app_daten()` that `haushaltsjahr - 1`
and `haushaltsjahr + 1` are both in `jahre` before evaluating `ABGELEITET`, or wrap the
per-formula evaluation to re-raise `KeyError` as `TexteFehler` with the formula name, e.g.:

```python
for name, formel in ABGELEITET.items():
    try:
        werte[f"abgeleitet.{name}"] = formel(werte)
    except KeyError as fehler:
        raise TexteFehler(f"abgeleitet.{name}: fehlender Schlüssel {fehler}") from fehler
```

## Info

### IN-01: `formatiere()` has no runtime fallback for an unknown kuerzel

**File:** `app/src/charts/format.ts:68-83`

**Issue:** The `switch` in `formatiere()` has no `default` branch. TypeScript accepts this
because `FormatKuerzel` is an exhaustive literal union, but if a value ever reaches this
function at runtime that isn't one of the six literals (e.g. a stale `texte.json` built by
an older pipeline version, or a manual edit), the function silently falls through and
returns `undefined`, which would render as the literal string `"undefined"` in the UI
rather than failing loudly.

**Fix:** Add an exhaustive-check fallback for defense in depth:

```ts
default: {
  const _unreachable: never = kuerzel
  throw new Error(`Unbekanntes Formatkürzel: ${_unreachable}`)
}
```

---

_Reviewed: 2026-10-03T20:06:13Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
