"""Tests für ostbevern.seiten: Seitenklassifikation (D-07, echte PDF-Seiten).

Ein modulweiter Fixture klassifiziert das gesamte PDF genau einmal (~11 s); alle
Tests lesen nur dessen Ergebnis oder gezielt einzelne Seiten nach. Kein Testcode
hält Jahrgangs- oder Seitenzahl-Literale fest (D-08) außer dort, wo eine
bestimmte PDF-Seite selbst Gegenstand des Tests ist.
"""

from __future__ import annotations

import dataclasses
import re

import polars as pl
import pytest

from ostbevern.konfiguration import STANDARD_JAHR, SynthetischeProduktgruppe, lade_jahrgang
from ostbevern.pdf import PdfDokument
from ostbevern.seiten import (
    Seite,
    SeitenFehler,
    Seitenkopf,
    _lies_kopfzeile,
    baue_hierarchie,
    klassifiziere_dokument,
    verbinde_namensteile,
)


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


def test_produktseiten_tragen_pg_aus_produktcode_oder_jahrgangsdeklaration(
    seiten, jahrgang
) -> None:
    """Die PG einer Produktseite ist der deklarierte Code aus
    jahrgang.synthetische_produktgruppen, falls das Produkt dort als `produkt`
    auftaucht (D-14), sonst der Standard (die ersten vier Ziffern des Produktcodes).
    Berechnet unabhängig von der Produktionslogik, nicht über den Helfer selbst."""
    deklarierte_produkte = {
        eintrag.produkt: code for code, eintrag in jahrgang.synthetische_produktgruppen.items()
    }
    for seite in seiten:
        if seite.produkt is not None:
            erwartet = deklarierte_produkte.get(seite.produkt, seite.produkt[:4])
            assert seite.pg == erwartet


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


# baue_hierarchie mit konstruierten Seiten/Köpfen (D-08, D-14, 261001-oim): prüft die
# Validierung von [synthetische_produktgruppen]-Deklarationen gegen die extrahierte
# Hierarchie. Nutzt NICHT die modulweiten PDF-Fixtures (läuft ohne das PDF zu öffnen),
# nur die reine `jahrgang`-Fixture. Produktbereich "99" ist frei erfunden (Präzedenzfall
# test_pruefung.py), Seitenzahlen basieren auf jahrgang.seitenbereiche["teilplaene"].von.


def _konstruierter_jahrgang(jahrgang, *, anzahl_pb, anzahl_produkte, synthetische_produktgruppen):
    return dataclasses.replace(
        jahrgang,
        anzahlen=dataclasses.replace(
            jahrgang.anzahlen, produktbereiche=anzahl_pb, produkte=anzahl_produkte
        ),
        synthetische_produktgruppen=synthetische_produktgruppen,
    )


def _konstruierte_seiten(jahrgang, koepfe_je_offset):
    """koepfe_je_offset: Liste von (Offset, Seitenkopf). pdf_seite ist
    jahrgang.seitenbereiche['teilplaene'].von + Offset."""
    basis = jahrgang.seitenbereiche["teilplaene"].von
    seiten = []
    koepfe = {}
    for offset, kopf in koepfe_je_offset:
        seite_nr = basis + offset
        seiten.append(
            Seite(pdf_seite=seite_nr, typ="teilergebnisplan", pb=None, pg=None, produkt=None)
        )
        koepfe[seite_nr] = kopf
    return tuple(seiten), koepfe


def test_baue_hierarchie_kollision_ohne_deklaration_meldet_beide_produkte(jahrgang) -> None:
    """Zwei Produkte, die ohne Deklaration auf denselben synthetischen PG-Code auflösen
    (D-14 "genau ein Produkt"), sind ein SeitenFehler, der beide Produktcodes nennt."""
    koepfe_je_offset = [
        (
            0,
            Seitenkopf(
                pb="99",
                pb_name="Testbereich",
                pg=None,
                pg_name=None,
                produkt="990101",
                produkt_name="ProduktEins",
            ),
        ),
        (
            1,
            Seitenkopf(
                pb="99",
                pb_name="Testbereich",
                pg=None,
                pg_name=None,
                produkt="990102",
                produkt_name="ProduktZwei",
            ),
        ),
    ]
    seiten, koepfe = _konstruierte_seiten(jahrgang, koepfe_je_offset)
    jahrgang_konstr = _konstruierter_jahrgang(
        jahrgang, anzahl_pb=1, anzahl_produkte=2, synthetische_produktgruppen={}
    )

    with pytest.raises(SeitenFehler, match="990101") as exc_info:
        baue_hierarchie(seiten, koepfe, jahrgang_konstr)
    assert "990102" in str(exc_info.value)


def test_baue_hierarchie_deklaration_mit_unbekanntem_produkt_wird_abgelehnt(jahrgang) -> None:
    """Eine Deklaration, deren produkt nicht unter den extrahierten P-Knoten ist, ist
    ein SeitenFehler (D-08)."""
    koepfe_je_offset = [
        (
            0,
            Seitenkopf(
                pb="99",
                pb_name="Testbereich",
                pg=None,
                pg_name=None,
                produkt="990101",
                produkt_name="ProduktEins",
            ),
        ),
    ]
    seiten, koepfe = _konstruierte_seiten(jahrgang, koepfe_je_offset)
    synthetische = {
        "9901": SynthetischeProduktgruppe(code="9901", produkt="990199", name="Falsch", pdf_seite=1)
    }
    jahrgang_konstr = _konstruierter_jahrgang(
        jahrgang, anzahl_pb=1, anzahl_produkte=1, synthetische_produktgruppen=synthetische
    )

    with pytest.raises(SeitenFehler, match="990199"):
        baue_hierarchie(seiten, koepfe, jahrgang_konstr)


def test_baue_hierarchie_deklaration_fuer_produkt_in_gedruckter_pg_wird_abgelehnt(
    jahrgang,
) -> None:
    """Eine Deklaration, deren produkt bereits zu einer gedruckten PG gehört, ist ein
    SeitenFehler (D-08) — eine solche Zuordnung kann nie zu einer synthetischen PG
    führen."""
    koepfe_je_offset = [
        (
            0,
            Seitenkopf(
                pb="99",
                pb_name="Testbereich",
                pg="9902",
                pg_name="Gedruckt",
                produkt=None,
                produkt_name=None,
            ),
        ),
        (
            1,
            Seitenkopf(
                pb="99",
                pb_name="Testbereich",
                pg=None,
                pg_name=None,
                produkt="990201",
                produkt_name="ProduktDrei",
            ),
        ),
    ]
    seiten, koepfe = _konstruierte_seiten(jahrgang, koepfe_je_offset)
    synthetische = {
        "9903": SynthetischeProduktgruppe(code="9903", produkt="990201", name="Y", pdf_seite=1)
    }
    jahrgang_konstr = _konstruierter_jahrgang(
        jahrgang, anzahl_pb=1, anzahl_produkte=1, synthetische_produktgruppen=synthetische
    )

    with pytest.raises(SeitenFehler, match="990201"):
        baue_hierarchie(seiten, koepfe, jahrgang_konstr)


def test_baue_hierarchie_deklarierter_code_ist_gedruckte_pg_wird_abgelehnt(jahrgang) -> None:
    """Eine Deklaration, deren Code bereits eine gedruckte PG ist, ist ein SeitenFehler
    (D-08) — der Code steht schon für eine andere, gedruckte Produktgruppe."""
    koepfe_je_offset = [
        (
            0,
            Seitenkopf(
                pb="99",
                pb_name="Testbereich",
                pg="9902",
                pg_name="Gedruckt",
                produkt=None,
                produkt_name=None,
            ),
        ),
        (
            1,
            Seitenkopf(
                pb="99",
                pb_name="Testbereich",
                pg=None,
                pg_name=None,
                produkt="990201",
                produkt_name="ProduktDrei",
            ),
        ),
        (
            2,
            Seitenkopf(
                pb="99",
                pb_name="Testbereich",
                pg=None,
                pg_name=None,
                produkt="990301",
                produkt_name="ProduktVier",
            ),
        ),
    ]
    seiten, koepfe = _konstruierte_seiten(jahrgang, koepfe_je_offset)
    synthetische = {
        "9902": SynthetischeProduktgruppe(code="9902", produkt="990301", name="Z", pdf_seite=1)
    }
    jahrgang_konstr = _konstruierter_jahrgang(
        jahrgang, anzahl_pb=1, anzahl_produkte=2, synthetische_produktgruppen=synthetische
    )

    with pytest.raises(SeitenFehler, match="9902"):
        baue_hierarchie(seiten, koepfe, jahrgang_konstr)


def test_baue_hierarchie_gueltige_deklaration_ergibt_deklarierte_pg(jahrgang) -> None:
    """Eine gültige Deklaration ergibt eine synthetische PG mit dem deklarierten Code,
    dem deklarierten Namen und der Startseite des Produkts (D-14)."""
    koepfe_je_offset = [
        (
            0,
            Seitenkopf(
                pb="99",
                pb_name="Testbereich",
                pg=None,
                pg_name=None,
                produkt="990101",
                produkt_name="ProduktEins",
            ),
        ),
    ]
    seiten, koepfe = _konstruierte_seiten(jahrgang, koepfe_je_offset)
    synthetische = {
        "9999": SynthetischeProduktgruppe(
            code="9999", produkt="990101", name="MeinName", pdf_seite=42
        )
    }
    jahrgang_konstr = _konstruierter_jahrgang(
        jahrgang, anzahl_pb=1, anzahl_produkte=1, synthetische_produktgruppen=synthetische
    )

    hierarchie = baue_hierarchie(seiten, koepfe, jahrgang_konstr)
    pg_zeile = hierarchie.filter((pl.col("ebene") == "PG") & (pl.col("code") == "9999")).row(
        0, named=True
    )
    assert pg_zeile["name"] == "MeinName"
    assert pg_zeile["synthetisch"] is True
    assert pg_zeile["eltern_code"] == "99"
    erwartete_startseite = jahrgang.seitenbereiche["teilplaene"].von
    assert pg_zeile["pdf_seite_start"] == erwartete_startseite
