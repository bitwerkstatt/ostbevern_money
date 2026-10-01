"""Schritt 02: Pläne extrahieren (Spez. 5.4).

Liest eine Plantabellen-Seite wortweise mit x-Koordinaten, prüft jede Zeile gegen
das Zeilen-Wörterbuch (D-12) und schreibt das Ergebnis im Langformat (D-10, D-11).
Bricht bei jedem Unstimmigkeit sofort mit PDF-Seite und Zeile ab (D-08).
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, replace
from pathlib import Path

import polars as pl

from ostbevern.konfiguration import Jahrgang
from ostbevern.pdf import PdfDokument, Textzeile, Wort
from ostbevern.schema import (
    DATEN_WURZEL,
    ERGEBNISPLAN_CSV,
    FINANZPLAN_CSV,
    PLAN_SPALTEN,
    schreibe_plan_csv,
    zerlege_spaltenkopf,
)
from ostbevern.zahlen import ist_betrag, lies_betrag, trenne_angeklebten_betrag, trenne_operator
from ostbevern.zeilen import ZEILEN, ZWISCHENUEBERSCHRIFTEN, normalisiere_bezeichnung, plantyp_fuer

_X_TOLERANZ = 2.0


class PlaeneFehler(ValueError):
    """Wird ausgelöst, wenn eine Plantabellen-Seite oder -Zeile nicht lesbar ist (D-08)."""


@dataclass(frozen=True)
class GedruckteZeile:
    """Eine geparste Planzeile vor dem Abgleich mit dem Zeilen-Wörterbuch."""

    zeile: str
    operator: str | None
    bezeichnung: str
    werte: tuple[int, ...]
    pdf_seite: int


@dataclass(frozen=True)
class ExtraktionsErgebnis:
    """Ergebnis von extrahiere_plaene: Anzahl geschriebener CSV-Zeilen und Zielpfad."""

    zeilen_geschrieben: int
    pfad: Path


def _finde_kopfzeile(zeilen: Sequence[Textzeile], pdf_seite: int) -> int:
    for index, zeile in enumerate(zeilen):
        if zeile.woerter and zeile.woerter[0].text == "Nr.":
            return index
    raise PlaeneFehler(f"S. {pdf_seite}: keine Kopfzeile mit 'Nr.' gefunden")


def _lies_spaltenkoepfe(
    kopfzeile: Textzeile, jahreszeile: Textzeile, pdf_seite: int
) -> tuple[list[str], tuple[Wort, ...]]:
    c_index = next((i for i, w in enumerate(kopfzeile.woerter) if w.text == "C"), None)
    if c_index is None:
        raise PlaeneFehler(f"S. {pdf_seite}: Spaltenkopf ohne 'C' (Eurozeichen) gefunden")
    label_woerter = kopfzeile.woerter[c_index + 1 :]
    jahreswoerter = jahreszeile.woerter
    if len(label_woerter) != len(jahreswoerter):
        raise PlaeneFehler(
            f"S. {pdf_seite}: {len(label_woerter)} Spaltenbezeichnungen, "
            f"{len(jahreswoerter)} Jahreszahlen"
        )
    spalten = [
        f"{label.text} {jahr.text}"
        for label, jahr in zip(label_woerter, jahreswoerter, strict=True)
    ]
    return spalten, jahreswoerter


def _ordne_werte(
    amount_woerter: list[Wort], jahreswoerter: tuple[Wort, ...], pdf_seite: int, zeilennummer: str
) -> tuple[int, ...]:
    if len(amount_woerter) != len(jahreswoerter):
        raise PlaeneFehler(
            f"S. {pdf_seite}, Zeile {zeilennummer}: {len(amount_woerter)} Beträge, "
            f"erwartet {len(jahreswoerter)}"
        )
    sortierte_betraege = sorted(amount_woerter, key=lambda w: w.x1)
    sortierte_jahre = sorted(jahreswoerter, key=lambda w: w.x1)
    abstaende = [
        abs(sortierte_jahre[i].x1 - sortierte_jahre[i - 1].x1)
        for i in range(1, len(sortierte_jahre))
    ]
    toleranz = min(abstaende) / 2 if abstaende else float("inf")

    werte: list[int] = []
    for jahreswort, betragwort in zip(sortierte_jahre, sortierte_betraege, strict=True):
        abstand = abs(betragwort.x1 - jahreswort.x1)
        if abstand >= toleranz:
            raise PlaeneFehler(
                f"S. {pdf_seite}, Zeile {zeilennummer}: Betrag {betragwort.text!r} passt zu "
                "keiner Spalte"
            )
        betrag = lies_betrag(betragwort.text)
        if betrag is None:
            raise PlaeneFehler(
                f"S. {pdf_seite}, Zeile {zeilennummer}: kein Wert in einer Plantabellen-Spalte"
            )
        werte.append(betrag)
    return tuple(werte)


def lies_plantabelle(
    zeilen: Sequence[Textzeile],
    *,
    plantyp: str,
    spalten: Sequence[str],
    pdf_seite: int,
) -> list[GedruckteZeile]:
    """Parst eine Plantabellen-Seite gegen das Zeilen-Wörterbuch (D-08, D-12)."""
    kopf_index = _finde_kopfzeile(zeilen, pdf_seite)
    kopfzeile = zeilen[kopf_index]
    jahreszeile = zeilen[kopf_index + 1]
    gelesene_spalten, jahreswoerter = _lies_spaltenkoepfe(kopfzeile, jahreszeile, pdf_seite)
    if tuple(gelesene_spalten) != tuple(spalten):
        raise PlaeneFehler(
            f"S. {pdf_seite}: Spaltenköpfe {gelesene_spalten} weichen von {tuple(spalten)} ab"
        )

    nr_x0 = kopfzeile.woerter[0].x0
    erste_jahresspalte_x0 = jahreswoerter[0].x0
    zwischenueberschriften = {
        normalisiere_bezeichnung(h) for h in ZWISCHENUEBERSCHRIFTEN.get(plantyp, ())
    }

    gelesene_zeilen: dict[str, GedruckteZeile] = {}
    aktuelle_zeile: str | None = None

    for zeile in zeilen[kopf_index + 2 :]:
        text = zeile.text_ohne_leerzeichen
        if text == str(pdf_seite):
            break

        normalisiert = normalisiere_bezeichnung(text)
        if normalisiert in zwischenueberschriften:
            aktuelle_zeile = None
            continue

        erstes_wort = zeile.woerter[0]
        ist_zeilenkopf = (
            len(erstes_wort.text) == 2
            and erstes_wort.text.isdigit()
            and abs(erstes_wort.x0 - nr_x0) <= _X_TOLERANZ
        )
        amount_woerter = [
            w for w in zeile.woerter if w.x1 > erste_jahresspalte_x0 and ist_betrag(w.text)
        ]

        if ist_zeilenkopf and amount_woerter:
            zeilennummer = erstes_wort.text
            amount_set = set(amount_woerter)
            label_woerter_roh = [w for w in zeile.woerter[1:] if w not in amount_set]
            if not label_woerter_roh:
                raise PlaeneFehler(f"S. {pdf_seite}, Zeile {zeilennummer}: keine Bezeichnung")

            # Ein Wort in der Betragszone, das selbst kein Betrag ist, kann einen
            # angeklebten Betrag am Ende tragen (Spez. 3.8/5.4); der Textteil bleibt
            # im Label, der Zahlenteil wird wie ein eigenes Betragswort zugeordnet.
            alle_amount_woerter = list(amount_woerter)
            label_teile: list[str] = []
            for wort in label_woerter_roh:
                if wort.x1 > erste_jahresspalte_x0:
                    rest_text, betrag_text = trenne_angeklebten_betrag(wort.text)
                    if betrag_text is not None:
                        label_teile.append(rest_text)
                        alle_amount_woerter.append(replace(wort, text=betrag_text))
                        continue
                label_teile.append(wort.text)

            operator, rest = trenne_operator(label_teile[0])
            bezeichnung = rest + "".join(label_teile[1:])
            werte = _ordne_werte(alle_amount_woerter, jahreswoerter, pdf_seite, zeilennummer)
            if zeilennummer in gelesene_zeilen:
                raise PlaeneFehler(
                    f"S. {pdf_seite}, Zeile {zeilennummer}: Zeilennummer kommt zweimal vor"
                )
            gelesene_zeilen[zeilennummer] = GedruckteZeile(
                zeile=zeilennummer,
                operator=operator,
                bezeichnung=bezeichnung,
                werte=werte,
                pdf_seite=pdf_seite,
            )
            aktuelle_zeile = zeilennummer
        elif not ist_zeilenkopf and not amount_woerter and aktuelle_zeile is not None:
            vorherige = gelesene_zeilen[aktuelle_zeile]
            gelesene_zeilen[aktuelle_zeile] = replace(
                vorherige, bezeichnung=vorherige.bezeichnung + text
            )
        else:
            raise PlaeneFehler(
                f"S. {pdf_seite}: unerwartete Zeile ohne Zeilennummer oder Fortsetzung: {text!r}"
            )

    woerterbuch = ZEILEN[plantyp]
    for zeilennummer, gedruckt in gelesene_zeilen.items():
        definition = woerterbuch.get(zeilennummer)
        if definition is None:
            raise PlaeneFehler(f"S. {pdf_seite}, Zeile {zeilennummer}: unbekannte Zeilennummer")
        if normalisiere_bezeichnung(gedruckt.bezeichnung) != normalisiere_bezeichnung(
            definition.name
        ):
            raise PlaeneFehler(
                f"S. {pdf_seite}, Zeile {zeilennummer}: Bezeichnung {gedruckt.bezeichnung!r} "
                f"passt nicht zum Wörterbuch ({definition.name!r})"
            )

    return [gelesene_zeilen[z] for z in sorted(gelesene_zeilen)]


def extrahiere_plaene(
    jahrgang: Jahrgang, *, daten_wurzel: Path = DATEN_WURZEL
) -> tuple[ExtraktionsErgebnis, ExtraktionsErgebnis]:
    """Extrahiert Gesamtergebnis- und Gesamtfinanzplan (GESAMT) nach daten_wurzel (EXTR-04/05)."""
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        ergebnisplan = _extrahiere_gesamtplan(
            dokument,
            jahrgang,
            daten_wurzel=daten_wurzel,
            datei="ergebnisplan",
            ziel_csv=ERGEBNISPLAN_CSV,
        )
        finanzplan = _extrahiere_gesamtplan(
            dokument,
            jahrgang,
            daten_wurzel=daten_wurzel,
            datei="finanzplan",
            ziel_csv=FINANZPLAN_CSV,
        )
    return ergebnisplan, finanzplan


def _extrahiere_gesamtplan(
    dokument: PdfDokument,
    jahrgang: Jahrgang,
    *,
    daten_wurzel: Path,
    datei: str,
    ziel_csv: Path,
) -> ExtraktionsErgebnis:
    plantyp = plantyp_fuer(datei, "GESAMT")
    bereich = jahrgang.seitenbereiche[plantyp]
    spalten = jahrgang.spalten[datei]

    zeilen = dokument.zeilen(bereich.von)
    gedruckte_zeilen = lies_plantabelle(
        zeilen, plantyp=plantyp, spalten=spalten, pdf_seite=bereich.von
    )

    zeilen_definition = ZEILEN[plantyp]
    datensaetze: list[dict[str, object]] = []
    for gedruckt in gedruckte_zeilen:
        definition = zeilen_definition[gedruckt.zeile]
        for spaltenkopf, betrag in zip(spalten, gedruckt.werte, strict=True):
            wertart, jahr = zerlege_spaltenkopf(spaltenkopf)
            datensaetze.append(
                {
                    "ebene": "GESAMT",
                    "code": None,
                    "synthetisch": False,
                    "zeile": gedruckt.zeile,
                    "zeile_kanonisch": definition.kanonisch,
                    "zeile_name": definition.name,
                    "operator": gedruckt.operator,
                    "ist_summe": definition.ist_summe,
                    "jahr": jahr,
                    "wertart": wertart,
                    "betrag": betrag,
                    "pdf_seite": gedruckt.pdf_seite,
                }
            )

    df = pl.DataFrame(datensaetze, schema=PLAN_SPALTEN)
    pfad = daten_wurzel / ziel_csv
    schreibe_plan_csv(df, pfad)
    return ExtraktionsErgebnis(zeilen_geschrieben=df.height, pfad=pfad)
