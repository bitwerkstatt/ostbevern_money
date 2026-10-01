# Phase 2: Kernzahlen - Pattern Map

**Mapped:** 2026-10-01
**Files analyzed:** 17 (11 new library/CLI files, 5 new test files, 2 modified config files)
**Analogs found:** 17 / 17 (all role-match or partial-match; no exact prior analog exists for PDF-parsing logic since Phase 1 had none — `konfiguration.py` is the closest and only non-trivial Python module so far)

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|--------------------|------|-----------|-----------------|----------------|
| `pipeline/ostbevern/zahlen.py` | utility (parser) | transform | `pipeline/ostbevern/konfiguration.py` | partial (module-level pure functions, same error-raising convention) |
| `pipeline/ostbevern/pdf.py` | service (PDF wrapper) | file-I/O | `pipeline/ostbevern/konfiguration.py` | partial (single-responsibility I/O wrapper, dataclass outputs) |
| `pipeline/ostbevern/seiten.py` | service (Schritt 01) | batch/transform | `pipeline/ostbevern/konfiguration.py` | role-match (reads config, builds dataclasses, raises `KonfigurationsFehler`-style errors) |
| `pipeline/ostbevern/plaene.py` | service (Schritt 02) | batch/transform | `pipeline/ostbevern/konfiguration.py` | role-match (dict-keyed lookup tables, dataclasses, abort-fast errors) |
| `pipeline/ostbevern/pruefung.py` | service (Schritt 06) | batch/transform | `pipeline/ostbevern/konfiguration.py` | role-match (loads + validates structured data, raises typed errors) |
| `pipeline/ostbevern/schema.py` | config (CSV schema) | transform | `pipeline/ostbevern/konfiguration.py` (dataclasses `Seitenbereich`/`Anzahlen`) | role-match (central typed schema definitions) |
| `pipeline/01_seiten_klassifizieren.py` | route/CLI entry | request-response (CLI) | `pipeline/alle.py` | exact (thin typer entry pattern) |
| `pipeline/02_plaene_extrahieren.py` | route/CLI entry | request-response (CLI) | `pipeline/alle.py` | exact |
| `pipeline/06_pruefen.py` | route/CLI entry | request-response (CLI) | `pipeline/alle.py` | exact |
| `pipeline/alle.py` (modified) | route/CLI entry | request-response (CLI) | itself (extend in place) | exact |
| `pipeline/jahrgaenge/2026.toml` (modified) | config | — | itself (extend `[kopfzeilen]` with `produktgruppe`) | exact |
| `pipeline/jahrgaenge/2026_sollwerte.toml` (modified) | config | — | itself (extend with B.1–B.3, Anhang A) | exact |
| `pipeline/ostbevern/konfiguration.py` (modified) | config loader | transform | itself (extend `Kopfzeilen` dataclass + validation) | exact |
| `pipeline/tests/test_zahlen.py` | test | transform (unit) | `pipeline/tests/test_konfiguration.py` | role-match (pure-function unit tests, regex-derived fixtures) |
| `pipeline/tests/test_seiten.py` | test | file-I/O (unit, real PDF pages) | `pipeline/tests/test_rauchtest.py` | role-match (opens real PDF via `pdfplumber`, asserts on `lade_jahrgang` output) |
| `pipeline/tests/test_plaene.py` | test | file-I/O (unit, real PDF pages) | `pipeline/tests/test_rauchtest.py` | role-match |
| `pipeline/tests/test_pruefung.py` | test | CRUD (reads checked-in CSVs) | `pipeline/tests/test_konfiguration.py` | role-match (tmp_path fixtures, `pytest.raises` on typed errors) |
| `pipeline/tests/test_hierarchie.py` | test | CRUD (reads checked-in CSVs) | `pipeline/tests/test_konfiguration.py` | role-match |

## Pattern Assignments

### `pipeline/ostbevern/zahlen.py` (utility, transform)

**Analog:** `pipeline/ostbevern/konfiguration.py`

**Module docstring + import style** (lines 1-16):
```python
"""Lädt die Jahrgangskonfiguration (D-06 bis D-09) aus `pipeline/jahrgaenge/*.toml`.
...
"""

from __future__ import annotations

import re
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any
```
Apply the same style to `zahlen.py`: module docstring referencing the relevant decisions (EXTR-01), `from __future__ import annotations`, stdlib-only imports (`re`), no PDF dependency per the Architectural Responsibility Map.

**Error type pattern** (lines 41-42):
```python
class KonfigurationsFehler(ValueError):
    """Wird ausgelöst, wenn eine Jahrgangs- oder Sollwertdatei fehlt oder unvollständig ist."""
```
`zahlen.py` should define its own `ValueError` subclass (e.g. `ZahlenFehler`) following this exact one-line-docstring convention, used by D-08 abort-fast behavior when a token cannot be parsed.

**Operator-splitting function** — use RESEARCH.md's verified Code Example directly (already project-idiomatic, German identifiers, no umlauts):
```python
OPERATOR_MUSTER = re.compile(r"^(\+/-|\+|-|=)")

def trenne_operator(erstes_wort: str) -> tuple[str | None, str]:
    treffer = OPERATOR_MUSTER.match(erstes_wort)
    if treffer:
        operator = treffer.group(1)
        rest = erstes_wort[len(operator):]
        return operator, rest
    return None, erstes_wort
```

---

### `pipeline/ostbevern/pdf.py` (service, file-I/O)

**Analog:** `pipeline/ostbevern/konfiguration.py` (I/O isolation pattern) + `pipeline/tests/test_rauchtest.py` (pdfplumber usage)

**I/O isolation convention** (konfiguration.py lines 1-7): konfiguration.py's docstring explicitly states "Dieses Modul ist die einzige Stelle, die `tomllib` importiert." Mirror this exactly for `pdf.py`: it must be the **only** module that imports `pdfplumber` (per Architectural Responsibility Map), stated in its docstring.

**pdfplumber usage pattern** (`pipeline/tests/test_rauchtest.py` lines 15-19):
```python
import pdfplumber

with pdfplumber.open(jahrgang.pdf_pfad) as pdf:
    assert len(pdf.pages) == jahrgang.anzahlen.pdf_seiten
```
`pdf.py` should wrap `pdfplumber.open()` in a context-managed helper returning per-page word lists with coordinates (`extract_words()`), per RESEARCH.md Pattern 1/Code Examples.

**Path handling:** reuse `jahrgang.pdf_pfad` (already an absolute, validated `Path` from `lade_jahrgang` — see konfiguration.py lines 133-143 path-traversal guard) rather than re-deriving or re-validating the PDF path.

---

### `pipeline/ostbevern/seiten.py`, `plaene.py`, `pruefung.py` (service, batch/transform)

**Analog:** `pipeline/ostbevern/konfiguration.py`

**Dataclass + typed-error validation pattern** (lines 45-82, 84-197):
```python
@dataclass(frozen=True)
class Kopfzeilen:
    produktbereich: str
    produkt: str
    seitentypen: tuple[str, ...]
    fortsetzung: str

def lade_jahrgang(jahr: int, *, verzeichnis: Path = JAHRGAENGE_VERZEICHNIS) -> Jahrgang:
    ...
    if fehlende_schluessel:
        raise KonfigurationsFehler(
            f"Jahrgangsdatei {pfad} fehlen Schlüssel: {', '.join(fehlende_schluessel)}"
        )
    ...
    return Jahrgang(...)
```
Apply this exact shape to each Schritt module: frozen dataclasses for row/page records, a top-level function taking explicit keyword-overridable paths (for test injection, mirroring `verzeichnis: Path = ...`), and abort-fast via a dedicated typed exception with an f-string that names the offending PDF page/line (D-08). Define one exception per concern (e.g. `SeitenFehler`, `PlaeneFehler`, `PruefungsFehler`) following the single-line-docstring `ValueError` subclass convention shown above — do not reuse `KonfigurationsFehler` outside `konfiguration.py`.

**Dict-keyed-by-number lookup convention** (`PFLICHT_PLANTYPEN`/`PFLICHT_SEITENBEREICHE` tuples, lines 27-38): the D-12 row dictionary should follow the same "module-level constant tuple/dict, validated against at load time" shape used for `PFLICHT_SEITENBEREICHE`.

**D-01 shared-logic entry point:** `pruefung.py` must expose one function (e.g. `pruefe_alles(...) -> Bericht`) called identically from `06_pruefen.py` and from `test_pruefung.py`, mirroring how `lade_jahrgang`/`lade_sollwerte` are each called identically from `alle.py` (lines 37-38) and from `test_rauchtest.py`/`test_konfiguration.py`.

---

### `pipeline/ostbevern/schema.py` (config, transform)

**Analog:** `pipeline/ostbevern/konfiguration.py` dataclasses (`Seitenbereich`, `Anzahlen`, lines 45-70) + RESEARCH.md polars Code Example.

**Pattern:**
```python
import polars as pl

SPALTEN_HIERARCHIE: dict[str, pl.DataType] = {
    "ebene": pl.Utf8,
    "code": pl.Utf8,
    ...
}
```
Use `schema_overrides=SPALTEN_HIERARCHIE` on every `pl.read_csv` call and `schema=SPALTEN_HIERARCHIE` on every `pl.DataFrame(...)` construction before `write_csv()`, per D-22 and the verified polars BOM/LF behavior:
```python
df = pl.DataFrame(
    {"code": ["01", "0106"], "betrag": [100, -50]},
    schema={"code": pl.Utf8, "betrag": pl.Int64},
)
csv_bytes = df.write_csv().encode("utf-8")
assert not csv_bytes.startswith(b"\xef\xbb\xbf")
assert b"\r\n" not in csv_bytes
```

---

### `pipeline/01_seiten_klassifizieren.py`, `02_plaene_extrahieren.py`, `06_pruefen.py` (route/CLI, request-response)

**Analog:** `pipeline/alle.py` (exact match — this is the only existing CLI entry point)

**Full thin-entry pattern** (lines 1-57):
```python
"""..."""

from __future__ import annotations

from typing import Annotated

import typer

from ostbevern.konfiguration import (
    PROJEKT_WURZEL,
    STANDARD_JAHR,
    KonfigurationsFehler,
    lade_jahrgang,
    lade_sollwerte,
)

app = typer.Typer(
    add_completion=False,
    help="...",
)


@app.command()
def main(
    jahr: Annotated[
        int,
        typer.Option("--jahr", help="Haushaltsjahr; lädt pipeline/jahrgaenge/{jahr}.toml"),
    ] = STANDARD_JAHR,
) -> None:
    try:
        jahrgang = lade_jahrgang(jahr)
        ...
    except KonfigurationsFehler as fehler:
        typer.echo(f"Fehler: {fehler}", err=True)
        raise typer.Exit(code=1) from fehler

    ...
    typer.echo(f"...")


if __name__ == "__main__":
    app()
```
Each new `NN_*.py` script copies this exact structure: module docstring naming its Spez. section, `--jahr` option defaulting to `STANDARD_JAHR`, `try`/`except KonfigurationsFehler` → `typer.Exit(code=1)`, and a final `typer.echo` summary line. The business logic itself must live in the corresponding `ostbevern/*.py` module (D-09) — these scripts only call it and format output.

**Modifying `alle.py` for D-09** (chaining steps 01→02→06): extend the existing `main()` body to call each step's library function in order inside the same `try`/`except KonfigurationsFehler` block already present (lines 36-46), rather than shelling out to the other scripts.

---

### `pipeline/jahrgaenge/2026.toml` (config, modified)

**Analog:** itself — extend `[kopfzeilen]` (lines 39-43)

**Pitfall 3 fix — add `produktgruppe` pattern:**
```toml
[kopfzeilen]
produktbereich = '^Produktbereich (\d{2}) (.+)$'
produkt = '^Produkt (\d{6}) (.+)$'
produktgruppe = '^Produktgruppe (\d{4}) (.+)$'
seitentypen = ["Produktinformationen", "Teilergebnisplan", "Teilfinanzplan", "Investitionen", "Investitionsmaßnahmen"]
fortsetzung = "Fortsetzung folgt"
```
Mirror `konfiguration.py`'s `Kopfzeilen` dataclass (lines 53-60) and its fehlende-Schlüssel validation loop (lines 110-113) to add `produktgruppe` as a required field, plus `re.compile(kopfzeilen.produktgruppe)` alongside the existing two `re.compile` calls (lines 187-188).

---

### `pipeline/jahrgaenge/2026_sollwerte.toml` (config, modified)

**Analog:** itself — extend following the existing `gesamtergebnisplan`/`satzung` shape (referenced via `lade_sollwerte`, lines 216-251, and `test_konfiguration.py` lines 154-164 for the per-row length-validation convention). New top-level tables for B.2, B.3 (per-PB), and Anhang A (product directory with start pages) should follow the same "jahre list + zeilen dict keyed by row number, validated for equal length" shape already enforced by `lade_sollwerte`'s `gesamtergebnisplan.jahre`/`zeilen` check (lines 240-247).

---

### `pipeline/tests/test_zahlen.py` (test, transform)

**Analog:** `pipeline/tests/test_konfiguration.py`

**Pure-function unit test style** (lines 1-23, 48-56):
```python
"""Tests für ostbevern.konfiguration: lade_jahrgang und lade_sollwerte.

Fixtures sind Textvarianten der echten Jahrgangs-/Sollwertdatei ...
"""
from __future__ import annotations

import pytest

from ostbevern.konfiguration import ...


def test_lade_jahrgang_gibt_vollstaendigen_jahrgang_zurueck() -> None:
    jahrgang = lade_jahrgang(STANDARD_JAHR)
    ...
```
`test_zahlen.py` is pure-string (D-07), so no fixtures/tmp_path needed — just direct `trenne_operator(...)`/number-parser calls with literal strings covering: German thousands separator, ASCII minus, `–` (no value), glued amounts, `C` currency marker, operator glued to text (`"+/-Bestandsveränderungen"`), and missing operator (plain text).

---

### `pipeline/tests/test_seiten.py`, `test_plaene.py` (test, file-I/O real PDF)

**Analog:** `pipeline/tests/test_rauchtest.py`

**Real-PDF-page test pattern** (lines 1-24):
```python
"""Rauchtest (D-12): Jahrgangsdatei lädt, PDF existiert mit erwarteter Seitenzahl."""

from __future__ import annotations

import pdfplumber

from ostbevern.konfiguration import STANDARD_JAHR, lade_jahrgang, lade_sollwerte


def test_pdf_existiert_mit_erwarteter_seitenzahl() -> None:
    jahrgang = lade_jahrgang(STANDARD_JAHR)
    assert jahrgang.pdf_pfad.is_file()
    with pdfplumber.open(jahrgang.pdf_pfad) as pdf:
        assert len(pdf.pages) == jahrgang.anzahlen.pdf_seiten
```
Follow this shape exactly: load `jahrgang` via `lade_jahrgang(STANDARD_JAHR)`, open the real PDF through `jahrgang.pdf_pfad`, and index into `pdf.pages[N-1]` for the specific sample pages named in D-07 (62, 63, 66, 83, 84-86, 150, continuation pages). No literal PDF page numbers for *values* being asserted — assert against values the test itself derives from the config, except where a specific PDF page number genuinely is the thing under test (page constants may live as local test constants with a comment citing D-07).

---

### `pipeline/tests/test_pruefung.py`, `test_hierarchie.py` (test, CRUD on checked-in CSVs)

**Analog:** `pipeline/tests/test_konfiguration.py`

**tmp_path + typed-error pattern** (lines 36-45, 64-68):
```python
def _schreibe_jahrgangsdatei(tmp_path: Path, text: str, jahr: int = STANDARD_JAHR) -> Path:
    pfad = tmp_path / f"{jahr}.toml"
    pfad.write_text(text, encoding="utf-8")
    return pfad


def test_fehlender_pdf_pfad_meldet_schluessel(tmp_path: Path) -> None:
    text = re.sub(r"(?m)^pdf_pfad\s*=.*\n", "", _jahrgangsdatei_text())
    _schreibe_jahrgangsdatei(tmp_path, text)
    with pytest.raises(KonfigurationsFehler, match="pdf_pfad"):
        lade_jahrgang(STANDARD_JAHR, verzeichnis=tmp_path)
```
`test_pruefung.py` reads the real checked-in CSVs under `daten/zwischen/`/`daten/aufbereitet/` (D-06, no PDF) directly for the happy path, and uses the same tmp_path-mutate-and-reload approach to test D-04/D-05 `befunde.md` edge cases (stale finding, amount mismatch) by writing a modified `befunde.md` to `tmp_path` and pointing the loader at it, mirroring `_schreibe_sollwertdatei`. `test_hierarchie.py` reads `hierarchie.csv` directly and cross-checks counts (15 PB, 48 PG, 63 Produkte) and Anhang-A start pages against `2026_sollwerte.toml` loaded via `lade_sollwerte`.

---

## Shared Patterns

### Typed, module-scoped exceptions (abort-fast, D-08)
**Source:** `pipeline/ostbevern/konfiguration.py` lines 41-42
**Apply to:** `zahlen.py`, `pdf.py`, `seiten.py`, `plaene.py`, `pruefung.py` — one `ValueError` subclass per module, one-line docstring, f-string messages naming the offending PDF page/line/key.
```python
class KonfigurationsFehler(ValueError):
    """Wird ausgelöst, wenn eine Jahrgangs- oder Sollwertdatei fehlt oder unvollständig ist."""
```

### Thin typer CLI entry + try/except/Exit
**Source:** `pipeline/alle.py` lines 29-53
**Apply to:** `01_seiten_klassifizieren.py`, `02_plaene_extrahieren.py`, `06_pruefen.py`, and the extended `alle.py`.

### Config-only jahrgang values, loaded exclusively via `lade_jahrgang`/`lade_sollwerte`
**Source:** `pipeline/ostbevern/konfiguration.py` (whole module) + CLAUDE.md convention
**Apply to:** every new module — never hardcode page numbers, row dictionaries' *numeric keys* are fine (they're structural, not jahrgang-specific per D-12), but column headers, page ranges, header regexes, and Sollwerte must come from `2026.toml`/`2026_sollwerte.toml` via the existing loader, extended only with validated new keys (e.g. `kopfzeilen.produktgruppe`).

### Central polars CSV schema (D-22)
**Source:** RESEARCH.md Code Examples (polars BOM/LF verification) + `pipeline/ostbevern/konfiguration.py` dataclass-centralization style
**Apply to:** `schema.py`, consumed by `seiten.py`, `plaene.py`, `pruefung.py` for every CSV read/write — always pass explicit `schema`/`schema_overrides` to prevent `"01"` → `1` coercion.

### Real-PDF-page tests vs. checked-in-CSV tests (D-06/D-07 split)
**Source:** `pipeline/tests/test_rauchtest.py` (PDF) vs. `pipeline/tests/test_konfiguration.py` (tmp_path config fixtures)
**Apply to:** `test_seiten.py`/`test_plaene.py` (PDF, D-07) must never read `daten/`; `test_pruefung.py`/`test_hierarchie.py` (CSV, D-06) must never open the PDF.

## No Analog Found

None. Every file has at least a role-match analog in the existing Phase 1 code (`konfiguration.py`, `alle.py`, and the three existing test files). There is no PDF-parsing analog yet since Phase 1 did not touch `pdfplumber` beyond the rauchtest — `pdf.py`, `seiten.py`, and `plaene.py` are "first of their kind" and must follow RESEARCH.md's Code Examples/Patterns (x-coordinate column mapping, operator-regex, section-scanning per Pitfall 2) rather than a direct codebase precedent for their PDF-specific internals; the *structural* conventions (dataclasses, typed errors, docstrings, German identifiers) are nonetheless fully covered by `konfiguration.py`.

## Metadata

**Analog search scope:** `pipeline/` (entire tracked tree: `ostbevern/`, `tests/`, `jahrgaenge/`, `alle.py`, `pyproject.toml`)
**Files scanned:** 8 tracked pipeline files (all of Phase 1's output) + `02-CONTEXT.md` + `02-RESEARCH.md`
**Pattern extraction date:** 2026-10-01
