# Phase 3: Details - Pattern Map

**Mapped:** 2026-10-01
**Files analyzed:** 14 (4 new pipeline modules, 2 new typer entrypoints, 1 extended module, 1 extended schema module, 5 new/extended test files, 1 extended `alle.py`)
**Analogs found:** 14 / 14

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|-----------------|----------------|
| `pipeline/ostbevern/freitext.py` | utility | transform | `pipeline/ostbevern/zahlen.py` | role-match (pure string utility module) |
| `pipeline/ostbevern/produkte.py` | service (PDF-parsing) | file-I/O → CRUD-write | `pipeline/ostbevern/plaene.py` | exact (coordinate-based page parser → CSV/record writer) |
| `pipeline/ostbevern/investitionen.py` | service (PDF-parsing) | file-I/O → CRUD-write | `pipeline/ostbevern/plaene.py` | exact (same `_ordne_werte`/block-buffering architecture) |
| `pipeline/ostbevern/querschnitte.py` | service (PDF-parsing) | file-I/O → CRUD-write | `pipeline/ostbevern/plaene.py` (page scan) + `pipeline/ostbevern/seiten.py` (classification-adjacent extraction) | role-match |
| `pipeline/ostbevern/schema.py` (extended) | config/schema | CRUD (I/O definitions) | itself, existing `PLAN_SPALTEN`/`schreibe_plan_csv`/`lies_plan_csv` triplet | exact (extend in place) |
| `pipeline/ostbevern/pruefung.py` (extended, Regeln 6-8) | service (validation) | batch (CSV-only comparison) | `pipeline/ostbevern/pruefung.py` `_pruefe_regel3`/`_pruefe_regel1` | exact (extend in place) |
| `pipeline/03_produktinfos.py` | route/CLI entrypoint | request-response (CLI) | `pipeline/02_plaene_extrahieren.py` | exact |
| `pipeline/04_investitionen.py` | route/CLI entrypoint | request-response (CLI) | `pipeline/02_plaene_extrahieren.py` | exact |
| `pipeline/06_pruefen.py` (extended: calls `querschnitte.extrahiere_querschnitte` before `pruefung.pruefe_alles`) | route/CLI entrypoint | request-response (CLI) | itself + `pipeline/02_plaene_extrahieren.py` for the PDF-reading-then-CSV-writing shape | exact |
| `pipeline/alle.py` (extended: steps 03→04→06) | route/CLI entrypoint | batch (orchestration) | itself (existing step chain) | exact |
| `pipeline/tests/test_freitext.py` | test | transform | `pipeline/tests/test_zahlen.py` | exact |
| `pipeline/tests/test_produkte.py` | test | file-I/O (real PDF pages) | `pipeline/tests/test_plaene.py` | exact |
| `pipeline/tests/test_investitionen.py` | test | file-I/O (real PDF pages) | `pipeline/tests/test_plaene.py` | exact |
| `pipeline/tests/test_querschnitte.py` | test | file-I/O (real PDF pages) | `pipeline/tests/test_plaene.py` | exact |
| `pipeline/tests/test_pruefung.py` (extended: Regeln 6-8) | test | batch (CSV-only) | itself, existing Regel-1/2/3 test blocks | exact |

## Pattern Assignments

### `pipeline/ostbevern/freitext.py` (utility, transform)

**Analog:** `pipeline/ostbevern/zahlen.py`

**Module docstring + no-PDF-dependency convention** (lines 1-9):
```python
"""Zahlen- und Operator-Parser für Planzeilen (EXTR-01).

Reines String-Parsing ohne PDF-Abhängigkeit. ...
"""

from __future__ import annotations

import re
```
Apply the same shape to `freitext.py`: a pure string-transform module (no `pdfplumber` import — callers pass already-extracted word/line text), with a module-level docstring citing the relevant CONTEXT decisions (D-10, D-11) and a dedicated `FreitextFehler(ValueError)` exception class if any transform can fail.

**Regex-driven single-purpose functions with inline rationale comments** (lines 12-27, 65-80):
```python
_ANGEKLEBTER_BETRAG_MUSTER = re.compile(
    r"^(?P<rest>.*?[A-Za-zÀ-ÖØ-öø-ÿ.)/])(?P<betrag>-?\d{1,3}(?:\.\d{3})*)$"
)

def trenne_angeklebten_betrag(wort: str) -> tuple[str, str | None]:
    """Trennt einen angeklebten Betrag vom Label-Ende ab (Spez. 3.8, 5.4).
    ...
    """
    treffer = _ANGEKLEBTER_BETRAG_MUSTER.match(wort)
    if treffer:
        return treffer.group("rest"), treffer.group("betrag")
    return wort, None
```
Copy this exact style for `freitext.py`'s three D-10 transforms: Silbentrennung removal (hyphen-at-line-end before lowercase, but not before uppercase/"und/oder/sowie"), `(cid:15)`-bullet splitting into a list, and the `extract_words(x_tolerance=1)`-based space-joining helper. Each function stays small, takes/returns plain strings or lists of strings, and documents the triggering CONTEXT decision ID in its docstring.

**Boolean helper without exception, paired with a strict variant** (lines 48-53):
```python
def ist_betrag(text: str) -> bool:
    """True, wenn `text` ein von lies_betrag akzeptierter Betrag ist (ohne Ausnahme)."""
    try:
        lies_betrag(text)
    except ZahlenFehler:
        return False
    return True
```
Useful if `produkte.py` needs an `ist_postenbeginn(text)` predicate (D-01: "führender Betrag + C") built on top of a strict parser.

---

### `pipeline/ostbevern/produkte.py` (service, file-I/O)

**Analog:** `pipeline/ostbevern/plaene.py`

**Module docstring + fail-fast exception class** (lines 1-39):
```python
"""Schritt 02: Pläne extrahieren (Spez. 5.4).
...
Bricht bei jedem Unstimmigkeit sofort mit PDF-Seite und Zeile ab (D-08).
"""
...
class PlaeneFehler(ValueError):
    """Wird ausgelöst, wenn eine Plantabellen-Seite oder -Zeile nicht lesbar ist (D-08)."""
```
`produkte.py` needs `ProdukteFehler(ValueError)` with the identical "message starts with `f"S. {pdf_seite}: …"`" convention (Pattern 2 from RESEARCH.md).

**Frozen dataclass result types** (lines 42-58):
```python
@dataclass(frozen=True)
class GedruckteZeile:
    """Eine geparste Planzeile vor dem Abgleich mit dem Zeilen-Wörterbuch."""
    zeile: str
    operator: str | None
    bezeichnung: str
    werte: tuple[int, ...]
    pdf_seite: int

@dataclass(frozen=True)
class ExtraktionsErgebnis:
    """Ergebnis von extrahiere_plaene: Anzahl geschriebener CSV-Zeilen und Zielpfad."""
    zeilen_geschrieben: int
    pfad: Path
```
Reuse this for `Produktinfo` (one frozen dataclass per 63-product record pre-JSON-serialization), `Erlaeuterungsposten`, `Grundzahl`, and a shared `ExtraktionsErgebnis`-like result wrapper for the `extrahiere_produkte(jahrgang)` entrypoint function.

**Multi-block-per-page scanning via a `schliesse()` closure + state machine** (lines 80-158, `lies_abschnitte`):
```python
def lies_abschnitte(
    zeilen: Sequence[Textzeile], jahrgang: Jahrgang, pdf_seite: int
) -> list[Abschnitt]:
    """Zerlegt eine Teilplan-Seite in Teilergebnisplan-/Teilfinanzplan-Abschnitte.

    Scannt die ganze Seite nach beiden Abschnitts-Headern statt einem einzigen Typ pro
    Seite zu vertrauen (Research Pattern 3, Pitfall 2). ...
    """
    ...
    def schliesse() -> None:
        nonlocal plantyp, fortsetzung, gesammelt
        if plantyp is not None:
            abschnitte.append(Abschnitt(plantyp=plantyp, zeilen=tuple(gesammelt), fortsetzung=fortsetzung))
        plantyp = None
        fortsetzung = False
        gesammelt = []

    for zeile in zeilen:
        ...
    schliesse()
    return abschnitte
```
This is the **direct template** for the Erläuterungsblock scanner (D-02/D-03, RESEARCH Pattern 5/Pitfall 4): scan every line of the page once, open a new block on a `zu Nr.`/generic `Erläuterung`-header match, close the previous block via the same `schliesse()` pattern, and never stop at the first match. Also directly reusable for two-page `produktinformationen` handling (Open Question 3).

**x-coordinate value assignment with tolerance derived from column spacing** (lines 188-218, `_ordne_werte`):
```python
def _ordne_werte(
    amount_woerter: list[Wort], jahreswoerter: tuple[Wort, ...], pdf_seite: int, zeilennummer: str
) -> tuple[int, ...]:
    ...
    sortierte_betraege = sorted(amount_woerter, key=lambda w: w.x1)
    sortierte_jahre = sorted(jahreswoerter, key=lambda w: w.x1)
    abstaende = [abs(sortierte_jahre[i].x1 - sortierte_jahre[i - 1].x1) for i in range(1, len(sortierte_jahre))]
    toleranz = min(abstaende) / 2 if abstaende else float("inf")
    ...
```
Needed verbatim-style for `grundzahlen.csv`'s year-column value assignment (same 7-ish column layout as plans) and for the Erläuterungsposten amount detection (leading `Betrag C`).

**Angeklebter-Betrag handling inline in a row parser** (lines 274-286): reuse `trenne_angeklebten_betrag` from `ostbevern.zahlen` directly — same import, same usage pattern — for Grundzahlen rows with glued amounts.

---

### `pipeline/ostbevern/investitionen.py` (service, file-I/O)

**Analog:** `pipeline/ostbevern/plaene.py`

**Imports pattern** (lines 8-32):
```python
from __future__ import annotations

import re
from collections.abc import Collection, Sequence
from dataclasses import dataclass, replace
from pathlib import Path

import polars as pl

from ostbevern.konfiguration import Jahrgang
from ostbevern.pdf import PdfDokument, Textzeile, Wort
from ostbevern.schema import (
    DATEN_WURZEL, ERGEBNISPLAN_CSV, FINANZPLAN_CSV, HIERARCHIE_CSV, PLAN_SPALTEN,
    SEITEN_CSV, lies_hierarchie_csv, lies_seiten_csv, schreibe_plan_csv, zerlege_spaltenkopf,
)
from ostbevern.zahlen import ist_betrag, lies_betrag, trenne_angeklebten_betrag, trenne_operator
from ostbevern.zeilen import ZEILEN, ZWISCHENUEBERSCHRIFTEN, normalisiere_bezeichnung, plantyp_fuer
```
`investitionen.py` mirrors this shape: import `PdfDokument`/`Textzeile`/`Wort` from `ostbevern.pdf`, the new `INVESTITIONEN_SPALTEN`/`VE_FAELLIGKEITEN_SPALTEN`/`schreibe_investitionen_csv` names from `ostbevern.schema`, and `ostbevern.zahlen` for amount parsing.

**Block-buffer-until-trailer pattern (directly matches Pattern 4/D-08 — Saldo-line ID disambiguation)**: `plaene.py` doesn't have an identical trailer-buffering example, but `lies_plantabelle`'s "continuation line attaches to `aktuelle_zeile`" logic (lines 303-307) is the closest existing precedent for "a row's identity isn't settled until a later marker is seen":
```python
elif not ist_zeilenkopf and not amount_woerter and aktuelle_zeile is not None:
    vorherige = gelesene_zeilen[aktuelle_zeile]
    gelesene_zeilen[aktuelle_zeile] = replace(vorherige, bezeichnung=vorherige.bezeichnung + text)
```
For `investitionen.py`, extend this to: buffer every line of a Maßnahmen-block (header + Kontozeilen + Kassenwirksamkeit-Zeile) into a list, and only split ID/Name once the `Saldo<ID>`-trailer line is read (D-08, RESEARCH Pattern 4) — use `dataclasses.replace` the same way to patch the buffered dataclass once the ID is known.

**Fail-fast cross-source reconciliation (D-06 Gegenprobe)**: model on `lies_teilplaene`'s post-loop completeness check (lines 459-473):
```python
erwartete_knoten = hierarchie.filter(pl.col("ebene").is_in(list(ebenen)) & ~pl.col("synthetisch"))
for knoten in erwartete_knoten.iter_rows(named=True):
    schluessel = (knoten["ebene"], knoten["code"])
    anzahl_teg = teilergebnisplan_abschnitte.get(schluessel, 0)
    if anzahl_teg != 1:
        raise PlaeneFehler(f"{knoten['ebene']} {knoten['code']}: {anzahl_teg} ... erwartet genau 1")
```
Use the identical "collect sets/dicts while scanning, then one fail-fast pass over the expected universe" shape for comparing Produktseiten-Maßnahmen vs. PB-Investitionslisten-Maßnahmen (D-06): a measure present in only one source raises `InvestitionenFehler`.

---

### `pipeline/ostbevern/querschnitte.py` (service, file-I/O)

**Analog:** `pipeline/ostbevern/plaene.py` (page scan + `_ordne_werte`) combined with `pipeline/ostbevern/schema.py`'s CSV write pair.

**Core pattern:** same `dokument.zeilen(pdf_seite)` → scan → `_ordne_werte`-style coordinate assignment → list-of-dataclasses → `pl.DataFrame(..., schema=QUERSCHNITTE_SPALTEN)` → `schreibe_csv(...)` pipeline as `plaene._gesamtplan_datensaetze` (lines 329-364):
```python
def _gesamtplan_datensaetze(dokument, jahrgang, *, datei) -> list[dict[str, object]]:
    ...
    zeilen = dokument.zeilen(bereich.von)
    gedruckte_zeilen = lies_plantabelle(zeilen, plantyp=plantyp, spalten=spalten, pdf_seite=bereich.von)
    ...
    return datensaetze
```
`querschnitte.extrahiere_querschnitte(jahrgang, daten_wurzel=...)` should follow this exact shape but write to `daten/zwischen/querschnitte.csv` (control-source location, per D-14) instead of `daten/aufbereitet/`.

**Architecture placement — resolves RESEARCH Open Question 1:** call `querschnitte.extrahiere_querschnitte` as its own PDF-reading step inside `06_pruefen.py`'s typer `main()`, **before** `pruefung.pruefe_alles(jahr)`. `pruefung.py` itself stays CSV-only (its own docstring line 5 states this invariant — do not import `ostbevern.pdf` into `pruefung.py`).

---

### `pipeline/ostbevern/schema.py` (extended)

**Analog:** itself — existing `PLAN_SPALTEN` + `schreibe_plan_csv`/`lies_plan_csv` triplet (lines 44-57, 95-105) and `SEITEN_SPALTEN`/`HIERARCHIE_SPALTEN` triplets (lines 108-144).

**Pattern to copy per new CSV** (`erlaeuterungen.csv`, `grundzahlen.csv`, `investitionen.csv`, `ve_faelligkeiten.csv`, `querschnitte.csv`):
```python
HIERARCHIE_SPALTEN: dict[str, pl.PolarsDataType] = {
    "ebene": pl.Utf8,
    "code": pl.Utf8,
    "name": pl.Utf8,
    "eltern_code": pl.Utf8,
    "pdf_seite_start": pl.Int64,
    "synthetisch": pl.Boolean,
}

def schreibe_hierarchie_csv(df: pl.DataFrame, pfad: Path) -> None:
    """Schreibt hierarchie.csv sortiert nach code, was Baumreihenfolge ergibt (D-14, D-15)."""
    schreibe_csv(df, pfad, HIERARCHIE_SPALTEN, ["code"])

def lies_hierarchie_csv(pfad: Path) -> pl.DataFrame:
    """Liest hierarchie.csv über `lies_csv` mit HIERARCHIE_SPALTEN."""
    return lies_csv(pfad, HIERARCHIE_SPALTEN)
```
Add five new `*_SPALTEN` dicts plus matching `schreibe_*_csv`/`lies_*_csv` pairs that just delegate to the existing generic `schreibe_csv`/`lies_csv` (lines 72-92) — never hand-roll new I/O. Also add five new `Path` constants next to `SEITEN_CSV`/`HIERARCHIE_CSV` (lines 17-22), e.g. `GRUNDZAHLEN_CSV = Path("aufbereitet/grundzahlen.csv")`, `QUERSCHNITTE_CSV = Path("zwischen/querschnitte.csv")` (note the `zwischen/` location per D-14, not `aufbereitet/`).

`produkte.json` is not a CSV — it needs a new, separate `schreibe_produkte_json`/analogous function (no existing analog in `schema.py`); follow the same "central, single I/O function, called by tests too" principle but write deterministic-key-order JSON (UTF-8, LF) instead.

---

### `pipeline/ostbevern/pruefung.py` (extended: Regeln 6-8)

**Analog:** `_pruefe_regel3` (lines 515-553, reproduced above) for a GESAMT-vs-sum rule shape; `_pruefe_regel1` (lines 376-413) for a per-row formula rule shape.

**Core CSV-only comparison pattern** (lines 515-553):
```python
def _pruefe_regel3(*, planwerte, hierarchie, spalten, pdf_seite) -> Regelergebnis:
    """Regel 3 – Σ der 15 PB == Gesamtergebnisplan, Z. 01-17/19/20, ohne TP 27/28 (Spez. 5.5)."""
    spalten_zu_wertart = _spalten_zu_wertart(spalten)
    ...
    geprueft = 0
    abweichungen: list[Pruefpunkt] = []
    for zeile in REGEL3_ZEILEN:
        for wertart, jahr in spalten_zu_wertart:
            soll = planwerte.wert("GESAMT", "", zeile, jahr, wertart)
            ist = sum(planwerte.wert("PB", pb_code, zeile, jahr, wertart) for pb_code in pb_codes)
            geprueft += 1
            punkt = Pruefpunkt(regel=3, plan=plantyp, ebene="GESAMT", code="", zeile=zeile,
                                jahr=jahr, wertart=wertart, soll=soll, ist=ist, pdf_seite=pdf_seite)
            if abs(punkt.abweichung) > TOLERANZ_EURO:
                abweichungen.append(punkt)
    return Regelergebnis(regel=3, titel="Regel 3 – ...", geprueft=geprueft, abweichungen=tuple(abweichungen))
```
Write `_pruefe_regel6` (Investitionssummen je Produkt/Gesamt vs. Teilfinanzplan Z. 23/30), `_pruefe_regel7` (Querschnitte vs. PG/PB-Teilpläne), `_pruefe_regel8` (Vollständigkeit über `produkte.json`) with the exact same `Pruefpunkt`-per-comparison / `TOLERANZ_EURO` / `Regelergebnis` return shape. `Pruefpunkt` (lines 85-108) and `Befund` are reused unchanged — just populate `regel=6/7/8`.

**Wiring into `pruefe_alles`** (around line 778-806): add `regel6 = _pruefe_regel6(...)`, `regel7 = _pruefe_regel7(...)`, `regel8 = _pruefe_regel8(...)` calls alongside the existing `regel1`/`regel3` calls, following the exact same local-variable-then-aggregate pattern already there.

---

### `pipeline/03_produktinfos.py`, `pipeline/04_investitionen.py` (CLI entrypoints)

**Analog:** `pipeline/02_plaene_extrahieren.py` (full file, reproduced above).

**Full pattern to copy verbatim, substituting module names:**
```python
"""Pipeline-Schritt 02: Pläne extrahieren (Spez. 5.4).

Dünner typer-Einstieg; die Logik liegt in `ostbevern.plaene`.
"""

from __future__ import annotations

from typing import Annotated

import typer

from ostbevern.konfiguration import PROJEKT_WURZEL, STANDARD_JAHR, KonfigurationsFehler, lade_jahrgang
from ostbevern.pdf import PdfFehler
from ostbevern.plaene import PlaeneFehler, extrahiere_plaene
from ostbevern.schema import SchemaFehler

app = typer.Typer(add_completion=False, help="...")

@app.command()
def main(jahr: Annotated[int, typer.Option("--jahr", help="...")] = STANDARD_JAHR) -> None:
    try:
        jahrgang = lade_jahrgang(jahr)
        ergebnisse = extrahiere_plaene(jahrgang)
    except (KonfigurationsFehler, PdfFehler, PlaeneFehler, SchemaFehler) as fehler:
        typer.echo(f"Fehler: {fehler}", err=True)
        raise typer.Exit(code=1) from fehler

    for ergebnis in ergebnisse:
        pfad_relativ = ergebnis.pfad.relative_to(PROJEKT_WURZEL)
        typer.echo(f"{ergebnis.zeilen_geschrieben} Zeilen geschrieben: {pfad_relativ}")

if __name__ == "__main__":
    app()
```
`03_produktinfos.py` catches `(KonfigurationsFehler, PdfFehler, ProdukteFehler, SchemaFehler)` and calls `ostbevern.produkte.extrahiere_produkte`; `04_investitionen.py` catches `InvestitionenFehler` and calls `ostbevern.investitionen.extrahiere_investitionen`.

---

### Test files

**Analog:** `pipeline/tests/test_plaene.py` (header + fixture pattern reproduced above).

**Header/no-literals convention** (lines 1-20):
```python
"""Tests für ostbevern.plaene: Gesamtergebnisplan-Extraktion aus echten PDF-Seiten (D-07).

Liest nur das Original-PDF, nie daten/. Keine Jahrgangs-, Seiten- oder
Sollwert-Literale – alles kommt aus lade_jahrgang(STANDARD_JAHR) bzw.
lade_sollwerte(STANDARD_JAHR).
"""
from __future__ import annotations
...
from ostbevern.konfiguration import STANDARD_JAHR, Jahrgang, lade_jahrgang, lade_sollwerte
from ostbevern.pdf import PdfDokument, Textzeile
from ostbevern.plaene import PlaeneFehler, lies_abschnitte, lies_plantabelle, lies_teilplaene
from ostbevern.schema import SEITEN_SPALTEN, zerlege_spaltenkopf
from ostbevern.seiten import baue_hierarchie, klassifiziere_dokument
from ostbevern.zeilen import ZEILEN, plantyp_fuer
```
All new integration tests (`test_produkte.py`, `test_investitionen.py`, `test_querschnitte.py`) must follow this exact no-hardcoded-page/year-literal convention: fixtures pull `STANDARD_JAHR`/`lade_jahrgang`/`lade_sollwerte`, open the real PDF via `PdfDokument.oeffne`, and never read from `daten/`. `test_freitext.py` follows `tests/test_zahlen.py` instead (pure unit tests, no PDF fixture needed).

**Module-scoped fixture for expensive PDF reads** (lines 23-30): reuse `@pytest.fixture(scope="module")` to open/classify the PDF once per test module, exactly as `_alle_teilplaene` does.

---

## Shared Patterns

### Fail-fast error classes with PDF-page-prefixed messages
**Source:** `pipeline/ostbevern/plaene.py` `PlaeneFehler` (lines 38-39) and every `raise PlaeneFehler(f"S. {pdf_seite}: ...")` call site.
**Apply to:** `ProdukteFehler`, `InvestitionenFehler`, `QuerschnitteFehler` in all three new parser modules. Every raised message must start with `f"S. {pdf_seite}: "` or `f"S. {pdf_seite}, Zeile {zeilennummer}: "`.

### Central schema/IO — never hand-roll CSV writes
**Source:** `pipeline/ostbevern/schema.py` `schreibe_csv`/`lies_csv` (lines 72-92).
**Apply to:** every new CSV in this phase. New `*_SPALTEN` dict + thin `schreibe_*_csv`/`lies_*_csv` wrapper, no direct `df.write_csv()` calls outside `schema.py`.

### Deutsches Zahlenformat
**Source:** `pipeline/ostbevern/zahlen.py` `lies_betrag`/`ist_betrag`/`trenne_angeklebten_betrag`/`trenne_operator`.
**Apply to:** `produkte.py` (Grundzahlen, Erläuterungsposten-Beträge), `investitionen.py` (7-column amounts, Kassenwirksamkeit-Werte), `querschnitte.py` (Kennzahl-Beträge). Import directly, never reimplement.

### Multi-block-per-page scanning via state-machine with `schliesse()` closure
**Source:** `pipeline/ostbevern/plaene.py` `lies_abschnitte` (lines 80-158).
**Apply to:** Erläuterungsblock-Scanner in `produkte.py` (D-02/D-03), Maßnahmen-Header-Scanner in `investitionen.py` (D-08 Pitfall 2/8), and the Querschnitt-Block-per-PG scanner in `querschnitte.py`.

### x-Koordinaten-Zuordnung mit Toleranz
**Source:** `pipeline/ostbevern/plaene.py` `_ordne_werte` (lines 188-218).
**Apply to:** Investitions-Kontozeilen (7 Spalten), Kassenwirksamkeit-Zeile (3 Spalten, Pitfall 3), Grundzahlen-Jahreswerte, Querschnitt-Kennzahlen.

### CLI-Entrypoint-Shape (typer + try/except + Exit(1))
**Source:** `pipeline/02_plaene_extrahieren.py` (full file).
**Apply to:** `03_produktinfos.py`, `04_investitionen.py`, and the extension of `06_pruefen.py` to call `querschnitte.extrahiere_querschnitte` first.

### Regel-Funktion-Shape (Pruefpunkt + TOLERANZ_EURO + Regelergebnis)
**Source:** `pipeline/ostbevern/pruefung.py` `_pruefe_regel1`/`_pruefe_regel3` (lines 376-413, 515-553).
**Apply to:** `_pruefe_regel6`, `_pruefe_regel7`, `_pruefe_regel8`.

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `produkte.json` writer (inside `produkte.py`) | utility (JSON I/O) | file-I/O | No existing JSON output exists in the codebase — all prior outputs are CSV via `schema.py`. Planner should design a small dedicated function (deterministic key order, UTF-8, LF, atomic write) rather than reuse a CSV analog; no existing "atomic Markdown write" precedent in `pruefung.schreibe_konsistenzbericht` is close enough to be a true analog but is the nearest reference for "write deterministically, create parent dirs." |
| D-09 Datenschutz-Test (`test_keine_personennamen`) | test | file-I/O (filesystem scan) | No existing test scans the entire `daten/` tree for absence of a value; closest precedent is ordinary fixture-based assertion tests in `test_plaene.py`, but the recursive-directory-scan shape itself has no analog — Claude should write this as a new, small pytest helper (`for pfad in DATEN_WURZEL.rglob("*"): ...`). |

## Metadata

**Analog search scope:** `pipeline/ostbevern/`, `pipeline/*.py` (entrypoints), `pipeline/tests/`
**Files scanned:** `plaene.py`, `pdf.py`, `schema.py`, `pruefung.py`, `zahlen.py`, `zeilen.py` (partially), `02_plaene_extrahieren.py`, `test_plaene.py` (partially)
**Pattern extraction date:** 2026-10-01
