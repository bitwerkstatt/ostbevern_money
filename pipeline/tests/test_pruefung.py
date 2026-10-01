"""Tests für ostbevern.pruefung: liest nur eingecheckte CSVs, nie das PDF (D-06).

Keine Jahrgangs-, Seiten- oder Sollwert-Literale; Werte kommen aus lade_sollwerte
oder werden aus den eingecheckten Dateien abgeleitet.
"""

from __future__ import annotations

from pathlib import Path

import polars as pl
import pytest

from ostbevern.konfiguration import JAHRGAENGE_VERZEICHNIS, STANDARD_JAHR, lade_sollwerte
from ostbevern.pruefung import (
    SATZUNG_FORMELN,
    TOLERANZ_EURO,
    PruefungsFehler,
    pruefe_alles,
    rendere_konsistenzbericht,
    schreibe_konsistenzbericht,
)
from ostbevern.schema import (
    DATEN_WURZEL,
    ERGEBNISPLAN_CSV,
    FINANZPLAN_CSV,
    KONSISTENZ_MD,
    lies_plan_csv,
    schreibe_plan_csv,
)


def _kopiere_finanzplan_nach(tmp_path: Path) -> None:
    """Kopiert die eingecheckte finanzplan.csv unverändert in den tmp-Datenbaum (D-06)."""
    finanzplan = lies_plan_csv(DATEN_WURZEL / FINANZPLAN_CSV)
    schreibe_plan_csv(finanzplan, tmp_path / FINANZPLAN_CSV)


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


def _erwartete_anzahl_regel4(sollwerte: dict) -> int:
    gesamtergebnisplan = sollwerte["gesamtergebnisplan"]
    b1 = len(gesamtergebnisplan["zeilen"]) * len(gesamtergebnisplan["jahre"])
    gesamtfinanzplan = sollwerte["gesamtfinanzplan"]
    b2 = len(gesamtfinanzplan.get("ansatz", {})) + len(gesamtfinanzplan.get("ve", {}))
    satzung = len(sollwerte["satzung"]) - 1  # ohne pdf_seite
    return b1 + b2 + satzung


def test_regel4_sollwerte_gesamtergebnisplan_gruen() -> None:
    bericht = pruefe_alles(STANDARD_JAHR)
    regel4 = next(regel for regel in bericht.regeln if regel.regel == 4)

    sollwerte = lade_sollwerte(STANDARD_JAHR)

    assert regel4.geprueft == _erwartete_anzahl_regel4(sollwerte)
    assert regel4.status == "grün"
    assert regel4.abweichungen == ()


def test_regel4_sollwerte_gesamtfinanzplan_und_satzung_gruen() -> None:
    bericht = pruefe_alles(STANDARD_JAHR)
    regel4 = next(regel for regel in bericht.regeln if regel.regel == 4)
    assert regel4.status == "grün"
    assert regel4.abweichungen == ()

    sollwerte = lade_sollwerte(STANDARD_JAHR)
    haushaltsjahr = sollwerte["haushaltsjahr"]
    finanzplan = lies_plan_csv(DATEN_WURZEL / FINANZPLAN_CSV)
    ergebnisplan = lies_plan_csv(DATEN_WURZEL / ERGEBNISPLAN_CSV)

    def _wert(df: pl.DataFrame, *, zeile: str, wertart: str) -> int:
        treffer = df.filter(
            (pl.col("ebene") == "GESAMT")
            & (pl.col("zeile") == zeile)
            & (pl.col("jahr") == haushaltsjahr)
            & (pl.col("wertart") == wertart)
        )
        return treffer["betrag"][0]

    gesamtfinanzplan = sollwerte["gesamtfinanzplan"]
    for wertart in ("ansatz", "ve"):
        for zeile, soll in gesamtfinanzplan.get(wertart, {}).items():
            assert _wert(finanzplan, zeile=zeile, wertart=wertart) == soll

    quellen = {"ergebnisplan": ergebnisplan, "finanzplan": finanzplan}
    for schluessel, (datei, wertart, komponenten) in SATZUNG_FORMELN.items():
        ist = sum(
            vorzeichen * _wert(quellen[datei], zeile=zeile, wertart=wertart)
            for vorzeichen, zeile in komponenten
        )
        assert ist == sollwerte["satzung"][schluessel]


def test_regel4_satzung_ohne_formel_bricht_ab(tmp_path: Path) -> None:
    quelle_pfad = JAHRGAENGE_VERZEICHNIS / f"{STANDARD_JAHR}_sollwerte.toml"
    text = quelle_pfad.read_text(encoding="utf-8")
    markierung = "verpflichtungsermaechtigungen = 11600000\n"
    assert markierung in text
    text = text.replace(markierung, markierung + "neuer_schluessel_ohne_formel = 1\n")
    ziel_pfad = tmp_path / f"{STANDARD_JAHR}_sollwerte.toml"
    ziel_pfad.write_text(text, encoding="utf-8")

    with pytest.raises(PruefungsFehler, match="neuer_schluessel_ohne_formel"):
        pruefe_alles(STANDARD_JAHR, sollwerte_verzeichnis=tmp_path)


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
    _kopiere_finanzplan_nach(tmp_path)

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
    _kopiere_finanzplan_nach(tmp_path)

    bericht = pruefe_alles(STANDARD_JAHR, daten_wurzel=tmp_path)
    regel4 = next(regel for regel in bericht.regeln if regel.regel == 4)

    assert regel4.status == "grün"
    assert regel4.abweichungen == ()
