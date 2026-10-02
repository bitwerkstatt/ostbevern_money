"""Tests für ostbevern.investitionen: Investitionsmaßnahmen, VE-Fälligkeiten (EXTR-09).

Liest nur das Original-PDF (über die `jahrgang`-Fixture) und eingecheckte, bereits von
früheren Phasen erzeugte CSVs (seiten.csv, finanzplan.csv, hierarchie.csv) als Kontext für
Produktseiten; nie `daten/aufbereitet/investitionen.csv` oder `ve_faelligkeiten.csv` selbst
als Quelle. Keine Jahrgangs-, Seiten- oder Sollwert-Literale — Produkte/Seiten kommen aus
`seiten.csv`, Sollwerte aus `lade_sollwerte(STANDARD_JAHR)`.
"""

from __future__ import annotations

import dataclasses
from pathlib import Path

import polars as pl
import pytest

from ostbevern.freitext import ersetze_eurozeichen, verbinde_zeilen
from ostbevern.investitionen import (
    InvestitionenFehler,
    Kontengruppe,
    extrahiere_investitionen,
    klassifiziere_konto,
    lies_massnahmen,
)
from ostbevern.konfiguration import STANDARD_JAHR, Jahrgang, lade_sollwerte, layout_text
from ostbevern.pdf import PdfDokument, Textzeile
from ostbevern.schema import (
    DATEN_WURZEL,
    FINANZPLAN_CSV,
    HIERARCHIE_CSV,
    INVESTITIONEN_CSV,
    INVESTITIONEN_PB_CSV,
    SEITEN_CSV,
    VE_FAELLIGKEITEN_CSV,
    lies_hierarchie_csv,
    lies_investitionen_csv,
    lies_investitionen_pb_csv,
    lies_seiten_csv,
    lies_ve_faelligkeiten_csv,
    zerlege_spaltenkopf,
)
from ostbevern.zahlen import ist_betrag

_PRODUKTSEITEN_TYPEN = ("teilergebnisplan", "teilfinanzplan", "investitionen_produkt")
_PBSEITEN_TYPEN = ("investitionen_pb", "teilergebnisplan", "teilfinanzplan")


def _seiten_fuer_pb(pb: str) -> tuple[int, ...]:
    seiten = lies_seiten_csv(DATEN_WURZEL / SEITEN_CSV)
    treffer = seiten.filter(
        (pl.col("pb") == pb)
        & pl.col("pg").is_null()
        & pl.col("produkt").is_null()
        & pl.col("typ").is_in(_PBSEITEN_TYPEN)
    ).sort("pdf_seite")
    return tuple(treffer["pdf_seite"].to_list())


def _seiten_fuer_produkt(produkt: str) -> tuple[int, ...]:
    seiten = lies_seiten_csv(DATEN_WURZEL / SEITEN_CSV)
    treffer = seiten.filter(
        (pl.col("produkt") == produkt) & pl.col("typ").is_in(_PRODUKTSEITEN_TYPEN)
    ).sort("pdf_seite")
    return tuple(treffer["pdf_seite"].to_list())


@dataclasses.dataclass
class _FehlerhaftesDokument:
    """Ersetzt die feinen Zeilen genau einer Seite eines echten PdfDokument (D-07).

    `lies_massnahmen` ruft nur `.zeilen_fein(pdf_seite)` auf (duck-typed) — dieser Wrapper
    delegiert an das echte Dokument, außer für `seite`, wo `ersatz` zurückgegeben wird.
    """

    echt: PdfDokument
    seite: int
    ersatz: tuple[Textzeile, ...]

    def zeilen_fein(self, pdf_seite: int) -> tuple[Textzeile, ...]:
        if pdf_seite == self.seite:
            return self.ersatz
        return self.echt.zeilen_fein(pdf_seite)


def _finde_zeile(zeilen, praedikat):  # noqa: ANN001, ANN202
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


@pytest.fixture(scope="module")
def produkt_mit_praefixkollision() -> tuple[str, tuple[int, ...]]:
    """Ein Produkt, dessen investitionen.csv zwei Maßnahmen-IDs enthält, von denen eine
    ein echtes Präfix der anderen ist (Research Pitfall 2/Pattern 4)."""
    investitionen = lies_investitionen_csv(DATEN_WURZEL / INVESTITIONEN_CSV)
    ids_je_produkt = investitionen.group_by("produkt").agg(pl.col("massnahme_id").unique())
    for zeile in ids_je_produkt.iter_rows(named=True):
        ids = sorted(zeile["massnahme_id"])
        for i, kurze_id in enumerate(ids):
            for laengere_id in ids[i + 1 :]:
                if laengere_id.startswith(kurze_id) and laengere_id != kurze_id:
                    return zeile["produkt"], _seiten_fuer_produkt(zeile["produkt"])
    pytest.fail("Kein Produkt mit ID-Präfixkollision in investitionen.csv gefunden")


def test_massnahme_id_entspricht_saldo_zeile_mit_praefixkollision(
    jahrgang: Jahrgang, produkt_mit_praefixkollision: tuple[str, tuple[int, ...]]
) -> None:
    produkt, seiten_nummern = produkt_mit_praefixkollision
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        massnahmen, _saldo = lies_massnahmen(
            dokument, jahrgang, seiten_nummern, ebene="P", code=produkt
        )
    ids = sorted({m.massnahme_id for m in massnahmen})
    kollision = next(
        (
            (kurz, lang)
            for i, kurz in enumerate(ids)
            for lang in ids[i + 1 :]
            if lang.startswith(kurz) and lang != kurz
        ),
        None,
    )
    assert kollision is not None, ids
    kurz, lang = kollision
    massnahme_kurz = next(m for m in massnahmen if m.massnahme_id == kurz)
    massnahme_lang = next(m for m in massnahmen if m.massnahme_id == lang)
    assert massnahme_kurz.massnahme_name
    assert massnahme_lang.massnahme_name
    assert massnahme_kurz.massnahme_name != massnahme_lang.massnahme_name
    for massnahme in massnahmen:
        assert massnahme.massnahme_id


def test_csv_hat_keine_konten_der_gruppe_692_792(tmp_path: Path, jahrgang: Jahrgang) -> None:
    _kopiere_kontext_nach(tmp_path)
    extrahiere_investitionen(jahrgang, daten_wurzel=tmp_path)
    investitionen = lies_investitionen_csv(tmp_path / INVESTITIONEN_CSV)
    assert not investitionen["konto"].str.slice(0, 3).is_in(["692", "792"]).any()


def test_unbekannte_kontengruppe_bricht_ab(jahrgang: Jahrgang) -> None:
    with pytest.raises(InvestitionenFehler, match=r"S\. \d+.*999999"):
        klassifiziere_konto("999999", 42)


def test_klassifiziere_konto_laengstes_praefix_gewinnt() -> None:
    gruppe = klassifiziere_konto("782111", 1)
    assert gruppe == Kontengruppe("auszahlung", "investition", "immaterielles")
    andere_gruppe = klassifiziere_konto("782113", 1)
    assert andere_gruppe == Kontengruppe("auszahlung", "investition", "grundstuecke")


def _erstes_produkt_mit_tabelle(jahrgang: Jahrgang) -> tuple[str, tuple[int, ...]]:
    investitionen = lies_investitionen_csv(DATEN_WURZEL / INVESTITIONEN_CSV)
    produkt = sorted(investitionen["produkt"].unique().to_list())[0]
    seiten_nummern = _seiten_fuer_produkt(produkt)
    return produkt, seiten_nummern


def _konto_zeilen_index(
    jahrgang: Jahrgang, dokument: PdfDokument, seiten_nummern: tuple[int, ...]
) -> tuple[int, int, Textzeile]:
    """Findet (pdf_seite, index, zeile) einer echten Kontozeile einer Investitionsmaßnahmen-
    Tabelle: 6-stelliges Konto am Zeilenanfang, gefolgt von genau len(spalten) Beträgen
    (unterscheidet sie von regulären Teilplan-Zeilen mit zufällig 6-stelligem erstem Wort)."""
    anzahl_spalten = len(jahrgang.spalten["investitionen"])
    for pdf_seite in seiten_nummern:
        zeilen = dokument.zeilen_fein(pdf_seite)
        for index, zeile in enumerate(zeilen):
            if not (
                zeile.woerter
                and zeile.woerter[0].text[:6].isdigit()
                and len(zeile.woerter[0].text) == 6
            ):
                continue
            betraege = [w for w in zeile.woerter[1:] if ist_betrag(w.text)]
            if len(betraege) == anzahl_spalten:
                return pdf_seite, index, zeile
    pytest.fail("Keine Kontozeile gefunden")


def test_unbekanntes_konto_in_tabelle_bricht_ab(jahrgang: Jahrgang) -> None:
    produkt, seiten_nummern = _erstes_produkt_mit_tabelle(jahrgang)
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        pdf_seite, index, zeile = _konto_zeilen_index(jahrgang, dokument, seiten_nummern)
        erstes_wort = zeile.woerter[0]
        unbekannt = dataclasses.replace(erstes_wort, text="999999")
        manipuliert = dataclasses.replace(zeile, woerter=(unbekannt, *zeile.woerter[1:]))
        zeilen = dokument.zeilen_fein(pdf_seite)
        ersatz = _ersetze_zeile(zeilen, index, manipuliert)
        fehlerhaft = _FehlerhaftesDokument(echt=dokument, seite=pdf_seite, ersatz=ersatz)
        with pytest.raises(InvestitionenFehler, match=rf"S\. {pdf_seite}.*999999"):
            lies_massnahmen(fehlerhaft, jahrgang, seiten_nummern, ebene="P", code=produkt)


def test_manipulierter_betrag_bricht_saldo_check(jahrgang: Jahrgang) -> None:
    produkt, seiten_nummern = _erstes_produkt_mit_tabelle(jahrgang)
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        pdf_seite, index, zeile = _konto_zeilen_index(jahrgang, dokument, seiten_nummern)
        letztes_wort = zeile.woerter[-1]
        geaendert = dataclasses.replace(
            letztes_wort, text=str(int(letztes_wort.text.replace(".", "") or "0") + 1_000_000)
        )
        manipuliert = dataclasses.replace(zeile, woerter=(*zeile.woerter[:-1], geaendert))
        zeilen = dokument.zeilen_fein(pdf_seite)
        ersatz = _ersetze_zeile(zeilen, index, manipuliert)
        fehlerhaft = _FehlerhaftesDokument(echt=dokument, seite=pdf_seite, ersatz=ersatz)
        with pytest.raises(InvestitionenFehler, match=rf"S\. {pdf_seite}"):
            lies_massnahmen(fehlerhaft, jahrgang, seiten_nummern, ebene="P", code=produkt)


def _kopiere_kontext_nach(tmp_path: Path) -> None:
    for quelle in (SEITEN_CSV, FINANZPLAN_CSV, HIERARCHIE_CSV):
        ziel = tmp_path / quelle
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ziel.write_bytes((DATEN_WURZEL / quelle).read_bytes())


def test_summe_trifft_sollwerte_gesamtfinanzplan(tmp_path: Path, jahrgang: Jahrgang) -> None:
    _kopiere_kontext_nach(tmp_path)
    extrahiere_investitionen(jahrgang, daten_wurzel=tmp_path)
    investitionen = lies_investitionen_csv(tmp_path / INVESTITIONEN_CSV)
    sollwerte = lade_sollwerte(STANDARD_JAHR)
    gesamtfinanzplan_ansatz = sollwerte["gesamtfinanzplan"]["ansatz"]

    ansatz = investitionen.filter(
        (pl.col("jahr") == jahrgang.haushaltsjahr) & (pl.col("wertart") == "ansatz")
    )
    einzahlung_summe = ansatz.filter(pl.col("richtung") == "einzahlung")["betrag"].sum()
    auszahlung_summe = ansatz.filter(pl.col("richtung") == "auszahlung")["betrag"].sum()
    assert einzahlung_summe == gesamtfinanzplan_ansatz["23"]
    assert auszahlung_summe == gesamtfinanzplan_ansatz["30"]
    assert set(investitionen["art"].unique().to_list()) <= {
        "bau",
        "grundstuecke",
        "ausstattung",
        "immaterielles",
        "finanzanlagen",
        "investitionszuschuesse",
        "zuwendungen",
        "beitraege",
    }


def test_zeilen_fein_trennt_id_vom_namen_und_setzt_fett(jahrgang: Jahrgang) -> None:
    _produkt, seiten_nummern = _erstes_produkt_mit_tabelle(jahrgang)
    tabellenkopf = layout_text(jahrgang, "investitionen", "tabellenkopf")
    saldo_praefix = layout_text(jahrgang, "investitionen", "saldo_praefix")
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        for pdf_seite in seiten_nummern:
            zeilen = dokument.zeilen_fein(pdf_seite)
            if not any(z.text_ohne_leerzeichen.startswith(tabellenkopf) for z in zeilen):
                continue
            assert any(w.fett for z in zeilen for w in z.woerter)
            saldo_zeilen = [
                z
                for z in zeilen
                if z.woerter and "".join(w.text for w in z.woerter).startswith(saldo_praefix)
            ]
            assert saldo_zeilen
            return
    pytest.fail("Keine Seite mit Investitionsmaßnahmen-Tabelle gefunden")


# --- Task 2: ve_faelligkeiten.csv ------------------------------------------------------


def test_ve_faelligkeiten_nur_planung_jahr_und_summe_stimmt_mit_investitionen(
    tmp_path: Path, jahrgang: Jahrgang
) -> None:
    _kopiere_kontext_nach(tmp_path)
    extrahiere_investitionen(jahrgang, daten_wurzel=tmp_path)
    investitionen = lies_investitionen_csv(tmp_path / INVESTITIONEN_CSV)
    faelligkeiten = lies_ve_faelligkeiten_csv(tmp_path / VE_FAELLIGKEITEN_CSV)

    planung_jahre = {
        jahr
        for spalte in jahrgang.spalten["investitionen"]
        for wertart, jahr in [zerlege_spaltenkopf(spalte)]
        if wertart == "planung"
    }
    assert set(faelligkeiten["jahr"].unique().to_list()) <= planung_jahre

    gruppiert = faelligkeiten.group_by(["produkt", "massnahme_id", "konto"]).agg(
        pl.col("betrag").sum().alias("fael_summe")
    )
    ve_zeilen = investitionen.filter(pl.col("wertart") == "ve")
    for zeile in gruppiert.iter_rows(named=True):
        ve_treffer = ve_zeilen.filter(
            (pl.col("produkt") == zeile["produkt"])
            & (pl.col("massnahme_id") == zeile["massnahme_id"])
            & (pl.col("konto") == zeile["konto"])
        )
        assert ve_treffer.height == 1
        assert ve_treffer["betrag"][0] == zeile["fael_summe"]
        # Jede Fälligkeit gehört zu einer Kontozeile, die tatsächlich in investitionen.csv
        # steht (mindestens eine Zeile mit demselben Schlüssel existiert).
        assert (
            investitionen.filter(
                (pl.col("produkt") == zeile["produkt"])
                & (pl.col("massnahme_id") == zeile["massnahme_id"])
                & (pl.col("konto") == zeile["konto"])
            ).height
            > 0
        )


def test_kein_ve_wert_ohne_faelligkeiten(tmp_path: Path, jahrgang: Jahrgang) -> None:
    _kopiere_kontext_nach(tmp_path)
    extrahiere_investitionen(jahrgang, daten_wurzel=tmp_path)
    investitionen = lies_investitionen_csv(tmp_path / INVESTITIONEN_CSV)
    faelligkeiten = lies_ve_faelligkeiten_csv(tmp_path / VE_FAELLIGKEITEN_CSV)

    ve_mit_wert = investitionen.filter((pl.col("wertart") == "ve") & (pl.col("betrag") != 0))
    faelligkeit_schluessel = faelligkeiten.select(["produkt", "massnahme_id", "konto"]).unique()
    schluessel_mit_faelligkeit = {
        (z["produkt"], z["massnahme_id"], z["konto"])
        for z in faelligkeit_schluessel.iter_rows(named=True)
    }
    for zeile in ve_mit_wert.iter_rows(named=True):
        schluessel = (zeile["produkt"], zeile["massnahme_id"], zeile["konto"])
        assert schluessel in schluessel_mit_faelligkeit


def _kassenwirksamkeit_zeilen_index(
    jahrgang: Jahrgang, dokument: PdfDokument
) -> tuple[str, int, int, Textzeile]:
    kassenwirksamkeit = layout_text(jahrgang, "investitionen", "kassenwirksamkeit")
    faelligkeiten = lies_ve_faelligkeiten_csv(DATEN_WURZEL / VE_FAELLIGKEITEN_CSV)
    produkte_mit_faelligkeiten = sorted(faelligkeiten["produkt"].unique().to_list())
    for produkt in produkte_mit_faelligkeiten:
        seiten_nummern = _seiten_fuer_produkt(produkt)
        for pdf_seite in seiten_nummern:
            zeilen = dokument.zeilen_fein(pdf_seite)
            for index, zeile in enumerate(zeilen):
                if zeile.woerter and zeile.woerter[0].text == kassenwirksamkeit:
                    return produkt, pdf_seite, index, zeile
    pytest.fail("Keine Kassenwirksamkeit-Zeile gefunden")
    raise AssertionError  # unreachable, für mypy/Typchecker


def test_kassenwirksamkeit_unter_falscher_spalte_bricht_ab(jahrgang: Jahrgang) -> None:
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        produkt, pdf_seite, index, zeile = _kassenwirksamkeit_zeilen_index(jahrgang, dokument)
        seiten_nummern = _seiten_fuer_produkt(produkt)
        # Verschiebt das erste Klammer-Wort auf die x1-Position der Ansatz-2026-Spalte
        # (keine Planung-Spalte) — muss abbrechen (D-08, EXTR-09).
        wert_wort = next(w for w in zeile.woerter[1:] if w.text.startswith("("))
        spalten = jahrgang.spalten["investitionen"]
        ansatz_index = next(
            i for i, spalte in enumerate(spalten) if zerlege_spaltenkopf(spalte)[0] == "ansatz"
        )
        kopfzeile_index = next(
            i
            for i, z in enumerate(dokument.zeilen_fein(pdf_seite))
            if z.text_ohne_leerzeichen.startswith(
                layout_text(jahrgang, "investitionen", "tabellenkopf")
            )
        )
        jahreszeile = dokument.zeilen_fein(pdf_seite)[kopfzeile_index + 1]
        ziel_x1 = jahreszeile.woerter[ansatz_index].x1 + 13.8  # Versatz wie reale Beträge
        verschoben = dataclasses.replace(wert_wort, x0=ziel_x1 - 5, x1=ziel_x1)
        andere = [w for w in zeile.woerter[1:] if w is not wert_wort]
        manipuliert = dataclasses.replace(zeile, woerter=(zeile.woerter[0], verschoben, *andere))
        zeilen = dokument.zeilen_fein(pdf_seite)
        ersatz = _ersetze_zeile(zeilen, index, manipuliert)
        fehlerhaft = _FehlerhaftesDokument(echt=dokument, seite=pdf_seite, ersatz=ersatz)
        with pytest.raises(InvestitionenFehler, match=rf"S\. {pdf_seite}"):
            lies_massnahmen(fehlerhaft, jahrgang, seiten_nummern, ebene="P", code=produkt)


def test_kassenwirksamkeit_ohne_vorherige_kontozeile_bricht_ab(jahrgang: Jahrgang) -> None:
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        produkt, pdf_seite, _index, zeile = _kassenwirksamkeit_zeilen_index(jahrgang, dokument)
        seiten_nummern = _seiten_fuer_produkt(produkt)
        zeilen = dokument.zeilen_fein(pdf_seite)
        tabellenkopf = layout_text(jahrgang, "investitionen", "tabellenkopf")
        kopf_index = next(
            i for i, z in enumerate(zeilen) if z.text_ohne_leerzeichen.startswith(tabellenkopf)
        )
        # Fügt die Kassenwirksamkeit-Zeile unmittelbar NACH dem Tabellenkopf ein (vor
        # jeder Kontozeile) -> keine vorherige Kontozeile im aktuellen Block.
        ersatz = (*zeilen[: kopf_index + 2], zeile, *zeilen[kopf_index + 2 :])
        fehlerhaft = _FehlerhaftesDokument(echt=dokument, seite=pdf_seite, ersatz=ersatz)
        with pytest.raises(InvestitionenFehler, match=rf"S\. {pdf_seite}"):
            lies_massnahmen(fehlerhaft, jahrgang, seiten_nummern, ebene="P", code=produkt)


# --- Task 1 (03-03): investitionen_pb.csv (D-06) -------------------------------------


def test_jede_pb_mit_investitionskonten_hat_pb_liste_und_umgekehrt() -> None:
    """D-06: jede PB, die auf ihren Produktseiten Investitions-Konten hat, hat auch eine
    PB-Investitionsliste, und umgekehrt (Flagged assumption EXTR-09/PRUEF-06)."""
    investitionen = lies_investitionen_csv(DATEN_WURZEL / INVESTITIONEN_CSV)
    investitionen_pb = lies_investitionen_pb_csv(DATEN_WURZEL / INVESTITIONEN_PB_CSV)
    hierarchie = lies_hierarchie_csv(DATEN_WURZEL / HIERARCHIE_CSV)

    pg_zu_pb = {
        zeile["code"]: zeile["eltern_code"]
        for zeile in hierarchie.filter(pl.col("ebene") == "PG").iter_rows(named=True)
    }
    produkt_zu_pb = {
        zeile["code"]: pg_zu_pb[zeile["eltern_code"]]
        for zeile in hierarchie.filter(pl.col("ebene") == "P").iter_rows(named=True)
    }
    pb_mit_produktkonten = {
        produkt_zu_pb[produkt] for produkt in investitionen["produkt"].unique().to_list()
    }
    pb_mit_liste = set(investitionen_pb["pb"].unique().to_list())
    assert pb_mit_produktkonten == pb_mit_liste


def test_pb_liste_behaelt_mehrere_bloecke_derselben_massnahme_id(
    tmp_path: Path, jahrgang: Jahrgang
) -> None:
    """D-06, Research Pitfall 8: eine Maßnahmen-ID kann auf einer PB-Liste mehrfach als
    eigener Block erscheinen (S. 146, PB 03: AIB00001 einmal mit Konto 785111, einmal mit
    681011) — beide Kontozeilen bleiben erhalten, keine Zusammenführung nach ID."""
    _kopiere_kontext_nach(tmp_path)
    extrahiere_investitionen(jahrgang, daten_wurzel=tmp_path)
    investitionen_pb = lies_investitionen_pb_csv(tmp_path / INVESTITIONEN_PB_CSV)

    mehrfach_blocke = (
        investitionen_pb.group_by(["pb", "massnahme_id"])
        .agg(pl.col("konto").n_unique().alias("anzahl_konten"))
        .filter(pl.col("anzahl_konten") > 1)
    )
    assert mehrfach_blocke.height > 0, "Keine Maßnahme mit mehreren Konten in PB-Liste gefunden"
    aib_zeilen = investitionen_pb.filter(pl.col("massnahme_id") == "AIB00001")
    assert {"681011", "785111"} <= set(aib_zeilen["konto"].unique().to_list())


def test_pb_liste_summe_trifft_sollwerte_und_keine_finanzierungskonten(
    tmp_path: Path, jahrgang: Jahrgang
) -> None:
    """D-06: Summiert über alle PB-Listen trifft Ansatz-Haushaltsjahr exakt die
    Gesamtfinanzplan-Sollwerte (wie auf den Produktseiten), und kein Finanzierungs-Konto
    (692/792) wird in investitionen_pb.csv geschrieben."""
    _kopiere_kontext_nach(tmp_path)
    extrahiere_investitionen(jahrgang, daten_wurzel=tmp_path)
    investitionen_pb = lies_investitionen_pb_csv(tmp_path / INVESTITIONEN_PB_CSV)
    sollwerte = lade_sollwerte(STANDARD_JAHR)
    gesamtfinanzplan_ansatz = sollwerte["gesamtfinanzplan"]["ansatz"]

    ansatz = investitionen_pb.filter(
        (pl.col("jahr") == jahrgang.haushaltsjahr) & (pl.col("wertart") == "ansatz")
    )
    assert (
        ansatz.filter(pl.col("richtung") == "einzahlung")["betrag"].sum()
        == gesamtfinanzplan_ansatz["23"]
    )
    assert (
        ansatz.filter(pl.col("richtung") == "auszahlung")["betrag"].sum()
        == gesamtfinanzplan_ansatz["30"]
    )
    assert not investitionen_pb["konto"].str.slice(0, 3).is_in(["692", "792"]).any()


def test_pb_liste_laesst_investitionen_csv_byte_identisch(
    tmp_path: Path, jahrgang: Jahrgang
) -> None:
    """D-06: das Lesen der PB-Listen ändert investitionen.csv und ve_faelligkeiten.csv
    nicht — Quelle bleiben ausschließlich die Produktseiten (Spez. 3.8)."""
    _kopiere_kontext_nach(tmp_path)
    extrahiere_investitionen(jahrgang, daten_wurzel=tmp_path)
    for pfad in (INVESTITIONEN_CSV, VE_FAELLIGKEITEN_CSV):
        assert (tmp_path / pfad).read_bytes() == (DATEN_WURZEL / pfad).read_bytes()


def _finanzierungs_konto_zeilen_index(
    jahrgang: Jahrgang, dokument: PdfDokument, seiten_nummern: tuple[int, ...]
) -> tuple[int, int, Textzeile]:
    """Findet eine echte Finanzierungs-Kontozeile (692/792) einer PB-Liste — verifiziert
    gegen S. 279 (PB 16), der einzigen PB-Liste mit einer zweiten, eigenständigen
    Finanzierungs-Tabelle im 2026er Jahrgang (CONTEXT.md Planning-time facts)."""
    anzahl_spalten = len(jahrgang.spalten["investitionen"])
    for pdf_seite in seiten_nummern:
        zeilen = dokument.zeilen_fein(pdf_seite)
        for index, zeile in enumerate(zeilen):
            if not (
                zeile.woerter
                and zeile.woerter[0].text[:6].isdigit()
                and len(zeile.woerter[0].text) == 6
                and zeile.woerter[0].text[:3] in ("692", "792")
            ):
                continue
            betraege = [w for w in zeile.woerter[1:] if ist_betrag(w.text)]
            if len(betraege) == anzahl_spalten:
                return pdf_seite, index, zeile
    pytest.fail("Keine Finanzierungs-Kontozeile gefunden")
    raise AssertionError  # unreachable, für mypy/Typchecker


def test_pb16_finanzierungskonto_manipuliert_bricht_ab(jahrgang: Jahrgang) -> None:
    """D-06: PB 16 (S. 279) hat eine zweite, eigenständige Investitionsmaßnahmen-Tabelle
    mit den Finanzierungs-Konten 692/792; ein manipulierter Betrag dort bricht den
    Saldo-Check in lies_massnahmen mit der PDF-Seite ab (D-08)."""
    seiten_nummern = _seiten_fuer_pb("16")
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        pdf_seite, index, zeile = _finanzierungs_konto_zeilen_index(
            jahrgang, dokument, seiten_nummern
        )
        letztes_wort = zeile.woerter[-1]
        geaendert = dataclasses.replace(
            letztes_wort, text=str(int(letztes_wort.text.replace(".", "") or "0") + 1_000_000)
        )
        manipuliert = dataclasses.replace(zeile, woerter=(*zeile.woerter[:-1], geaendert))
        zeilen = dokument.zeilen_fein(pdf_seite)
        ersatz = _ersetze_zeile(zeilen, index, manipuliert)
        fehlerhaft = _FehlerhaftesDokument(echt=dokument, seite=pdf_seite, ersatz=ersatz)
        with pytest.raises(InvestitionenFehler, match=rf"S\. {pdf_seite}"):
            lies_massnahmen(fehlerhaft, jahrgang, seiten_nummern, ebene="PB", code="16")


def test_finanzierungskonten_weichen_vom_teilfinanzplan_ab_bricht_ab(
    tmp_path: Path, jahrgang: Jahrgang
) -> None:
    """G1: Finanzierungs-Konten (692/792) werden gegen Teilfinanzplan Z. 33/35 geprüft.
    Ein Betrag, der um mehr als 1€ abweicht, löst InvestitionenFehler aus (EXTR-09, D-06).

    Test mit realen Produktseiten: Produkt 160101 hat Finanzierungs-Konten; die Gegenprobe
    in _pruefe_finanzierungskonten wird aufgerufen (hat_finanzierung==True) und muss bei
    manipuliertem finanzplan.csv abbrechen."""
    from ostbevern.schema import PLAN_SPALTEN

    _kopiere_kontext_nach(tmp_path)

    # Finanzplan lesen mit fester Typung und manipulieren
    finanzplan_pfad = tmp_path / FINANZPLAN_CSV
    finanzplan = pl.read_csv(finanzplan_pfad).cast(PLAN_SPALTEN)

    # Zeile 33 (Einzahlung/Kreditaufnahme) für Produkt 160101, Ansatz 2026
    manipuliert = finanzplan.with_columns(
        pl.when(
            (pl.col("ebene") == "P")
            & (pl.col("code") == "160101")
            & (pl.col("zeile") == "33")
            & (pl.col("jahr") == 2026)
            & (pl.col("wertart") == "ansatz")
        )
        .then(pl.col("betrag") + 1_000_000)
        .otherwise(pl.col("betrag"))
        .alias("betrag")
    )
    manipuliert.write_csv(finanzplan_pfad)

    # Die Gegenprobe sollte beim Erzeugen der CSV fehlschlagen
    with pytest.raises(InvestitionenFehler, match=r"Teilfinanzplan Zeile 33"):
        extrahiere_investitionen(jahrgang, daten_wurzel=tmp_path)


def test_finanzierungskonten_pb_weichen_vom_teilfinanzplan_ab_bricht_ab(
    tmp_path: Path, jahrgang: Jahrgang
) -> None:
    """G1: Wie finanzierungskonten_weichen_vom_teilfinanzplan_ab_bricht_ab, aber für
    die PB-Verarbeitung (ebene="PB"). PB 16 hat Finanzierungs-Konten."""
    from ostbevern.schema import PLAN_SPALTEN

    _kopiere_kontext_nach(tmp_path)

    finanzplan_pfad = tmp_path / FINANZPLAN_CSV
    finanzplan = pl.read_csv(finanzplan_pfad).cast(PLAN_SPALTEN)

    # Zeile 35 (Auszahlung/Tilgung) für PB 16, Ansatz 2026
    manipuliert = finanzplan.with_columns(
        pl.when(
            (pl.col("ebene") == "PB")
            & (pl.col("code") == "16")
            & (pl.col("zeile") == "35")
            & (pl.col("jahr") == 2026)
            & (pl.col("wertart") == "ansatz")
        )
        .then(pl.col("betrag") + 1_000_000)
        .otherwise(pl.col("betrag"))
        .alias("betrag")
    )
    manipuliert.write_csv(finanzplan_pfad)

    # Die Gegenprobe sollte beim Erzeugen der CSV fehlschlagen
    with pytest.raises(InvestitionenFehler, match=r"Teilfinanzplan Zeile 35"):
        extrahiere_investitionen(jahrgang, daten_wurzel=tmp_path)


def test_verbinde_zeilen_und_ersetze_eurozeichen_wiederverwendet() -> None:
    """freitext.py wird von investitionen.py importiert und genutzt (D-10)."""
    import ostbevern.investitionen as modul

    quelltext = Path(modul.__file__).read_text(encoding="utf-8")
    assert "verbinde_zeilen" in quelltext
    assert "ersetze_eurozeichen" in quelltext
    # Sanity: die importierten Funktionen funktionieren wie erwartet.
    assert verbinde_zeilen(["a-", "bc"]) == "abc"
    assert ersetze_eurozeichen("1 C") == "1 €"
