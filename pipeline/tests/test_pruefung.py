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
    KONSISTENZ_MD,
    PLAN_SPALTEN,
    lies_plan_csv,
    schreibe_plan_csv,
)

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


def test_regel1_sollwerte_gesamtplaene_gruen() -> None:
    bericht = pruefe_alles(STANDARD_JAHR)
    regel1 = next(regel for regel in bericht.regeln if regel.regel == 1)

    # Gesamtergebnisplan: 8 Formelzeilen (10,17,18,21,22,25,26,28) x 6 Spalten = 48.
    # Gesamtfinanzplan: 10 Formelzeilen (09,16,17,23,30,31,32,37,38,41) x 7 Spalten = 70.
    assert regel1.geprueft == 118
    assert regel1.status == "grün"
    assert regel1.abweichungen == ()


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

    df = lies_plan_csv(DATEN_WURZEL / ERGEBNISPLAN_CSV)
    manipuliert = _manipuliere_betrag(df, zeile=zeile_sollwert, jahr=jahr, delta=5)
    schreibe_plan_csv(manipuliert, tmp_path / ERGEBNISPLAN_CSV)
    _kopiere_finanzplan_nach(tmp_path)

    befund_zeile = _befunde_zeile(
        regel=4,
        plan="gesamtergebnisplan",
        ebene="GESAMT",
        code="",
        zeile=zeile_sollwert,
        jahr=jahr,
        wertart="ansatz",
        abweichung=5,
        pdf_seite=62,
        begruendung="Testabweichung",
    )
    _schreibe_befunde_md(tmp_path / BEFUNDE_MD, zeilen=[befund_zeile])

    bericht = pruefe_alles(STANDARD_JAHR, daten_wurzel=tmp_path)
    regel4 = next(regel for regel in bericht.regeln if regel.regel == 4)
    assert regel4.status == "grün"
    assert bericht.ist_gruen is True
    assert len(regel4.bekannte) == 1
    assert regel4.bekannte[0][1].begruendung == "Testabweichung"

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
