"""Tests für die Belegbilder (Phase 7, DATA-04, Plan 07-03): Integrität und Schwärzung.

Die eingecheckten Bilder werden nur gelesen. Gerendert wird ausschließlich in tmp-Verzeichnisse.
WebP-Bytes werden nicht verglichen (nicht über Plattformen hinweg belegt); geprüft werden
Existenz, Pixelmaße und die Pixel innerhalb der Schwärzungsrechtecke.

PRIVACY (D-09, T-07-08): `lies_personennamen` liefert hier nur die Wortfolge, aus der die
Wortkästen bestimmt werden. Keine Assertion-Meldung nennt einen Namen; sie nennt nur
Seitenzahlen und Anzahlen.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import polars as pl
import pytest
from PIL import Image

from ostbevern.app_daten import APP_DATEN_WURZEL
from ostbevern.belegbilder import BelegbildFehler, bild_name, rendere_seiten
from ostbevern.konfiguration import Jahrgang
from ostbevern.pdf import PdfDokument, WortRahmen
from ostbevern.produkte import lies_personennamen, personenfeld_rechtecke
from ostbevern.quellen import BELEGBILDER_WURZEL, QUELLEN_JSON
from ostbevern.schema import (
    DATEN_WURZEL,
    HIERARCHIE_CSV,
    SEITEN_CSV,
    lies_hierarchie_csv,
    lies_seiten_csv,
)

MAX_KANAL_IN_SCHWAERZUNG = 40
MASSSTAB = 2


@pytest.fixture(scope="module")
def eingecheckt() -> dict:
    return json.loads((APP_DATEN_WURZEL / QUELLEN_JSON).read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def kontext() -> tuple[pl.DataFrame, pl.DataFrame]:
    return (
        lies_seiten_csv(DATEN_WURZEL / SEITEN_CSV),
        lies_hierarchie_csv(DATEN_WURZEL / HIERARCHIE_CSV),
    )


@pytest.fixture(scope="module")
def dokument(jahrgang: Jahrgang):
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as pdf:
        yield pdf


@pytest.fixture(scope="module")
def rechtecke(
    dokument: PdfDokument, jahrgang: Jahrgang, kontext: tuple[pl.DataFrame, pl.DataFrame]
) -> dict[int, tuple[tuple[float, float, float, float], ...]]:
    seiten, hierarchie = kontext
    return personenfeld_rechtecke(dokument, jahrgang, seiten, hierarchie)


def _seitentypen(seiten: pl.DataFrame) -> dict[int, str]:
    return {int(r["pdf_seite"]): str(r["typ"]) for r in seiten.iter_rows(named=True)}


def _erste_pi_seite(seiten: pl.DataFrame) -> int:
    return int(seiten.filter(pl.col("typ") == "produktinformationen")["pdf_seite"][0])


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


def test_jedes_bild_gehoert_zu_einem_beleg(eingecheckt: dict) -> None:
    belegseiten = {str(beleg["pdf_seite"]) for beleg in eingecheckt["belege"].values()}
    assert set(eingecheckt["seiten"]) == belegseiten


def test_produktinformationen_seite_ohne_schwaerzung_wird_nicht_gerendert(
    jahrgang: Jahrgang, tmp_path: Path
) -> None:
    seiten = lies_seiten_csv(DATEN_WURZEL / SEITEN_CSV)
    erste = _erste_pi_seite(seiten)

    with pytest.raises(BelegbildFehler, match=str(erste)):
        rendere_seiten(jahrgang.pdf_pfad, [erste], tmp_path, seitentypen=_seitentypen(seiten))
    assert list(tmp_path.iterdir()) == []


def test_leere_rechteckliste_fuer_produktinformationen_seite_wird_abgelehnt(
    jahrgang: Jahrgang, tmp_path: Path
) -> None:
    seiten = lies_seiten_csv(DATEN_WURZEL / SEITEN_CSV)
    erste = _erste_pi_seite(seiten)

    with pytest.raises(BelegbildFehler, match=str(erste)):
        rendere_seiten(
            jahrgang.pdf_pfad,
            [erste],
            tmp_path,
            seitentypen=_seitentypen(seiten),
            schwaerzungen={erste: ()},
        )
    assert list(tmp_path.iterdir()) == []


def test_fortsetzungsseite_ohne_personenfelder_wird_nur_mit_ausdruecklicher_freigabe_gerendert(
    jahrgang: Jahrgang, tmp_path: Path
) -> None:
    seiten = lies_seiten_csv(DATEN_WURZEL / SEITEN_CSV)
    erste = _erste_pi_seite(seiten)

    geschrieben = rendere_seiten(
        jahrgang.pdf_pfad,
        [erste],
        tmp_path,
        seitentypen=_seitentypen(seiten),
        ohne_personenfelder=[erste],
    )
    assert [pfad.name for pfad in geschrieben] == [bild_name(erste)]


def test_produktinformationen_seite_mit_schwaerzung_wird_geschwaerzt(
    jahrgang: Jahrgang, tmp_path: Path
) -> None:
    seiten = lies_seiten_csv(DATEN_WURZEL / SEITEN_CSV)
    erste = _erste_pi_seite(seiten)
    rechteck = [100.0, 100.0, 300.0, 140.0]

    geschrieben = rendere_seiten(
        jahrgang.pdf_pfad,
        [erste],
        tmp_path,
        seitentypen=_seitentypen(seiten),
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


def test_jedes_produkt_hat_rechtecke_auf_seiner_ersten_produktinformationen_seite(
    rechtecke: dict[int, tuple[tuple[float, float, float, float], ...]],
    kontext: tuple[pl.DataFrame, pl.DataFrame],
    eingecheckt: dict,
) -> None:
    seiten, _ = kontext
    pi = seiten.filter(pl.col("produkt").is_not_null() & (pl.col("typ") == "produktinformationen"))
    erste = pi.group_by("produkt").agg(pl.col("pdf_seite").min())["pdf_seite"].to_list()
    assert len(erste) == 63
    fehlend = sorted(set(erste) - set(rechtecke))
    assert fehlend == [], f"{len(fehlend)} erste Produktinformationen-Seiten ohne Rechteck"
    nicht_im_beleg = sorted(
        str(seite) for seite in rechtecke if str(seite) not in eingecheckt["seiten"]
    )
    assert nicht_im_beleg == [], f"{len(nicht_im_beleg)} geschwärzte Seiten ohne Belegbild"


def _liegt_in(wort: WortRahmen, rechteck: tuple[float, float, float, float]) -> bool:
    x0, top, x1, bottom = rechteck
    return x0 <= wort.x0 and wort.x1 <= x1 and top <= wort.top and wort.bottom <= bottom


def _namenswoerter(dokument: PdfDokument, seite: int, text: str) -> list[WortRahmen] | None:
    """Wortkästen der zusammenhängenden Wortfolge `text` auf `seite` (None, wenn nicht gefunden)."""
    woerter = [w for zeile in dokument.zeilen_mit_rahmen(seite, fein=True) for w in zeile.woerter]
    teile = text.split()
    for start in range(len(woerter) - len(teile) + 1):
        if [w.text for w in woerter[start : start + len(teile)]] == teile:
            return woerter[start : start + len(teile)]
    return None


def test_jedes_namenswort_liegt_in_einem_schwaerzungsrechteck(
    dokument: PdfDokument,
    jahrgang: Jahrgang,
    kontext: tuple[pl.DataFrame, pl.DataFrame],
    rechtecke: dict[int, tuple[tuple[float, float, float, float], ...]],
) -> None:
    seiten, hierarchie = kontext
    namen = lies_personennamen(dokument, jahrgang, seiten, hierarchie)
    assert len(namen) >= 63
    nicht_gefunden = 0
    nicht_abgedeckt = 0
    geprueft = 0
    for seite, text in namen:
        woerter = _namenswoerter(dokument, seite, text)
        if woerter is None:
            nicht_gefunden += 1
            continue
        for wort in woerter:
            geprueft += 1
            if not any(_liegt_in(wort, r) for r in rechtecke.get(seite, ())):
                nicht_abgedeckt += 1
    assert nicht_gefunden == 0, f"{nicht_gefunden} von {len(namen)} Feldwerten nicht lokalisiert"
    assert geprueft > 0
    assert nicht_abgedeckt == 0, f"{nicht_abgedeckt} von {geprueft} Wortkästen nicht geschwärzt"


def test_in_jedem_eingecheckten_schwaerzungsrechteck_sind_die_pixel_schwarz(
    rechtecke: dict[int, tuple[tuple[float, float, float, float], ...]], eingecheckt: dict
) -> None:
    zu_hell: list[int] = []
    geprueft = 0
    for seite, liste in sorted(rechtecke.items()):
        pfad = BELEGBILDER_WURZEL / eingecheckt["seiten"][str(seite)]["bild"]
        with Image.open(pfad) as bild:
            rgb = bild.convert("RGB")
        for x0, top, x1, bottom in liste:
            box = (
                math.ceil(x0 * MASSSTAB),
                math.ceil(top * MASSSTAB),
                math.floor(x1 * MASSSTAB),
                math.floor(bottom * MASSSTAB),
            )
            ausschnitt = rgb.crop(box)
            geprueft += 1
            if (
                max(max(maximum for _, maximum in ausschnitt.getextrema()), 0)
                > MAX_KANAL_IN_SCHWAERZUNG
            ):
                zu_hell.append(seite)
    assert geprueft > 0
    assert zu_hell == [], (
        f"{len(zu_hell)} von {geprueft} Rechtecken nicht schwarz (Seiten {zu_hell})"
    )
