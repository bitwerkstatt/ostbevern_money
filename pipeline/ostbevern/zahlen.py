"""Zahlen- und Operator-Parser für Planzeilen (EXTR-01) und Grundzahlen (EXTR-07).

Reines String-Parsing ohne PDF-Abhängigkeit. Deckt alle EXTR-01-Formen: deutsches
Tausenderformat ("1.234.567"), ASCII- und U+2212-Minus, "–" (U+2013) als kein Wert,
C/€ als angeklebtes oder durch Leerzeichen getrenntes Eurozeichen, sowie angeklebte
Beträge am Label-Ende (Spez. 3.8, 5.4). Plan-Beträge sind int-Euro, ausschließlich über
`lies_betrag`; Dezimalzahlen (Grundzahlen-Kennzahlen wie Gebühren, Quoten, Phase 3
EXTR-07) werden ausschließlich über `lies_kennzahl` gelesen, das als Float64 plus
printed-Nachkommastellen zurückgibt. `lies_betrag` bleibt int-only und lehnt jeden
Dezimalwert mit Komma weiterhin als ZahlenFehler ab.
"""

from __future__ import annotations

import re

_BETRAG_MUSTER = re.compile(r"^-?\d{1,3}(\.\d{3})*$")
# Wie _BETRAG_MUSTER, zusätzlich ein optionaler Dezimalteil (Komma + mind. eine Ziffer,
# EXTR-07 Grundzahlen-Kennzahlen: Gebühren, Quoten; nie Teil von lies_betrag).
_KENNZAHL_MUSTER = re.compile(r"^-?\d{1,3}(\.\d{3})*(,\d+)?$")
_OPERATOR_MUSTER = re.compile(r"^(\+/-|\+|-|=)")
_EUROZEICHEN_MUSTER = re.compile(r"[ \t]*[C€]$")
_UNICODE_MINUS = "−"
_KEIN_WERT = "–"

# Trennt einen angeklebten Betrag vom Label-Ende: der letzte Buchstabe, Punkt,
# Schrägstrich oder die letzte schließende Klammer vor der Ziffernfolge markiert den
# Übergang (Spez. 5.4). Lazy `.*?` findet die LINKESTE gültige Trennstelle, also den
# LÄNGSTEN zusammenhängenden Betrag am Ende (z. B. "50.126", nicht nur "126").
_ANGEKLEBTER_BETRAG_MUSTER = re.compile(
    r"^(?P<rest>.*?[A-Za-zÀ-ÖØ-öø-ÿ.)/])(?P<betrag>-?\d{1,3}(?:\.\d{3})*)$"
)


class ZahlenFehler(ValueError):
    """Wird ausgelöst, wenn ein Text kein gültiger Betrag im Plantabellen-Format ist."""


def lies_betrag(text: str) -> int | None:
    """Parst einen gedruckten Betrag zu int-Euro; löst ZahlenFehler bei ungültigem Text aus.

    "–" (U+2013, kein Wert) ergibt None. Ein angeklebtes oder durch Leerzeichen
    getrenntes "C"/"€" wird als Eurozeichen entfernt, U+2212 als Minus interpretiert.
    """
    bereinigt = text.strip()
    if bereinigt == _KEIN_WERT:
        return None
    ohne_eurozeichen = _EUROZEICHEN_MUSTER.sub("", bereinigt).strip()
    normalisiert = ohne_eurozeichen.replace(_UNICODE_MINUS, "-")
    if not _BETRAG_MUSTER.match(normalisiert):
        raise ZahlenFehler(f"Kein gültiger Betrag: {text!r}")
    return int(normalisiert.replace(".", ""))


def lies_kennzahl(text: str) -> tuple[float, int] | None:
    """Parst eine gedruckte Grundzahlen-Kennzahl zu (Wert, Nachkommastellen) (EXTR-07).

    Deckt deutsches Tausenderformat mit optionalem Dezimalteil (Komma, mind. eine
    Ziffer) ab, z. B. "4.771.497" -> (4771497.0, 0), "2,82" -> (2.82, 2). "–"
    (U+2013, kein Wert) ergibt None, wie bei `lies_betrag`. ASCII- und U+2212-Minus
    werden wie in `lies_betrag` interpretiert. Jeder andere Text (z. B. ein
    Datumsformat wie "30.06." oder mehr als ein Komma) löst ZahlenFehler aus.
    """
    bereinigt = text.strip()
    if bereinigt == _KEIN_WERT:
        return None
    normalisiert = bereinigt.replace(_UNICODE_MINUS, "-")
    if not _KENNZAHL_MUSTER.match(normalisiert):
        raise ZahlenFehler(f"Keine gültige Kennzahl: {text!r}")
    if "," in normalisiert:
        ganzzahl_teil, dezimal_teil = normalisiert.split(",")
    else:
        ganzzahl_teil, dezimal_teil = normalisiert, ""
    ganzzahl_ohne_punkte = ganzzahl_teil.replace(".", "")
    nachkommastellen = len(dezimal_teil)
    wert = (
        float(f"{ganzzahl_ohne_punkte}.{dezimal_teil}")
        if dezimal_teil
        else float(ganzzahl_ohne_punkte)
    )
    return wert, nachkommastellen


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
    """Trennt einen angeklebten Betrag vom Label-Ende ab (Spez. 3.8, 5.4).

    Gibt (wort, None) zurück, wenn `wort` nicht mit einem gültigen, an einen
    Buchstaben/Punkt/Schrägstrich/einer schließenden Klammer angeklebten
    Tausenderformat-Betrag endet. Diese Funktion kennt keine Spaltenposition und
    trennt jeden passenden Text, auch reine Bezeichnungen mit zufällig angeklebter
    Zahl (z. B. "AVüber800"). Aufrufer wenden sie deshalb nur auf Wörter an, deren
    x1 in der Betragsspaltenzone liegt (plaene.lies_plantabelle).
    """
    treffer = _ANGEKLEBTER_BETRAG_MUSTER.match(wort)
    if treffer:
        return treffer.group("rest"), treffer.group("betrag")
    return wort, None
