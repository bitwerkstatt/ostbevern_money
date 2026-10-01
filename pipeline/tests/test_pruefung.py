"""Tests für ostbevern.pruefung: liest nur eingecheckte CSVs, nie das PDF (D-06).

Keine Jahrgangs-, Seiten- oder Sollwert-Literale; Werte kommen aus lade_sollwerte
oder werden aus den eingecheckten Dateien abgeleitet.
"""

from __future__ import annotations

from pathlib import Path

import polars as pl

from ostbevern.konfiguration import STANDARD_JAHR, lade_sollwerte
from ostbevern.pruefung import (
    TOLERANZ_EURO,
    pruefe_alles,
    rendere_konsistenzbericht,
    schreibe_konsistenzbericht,
)
from ostbevern.schema import (
    DATEN_WURZEL,
    ERGEBNISPLAN_CSV,
    KONSISTENZ_MD,
    lies_plan_csv,
    schreibe_plan_csv,
)


def _manipuliere_betrag(df: pl.DataFrame, *, zeile: str, jahr: int, delta: int) -> pl.DataFrame:
    bedingung = (
        (pl.col("ebene") == "GESAMT") & (pl.col("zeile") == zeile) & (pl.col("jahr") == jahr)
    )
    return df.with_columns(
        pl.when(bedingung)
        .then(pl.col("betrag") + delta)
        .otherwise(pl.col("betrag"))
        .alias("betrag")
    )


def test_regel4_sollwerte_gesamtergebnisplan_gruen() -> None:
    bericht = pruefe_alles(STANDARD_JAHR)
    regel4 = next(regel for regel in bericht.regeln if regel.regel == 4)

    sollwerte = lade_sollwerte(STANDARD_JAHR)
    gesamtergebnisplan = sollwerte["gesamtergebnisplan"]
    erwartete_anzahl = len(gesamtergebnisplan["zeilen"]) * len(gesamtergebnisplan["jahre"])

    assert regel4.geprueft == erwartete_anzahl
    assert regel4.status == "grün"
    assert regel4.abweichungen == ()


def test_konsistenzbericht_wird_geschrieben() -> None:
    bericht = pruefe_alles(STANDARD_JAHR)
    pfad = schreibe_konsistenzbericht(bericht)

    assert pfad == DATEN_WURZEL / KONSISTENZ_MD
    inhalt = pfad.read_text(encoding="utf-8")
    assert inhalt == rendere_konsistenzbericht(bericht)
    for regel in bericht.regeln:
        assert regel.titel in inhalt


def test_konsistenzbericht_meldet_abweichung_ueber_einem_euro(tmp_path: Path) -> None:
    sollwerte = lade_sollwerte(STANDARD_JAHR)
    gesamtergebnisplan = sollwerte["gesamtergebnisplan"]
    zeile = next(iter(gesamtergebnisplan["zeilen"]))
    jahr = gesamtergebnisplan["jahre"][0]

    df = lies_plan_csv(DATEN_WURZEL / ERGEBNISPLAN_CSV)
    manipuliert = _manipuliere_betrag(df, zeile=zeile, jahr=jahr, delta=TOLERANZ_EURO + 1)
    schreibe_plan_csv(manipuliert, tmp_path / ERGEBNISPLAN_CSV)

    bericht = pruefe_alles(STANDARD_JAHR, daten_wurzel=tmp_path)
    regel4 = next(regel for regel in bericht.regeln if regel.regel == 4)

    assert regel4.status == "rot"
    assert len(regel4.abweichungen) == 1
    abweichung = regel4.abweichungen[0]
    assert abweichung.zeile == zeile
    assert abweichung.jahr == jahr
    assert abweichung.abweichung == TOLERANZ_EURO + 1


def test_konsistenzbericht_toleriert_einen_euro(tmp_path: Path) -> None:
    sollwerte = lade_sollwerte(STANDARD_JAHR)
    gesamtergebnisplan = sollwerte["gesamtergebnisplan"]
    zeile = next(iter(gesamtergebnisplan["zeilen"]))
    jahr = gesamtergebnisplan["jahre"][0]

    df = lies_plan_csv(DATEN_WURZEL / ERGEBNISPLAN_CSV)
    manipuliert = _manipuliere_betrag(df, zeile=zeile, jahr=jahr, delta=TOLERANZ_EURO)
    schreibe_plan_csv(manipuliert, tmp_path / ERGEBNISPLAN_CSV)

    bericht = pruefe_alles(STANDARD_JAHR, daten_wurzel=tmp_path)
    regel4 = next(regel for regel in bericht.regeln if regel.regel == 4)

    assert regel4.status == "grün"
    assert regel4.abweichungen == ()
