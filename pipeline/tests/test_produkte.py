"""Tests für ostbevern.produkte: Produktinformationen und Erläuterungen (EXTR-06, EXTR-08).

Liest nur das Original-PDF (über die `jahrgang`-Fixture) und eingecheckte, bereits von
früheren Phasen erzeugte CSVs (seiten.csv, hierarchie.csv, ergebnisplan.csv) als Kontext;
nie `daten/aufbereitet/produkte.json`/`erlaeuterungen.csv` selbst als Quelle. Keine
Jahrgangs-, Seiten- oder Sollwert-Literale — alles kommt aus `lade_jahrgang(STANDARD_JAHR)`,
`lade_sollwerte(STANDARD_JAHR)` oder den eingecheckten CSVs.

PRIVACY (D-09): Dieses Modul liest nie einen Personennamen in eine Variable, die auf dem
Bildschirm/in Testausgaben erscheinen könnte, außer über `lies_personennamen` selbst, deren
Ergebnis ausschließlich in Mengenvergleiche (nie in eine Fehlermeldung oder ein print)
einfließt.
"""

from __future__ import annotations

import dataclasses
import re
from pathlib import Path

import polars as pl
import pytest

from ostbevern.freitext import verbinde_zeilen
from ostbevern.konfiguration import STANDARD_JAHR, Jahrgang, lade_sollwerte, layout_text
from ostbevern.pdf import PdfDokument, Textzeile
from ostbevern.produkte import (
    BINDUNGSGRADE,
    KLASSIFIZIERUNGEN,
    PERSONENFELDER,
    Erlaeuterung,
    Grundzahl,
    ProdukteFehler,
    extrahiere_produkte,
    lies_erlaeuterungen,
    lies_grundzahlen,
    lies_personennamen,
    lies_produktinformationen,
    pruefe_plausibilitaet,
    zerlege_felder,
)
from ostbevern.schema import (
    DATEN_WURZEL,
    ERGEBNISPLAN_CSV,
    ERLAEUTERUNGEN_CSV,
    GRUNDZAHLEN_CSV,
    HIERARCHIE_CSV,
    PRODUKT_SCHLUESSEL,
    PRODUKTE_JSON,
    SEITEN_CSV,
    SchemaFehler,
    lies_grundzahlen_csv,
    lies_hierarchie_csv,
    lies_plan_csv,
    lies_produkte_json,
    lies_seiten_csv,
    schreibe_produkte_json,
)


@pytest.fixture(scope="module")
def kontext() -> tuple[pl.DataFrame, pl.DataFrame]:
    seiten = lies_seiten_csv(DATEN_WURZEL / SEITEN_CSV)
    hierarchie = lies_hierarchie_csv(DATEN_WURZEL / HIERARCHIE_CSV)
    return seiten, hierarchie


@pytest.fixture(scope="module")
def produktinfos(jahrgang: Jahrgang, kontext: tuple[pl.DataFrame, pl.DataFrame]) -> tuple:
    seiten, hierarchie = kontext
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        return tuple(lies_produktinformationen(dokument, jahrgang, seiten, hierarchie))


@pytest.fixture(scope="module")
def produkte_json(jahrgang: Jahrgang) -> list[dict]:
    """Regeneriert produkte.json einmal pro Testlauf (liest nie die eingecheckte Datei
    als Quelle, D-06-Stil); `extrahiere_produkte` schreibt nach `DATEN_WURZEL/PRODUKTE_JSON`."""
    extrahiere_produkte(jahrgang)
    return lies_produkte_json(DATEN_WURZEL / PRODUKTE_JSON)


@pytest.fixture(scope="module")
def erlaeuterungen(
    jahrgang: Jahrgang, kontext: tuple[pl.DataFrame, pl.DataFrame]
) -> tuple[Erlaeuterung, ...]:
    seiten, hierarchie = kontext
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        return tuple(lies_erlaeuterungen(dokument, jahrgang, seiten, hierarchie))


@pytest.fixture(scope="module")
def grundzahlen(
    jahrgang: Jahrgang, kontext: tuple[pl.DataFrame, pl.DataFrame]
) -> tuple[Grundzahl, ...]:
    seiten, hierarchie = kontext
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        return tuple(lies_grundzahlen(dokument, jahrgang, seiten, hierarchie))


def test_verbinde_zeilen_entfernt_leerzeichen_vor_komma_leistungen_label() -> None:
    # Regressions-Doku (eigentlicher Test in test_freitext.py): die Fließtext-Fixfunktion
    # wird von produkte.py für die Leistungen-Label-Zeile (010602, S. 88) gebraucht.
    assert (
        verbinde_zeilen(["Leistungen , die unter anderen Produkten veranschlagt werden:"])
        == "Leistungen, die unter anderen Produkten veranschlagt werden:"
    )


def test_produkte_json_hat_63_codes_sortiert_mit_schluessel(produkte_json: list[dict]) -> None:
    assert len(produkte_json) == 63
    codes = [p["code"] for p in produkte_json]
    assert codes == sorted(codes)
    for produkt in produkte_json:
        assert tuple(produkt) == PRODUKT_SCHLUESSEL


_STRING_FELDER = (
    "fachbereich",
    "gremium",
    "beschreibung",
    "auftragsgrundlage",
    "bindungsgrad",
    "bindungsgrad_original",
    "klassifizierung",
    "zielgruppe",
    "ziele",
)


def test_produkte_json_felder_nicht_leer_und_vokabular(produkte_json: list[dict]) -> None:
    seiten = lies_seiten_csv(DATEN_WURZEL / SEITEN_CSV)
    for produkt in produkte_json:
        for feld in _STRING_FELDER:
            wert = produkt[feld]
            assert isinstance(wert, str) and wert, (produkt["code"], feld)
        assert produkt["bindungsgrad"] in set(BINDUNGSGRADE.values())
        assert produkt["klassifizierung"] in KLASSIFIZIERUNGEN
        assert produkt["leistungen"] and all(
            isinstance(eintrag, str) and eintrag for eintrag in produkt["leistungen"]
        )
        erwartete_seiten = sorted(
            seiten.filter(pl.col("produkt") == produkt["code"])["pdf_seite"].to_list()
        )
        assert produkt["pdf_seiten"] == erwartete_seiten


_VERBOTENE_MUSTER = (
    "(cid:15)",
    "  ",
)


def test_produkte_json_keine_rohartefakte(produkte_json: list[dict]) -> None:
    standalone_c = re.compile(r"(?<!\w) C (?!\w)|^C | C$")
    for produkt in produkte_json:
        werte = [produkt[feld] for feld in _STRING_FELDER] + list(produkt["leistungen"])
        for wert in werte:
            for verboten in _VERBOTENE_MUSTER:
                assert verboten not in wert, (produkt["code"], wert)
            assert not standalone_c.search(wert), (produkt["code"], wert)
            assert wert == wert.strip(), (produkt["code"], repr(wert))


def test_stichprobe_produktinfo_030101(produkte_json: list[dict]) -> None:
    sollwerte = lade_sollwerte(STANDARD_JAHR)
    stichprobe = sollwerte["stichproben"]["produktinfo"]
    produkt = next(p for p in produkte_json if p["code"] == stichprobe["produkt"])
    assert produkt["fachbereich"] == stichprobe["fachbereich"]
    assert produkt["gremium"] == stichprobe["gremium"]
    assert produkt["bindungsgrad"] == stichprobe["bindungsgrad"]
    assert produkt["bindungsgrad_original"] == stichprobe["bindungsgrad_original"]
    assert produkt["klassifizierung"] == stichprobe["klassifizierung"]
    assert produkt["leistungen"][0] == stichprobe["erste_leistung"]
    assert produkt["pdf_seiten"] == stichprobe["pdf_seiten"]


def test_zweiseitiges_produkt_liefert_einen_datensatz(
    produktinfos: tuple, kontext: tuple[pl.DataFrame, pl.DataFrame]
) -> None:
    seiten, _hierarchie = kontext
    pi_seiten = seiten.filter(
        pl.col("produkt").is_not_null() & (pl.col("typ") == "produktinformationen")
    )
    anzahl_je_produkt = pi_seiten.group_by("produkt").agg(pl.len().alias("n"))
    zweiseitige = anzahl_je_produkt.filter(pl.col("n") > 1)
    assert zweiseitige.height == 1
    produkt_code = zweiseitige["produkt"][0]
    treffer = [info for info in produktinfos if info.code == produkt_code]
    assert len(treffer) == 1
    info = treffer[0]
    assert info.zielgruppe
    assert info.ziele


def test_keine_personennamen(
    jahrgang: Jahrgang, kontext: tuple[pl.DataFrame, pl.DataFrame], produkte_json: list[dict]
) -> None:
    seiten, hierarchie = kontext
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        namen = lies_personennamen(dokument, jahrgang, seiten, hierarchie)

    assert len(namen) >= jahrgang.anzahlen.produkte

    nadeln = set()
    for _seite, text in namen:
        nadeln.add(text)
        nadeln.add("".join(text.split()))

    for produkt in produkte_json:
        assert PERSONENFELDER[0] not in produkt
        assert PERSONENFELDER[1] not in produkt
        assert set(produkt) == set(PRODUKT_SCHLUESSEL)

    treffer: list[tuple[str, int]] = []
    for pfad in DATEN_WURZEL.rglob("*"):
        if not pfad.is_file():
            continue
        try:
            inhalt = pfad.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for nadel in nadeln:
            if nadel and nadel in inhalt:
                treffer.append((str(pfad.relative_to(DATEN_WURZEL)), 0))
    assert treffer == []


def test_schreibe_produkte_json_lehnt_extra_schluessel_ab(tmp_path) -> None:
    datensatz = {schluessel: "x" for schluessel in PRODUKT_SCHLUESSEL}
    datensatz["code"] = "999999"
    datensatz["leistungen"] = ["x"]
    datensatz["pdf_seiten"] = [1]
    datensatz["verantwortlich"] = "sollte nie vorkommen"
    with pytest.raises(SchemaFehler, match="999999"):
        schreibe_produkte_json([datensatz], tmp_path / "produkte.json")


def test_schreibe_produkte_json_lehnt_fehlenden_schluessel_ab(tmp_path) -> None:
    datensatz = {schluessel: "x" for schluessel in PRODUKT_SCHLUESSEL}
    datensatz["code"] = "999999"
    datensatz["leistungen"] = ["x"]
    datensatz["pdf_seiten"] = [1]
    del datensatz["gremium"]
    with pytest.raises(SchemaFehler, match="999999"):
        schreibe_produkte_json([datensatz], tmp_path / "produkte.json")


def _erstes_produkt_mit_pi_seiten(
    kontext: tuple[pl.DataFrame, pl.DataFrame],
) -> tuple[str, tuple[int, ...]]:
    seiten, _hierarchie = kontext
    pi_seiten = seiten.filter(
        pl.col("produkt").is_not_null() & (pl.col("typ") == "produktinformationen")
    ).sort(["produkt", "pdf_seite"])
    produkt = sorted(pi_seiten["produkt"].unique().to_list())[0]
    pdf_seiten = tuple(pi_seiten.filter(pl.col("produkt") == produkt)["pdf_seite"].to_list())
    return produkt, pdf_seiten


@dataclasses.dataclass
class _FehlerhaftesDokument:
    """Ersetzt die feinen Zeilen genau einer Seite eines echten PdfDokument (D-07, wie
    test_investitionen.py): `lies_produktinformationen` ruft nur `.zeilen_fein(pdf_seite)`
    auf (duck-typed) — dieser Wrapper delegiert an das echte Dokument, außer für `seite`,
    wo `ersatz` zurückgegeben wird."""

    echt: PdfDokument
    seite: int
    ersatz: tuple[Textzeile, ...]

    def zeilen_fein(self, pdf_seite: int) -> tuple[Textzeile, ...]:
        if pdf_seite == self.seite:
            return self.ersatz
        return self.echt.zeilen_fein(pdf_seite)


def _manipuliere_feldwert(
    jahrgang: Jahrgang,
    dokument: PdfDokument,
    pdf_seiten: tuple[int, ...],
    *,
    feldname: str,
    neuer_wert: str,
) -> _FehlerhaftesDokument:
    """Ersetzt das letzte Wort der Feld-Kopfzeile `feldname` (z. B. "Bindungsgrad") auf
    einer der gegebenen Seiten durch `neuer_wert`; gibt ein Dokument zurück, dessen
    `zeilen_fein` für genau diese Seite die manipulierte Fassung liefert."""
    label = layout_text(jahrgang, "produktinformationen", feldname)
    for pdf_seite in pdf_seiten:
        zeilen = dokument.zeilen_fein(pdf_seite)
        for index, zeile in enumerate(zeilen):
            if zeile.woerter and zeile.woerter[0].fett and zeile.woerter[0].text == label:
                wert_wort = zeile.woerter[-1]
                geaendert = dataclasses.replace(wert_wort, text=neuer_wert)
                neue_zeile = dataclasses.replace(zeile, woerter=(*zeile.woerter[:-1], geaendert))
                ersatz = list(zeilen)
                ersatz[index] = neue_zeile
                return _FehlerhaftesDokument(echt=dokument, seite=pdf_seite, ersatz=tuple(ersatz))
    pytest.fail(f"Feld-Kopfzeile {feldname!r} nicht gefunden")


def test_zerlege_felder_segmentiert_alle_felder_eines_produkts(
    jahrgang: Jahrgang, kontext: tuple[pl.DataFrame, pl.DataFrame]
) -> None:
    _produkt, pdf_seiten = _erstes_produkt_mit_pi_seiten(kontext)
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        seiten_zeilen = tuple((seite, dokument.zeilen_fein(seite)) for seite in pdf_seiten)
        felder = zerlege_felder(seiten_zeilen, jahrgang)

    erwartete_felder = {
        "fachbereich",
        "verantwortlich",
        "sachbearbeiter",
        "gremium",
        "beschreibung",
        "leistungen",
        "auftragsgrundlage",
        "bindungsgrad",
        "klassifizierung",
        "zielgruppe",
        "ziele",
    }
    assert erwartete_felder <= set(felder)
    for feld, eintraege in felder.items():
        assert eintraege, feld


def test_unbekannter_bindungsgrad_bricht_ab(
    jahrgang: Jahrgang, kontext: tuple[pl.DataFrame, pl.DataFrame]
) -> None:
    seiten, hierarchie = kontext
    _produkt, pdf_seiten = _erstes_produkt_mit_pi_seiten(kontext)
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        fehlerhaft = _manipuliere_feldwert(
            jahrgang, dokument, pdf_seiten, feldname="bindungsgrad", neuer_wert="unbekannt"
        )
        with pytest.raises(ProdukteFehler, match="Bindungsgrad unbekannt"):
            lies_produktinformationen(fehlerhaft, jahrgang, seiten, hierarchie)


def test_unbekannte_klassifizierung_bricht_ab(
    jahrgang: Jahrgang, kontext: tuple[pl.DataFrame, pl.DataFrame]
) -> None:
    seiten, hierarchie = kontext
    _produkt, pdf_seiten = _erstes_produkt_mit_pi_seiten(kontext)
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        fehlerhaft = _manipuliere_feldwert(
            jahrgang, dokument, pdf_seiten, feldname="klassifizierung", neuer_wert="unbekannt"
        )
        with pytest.raises(ProdukteFehler, match="Klassifizierung unbekannt"):
            lies_produktinformationen(fehlerhaft, jahrgang, seiten, hierarchie)


# --- Task 1: Grundzahlen (EXTR-07, D-12, D-13) --------------------------------------


def _manipuliere_grundzahlen_wort(
    dokument: PdfDokument, pdf_seite: int, *, such_text: str, **ersatz_felder: object
) -> _FehlerhaftesDokument:
    """Ersetzt das ERSTE Wort mit Text `such_text` auf `pdf_seite` durch dieselben Felder,
    mit `ersatz_felder` überschrieben (wie `_manipuliere_feldwert`, aber textsuchend statt
    feldlabel-suchend — für Grundzahlen-Werte, die kein eigenes Feld-Label tragen)."""
    zeilen = dokument.zeilen_fein(pdf_seite)
    for zeilen_index, zeile in enumerate(zeilen):
        for wort_index, wort in enumerate(zeile.woerter):
            if wort.text == such_text:
                neues_wort = dataclasses.replace(wort, **ersatz_felder)
                neue_woerter = list(zeile.woerter)
                neue_woerter[wort_index] = neues_wort
                neue_zeile = dataclasses.replace(zeile, woerter=tuple(neue_woerter))
                ersatz = list(zeilen)
                ersatz[zeilen_index] = neue_zeile
                return _FehlerhaftesDokument(echt=dokument, seite=pdf_seite, ersatz=tuple(ersatz))
    pytest.fail(f"Wort {such_text!r} nicht gefunden auf S. {pdf_seite}")


def test_stichprobe_grundzahl_steuer(grundzahlen: tuple[Grundzahl, ...]) -> None:
    sollwerte = lade_sollwerte(STANDARD_JAHR)
    stichprobe = sollwerte["stichproben"]["grundzahl_steuer"]
    treffer = [
        g
        for g in grundzahlen
        if g.produkt == stichprobe["produkt"]
        and g.bezeichnung == stichprobe["bezeichnung"]
        and g.jahr == stichprobe["jahr"]
    ]
    assert len(treffer) == 1, treffer
    zeile = treffer[0]
    assert zeile.einheit == stichprobe["einheit"]
    assert zeile.wert == stichprobe["wert"]
    assert zeile.nachkommastellen == 0
    assert zeile.pdf_seite == stichprobe["pdf_seite"]


def test_stichprobe_grundzahl_stichtag(grundzahlen: tuple[Grundzahl, ...]) -> None:
    sollwerte = lade_sollwerte(STANDARD_JAHR)
    stichprobe = sollwerte["stichproben"]["grundzahl_stichtag"]
    eigene_zeilen = [
        g
        for g in grundzahlen
        if g.produkt == stichprobe["produkt"] and g.bezeichnung == stichprobe["bezeichnung"]
    ]
    ziel = next(g for g in eigene_zeilen if g.jahr == stichprobe["jahr"])
    assert ziel.einheit == stichprobe["einheit"]
    assert ziel.wert == stichprobe["wert"]
    assert ziel.hinweis is not None and stichprobe["hinweis_enthaelt"] in ziel.hinweis
    assert ziel.pdf_seite == stichprobe["pdf_seite"]
    for andere in eigene_zeilen:
        if andere.jahr != stichprobe["jahr"]:
            assert andere.hinweis is None or stichprobe["hinweis_enthaelt"] not in andere.hinweis


def test_stichprobe_grundzahl_ueberschreibung(grundzahlen: tuple[Grundzahl, ...]) -> None:
    sollwerte = lade_sollwerte(STANDARD_JAHR)
    stichprobe = sollwerte["stichproben"]["grundzahl_ueberschreibung"]
    zeilen_des_jahres = [
        g
        for g in grundzahlen
        if g.produkt == stichprobe["produkt"] and g.jahr == stichprobe["jahr"]
    ]
    assert zeilen_des_jahres
    for zeile in zeilen_des_jahres:
        assert zeile.hinweis is not None
        assert stichprobe["hinweis_enthaelt"] in zeile.hinweis
        assert stichprobe["hinweis_ohne"] not in zeile.hinweis


def test_stichprobe_grundzahl_gruppe(grundzahlen: tuple[Grundzahl, ...]) -> None:
    sollwerte = lade_sollwerte(STANDARD_JAHR)
    stichprobe = sollwerte["stichproben"]["grundzahl_gruppe"]
    zeilen_der_seite = [
        g
        for g in grundzahlen
        if g.produkt == stichprobe["produkt"] and g.pdf_seite == stichprobe["pdf_seite"]
    ]
    assert zeilen_der_seite
    for zeile in zeilen_der_seite:
        assert zeile.gruppe == stichprobe["gruppe"]
        assert zeile.bezeichnung != stichprobe["gruppe"]


def test_stichprobe_grundzahl_kein_wert(grundzahlen: tuple[Grundzahl, ...]) -> None:
    sollwerte = lade_sollwerte(STANDARD_JAHR)
    stichprobe = sollwerte["stichproben"]["grundzahl_kein_wert"]
    treffer = [
        g
        for g in grundzahlen
        if g.produkt == stichprobe["produkt"] and g.bezeichnung == stichprobe["bezeichnung"]
    ]
    assert [g.jahr for g in treffer] == stichprobe["jahre"]
    assert treffer[0].wert == stichprobe["wert"]


def test_grundzahlen_anzahl_produkte_stimmt_mit_stichprobe(
    grundzahlen: tuple[Grundzahl, ...],
) -> None:
    sollwerte = lade_sollwerte(STANDARD_JAHR)
    erwartet = sollwerte["stichproben"]["anzahlen"]["produkte_mit_grundzahlen"]
    assert len({g.produkt for g in grundzahlen}) == erwartet


def test_grundzahlen_jede_zeile_hat_nichtleere_einheit(
    grundzahlen: tuple[Grundzahl, ...],
) -> None:
    for zeile in grundzahlen:
        assert zeile.einheit, (zeile.produkt, zeile.position)


def test_grundzahlen_eurozeichen_normalisiert(grundzahlen: tuple[Grundzahl, ...]) -> None:
    assert not any(g.einheit == "C" for g in grundzahlen)
    assert not any(g.einheit.startswith("C/") for g in grundzahlen)
    assert any(g.nachkommastellen > 0 and g.einheit.startswith("EUR/") for g in grundzahlen)


def test_grundzahlen_manipuliertes_wort_bricht_mit_seite_ab(
    jahrgang: Jahrgang, kontext: tuple[pl.DataFrame, pl.DataFrame]
) -> None:
    sollwerte = lade_sollwerte(STANDARD_JAHR)
    stichprobe = sollwerte["stichproben"]["grundzahl_steuer"]
    seiten, hierarchie = kontext
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        fehlerhaft = _manipuliere_grundzahlen_wort(
            dokument, stichprobe["pdf_seite"], such_text="4.771.497", text="x,y"
        )
        with pytest.raises(ProdukteFehler, match=f"S. {stichprobe['pdf_seite']}: "):
            lies_grundzahlen(fehlerhaft, jahrgang, seiten, hierarchie)


def test_grundzahlen_wert_ausserhalb_der_spalten_bricht_ab(
    jahrgang: Jahrgang, kontext: tuple[pl.DataFrame, pl.DataFrame]
) -> None:
    sollwerte = lade_sollwerte(STANDARD_JAHR)
    stichprobe = sollwerte["stichproben"]["grundzahl_steuer"]
    seiten, hierarchie = kontext
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        # x0/x1 verschoben in die Lücke zwischen Label- und Einheit-Zone (keine der drei
        # Spalten-Zonen trifft zu, siehe _grundzahlen_zonen).
        fehlerhaft = _manipuliere_grundzahlen_wort(
            dokument, stichprobe["pdf_seite"], such_text="4.771.497", x0=0.0, x1=295.0
        )
        with pytest.raises(ProdukteFehler, match="liegt in keiner Grundzahlen-Spalte"):
            lies_grundzahlen(fehlerhaft, jahrgang, seiten, hierarchie)


def test_grundzahlen_csv_wird_von_extrahiere_produkte_geschrieben(
    produkte_json: list[dict], grundzahlen: tuple[Grundzahl, ...]
) -> None:
    # produkte_json regeneriert auch grundzahlen.csv (extrahiere_produkte, 03-05).
    del produkte_json  # nur für die Fixture-Reihenfolge (Regeneration) benötigt
    df = lies_grundzahlen_csv(DATEN_WURZEL / GRUNDZAHLEN_CSV)
    assert df.height == sum(1 for _ in grundzahlen)
    assert list(df.columns) == [
        "produkt",
        "position",
        "gruppe",
        "bezeichnung",
        "einheit",
        "jahr",
        "wert",
        "nachkommastellen",
        "hinweis",
        "pdf_seite",
    ]


# --- Task 2: Erläuterungsposten (EXTR-08, D-01 bis D-04) ---------------------------


def test_header_normalisierung_zu_nr_muster(jahrgang: Jahrgang) -> None:
    """Zu_nr_muster normalisiert alle gefundenen Header-Varianten auf zweistellige
    Zeilennummern (D-02). Reiner String-Test ohne PDF-Zugriff."""
    zu_nr_muster = re.compile(layout_text(jahrgang, "erlaeuterungen", "zu_nr_muster"))

    faelle = (
        ("zu Nr. 6", ["06"], ""),
        ("Zu Nr. 02", ["02"], ""),
        ("zu Nr. 02 und 13", ["02", "13"], ""),
        ("zu Nr. 13 und Nr. 16 (tlw.)", ["13", "16"], "(tlw.)"),
        ("zu Nr. 16: Anmietung Scheune als Lager", ["16"], "Anmietung Scheune als Lager"),
        ("Nr. 13 und Nr. 16", ["13", "16"], ""),
    )
    for text, erwartete_zeilen, erwarteter_rest in faelle:
        treffer = zu_nr_muster.match(text)
        assert treffer is not None, text
        zeilen = [f"{int(z):02d}" for z in re.findall(r"\d{1,2}", treffer.group("zeilen"))]
        assert zeilen == erwartete_zeilen, text
        rest = treffer.group("rest").strip()
        if rest.startswith(":"):
            rest = rest[1:].strip()
        assert rest == erwarteter_rest, text


def test_stichprobe_erlaeuterung_posten(erlaeuterungen: tuple[Erlaeuterung, ...]) -> None:
    sollwerte = lade_sollwerte(STANDARD_JAHR)
    stichprobe = sollwerte["stichproben"]["erlaeuterung_posten"]
    treffer = next(
        e
        for e in erlaeuterungen
        if e.produkt == stichprobe["produkt"] and e.betrag == stichprobe["betrag"]
    )
    assert list(treffer.zu_zeilen) == stichprobe["zu_zeilen"]
    assert treffer.text == stichprobe["text"]
    assert treffer.pdf_seite == stichprobe["pdf_seite"]


def test_stichprobe_erlaeuterung_ohne_zu_nr(erlaeuterungen: tuple[Erlaeuterung, ...]) -> None:
    sollwerte = lade_sollwerte(STANDARD_JAHR)
    stichprobe = sollwerte["stichproben"]["erlaeuterung_ohne_zu_nr"]
    eintraege = sorted(
        (e for e in erlaeuterungen if e.produkt == stichprobe["produkt"]),
        key=lambda e: (e.block, e.position),
    )
    assert len({e.block for e in eintraege}) == stichprobe["bloecke"]
    bloecke_sortiert = sorted({e.block for e in eintraege})
    erster_block, zweiter_block = bloecke_sortiert[0], bloecke_sortiert[1]
    assert all(not e.zu_zeilen for e in eintraege if e.block == erster_block)
    zweite_block_zeilen = next(e.zu_zeilen for e in eintraege if e.block == zweiter_block)
    assert list(zweite_block_zeilen) == stichprobe["zweiter_block_zu_zeilen"]
    assert all(e.pdf_seite == stichprobe["pdf_seite"] for e in eintraege)


def test_anzahl_produkte_mit_erlaeuterungen_stimmt_mit_stichprobe(
    erlaeuterungen: tuple[Erlaeuterung, ...],
) -> None:
    sollwerte = lade_sollwerte(STANDARD_JAHR)
    erwartet = sollwerte["stichproben"]["anzahlen"]["produkte_mit_erlaeuterungen"]
    assert len({e.produkt for e in erlaeuterungen}) == erwartet


def test_produkte_ohne_erlaeuterung_haben_leere_liste(
    produkte_json: list[dict], erlaeuterungen: tuple[Erlaeuterung, ...]
) -> None:
    produkte_mit = {e.produkt for e in erlaeuterungen}
    for produkt in produkte_json:
        if produkt["code"] in produkte_mit:
            assert produkt["erlaeuterungen"], produkt["code"]
        else:
            assert produkt["erlaeuterungen"] == [], produkt["code"]


def test_embedded_erlaeuterungen_entsprechen_den_eigenen_erlaeuterungen(
    produkte_json: list[dict], erlaeuterungen: tuple[Erlaeuterung, ...]
) -> None:
    for produkt in produkte_json:
        eigene = sorted(
            (e for e in erlaeuterungen if e.produkt == produkt["code"]),
            key=lambda e: (e.block, e.position),
        )
        eingebettet = produkt["erlaeuterungen"]
        assert len(eingebettet) == len(eigene)
        for eintrag, erwartet in zip(eingebettet, eigene, strict=True):
            assert eintrag["block"] == erwartet.block
            assert eintrag["position"] == erwartet.position
            assert eintrag["zu_zeilen"] == list(erwartet.zu_zeilen)
            assert eintrag["betrag"] == erwartet.betrag
            assert eintrag["text"] == erwartet.text
            assert eintrag["pdf_seite"] == erwartet.pdf_seite


def test_erlaeuterung_blocks_und_positionen_sind_1_basiert(
    erlaeuterungen: tuple[Erlaeuterung, ...],
) -> None:
    produkte_mit = {e.produkt for e in erlaeuterungen}
    for produkt in produkte_mit:
        eigene = sorted(
            (e for e in erlaeuterungen if e.produkt == produkt), key=lambda e: e.position
        )
        assert [e.position for e in eigene] == list(range(1, len(eigene) + 1))
        assert min(e.block for e in eigene) == 1


def test_sub_betrag_in_posten_text_bleibt_text(erlaeuterungen: tuple[Erlaeuterung, ...]) -> None:
    # D-01: ein Unterbetrag innerhalb eines Postentextes ("zusätzlich 55.000 C aus
    # Rückstellungen") bleibt Teil des Textes und wird nicht als eigener Posten gezählt.
    sub_betrag_muster = re.compile(r"zusätzlich \d")
    treffer = [
        e for e in erlaeuterungen if e.betrag is not None and sub_betrag_muster.search(e.text)
    ]
    assert treffer
    for eintrag in treffer:
        assert "€" in eintrag.text
        assert "(cid:15)" not in eintrag.text


def test_pruefe_plausibilitaet_erkennt_fehlende_zeile(
    erlaeuterungen: tuple[Erlaeuterung, ...],
) -> None:
    ergebnisplan = lies_plan_csv(DATEN_WURZEL / ERGEBNISPLAN_CSV)
    posten = next(e for e in erlaeuterungen if e.betrag is not None)
    zeile_zu_entfernen = posten.zu_zeilen[0]
    manipuliert = ergebnisplan.filter(
        ~(
            (pl.col("ebene") == "P")
            & (pl.col("code") == posten.produkt)
            & (pl.col("zeile") == zeile_zu_entfernen)
        )
    )
    with pytest.raises(ProdukteFehler, match="nicht gedruckt"):
        pruefe_plausibilitaet(erlaeuterungen, manipuliert, STANDARD_JAHR)


def test_pruefe_plausibilitaet_erkennt_zu_grossen_posten(
    erlaeuterungen: tuple[Erlaeuterung, ...], jahrgang: Jahrgang
) -> None:
    ergebnisplan = lies_plan_csv(DATEN_WURZEL / ERGEBNISPLAN_CSV)
    posten = next(e for e in erlaeuterungen if e.betrag is not None)
    manipuliert = ergebnisplan.with_columns(
        pl.when(
            (pl.col("ebene") == "P")
            & (pl.col("code") == posten.produkt)
            & pl.col("zeile").is_in(list(posten.zu_zeilen))
            & (pl.col("jahr") == jahrgang.haushaltsjahr)
            & (pl.col("wertart") == "ansatz")
        )
        .then(0)
        .otherwise(pl.col("betrag"))
        .alias("betrag")
    )
    with pytest.raises(ProdukteFehler, match="übersteigt"):
        pruefe_plausibilitaet(erlaeuterungen, manipuliert, jahrgang.haushaltsjahr)


def test_pruefe_plausibilitaet_gruen_auf_echten_daten(
    erlaeuterungen: tuple[Erlaeuterung, ...], jahrgang: Jahrgang
) -> None:
    ergebnisplan = lies_plan_csv(DATEN_WURZEL / ERGEBNISPLAN_CSV)
    pruefe_plausibilitaet(erlaeuterungen, ergebnisplan, jahrgang.haushaltsjahr)


def test_erlaeuterungen_csv_zu_zeilen_format(produkte_json: list[dict]) -> None:
    # zu_zeilen ist in der JSON eine Liste, jedes Element zweistellig (D-02).
    for produkt in produkte_json:
        for eintrag in produkt["erlaeuterungen"]:
            for zeile in eintrag["zu_zeilen"]:
                assert re.fullmatch(r"\d{2}", zeile), (produkt["code"], zeile)


# --- Deterministische Regeneration (G2) ---------------------------------------------------


def _kopiere_produkte_input_nach(tmp_path: Path) -> None:
    """Kopiert die Input-CSVs, die extrahiere_produkte benötigt."""
    for quelle in (SEITEN_CSV, HIERARCHIE_CSV, ERGEBNISPLAN_CSV):
        ziel = tmp_path / quelle
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ziel.write_bytes((DATEN_WURZEL / quelle).read_bytes())


def test_produkte_json_erlaeuterungen_csv_grundzahlen_csv_byte_identisch(
    tmp_path: Path, jahrgang: Jahrgang
) -> None:
    """G2: Schritt 03 erzeugt produkte.json, erlaeuterungen.csv und grundzahlen.csv
    deterministisch — byte-identisch zu den eingecheckten Dateien (EXTR-06, EXTR-08).

    Kopiert die Input-Dateien (seiten.csv, hierarchie.csv, ergebnisplan.csv) in ein
    Temp-Verzeichnis, lässt extrahiere_produkte darin neu erzeugen und vergleicht
    byte-für-byte mit daten/aufbereitet/."""
    _kopiere_produkte_input_nach(tmp_path)
    extrahiere_produkte(jahrgang, daten_wurzel=tmp_path)

    # Alle drei Output-Dateien müssen byte-identisch sein
    for pfad in (PRODUKTE_JSON, ERLAEUTERUNGEN_CSV, GRUNDZAHLEN_CSV):
        generiert = tmp_path / pfad
        original = DATEN_WURZEL / pfad
        assert generiert.read_bytes() == original.read_bytes(), (
            f"{pfad} ist nicht byte-identisch: "
            f"temporär {generiert.stat().st_size} Bytes, "
            f"eingecheckt {original.stat().st_size} Bytes"
        )
