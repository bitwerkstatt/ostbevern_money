"""Lädt die Jahrgangskonfiguration (D-06 bis D-09) aus `pipeline/jahrgaenge/*.toml`.

Jede PDF-spezifische Angabe (Haushaltsjahr, PDF-Pfad, Spaltenköpfe, Seitenbereiche,
Kopfzeilen-Muster, erwartete Anzahlen, Sollwerte) steht ausschließlich in den
Jahrgangs- bzw. Sollwertdateien, nie im Code. Dieses Modul ist die einzige Stelle,
die `tomllib` importiert.
"""

from __future__ import annotations

import re
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass
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
    produkt: str
    seitentypen: tuple[str, ...]
    fortsetzung: str


@dataclass(frozen=True)
class Anzahlen:
    """Erwartete Anzahlen aus der Jahrgangsdatei (D-07)."""

    pdf_seiten: int
    produktbereiche: int
    produkte: int


@dataclass(frozen=True)
class Jahrgang:
    """Alle PDF-spezifischen Werte eines Haushaltsjahrgangs (D-07)."""

    haushaltsjahr: int
    pdf_pfad: Path
    anzahlen: Anzahlen
    spalten: Mapping[str, tuple[str, ...]]
    seitenbereiche: Mapping[str, Seitenbereich]
    kopfzeilen: Kopfzeilen


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
    for teil_schluessel in ("produktbereich", "produkt", "seitentypen", "fortsetzung"):
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

    fehlende_seitenbereiche = [
        name for name in PFLICHT_SEITENBEREICHE if name not in seitenbereiche
    ]
    if fehlende_seitenbereiche:
        raise KonfigurationsFehler(
            f"Jahrgangsdatei {pfad} fehlen Seitenbereiche: {', '.join(fehlende_seitenbereiche)}"
        )

    kopfzeilen = Kopfzeilen(
        produktbereich=kopfzeilen_rohdaten["produktbereich"],
        produkt=kopfzeilen_rohdaten["produkt"],
        seitentypen=tuple(kopfzeilen_rohdaten["seitentypen"]),
        fortsetzung=kopfzeilen_rohdaten["fortsetzung"],
    )
    re.compile(kopfzeilen.produktbereich)
    re.compile(kopfzeilen.produkt)

    return Jahrgang(
        haushaltsjahr=rohdaten["haushaltsjahr"],
        pdf_pfad=pdf_pfad,
        anzahlen=anzahlen,
        spalten=spalten,
        seitenbereiche=seitenbereiche,
        kopfzeilen=kopfzeilen,
    )


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


def lade_sollwerte(jahr: int, *, verzeichnis: Path = JAHRGAENGE_VERZEICHNIS) -> dict[str, Any]:
    """Lädt die Sollwertdatei `{jahr}_sollwerte.toml` und validiert sie (D-08, D-12)."""
    pfad = verzeichnis / f"{jahr}_sollwerte.toml"
    if not pfad.is_file():
        raise KonfigurationsFehler(f"Sollwertdatei nicht gefunden: {pfad}")

    with pfad.open("rb") as datei:
        rohdaten = tomllib.load(datei)

    fehlende_schluessel = [
        schluessel
        for schluessel in ("haushaltsjahr", "satzung", "gesamtergebnisplan")
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

    _pruefe_nur_ganzzahlen(rohdaten, "sollwerte")

    return rohdaten
