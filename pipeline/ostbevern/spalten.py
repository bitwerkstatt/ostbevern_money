"""Gemeinsame x-Koordinaten-Spaltenzuordnung mit Toleranz (Research Pattern 1).

Reine Koordinatenlogik ohne PDF-Zugriff: Aufrufer übergeben bereits extrahierte
Wort-Listen und Anker-x1-Werte. Wird von `querschnitte.py` genutzt und ist für
spätere Parser dieser Phase (Investitionen, Produktinfos) als Vorlage gedacht.
"""

from __future__ import annotations

from collections.abc import Sequence

from ostbevern.pdf import Wort


class SpaltenFehler(ValueError):
    """Wird ausgelöst, wenn ein Wort zu keinem Anker passt oder zwei Wörter denselben
    Anker beanspruchen."""


def ordne_spalten(woerter: Sequence[Wort], anker_x1: Sequence[float]) -> dict[int, Wort]:
    """Ordnet jedes Wort dem nächstgelegenen Anker-Index zu (kleinster |x1-x1|-Abstand).

    Toleranz ist die Hälfte des kleinsten Abstands zwischen benachbarten, nach x1
    sortierten Ankern (unendlich bei nur einem Anker). Ein Wort, dessen Abstand zum
    nächstgelegenen Anker die Toleranz erreicht oder überschreitet, oder das sich einen
    Anker mit einem anderen Wort teilt, löst `SpaltenFehler` aus. Aufrufer entscheiden
    selbst, ob alle Anker belegt sein müssen (Rückgabe kann unvollständig sein).
    """
    sortierte_indices = sorted(range(len(anker_x1)), key=lambda i: anker_x1[i])
    abstaende = [
        abs(anker_x1[sortierte_indices[i]] - anker_x1[sortierte_indices[i - 1]])
        for i in range(1, len(sortierte_indices))
    ]
    toleranz = min(abstaende) / 2 if abstaende else float("inf")

    ergebnis: dict[int, Wort] = {}
    for wort in woerter:
        index = min(range(len(anker_x1)), key=lambda i: abs(wort.x1 - anker_x1[i]))
        abstand = abs(wort.x1 - anker_x1[index])
        if abstand >= toleranz:
            raise SpaltenFehler(
                f"Wort {wort.text!r} (x1={wort.x1:.1f}) passt zu keinem Anker "
                f"(nächster Abstand {abstand:.1f}, Toleranz {toleranz:.1f})"
            )
        if index in ergebnis:
            raise SpaltenFehler(
                f"Zwei Wörter beanspruchen denselben Anker (Index {index}): "
                f"{ergebnis[index].text!r} und {wort.text!r}"
            )
        ergebnis[index] = wort
    return ergebnis
