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

    Toleranz ist pro Wort die Hälfte des Abstands zu den beiden (nach x1 sortierten)
    Nachbar-Ankern des zugeordneten Index (unendlich, wenn dieser Anker keinen Nachbarn
    hat). Diese lokale Berechnung verhindert, dass ein einzelnes doppeltes/identisches
    Anker-Paar (Abstand 0) die Toleranz für die gesamte Tabelle auf 0 drückt und damit
    auch eindeutige Zuordnungen an anderen Ankern verwirft. Ein Wort, dessen Abstand zum
    nächstgelegenen Anker die Toleranz erreicht oder überschreitet, oder das sich einen
    Anker mit einem anderen Wort teilt, löst `SpaltenFehler` aus. Aufrufer entscheiden
    selbst, ob alle Anker belegt sein müssen (Rückgabe kann unvollständig sein).
    """
    sortierte_indices = sorted(range(len(anker_x1)), key=lambda i: anker_x1[i])

    ergebnis: dict[int, Wort] = {}
    for wort in woerter:
        index = min(range(len(anker_x1)), key=lambda i: abs(wort.x1 - anker_x1[i]))
        abstand = abs(wort.x1 - anker_x1[index])
        rang = sortierte_indices.index(index)
        nachbarn = [
            abs(anker_x1[index] - anker_x1[sortierte_indices[i]])
            for i in (rang - 1, rang + 1)
            if 0 <= i < len(sortierte_indices)
        ]
        toleranz = min(nachbarn) / 2 if nachbarn else float("inf")
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
