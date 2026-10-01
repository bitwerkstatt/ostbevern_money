"""Tests für ostbevern.querschnitte: Koordinaten-Extraktion der Haushaltsquerschnitte
S. 291-300 (PRUEF-07, D-14, D-15).

Liest nur das Original-PDF, nie daten/. Keine Jahrgangs-, Seiten- oder
Sollwert-Literale – alles kommt aus lade_jahrgang(STANDARD_JAHR),
lade_sollwerte(STANDARD_JAHR) oder der pdf_klassifikation-Fixture.
"""

from __future__ import annotations

import polars as pl
import pytest

from ostbevern.konfiguration import (
    STANDARD_JAHR,
    Jahrgang,
    lade_sollwerte,
    layout_liste,
)
from ostbevern.pdf import PdfDokument
from ostbevern.querschnitte import Querschnittwert, lies_querschnitte


@pytest.fixture(scope="module")
def querschnittwerte(jahrgang: Jahrgang) -> tuple[Querschnittwert, ...]:
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        return tuple(lies_querschnitte(dokument, jahrgang))


def _als_dataframe(werte: tuple[Querschnittwert, ...]) -> pl.DataFrame:
    return pl.DataFrame(
        [
            {
                "pb": w.pb,
                "pg": w.pg,
                "gesamtsumme": w.gesamtsumme,
                "plan": w.plan,
                "kennzahl": w.kennzahl,
                "betrag": w.betrag,
                "pdf_seite": w.pdf_seite,
            }
            for w in werte
        ]
    )


def test_querschnitte_alle_pb_beide_plaene(
    querschnittwerte: tuple[Querschnittwert, ...],
    pdf_klassifikation: tuple[pl.DataFrame, pl.DataFrame],
    jahrgang: Jahrgang,
) -> None:
    """Jede PB von hierarchie.csv hat beide Plantypen, genau eine GESAMTSUMME je Plan,
    und jede (pb, pg|GESAMTSUMME, plan)-Zeile hat genau len(kennzahlen_<plan>) Werte."""
    _seiten_df, hierarchie_df = pdf_klassifikation
    df = _als_dataframe(querschnittwerte)
    pb_codes = set(hierarchie_df.filter(pl.col("ebene") == "PB")["code"].to_list())
    anzahl_kennzahlen = {
        "ergebnisplan": len(layout_liste(jahrgang, "querschnitte", "kennzahlen_ergebnisplan")),
        "finanzplan": len(layout_liste(jahrgang, "querschnitte", "kennzahlen_finanzplan")),
    }

    assert set(df["pb"].unique().to_list()) == pb_codes

    for pb in pb_codes:
        for plan in ("ergebnisplan", "finanzplan"):
            teilmenge = df.filter((pl.col("pb") == pb) & (pl.col("plan") == plan))
            assert teilmenge.height > 0, (pb, plan)

            gesamtsumme = teilmenge.filter(pl.col("gesamtsumme"))
            assert gesamtsumme.height == anzahl_kennzahlen[plan], (pb, plan)
            assert gesamtsumme["pg"].null_count() == gesamtsumme.height, (pb, plan)

            for _pg, gruppe in teilmenge.filter(~pl.col("gesamtsumme")).group_by("pg"):
                assert gruppe.height == anzahl_kennzahlen[plan], (pb, plan, _pg)


def test_querschnitte_pg_menge_wie_hierarchie(
    querschnittwerte: tuple[Querschnittwert, ...],
    pdf_klassifikation: tuple[pl.DataFrame, pl.DataFrame],
) -> None:
    """Je PB und Plantyp entspricht die Menge der gefundenen PG-Codes genau den PG-Kindern
    dieser PB in hierarchie.csv (gedruckt und synthetisch)."""
    _seiten_df, hierarchie_df = pdf_klassifikation
    df = _als_dataframe(querschnittwerte)
    pb_codes = sorted(hierarchie_df.filter(pl.col("ebene") == "PB")["code"].to_list())

    for pb in pb_codes:
        erwartete_pg = set(
            hierarchie_df.filter((pl.col("ebene") == "PG") & (pl.col("eltern_code") == pb))[
                "code"
            ].to_list()
        )
        for plan in ("ergebnisplan", "finanzplan"):
            gefundene_pg = set(
                df.filter((pl.col("pb") == pb) & (pl.col("plan") == plan) & ~pl.col("gesamtsumme"))[
                    "pg"
                ].to_list()
            )
            assert gefundene_pg == erwartete_pg, (pb, plan)


def test_querschnitte_trifft_sollwert_haushaltsquerschnitt_pg(
    querschnittwerte: tuple[Querschnittwert, ...],
) -> None:
    """Für jede PG in lade_sollwerte()["haushaltsquerschnitt_pg"] entspricht der Querschnitt-
    wert von Kennzahl "ergebnis_teilhaushalt" dem Sollwert und der pdf_seite (D-14)."""
    sollwerte = lade_sollwerte(STANDARD_JAHR)
    haushaltsquerschnitt_pg = sollwerte.get("haushaltsquerschnitt_pg", {})
    assert haushaltsquerschnitt_pg, "Sollwertdatei hat keine [haushaltsquerschnitt_pg]-Einträge"

    df = _als_dataframe(querschnittwerte)
    for pg_code, eintrag in haushaltsquerschnitt_pg.items():
        treffer = df.filter(
            (pl.col("pg") == pg_code)
            & (pl.col("plan") == "ergebnisplan")
            & (pl.col("kennzahl") == "ergebnis_teilhaushalt")
            & (~pl.col("gesamtsumme"))
        )
        assert treffer.height == 1, pg_code
        zeile = treffer.row(0, named=True)
        assert zeile["betrag"] == eintrag["ergebnis_mit_internen_verrechnungen"], pg_code
        assert zeile["pdf_seite"] == eintrag["pdf_seite"], pg_code


def test_querschnitte_fortsetzung_ueber_seiten(
    querschnittwerte: tuple[Querschnittwert, ...],
) -> None:
    """Mindestens ein (pb, plan)-Block hat Werte auf zwei verschiedenen pdf_seite und trotzdem
    genau eine GESAMTSUMME (Seitenumbruch mitten im Block, Research Pitfall)."""
    df = _als_dataframe(querschnittwerte)
    gefunden = False
    for (pb, plan), gruppe in df.group_by(["pb", "plan"]):
        seiten = set(gruppe["pdf_seite"].to_list())
        if len(seiten) <= 1:
            continue
        gesamtsumme = gruppe.filter(pl.col("gesamtsumme"))
        anzahl_kennzahlen = gruppe["kennzahl"].n_unique()
        assert gesamtsumme.height == anzahl_kennzahlen, (pb, plan)
        gefunden = True
    assert gefunden, "kein (pb, plan)-Block erstreckt sich über mehr als eine pdf_seite"


def test_querschnitte_seitenzahl_am_rand_wird_entfernt(
    querschnittwerte: tuple[Querschnittwert, ...],
    pdf_klassifikation: tuple[pl.DataFrame, pl.DataFrame],
    jahrgang: Jahrgang,
) -> None:
    """Auf jeder Querschnitt-Seite trägt kein Querschnittwert die links angeklebte PDF-
    Seitenzahl als pg; die PG-Zahl je (pb, plan) entspricht hierarchie.csv (Guard für den
    S. 293-Merge mit PG 0302)."""
    bereich = jahrgang.seitenbereiche["querschnitte"]
    seitenzahlen = {str(seite) for seite in range(bereich.von, bereich.bis + 1)}

    df = _als_dataframe(querschnittwerte)
    getroffene_seitenzahlen = {pg for pg in df["pg"].drop_nulls().to_list() if pg in seitenzahlen}
    assert not getroffene_seitenzahlen

    _seiten_df, hierarchie_df = pdf_klassifikation
    for pb in sorted(hierarchie_df.filter(pl.col("ebene") == "PB")["code"].to_list()):
        erwartete_anzahl = hierarchie_df.filter(
            (pl.col("ebene") == "PG") & (pl.col("eltern_code") == pb)
        ).height
        for plan in ("ergebnisplan", "finanzplan"):
            gefundene_anzahl = df.filter(
                (pl.col("pb") == pb) & (pl.col("plan") == plan) & ~pl.col("gesamtsumme")
            )["pg"].n_unique()
            assert gefundene_anzahl == erwartete_anzahl, (pb, plan)
