"""Tests für ostbevern.schema.schreibe_csv: Round-Trip-Prüfung bei Float->Int-Narrowing.

`strict=True` auf dem zentralen `.cast()` in `schreibe_csv` erkennt Overflow/NaN/
unparsable Input, aber KEINE Nachkommastellen-Truncation bei Float->Int (verifiziert
gegen polars>=1.44.2, 03-REVIEW.md CR-01). Diese Tests belegen, dass die zusätzliche
Round-Trip-Prüfung genau diese Lücke schließt, ohne gültige Ganzzahl-Werte abzulehnen.
"""

from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest

from ostbevern.schema import SchemaFehler, schreibe_csv

_SPALTEN: dict[str, pl.PolarsDataType] = {"code": pl.Utf8, "betrag": pl.Int64}


def test_schreibe_csv_lehnt_fraktionalen_float_bei_int_narrowing_ab(tmp_path: Path) -> None:
    df = pl.DataFrame({"code": ["01"], "betrag": [1234.5]})
    pfad = tmp_path / "betrag.csv"
    with pytest.raises(SchemaFehler, match="betrag"):
        schreibe_csv(df, pfad, _SPALTEN, ["code"])
    assert not pfad.exists()


def test_schreibe_csv_schreibt_ganzzahligen_float_bei_int_narrowing(tmp_path: Path) -> None:
    df = pl.DataFrame({"code": ["01"], "betrag": [1234.0]})
    pfad = tmp_path / "betrag.csv"
    schreibe_csv(df, pfad, _SPALTEN, ["code"])
    geschrieben = pl.read_csv(pfad, schema_overrides=_SPALTEN)
    assert geschrieben["betrag"].to_list() == [1234]
