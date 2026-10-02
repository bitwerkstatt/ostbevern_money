# Phase 4: Manuelle Daten und App-Daten - Pattern Map

**Mapped:** 2026-10-02
**Files analyzed:** 21 (new/modified)
**Analogs found:** 21 / 21

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `pipeline/05_stellenplan.py` | route (typer entrypoint) | file-I/O | `pipeline/alle.py` command block for `investitionen`/`querschnitte` (lines 96-108) | exact |
| `pipeline/07_app_daten.py` | route (typer entrypoint) | transform | `pipeline/alle.py` command block for `pruefung.pruefe_alles` (lines 113-124) | exact |
| `pipeline/ostbevern/manuell.py` | service | CRUD (read CSV, cross-check) | `pipeline/ostbevern/pruefung.py` (`_pruefe_regel4_satzung`, lines 685-725) | exact |
| `pipeline/ostbevern/stellenplan.py` | service (PDF parser) | transform | `pipeline/ostbevern/investitionen.py` (sparse-row handling, `_TOLERANZ_EURO`, Gegenprobe) | role-match (new sparse-row variant) |
| `pipeline/ostbevern/app_daten.py` | service | transform | `pipeline/ostbevern/produkte.py` (`schreibe_produkte_json`) + `pipeline/ostbevern/pruefung.py` (`Planwerte.wert`) | exact |
| `pipeline/ostbevern/texte.py` | utility (parser) | transform | `pipeline/ostbevern/freitext.py` (fail-fast text parsing) | role-match |
| `pipeline/ostbevern/schema.py` (extended) | config/schema | CRUD | existing module itself, pattern `*_SPALTEN` + `schreibe_*_csv`/`lies_*_csv` (lines 203-234) | exact |
| `pipeline/ostbevern/pruefung.py` (Regel 5 added) | service | CRUD (validation) | `_pruefe_regel4_satzung`, `_pruefe_regel4_b3` (lines 685-793) | exact |
| `pipeline/ostbevern/konfiguration.py` (B.4-B.6 sollwerte) | config | CRUD | `lade_sollwerte` (line 470) existing TOML tables | exact |
| `pipeline/alle.py` (steps 05, 07 wired in) | route | event-driven (pipeline chain) | existing step blocks (02-06) in same file | exact |
| `pipeline/tests/test_manuell.py` | test | CRUD | `pipeline/tests/test_pruefung.py` + `pipeline/tests/test_investitionen.py` | exact |
| `pipeline/tests/test_stellenplan.py` | test | transform | `pipeline/tests/test_investitionen.py` | exact |
| `pipeline/tests/test_texte.py` | test | transform | `pipeline/tests/test_freitext.py` | role-match |
| `pipeline/tests/test_app_daten.py` | test | CRUD | `pipeline/tests/test_produkte.py` (`test_keine_personennamen`, lines 196-226) | exact |
| `daten/manuell/*.csv` (steuerarten, zuwendungen, transferaufwendungen, kita_zuschuesse, weitere_vorberichtstabellen, verbindlichkeiten, eigenkapital, ve_uebersicht) | config (data file) | file-I/O | `daten/aufbereitet/grundzahlen.csv` schema shape (Langformat) | role-match |
| `daten/manuell/meta.json` | config (data file) | file-I/O | `daten/aufbereitet/produkte.json` (value+quelle shape) | role-match |
| `daten/manuell/README.md` | config (doc) | file-I/O | none in repo (new doc pattern) | no analog |
| `daten/aufbereitet/stellenplan.csv` | model (data) | CRUD | `daten/aufbereitet/investitionen.csv` schema | exact |
| `texte/erklaerungen.md` | config (data file) | transform | none in repo (new placeholder-text file) | no analog |
| `app/src/data/{haushalt,investitionen,stellenplan,texte}.json` | model (static data artifact) | file-I/O | `app/src/data/jahrgang.json` / `aufbereitet/produkte.json` writer pattern | role-match |
| `app/src/data/typen.ts` | model (TS types) | transform | none in repo yet (new; `app/src/charts/format.ts` as sibling convention) | no analog |
| `.github/workflows/ci.yml` (diff step added) | config (CI) | batch | existing `pipeline` job steps | exact |

## Pattern Assignments

### `pipeline/05_stellenplan.py` and `pipeline/07_app_daten.py` (route, typer entrypoint)

**Analog:** `pipeline/alle.py` (whole file is itself the orchestrator; module-level docstring convention is the analog for any new thin entrypoint)

**Imports pattern** (`pipeline/alle.py` lines 1-30):
```python
from __future__ import annotations

from typing import Annotated

import typer

from ostbevern import investitionen, plaene, produkte, pruefung, querschnitte, seiten
from ostbevern.investitionen import InvestitionenFehler
from ostbevern.konfiguration import (
    PROJEKT_WURZEL,
    STANDARD_JAHR,
    KonfigurationsFehler,
    lade_jahrgang,
    lade_sollwerte,
)
from ostbevern.pdf import PdfFehler
...
app = typer.Typer(add_completion=False, help="...")
```

**Core CLI pattern** (`pipeline/alle.py` lines 38-47, 96-108):
```python
@app.command()
def main(
    jahr: Annotated[
        int,
        typer.Option("--jahr", help="Haushaltsjahr; lädt pipeline/jahrgaenge/{jahr}.toml"),
    ] = STANDARD_JAHR,
) -> None:
    try:
        jahrgang = lade_jahrgang(jahr)
        lade_sollwerte(jahr)
    except KonfigurationsFehler as fehler:
        typer.echo(f"Fehler: {fehler}", err=True)
        raise typer.Exit(code=1) from fehler
    ...
    try:
        ergebnis_querschnitte = querschnitte.extrahiere_querschnitte(jahrgang)
    except (PdfFehler, QuerschnitteFehler, SchemaFehler, KonfigurationsFehler) as fehler:
        typer.echo(f"Fehler: {fehler}", err=True)
        raise typer.Exit(code=1) from fehler
    typer.echo(f"Querschnitte: {ergebnis_querschnitte.zeilen_geschrieben} Werte geschrieben.")
```

**Error handling pattern**: every pipeline step is wrapped in `try/except (<ModulFehler>, SchemaFehler, KonfigurationsFehler)` → `typer.echo(f"Fehler: {fehler}", err=True); raise typer.Exit(code=1) from fehler`. `05_stellenplan.py` and `07_app_daten.py` must each expose their own `@app.command() def main(jahr: ... = STANDARD_JAHR)` (standalone typer apps, same as `03_produkte`-style modules are invoked from within `alle.py`), and `alle.py` itself gets two new blocks mirroring the `querschnitte`/`pruefung` blocks, inserted after step 04 (Investitionen) and after step 06 (Prüfung) respectively, per D-24 ordering (01→02→03→04→Querschnitte→05→06→07).

---

### `pipeline/ostbevern/manuell.py` (service, CRUD + validation)

**Analog:** `pipeline/ostbevern/pruefung.py`, function `_pruefe_regel4_satzung` (lines 685-725) and `_pruefe_regel4_b3` (lines 728-793)

**Core pattern** — iterate posten, build a `Pruefpunkt`, collect deviations beyond tolerance:
```python
# pipeline/ostbevern/pruefung.py:706-724
ist = sum(
    vorzeichen * planwerte.wert("GESAMT", "", zeile, haushaltsjahr, wertart)
    for vorzeichen, zeile in komponenten
)
geprueft += 1
punkt = Pruefpunkt(
    regel=4,
    plan="satzung",
    ebene="GESAMT",
    code="",
    zeile=schluessel,
    jahr=haushaltsjahr,
    wertart=wertart,
    soll=soll,
    ist=ist,
    pdf_seite=pdf_seite,
)
if abs(punkt.abweichung) > TOLERANZ_EURO:
    abweichungen.append(punkt)
```

**Apply to Regel 5 (D-07):** Reuse `Pruefpunkt`/`Befund`/`Abgleich` dataclasses unmodified. For non-PB/PG/P contexts use `ebene="GESAMT", code=""` and put the fachlicher Kontext in `plan` (e.g. `plan="vorbericht_transferaufwendungen"`), and the Posten-Schlüssel in `zeile` (e.g. `zeile="kreisumlage_netto"`) — this is the documented workaround for the strict `EBENEN`/`WERTARTEN` enum validation in `lies_befunde` (Research Pattern 3). Define two **new, local** tolerance constants in `pruefung.py` (do not touch `TOLERANZ_EURO=1`, following the `investitionen._TOLERANZ_EURO` precedent at `investitionen.py:52`):
```python
REGEL5_TOLERANZ_POSTEN_T_EURO = 1      # Stufe (a)
REGEL5_TOLERANZ_GEP_EURO = 1000        # Stufe (b)
```

**Error handling pattern:** `PruefungsFehler` (ValueError subclass, `pruefung.py:118`) raised for structural problems (unknown Satzungsformel-Schlüssel, missing hierarchy code); deviations beyond tolerance become `Pruefpunkt` entries collected into the `Bericht`, not exceptions — this distinction must carry over to Regel 5.

---

### `pipeline/ostbevern/stellenplan.py` (service, PDF→CSV parser, sparse rows)

**Analog:** `pipeline/ostbevern/investitionen.py` (column-zuordnung, Gegenprobe, tolerance) + `pipeline/ostbevern/spalten.py` (`ordne_spalten`)

**Imports pattern** (typical for all PDF parsers, see `investitionen.py` top):
```python
from __future__ import annotations
import polars as pl
from ostbevern.konfiguration import Jahrgang
from ostbevern.pdf import PdfDokument, Wort
from ostbevern.spalten import ordne_spalten, SpaltenFehler
from ostbevern.zahlen import lies_kennzahl
from ostbevern.schema import schreibe_csv  # new STELLENPLAN_SPALTEN
```

**Core sparse-row pattern** (deviates from `investitionen.py`'s completeness check — Research Pitfall 1):
```python
# pipeline/ostbevern/spalten.py:19-30 (ordne_spalten itself never requires full coverage)
zugeordnet = ordne_spalten(woerter, anker_x1)  # may be incomplete — do NOT add
# `if len(zugeordnet) != anzahl_spalten: raise ...` here (that's the investitionen.py/
# querschnitte.py caller convention for DENSE tables; S. 287-289 PB-Übersichten are
# sparse — missing index means "no entry for this combination", not an error).
```

**Hundertstel-exact decimal parsing** (D-18) — build on `zahlen.lies_kennzahl` but avoid float multiplication:
```python
# Eigene Herleitung, siehe pipeline/ostbevern/zahlen.py _KENNZAHL_MUSTER
def lies_stellen_hundertstel(text: str) -> int | None:
    wert = lies_kennzahl(text)
    if wert is None:
        return None
    _, nachkommastellen = wert
    if nachkommastellen != 2:
        raise ZahlenFehler(f"Stellenwert ohne exakt 2 Nachkommastellen: {text!r}")
    ganzzahl_teil, dezimal_teil = text.strip().replace("−", "-").split(",")
    vorzeichen = -1 if ganzzahl_teil.startswith("-") else 1
    ziffern = ganzzahl_teil.lstrip("-").replace(".", "") + dezimal_teil
    return vorzeichen * int(ziffern)
```

**Gegenprobe/tolerance pattern** (`investitionen.py:49-52,250`):
```python
_TOLERANZ_EURO = 1  # local, independent from pruefung.TOLERANZ_EURO
...
return all(abs((x or 0) - (y or 0)) <= _TOLERANZ_EURO for x, y in zip(a, b, strict=True))
```
Apply the same local-tolerance pattern for the printed "insgesamt"/"Summe" row cross-check (D-20): compare parsed sum vs. printed total, raise `StellenplanFehler` (new, same shape as `InvestitionenFehler`) with PDF-Seite on mismatch, same wording style as `investitionen.py` raises (`raise InvestitionenFehler(f"S. {pdf_seite}: ...")`).

**Error handling pattern:** define `class StellenplanFehler(ValueError)` at module top (mirrors `InvestitionenFehler`), raise with `f"S. {pdf_seite}: <Kontext>: <Grund>"` message shape throughout, matching ~20 raise sites in `investitionen.py`.

---

### `pipeline/ostbevern/app_daten.py` (service, transform + JSON writer)

**Analog:** `pipeline/ostbevern/schema.py`, function `schreibe_produkte_json` (lines 321-350) for the writer; `pipeline/ostbevern/pruefung.py` class `Planwerte` (lines 234-287) for reading plan values by node/zeile/jahr/wertart.

**Atomic JSON write pattern** (schema.py:339-350):
```python
inhalt = json.dumps(geordnet, ensure_ascii=False, indent=2) + "\n"
pfad.parent.mkdir(parents=True, exist_ok=True)
deskriptor, temp_pfad_str = tempfile.mkstemp(dir=pfad.parent, prefix=".produkte-", suffix=".tmp")
temp_pfad = Path(temp_pfad_str)
try:
    with os.fdopen(deskriptor, "w", encoding="utf-8", newline="\n") as datei:
        datei.write(inhalt)
    os.replace(temp_pfad, pfad)
finally:
    temp_pfad.unlink(missing_ok=True)
```
Apply identically for every writer in `app_daten.py` (`haushalt.json`, `investitionen.json`, `stellenplan.json`, `texte.json`), just change `prefix` per file (e.g. `.haushalt-`) and the allowlist-schema check preceding it (mirror the `fehlend`/`unerwartet` key-set check at `schema.py:325-334`).

**Plan-value lookup pattern** (`pruefung.py` `Planwerte.wert`, line 258) — use for Zuschussbedarf (D-23) and KL-split (D-02/D-03):
```python
def wert(self, ebene: str, code: str, zeile: str, jahr: int, wertart: str) -> int: ...
```
Zuschussbedarf: `aufwand = wert(...,"17",...) + wert(...,"20",...)`; `ertraege = wert(...,"10",...) + wert(...,"19",...)`; `zuschussbedarf = aufwand - ertraege`, tagged with `"berechnet": True` key per D-23, same style as `gerundet`/`berechnet` flags described in D-02/D-10/D-13.

**Anti-pattern to flag in review:** never mutate `daten/aufbereitet/hierarchie.csv` for the KL split — it must be a pure in-memory transform inside `app_daten.py` only (explicit Anti-Pattern in RESEARCH.md).

---

### `pipeline/ostbevern/texte.py` (utility, placeholder parser)

**Analog:** `pipeline/ostbevern/freitext.py` (fail-fast text-processing style, small single-purpose module)

**Core pattern** (own design, following D-08-style fail-fast, given in RESEARCH.md Code Examples):
```python
import re

_PLATZHALTER_MUSTER = re.compile(r"\{\{([a-z0-9_.]+)\|([a-z]+)\}\}")

def loese_platzhalter_auf(text: str, werte: dict[str, int | float]) -> tuple[str, dict]:
    verwendete: dict[str, tuple[int | float, str]] = {}

    def _ersetze(treffer: re.Match[str]) -> str:
        schluessel, format_kuerzel = treffer.group(1), treffer.group(2)
        if schluessel not in werte:
            raise TexteFehler(f"Unbekannter Datenschlüssel: {schluessel!r}")
        verwendete[schluessel] = (werte[schluessel], format_kuerzel)
        return treffer.group(0)

    _PLATZHALTER_MUSTER.sub(_ersetze, text)
    return text, verwendete
```

**Error handling pattern:** define `class TexteFehler(ValueError)` (same shape as `InvestitionenFehler`/`StellenplanFehler`); raise on unknown placeholder key (fail hard, no silent default — per D-15 and the project-wide fail-fast convention).

**Nackte-Ziffern test** belongs in `pipeline/tests/test_texte.py`, analog to validation-style tests in `test_freitext.py`.

---

### `pipeline/ostbevern/schema.py` (extended: new `*_SPALTEN` dicts + `schreibe_*_csv`/`lies_*_csv`)

**Analog:** existing `INVESTITIONEN_SPALTEN` + `schreibe_investitionen_csv`/`lies_investitionen_csv` (schema.py:206-234)

**Pattern to copy verbatim** for each new manual CSV and `stellenplan.csv`:
```python
# schema.py:206-234
<NAME>_SPALTEN: dict[str, pl.PolarsDataType] = {
    "...": pl.Utf8,
    ...
    "pdf_seite": pl.Int64,
}

def schreibe_<name>_csv(df: pl.DataFrame, pfad: Path) -> None:
    """Schreibt <name>.csv sortiert nach ... (D-21)."""
    schreibe_csv(df, pfad, <NAME>_SPALTEN, [<sortierspalten>])

def lies_<name>_csv(pfad: Path) -> pl.DataFrame:
    """Liest <name>.csv über `lies_csv` mit <NAME>_SPALTEN."""
    return lies_csv(pfad, <NAME>_SPALTEN)
```
Note the general `schreibe_csv`/`lies_csv` (schema.py:89-124) already enforce: UTF-8/LF, strict cast with float-truncation guard, and header-must-match-schema on read — reuse unmodified, do not add a parallel CSV writer.

Add new path constants at the top of `schema.py` following the existing `*_CSV = Path("...")` convention (lines 20-39), e.g.:
```python
MANUELL_WURZEL = Path("manuell")
STEUERARTEN_CSV = MANUELL_WURZEL / "steuerarten.csv"
ZUWENDUNGEN_CSV = MANUELL_WURZEL / "zuwendungen.csv"
...
STELLENPLAN_CSV = Path("aufbereitet/stellenplan.csv")
```

---

### `pipeline/ostbevern/konfiguration.py` (extended `lade_sollwerte` tables for B.4-B.6)

**Analog:** existing optional top-level TOML tables already loaded by `lade_sollwerte` (e.g. `haushaltsquerschnitt_pg`, `stichproben` per RESEARCH.md "Don't Hand-Roll" table)

**Pattern:** add new keys to `2026_sollwerte.toml` under their own top-level table names (e.g. `[steuerarten]`, `[transferaufwendungen]`, `[stellenplan]`), validated automatically through the existing `_pruefe_nur_ganzzahlen`-style validation already wired into `lade_sollwerte` — no new loader function needed.

---

### `pipeline/tests/test_app_daten.py` (test, extends personennamen scan)

**Analog:** `pipeline/tests/test_produkte.py`, function `test_keine_personennamen` (lines 196-226)

**Pattern to extend** (RESEARCH.md Code Examples, directly copy-adaptable):
```python
from ostbevern.konfiguration import PROJEKT_WURZEL

APP_DATEN_WURZEL = PROJEKT_WURZEL / "app" / "src" / "data"

def test_keine_personennamen_in_app_daten(jahrgang, kontext) -> None:
    seiten, hierarchie = kontext
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        namen = lies_personennamen(dokument, jahrgang, seiten, hierarchie)
    nadeln = {text for _seite, text in namen} | {
        "".join(text.split()) for _seite, text in namen
    }
    for pfad in APP_DATEN_WURZEL.rglob("*.json"):
        inhalt = pfad.read_text(encoding="utf-8")
        for nadel in nadeln:
            assert nadel not in inhalt, f"{pfad}: Personenname gefunden"
```
This is a near-exact copy of the existing `test_keine_personennamen` body (`test_produkte.py:196-226`), just pointed at `app/src/data/` instead of `DATEN_WURZEL`. Do not invent a second name-detection heuristic (explicit "Don't Hand-Roll" entry).

---

## Shared Patterns

### Fail-fast error classes
**Source:** `pipeline/ostbevern/investitionen.py` (`class InvestitionenFehler(ValueError)`), `pipeline/ostbevern/pruefung.py` (`class PruefungsFehler(ValueError)`), `pipeline/ostbevern/schema.py` (`class SchemaFehler(ValueError)`)
**Apply to:** every new module (`manuell.py` → `ManuellFehler`? — actually Regel 5 lives inside `pruefung.py`, reuses `PruefungsFehler`; `stellenplan.py` → `StellenplanFehler`; `texte.py` → `TexteFehler`; `app_daten.py` → `AppDatenFehler`)
```python
class <Modul>Fehler(ValueError):
    """Wird ausgelöst, wenn ..."""
```
All raise sites use the `f"S. {pdf_seite}: <Kontext>: <Grund>"` message shape where a PDF page is relevant, otherwise `f"<Datei>: <Grund>"` (schema.py style).

### Atomic, deterministic JSON writing
**Source:** `pipeline/ostbevern/schema.py:321-350` (`schreibe_produkte_json`)
**Apply to:** all `app/src/data/*.json` writers in `app_daten.py` — tempfile + os.replace, `ensure_ascii=False`, `indent=2`, trailing `\n`, UTF-8 no BOM, LF newlines. This is the exact mechanism D-24's CI-diff-stability requirement depends on.

### CSV schema + strict cast + sorted write
**Source:** `pipeline/ostbevern/schema.py:89-124` (`schreibe_csv`/`lies_csv`)
**Apply to:** every new manual CSV (`steuerarten.csv`, `zuwendungen.csv`, `transferaufwendungen.csv`, `kita_zuschuesse.csv`, `weitere_vorberichtstabellen.csv`, `verbindlichkeiten.csv`, `eigenkapital.csv`, `ve_uebersicht.csv`) and `stellenplan.csv`. Column-header mismatch → `SchemaFehler`; float truncation → `SchemaFehler`; fixed sort order mandatory.

### Tolerance constants kept local to their module
**Source:** `pipeline/ostbevern/investitionen.py:52` (`_TOLERANZ_EURO = 1`, independent of `pruefung.TOLERANZ_EURO`)
**Apply to:** Regel 5's two new tolerances (`REGEL5_TOLERANZ_POSTEN_T_EURO`, `REGEL5_TOLERANZ_GEP_EURO`) defined in `pruefung.py` itself (since Regel 5 lives there), never reusing/overwriting the existing `TOLERANZ_EURO=1`.

### Personennamen-Dreifachsicherung
**Source:** `pipeline/ostbevern/produkte.py` (`lies_personennamen`, `PERSONENFELDER` allowlist) + `pipeline/tests/test_produkte.py:196-226`
**Apply to:** `app_daten.py` must never write a names field into any `app/src/data/*.json`; `test_app_daten.py` extends the scan to `app/src/data/`.

### Thin typer entrypoints, logic in `ostbevern/`
**Source:** every `pipeline/0N_*.py` script + `pipeline/alle.py`
**Apply to:** `05_stellenplan.py`, `07_app_daten.py` — command body is ~10-20 lines of jahrgang loading + one function call + echo/error handling; all real logic in `ostbevern/stellenplan.py` / `ostbevern/app_daten.py`.

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `daten/manuell/README.md` | config (doc) | file-I/O | No README exists yet under `daten/`; follow general project-doc tone (German, Du-Anrede not required here since it's a maintainer doc) and MANU-07's requirement to justify each file's values with PDF page references |
| `texte/erklaerungen.md` | config (data file) | transform | First placeholder-syntax text file in the repo; structure is fully Claude's Discretion per CONTEXT.md — use the `{{schluessel|format}}` syntax from RESEARCH.md Pattern/Code Example as the de facto standard since it's already been designed there |
| `app/src/data/typen.ts` | model (TS types) | transform | No existing shared TS data-types module; follow `app/src/charts/format.ts` only as a sibling-file convention (single-purpose module under `app/src/data/` or `app/src/charts/`), not as a structural analog |

## Metadata

**Analog search scope:** `pipeline/ostbevern/`, `pipeline/tests/`, `pipeline/alle.py`, `daten/aufbereitet/`, `app/src/data/`, `app/src/charts/`
**Files scanned:** 16 pipeline modules, 16 pipeline test files, `pipeline/alle.py`, 8 `daten/aufbereitet/` files, 2 `app/src/data/` files
**Pattern extraction date:** 2026-10-02
