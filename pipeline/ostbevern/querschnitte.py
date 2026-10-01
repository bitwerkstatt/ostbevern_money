"""Haushaltsquerschnitte S. 291-300: Koordinatenparser (PRUEF-07, D-14, D-15).

Kontrollquelle, nie Datenquelle der App (Spez. 2): `daten/zwischen/querschnitte.csv`
wird mit den eigenen PG-/PB-Teilplänen abgeglichen (Regel 7 in `pruefung.py`), fließt
aber in keine Datei unter `daten/aufbereitet/` oder in die App-JSON-Erzeugung ein.

Dieses Modul öffnet das PDF selbst und ist daher nicht CSV-only wie `pruefung.py`
(dessen Invariante "liest nie das PDF" dadurch unverändert bleibt, D-06): die
Extraktion läuft als eigener Schritt in `06_pruefen.py`/`alle.py` VOR der eigentlichen
Prüfung, niemals innerhalb von `pruefung.py` selbst.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from pathlib import Path

import polars as pl

from ostbevern.konfiguration import Jahrgang, layout_liste, layout_text
from ostbevern.pdf import PdfDokument, Textzeile
from ostbevern.plaene import ExtraktionsErgebnis
from ostbevern.schema import (
    DATEN_WURZEL,
    HIERARCHIE_CSV,
    QUERSCHNITTE_CSV,
    lies_hierarchie_csv,
    schreibe_querschnitte_csv,
)
from ostbevern.spalten import SpaltenFehler, ordne_spalten
from ostbevern.zahlen import ist_betrag, lies_betrag


class QuerschnitteFehler(ValueError):
    """Wird ausgelöst, wenn eine Querschnitt-Seite oder -Zeile nicht lesbar ist (D-08)."""


@dataclass(frozen=True)
class Querschnittwert:
    """Ein einzelner Kennzahlwert einer Querschnitt-Zeile (PB, PG oder GESAMTSUMME)."""

    pb: str
    pg: str | None
    gesamtsumme: bool
    plan: str
    kennzahl: str
    betrag: int
    pdf_seite: int


@dataclass(frozen=True)
class _Block:
    """Zustand eines offenen Querschnitt-Blocks (ein PB x ein Plantyp)."""

    pb: str
    plan: str
    anker_x1: tuple[float, ...]
    kennzahlen: tuple[str, ...]


def _bereinige_seitenzahl_am_rand(
    zeilen: tuple[Textzeile, ...], pdf_seite: int
) -> tuple[Textzeile, ...]:
    """Entfernt das links angeklebte/eigenständige Wort der PDF-Seitenzahl (D-14).

    Die Seitenzahl steht normalerweise als eigene Zeile am linken Rand (x0 ~ 13), kann
    aber in eine Daten- oder Umbruchzeile hineingruppiert werden (S. 293: PG 0302, S.
    296: umgebrochener PG-Name). Entfernt wird nur ein Wort, dessen Text exakt der
    Seitenzahl entspricht und dessen x1 links von jedem anderen Wort auf der Seite
    liegt (Title/Kopf-/Datenzeilen beginnen bei x0 >= 42).
    """
    alle_woerter = [wort for zeile in zeilen for wort in zeile.woerter]
    andere_x0 = [wort.x0 for wort in alle_woerter if wort.text != str(pdf_seite)]
    if not andere_x0:
        return zeilen
    schwelle = min(andere_x0)

    bereinigt: list[Textzeile] = []
    for zeile in zeilen:
        neue_woerter = tuple(
            wort
            for wort in zeile.woerter
            if not (wort.text == str(pdf_seite) and wort.x1 < schwelle)
        )
        bereinigt.append(
            zeile if neue_woerter == zeile.woerter else replace(zeile, woerter=neue_woerter)
        )
    return tuple(bereinigt)


_PLAN_HINWEIS_MUSTER = re.compile(r"Ergebnisplan|Finanzplan")


def lies_querschnitte(dokument: PdfDokument, jahrgang: Jahrgang) -> list[Querschnittwert]:
    """Liest alle Haushaltsquerschnitt-Werte des konfigurierten Seitenbereichs.

    Scannt jede Seite zeilenweise: Titelzeilen setzen den PB-Code für den nächsten
    Block, Kopfzeilen (erstes Wort = `kopf_beginn`) liefern die Spaltenanker und den
    Plantyp (Spaltenzahl), Datenzeilen (vier Ziffern + Name) und die GESAMTSUMME-Zeile
    liefern die Werte. Eine Kopfzeile ohne ausstehenden Titel re-ankert einen über den
    Seitenumbruch offenen Block desselben Plantyps, oder wird (einmalig) als reine
    "Vorschau"-Kopfzeile ignoriert, wenn die vorherige Zeile die Fortsetzung-Markierung
    war (verifiziert S. 297->298, PB 11 -> PB 12); ohne diese Markierung bricht eine
    Kopfzeile ohne ausstehenden Titel/offenen Block mit QuerschnitteFehler ab (D-08).

    Fail-fast-Wächter (D-08): Betragsanzahl muss der Ankerzahl entsprechen; eine PG muss
    zu ihrer Block-PB passen; höchstens eine GESAMTSUMME je Block, danach keine Datenzeile
    mehr; eine neue Titelzeile, während der vorherige Block noch offen ist, meldet die
    fehlende GESAMTSUMME; ein Titeltext mit "Ergebnisplan"/"Finanzplan" muss zum
    Kopfzeilen-Plantyp passen; am Ende des Seitenbereichs darf kein Block offen sein;
    dasselbe (PB, Plan) darf nicht zweimal geöffnet werden.
    """
    bereich = jahrgang.seitenbereiche["querschnitte"]
    titel_muster = re.compile(layout_text(jahrgang, "querschnitte", "titel_muster"))
    kopf_beginn = layout_text(jahrgang, "querschnitte", "kopf_beginn")
    gesamtsumme_wort = layout_text(jahrgang, "querschnitte", "gesamtsumme")
    kennzahlen_ergebnisplan = layout_liste(jahrgang, "querschnitte", "kennzahlen_ergebnisplan")
    kennzahlen_finanzplan = layout_liste(jahrgang, "querschnitte", "kennzahlen_finanzplan")
    fortsetzung_normalisiert = "".join(jahrgang.kopfzeilen.fortsetzung.split())

    werte: list[Querschnittwert] = []
    pending_titel_pb: str | None = None
    pending_titel_plan_hinweis: str | None = None
    aktueller_block: _Block | None = None
    fortsetzung_erlaubt_bare_kopfzeile = False
    geoeffnete_bloecke: set[tuple[str, str]] = set()

    for pdf_seite in range(bereich.von, bereich.bis + 1):
        zeilen = _bereinige_seitenzahl_am_rand(dokument.zeilen(pdf_seite), pdf_seite)

        for zeile in zeilen:
            if not zeile.woerter:
                continue  # Fußzeile: Seitenzahl war das einzige Wort

            if len(zeile.woerter) == 1 and ist_betrag(zeile.woerter[0].text):
                continue  # Anlagen-Fußzeilennummer (eine einzelne Ganzzahl)

            text_ohne_leerzeichen = zeile.text_ohne_leerzeichen
            if text_ohne_leerzeichen.startswith(fortsetzung_normalisiert):
                fortsetzung_erlaubt_bare_kopfzeile = True
                continue  # reiner Hinweis; der offene Block bleibt über den Seitenumbruch

            erstes_wort = zeile.woerter[0].text

            titel_treffer = titel_muster.match(zeile.text)
            if titel_treffer is not None:
                if aktueller_block is not None:
                    raise QuerschnitteFehler(
                        f"S. {pdf_seite}: Titelzeile {zeile.text!r}, während Block PB "
                        f"{aktueller_block.pb} ({aktueller_block.plan}) noch offen ist "
                        "(fehlende GESAMTSUMME)"
                    )
                pending_titel_pb = titel_treffer.group("pb")
                plan_hinweis_treffer = _PLAN_HINWEIS_MUSTER.search(zeile.text)
                pending_titel_plan_hinweis = (
                    "ergebnisplan"
                    if plan_hinweis_treffer and plan_hinweis_treffer.group() == "Ergebnisplan"
                    else "finanzplan"
                    if plan_hinweis_treffer
                    else None
                )
                continue

            if erstes_wort == kopf_beginn:
                anker_woerter = zeile.woerter[1:]
                if len(anker_woerter) == len(kennzahlen_ergebnisplan):
                    plan, kennzahlen = "ergebnisplan", kennzahlen_ergebnisplan
                elif len(anker_woerter) == len(kennzahlen_finanzplan):
                    plan, kennzahlen = "finanzplan", kennzahlen_finanzplan
                else:
                    raise QuerschnitteFehler(
                        f"S. {pdf_seite}: Kopfzeile hat {len(anker_woerter)} Spalten, "
                        f"erwartet {len(kennzahlen_ergebnisplan)} oder "
                        f"{len(kennzahlen_finanzplan)}"
                    )
                anker_x1 = tuple(wort.x1 for wort in anker_woerter)

                if pending_titel_pb is not None:
                    if (
                        pending_titel_plan_hinweis is not None
                        and pending_titel_plan_hinweis != plan
                    ):
                        raise QuerschnitteFehler(
                            f"S. {pdf_seite}: Titel nennt {pending_titel_plan_hinweis!r}, "
                            f"Kopfzeile hat {len(anker_woerter)} Spalten ({plan!r}) "
                            "(Titel/Kopfzeilen-Widerspruch)"
                        )
                    block_schluessel = (pending_titel_pb, plan)
                    if block_schluessel in geoeffnete_bloecke:
                        raise QuerschnitteFehler(
                            f"S. {pdf_seite}: PB {pending_titel_pb} ({plan}) wird zweimal geöffnet"
                        )
                    geoeffnete_bloecke.add(block_schluessel)
                    aktueller_block = _Block(
                        pb=pending_titel_pb, plan=plan, anker_x1=anker_x1, kennzahlen=kennzahlen
                    )
                    pending_titel_pb = None
                    pending_titel_plan_hinweis = None
                elif aktueller_block is not None and aktueller_block.plan == plan:
                    if not fortsetzung_erlaubt_bare_kopfzeile:
                        raise QuerschnitteFehler(
                            f"S. {pdf_seite}: Fortsetzungs-Kopfzeile ohne vorherige "
                            "Fortsetzung-Markierung"
                        )
                    fortsetzung_erlaubt_bare_kopfzeile = False
                    aktueller_block = replace(aktueller_block, anker_x1=anker_x1)
                elif fortsetzung_erlaubt_bare_kopfzeile:
                    # Vorschau-Kopfzeile ohne ausstehenden Titel/offenen Block, aber direkt
                    # nach einer Fortsetzung-Markierung (verifiziert S. 297->298) -> ignorieren.
                    fortsetzung_erlaubt_bare_kopfzeile = False
                else:
                    raise QuerschnitteFehler(
                        f"S. {pdf_seite}: Kopfzeile ohne ausstehenden Titel und ohne offenen "
                        "Block (keine vorherige Fortsetzung-Markierung)"
                    )
                continue

            ist_datenzeilenkopf = (
                len(erstes_wort) >= 5 and erstes_wort[:4].isdigit() and not erstes_wort[4].isdigit()
            )
            ist_gesamtsumme = erstes_wort == gesamtsumme_wort

            if not ist_datenzeilenkopf and not ist_gesamtsumme:
                # Kopfzeilen-Fortsetzungszeile oder umgebrochener PG-Name (ohne Beträge)
                continue

            if aktueller_block is None:
                raise QuerschnitteFehler(
                    f"S. {pdf_seite}: Datenzeile ohne offenen Block: {text_ohne_leerzeichen!r}"
                )

            pg = None if ist_gesamtsumme else erstes_wort[:4]
            if pg is not None and pg[:2] != aktueller_block.pb:
                raise QuerschnitteFehler(
                    f"S. {pdf_seite}: PG {pg} gehört nicht zu PB {aktueller_block.pb} "
                    f"({text_ohne_leerzeichen!r})"
                )

            amount_woerter = [wort for wort in zeile.woerter[1:] if ist_betrag(wort.text)]
            try:
                zugeordnet = ordne_spalten(amount_woerter, aktueller_block.anker_x1)
            except SpaltenFehler as fehler:
                raise QuerschnitteFehler(f"S. {pdf_seite}: {fehler}") from fehler
            if len(zugeordnet) != len(aktueller_block.anker_x1):
                bezeichner = "GESAMTSUMME" if ist_gesamtsumme else f"PG {pg}"
                raise QuerschnitteFehler(
                    f"S. {pdf_seite}: {bezeichner} ({aktueller_block.pb}, "
                    f"{aktueller_block.plan}): {len(zugeordnet)} Beträge zugeordnet, "
                    f"erwartet {len(aktueller_block.anker_x1)}"
                )

            for index, kennzahl in enumerate(aktueller_block.kennzahlen):
                betrag = lies_betrag(zugeordnet[index].text)
                if betrag is None:
                    raise QuerschnitteFehler(
                        f"S. {pdf_seite}: kein Wert für Kennzahl {kennzahl!r} "
                        f"({text_ohne_leerzeichen!r})"
                    )
                werte.append(
                    Querschnittwert(
                        pb=aktueller_block.pb,
                        pg=pg,
                        gesamtsumme=ist_gesamtsumme,
                        plan=aktueller_block.plan,
                        kennzahl=kennzahl,
                        betrag=betrag,
                        pdf_seite=pdf_seite,
                    )
                )

            if ist_gesamtsumme:
                aktueller_block = None

    if aktueller_block is not None:
        raise QuerschnitteFehler(
            f"S. {bereich.bis}: Block PB {aktueller_block.pb} ({aktueller_block.plan}) am "
            "Ende des Seitenbereichs noch offen (fehlende GESAMTSUMME)"
        )

    return werte


def pruefe_vollstaendigkeit(werte: list[Querschnittwert], hierarchie: pl.DataFrame) -> None:
    """Prüft `werte` gegen die erwartete PB-/PG-Menge aus `hierarchie` (D-08).

    Fehler: die PB-Menge weicht von hierarchie.csv ab, eine PB hat nicht beide Plantypen,
    oder die PG-Menge eines (PB, Plan) weicht von den PG-Kindern dieser PB ab (gedruckt
    und synthetisch, via `eltern_code`).
    """
    hierarchie_pb_codes = set(hierarchie.filter(pl.col("ebene") == "PB")["code"].to_list())
    gefundene_pb = {wert.pb for wert in werte}
    if gefundene_pb != hierarchie_pb_codes:
        raise QuerschnitteFehler(
            f"Produktbereiche im Querschnitt {sorted(gefundene_pb)} weichen von "
            f"hierarchie.csv {sorted(hierarchie_pb_codes)} ab"
        )

    for pb in sorted(hierarchie_pb_codes):
        erwartete_pg = set(
            hierarchie.filter((pl.col("ebene") == "PG") & (pl.col("eltern_code") == pb))[
                "code"
            ].to_list()
        )
        for plan in ("ergebnisplan", "finanzplan"):
            treffer_pb_plan = [wert for wert in werte if wert.pb == pb and wert.plan == plan]
            if not treffer_pb_plan:
                raise QuerschnitteFehler(f"PB {pb}: kein Querschnitt-Block für {plan} gefunden")
            gefundene_pg = {wert.pg for wert in treffer_pb_plan if not wert.gesamtsumme}
            if gefundene_pg != erwartete_pg:
                raise QuerschnitteFehler(
                    f"PB {pb} ({plan}): gefundene PG {sorted(gefundene_pg)} weicht von "
                    f"hierarchie.csv ({sorted(erwartete_pg)}) ab"
                )


def extrahiere_querschnitte(
    jahrgang: Jahrgang, *, daten_wurzel: Path = DATEN_WURZEL
) -> ExtraktionsErgebnis:
    """Liest die Querschnitte, prüft sie gegen `hierarchie.csv` und schreibt
    `daten_wurzel/QUERSCHNITTE_CSV` (D-14)."""
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        werte = lies_querschnitte(dokument, jahrgang)

    hierarchie = lies_hierarchie_csv(daten_wurzel / HIERARCHIE_CSV)
    pruefe_vollstaendigkeit(werte, hierarchie)

    df = pl.DataFrame(
        [
            {
                "pb": wert.pb,
                "pg": wert.pg,
                "gesamtsumme": wert.gesamtsumme,
                "plan": wert.plan,
                "kennzahl": wert.kennzahl,
                "betrag": wert.betrag,
                "pdf_seite": wert.pdf_seite,
            }
            for wert in werte
        ],
        schema={
            "pb": pl.Utf8,
            "pg": pl.Utf8,
            "gesamtsumme": pl.Boolean,
            "plan": pl.Utf8,
            "kennzahl": pl.Utf8,
            "betrag": pl.Int64,
            "pdf_seite": pl.Int64,
        },
    )
    pfad = daten_wurzel / QUERSCHNITTE_CSV
    schreibe_querschnitte_csv(df, pfad)
    return ExtraktionsErgebnis(zeilen_geschrieben=df.height, pfad=pfad)
