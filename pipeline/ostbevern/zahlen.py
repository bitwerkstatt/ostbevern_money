"""Zahlen- und Operator-Parser für Planzeilen (EXTR-01).

Reines String-Parsing ohne PDF-Abhängigkeit. Diese Formen deckt Task 1 (02-01):
deutsches Tausenderformat ("1.234.567"), führendes ASCII-Minus, "0". Die übrigen
EXTR-01-Formen (U+2212-Minus, "–" als kein Wert, C/€ als Eurozeichen, angeklebte
Beträge) ergänzt Task 2 test-first (D-07: reine String-Tests).
"""

from __future__ import annotations

import re

_BETRAG_MUSTER = re.compile(r"^-?\d{1,3}(\.\d{3})*$")
_OPERATOR_MUSTER = re.compile(r"^(\+/-|\+|-|=)")


class ZahlenFehler(ValueError):
    """Wird ausgelöst, wenn ein Text kein gültiger Betrag im Plantabellen-Format ist."""


def lies_betrag(text: str) -> int | None:
    """Parst einen gedruckten Betrag zu int-Euro; löst ZahlenFehler bei ungültigem Text aus."""
    bereinigt = text.strip()
    if not _BETRAG_MUSTER.match(bereinigt):
        raise ZahlenFehler(f"Kein gültiger Betrag: {text!r}")
    return int(bereinigt.replace(".", ""))


def ist_betrag(text: str) -> bool:
    """True, wenn `text` ein von lies_betrag akzeptierter Betrag ist (ohne Ausnahme)."""
    try:
        lies_betrag(text)
    except ZahlenFehler:
        return False
    return True


def trenne_operator(wort: str) -> tuple[str | None, str]:
    """Trennt einen angeklebten Operator (+/-, +, -, =) vom Rest; kein Operator ist gültig."""
    treffer = _OPERATOR_MUSTER.match(wort)
    if treffer:
        operator = treffer.group(1)
        return operator, wort[len(operator) :]
    return None, wort


def trenne_angeklebten_betrag(wort: str) -> tuple[str, str | None]:
    """Trennt einen angeklebten Betrag vom Label-Ende ab (Spez. 5.4); GREEN folgt in Task 2."""
    raise NotImplementedError("trenne_angeklebten_betrag: GREEN-Implementierung folgt (RED)")
