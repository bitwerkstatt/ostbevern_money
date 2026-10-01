"""Tests für ostbevern.konfiguration: lade_jahrgang und lade_sollwerte.

Fixtures sind Textvarianten der echten Jahrgangs-/Sollwertdatei (gelesen, verändert,
in tmp_path geschrieben). Kein Testcode enthält Jahrgangszahlen, Seitenzahlen oder
Sollwert-Literale (D-08) – alle Vergleichswerte kommen aus den geladenen Konstanten
oder werden per Regex aus der echten Datei abgeleitet.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from ostbevern.konfiguration import (
    JAHRGAENGE_VERZEICHNIS,
    PFLICHT_SEITENBEREICHE,
    STANDARD_JAHR,
    KonfigurationsFehler,
    lade_jahrgang,
    lade_sollwerte,
)


def _jahrgangsdatei_text() -> str:
    pfad = JAHRGAENGE_VERZEICHNIS / f"{STANDARD_JAHR}.toml"
    return pfad.read_text(encoding="utf-8")


def _sollwertdatei_text() -> str:
    pfad = JAHRGAENGE_VERZEICHNIS / f"{STANDARD_JAHR}_sollwerte.toml"
    return pfad.read_text(encoding="utf-8")


def _schreibe_jahrgangsdatei(tmp_path: Path, text: str, jahr: int = STANDARD_JAHR) -> Path:
    pfad = tmp_path / f"{jahr}.toml"
    pfad.write_text(text, encoding="utf-8")
    return pfad


def _schreibe_sollwertdatei(tmp_path: Path, text: str, jahr: int = STANDARD_JAHR) -> Path:
    pfad = tmp_path / f"{jahr}_sollwerte.toml"
    pfad.write_text(text, encoding="utf-8")
    return pfad


def test_lade_jahrgang_gibt_vollstaendigen_jahrgang_zurueck() -> None:
    jahrgang = lade_jahrgang(STANDARD_JAHR)
    for plantyp in ("ergebnisplan", "finanzplan", "investitionen"):
        assert jahrgang.spalten[plantyp]
    for name in PFLICHT_SEITENBEREICHE:
        assert name in jahrgang.seitenbereiche
    re.compile(jahrgang.kopfzeilen.produktbereich)
    re.compile(jahrgang.kopfzeilen.produkt)


def test_seitenbereiche_liegen_im_gueltigen_bereich() -> None:
    jahrgang = lade_jahrgang(STANDARD_JAHR)
    for bereich in jahrgang.seitenbereiche.values():
        assert 1 <= bereich.von <= bereich.bis <= jahrgang.anzahlen.pdf_seiten


def test_fehlender_pdf_pfad_meldet_schluessel(tmp_path: Path) -> None:
    text = re.sub(r"(?m)^pdf_pfad\s*=.*\n", "", _jahrgangsdatei_text())
    _schreibe_jahrgangsdatei(tmp_path, text)
    with pytest.raises(KonfigurationsFehler, match="pdf_pfad"):
        lade_jahrgang(STANDARD_JAHR, verzeichnis=tmp_path)


def test_fehlende_spalten_tabelle_meldet_schluessel(tmp_path: Path) -> None:
    text = re.sub(r"(?ms)^\[spalten\]\n.*?(?=^\[)", "", _jahrgangsdatei_text())
    _schreibe_jahrgangsdatei(tmp_path, text)
    with pytest.raises(KonfigurationsFehler, match="spalten"):
        lade_jahrgang(STANDARD_JAHR, verzeichnis=tmp_path)


def test_fehlende_jahrgangsdatei_meldet_pfad(tmp_path: Path) -> None:
    fehlendes_jahr = STANDARD_JAHR + 1
    with pytest.raises(KonfigurationsFehler, match=str(fehlendes_jahr)):
        lade_jahrgang(fehlendes_jahr, verzeichnis=tmp_path)


def test_abweichendes_haushaltsjahr_wird_abgelehnt(tmp_path: Path) -> None:
    anderes_jahr = STANDARD_JAHR + 1
    text = re.sub(
        r"(?m)^haushaltsjahr\s*=\s*\d+",
        f"haushaltsjahr = {anderes_jahr}",
        _jahrgangsdatei_text(),
        count=1,
    )
    _schreibe_jahrgangsdatei(tmp_path, text)
    with pytest.raises(KonfigurationsFehler):
        lade_jahrgang(STANDARD_JAHR, verzeichnis=tmp_path)


def test_absoluter_pdf_pfad_wird_abgelehnt(tmp_path: Path) -> None:
    text = re.sub(
        r'(?m)^pdf_pfad\s*=\s*".*"',
        'pdf_pfad = "/etc/passwd"',
        _jahrgangsdatei_text(),
        count=1,
    )
    _schreibe_jahrgangsdatei(tmp_path, text)
    with pytest.raises(KonfigurationsFehler):
        lade_jahrgang(STANDARD_JAHR, verzeichnis=tmp_path)


def test_relativer_pdf_pfad_ausserhalb_projekt_wird_abgelehnt(tmp_path: Path) -> None:
    text = re.sub(
        r'(?m)^pdf_pfad\s*=\s*".*"',
        'pdf_pfad = "../ausserhalb.pdf"',
        _jahrgangsdatei_text(),
        count=1,
    )
    _schreibe_jahrgangsdatei(tmp_path, text)
    with pytest.raises(KonfigurationsFehler):
        lade_jahrgang(STANDARD_JAHR, verzeichnis=tmp_path)


def test_seitenbereich_von_groesser_bis_wird_abgelehnt(tmp_path: Path) -> None:
    muster = re.compile(
        r"(?m)^(haushaltssatzung\s*=\s*\{\s*von\s*=\s*)(\d+)(,\s*bis\s*=\s*)(\d+)(\s*\})"
    )
    text = muster.sub(
        lambda m: f"{m.group(1)}{m.group(4)}{m.group(3)}{m.group(2)}{m.group(5)}",
        _jahrgangsdatei_text(),
        count=1,
    )
    _schreibe_jahrgangsdatei(tmp_path, text)
    with pytest.raises(KonfigurationsFehler, match="haushaltssatzung"):
        lade_jahrgang(STANDARD_JAHR, verzeichnis=tmp_path)


def test_lade_sollwerte_gibt_satzung_und_gesamtergebnisplan_zurueck() -> None:
    sollwerte = lade_sollwerte(STANDARD_JAHR)
    assert sollwerte["haushaltsjahr"] == STANDARD_JAHR
    assert "satzung" in sollwerte
    assert "gesamtergebnisplan" in sollwerte


def test_sollwert_als_float_wird_abgelehnt(tmp_path: Path) -> None:
    text = re.sub(
        r"(?m)^(ertraege\s*=\s*\d+)$",
        r"\1.0",
        _sollwertdatei_text(),
        count=1,
    )
    _schreibe_sollwertdatei(tmp_path, text)
    with pytest.raises(KonfigurationsFehler):
        lade_sollwerte(STANDARD_JAHR, verzeichnis=tmp_path)


def test_gesamtergebnisplan_zeile_mit_falscher_laenge_wird_abgelehnt(tmp_path: Path) -> None:
    text = _sollwertdatei_text()
    zeilen_muster = re.compile(r'(?m)^"10" = \[(?P<werte>[^\]]*)\]$')
    treffer = zeilen_muster.search(text)
    assert treffer is not None
    werte = [w.strip() for w in treffer.group("werte").split(",")]
    gekuerzt = ", ".join(werte[:-1])
    text = zeilen_muster.sub(f'"10" = [{gekuerzt}]', text, count=1)
    _schreibe_sollwertdatei(tmp_path, text)
    with pytest.raises(KonfigurationsFehler, match="10"):
        lade_sollwerte(STANDARD_JAHR, verzeichnis=tmp_path)


def test_lade_sollwerte_gibt_alle_tabellen_vollstaendig_zurueck() -> None:
    jahrgang = lade_jahrgang(STANDARD_JAHR)
    sollwerte = lade_sollwerte(STANDARD_JAHR)

    gesamtergebnisplan = sollwerte["gesamtergebnisplan"]
    assert len(gesamtergebnisplan["zeilen"]) == 21

    gesamtfinanzplan = sollwerte["gesamtfinanzplan"]
    assert gesamtfinanzplan["ansatz"]
    assert gesamtfinanzplan["ve"]

    teilergebnisplaene_pb = sollwerte["teilergebnisplaene_pb"]
    assert len(teilergebnisplaene_pb) == jahrgang.anzahlen.produktbereiche
    for eintrag in teilergebnisplaene_pb.values():
        assert set(eintrag) == {
            "ordentliche_ertraege",
            "ordentliche_aufwendungen",
            "ergebnis_mit_internen_verrechnungen",
        }

    teilergebnisplaene_pb_summe = sollwerte["teilergebnisplaene_pb_summe"]
    assert "ordentliche_ertraege" in teilergebnisplaene_pb_summe
    assert "ordentliche_aufwendungen" in teilergebnisplaene_pb_summe


def test_sollwertdatei_ohne_gesamtfinanzplan_meldet_schluessel(tmp_path: Path) -> None:
    text = re.sub(
        r"(?ms)^\[gesamtfinanzplan\].*?(?=^\[(?!gesamtfinanzplan))",
        "",
        _sollwertdatei_text(),
    )
    _schreibe_sollwertdatei(tmp_path, text)
    with pytest.raises(KonfigurationsFehler, match="gesamtfinanzplan"):
        lade_sollwerte(STANDARD_JAHR, verzeichnis=tmp_path)


def test_teilergebnisplaene_pb_eintrag_ohne_ordentliche_aufwendungen_meldet_feld(
    tmp_path: Path,
) -> None:
    text = _sollwertdatei_text()
    eintrag_muster = re.compile(r'(?m)^"01" = \{ (?P<inhalt>[^}]*) \}$')
    treffer = eintrag_muster.search(text)
    assert treffer is not None
    ohne_aufwendungen = re.sub(
        r"ordentliche_aufwendungen\s*=\s*-?\d+,\s*", "", treffer.group("inhalt")
    )
    text = eintrag_muster.sub(f'"01" = {{ {ohne_aufwendungen} }}', text, count=1)
    _schreibe_sollwertdatei(tmp_path, text)
    with pytest.raises(KonfigurationsFehler, match="01"):
        lade_sollwerte(STANDARD_JAHR, verzeichnis=tmp_path)


def test_gesamtfinanzplan_ansatz_schluessel_ohne_zweistellige_zeile_wird_abgelehnt(
    tmp_path: Path,
) -> None:
    text = re.sub(r'(?m)^"09" = (\d+)$', r'"9" = \1', _sollwertdatei_text(), count=1)
    _schreibe_sollwertdatei(tmp_path, text)
    with pytest.raises(KonfigurationsFehler):
        lade_sollwerte(STANDARD_JAHR, verzeichnis=tmp_path)
