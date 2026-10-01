"""Tests für ostbevern.seiten: Seitenklassifikation (D-07, echte PDF-Seiten).

Ein modulweiter Fixture klassifiziert das gesamte PDF genau einmal (~11 s); alle
Tests lesen nur dessen Ergebnis oder gezielt einzelne Seiten nach. Kein Testcode
hält Jahrgangs- oder Seitenzahl-Literale fest (D-08) außer dort, wo eine
bestimmte PDF-Seite selbst Gegenstand des Tests ist.
"""

from __future__ import annotations

import re

import pytest

from ostbevern.konfiguration import STANDARD_JAHR, lade_jahrgang
from ostbevern.pdf import PdfDokument
from ostbevern.seiten import _lies_kopfzeile, klassifiziere_dokument, verbinde_namensteile


@pytest.fixture(scope="module")
def jahrgang():
    return lade_jahrgang(STANDARD_JAHR)


@pytest.fixture(scope="module")
def pdf_dokument(jahrgang):
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        yield dokument


@pytest.fixture(scope="module")
def klassifizierung(jahrgang, pdf_dokument):
    return klassifiziere_dokument(pdf_dokument, jahrgang)


@pytest.fixture(scope="module")
def seiten(klassifizierung):
    return klassifizierung[0]


def test_jede_seite_genau_einmal(seiten, jahrgang) -> None:
    pdf_seiten = [seite.pdf_seite for seite in seiten]
    assert pdf_seiten == list(range(1, jahrgang.anzahlen.pdf_seiten + 1))


def test_kapitelseiten_tragen_kapitelnamen(seiten, jahrgang) -> None:
    for seite in seiten:
        kapitel = None
        for name, bereich in jahrgang.seitenbereiche.items():
            if bereich.von <= seite.pdf_seite <= bereich.bis:
                kapitel = name
                break
        if kapitel is None:
            assert seite.typ == "sonstige"
            assert seite.pb is None
            assert seite.pg is None
            assert seite.produkt is None
        elif kapitel != "teilplaene":
            assert seite.typ == kapitel
            assert seite.pb is None
            assert seite.pg is None
            assert seite.produkt is None


def test_keine_unbekannten_teilplanseiten(seiten) -> None:
    unbekannte = [seite.pdf_seite for seite in seiten if seite.typ == "unbekannt"]
    assert unbekannte == []


def test_jeder_knoten_hat_genau_eine_teilergebnisplanseite(seiten, jahrgang) -> None:
    teilergebnisplan_seiten = [seite for seite in seiten if seite.typ == "teilergebnisplan"]
    knoten = [(seite.pb, seite.pg, seite.produkt) for seite in teilergebnisplan_seiten]
    assert len(knoten) == len(set(knoten))

    pb_knoten = {k for k in knoten if k[1] is None and k[2] is None}
    produkt_knoten = {k for k in knoten if k[2] is not None}
    assert len(pb_knoten) == jahrgang.anzahlen.produktbereiche
    assert len(produkt_knoten) == jahrgang.anzahlen.produkte


def test_produktseiten_tragen_pg_aus_produktcode(seiten) -> None:
    for seite in seiten:
        if seite.produkt is not None:
            assert seite.pg == seite.produkt[:4]


def test_erste_teilplanseite_ist_teilergebnisplan_eines_pb(seiten, jahrgang) -> None:
    bereich = jahrgang.seitenbereiche["teilplaene"]
    erste_seite = next(seite for seite in seiten if seite.pdf_seite == bereich.von)
    assert erste_seite.typ == "teilergebnisplan"
    assert erste_seite.pb is not None
    assert erste_seite.pg is None
    assert erste_seite.produkt is None


def test_fortsetzungsseite_erbt_typ(seiten, jahrgang, pdf_dokument) -> None:
    """Sucht im echten PDF eine Teilplanseite, deren erste Inhaltszeile keinem
    Seitentyp-Muster entspricht, und prüft, dass sie den Typ der Vorgängerseite
    erbt (D-17, Fortsetzungsseite)."""
    bereich = jahrgang.seitenbereiche["teilplaene"]
    gefunden = False
    for index in range(1, len(seiten)):
        seite = seiten[index]
        vorherige = seiten[index - 1]
        if not (bereich.von <= seite.pdf_seite <= bereich.bis):
            continue
        if not (bereich.von <= vorherige.pdf_seite <= bereich.bis):
            continue

        zeilen = pdf_dokument.zeilen(seite.pdf_seite)
        kopf, erste_inhaltszeile_index = _lies_kopfzeile(zeilen, jahrgang, seite.pdf_seite)
        if kopf is None or erste_inhaltszeile_index >= len(zeilen):
            continue
        erste_inhaltszeile = zeilen[erste_inhaltszeile_index].text_ohne_leerzeichen
        passt_muster = any(
            re.match(muster, erste_inhaltszeile)
            for muster in jahrgang.kopfzeilen.seitentypen.values()
        )
        if passt_muster:
            continue

        assert seite.typ == vorherige.typ
        gefunden = True
        break

    assert gefunden, "keine Fortsetzungsseite im Teilplanbereich gefunden"


def test_namensteile_werden_verbunden() -> None:
    # Einfacher Leerzeichen-Join (keine Trennung mitten im Wort).
    assert (
        verbinde_namensteile(
            ["Zentrale Dienste für Organisationseinheiten im", "Hause und Dritter"]
        )
        == "Zentrale Dienste für Organisationseinheiten im Hause und Dritter"
    )
    # Worttrennung am Zeilenumbruch: Bindestrich entfällt, kein Leerzeichen.
    assert (
        verbinde_namensteile(["Räumliche Planung und Entwicklung, Geoinforma-", "tionen"])
        == "Räumliche Planung und Entwicklung, Geoinformationen"
    )
    # Bindestrich vor und/oder bleibt erhalten, mit Leerzeichen verbunden.
    assert (
        verbinde_namensteile(["Natur-", "und Landschaftspflege"]) == "Natur- und Landschaftspflege"
    )
