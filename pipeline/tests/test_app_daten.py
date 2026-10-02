"""Tests für ostbevern.app_daten: Schritt 07, App-JSON-Erzeugung (D-21, D-24).

Erzeugt `haushalt.json` ausschließlich in tmp-Verzeichnisse (nie in das eingecheckte
`app/src/data/`, D-06-Stil); eine Ausnahme ist `test_haushalt_json_eingecheckt_aktuell`,
die das neu erzeugte tmp-Ergebnis gegen die eingecheckte Datei vergleicht, ohne sie zu
überschreiben.

PRIVACY (D-09): Dieses Modul liest nie einen Personennamen in eine Variable, die auf dem
Bildschirm/in Testausgaben erscheinen könnte, außer über `lies_personennamen` selbst,
deren Ergebnis ausschließlich in Mengenvergleiche einfließt (wie test_produkte.py).
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import polars as pl
import pytest

from ostbevern import app_daten
from ostbevern.app_daten import APP_DATEN_WURZEL, HAUSHALT_JSON, erzeuge_app_daten
from ostbevern.konfiguration import STANDARD_JAHR, Jahrgang
from ostbevern.pdf import PdfDokument
from ostbevern.produkte import lies_personennamen
from ostbevern.pruefung import Planwerte
from ostbevern.schema import (
    DATEN_WURZEL,
    ERGEBNISPLAN_CSV,
    HIERARCHIE_CSV,
    SEITEN_CSV,
    STEUERARTEN_CSV,
    lies_hierarchie_csv,
    lies_plan_csv,
    lies_seiten_csv,
    lies_vorbericht_csv,
)


@pytest.fixture(scope="module")
def kontext() -> tuple[pl.DataFrame, pl.DataFrame]:
    seiten = lies_seiten_csv(DATEN_WURZEL / SEITEN_CSV)
    hierarchie = lies_hierarchie_csv(DATEN_WURZEL / HIERARCHIE_CSV)
    return seiten, hierarchie


def test_haushalt_json_steuerarten_aus_manueller_tabelle(tmp_path: Path) -> None:
    app_daten_wurzel = tmp_path / "app"
    pfade = erzeuge_app_daten(STANDARD_JAHR, app_daten_wurzel=app_daten_wurzel)
    assert pfade == [app_daten_wurzel / HAUSHALT_JSON]

    daten = json.loads((app_daten_wurzel / HAUSHALT_JSON).read_text(encoding="utf-8"))
    steuerarten = daten["vorbericht"]["steuerarten"]
    jahre = daten["jahre"]
    wertarten = daten["wertarten"]

    df = lies_vorbericht_csv(DATEN_WURZEL / STEUERARTEN_CSV)
    for posten_eintrag in steuerarten["posten"]:
        zeilen = df.filter(pl.col("posten") == posten_eintrag["posten"])
        assert posten_eintrag["gerundet"] is True
        assert posten_eintrag["berechnet"] is False
        for index, jahr in enumerate(jahre):
            zeile = zeilen.filter(pl.col("jahr") == jahr)
            assert zeile.height == 1
            assert posten_eintrag["werte"][index] == zeile["betrag_teur"][0] * 1000

    ergebnisplan = lies_plan_csv(DATEN_WURZEL / ERGEBNISPLAN_CSV)
    planwerte = Planwerte(ergebnisplan, datei="ergebnisplan")
    erwarteter_gesamt_plan = [
        planwerte.wert("GESAMT", "", "01", jahr, wertart)
        for jahr, wertart in zip(jahre, wertarten, strict=True)
    ]
    assert steuerarten["gesamt_plan"] == erwarteter_gesamt_plan
    assert steuerarten["planzeile"] == "steuern"


def test_app_json_deterministisch(tmp_path: Path) -> None:
    ziel_a = tmp_path / "a"
    ziel_b = tmp_path / "b"
    erzeuge_app_daten(STANDARD_JAHR, app_daten_wurzel=ziel_a)
    erzeuge_app_daten(STANDARD_JAHR, app_daten_wurzel=ziel_b)

    inhalt_a = (ziel_a / HAUSHALT_JSON).read_bytes()
    inhalt_b = (ziel_b / HAUSHALT_JSON).read_bytes()
    assert inhalt_a == inhalt_b

    text = inhalt_a.decode("utf-8")
    assert text.endswith("\n")
    assert "\r" not in text


def test_haushalt_json_eingecheckt_aktuell(tmp_path: Path) -> None:
    erzeuge_app_daten(STANDARD_JAHR, app_daten_wurzel=tmp_path)
    neu = (tmp_path / HAUSHALT_JSON).read_bytes()
    eingecheckt = (APP_DATEN_WURZEL / HAUSHALT_JSON).read_bytes()
    assert neu == eingecheckt


def test_keine_personennamen_in_app_daten(
    jahrgang: Jahrgang, kontext: tuple[pl.DataFrame, pl.DataFrame]
) -> None:
    seiten, hierarchie = kontext
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        namen = lies_personennamen(dokument, jahrgang, seiten, hierarchie)

    nadeln: set[str] = set()
    for _seite, text in namen:
        nadeln.add(text)
        nadeln.add("".join(text.split()))

    treffer: list[str] = []
    for pfad in APP_DATEN_WURZEL.rglob("*.json"):
        inhalt = pfad.read_text(encoding="utf-8")
        for nadel in nadeln:
            if nadel and nadel in inhalt:
                treffer.append(str(pfad.relative_to(APP_DATEN_WURZEL)))
    assert treffer == []


def test_app_daten_liest_kein_pdf() -> None:
    quelle = Path(app_daten.__file__).read_text(encoding="utf-8")
    baum = ast.parse(quelle)
    module_namen: set[str] = set()
    for knoten in ast.walk(baum):
        if isinstance(knoten, ast.Import):
            module_namen.update(alias.name for alias in knoten.names)
        elif isinstance(knoten, ast.ImportFrom) and knoten.module:
            module_namen.add(knoten.module)
    verbotene = {"pdfplumber", "ostbevern.pdf"}
    assert not (module_namen & verbotene)
