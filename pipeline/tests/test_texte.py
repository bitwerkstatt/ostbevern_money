"""Tests für ostbevern.texte: Platzhalter-Vertrag der Erklärtexte (D-15, D-16, MANU-08).

`lies_erklaerungen`/`pruefe_text` werden gegen synthetische Dateien in `tmp_path`
getestet (keine Jahrgangswerte im Test, synthetische Schlüssel). `textwerte`/
`loese_auf` werden gegen die eingecheckten App-JSON-Dateien getestet (`app/src/data/`),
die Jahre kommen aus `haushalt.json` selbst (`haushaltsjahr`/`jahre`), nie als Literal.
"""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import pytest

from ostbevern.konfiguration import PROJEKT_WURZEL, STANDARD_JAHR, lade_jahrgang
from ostbevern.schema import DATEN_WURZEL, ERKLAERUNGEN_MD, GLOSSAR_MD
from ostbevern.texte import (
    ABGELEITET,
    FORMATKUERZEL,
    Erklaertext,
    TexteFehler,
    lies_erklaerungen,
    lies_glossar,
    loese_auf,
    pruefe_grundzahl_jahre,
    pruefe_text,
    textwerte,
    vorschau,
)

APP_DATEN_WURZEL = PROJEKT_WURZEL / "app" / "src" / "data"

# Die zehn Erklärtexte des Phase-4-Umfangs (D-16); gleicher Vollständigkeits-Check wie
# die Task-1-Acceptance-Kriterien, aber als dauerhafter Regressionstest.
_PHASE4_SCHLUESSEL = {
    "schluesselzuweisung",
    "gewerbesteuer",
    "kreisumlage",
    "grundsteuer_hebesaetze",
    "sonderposten",
    "globaler_minderaufwand",
    "defizit_ruecklagen",
    "schulden",
    "verpflichtungsermaechtigungen",
    "nicht_im_haushalt",
}

# Phase 5 (Plan 05-03, D-19, AUSG-03, EINN-02/03): sieben jahrneutrale Erklärtexte ohne
# jeden Platzhalter -- gültig für jedes wählbare Jahr (Pitfall 6).
_JAHRNEUTRAL_SCHLUESSEL = {
    "steuern_selbst_festgelegt",
    "zuwendungen_laufende_zwecke",
    "ueberschuss_pb_16",
    "ueberschuss_pb_11",
    "ueberschuss_allgemein",
    "ueberschuss_ruecklage",
    "geldfluss_lesehilfe",
}

# Phase 6 (Plan 06-04, D-20): vier abgenommene Erklärtexte. Die ersten beiden sind
# jahrneutral (ohne Platzhalter), polster und schulden_anstieg ziehen ihre Zahlen aus den
# ABGELEITET-Formeln.
_PHASE6_JAHRNEUTRAL = {"bindungsgrad_selbstauskunft", "ueberschuss_produkte"}
_PHASE6_SCHLUESSEL = _PHASE6_JAHRNEUTRAL | {"polster", "schulden_anstieg"}
# Phase 6: drei neue Glossarbegriffe (D-17, D-18), alle ohne Platzhalter.
_PHASE6_GLOSSAR = {"nicht_im_haushalt", "vzae", "entgeltgruppen"}
_ERKLAERUNGEN_SCHLUESSEL = _PHASE4_SCHLUESSEL | _JAHRNEUTRAL_SCHLUESSEL | _PHASE6_SCHLUESSEL

# GLOS-01 / Spez. 6.14: die 22 Pflichtbegriffe des Glossars unter stabilen Schlüsseln.
_GLOSSAR_PFLICHT = {
    "ergebnisplan",
    "finanzplan",
    "ertrag_aufwand",
    "einzahlung_auszahlung",
    "produkt",
    "produktbereich",
    "transferaufwendungen",
    "kreisumlage",
    "jugendamtsumlage",
    "gewerbesteuerumlage",
    "schluesselzuweisung",
    "hebesatz",
    "sonderposten",
    "abschreibungen",
    "globaler_minderaufwand",
    "ausgleichsruecklage",
    "allgemeine_ruecklage",
    "verpflichtungsermaechtigung",
    "bindungsgrad",
    "zuschussbedarf",
    "nkf",
    "haushaltssicherung",
}


def _schreibe(tmp_path: Path, inhalt: str) -> Path:
    pfad = tmp_path / "erklaerungen.md"
    pfad.write_text(inhalt, encoding="utf-8")
    return pfad


_GUELTIGE_DATEI = """# Erklärtexte

## testschluessel
Titel: Ein Testtitel
Quelle: S. 12

Ein Absatz mit {{meta.einwohner|zahl}} Menschen, im Jahr 2026 geschrieben.

Ein zweiter Absatz ohne Zahl.

## zweiterschluessel
Titel: Noch ein Titel
Quelle: S. 5, S. 6

Nur ein Absatz, siehe § 4 und S. 311.
"""


# ---------------------------------------------------------------------------
# lies_erklaerungen
# ---------------------------------------------------------------------------


def test_lies_erklaerungen_gueltige_datei(tmp_path: Path) -> None:
    pfad = _schreibe(tmp_path, _GUELTIGE_DATEI)
    texte = lies_erklaerungen(pfad)
    assert len(texte) == 2
    erster = texte[0]
    assert erster.schluessel == "testschluessel"
    assert erster.titel == "Ein Testtitel"
    assert erster.quelle_seiten == (12,)
    assert len(erster.absaetze) == 2
    assert "{{meta.einwohner|zahl}}" in erster.absaetze[0]
    zweiter = texte[1]
    assert zweiter.quelle_seiten == (5, 6)


def test_lies_erklaerungen_fehlende_kopfzeile(tmp_path: Path) -> None:
    pfad = _schreibe(tmp_path, _GUELTIGE_DATEI.replace("# Erklärtexte", "# Etwas anderes"))
    with pytest.raises(TexteFehler):
        lies_erklaerungen(pfad)


def test_lies_erklaerungen_fehlende_titel_zeile(tmp_path: Path) -> None:
    inhalt = """# Erklärtexte

## testschluessel
Quelle: S. 12

Ein Absatz.
"""
    pfad = _schreibe(tmp_path, inhalt)
    with pytest.raises(TexteFehler):
        lies_erklaerungen(pfad)


def test_lies_erklaerungen_fehlende_quelle_zeile(tmp_path: Path) -> None:
    inhalt = """# Erklärtexte

## testschluessel
Titel: Ein Titel

Ein Absatz.
"""
    pfad = _schreibe(tmp_path, inhalt)
    with pytest.raises(TexteFehler):
        lies_erklaerungen(pfad)


def test_lies_erklaerungen_doppelter_schluessel(tmp_path: Path) -> None:
    inhalt = """# Erklärtexte

## testschluessel
Titel: Ein Titel
Quelle: S. 12

Ein Absatz.

## testschluessel
Titel: Noch ein Titel
Quelle: S. 13

Ein anderer Absatz.
"""
    pfad = _schreibe(tmp_path, inhalt)
    with pytest.raises(TexteFehler):
        lies_erklaerungen(pfad)


@pytest.mark.parametrize("schluessel", ["Grossbuchstabe", "123zahl", "mit-strich", "_unterstrich"])
def test_lies_erklaerungen_ungueltiger_schluessel(tmp_path: Path, schluessel: str) -> None:
    inhalt = f"""# Erklärtexte

## {schluessel}
Titel: Ein Titel
Quelle: S. 12

Ein Absatz.
"""
    pfad = _schreibe(tmp_path, inhalt)
    with pytest.raises(TexteFehler):
        lies_erklaerungen(pfad)


def test_lies_erklaerungen_kein_absatz_nach_titel_quelle(tmp_path: Path) -> None:
    inhalt = """# Erklärtexte

## testschluessel
Titel: Ein Titel
Quelle: S. 12
"""
    pfad = _schreibe(tmp_path, inhalt)
    with pytest.raises(TexteFehler):
        lies_erklaerungen(pfad)


# ---------------------------------------------------------------------------
# lies_erklaerungen: Kopfzeile und Quelle-Pflicht parametrierbar (Plan 05-03)
# ---------------------------------------------------------------------------


def test_lies_erklaerungen_eigene_kopfzeile(tmp_path: Path) -> None:
    pfad = _schreibe(tmp_path, _GUELTIGE_DATEI.replace("# Erklärtexte", "# Anderes"))
    assert len(lies_erklaerungen(pfad, kopfzeile="# Anderes")) == 2
    with pytest.raises(TexteFehler):
        lies_erklaerungen(pfad)


@pytest.mark.parametrize(
    "spanne",
    [
        "S. 309-311",
        "S. 24/25",
        "S. 5, S. 8 - 9",
        "S. 24, 25",
        "S. 309 bis 311",
        "S. 309 f.",
        "S. 309\u2014311",
        "S. 309 \u2212 311",
    ],
)
def test_lies_erklaerungen_lehnt_seitenspannen_in_der_quelle_ab(
    tmp_path: Path, spanne: str
) -> None:
    pfad = _schreibe(tmp_path, _GUELTIGE_DATEI.replace("Quelle: S. 12", f"Quelle: {spanne}"))
    with pytest.raises(TexteFehler, match="jede Seite einzeln"):
        lies_erklaerungen(pfad)


def test_lies_erklaerungen_quelle_optional_erlaubt_nur_titel(tmp_path: Path) -> None:
    inhalt = """# Erklärtexte

## nurtitel
Titel: Ein Titel

Ein Absatz ohne Zahl.
"""
    pfad = _schreibe(tmp_path, inhalt)
    with pytest.raises(TexteFehler):
        lies_erklaerungen(pfad)
    texte = lies_erklaerungen(pfad, quelle_pflicht=False)
    assert texte[0].quelle_seiten == ()
    assert texte[0].titel == "Ein Titel"


# ---------------------------------------------------------------------------
# lies_glossar (D-14, GLOS-01)
# ---------------------------------------------------------------------------

_GUELTIGES_GLOSSAR = """# Glossar

## begriff_a
Titel: Begriff A

Der Begriff A ist etwas Erklärtes. Er hat keine Zahl.

## begriff_b
Titel: Begriff B
Quelle: S. 24, S. 25

Begriff B betrifft {{meta.einwohner|zahl}} Menschen.
"""


def _glossar(tmp_path: Path, inhalt: str) -> Path:
    pfad = tmp_path / "glossar.md"
    pfad.write_text(inhalt, encoding="utf-8")
    return pfad


def test_lies_glossar_gueltige_datei(tmp_path: Path) -> None:
    texte = lies_glossar(_glossar(tmp_path, _GUELTIGES_GLOSSAR))
    assert [t.schluessel for t in texte] == ["begriff_a", "begriff_b"]
    assert texte[0].titel == "Begriff A"
    assert texte[0].quelle_seiten == ()
    assert texte[1].quelle_seiten == (24, 25)
    assert len(texte[0].absaetze) == 1


def test_lies_glossar_verlangt_kopfzeile_glossar(tmp_path: Path) -> None:
    with pytest.raises(TexteFehler):
        lies_glossar(_glossar(tmp_path, _GUELTIGES_GLOSSAR.replace("# Glossar", "# Erklärtexte")))


def test_lies_glossar_platzhalter_ohne_quelle_bricht_ab(tmp_path: Path) -> None:
    inhalt = _GUELTIGES_GLOSSAR.replace("Quelle: S. 24, S. 25\n", "")
    with pytest.raises(TexteFehler, match="begriff_b"):
        lies_glossar(_glossar(tmp_path, inhalt))


def test_lies_glossar_doppelter_schluessel_bricht_ab(tmp_path: Path) -> None:
    with pytest.raises(TexteFehler):
        lies_glossar(_glossar(tmp_path, _GUELTIGES_GLOSSAR.replace("begriff_b", "begriff_a")))


def test_lies_glossar_ungueltiger_schluessel_bricht_ab(tmp_path: Path) -> None:
    with pytest.raises(TexteFehler):
        lies_glossar(_glossar(tmp_path, _GUELTIGES_GLOSSAR.replace("begriff_b", "Begriff-B")))


def test_lies_glossar_ohne_titel_bricht_ab(tmp_path: Path) -> None:
    inhalt = _GUELTIGES_GLOSSAR.replace("Titel: Begriff A\n", "")
    with pytest.raises(TexteFehler):
        lies_glossar(_glossar(tmp_path, inhalt))


# ---------------------------------------------------------------------------
# pruefe_grundzahl_jahre (D-02)
# ---------------------------------------------------------------------------


def _produkte_fuer_d02() -> list[dict]:
    return [
        {
            "code": "999901",
            "grundzahlen": [
                {"position": 1, "einheit": "EUR"},
                {"position": 2, "einheit": "Anz."},
            ],
        }
    ]


def _text_mit(absatz: str) -> list[Erklaertext]:
    return [Erklaertext("t", "T", (1,), (absatz,))]


def test_grundzahl_jahre_euro_ab_erstem_planjahr_bricht_ab() -> None:
    texte = _text_mit("Es waren {{grundzahlen.999901.1.2024|mio}}.")
    with pytest.raises(TexteFehler, match="grundzahlen.999901.1.2024"):
        pruefe_grundzahl_jahre(texte, _produkte_fuer_d02(), 2024)


def test_grundzahl_jahre_euro_spaeter_als_erstes_planjahr_bricht_ab() -> None:
    texte = _text_mit("Es waren {{grundzahlen.999901.1.2025|euro}}.")
    with pytest.raises(TexteFehler):
        pruefe_grundzahl_jahre(texte, _produkte_fuer_d02(), 2024)


def test_grundzahl_jahre_jahr_vor_erstem_planjahr_besteht() -> None:
    texte = _text_mit("Es waren {{grundzahlen.999901.1.2023|mio}}.")
    pruefe_grundzahl_jahre(texte, _produkte_fuer_d02(), 2024)


def test_grundzahl_jahre_nicht_euro_besteht() -> None:
    texte = _text_mit("Es waren {{grundzahlen.999901.2.2025|zahl}}.")
    pruefe_grundzahl_jahre(texte, _produkte_fuer_d02(), 2024)


def test_grundzahl_jahre_andere_platzhalter_bleiben_unberuehrt() -> None:
    texte = _text_mit("Es waren {{vorbericht.steuerarten.gewerbesteuer.2024|mio}}.")
    pruefe_grundzahl_jahre(texte, _produkte_fuer_d02(), 2024)


# ---------------------------------------------------------------------------
# pruefe_text
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "text",
    [
        "{{meta.einwohner|zahl}} Menschen",
        "im Jahr 2026",
        "§ 4",
        "S. 311",
        "S. 24/25",
        "mehrere Seiten S. 27, S. 28",
        "{{abgeleitet.schluesselzuweisung_rueckgang_haushaltsjahr|mio}} weniger",
    ],
)
def test_pruefe_text_gueltig(text: str) -> None:
    pruefe_text(text)  # darf nicht werfen


@pytest.mark.parametrize(
    "text",
    [
        "rund 656 Euro",
        "{{x|unbekannt}}",
        "{{x|mio",
        "<b>fett</b>",
        "ein Text mit > Zeichen",
    ],
)
def test_pruefe_text_ungueltig(text: str) -> None:
    with pytest.raises(TexteFehler):
        pruefe_text(text)


def test_pruefe_text_fehlermeldung_nennt_ausschnitt() -> None:
    with pytest.raises(TexteFehler, match="656"):
        pruefe_text("rund 656 Euro mehr als geplant")


# ---------------------------------------------------------------------------
# textwerte / loese_auf (gegen die eingecheckten App-JSON-Dateien)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def app_daten() -> tuple[dict, dict, list[dict]]:
    haushalt = json.loads((APP_DATEN_WURZEL / "haushalt.json").read_text(encoding="utf-8"))
    investitionen = json.loads(
        (APP_DATEN_WURZEL / "investitionen.json").read_text(encoding="utf-8")
    )
    produkte = json.loads((APP_DATEN_WURZEL / "produkte.json").read_text(encoding="utf-8"))
    return haushalt, investitionen, produkte


@pytest.fixture(scope="module")
def werte(app_daten: tuple[dict, dict, list[dict]]) -> dict[str, int | float]:
    haushalt, investitionen, produkte = app_daten
    return textwerte(haushalt, investitionen, produkte)


def test_textwerte_enthaelt_erwartete_schluessel(
    app_daten: tuple[dict, dict, list[dict]], werte: dict[str, int | float]
) -> None:
    haushalt, _investitionen, _produkte = app_daten
    haushaltsjahr = haushalt["haushaltsjahr"]
    vorjahr = haushaltsjahr - 1

    assert f"vorbericht.zuwendungen.schluesselzuweisung.{haushaltsjahr}" in werte
    assert f"gep.jahresergebnis.{haushaltsjahr}" in werte
    assert "meta.einwohner" in werte
    assert f"schulden.pro_kopf.{vorjahr}" in werte
    assert "ve.gesamt" in werte
    for name in ABGELEITET:
        assert f"abgeleitet.{name}" in werte


def _ohne_folgejahr_ausgleichsruecklage(haushalt: dict) -> dict:
    """Kopie von `haushalt`, in der die Ausgleichsrücklage des Folgejahrs fehlt (WR-06)."""
    kopie = copy.deepcopy(haushalt)
    folgejahr_index = kopie["jahre"].index(kopie["haushaltsjahr"] + 1)
    for posten in kopie["eigenkapital"]["posten"]:
        if posten["posten"] == "ausgleichsruecklage":
            posten["werte"][folgejahr_index] = None
    return kopie


def test_textwerte_fehlender_formeleingang_ist_texte_fehler_kein_key_error(
    app_daten: tuple[dict, dict, list[dict]],
) -> None:
    haushalt, investitionen, produkte = app_daten
    with pytest.raises(TexteFehler, match="ausgleichsruecklage_minderung_haushaltsjahr"):
        textwerte(_ohne_folgejahr_ausgleichsruecklage(haushalt), investitionen, produkte)


def test_textwerte_wertet_nur_verwendete_formeln_aus(
    app_daten: tuple[dict, dict, list[dict]],
) -> None:
    haushalt, investitionen, produkte = app_daten
    kaputt = _ohne_folgejahr_ausgleichsruecklage(haushalt)
    ohne_formel = Erklaertext("a", "A", (1,), ("Einwohner: {{meta.einwohner|zahl}}.",))
    werte = textwerte(kaputt, investitionen, produkte, texte=[ohne_formel])
    assert "abgeleitet.ausgleichsruecklage_minderung_haushaltsjahr" not in werte
    mit_formel = Erklaertext(
        "b",
        "B",
        (1,),
        ("Minderung: {{abgeleitet.ausgleichsruecklage_minderung_haushaltsjahr|euro}}.",),
    )
    with pytest.raises(TexteFehler, match="ausgleichsruecklage_minderung_haushaltsjahr"):
        textwerte(kaputt, investitionen, produkte, texte=[mit_formel])


def test_textwerte_vorjahr_schluesselzuweisung_groesser_als_haushaltsjahr(
    app_daten: tuple[dict, dict, list[dict]], werte: dict[str, int | float]
) -> None:
    """Prüft D-15-Beispiel: die Schlüsselzuweisung bricht im Haushaltsjahr ein."""
    haushalt, _investitionen, _produkte = app_daten
    haushaltsjahr = haushalt["haushaltsjahr"]
    vorjahr = haushaltsjahr - 1
    vorjahr_wert = werte[f"vorbericht.zuwendungen.schluesselzuweisung.{vorjahr}"]
    haushaltsjahr_wert = werte[f"vorbericht.zuwendungen.schluesselzuweisung.{haushaltsjahr}"]
    assert vorjahr_wert > haushaltsjahr_wert
    assert werte["abgeleitet.schluesselzuweisung_rueckgang_haushaltsjahr"] == (
        vorjahr_wert - haushaltsjahr_wert
    )


# ---------------------------------------------------------------------------
# Phase 6 (Plan 06-04): Polster- und Schuldenformeln (D-14, D-09, D-20)
# ---------------------------------------------------------------------------


def _eigenkapital_reihe(haushalt: dict, posten: str) -> list[int | float]:
    for eintrag in haushalt["eigenkapital"]["posten"]:
        if eintrag["posten"] == posten:
            return eintrag["werte"]
    raise AssertionError(f"Eigenkapitalposten {posten!r} fehlt")


def test_textwerte_enthaelt_letztes_jahr(
    app_daten: tuple[dict, dict, list[dict]], werte: dict[str, int | float]
) -> None:
    haushalt, _investitionen, _produkte = app_daten
    assert werte["jahr.letztes_jahr"] == haushalt["jahre"][-1]


def test_ausgleichsruecklage_aufgebraucht_ohne_nullspalte_ist_texte_fehler(
    app_daten: tuple[dict, dict, list[dict]],
) -> None:
    haushalt, investitionen, produkte = app_daten
    kopie = copy.deepcopy(haushalt)
    for posten in kopie["eigenkapital"]["posten"]:
        if posten["posten"] == "ausgleichsruecklage":
            posten["werte"] = [1] * len(posten["werte"])
    with pytest.raises(TexteFehler, match="ausgleichsruecklage_aufgebraucht_jahr"):
        textwerte(kopie, investitionen, produkte)


def test_ausgleichsruecklage_aufgebraucht_jahr_ist_jahr_vor_erster_nullspalte(
    app_daten: tuple[dict, dict, list[dict]], werte: dict[str, int | float]
) -> None:
    """S. 311 nennt Anfangsbestände: die erste Nullspalte nach dem Haushaltsjahr ist der
    Stand zu Beginn des Folgejahrs, aufgebraucht ist die Rücklage also am Ende des Jahres
    davor."""
    haushalt, _investitionen, _produkte = app_daten
    reihe = _eigenkapital_reihe(haushalt, "ausgleichsruecklage")
    jahre = haushalt["jahre"]
    erste_nullspalte = next(
        jahr for jahr, wert in zip(jahre, reihe, strict=True) if jahr > jahre[0] and wert == 0
    )
    assert erste_nullspalte > haushalt["haushaltsjahr"]
    assert werte["abgeleitet.ausgleichsruecklage_aufgebraucht_jahr"] == erste_nullspalte - 1


def test_allgemeine_ruecklage_ende_letztes_jahr_gleich_gedruckter_gesamtsumme(
    app_daten: tuple[dict, dict, list[dict]], werte: dict[str, int | float]
) -> None:
    """Gegenprobe gegen S. 311: ist die Ausgleichsrücklage im letzten Jahr 0, ist das
    Eigenkapital des letzten Jahres (gedruckte Summe) die allgemeine Rücklage nach Abbau."""
    haushalt, _investitionen, _produkte = app_daten
    assert _eigenkapital_reihe(haushalt, "ausgleichsruecklage")[-1] == 0
    gedruckt = haushalt["eigenkapital"]["gesamt_vorbericht"]["werte"][-1]
    assert werte["abgeleitet.allgemeine_ruecklage_ende_letztes_jahr"] == gedruckt


def test_allgemeine_ruecklage_rueckgang_ist_relativ_zum_haushaltsjahr(
    app_daten: tuple[dict, dict, list[dict]], werte: dict[str, int | float]
) -> None:
    haushalt, _investitionen, _produkte = app_daten
    jahre = haushalt["jahre"]
    ruecklage = _eigenkapital_reihe(haushalt, "allgemeine_ruecklage")
    anfang = ruecklage[jahre.index(haushalt["haushaltsjahr"])]
    ende = werte["abgeleitet.allgemeine_ruecklage_ende_letztes_jahr"]
    erwartet = (anfang - ende) / anfang * 100
    assert werte["abgeleitet.allgemeine_ruecklage_rueckgang_bis_letztes_jahr"] == pytest.approx(
        erwartet
    )
    assert 0 < erwartet < 100


def test_schulden_formeln_kreditaufnahme_minus_tilgung_ist_anstieg_der_investitionskredite(
    app_daten: tuple[dict, dict, list[dict]], werte: dict[str, int | float]
) -> None:
    haushalt, _investitionen, _produkte = app_daten
    vorjahr = haushalt["haushaltsjahr"] - 1
    letztes = haushalt["jahre"][-1]
    anstieg = (
        werte[f"schulden.investitionskredite.{letztes}"]
        - werte[f"schulden.investitionskredite.{vorjahr}"]
    )
    kredit = werte["abgeleitet.kreditaufnahme_ab_haushaltsjahr"]
    tilgung = werte["abgeleitet.tilgung_ab_haushaltsjahr"]
    assert anstieg == kredit - tilgung
    assert werte["abgeleitet.schulden_gesamt_vorjahr"] == werte[f"schulden.gesamt.{vorjahr}"]
    assert werte["abgeleitet.schulden_gesamt_letztes_jahr"] == werte[f"schulden.gesamt.{letztes}"]


def test_phase6_formeln_auf_den_echten_daten_2026(
    app_daten: tuple[dict, dict, list[dict]], werte: dict[str, int | float]
) -> None:
    """Gedruckte Eckwerte des Haushalts 2026 (S. 23, S. 310, S. 311, GFP Z. 33/35)."""
    haushalt, _investitionen, _produkte = app_daten
    if haushalt["haushaltsjahr"] != 2026:
        pytest.skip("Eckwerte gelten nur für den Haushalt 2026")
    assert werte["abgeleitet.ausgleichsruecklage_aufgebraucht_jahr"] == 2026
    assert werte["abgeleitet.allgemeine_ruecklage_ende_letztes_jahr"] == 31866316
    assert round(werte["abgeleitet.allgemeine_ruecklage_rueckgang_bis_letztes_jahr"], 2) == 19.37
    assert werte["abgeleitet.schulden_gesamt_vorjahr"] == 7710000
    assert werte["abgeleitet.schulden_gesamt_letztes_jahr"] == 19625000
    assert werte["abgeleitet.kreditaufnahme_ab_haushaltsjahr"] == 14700000
    assert werte["abgeleitet.tilgung_ab_haushaltsjahr"] == 2700000


def test_loese_auf_gibt_verwendete_schluessel_zurueck(
    werte: dict[str, int | float],
) -> None:
    texte = [
        Erklaertext(
            schluessel="test",
            titel="Test",
            quelle_seiten=(1,),
            absaetze=("{{meta.einwohner|zahl}} Menschen und {{ve.gesamt|mio}} VE.",),
        )
    ]
    aufgeloest = loese_auf(texte, werte)
    assert set(aufgeloest) == {"meta.einwohner", "ve.gesamt"}
    assert aufgeloest["meta.einwohner"] == (werte["meta.einwohner"], "zahl")
    assert aufgeloest["ve.gesamt"] == (werte["ve.gesamt"], "mio")


def test_loese_auf_unbekannter_schluessel_bricht_ab(werte: dict[str, int | float]) -> None:
    texte = [
        Erklaertext(
            schluessel="test",
            titel="Test",
            quelle_seiten=(1,),
            absaetze=("{{nicht.vorhanden|euro}} fehlt.",),
        )
    ]
    with pytest.raises(TexteFehler, match="nicht.vorhanden"):
        loese_auf(texte, werte)


def test_vorschau_annotiert_platzhalter_mit_rohwert(werte: dict[str, int | float]) -> None:
    texte = [
        Erklaertext(
            schluessel="test",
            titel="Test",
            quelle_seiten=(1,),
            absaetze=("{{meta.einwohner|zahl}} Menschen.",),
        )
    ]
    ausgabe = vorschau(texte, werte)
    einwohner = werte["meta.einwohner"]
    assert f"{{{{meta.einwohner|zahl}}}}[{einwohner}]" in ausgabe
    assert "## test" in ausgabe


def test_texte_py_validiert_sich_selbst_gegen_echte_daten(
    tmp_path: Path,
    app_daten: tuple[dict, dict, list[dict]],
    werte: dict[str, int | float],
) -> None:
    """Spiegelt die Task-1-Verify-Zeile: lies_erklaerungen/pruefe_text/loese_auf auf
    einer synthetischen Mini-Datei, die ausschließlich echte textwerte-Schlüssel nutzt."""
    haushalt, _investitionen, _produkte = app_daten
    haushaltsjahr = haushalt["haushaltsjahr"]
    inhalt = f"""# Erklärtexte

## selbsttest
Titel: Selbsttest
Quelle: S. 1

Im Haushaltsjahr {{{{jahr.haushaltsjahr|jahr}}}} plant Ostbevern mit einem Jahresergebnis
von {{{{gep.jahresergebnis.{haushaltsjahr}|euro}}}}.
"""
    pfad = _schreibe(tmp_path, inhalt)
    texte = lies_erklaerungen(pfad)
    for text in texte:
        for absatz in text.absaetze:
            pruefe_text(absatz)
    aufgeloest = loese_auf(texte, werte)
    assert "gep.jahresergebnis." + str(haushaltsjahr) in aufgeloest


# ---------------------------------------------------------------------------
# Echte Datei: daten/manuell/texte/erklaerungen.md (D-16, D-17)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def echte_erklaerungen() -> list[Erklaertext]:
    return lies_erklaerungen(DATEN_WURZEL / ERKLAERUNGEN_MD)


def test_erklaerungen_umfang_d16(echte_erklaerungen: list[Erklaertext]) -> None:
    assert {text.schluessel for text in echte_erklaerungen} >= _ERKLAERUNGEN_SCHLUESSEL


def test_erklaerungen_keine_nackten_ziffern(echte_erklaerungen: list[Erklaertext]) -> None:
    for text in echte_erklaerungen:
        for absatz in text.absaetze:
            pruefe_text(absatz)  # darf nicht werfen


def test_erklaerungen_alle_schluessel_existieren(
    echte_erklaerungen: list[Erklaertext], werte: dict[str, int | float]
) -> None:
    loese_auf(echte_erklaerungen, werte)  # darf nicht werfen


def test_erklaerungen_jeder_text_hat_quelle(echte_erklaerungen: list[Erklaertext]) -> None:
    jahrgang = lade_jahrgang(STANDARD_JAHR)
    for text in echte_erklaerungen:
        assert text.quelle_seiten
        for seite in text.quelle_seiten:
            assert 1 <= seite <= jahrgang.anzahlen.pdf_seiten


def test_jahrneutrale_erklaerungen_ohne_platzhalter(
    echte_erklaerungen: list[Erklaertext],
) -> None:
    """Pitfall 6: die sieben neuen Texte gelten für jedes wählbare Jahr, enthalten also
    keinen Platzhalter (und damit keinen Wert, der nur für ein Jahr stimmt)."""
    je_schluessel = {text.schluessel: text for text in echte_erklaerungen}
    for schluessel in _JAHRNEUTRAL_SCHLUESSEL:
        for absatz in je_schluessel[schluessel].absaetze:
            assert "{{" not in absatz, f"{schluessel}: Platzhalter in jahrneutralem Text"


def test_phase6_texte_ohne_platzhalter(echte_erklaerungen: list[Erklaertext]) -> None:
    """bindungsgrad_selbstauskunft und ueberschuss_produkte gelten für jedes Jahr."""
    je_schluessel = {text.schluessel: text for text in echte_erklaerungen}
    for schluessel in _PHASE6_JAHRNEUTRAL:
        for absatz in je_schluessel[schluessel].absaetze:
            assert "{{" not in absatz, f"{schluessel}: Platzhalter in jahrneutralem Text"


def test_polster_ohne_rechtliche_bewertung(echte_erklaerungen: list[Erklaertext]) -> None:
    """D-14: Der Polster-Text nennt keine eigene Verpflichtung, keine Drohung und keine
    Prognose; jede Jahreszahl darin ist ein Platzhalter."""
    je_schluessel = {text.schluessel: text for text in echte_erklaerungen}
    absaetze = je_schluessel["polster"].absaetze
    for wort in ("muss", "müssen", "droht", "drohen", "Prognose"):
        for absatz in absaetze:
            assert wort not in absatz, f"polster: Wort '{wort}' ist nicht zulässig (D-14)"
    for absatz in absaetze:
        ohne_platzhalter = re.sub(r"\{\{.*?\}\}", "", absatz)
        assert not re.search(r"\b(?:19|20)\d{2}\b", ohne_platzhalter), (
            "polster: Jahreszahl nicht als Platzhalter"
        )


def test_schulden_anstieg_richtung(werte: dict[str, int | float]) -> None:
    """UI-SPEC: Das Verb 'steigt' in schulden_anstieg folgt den Daten. Fällt der Schuldenstand,
    muss der Text neu formuliert werden."""
    assert (
        werte["abgeleitet.schulden_gesamt_letztes_jahr"]
        > werte["abgeleitet.schulden_gesamt_vorjahr"]
    )


def test_d02_keine_euro_grundzahl_ab_erstem_planjahr(
    echte_erklaerungen: list[Erklaertext],
    echtes_glossar: list[Erklaertext],
    app_daten: tuple[dict, dict, list[dict]],
) -> None:
    """D-02: Text und Steuer-Zeitreihe nutzen für dasselbe Jahr dieselbe Quelle -- kein
    Euro-Grundzahl-Platzhalter für ein Jahr ab dem ersten Planjahr (D-01)."""
    haushalt, _investitionen, produkte = app_daten
    pruefe_grundzahl_jahre(echte_erklaerungen + echtes_glossar, produkte, haushalt["jahre"][0])


# ---------------------------------------------------------------------------
# Echte Datei: daten/manuell/texte/glossar.md (D-14, D-16, GLOS-01)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def echtes_glossar() -> list[Erklaertext]:
    return lies_glossar(DATEN_WURZEL / GLOSSAR_MD)


def test_glossar_pflichtbegriffe(echtes_glossar: list[Erklaertext]) -> None:
    """GLOS-01 (Probe, explizit aufgelöst): alle 22 Pflichtschlüssel sind da, kein Schlüssel
    kommt doppelt vor."""
    schluessel = [text.schluessel for text in echtes_glossar]
    assert len(schluessel) == len(set(schluessel)), "doppelter Glossarschlüssel"
    fehlend = _GLOSSAR_PFLICHT - set(schluessel)
    assert not fehlend, f"Pflichtbegriffe fehlen: {sorted(fehlend)}"


def test_glossar_phase6_begriffe(echtes_glossar: list[Erklaertext]) -> None:
    """D-17, D-18: drei neue Begriffe, jahrneutral und ohne Platzhalter."""
    je_schluessel = {text.schluessel: text for text in echtes_glossar}
    fehlend = _PHASE6_GLOSSAR - set(je_schluessel)
    assert not fehlend, f"Phase-6-Glossarbegriffe fehlen: {sorted(fehlend)}"
    for schluessel in _PHASE6_GLOSSAR:
        for absatz in je_schluessel[schluessel].absaetze:
            assert "{{" not in absatz, f"{schluessel}: Platzhalter in Glossarbegriff"


def test_glossar_keine_nackten_ziffern(echtes_glossar: list[Erklaertext]) -> None:
    for text in echtes_glossar:
        for absatz in text.absaetze:
            pruefe_text(absatz)  # darf nicht werfen (Ziffernregel, HTML-Verbot)


def test_glossar_alle_schluessel_existieren(
    echtes_glossar: list[Erklaertext], werte: dict[str, int | float]
) -> None:
    loese_auf(echtes_glossar, werte)  # darf nicht werfen


def test_glossar_quelle_bei_platzhalter(echtes_glossar: list[Erklaertext]) -> None:
    jahrgang = lade_jahrgang(STANDARD_JAHR)
    for text in echtes_glossar:
        if any("{{" in absatz for absatz in text.absaetze):
            assert text.quelle_seiten, f"{text.schluessel}: Platzhalter ohne Quelle"
        for seite in text.quelle_seiten:
            assert 1 <= seite <= jahrgang.anzahlen.pdf_seiten


def test_glossar_erster_satz_ohne_platzhalter(echtes_glossar: list[Erklaertext]) -> None:
    """D-16: der erste Absatz steht allein als Tooltip und enthält nie einen Platzhalter."""
    for text in echtes_glossar:
        assert "{{" not in text.absaetze[0], f"{text.schluessel}: Platzhalter im Tooltip-Text"
        assert text.titel


# ---------------------------------------------------------------------------
# Vertrag mit app/src/charts/format.ts (D-15)
# ---------------------------------------------------------------------------

_FORMAT_TS_MUSTER = re.compile(r"export type FormatKuerzel = ([^\n]+)")


def test_formatkuerzel_wie_format_ts() -> None:
    inhalt = (PROJEKT_WURZEL / "app" / "src" / "charts" / "format.ts").read_text(encoding="utf-8")
    treffer = _FORMAT_TS_MUSTER.search(inhalt)
    assert treffer is not None, "format.ts: FormatKuerzel-Union nicht gefunden"
    kuerzel_ts = tuple(re.findall(r"'([a-z]+)'", treffer.group(1)))
    assert kuerzel_ts == FORMATKUERZEL
    assert "export function formatiere" in inhalt


# ---------------------------------------------------------------------------
# Phase 7 / Plan 02 (D-20): Restpunkte der Phase-4-Review (WR-03, WR-05)
# ---------------------------------------------------------------------------


class _ZugriffsProtokoll(dict):
    """Werte-Dict, das alle gelesenen Schlüssel festhält."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)  # type: ignore[arg-type]
        self.gelesen: list[str] = []

    def __getitem__(self, schluessel: str) -> int | float:
        self.gelesen.append(schluessel)
        return super().__getitem__(schluessel)


def _formel_und_eingabeschluessel(werte: dict[str, int | float]) -> list[tuple[str, str]]:
    paare: list[tuple[str, str]] = []
    for name, formel in ABGELEITET.items():
        protokoll = _ZugriffsProtokoll(werte)
        formel(protokoll)
        paare.extend((name, schluessel) for schluessel in dict.fromkeys(protokoll.gelesen))
    return paare


def test_abgeleitete_formel_ohne_eingabewert_nennt_formel_und_schluessel(
    werte: dict[str, int | float],
) -> None:
    paare = _formel_und_eingabeschluessel(werte)
    assert any(schluessel.startswith("jahr.") for _name, schluessel in paare)
    for name, schluessel in paare:
        ohne = {k: v for k, v in werte.items() if k != schluessel}
        with pytest.raises(TexteFehler) as fehler:
            ABGELEITET[name](ohne)
        assert name in str(fehler.value)
        assert schluessel in str(fehler.value)


def test_pruefe_text_jahr_platzhalter_braucht_formatkuerzel_jahr() -> None:
    pruefe_text("Haushalt {{jahr.haushaltsjahr|jahr}}.")
    with pytest.raises(TexteFehler, match=r"jahr\.haushaltsjahr"):
        pruefe_text("Haushalt {{jahr.haushaltsjahr|zahl}}.")
