"""Validierung von `meta.json` und gemeinsame Domänenformeln für die manuell
gepflegten Dateien (Phase 4, D-09 bis D-14, MANU-06).

`lies_meta_json` validiert die Datei strikt gegen eine feste Struktur: kein
unbekanntes Feld, keine Namen natürlicher Personen (Datenschutz) — die Satzung
S. 9 druckt die Namen der Unterzeichnenden neben den Daten, hier werden nur die
Daten selbst und rollenfreie Werte übernommen.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

_META_EINHEITEN = frozenset({"personen", "ha", "prozent", "promille", "euro", "datum"})
_META_LEAF_PFLICHT = frozenset({"wert", "einheit", "quelle"})
_META_LEAF_OPTIONAL = frozenset(
    {"stichtag", "herkunft", "berechnet", "gerundet", "formel", "vorjahr", "anmerkung"}
)
_ISO_DATUM_MUSTER = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_VORBERICHT_WERTE_SCHLUESSEL_MUSTER = re.compile(r"^[a-z][a-z0-9_]*$")

# Feste Struktur von meta.json (D-10, MANU-06); jede Erweiterung braucht Review hier.
_META_TOP_SCHLUESSEL: tuple[str, ...] = (
    "einwohner",
    "flaeche",
    "hebesaetze",
    "kreisumlage",
    "satzung",
    "vorbericht_werte",
)
_META_HEBESAETZE_SCHLUESSEL: tuple[str, ...] = ("grundsteuer_a", "grundsteuer_b", "gewerbesteuer")
_META_KREISUMLAGE_SCHLUESSEL: tuple[str, ...] = (
    "netto",
    "rueckstellungsaufloesung",
    "brutto",
    "hebesatz_kreisumlage",
    "hebesatz_jugendamtsumlage",
)
_META_SATZUNG_SCHLUESSEL: tuple[str, ...] = ("beschluss", "ausfertigung")

# Schulden-Definition des Vorberichts (D-14): Investitionskredite plus die haushalts-
# rechtlich als Transferverbindlichkeit gebuchten NRW.Bank-Mittel für Flüchtlings-
# unterkünfte. Schritt 07 (04-04) nutzt dieselbe Definition wie Regel 5/9.
SCHULDEN_POSTEN: tuple[str, ...] = ("kredite_investitionen", "transferleistungen")


class ManuellFehler(ValueError):
    """Wird ausgelöst, wenn eine manuelle Datei (meta.json, Verbindlichkeiten, ...)
    nicht dem erwarteten Format entspricht."""


def _pruefe_meta_leaf(wert: object, pfad: str) -> None:
    if not isinstance(wert, dict):
        raise ManuellFehler(f"meta.json: {pfad} muss ein Objekt sein")
    vorhandene = set(wert)
    fehlend = _META_LEAF_PFLICHT - vorhandene
    if fehlend:
        raise ManuellFehler(f"meta.json: {pfad} fehlen Felder: {sorted(fehlend)}")
    unerwartet = vorhandene - _META_LEAF_PFLICHT - _META_LEAF_OPTIONAL
    if unerwartet:
        raise ManuellFehler(f"meta.json: {pfad} hat unbekannte Felder: {sorted(unerwartet)}")

    einheit = wert.get("einheit")
    if einheit not in _META_EINHEITEN:
        raise ManuellFehler(f"meta.json: {pfad}.einheit ist ungültig: {einheit!r}")

    betrag = wert.get("wert")
    if einheit == "datum":
        if not isinstance(betrag, str) or not _ISO_DATUM_MUSTER.match(betrag):
            raise ManuellFehler(f"meta.json: {pfad}.wert ist kein ISO-Datum: {betrag!r}")
    elif not isinstance(betrag, int) or isinstance(betrag, bool):
        raise ManuellFehler(f"meta.json: {pfad}.wert muss eine Ganzzahl sein: {betrag!r}")

    quelle = wert.get("quelle")
    if not isinstance(quelle, int) or isinstance(quelle, bool) or quelle < 1:
        raise ManuellFehler(f"meta.json: {pfad}.quelle muss eine Ganzzahl >= 1 sein")

    if "stichtag" in wert:
        stichtag = wert["stichtag"]
        if not isinstance(stichtag, str) or not _ISO_DATUM_MUSTER.match(stichtag):
            raise ManuellFehler(f"meta.json: {pfad}.stichtag ist kein ISO-Datum: {stichtag!r}")
    for feld in ("herkunft", "formel", "anmerkung"):
        if feld in wert and not isinstance(wert[feld], str):
            raise ManuellFehler(f"meta.json: {pfad}.{feld} muss ein String sein")
    for feld in ("berechnet", "gerundet"):
        if feld in wert and not isinstance(wert[feld], bool):
            raise ManuellFehler(f"meta.json: {pfad}.{feld} muss ein Wahrheitswert sein")
    if "vorjahr" in wert and (
        not isinstance(wert["vorjahr"], int) or isinstance(wert["vorjahr"], bool)
    ):
        raise ManuellFehler(f"meta.json: {pfad}.vorjahr muss eine Ganzzahl sein")


def _pruefe_meta_container(wert: object, pfad: str, erwartete_schluessel: tuple[str, ...]) -> None:
    if not isinstance(wert, dict):
        raise ManuellFehler(f"meta.json: {pfad} muss ein Objekt sein")
    vorhandene = set(wert)
    erwartet = set(erwartete_schluessel)
    fehlend = erwartet - vorhandene
    if fehlend:
        raise ManuellFehler(f"meta.json: {pfad} fehlen Felder: {sorted(fehlend)}")
    unerwartet = vorhandene - erwartet
    if unerwartet:
        raise ManuellFehler(f"meta.json: {pfad} hat unbekannte Felder: {sorted(unerwartet)}")
    for schluessel in erwartete_schluessel:
        _pruefe_meta_leaf(wert[schluessel], f"{pfad}.{schluessel}")


def lies_meta_json(pfad: Path) -> dict[str, Any]:
    """Liest und validiert `meta.json` strikt (D-10, MANU-06).

    Lehnt ab: einen unbekannten Top-Level- oder Blatt-Schlüssel, ein Blatt ohne
    `quelle`, einen Float-`wert`, eine `quelle` < 1, eine `einheit` außerhalb des
    erlaubten Vokabulars und ein nicht-ISO-Datum.
    """
    if not pfad.is_file():
        raise ManuellFehler(f"meta.json nicht gefunden: {pfad}")
    daten = json.loads(pfad.read_text(encoding="utf-8"))
    if not isinstance(daten, dict):
        raise ManuellFehler("meta.json: Wurzelobjekt muss ein Objekt sein")

    vorhandene = set(daten)
    erwartet = set(_META_TOP_SCHLUESSEL)
    fehlend = erwartet - vorhandene
    if fehlend:
        raise ManuellFehler(f"meta.json: fehlende Schlüssel: {sorted(fehlend)}")
    unerwartet = vorhandene - erwartet
    if unerwartet:
        raise ManuellFehler(f"meta.json: unbekannte Schlüssel: {sorted(unerwartet)}")

    _pruefe_meta_leaf(daten["einwohner"], "einwohner")
    _pruefe_meta_leaf(daten["flaeche"], "flaeche")
    _pruefe_meta_container(daten["hebesaetze"], "hebesaetze", _META_HEBESAETZE_SCHLUESSEL)
    _pruefe_meta_container(daten["kreisumlage"], "kreisumlage", _META_KREISUMLAGE_SCHLUESSEL)
    _pruefe_meta_container(daten["satzung"], "satzung", _META_SATZUNG_SCHLUESSEL)

    vorbericht_werte = daten["vorbericht_werte"]
    if not isinstance(vorbericht_werte, dict):
        raise ManuellFehler("meta.json: vorbericht_werte muss ein Objekt sein")
    for schluessel, wert in vorbericht_werte.items():
        if not _VORBERICHT_WERTE_SCHLUESSEL_MUSTER.match(schluessel):
            raise ManuellFehler(
                f"meta.json: vorbericht_werte hat ungültigen Schlüssel: {schluessel!r}"
            )
        _pruefe_meta_leaf(wert, f"vorbericht_werte.{schluessel}")

    return daten
