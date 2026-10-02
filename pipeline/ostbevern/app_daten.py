"""Schritt 07: deterministische App-JSON-Erzeugung (D-21, D-24).

Liest ausschließlich bereits generierte Dateien unter `daten/` (CSVs), nie das
Haushalts-PDF (D-06) — die Weitergabe an die App ist eine reine Datentransformation.
Schreibt `app/src/data/haushalt.json` atomar und deterministisch (fester
Schlüsselreihenfolge, UTF-8 ohne BOM, LF, abschließendem Zeilenumbruch), nach demselben
Muster wie `ostbevern.schema.schreibe_produkte_json` (Research Pattern 4).
"""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Mapping
from pathlib import Path

import polars as pl

from ostbevern.konfiguration import PROJEKT_WURZEL, lade_jahrgang
from ostbevern.pruefung import REGEL5_GEP_ZEILEN, Planwerte
from ostbevern.schema import (
    DATEN_WURZEL,
    ERGEBNISPLAN_CSV,
    STEUERARTEN_CSV,
    lies_plan_csv,
    lies_vorbericht_csv,
    zerlege_spaltenkopf,
)
from ostbevern.zeilen import ZEILEN


class AppDatenFehler(ValueError):
    """Wird ausgelöst, wenn die Eingabedaten für die App-JSON-Erzeugung inkonsistent sind."""


APP_DATEN_WURZEL = PROJEKT_WURZEL / "app" / "src" / "data"
HAUSHALT_JSON = Path("haushalt.json")


def schreibe_app_json(daten: Mapping[str, object], pfad: Path, *, praefix: str) -> None:
    """Schreibt `daten` atomar nach `pfad` (D-24): tempfile + os.replace, UTF-8 ohne BOM,
    LF, feste Schlüsselreihenfolge (Einfügereihenfolge der übergebenen dicts), mit
    abschließendem Zeilenumbruch — dasselbe Muster wie `schema.schreibe_produkte_json`."""
    inhalt = json.dumps(daten, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    pfad.parent.mkdir(parents=True, exist_ok=True)
    deskriptor, temp_pfad_str = tempfile.mkstemp(
        dir=pfad.parent, prefix=f".{praefix}-", suffix=".tmp"
    )
    temp_pfad = Path(temp_pfad_str)
    try:
        with os.fdopen(deskriptor, "w", encoding="utf-8", newline="\n") as datei:
            datei.write(inhalt)
        os.replace(temp_pfad, pfad)
    finally:
        temp_pfad.unlink(missing_ok=True)


def baue_vorbericht_tabelle(
    df: pl.DataFrame,
    *,
    jahre: list[int],
    planwerte: Planwerte,
    gep_zeile: str | None,
) -> dict[str, object]:
    """Baut die App-JSON-Struktur einer manuellen Vorberichtstabelle (D-02, D-21).

    `gesamt_plan` ist die eurogenaue GEP-Zeile (D-01), `gesamt_vorbericht` die gedruckte,
    nur in T€ geführte Gesamtzeile × 1000 (als `gerundet` gekennzeichnet). Jeder Posten
    trägt seine Werte × 1000, ebenfalls `gerundet: true`, `berechnet: false` (D-02, D-10).
    Fehlt für ein Jahr aus `jahre` eine Gesamtzeile, oder gibt es mehr als eine je Jahr,
    bricht die Funktion mit `AppDatenFehler` ab (inkonsistente Eingabedaten).
    """
    tabelle = df["tabelle"][0]
    gesamt_df = df.filter(pl.col("ist_gesamt"))
    gesamt_nach_jahr = {zeile["jahr"]: zeile for zeile in gesamt_df.iter_rows(named=True)}
    if len(gesamt_nach_jahr) != gesamt_df.height:
        raise AppDatenFehler(f"{tabelle}: mehrere Gesamtzeilen für dasselbe Jahr")

    gesamt_werte: list[int] = []
    gesamt_quelle: int | None = None
    for jahr in jahre:
        zeile = gesamt_nach_jahr.get(jahr)
        if zeile is None:
            raise AppDatenFehler(f"{tabelle}: keine Gesamtzeile für Jahr {jahr}")
        gesamt_werte.append(zeile["betrag_teur"] * 1000)
        gesamt_quelle = zeile["quelle"]

    if gep_zeile is not None:
        planzeile = ZEILEN["gesamtergebnisplan"][gep_zeile].kanonisch
        gesamt_plan: list[int] | None = [
            planwerte.wert("GESAMT", "", gep_zeile, jahr, gesamt_nach_jahr[jahr]["wertart"])
            for jahr in jahre
        ]
    else:
        planzeile = None
        gesamt_plan = None

    posten_df = df.filter(~pl.col("ist_gesamt"))
    positionen = sorted(posten_df["position"].unique().to_list())
    posten_liste: list[dict[str, object]] = []
    for position in positionen:
        teil = posten_df.filter(pl.col("position") == position)
        name = teil["posten_name"][0]
        posten_schluessel = teil["posten"][0]
        zeilen_nach_jahr = {zeile["jahr"]: zeile for zeile in teil.iter_rows(named=True)}
        if len(zeilen_nach_jahr) != teil.height:
            raise AppDatenFehler(
                f"{tabelle}: Posten {posten_schluessel!r} hat mehrere Zeilen für dasselbe Jahr"
            )

        werte: list[int | None] = []
        quelle: int | None = None
        anmerkung: str | None = None
        for jahr in jahre:
            zeile = zeilen_nach_jahr.get(jahr)
            if zeile is None:
                werte.append(None)
                continue
            werte.append(zeile["betrag_teur"] * 1000)
            quelle = zeile["quelle"]
            anmerkung = zeile["anmerkung"]

        posten_liste.append(
            {
                "posten": posten_schluessel,
                "name": name,
                "werte": werte,
                "gerundet": True,
                "berechnet": False,
                "quelle": quelle,
                "anmerkung": anmerkung,
            }
        )

    return {
        "tabelle": tabelle,
        "quelle_einheit": "teur",
        "planzeile": planzeile,
        "gesamt_plan": gesamt_plan,
        "gesamt_vorbericht": {
            "werte": gesamt_werte,
            "gerundet": True,
            "quelle": gesamt_quelle,
        },
        "posten": posten_liste,
    }


def erzeuge_app_daten(
    jahr: int,
    *,
    daten_wurzel: Path = DATEN_WURZEL,
    app_daten_wurzel: Path = APP_DATEN_WURZEL,
) -> list[Path]:
    """Schritt 07 (D-21, D-24): baut `app/src/data/haushalt.json` aus `daten/` auf.

    Liest nur CSVs unter `daten_wurzel` (nie das PDF, D-06). `jahre`/`wertarten` kommen
    aus den Ergebnisplan-Spaltenköpfen des Jahrgangs (D-21), nie hartkodiert.
    """
    jahrgang = lade_jahrgang(jahr)
    ergebnisplan = lies_plan_csv(daten_wurzel / ERGEBNISPLAN_CSV)
    planwerte = Planwerte(ergebnisplan, datei="ergebnisplan")

    spalten_zu_wertart = [zerlege_spaltenkopf(kopf) for kopf in jahrgang.spalten["ergebnisplan"]]
    jahre = [jahr_wert for _wertart, jahr_wert in spalten_zu_wertart]
    wertarten = [wertart for wertart, _jahr_wert in spalten_zu_wertart]

    vorbericht_quellen = {"steuerarten": lies_vorbericht_csv(daten_wurzel / STEUERARTEN_CSV)}
    vorbericht = {
        tabelle: baue_vorbericht_tabelle(
            df, jahre=jahre, planwerte=planwerte, gep_zeile=REGEL5_GEP_ZEILEN.get(tabelle)
        )
        for tabelle, df in vorbericht_quellen.items()
    }

    daten = {
        "haushaltsjahr": jahrgang.haushaltsjahr,
        "jahre": jahre,
        "wertarten": wertarten,
        "vorbericht": vorbericht,
    }

    pfad = app_daten_wurzel / HAUSHALT_JSON
    schreibe_app_json(daten, pfad, praefix="haushalt")
    return [pfad]
