"""Tests für ostbevern.querschnitte: Koordinaten-Extraktion der Haushaltsquerschnitte
S. 291-300 (PRUEF-07, D-14, D-15).

Liest nur das Original-PDF, nie daten/. Keine Jahrgangs-, Seiten- oder
Sollwert-Literale – alles kommt aus lade_jahrgang(STANDARD_JAHR),
lade_sollwerte(STANDARD_JAHR) oder der pdf_klassifikation-Fixture.
"""

from __future__ import annotations

import dataclasses
import re

import polars as pl
import pytest

from ostbevern.konfiguration import (
    STANDARD_JAHR,
    Jahrgang,
    lade_sollwerte,
    layout_liste,
    layout_text,
)
from ostbevern.pdf import PdfDokument, Textzeile
from ostbevern.querschnitte import (
    QuerschnitteFehler,
    Querschnittwert,
    lies_querschnitte,
    pruefe_vollstaendigkeit,
)


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


@dataclasses.dataclass
class _FehlerhaftesDokument:
    """Ersetzt die Zeilen genau einer Seite eines echten PdfDokument (D-07, Task 2).

    `lies_querschnitte` ruft nur `.zeilen(pdf_seite)` auf (duck-typed) — dieser Wrapper
    delegiert an das echte Dokument, außer für `seite`, wo `ersatz` zurückgegeben wird.
    """

    echt: PdfDokument
    seite: int
    ersatz: tuple[Textzeile, ...]

    def zeilen(self, pdf_seite: int) -> tuple[Textzeile, ...]:
        if pdf_seite == self.seite:
            return self.ersatz
        return self.echt.zeilen(pdf_seite)


def _finde_zeile(zeilen, praedikat) -> tuple[int, Textzeile]:  # noqa: ANN001
    for index, zeile in enumerate(zeilen):
        if praedikat(zeile):
            return index, zeile
    pytest.fail("Keine passende Zeile gefunden")


def _ersetze_zeile(
    zeilen: tuple[Textzeile, ...], index: int, neue_zeile: Textzeile
) -> tuple[Textzeile, ...]:
    liste = list(zeilen)
    liste[index] = neue_zeile
    return tuple(liste)


def test_querschnitte_bricht_ab_bei_fehlendem_betrag(jahrgang: Jahrgang) -> None:
    """Eine Datenzeile mit einem entfernten Betragswort bricht mit PDF-Seite und PG ab."""
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        zeilen = dokument.zeilen(291)
        index, zeile = _finde_zeile(
            zeilen, lambda z: bool(z.woerter) and z.woerter[0].text.startswith("0101")
        )
        manipuliert = dataclasses.replace(zeile, woerter=zeile.woerter[:-1])
        ersatz = _ersetze_zeile(zeilen, index, manipuliert)
        fehlerhaft = _FehlerhaftesDokument(echt=dokument, seite=291, ersatz=ersatz)
        with pytest.raises(QuerschnitteFehler, match=r"S\. 291.*0101"):
            lies_querschnitte(fehlerhaft, jahrgang)


def test_querschnitte_bricht_ab_bei_pg_aus_anderer_pb(jahrgang: Jahrgang) -> None:
    """Eine PG, deren Code nicht zur PB ihres Blocks passt, bricht ab (D-08)."""
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        zeilen = dokument.zeilen(291)
        index, zeile = _finde_zeile(
            zeilen, lambda z: bool(z.woerter) and z.woerter[0].text.startswith("0101")
        )
        erstes_wort = zeile.woerter[0]
        fremde_pg = dataclasses.replace(erstes_wort, text="0201" + erstes_wort.text[4:])
        manipuliert = dataclasses.replace(zeile, woerter=(fremde_pg, *zeile.woerter[1:]))
        ersatz = _ersetze_zeile(zeilen, index, manipuliert)
        fehlerhaft = _FehlerhaftesDokument(echt=dokument, seite=291, ersatz=ersatz)
        with pytest.raises(QuerschnitteFehler, match=r"S\. 291.*PG 0201.*PB 01"):
            lies_querschnitte(fehlerhaft, jahrgang)


def test_querschnitte_bricht_ab_bei_fehlender_gesamtsumme(jahrgang: Jahrgang) -> None:
    """Ein Block, dessen GESAMTSUMME-Zeile entfernt wurde, bricht spätestens bei der
    nächsten Titelzeile ab (fehlende GESAMTSUMME, D-08)."""
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        zeilen = dokument.zeilen(291)
        index, _zeile = _finde_zeile(
            zeilen, lambda z: bool(z.woerter) and z.woerter[0].text == "GESAMTSUMME"
        )
        ohne_gesamtsumme = zeilen[:index] + zeilen[index + 1 :]
        fehlerhaft = _FehlerhaftesDokument(echt=dokument, seite=291, ersatz=ohne_gesamtsumme)
        with pytest.raises(QuerschnitteFehler, match=r"S\. 291"):
            lies_querschnitte(fehlerhaft, jahrgang)


def test_querschnitte_bricht_ab_bei_kopfzeile_ohne_block(jahrgang: Jahrgang) -> None:
    """Eine Kopfzeile ohne ausstehenden Titel und ohne vorherige Fortsetzung-Markierung
    bricht ab (D-08) — Gegenprobe zum legitimen Vorschau-Fall S. 297->298."""
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        kopf_beginn = layout_text(jahrgang, "querschnitte", "kopf_beginn")
        header_zeile = next(
            zeile
            for zeile in dokument.zeilen(291)
            if zeile.woerter and zeile.woerter[0].text == kopf_beginn
        )
        zeilen_293 = dokument.zeilen(293)
        eingefuegt = (header_zeile, *zeilen_293)
        fehlerhaft = _FehlerhaftesDokument(echt=dokument, seite=293, ersatz=eingefuegt)
        with pytest.raises(QuerschnitteFehler, match=r"S\. 293.*Kopfzeile"):
            lies_querschnitte(fehlerhaft, jahrgang)


def test_querschnitte_bricht_ab_bei_titel_kopfzeilen_widerspruch(jahrgang: Jahrgang) -> None:
    """Ein Titel, der "Finanzplan" durch "Ergebnisplan" ersetzt bekommt, widerspricht der
    tatsächlichen (11-spaltigen) Kopfzeile und bricht ab (D-08)."""
    titel_muster = layout_text(jahrgang, "querschnitte", "titel_muster")
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        zeilen = dokument.zeilen(294)
        index, titel_zeile = _finde_zeile(
            zeilen, lambda z: bool(z.woerter) and re.match(titel_muster, z.text) is not None
        )
        letzter_index = len(titel_zeile.woerter) - 1
        letztes_wort = titel_zeile.woerter[letzter_index]
        assert letztes_wort.text == "Finanzplan"
        ersetzt = dataclasses.replace(letztes_wort, text="Ergebnisplan")
        neue_woerter = (*titel_zeile.woerter[:letzter_index], ersetzt)
        manipuliert = dataclasses.replace(titel_zeile, woerter=neue_woerter)
        ersatz = _ersetze_zeile(zeilen, index, manipuliert)
        fehlerhaft = _FehlerhaftesDokument(echt=dokument, seite=294, ersatz=ersatz)
        with pytest.raises(QuerschnitteFehler, match=r"S\. 294.*Widerspruch"):
            lies_querschnitte(fehlerhaft, jahrgang)


def test_querschnitte_vollstaendigkeit_erkennt_fehlende_pg(
    querschnittwerte: tuple[Querschnittwert, ...],
    pdf_klassifikation: tuple[pl.DataFrame, pl.DataFrame],
) -> None:
    _seiten_df, hierarchie_df = pdf_klassifikation
    ziel = next(w for w in querschnittwerte if w.pg is not None)
    gefiltert = [
        w
        for w in querschnittwerte
        if not (w.pb == ziel.pb and w.pg == ziel.pg and w.plan == ziel.plan)
    ]
    with pytest.raises(QuerschnitteFehler):
        pruefe_vollstaendigkeit(gefiltert, hierarchie_df)


def test_querschnitte_vollstaendigkeit_erkennt_unbekannte_pg(
    querschnittwerte: tuple[Querschnittwert, ...],
    pdf_klassifikation: tuple[pl.DataFrame, pl.DataFrame],
) -> None:
    _seiten_df, hierarchie_df = pdf_klassifikation
    basis = next(w for w in querschnittwerte if w.pg is not None)
    unbekannt = dataclasses.replace(basis, pg="9999")
    with pytest.raises(QuerschnitteFehler):
        pruefe_vollstaendigkeit([*querschnittwerte, unbekannt], hierarchie_df)


def test_querschnitte_vollstaendigkeit_erkennt_fehlenden_plan(
    querschnittwerte: tuple[Querschnittwert, ...],
    pdf_klassifikation: tuple[pl.DataFrame, pl.DataFrame],
) -> None:
    _seiten_df, hierarchie_df = pdf_klassifikation
    ziel_pb = next(iter(querschnittwerte)).pb
    gefiltert = [w for w in querschnittwerte if not (w.pb == ziel_pb and w.plan == "finanzplan")]
    with pytest.raises(QuerschnitteFehler):
        pruefe_vollstaendigkeit(gefiltert, hierarchie_df)
