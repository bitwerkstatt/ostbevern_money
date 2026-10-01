"""Tests für den alle.py-Einstiegspunkt: Schrittfolge 01 -> 02 -> 06 (D-09)."""

from __future__ import annotations

import dataclasses
from pathlib import Path

import pytest
from typer.testing import CliRunner

import alle
from ostbevern import plaene, pruefung, seiten
from ostbevern.konfiguration import STANDARD_JAHR
from ostbevern.plaene import ExtraktionsErgebnis
from ostbevern.pruefung import Bericht, Pruefpunkt, Regelergebnis
from ostbevern.seiten import KlassifizierungsErgebnis, SeitenFehler

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
        anzahl_seiten=400,
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

    def _pruefe_alles(jahr, **kwargs):  # noqa: ANN001, ANN003, ANN202
        aufzeichnung.reihenfolge.append("pruefe")
        aufzeichnung.jahre["pruefe"] = jahr
        return _gruener_bericht(jahr)

    def _schreibe_konsistenzbericht(bericht, **kwargs):  # noqa: ANN001, ANN003, ANN202
        aufzeichnung.reihenfolge.append("schreibe")
        aufzeichnung.geschriebene_berichte.append(bericht)
        return Path("daten/pruefberichte/konsistenz.md")

    monkeypatch.setattr(seiten, "klassifiziere_seiten", _klassifiziere_seiten)
    monkeypatch.setattr(plaene, "extrahiere_plaene", _extrahiere_plaene)
    monkeypatch.setattr(pruefung, "pruefe_alles", _pruefe_alles)
    monkeypatch.setattr(pruefung, "schreibe_konsistenzbericht", _schreibe_konsistenzbericht)
    return aufzeichnung


def test_ohne_jahr_nutzt_standardjahr(aufrufe: _Aufrufe) -> None:
    ergebnis = runner.invoke(alle.app, [])
    assert ergebnis.exit_code == 0
    assert str(STANDARD_JAHR) in ergebnis.output
    assert aufrufe.reihenfolge == ["seiten", "plaene", "pruefe", "schreibe"]
    assert aufrufe.jahre == {
        "seiten": STANDARD_JAHR,
        "plaene": STANDARD_JAHR,
        "pruefe": STANDARD_JAHR,
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
    assert aufrufe.reihenfolge == ["seiten", "plaene", "pruefe", "schreibe"]
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
