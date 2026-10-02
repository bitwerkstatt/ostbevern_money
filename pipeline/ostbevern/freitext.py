"""Freitext-Hilfsfunktionen: Zeilen-Join mit Silbentrennung, Euro-Glyphe (D-10).

Reines String-Parsing ohne PDF-Zugriff, analog zu `zahlen.py`: Aufrufer übergeben
bereits aus `ostbevern.pdf.PdfDokument.zeilen_fein` extrahierten und Leerzeichen-
rekonstruierten Zeilentext. Zweck ist die lesbare Fließtext-Rekonstruktion von
Produktinformationen, Namen und Investitionsmaßnahmen-Bezeichnungen (D-10).
"""

from __future__ import annotations

import re
from collections.abc import Sequence

_WHITESPACE_MUSTER = re.compile(r"\s+")
_UND_ODER_SOWIE = ("und", "oder", "sowie")

# Der Euro-Glyph im PDF liest als "C" (Spez. 2.2). Ersetzt wird nur ein Vorkommen, das
# direkt (mit oder ohne Leerzeichen) auf eine gültige Zahl im Plantabellen-Zahlenformat
# folgt ("800 C" oder angeklebt "800C"), nie ein freistehendes "C" in Fließtext (z. B.
# "Kategorie C").
_EUROZEICHEN_NACH_ZAHL_MUSTER = re.compile(r"(?<=\d)(\s?)C(?=\s|$|[^\wÀ-ÖØ-öø-ÿ])")


def verbinde_zeilen(zeilen: Sequence[str]) -> str:
    """Verbindet mehrere Zeilentexte zu lesbarem Fließtext (D-10).

    Jede Zeile wird zuerst getrimmt und ihre inneren Leerzeichen kollabiert. Endet eine
    Zeile (nach dem Trimmen) mit einem Bindestrich, der auf ein mindestens zwei Zeichen
    langes Wort folgt (echte Silbentrennung, kein freistehendes "-"), entscheidet das
    erste Wort der nächsten Zeile: beginnt es mit "und"/"oder"/"sowie", bleibt der
    Bindestrich erhalten und die Zeilen werden mit einem Leerzeichen verbunden
    (Bindestrich-Komposita wie "Bildungs-, Generationen- und ..."); beginnt es mit einem
    Kleinbuchstaben, wird der Bindestrich entfernt und ohne Leerzeichen verbunden (echte
    Worttrennung, z. B. "Hochbaumaßnah-"/"men" -> "Hochbaumaßnahmen"); sonst (Großbuchstabe,
    Ziffer, Satzzeichen) bleibt der Bindestrich erhalten, ohne Leerzeichen verbunden
    ("EDV-"/"Hardware." -> "EDV-Hardware.").
    """
    normalisierte = [_WHITESPACE_MUSTER.sub(" ", zeile.strip()) for zeile in zeilen]
    ergebnis = normalisierte[0]
    for teil in normalisierte[1:]:
        letztes_wort = ergebnis.rsplit(" ", 1)[-1]
        if len(letztes_wort) >= 2 and letztes_wort.endswith("-") and teil:
            erstes_wort_naechste = teil.split(" ", 1)[0]
            if erstes_wort_naechste in _UND_ODER_SOWIE:
                ergebnis = f"{ergebnis} {teil}"
            elif teil[0].islower():
                ergebnis = f"{ergebnis[:-1]}{teil}"
            else:
                ergebnis = f"{ergebnis}{teil}"
        else:
            ergebnis = f"{ergebnis} {teil}" if teil else ergebnis
    return ergebnis


def ersetze_eurozeichen(text: str) -> str:
    """Ersetzt den misslesbaren Euro-Glyphen "C" nach einer Zahl durch "€" (Spez. 2.2).

    Ein "C", das nicht unmittelbar auf eine Ziffer folgt (mit höchstens einem
    trennenden Leerzeichen), bleibt unverändert (z. B. "Kategorie C").
    """
    return _EUROZEICHEN_NACH_ZAHL_MUSTER.sub(r"\1€", text)
