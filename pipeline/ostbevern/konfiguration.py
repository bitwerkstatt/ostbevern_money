"""Lädt die Jahrgangskonfiguration (D-06 bis D-09) aus `pipeline/jahrgaenge/*.toml`.

Jede PDF-spezifische Angabe (Haushaltsjahr, PDF-Pfad, Spaltenköpfe, Seitenbereiche,
Kopfzeilen-Muster, erwartete Anzahlen, Sollwerte) steht ausschließlich in den
Jahrgangs- bzw. Sollwertdateien, nie im Code. Dieses Modul ist die einzige Stelle,
die `tomllib` importiert.
"""

from __future__ import annotations

import itertools
import re
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Der Standardjahrgang steht an genau dieser einen Stelle im Code (D-09).
STANDARD_JAHR = 2026

PIPELINE_WURZEL = Path(__file__).resolve().parent.parent
PROJEKT_WURZEL = PIPELINE_WURZEL.parent
JAHRGAENGE_VERZEICHNIS = PIPELINE_WURZEL / "jahrgaenge"

# Strukturelle Pipeline-Konzepte (keine Jahrgangsdaten): Plantypen und die
# Kapitel, die jede Jahrgangsdatei mindestens enthalten muss.
PFLICHT_PLANTYPEN = ("ergebnisplan", "finanzplan", "investitionen")
PFLICHT_SEITENBEREICHE = (
    "inhaltsverzeichnis",
    "haushaltssatzung",
    "vorbericht",
    "gesamtergebnisplan",
    "gesamtfinanzplan",
    "teilplaene",
    "stellenplan",
    "querschnitte",
    "verpflichtungen_schulden",
)
# Feines Typ-Vokabular im Teilplanbereich (D-17), das jede Jahrgangsdatei unter
# [kopfzeilen.seitentypen] mit einem Muster belegen muss.
PFLICHT_SEITENTYPEN = (
    "produktinformationen",
    "grundzahlen",
    "teilergebnisplan",
    "erlaeuterungen",
    "teilfinanzplan",
    "investitionen",
)

# Vierstelliger Code: sowohl Schlüssel von [synthetische_produktgruppen] (Jahrgangsdatei,
# D-14) als auch von [haushaltsquerschnitt_pg] (Sollwertdatei).
_VIERSTELLIGER_CODE_MUSTER = re.compile(r"^\d{4}$")
_SECHSSTELLIGER_PRODUKTCODE_MUSTER = re.compile(r"^\d{6}$")
_SYNTHETISCHE_PG_PFLICHTFELDER = frozenset({"produkt", "name", "pdf_seite"})


class KonfigurationsFehler(ValueError):
    """Wird ausgelöst, wenn eine Jahrgangs- oder Sollwertdatei fehlt oder unvollständig ist."""


@dataclass(frozen=True)
class Seitenbereich:
    """PDF-Seitenbereich eines Kapitels (1-basiert, inklusive)."""

    von: int
    bis: int


@dataclass(frozen=True)
class Kopfzeilen:
    """Kopfzeilen-Muster für die Seitenklassifikation (Spez. 5.3)."""

    produktbereich: str
    produktgruppe: str
    produkt: str
    seitentypen: Mapping[str, str]
    fortsetzung: str


@dataclass(frozen=True)
class Anzahlen:
    """Erwartete Anzahlen aus der Jahrgangsdatei (D-07)."""

    pdf_seiten: int
    produktbereiche: int
    produkte: int


@dataclass(frozen=True)
class SynthetischeProduktgruppe:
    """Deklarierte Ausnahme vom D-14-Standard (Code = erste vier Ziffern des
    Produktcodes): ordnet ein einzelnes Produkt einer synthetischen PG mit
    abweichendem Code und/oder Namen zu, belegt durch `pdf_seite` (Spez. Anhang,
    hier der Haushaltsquerschnitt). `code` ist der TOML-Tabellenschlüssel."""

    code: str
    produkt: str
    name: str
    pdf_seite: int


@dataclass(frozen=True)
class Jahrgang:
    """Alle PDF-spezifischen Werte eines Haushaltsjahrgangs (D-07)."""

    haushaltsjahr: int
    pdf_pfad: Path
    anzahlen: Anzahlen
    spalten: Mapping[str, tuple[str, ...]]
    seitenbereiche: Mapping[str, Seitenbereich]
    kopfzeilen: Kopfzeilen
    synthetische_produktgruppen: Mapping[str, SynthetischeProduktgruppe]
    # Generische [layout.*]-Tabellen der Detailseiten (Phase 3): gedruckte Texte und
    # Regex-Muster, die gegen Textzeile.text geprüft werden, sofern nicht anders
    # angegeben. Optional, Standard ist eine leere Zuordnung (D-07-Stil).
    layout: Mapping[str, Mapping[str, str | tuple[str, ...]]] = field(default_factory=dict)


def lade_jahrgang(jahr: int, *, verzeichnis: Path = JAHRGAENGE_VERZEICHNIS) -> Jahrgang:
    """Lädt die Jahrgangsdatei `{jahr}.toml` und validiert sie vollständig (D-07, D-12)."""
    pfad = verzeichnis / f"{jahr}.toml"
    if not pfad.is_file():
        raise KonfigurationsFehler(f"Jahrgangsdatei nicht gefunden: {pfad}")

    with pfad.open("rb") as datei:
        rohdaten = tomllib.load(datei)

    fehlende_schluessel: list[str] = []
    for schluessel in (
        "haushaltsjahr",
        "pdf_pfad",
        "anzahlen",
        "spalten",
        "seitenbereiche",
        "kopfzeilen",
    ):
        if schluessel not in rohdaten:
            fehlende_schluessel.append(schluessel)

    anzahlen_rohdaten = rohdaten.get("anzahlen", {})
    for teil_schluessel in ("pdf_seiten", "produktbereiche", "produkte"):
        if teil_schluessel not in anzahlen_rohdaten:
            fehlende_schluessel.append(f"anzahlen.{teil_schluessel}")

    kopfzeilen_rohdaten = rohdaten.get("kopfzeilen", {})
    for teil_schluessel in (
        "produktbereich",
        "produktgruppe",
        "produkt",
        "seitentypen",
        "fortsetzung",
    ):
        if teil_schluessel not in kopfzeilen_rohdaten:
            fehlende_schluessel.append(f"kopfzeilen.{teil_schluessel}")

    if fehlende_schluessel:
        raise KonfigurationsFehler(
            f"Jahrgangsdatei {pfad} fehlen Schlüssel: {', '.join(fehlende_schluessel)}"
        )

    if rohdaten["haushaltsjahr"] != jahr:
        raise KonfigurationsFehler(
            f"Jahrgangsdatei {pfad} hat Haushaltsjahr {rohdaten['haushaltsjahr']}, erwartet {jahr}"
        )

    for teil_schluessel in ("pdf_seiten", "produktbereiche", "produkte"):
        wert = anzahlen_rohdaten[teil_schluessel]
        if not isinstance(wert, int) or isinstance(wert, bool):
            raise KonfigurationsFehler(
                f"Jahrgangsdatei {pfad}: anzahlen.{teil_schluessel} muss eine Ganzzahl "
                f"sein, nicht {wert!r}"
            )

    pdf_pfad_roh = rohdaten["pdf_pfad"]
    pdf_pfad_relativ = Path(pdf_pfad_roh)
    if pdf_pfad_relativ.is_absolute():
        raise KonfigurationsFehler(
            f"Jahrgangsdatei {pfad}: pdf_pfad muss relativ sein, nicht absolut: {pdf_pfad_roh}"
        )
    pdf_pfad = (PROJEKT_WURZEL / pdf_pfad_relativ).resolve()
    if not pdf_pfad.is_relative_to(PROJEKT_WURZEL):
        raise KonfigurationsFehler(
            f"Jahrgangsdatei {pfad}: pdf_pfad liegt außerhalb des Projekts: {pdf_pfad_roh}"
        )

    anzahlen = Anzahlen(
        pdf_seiten=anzahlen_rohdaten["pdf_seiten"],
        produktbereiche=anzahlen_rohdaten["produktbereiche"],
        produkte=anzahlen_rohdaten["produkte"],
    )

    spalten_rohdaten = rohdaten["spalten"]
    spalten: dict[str, tuple[str, ...]] = {
        name: tuple(werte) for name, werte in spalten_rohdaten.items()
    }
    for plantyp in PFLICHT_PLANTYPEN:
        werte = spalten.get(plantyp)
        if not werte or not all(isinstance(w, str) for w in werte):
            raise KonfigurationsFehler(
                f"Jahrgangsdatei {pfad}: Spalten für Plantyp {plantyp!r} fehlen oder sind leer"
            )

    seitenbereiche_rohdaten = rohdaten["seitenbereiche"]
    seitenbereiche: dict[str, Seitenbereich] = {}
    for name, werte in seitenbereiche_rohdaten.items():
        bereich = Seitenbereich(von=werte["von"], bis=werte["bis"])
        if not (1 <= bereich.von <= bereich.bis <= anzahlen.pdf_seiten):
            raise KonfigurationsFehler(
                f"Jahrgangsdatei {pfad}: Seitenbereich {name!r} ungültig "
                f"(von={bereich.von}, bis={bereich.bis}, pdf_seiten={anzahlen.pdf_seiten})"
            )
        seitenbereiche[name] = bereich

    for (name_a, bereich_a), (name_b, bereich_b) in itertools.combinations(
        seitenbereiche.items(), 2
    ):
        if bereich_a.von <= bereich_b.bis and bereich_b.von <= bereich_a.bis:
            raise KonfigurationsFehler(
                f"Jahrgangsdatei {pfad}: Seitenbereiche {name_a!r} und {name_b!r} überlappen "
                f"(von={bereich_a.von}, bis={bereich_a.bis} / von={bereich_b.von}, "
                f"bis={bereich_b.bis})"
            )

    fehlende_seitenbereiche = [
        name for name in PFLICHT_SEITENBEREICHE if name not in seitenbereiche
    ]
    if fehlende_seitenbereiche:
        raise KonfigurationsFehler(
            f"Jahrgangsdatei {pfad} fehlen Seitenbereiche: {', '.join(fehlende_seitenbereiche)}"
        )

    seitentypen_rohdaten = kopfzeilen_rohdaten["seitentypen"]
    if not isinstance(seitentypen_rohdaten, dict):
        raise KonfigurationsFehler(
            f"Jahrgangsdatei {pfad}: kopfzeilen.seitentypen muss eine Tabelle sein, "
            f"nicht {seitentypen_rohdaten!r}"
        )
    fehlende_seitentypen = [
        name for name in PFLICHT_SEITENTYPEN if name not in seitentypen_rohdaten
    ]
    if fehlende_seitentypen:
        raise KonfigurationsFehler(
            f"Jahrgangsdatei {pfad}: kopfzeilen.seitentypen fehlen Schlüssel: "
            f"{', '.join(fehlende_seitentypen)}"
        )
    for name, muster in seitentypen_rohdaten.items():
        if not isinstance(muster, str):
            raise KonfigurationsFehler(
                f"Jahrgangsdatei {pfad}: kopfzeilen.seitentypen.{name} muss ein String "
                f"sein, nicht {muster!r}"
            )

    kopfzeilen = Kopfzeilen(
        produktbereich=kopfzeilen_rohdaten["produktbereich"],
        produktgruppe=kopfzeilen_rohdaten["produktgruppe"],
        produkt=kopfzeilen_rohdaten["produkt"],
        seitentypen=dict(seitentypen_rohdaten),
        fortsetzung=kopfzeilen_rohdaten["fortsetzung"],
    )
    for muster_name, muster in (
        ("kopfzeilen.produktbereich", kopfzeilen.produktbereich),
        ("kopfzeilen.produktgruppe", kopfzeilen.produktgruppe),
        ("kopfzeilen.produkt", kopfzeilen.produkt),
        *(
            (f"kopfzeilen.seitentypen.{name}", teilmuster)
            for name, teilmuster in kopfzeilen.seitentypen.items()
        ),
    ):
        try:
            re.compile(muster)
        except re.error as fehler:
            raise KonfigurationsFehler(
                f"Jahrgangsdatei {pfad}: {muster_name} ist kein gültiger regulärer "
                f"Ausdruck: {fehler}"
            ) from fehler

    # Synthetische Produktgruppen (D-14): optionale Tabelle, Standard ist eine leere
    # Zuordnung (jedes Produkt folgt dem Code-Präfix-Standard). Validiert Schlüssel-
    # und Feldmenge, Formate, PB-Präfix-Übereinstimmung, Seitenbereich und doppelte
    # Produkte (D-08); die semantische Prüfung gegen die extrahierte Hierarchie
    # (Produkt existiert, gehört nicht zu einer gedruckten PG, Code ist nicht
    # gedruckt) folgt in seiten.baue_hierarchie, wo die Hierarchie bekannt ist.
    synthetische_produktgruppen_rohdaten = rohdaten.get("synthetische_produktgruppen", {})
    if not isinstance(synthetische_produktgruppen_rohdaten, dict):
        raise KonfigurationsFehler(
            f"Jahrgangsdatei {pfad}: synthetische_produktgruppen muss eine Tabelle sein, "
            f"nicht {synthetische_produktgruppen_rohdaten!r}"
        )

    synthetische_produktgruppen: dict[str, SynthetischeProduktgruppe] = {}
    gesehene_produkte: dict[str, str] = {}
    for code, eintrag in synthetische_produktgruppen_rohdaten.items():
        if not _VIERSTELLIGER_CODE_MUSTER.match(code):
            raise KonfigurationsFehler(
                f"Jahrgangsdatei {pfad}: synthetische_produktgruppen hat keinen "
                f"vierstelligen Code: {code!r}"
            )
        if not isinstance(eintrag, dict):
            raise KonfigurationsFehler(
                f"Jahrgangsdatei {pfad}: synthetische_produktgruppen.{code} muss eine "
                f"Tabelle sein, nicht {eintrag!r}"
            )
        fehlende_felder = _SYNTHETISCHE_PG_PFLICHTFELDER - set(eintrag)
        if fehlende_felder:
            raise KonfigurationsFehler(
                f"Jahrgangsdatei {pfad}: synthetische_produktgruppen.{code} fehlen "
                f"Felder: {', '.join(sorted(fehlende_felder))}"
            )
        unbekannte_felder = set(eintrag) - _SYNTHETISCHE_PG_PFLICHTFELDER
        if unbekannte_felder:
            raise KonfigurationsFehler(
                f"Jahrgangsdatei {pfad}: synthetische_produktgruppen.{code} hat "
                f"unbekannte Felder: {', '.join(sorted(unbekannte_felder))}"
            )

        produkt = eintrag["produkt"]
        if not isinstance(produkt, str) or not _SECHSSTELLIGER_PRODUKTCODE_MUSTER.match(produkt):
            raise KonfigurationsFehler(
                f"Jahrgangsdatei {pfad}: synthetische_produktgruppen.{code}.produkt ist "
                f"kein sechsstelliger Produktcode: {produkt!r}"
            )
        if produkt[:2] != code[:2]:
            raise KonfigurationsFehler(
                f"Jahrgangsdatei {pfad}: synthetische_produktgruppen.{code}.produkt "
                f"{produkt!r} gehört nicht zum Produktbereich von {code!r}"
            )
        if produkt in gesehene_produkte:
            raise KonfigurationsFehler(
                f"Jahrgangsdatei {pfad}: synthetische_produktgruppen: Produkt "
                f"{produkt!r} ist sowohl unter {gesehene_produkte[produkt]!r} als auch "
                f"{code!r} deklariert"
            )
        gesehene_produkte[produkt] = code

        name = eintrag["name"]
        if not isinstance(name, str) or not name:
            raise KonfigurationsFehler(
                f"Jahrgangsdatei {pfad}: synthetische_produktgruppen.{code} hat keinen Namen"
            )

        pdf_seite = eintrag["pdf_seite"]
        if (
            not isinstance(pdf_seite, int)
            or isinstance(pdf_seite, bool)
            or not (1 <= pdf_seite <= anzahlen.pdf_seiten)
        ):
            raise KonfigurationsFehler(
                f"Jahrgangsdatei {pfad}: synthetische_produktgruppen.{code} hat keine "
                "gültige pdf_seite"
            )

        synthetische_produktgruppen[code] = SynthetischeProduktgruppe(
            code=code, produkt=produkt, name=name, pdf_seite=pdf_seite
        )

    # [layout.*] (Phase 3): generische Tabellen gedruckter Texte/Muster der Detailseiten.
    # Optional, Standard ist eine leere Zuordnung. Jeder Wert ist entweder ein nicht-
    # leerer String oder eine nicht-leere Liste paarweise verschiedener, nicht-leerer
    # Strings (als Tupel gespeichert); ein Schlüssel, der auf "_muster" endet, muss ein
    # einzelner String sein, der mit re.compile kompiliert.
    layout_rohdaten = rohdaten.get("layout", {})
    if not isinstance(layout_rohdaten, dict):
        raise KonfigurationsFehler(
            f"Jahrgangsdatei {pfad}: layout muss eine Tabelle sein, nicht {layout_rohdaten!r}"
        )
    layout: dict[str, dict[str, str | tuple[str, ...]]] = {}
    for bereich, eintraege in layout_rohdaten.items():
        if not isinstance(eintraege, dict):
            raise KonfigurationsFehler(
                f"Jahrgangsdatei {pfad}: layout.{bereich} muss eine Tabelle sein, "
                f"nicht {eintraege!r}"
            )
        bereich_werte: dict[str, str | tuple[str, ...]] = {}
        for schluessel, wert in eintraege.items():
            pfad_hinweis = f"layout.{bereich}.{schluessel}"
            if isinstance(wert, str):
                if not wert:
                    raise KonfigurationsFehler(
                        f"Jahrgangsdatei {pfad}: {pfad_hinweis} ist ein leerer String"
                    )
                bereich_werte[schluessel] = wert
            elif isinstance(wert, list):
                if not wert or not all(isinstance(w, str) and w for w in wert):
                    raise KonfigurationsFehler(
                        f"Jahrgangsdatei {pfad}: {pfad_hinweis} ist eine leere Liste oder "
                        "enthält leere bzw. nicht-String-Einträge"
                    )
                if len(set(wert)) != len(wert):
                    raise KonfigurationsFehler(
                        f"Jahrgangsdatei {pfad}: {pfad_hinweis} enthält doppelte Einträge"
                    )
                bereich_werte[schluessel] = tuple(wert)
            else:
                raise KonfigurationsFehler(
                    f"Jahrgangsdatei {pfad}: {pfad_hinweis} muss ein String oder eine "
                    f"Liste von Strings sein, nicht {wert!r}"
                )
            if schluessel.endswith("_muster"):
                muster_wert = bereich_werte[schluessel]
                if not isinstance(muster_wert, str):
                    raise KonfigurationsFehler(
                        f"Jahrgangsdatei {pfad}: {pfad_hinweis} muss für ein "
                        "'_muster'-Suffix ein einzelner String sein"
                    )
                try:
                    re.compile(muster_wert)
                except re.error as fehler:
                    raise KonfigurationsFehler(
                        f"Jahrgangsdatei {pfad}: {pfad_hinweis} ist kein gültiger "
                        f"regulärer Ausdruck: {fehler}"
                    ) from fehler
        layout[bereich] = bereich_werte

    return Jahrgang(
        haushaltsjahr=rohdaten["haushaltsjahr"],
        pdf_pfad=pdf_pfad,
        anzahlen=anzahlen,
        spalten=spalten,
        seitenbereiche=seitenbereiche,
        kopfzeilen=kopfzeilen,
        synthetische_produktgruppen=synthetische_produktgruppen,
        layout=layout,
    )


def layout_text(jahrgang: Jahrgang, bereich: str, schluessel: str) -> str:
    """Liest einen String aus `jahrgang.layout` (Phase 3); meldet Pfad statt KeyError."""
    wert = jahrgang.layout.get(bereich, {}).get(schluessel)
    if not isinstance(wert, str):
        raise KonfigurationsFehler(
            f"Jahrgangsdatei {jahrgang.haushaltsjahr}: layout.{bereich}.{schluessel} fehlt"
        )
    return wert


def layout_liste(jahrgang: Jahrgang, bereich: str, schluessel: str) -> tuple[str, ...]:
    """Liest eine String-Liste aus `jahrgang.layout` (Phase 3); meldet Pfad statt KeyError."""
    wert = jahrgang.layout.get(bereich, {}).get(schluessel)
    if not isinstance(wert, tuple):
        raise KonfigurationsFehler(
            f"Jahrgangsdatei {jahrgang.haushaltsjahr}: layout.{bereich}.{schluessel} fehlt"
        )
    return wert


def _pruefe_nur_ganzzahlen(wert: object, pfad_hinweis: str) -> None:
    """Rekursive Prüfung: jeder Zahlenwert in der Sollwertdatei ist int, nie float/bool."""
    if isinstance(wert, bool):
        raise KonfigurationsFehler(f"Sollwert {pfad_hinweis} darf kein Wahrheitswert sein")
    if isinstance(wert, float):
        raise KonfigurationsFehler(
            f"Sollwert {pfad_hinweis} ist keine Ganzzahl (int-Euro erwartet): {wert}"
        )
    if isinstance(wert, dict):
        for schluessel, teilwert in wert.items():
            _pruefe_nur_ganzzahlen(teilwert, f"{pfad_hinweis}.{schluessel}")
    elif isinstance(wert, list):
        for index, teilwert in enumerate(wert):
            _pruefe_nur_ganzzahlen(teilwert, f"{pfad_hinweis}[{index}]")


_ZWEISTELLIGE_ZEILE_MUSTER = re.compile(r"^\d{2}$")
_TEILERGEBNISPLAENE_PB_FELDER = frozenset(
    {"ordentliche_ertraege", "ordentliche_aufwendungen", "ergebnis_mit_internen_verrechnungen"}
)
_ANHANG_A_CODE_MUSTER = re.compile(r"^(\d{2}|\d{4}|\d{6})$")


def lade_sollwerte(jahr: int, *, verzeichnis: Path = JAHRGAENGE_VERZEICHNIS) -> dict[str, Any]:
    """Lädt die Sollwertdatei `{jahr}_sollwerte.toml` und validiert sie (D-08, D-12, D-18)."""
    pfad = verzeichnis / f"{jahr}_sollwerte.toml"
    if not pfad.is_file():
        raise KonfigurationsFehler(f"Sollwertdatei nicht gefunden: {pfad}")

    with pfad.open("rb") as datei:
        rohdaten = tomllib.load(datei)

    fehlende_schluessel = [
        schluessel
        for schluessel in (
            "haushaltsjahr",
            "satzung",
            "gesamtergebnisplan",
            "gesamtfinanzplan",
            "teilergebnisplaene_pb",
            "teilergebnisplaene_pb_summe",
            "anhang_a",
        )
        if schluessel not in rohdaten
    ]
    if fehlende_schluessel:
        raise KonfigurationsFehler(
            f"Sollwertdatei {pfad} fehlen Schlüssel: {', '.join(fehlende_schluessel)}"
        )

    if rohdaten["haushaltsjahr"] != jahr:
        raise KonfigurationsFehler(
            f"Sollwertdatei {pfad} hat Haushaltsjahr {rohdaten['haushaltsjahr']}, erwartet {jahr}"
        )

    gesamtergebnisplan = rohdaten["gesamtergebnisplan"]
    jahre = gesamtergebnisplan.get("jahre", [])
    for zeile, werte in gesamtergebnisplan.get("zeilen", {}).items():
        if len(werte) != len(jahre):
            raise KonfigurationsFehler(
                f"Sollwertdatei {pfad}: Zeile {zeile!r} hat {len(werte)} Werte, "
                f"erwartet {len(jahre)}"
            )

    gesamtfinanzplan = rohdaten["gesamtfinanzplan"]
    if "ansatz" not in gesamtfinanzplan:
        raise KonfigurationsFehler(f"Sollwertdatei {pfad}: gesamtfinanzplan.ansatz fehlt")
    for teiltabelle_name in ("ansatz", "ve"):
        for zeile in gesamtfinanzplan.get(teiltabelle_name, {}):
            if not _ZWEISTELLIGE_ZEILE_MUSTER.match(zeile):
                raise KonfigurationsFehler(
                    f"Sollwertdatei {pfad}: gesamtfinanzplan.{teiltabelle_name} hat keine "
                    f"zweistellige Zeilennummer: {zeile!r}"
                )

    teilergebnisplaene_pb = rohdaten["teilergebnisplaene_pb"]
    for pb_schluessel, eintrag in teilergebnisplaene_pb.items():
        if not _ZWEISTELLIGE_ZEILE_MUSTER.match(pb_schluessel):
            raise KonfigurationsFehler(
                f"Sollwertdatei {pfad}: teilergebnisplaene_pb hat keinen zweistelligen "
                f"PB-Schlüssel: {pb_schluessel!r}"
            )
        fehlende_felder = _TEILERGEBNISPLAENE_PB_FELDER - set(eintrag)
        if fehlende_felder:
            raise KonfigurationsFehler(
                f"Sollwertdatei {pfad}: teilergebnisplaene_pb.{pb_schluessel} fehlen Felder: "
                f"{', '.join(sorted(fehlende_felder))}"
            )

    teilergebnisplaene_pb_summe = rohdaten["teilergebnisplaene_pb_summe"]
    fehlende_summenfelder = [
        feld
        for feld in ("ordentliche_ertraege", "ordentliche_aufwendungen")
        if feld not in teilergebnisplaene_pb_summe
    ]
    if fehlende_summenfelder:
        raise KonfigurationsFehler(
            f"Sollwertdatei {pfad}: teilergebnisplaene_pb_summe fehlen Felder: "
            f"{', '.join(fehlende_summenfelder)}"
        )

    anhang_a = rohdaten["anhang_a"]
    for code, eintrag in anhang_a.items():
        if not _ANHANG_A_CODE_MUSTER.match(code):
            raise KonfigurationsFehler(
                f"Sollwertdatei {pfad}: anhang_a hat keinen 2-, 4- oder 6-stelligen Code: {code!r}"
            )
        name = eintrag.get("name")
        if not isinstance(name, str) or not name:
            raise KonfigurationsFehler(f"Sollwertdatei {pfad}: anhang_a.{code} hat keinen Namen")
        pdf_seite = eintrag.get("pdf_seite")
        if not isinstance(pdf_seite, int) or isinstance(pdf_seite, bool) or pdf_seite < 1:
            raise KonfigurationsFehler(
                f"Sollwertdatei {pfad}: anhang_a.{code} hat keine gültige pdf_seite"
            )

    # [haushaltsquerschnitt_pg] (D-14): optionale Sollwerte für den Haushaltsquerschnitt-
    # Abgleich einer synthetischen PG. Bewusst NICHT in den Pflichtschlüsseln oben und
    # nicht in Regel 4 verdrahtet (das ist Phase 3 Regel 7, PRUEF-07); Zahlenwerte prüft
    # bereits _pruefe_nur_ganzzahlen unten.
    haushaltsquerschnitt_pg = rohdaten.get("haushaltsquerschnitt_pg", {})
    if not isinstance(haushaltsquerschnitt_pg, dict):
        raise KonfigurationsFehler(
            f"Sollwertdatei {pfad}: haushaltsquerschnitt_pg muss eine Tabelle sein, "
            f"nicht {haushaltsquerschnitt_pg!r}"
        )
    for code, eintrag in haushaltsquerschnitt_pg.items():
        if not _VIERSTELLIGER_CODE_MUSTER.match(code):
            raise KonfigurationsFehler(
                f"Sollwertdatei {pfad}: haushaltsquerschnitt_pg hat keinen vierstelligen "
                f"Code: {code!r}"
            )
        if not isinstance(eintrag, dict):
            raise KonfigurationsFehler(
                f"Sollwertdatei {pfad}: haushaltsquerschnitt_pg.{code} muss eine Tabelle "
                f"sein, nicht {eintrag!r}"
            )
        if "ergebnis_mit_internen_verrechnungen" not in eintrag:
            raise KonfigurationsFehler(
                f"Sollwertdatei {pfad}: haushaltsquerschnitt_pg.{code} fehlt "
                "ergebnis_mit_internen_verrechnungen"
            )
        pdf_seite = eintrag.get("pdf_seite")
        if not isinstance(pdf_seite, int) or isinstance(pdf_seite, bool) or pdf_seite < 1:
            raise KonfigurationsFehler(
                f"Sollwertdatei {pfad}: haushaltsquerschnitt_pg.{code} hat keine gültige pdf_seite"
            )

    # [stichproben] (Phase 3, 03-04): optionale, PDF-geprüfte Testreferenzen (keine
    # Extraktions-Steuerung). Muss eine Tabelle von Tabellen sein (jede Stichprobe ist
    # selbst eine TOML-Tabelle, z. B. [stichproben.produktinfo]); Zahlenwerte prüft
    # bereits _pruefe_nur_ganzzahlen unten.
    stichproben = rohdaten.get("stichproben", {})
    if not isinstance(stichproben, dict):
        raise KonfigurationsFehler(
            f"Sollwertdatei {pfad}: stichproben muss eine Tabelle sein, nicht {stichproben!r}"
        )
    for name, eintrag in stichproben.items():
        if not isinstance(eintrag, dict):
            raise KonfigurationsFehler(
                f"Sollwertdatei {pfad}: stichproben.{name} muss eine Tabelle sein, "
                f"nicht {eintrag!r}"
            )

    _pruefe_nur_ganzzahlen(rohdaten, "sollwerte")

    return rohdaten
