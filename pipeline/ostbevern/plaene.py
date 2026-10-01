"""Schritt 02: Pläne extrahieren (Spez. 5.4).

Liest eine Plantabellen-Seite wortweise mit x-Koordinaten, prüft jede Zeile gegen
das Zeilen-Wörterbuch (D-12) und schreibt das Ergebnis im Langformat (D-10, D-11).
Bricht bei jedem Unstimmigkeit sofort mit PDF-Seite und Zeile ab (D-08).
"""

from __future__ import annotations

import re
from collections.abc import Collection, Sequence
from dataclasses import dataclass, replace
from pathlib import Path

import polars as pl

from ostbevern.konfiguration import Jahrgang
from ostbevern.pdf import PdfDokument, Textzeile, Wort
from ostbevern.schema import (
    DATEN_WURZEL,
    ERGEBNISPLAN_CSV,
    FINANZPLAN_CSV,
    HIERARCHIE_CSV,
    PLAN_SPALTEN,
    SEITEN_CSV,
    lies_hierarchie_csv,
    lies_seiten_csv,
    schreibe_plan_csv,
    zerlege_spaltenkopf,
)
from ostbevern.zahlen import ist_betrag, lies_betrag, trenne_angeklebten_betrag, trenne_operator
from ostbevern.zeilen import ZEILEN, ZWISCHENUEBERSCHRIFTEN, normalisiere_bezeichnung, plantyp_fuer

_X_TOLERANZ = 2.0
_NR_WORT = "Nr."


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


@dataclass(frozen=True)
class Abschnitt:
    """Ein zusammenhängender Teilergebnis- oder Teilfinanzplan-Abschnitt einer Seite.

    `zeilen` beginnt bei der "Nr."-Kopfzeile des Abschnitts (Research Pattern 3).
    `fortsetzung` ist True, wenn der Abschnitt ohne eigenen Titel als Fortsetzung eines
    auf einer Vorseite begonnenen Teilfinanzplans startet (bare Tabellenkopf statt Titel,
    D-17/EXTR-05).
    """

    plantyp: str
    zeilen: tuple[Textzeile, ...]
    fortsetzung: bool


def _ist_nr_zeile(zeile: Textzeile) -> bool:
    return bool(zeile.woerter) and zeile.woerter[0].text == _NR_WORT


def lies_abschnitte(
    zeilen: Sequence[Textzeile], jahrgang: Jahrgang, pdf_seite: int
) -> list[Abschnitt]:
    """Zerlegt eine Teilplan-Seite in Teilergebnisplan-/Teilfinanzplan-Abschnitte.

    Scannt die ganze Seite nach beiden Abschnitts-Headern statt einem einzigen Typ pro
    Seite zu vertrauen (Research Pattern 3, Pitfall 2). Ein Abschnitt endet vor dem
    nächsten Abschnitts-Start, vor einer Erläuterungen-/Investitionen-Zeile, vor der
    Fortsetzung-Markierung oder am Seitenzahl-Fußzeilen-Fund (D-08).
    """
    seitentypen = jahrgang.kopfzeilen.seitentypen
    fortsetzung_normalisiert = "".join(jahrgang.kopfzeilen.fortsetzung.split())

    abschnitte: list[Abschnitt] = []
    plantyp: str | None = None
    fortsetzung = False
    gesammelt: list[Textzeile] = []

    def schliesse() -> None:
        nonlocal plantyp, fortsetzung, gesammelt
        if plantyp is not None:
            abschnitte.append(
                Abschnitt(plantyp=plantyp, zeilen=tuple(gesammelt), fortsetzung=fortsetzung)
            )
        plantyp = None
        fortsetzung = False
        gesammelt = []

    for zeile in zeilen:
        text = zeile.text_ohne_leerzeichen
        if text == str(pdf_seite):
            break

        ist_nr_zeile = _ist_nr_zeile(zeile)
        ist_teg_treffer = re.match(seitentypen["teilergebnisplan"], text) is not None
        ist_tfp_treffer = re.match(seitentypen["teilfinanzplan"], text) is not None

        if ist_teg_treffer and not ist_nr_zeile:
            # Der Titel "Teilergebnisplan" eröffnet einen neuen Abschnitt; er spannt nie
            # mehrere Seiten (Flagged assumptions, 02-04-PLAN.md).
            schliesse()
            plantyp = "teilergebnisplan"
            fortsetzung = False
            continue

        if ist_tfp_treffer and not ist_nr_zeile:
            # Der Titel "Teilfinanzplan" eröffnet einen neuen Abschnitt. Direkt danach
            # folgt die eigene "Nr."-Kopfzeile, die den Teilfinanzplan-Treffer über die
            # zweite Alternative ebenfalls erfüllt — die unten folgende Prüfung
            # (plantyp bereits "teilfinanzplan") verhindert, dass daraus ein zweiter
            # Abschnitt wird (02-04-PLAN.md: "Titel direkt gefolgt von Kopfzeile").
            schliesse()
            plantyp = "teilfinanzplan"
            fortsetzung = False
            continue

        if ist_tfp_treffer and ist_nr_zeile and plantyp != "teilfinanzplan":
            # Bare Tabellenkopf ohne vorherigen Titel auf dieser Seite: Fortsetzung eines
            # auf der Vorseite begonnenen Teilfinanzplans (Research Pitfall 2/EXTR-05).
            schliesse()
            plantyp = "teilfinanzplan"
            fortsetzung = True
            gesammelt.append(zeile)
            continue

        ist_ende = (
            re.match(seitentypen["erlaeuterungen"], text) is not None
            or re.match(seitentypen["investitionen"], text) is not None
            or text.startswith(fortsetzung_normalisiert)
        )
        if ist_ende:
            schliesse()
            continue

        if plantyp is not None:
            gesammelt.append(zeile)

    schliesse()
    return abschnitte


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


def _gesamtplan_datensaetze(
    dokument: PdfDokument, jahrgang: Jahrgang, *, datei: str
) -> list[dict[str, object]]:
    """Liest den Gesamtergebnis- oder Gesamtfinanzplan (GESAMT) als Datensatzliste (EXTR-04/05)."""
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
    return datensaetze


def _knoten_fuer_seite(seite: dict[str, object]) -> tuple[str, str]:
    """Leitet (ebene, code) aus einer seiten.csv-Zeile ab: Produkt > PG > PB (D-13)."""
    if seite["produkt"] is not None:
        return "P", seite["produkt"]
    if seite["pg"] is not None:
        return "PG", seite["pg"]
    return "PB", seite["pb"]


def lies_teilplaene(
    dokument: PdfDokument,
    jahrgang: Jahrgang,
    seiten: pl.DataFrame,
    hierarchie: pl.DataFrame,
    *,
    ebenen: Collection[str],
) -> tuple[pl.DataFrame, pl.DataFrame]:
    """Extrahiert Teilergebnis-/Teilfinanzpläne der verarbeiteten Ebenen (D-08, D-13, EXTR-04/05).

    Iteriert alle als teilergebnisplan/teilfinanzplan klassifizierten Seiten in Seitenreihenfolge,
    zerlegt jede Seite über `lies_abschnitte` und ordnet jeden Abschnitt dem Knoten (PB, PG oder
    Produkt) der Seite zu. Nur Knoten, deren Ebene in `ebenen` liegt, werden verarbeitet.
    Vollständigkeit (D-08): jeder erwartete, nicht-synthetische Knoten der verarbeiteten Ebenen
    braucht genau einen Teilergebnisplan- und mindestens einen Teilfinanzplan-Abschnitt; eine
    Zeilennummer darf innerhalb eines Knotens/Plantyps nicht zweimal vorkommen.
    """
    relevante_typen = ("teilergebnisplan", "teilfinanzplan")
    teilplan_seiten = seiten.filter(pl.col("typ").is_in(relevante_typen)).sort("pdf_seite")

    ergebnisplan_datensaetze: list[dict[str, object]] = []
    finanzplan_datensaetze: list[dict[str, object]] = []
    gesehene_zeilen: dict[tuple[str, str, str], dict[str, int]] = {}
    teilergebnisplan_abschnitte: dict[tuple[str, str], int] = {}
    teilfinanzplan_knoten: set[tuple[str, str]] = set()

    for seite in teilplan_seiten.iter_rows(named=True):
        ebene, code = _knoten_fuer_seite(seite)
        if ebene not in ebenen:
            continue

        pdf_seite = seite["pdf_seite"]
        zeilen = dokument.zeilen(pdf_seite)
        for abschnitt in lies_abschnitte(zeilen, jahrgang, pdf_seite):
            if abschnitt.plantyp == "teilergebnisplan":
                spalten = jahrgang.spalten["ergebnisplan"]
                ziel = ergebnisplan_datensaetze
                teilergebnisplan_abschnitte[(ebene, code)] = (
                    teilergebnisplan_abschnitte.get((ebene, code), 0) + 1
                )
            else:
                spalten = jahrgang.spalten["finanzplan"]
                ziel = finanzplan_datensaetze
                if abschnitt.fortsetzung and (ebene, code) not in teilfinanzplan_knoten:
                    raise PlaeneFehler(
                        f"S. {pdf_seite}: Fortsetzung des Teilfinanzplans ohne vorherigen "
                        f"Abschnitt für {ebene} {code}"
                    )
                teilfinanzplan_knoten.add((ebene, code))

            gedruckte_zeilen = lies_plantabelle(
                abschnitt.zeilen, plantyp=abschnitt.plantyp, spalten=spalten, pdf_seite=pdf_seite
            )
            zeilen_definition = ZEILEN[abschnitt.plantyp]
            knoten_schluessel = (ebene, code, abschnitt.plantyp)
            bereits_gesehen = gesehene_zeilen.setdefault(knoten_schluessel, {})
            for gedruckt in gedruckte_zeilen:
                if gedruckt.zeile in bereits_gesehen:
                    raise PlaeneFehler(
                        f"{ebene} {code} ({abschnitt.plantyp}): Zeile {gedruckt.zeile} kommt auf "
                        f"S. {bereits_gesehen[gedruckt.zeile]} und S. {pdf_seite} doppelt vor"
                    )
                bereits_gesehen[gedruckt.zeile] = pdf_seite
                definition = zeilen_definition[gedruckt.zeile]
                for spaltenkopf, betrag in zip(spalten, gedruckt.werte, strict=True):
                    wertart, jahr = zerlege_spaltenkopf(spaltenkopf)
                    ziel.append(
                        {
                            "ebene": ebene,
                            "code": code,
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

    erwartete_knoten = hierarchie.filter(
        pl.col("ebene").is_in(list(ebenen)) & ~pl.col("synthetisch")
    )
    for knoten in erwartete_knoten.iter_rows(named=True):
        schluessel = (knoten["ebene"], knoten["code"])
        anzahl_teg = teilergebnisplan_abschnitte.get(schluessel, 0)
        if anzahl_teg != 1:
            raise PlaeneFehler(
                f"{knoten['ebene']} {knoten['code']}: {anzahl_teg} Teilergebnisplan-Abschnitte "
                "gefunden, erwartet genau 1"
            )
        if schluessel not in teilfinanzplan_knoten:
            raise PlaeneFehler(
                f"{knoten['ebene']} {knoten['code']}: kein Teilfinanzplan-Abschnitt gefunden"
            )

    return (
        pl.DataFrame(ergebnisplan_datensaetze, schema=PLAN_SPALTEN),
        pl.DataFrame(finanzplan_datensaetze, schema=PLAN_SPALTEN),
    )


def _synthetische_pg_datensaetze(
    teil_df: pl.DataFrame, hierarchie: pl.DataFrame, plantyp: str
) -> list[dict[str, object]]:
    """Baut synthetische-PG-Zeilen als exakte Kopie der Zeilen ihres einzigen Kind-
    Produkts (D-14, 261001-oim: jede synthetische PG hat genau ein Produkt).

    Mitgliedschaft kommt ausschließlich aus `hierarchie.eltern_code` (P-Zeilen, deren
    eltern_code dem PG-Code entspricht) — keine erneute Ableitung aus einem Code-
    Präfix, keine Summenbildung. Fehler (D-08): eine synthetische PG mit einer Kind-
    Anzahl ungleich 1, oder ein Kind ohne Zeilen in `teil_df`.
    """
    synthetische_pg = hierarchie.filter((pl.col("ebene") == "PG") & pl.col("synthetisch"))
    if synthetische_pg.height == 0:
        return []

    p_zeilen = hierarchie.filter(pl.col("ebene") == "P")

    datensaetze: list[dict[str, object]] = []
    for pg in synthetische_pg.iter_rows(named=True):
        pg_code = pg["code"]
        kinder = p_zeilen.filter(pl.col("eltern_code") == pg_code)["code"].to_list()
        if len(kinder) != 1:
            raise PlaeneFehler(
                f"PG {pg_code}: synthetische Produktgruppe hat {len(kinder)} Produkte "
                "als Kinder, erwartet genau 1 (D-14)"
            )
        kind_code = kinder[0]
        kind_zeilen = teil_df.filter((pl.col("ebene") == "P") & (pl.col("code") == kind_code))
        if kind_zeilen.height == 0:
            raise PlaeneFehler(f"PG {pg_code}: Produkt {kind_code} hat keine Planzeilen")

        for zeile in kind_zeilen.iter_rows(named=True):
            datensatz = dict(zeile)
            datensatz["ebene"] = "PG"
            datensatz["code"] = pg_code
            datensatz["synthetisch"] = True
            datensaetze.append(datensatz)
    return datensaetze


def extrahiere_plaene(
    jahrgang: Jahrgang, *, daten_wurzel: Path = DATEN_WURZEL
) -> tuple[ExtraktionsErgebnis, ExtraktionsErgebnis]:
    """Extrahiert Gesamt- und alle Teilpläne (PB, PG, Produkt) nach daten_wurzel (EXTR-04/05).

    Liest `seiten.csv` und `hierarchie.csv` aus `daten_wurzel`, hängt die Teilplanzeilen
    (gedruckte und synthetische PG, D-14) an die GESAMT-Zeilen beider Dateien an und
    schreibt beide CSVs einmal.
    """
    seiten = lies_seiten_csv(daten_wurzel / SEITEN_CSV)
    hierarchie = lies_hierarchie_csv(daten_wurzel / HIERARCHIE_CSV)

    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        gesamt_ergebnisplan = _gesamtplan_datensaetze(dokument, jahrgang, datei="ergebnisplan")
        gesamt_finanzplan = _gesamtplan_datensaetze(dokument, jahrgang, datei="finanzplan")
        teil_ergebnisplan, teil_finanzplan = lies_teilplaene(
            dokument, jahrgang, seiten, hierarchie, ebenen=("PB", "PG", "P")
        )

    synthetisch_ergebnisplan = _synthetische_pg_datensaetze(
        teil_ergebnisplan, hierarchie, "teilergebnisplan"
    )
    synthetisch_finanzplan = _synthetische_pg_datensaetze(
        teil_finanzplan, hierarchie, "teilfinanzplan"
    )

    ergebnisplan_df = pl.concat(
        [
            pl.DataFrame(gesamt_ergebnisplan, schema=PLAN_SPALTEN),
            teil_ergebnisplan,
            pl.DataFrame(synthetisch_ergebnisplan, schema=PLAN_SPALTEN),
        ]
    )
    finanzplan_df = pl.concat(
        [
            pl.DataFrame(gesamt_finanzplan, schema=PLAN_SPALTEN),
            teil_finanzplan,
            pl.DataFrame(synthetisch_finanzplan, schema=PLAN_SPALTEN),
        ]
    )

    ergebnisplan_pfad = daten_wurzel / ERGEBNISPLAN_CSV
    finanzplan_pfad = daten_wurzel / FINANZPLAN_CSV
    schreibe_plan_csv(ergebnisplan_df, ergebnisplan_pfad)
    schreibe_plan_csv(finanzplan_df, finanzplan_pfad)
    return (
        ExtraktionsErgebnis(zeilen_geschrieben=ergebnisplan_df.height, pfad=ergebnisplan_pfad),
        ExtraktionsErgebnis(zeilen_geschrieben=finanzplan_df.height, pfad=finanzplan_pfad),
    )
