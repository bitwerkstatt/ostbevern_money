"""Schritt 01: Seitenklassifikation (Spez. 5.3, D-16, D-17).

Liest die Kopfzeilen jeder PDF-Seite und ordnet sie einem Kapitel bzw. im
Teilplanbereich einem Produktbereich/einer Produktgruppe/einem Produkt und
einem feinen Seitentyp zu. Seiten ohne erkennbares Muster werden `unbekannt`
(D-17, bewusste Ausnahme zu D-08) statt den Lauf abzubrechen.
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

import polars as pl

from ostbevern.konfiguration import Jahrgang, Seitenbereich
from ostbevern.pdf import PdfDokument, Textzeile
from ostbevern.schema import DATEN_WURZEL, SEITEN_CSV, SEITEN_SPALTEN, schreibe_seiten_csv

# Toleranz für den Kopfzeilen-Einzug (Fortsetzungszeile vs. Abschnittstitel). Ein
# Abschnittstitel wie "Produktinformationen" steht auf derselben x0-Position wie die
# Kopfzeile selbst (~42.52), aber pdfplumber liefert dafür gelegentlich einen minimal
# abweichenden Float (z. B. 42.52000000000001) statt exakter Gleichheit. Fortsetzungs-
# zeilen sind dagegen deutlich eingerückt (x0 ~ 249). Die Toleranz muss daher größer als
# jegliches Float-Rauschen, aber viel kleiner als der tatsächliche Einzug sein.
_KOPFZEILE_X_TOLERANZ = 5.0
_KOPFZEILE_GROESSE_TOLERANZ = 0.5


class SeitenFehler(ValueError):
    """Wird ausgelöst, wenn eine Teilplanseite widersprüchliche Kopfzeilen trägt."""


@dataclass(frozen=True)
class Seitenkopf:
    """Aus den Kopfzeilen einer Teilplanseite gelesene Codes und Namen (D-15)."""

    pb: str | None
    pb_name: str | None
    pg: str | None
    pg_name: str | None
    produkt: str | None
    produkt_name: str | None


@dataclass(frozen=True)
class Seite:
    """Eine klassifizierte PDF-Seite (D-16, D-17)."""

    pdf_seite: int
    typ: str
    pb: str | None
    pg: str | None
    produkt: str | None


@dataclass(frozen=True)
class KlassifizierungsErgebnis:
    """Ergebnis von `klassifiziere_seiten`: Zielpfad und Lauf-Kennzahlen."""

    seiten_pfad: Path
    anzahl_seiten: int
    unbekannte_seiten: tuple[int, ...]


def verbinde_namensteile(teile: Sequence[str]) -> str:
    """Verbindet mehrzeilige Kopfzeilen-Namensteile zu einem Namen (D-15).

    Join-Regel: Fragmente werden mit einem Leerzeichen verbunden. Endet ein
    Fragment mit einem Bindestrich (Zeilenumbruch mitten im Wort), wird der
    Bindestrich ohne Leerzeichen entfernt — außer das nächste Fragment beginnt
    mit "und"/"oder" (z. B. "Natur- und Landschaftspflege"); dann bleibt der
    Bindestrich erhalten und es wird mit Leerzeichen verbunden.
    """
    ergebnis = teile[0]
    for teil in teile[1:]:
        if ergebnis.endswith("-"):
            erstes_wort = teil.split(" ", 1)[0]
            if erstes_wort in ("und", "oder"):
                ergebnis = f"{ergebnis} {teil}"
            else:
                ergebnis = f"{ergebnis[:-1]}{teil}"
        else:
            ergebnis = f"{ergebnis} {teil}"
    return ergebnis


def _kapitel_fuer_seite(pdf_seite: int, seitenbereiche: Mapping[str, Seitenbereich]) -> str | None:
    for name, bereich in seitenbereiche.items():
        if bereich.von <= pdf_seite <= bereich.bis:
            return name
    return None


def _ist_seitentyp_zeile(zeile: Textzeile, seitentypen: Mapping[str, str]) -> bool:
    text = zeile.text_ohne_leerzeichen
    return any(re.match(muster, text) for muster in seitentypen.values())


def _lies_kopfzeilenblock(
    zeilen: Sequence[Textzeile], index: int, treffer: re.Match[str]
) -> tuple[str, str, int]:
    """Liest einen PB-/PG-/Produkt-Kopfzeilenblock samt Fortsetzungszeilen (D-15)."""
    code = treffer.group(1)
    namensteile = [treffer.group(2)]
    kopf_zeile = zeilen[index]
    index += 1
    while index < len(zeilen):
        zeile = zeilen[index]
        ist_fortsetzung = (
            abs(zeile.groesse - kopf_zeile.groesse) < _KOPFZEILE_GROESSE_TOLERANZ
            and zeile.x0 > kopf_zeile.x0 + _KOPFZEILE_X_TOLERANZ
        )
        if ist_fortsetzung:
            namensteile.append(zeile.text)
            index += 1
        else:
            break
    return code, verbinde_namensteile(namensteile), index


def _lies_kopfzeile(
    zeilen: Sequence[Textzeile], jahrgang: Jahrgang, pdf_seite: int
) -> tuple[Seitenkopf | None, int]:
    """Sucht vom Seitenanfang aus die PB-/PG-/Produkt-Kopfzeile (Spez. 5.3, D-15)."""
    kopfzeilen = jahrgang.kopfzeilen
    index = 0
    pb_treffer: re.Match[str] | None = None
    while index < len(zeilen):
        zeile = zeilen[index]
        if _ist_seitentyp_zeile(zeile, kopfzeilen.seitentypen):
            return None, index
        treffer = re.match(kopfzeilen.produktbereich, zeile.text)
        if treffer:
            pb_treffer = treffer
            break
        index += 1

    if pb_treffer is None:
        return None, len(zeilen)

    pb_code, pb_name, index = _lies_kopfzeilenblock(zeilen, index, pb_treffer)

    pg_code = pg_name = produkt_code = produkt_name = None
    if index < len(zeilen):
        pg_treffer = re.match(kopfzeilen.produktgruppe, zeilen[index].text)
        if pg_treffer:
            pg_code, pg_name, index = _lies_kopfzeilenblock(zeilen, index, pg_treffer)
        else:
            produkt_treffer = re.match(kopfzeilen.produkt, zeilen[index].text)
            if produkt_treffer:
                produkt_code, produkt_name, index = _lies_kopfzeilenblock(
                    zeilen, index, produkt_treffer
                )

    if pg_code is not None and pg_code[:2] != pb_code:
        raise SeitenFehler(
            f"S. {pdf_seite}: Produktgruppe {pg_code} passt nicht zu Produktbereich {pb_code}"
        )
    if produkt_code is not None and produkt_code[:2] != pb_code:
        raise SeitenFehler(
            f"S. {pdf_seite}: Produkt {produkt_code} passt nicht zu Produktbereich {pb_code}"
        )

    kopf = Seitenkopf(
        pb=pb_code,
        pb_name=pb_name,
        pg=pg_code,
        pg_name=pg_name,
        produkt=produkt_code,
        produkt_name=produkt_name,
    )
    return kopf, index


def klassifiziere_dokument(
    dokument: PdfDokument, jahrgang: Jahrgang
) -> tuple[tuple[Seite, ...], Mapping[int, Seitenkopf]]:
    """Klassifiziert alle Seiten des Dokuments (D-16, D-17)."""
    if dokument.seitenanzahl != jahrgang.anzahlen.pdf_seiten:
        raise SeitenFehler(
            f"PDF hat {dokument.seitenanzahl} Seiten, Jahrgangsdatei erwartet "
            f"{jahrgang.anzahlen.pdf_seiten}"
        )

    seiten: list[Seite] = []
    koepfe: dict[int, Seitenkopf] = {}

    for pdf_seite in range(1, dokument.seitenanzahl + 1):
        kapitel = _kapitel_fuer_seite(pdf_seite, jahrgang.seitenbereiche)
        if kapitel is None:
            seiten.append(
                Seite(pdf_seite=pdf_seite, typ="sonstige", pb=None, pg=None, produkt=None)
            )
            continue
        if kapitel != "teilplaene":
            seiten.append(Seite(pdf_seite=pdf_seite, typ=kapitel, pb=None, pg=None, produkt=None))
            continue

        zeilen = dokument.zeilen(pdf_seite)
        kopf, erste_inhaltszeile_index = _lies_kopfzeile(zeilen, jahrgang, pdf_seite)
        if kopf is None:
            seiten.append(
                Seite(pdf_seite=pdf_seite, typ="unbekannt", pb=None, pg=None, produkt=None)
            )
            continue
        koepfe[pdf_seite] = kopf

        pg = kopf.pg or (kopf.produkt[:4] if kopf.produkt else None)

        typ: str | None = None
        if erste_inhaltszeile_index < len(zeilen):
            erste_inhaltszeile = zeilen[erste_inhaltszeile_index].text_ohne_leerzeichen
            for name, muster in jahrgang.kopfzeilen.seitentypen.items():
                if re.match(muster, erste_inhaltszeile):
                    typ = name
                    break

        if typ == "investitionen":
            typ = "investitionen_produkt" if kopf.produkt else "investitionen_pb"

        if typ is None:
            vorherige_seite = seiten[-1] if seiten else None
            if (
                vorherige_seite is not None
                and (pdf_seite - 1) in koepfe
                and vorherige_seite.pb == kopf.pb
                and vorherige_seite.pg == pg
                and vorherige_seite.produkt == kopf.produkt
            ):
                typ = vorherige_seite.typ
            else:
                typ = "unbekannt"

        seiten.append(Seite(pdf_seite=pdf_seite, typ=typ, pb=kopf.pb, pg=pg, produkt=kopf.produkt))

    return tuple(seiten), koepfe


def klassifiziere_seiten(
    jahrgang: Jahrgang, *, daten_wurzel: Path = DATEN_WURZEL
) -> KlassifizierungsErgebnis:
    """Klassifiziert alle Seiten und schreibt `daten_wurzel/SEITEN_CSV` (D-16)."""
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        seiten, _koepfe = klassifiziere_dokument(dokument, jahrgang)

    datensaetze = [
        {
            "pdf_seite": seite.pdf_seite,
            "typ": seite.typ,
            "pb": seite.pb,
            "pg": seite.pg,
            "produkt": seite.produkt,
        }
        for seite in seiten
    ]
    df = pl.DataFrame(datensaetze, schema=SEITEN_SPALTEN)
    pfad = daten_wurzel / SEITEN_CSV
    schreibe_seiten_csv(df, pfad)

    unbekannte_seiten = tuple(seite.pdf_seite for seite in seiten if seite.typ == "unbekannt")
    return KlassifizierungsErgebnis(
        seiten_pfad=pfad, anzahl_seiten=len(seiten), unbekannte_seiten=unbekannte_seiten
    )
