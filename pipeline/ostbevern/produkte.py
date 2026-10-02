"""Schritt 03: Produktinformationen und Erläuterungen (Spez. 2.1, 4.2, 5.2).

Liest die "Produktinformationen"-Seiten aller 63 Produkte (Fachbereich, Gremium,
Beschreibung, Leistungen, Auftragsgrundlage, Bindungsgrad, Klassifizierung, Zielgruppe,
Ziele) und schreibt `produkte.json` (EXTR-06). Personenfelder ("Verantwortliche/r",
"Sachbearbeiter/innen") werden beim Parsen als Felder erkannt, um die Feldstruktur der
Seite zu verstehen, aber sofort danach verworfen und erreichen nie einen Datensatz,
ein Dict oder eine Datei (D-09, Datenschutz, da `daten/` eingecheckt wird).

Liest außerdem die Erläuterungsblöcke der Teilergebnisplan-Seiten (EXTR-08, D-01 bis
D-04) und schreibt `erlaeuterungen.csv` sowie eine Einbettung unter `erlaeuterungen` in
`produkte.json`; eine D-04-Plausibilitätsprüfung (Zeile gedruckt, Posten nicht größer
als die Summe der referenzierten Zeilen) bricht bei einem Verstoß ab.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import polars as pl

from ostbevern.freitext import ersetze_eurozeichen, verbinde_zeilen
from ostbevern.konfiguration import Jahrgang, layout_text
from ostbevern.pdf import PdfDokument, Textzeile, Wort
from ostbevern.schema import (
    DATEN_WURZEL,
    ERGEBNISPLAN_CSV,
    ERLAEUTERUNGEN_CSV,
    GRUNDZAHLEN_CSV,
    HIERARCHIE_CSV,
    PRODUKTE_JSON,
    SEITEN_CSV,
    lies_hierarchie_csv,
    lies_plan_csv,
    lies_seiten_csv,
    schreibe_erlaeuterungen_csv,
    schreibe_grundzahlen_csv,
    schreibe_produkte_json,
)
from ostbevern.spalten import SpaltenFehler, ordne_spalten
from ostbevern.zahlen import ZahlenFehler, lies_betrag, lies_kennzahl

# Toleranz für die Körpertext-Schriftgröße (die Größe der ersten Feld-Kopfzeile; Lauf-
# köpfe, Titel und Seitenzahlen haben andere Größen, Phase 3 zerlege_felder) und für die
# x-Koordinaten-Zuordnung innerhalb der Leistungen-Aufzählung (bündig mit der jeweiligen
# Spaltenanker-Logik in investitionen.py/querschnitte.py).
_GROESSEN_TOLERANZ = 0.5
_LEISTUNGEN_X_TOLERANZ = 3.0
# Toleranz für die Posten-Fortsetzungszeile (D-01): eine Folgezeile, deren x0 mindestens
# die Text-x0 des Postens minus dieser Toleranz erreicht, gehört noch zum selben Posten.
_POSTEN_X_TOLERANZ = 2.0
# Satzende-Satzzeichen (D-01): nach einer dieser Zeichen beginnt eine neue Freitextzeile
# einen neuen Eintrag statt den vorherigen fortzusetzen.
_SATZENDE_ZEICHEN = (".", ":", "!", "?")
# Grundzahlen-Spaltenzonen (03-05, EXTR-07, D-12/D-13): die Label-Zone endet und die
# Einheit-Zone beginnt diese Toleranz links der x0 des Worts "Einheit" (verifiziert gegen
# das echte PDF: "Einheit" x0 ~297, erstes Jahreswort x0 ~347 — kein gedrucktes Wort
# liegt je zwischen x0("Einheit")-6 und x0("Einheit")).
_GRUNDZAHLEN_EINHEIT_TOLERANZ = 6.0


class ProdukteFehler(ValueError):
    """Wird ausgelöst, wenn eine Produktinformationen- oder Erläuterungs-Seite oder
    -Zeile nicht lesbar ist, oder ein gelesener Wert nicht zum Vokabular passt (D-08)."""


# Fachliche Datenschutzregel (D-09): diese beiden Feldnamen werden in zerlege_felder wie
# jedes andere Feld erkannt (die Seitenstruktur braucht sie), aber nie in einen
# Produktinfo-Datensatz übernommen und nie geschrieben.
PERSONENFELDER: tuple[str, ...] = ("verantwortlich", "sachbearbeiter")

# Normalisierung des Bindungsgrads (Claude's Ermessen, CONTEXT.md): ein unbekannter
# gedruckter Wert bricht ab (D-08), kein stiller Standardwert.
BINDUNGSGRADE: dict[str, str] = {
    "pflichtig": "pflichtig",
    "freiwillig": "freiwillig",
    "teils pflichtig teils freiwillig": "teils",
    "teils freiwillig teils pflichtig": "teils",
}

KLASSIFIZIERUNGEN: frozenset[str] = frozenset({"extern", "intern", "extern und intern"})


@dataclass(frozen=True)
class ExtraktionsErgebnis:
    """Ergebnis von `extrahiere_produkte`: Anzahl geschriebener Datensätze/Zeilen und
    Zielpfad je geschriebener Datei (wie plaene.py/investitionen.py)."""

    zeilen_geschrieben: int
    pfad: Path


@dataclass(frozen=True)
class Produktinfo:
    """Eine gelesene Produktinformationen-Seite (oder zwei, 010901) ohne Personenfelder
    (D-09, D-10, D-11)."""

    code: str
    name: str
    pb: str
    pg: str
    fachbereich: str
    gremium: str
    beschreibung: str
    leistungen: tuple[str, ...]
    auftragsgrundlage: str
    bindungsgrad: str
    bindungsgrad_original: str
    klassifizierung: str
    zielgruppe: str
    ziele: str
    pdf_seiten: tuple[int, ...]


@dataclass(frozen=True)
class Erlaeuterung:
    """Ein Erläuterungs-Blockeintrag (Posten oder Freitext, EXTR-08, D-01 bis D-03).

    `zu_zeilen` ist leer, wenn der Block kein "zu Nr." trägt (D-02). `betrag` ist
    `None` für eine Freitextzeile. `block` und `position` sind 1-basiert in Lesereihen-
    folge je Produkt.
    """

    produkt: str
    block: int
    position: int
    zu_zeilen: tuple[str, ...]
    betrag: int | None
    text: str
    pdf_seite: int


def _label_zu_feld(jahrgang: Jahrgang) -> dict[str, str]:
    """Löst jedes konfigurierte Feld-Label auf seinen Feldnamen auf (PERSONENFELDER
    eingeschlossen; sie werden erst in `lies_produktinformationen` verworfen)."""
    felder = ("fachbereich", *PERSONENFELDER, "gremium", "beschreibung", "auftragsgrundlage")
    felder += ("bindungsgrad", "klassifizierung", "zielgruppe", "ziele")
    return {layout_text(jahrgang, "produktinformationen", feld): feld for feld in felder}


def zerlege_felder(
    seiten_zeilen: Sequence[tuple[int, tuple[Textzeile, ...]]], jahrgang: Jahrgang
) -> dict[str, list[tuple[int, Textzeile]]]:
    """Segmentiert die Fein-Zeilen der Produktinformationen-Seite(n) eines Produkts nach
    Feld (Spez. 2.1).

    Körpertext-Zeilen sind jene mit derselben Schriftgröße wie die erste gefundene
    Feld-Kopfzeile (Laufköpfe, Titel und Seitenzahlen haben andere Größen; das erkennt
    auch die titellose zweite Seite, 010901). Eine fette Zeile, deren erstes Wort einem
    konfigurierten Label entspricht, startet dieses Feld (der Rest der Zeile ist ihre
    erste Wertzeile, inklusive Label-Wort — `lies_produktinformationen` trennt es ab,
    außer für `fachbereich`). Eine fette Zeile, die `leistungen_muster` entspricht,
    startet das virtuelle Feld "leistungen". Die `grundzahlen_kopf`-Zeile beendet den
    Produktinformationen-Block vollständig. Fortsetzung-Zeilen werden übersprungen. Eine
    Zeile vor dem ersten Feld bricht ab.
    """
    label_zu_feld = _label_zu_feld(jahrgang)
    leistungen_muster = re.compile(
        layout_text(jahrgang, "produktinformationen", "leistungen_muster")
    )
    grundzahlen_kopf = layout_text(jahrgang, "produktinformationen", "grundzahlen_kopf")
    fortsetzung_normalisiert = "".join(jahrgang.kopfzeilen.fortsetzung.split())

    felder: dict[str, list[tuple[int, Textzeile]]] = {}
    aktuelles_feld: str | None = None
    erste_groesse: float | None = None

    for pdf_seite, zeilen in seiten_zeilen:
        for zeile in zeilen:
            if not zeile.woerter:
                continue
            fett_erstes_wort = zeile.woerter[0].fett
            erstes_wort = zeile.woerter[0].text

            if erste_groesse is None:
                if fett_erstes_wort and erstes_wort in label_zu_feld:
                    erste_groesse = zeile.groesse
                else:
                    continue
            elif abs(zeile.groesse - erste_groesse) > _GROESSEN_TOLERANZ:
                continue

            text_ns = zeile.text_ohne_leerzeichen
            if fett_erstes_wort and text_ns.startswith(grundzahlen_kopf):
                return felder
            if text_ns.startswith(fortsetzung_normalisiert):
                continue

            if fett_erstes_wort and erstes_wort in label_zu_feld:
                aktuelles_feld = label_zu_feld[erstes_wort]
                felder.setdefault(aktuelles_feld, []).append((pdf_seite, zeile))
                continue
            if fett_erstes_wort and leistungen_muster.match(zeile.text):
                aktuelles_feld = "leistungen"
                felder.setdefault(aktuelles_feld, []).append((pdf_seite, zeile))
                continue

            if aktuelles_feld is None:
                raise ProdukteFehler(
                    f"S. {pdf_seite}: Zeile vor dem ersten Produktinformationen-Feld"
                )
            felder[aktuelles_feld].append((pdf_seite, zeile))

    return felder


def _feld_text(eintraege: Sequence[tuple[int, Textzeile]] | None, *, label_behalten: bool) -> str:
    """Verbindet die Wertzeilen eines Feldes zu lesbarem Fließtext (D-10, D-11).

    Die erste Zeile trägt noch das Label-Wort; es wird abgetrennt, außer
    `label_behalten` ist gesetzt (nur `fachbereich`, Spez. 4.2: "Fachbereich I/Schulen").
    """
    if not eintraege:
        return ""
    teile: list[str] = []
    for index, (_, zeile) in enumerate(eintraege):
        if index == 0 and not label_behalten:
            text = " ".join(wort.text for wort in zeile.woerter[1:])
        else:
            text = zeile.text
        if text:
            teile.append(text)
    if not teile:
        return ""
    return ersetze_eurozeichen(verbinde_zeilen(teile))


def _baue_leistungen(
    eintraege: Sequence[tuple[int, Textzeile]] | None, jahrgang: Jahrgang
) -> tuple[str, ...]:
    """Zerlegt die Rohzeilen des virtuellen Feldes "leistungen" in einzelne Einträge:
    ein Eintrag je Aufzählungspunkt (D-11), ein Eintrag je Unterüberschrift ohne
    Aufzählungszeichen (Claude's Ermessen, CONTEXT.md), und die auslösende
    Leistungen-Label-Zeile selbst, falls sie mehr als nur das Label-Wort trägt
    (010602, S. 88: "Leistungen , die unter anderen Produkten veranschlagt werden:")."""
    if not eintraege:
        return ()
    aufzaehlungszeichen = layout_text(jahrgang, "produktinformationen", "aufzaehlungszeichen")

    eintraege_text: list[str] = []
    aktuelle_teile: list[str] = []
    anker_x0: float | None = None
    wartet_auf_bullet_text = False

    def schliesse() -> None:
        nonlocal aktuelle_teile
        if aktuelle_teile:
            eintraege_text.append(ersetze_eurozeichen(verbinde_zeilen(aktuelle_teile)))
        aktuelle_teile = []

    for index, (_, zeile) in enumerate(eintraege):
        if index == 0:
            # Die auslösende Leistungen-Label-Zeile: nur ein eigener Eintrag, wenn mehr
            # als das bloße Label-Wort gedruckt ist (sonst wäre leistungen[0] immer nur
            # "Leistungen:").
            if len(zeile.woerter) > 1:
                aktuelle_teile = [zeile.text]
                schliesse()
            continue

        text_ns = zeile.text_ohne_leerzeichen
        if text_ns == aufzaehlungszeichen:
            schliesse()
            wartet_auf_bullet_text = True
            continue
        if wartet_auf_bullet_text:
            schliesse()
            aktuelle_teile = [zeile.text]
            anker_x0 = zeile.x0
            wartet_auf_bullet_text = False
            continue
        if anker_x0 is not None and abs(zeile.x0 - anker_x0) <= _LEISTUNGEN_X_TOLERANZ:
            aktuelle_teile.append(zeile.text)
            continue

        schliesse()
        aktuelle_teile = [zeile.text]
        anker_x0 = zeile.x0

    schliesse()
    return tuple(eintraege_text)


@dataclass(frozen=True)
class Grundzahl:
    """Eine gelesene Grundzahlen-Zeile für ein Jahr (EXTR-07, D-12, D-13).

    `wert` ist Float64 plus `nachkommastellen` (Claude's Ermessen, CONTEXT.md):
    Grundzahlen enthalten Dezimalwerte (Gebühren, Quoten) neben Ganzzahlen (Euro-
    Beträge), die Float64 mit `nachkommastellen=0` exakt darstellt. `gruppe` ist
    `None` ohne Gruppenüberschrift; `hinweis` ist `None` ohne Stichtag-/Fußnotentext.
    `position` ist 1-basiert in gedruckter Zeilenreihenfolge je Produkt (eine Position
    je gedruckter Tabellenzeile, unabhängig davon, wie viele Jahre einen Wert tragen).
    """

    produkt: str
    position: int
    gruppe: str | None
    bezeichnung: str
    einheit: str
    jahr: int
    wert: float
    nachkommastellen: int
    hinweis: str | None
    pdf_seite: int


@dataclass
class _RohGrundzahlenZeile:
    """Veränderlicher Baustein für eine Grundzahlen-Zeile, während Bezeichnung/Einheit
    noch durch Fortsetzungszeilen wachsen können (D-13)."""

    position: int
    gruppe: str | None
    bezeichnung_teile: list[str]
    einheit: str
    werte: dict[int, tuple[float, int]]
    pdf_seite: int


def _grundzahlen_zonen(
    zeile: Textzeile, *, x0_einheit: float, erste_jahr_x0: float, pdf_seite: int, produkt: str
) -> tuple[list[Wort], list[Wort], list[Wort]]:
    """Teilt die Wörter einer Grundzahlen-Zeile in (Label, Einheit, Werte) (D-12/D-13).

    Label = Wörter mit x1 < x0(Einheit) - Toleranz; Einheit = x0 >= x0(Einheit) -
    Toleranz und x1 <= erste_jahr_x0; Werte = x1 > erste_jahr_x0. Ein Wort außerhalb
    aller drei Zonen bricht ab (Behavior: "value outside every column zone").
    """
    label_grenze = x0_einheit - _GRUNDZAHLEN_EINHEIT_TOLERANZ
    label_woerter: list[Wort] = []
    einheit_woerter: list[Wort] = []
    werte_woerter: list[Wort] = []
    for wort in zeile.woerter:
        if wort.x1 < label_grenze:
            label_woerter.append(wort)
        elif wort.x0 >= label_grenze and wort.x1 <= erste_jahr_x0:
            einheit_woerter.append(wort)
        elif wort.x1 > erste_jahr_x0:
            werte_woerter.append(wort)
        else:
            raise ProdukteFehler(
                f"S. {pdf_seite}: Wort {wort.text!r} liegt in keiner Grundzahlen-Spalte "
                f"(Produkt {produkt})"
            )
    return label_woerter, einheit_woerter, werte_woerter


def _normalisiere_grundzahlen_einheit(einheit: str, eurozeichen: str) -> str:
    """Normalisiert das Euro-Glyph "C" zu "EUR"/"EUR/..." (D-13, Spez. 2.2)."""
    if einheit == eurozeichen:
        return "EUR"
    praefix = f"{eurozeichen}/"
    if einheit.startswith(praefix):
        return f"EUR/{einheit[len(praefix) :]}"
    return einheit


def _lies_grundzahlen_produkt(
    dokument: PdfDokument,
    produkt: str,
    pdf_seiten: Sequence[int],
    *,
    kopf: str,
    einheit_label: str,
    fussnote_jahr_muster: re.Pattern[str],
    fussnote_allgemein_muster: re.Pattern[str],
    eurozeichen: str,
    fortsetzung_normalisiert: str,
) -> list[Grundzahl]:
    position = 0
    gruppe: str | None = None
    allgemeine_fussnoten: list[str] = []
    jahr_fussnoten: dict[int, list[str]] = {}
    stempel_jahre: set[int] = set()
    stempel_text: str | None = None
    rohzeilen: list[_RohGrundzahlenZeile] = []

    for pdf_seite in pdf_seiten:
        zeilen = dokument.zeilen_fein(pdf_seite)
        aktiv = False
        anker_x1: tuple[float, ...] = ()
        jahr_woerter: tuple[Wort, ...] = ()
        x0_einheit: float = 0.0
        erste_jahr_x0: float = 0.0
        index = 0

        while index < len(zeilen):
            zeile = zeilen[index]
            text_ns = zeile.text_ohne_leerzeichen
            erstes_wort = zeile.woerter[0] if zeile.woerter else None

            if not aktiv:
                if erstes_wort is not None and erstes_wort.fett and erstes_wort.text == kopf:
                    einheit_wort = next((w for w in zeile.woerter if w.text == einheit_label), None)
                    if einheit_wort is None:
                        raise ProdukteFehler(
                            f"S. {pdf_seite}: Grundzahlen-Kopf ohne {einheit_label!r} "
                            f"(Produkt {produkt})"
                        )
                    x0_einheit = einheit_wort.x0
                    jahr_zeile = zeilen[index + 1]
                    jahr_woerter = jahr_zeile.woerter
                    anker_x1 = tuple(w.x1 for w in jahr_woerter)
                    erste_jahr_x0 = jahr_woerter[0].x0
                    aktiv = True
                    index += 2
                    continue
                index += 1
                continue

            if text_ns == str(pdf_seite) or text_ns.startswith(fortsetzung_normalisiert):
                break

            ist_fett = erstes_wort is not None and erstes_wort.fett

            # Bold-Zeilen (Stempel, Fußnoten, Gruppenüberschriften) sind nie eine
            # Datenzeile (Rows sind stets unfett, verifiziert gegen das echte PDF) und
            # werden VOR jeder Zonen-Klassifikation behandelt: ihr Text kann Wörter
            # enthalten, die über die Label-/Einheit-Grenze hinweg reichen (z. B. das
            # letzte Wort einer Zwei-Jahre-Fußnote wie "Ist-Werte ... und Prognose ...",
            # S. 103) und würden die strikte Drei-Zonen-Prüfung einer echten Datenzeile
            # fälschlich als "in keiner Spalte" ablehnen.
            if ist_fett:
                if all(w.x0 >= erste_jahr_x0 for w in zeile.woerter):
                    letztes_wort = zeile.woerter[-1]
                    try:
                        zugeordnet = ordne_spalten([letztes_wort], anker_x1)
                    except SpaltenFehler as fehler:
                        raise ProdukteFehler(f"S. {pdf_seite}: {fehler}") from fehler
                    (spalten_index,) = zugeordnet
                    stempel_jahre.add(int(jahr_woerter[spalten_index].text))
                    stempel_text = zeile.text
                    index += 1
                    continue
                jahr_treffer = fussnote_jahr_muster.match(zeile.text)
                if jahr_treffer:
                    for jahr in (int(j) for j in re.findall(r"\d{4}", jahr_treffer.group("jahre"))):
                        jahr_fussnoten.setdefault(jahr, []).append(zeile.text)
                    index += 1
                    continue
                if fussnote_allgemein_muster.search(zeile.text):
                    allgemeine_fussnoten.append(zeile.text)
                    index += 1
                    continue
                gruppe = zeile.text
                index += 1
                continue

            label_woerter, einheit_woerter, werte_woerter = _grundzahlen_zonen(
                zeile,
                x0_einheit=x0_einheit,
                erste_jahr_x0=erste_jahr_x0,
                pdf_seite=pdf_seite,
                produkt=produkt,
            )

            if werte_woerter:
                if not einheit_woerter:
                    raise ProdukteFehler(
                        f"S. {pdf_seite}: Grundzahlen-Zeile ohne Einheit (Produkt {produkt})"
                    )
                try:
                    zugeordnet = ordne_spalten(werte_woerter, anker_x1)
                except SpaltenFehler as fehler:
                    raise ProdukteFehler(f"S. {pdf_seite}: {fehler}") from fehler
                werte: dict[int, tuple[float, int]] = {}
                for spalten_index, wort in zugeordnet.items():
                    jahr = int(jahr_woerter[spalten_index].text)
                    try:
                        geparst = lies_kennzahl(wort.text)
                    except ZahlenFehler as fehler:
                        raise ProdukteFehler(f"S. {pdf_seite}: {fehler}") from fehler
                    if geparst is not None:
                        werte[jahr] = geparst
                position += 1
                rohzeilen.append(
                    _RohGrundzahlenZeile(
                        position=position,
                        gruppe=gruppe,
                        bezeichnung_teile=(
                            [" ".join(w.text for w in label_woerter)] if label_woerter else []
                        ),
                        einheit=" ".join(w.text for w in einheit_woerter),
                        werte=werte,
                        pdf_seite=pdf_seite,
                    )
                )
                index += 1
                continue

            if not rohzeilen:
                raise ProdukteFehler(
                    f"S. {pdf_seite}: Grundzahlen-Fortsetzungszeile ohne vorherige Zeile "
                    f"(Produkt {produkt})"
                )
            letzte = rohzeilen[-1]
            if label_woerter:
                letzte.bezeichnung_teile.append(" ".join(w.text for w in label_woerter))
            if einheit_woerter:
                letzte.einheit += "".join(w.text for w in einheit_woerter)
            index += 1

    def _hinweis(jahr: int) -> str | None:
        teile = list(allgemeine_fussnoten)
        if jahr in jahr_fussnoten:
            teile.extend(jahr_fussnoten[jahr])
        elif jahr in stempel_jahre and stempel_text is not None:
            teile.append(stempel_text)
        return "; ".join(teile) if teile else None

    ergebnisse: list[Grundzahl] = []
    for roh in rohzeilen:
        bezeichnung = (
            ersetze_eurozeichen(verbinde_zeilen(roh.bezeichnung_teile))
            if roh.bezeichnung_teile
            else ""
        )
        if not bezeichnung:
            raise ProdukteFehler(
                f"S. {roh.pdf_seite}: Grundzahlen-Zeile ohne Bezeichnung (Produkt {produkt})"
            )
        einheit = _normalisiere_grundzahlen_einheit(roh.einheit, eurozeichen)
        for jahr, (wert, nachkommastellen) in sorted(roh.werte.items()):
            ergebnisse.append(
                Grundzahl(
                    produkt=produkt,
                    position=roh.position,
                    gruppe=roh.gruppe,
                    bezeichnung=bezeichnung,
                    einheit=einheit,
                    jahr=jahr,
                    wert=wert,
                    nachkommastellen=nachkommastellen,
                    hinweis=_hinweis(jahr),
                    pdf_seite=roh.pdf_seite,
                )
            )
    return ergebnisse


def lies_grundzahlen(
    dokument: PdfDokument, jahrgang: Jahrgang, seiten: pl.DataFrame, hierarchie: pl.DataFrame
) -> list[Grundzahl]:
    """Liest die Grundzahlen-Tabellen aller Produkte (EXTR-07, D-12, D-13).

    Scannt je Produkt seine Produktinformationen- UND grundzahlen-typisierten Seiten
    (Seitenreihenfolge): die Tabelle kann auf der Produktinformationen-Seite beginnen
    und auf einer eigenen, fortsetzenden `grundzahlen`-Seite weiterlaufen (jede Seite
    druckt den Tabellenkopf neu, wie investitionen.lies_massnahmen). Produkte ohne
    Grundzahlen-Tabelle (15 von 63) liefern keinen Eintrag.
    """
    kopf = layout_text(jahrgang, "grundzahlen", "kopf")
    einheit_label = layout_text(jahrgang, "grundzahlen", "einheit")
    fussnote_jahr_muster = re.compile(layout_text(jahrgang, "grundzahlen", "fussnote_jahr_muster"))
    fussnote_allgemein_muster = re.compile(
        layout_text(jahrgang, "grundzahlen", "fussnote_allgemein_muster")
    )
    eurozeichen = layout_text(jahrgang, "grundzahlen", "eurozeichen")
    fortsetzung_normalisiert = "".join(jahrgang.kopfzeilen.fortsetzung.split())

    gz_seiten = seiten.filter(
        pl.col("produkt").is_not_null()
        & pl.col("typ").is_in(("produktinformationen", "grundzahlen"))
    ).sort(["produkt", "pdf_seite"])

    alle: list[Grundzahl] = []
    for produkt in sorted(gz_seiten["produkt"].unique().to_list()):
        pdf_seiten = tuple(gz_seiten.filter(pl.col("produkt") == produkt)["pdf_seite"].to_list())
        alle.extend(
            _lies_grundzahlen_produkt(
                dokument,
                produkt,
                pdf_seiten,
                kopf=kopf,
                einheit_label=einheit_label,
                fussnote_jahr_muster=fussnote_jahr_muster,
                fussnote_allgemein_muster=fussnote_allgemein_muster,
                eurozeichen=eurozeichen,
                fortsetzung_normalisiert=fortsetzung_normalisiert,
            )
        )
    return alle


def _zu_zeilen_aus_gruppe(gruppe: str) -> tuple[str, ...]:
    """Extrahiert alle ein- bis zweistelligen Zahlen aus der `zeilen`-Gruppe des
    `zu_nr_muster`-Treffers und normalisiert sie auf zweistellige Strings (D-02)."""
    return tuple(f"{int(zahl):02d}" for zahl in re.findall(r"\d{1,2}", gruppe))


def lies_erlaeuterungen(
    dokument: PdfDokument, jahrgang: Jahrgang, seiten: pl.DataFrame, hierarchie: pl.DataFrame
) -> list[Erlaeuterung]:
    """Liest die Erläuterungsblöcke aller Produkte von ihren Teilergebnisplan-Seiten
    (EXTR-08, D-01 bis D-03).

    Je Produkt wird ab der ersten `kopf_muster`-Zeile ("Erläuterung") gescannt, bis eine
    Zeile den Teilfinanzplan-Seitentyp, eine "Nr."-Kopfzeile, die Fortsetzung-Markierung
    oder die Seitenzahl trifft. Produkte ohne Erläuterung liefern keinen Eintrag.
    """
    kopf_muster = re.compile(layout_text(jahrgang, "erlaeuterungen", "kopf_muster"))
    zu_nr_muster = re.compile(layout_text(jahrgang, "erlaeuterungen", "zu_nr_muster"))
    posten_muster = re.compile(layout_text(jahrgang, "erlaeuterungen", "posten_muster"))
    fortsetzung_normalisiert = "".join(jahrgang.kopfzeilen.fortsetzung.split())
    teilfinanzplan_muster = jahrgang.kopfzeilen.seitentypen["teilfinanzplan"]

    teg_seiten = seiten.filter(
        pl.col("produkt").is_not_null() & (pl.col("typ") == "teilergebnisplan")
    ).sort(["produkt", "pdf_seite"])

    alle: list[Erlaeuterung] = []
    for produkt in sorted(teg_seiten["produkt"].unique().to_list()):
        pdf_seiten = tuple(teg_seiten.filter(pl.col("produkt") == produkt)["pdf_seite"].to_list())
        alle.extend(
            _lies_erlaeuterungen_produkt(
                dokument,
                produkt,
                pdf_seiten,
                kopf_muster=kopf_muster,
                zu_nr_muster=zu_nr_muster,
                posten_muster=posten_muster,
                fortsetzung_normalisiert=fortsetzung_normalisiert,
                teilfinanzplan_muster=teilfinanzplan_muster,
            )
        )
    return alle


def _lies_erlaeuterungen_produkt(
    dokument: PdfDokument,
    produkt: str,
    pdf_seiten: Sequence[int],
    *,
    kopf_muster: re.Pattern[str],
    zu_nr_muster: re.Pattern[str],
    posten_muster: re.Pattern[str],
    fortsetzung_normalisiert: str,
    teilfinanzplan_muster: str,
) -> list[Erlaeuterung]:
    ergebnisse: list[Erlaeuterung] = []
    block_nr = 0
    position = 0
    block_zu_zeilen: tuple[str, ...] = ()
    eintraege: list[dict[str, object]] = []
    in_scan = False

    def schliesse_block() -> None:
        nonlocal eintraege, position
        for eintrag in eintraege:
            position += 1
            text = ersetze_eurozeichen(verbinde_zeilen(eintrag["teile"]))
            ergebnisse.append(
                Erlaeuterung(
                    produkt=produkt,
                    block=block_nr,
                    position=position,
                    zu_zeilen=block_zu_zeilen,
                    betrag=eintrag["betrag"],
                    text=text,
                    pdf_seite=eintrag["pdf_seite"],
                )
            )
        eintraege = []

    def oeffne_block(zu_zeilen: tuple[str, ...], rest_text: str, pdf_seite: int) -> None:
        nonlocal block_zu_zeilen, block_nr
        schliesse_block()
        block_nr += 1
        block_zu_zeilen = zu_zeilen
        if rest_text:
            eintraege.append({"betrag": None, "teile": [rest_text], "pdf_seite": pdf_seite})

    for pdf_seite in pdf_seiten:
        zeilen = dokument.zeilen_fein(pdf_seite)
        for zeile in zeilen:
            text_ns = zeile.text_ohne_leerzeichen

            if not in_scan:
                if zeile.woerter and zeile.woerter[0].fett and kopf_muster.match(zeile.text):
                    in_scan = True
                else:
                    continue

            if text_ns == str(pdf_seite) or text_ns.startswith(fortsetzung_normalisiert):
                schliesse_block()
                return ergebnisse
            if re.match(teilfinanzplan_muster, text_ns) or (
                zeile.woerter and zeile.woerter[0].text == "Nr."
            ):
                schliesse_block()
                return ergebnisse

            ist_label_zeile = bool(zeile.woerter) and zeile.woerter[0].fett
            zu_nr_treffer = zu_nr_muster.match(zeile.text) if ist_label_zeile else None
            if zu_nr_treffer:
                zu_zeilen = _zu_zeilen_aus_gruppe(zu_nr_treffer.group("zeilen"))
                rest = zu_nr_treffer.group("rest").strip()
                if rest.startswith(":"):
                    rest = rest[1:].strip()
                oeffne_block(zu_zeilen, rest, pdf_seite)
                continue
            if ist_label_zeile and kopf_muster.match(zeile.text):
                # Eine "Erläuterung"-Kopfzeile OHNE "zu Nr." (D-02, S. 184): leeres
                # zu_zeilen, der Rest der Zeile (Label-Wort abgetrennt) wird die erste
                # Freitextzeile.
                rest = " ".join(wort.text for wort in zeile.woerter[1:])
                oeffne_block((), rest, pdf_seite)
                continue

            posten_treffer = posten_muster.match(zeile.text)
            if posten_treffer:
                betrag = lies_betrag(posten_treffer.group("betrag"))
                eintraege.append(
                    {
                        "betrag": betrag,
                        "teile": [posten_treffer.group("text")],
                        "pdf_seite": pdf_seite,
                        "text_x0": zeile.woerter[2].x0 if len(zeile.woerter) > 2 else zeile.x0,
                    }
                )
                continue

            if (
                eintraege
                and eintraege[-1]["betrag"] is not None
                and zeile.x0 >= eintraege[-1]["text_x0"] - _POSTEN_X_TOLERANZ
            ):
                eintraege[-1]["teile"].append(zeile.text)
                continue

            if (
                eintraege
                and eintraege[-1]["betrag"] is None
                and not eintraege[-1]["teile"][-1].rstrip().endswith(_SATZENDE_ZEICHEN)
            ):
                eintraege[-1]["teile"].append(zeile.text)
            else:
                eintraege.append({"betrag": None, "teile": [zeile.text], "pdf_seite": pdf_seite})

    schliesse_block()
    return ergebnisse


def pruefe_plausibilitaet(
    erlaeuterungen: Sequence[Erlaeuterung], ergebnisplan: pl.DataFrame, haushaltsjahr: int
) -> None:
    """D-04: jede `zu_zeilen`-Nummer eines POSTENS (ein Betrag ist angegeben) muss im
    Teilergebnisplan des Produkts gedruckt sein; kein Posten darf die Summe der
    referenzierten Zeilen (Ansatz Haushaltsjahr) übersteigen (die Posten sind
    ausdrücklich "u. a. enthalten", nie vollständig).

    Die Zeilen-Existenzprüfung gilt NUR für Postenzeilen (D-04 schützt die Zuordnung
    eines gedruckten BETRAGS zu einer Planzeile): verifiziert gegen das reale PDF
    verweisen drei reine Freitextzeilen (kein Betrag, S. 212/216/270) auf eine Zeile, die
    im Teilergebnisplan nicht gedruckt ist, weil ihr Wert 0 ist (Phase 2 D-11, "fehlende
    Zeile bedeutet 0") — der Freitext erklärt dort gerade, warum diese Kategorie dieses
    Jahr keinen Wert hat. Ohne Betrag gibt es keine Fehlzuordnung eines Geldbetrags zu
    verhindern; kein einziger der 119 echten Postenzeilen referenziert eine nicht
    gedruckte Zeile (verifiziert).
    """
    for erlaeuterung in erlaeuterungen:
        if not erlaeuterung.zu_zeilen or erlaeuterung.betrag is None:
            continue
        for zeile in erlaeuterung.zu_zeilen:
            treffer = ergebnisplan.filter(
                (pl.col("ebene") == "P")
                & (pl.col("code") == erlaeuterung.produkt)
                & (pl.col("zeile") == zeile)
            )
            if treffer.height == 0:
                raise ProdukteFehler(
                    f"S. {erlaeuterung.pdf_seite}: Erläuterung zu Nr. {zeile}: Zeile im "
                    f"Teilergebnisplan von {erlaeuterung.produkt} nicht gedruckt (D-04)"
                )
        summe = (
            ergebnisplan.filter(
                (pl.col("ebene") == "P")
                & (pl.col("code") == erlaeuterung.produkt)
                & pl.col("zeile").is_in(list(erlaeuterung.zu_zeilen))
                & (pl.col("jahr") == haushaltsjahr)
                & (pl.col("wertart") == "ansatz")
            )["betrag"].sum()
            or 0
        )
        if erlaeuterung.betrag > summe:
            raise ProdukteFehler(
                f"S. {erlaeuterung.pdf_seite}: Erläuterung (Produkt "
                f"{erlaeuterung.produkt}) Posten {erlaeuterung.betrag} übersteigt die "
                f"Summe der Zeilen {erlaeuterung.zu_zeilen} ({summe}) (D-04)"
            )


def lies_personennamen(
    dokument: PdfDokument, jahrgang: Jahrgang, seiten: pl.DataFrame, hierarchie: pl.DataFrame
) -> list[tuple[int, str]]:
    """Liest NUR die Personenfelder (Verantwortliche/r, Sachbearbeiter/innen) aller
    Produkte zurück: (erste Seite, vollständiger Feldwert, über alle seine Zeilen
    verbunden). Ausschließlich für `test_keine_personennamen` (D-09) — der
    Produktionscode ruft diese Funktion nie auf.

    Der Feldwert wird bewusst GANZ (nicht Zeile für Zeile) zurückgegeben: ein einzelnes
    Namenswort kann wortgleich mit einem völlig unabhängigen, öffentlichen Bestandteil
    an anderer Stelle kollidieren (verifiziert: ein Mitarbeiter-Nachname kommt auch im
    amtlichen Namen einer Schule vor, "Josef-<Nachname>-Schule", benannt nach einer
    historischen Person gleichen Namens). Der vollständige, mehrwortige Feldwert ist
    dagegen hinreichend spezifisch, um nicht zufällig an öffentlicher Stelle wörtlich
    wiederzukehren.
    """
    pi_seiten = seiten.filter(
        pl.col("produkt").is_not_null() & (pl.col("typ") == "produktinformationen")
    ).sort(["produkt", "pdf_seite"])

    namen: list[tuple[int, str]] = []
    for produkt in sorted(pi_seiten["produkt"].unique().to_list()):
        pdf_seiten = tuple(pi_seiten.filter(pl.col("produkt") == produkt)["pdf_seite"].to_list())
        seiten_zeilen = tuple((seite, dokument.zeilen_fein(seite)) for seite in pdf_seiten)
        felder = zerlege_felder(seiten_zeilen, jahrgang)
        for feld in PERSONENFELDER:
            eintraege = felder.get(feld)
            if not eintraege:
                continue
            text = _feld_text(eintraege, label_behalten=False)
            if text:
                namen.append((eintraege[0][0], text))
    return namen


def _baue_produktinfo(
    produkt: str,
    felder: dict[str, list[tuple[int, Textzeile]]],
    *,
    name: str,
    pg: str,
    pb: str,
    pdf_seiten: tuple[int, ...],
    jahrgang: Jahrgang,
) -> Produktinfo:
    def _pflichtfeld(feldname: str) -> str:
        wert = _feld_text(felder.get(feldname), label_behalten=feldname == "fachbereich")
        if not wert:
            seite = pdf_seiten[0] if pdf_seiten else 0
            raise ProdukteFehler(f"S. {seite}: {feldname} fehlt oder ist leer (Produkt {produkt})")
        return wert

    fachbereich = _pflichtfeld("fachbereich")
    gremium = _pflichtfeld("gremium")
    beschreibung = _pflichtfeld("beschreibung")
    auftragsgrundlage = _pflichtfeld("auftragsgrundlage")
    zielgruppe = _pflichtfeld("zielgruppe")
    ziele = _pflichtfeld("ziele")

    bindungsgrad_original = _pflichtfeld("bindungsgrad")
    bindungsgrad_seite = felder["bindungsgrad"][0][0]
    bindungsgrad = BINDUNGSGRADE.get(bindungsgrad_original)
    if bindungsgrad is None:
        raise ProdukteFehler(f"S. {bindungsgrad_seite}: Bindungsgrad unbekannt (Produkt {produkt})")

    klassifizierung = _pflichtfeld("klassifizierung")
    klassifizierung_seite = felder["klassifizierung"][0][0]
    if klassifizierung not in KLASSIFIZIERUNGEN:
        raise ProdukteFehler(
            f"S. {klassifizierung_seite}: Klassifizierung unbekannt (Produkt {produkt})"
        )

    leistungen = _baue_leistungen(felder.get("leistungen"), jahrgang)
    if not leistungen:
        seite = pdf_seiten[0] if pdf_seiten else 0
        raise ProdukteFehler(f"S. {seite}: Leistungen fehlen (Produkt {produkt})")

    return Produktinfo(
        code=produkt,
        name=name,
        pb=pb,
        pg=pg,
        fachbereich=fachbereich,
        gremium=gremium,
        beschreibung=beschreibung,
        leistungen=leistungen,
        auftragsgrundlage=auftragsgrundlage,
        bindungsgrad=bindungsgrad,
        bindungsgrad_original=bindungsgrad_original,
        klassifizierung=klassifizierung,
        zielgruppe=zielgruppe,
        ziele=ziele,
        pdf_seiten=pdf_seiten,
    )


def lies_produktinformationen(
    dokument: PdfDokument, jahrgang: Jahrgang, seiten: pl.DataFrame, hierarchie: pl.DataFrame
) -> list[Produktinfo]:
    """Liest die Produktinformationen aller Produkte (hierarchie Ebene P, D-09 bis D-11).

    Personenfelder werden direkt nach dem Segmentieren verworfen — sie erreichen nie
    einen `Produktinfo`-Datensatz (D-09).
    """
    pi_seiten = seiten.filter(
        pl.col("produkt").is_not_null() & (pl.col("typ") == "produktinformationen")
    ).sort(["produkt", "pdf_seite"])

    p_zeilen = hierarchie.filter(pl.col("ebene") == "P")
    name_je_produkt = {z["code"]: z["name"] for z in p_zeilen.iter_rows(named=True)}
    pg_je_produkt = {z["code"]: z["eltern_code"] for z in p_zeilen.iter_rows(named=True)}
    pg_zeilen = hierarchie.filter(pl.col("ebene") == "PG")
    pb_je_pg = {z["code"]: z["eltern_code"] for z in pg_zeilen.iter_rows(named=True)}

    alle_pdf_seiten_je_produkt = {
        zeile["produkt"]: tuple(sorted(zeile["pdf_seite"]))
        for zeile in seiten.filter(pl.col("produkt").is_not_null())
        .group_by("produkt")
        .agg(pl.col("pdf_seite"))
        .iter_rows(named=True)
    }

    produkte: list[Produktinfo] = []
    for produkt in sorted(pi_seiten["produkt"].unique().to_list()):
        pi_pdf_seiten = tuple(pi_seiten.filter(pl.col("produkt") == produkt)["pdf_seite"].to_list())
        seiten_zeilen = tuple((seite, dokument.zeilen_fein(seite)) for seite in pi_pdf_seiten)
        felder = zerlege_felder(seiten_zeilen, jahrgang)
        for feld in PERSONENFELDER:
            felder.pop(feld, None)

        pg = pg_je_produkt[produkt]
        produkte.append(
            _baue_produktinfo(
                produkt,
                felder,
                name=name_je_produkt[produkt],
                pg=pg,
                pb=pb_je_pg[pg],
                pdf_seiten=alle_pdf_seiten_je_produkt[produkt],
                jahrgang=jahrgang,
            )
        )
    return produkte


def extrahiere_produkte(
    jahrgang: Jahrgang, *, daten_wurzel: Path = DATEN_WURZEL
) -> tuple[ExtraktionsErgebnis, ExtraktionsErgebnis, ExtraktionsErgebnis]:
    """Liest Produktinformationen, Grundzahlen und Erläuterungen aller 63 Produkte und
    schreibt produkte.json, grundzahlen.csv sowie erlaeuterungen.csv (EXTR-06, EXTR-07,
    EXTR-08, D-04, D-09)."""
    seiten = lies_seiten_csv(daten_wurzel / SEITEN_CSV)
    hierarchie = lies_hierarchie_csv(daten_wurzel / HIERARCHIE_CSV)
    ergebnisplan = lies_plan_csv(daten_wurzel / ERGEBNISPLAN_CSV)

    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        produktinfos = lies_produktinformationen(dokument, jahrgang, seiten, hierarchie)
        grundzahlen = lies_grundzahlen(dokument, jahrgang, seiten, hierarchie)
        erlaeuterungen = lies_erlaeuterungen(dokument, jahrgang, seiten, hierarchie)

    pruefe_plausibilitaet(erlaeuterungen, ergebnisplan, jahrgang.haushaltsjahr)

    erlaeuterungen_je_produkt: dict[str, list[Erlaeuterung]] = {}
    for erlaeuterung in erlaeuterungen:
        erlaeuterungen_je_produkt.setdefault(erlaeuterung.produkt, []).append(erlaeuterung)

    datensaetze = [
        {
            "code": info.code,
            "name": info.name,
            "pb": info.pb,
            "pg": info.pg,
            "fachbereich": info.fachbereich,
            "gremium": info.gremium,
            "beschreibung": info.beschreibung,
            "leistungen": list(info.leistungen),
            "auftragsgrundlage": info.auftragsgrundlage,
            "bindungsgrad": info.bindungsgrad,
            "bindungsgrad_original": info.bindungsgrad_original,
            "klassifizierung": info.klassifizierung,
            "zielgruppe": info.zielgruppe,
            "ziele": info.ziele,
            "erlaeuterungen": [
                {
                    "block": e.block,
                    "position": e.position,
                    "zu_zeilen": list(e.zu_zeilen),
                    "betrag": e.betrag,
                    "text": e.text,
                    "pdf_seite": e.pdf_seite,
                }
                for e in sorted(
                    erlaeuterungen_je_produkt.get(info.code, []),
                    key=lambda e: (e.block, e.position),
                )
            ],
            "pdf_seiten": list(info.pdf_seiten),
        }
        for info in produktinfos
    ]

    produkte_pfad = daten_wurzel / PRODUKTE_JSON
    schreibe_produkte_json(datensaetze, produkte_pfad)

    erlaeuterungen_df = pl.DataFrame(
        [
            {
                "produkt": e.produkt,
                "block": e.block,
                "position": e.position,
                "zu_zeilen": "|".join(e.zu_zeilen) if e.zu_zeilen else None,
                "betrag": e.betrag,
                "text": e.text,
                "pdf_seite": e.pdf_seite,
            }
            for e in erlaeuterungen
        ],
        schema={
            "produkt": pl.Utf8,
            "block": pl.Int64,
            "position": pl.Int64,
            "zu_zeilen": pl.Utf8,
            "betrag": pl.Int64,
            "text": pl.Utf8,
            "pdf_seite": pl.Int64,
        },
    )
    erlaeuterungen_pfad = daten_wurzel / ERLAEUTERUNGEN_CSV
    schreibe_erlaeuterungen_csv(erlaeuterungen_df, erlaeuterungen_pfad)

    grundzahlen_df = pl.DataFrame(
        [
            {
                "produkt": g.produkt,
                "position": g.position,
                "gruppe": g.gruppe,
                "bezeichnung": g.bezeichnung,
                "einheit": g.einheit,
                "jahr": g.jahr,
                "wert": g.wert,
                "nachkommastellen": g.nachkommastellen,
                "hinweis": g.hinweis,
                "pdf_seite": g.pdf_seite,
            }
            for g in grundzahlen
        ],
        schema={
            "produkt": pl.Utf8,
            "position": pl.Int64,
            "gruppe": pl.Utf8,
            "bezeichnung": pl.Utf8,
            "einheit": pl.Utf8,
            "jahr": pl.Int64,
            "wert": pl.Float64,
            "nachkommastellen": pl.Int64,
            "hinweis": pl.Utf8,
            "pdf_seite": pl.Int64,
        },
    )
    grundzahlen_pfad = daten_wurzel / GRUNDZAHLEN_CSV
    schreibe_grundzahlen_csv(grundzahlen_df, grundzahlen_pfad)

    return (
        ExtraktionsErgebnis(zeilen_geschrieben=len(datensaetze), pfad=produkte_pfad),
        ExtraktionsErgebnis(zeilen_geschrieben=grundzahlen_df.height, pfad=grundzahlen_pfad),
        ExtraktionsErgebnis(zeilen_geschrieben=erlaeuterungen_df.height, pfad=erlaeuterungen_pfad),
    )
