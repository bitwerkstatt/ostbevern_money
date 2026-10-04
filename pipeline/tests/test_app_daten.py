"""Tests für ostbevern.app_daten: Schritt 07, App-JSON-Erzeugung (D-21, D-24).

Erzeugt `haushalt.json` ausschließlich in tmp-Verzeichnisse (nie in das eingecheckte
`app/src/data/`, D-06-Stil); eine Ausnahme ist `test_haushalt_json_eingecheckt_aktuell`,
die das neu erzeugte tmp-Ergebnis gegen die eingecheckte Datei vergleicht, ohne sie zu
überschreiben.

PRIVACY (D-09): Dieses Modul liest nie einen Personennamen in eine Variable, die auf dem
Bildschirm/in Testausgaben erscheinen könnte, außer über `lies_personennamen` selbst,
deren Ergebnis ausschließlich in Mengenvergleiche einfließt (wie test_produkte.py).
"""

from __future__ import annotations

import ast
import json
import shutil
from pathlib import Path

import polars as pl
import pytest

from ostbevern import app_daten
from ostbevern.app_daten import (
    APP_DATEN_WURZEL,
    HAUSHALT_JSON,
    STELLENPLAN_JSON,
    erzeuge_app_daten,
)
from ostbevern.konfiguration import STANDARD_JAHR, Jahrgang, lade_jahrgang, layout_text
from ostbevern.pdf import PdfDokument
from ostbevern.produkte import lies_personennamen
from ostbevern.pruefung import REGEL5_TOLERANZ_GEP_EURO, WEITERGABE_POSTEN, Planwerte
from ostbevern.schema import (
    DATEN_WURZEL,
    ERGEBNISPLAN_CSV,
    ERKLAERUNGEN_MD,
    FINANZPLAN_CSV,
    HIERARCHIE_CSV,
    SEITEN_CSV,
    STELLENPLAN_CSV,
    STEUERARTEN_CSV,
    TRANSFERAUFWENDUNGEN_CSV,
    lies_hierarchie_csv,
    lies_plan_csv,
    lies_seiten_csv,
    lies_stellenplan_csv,
    lies_vorbericht_csv,
)
from ostbevern.texte import PLATZHALTER_MUSTER, TexteFehler
from ostbevern.zeilen import ZEILEN


@pytest.fixture(scope="module")
def kontext() -> tuple[pl.DataFrame, pl.DataFrame]:
    seiten = lies_seiten_csv(DATEN_WURZEL / SEITEN_CSV)
    hierarchie = lies_hierarchie_csv(DATEN_WURZEL / HIERARCHIE_CSV)
    return seiten, hierarchie


def test_haushalt_json_steuerarten_aus_manueller_tabelle(tmp_path: Path) -> None:
    app_daten_wurzel = tmp_path / "app"
    pfade = erzeuge_app_daten(STANDARD_JAHR, app_daten_wurzel=app_daten_wurzel)
    assert pfade == [
        app_daten_wurzel / HAUSHALT_JSON,
        app_daten_wurzel / STELLENPLAN_JSON,
        app_daten_wurzel / app_daten.PRODUKTE_APP_JSON,
        app_daten_wurzel / app_daten.INVESTITIONEN_JSON,
        app_daten_wurzel / app_daten.TEXTE_JSON,
    ]

    daten = json.loads((app_daten_wurzel / HAUSHALT_JSON).read_text(encoding="utf-8"))
    steuerarten = daten["vorbericht"]["steuerarten"]
    jahre = daten["jahre"]
    wertarten = daten["wertarten"]

    df = lies_vorbericht_csv(DATEN_WURZEL / STEUERARTEN_CSV)
    for posten_eintrag in steuerarten["posten"]:
        zeilen = df.filter(pl.col("posten") == posten_eintrag["posten"])
        assert posten_eintrag["gerundet"] is True
        assert posten_eintrag["berechnet"] is False
        for index, jahr in enumerate(jahre):
            zeile = zeilen.filter(pl.col("jahr") == jahr)
            assert zeile.height == 1
            assert posten_eintrag["werte"][index] == zeile["betrag_teur"][0] * 1000

    ergebnisplan = lies_plan_csv(DATEN_WURZEL / ERGEBNISPLAN_CSV)
    planwerte = Planwerte(ergebnisplan, datei="ergebnisplan")
    erwarteter_gesamt_plan = [
        planwerte.wert("GESAMT", "", "01", jahr, wertart)
        for jahr, wertart in zip(jahre, wertarten, strict=True)
    ]
    assert steuerarten["gesamt_plan"] == erwarteter_gesamt_plan
    assert steuerarten["planzeile"] == "steuern"


def test_app_json_deterministisch(tmp_path: Path) -> None:
    ziel_a = tmp_path / "a"
    ziel_b = tmp_path / "b"
    erzeuge_app_daten(STANDARD_JAHR, app_daten_wurzel=ziel_a)
    erzeuge_app_daten(STANDARD_JAHR, app_daten_wurzel=ziel_b)

    for json_pfad in (
        HAUSHALT_JSON,
        STELLENPLAN_JSON,
        app_daten.PRODUKTE_APP_JSON,
        app_daten.INVESTITIONEN_JSON,
        app_daten.TEXTE_JSON,
    ):
        inhalt_a = (ziel_a / json_pfad).read_bytes()
        inhalt_b = (ziel_b / json_pfad).read_bytes()
        assert inhalt_a == inhalt_b

        text = inhalt_a.decode("utf-8")
        assert text.endswith("\n")
        assert "\r" not in text


def test_haushalt_json_eingecheckt_aktuell(tmp_path: Path) -> None:
    erzeuge_app_daten(STANDARD_JAHR, app_daten_wurzel=tmp_path)
    neu = (tmp_path / HAUSHALT_JSON).read_bytes()
    eingecheckt = (APP_DATEN_WURZEL / HAUSHALT_JSON).read_bytes()
    assert neu == eingecheckt


def test_stellenplan_json_eingecheckt_aktuell(tmp_path: Path) -> None:
    erzeuge_app_daten(STANDARD_JAHR, app_daten_wurzel=tmp_path)
    neu = (tmp_path / STELLENPLAN_JSON).read_bytes()
    eingecheckt = (APP_DATEN_WURZEL / STELLENPLAN_JSON).read_bytes()
    assert neu == eingecheckt


def test_keine_personennamen_in_app_daten(
    jahrgang: Jahrgang, kontext: tuple[pl.DataFrame, pl.DataFrame]
) -> None:
    seiten, hierarchie = kontext
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        namen = lies_personennamen(dokument, jahrgang, seiten, hierarchie)

    nadeln: set[str] = set()
    for _seite, text in namen:
        nadeln.add(text)
        nadeln.add("".join(text.split()))

    treffer: list[str] = []
    for pfad in APP_DATEN_WURZEL.rglob("*.json"):
        inhalt = pfad.read_text(encoding="utf-8")
        for nadel in nadeln:
            if nadel and nadel in inhalt:
                treffer.append(str(pfad.relative_to(APP_DATEN_WURZEL)))
    assert treffer == []


def test_haushalt_json_zuwendungen_sonstige(tmp_path: Path) -> None:
    erzeuge_app_daten(STANDARD_JAHR, app_daten_wurzel=tmp_path)
    daten = json.loads((tmp_path / HAUSHALT_JSON).read_text(encoding="utf-8"))
    zuwendungen = daten["vorbericht"]["zuwendungen"]
    jahre = daten["jahre"]

    sonstige = next(posten for posten in zuwendungen["posten"] if posten["posten"] == "sonstige")
    assert sonstige["berechnet"] is True
    assert sonstige["gerundet"] is False
    assert sonstige["name"] == "Sonstige"

    index_2026 = jahre.index(2026)
    assert sonstige["werte"][index_2026] is not None
    summe_posten = sum(
        posten["werte"][index_2026]
        for posten in zuwendungen["posten"]
        if posten["posten"] != "sonstige" and posten["werte"][index_2026] is not None
    )
    assert summe_posten + sonstige["werte"][index_2026] == zuwendungen["gesamt_plan"][index_2026]

    for index, jahr in enumerate(jahre):
        if jahr != 2026:
            assert sonstige["werte"][index] is None


def test_haushalt_json_vorbericht_reihenfolge(tmp_path: Path) -> None:
    erzeuge_app_daten(STANDARD_JAHR, app_daten_wurzel=tmp_path)
    daten = json.loads((tmp_path / HAUSHALT_JSON).read_text(encoding="utf-8"))
    assert list(daten["vorbericht"]) == [
        "steuerarten",
        "zuwendungen",
        "transferaufwendungen",
        "kita_zuschuesse",
        "investitionszuwendungen",
        "leistungsentgelte",
        "kostenerstattungen",
        "personal",
        "sachaufwand",
        "sonstige_aufwendungen",
        "sonstige_ertraege",
    ]


def test_sonstige_ertraege_ergibt_gep_zeile_07(tmp_path: Path) -> None:
    """Tabelle 2.1.7 (Phase 5 D-04): wo der berechnete Posten "Sonstige" nicht null ist,
    ergibt Σ Posten inkl. Sonstige exakt GEP Z. 07; in allen anderen Jahren liegt die
    gedruckte Gesamtzeile innerhalb ±REGEL5_TOLERANZ_GEP_EURO an GEP Z. 07."""
    erzeuge_app_daten(STANDARD_JAHR, app_daten_wurzel=tmp_path)
    daten = json.loads((tmp_path / HAUSHALT_JSON).read_text(encoding="utf-8"))
    tabelle = daten["vorbericht"]["sonstige_ertraege"]
    gep_07 = daten["ergebnisplan"]["GESAMT"]["zeilen"]["sonstige_ordentliche_ertraege"]

    assert tabelle["planzeile"] == "sonstige_ordentliche_ertraege"
    assert tabelle["gesamt_plan"] == gep_07
    sonstige = next(p for p in tabelle["posten"] if p["posten"] == "sonstige")
    assert sonstige["berechnet"] is True
    assert tabelle["posten"][-1] is sonstige
    assert any(p["posten"] == "konzessionsabgaben" for p in tabelle["posten"])

    mit_sonstige = 0
    for index in range(len(daten["jahre"])):
        if sonstige["werte"][index] is not None:
            mit_sonstige += 1
            summe = sum(p["werte"][index] or 0 for p in tabelle["posten"])
            assert summe == gep_07[index]
        else:
            gesamt = tabelle["gesamt_vorbericht"]["werte"][index]
            assert abs(gesamt - gep_07[index]) <= REGEL5_TOLERANZ_GEP_EURO
    # Der gedruckte 2028-Fehler (S. 33) muss als "Sonstige" sichtbar sein, nicht verschwinden.
    assert mit_sonstige >= 1


def test_investitionszuwendungen_gleich_gfp_18_im_haushaltsjahr(tmp_path: Path) -> None:
    """Vorbericht S. 52 (Phase 5 D-03): Σ Pauschalen und Förderungen == GFP Z. 18 im
    Haushaltsjahr, alle anderen Jahre ohne Wert; keine Ergebnisplan-Zeile (Spez. 3.1)."""
    erzeuge_app_daten(STANDARD_JAHR, app_daten_wurzel=tmp_path)
    daten = json.loads((tmp_path / HAUSHALT_JSON).read_text(encoding="utf-8"))
    tabelle = daten["vorbericht"]["investitionszuwendungen"]
    index = daten["jahre"].index(daten["haushaltsjahr"])
    gfp_18 = daten["finanzplan"]["GESAMT"]["zeilen"]["investitionszuwendungen"]

    assert tabelle["tabelle"] == "investitionszuwendungen"
    assert tabelle["planzeile"] is None
    assert tabelle["gesamt_plan"] is None
    assert tabelle["posten"], "investitionszuwendungen: keine Posten"
    assert all(not posten["berechnet"] for posten in tabelle["posten"])

    summe = sum(p["werte"][index] for p in tabelle["posten"] if p["werte"][index] is not None)
    assert summe == gfp_18[index]
    assert tabelle["gesamt_vorbericht"]["werte"][index] == gfp_18[index]
    for andere, wert in enumerate(tabelle["gesamt_vorbericht"]["werte"]):
        if andere != index:
            assert wert is None
            assert all(posten["werte"][andere] is None for posten in tabelle["posten"])


def test_haushalt_json_weitere_vorberichtstabellen(tmp_path: Path) -> None:
    erzeuge_app_daten(STANDARD_JAHR, app_daten_wurzel=tmp_path)
    daten = json.loads((tmp_path / HAUSHALT_JSON).read_text(encoding="utf-8"))
    jahre = daten["jahre"]
    wertarten = daten["wertarten"]
    ergebnisplan = lies_plan_csv(DATEN_WURZEL / ERGEBNISPLAN_CSV)
    planwerte = Planwerte(ergebnisplan, datei="ergebnisplan")

    erwartete_gep_zeile = {
        "leistungsentgelte": "04",
        "kostenerstattungen": "06",
        "personal": "11",
        "sachaufwand": "13",
        "sonstige_aufwendungen": "16",
    }
    for tabelle, gep_zeile in erwartete_gep_zeile.items():
        eintrag = daten["vorbericht"][tabelle]
        assert eintrag["tabelle"] == tabelle
        assert eintrag["planzeile"] is not None
        erwarteter_gesamt_plan = [
            planwerte.wert("GESAMT", "", gep_zeile, jahr, wertart)
            for jahr, wertart in zip(jahre, wertarten, strict=True)
        ]
        assert eintrag["gesamt_plan"] == erwarteter_gesamt_plan
        assert eintrag["posten"], f"{tabelle}: keine Posten"


def test_zeilen_namen_decken_ergebnisplan_ab(tmp_path: Path) -> None:
    """Phase 5 (RESEARCH Pitfall 9): `zeilen_namen.ergebnisplan` hat genau einen Eintrag je
    App-Zeile des Ergebnisplans, in derselben Reihenfolge, mit dem gedruckten Namen aus
    `ZEILEN` -- keine zweite Namenstabelle."""
    erzeuge_app_daten(STANDARD_JAHR, app_daten_wurzel=tmp_path)
    daten = json.loads((tmp_path / HAUSHALT_JSON).read_text(encoding="utf-8"))
    namen = daten["zeilen_namen"]["ergebnisplan"]

    assert [eintrag["schluessel"] for eintrag in namen] == list(
        daten["ergebnisplan"]["GESAMT"]["zeilen"]
    )
    assert [eintrag["schluessel"] for eintrag in namen] == list(app_daten.ERGEBNISPLAN_APP_ZEILEN)
    for eintrag in namen:
        definition = ZEILEN["gesamtergebnisplan"][eintrag["nummer"]]
        assert eintrag["schluessel"] == definition.kanonisch
        assert eintrag["name"] == definition.name
        assert eintrag["ist_summe"] is definition.ist_summe
    assert list(namen[0]) == ["schluessel", "nummer", "name", "ist_summe"]


def test_zeilen_namen_decken_finanzplan_ab(tmp_path: Path) -> None:
    erzeuge_app_daten(STANDARD_JAHR, app_daten_wurzel=tmp_path)
    daten = json.loads((tmp_path / HAUSHALT_JSON).read_text(encoding="utf-8"))
    namen = daten["zeilen_namen"]["finanzplan"]

    assert [eintrag["schluessel"] for eintrag in namen] == list(
        daten["finanzplan"]["GESAMT"]["zeilen"]
    )
    for eintrag in namen:
        definition = ZEILEN["gesamtfinanzplan"][eintrag["nummer"]]
        assert eintrag["schluessel"] == definition.kanonisch
        assert eintrag["name"] == definition.name
        assert eintrag["ist_summe"] is definition.ist_summe
    investiv = next(e for e in namen if e["schluessel"] == "investitionszuwendungen")
    assert investiv["nummer"] == "18"
    assert investiv["name"] == "Zuwendungen für Investitionsmaßnahmen"


def test_zeilen_namen_ist_letzter_schluessel_nach_eigenkapital(tmp_path: Path) -> None:
    """Das neue Top-Level-Feld hängt hinten an: bestehende Schlüssel behalten ihre
    Reihenfolge (D-21-Vertrag)."""
    erzeuge_app_daten(STANDARD_JAHR, app_daten_wurzel=tmp_path)
    daten = json.loads((tmp_path / HAUSHALT_JSON).read_text(encoding="utf-8"))
    assert list(daten)[-2:] == ["eigenkapital", "zeilen_namen"]


def test_haushalt_json_meta(tmp_path: Path) -> None:
    erzeuge_app_daten(STANDARD_JAHR, app_daten_wurzel=tmp_path)
    daten = json.loads((tmp_path / HAUSHALT_JSON).read_text(encoding="utf-8"))
    assert list(daten)[:4] == ["haushaltsjahr", "jahre", "wertarten", "meta"]
    meta = daten["meta"]
    assert meta["einwohner"]["wert"] == 11741
    assert meta["kreisumlage"]["brutto"]["wert"] == 11472478
    assert meta["kreisumlage"]["brutto"]["berechnet"] is True


def test_haushalt_json_eigenkapital(tmp_path: Path) -> None:
    erzeuge_app_daten(STANDARD_JAHR, app_daten_wurzel=tmp_path)
    daten = json.loads((tmp_path / HAUSHALT_JSON).read_text(encoding="utf-8"))
    assert list(daten)[-2] == "eigenkapital"
    eigenkapital = daten["eigenkapital"]
    assert eigenkapital["tabelle"] == "eigenkapital"
    assert eigenkapital["quelle_einheit"] == "euro"
    assert eigenkapital["planzeile"] is None
    assert eigenkapital["gesamt_plan"] is None
    jahresergebnis = next(p for p in eigenkapital["posten"] if p["posten"] == "jahresergebnis")
    index_2026 = daten["jahre"].index(2026)
    assert jahresergebnis["werte"][index_2026] == -2353506


def test_stellenplan_json_vzae(tmp_path: Path) -> None:
    """`stellenplan.json`-Zeilen entsprechen `stellenplan.csv`-Zeilen mit
    `stellen = stellen_hundertstel / 100` (VZÄ); `personen` bleibt unverändert (D-18,
    D-19, Plan 04-03)."""
    erzeuge_app_daten(STANDARD_JAHR, app_daten_wurzel=tmp_path)
    daten = json.loads((tmp_path / STELLENPLAN_JSON).read_text(encoding="utf-8"))
    assert daten["haushaltsjahr"] == STANDARD_JAHR
    assert daten["einheit_stellen"] == "vzae"

    df = lies_stellenplan_csv(DATEN_WURZEL / STELLENPLAN_CSV)
    assert len(daten["zeilen"]) == df.height

    for zeile_json, zeile_csv in zip(daten["zeilen"], df.iter_rows(named=True), strict=True):
        assert zeile_json["teil"] == zeile_csv["teil"]
        assert zeile_json["gruppe"] == zeile_csv["gruppe"]
        assert zeile_json["merkmal"] == zeile_csv["merkmal"]
        assert zeile_json["jahr"] == zeile_csv["jahr"]
        assert zeile_json["personen"] == zeile_csv["personen"]
        if zeile_csv["stellen_hundertstel"] is None:
            assert zeile_json["stellen"] is None
        else:
            assert zeile_json["stellen"] == zeile_csv["stellen_hundertstel"] / 100

    tarif_2026 = [
        zeile
        for zeile in daten["zeilen"]
        if zeile["teil"] == "tarif"
        and zeile["produktbereich"] is None
        and zeile["merkmal"] == "stellen"
        and zeile["jahr"] == daten["haushaltsjahr"]
    ]
    assert round(sum(zeile["stellen"] for zeile in tarif_2026), 2) == 52.26


@pytest.fixture(scope="module")
def kl_kontext() -> dict[str, object]:
    """Baut knoten/ergebnisplan/finanzplan einmal direkt über die app_daten-Funktionen
    (nicht über JSON-Rundreise), für die KL-/Zuschussbedarf-Tests unten (D-01 bis D-04,
    D-22, D-23)."""
    jahrgang = lade_jahrgang(STANDARD_JAHR)
    ergebnisplan = lies_plan_csv(DATEN_WURZEL / ERGEBNISPLAN_CSV)
    finanzplan = lies_plan_csv(DATEN_WURZEL / FINANZPLAN_CSV)
    hierarchie = lies_hierarchie_csv(DATEN_WURZEL / HIERARCHIE_CSV)
    transfer_df = lies_vorbericht_csv(DATEN_WURZEL / TRANSFERAUFWENDUNGEN_CSV)
    produkt = layout_text(jahrgang, "weitergabe_kreis_land", "produkt")

    spalten_zu_wertart = [
        app_daten.zerlege_spaltenkopf(kopf) for kopf in jahrgang.spalten["ergebnisplan"]
    ]
    jahre = [jahr for _wertart, jahr in spalten_zu_wertart]
    wertarten = [wertart for wertart, _jahr in spalten_zu_wertart]
    gep_pdf_seite = ergebnisplan.filter(pl.col("ebene") == "GESAMT")["pdf_seite"][0]

    knoten = app_daten.baue_knoten(
        hierarchie,
        ergebnisplan=ergebnisplan,
        transfer_df=transfer_df,
        produkt=produkt,
        gep_pdf_seite=gep_pdf_seite,
    )
    ergebnisplan_app = app_daten.baue_ergebnisplan(
        knoten,
        ergebnisplan=ergebnisplan,
        transfer_df=transfer_df,
        hierarchie=hierarchie,
        produkt=produkt,
        jahre=jahre,
        wertarten=wertarten,
    )
    finanzplan_app = app_daten.baue_finanzplan(
        finanzplan, jahre=jahre, wertarten=wertarten, haushaltsjahr=jahrgang.haushaltsjahr
    )
    return {
        "jahrgang": jahrgang,
        "ergebnisplan": ergebnisplan,
        "finanzplan": finanzplan,
        "hierarchie": hierarchie,
        "transfer_df": transfer_df,
        "produkt": produkt,
        "jahre": jahre,
        "wertarten": wertarten,
        "knoten": knoten,
        "ergebnisplan_app": ergebnisplan_app,
        "finanzplan_app": finanzplan_app,
    }


def test_kl_knoten_gleich_tp_15(kl_kontext: dict[str, object]) -> None:
    """D-01: KL zeilen.transferaufwendungen == Planwerte P <produkt> Z. 15, jedes Jahr."""
    ergebnisplan_app = kl_kontext["ergebnisplan_app"]
    ergebnisplan = kl_kontext["ergebnisplan"]
    jahre = kl_kontext["jahre"]
    wertarten = kl_kontext["wertarten"]
    produkt = kl_kontext["produkt"]
    planwerte = Planwerte(ergebnisplan, datei="ergebnisplan")

    kl_transfer = ergebnisplan_app[app_daten.KL_CODE]["zeilen"]["transferaufwendungen"]
    for index, (jahr, wertart) in enumerate(zip(jahre, wertarten, strict=True)):
        erwartet = planwerte.wert("P", produkt, "15", jahr, wertart)
        assert kl_transfer[index] == erwartet


def test_kl_knoten_reduziert_kette(kl_kontext: dict[str, object]) -> None:
    """D-03: Produkt, PG und PB sind um TP Z. 15 reduziert; PB heißt "Allgemeine
    Finanzwirtschaft"."""
    ergebnisplan_app = kl_kontext["ergebnisplan_app"]
    ergebnisplan = kl_kontext["ergebnisplan"]
    hierarchie = kl_kontext["hierarchie"]
    jahre = kl_kontext["jahre"]
    wertarten = kl_kontext["wertarten"]
    produkt = kl_kontext["produkt"]
    planwerte = Planwerte(ergebnisplan, datei="ergebnisplan")

    eltern_je_code = {z["code"]: z["eltern_code"] for z in hierarchie.iter_rows(named=True)}
    kette = [produkt]
    eltern = eltern_je_code[produkt]
    while eltern is not None:
        kette.append(eltern)
        eltern = eltern_je_code.get(eltern)
    assert len(kette) == 3

    for code in kette:
        ebene = {0: "P", 1: "PG", 2: "PB"}[kette.index(code)]
        for index, (jahr, wertart) in enumerate(zip(jahre, wertarten, strict=True)):
            delta = planwerte.wert("P", produkt, "15", jahr, wertart)
            orig_transfer = planwerte.wert(ebene, code, "15", jahr, wertart)
            orig_aufwand = planwerte.wert(ebene, code, "17", jahr, wertart)
            orig_jahresergebnis = planwerte.wert(ebene, code, "26", jahr, wertart)
            assert ergebnisplan_app[code]["zeilen"]["transferaufwendungen"][index] == (
                orig_transfer - delta
            )
            assert ergebnisplan_app[code]["zeilen"]["ordentliche_aufwendungen"][index] == (
                orig_aufwand - delta
            )
            assert ergebnisplan_app[code]["zeilen"]["jahresergebnis"][index] == (
                orig_jahresergebnis + delta
            )

    pb_name = next(k["name"] for k in kl_kontext["knoten"] if k["code"] == kette[2])
    assert pb_name == "Allgemeine Finanzwirtschaft"


def test_kl_knoten_kinder_gerundet(kl_kontext: dict[str, object]) -> None:
    """D-02: die drei Kinder sind posten x 1000, gerundet, Summe nahe KL (Toleranz)."""
    knoten_je_code = {k["code"]: k for k in kl_kontext["knoten"]}
    ergebnisplan_app = kl_kontext["ergebnisplan_app"]
    jahre = kl_kontext["jahre"]

    kind_codes = [f"{app_daten.KL_CODE}.{posten}" for posten in WEITERGABE_POSTEN]
    for code in kind_codes:
        assert knoten_je_code[code]["gerundet"] is True
        assert knoten_je_code[code]["ebene"] == "PG"
        assert knoten_je_code[code]["eltern"] == app_daten.KL_CODE

    toleranz = len(WEITERGABE_POSTEN) * REGEL5_TOLERANZ_GEP_EURO
    for index in range(len(jahre)):
        kinder_summe = sum(
            ergebnisplan_app[code]["zeilen"]["transferaufwendungen"][index] for code in kind_codes
        )
        kl_wert = ergebnisplan_app[app_daten.KL_CODE]["zeilen"]["transferaufwendungen"][index]
        assert abs(kinder_summe - kl_wert) <= toleranz


def test_zuschussbedarf_formel(kl_kontext: dict[str, object]) -> None:
    """D-23: berechnet.zuschussbedarf == aufwand - ertraege; ueberschuss == (< 0)."""
    ergebnisplan_app = kl_kontext["ergebnisplan_app"]
    for code, werte in ergebnisplan_app.items():
        berechnet = werte["berechnet"]
        for index in range(len(kl_kontext["jahre"])):
            erwarteter_aufwand = (
                werte["zeilen"]["ordentliche_aufwendungen"][index]
                + werte["zeilen"]["zinsaufwendungen"][index]
            )
            erwartete_ertraege = (
                werte["zeilen"]["ordentliche_ertraege"][index]
                + werte["zeilen"]["finanzertraege"][index]
            )
            assert berechnet["aufwand"][index] == erwarteter_aufwand, code
            assert berechnet["ertraege"][index] == erwartete_ertraege, code
            erwarteter_zuschussbedarf = erwarteter_aufwand - erwartete_ertraege
            assert berechnet["zuschussbedarf"][index] == erwarteter_zuschussbedarf, code
            assert berechnet["ueberschuss"][index] == (erwarteter_zuschussbedarf < 0), code


def test_zuschussbedarf_summe_top_knoten(kl_kontext: dict[str, object]) -> None:
    """D-23: Σ top knoten (15 PB inkl. reduziertem 16, plus KL) == Σ unreduzierter PB,
    je Zeile/Jahr; GESAMT aufwand/ertraege im Haushaltsjahr == Satzung."""
    ergebnisplan_app = kl_kontext["ergebnisplan_app"]
    ergebnisplan = kl_kontext["ergebnisplan"]
    hierarchie = kl_kontext["hierarchie"]
    jahre = kl_kontext["jahre"]
    wertarten = kl_kontext["wertarten"]
    planwerte = Planwerte(ergebnisplan, datei="ergebnisplan")

    pb_codes = sorted(hierarchie.filter(pl.col("ebene") == "PB")["code"].unique().to_list())
    top_codes = pb_codes + [app_daten.KL_CODE]

    for kanonisch in app_daten.ERGEBNISPLAN_APP_ZEILEN:
        for index, (jahr, wertart) in enumerate(zip(jahre, wertarten, strict=True)):
            top_summe = sum(
                ergebnisplan_app[code]["zeilen"][kanonisch][index] for code in top_codes
            )
            zeile_nr = app_daten._zeile_fuer_kanonisch("teilergebnisplan")[kanonisch]
            pb_summe = sum(
                planwerte.wert("PB", pb_code, zeile_nr, jahr, wertart) for pb_code in pb_codes
            )
            assert top_summe == pb_summe, (kanonisch, jahr, wertart)

    jahrgang = kl_kontext["jahrgang"]
    index_haushaltsjahr = jahre.index(jahrgang.haushaltsjahr)
    gesamt_berechnet = ergebnisplan_app[app_daten.GESAMT_CODE]["berechnet"]
    assert gesamt_berechnet["aufwand"][index_haushaltsjahr] == 30455569
    assert gesamt_berechnet["ertraege"][index_haushaltsjahr] == 27502063


def test_zuschussbedarf_allgemeine_finanzwirtschaft_ueberschuss(
    kl_kontext: dict[str, object],
) -> None:
    """D-04: die PB des konfigurierten Produkts hat ueberschuss true im Haushaltsjahr."""
    jahrgang = kl_kontext["jahrgang"]
    index_haushaltsjahr = kl_kontext["jahre"].index(jahrgang.haushaltsjahr)
    pb_name_code = "16"
    ueberschuss = kl_kontext["ergebnisplan_app"][pb_name_code]["berechnet"]["ueberschuss"]
    assert ueberschuss[index_haushaltsjahr] is True


def test_ergebnisplan_ohne_interne_leistungen(kl_kontext: dict[str, object]) -> None:
    """D-22: TP 27/28 (interne Erträge/Aufwendungen) tauchen in keinem Knoten auf."""
    for werte in kl_kontext["ergebnisplan_app"].values():
        assert "interne_ertraege" not in werte["zeilen"]
        assert "interne_aufwendungen" not in werte["zeilen"]


def test_finanzplan_nur_gesamt(kl_kontext: dict[str, object]) -> None:
    """D-22: finanzplan hat ausschließlich den GESAMT-Schlüssel, mit allen 41 Zeilen."""
    finanzplan_app = kl_kontext["finanzplan_app"]
    assert list(finanzplan_app) == ["GESAMT"]
    assert len(finanzplan_app["GESAMT"]["zeilen"]) == 41
    assert finanzplan_app["GESAMT"]["ve"]["auszahlungen_investitionen"] == 11600000


def test_hierarchie_csv_unveraendert(tmp_path: Path) -> None:
    """D-03: erzeuge_app_daten lässt hierarchie.csv byte-identisch (KL-Split lebt
    ausschließlich in app_daten.py, nie in daten/aufbereitet/)."""
    vorher = (DATEN_WURZEL / HIERARCHIE_CSV).read_bytes()
    erzeuge_app_daten(STANDARD_JAHR, app_daten_wurzel=tmp_path)
    nachher = (DATEN_WURZEL / HIERARCHIE_CSV).read_bytes()
    assert nachher == vorher


def test_haushalt_json_knoten_und_ergebnisplan(tmp_path: Path) -> None:
    """Integrationstest über die JSON-Rundreise: knoten/ergebnisplan/finanzplan landen
    in haushalt.json mit den erwarteten Schlüsseln (D-21)."""
    erzeuge_app_daten(STANDARD_JAHR, app_daten_wurzel=tmp_path)
    daten = json.loads((tmp_path / HAUSHALT_JSON).read_text(encoding="utf-8"))
    assert list(daten) == [
        "haushaltsjahr",
        "jahre",
        "wertarten",
        "meta",
        "knoten",
        "ergebnisplan",
        "finanzplan",
        "vorbericht",
        "eigenkapital",
        "zeilen_namen",
    ]
    knoten_je_code = {k["code"]: k for k in daten["knoten"]}
    assert knoten_je_code["KL"]["eltern"] == "GESAMT"
    assert knoten_je_code["KL"]["synthetisch"] is True
    assert knoten_je_code["KL.kreisumlage"]["gerundet"] is True
    assert knoten_je_code["16"]["name"] == "Allgemeine Finanzwirtschaft"
    index_haushaltsjahr = daten["jahre"].index(daten["haushaltsjahr"])
    assert (
        daten["ergebnisplan"]["KL"]["zeilen"]["transferaufwendungen"][index_haushaltsjahr]
        == 11001181
    )
    assert daten["ergebnisplan"]["16"]["berechnet"]["ueberschuss"][index_haushaltsjahr] is True
    assert list(daten["finanzplan"]) == ["GESAMT"]
    assert "interne_ertraege" not in json.dumps(daten["ergebnisplan"])


def test_produkte_app_json_eingecheckt_aktuell(tmp_path: Path) -> None:
    erzeuge_app_daten(STANDARD_JAHR, app_daten_wurzel=tmp_path)
    neu = (tmp_path / app_daten.PRODUKTE_APP_JSON).read_bytes()
    eingecheckt = (APP_DATEN_WURZEL / app_daten.PRODUKTE_APP_JSON).read_bytes()
    assert neu == eingecheckt


def test_investitionen_json_eingecheckt_aktuell(tmp_path: Path) -> None:
    erzeuge_app_daten(STANDARD_JAHR, app_daten_wurzel=tmp_path)
    neu = (tmp_path / app_daten.INVESTITIONEN_JSON).read_bytes()
    eingecheckt = (APP_DATEN_WURZEL / app_daten.INVESTITIONEN_JSON).read_bytes()
    assert neu == eingecheckt


def test_produkte_json_ohne_personenfelder(tmp_path: Path) -> None:
    """D-13, D-21: 63 Datensätze, exakt APP_PRODUKT_SCHLUESSEL, keine PERSONENFELDER;
    Grundzahlen-Werte sind int bei nachkommastellen == 0."""
    from ostbevern.produkte import PERSONENFELDER

    erzeuge_app_daten(STANDARD_JAHR, app_daten_wurzel=tmp_path)
    produkte = json.loads((tmp_path / app_daten.PRODUKTE_APP_JSON).read_text(encoding="utf-8"))
    assert len(produkte) == 63
    for produkt in produkte:
        assert set(produkt) == set(app_daten.APP_PRODUKT_SCHLUESSEL)
        for feld in PERSONENFELDER:
            assert feld not in produkt
        assert "grundzahlen" in produkt
        for eintrag in produkt["grundzahlen"]:
            if eintrag["nachkommastellen"] == 0:
                for wert in eintrag["werte"]:
                    assert isinstance(wert["wert"], int)


def test_investitionen_massnahmen_summen_und_pb(tmp_path: Path) -> None:
    """D-13: Σ werte (Auszahlung) im Haushaltsjahr == GFP Z. 30, Σ (Einzahlung) ==
    GFP Z. 23 (wie Regel 6); jede Maßnahme hat ein pb."""
    erzeuge_app_daten(STANDARD_JAHR, app_daten_wurzel=tmp_path)
    daten = json.loads((tmp_path / app_daten.INVESTITIONEN_JSON).read_text(encoding="utf-8"))
    jahre = daten["jahre"]
    index_haushaltsjahr = jahre.index(daten["haushaltsjahr"])

    finanzplan = lies_plan_csv(DATEN_WURZEL / FINANZPLAN_CSV)
    planwerte = Planwerte(finanzplan, datei="finanzplan")
    wertart_haushaltsjahr = daten["wertarten"][index_haushaltsjahr]

    for richtung, zeile in (("auszahlung", "30"), ("einzahlung", "23")):
        summe = sum(
            massnahme["werte"][index_haushaltsjahr] or 0
            for massnahme in daten["massnahmen"]
            if massnahme["richtung"] == richtung
        )
        erwartet = planwerte.wert(
            "GESAMT", "", zeile, daten["haushaltsjahr"], wertart_haushaltsjahr
        )
        assert summe == erwartet

    for massnahme in daten["massnahmen"]:
        assert massnahme["pb"]


def test_investitionen_schuldenstand_fortschreibung(tmp_path: Path) -> None:
    """D-14: gedruckte Jahre == verbindlichkeiten x1000, berechnet False; spätere Jahre
    per Formel, NRW.Bank konstant auf dem letzten gedruckten Stand, berechnet True;
    pro_kopf trifft 656 Ende Vorjahr; liquiditaetskredite null ohne gedruckten Stand."""
    erzeuge_app_daten(STANDARD_JAHR, app_daten_wurzel=tmp_path)
    daten = json.loads((tmp_path / app_daten.INVESTITIONEN_JSON).read_text(encoding="utf-8"))
    s = daten["schuldenstand"]
    jahre = daten["jahre"]
    i = jahre.index(daten["haushaltsjahr"])

    assert s["pro_kopf"][i - 1] == 656
    assert s["investitionskredite"][i] == 11629000
    assert s["berechnet"][i] is False
    assert s["berechnet"][i + 1] is True
    assert s["nrw_bank"][i + 1] == s["nrw_bank"][i]
    for index in range(len(jahre)):
        assert s["gesamt"][index] == s["investitionskredite"][index] + s["nrw_bank"][index]
    for index in range(i + 1, len(jahre)):
        assert s["liquiditaetskredite"][index] is None
    for index in range(0, i + 1):
        assert s["liquiditaetskredite"][index] is not None


def test_app_daten_liest_kein_pdf() -> None:
    quelle = Path(app_daten.__file__).read_text(encoding="utf-8")
    baum = ast.parse(quelle)
    module_namen: set[str] = set()
    for knoten in ast.walk(baum):
        if isinstance(knoten, ast.Import):
            module_namen.update(alias.name for alias in knoten.names)
        elif isinstance(knoten, ast.ImportFrom) and knoten.module:
            module_namen.add(knoten.module)
    verbotene = {"pdfplumber", "ostbevern.pdf"}
    assert not (module_namen & verbotene)


def test_texte_json_eingecheckt_aktuell(tmp_path: Path) -> None:
    erzeuge_app_daten(STANDARD_JAHR, app_daten_wurzel=tmp_path)
    neu = (tmp_path / app_daten.TEXTE_JSON).read_bytes()
    eingecheckt = (APP_DATEN_WURZEL / app_daten.TEXTE_JSON).read_bytes()
    assert neu == eingecheckt


def test_texte_json_nur_verwendete_werte(tmp_path: Path) -> None:
    """D-15: `werte` enthält ausschließlich die tatsächlich in `texte` verwendeten
    Datenschlüssel, kein vollständiger Dump der textwerte-Namensraum (die hunderte
    ungenutzte Schlüssel hat)."""
    erzeuge_app_daten(STANDARD_JAHR, app_daten_wurzel=tmp_path)
    daten = json.loads((tmp_path / app_daten.TEXTE_JSON).read_text(encoding="utf-8"))
    assert list(daten) == ["haushaltsjahr", "texte", "werte"]

    verwendete_schluessel: set[str] = set()
    for text in daten["texte"]:
        assert text["quelle_seiten"]
        for absatz in text["absaetze"]:
            for treffer in PLATZHALTER_MUSTER.finditer(absatz):
                verwendete_schluessel.add(treffer.group(1))

    assert set(daten["werte"]) == verwendete_schluessel
    # Deutlich weniger als die vollständige textwerte-Namensraum (hunderte Schlüssel).
    assert len(daten["werte"]) < 100


def test_unbekannter_platzhalter_bricht_schritt_07_ab(tmp_path: Path) -> None:
    """D-15: ein Platzhalter mit unbekanntem Datenschlüssel bricht erzeuge_app_daten mit
    TexteFehler ab -- geprüft über eine tmp-Kopie von daten/ mit manipulierter
    erklaerungen.md (die eingecheckte Datei bleibt unberührt, D-06-Stil)."""
    daten_kopie = tmp_path / "daten"
    shutil.copytree(DATEN_WURZEL, daten_kopie)
    ziel = daten_kopie / ERKLAERUNGEN_MD
    ziel.write_text(
        "# Erklärtexte\n\n"
        "## testschluessel\n"
        "Titel: Test\n"
        "Quelle: S. 1\n\n"
        "Ein Text mit {{nicht.vorhandener.schluessel|euro}}.\n",
        encoding="utf-8",
    )
    with pytest.raises(TexteFehler, match="nicht.vorhandener.schluessel"):
        erzeuge_app_daten(
            STANDARD_JAHR, daten_wurzel=daten_kopie, app_daten_wurzel=tmp_path / "app"
        )
