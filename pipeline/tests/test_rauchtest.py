"""Rauchtest (D-12): Jahrgangsdatei lädt, PDF existiert mit erwarteter Seitenzahl."""

from __future__ import annotations

import pdfplumber

from ostbevern.konfiguration import STANDARD_JAHR, lade_jahrgang


def test_jahrgangsdatei_laedt() -> None:
    jahrgang = lade_jahrgang(STANDARD_JAHR)
    assert jahrgang.haushaltsjahr == STANDARD_JAHR


def test_pdf_existiert_mit_erwarteter_seitenzahl() -> None:
    jahrgang = lade_jahrgang(STANDARD_JAHR)
    assert jahrgang.pdf_pfad.is_file()
    with pdfplumber.open(jahrgang.pdf_pfad) as pdf:
        assert len(pdf.pages) == jahrgang.anzahlen.pdf_seiten
