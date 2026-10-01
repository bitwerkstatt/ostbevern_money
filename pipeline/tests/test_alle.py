"""Tests für den alle.py-Einstiegspunkt (--jahr, Standardjahr, Fehlerfall)."""

from __future__ import annotations

from typer.testing import CliRunner

import alle
from ostbevern.konfiguration import STANDARD_JAHR

runner = CliRunner()


def test_ohne_jahr_nutzt_standardjahr() -> None:
    ergebnis = runner.invoke(alle.app, [])
    assert ergebnis.exit_code == 0
    assert str(STANDARD_JAHR) in ergebnis.output


def test_unbekannter_jahrgang_bricht_ab() -> None:
    ergebnis = runner.invoke(alle.app, ["--jahr", "1"])
    assert ergebnis.exit_code == 1
    ausgabe = (
        ergebnis.output if ergebnis.stderr_bytes is None else ergebnis.output + ergebnis.stderr
    )
    assert "Jahrgangsdatei" in ausgabe
