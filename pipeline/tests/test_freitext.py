"""Tests für ostbevern.freitext: Zeilen-Join mit Silbentrennung, Euro-Glyphe (D-10).

Reine Unit-Tests ohne PDF-Zugriff (analog test_zahlen.py).
"""

from __future__ import annotations

from ostbevern.freitext import ersetze_eurozeichen, verbinde_zeilen


def test_verbinde_zeilen_entfernt_trennstrich_vor_kleinbuchstabe() -> None:
    assert (
        verbinde_zeilen(["Auszahl. f. d. Abwickl. Hochbaumaßnah-", "men"])
        == "Auszahl. f. d. Abwickl. Hochbaumaßnahmen"
    )


def test_verbinde_zeilen_behaelt_trennstrich_vor_grossbuchstabe() -> None:
    assert (
        verbinde_zeilen(["Kaufv. Technischen Anlagen/EDV-", "Hardware./Fzg."])
        == "Kaufv. Technischen Anlagen/EDV-Hardware./Fzg."
    )


def test_verbinde_zeilen_behaelt_trennstrich_vor_und_oder_sowie() -> None:
    assert (
        verbinde_zeilen(["Bildungs-, Generationen-", "oder Sozialausschuss"])
        == "Bildungs-, Generationen- oder Sozialausschuss"
    )


def test_verbinde_zeilen_behaelt_trennstrich_bei_personal_und_sachaufwendungen() -> None:
    assert (
        verbinde_zeilen(["Hier nur interne Personal-", "und Sachaufwendungen."])
        == "Hier nur interne Personal- und Sachaufwendungen."
    )


def test_verbinde_zeilen_standalone_trennstrich_am_zeilenende_bleibt() -> None:
    # Ein alleinstehendes "-" (kein Teil eines mind. 2 Zeichen langen Worts) bekommt
    # keine Silbentrennungs-Sonderbehandlung und wird wie jedes andere Wort mit
    # Leerzeichen verbunden.
    assert verbinde_zeilen(["ein Wort -", "nächstes"]) == "ein Wort - nächstes"


def test_verbinde_zeilen_kollabiert_mehrfache_leerzeichen() -> None:
    assert verbinde_zeilen(["  ein   Wort  ", " zweites "]) == "ein Wort zweites"


def test_verbinde_zeilen_einzelne_zeile() -> None:
    assert verbinde_zeilen(["Nur eine Zeile"]) == "Nur eine Zeile"


def test_ersetze_eurozeichen_nach_zahl() -> None:
    assert ersetze_eurozeichen("über 800 C") == "über 800 €"


def test_ersetze_eurozeichen_nicht_nach_zahl_bleibt() -> None:
    assert ersetze_eurozeichen("Kategorie C") == "Kategorie C"


def test_ersetze_eurozeichen_angeklebt_nach_zahl() -> None:
    assert ersetze_eurozeichen("800C") == "800€"


def test_ersetze_eurozeichen_mehrfach() -> None:
    assert ersetze_eurozeichen("100 C und 200 C") == "100 € und 200 €"


def test_verbinde_zeilen_entfernt_leerzeichen_vor_komma() -> None:
    # Feine Extraktion (x_tolerance=1) fügt zwischen zwei direkt angrenzenden Wörtern
    # (z. B. "Leistungen" und ",") beim Join mit " " ein künstliches Leerzeichen ein,
    # das im PDF nicht gedruckt ist (010602, S. 88).
    assert (
        verbinde_zeilen(["Leistungen , die unter anderen Produkten veranschlagt werden:"])
        == "Leistungen, die unter anderen Produkten veranschlagt werden:"
    )
