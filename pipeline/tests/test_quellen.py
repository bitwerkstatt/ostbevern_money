"""Tests für Schritt 08: Quellenbelege (Phase 7, DATA-04, Plan 07-01).

Schreibt ausschließlich in tmp-Verzeichnisse, nie in das eingecheckte `app/src/data/` oder
`app/public/quellen/`. Die eingecheckten Dateien werden nur gelesen und gegen das
tmp-Ergebnis bzw. das PDF geprüft. WebP-Bytes werden nicht verglichen (nicht über
Plattformen hinweg belegt); geprüft werden Existenz und Pixelmaße.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import polars as pl
import pytest
from PIL import Image

from ostbevern import quellen
from ostbevern.app_daten import APP_DATEN_WURZEL, erzeuge_app_daten
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
    QUELLENBELEGE_MD,
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
) -> tuple[QuellenErgebnis, Path, Path]:
    """Schritt 08 einmal ohne Rendern in tmp-Verzeichnisse (das PDF wird einmal gelesen).

    Liest die App-JSONs aus einem frischen tmp-Lauf von Schritt 07 und schreibt den Bericht in
    eine Kopie von `daten/`, nie in das eingecheckte Verzeichnis.
    """
    app_daten = tmp_path_factory.mktemp("app_daten")
    bilder = tmp_path_factory.mktemp("bilder")
    daten = tmp_path_factory.mktemp("daten") / "daten"
    shutil.copytree(DATEN_WURZEL, daten)
    erzeuge_app_daten(jahrgang.haushaltsjahr, daten_wurzel=daten, app_daten_wurzel=app_daten)
    ergebnis = erzeuge_quellen(
        jahrgang.haushaltsjahr,
        daten_wurzel=daten,
        app_daten_wurzel=app_daten,
        bild_wurzel=bilder,
        rendern=False,
    )
    return ergebnis, bilder, daten


@pytest.fixture(scope="session")
def tmp_belege(tmp_ergebnis: tuple[QuellenErgebnis, Path, Path]) -> dict:
    ergebnis, _, _ = tmp_ergebnis
    return json.loads(ergebnis.pfad.read_text(encoding="utf-8"))


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


def test_quellen_json_eingecheckt_aktuell(
    tmp_ergebnis: tuple[QuellenErgebnis, Path, Path],
) -> None:
    ergebnis, _, _ = tmp_ergebnis
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
    # Beleg nur für Zeilen, die die App als Datensatz kennt (ab Plan 07-03 verlangt der
    # Vertragstest, dass jeder Schlüssel auf einen Datensatz zeigt): die nachrichtlichen GEP-Zeilen
    # unter Z. 28 stehen nicht in `haushalt.ergebnisplan.GESAMT.zeilen`.
    haushalt = json.loads((APP_DATEN_WURZEL / "haushalt.json").read_text(encoding="utf-8"))
    app_zeilen = set(
        haushalt["ergebnisplan" if praefix == "ep" else "finanzplan"]["GESAMT"]["zeilen"]
    )
    plan = plan.filter(pl.col("zeile_kanonisch").is_in(app_zeilen))
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


# --- Plan 07-03, Aufgabe 1: alle Belegarten außer Produkt-, Grundzahl- und Seitenbelegen ---


@pytest.fixture(scope="session")
def pdf_dok(jahrgang: Jahrgang):
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        yield dokument


@pytest.fixture(scope="session")
def haushalt() -> dict:
    return json.loads((APP_DATEN_WURZEL / "haushalt.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def investitionen() -> dict:
    return json.loads((APP_DATEN_WURZEL / "investitionen.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def stellenplan() -> dict:
    return json.loads((APP_DATEN_WURZEL / "stellenplan.json").read_text(encoding="utf-8"))


def _umschliesst(bbox: list[float], wort: WortRahmen) -> bool:
    return (
        bbox[0] <= wort.x0 and wort.x1 <= bbox[2] and bbox[1] <= wort.top and wort.bottom <= bbox[3]
    )


def _woerter(pdf_dok: PdfDokument, seite: int) -> list[WortRahmen]:
    return [wort for zeile in pdf_dok.zeilen_mit_rahmen(seite) for wort in zeile.woerter]


def _beleg(belege: dict, schluessel: str, seite: int) -> list[float]:
    beleg = belege["belege"][schluessel]
    assert beleg["pdf_seite"] == seite
    assert beleg["bbox"] is not None, schluessel
    return beleg["bbox"]


def test_schluesselgrammatik_alle_arten() -> None:
    assert quellen.schluessel_vb("steuerarten", "gewerbesteuer") == "vb:steuerarten:gewerbesteuer"
    assert quellen.schluessel_vb_gesamt("steuerarten") == "vb:steuerarten:gesamt"
    assert quellen.schluessel_meta("hebesaetze.gewerbesteuer") == "meta:hebesaetze.gewerbesteuer"
    assert quellen.schluessel_gz("010101", 3) == "gz:010101:3"
    assert quellen.schluessel_pr("010101") == "pr:010101"
    assert (
        quellen.schluessel_inv("010601", "BGA010601", "783111", "auszahlung")
        == "inv:010601:BGA010601:783111:auszahlung"
    )
    assert quellen.schluessel_ve("020701", "AIBH012", "785111") == "ve:020701:AIBH012:785111"
    assert quellen.schluessel_sd("nrw_bank") == "sd:nrw_bank"
    assert quellen.schluessel_sp("beamte", 1, None) == "sp:beamte:1:-"
    assert quellen.schluessel_sp("beamte", 1, "01") == "sp:beamte:1:01"
    assert quellen.schluessel_seite(62) == "seite:62"


def test_alle_belegarten_der_aufgabe_vorhanden(tmp_belege: dict) -> None:
    arten = {schluessel.split(":")[0] for schluessel in tmp_belege["belege"]}
    assert {"ep", "fp", "vb", "meta", "sd", "inv", "ve", "sp"} <= arten
    assert not any(schluessel.startswith("ep:KL") for schluessel in tmp_belege["belege"])


def test_probe_ergebnisplanzeile_eines_produkts(tmp_belege: dict, pdf_dok: PdfDokument) -> None:
    bbox = _beleg(tmp_belege, "ep:010101:ordentliche_ertraege", 73)
    zeilen = [z for z in pdf_dok.zeilen_mit_rahmen(73) if z.woerter[0].text == "10"]
    assert len(zeilen) == 1
    betraege = [w for w in zeilen[0].woerter[1:] if w.text == "1.400"]
    assert betraege
    for wort in (zeilen[0].woerter[0], *betraege):
        assert _umschliesst(bbox, wort)


def test_probe_vorberichtsposten(tmp_belege: dict, pdf_dok: PdfDokument) -> None:
    bbox = _beleg(tmp_belege, "vb:steuerarten:gewerbesteuer", 27)
    treffer = [w for w in _woerter(pdf_dok, 27) if w.text == "7.800" and _umschliesst(bbox, w)]
    assert treffer


def test_probe_meta_einwohner(tmp_belege: dict, pdf_dok: PdfDokument) -> None:
    bbox = _beleg(tmp_belege, "meta:einwohner", 25)
    treffer = [w for w in _woerter(pdf_dok, 25) if w.text == "11.741" and _umschliesst(bbox, w)]
    assert treffer


def test_probe_schuldenstand(tmp_belege: dict, pdf_dok: PdfDokument) -> None:
    bbox = _beleg(tmp_belege, "sd:investitionskredite", 310)
    treffer = [w for w in _woerter(pdf_dok, 310) if w.text == "11.629" and _umschliesst(bbox, w)]
    assert treffer


def test_probe_massnahme_mit_kontowort(tmp_belege: dict, pdf_dok: PdfDokument) -> None:
    bbox = _beleg(tmp_belege, "inv:010601:010601:783112:auszahlung", 87)
    treffer = [
        w for w in _woerter(pdf_dok, 87) if w.text.startswith("783112") and _umschliesst(bbox, w)
    ]
    assert treffer


def test_probe_stellenzeile_im_querformat(tmp_belege: dict, pdf_dok: PdfDokument) -> None:
    bbox = _beleg(tmp_belege, "sp:beamte:1:-", 284)
    seite = tmp_belege["seiten"]["284"]
    assert seite["breite"] > seite["hoehe"]
    treffer = [w for w in _woerter(pdf_dok, 284) if w.text == "Bürgermeister/in"]
    assert treffer and _umschliesst(bbox, treffer[0])


def test_probe_stellenuebersicht_zeile_des_produktbereichs(
    tmp_belege: dict, pdf_dok: PdfDokument
) -> None:
    bbox = _beleg(tmp_belege, "sp:beamte:1:01", 287)
    zeilen = [z for z in pdf_dok.zeilen_mit_rahmen(287) if z.woerter[0].text == "01"]
    assert zeilen
    assert _umschliesst(bbox, zeilen[0].woerter[0])


def test_jede_gedruckte_ergebnisplanzeile_hat_einen_beleg(
    tmp_belege: dict, haushalt: dict, jahrgang: Jahrgang
) -> None:
    wertart = quellen._haushaltsjahr_wertart(jahrgang, "ergebnisplan")
    plan = lies_plan_csv(DATEN_WURZEL / ERGEBNISPLAN_CSV).filter(
        (pl.col("jahr") == jahrgang.haushaltsjahr) & (pl.col("wertart") == wertart)
    )
    erwartet: dict[str, int] = {}
    for zeile in plan.iter_rows(named=True):
        code = "GESAMT" if zeile["ebene"] == "GESAMT" else zeile["code"]
        if code.startswith("KL"):
            continue
        app_zeilen = haushalt["ergebnisplan"].get(code, {}).get("zeilen", {})
        if zeile["zeile_kanonisch"] not in app_zeilen:
            continue
        erwartet[f"ep:{code}:{zeile['zeile_kanonisch']}"] = zeile["pdf_seite"]
    assert len(erwartet) > 1500
    vorhanden = {
        schluessel: beleg["pdf_seite"]
        for schluessel, beleg in tmp_belege["belege"].items()
        if schluessel.startswith("ep:")
    }
    assert vorhanden == erwartet


def test_belege_decken_alle_datensaetze_der_aufgabe(
    tmp_belege: dict, haushalt: dict, investitionen: dict, stellenplan: dict
) -> None:
    belege = set(tmp_belege["belege"])

    def _art(praefix: str) -> set[str]:
        return {schluessel for schluessel in belege if schluessel.startswith(praefix + ":")}

    vb: set[str] = set()
    tabellen = {**haushalt["vorbericht"], "eigenkapital": haushalt["eigenkapital"]}
    for name, tabelle in tabellen.items():
        vb |= {f"vb:{name}:{p['posten']}" for p in tabelle["posten"] if p["quelle"] is not None}
        if tabelle["gesamt_vorbericht"]["quelle"] is not None:
            vb.add(f"vb:{name}:gesamt")
    assert _art("vb") == vb

    meta: set[str] = set()
    for name, eintrag in haushalt["meta"].items():
        if "wert" in eintrag:
            meta.add(f"meta:{name}")
        else:
            meta |= {f"meta:{name}.{unter}" for unter in eintrag}
    assert _art("meta") == meta

    assert _art("inv") == {
        f"inv:{m['produkt']}:{m['massnahme_id']}:{m['konto']}:{m['richtung']}"
        for m in investitionen["massnahmen"]
    }
    assert _art("ve") == {
        f"ve:{v['produkt']}:{v['massnahme_id']}:{v['konto']}"
        for v in investitionen["ve_faelligkeiten"]
    }
    assert _art("sd") == {"sd:investitionskredite", "sd:nrw_bank", "sd:liquiditaetskredite"}
    assert _art("sp") == {
        f"sp:{z['teil']}:{z['position']}:{z['produktbereich'] or '-'}"
        for z in stellenplan["zeilen"]
    }


def _zeilenidentitaet(schluessel: str) -> tuple[str, ...]:
    art, *rest = schluessel.split(":")
    if art == "ep":
        return ("ep", rest[1])
    if art in ("inv", "ve"):
        return ("kontozeile", *rest[:3])
    if art == "sp" and rest[2] != "-":
        return ("sp", rest[0], rest[2])
    return (schluessel,)


# Zwei verschiedene Werte, die dieselbe gedruckte Zeile belegen (Vorbericht S. 46: die Kreisumlage
# steht in der Transferaufwendungen-Tabelle und ist zugleich der Nettowert in `meta`).
GLEICHE_GEDRUCKTE_ZEILE = [
    frozenset({"meta:kreisumlage.netto", "vb:transferaufwendungen:kreisumlage"})
]


def test_keine_zwei_belege_teilen_dieselbe_bbox_ohne_dieselbe_zeile(tmp_belege: dict) -> None:
    gruppen: dict[tuple[int, tuple[float, ...]], list[str]] = {}
    for schluessel, beleg in tmp_belege["belege"].items():
        if beleg["bbox"] is not None:
            gruppen.setdefault((beleg["pdf_seite"], tuple(beleg["bbox"])), []).append(schluessel)
    zweifelhaft = [
        sorted(schluessel)
        for schluessel in gruppen.values()
        if len(schluessel) > 1
        and len({_zeilenidentitaet(s) for s in schluessel}) > 1
        and frozenset(schluessel) not in GLEICHE_GEDRUCKTE_ZEILE
    ]
    assert zweifelhaft == []


def test_bericht_listet_jeden_beleg_ohne_bbox_ausser_seiten(
    tmp_ergebnis: tuple[QuellenErgebnis, Path, Path], tmp_belege: dict
) -> None:
    ergebnis, _, daten = tmp_ergebnis
    text = (daten / QUELLENBELEGE_MD).read_text(encoding="utf-8")
    assert text.startswith("# Quellenbelege – Werte ohne Markierung\n")
    assert "\r" not in text and text.endswith("\n")
    ohne = [
        schluessel
        for schluessel, beleg in tmp_belege["belege"].items()
        if beleg["bbox"] is None and not schluessel.startswith("seite:")
    ]
    assert ohne, "mindestens ein Wert ohne Markierung erwartet (z. B. berechnete Werte)"
    for schluessel in ohne:
        assert f"`{schluessel}`" in text, schluessel
    assert ergebnis.anzahl_ohne_bbox == len(ohne)


def test_quellenbericht_eingecheckt_aktuell(
    tmp_ergebnis: tuple[QuellenErgebnis, Path, Path],
) -> None:
    _, _, daten = tmp_ergebnis
    assert (DATEN_WURZEL / QUELLENBELEGE_MD).read_bytes() == (daten / QUELLENBELEGE_MD).read_bytes()


def test_bericht_ist_sortiert_und_deterministisch(tmp_path: Path) -> None:
    belege = {
        "meta:flaeche": {"pdf_seite": 10, "bild": "s010.webp", "bbox": None},
        "ep:010101:ordentliche_ertraege": {"pdf_seite": 73, "bild": "s073.webp", "bbox": None},
        "ep:010101:steuern": {"pdf_seite": 73, "bild": "s073.webp", "bbox": [1.0, 2.0, 3.0, 4.0]},
        "seite:10": {"pdf_seite": 10, "bild": "s010.webp", "bbox": None},
    }
    gruende = {"meta:flaeche": "nicht_gefunden", "ep:010101:ordentliche_ertraege": "mehrdeutig"}
    erster, zweiter = tmp_path / "a.md", tmp_path / "b.md"
    quellen.schreibe_quellenbericht(belege, gruende, erster)
    quellen.schreibe_quellenbericht(dict(reversed(belege.items())), gruende, zweiter)
    text = erster.read_text(encoding="utf-8")
    assert erster.read_bytes() == zweiter.read_bytes()
    assert text.index("`ep:010101:ordentliche_ertraege`") < text.index("`meta:flaeche`")
    assert "`seite:10`" not in text
    assert "`ep:010101:steuern`" not in text
    assert "nicht_gefunden" in text and "mehrdeutig" in text


def test_tabellenzeile_findet_label_und_haushaltsjahrbetrag() -> None:
    zeilen = [
        _zeile(_wort("Grundsteuer", 40, 90, 100, 108), _wort("A", 92, 98, 100, 108)),
        _zeile(
            _wort("Grundsteuer", 40, 90, 120, 128),
            _wort("A", 92, 98, 120, 128),
            _wort("160", 300, 320, 120, 128),
            _wort("130", 340, 360, 120, 128),
            _wort("90", 380, 400, 120, 128),
        ),
    ]
    bbox, grund = quellen.finde_tabellenzeile(
        zeilen, "Grundsteuer A", [160, 130, 90], ziel_index=2, breite=595.28, hoehe=841.89
    )
    assert grund is None and bbox == [38.0, 118.0, 402.0, 130.0]
    assert quellen.finde_tabellenzeile(
        zeilen, "Grundsteuer A", [160, 130, 91], ziel_index=2, breite=595.28, hoehe=841.89
    ) == (None, GRUND_BETRAG_FEHLT)
    assert quellen.finde_tabellenzeile(
        zeilen, "Hundesteuer", [1, 2, 3], ziel_index=2, breite=595.28, hoehe=841.89
    ) == (None, GRUND_NICHT_GEFUNDEN)


def test_tabellenzeile_mit_umgebrochenem_label_und_nummerierung() -> None:
    zeilen = [
        _zeile(
            _wort("2.5.1", 40, 60, 100, 108),
            _wort("von", 62, 80, 100, 108),
            _wort("Banken", 82, 120, 100, 108),
            _wort("7.208", 300, 330, 100, 108),
            _wort("6.879", 340, 370, 100, 108),
            _wort("11.629", 380, 420, 100, 108),
        ),
        _zeile(
            _wort("für", 40, 60, 120, 128),
            _wort("Investitionen", 62, 120, 120, 128),
            _wort("7.208", 300, 330, 120, 128),
            _wort("6.879", 340, 370, 120, 128),
            _wort("11.629", 380, 420, 120, 128),
        ),
        _zeile(
            _wort("9.", 40, 50, 140, 148),
            _wort("Summe", 52, 90, 140, 148),
            _wort("28.631", 300, 330, 140, 148),
        ),
    ]
    bbox, grund = quellen.finde_tabellenzeile(
        zeilen,
        "Verbindlichkeiten aus Krediten für Investitionen",
        [7208, 6879, 11629],
        ziel_index=2,
        breite=595.28,
        hoehe=841.89,
    )
    assert grund is None and bbox is not None and bbox[1] == 118.0
    bbox, grund = quellen.finde_tabellenzeile(
        zeilen, "Summe", [28631], ziel_index=0, breite=595.28, hoehe=841.89
    )
    assert grund is None and bbox is not None and bbox[1] == 138.0


def test_tabellenzeile_zwei_gleiche_zeilen_sind_mehrdeutig_und_cent_werte_passen() -> None:
    doppelt = [
        _zeile(_wort("Summe", 40, 90, 100, 108), _wort("5", 300, 310, 100, 108)),
        _zeile(_wort("Summe", 40, 90, 200, 208), _wort("5", 300, 310, 200, 208)),
    ]
    assert quellen.finde_tabellenzeile(
        doppelt, "Summe", [5], ziel_index=0, breite=595.28, hoehe=841.89
    ) == (None, GRUND_MEHRDEUTIG)
    cent = [
        _zeile(
            _wort("Allgemeine", 40, 90, 100, 108),
            _wort("Rücklage", 92, 140, 100, 108),
            _wort("39.522.990,85", 300, 380, 100, 108),
        )
    ]
    bbox, grund = quellen.finde_tabellenzeile(
        cent, "Allgemeine Rücklage", [39522991], ziel_index=0, breite=595.28, hoehe=841.89
    )
    assert grund is None and bbox is not None


def test_meta_kandidaten_gedruckte_formen() -> None:
    assert quellen.meta_kandidaten(11741, "personen", False) == ["11.741"]
    assert quellen.meta_kandidaten("2026-03-03", "datum", False) == ["03.03.2026"]
    assert quellen.meta_kandidaten(315000, "euro", True) == ["315.000", "315"]
    assert quellen.meta_kandidaten(1325478, "euro", False) == ["1.325.478"]
    assert quellen.meta_kandidaten(242, "prozent", False) == ["242"]


def test_wertzeile_braucht_genau_eine_zeile_und_ignoriert_die_seitenzahl() -> None:
    zeilen = [
        _zeile(_wort("bei", 40, 60, 100, 108), _wort("11.741", 62, 100, 100, 108)),
        _zeile(_wort("25", 290, 300, 800, 808)),
    ]
    bbox, grund = quellen.finde_wertzeile(zeilen, ["11.741"], seite=25, breite=595.28, hoehe=841.89)
    assert grund is None and bbox is not None
    assert quellen.finde_wertzeile(zeilen, ["25"], seite=25, breite=595.28, hoehe=841.89) == (
        None,
        GRUND_NICHT_GEFUNDEN,
    )
    zwei = [*zeilen, _zeile(_wort("11.741", 40, 80, 300, 308))]
    assert quellen.finde_wertzeile(zwei, ["11.741"], seite=25, breite=595.28, hoehe=841.89) == (
        None,
        GRUND_MEHRDEUTIG,
    )
