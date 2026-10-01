"""Tests für ostbevern.zahlen: reine String-Tests, kein PDF (D-07, EXTR-01).

Die Literale hier sind Parser-Beispiele, keine Jahrgangswerte.
"""

from __future__ import annotations

import pytest

from ostbevern.zahlen import (
    ZahlenFehler,
    ist_betrag,
    lies_betrag,
    trenne_angeklebten_betrag,
    trenne_operator,
)


def test_lies_betrag_deutsches_tausenderformat() -> None:
    assert lies_betrag("1.234.567") == 1234567


def test_lies_betrag_null() -> None:
    assert lies_betrag("0") == 0


def test_lies_betrag_ascii_minus() -> None:
    assert lies_betrag("-214.618") == -214618


def test_lies_betrag_unicode_minus() -> None:
    assert lies_betrag("−600.000") == -600000


def test_lies_betrag_kein_wert_gibt_none() -> None:
    assert lies_betrag("–") is None


def test_lies_betrag_kein_wert_ignoriert_leerzeichen() -> None:
    assert lies_betrag(" – ") is None


def test_lies_betrag_ignoriert_umgebende_leerzeichen() -> None:
    assert lies_betrag("  1.234  ") == 1234


def test_lies_betrag_eurozeichen_c_mit_leerzeichen() -> None:
    assert lies_betrag("66.500 C") == 66500


def test_lies_betrag_eurozeichen_c_angeklebt() -> None:
    assert lies_betrag("66.500C") == 66500


def test_lies_betrag_eurosymbol_angeklebt() -> None:
    assert lies_betrag("66.500€") == 66500


def test_lies_betrag_eurosymbol_mit_leerzeichen() -> None:
    assert lies_betrag("66.500 €") == 66500


@pytest.mark.parametrize(
    "text",
    ["", "abc", "1.23.4", "12,5", "C", "1.234.567,89"],
)
def test_lies_betrag_ungueltige_formen_loesen_zahlenfehler_aus(text: str) -> None:
    with pytest.raises(ZahlenFehler):
        lies_betrag(text)


@pytest.mark.parametrize(
    "text", ["1.234.567", "0", "-214.618", "−600.000", "–", "66.500 C", "66.500€"]
)
def test_ist_betrag_true_fuer_gueltige_formen(text: str) -> None:
    assert ist_betrag(text) is True


@pytest.mark.parametrize("text", ["Personalaufwendungen", "(Z.10+17)", "abc", "12,5"])
def test_ist_betrag_false_fuer_bezeichnungen(text: str) -> None:
    assert ist_betrag(text) is False


def test_trenne_angeklebten_betrag_findet_glued_amount() -> None:
    assert trenne_angeklebten_betrag("Hardware./Fzg.50.126") == ("Hardware./Fzg.", "50.126")


@pytest.mark.parametrize(
    "wort",
    ["Personalaufwendungen", "OrdentlichesErgebnis(Z.10+17)", "Anlagevermö-"],
)
def test_trenne_angeklebten_betrag_ohne_zahl_gibt_none(wort: str) -> None:
    assert trenne_angeklebten_betrag(wort) == (wort, None)


def test_trenne_operator_angeklebt_plus_minus() -> None:
    assert trenne_operator("+/-Bestandsveränderungen") == ("+/-", "Bestandsveränderungen")


def test_trenne_operator_minus_allein() -> None:
    assert trenne_operator("-") == ("-", "")


def test_trenne_operator_gleich_allein() -> None:
    assert trenne_operator("=") == ("=", "")


def test_trenne_operator_kein_operator() -> None:
    assert trenne_operator("SteuernundähnlicheAbgaben") == (None, "SteuernundähnlicheAbgaben")
