"""Tests für ostbevern.pruefung: liest nur eingecheckte CSVs, nie das PDF (D-06).

Keine Jahrgangs-, Seiten- oder Sollwert-Literale; Werte kommen aus lade_sollwerte
oder werden aus den eingecheckten Dateien abgeleitet.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Sequence
from pathlib import Path

import polars as pl
import pytest

from ostbevern.konfiguration import JAHRGAENGE_VERZEICHNIS, STANDARD_JAHR, lade_sollwerte
from ostbevern.pruefung import (
    REGEL3_ZEILEN,
    SATZUNG_FORMELN,
    TOLERANZ_EURO,
    Abgleich,
    Befund,
    Planwerte,
    Pruefpunkt,
    PruefungsFehler,
    _pruefe_regel1,
    gleiche_befunde_ab,
    lies_befunde,
    pruefe_alles,
    rendere_konsistenzbericht,
    schreibe_konsistenzbericht,
)
from ostbevern.schema import (
    BEFUNDE_MD,
    DATEN_WURZEL,
    ERGEBNISPLAN_CSV,
    FINANZPLAN_CSV,
    HIERARCHIE_CSV,
    KONSISTENZ_MD,
    PLAN_SPALTEN,
    SEITEN_CSV,
    lies_hierarchie_csv,
    lies_plan_csv,
    lies_seiten_csv,
    schreibe_plan_csv,
    schreibe_seiten_csv,
)
from ostbevern.zeilen import FORMELN

_SCHLUESSELTABELLE_KOPF = (
    "| regel | plan | ebene | code | zeile | jahr | wertart | abweichung | pdf_seite | "
    "begruendung |"
)
_SCHLUESSELTABELLE_TRENNZEILE = "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"


def _schreibe_befunde_md(pfad: Path, *, zeilen: Sequence[str] = ()) -> None:
    """Schreibt eine Test-befunde.md mit gültiger Überschrift und Kopfzeile (D-02)."""
    inhalt = [
        "# Befunde – Test",
        "",
        "## Schlüsseltabelle",
        "",
        _SCHLUESSELTABELLE_KOPF,
        _SCHLUESSELTABELLE_TRENNZEILE,
        *zeilen,
        "",
    ]
    pfad.parent.mkdir(parents=True, exist_ok=True)
    pfad.write_text("\n".join(inhalt), encoding="utf-8")


def _lies_schluesseltabelle_markdown_zeilen(pfad: Path) -> list[str]:
    """Liest die rohen Markdown-Tabellenzeilen der Schlüsseltabelle einer befunde.md.

    Für Tests, die eigene Befunde zu den real eingecheckten (D-06) hinzufügen wollen, ohne
    deren bekannte PDF-Rundungsdifferenzen (Regel 1/2/3) von Hand zu duplizieren.
    """
    zeilen = pfad.read_text(encoding="utf-8").splitlines()
    start = next(i for i, z in enumerate(zeilen) if z.strip() == "## Schlüsseltabelle")
    kopfzeile_index = next(i for i in range(start + 1, len(zeilen)) if zeilen[i].strip())
    ergebnis: list[str] = []
    for zeile in zeilen[kopfzeile_index + 2 :]:
        if not zeile.strip().startswith("|"):
            break
        ergebnis.append(zeile)
    return ergebnis


def _befunde_zeile(
    *,
    regel: int,
    plan: str,
    ebene: str,
    code: str,
    zeile: str,
    jahr: int,
    wertart: str,
    abweichung: int,
    pdf_seite: int,
    begruendung: str,
) -> str:
    return (
        f"| {regel} | {plan} | {ebene} | {code} | {zeile} | {jahr} | {wertart} | "
        f"{abweichung} | {pdf_seite} | {begruendung} |"
    )


_LEERER_PLAN = pl.DataFrame([], schema=PLAN_SPALTEN)


def _synthetischer_teilergebnisplan(z29_betrag: int) -> pl.DataFrame:
    """PB-Knoten, der nur Z. 02/10/11/17/27/28/29 druckt (Research Pitfall 1, PB01-Muster).

    Z. 18/22/26 (Ordentliches Ergebnis, Ergebnis lfd. Verw., Jahresergebnis) fehlen bewusst
    und müssen über die Formelkette hergeleitet werden: Z18 = Z10 - Z17 = 1000 - 2000 = -1000,
    Z22 = Z18 + Z21(=0) = -1000, Z26 = Z22 + Z25(=0) = -1000.
    """
    jahr, wertart = STANDARD_JAHR, "ansatz"
    basis = {
        "synthetisch": False,
        "operator": None,
        "jahr": jahr,
        "wertart": wertart,
        "pdf_seite": 66,
    }

    def _zeile(
        zeile: str, kanonisch: str, name: str, betrag: int, *, ist_summe: bool = False
    ) -> dict:
        return {
            "ebene": "PB",
            "code": "99",
            "zeile": zeile,
            "zeile_kanonisch": kanonisch,
            "zeile_name": name,
            "betrag": betrag,
            "ist_summe": ist_summe,
            **basis,
        }

    datensaetze = [
        _zeile("02", "zuwendungen", "Zuwendungen und allgemeine Umlagen", 1000),
        _zeile("10", "ordentliche_ertraege", "Ordentliche Erträge", 1000, ist_summe=True),
        _zeile("11", "personalaufwendungen", "Personalaufwendungen", 2000),
        _zeile("17", "ordentliche_aufwendungen", "Ordentliche Aufwendungen", 2000, ist_summe=True),
        _zeile("27", "interne_ertraege", "Erträge aus internen Leistungsbeziehungen", 500),
        _zeile("28", "interne_aufwendungen", "Aufwendungen aus internen Leistungsbeziehungen", 300),
        _zeile(
            "29",
            "ergebnis_mit_internen_verrechnungen",
            "Ergebnis mit inneren Verrechnungen",
            z29_betrag,
            ist_summe=True,
        ),
    ]
    return pl.DataFrame(datensaetze, schema=PLAN_SPALTEN)


def _kopiere_finanzplan_nach(tmp_path: Path) -> None:
    """Kopiert die eingecheckte finanzplan.csv unverändert in den tmp-Datenbaum (D-06)."""
    finanzplan = lies_plan_csv(DATEN_WURZEL / FINANZPLAN_CSV)
    schreibe_plan_csv(finanzplan, tmp_path / FINANZPLAN_CSV)


def _kopiere_hierarchie_nach(tmp_path: Path) -> None:
    """Kopiert die eingecheckte hierarchie.csv unverändert in den tmp-Datenbaum (D-06)."""
    pfad_ziel = tmp_path / HIERARCHIE_CSV
    pfad_ziel.parent.mkdir(parents=True, exist_ok=True)
    pfad_ziel.write_bytes((DATEN_WURZEL / HIERARCHIE_CSV).read_bytes())


def _kopiere_befunde_nach(tmp_path: Path) -> None:
    """Kopiert die eingecheckte befunde.md unverändert in den tmp-Datenbaum (D-02)."""
    pfad_ziel = tmp_path / BEFUNDE_MD
    pfad_ziel.parent.mkdir(parents=True, exist_ok=True)
    pfad_ziel.write_bytes((DATEN_WURZEL / BEFUNDE_MD).read_bytes())


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


def _manipuliere_eine_zeile(
    df: pl.DataFrame,
    *,
    ebene: str,
    code: str,
    zeile: str,
    jahr: int,
    wertart: str,
    delta: int,
) -> pl.DataFrame:
    """Ändert genau eine (ebene, code, zeile, jahr, wertart)-Zelle um `delta` (Regel 2/3)."""
    bedingung = (
        (pl.col("ebene") == ebene)
        & (pl.col("code") == code)
        & (pl.col("zeile") == zeile)
        & (pl.col("jahr") == jahr)
        & (pl.col("wertart") == wertart)
    )
    return df.with_columns(
        pl.when(bedingung)
        .then(pl.col("betrag") + delta)
        .otherwise(pl.col("betrag"))
        .alias("betrag")
    )


def _erste_zeile(df: pl.DataFrame, *, ebene: str, zeile: str) -> dict:
    """Die erste (nach code/jahr/wertart sortierte) Zeile eines Knotens für eine Zeilennummer."""
    treffer = df.filter((pl.col("ebene") == ebene) & (pl.col("zeile") == zeile))
    return treffer.sort(["code", "jahr", "wertart"]).row(0, named=True)


def _erwartete_anzahl_regel4(sollwerte: dict) -> int:
    gesamtergebnisplan = sollwerte["gesamtergebnisplan"]
    b1 = len(gesamtergebnisplan["zeilen"]) * len(gesamtergebnisplan["jahre"])
    gesamtfinanzplan = sollwerte["gesamtfinanzplan"]
    b2 = len(gesamtfinanzplan.get("ansatz", {})) + len(gesamtfinanzplan.get("ve", {}))
    satzung = len(sollwerte["satzung"]) - 1  # ohne pdf_seite
    # Anhang B.3: je PB die Felder aus teilergebnisplaene_pb (ordentliche_ertraege,
    # ordentliche_aufwendungen, ergebnis_mit_internen_verrechnungen), plus die PB-Summenfelder.
    teilergebnisplaene_pb = sollwerte["teilergebnisplaene_pb"]
    felder_pro_pb = len(next(iter(teilergebnisplaene_pb.values())))
    b3 = len(teilergebnisplaene_pb) * felder_pro_pb + len(sollwerte["teilergebnisplaene_pb_summe"])
    return b1 + b2 + satzung + b3


def _kopiere_seiten_nach(tmp_path: Path) -> None:
    """Kopiert die eingecheckte seiten.csv unverändert in den tmp-Datenbaum (D-06)."""
    pfad_ziel = tmp_path / SEITEN_CSV
    pfad_ziel.parent.mkdir(parents=True, exist_ok=True)
    pfad_ziel.write_bytes((DATEN_WURZEL / SEITEN_CSV).read_bytes())


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


def test_regel4_b3_gruen_auf_eingecheckten_daten() -> None:
    bericht = pruefe_alles(STANDARD_JAHR)
    regel4 = next((regel for regel in bericht.regeln if regel.regel == 4), None)
    assert regel4 is not None, "Regel 4 fehlt im Bericht"

    sollwerte = lade_sollwerte(STANDARD_JAHR)
    assert regel4.geprueft == _erwartete_anzahl_regel4(sollwerte)
    assert regel4.status == "grün"
    assert regel4.abweichungen == ()


def test_regel4_b3_herleitet_fehlende_z29() -> None:
    """Mind. eine PB druckt Anhang B.3 Z. 29 nicht; Planwerte muss sie über die Formelkette
    (Z.26+27-28) aus den gedruckten PB-Zeilen herleiten (Research Planning-time facts)."""
    sollwerte = lade_sollwerte(STANDARD_JAHR)
    haushaltsjahr = sollwerte["haushaltsjahr"]
    ergebnisplan = lies_plan_csv(DATEN_WURZEL / ERGEBNISPLAN_CSV)

    pb_ohne_z29 = next(
        pb_code
        for pb_code in sollwerte["teilergebnisplaene_pb"]
        if ergebnisplan.filter(
            (pl.col("ebene") == "PB")
            & (pl.col("code") == pb_code)
            & (pl.col("zeile") == "29")
            & (pl.col("jahr") == haushaltsjahr)
        ).height
        == 0
    )

    planwerte = Planwerte(ergebnisplan, datei="ergebnisplan")
    hergeleitet = planwerte.wert("PB", pb_ohne_z29, "29", haushaltsjahr, "ansatz")
    soll = sollwerte["teilergebnisplaene_pb"][pb_ohne_z29]["ergebnis_mit_internen_verrechnungen"]
    assert hergeleitet == soll


def test_regel4_b3_unbekannte_pb_bricht_ab(tmp_path: Path) -> None:
    quelle_pfad = JAHRGAENGE_VERZEICHNIS / f"{STANDARD_JAHR}_sollwerte.toml"
    text = quelle_pfad.read_text(encoding="utf-8")
    markierung = "[teilergebnisplaene_pb_summe]\n"
    assert markierung in text
    neue_zeile = (
        '"99" = { ordentliche_ertraege = 1, ordentliche_aufwendungen = 1, '
        "ergebnis_mit_internen_verrechnungen = 1 }\n"
    )
    text = text.replace(markierung, neue_zeile + markierung)
    ziel_pfad = tmp_path / f"{STANDARD_JAHR}_sollwerte.toml"
    ziel_pfad.write_text(text, encoding="utf-8")

    with pytest.raises(PruefungsFehler, match="99"):
        pruefe_alles(STANDARD_JAHR, sollwerte_verzeichnis=tmp_path)


def test_regel1_sollwerte_gesamtplaene_gruen() -> None:
    bericht = pruefe_alles(STANDARD_JAHR)
    regel1 = next(regel for regel in bericht.regeln if regel.regel == 1)

    # Gesamtergebnisplan: 8 Formelzeilen (10,17,18,21,22,25,26,28) x 6 Spalten = 48.
    # Gesamtfinanzplan: 10 Formelzeilen (09,16,17,23,30,31,32,37,38,41) x 7 Spalten = 70.
    # 118 GESAMT + 6432 Teilplan-Formelzeilen seit 02-04 (alle PB/PG/P-Knoten inkl.
    # synthetischer PG; nur tatsächlich gedruckte Zeilen zählen, D-13).
    assert regel1.geprueft == 6550
    assert regel1.status == "grün"
    # Die einzigen echten PDF-Abweichungen (PB 08/PG 0801/P 080101, je Z. 17, 2024 —
    # dieselbe Rundungsdifferenz auf allen drei Ebenen, PB 08 hat nur ein Produkt) sind
    # in befunde.md dokumentiert und deshalb hier "bekannt", nicht "offen" (D-04/D-05).
    assert regel1.abweichungen == ()


def test_regel2_gruen_auf_eingecheckten_daten() -> None:
    bericht = pruefe_alles(STANDARD_JAHR)
    regel2 = next((regel for regel in bericht.regeln if regel.regel == 2), None)
    assert regel2 is not None, "Regel 2 fehlt im Bericht"
    assert regel2.status == "grün"
    assert regel2.abweichungen == ()


def test_regel2_erkennt_manipulierte_produktzeile(tmp_path: Path) -> None:
    ergebnisplan = lies_plan_csv(DATEN_WURZEL / ERGEBNISPLAN_CSV)
    hierarchie = lies_hierarchie_csv(DATEN_WURZEL / HIERARCHIE_CSV)
    produkt_zeile = _erste_zeile(ergebnisplan, ebene="P", zeile="13")
    pg_code = hierarchie.filter(
        (pl.col("ebene") == "P") & (pl.col("code") == produkt_zeile["code"])
    )["eltern_code"][0]

    manipuliert_2 = _manipuliere_eine_zeile(
        ergebnisplan,
        ebene="P",
        code=produkt_zeile["code"],
        zeile=produkt_zeile["zeile"],
        jahr=produkt_zeile["jahr"],
        wertart=produkt_zeile["wertart"],
        delta=2,
    )
    schreibe_plan_csv(manipuliert_2, tmp_path / ERGEBNISPLAN_CSV)
    _kopiere_finanzplan_nach(tmp_path)
    _kopiere_hierarchie_nach(tmp_path)
    _kopiere_seiten_nach(tmp_path)
    _kopiere_befunde_nach(tmp_path)

    bericht = pruefe_alles(STANDARD_JAHR, daten_wurzel=tmp_path)
    regel2 = next((regel for regel in bericht.regeln if regel.regel == 2), None)
    assert regel2 is not None, "Regel 2 fehlt im Bericht"
    assert len(regel2.abweichungen) == 1
    abweichung = regel2.abweichungen[0]
    assert abweichung.ebene == "PG"
    assert abweichung.code == pg_code
    assert abweichung.zeile == produkt_zeile["zeile"]
    assert abweichung.jahr == produkt_zeile["jahr"]
    assert abweichung.wertart == produkt_zeile["wertart"]
    assert abweichung.abweichung == 2

    # +1 EUR bleibt innerhalb von TOLERANZ_EURO (Regel 2 bleibt grün).
    manipuliert_1 = _manipuliere_eine_zeile(
        ergebnisplan,
        ebene="P",
        code=produkt_zeile["code"],
        zeile=produkt_zeile["zeile"],
        jahr=produkt_zeile["jahr"],
        wertart=produkt_zeile["wertart"],
        delta=TOLERANZ_EURO,
    )
    schreibe_plan_csv(manipuliert_1, tmp_path / ERGEBNISPLAN_CSV)
    bericht_ein_euro = pruefe_alles(STANDARD_JAHR, daten_wurzel=tmp_path)
    regel2_ein_euro = next((regel for regel in bericht_ein_euro.regeln if regel.regel == 2), None)
    assert regel2_ein_euro is not None, "Regel 2 fehlt im Bericht"
    assert regel2_ein_euro.status == "grün"


def test_regel3_gruen_auf_eingecheckten_daten() -> None:
    bericht = pruefe_alles(STANDARD_JAHR)
    regel3 = next((regel for regel in bericht.regeln if regel.regel == 3), None)
    assert regel3 is not None, "Regel 3 fehlt im Bericht"
    assert regel3.geprueft == 114
    assert regel3.status == "grün"
    assert regel3.abweichungen == ()


def test_regel3_ignoriert_tp_27_28(tmp_path: Path) -> None:
    ergebnisplan = lies_plan_csv(DATEN_WURZEL / ERGEBNISPLAN_CSV)
    pb_zeile_27 = _erste_zeile(ergebnisplan, ebene="PB", zeile="27")
    manipuliert = _manipuliere_eine_zeile(
        ergebnisplan,
        ebene="PB",
        code=pb_zeile_27["code"],
        zeile="27",
        jahr=pb_zeile_27["jahr"],
        wertart=pb_zeile_27["wertart"],
        delta=1_000_000,
    )
    schreibe_plan_csv(manipuliert, tmp_path / ERGEBNISPLAN_CSV)
    _kopiere_finanzplan_nach(tmp_path)
    _kopiere_hierarchie_nach(tmp_path)
    _kopiere_seiten_nach(tmp_path)
    _kopiere_befunde_nach(tmp_path)

    bericht = pruefe_alles(STANDARD_JAHR, daten_wurzel=tmp_path)
    regel3 = next((regel for regel in bericht.regeln if regel.regel == 3), None)
    assert regel3 is not None, "Regel 3 fehlt im Bericht"
    assert regel3.status == "grün"
    assert regel3.abweichungen == ()


def test_regel3_erkennt_manipulierte_pb_zeile(tmp_path: Path) -> None:
    ergebnisplan = lies_plan_csv(DATEN_WURZEL / ERGEBNISPLAN_CSV)
    pb_zeile_15 = _erste_zeile(ergebnisplan, ebene="PB", zeile="15")
    manipuliert = _manipuliere_eine_zeile(
        ergebnisplan,
        ebene="PB",
        code=pb_zeile_15["code"],
        zeile="15",
        jahr=pb_zeile_15["jahr"],
        wertart=pb_zeile_15["wertart"],
        delta=2,
    )
    schreibe_plan_csv(manipuliert, tmp_path / ERGEBNISPLAN_CSV)
    _kopiere_finanzplan_nach(tmp_path)
    _kopiere_hierarchie_nach(tmp_path)
    _kopiere_seiten_nach(tmp_path)
    _kopiere_befunde_nach(tmp_path)

    bericht = pruefe_alles(STANDARD_JAHR, daten_wurzel=tmp_path)
    regel3 = next((regel for regel in bericht.regeln if regel.regel == 3), None)
    assert regel3 is not None, "Regel 3 fehlt im Bericht"
    assert len(regel3.abweichungen) == 1
    abweichung = regel3.abweichungen[0]
    assert abweichung.zeile == "15"
    assert abweichung.jahr == pb_zeile_15["jahr"]
    assert abweichung.wertart == pb_zeile_15["wertart"]
    assert abweichung.abweichung == 2


def test_regel1_formelkette_fuer_fehlende_zwischenzeilen() -> None:
    df = _synthetischer_teilergebnisplan(z29_betrag=-800)
    jahr, wertart = STANDARD_JAHR, "ansatz"

    planwerte = Planwerte(df, datei="ergebnisplan")
    assert planwerte.wert("PB", "99", "18", jahr, wertart) == -1000
    assert planwerte.wert("PB", "99", "22", jahr, wertart) == -1000
    assert planwerte.wert("PB", "99", "26", jahr, wertart) == -1000

    regel1 = _pruefe_regel1(ergebnisplan=df, finanzplan=_LEERER_PLAN)
    assert regel1.status == "grün"
    assert regel1.abweichungen == ()


def test_regel1_toleriert_einen_euro_sonst_rot() -> None:
    # Formelkette ergibt -800; +1 EUR bleibt innerhalb TOLERANZ_EURO, +2 EUR nicht.
    df_ein_euro = _synthetischer_teilergebnisplan(z29_betrag=-800 + TOLERANZ_EURO)
    regel1_ein_euro = _pruefe_regel1(ergebnisplan=df_ein_euro, finanzplan=_LEERER_PLAN)
    assert regel1_ein_euro.status == "grün"

    df_zwei_euro = _synthetischer_teilergebnisplan(z29_betrag=-800 + TOLERANZ_EURO + 1)
    regel1_zwei_euro = _pruefe_regel1(ergebnisplan=df_zwei_euro, finanzplan=_LEERER_PLAN)
    assert regel1_zwei_euro.status == "rot"
    assert len(regel1_zwei_euro.abweichungen) == 1
    abweichung = regel1_zwei_euro.abweichungen[0]
    assert abweichung.zeile == "29"
    assert abweichung.abweichung == -(TOLERANZ_EURO + 1)


def test_regel1_keine_formel_fuer_nachrichtlich_zeile_33(tmp_path: Path) -> None:
    ergebnisplan = lies_plan_csv(DATEN_WURZEL / ERGEBNISPLAN_CSV)
    manipuliert = _manipuliere_betrag(ergebnisplan, zeile="33", jahr=2024, delta=1_000_000)
    schreibe_plan_csv(manipuliert, tmp_path / ERGEBNISPLAN_CSV)
    _kopiere_finanzplan_nach(tmp_path)
    _kopiere_hierarchie_nach(tmp_path)
    _kopiere_seiten_nach(tmp_path)
    _kopiere_befunde_nach(tmp_path)

    bericht = pruefe_alles(STANDARD_JAHR, daten_wurzel=tmp_path)
    regel1 = next(regel for regel in bericht.regeln if regel.regel == 1)

    assert regel1.status == "grün"
    assert regel1.abweichungen == ()


def test_planwerte_gibt_null_fuer_fehlende_leerzeile() -> None:
    df = _synthetischer_teilergebnisplan(z29_betrag=-800)
    planwerte = Planwerte(df, datei="ergebnisplan")
    # Zeile 01 (Steuern) ist in diesem Knoten nie gedruckt (D-11) und hat keine Formel.
    assert planwerte.wert("PB", "99", "01", STANDARD_JAHR, "ansatz") == 0


def test_planwerte_formelzyklus_bricht_ab(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        "ostbevern.pruefung.FORMELN",
        {"gesamtergebnisplan": {"10": ((1, "10"),)}},
    )
    planwerte = Planwerte(_LEERER_PLAN, datei="ergebnisplan")
    with pytest.raises(PruefungsFehler, match="Formelzyklus"):
        planwerte.wert("GESAMT", "", "10", STANDARD_JAHR, "ansatz")


def test_befund_deckt_abweichung_innerhalb_toleranz_ab() -> None:
    punkt = Pruefpunkt(
        regel=4,
        plan="gesamtergebnisplan",
        ebene="GESAMT",
        code="",
        zeile="02",
        jahr=STANDARD_JAHR,
        wertart="ansatz",
        soll=1000,
        ist=1005,
        pdf_seite=62,
    )
    befund_exakt = Befund(
        regel=4,
        plan="gesamtergebnisplan",
        ebene="GESAMT",
        code="",
        zeile="02",
        jahr=STANDARD_JAHR,
        wertart="ansatz",
        abweichung=5,
        pdf_seite=62,
        begruendung="Rundungsdifferenz laut PDF",
    )
    abgleich = gleiche_befunde_ab((punkt,), (befund_exakt,))
    assert isinstance(abgleich, Abgleich)
    assert abgleich.offen == ()
    assert abgleich.veraltet == ()
    assert abgleich.bekannt == ((punkt, befund_exakt),)

    # D-05: die dokumentierte Abweichung darf bis zu TOLERANZ_EURO von der tatsächlichen
    # abweichen (hier: 6 statt 5) und deckt die Abweichung trotzdem ab.
    befund_plus_toleranz = dataclasses.replace(befund_exakt, abweichung=5 + TOLERANZ_EURO)
    abgleich_toleranz = gleiche_befunde_ab((punkt,), (befund_plus_toleranz,))
    assert abgleich_toleranz.offen == ()
    assert len(abgleich_toleranz.bekannt) == 1


def test_veralteter_befund_wenn_abweichung_nicht_mehr_passt() -> None:
    punkt = Pruefpunkt(
        regel=4,
        plan="gesamtergebnisplan",
        ebene="GESAMT",
        code="",
        zeile="02",
        jahr=STANDARD_JAHR,
        wertart="ansatz",
        soll=1000,
        ist=1008,
        pdf_seite=62,
    )
    befund = Befund(
        regel=4,
        plan="gesamtergebnisplan",
        ebene="GESAMT",
        code="",
        zeile="02",
        jahr=STANDARD_JAHR,
        wertart="ansatz",
        abweichung=5,
        pdf_seite=62,
        begruendung="Rundungsdifferenz laut PDF",
    )
    abgleich = gleiche_befunde_ab((punkt,), (befund,))
    assert abgleich.offen == (punkt,)
    assert abgleich.bekannt == ()
    assert abgleich.veraltet == (befund,)


def test_veralteter_befund_ohne_passende_abweichung() -> None:
    befund = Befund(
        regel=4,
        plan="gesamtergebnisplan",
        ebene="GESAMT",
        code="",
        zeile="02",
        jahr=STANDARD_JAHR,
        wertart="ansatz",
        abweichung=5,
        pdf_seite=62,
        begruendung="tritt nicht mehr auf",
    )
    abgleich = gleiche_befunde_ab((), (befund,))
    assert abgleich.offen == ()
    assert abgleich.bekannt == ()
    assert abgleich.veraltet == (befund,)


def test_veralteter_befund_macht_bericht_nicht_gruen(tmp_path: Path) -> None:
    ergebnisplan = lies_plan_csv(DATEN_WURZEL / ERGEBNISPLAN_CSV)
    schreibe_plan_csv(ergebnisplan, tmp_path / ERGEBNISPLAN_CSV)
    _kopiere_finanzplan_nach(tmp_path)
    _kopiere_hierarchie_nach(tmp_path)
    _kopiere_seiten_nach(tmp_path)
    zeile = _befunde_zeile(
        regel=4,
        plan="gesamtergebnisplan",
        ebene="GESAMT",
        code="",
        zeile="02",
        jahr=STANDARD_JAHR,
        wertart="ansatz",
        abweichung=5,
        pdf_seite=62,
        begruendung="nie aufgetreten",
    )
    _schreibe_befunde_md(tmp_path / BEFUNDE_MD, zeilen=[zeile])

    bericht = pruefe_alles(STANDARD_JAHR, daten_wurzel=tmp_path)
    assert bericht.ist_gruen is False
    assert len(bericht.veraltete_befunde) == 1


def test_kaputte_schluesseltabelle_falsche_zellenzahl(tmp_path: Path) -> None:
    pfad = tmp_path / "befunde.md"
    # Nur 9 Zellen statt 10 (Begründung fehlt).
    zeile = f"| 4 | gesamtergebnisplan | GESAMT |  | 02 | {STANDARD_JAHR} | ansatz | 5 | 62 |"
    _schreibe_befunde_md(pfad, zeilen=[zeile])
    with pytest.raises(PruefungsFehler, match="10"):
        lies_befunde(pfad)


def test_kaputte_schluesseltabelle_abweichung_nicht_int(tmp_path: Path) -> None:
    pfad = tmp_path / "befunde.md"
    zeile = _befunde_zeile(
        regel=4,
        plan="gesamtergebnisplan",
        ebene="GESAMT",
        code="",
        zeile="02",
        jahr=STANDARD_JAHR,
        wertart="ansatz",
        abweichung="fuenf",  # type: ignore[arg-type]
        pdf_seite=62,
        begruendung="x",
    )
    _schreibe_befunde_md(pfad, zeilen=[zeile])
    with pytest.raises(PruefungsFehler):
        lies_befunde(pfad)


def test_kaputte_schluesseltabelle_abweichung_zu_klein(tmp_path: Path) -> None:
    pfad = tmp_path / "befunde.md"
    zeile = _befunde_zeile(
        regel=4,
        plan="gesamtergebnisplan",
        ebene="GESAMT",
        code="",
        zeile="02",
        jahr=STANDARD_JAHR,
        wertart="ansatz",
        abweichung=TOLERANZ_EURO,
        pdf_seite=62,
        begruendung="x",
    )
    _schreibe_befunde_md(pfad, zeilen=[zeile])
    with pytest.raises(PruefungsFehler):
        lies_befunde(pfad)


def test_kaputte_schluesseltabelle_leere_begruendung(tmp_path: Path) -> None:
    pfad = tmp_path / "befunde.md"
    zeile = f"| 4 | gesamtergebnisplan | GESAMT |  | 02 | {STANDARD_JAHR} | ansatz | 5 | 62 |  |"
    _schreibe_befunde_md(pfad, zeilen=[zeile])
    with pytest.raises(PruefungsFehler):
        lies_befunde(pfad)


def test_kaputte_schluesseltabelle_fehlende_ueberschrift(tmp_path: Path) -> None:
    pfad = tmp_path / "befunde.md"
    pfad.write_text("# Befunde – Test\n\nKein Schlüsseltabelle-Abschnitt hier.\n", encoding="utf-8")
    with pytest.raises(PruefungsFehler):
        lies_befunde(pfad)


def test_kaputte_schluesseltabelle_fehlende_datei(tmp_path: Path) -> None:
    with pytest.raises(PruefungsFehler):
        lies_befunde(tmp_path / "existiert-nicht.md")


def test_lies_befunde_leere_schluesseltabelle_ist_gueltig(tmp_path: Path) -> None:
    pfad = tmp_path / "befunde.md"
    _schreibe_befunde_md(pfad, zeilen=[])
    assert lies_befunde(pfad) == ()


def test_konsistenzbericht_listet_bekannten_befund(tmp_path: Path) -> None:
    sollwerte = lade_sollwerte(STANDARD_JAHR)
    gesamtergebnisplan = sollwerte["gesamtergebnisplan"]
    zeile_sollwert = sorted(gesamtergebnisplan["zeilen"])[0]
    # Das Haushaltsjahr selbst ist immer Teil von B.1's Jahresreihe (Ansatz-Spalte).
    assert STANDARD_JAHR in gesamtergebnisplan["jahre"]
    jahr = STANDARD_JAHR

    # zeile_sollwert ist eine Komponente einer Regel-1-Formelzeile (z. B. Zeile 10 = Summe
    # 01-09): eine Manipulation von zeile_sollwert erzeugt deshalb zwei Abweichungen, die
    # beide einen passenden Befund brauchen — Regel 4 (Sollwert) und Regel 1 (Formelzeile,
    # deren gedruckte Summe nun von den manipulierten Komponenten abweicht).
    formelzeile = next(
        zeile
        for zeile, formel in FORMELN["gesamtergebnisplan"].items()
        if any(komponente == zeile_sollwert for _, komponente in formel)
    )

    df = lies_plan_csv(DATEN_WURZEL / ERGEBNISPLAN_CSV)
    manipuliert = _manipuliere_betrag(df, zeile=zeile_sollwert, jahr=jahr, delta=5)
    schreibe_plan_csv(manipuliert, tmp_path / ERGEBNISPLAN_CSV)
    _kopiere_finanzplan_nach(tmp_path)
    _kopiere_hierarchie_nach(tmp_path)
    _kopiere_seiten_nach(tmp_path)

    befund_regel4 = _befunde_zeile(
        regel=4,
        plan="gesamtergebnisplan",
        ebene="GESAMT",
        code="",
        zeile=zeile_sollwert,
        jahr=jahr,
        wertart="ansatz",
        abweichung=5,
        pdf_seite=62,
        begruendung="Testabweichung Sollwert",
    )
    befund_regel1 = _befunde_zeile(
        regel=1,
        plan="gesamtergebnisplan",
        ebene="GESAMT",
        code="",
        zeile=formelzeile,
        jahr=jahr,
        wertart="ansatz",
        abweichung=5,
        pdf_seite=62,
        begruendung="Testabweichung Formelzeile",
    )
    # Seit 02-04 enthält ergebnisplan.csv auch die PB/PG/P-Teilplanzeilen; deren einzige
    # echte, im PDF so gedruckte Abweichung (dieselbe Rundungsdifferenz auf allen drei
    # Ebenen, da PB 08 nur ein Produkt hat) braucht denselben Befund-Abgleich wie die
    # beiden Test-Befunde oben, sonst bleibt sie hier offen (rot).
    befunde_teilplan = [
        _befunde_zeile(
            regel=1,
            plan="teilergebnisplan",
            ebene=ebene,
            code=code,
            zeile="17",
            jahr=2024,
            wertart="ergebnis",
            abweichung=2,
            pdf_seite=pdf_seite,
            begruendung="Rundungsdifferenz im PDF (siehe daten/pruefberichte/befunde.md)",
        )
        for ebene, code, pdf_seite in (
            ("PB", "08", 203),
            ("PG", "0801", 206),
            ("P", "080101", 206),
        )
    ]
    # zeile_sollwert kann auch eine Regel-3-Zeile sein (Z. 01-17/19/20): die GESAMT-Manipulation
    # wirkt dann auch auf Regel 3 (soll = Gesamt, ist = Σ PB bleibt unverändert), seit diesem
    # Plan braucht das denselben Befund-Abgleich wie Regel 1/4 oben.
    befunde_regel3: list[str] = []
    if zeile_sollwert in REGEL3_ZEILEN:
        hierarchie = lies_hierarchie_csv(DATEN_WURZEL / HIERARCHIE_CSV)
        planwerte_basis = Planwerte(df, datei="ergebnisplan")
        pb_codes = sorted(hierarchie.filter(pl.col("ebene") == "PB")["code"].unique().to_list())
        ist_basis = sum(
            planwerte_basis.wert("PB", code, zeile_sollwert, jahr, "ansatz") for code in pb_codes
        )
        soll_basis = planwerte_basis.wert("GESAMT", "", zeile_sollwert, jahr, "ansatz")
        abweichung_regel3 = ist_basis - (soll_basis + 5)
        if abs(abweichung_regel3) > TOLERANZ_EURO:
            befunde_regel3 = [
                _befunde_zeile(
                    regel=3,
                    plan="gesamtergebnisplan",
                    ebene="GESAMT",
                    code="",
                    zeile=zeile_sollwert,
                    jahr=jahr,
                    wertart="ansatz",
                    abweichung=abweichung_regel3,
                    pdf_seite=62,
                    begruendung="Testabweichung Regel 3 (GESAMT-Manipulation wirkt auch hier)",
                )
            ]

    # Die real eingecheckte befunde.md deckt bereits die bekannten PDF-Rundungsdifferenzen von
    # Regel 1 (PB08/PG0801/P080101 Z.17 2024, s. befunde_teilplan) und Regel 2/3 ab; diese Datei
    # ergänzt nur die beiden testspezifischen Einträge (und ggf. den Regel-3-Folgeeffekt).
    reale_befunde_zeilen = _lies_schluesseltabelle_markdown_zeilen(DATEN_WURZEL / BEFUNDE_MD)
    _schreibe_befunde_md(
        tmp_path / BEFUNDE_MD,
        zeilen=[*reale_befunde_zeilen, befund_regel4, befund_regel1, *befunde_regel3],
    )

    bericht = pruefe_alles(STANDARD_JAHR, daten_wurzel=tmp_path)
    regel1 = next(regel for regel in bericht.regeln if regel.regel == 1)
    regel4 = next(regel for regel in bericht.regeln if regel.regel == 4)
    assert regel4.status == "grün"
    assert regel1.status == "grün"
    assert bericht.ist_gruen is True
    assert len(regel4.bekannte) == 1
    assert regel4.bekannte[0][1].begruendung == "Testabweichung Sollwert"
    assert len(regel1.bekannte) == 1 + len(befunde_teilplan)

    # Ohne passenden Befund bleibt dieselbe Abweichung offen (rot).
    _schreibe_befunde_md(tmp_path / BEFUNDE_MD, zeilen=[])
    bericht_ohne_befund = pruefe_alles(STANDARD_JAHR, daten_wurzel=tmp_path)
    regel4_ohne = next(regel for regel in bericht_ohne_befund.regeln if regel.regel == 4)
    assert regel4_ohne.status == "rot"


def test_konsistenzbericht_wird_geschrieben() -> None:
    bericht = pruefe_alles(STANDARD_JAHR)
    pfad = schreibe_konsistenzbericht(bericht)

    assert pfad == DATEN_WURZEL / KONSISTENZ_MD
    inhalt = pfad.read_text(encoding="utf-8")
    assert inhalt == rendere_konsistenzbericht(bericht)
    for regel in bericht.regeln:
        assert regel.titel in inhalt


def test_konsistenzbericht_unbekannte_seiten_keine_auf_echten_daten() -> None:
    bericht = pruefe_alles(STANDARD_JAHR)
    unbekannte_seiten = getattr(bericht, "unbekannte_seiten", None)
    assert unbekannte_seiten is not None, "Bericht.unbekannte_seiten fehlt"
    assert unbekannte_seiten == ()

    pfad = schreibe_konsistenzbericht(bericht)
    inhalt = pfad.read_text(encoding="utf-8")
    abschnitt = inhalt.split("## Seiten mit typ=unbekannt")
    assert len(abschnitt) == 2, "Abschnitt '## Seiten mit typ=unbekannt' fehlt im Bericht"
    assert "Keine." in abschnitt[1]


def test_konsistenzbericht_unbekannte_seiten_gelistet(tmp_path: Path) -> None:
    seiten = lies_seiten_csv(DATEN_WURZEL / SEITEN_CSV)
    erste_seite = seiten.sort("pdf_seite").row(0, named=True)["pdf_seite"]
    manipuliert = seiten.with_columns(
        pl.when(pl.col("pdf_seite") == erste_seite)
        .then(pl.lit("unbekannt"))
        .otherwise(pl.col("typ"))
        .alias("typ")
    )
    schreibe_seiten_csv(manipuliert, tmp_path / SEITEN_CSV)

    ergebnisplan = lies_plan_csv(DATEN_WURZEL / ERGEBNISPLAN_CSV)
    schreibe_plan_csv(ergebnisplan, tmp_path / ERGEBNISPLAN_CSV)
    _kopiere_finanzplan_nach(tmp_path)
    _kopiere_hierarchie_nach(tmp_path)
    _kopiere_befunde_nach(tmp_path)

    bericht = pruefe_alles(STANDARD_JAHR, daten_wurzel=tmp_path)
    unbekannte_seiten = getattr(bericht, "unbekannte_seiten", None)
    assert unbekannte_seiten is not None, "Bericht.unbekannte_seiten fehlt"
    assert erste_seite in unbekannte_seiten
    # D-17: unbekannt-Seiten sind eine bewusste Ausnahme von D-08 und machen den Bericht
    # nicht rot.
    assert bericht.ist_gruen is True

    pfad = schreibe_konsistenzbericht(bericht)
    inhalt = pfad.read_text(encoding="utf-8")
    abschnitt = inhalt.split("## Seiten mit typ=unbekannt")
    assert len(abschnitt) == 2, "Abschnitt '## Seiten mit typ=unbekannt' fehlt im Bericht"
    assert str(erste_seite) in abschnitt[1]


def test_konsistenzbericht_meldet_abweichung_ueber_einem_euro(tmp_path: Path) -> None:
    sollwerte = lade_sollwerte(STANDARD_JAHR)
    gesamtergebnisplan = sollwerte["gesamtergebnisplan"]
    zeile = next(iter(gesamtergebnisplan["zeilen"]))
    jahr = gesamtergebnisplan["jahre"][0]

    df = lies_plan_csv(DATEN_WURZEL / ERGEBNISPLAN_CSV)
    manipuliert = _manipuliere_betrag(df, zeile=zeile, jahr=jahr, delta=TOLERANZ_EURO + 1)
    schreibe_plan_csv(manipuliert, tmp_path / ERGEBNISPLAN_CSV)
    _kopiere_finanzplan_nach(tmp_path)
    _kopiere_hierarchie_nach(tmp_path)
    _kopiere_seiten_nach(tmp_path)
    _kopiere_befunde_nach(tmp_path)

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
    _kopiere_hierarchie_nach(tmp_path)
    _kopiere_seiten_nach(tmp_path)
    _kopiere_befunde_nach(tmp_path)

    bericht = pruefe_alles(STANDARD_JAHR, daten_wurzel=tmp_path)
    regel4 = next(regel for regel in bericht.regeln if regel.regel == 4)

    assert regel4.status == "grün"
    assert regel4.abweichungen == ()
