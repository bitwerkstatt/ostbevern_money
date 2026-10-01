"""Zeilen-Wörterbuch und Label-Normalisierung je Plantyp.

Das Wörterbuch und die Zwischenüberschriften sind fachliche Regeln (Phase 1 D-07),
keine Jahrgangswerte: sie stehen hier im Code, nicht in `pipeline/jahrgaenge/*.toml`.
Dieses Modul deckt bislang die Plantypen "gesamtergebnisplan" und "gesamtfinanzplan" ab;
Teilergebnis- und Teilfinanzplan folgen in Plan 02-04 dieser Phase.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

PLANTYPEN = ("gesamtergebnisplan", "teilergebnisplan", "gesamtfinanzplan", "teilfinanzplan")

_FORMEL_HINWEIS_MUSTER = re.compile(r"\(Z\.[^)]*\)$")
_WHITESPACE_MUSTER = re.compile(r"\s+")


@dataclass(frozen=True)
class Zeilendefinition:
    """Fester Name, Kurzschlüssel und Summenflag einer Planzeile (D-12)."""

    name: str
    kanonisch: str
    ist_summe: bool


ZEILEN: dict[str, dict[str, Zeilendefinition]] = {
    "gesamtergebnisplan": {
        "01": Zeilendefinition("Steuern und ähnliche Abgaben", "steuern", False),
        "02": Zeilendefinition("Zuwendungen und allgemeine Umlagen", "zuwendungen", False),
        "03": Zeilendefinition("Sonstige Transfererträge", "sonstige_transferertraege", False),
        "04": Zeilendefinition(
            "Öffentlich-rechtliche Leistungsentgelte",
            "oeffentlich_rechtliche_entgelte",
            False,
        ),
        "05": Zeilendefinition(
            "Privatrechtliche Leistungsentgelte", "privatrechtliche_entgelte", False
        ),
        "06": Zeilendefinition("Kostenerstattungen und Kostenumlagen", "kostenerstattungen", False),
        "07": Zeilendefinition(
            "Sonstige ordentliche Erträge", "sonstige_ordentliche_ertraege", False
        ),
        "08": Zeilendefinition("Aktivierte Eigenleistungen", "aktivierte_eigenleistungen", False),
        "09": Zeilendefinition("Bestandsveränderungen", "bestandsveraenderungen", False),
        "10": Zeilendefinition("Ordentliche Erträge", "ordentliche_ertraege", True),
        "11": Zeilendefinition("Personalaufwendungen", "personalaufwendungen", False),
        "12": Zeilendefinition("Versorgungsaufwendungen", "versorgungsaufwendungen", False),
        "13": Zeilendefinition(
            "Aufwendungen für Sach- und Dienstleistungen",
            "sach_und_dienstleistungen",
            False,
        ),
        "14": Zeilendefinition("Bilanzielle Abschreibungen", "abschreibungen", False),
        "15": Zeilendefinition("Transferaufwendungen", "transferaufwendungen", False),
        "16": Zeilendefinition(
            "Sonstige ordentliche Aufwendungen", "sonstige_ordentliche_aufwendungen", False
        ),
        "17": Zeilendefinition("Ordentliche Aufwendungen", "ordentliche_aufwendungen", True),
        "18": Zeilendefinition("Ordentliches Ergebnis", "ordentliches_ergebnis", True),
        "19": Zeilendefinition("Finanzerträge", "finanzertraege", False),
        "20": Zeilendefinition("Zinsen und ähnliche Aufwendungen", "zinsaufwendungen", False),
        "21": Zeilendefinition("Finanzergebnis", "finanzergebnis", True),
        "22": Zeilendefinition(
            "Ergebnis der lfd. Verw.-tätigkeit", "ergebnis_laufende_verwaltung", True
        ),
        "23": Zeilendefinition("Außerordentliche Erträge", "ausserordentliche_ertraege", False),
        "24": Zeilendefinition(
            "Außerordentliche Aufwendungen", "ausserordentliche_aufwendungen", False
        ),
        "25": Zeilendefinition("Außerordentliches Ergebnis", "ausserordentliches_ergebnis", True),
        "26": Zeilendefinition("Jahresergebnis", "jahresergebnis", True),
        "27": Zeilendefinition("Globaler Minderaufwand", "globaler_minderaufwand", False),
        "28": Zeilendefinition(
            "Jahresergebnis nach Abzug globaler Minderaufwand",
            "ergebnis_nach_minderaufwand",
            True,
        ),
        "29": Zeilendefinition(
            "Verrechnete Erträge bei Vermögensgegenständen",
            "nachrichtlich_ertraege_vermoegensgegenstaende",
            False,
        ),
        "30": Zeilendefinition(
            "Verrechnete Erträge bei Finanzanlagen",
            "nachrichtlich_ertraege_finanzanlagen",
            False,
        ),
        "31": Zeilendefinition(
            "Verrechnete Aufw. bei Vermögensgegenständen",
            "nachrichtlich_aufwendungen_vermoegensgegenstaende",
            False,
        ),
        "32": Zeilendefinition(
            "Verrechnete Aufwendungen bei Finanzanlagen",
            "nachrichtlich_aufwendungen_finanzanlagen",
            False,
        ),
        "33": Zeilendefinition("Verrechnungssaldo", "nachrichtlich_verrechnungssaldo", True),
    },
    "gesamtfinanzplan": {
        "01": Zeilendefinition("Steuern und ähnliche Abgaben", "steuern", False),
        "02": Zeilendefinition("Zuwendungen und allgemeine Umlagen", "zuwendungen", False),
        "03": Zeilendefinition(
            "Sonstige Transfereinzahlungen", "sonstige_transfereinzahlungen", False
        ),
        "04": Zeilendefinition(
            "Öffentlich-rechtliche Leistungsentgelte",
            "oeffentlich_rechtliche_entgelte",
            False,
        ),
        "05": Zeilendefinition(
            "Privatrechtliche Leistungsentgelte", "privatrechtliche_entgelte", False
        ),
        "06": Zeilendefinition("Kostenerstattungen und Kostenumlagen", "kostenerstattungen", False),
        "07": Zeilendefinition("Sonstige Einzahlungen", "sonstige_einzahlungen", False),
        "08": Zeilendefinition(
            "Zinsen und sonstige Finanzeinzahlungen", "finanzeinzahlungen", False
        ),
        "09": Zeilendefinition(
            "Einzahlungen aus lfd. Verw.-tätigkeit",
            "einzahlungen_laufende_verwaltung",
            True,
        ),
        "10": Zeilendefinition("Personalauszahlungen", "personalauszahlungen", False),
        "11": Zeilendefinition("Versorgungsauszahlungen", "versorgungsauszahlungen", False),
        "12": Zeilendefinition(
            "Auszahlg. Sach- und Dienstleistungen", "sach_und_dienstleistungen", False
        ),
        "13": Zeilendefinition(
            "Zinsen und sonstige Finanzauszahlungen", "finanzauszahlungen", False
        ),
        "14": Zeilendefinition("Transferauszahlungen", "transferauszahlungen", False),
        "15": Zeilendefinition("Sonstige Auszahlungen", "sonstige_auszahlungen", False),
        "16": Zeilendefinition(
            "Auszahlungen aus lfd. Verw.-tätigkeit",
            "auszahlungen_laufende_verwaltung",
            True,
        ),
        "17": Zeilendefinition("Saldo aus lfd. Verw.-tätigkeit", "saldo_laufende_verwaltung", True),
        "18": Zeilendefinition(
            "Zuwendungen für Investitionsmaßnahmen", "investitionszuwendungen", False
        ),
        "19": Zeilendefinition(
            "Einz. aus Veräußerung v. Sachanlagen", "veraeusserung_sachanlagen", False
        ),
        "20": Zeilendefinition(
            "Einz. aus Veräußerung v. Finanzanlagen", "veraeusserung_finanzanlagen", False
        ),
        "21": Zeilendefinition("Einz. aus Beiträgen u. ä. Entgelten", "beitraege", False),
        "22": Zeilendefinition(
            "Sonstige Investitionseinzahlungen", "sonstige_investitionseinzahlungen", False
        ),
        "23": Zeilendefinition(
            "Einzahlungen aus Investitionstätigkeit", "einzahlungen_investitionen", True
        ),
        "24": Zeilendefinition(
            "Ausz. f. Erwerb von Grundst. u. Gebäuden", "erwerb_grundstuecke_gebaeude", False
        ),
        "25": Zeilendefinition("Ausz. f. Baumaßnahmen", "baumassnahmen", False),
        "26": Zeilendefinition(
            "Ausz. f. Erwerb v. bewegl. Anlageverm.",
            "erwerb_bewegliches_anlagevermoegen",
            False,
        ),
        "27": Zeilendefinition("Ausz. f. Erwerb v. Finanzanlagen", "erwerb_finanzanlagen", False),
        "28": Zeilendefinition(
            "Ausz. v. aktivierbaren Zuwendungen", "aktivierbare_zuwendungen", False
        ),
        "29": Zeilendefinition(
            "Sonstige Investitionsauszahlungen", "sonstige_investitionsauszahlungen", False
        ),
        "30": Zeilendefinition(
            "Auszahlungen aus Investitionstätigkeit", "auszahlungen_investitionen", True
        ),
        "31": Zeilendefinition("Saldo aus Investitionstätigkeit", "saldo_investitionen", True),
        "32": Zeilendefinition("Überschuss/Fehlbetrag", "finanzmittelueberschuss", True),
        "33": Zeilendefinition("Aufnahme und Rückflüsse von Darlehen", "kreditaufnahme", False),
        "34": Zeilendefinition(
            "Aufn. v. Krediten z. Liquiditätssicherung",
            "liquiditaetskredite_aufnahme",
            False,
        ),
        "35": Zeilendefinition("Tilgung und Gewährung von Darlehen", "tilgung", False),
        "36": Zeilendefinition(
            "Tilgung v. Krediten z. Liquiditätssicherung",
            "liquiditaetskredite_tilgung",
            False,
        ),
        "37": Zeilendefinition("Saldo aus Finanzierungstätigkeit", "saldo_finanzierung", True),
        "38": Zeilendefinition("Änd. des Finanzbestandes", "aenderung_finanzbestand", True),
        "39": Zeilendefinition(
            "Anfangsbestand an Finanzmitteln", "anfangsbestand_finanzmittel", False
        ),
        "40": Zeilendefinition("Bestand an fremden Finanzmitteln", "fremde_finanzmittel", False),
        "41": Zeilendefinition("Liquide Mittel", "liquide_mittel", True),
    },
}

ZWISCHENUEBERSCHRIFTEN: dict[str, tuple[str, ...]] = {
    "gesamtergebnisplan": (
        "Nachrichtlich: Verrechnung von Erträgen und Aufwendungen mit der allgemeinen Rücklage",
    ),
}

# Zeilenformeln je Plantyp (PRUEF-01, Regel 1): Zeile -> Summe aus (Vorzeichen, Komponente).
# GREEN-Implementierung folgt im nächsten Commit dieses Plans (02-03 Task 2); dieser Stub
# hält das Modul importierbar, ohne die Prüfregel bereits zu erfüllen (RED).
FORMELN: dict[str, dict[str, tuple[tuple[int, str], ...]]] = {}


def normalisiere_bezeichnung(text: str) -> str:
    """Entfernt Leerzeichen, einen abschließenden Formelhinweis und Bindestriche (D-12).

    Wird identisch auf den gedruckten PDF-Text und die Wörterbuch-Namen angewendet,
    damit umgebrochene und mit Bindestrich getrennte Labels gleich verglichen werden.
    """
    ohne_leerzeichen = _WHITESPACE_MUSTER.sub("", text)
    ohne_formel = _FORMEL_HINWEIS_MUSTER.sub("", ohne_leerzeichen)
    return ohne_formel.replace("-", "")


def plantyp_fuer(datei: str, ebene: str) -> str:
    """Leitet den Plantyp aus Zieldatei ("ergebnisplan"/"finanzplan") und Ebene ab."""
    vorsilbe = "gesamt" if ebene == "GESAMT" else "teil"
    return f"{vorsilbe}{datei}"
