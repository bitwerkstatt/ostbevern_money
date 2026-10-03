"""Tests für ostbevern.stellenplan: Koordinaten-Extraktion des Stellenplans S. 284-290
(EXTR-10, D-18 bis D-20).

Liest nur das Original-PDF, nie daten/ (außer `test_stellenplan_csv_eingecheckt_aktuell`,
die die eingecheckte CSV gegen eine frische Extraktion vergleicht). Keine Jahrgangs-
Literale außer den in der Aufgabe fest verifizierten Struktur-Fakten (Gruppen,
Vermerke, Summen) — Zahlen kommen aus dem gedruckten PDF, nicht erfunden.
"""

from __future__ import annotations

import dataclasses
import tempfile
from pathlib import Path

import polars as pl
import pytest

from ostbevern.konfiguration import Jahrgang
from ostbevern.pdf import PdfDokument, Textzeile
from ostbevern.schema import DATEN_WURZEL, HIERARCHIE_CSV, STELLENPLAN_CSV, lies_stellenplan_csv
from ostbevern.stellenplan import (
    StellenplanFehler,
    Stellenwert,
    extrahiere_stellenplan,
    lies_stellen_hundertstel,
    lies_stellenplan,
)


def _kopiere_hierarchie_nach(tmp_pfad: Path) -> None:
    """Kopiert die eingecheckte hierarchie.csv unverändert in den tmp-Datenbaum (D-06):
    `lies_stellenplan` liest sie für die Stellenübersicht-PB-Codes bei jedem Aufruf."""
    ziel = tmp_pfad / HIERARCHIE_CSV
    ziel.parent.mkdir(parents=True, exist_ok=True)
    ziel.write_bytes((DATEN_WURZEL / HIERARCHIE_CSV).read_bytes())


@pytest.fixture(scope="module")
def stellenwerte(jahrgang: Jahrgang) -> tuple[Stellenwert, ...]:
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        return tuple(lies_stellenplan(dokument, jahrgang))


def _als_dataframe(werte: tuple[Stellenwert, ...]) -> pl.DataFrame:
    return pl.DataFrame(
        [
            {
                "teil": w.teil,
                "position": w.position,
                "gruppe": w.gruppe,
                "amtsbezeichnung": w.amtsbezeichnung,
                "verguetung": w.verguetung,
                "produktbereich": w.produktbereich,
                "merkmal": w.merkmal,
                "jahr": w.jahr,
                "stichtag": w.stichtag,
                "stellen_hundertstel": w.stellen_hundertstel,
                "personen": w.personen,
                "vermerk": w.vermerk,
                "pdf_seite": w.pdf_seite,
            }
            for w in werte
        ],
        schema={
            "teil": pl.Utf8,
            "position": pl.Int64,
            "gruppe": pl.Utf8,
            "amtsbezeichnung": pl.Utf8,
            "verguetung": pl.Utf8,
            "produktbereich": pl.Utf8,
            "merkmal": pl.Utf8,
            "jahr": pl.Int64,
            "stichtag": pl.Utf8,
            "stellen_hundertstel": pl.Int64,
            "personen": pl.Int64,
            "vermerk": pl.Utf8,
            "pdf_seite": pl.Int64,
        },
    )


# --- lies_stellen_hundertstel (D-18, Research Pattern 2) ---------------------------


@pytest.mark.parametrize(
    ("text", "erwartet"),
    [
        ("52,26", 5226),
        ("6,9", 690),
        ("8", 800),
        ("0,41", 41),
        ("18,95", 1895),
        ("-", None),
        ("–", None),
    ],
)
def test_lies_stellen_hundertstel(text: str, erwartet: int | None) -> None:
    assert lies_stellen_hundertstel(text) == erwartet


@pytest.mark.parametrize("text", ["1,234", "abc"])
def test_lies_stellen_hundertstel_ungueltig(text: str) -> None:
    with pytest.raises(StellenplanFehler):
        lies_stellen_hundertstel(text)


# --- Teil A: Beamte (S. 284) --------------------------------------------------------


def test_stellenplan_beamte_b3_davon_ausgesondert(
    stellenwerte: tuple[Stellenwert, ...],
) -> None:
    """B 3 hat eine davon_ausgesondert-Zeile von 100 Hundertsteln (1 Stelle, D-19)."""
    df = _als_dataframe(stellenwerte)
    zeile = df.filter(
        (pl.col("teil") == "beamte")
        & (pl.col("gruppe") == "B 3")
        & (pl.col("merkmal") == "davon_ausgesondert")
    )
    assert zeile.height == 1
    assert zeile["stellen_hundertstel"][0] == 100


def test_stellenplan_beamte_a14_stellen_vermerk_besetzt(
    stellenwerte: tuple[Stellenwert, ...],
) -> None:
    """A 14 hat Stellen 2026=200 mit Vermerk, Stellen 2025=300, besetzt 2025-06-30=300."""
    df = _als_dataframe(stellenwerte)
    a14 = df.filter(
        (pl.col("teil") == "beamte")
        & (pl.col("gruppe") == "A 14")
        & pl.col("produktbereich").is_null()
    )
    stellen_2026 = a14.filter((pl.col("merkmal") == "stellen") & (pl.col("jahr") == 2026))
    assert stellen_2026.height == 1
    assert stellen_2026["stellen_hundertstel"][0] == 200
    assert stellen_2026["vermerk"][0] == "1 Stelle künftig wegfallend (05.2029)"
    assert stellen_2026["amtsbezeichnung"][0] == "Oberverwaltungsrat/rätin"

    stellen_2025 = a14.filter((pl.col("merkmal") == "stellen") & (pl.col("jahr") == 2025))
    assert stellen_2025.height == 1
    assert stellen_2025["stellen_hundertstel"][0] == 300
    assert stellen_2025["vermerk"][0] is None

    besetzt = a14.filter(pl.col("merkmal") == "besetzt")
    assert besetzt.height == 1
    assert besetzt["stellen_hundertstel"][0] == 300
    assert besetzt["stichtag"][0] == "2025-06-30"
    assert besetzt["jahr"][0] == 2025


def test_stellenplan_beamte_a13_nur_haushaltsjahr(
    stellenwerte: tuple[Stellenwert, ...],
) -> None:
    """A 13 hat nur Stellen 2026 (keine Stellen 2025, kein besetzt, D-19)."""
    df = _als_dataframe(stellenwerte)
    a13 = df.filter(
        (pl.col("teil") == "beamte")
        & (pl.col("gruppe") == "A 13")
        & pl.col("produktbereich").is_null()
    )
    assert a13.height == 1
    assert a13["merkmal"][0] == "stellen"
    assert a13["jahr"][0] == 2026
    assert a13["stellen_hundertstel"][0] == 100


def test_stellenplan_beamte_a11_keine_zeile(stellenwerte: tuple[Stellenwert, ...]) -> None:
    """A 11 (ohne gedruckte Werte) erzeugt keine Zeile (D-19: leer heißt kein Eintrag)."""
    df = _als_dataframe(stellenwerte)
    a11 = df.filter(
        (pl.col("teil") == "beamte")
        & (pl.col("gruppe") == "A 11")
        & pl.col("produktbereich").is_null()
    )
    assert a11.height == 0


# --- Teil B: Tariflich Beschäftigte (S. 285) ---------------------------------------


def test_stellenplan_tarif_9c_nicht_an_10_angehaengt(
    stellenwerte: tuple[Stellenwert, ...],
) -> None:
    """9c hat Stellen 2026=326, 2025=426, besetzt=526 — nicht an EG 10 angehängt (D-20,
    Research Pitfall: Werte stehen auf einer anderen `top`-Zeile als ihr Label)."""
    df = _als_dataframe(stellenwerte)
    eg10 = df.filter(
        (pl.col("teil") == "tarif")
        & (pl.col("gruppe") == "10")
        & pl.col("produktbereich").is_null()
    )
    assert eg10.height == 0

    eg9c = df.filter(
        (pl.col("teil") == "tarif")
        & (pl.col("gruppe") == "9c")
        & pl.col("produktbereich").is_null()
    )
    stellen_2026 = eg9c.filter((pl.col("merkmal") == "stellen") & (pl.col("jahr") == 2026))
    stellen_2025 = eg9c.filter((pl.col("merkmal") == "stellen") & (pl.col("jahr") == 2025))
    besetzt = eg9c.filter(pl.col("merkmal") == "besetzt")
    assert stellen_2026["stellen_hundertstel"][0] == 326
    assert stellen_2025["stellen_hundertstel"][0] == 426
    assert besetzt["stellen_hundertstel"][0] == 526


def test_stellenplan_tarif_9a_vermerk_sperrvermerk(
    stellenwerte: tuple[Stellenwert, ...],
) -> None:
    """9a trägt den Vermerk "0,46 VZÄ mit Sperrvermerk" nur auf der Stellen-2026-Zeile."""
    df = _als_dataframe(stellenwerte)
    eg9a = df.filter(
        (pl.col("teil") == "tarif")
        & (pl.col("gruppe") == "9a")
        & pl.col("produktbereich").is_null()
    )
    stellen_2026 = eg9a.filter((pl.col("merkmal") == "stellen") & (pl.col("jahr") == 2026))
    assert stellen_2026["vermerk"][0] == "0,46 VZÄ mit Sperrvermerk"
    andere = eg9a.filter(~((pl.col("merkmal") == "stellen") & (pl.col("jahr") == 2026)))
    assert andere["vermerk"].null_count() == andere.height


def test_stellenplan_tarif_eg3_nur_vorjahr(stellenwerte: tuple[Stellenwert, ...]) -> None:
    """EG 3 hat nur einen Wert in der 2025-Spalte (merkmal=stellen, jahr=2025, D-19)."""
    df = _als_dataframe(stellenwerte)
    eg3 = df.filter(
        (pl.col("teil") == "tarif") & (pl.col("gruppe") == "3") & pl.col("produktbereich").is_null()
    )
    assert eg3.height == 1
    assert eg3["merkmal"][0] == "stellen"
    assert eg3["jahr"][0] == 2025
    assert eg3["stellen_hundertstel"][0] == 26


# --- Summen (D-20) ------------------------------------------------------------------


def test_stellenplan_summen_je_teil(stellenwerte: tuple[Stellenwert, ...]) -> None:
    """Σ Stellen 2026 je Teil (ohne Produktbereich): Beamte 800, Tarif 5226, SuE 265."""
    df = _als_dataframe(stellenwerte)
    stellen_2026 = df.filter(
        (pl.col("merkmal") == "stellen")
        & (pl.col("jahr") == 2026)
        & pl.col("produktbereich").is_null()
    )
    summen = dict(
        stellen_2026.group_by("teil").agg(pl.col("stellen_hundertstel").sum()).iter_rows()
    )
    assert summen == {"beamte": 800, "tarif": 5226, "sozial_erziehungsdienst": 265}


def test_stellenplan_nachwuchs_summen_und_keine_stellen(
    stellenwerte: tuple[Stellenwert, ...],
) -> None:
    """Nachwuchs: Σ vorgesehen=6, Σ beschaeftigt=5 Personen; stellen_hundertstel immer
    null (D-19: Nachwuchskräfte zählen nie als Stelle)."""
    df = _als_dataframe(stellenwerte)
    nachwuchs = df.filter(pl.col("teil") == "nachwuchs")
    assert nachwuchs.height > 0
    assert nachwuchs["stellen_hundertstel"].null_count() == nachwuchs.height

    vorgesehen = nachwuchs.filter(pl.col("merkmal") == "vorgesehen")
    beschaeftigt = nachwuchs.filter(pl.col("merkmal") == "beschaeftigt")
    assert vorgesehen["personen"].sum() == 6
    assert beschaeftigt["personen"].sum() == 5
    assert beschaeftigt["stichtag"].to_list() == ["2025-10-01"] * beschaeftigt.height


def test_stellenplan_nachwuchs_auszubildende(stellenwerte: tuple[Stellenwert, ...]) -> None:
    """Die Auszubildenden-Zeile hat vorgesehen=4 und beschaeftigt=4 Personen, Vergütung
    "Ausbildungsvergütung" (D-19)."""
    df = _als_dataframe(stellenwerte)
    auszubildende = df.filter(
        (pl.col("teil") == "nachwuchs") & (pl.col("gruppe") == "Auszubildende")
    )
    assert auszubildende.height == 2
    assert set(auszubildende["verguetung"].to_list()) == {"Ausbildungsvergütung"}
    vorgesehen = auszubildende.filter(pl.col("merkmal") == "vorgesehen")
    beschaeftigt = auszubildende.filter(pl.col("merkmal") == "beschaeftigt")
    assert vorgesehen["personen"][0] == 4
    assert beschaeftigt["personen"][0] == 4


# --- Fehlerfälle (D-20, Manipulation via dataclasses.replace) ----------------------


@dataclasses.dataclass
class _FehlerhaftesDokument:
    """Ersetzt die Zeilen genau einer Seite eines echten PdfDokument (D-07)."""

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


def test_stellenplan_manipulierte_insgesamt_bricht_ab(jahrgang: Jahrgang) -> None:
    """Eine manipulierte "insgesamt"-Zeile auf der Tarif-Seite (S. 285) bricht mit der
    PDF-Seite ab (D-20)."""
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        zeilen = dokument.zeilen(285)
        index, zeile = _finde_zeile(
            zeilen, lambda z: bool(z.woerter) and z.woerter[0].text == "insgesamt"
        )
        letztes_wort = zeile.woerter[-1]
        verfaelscht = dataclasses.replace(letztes_wort, text="99,99")
        manipuliert = dataclasses.replace(zeile, woerter=(*zeile.woerter[:-1], verfaelscht))
        ersatz = _ersetze_zeile(zeilen, index, manipuliert)
        fehlerhaft = _FehlerhaftesDokument(echt=dokument, seite=285, ersatz=ersatz)
        with pytest.raises(StellenplanFehler, match=r"S\. 285.*insgesamt"):
            lies_stellenplan(fehlerhaft, jahrgang)


def test_stellenplan_wert_ohne_gruppe_innerhalb_toleranz_bricht_ab(jahrgang: Jahrgang) -> None:
    """Eine Wertzeile, deren nächste Gruppe mehr als 8pt entfernt liegt, bricht ab
    (D-20, T-04-09): die EG-9c-Werte werden weit von jeder Gruppe weggeschoben."""
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        zeilen = dokument.zeilen(285)
        index, zeile = _finde_zeile(
            zeilen, lambda z: bool(z.woerter) and z.woerter[0].text == "3,26"
        )
        weit_weg = dataclasses.replace(zeile, top=zeile.top + 200)
        ersatz = _ersetze_zeile(zeilen, index, weit_weg)
        fehlerhaft = _FehlerhaftesDokument(echt=dokument, seite=285, ersatz=ersatz)
        with pytest.raises(StellenplanFehler, match=r"S\. 285.*keine Gruppe"):
            lies_stellenplan(fehlerhaft, jahrgang)


def test_stellenplan_csv_eingecheckt_aktuell(jahrgang: Jahrgang) -> None:
    """Eine frische Extraktion in ein tmp-Verzeichnis ist byte-identisch zur eingecheckten
    stellenplan.csv (D-21, D-24)."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_pfad = Path(tmp)
        _kopiere_hierarchie_nach(tmp_pfad)
        extrahiere_stellenplan(jahrgang, daten_wurzel=tmp_pfad)
        frisch = lies_stellenplan_csv(tmp_pfad / STELLENPLAN_CSV)
    eingecheckt = lies_stellenplan_csv(DATEN_WURZEL / STELLENPLAN_CSV)
    assert frisch.equals(eingecheckt)


# --- Stellenübersicht nach Produktbereichen (S. 287-289, Task 2) -------------------


def test_stellenplan_uebersicht_pb11_pb16_ohne_summe_zelle(
    stellenwerte: tuple[Stellenwert, ...],
) -> None:
    """PB 11 und PB 16 liefern je eine A-14-Zeile (1 bzw. 6 Hundertstel), obwohl S. 287
    für sie keine gedruckte Summe-Zelle zeigt (Research Pitfall 1: dünn besetzte
    Matrix, fehlende Summe-Zelle ist kein Fehler, D-20)."""
    df = _als_dataframe(stellenwerte)
    pb11 = df.filter(
        (pl.col("teil") == "beamte")
        & (pl.col("produktbereich") == "11")
        & (pl.col("gruppe") == "A 14")
    )
    pb16 = df.filter(
        (pl.col("teil") == "beamte")
        & (pl.col("produktbereich") == "16")
        & (pl.col("gruppe") == "A 14")
    )
    assert pb11.height == 1
    assert pb11["stellen_hundertstel"][0] == 1
    assert pb16.height == 1
    assert pb16["stellen_hundertstel"][0] == 6


def test_stellenplan_uebersicht_tarif_pb09_zwei_namenszeilen(
    stellenwerte: tuple[Stellenwert, ...],
) -> None:
    """PB 09 (Tarif, S. 288) hat Werte auf beiden Namenszeilen des umgebrochenen
    PB-Namens; ihre Summe ist 0,11 (Research Pitfall 2)."""
    df = _als_dataframe(stellenwerte)
    pb09 = df.filter((pl.col("teil") == "tarif") & (pl.col("produktbereich") == "09"))
    assert pb09.height == 2
    assert pb09["stellen_hundertstel"].sum() == 11


def test_stellenplan_uebersicht_summen_je_teil(stellenwerte: tuple[Stellenwert, ...]) -> None:
    """Σ Stellenübersicht je Teil entspricht der Teil-A/B-Haushaltsjahr-Summe (800 /
    5226 / 265, D-20)."""
    df = _als_dataframe(stellenwerte)
    uebersicht = df.filter(pl.col("produktbereich").is_not_null())
    summen = dict(uebersicht.group_by("teil").agg(pl.col("stellen_hundertstel").sum()).iter_rows())
    assert summen == {"beamte": 800, "tarif": 5226, "sozial_erziehungsdienst": 265}


def test_stellenplan_uebersicht_manipulierte_summe_zeile_bricht_ab(jahrgang: Jahrgang) -> None:
    """Eine verfälschte PB-Summe-Zelle auf S. 287 (Beamte-Übersicht) bricht ab (D-20)."""
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        zeilen = dokument.zeilen(287)
        index, zeile = _finde_zeile(
            zeilen,
            lambda z: (
                bool(z.woerter)
                and z.woerter[0].text == "01"
                and any(w.text == "3,87" for w in z.woerter)
            ),
        )
        ziel_wort = next(w for w in zeile.woerter if w.text == "3,87")
        verfaelscht = dataclasses.replace(ziel_wort, text="9,99")
        neue_woerter = tuple(verfaelscht if w is ziel_wort else w for w in zeile.woerter)
        manipuliert = dataclasses.replace(zeile, woerter=neue_woerter)
        ersatz = _ersetze_zeile(zeilen, index, manipuliert)
        fehlerhaft = _FehlerhaftesDokument(echt=dokument, seite=287, ersatz=ersatz)
        with pytest.raises(StellenplanFehler, match=r"S\. 287.*PB 01.*Summe"):
            lies_stellenplan(fehlerhaft, jahrgang)


def test_stellenplan_uebersicht_unbekannter_pb_code_bricht_ab(jahrgang: Jahrgang) -> None:
    """Ein PB-Code, der nicht in hierarchie.csv steht, bricht ab (D-20)."""
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        zeilen = dokument.zeilen(287)
        index, zeile = _finde_zeile(zeilen, lambda z: bool(z.woerter) and z.woerter[0].text == "01")
        erstes_wort = zeile.woerter[0]
        unbekannt = dataclasses.replace(erstes_wort, text="99")
        manipuliert = dataclasses.replace(zeile, woerter=(unbekannt, *zeile.woerter[1:]))
        ersatz = _ersetze_zeile(zeilen, index, manipuliert)
        fehlerhaft = _FehlerhaftesDokument(echt=dokument, seite=287, ersatz=ersatz)
        with pytest.raises(StellenplanFehler):
            lies_stellenplan(fehlerhaft, jahrgang)
