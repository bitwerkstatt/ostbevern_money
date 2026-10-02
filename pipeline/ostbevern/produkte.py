"""Schritt 03: Produktinformationen und Erläuterungen (Spez. 2.1, 4.2, 5.2).

Liest die "Produktinformationen"-Seiten aller 63 Produkte (Fachbereich, Gremium,
Beschreibung, Leistungen, Auftragsgrundlage, Bindungsgrad, Klassifizierung, Zielgruppe,
Ziele) und schreibt `produkte.json` (EXTR-06). Personenfelder ("Verantwortliche/r",
"Sachbearbeiter/innen") werden beim Parsen als Felder erkannt, um die Feldstruktur der
Seite zu verstehen, aber sofort danach verworfen und erreichen nie einen Datensatz,
ein Dict oder eine Datei (D-09, Datenschutz, da `daten/` eingecheckt wird).
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import polars as pl

from ostbevern.freitext import ersetze_eurozeichen, verbinde_zeilen
from ostbevern.konfiguration import Jahrgang, layout_text
from ostbevern.pdf import PdfDokument, Textzeile
from ostbevern.schema import (
    DATEN_WURZEL,
    HIERARCHIE_CSV,
    PRODUKTE_JSON,
    SEITEN_CSV,
    lies_hierarchie_csv,
    lies_seiten_csv,
    schreibe_produkte_json,
)

# Toleranz für die Körpertext-Schriftgröße (die Größe der ersten Feld-Kopfzeile; Lauf-
# köpfe, Titel und Seitenzahlen haben andere Größen, Phase 3 zerlege_felder) und für die
# x-Koordinaten-Zuordnung innerhalb der Leistungen-Aufzählung (bündig mit der jeweiligen
# Spaltenanker-Logik in investitionen.py/querschnitte.py).
_GROESSEN_TOLERANZ = 0.5
_LEISTUNGEN_X_TOLERANZ = 3.0


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
) -> tuple[ExtraktionsErgebnis]:
    """Liest Produktinformationen aller 63 Produkte und schreibt produkte.json
    (EXTR-06, D-09)."""
    seiten = lies_seiten_csv(daten_wurzel / SEITEN_CSV)
    hierarchie = lies_hierarchie_csv(daten_wurzel / HIERARCHIE_CSV)

    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        produktinfos = lies_produktinformationen(dokument, jahrgang, seiten, hierarchie)

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
            "pdf_seiten": list(info.pdf_seiten),
        }
        for info in produktinfos
    ]

    produkte_pfad = daten_wurzel / PRODUKTE_JSON
    schreibe_produkte_json(datensaetze, produkte_pfad)

    return (ExtraktionsErgebnis(zeilen_geschrieben=len(datensaetze), pfad=produkte_pfad),)
