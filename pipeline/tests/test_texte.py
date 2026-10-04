"""Tests für ostbevern.texte: Platzhalter-Vertrag der Erklärtexte (D-15, D-16, MANU-08).

`lies_erklaerungen`/`pruefe_text` werden gegen synthetische Dateien in `tmp_path`
getestet (keine Jahrgangswerte im Test, synthetische Schlüssel). `textwerte`/
`loese_auf` werden gegen die eingecheckten App-JSON-Dateien getestet (`app/src/data/`),
die Jahre kommen aus `haushalt.json` selbst (`haushaltsjahr`/`jahre`), nie als Literal.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from ostbevern.konfiguration import PROJEKT_WURZEL, STANDARD_JAHR, lade_jahrgang
from ostbevern.schema import DATEN_WURZEL, ERKLAERUNGEN_MD
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
_D16_SCHLUESSEL = {
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

Im Haushaltsjahr {{{{jahr.haushaltsjahr|zahl}}}} plant Ostbevern mit einem Jahresergebnis
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
    assert {text.schluessel for text in echte_erklaerungen} == _D16_SCHLUESSEL


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
