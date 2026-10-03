"""Tests für den alle.py-Einstiegspunkt: Schrittfolge 01 -> 02 -> 03 -> 04 -> Querschnitte
-> 05 -> 06 -> 07 (D-09, D-24)."""

from __future__ import annotations

import dataclasses
from pathlib import Path

import pytest
from typer.testing import CliRunner

import alle
from ostbevern import (
    app_daten,
    investitionen,
    plaene,
    produkte,
    pruefung,
    querschnitte,
    seiten,
    stellenplan,
)
from ostbevern.app_daten import AppDatenFehler
from ostbevern.investitionen import ExtraktionsErgebnis as InvestitionenErgebnis
from ostbevern.investitionen import InvestitionenFehler
from ostbevern.konfiguration import PROJEKT_WURZEL, STANDARD_JAHR
from ostbevern.plaene import ExtraktionsErgebnis
from ostbevern.produkte import ExtraktionsErgebnis as ProdukteErgebnis
from ostbevern.produkte import ProdukteFehler
from ostbevern.pruefung import Bericht, Pruefpunkt, Regelergebnis
from ostbevern.querschnitte import QuerschnitteFehler
from ostbevern.seiten import KlassifizierungsErgebnis, SeitenFehler
from ostbevern.stellenplan import StellenplanFehler

runner = CliRunner()


@dataclasses.dataclass
class _Aufrufe:
    """Zeichnet Reihenfolge und Argumente der monkeypatchten Schritt-Funktionen auf."""

    reihenfolge: list[str] = dataclasses.field(default_factory=list)
    jahre: dict[str, int] = dataclasses.field(default_factory=dict)
    geschriebene_berichte: list[Bericht] = dataclasses.field(default_factory=list)


def _klassifizierungs_ergebnis() -> KlassifizierungsErgebnis:
    return KlassifizierungsErgebnis(
        seiten_pfad=Path("daten/zwischen/seiten.csv"),
        hierarchie_pfad=Path("daten/aufbereitet/hierarchie.csv"),
        anzahl_seiten=42,
        unbekannte_seiten=(),
        anzahl_pb=15,
        anzahl_pg=48,
        anzahl_pg_synthetisch=40,
        anzahl_p=63,
    )


def _extraktions_ergebnisse() -> tuple[ExtraktionsErgebnis, ExtraktionsErgebnis]:
    return (
        ExtraktionsErgebnis(
            zeilen_geschrieben=10128, pfad=Path("daten/aufbereitet/ergebnisplan.csv")
        ),
        ExtraktionsErgebnis(zeilen_geschrieben=4697, pfad=Path("daten/aufbereitet/finanzplan.csv")),
    )


def _produkte_ergebnisse() -> tuple[ProdukteErgebnis, ProdukteErgebnis, ProdukteErgebnis]:
    # alle.py ruft .relative_to(PROJEKT_WURZEL) auf diesen Pfaden auf (wie
    # 03_produktinfos.py); die Fixture braucht deshalb absolute Pfade, wie
    # _investitionen_ergebnisse() unten.
    # Reihenfolge entspricht dem echten Rückgabewert von produkte.extrahiere_produkte:
    # (produkte_ergebnis, grundzahlen_ergebnis, erlaeuterungen_ergebnis).
    return (
        ProdukteErgebnis(
            zeilen_geschrieben=63, pfad=PROJEKT_WURZEL / "daten/aufbereitet/produkte.json"
        ),
        ProdukteErgebnis(
            zeilen_geschrieben=1234, pfad=PROJEKT_WURZEL / "daten/aufbereitet/grundzahlen.csv"
        ),
        ProdukteErgebnis(
            zeilen_geschrieben=229, pfad=PROJEKT_WURZEL / "daten/aufbereitet/erlaeuterungen.csv"
        ),
    )


def _querschnitte_ergebnis() -> ExtraktionsErgebnis:
    return ExtraktionsErgebnis(
        zeilen_geschrieben=1152, pfad=Path("daten/zwischen/querschnitte.csv")
    )


def _stellenplan_ergebnis() -> ExtraktionsErgebnis:
    # alle.py ruft .relative_to(PROJEKT_WURZEL) auf diesem Pfad auf (wie bei investitionen).
    return ExtraktionsErgebnis(
        zeilen_geschrieben=162, pfad=PROJEKT_WURZEL / "daten/aufbereitet/stellenplan.csv"
    )


def _app_daten_ergebnis() -> list[Path]:
    # alle.py ruft .relative_to(PROJEKT_WURZEL) auf diesen Pfaden auf (wie
    # 07_app_daten.py); die Fixture braucht deshalb einen absoluten Pfad, wie
    # _investitionen_ergebnisse() oben.
    return [PROJEKT_WURZEL / "app/src/data/haushalt.json"]


def _investitionen_ergebnisse() -> tuple[InvestitionenErgebnis, InvestitionenErgebnis]:
    # alle.py ruft .relative_to(PROJEKT_WURZEL) auf diesen Pfaden auf (wie
    # 04_investitionen.py); die Fixture braucht deshalb absolute Pfade, anders als die
    # übrigen Schritt-Ergebnisse hier, deren Pfade alle.py nur zählt, nie relativiert.
    return (
        InvestitionenErgebnis(
            zeilen_geschrieben=959,
            pfad=PROJEKT_WURZEL / "daten/aufbereitet/investitionen.csv",
        ),
        InvestitionenErgebnis(
            zeilen_geschrieben=8,
            pfad=PROJEKT_WURZEL / "daten/aufbereitet/ve_faelligkeiten.csv",
        ),
    )


def _gruener_bericht(jahr: int) -> Bericht:
    regel = Regelergebnis(regel=1, titel="Regel 1 – Zeilenformeln", geprueft=1, abweichungen=())
    return Bericht(jahr=jahr, regeln=(regel,))


def _roter_bericht(jahr: int) -> Bericht:
    punkt = Pruefpunkt(
        regel=1,
        plan="gesamtergebnisplan",
        ebene="GESAMT",
        code="",
        zeile="10",
        jahr=jahr,
        wertart="ansatz",
        soll=0,
        ist=10,
        pdf_seite=62,
    )
    regel = Regelergebnis(
        regel=1, titel="Regel 1 – Zeilenformeln", geprueft=1, abweichungen=(punkt,)
    )
    return Bericht(jahr=jahr, regeln=(regel,))


@pytest.fixture
def aufrufe(monkeypatch: pytest.MonkeyPatch) -> _Aufrufe:
    aufzeichnung = _Aufrufe()

    def _klassifiziere_seiten(jahrgang, **kwargs):  # noqa: ANN001, ANN003, ANN202
        aufzeichnung.reihenfolge.append("seiten")
        aufzeichnung.jahre["seiten"] = jahrgang.haushaltsjahr
        return _klassifizierungs_ergebnis()

    def _extrahiere_plaene(jahrgang, **kwargs):  # noqa: ANN001, ANN003, ANN202
        aufzeichnung.reihenfolge.append("plaene")
        aufzeichnung.jahre["plaene"] = jahrgang.haushaltsjahr
        return _extraktions_ergebnisse()

    def _extrahiere_produkte(jahrgang, **kwargs):  # noqa: ANN001, ANN003, ANN202
        aufzeichnung.reihenfolge.append("produkte")
        aufzeichnung.jahre["produkte"] = jahrgang.haushaltsjahr
        return _produkte_ergebnisse()

    def _extrahiere_investitionen(jahrgang, **kwargs):  # noqa: ANN001, ANN003, ANN202
        aufzeichnung.reihenfolge.append("investitionen")
        aufzeichnung.jahre["investitionen"] = jahrgang.haushaltsjahr
        return _investitionen_ergebnisse()

    def _extrahiere_querschnitte(jahrgang, **kwargs):  # noqa: ANN001, ANN003, ANN202
        aufzeichnung.reihenfolge.append("querschnitte")
        aufzeichnung.jahre["querschnitte"] = jahrgang.haushaltsjahr
        return _querschnitte_ergebnis()

    def _extrahiere_stellenplan(jahrgang, **kwargs):  # noqa: ANN001, ANN003, ANN202
        aufzeichnung.reihenfolge.append("stellenplan")
        aufzeichnung.jahre["stellenplan"] = jahrgang.haushaltsjahr
        return _stellenplan_ergebnis()

    def _pruefe_alles(jahr, **kwargs):  # noqa: ANN001, ANN003, ANN202
        aufzeichnung.reihenfolge.append("pruefe")
        aufzeichnung.jahre["pruefe"] = jahr
        return _gruener_bericht(jahr)

    def _schreibe_konsistenzbericht(bericht, **kwargs):  # noqa: ANN001, ANN003, ANN202
        aufzeichnung.reihenfolge.append("schreibe")
        aufzeichnung.geschriebene_berichte.append(bericht)
        return Path("daten/pruefberichte/konsistenz.md")

    def _erzeuge_app_daten(jahr, **kwargs):  # noqa: ANN001, ANN003, ANN202
        aufzeichnung.reihenfolge.append("app_daten")
        aufzeichnung.jahre["app_daten"] = jahr
        return _app_daten_ergebnis()

    monkeypatch.setattr(seiten, "klassifiziere_seiten", _klassifiziere_seiten)
    monkeypatch.setattr(plaene, "extrahiere_plaene", _extrahiere_plaene)
    monkeypatch.setattr(produkte, "extrahiere_produkte", _extrahiere_produkte)
    monkeypatch.setattr(investitionen, "extrahiere_investitionen", _extrahiere_investitionen)
    monkeypatch.setattr(querschnitte, "extrahiere_querschnitte", _extrahiere_querschnitte)
    monkeypatch.setattr(stellenplan, "extrahiere_stellenplan", _extrahiere_stellenplan)
    monkeypatch.setattr(pruefung, "pruefe_alles", _pruefe_alles)
    monkeypatch.setattr(pruefung, "schreibe_konsistenzbericht", _schreibe_konsistenzbericht)
    monkeypatch.setattr(app_daten, "erzeuge_app_daten", _erzeuge_app_daten)
    return aufzeichnung


def test_ohne_jahr_nutzt_standardjahr(aufrufe: _Aufrufe) -> None:
    ergebnis = runner.invoke(alle.app, [])
    assert ergebnis.exit_code == 0
    assert str(STANDARD_JAHR) in ergebnis.output
    assert aufrufe.reihenfolge == [
        "seiten",
        "plaene",
        "produkte",
        "investitionen",
        "querschnitte",
        "stellenplan",
        "pruefe",
        "schreibe",
        "app_daten",
    ]
    assert aufrufe.jahre == {
        "seiten": STANDARD_JAHR,
        "plaene": STANDARD_JAHR,
        "produkte": STANDARD_JAHR,
        "investitionen": STANDARD_JAHR,
        "querschnitte": STANDARD_JAHR,
        "stellenplan": STANDARD_JAHR,
        "pruefe": STANDARD_JAHR,
        "app_daten": STANDARD_JAHR,
    }


def test_unbekannter_jahrgang_bricht_ab(aufrufe: _Aufrufe) -> None:
    ergebnis = runner.invoke(alle.app, ["--jahr", "1"])
    assert ergebnis.exit_code == 1
    ausgabe = (
        ergebnis.output if ergebnis.stderr_bytes is None else ergebnis.output + ergebnis.stderr
    )
    assert "Jahrgangsdatei" in ausgabe
    assert aufrufe.reihenfolge == []


def test_roter_bericht_beendet_mit_fehler(
    aufrufe: _Aufrufe, monkeypatch: pytest.MonkeyPatch
) -> None:
    def _rot(jahr, **kwargs):  # noqa: ANN001, ANN003, ANN202
        aufrufe.reihenfolge.append("pruefe")
        return _roter_bericht(jahr)

    monkeypatch.setattr(pruefung, "pruefe_alles", _rot)

    ergebnis = runner.invoke(alle.app, [])
    assert ergebnis.exit_code == 1
    # Der Bericht wird trotz Fehlerabbruch geschrieben (D-01: Transparenz über rote Berichte).
    assert aufrufe.reihenfolge == [
        "seiten",
        "plaene",
        "produkte",
        "investitionen",
        "querschnitte",
        "stellenplan",
        "pruefe",
        "schreibe",
    ]
    assert len(aufrufe.geschriebene_berichte) == 1


def test_schrittfehler_beendet_mit_fehler(
    aufrufe: _Aufrufe, monkeypatch: pytest.MonkeyPatch
) -> None:
    def _bricht_ab(jahrgang, **kwargs):  # noqa: ANN001, ANN003, ANN202
        raise SeitenFehler("Testfehler: Seite nicht lesbar")

    monkeypatch.setattr(seiten, "klassifiziere_seiten", _bricht_ab)

    ergebnis = runner.invoke(alle.app, [])
    assert ergebnis.exit_code == 1
    ausgabe = (
        ergebnis.output if ergebnis.stderr_bytes is None else ergebnis.output + ergebnis.stderr
    )
    assert "Fehler:" in ausgabe
    # plaene und pruefung wurden nicht aufgerufen (D-09: Abbruch nach dem ersten Fehler).
    assert aufrufe.reihenfolge == []


def test_produktfehler_beendet_mit_fehler(
    aufrufe: _Aufrufe, monkeypatch: pytest.MonkeyPatch
) -> None:
    def _bricht_ab(jahrgang, **kwargs):  # noqa: ANN001, ANN003, ANN202
        aufrufe.reihenfolge.append("produkte")
        raise ProdukteFehler("Testfehler: Produktinformationen nicht lesbar")

    monkeypatch.setattr(produkte, "extrahiere_produkte", _bricht_ab)

    ergebnis = runner.invoke(alle.app, [])
    assert ergebnis.exit_code == 1
    ausgabe = (
        ergebnis.output if ergebnis.stderr_bytes is None else ergebnis.output + ergebnis.stderr
    )
    assert "Fehler:" in ausgabe
    # investitionen, querschnitte und pruefung wurden nicht aufgerufen
    # (D-09: Abbruch nach dem ersten Fehler).
    assert aufrufe.reihenfolge == ["seiten", "plaene", "produkte"]


def test_investitionsfehler_beendet_mit_fehler(
    aufrufe: _Aufrufe, monkeypatch: pytest.MonkeyPatch
) -> None:
    def _bricht_ab(jahrgang, **kwargs):  # noqa: ANN001, ANN003, ANN202
        aufrufe.reihenfolge.append("investitionen")
        raise InvestitionenFehler("Testfehler: Investitionsmaßnahme nicht lesbar")

    monkeypatch.setattr(investitionen, "extrahiere_investitionen", _bricht_ab)

    ergebnis = runner.invoke(alle.app, [])
    assert ergebnis.exit_code == 1
    ausgabe = (
        ergebnis.output if ergebnis.stderr_bytes is None else ergebnis.output + ergebnis.stderr
    )
    assert "Fehler:" in ausgabe
    # querschnitte und pruefung wurden nicht aufgerufen (D-09: Abbruch nach dem ersten Fehler).
    assert aufrufe.reihenfolge == ["seiten", "plaene", "produkte", "investitionen"]


def test_querschnittfehler_beendet_mit_fehler(
    aufrufe: _Aufrufe, monkeypatch: pytest.MonkeyPatch
) -> None:
    def _bricht_ab(jahrgang, **kwargs):  # noqa: ANN001, ANN003, ANN202
        aufrufe.reihenfolge.append("querschnitte")
        raise QuerschnitteFehler("Testfehler: Querschnitt nicht lesbar")

    monkeypatch.setattr(querschnitte, "extrahiere_querschnitte", _bricht_ab)

    ergebnis = runner.invoke(alle.app, [])
    assert ergebnis.exit_code == 1
    ausgabe = (
        ergebnis.output if ergebnis.stderr_bytes is None else ergebnis.output + ergebnis.stderr
    )
    assert "Fehler:" in ausgabe
    # pruefung wurde nicht aufgerufen (D-09: Abbruch nach dem ersten Fehler).
    assert aufrufe.reihenfolge == ["seiten", "plaene", "produkte", "investitionen", "querschnitte"]


def test_stellenplanfehler_beendet_mit_fehler(
    aufrufe: _Aufrufe, monkeypatch: pytest.MonkeyPatch
) -> None:
    def _bricht_ab(jahrgang, **kwargs):  # noqa: ANN001, ANN003, ANN202
        aufrufe.reihenfolge.append("stellenplan")
        raise StellenplanFehler("Testfehler: Stellenplan nicht lesbar")

    monkeypatch.setattr(stellenplan, "extrahiere_stellenplan", _bricht_ab)

    ergebnis = runner.invoke(alle.app, [])
    assert ergebnis.exit_code == 1
    ausgabe = (
        ergebnis.output if ergebnis.stderr_bytes is None else ergebnis.output + ergebnis.stderr
    )
    assert "Fehler:" in ausgabe
    # pruefung wurde nicht aufgerufen (D-09: Abbruch nach dem ersten Fehler).
    assert aufrufe.reihenfolge == [
        "seiten",
        "plaene",
        "produkte",
        "investitionen",
        "querschnitte",
        "stellenplan",
    ]


def test_roter_bericht_ruft_app_daten_nicht_auf(
    aufrufe: _Aufrufe, monkeypatch: pytest.MonkeyPatch
) -> None:
    def _rot(jahr, **kwargs):  # noqa: ANN001, ANN003, ANN202
        aufrufe.reihenfolge.append("pruefe")
        return _roter_bericht(jahr)

    monkeypatch.setattr(pruefung, "pruefe_alles", _rot)

    ergebnis = runner.invoke(alle.app, [])
    assert ergebnis.exit_code == 1
    # Schritt 07 läuft nur nach einem grünen Bericht (D-24); der Bericht wird trotzdem
    # geschrieben (D-01: Transparenz über rote Berichte).
    assert aufrufe.reihenfolge == [
        "seiten",
        "plaene",
        "produkte",
        "investitionen",
        "querschnitte",
        "stellenplan",
        "pruefe",
        "schreibe",
    ]
    assert "app_daten" not in aufrufe.reihenfolge


def test_app_daten_fehler_beendet_mit_fehler(
    aufrufe: _Aufrufe, monkeypatch: pytest.MonkeyPatch
) -> None:
    def _bricht_ab(jahr, **kwargs):  # noqa: ANN001, ANN003, ANN202
        aufrufe.reihenfolge.append("app_daten")
        raise AppDatenFehler("Testfehler: App-Daten nicht erzeugbar")

    monkeypatch.setattr(app_daten, "erzeuge_app_daten", _bricht_ab)

    ergebnis = runner.invoke(alle.app, [])
    assert ergebnis.exit_code == 1
    ausgabe = (
        ergebnis.output if ergebnis.stderr_bytes is None else ergebnis.output + ergebnis.stderr
    )
    assert "Fehler:" in ausgabe
    assert aufrufe.reihenfolge == [
        "seiten",
        "plaene",
        "produkte",
        "investitionen",
        "querschnitte",
        "stellenplan",
        "pruefe",
        "schreibe",
        "app_daten",
    ]
