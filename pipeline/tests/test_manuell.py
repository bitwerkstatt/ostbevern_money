"""Tests für die manuellen Vorberichtstabellen (schema.py VORBERICHT_SPALTEN) und Regel 5
(ostbevern.pruefung._pruefe_regel5, MANU-01 bis MANU-04, MANU-07, PRUEF-05).

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
import pytest

from ostbevern.konfiguration import STANDARD_JAHR, lade_jahrgang
from ostbevern.pruefung import PruefungsFehler, pruefe_alles
from ostbevern.schema import (
    DATEN_WURZEL,
    KITA_ZUSCHUESSE_CSV,
    MANUELL_WURZEL,
    STEUERARTEN_CSV,
    TRANSFERAUFWENDUNGEN_CSV,
    ZUWENDUNGEN_CSV,
    lies_vorbericht_csv,
    schreibe_vorbericht_csv,
    zerlege_spaltenkopf,
)

_ALLE_VORBERICHT_CSVS = (
    STEUERARTEN_CSV,
    ZUWENDUNGEN_CSV,
    TRANSFERAUFWENDUNGEN_CSV,
    KITA_ZUSCHUESSE_CSV,
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


@pytest.mark.parametrize("pfad", _ALLE_VORBERICHT_CSVS, ids=lambda p: p.stem)
def test_schema_vorbericht_tabelle_kanonisch(pfad: Path, tmp_path: Path) -> None:
    df = lies_vorbericht_csv(DATEN_WURZEL / pfad)

    # Read -> rewrite -> byte-identical (schreibe_vorbericht_csv ist deterministisch, D-21).
    ziel = tmp_path / pfad.name
    schreibe_vorbericht_csv(df, ziel)
    assert ziel.read_bytes() == (DATEN_WURZEL / pfad).read_bytes()

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
    # kita_zuschuesse druckt nur das Haushaltsjahr (MANU-04): seine (jahr, wertart)-Menge ist
    # eine echte Teilmenge der Ergebnisplan-Spaltenköpfe, nicht deren vollständige Menge.
    assert tatsaechliche_jahre_wertarten <= erwartete_jahre_wertarten
    if pfad != KITA_ZUSCHUESSE_CSV:
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


def test_regel5_kita_gleich_transferposten(tmp_path: Path) -> None:
    _kopiere_daten_baum_nach(tmp_path)
    bericht = pruefe_alles(STANDARD_JAHR, daten_wurzel=tmp_path)
    regel5 = next(regel for regel in bericht.regeln if regel.regel == 5)
    assert regel5.status == "grün"
    treffer = [
        punkt
        for punkt in regel5.abweichungen
        if punkt.plan == "vorbericht_kita_zuschuesse" and punkt.zeile == "transfer_kita"
    ]
    assert treffer == []
    # Direkter Beleg, dass der Kita/Transfer-Kreuzvergleich tatsächlich lief (Plan 04-01
    # Task 1 kam ohne die drei neuen Tabellen nur auf 12 geprüfte Punkte).
    assert regel5.geprueft > 12


def test_regel5_kita_erkennt_abweichung(tmp_path: Path) -> None:
    _kopiere_daten_baum_nach(tmp_path)
    df = lies_vorbericht_csv(tmp_path / TRANSFERAUFWENDUNGEN_CSV)
    mutiert = _mutiere_betrag_teur(
        df, posten=("zuschuesse_kindertageseinrichtungen",), jahr=2026, delta=2
    )
    schreibe_vorbericht_csv(mutiert, tmp_path / TRANSFERAUFWENDUNGEN_CSV)

    bericht = pruefe_alles(STANDARD_JAHR, daten_wurzel=tmp_path)
    regel5 = next(regel for regel in bericht.regeln if regel.regel == 5)
    assert regel5.status == "rot"
    treffer = [
        punkt
        for punkt in regel5.abweichungen
        if punkt.plan == "vorbericht_kita_zuschuesse" and punkt.zeile == "transfer_kita"
    ]
    assert len(treffer) == 1
    assert treffer[0].abweichung == -2000


def test_regel5_weitergabe_kreis_land_gleich_tp_15() -> None:
    bericht = pruefe_alles(STANDARD_JAHR)
    regel5 = next(regel for regel in bericht.regeln if regel.regel == 5)
    assert regel5.status == "grün"
    treffer = [punkt for punkt in regel5.abweichungen if punkt.plan == "weitergabe_kreis_land"]
    assert treffer == []
    assert regel5.geprueft > 12


def test_regel5_weitergabe_erkennt_abweichung(tmp_path: Path) -> None:
    _kopiere_daten_baum_nach(tmp_path)
    df = lies_vorbericht_csv(tmp_path / TRANSFERAUFWENDUNGEN_CSV)
    mutiert = _mutiere_betrag_teur(df, posten=("kreisumlage",), jahr=STANDARD_JAHR, delta=4)
    schreibe_vorbericht_csv(mutiert, tmp_path / TRANSFERAUFWENDUNGEN_CSV)

    bericht = pruefe_alles(STANDARD_JAHR, daten_wurzel=tmp_path)
    regel5 = next(regel for regel in bericht.regeln if regel.regel == 5)
    assert regel5.status == "rot"
    treffer = [
        punkt
        for punkt in regel5.abweichungen
        if punkt.plan == "weitergabe_kreis_land" and punkt.jahr == STANDARD_JAHR
    ]
    assert len(treffer) == 1
    assert treffer[0].zeile == "tp_15"
    assert treffer[0].ebene == "P"


def test_regel5_weitergabe_fehlender_posten_bricht_ab(tmp_path: Path) -> None:
    _kopiere_daten_baum_nach(tmp_path)
    df = lies_vorbericht_csv(tmp_path / TRANSFERAUFWENDUNGEN_CSV)
    ohne_kreisumlage = df.filter(pl.col("posten") != "kreisumlage")
    schreibe_vorbericht_csv(ohne_kreisumlage, tmp_path / TRANSFERAUFWENDUNGEN_CSV)

    with pytest.raises(PruefungsFehler):
        pruefe_alles(STANDARD_JAHR, daten_wurzel=tmp_path)


def test_readme_nennt_jede_manuelle_datei() -> None:
    readme = (DATEN_WURZEL / MANUELL_WURZEL / "README.md").read_text(encoding="utf-8")
    dateien = sorted(
        pfad.name
        for pfad in (DATEN_WURZEL / MANUELL_WURZEL).iterdir()
        if pfad.is_file() and pfad.name not in ("README.md", ".gitkeep")
    )
    assert dateien
    for datei in dateien:
        assert datei in readme, f"README.md erwähnt {datei} nicht"
