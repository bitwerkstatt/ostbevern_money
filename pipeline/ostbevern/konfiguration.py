"""Lädt die Jahrgangskonfiguration (D-06 bis D-09) aus `pipeline/jahrgaenge/*.toml`.

Jede PDF-spezifische Angabe (Haushaltsjahr, PDF-Pfad, Spaltenköpfe, Seitenbereiche,
Kopfzeilen-Muster, erwartete Anzahlen) steht ausschließlich in der Jahrgangsdatei, nie
im Code. Dieses Modul ist die einzige Stelle, die `tomllib` importiert.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass
from pathlib import Path

# Der Standardjahrgang steht an genau dieser einen Stelle im Code (D-09).
STANDARD_JAHR = 2026

PIPELINE_WURZEL = Path(__file__).resolve().parent.parent
PROJEKT_WURZEL = PIPELINE_WURZEL.parent
JAHRGAENGE_VERZEICHNIS = PIPELINE_WURZEL / "jahrgaenge"


class KonfigurationsFehler(ValueError):
    """Wird ausgelöst, wenn eine Jahrgangs- oder Sollwertdatei fehlt oder unvollständig ist."""


@dataclass(frozen=True)
class Anzahlen:
    """Erwartete Anzahlen aus der Jahrgangsdatei (D-07)."""

    pdf_seiten: int


@dataclass(frozen=True)
class Jahrgang:
    """Alle PDF-spezifischen Werte eines Haushaltsjahrgangs (D-07)."""

    haushaltsjahr: int
    pdf_pfad: Path
    anzahlen: Anzahlen


def lade_jahrgang(jahr: int, *, verzeichnis: Path = JAHRGAENGE_VERZEICHNIS) -> Jahrgang:
    """Lädt die Jahrgangsdatei `{jahr}.toml` und validiert die Pflichtschlüssel (D-12)."""
    pfad = verzeichnis / f"{jahr}.toml"
    if not pfad.is_file():
        raise KonfigurationsFehler(f"Jahrgangsdatei nicht gefunden: {pfad}")

    with pfad.open("rb") as datei:
        rohdaten = tomllib.load(datei)

    fehlende_schluessel = []
    if "haushaltsjahr" not in rohdaten:
        fehlende_schluessel.append("haushaltsjahr")
    if "pdf_pfad" not in rohdaten:
        fehlende_schluessel.append("pdf_pfad")
    if "anzahlen" not in rohdaten or "pdf_seiten" not in rohdaten.get("anzahlen", {}):
        fehlende_schluessel.append("anzahlen.pdf_seiten")
    if fehlende_schluessel:
        raise KonfigurationsFehler(
            f"Jahrgangsdatei {pfad} fehlen Schlüssel: {', '.join(fehlende_schluessel)}"
        )

    pdf_pfad = (PROJEKT_WURZEL / rohdaten["pdf_pfad"]).resolve()

    return Jahrgang(
        haushaltsjahr=rohdaten["haushaltsjahr"],
        pdf_pfad=pdf_pfad,
        anzahlen=Anzahlen(pdf_seiten=rohdaten["anzahlen"]["pdf_seiten"]),
    )
