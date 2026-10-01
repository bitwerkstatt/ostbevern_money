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


def test_fehlende_produktgruppe_kopfzeile_meldet_schluessel(tmp_path: Path) -> None:
    text = re.sub(r"(?m)^produktgruppe\s*=.*\n", "", _jahrgangsdatei_text())
    _schreibe_jahrgangsdatei(tmp_path, text)
    with pytest.raises(KonfigurationsFehler, match="kopfzeilen.produktgruppe"):
        lade_jahrgang(STANDARD_JAHR, verzeichnis=tmp_path)


def test_seitentypen_ohne_teilfinanzplan_meldet_schluessel(tmp_path: Path) -> None:
    text = re.sub(r"(?m)^teilfinanzplan\s*=.*\n", "", _jahrgangsdatei_text())
    _schreibe_jahrgangsdatei(tmp_path, text)
    with pytest.raises(KonfigurationsFehler, match="teilfinanzplan"):
        lade_jahrgang(STANDARD_JAHR, verzeichnis=tmp_path)


def test_ungueltiges_kopfzeilen_muster_meldet_schluessel(tmp_path: Path) -> None:
    text = re.sub(
        r"(?m)^produktgruppe\s*=.*$",
        "produktgruppe = '('",
        _jahrgangsdatei_text(),
        count=1,
    )
    _schreibe_jahrgangsdatei(tmp_path, text)
    with pytest.raises(KonfigurationsFehler, match="kopfzeilen.produktgruppe"):
        lade_jahrgang(STANDARD_JAHR, verzeichnis=tmp_path)


def test_ueberlappende_seitenbereiche_werden_abgelehnt(tmp_path: Path) -> None:
    text = re.sub(
        r"(?m)^teilplaene\s*=\s*\{\s*von\s*=\s*\d+",
        "teilplaene = { von = 63",
        _jahrgangsdatei_text(),
        count=1,
    )
    _schreibe_jahrgangsdatei(tmp_path, text)
    with pytest.raises(KonfigurationsFehler, match="überlappen"):
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


def _ohne_anhang_a(text: str) -> str:
    """Entfernt eine vorhandene [anhang_a]-Tabelle (steht am Dateiende); ist sie
    noch nicht vorhanden, bleibt der Text unverändert."""
    return re.sub(r"(?ms)^\[anhang_a\]\n.*", "", text)


def test_lade_sollwerte_lehnt_ungueltigen_anhang_a_schluessel_ab(tmp_path: Path) -> None:
    text = _ohne_anhang_a(_sollwertdatei_text())
    text += '\n[anhang_a]\n"1" = { name = "Testfall", pdf_seite = 1 }\n'
    _schreibe_sollwertdatei(tmp_path, text)
    with pytest.raises(KonfigurationsFehler, match="anhang_a"):
        lade_sollwerte(STANDARD_JAHR, verzeichnis=tmp_path)


def test_lade_sollwerte_lehnt_anhang_a_eintrag_ohne_namen_ab(tmp_path: Path) -> None:
    text = _ohne_anhang_a(_sollwertdatei_text())
    text += '\n[anhang_a]\n"01" = { pdf_seite = 1 }\n'
    _schreibe_sollwertdatei(tmp_path, text)
    with pytest.raises(KonfigurationsFehler, match="anhang_a"):
        lade_sollwerte(STANDARD_JAHR, verzeichnis=tmp_path)


# [synthetische_produktgruppen] (D-14, 261001-oim): Zuordnung eines Produkts zu einer
# synthetischen PG, wenn der Standard (Code = erste vier Ziffern des Produktcodes)
# nicht zutrifft. Mutiert die echte 2026.toml-Tabelle "1502" (produkt="150102",
# name="Tourismus", pdf_seite=299), nie ein frei erfundenes Fixture.


def test_synthetische_produktgruppen_vollstaendig_und_gueltig() -> None:
    jahrgang = lade_jahrgang(STANDARD_JAHR)
    assert jahrgang.synthetische_produktgruppen
    for code, eintrag in jahrgang.synthetische_produktgruppen.items():
        assert eintrag.code == code
        assert re.match(r"^\d{4}$", code)
        assert re.match(r"^\d{6}$", eintrag.produkt)
        assert eintrag.produkt[:2] == code[:2]
        assert eintrag.name
        assert 1 <= eintrag.pdf_seite <= jahrgang.anzahlen.pdf_seiten


def test_jahrgangsdatei_ohne_synthetische_produktgruppen_laedt_leere_zuordnung(
    tmp_path: Path,
) -> None:
    text = re.sub(r"(?ms)^\[synthetische_produktgruppen\..*", "", _jahrgangsdatei_text())
    _schreibe_jahrgangsdatei(tmp_path, text)
    jahrgang = lade_jahrgang(STANDARD_JAHR, verzeichnis=tmp_path)
    assert jahrgang.synthetische_produktgruppen == {}


def test_synthetische_produktgruppen_schluessel_nicht_vierstellig_wird_abgelehnt(
    tmp_path: Path,
) -> None:
    text = re.sub(
        r'\[synthetische_produktgruppen\."1502"\]',
        '[synthetische_produktgruppen."150"]',
        _jahrgangsdatei_text(),
        count=1,
    )
    _schreibe_jahrgangsdatei(tmp_path, text)
    with pytest.raises(KonfigurationsFehler, match="synthetische_produktgruppen"):
        lade_jahrgang(STANDARD_JAHR, verzeichnis=tmp_path)


def test_synthetische_produktgruppen_eintrag_ohne_produkt_meldet_feld(tmp_path: Path) -> None:
    text = re.sub(r'(?m)^produkt\s*=\s*"150102"\n', "", _jahrgangsdatei_text(), count=1)
    _schreibe_jahrgangsdatei(tmp_path, text)
    with pytest.raises(KonfigurationsFehler, match="synthetische_produktgruppen"):
        lade_jahrgang(STANDARD_JAHR, verzeichnis=tmp_path)


def test_synthetische_produktgruppen_eintrag_mit_unbekanntem_schluessel_wird_abgelehnt(
    tmp_path: Path,
) -> None:
    text = re.sub(
        r'(\[synthetische_produktgruppen\."1502"\]\n)',
        r'\1unbekannt = "x"\n',
        _jahrgangsdatei_text(),
        count=1,
    )
    _schreibe_jahrgangsdatei(tmp_path, text)
    with pytest.raises(KonfigurationsFehler, match="synthetische_produktgruppen"):
        lade_jahrgang(STANDARD_JAHR, verzeichnis=tmp_path)


def test_synthetische_produktgruppen_produkt_nicht_sechsstellig_wird_abgelehnt(
    tmp_path: Path,
) -> None:
    text = re.sub(
        r'(?m)^produkt\s*=\s*"150102"$', 'produkt = "1501"', _jahrgangsdatei_text(), count=1
    )
    _schreibe_jahrgangsdatei(tmp_path, text)
    with pytest.raises(KonfigurationsFehler, match="synthetische_produktgruppen"):
        lade_jahrgang(STANDARD_JAHR, verzeichnis=tmp_path)


def test_synthetische_produktgruppen_produkt_falscher_produktbereich_wird_abgelehnt(
    tmp_path: Path,
) -> None:
    text = re.sub(
        r'(?m)^produkt\s*=\s*"150102"$', 'produkt = "160101"', _jahrgangsdatei_text(), count=1
    )
    _schreibe_jahrgangsdatei(tmp_path, text)
    with pytest.raises(KonfigurationsFehler, match="synthetische_produktgruppen"):
        lade_jahrgang(STANDARD_JAHR, verzeichnis=tmp_path)


def test_synthetische_produktgruppen_leerer_name_wird_abgelehnt(tmp_path: Path) -> None:
    text = re.sub(r'(?m)^name\s*=\s*"Tourismus"$', 'name = ""', _jahrgangsdatei_text(), count=1)
    _schreibe_jahrgangsdatei(tmp_path, text)
    with pytest.raises(KonfigurationsFehler, match="synthetische_produktgruppen"):
        lade_jahrgang(STANDARD_JAHR, verzeichnis=tmp_path)


def test_synthetische_produktgruppen_pdf_seite_ausserhalb_bereich_wird_abgelehnt(
    tmp_path: Path,
) -> None:
    text = re.sub(r"(?m)^pdf_seite\s*=\s*299$", "pdf_seite = 0", _jahrgangsdatei_text(), count=1)
    _schreibe_jahrgangsdatei(tmp_path, text)
    with pytest.raises(KonfigurationsFehler, match="synthetische_produktgruppen"):
        lade_jahrgang(STANDARD_JAHR, verzeichnis=tmp_path)


def test_synthetische_produktgruppen_pdf_seite_als_bool_wird_abgelehnt(tmp_path: Path) -> None:
    text = re.sub(r"(?m)^pdf_seite\s*=\s*299$", "pdf_seite = true", _jahrgangsdatei_text(), count=1)
    _schreibe_jahrgangsdatei(tmp_path, text)
    with pytest.raises(KonfigurationsFehler, match="synthetische_produktgruppen"):
        lade_jahrgang(STANDARD_JAHR, verzeichnis=tmp_path)


def test_synthetische_produktgruppen_doppeltes_produkt_wird_abgelehnt(tmp_path: Path) -> None:
    text = _jahrgangsdatei_text() + (
        '\n[synthetische_produktgruppen."1503"]\n'
        'produkt = "150102"\n'
        'name = "Duplikat"\n'
        "pdf_seite = 299\n"
    )
    _schreibe_jahrgangsdatei(tmp_path, text)
    with pytest.raises(KonfigurationsFehler, match="synthetische_produktgruppen"):
        lade_jahrgang(STANDARD_JAHR, verzeichnis=tmp_path)


def test_synthetische_produktgruppen_falscher_typ_wird_abgelehnt(tmp_path: Path) -> None:
    ohne = re.sub(r"(?ms)^\[synthetische_produktgruppen\..*", "", _jahrgangsdatei_text())
    text = ohne + '\nsynthetische_produktgruppen = "nicht-tabelle"\n'
    _schreibe_jahrgangsdatei(tmp_path, text)
    with pytest.raises(KonfigurationsFehler, match="synthetische_produktgruppen"):
        lade_jahrgang(STANDARD_JAHR, verzeichnis=tmp_path)


# [haushaltsquerschnitt_pg] (D-14, 261001-oim): optionale Sollwerte für den
# Haushaltsquerschnitt-Abgleich einer synthetischen PG (Phase 3 Regel 7). Mutiert die
# echte 2026_sollwerte.toml-Zeile "1501".


def test_haushaltsquerschnitt_pg_schluessel_nicht_vierstellig_wird_abgelehnt(
    tmp_path: Path,
) -> None:
    text = re.sub(r'(?m)^"1501" = ', '"150" = ', _sollwertdatei_text(), count=1)
    _schreibe_sollwertdatei(tmp_path, text)
    with pytest.raises(KonfigurationsFehler, match="haushaltsquerschnitt_pg"):
        lade_sollwerte(STANDARD_JAHR, verzeichnis=tmp_path)


def test_haushaltsquerschnitt_pg_eintrag_ohne_ergebnis_meldet_feld(tmp_path: Path) -> None:
    text = re.sub(
        r'(?m)^("1501" = \{ )ergebnis_mit_internen_verrechnungen = -?\d+, (pdf_seite = \d+ \})$',
        r"\1\2",
        _sollwertdatei_text(),
        count=1,
    )
    _schreibe_sollwertdatei(tmp_path, text)
    with pytest.raises(KonfigurationsFehler, match="haushaltsquerschnitt_pg"):
        lade_sollwerte(STANDARD_JAHR, verzeichnis=tmp_path)


def test_haushaltsquerschnitt_pg_ungueltige_pdf_seite_wird_abgelehnt(tmp_path: Path) -> None:
    text = re.sub(
        r'(?m)^("1501" = \{ ergebnis_mit_internen_verrechnungen = -?\d+, pdf_seite = )\d+( \})$',
        r"\g<1>0\2",
        _sollwertdatei_text(),
        count=1,
    )
    _schreibe_sollwertdatei(tmp_path, text)
    with pytest.raises(KonfigurationsFehler, match="haushaltsquerschnitt_pg"):
        lade_sollwerte(STANDARD_JAHR, verzeichnis=tmp_path)


def test_sollwertdatei_ohne_haushaltsquerschnitt_pg_bleibt_gueltig(tmp_path: Path) -> None:
    text = re.sub(r"(?ms)^\[haushaltsquerschnitt_pg\]\n.*?(?=^\[)", "", _sollwertdatei_text())
    _schreibe_sollwertdatei(tmp_path, text)
    sollwerte = lade_sollwerte(STANDARD_JAHR, verzeichnis=tmp_path)
    assert "haushaltsquerschnitt_pg" not in sollwerte
