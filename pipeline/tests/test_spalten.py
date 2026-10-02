"""Tests für ostbevern.spalten: x-Koordinaten-Zuordnung mit Toleranz (Research Pattern 1).

Rein konstruierte Wort-Objekte, kein PDF-Zugriff.
"""

from __future__ import annotations

import pytest

from ostbevern.pdf import Wort
from ostbevern.spalten import SpaltenFehler, ordne_spalten


def _wort(text: str, x1: float) -> Wort:
    return Wort(text=text, x0=x1 - 10.0, x1=x1, top=0.0, groesse=8.0)


def test_ordne_spalten_exakte_zuordnung() -> None:
    anker = [100.0, 200.0, 300.0]
    woerter = [_wort("a", 100.0), _wort("b", 200.0), _wort("c", 300.0)]
    ergebnis = ordne_spalten(woerter, anker)
    assert {index: wort.text for index, wort in ergebnis.items()} == {0: "a", 1: "b", 2: "c"}


def test_ordne_spalten_wort_ausserhalb_toleranz_bricht_ab() -> None:
    anker = [100.0, 200.0, 300.0]  # Toleranz = min(100, 100) / 2 = 50
    woerter = [_wort("x", 150.0)]  # genau mittig zwischen Anker 0/1: Abstand 50 >= Toleranz
    with pytest.raises(SpaltenFehler):
        ordne_spalten(woerter, anker)


def test_ordne_spalten_zwei_woerter_auf_einem_anker_bricht_ab() -> None:
    anker = [100.0, 200.0]
    woerter = [_wort("a", 101.0), _wort("b", 99.0)]
    with pytest.raises(SpaltenFehler):
        ordne_spalten(woerter, anker)


def test_ordne_spalten_teilweise_zuordnung() -> None:
    anker = [100.0, 200.0, 300.0]
    woerter = [_wort("a", 100.0), _wort("c", 300.0)]
    ergebnis = ordne_spalten(woerter, anker)
    assert set(ergebnis) == {0, 2}
    assert ergebnis[0].text == "a"
    assert ergebnis[2].text == "c"


def test_ordne_spalten_einzelner_anker_hat_unendliche_toleranz() -> None:
    anker = [500.0]
    woerter = [_wort("weit_weg", 0.0)]
    ergebnis = ordne_spalten(woerter, anker)
    assert ergebnis[0].text == "weit_weg"


def test_ordne_spalten_doppelter_anker_bricht_nicht_die_ganze_zuordnung() -> None:
    # Zwei Anker mit demselben x1 (z. B. eine leere/zusammengeführte Spalte) duerfen die
    # Toleranz nicht global auf 0 druecken: ein Wort an einem dritten, eindeutigen Anker
    # muss trotzdem zugeordnet werden (Regressionstest zu WR-01).
    anker = [100.0, 100.0, 500.0]
    woerter = [_wort("c", 500.0)]
    ergebnis = ordne_spalten(woerter, anker)
    assert ergebnis[2].text == "c"
