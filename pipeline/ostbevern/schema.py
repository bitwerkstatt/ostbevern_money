"""Zentrales CSV-Schema und -IO für alle generierten Dateien unter daten/ (D-21, D-22).

Schreiben und Lesen laufen ausschließlich über dieses Modul, auch in den Tests. So
wird z. B. der Code "01" nie als Zahl 1 interpretiert.
"""

from __future__ import annotations

from pathlib import Path

import polars as pl

from ostbevern.konfiguration import PROJEKT_WURZEL

DATEN_WURZEL = PROJEKT_WURZEL / "daten"

SEITEN_CSV = Path("zwischen/seiten.csv")
HIERARCHIE_CSV = Path("aufbereitet/hierarchie.csv")
ERGEBNISPLAN_CSV = Path("aufbereitet/ergebnisplan.csv")
FINANZPLAN_CSV = Path("aufbereitet/finanzplan.csv")
KONSISTENZ_MD = Path("pruefberichte/konsistenz.md")
BEFUNDE_MD = Path("pruefberichte/befunde.md")


class SchemaFehler(ValueError):
    """Wird ausgelöst, wenn eine CSV-Datei nicht dem zentralen Schema entspricht."""


EBENEN = ("GESAMT", "PB", "PG", "P")
WERTARTEN = ("ergebnis", "ansatz", "ve", "planung")

_EBENEN_RANG = {ebene: rang for rang, ebene in enumerate(EBENEN)}
_WERTART_LABEL = {"Ergebnis": "ergebnis", "Ansatz": "ansatz", "VE": "ve", "Planung": "planung"}


def zerlege_spaltenkopf(kopf: str) -> tuple[str, int]:
    """Zerlegt einen Spaltenkopf wie "Ergebnis 2024" in (wertart, jahr)."""
    teile = kopf.split()
    if len(teile) != 2 or teile[0] not in _WERTART_LABEL or not teile[1].isdigit():
        raise SchemaFehler(f"Unbekannter Spaltenkopf: {kopf!r}")
    return _WERTART_LABEL[teile[0]], int(teile[1])


PLAN_SPALTEN: dict[str, pl.PolarsDataType] = {
    "ebene": pl.Utf8,
    "code": pl.Utf8,
    "synthetisch": pl.Boolean,
    "zeile": pl.Utf8,
    "zeile_kanonisch": pl.Utf8,
    "zeile_name": pl.Utf8,
    "operator": pl.Utf8,
    "ist_summe": pl.Boolean,
    "jahr": pl.Int64,
    "wertart": pl.Utf8,
    "betrag": pl.Int64,
    "pdf_seite": pl.Int64,
}


def _pruefe_keine_leeren_strings(
    df: pl.DataFrame, spalten: dict[str, pl.PolarsDataType], pfad: Path
) -> None:
    for name, dtype in spalten.items():
        if dtype == pl.Utf8 and name in df.columns:
            leer = df.filter(pl.col(name) == "")
            if leer.height > 0:
                raise SchemaFehler(
                    f"{pfad}: Spalte {name!r} enthält leere Strings; kein Wert ist null, nicht ''"
                )


def schreibe_csv(
    df: pl.DataFrame,
    pfad: Path,
    spalten: dict[str, pl.PolarsDataType],
    sortierung: list[str],
) -> None:
    """Schreibt `df` nach `pfad` in fester Spaltenreihenfolge, UTF-8 ohne BOM, LF (D-21)."""
    _pruefe_keine_leeren_strings(df, spalten, pfad)
    sortiert = df.sort(sortierung, nulls_last=False)
    geordnet = sortiert.select(list(spalten.keys())).cast(spalten)
    pfad.parent.mkdir(parents=True, exist_ok=True)
    geordnet.write_csv(pfad)


def lies_csv(pfad: Path, spalten: dict[str, pl.PolarsDataType]) -> pl.DataFrame:
    """Liest `pfad` mit festem Schema; lehnt eine abweichende Kopfzeile ab (D-22)."""
    df = pl.read_csv(pfad, schema_overrides=spalten)
    erwartet = list(spalten.keys())
    if df.columns != erwartet:
        raise SchemaFehler(f"{pfad}: Kopfzeile {df.columns} weicht vom Schema {erwartet} ab")
    return df


def schreibe_plan_csv(df: pl.DataFrame, pfad: Path) -> None:
    """Schreibt eine Plan-CSV sortiert nach (Ebenenrang, Code, Zeile, Jahr, Wertart)."""
    mit_rang = df.with_columns(
        pl.col("ebene").replace_strict(_EBENEN_RANG, return_dtype=pl.Int64).alias("_ebenenrang")
    )
    schreibe_csv(mit_rang, pfad, PLAN_SPALTEN, ["_ebenenrang", "code", "zeile", "jahr", "wertart"])


def lies_plan_csv(pfad: Path) -> pl.DataFrame:
    """Liest eine Plan-CSV über `lies_csv` mit PLAN_SPALTEN."""
    return lies_csv(pfad, PLAN_SPALTEN)


SEITEN_SPALTEN: dict[str, pl.PolarsDataType] = {
    "pdf_seite": pl.Int64,
    "typ": pl.Utf8,
    "pb": pl.Utf8,
    "pg": pl.Utf8,
    "produkt": pl.Utf8,
}


def schreibe_seiten_csv(df: pl.DataFrame, pfad: Path) -> None:
    """Schreibt seiten.csv sortiert nach pdf_seite (D-16, D-17, D-21)."""
    schreibe_csv(df, pfad, SEITEN_SPALTEN, ["pdf_seite"])


def lies_seiten_csv(pfad: Path) -> pl.DataFrame:
    """Liest seiten.csv über `lies_csv` mit SEITEN_SPALTEN."""
    return lies_csv(pfad, SEITEN_SPALTEN)
