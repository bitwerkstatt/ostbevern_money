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
from ostbevern.manuell import lies_meta_json
from ostbevern.pruefung import (
    REGEL5_GEP_ZEILEN,
    REGEL5_TOLERANZ_GEP_EURO,
    Planwerte,
    zerlege_weitere_vorberichtstabellen,
)
from ostbevern.schema import (
    DATEN_WURZEL,
    EIGENKAPITAL_CSV,
    ERGEBNISPLAN_CSV,
    KITA_ZUSCHUESSE_CSV,
    META_JSON,
    STELLENPLAN_CSV,
    STEUERARTEN_CSV,
    TRANSFERAUFWENDUNGEN_CSV,
    WEITERE_VORBERICHTSTABELLEN_CSV,
    ZUWENDUNGEN_CSV,
    lies_eigenkapital_csv,
    lies_plan_csv,
    lies_stellenplan_csv,
    lies_vorbericht_csv,
    zerlege_spaltenkopf,
)
from ostbevern.zeilen import ZEILEN


class AppDatenFehler(ValueError):
    """Wird ausgelöst, wenn die Eingabedaten für die App-JSON-Erzeugung inkonsistent sind."""


APP_DATEN_WURZEL = PROJEKT_WURZEL / "app" / "src" / "data"
HAUSHALT_JSON = Path("haushalt.json")
STELLENPLAN_JSON = Path("stellenplan.json")


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
    sonstige: bool = False,
) -> dict[str, object]:
    """Baut die App-JSON-Struktur einer manuellen Vorberichtstabelle (D-02, D-21).

    `gesamt_plan` ist die eurogenaue GEP-Zeile (D-01), `gesamt_vorbericht` die gedruckte,
    nur in T€ geführte Gesamtzeile × 1000 (als `gerundet` gekennzeichnet). Jeder Posten
    trägt seine Werte × 1000, ebenfalls `gerundet: true`, `berechnet: false` (D-02, D-10).
    Eine Tabelle ohne `gep_zeile` (z. B. kita_zuschuesse) hat `planzeile`/`gesamt_plan`
    `null`; druckt sie nicht jedes Jahr aus `jahre` (MANU-04: nur das Haushaltsjahr), sind
    die fehlenden Jahre in `gesamt_vorbericht.werte` ebenfalls `null` — fehlt die
    Gesamtzeile für JEDES Jahr, bricht die Funktion mit `AppDatenFehler` ab.

    `sonstige=True` (nur zuwendungen, Spez. 3.8) hängt einen letzten, rein berechneten
    Posten "Sonstige" an: nicht-`null` genau in den Jahren, in denen die gedruckte
    Gesamtzeile um mehr als REGEL5_TOLERANZ_GEP_EURO von der GEP-Zeile abweicht, und dort
    so bemessen, dass Σ Posten + Sonstige exakt die GEP-Zeile ergibt (die Planzeile bleibt
    maßgeblich, D-07b).
    """
    tabelle = df["tabelle"][0]
    gesamt_df = df.filter(pl.col("ist_gesamt"))
    gesamt_nach_jahr = {zeile["jahr"]: zeile for zeile in gesamt_df.iter_rows(named=True)}
    if len(gesamt_nach_jahr) != gesamt_df.height:
        raise AppDatenFehler(f"{tabelle}: mehrere Gesamtzeilen für dasselbe Jahr")
    if not gesamt_nach_jahr:
        raise AppDatenFehler(f"{tabelle}: keine Gesamtzeile vorhanden")

    gesamt_werte: list[int | None] = []
    gesamt_quelle: int | None = None
    for jahr in jahre:
        zeile = gesamt_nach_jahr.get(jahr)
        if zeile is None:
            gesamt_werte.append(None)
            continue
        gesamt_werte.append(zeile["betrag_teur"] * 1000)
        gesamt_quelle = zeile["quelle"]

    if gep_zeile is not None:
        planzeile = ZEILEN["gesamtergebnisplan"][gep_zeile].kanonisch
        gesamt_plan: list[int | None] | None = [
            planwerte.wert("GESAMT", "", gep_zeile, jahr, gesamt_nach_jahr[jahr]["wertart"])
            if jahr in gesamt_nach_jahr
            else None
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

    if sonstige:
        if gesamt_plan is None:
            raise AppDatenFehler(f"{tabelle}: sonstige=True verlangt eine GEP-Zeile")
        sonstige_werte: list[int | None] = []
        for index in range(len(jahre)):
            plan_wert = gesamt_plan[index]
            gesamt_wert = gesamt_werte[index]
            if plan_wert is None or gesamt_wert is None:
                sonstige_werte.append(None)
                continue
            if abs(plan_wert - gesamt_wert) <= REGEL5_TOLERANZ_GEP_EURO:
                sonstige_werte.append(None)
                continue
            posten_summe = sum(
                posten["werte"][index] or 0  # type: ignore[index]
                for posten in posten_liste
            )
            sonstige_werte.append(plan_wert - posten_summe)
        posten_liste.append(
            {
                "posten": "sonstige",
                "name": "Sonstige",
                "werte": sonstige_werte,
                "gerundet": False,
                "berechnet": True,
                "quelle": gesamt_quelle,
                "anmerkung": (
                    "Differenz zwischen der eurogenauen Planzeile des Gesamtergebnisplans "
                    "und der Summe der gedruckten Vorbericht-Posten (Spez. 3.8); die "
                    "Planzeile ist maßgeblich."
                ),
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


def baue_eigenkapital_tabelle(df: pl.DataFrame, *, jahre: list[int]) -> dict[str, object]:
    """Baut die App-JSON-Struktur von `eigenkapital.csv` (D-11, D-21): wie eine
    manuelle Vorberichtstabelle (`baue_vorbericht_tabelle`), aber `quelle_einheit`
    "euro" (bereits kaufmännisch gerundete Cent, kein ×1000, D-12), `planzeile`/
    `gesamt_plan` `null` (kein GEP-Bezug — die GEP-Z.-28-Prüfung läuft über Regel 5,
    nicht über die App-Daten)."""
    gesamt_df = df.filter(pl.col("ist_gesamt"))
    gesamt_nach_jahr = {zeile["jahr"]: zeile for zeile in gesamt_df.iter_rows(named=True)}
    if not gesamt_nach_jahr:
        raise AppDatenFehler("eigenkapital: keine Gesamtzeile vorhanden")

    gesamt_werte: list[int | None] = []
    gesamt_quelle: int | None = None
    for jahr in jahre:
        zeile = gesamt_nach_jahr.get(jahr)
        if zeile is None:
            gesamt_werte.append(None)
            continue
        gesamt_werte.append(zeile["betrag"])
        gesamt_quelle = zeile["quelle"]

    posten_df = df.filter(~pl.col("ist_gesamt"))
    positionen = sorted(posten_df["position"].unique().to_list())
    posten_liste: list[dict[str, object]] = []
    for position in positionen:
        teil = posten_df.filter(pl.col("position") == position)
        name = teil["posten_name"][0]
        posten_schluessel = teil["posten"][0]
        zeilen_nach_jahr = {zeile["jahr"]: zeile for zeile in teil.iter_rows(named=True)}

        werte: list[int | None] = []
        quelle: int | None = None
        anmerkung: str | None = None
        for jahr in jahre:
            zeile = zeilen_nach_jahr.get(jahr)
            if zeile is None:
                werte.append(None)
                continue
            werte.append(zeile["betrag"])
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
        "tabelle": "eigenkapital",
        "quelle_einheit": "euro",
        "planzeile": None,
        "gesamt_plan": None,
        "gesamt_vorbericht": {
            "werte": gesamt_werte,
            "gerundet": True,
            "quelle": gesamt_quelle,
        },
        "posten": posten_liste,
    }


def baue_stellenplan_json(df: pl.DataFrame, *, haushaltsjahr: int) -> dict[str, object]:
    """Baut die App-JSON-Struktur von `stellenplan.csv` (D-18, D-21, Plan 04-03): eine
    Zeile je CSV-Zeile (bereits in CSV-Reihenfolge, teil/produktbereich/position/
    merkmal/jahr), `stellen_hundertstel` durch 100 geteilt (VZÄ, `einheit_stellen`
    "vzae"); `personen` bleibt unverändert (D-19: Nachwuchskräfte sind keine Stellen)."""

    def _stellen(hundertstel: int | None) -> float | None:
        return hundertstel / 100 if hundertstel is not None else None

    zeilen = [
        {
            "teil": zeile["teil"],
            "position": zeile["position"],
            "gruppe": zeile["gruppe"],
            "amtsbezeichnung": zeile["amtsbezeichnung"],
            "verguetung": zeile["verguetung"],
            "produktbereich": zeile["produktbereich"],
            "merkmal": zeile["merkmal"],
            "jahr": zeile["jahr"],
            "stichtag": zeile["stichtag"],
            "stellen": _stellen(zeile["stellen_hundertstel"]),
            "personen": zeile["personen"],
            "vermerk": zeile["vermerk"],
            "pdf_seite": zeile["pdf_seite"],
        }
        for zeile in df.iter_rows(named=True)
    ]
    return {
        "haushaltsjahr": haushaltsjahr,
        "einheit_stellen": "vzae",
        "zeilen": zeilen,
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

    # Reihenfolge ist Teil des App-JSON-Vertrags (D-21): steuerarten, zuwendungen,
    # transferaufwendungen, kita_zuschuesse, dann die fünf D-08-Tabellen (leistungsentgelte,
    # kostenerstattungen, personal, sachaufwand, sonstige_aufwendungen) — dict-
    # Einfügereihenfolge bleibt beim Schreiben erhalten (schreibe_app_json/json.dumps,
    # keine sort_keys).
    vorbericht_quellen = {
        "steuerarten": lies_vorbericht_csv(daten_wurzel / STEUERARTEN_CSV),
        "zuwendungen": lies_vorbericht_csv(daten_wurzel / ZUWENDUNGEN_CSV),
        "transferaufwendungen": lies_vorbericht_csv(daten_wurzel / TRANSFERAUFWENDUNGEN_CSV),
        "kita_zuschuesse": lies_vorbericht_csv(daten_wurzel / KITA_ZUSCHUESSE_CSV),
        **zerlege_weitere_vorberichtstabellen(
            lies_vorbericht_csv(daten_wurzel / WEITERE_VORBERICHTSTABELLEN_CSV)
        ),
    }
    vorbericht = {
        tabelle: baue_vorbericht_tabelle(
            df,
            jahre=jahre,
            planwerte=planwerte,
            gep_zeile=REGEL5_GEP_ZEILEN.get(tabelle),
            sonstige=(tabelle == "zuwendungen"),
        )
        for tabelle, df in vorbericht_quellen.items()
    }

    meta = lies_meta_json(daten_wurzel / META_JSON)
    eigenkapital_df = lies_eigenkapital_csv(daten_wurzel / EIGENKAPITAL_CSV)
    eigenkapital = baue_eigenkapital_tabelle(eigenkapital_df, jahre=jahre)

    daten = {
        "haushaltsjahr": jahrgang.haushaltsjahr,
        "jahre": jahre,
        "wertarten": wertarten,
        "meta": meta,
        "vorbericht": vorbericht,
        "eigenkapital": eigenkapital,
    }

    pfad = app_daten_wurzel / HAUSHALT_JSON
    schreibe_app_json(daten, pfad, praefix="haushalt")

    stellenplan_df = lies_stellenplan_csv(daten_wurzel / STELLENPLAN_CSV)
    stellenplan_daten = baue_stellenplan_json(stellenplan_df, haushaltsjahr=jahrgang.haushaltsjahr)
    stellenplan_pfad = app_daten_wurzel / STELLENPLAN_JSON
    schreibe_app_json(stellenplan_daten, stellenplan_pfad, praefix="stellenplan")

    return [pfad, stellenplan_pfad]
