"""Tests für Schritt 08: Quellenbelege (Phase 7, DATA-04, Plan 07-01).

Schreibt ausschließlich in tmp-Verzeichnisse, nie in das eingecheckte `app/src/data/` oder
`app/public/quellen/`. Die eingecheckten Dateien werden nur gelesen und gegen das
tmp-Ergebnis bzw. das PDF geprüft. WebP-Bytes werden nicht verglichen (nicht über
Plattformen hinweg belegt); geprüft werden Existenz und Pixelmaße.
"""

from __future__ import annotations

import json
from pathlib import Path

import polars as pl
import pytest
from PIL import Image

from ostbevern.app_daten import APP_DATEN_WURZEL
from ostbevern.belegbilder import (
    BelegbildFehler,
    bild_name,
    rendere_seiten,
    seitenmass_pdfium,
)
from ostbevern.konfiguration import Jahrgang
from ostbevern.pdf import PdfDokument, RahmenZeile, WortRahmen
from ostbevern.quellen import (
    BELEGBILDER_WURZEL,
    GRUND_BETRAG_FEHLT,
    GRUND_MEHRDEUTIG,
    GRUND_NICHT_GEFUNDEN,
    QUELLEN_JSON,
    QuellenErgebnis,
    bbox_mit_rand,
    erzeuge_quellen,
    finde_planzeile,
    schluessel_ep,
    schluessel_fp,
)
from ostbevern.schema import (
    DATEN_WURZEL,
    ERGEBNISPLAN_CSV,
    FINANZPLAN_CSV,
    SEITEN_CSV,
    lies_plan_csv,
    lies_seiten_csv,
)
from ostbevern.zahlen import ZahlenFehler, lies_betrag

EINGECHECKT = APP_DATEN_WURZEL / QUELLEN_JSON
TOLERANZ_PDFIUM = 0.01


@pytest.fixture(scope="session")
def tmp_ergebnis(
    tmp_path_factory: pytest.TempPathFactory, jahrgang: Jahrgang
) -> tuple[QuellenErgebnis, Path]:
    """Schritt 08 einmal ohne Rendern in tmp-Verzeichnisse (das PDF wird einmal gelesen)."""
    app_daten = tmp_path_factory.mktemp("app_daten")
    bilder = tmp_path_factory.mktemp("bilder")
    ergebnis = erzeuge_quellen(
        jahrgang.haushaltsjahr,
        app_daten_wurzel=app_daten,
        bild_wurzel=bilder,
        rendern=False,
    )
    return ergebnis, bilder


@pytest.fixture(scope="session")
def eingecheckt() -> dict:
    return json.loads(EINGECHECKT.read_text(encoding="utf-8"))


def _wort(text: str, x0: float, x1: float, top: float, bottom: float) -> WortRahmen:
    return WortRahmen(text=text, x0=x0, x1=x1, top=top, bottom=bottom)


def _zeile(*woerter: WortRahmen) -> RahmenZeile:
    return RahmenZeile(
        top=min(w.top for w in woerter),
        bottom=max(w.bottom for w in woerter),
        woerter=woerter,
    )


def test_quellen_json_eingecheckt_aktuell(tmp_ergebnis: tuple[QuellenErgebnis, Path]) -> None:
    ergebnis, _ = tmp_ergebnis
    assert EINGECHECKT.read_bytes() == ergebnis.pfad.read_bytes()


def test_schluesselgrammatik() -> None:
    assert schluessel_ep("GESAMT", "steuern") == "ep:GESAMT:steuern"
    assert schluessel_fp("GESAMT", "kreditaufnahme") == "fp:GESAMT:kreditaufnahme"


def test_ordentliche_ertraege_bbox_enthaelt_zeilennummer_und_betrag(
    jahrgang: Jahrgang, eingecheckt: dict
) -> None:
    beleg = eingecheckt["belege"][schluessel_ep("GESAMT", "ordentliche_ertraege")]
    assert beleg["pdf_seite"] == 62
    bbox = beleg["bbox"]
    assert bbox is not None and len(bbox) == 4

    plan = lies_plan_csv(DATEN_WURZEL / ERGEBNISPLAN_CSV)
    zeile = plan.filter(
        (pl.col("ebene") == "GESAMT")
        & (pl.col("zeile_kanonisch") == "ordentliche_ertraege")
        & (pl.col("jahr") == jahrgang.haushaltsjahr)
        & (pl.col("wertart") == "ansatz")
    )
    assert zeile.height == 1
    nummer = zeile["zeile"][0]
    betrag = zeile["betrag"][0]

    with PdfDokument.oeffne(jahrgang.pdf_pfad) as pdf:
        gedruckt = [z for z in pdf.zeilen_mit_rahmen(62) if z.woerter[0].text == nummer]
    assert len(gedruckt) == 1
    nummer_wort = gedruckt[0].woerter[0]
    betrag_woerter = []
    for wort in gedruckt[0].woerter[1:]:
        try:
            if lies_betrag(wort.text) == betrag:
                betrag_woerter.append(wort)
        except ZahlenFehler:
            continue
    assert betrag_woerter, "Haushaltsjahr-Betrag der gedruckten Zeile nicht gefunden"

    for wort in (nummer_wort, *betrag_woerter):
        assert bbox[0] <= wort.x0 and wort.x1 <= bbox[2]
        assert bbox[1] <= wort.top and wort.bottom <= bbox[3]


@pytest.mark.parametrize(
    ("csv", "praefix"), [(ERGEBNISPLAN_CSV, "ep"), (FINANZPLAN_CSV, "fp")], ids=["ep", "fp"]
)
def test_jede_gesamtzeile_hat_einen_beleg(csv: Path, praefix: str, eingecheckt: dict) -> None:
    plan = lies_plan_csv(DATEN_WURZEL / csv).filter(pl.col("ebene") == "GESAMT")
    erwartet = {f"{praefix}:GESAMT:{zeile}" for zeile in plan["zeile_kanonisch"].unique()}
    assert erwartet
    assert erwartet <= set(eingecheckt["belege"])
    seiten_csv = set(plan["pdf_seite"].unique())
    belegseiten = {eingecheckt["belege"][schluessel]["pdf_seite"] for schluessel in erwartet}
    assert belegseiten == seiten_csv


def test_schema_von_quellen_json(eingecheckt: dict, jahrgang: Jahrgang) -> None:
    assert set(eingecheckt) == {"haushaltsjahr", "seiten", "belege"}
    assert eingecheckt["haushaltsjahr"] == jahrgang.haushaltsjahr
    assert list(eingecheckt["belege"]) == sorted(eingecheckt["belege"])
    assert [int(seite) for seite in eingecheckt["seiten"]] == sorted(
        int(seite) for seite in eingecheckt["seiten"]
    )
    for seite in eingecheckt["seiten"].values():
        assert set(seite) == {"bild", "breite", "hoehe"}
        assert round(seite["breite"], 2) == seite["breite"]
        assert round(seite["hoehe"], 2) == seite["hoehe"]
    for beleg in eingecheckt["belege"].values():
        assert set(beleg) == {"pdf_seite", "bild", "bbox"}
        assert str(beleg["pdf_seite"]) in eingecheckt["seiten"]
        assert beleg["bild"] == eingecheckt["seiten"][str(beleg["pdf_seite"])]["bild"]
        if beleg["bbox"] is not None:
            assert len(beleg["bbox"]) == 4
            assert all(round(wert, 2) == wert for wert in beleg["bbox"])


def test_bbox_liegt_innerhalb_der_seite(eingecheckt: dict) -> None:
    for schluessel, beleg in eingecheckt["belege"].items():
        if beleg["bbox"] is None:
            continue
        seite = eingecheckt["seiten"][str(beleg["pdf_seite"])]
        x0, top, x1, bottom = beleg["bbox"]
        assert 0 <= x0 < x1 <= seite["breite"], schluessel
        assert 0 <= top < bottom <= seite["hoehe"], schluessel


@pytest.mark.parametrize("pdf_seite", [62, 63, 291, 311])
def test_seitenmass_pdfplumber_gleich_pdfium(jahrgang: Jahrgang, pdf_seite: int) -> None:
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as pdf:
        breite, hoehe = pdf.seitenmass(pdf_seite)
    breite_pdfium, hoehe_pdfium = seitenmass_pdfium(jahrgang.pdf_pfad, pdf_seite)
    assert breite == pytest.approx(breite_pdfium, abs=TOLERANZ_PDFIUM)
    assert hoehe == pytest.approx(hoehe_pdfium, abs=TOLERANZ_PDFIUM)


def test_querformat_seiten_haben_vertauschtes_mass(jahrgang: Jahrgang) -> None:
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as pdf:
        hoch = pdf.seitenmass(62)
        quer = pdf.seitenmass(291)
    assert hoch[0] < hoch[1]
    assert quer[0] > quer[1]


def test_eingecheckte_bilder_existieren_mit_erwarteten_massen(eingecheckt: dict) -> None:
    for nummer, seite in eingecheckt["seiten"].items():
        pfad = BELEGBILDER_WURZEL / seite["bild"]
        assert seite["bild"] == bild_name(int(nummer))
        assert pfad.is_file(), f"Belegbild fehlt: {pfad}"
        with Image.open(pfad) as bild:
            assert bild.format == "WEBP"
            assert abs(bild.width - round(2 * seite["breite"])) <= 1
            assert abs(bild.height - round(2 * seite["hoehe"])) <= 1


def test_keine_verwaisten_belegbilder(eingecheckt: dict) -> None:
    erwartet = {seite["bild"] for seite in eingecheckt["seiten"].values()}
    vorhanden = {pfad.name for pfad in BELEGBILDER_WURZEL.glob("*.webp")}
    assert vorhanden == erwartet


def test_produktinformationen_seite_ohne_schwaerzung_wird_nicht_gerendert(
    jahrgang: Jahrgang, tmp_path: Path
) -> None:
    seiten = lies_seiten_csv(DATEN_WURZEL / SEITEN_CSV)
    seitentypen = {int(r["pdf_seite"]): str(r["typ"]) for r in seiten.iter_rows(named=True)}
    erste = int(seiten.filter(pl.col("typ") == "produktinformationen")["pdf_seite"][0])

    with pytest.raises(BelegbildFehler, match=str(erste)):
        rendere_seiten(jahrgang.pdf_pfad, [erste], tmp_path, seitentypen=seitentypen)
    assert list(tmp_path.iterdir()) == []


def test_produktinformationen_seite_mit_schwaerzung_wird_geschwaerzt(
    jahrgang: Jahrgang, tmp_path: Path
) -> None:
    seiten = lies_seiten_csv(DATEN_WURZEL / SEITEN_CSV)
    seitentypen = {int(r["pdf_seite"]): str(r["typ"]) for r in seiten.iter_rows(named=True)}
    erste = int(seiten.filter(pl.col("typ") == "produktinformationen")["pdf_seite"][0])
    rechteck = [100.0, 100.0, 300.0, 140.0]

    geschrieben = rendere_seiten(
        jahrgang.pdf_pfad,
        [erste],
        tmp_path,
        seitentypen=seitentypen,
        schwaerzungen={erste: [rechteck]},
    )
    assert [pfad.name for pfad in geschrieben] == [bild_name(erste)]
    with Image.open(geschrieben[0]) as bild:
        pixel = bild.convert("RGB").getpixel((400, 240))
    assert max(pixel) < 24


def test_vorhandene_bilder_werden_ohne_neu_nicht_erneut_gerendert(
    jahrgang: Jahrgang, tmp_path: Path
) -> None:
    seitentypen = {62: "sonstige"}
    erstes = rendere_seiten(jahrgang.pdf_pfad, [62], tmp_path, seitentypen=seitentypen)
    assert len(erstes) == 1
    inhalt = (tmp_path / bild_name(62)).read_bytes()
    zweites = rendere_seiten(jahrgang.pdf_pfad, [62], tmp_path, seitentypen=seitentypen)
    assert zweites == []
    assert (tmp_path / bild_name(62)).read_bytes() == inhalt


def test_bbox_mit_rand_klemmt_an_den_seitenraendern_und_rundet() -> None:
    woerter = [
        _wort("a", 0.5, 10.123, 1.0, 9.999),
        _wort("b", 590.0, 594.7, 835.0, 841.0),
    ]
    assert bbox_mit_rand(woerter, 595.28, 841.89) == [0.0, 0.0, 595.28, 841.89]


def test_bbox_mit_rand_fuegt_zwei_punkte_rand_hinzu() -> None:
    woerter = [_wort("a", 50.126, 100.004, 200.0, 210.555)]
    assert bbox_mit_rand(woerter, 595.28, 841.89) == [48.13, 198.0, 102.0, 212.56]


def test_planzeile_mit_nummer_und_betrag_wird_gefunden() -> None:
    zeilen = [
        _zeile(_wort("09", 44, 55, 100, 108), _wort("Bestand", 70, 120, 100, 108)),
        _zeile(
            _wort("10", 44, 55, 120, 128),
            _wort("=", 60, 65, 120, 128),
            _wort("Ordentliche", 70, 120, 120, 128),
            _wort("27.042.063", 400, 460, 120, 128),
        ),
    ]
    bbox, grund = finde_planzeile(zeilen, "10", 27_042_063, breite=595.28, hoehe=841.89)
    assert grund is None
    assert bbox == [42.0, 118.0, 462.0, 130.0]


def test_planzeile_ohne_passenden_betrag_bekommt_keine_bbox() -> None:
    zeilen = [_zeile(_wort("10", 44, 55, 120, 128), _wort("27.042.063", 400, 460, 120, 128))]
    assert finde_planzeile(zeilen, "10", 1, breite=595.28, hoehe=841.89) == (
        None,
        GRUND_BETRAG_FEHLT,
    )


def test_planzeile_ohne_nummer_bekommt_keine_bbox() -> None:
    zeilen = [_zeile(_wort("11", 44, 55, 120, 128), _wort("5", 400, 410, 120, 128))]
    assert finde_planzeile(zeilen, "10", 5, breite=595.28, hoehe=841.89) == (
        None,
        GRUND_NICHT_GEFUNDEN,
    )


def test_planzeile_mit_zwei_gleichen_treffern_ist_mehrdeutig() -> None:
    zeilen = [
        _zeile(_wort("10", 44, 55, 120, 128), _wort("1.000", 400, 450, 120, 128)),
        _zeile(_wort("10", 44, 55, 300, 308), _wort("1.000", 400, 450, 300, 308)),
    ]
    assert finde_planzeile(zeilen, "10", 1000, breite=595.28, hoehe=841.89) == (
        None,
        GRUND_MEHRDEUTIG,
    )


def test_planzeile_mit_betrag_null_braucht_nur_die_nummer() -> None:
    zeilen = [_zeile(_wort("03", 44, 55, 120, 128), _wort("0", 400, 410, 120, 128))]
    bbox, grund = finde_planzeile(zeilen, "03", 0, breite=595.28, hoehe=841.89)
    assert grund is None
    assert bbox is not None


def test_die_zeilennummer_zaehlt_nicht_als_betrag() -> None:
    """Die Zeilennummer `10` darf einen Betrag 10 nicht belegen."""
    zeilen = [_zeile(_wort("10", 44, 55, 120, 128), _wort("Text", 70, 120, 120, 128))]
    assert finde_planzeile(zeilen, "10", 10, breite=595.28, hoehe=841.89) == (
        None,
        GRUND_BETRAG_FEHLT,
    )
