"""Schritt 05: Stellenplan S. 284-290 (EXTR-10, D-18 bis D-20).

Koordinatenparser für die Teil-A/B-Tabellen (Beamte S. 284, Tarif S. 285, Sozial- und
Erziehungsdienst S. 286), die Nachwuchskräfte (S. 290) und die drei Stellenübersichten
nach Produktbereichen (S. 287-289). Anders als `investitionen.py`/`querschnitte.py`
(dichte Tabellen, jede Spalte hat immer einen Wert) sind die Stellenübersichten dünn
besetzt — eine PB/Gruppe-Kombination ohne gedruckten Wert bedeutet "kein Eintrag", nicht
0 (Research Pattern 1, Pitfall 1). Stellenwerte werden ausschließlich aus der gedruckten
Zeichenkette in Hundertstel umgewandelt (nie `round(float * 100)`, D-18, Research
Pattern 2).

`extrahiere_stellenplan` öffnet das PDF selbst (wie `investitionen.py`/`querschnitte.py`)
und liest direkt über `jahrgang.seitenbereiche["stellenplan"]` — kein `seiten.csv`-
Zwischenschritt nötig (Research Pitfall 7).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import polars as pl

from ostbevern.konfiguration import Jahrgang, layout_text
from ostbevern.pdf import PdfDokument, Textzeile, Wort
from ostbevern.plaene import ExtraktionsErgebnis
from ostbevern.schema import DATEN_WURZEL, STELLENPLAN_CSV, schreibe_stellenplan_csv
from ostbevern.spalten import SpaltenFehler, ordne_spalten

# Maximaler top-Abstand zwischen einer wertlosen Zeile und der Gruppe, der sie zugeordnet
# wird (S. 285 EG 9c/9b/9a, Research Pitfall, D-20/T-04-09). Oberhalb dieser Schwelle (oder
# bei Gleichstand zweier Gruppen) ist die Zuordnung nicht mehr eindeutig.
_TOP_TOLERANZ = 8.0


class StellenplanFehler(ValueError):
    """Wird ausgelöst, wenn eine Stellenplan-Seite oder -Zeile nicht lesbar ist (D-18 bis D-20)."""


_STELLENWERT_MUSTER = re.compile(r"^-?\d{1,3}(?:\.\d{3})*(?:,\d{1,2})?$")
_KEIN_WERT_ZEICHEN = ("-", "–")


def lies_stellen_hundertstel(text: str) -> int | None:
    """Parst einen gedruckten Stellenwert zu int-Hundertsteln (D-18, Research Pattern 2):
    "52,26" -> 5226, "6,9" -> 690, "8" -> 800, "0,41" -> 41. "-"/"–" (kein Wert) ergibt
    None. Arbeitet ausschließlich auf der gedruckten Zeichenkette (kein
    `round(wert * 100)` — Float-Rundungsfehler, D-18). Mehr als zwei Nachkommastellen
    oder ein anderer Text lösen StellenplanFehler aus."""
    bereinigt = text.strip()
    if bereinigt in _KEIN_WERT_ZEICHEN:
        return None
    normalisiert = bereinigt.replace("−", "-")
    if not _STELLENWERT_MUSTER.match(normalisiert):
        raise StellenplanFehler(f"Kein gültiger Stellenwert: {text!r}")
    vorzeichen = -1 if normalisiert.startswith("-") else 1
    ohne_vorzeichen = normalisiert.lstrip("-")
    if "," in ohne_vorzeichen:
        ganzzahl_teil, dezimal_teil = ohne_vorzeichen.split(",")
    else:
        ganzzahl_teil, dezimal_teil = ohne_vorzeichen, ""
    dezimal_teil = dezimal_teil.ljust(2, "0")
    ziffern = ganzzahl_teil.replace(".", "") + dezimal_teil
    return vorzeichen * int(ziffern)


def _lies_personen(text: str, *, kein_wert: str) -> int | None:
    """Parst eine gedruckte Nachwuchskräfte-Personenzahl (D-19, ganzzahlig, nie Stellen)."""
    bereinigt = text.strip()
    if bereinigt in (kein_wert, "–"):
        return None
    if not bereinigt.isdigit():
        raise StellenplanFehler(f"Keine gültige Personenzahl: {text!r}")
    return int(bereinigt)


def _datum_iso(text: str) -> str:
    """Wandelt ein gedrucktes Datum "TT.MM.JJJJ" nach ISO "JJJJ-MM-TT" (D-19)."""
    tag, monat, jahr = text.split(".")
    return f"{jahr}-{monat}-{tag}"


@dataclass(frozen=True)
class Stellenwert:
    """Ein einzelner Stellenplan-Wert (ein CSV-Zeilen-Entwurf, D-18 bis D-20)."""

    teil: str
    position: int
    gruppe: str
    amtsbezeichnung: str | None
    verguetung: str | None
    produktbereich: str | None
    merkmal: str
    jahr: int
    stichtag: str | None
    stellen_hundertstel: int | None
    personen: int | None
    vermerk: str | None
    pdf_seite: int


def _entferne_seitenzahl(zeilen: tuple[Textzeile, ...], pdf_seite: int) -> tuple[Textzeile, ...]:
    """Entfernt das links angeklebte/eigenständige Wort der PDF-Seitenzahl (wie
    `querschnitte._bereinige_seitenzahl_am_rand`); eine dadurch leere Zeile wird verworfen,
    statt als leere Textzeile weitergereicht zu werden."""
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
        if neue_woerter:
            bereinigt.append(
                zeile
                if neue_woerter == zeile.woerter
                else Textzeile(top=zeile.top, woerter=neue_woerter)
            )
    return tuple(bereinigt)


def _ordne_werte(
    woerter: list[Wort], anker_x1: tuple[float, ...], *, pdf_seite: int, bezeichner: str
) -> dict[int, Wort]:
    try:
        return ordne_spalten(woerter, anker_x1)
    except SpaltenFehler as fehler:
        raise StellenplanFehler(f"S. {pdf_seite}: {bezeichner}: {fehler}") from fehler


def _finde_spaltennummern_zeile(
    zeilen: tuple[Textzeile, ...], *, anzahl_spalten: int, pdf_seite: int
) -> int:
    erwartet = tuple(str(n) for n in range(1, anzahl_spalten + 1))
    for index, zeile in enumerate(zeilen):
        if tuple(wort.text for wort in zeile.woerter) == erwartet:
            return index
    raise StellenplanFehler(
        f"S. {pdf_seite}: Spaltennummern-Zeile (1..{anzahl_spalten}) nicht gefunden"
    )


def _finde_zeile_mit_erstem_wort(
    zeilen: tuple[Textzeile, ...], *, text: str, start: int, pdf_seite: int, kontext: str
) -> int:
    for index in range(start, len(zeilen)):
        woerter = zeilen[index].woerter
        if woerter and woerter[0].text == text:
            return index
    raise StellenplanFehler(f"S. {pdf_seite}: Zeile {kontext!r} nicht gefunden")


_BEAMTE_BUCHSTABE = re.compile(r"^[AB]$")
_ZWEISTELLIG = re.compile(r"^\d{1,2}$")
_TARIF_GRUPPE = re.compile(r"^\d{1,2}[a-z]?$")


def _erkenne_gruppe(
    woerter: tuple[Wort, ...], *, teil: str, pauschal: str
) -> tuple[int, str, int] | None:
    """Erkennt den Gruppe-Token einer Teil-A/B-Zeile; gibt (Start-Index im Wortfeld,
    Gruppe-Text, Anzahl verbrauchter Wörter) zurück, oder None (kein Gruppe-Token)."""
    if teil == "beamte":
        for index in range(len(woerter) - 1):
            if _BEAMTE_BUCHSTABE.match(woerter[index].text) and _ZWEISTELLIG.match(
                woerter[index + 1].text
            ):
                return index, f"{woerter[index].text} {woerter[index + 1].text}", 2
        return None
    if teil == "sozial_erziehungsdienst":
        if not woerter:
            return None
        if woerter[0].text == pauschal:
            return 0, pauschal, 1
        if len(woerter) >= 2 and woerter[0].text == "S" and _ZWEISTELLIG.match(woerter[1].text):
            return 0, f"S {woerter[1].text}", 2
        return None
    # tarif
    if woerter and _TARIF_GRUPPE.match(woerter[0].text):
        return 0, woerter[0].text, 1
    return None


@dataclass
class _Label:
    """Eine erkannte Teil-A/B-Gruppenzeile mit ihren zugeordneten Werten (D-19, D-20)."""

    top: float
    gruppe: str
    amtsbezeichnung: str | None
    werte: dict[int, Wort] = field(default_factory=dict)
    vermerk_teile: list[str] = field(default_factory=list)


_SPALTE_MERKMAL: dict[str, str] = {
    "stellen": "stellen",
    "davon_ausgesondert": "davon_ausgesondert",
    "stellen_vorjahr": "stellen",
    "besetzt": "besetzt",
}


def _jahr_fuer_spalte(spalte: str, *, haushaltsjahr: int, stichtag_jahr: int) -> int:
    if spalte == "stellen_vorjahr":
        return haushaltsjahr - 1
    if spalte == "besetzt":
        return stichtag_jahr
    return haushaltsjahr


def _lies_teil_ab_seite(
    zeilen: tuple[Textzeile, ...],
    *,
    teil: str,
    spalten_namen: tuple[str, ...],
    jahrgang: Jahrgang,
    pdf_seite: int,
) -> list[Stellenwert]:
    """Liest eine Teil-A/B-Seite (Beamte S. 284, Tarif S. 285, Sozial- und
    Erziehungsdienst S. 286) nach dem gemeinsamen Spaltenlayout `spalten_namen`.

    Jede Zeile zwischen der Spaltennummern-Zeile und der "insgesamt"-Zeile trägt
    entweder einen Gruppe-Token (startet eine neue Gruppenzeile, D-19), reine Werte ohne
    Gruppe (S. 285 EG 9c/9b/9a: Werte stehen auf einer anderen `top`-Zeile als ihr Label
    — zweiter Durchlauf, nächstgelegene Gruppe per |Δtop| <= 8.0pt, eindeutiges Minimum)
    oder reine Vermerk-Fortsetzung (hängt an die zuletzt gesehene Gruppenzeile, in
    Lesereihenfolge). Die "insgesamt"-Zeile wird je Spalte gegen die Summe der
    Gruppenwerte geprüft, nie gespeichert (D-20)."""
    insgesamt_wort = layout_text(jahrgang, "stellenplan", "insgesamt")
    datum_muster = re.compile(layout_text(jahrgang, "stellenplan", "datum_muster"))
    pauschal = layout_text(jahrgang, "stellenplan", "sozial_erziehungsdienst_pauschal")
    haushaltsjahr = jahrgang.haushaltsjahr

    anzahl_spalten = len(spalten_namen)
    spaltennummern_index = _finde_spaltennummern_zeile(
        zeilen, anzahl_spalten=anzahl_spalten, pdf_seite=pdf_seite
    )
    anker_x1 = tuple(wort.x1 for wort in zeilen[spaltennummern_index].woerter)

    gruppe_index = spalten_namen.index("gruppe")
    vermerk_index = spalten_namen.index("vermerk")
    value_indizes = range(gruppe_index + 1, vermerk_index)
    value_anker = tuple(anker_x1[i] for i in value_indizes)
    value_namen = tuple(spalten_namen[i] for i in value_indizes)
    vermerk_schwelle = anker_x1[vermerk_index - 1]

    kopf_woerter = [wort for zeile in zeilen[:spaltennummern_index] for wort in zeile.woerter]
    kopf_texte = {wort.text for wort in kopf_woerter}
    if str(haushaltsjahr) not in kopf_texte or str(haushaltsjahr - 1) not in kopf_texte:
        raise StellenplanFehler(
            f"S. {pdf_seite}: Kopfzeile enthält nicht beide Jahre "
            f"{haushaltsjahr}/{haushaltsjahr - 1}"
        )
    datum_treffer = [wort.text for wort in kopf_woerter if datum_muster.match(wort.text)]
    if len(datum_treffer) != 1:
        raise StellenplanFehler(
            f"S. {pdf_seite}: Kopfzeile hat {len(datum_treffer)} Stichtags-Daten, erwartet genau 1"
        )
    stichtag = _datum_iso(datum_treffer[0])
    stichtag_jahr = int(stichtag[:4])

    insgesamt_index = _finde_zeile_mit_erstem_wort(
        zeilen,
        text=insgesamt_wort,
        start=spaltennummern_index + 1,
        pdf_seite=pdf_seite,
        kontext=insgesamt_wort,
    )
    koerper = zeilen[spaltennummern_index + 1 : insgesamt_index]

    labels: list[_Label] = []
    unzugeordnete_werte: list[tuple[float, list[Wort]]] = []

    for zeile in koerper:
        gruppe_treffer = _erkenne_gruppe(zeile.woerter, teil=teil, pauschal=pauschal)
        wert_woerter = [wort for wort in zeile.woerter if wort.x0 <= vermerk_schwelle]
        vermerk_woerter = [wort for wort in zeile.woerter if wort.x0 > vermerk_schwelle]

        if gruppe_treffer is not None:
            start, gruppe_text, anzahl_token = gruppe_treffer
            gruppen_woerter = set(zeile.woerter[start : start + anzahl_token])
            amtsbezeichnung: str | None = None
            if teil == "beamte":
                vor = zeile.woerter[:start]
                amtsbezeichnung = " ".join(wort.text for wort in vor) if vor else None
            wert_rest = [
                wort
                for wort in wert_woerter
                if wort not in gruppen_woerter and wort not in zeile.woerter[:start]
            ]
            zugeordnet = _ordne_werte(
                wert_rest, value_anker, pdf_seite=pdf_seite, bezeichner=gruppe_text
            )
            labels.append(
                _Label(
                    top=zeile.top,
                    gruppe=gruppe_text,
                    amtsbezeichnung=amtsbezeichnung,
                    werte=zugeordnet,
                    vermerk_teile=(
                        [" ".join(wort.text for wort in vermerk_woerter)] if vermerk_woerter else []
                    ),
                )
            )
        elif wert_woerter and all(
            _STELLENWERT_MUSTER.match(wort.text.replace("−", "-"))
            or wort.text in _KEIN_WERT_ZEICHEN
            for wort in wert_woerter
        ):
            unzugeordnete_werte.append((zeile.top, wert_woerter))
        elif vermerk_woerter:
            if not labels:
                raise StellenplanFehler(f"S. {pdf_seite}: Vermerk ohne vorherige Datenzeile")
            labels[-1].vermerk_teile.append(" ".join(wort.text for wort in vermerk_woerter))
        else:
            # Block-Überschrift ohne Gruppe-Token und ohne wertartige Zeichenkette
            # ("Wahlbeamte", "Laufbahngruppe 2"/"1", Research Pitfall): keine Datenzeile.
            continue

    for top, wert_woerter in unzugeordnete_werte:
        if not labels:
            raise StellenplanFehler(f"S. {pdf_seite}: Werte bei top={top:.1f} ohne jede Gruppe")
        abstaende = sorted((abs(label.top - top), index) for index, label in enumerate(labels))
        bester_abstand, bester_index = abstaende[0]
        if bester_abstand > _TOP_TOLERANZ:
            raise StellenplanFehler(
                f"S. {pdf_seite}: Werte bei top={top:.1f} haben keine Gruppe innerhalb von "
                f"{_TOP_TOLERANZ}pt"
            )
        if len(abstaende) > 1 and abstaende[1][0] == bester_abstand:
            raise StellenplanFehler(
                f"S. {pdf_seite}: Werte bei top={top:.1f} sind zwei Gruppen gleich nah"
            )
        ziel = labels[bester_index]
        zugeordnet = _ordne_werte(
            wert_woerter, value_anker, pdf_seite=pdf_seite, bezeichner=ziel.gruppe
        )
        if set(zugeordnet) & set(ziel.werte):
            raise StellenplanFehler(
                f"S. {pdf_seite}: Gruppe {ziel.gruppe!r} hat doppelte Spaltenwerte"
            )
        ziel.werte.update(zugeordnet)

    insgesamt_wert_woerter = [
        wort for wort in zeilen[insgesamt_index].woerter[1:] if wort.x0 <= vermerk_schwelle
    ]
    insgesamt_zugeordnet = _ordne_werte(
        insgesamt_wert_woerter, value_anker, pdf_seite=pdf_seite, bezeichner=insgesamt_wort
    )
    for index, name in enumerate(value_namen):
        gedruckt_wort = insgesamt_zugeordnet.get(index)
        gedruckter_wert = lies_stellen_hundertstel(gedruckt_wort.text) if gedruckt_wort else None
        summe = sum(
            (wert or 0)
            for label in labels
            if (wort := label.werte.get(index)) is not None
            for wert in (lies_stellen_hundertstel(wort.text),)
        )
        if (gedruckter_wert or 0) != summe:
            raise StellenplanFehler(
                f"S. {pdf_seite}: {insgesamt_wort} Spalte {name!r}: gedruckt "
                f"{gedruckter_wert}, Summe der Zeilen {summe}"
            )

    ergebnis: list[Stellenwert] = []
    position = 0
    for label in labels:
        if not label.werte:
            continue
        position += 1
        vermerk_text = " ".join(label.vermerk_teile) if label.vermerk_teile else None
        for index, spalte in enumerate(value_namen):
            wort = label.werte.get(index)
            if wort is None:
                continue
            wert = lies_stellen_hundertstel(wort.text)
            if wert is None:
                continue
            merkmal = _SPALTE_MERKMAL[spalte]
            jahr = _jahr_fuer_spalte(
                spalte, haushaltsjahr=haushaltsjahr, stichtag_jahr=stichtag_jahr
            )
            ist_stellen_haushaltsjahr = merkmal == "stellen" and jahr == haushaltsjahr
            ergebnis.append(
                Stellenwert(
                    teil=teil,
                    position=position,
                    gruppe=label.gruppe,
                    amtsbezeichnung=label.amtsbezeichnung,
                    verguetung=None,
                    produktbereich=None,
                    merkmal=merkmal,
                    jahr=jahr,
                    stichtag=stichtag if merkmal == "besetzt" else None,
                    stellen_hundertstel=wert,
                    personen=None,
                    vermerk=vermerk_text if ist_stellen_haushaltsjahr else None,
                    pdf_seite=pdf_seite,
                )
            )
    return ergebnis


@dataclass
class _NachwuchsEintrag:
    """Eine erkannte Nachwuchskräfte-Zeile (S. 290, D-19)."""

    bezeichnung_teile: list[str]
    verguetung_teile: list[str]
    vorgesehen: Wort | None
    beschaeftigt: Wort | None


def _lies_nachwuchs_seite(
    zeilen: tuple[Textzeile, ...], *, jahrgang: Jahrgang, pdf_seite: int
) -> list[Stellenwert]:
    """Liest die Nachwuchskräfte-Tabelle (S. 290, D-19): eigener `teil`, Personen (nie
    Stellen), zwei Spalten (`vorgesehen` zum Haushaltsjahr, `beschaeftigt` zu einem
    Stichtag). Spalten 1/2 (Bezeichnung/Vergütung) sind Freitext, abgegrenzt über die
    Mittelpunkte der Spaltenanker (wie Beamte-Amtsbezeichnung); Spalten 3/4 sind Werte,
    über `ordne_spalten` zugeordnet."""
    kein_wert = layout_text(jahrgang, "stellenplan", "kein_wert")
    insgesamt_wort = layout_text(jahrgang, "stellenplan", "insgesamt")
    datum_muster = re.compile(layout_text(jahrgang, "stellenplan", "datum_muster"))
    spalten_namen = jahrgang.layout["stellenplan"]["spalten_nachwuchs"]
    haushaltsjahr = jahrgang.haushaltsjahr

    spaltennummern_index = _finde_spaltennummern_zeile(
        zeilen, anzahl_spalten=len(spalten_namen), pdf_seite=pdf_seite
    )
    anker_x1 = tuple(wort.x1 for wort in zeilen[spaltennummern_index].woerter)
    grenzen = tuple((anker_x1[i] + anker_x1[i + 1]) / 2 for i in range(len(anker_x1) - 1))

    def _zone(x0: float) -> int:
        for index, grenze in enumerate(grenzen):
            if x0 < grenze:
                return index
        return len(grenzen)

    kopf_woerter = [wort for zeile in zeilen[:spaltennummern_index] for wort in zeile.woerter]
    if str(haushaltsjahr) not in {wort.text for wort in kopf_woerter}:
        raise StellenplanFehler(f"S. {pdf_seite}: Kopfzeile enthält nicht das Haushaltsjahr")
    datum_treffer = [wort.text for wort in kopf_woerter if datum_muster.match(wort.text)]
    if len(datum_treffer) != 1:
        raise StellenplanFehler(
            f"S. {pdf_seite}: Kopfzeile hat {len(datum_treffer)} Stichtags-Daten, erwartet genau 1"
        )
    stichtag = _datum_iso(datum_treffer[0])
    stichtag_jahr = int(stichtag[:4])

    insgesamt_index = _finde_zeile_mit_erstem_wort(
        zeilen,
        text=insgesamt_wort,
        start=spaltennummern_index + 1,
        pdf_seite=pdf_seite,
        kontext=insgesamt_wort,
    )
    koerper = zeilen[spaltennummern_index + 1 : insgesamt_index]

    vorgesehen_index = spalten_namen.index("vorgesehen")
    beschaeftigt_index = spalten_namen.index("beschaeftigt")

    eintraege: list[_NachwuchsEintrag] = []
    for zeile in koerper:
        nach_zone: dict[int, list[Wort]] = {}
        for wort in zeile.woerter:
            nach_zone.setdefault(_zone(wort.x0), []).append(wort)
        hat_verguetung_oder_werte = any(
            index in nach_zone for index in (1, vorgesehen_index, beschaeftigt_index)
        )
        if hat_verguetung_oder_werte or not eintraege:
            eintraege.append(
                _NachwuchsEintrag(
                    bezeichnung_teile=(
                        [" ".join(wort.text for wort in nach_zone[0])] if nach_zone.get(0) else []
                    ),
                    verguetung_teile=(
                        [" ".join(wort.text for wort in nach_zone[1])] if nach_zone.get(1) else []
                    ),
                    vorgesehen=next(iter(nach_zone.get(vorgesehen_index, [])), None),
                    beschaeftigt=next(iter(nach_zone.get(beschaeftigt_index, [])), None),
                )
            )
            continue
        if not nach_zone.get(0):
            raise StellenplanFehler(f"S. {pdf_seite}: unerwartete leere Nachwuchs-Zeile")
        eintraege[-1].bezeichnung_teile.append(" ".join(wort.text for wort in nach_zone[0]))

    insgesamt_nach_zone: dict[int, list[Wort]] = {}
    for wort in zeilen[insgesamt_index].woerter[1:]:
        insgesamt_nach_zone.setdefault(_zone(wort.x0), []).append(wort)
    insgesamt_vorgesehen = next(iter(insgesamt_nach_zone.get(vorgesehen_index, [])), None)
    insgesamt_beschaeftigt = next(iter(insgesamt_nach_zone.get(beschaeftigt_index, [])), None)

    summe_vorgesehen = sum(
        (personen or 0)
        for eintrag in eintraege
        if eintrag.vorgesehen is not None
        for personen in (_lies_personen(eintrag.vorgesehen.text, kein_wert=kein_wert),)
    )
    summe_beschaeftigt = sum(
        (personen or 0)
        for eintrag in eintraege
        if eintrag.beschaeftigt is not None
        for personen in (_lies_personen(eintrag.beschaeftigt.text, kein_wert=kein_wert),)
    )
    gedruckt_vorgesehen = (
        _lies_personen(insgesamt_vorgesehen.text, kein_wert=kein_wert)
        if insgesamt_vorgesehen
        else None
    )
    gedruckt_beschaeftigt = (
        _lies_personen(insgesamt_beschaeftigt.text, kein_wert=kein_wert)
        if insgesamt_beschaeftigt
        else None
    )
    if (gedruckt_vorgesehen or 0) != summe_vorgesehen:
        raise StellenplanFehler(
            f"S. {pdf_seite}: {insgesamt_wort} vorgesehen: gedruckt {gedruckt_vorgesehen}, "
            f"Summe der Zeilen {summe_vorgesehen}"
        )
    if (gedruckt_beschaeftigt or 0) != summe_beschaeftigt:
        raise StellenplanFehler(
            f"S. {pdf_seite}: {insgesamt_wort} beschäftigt: gedruckt {gedruckt_beschaeftigt}, "
            f"Summe der Zeilen {summe_beschaeftigt}"
        )

    ergebnis: list[Stellenwert] = []
    position = 0
    for eintrag in eintraege:
        vorgesehen = (
            _lies_personen(eintrag.vorgesehen.text, kein_wert=kein_wert)
            if eintrag.vorgesehen is not None
            else None
        )
        beschaeftigt = (
            _lies_personen(eintrag.beschaeftigt.text, kein_wert=kein_wert)
            if eintrag.beschaeftigt is not None
            else None
        )
        if vorgesehen is None and beschaeftigt is None:
            continue
        position += 1
        gruppe = " ".join(teil for teil in eintrag.bezeichnung_teile if teil)
        verguetung = " ".join(teil for teil in eintrag.verguetung_teile if teil) or None
        if vorgesehen is not None:
            ergebnis.append(
                Stellenwert(
                    teil="nachwuchs",
                    position=position,
                    gruppe=gruppe,
                    amtsbezeichnung=None,
                    verguetung=verguetung,
                    produktbereich=None,
                    merkmal="vorgesehen",
                    jahr=haushaltsjahr,
                    stichtag=None,
                    stellen_hundertstel=None,
                    personen=vorgesehen,
                    vermerk=None,
                    pdf_seite=pdf_seite,
                )
            )
        if beschaeftigt is not None:
            ergebnis.append(
                Stellenwert(
                    teil="nachwuchs",
                    position=position,
                    gruppe=gruppe,
                    amtsbezeichnung=None,
                    verguetung=verguetung,
                    produktbereich=None,
                    merkmal="beschaeftigt",
                    jahr=stichtag_jahr,
                    stichtag=stichtag,
                    stellen_hundertstel=None,
                    personen=beschaeftigt,
                    vermerk=None,
                    pdf_seite=pdf_seite,
                )
            )
    return ergebnis


def lies_stellenplan(dokument: PdfDokument, jahrgang: Jahrgang) -> list[Stellenwert]:
    """Liest alle Stellenplan-Seiten des konfigurierten Seitenbereichs (D-18 bis D-20).

    Jede Seite wird über ihren gedruckten Titel (exakter Textzeile.text-Vergleich) einer
    der konfigurierten Tabellen zugeordnet; eine Seite ohne passenden Titel wird noch
    übersprungen, bis der letzte Plan-Task (Stellenübersichten) alle Titel abdeckt.
    """
    bereich = jahrgang.seitenbereiche["stellenplan"]
    titel_beamte = layout_text(jahrgang, "stellenplan", "titel_beamte")
    titel_tarif = layout_text(jahrgang, "stellenplan", "titel_tarif")
    titel_sozial_erziehungsdienst = layout_text(
        jahrgang, "stellenplan", "titel_sozial_erziehungsdienst"
    )
    titel_nachwuchs = layout_text(jahrgang, "stellenplan", "titel_nachwuchs")

    werte: list[Stellenwert] = []
    for pdf_seite in range(bereich.von, bereich.bis + 1):
        zeilen = _entferne_seitenzahl(dokument.zeilen(pdf_seite), pdf_seite)
        titel_texte = {zeile.text for zeile in zeilen}

        if titel_beamte in titel_texte:
            werte += _lies_teil_ab_seite(
                zeilen,
                teil="beamte",
                spalten_namen=jahrgang.layout["stellenplan"]["spalten_beamte"],
                jahrgang=jahrgang,
                pdf_seite=pdf_seite,
            )
        elif titel_tarif in titel_texte:
            werte += _lies_teil_ab_seite(
                zeilen,
                teil="tarif",
                spalten_namen=jahrgang.layout["stellenplan"]["spalten_tarif"],
                jahrgang=jahrgang,
                pdf_seite=pdf_seite,
            )
        elif titel_sozial_erziehungsdienst in titel_texte:
            werte += _lies_teil_ab_seite(
                zeilen,
                teil="sozial_erziehungsdienst",
                spalten_namen=jahrgang.layout["stellenplan"]["spalten_tarif"],
                jahrgang=jahrgang,
                pdf_seite=pdf_seite,
            )
        elif titel_nachwuchs in titel_texte:
            werte += _lies_nachwuchs_seite(zeilen, jahrgang=jahrgang, pdf_seite=pdf_seite)
        # Stellenübersichten (S. 287-289) folgen in einem späteren Task dieses Plans.

    return werte


def extrahiere_stellenplan(
    jahrgang: Jahrgang, *, daten_wurzel: Path = DATEN_WURZEL
) -> ExtraktionsErgebnis:
    """Liest den Stellenplan und schreibt `daten_wurzel/STELLENPLAN_CSV` (D-18 bis D-20).

    Öffnet das PDF selbst und liest direkt über `jahrgang.seitenbereiche["stellenplan"]`
    (kein `seiten.csv`-Zwischenschritt, Research Pitfall 7)."""
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        werte = lies_stellenplan(dokument, jahrgang)

    df = pl.DataFrame(
        [
            {
                "teil": wert.teil,
                "position": wert.position,
                "gruppe": wert.gruppe,
                "amtsbezeichnung": wert.amtsbezeichnung,
                "verguetung": wert.verguetung,
                "produktbereich": wert.produktbereich,
                "merkmal": wert.merkmal,
                "jahr": wert.jahr,
                "stichtag": wert.stichtag,
                "stellen_hundertstel": wert.stellen_hundertstel,
                "personen": wert.personen,
                "vermerk": wert.vermerk,
                "pdf_seite": wert.pdf_seite,
            }
            for wert in werte
        ],
        schema={
            "teil": pl.Utf8,
            "position": pl.Int64,
            "gruppe": pl.Utf8,
            "amtsbezeichnung": pl.Utf8,
            "verguetung": pl.Utf8,
            "produktbereich": pl.Utf8,
            "merkmal": pl.Utf8,
            "jahr": pl.Int64,
            "stichtag": pl.Utf8,
            "stellen_hundertstel": pl.Int64,
            "personen": pl.Int64,
            "vermerk": pl.Utf8,
            "pdf_seite": pl.Int64,
        },
    )
    pfad = daten_wurzel / STELLENPLAN_CSV
    schreibe_stellenplan_csv(df, pfad)
    return ExtraktionsErgebnis(zeilen_geschrieben=df.height, pfad=pfad)
