"""Tests für die PB/PG/Produkt-Hierarchie (D-06: liest nur die eingecheckten
CSVs unter daten/ und die Sollwertdatei, nie das PDF).

Deckt EXTR-03 (hierarchie.csv: 15 PB, 48 PG davon 40 synthetisch, 63 Produkte)
und den Abgleich der Startseiten/Namen gegen Anhang A (D-19, Roadmap SC 1).
"""

from __future__ import annotations

from ostbevern.konfiguration import STANDARD_JAHR, lade_jahrgang, lade_sollwerte
from ostbevern.schema import (
    DATEN_WURZEL,
    HIERARCHIE_CSV,
    SEITEN_CSV,
    lies_hierarchie_csv,
    lies_seiten_csv,
)


def _normiert(text: str) -> str:
    """Whitespace- und case-insensitiver Vergleich (Planvorgabe D-19)."""
    return "".join(text.split()).casefold()


def test_hierarchie_hat_korrekte_ebenenzahlen() -> None:
    jahrgang = lade_jahrgang(STANDARD_JAHR)
    anhang_a = lade_sollwerte(STANDARD_JAHR)["anhang_a"]
    hierarchie = lies_hierarchie_csv(DATEN_WURZEL / HIERARCHIE_CSV)

    pb_zeilen = hierarchie.filter(hierarchie["ebene"] == "PB")
    pg_zeilen = hierarchie.filter(hierarchie["ebene"] == "PG")
    p_zeilen = hierarchie.filter(hierarchie["ebene"] == "P")

    assert pb_zeilen.height == jahrgang.anzahlen.produktbereiche
    assert p_zeilen.height == jahrgang.anzahlen.produkte

    erwartete_pg_codes = {code for code in anhang_a if len(code) == 4}
    erwartete_pg_codes |= {code[:4] for code in anhang_a if len(code) == 6}
    assert set(pg_zeilen["code"].to_list()) == erwartete_pg_codes
    assert set(pb_zeilen["code"].to_list()) == {code for code in anhang_a if len(code) == 2}
    assert set(p_zeilen["code"].to_list()) == {code for code in anhang_a if len(code) == 6}


def test_anhang_a_eintraege_stimmen_mit_hierarchie_ueberein() -> None:
    anhang_a = lade_sollwerte(STANDARD_JAHR)["anhang_a"]
    hierarchie = lies_hierarchie_csv(DATEN_WURZEL / HIERARCHIE_CSV)
    hierarchie_nach_code = {row["code"]: row for row in hierarchie.iter_rows(named=True)}

    for code, eintrag in anhang_a.items():
        zeile = hierarchie_nach_code[code]
        assert zeile["pdf_seite_start"] == eintrag["pdf_seite"]
        assert _normiert(zeile["name"]) == _normiert(eintrag["name"])


def test_synthetische_pg_markierung_und_namen() -> None:
    anhang_a = lade_sollwerte(STANDARD_JAHR)["anhang_a"]
    hierarchie = lies_hierarchie_csv(DATEN_WURZEL / HIERARCHIE_CSV)
    gedruckte_pg_codes = {code for code in anhang_a if len(code) == 4}
    pg_zeilen = hierarchie.filter(hierarchie["ebene"] == "PG")

    for row in pg_zeilen.iter_rows(named=True):
        erwartet_synthetisch = row["code"] not in gedruckte_pg_codes
        assert row["synthetisch"] == erwartet_synthetisch
        assert row["eltern_code"] == row["code"][:2]
        if erwartet_synthetisch:
            produkte_dieser_pg = sorted(
                code for code in anhang_a if len(code) == 6 and code[:4] == row["code"]
            )
            assert produkte_dieser_pg
            niedrigstes_produkt = produkte_dieser_pg[0]
            assert _normiert(row["name"]) == _normiert(anhang_a[niedrigstes_produkt]["name"])
            erwartete_startseite = min(anhang_a[code]["pdf_seite"] for code in produkte_dieser_pg)
            assert row["pdf_seite_start"] == erwartete_startseite


def test_eltern_code_je_ebene() -> None:
    hierarchie = lies_hierarchie_csv(DATEN_WURZEL / HIERARCHIE_CSV)
    for row in hierarchie.iter_rows(named=True):
        if row["ebene"] == "PB":
            assert row["eltern_code"] is None
        elif row["ebene"] == "PG":
            assert row["eltern_code"] == row["code"][:2]
        elif row["ebene"] == "P":
            assert row["eltern_code"] == row["code"][:4]


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
