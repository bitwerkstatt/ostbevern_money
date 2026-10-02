"""Tests für die manuellen Vorberichtstabellen (schema.py VORBERICHT_SPALTEN) und Regel 5
(ostbevern.pruefung._pruefe_regel5, MANU-01, PRUEF-05).

Keine Jahrgangs-, Seiten- oder Sollwert-Literale; Werte kommen aus `lade_jahrgang`,
`lade_sollwerte` oder werden aus den eingecheckten CSVs abgeleitet (D-06). Mutationstests
kopieren den gesamten `daten/`-Baum in ein tmp-Verzeichnis und ändern dort gezielt eine
einzelne manuelle Tabelle, damit `pruefe_alles` weiterhin alle übrigen Eingabedateien
konsistent vorfindet (derselbe Huckepack-Mechanismus wie in test_pruefung.py).
"""

from __future__ import annotations

import shutil
from pathlib import Path

import polars as pl

from ostbevern.konfiguration import STANDARD_JAHR, lade_jahrgang
from ostbevern.pruefung import pruefe_alles
from ostbevern.schema import (
    DATEN_WURZEL,
    STEUERARTEN_CSV,
    lies_vorbericht_csv,
    schreibe_vorbericht_csv,
    zerlege_spaltenkopf,
)


def _kopiere_daten_baum_nach(tmp_path: Path) -> None:
    """Kopiert den gesamten eingecheckten `daten/`-Baum unverändert nach `tmp_path` (D-06):
    einfachste Grundlage für Mutationstests, die anschließend gezielt eine einzelne
    manuelle Tabelle ändern, ohne jede von `pruefe_alles` gelesene Datei einzeln
    aufzuzählen."""
    shutil.copytree(DATEN_WURZEL, tmp_path, dirs_exist_ok=True)


def _mutiere_betrag_teur(
    df: pl.DataFrame, *, posten: tuple[str, ...], jahr: int, delta: int
) -> pl.DataFrame:
    bedingung = pl.col("posten").is_in(posten) & (pl.col("jahr") == jahr)
    return df.with_columns(
        pl.when(bedingung)
        .then(pl.col("betrag_teur") + delta)
        .otherwise(pl.col("betrag_teur"))
        .alias("betrag_teur")
    )


def test_schema_steuerarten_kanonisch(tmp_path: Path) -> None:
    df = lies_vorbericht_csv(DATEN_WURZEL / STEUERARTEN_CSV)

    # Read -> rewrite -> byte-identical (schreibe_vorbericht_csv ist deterministisch, D-21).
    ziel = tmp_path / "steuerarten.csv"
    schreibe_vorbericht_csv(df, ziel)
    assert ziel.read_bytes() == (DATEN_WURZEL / STEUERARTEN_CSV).read_bytes()

    assert (df["quelle"] >= 1).all()

    gesamt_je_jahr = df.filter(pl.col("ist_gesamt")).group_by("jahr").agg(pl.len().alias("n"))
    assert (gesamt_je_jahr["n"] == 1).all()

    jahrgang = lade_jahrgang(STANDARD_JAHR)
    erwartete_jahre_wertarten = {
        (jahr, wertart)
        for wertart, jahr in (
            zerlege_spaltenkopf(kopf) for kopf in jahrgang.spalten["ergebnisplan"]
        )
    }
    tatsaechliche_jahre_wertarten = set(df.select(["jahr", "wertart"]).unique().iter_rows())
    assert tatsaechliche_jahre_wertarten == erwartete_jahre_wertarten


def test_regel5_gruen_auf_eingecheckten_daten() -> None:
    bericht = pruefe_alles(STANDARD_JAHR)
    regel5 = next(regel for regel in bericht.regeln if regel.regel == 5)
    assert regel5.status == "grün"
    assert regel5.abweichungen == ()
    assert regel5.geprueft > 0


def test_regel5_stufe_a_erkennt_tippfehler(tmp_path: Path) -> None:
    _kopiere_daten_baum_nach(tmp_path)
    df = lies_vorbericht_csv(tmp_path / STEUERARTEN_CSV)
    mutiert = _mutiere_betrag_teur(df, posten=("grundsteuer_a",), jahr=STANDARD_JAHR, delta=1)
    schreibe_vorbericht_csv(mutiert, tmp_path / STEUERARTEN_CSV)

    bericht = pruefe_alles(STANDARD_JAHR, daten_wurzel=tmp_path)
    regel5 = next(regel for regel in bericht.regeln if regel.regel == 5)
    assert regel5.status == "rot"
    treffer = [
        punkt
        for punkt in regel5.abweichungen
        if punkt.zeile == "summe_posten" and punkt.jahr == STANDARD_JAHR
    ]
    assert len(treffer) == 1
    assert treffer[0].abweichung == 1000


def test_regel5_stufe_b_toleriert_1000_euro(tmp_path: Path) -> None:
    # +1 T€ an Posten UND Gesamtzeile desselben Jahres: Stufe (a) bleibt exakt (beide
    # Seiten wandern gleich), Stufe (b) verschiebt sich um genau 1.000 € — die Grenze der
    # Toleranz (D-07b), noch kein Befund nötig.
    _kopiere_daten_baum_nach(tmp_path)
    df = lies_vorbericht_csv(tmp_path / STEUERARTEN_CSV)
    mutiert_1 = _mutiere_betrag_teur(
        df, posten=("grundsteuer_a", "gesamt"), jahr=STANDARD_JAHR, delta=1
    )
    schreibe_vorbericht_csv(mutiert_1, tmp_path / STEUERARTEN_CSV)

    bericht_1 = pruefe_alles(STANDARD_JAHR, daten_wurzel=tmp_path)
    regel5_1 = next(regel for regel in bericht_1.regeln if regel.regel == 5)
    assert regel5_1.status == "grün"

    # +2 T€ überschreitet die Toleranz: Regel 5 wird rot, mit einem Punkt auf gep_01.
    mutiert_2 = _mutiere_betrag_teur(
        df, posten=("grundsteuer_a", "gesamt"), jahr=STANDARD_JAHR, delta=2
    )
    schreibe_vorbericht_csv(mutiert_2, tmp_path / STEUERARTEN_CSV)

    bericht_2 = pruefe_alles(STANDARD_JAHR, daten_wurzel=tmp_path)
    regel5_2 = next(regel for regel in bericht_2.regeln if regel.regel == 5)
    assert regel5_2.status == "rot"
    treffer = [
        punkt
        for punkt in regel5_2.abweichungen
        if punkt.zeile == "gep_01" and punkt.jahr == STANDARD_JAHR
    ]
    assert len(treffer) == 1
