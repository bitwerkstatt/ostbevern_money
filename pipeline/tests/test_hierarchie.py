"""Tests für die PB/PG/Produkt-Hierarchie (D-06: liest nur die eingecheckten
CSVs unter daten/ und die Jahrgangs-/Sollwertdatei, nie das PDF).

Deckt EXTR-03 (hierarchie.csv: PB, PG davon ein Teil synthetisch, Produkte) und den
Abgleich der Startseiten/Namen gegen Anhang A (D-19, Roadmap SC 1), die Vollständigkeit
von ergebnisplan.csv/finanzplan.csv je Knoten sowie seit D-14 (261001-oim) die Regel
"genau ein Produkt je synthetischer PG": jede synthetische PG ist eine exakte Kopie der
Zeilen ihres einzigen Kind-Produkts, nicht mehr eine Summe mehrerer Produkte. Zuordnungen,
die vom Standard (Code = erste vier Ziffern des Produktcodes) abweichen, stehen unter
[synthetische_produktgruppen] in der Jahrgangsdatei; kein Testcode hält diese Zuordnung
oder ihre Sollwerte als Literal fest, alles kommt aus lade_jahrgang/lade_sollwerte.
"""

from __future__ import annotations

import polars as pl

from ostbevern.konfiguration import STANDARD_JAHR, lade_jahrgang, lade_sollwerte
from ostbevern.schema import (
    DATEN_WURZEL,
    ERGEBNISPLAN_CSV,
    FINANZPLAN_CSV,
    HIERARCHIE_CSV,
    SEITEN_CSV,
    lies_hierarchie_csv,
    lies_plan_csv,
    lies_seiten_csv,
    zerlege_spaltenkopf,
)


def _normiert(text: str) -> str:
    """Whitespace- und case-insensitiver Vergleich (Planvorgabe D-19)."""
    return "".join(text.split()).casefold()


def _resolved_pg_code(produkt_code: str, jahrgang) -> str:
    """Testeigene Ableitung des D-14-Standards, unabhängig von der Produktionslogik:
    deklarierter Code, falls das Produkt in [synthetische_produktgruppen] auftaucht,
    sonst die ersten vier Ziffern des Produktcodes."""
    for code, eintrag in jahrgang.synthetische_produktgruppen.items():
        if eintrag.produkt == produkt_code:
            return code
    return produkt_code[:4]


def test_hierarchie_hat_korrekte_ebenenzahlen() -> None:
    jahrgang = lade_jahrgang(STANDARD_JAHR)
    anhang_a = lade_sollwerte(STANDARD_JAHR)["anhang_a"]
    hierarchie = lies_hierarchie_csv(DATEN_WURZEL / HIERARCHIE_CSV)

    pb_zeilen = hierarchie.filter(hierarchie["ebene"] == "PB")
    pg_zeilen = hierarchie.filter(hierarchie["ebene"] == "PG")
    p_zeilen = hierarchie.filter(hierarchie["ebene"] == "P")

    assert pb_zeilen.height == jahrgang.anzahlen.produktbereiche
    assert p_zeilen.height == jahrgang.anzahlen.produkte

    produkt_codes = {code for code in anhang_a if len(code) == 6}
    erwartete_pg_codes = {code for code in anhang_a if len(code) == 4}
    erwartete_pg_codes |= {_resolved_pg_code(code, jahrgang) for code in produkt_codes}

    assert set(pg_zeilen["code"].to_list()) == erwartete_pg_codes
    assert set(pb_zeilen["code"].to_list()) == {code for code in anhang_a if len(code) == 2}
    assert set(p_zeilen["code"].to_list()) == produkt_codes


def test_anhang_a_eintraege_stimmen_mit_hierarchie_ueberein() -> None:
    anhang_a = lade_sollwerte(STANDARD_JAHR)["anhang_a"]
    hierarchie = lies_hierarchie_csv(DATEN_WURZEL / HIERARCHIE_CSV)
    hierarchie_nach_code = {row["code"]: row for row in hierarchie.iter_rows(named=True)}

    for code, eintrag in anhang_a.items():
        zeile = hierarchie_nach_code[code]
        assert zeile["pdf_seite_start"] == eintrag["pdf_seite"]
        assert _normiert(zeile["name"]) == _normiert(eintrag["name"])


def test_synthetische_pg_markierung_und_namen() -> None:
    """Jede synthetische PG hat genau ein P-Kind. Ohne Deklaration startet dessen Code
    mit dem PG-Code (D-14-Standard); mit Deklaration ist das Kind exakt der deklarierte
    produkt-Wert. In beiden Fällen teilen sich PG und Kind den PB-Präfix, Name und
    pdf_seite_start kommen vom Kind, außer die Deklaration überschreibt den Namen."""
    jahrgang = lade_jahrgang(STANDARD_JAHR)
    anhang_a = lade_sollwerte(STANDARD_JAHR)["anhang_a"]
    hierarchie = lies_hierarchie_csv(DATEN_WURZEL / HIERARCHIE_CSV)
    gedruckte_pg_codes = {code for code in anhang_a if len(code) == 4}
    pg_zeilen = hierarchie.filter(hierarchie["ebene"] == "PG")
    p_zeilen = hierarchie.filter(hierarchie["ebene"] == "P")

    for row in pg_zeilen.iter_rows(named=True):
        erwartet_synthetisch = row["code"] not in gedruckte_pg_codes
        assert row["synthetisch"] == erwartet_synthetisch
        assert row["eltern_code"] == row["code"][:2]
        if not erwartet_synthetisch:
            continue

        kinder = [
            p_row["code"]
            for p_row in p_zeilen.iter_rows(named=True)
            if p_row["eltern_code"] == row["code"]
        ]
        assert len(kinder) == 1, row["code"]
        kind_code = kinder[0]
        assert kind_code[:2] == row["code"][:2]

        deklariert = jahrgang.synthetische_produktgruppen.get(row["code"])
        if deklariert is not None:
            assert kind_code == deklariert.produkt
            assert _normiert(row["name"]) == _normiert(deklariert.name)
        else:
            assert kind_code.startswith(row["code"])
            assert _normiert(row["name"]) == _normiert(anhang_a[kind_code]["name"])

        assert row["pdf_seite_start"] == anhang_a[kind_code]["pdf_seite"]


def test_deklarierte_synthetische_pg_vorhanden_in_hierarchie() -> None:
    jahrgang = lade_jahrgang(STANDARD_JAHR)
    assert jahrgang.synthetische_produktgruppen

    hierarchie = lies_hierarchie_csv(DATEN_WURZEL / HIERARCHIE_CSV)
    pg_nach_code = {
        row["code"]: row
        for row in hierarchie.filter(hierarchie["ebene"] == "PG").iter_rows(named=True)
    }
    for code, eintrag in jahrgang.synthetische_produktgruppen.items():
        zeile = pg_nach_code[code]
        assert zeile["synthetisch"] is True
        assert _normiert(zeile["name"]) == _normiert(eintrag.name)


def test_eltern_code_je_ebene() -> None:
    jahrgang = lade_jahrgang(STANDARD_JAHR)
    hierarchie = lies_hierarchie_csv(DATEN_WURZEL / HIERARCHIE_CSV)
    deklarierte_produkte = {
        eintrag.produkt: code for code, eintrag in jahrgang.synthetische_produktgruppen.items()
    }
    for row in hierarchie.iter_rows(named=True):
        if row["ebene"] == "PB":
            assert row["eltern_code"] is None
        elif row["ebene"] == "PG":
            assert row["eltern_code"] == row["code"][:2]
        elif row["ebene"] == "P":
            erwartet = deklarierte_produkte.get(row["code"], row["code"][:4])
            assert row["eltern_code"] == erwartet


def test_produktseiten_in_seiten_csv_stimmen_mit_anhang_a() -> None:
    anhang_a = lade_sollwerte(STANDARD_JAHR)["anhang_a"]
    seiten = lies_seiten_csv(DATEN_WURZEL / SEITEN_CSV)
    seiten_nach_seite = {row["pdf_seite"]: row for row in seiten.iter_rows(named=True)}

    for code, eintrag in anhang_a.items():
        startseite = seiten_nach_seite[eintrag["pdf_seite"]]
        if len(code) == 6:
            assert startseite["produkt"] == code
            assert startseite["typ"] == "produktinformationen"
        else:
            assert startseite["typ"] == "teilergebnisplan"
            if len(code) == 2:
                assert startseite["pb"] == code
            else:
                assert startseite["pg"] == code


def test_jeder_knoten_hat_ergebnis_und_finanzplanzeilen() -> None:
    """Jeder Knoten aus hierarchie.csv (PB, PG gedruckt und synthetisch, P) hat mindestens
    eine Zeile in ergebnisplan.csv und finanzplan.csv (D-08, D-13, D-14)."""
    hierarchie = lies_hierarchie_csv(DATEN_WURZEL / HIERARCHIE_CSV)
    ergebnisplan = lies_plan_csv(DATEN_WURZEL / ERGEBNISPLAN_CSV)
    finanzplan = lies_plan_csv(DATEN_WURZEL / FINANZPLAN_CSV)

    for knoten in hierarchie.iter_rows(named=True):
        ebene, code = knoten["ebene"], knoten["code"]
        teilergebnisplan_zeilen = ergebnisplan.filter(
            (pl.col("ebene") == ebene) & (pl.col("code") == code)
        )
        assert teilergebnisplan_zeilen.height > 0, (ebene, code)
        teilfinanzplan_zeilen = finanzplan.filter(
            (pl.col("ebene") == ebene) & (pl.col("code") == code)
        )
        assert teilfinanzplan_zeilen.height > 0, (ebene, code)
        assert (teilergebnisplan_zeilen["synthetisch"] == knoten["synthetisch"]).all()
        assert (teilfinanzplan_zeilen["synthetisch"] == knoten["synthetisch"]).all()


def test_synthetische_pg_ist_kopie_ihres_einzigen_produkts() -> None:
    """Jede synthetische-PG-Zeile ist eine exakte Kopie der Zeile ihres einzigen
    Kind-Produkts (D-14, 261001-oim): gleiche (zeile, zeile_kanonisch, zeile_name,
    operator, ist_summe, jahr, wertart, betrag, pdf_seite); nur ebene, code und
    synthetisch unterscheiden sich. Keine Summenbildung mehr, da jede synthetische
    PG genau ein Produkt hat."""
    hierarchie = lies_hierarchie_csv(DATEN_WURZEL / HIERARCHIE_CSV)
    synthetische_pg = hierarchie.filter((pl.col("ebene") == "PG") & pl.col("synthetisch"))
    assert synthetische_pg.height > 0
    p_zeilen = hierarchie.filter(pl.col("ebene") == "P")

    vergleichsspalten = [
        "zeile",
        "zeile_kanonisch",
        "zeile_name",
        "operator",
        "ist_summe",
        "jahr",
        "wertart",
        "betrag",
        "pdf_seite",
    ]
    sortierspalten = ["zeile", "jahr", "wertart"]

    for datei in (
        lies_plan_csv(DATEN_WURZEL / ERGEBNISPLAN_CSV),
        lies_plan_csv(DATEN_WURZEL / FINANZPLAN_CSV),
    ):
        for pg in synthetische_pg.iter_rows(named=True):
            pg_code = pg["code"]
            kinder = p_zeilen.filter(pl.col("eltern_code") == pg_code)["code"].to_list()
            assert len(kinder) == 1, pg_code
            kind_code = kinder[0]

            pg_zeilen_sortiert = (
                datei.filter((pl.col("ebene") == "PG") & (pl.col("code") == pg_code))
                .select(vergleichsspalten)
                .sort(sortierspalten)
            )
            kind_zeilen_sortiert = (
                datei.filter((pl.col("ebene") == "P") & (pl.col("code") == kind_code))
                .select(vergleichsspalten)
                .sort(sortierspalten)
            )
            assert pg_zeilen_sortiert.height > 0, pg_code
            assert pg_zeilen_sortiert.equals(kind_zeilen_sortiert), pg_code


def test_haushaltsquerschnitt_pg_sollwerte() -> None:
    """Jede deklarierte synthetische PG ist durch einen Haushaltsquerschnitt-Sollwert
    (S. 299) belegt, und ergebnisplan.csv trägt für ihre Z. 29 (Ansatz des
    Haushaltsjahres) genau diesen Wert (D-14, 261001-oim)."""
    jahrgang = lade_jahrgang(STANDARD_JAHR)
    sollwerte = lade_sollwerte(STANDARD_JAHR)
    haushaltsquerschnitt_pg = sollwerte["haushaltsquerschnitt_pg"]
    ergebnisplan = lies_plan_csv(DATEN_WURZEL / ERGEBNISPLAN_CSV)

    wertart, jahr = next(
        (wertart, jahr)
        for wertart, jahr in (
            zerlege_spaltenkopf(kopf) for kopf in jahrgang.spalten["ergebnisplan"]
        )
        if wertart == "ansatz" and jahr == jahrgang.haushaltsjahr
    )

    for code, eintrag in haushaltsquerschnitt_pg.items():
        zeile = ergebnisplan.filter(
            (pl.col("ebene") == "PG")
            & (pl.col("code") == code)
            & (pl.col("zeile_kanonisch") == "ergebnis_mit_internen_verrechnungen")
            & (pl.col("jahr") == jahr)
            & (pl.col("wertart") == wertart)
        )
        assert zeile.height == 1, code
        assert zeile["betrag"][0] == eintrag["ergebnis_mit_internen_verrechnungen"]

    for code in jahrgang.synthetische_produktgruppen:
        assert code in haushaltsquerschnitt_pg
