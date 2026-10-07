"""Platzhalter-Vertrag für die Erklärtexte des Vorberichts (D-15, D-16, MANU-08).

`daten/manuell/texte/erklaerungen.md` enthält von Hand entworfene, fachlich geprüfte
Texte (D-17). Jede Zahl darin ist ein Platzhalter `{{schluessel|formatkuerzel}}` — nie
eine von Hand eingetippte Ziffer (Ausnahmen: Jahreszahlen, „§ n" und „S. n"). Dieses
Modul parst die Datei (`lies_erklaerungen`), prüft jeden Absatz gegen die Ziffernregel
(`pruefe_text`), baut die kuratierte Werte-Namensraum aus den bereits erzeugten
App-Dictionaries (`textwerte`) und löst die verwendeten Platzhalter auf (`loese_auf`).

Die Pipeline formatiert nie (D-15) — `loese_auf`/`vorschau` liefern Rohwerte, die
App-Komponente (Phase 5/6) ruft `app/src/charts/format.ts::formatiere` auf. Ein
unbekannter Datenschlüssel oder ein unbekanntes Formatkürzel bricht Schritt 07 ab
(fail-fast wie alle Extraktionsschritte, D-08).
"""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path


class TexteFehler(ValueError):
    """Wird ausgelöst, wenn `erklaerungen.md` oder ein Platzhalter ungültig ist (D-15)."""


# Formatkürzel der Platzhalter (D-15); muss exakt der FormatKuerzel-Union in
# app/src/charts/format.ts entsprechen (test_formatkuerzel_wie_format_ts). "jahr" ist
# eine Jahreszahl ohne Tausendertrennung (z. B. Haushaltsjahr), anders als "zahl" (CR-01).
FORMATKUERZEL: tuple[str, ...] = ("euro", "mio", "zahl", "jahr", "prozent", "promille", "vzae")

# Ein vollständiger Platzhalter `{{schluessel|format}}`; Schlüsselzeichen sind
# Kleinbuchstaben, Ziffern, Unterstrich und Punkt (Namensraum-Trenner).
PLATZHALTER_MUSTER = re.compile(r"\{\{([a-z0-9_.]+)\|([a-z]+)\}\}")

# Jede geschweifte Klammerspanne ohne verschachtelte Klammern — Kandidat für einen
# Platzhalter, auch wenn der Inhalt nicht dem PLATZHALTER_MUSTER entspricht (dann ist
# es ein ungültiger Platzhalter, kein unbekanntes Formatkürzel).
_PLATZHALTER_SPAN_MUSTER = re.compile(r"\{\{[^{}]*\}\}")

# Ausnahmen der Ziffernregel (D-15): Paragraphen und Seitenverweise (inkl. Spannen wie
# "S. 24/25" oder "S. 309-311"). Jahreszahlen sind keine Ausnahme mehr (D-01): sie stehen
# nur als Platzhalter `{{jahr.…|jahr}}`; das Muster dient als Detektor für die Fehlermeldung.
_JAHRESZAHL_MUSTER = re.compile(r"\b(?:19|20)\d{2}\b")
_PARAGRAF_MUSTER = re.compile(r"§\s*\d+")
_SEITE_MUSTER = re.compile(r"S\.\s*\d+(?:[-/]\d+)*")

# Feste Ereignisjahre (D-02): `jahr.fest_JJJJ` steht für genau dieses Jahr (z. B. ein
# historisches Ergebnisjahr) und wird aus dem Schlüsselnamen aufgelöst, nicht aus `werte`.
_FESTES_JAHR_MUSTER = re.compile(r"^jahr\.fest_((?:19|20)\d{2})$")

# Format von erklaerungen.md: "## schluessel"-Abschnitte, je mit einer Titel- und einer
# Quelle-Zeile direkt danach (kein Leerzeilenabstand), dann eine Leerzeile, dann
# Absätze, durch Leerzeilen getrennt.
_ABSCHNITT_MUSTER = re.compile(r"^## (.+)$", re.MULTILINE)
_TITEL_MUSTER = re.compile(r"^Titel:\s*(.+)$")
_QUELLE_MUSTER = re.compile(r"^Quelle:\s*(.+)$")
_SEITENZAHL_MUSTER = re.compile(r"S\.\s*(\d+)")
# Die Quelle-Zeile darf ausschließlich aus einzeln genannten Seiten bestehen
# ("S. 309, S. 310"). Alles andere ("S. 24, 25", "S. 309-311", "S. 309 bis 311",
# "S. 309 f.") würde von _SEITENZAHL_MUSTER auf die erste Seite verkürzt; daher wird die
# ganze Zeile validiert statt einzelne Spannen-Schreibweisen zu sperren.
_QUELLE_ERLAUBT_MUSTER = re.compile(r"S\.\s*\d+(?:\s*[,;]\s*S\.\s*\d+)*")
_SCHLUESSEL_MUSTER = re.compile(r"^[a-z][a-z0-9_]*$")
_KOPFZEILE = "# Erklärtexte"
_KOPFZEILE_GLOSSAR = "# Glossar"


@dataclass(frozen=True)
class Erklaertext:
    """Ein geprüfter Erklärtext-Abschnitt (D-16): Schlüssel, Titel, Quellseiten, Absätze."""

    schluessel: str
    titel: str
    quelle_seiten: tuple[int, ...]
    absaetze: tuple[str, ...]


def _lies_abschnitte(pfad: Path, *, kopfzeile: str, quelle_pflicht: bool) -> list[Erklaertext]:
    rohtext = pfad.read_text(encoding="utf-8")
    zeilen = rohtext.splitlines()
    if not zeilen or zeilen[0].strip() != kopfzeile:
        raise TexteFehler(f"{pfad}: erste Zeile muss {kopfzeile!r} sein")
    rest = "\n".join(zeilen[1:])

    treffer = list(_ABSCHNITT_MUSTER.finditer(rest))
    if not treffer:
        raise TexteFehler(f"{pfad}: keine Abschnitte ('## schluessel') gefunden")

    ergebnis: list[Erklaertext] = []
    gesehen: set[str] = set()
    for index, abschnitt_treffer in enumerate(treffer):
        schluessel = abschnitt_treffer.group(1).strip()
        if not _SCHLUESSEL_MUSTER.match(schluessel):
            raise TexteFehler(
                f"{pfad}: ungültiger Schlüssel {schluessel!r} (erwartet ^[a-z][a-z0-9_]*$)"
            )
        if schluessel in gesehen:
            raise TexteFehler(f"{pfad}: doppelter Schlüssel {schluessel!r}")
        gesehen.add(schluessel)

        start = abschnitt_treffer.end()
        ende = treffer[index + 1].start() if index + 1 < len(treffer) else len(rest)
        abschnitt = rest[start:ende].strip("\n")

        bloecke = re.split(r"\n\s*\n", abschnitt)
        if len(bloecke) < 2:
            raise TexteFehler(
                f"{pfad}: Abschnitt {schluessel!r} hat keine Absätze nach Titel/Quelle"
            )
        kopf_zeilen = [z.strip() for z in bloecke[0].splitlines() if z.strip()]
        erlaubte_zeilen = (2,) if quelle_pflicht else (1, 2)
        if len(kopf_zeilen) not in erlaubte_zeilen:
            erwartet = (
                "genau eine Titel- und eine Quelle-Zeile"
                if quelle_pflicht
                else "eine Titel- und höchstens eine Quelle-Zeile"
            )
            raise TexteFehler(
                f"{pfad}: Abschnitt {schluessel!r} braucht {erwartet} direkt nach der Überschrift"
            )
        titel_treffer = _TITEL_MUSTER.match(kopf_zeilen[0])
        if titel_treffer is None:
            raise TexteFehler(f"{pfad}: Abschnitt {schluessel!r} hat keine 'Titel:'-Zeile")

        seiten: tuple[int, ...] = ()
        if len(kopf_zeilen) == 2:
            quelle_treffer = _QUELLE_MUSTER.match(kopf_zeilen[1])
            if quelle_treffer is None:
                raise TexteFehler(f"{pfad}: Abschnitt {schluessel!r} hat keine 'Quelle:'-Zeile")
            seiten = tuple(int(s) for s in _SEITENZAHL_MUSTER.findall(quelle_treffer.group(1)))
            if not seiten:
                raise TexteFehler(f"{pfad}: Abschnitt {schluessel!r}: Quelle ohne Seitenzahl")
            if not _QUELLE_ERLAUBT_MUSTER.fullmatch(quelle_treffer.group(1).strip()):
                raise TexteFehler(
                    f"{pfad}: Abschnitt {schluessel!r}: Quelle muss 'S. n, S. m' sein "
                    "(jede Seite einzeln, keine Spannen oder Listen ohne 'S.')"
                )
        elif quelle_pflicht:  # pragma: no cover - durch erlaubte_zeilen bereits ausgeschlossen
            raise TexteFehler(f"{pfad}: Abschnitt {schluessel!r} hat keine 'Quelle:'-Zeile")

        titel = titel_treffer.group(1).strip()
        absaetze = tuple(
            " ".join(z.strip() for z in block.splitlines() if z.strip())
            for block in bloecke[1:]
            if block.strip()
        )
        if not absaetze:
            raise TexteFehler(f"{pfad}: Abschnitt {schluessel!r} hat keinen Absatztext")

        ergebnis.append(Erklaertext(schluessel, titel, seiten, absaetze))
    return ergebnis


def lies_erklaerungen(
    pfad: Path, *, kopfzeile: str = _KOPFZEILE, quelle_pflicht: bool = True
) -> list[Erklaertext]:
    """Parst `erklaerungen.md` (D-16, D-17).

    Bricht mit `TexteFehler` ab, wenn: die erste Zeile nicht `kopfzeile` (Standard
    `# Erklärtexte`) ist, ein Abschnitt keine `Titel:`- oder (bei `quelle_pflicht`) keine
    `Quelle:`-Zeile hat, ein Schlüssel nicht `^[a-z][a-z0-9_]*$` entspricht, ein Schlüssel
    doppelt vorkommt, eine Quelle-Zeile keine Seitenzahl enthält oder ein Abschnitt keinen
    Absatztext nach Titel/Quelle hat.

    Mit `quelle_pflicht=False` darf der Kopfblock nur aus der Titel-Zeile bestehen;
    `quelle_seiten` ist dann leer (Plan 05-03, Glossar).
    """
    return _lies_abschnitte(pfad, kopfzeile=kopfzeile, quelle_pflicht=quelle_pflicht)


def lies_glossar(pfad: Path) -> list[Erklaertext]:
    """Parst `glossar.md` (D-14, GLOS-01): Kopfzeile `# Glossar`, je Begriff ein
    `## schluessel`-Abschnitt mit `Titel:` (dem angezeigten Begriff), optionaler
    `Quelle:`-Zeile und Absätzen.

    Gleiche Regeln wie `lies_erklaerungen`, aber die Quelle ist nur Pflicht, sobald ein
    Absatz des Abschnitts einen Platzhalter (also eine Zahl) enthält — sonst bricht der
    Parser mit `TexteFehler` ab (Seitenverweis bei Zahlen, D-14).

    Der erste Absatz eines Begriffs steht allein (sein erster Satz ist der Tooltip-Text) und
    darf nie einen Platzhalter enthalten (Invariante aus `typen.ts`); sonst `TexteFehler`.
    """
    texte = _lies_abschnitte(pfad, kopfzeile=_KOPFZEILE_GLOSSAR, quelle_pflicht=False)
    for text in texte:
        if PLATZHALTER_MUSTER.search(text.absaetze[0]) or "{{" in text.absaetze[0]:
            raise TexteFehler(
                f"{pfad}: Glossarbegriff {text.schluessel!r}: der erste Absatz steht allein "
                "und darf keinen Platzhalter enthalten"
            )
        if not text.quelle_seiten and any(
            PLATZHALTER_MUSTER.search(absatz) or "{{" in absatz for absatz in text.absaetze
        ):
            raise TexteFehler(
                f"{pfad}: Glossarbegriff {text.schluessel!r} enthält einen Platzhalter, "
                "aber keine 'Quelle:'-Zeile (Seitenverweis bei Zahlen, D-14)"
            )
    return texte


def festes_jahr(schluessel: str) -> int | None:
    """Das Jahr eines Schlüssels `jahr.fest_JJJJ` (nur 19xx/20xx) oder `None` (D-02)."""
    treffer = _FESTES_JAHR_MUSTER.fullmatch(schluessel)
    return int(treffer.group(1)) if treffer is not None else None


def pruefe_text(text: str, *, abschnitt: str | None = None) -> None:
    """Prüft einen Absatz gegen die Ziffernregel und das HTML-Verbot (D-15).

    Bricht mit `TexteFehler` ab bei: einem unbekannten Formatkürzel in einem sonst
    wohlgeformten Platzhalter, einem unvollständigen/unverschachtelten Platzhalter
    (z. B. fehlende schließende Klammer), einem HTML-Zeichen ("<"/">"), einer getippten
    Jahreszahl (19xx/20xx, D-01; Ausweg: `{{jahr.haushaltsjahr|jahr}}` bzw.
    `{{jahr.fest_JJJJ|jahr}}`) oder einer Ziffer außerhalb eines gültigen Platzhalters.
    Ausgenommen bleiben Paragraphen ("§ n") und Seitenverweise ("S. n", auch als Spanne).
    Ein Platzhalter im Namensraum "jahr." muss das Formatkürzel "jahr" tragen. `abschnitt`
    benennt den Abschnitt in der Jahres-Meldung.
    """
    if "<" in text or ">" in text:
        raise TexteFehler(f"Text enthält ein HTML-Zeichen: {text!r}")

    rest = text
    for span_treffer in _PLATZHALTER_SPAN_MUSTER.finditer(text):
        span = span_treffer.group(0)
        platzhalter_treffer = PLATZHALTER_MUSTER.fullmatch(span)
        if platzhalter_treffer is None:
            raise TexteFehler(f"Ungültiger Platzhalter: {span!r}")
        schluessel, format_kuerzel = platzhalter_treffer.groups()
        if format_kuerzel not in FORMATKUERZEL:
            raise TexteFehler(f"Unbekanntes Formatkürzel in Platzhalter: {span!r}")
        # CR-01/WR-05: Jahreszahlen dürfen nie mit Tausendertrennung erscheinen.
        if schluessel.startswith("jahr.") and format_kuerzel != "jahr":
            raise TexteFehler(
                f"Platzhalter {span!r} im Namensraum 'jahr.' braucht das Formatkürzel 'jahr'"
            )
        rest = rest.replace(span, "", 1)

    if "{{" in rest or "}}" in rest:
        raise TexteFehler(f"Unvollständiger Platzhalter in Text: {text!r}")

    rest = _PARAGRAF_MUSTER.sub("", rest)
    rest = _SEITE_MUSTER.sub("", rest)

    jahr_treffer = _JAHRESZAHL_MUSTER.search(rest)
    if jahr_treffer is not None:
        ort = f" in Abschnitt „{abschnitt}“" if abschnitt is not None else ""
        raise TexteFehler(
            f"Handgetippte Jahreszahl „{jahr_treffer.group(0)}“{ort}. Jahreszahlen stehen "
            "nur als Platzhalter, zum Beispiel {{jahr.haushaltsjahr|jahr}}. "
            f"(voller Text: {text!r})"
        )

    ziffer_treffer = re.search(r"\d", rest)
    if ziffer_treffer is not None:
        start = max(0, ziffer_treffer.start() - 15)
        ende = min(len(rest), ziffer_treffer.start() + 15)
        raise TexteFehler(
            "Nackte Ziffer außerhalb Platzhalter/§/S.: "
            f"{rest[start:ende]!r} (voller Text: {text!r})"
        )


def pruefe_titel(titel: str, abschnitt: str) -> None:
    """Prüft den Titel eines Abschnitts (D-05).

    Titel werden von der App roh ausgegeben und nicht aufgelöst; ein Platzhalter im Titel
    wäre dort sichtbarer Rohtext und wird abgelehnt. Sonst gelten dieselben Regeln wie
    für Absätze (`pruefe_text`, auch die Jahresregel).
    """
    if "{{" in titel or "}}" in titel:
        raise TexteFehler(
            f"Titel von Abschnitt „{abschnitt}“ enthält einen Platzhalter; "
            f"Titel werden nicht aufgelöst: {titel!r}"
        )
    pruefe_text(titel, abschnitt=abschnitt)


def _ist_zahl(wert: object) -> bool:
    return isinstance(wert, (int, float)) and not isinstance(wert, bool)


def _fuege_zeilen_hinzu(
    ziel: dict[str, int | float],
    praefix: str,
    zeilen: Mapping[str, Sequence[object]],
    jahre: Sequence[int],
) -> None:
    for kanonisch, werte in zeilen.items():
        for jahr, wert in zip(jahre, werte, strict=True):
            if _ist_zahl(wert):
                ziel[f"{praefix}.{kanonisch}.{jahr}"] = wert  # type: ignore[arg-type]


def _meta_eintragen(
    ziel: dict[str, int | float], praefix: str, blatt: Mapping[str, object]
) -> None:
    wert = blatt.get("wert")
    if _ist_zahl(wert):
        ziel[praefix] = wert  # type: ignore[assignment]
    vorjahr = blatt.get("vorjahr")
    if _ist_zahl(vorjahr):
        ziel[f"{praefix}.vorjahr"] = vorjahr  # type: ignore[assignment]


def _schluesselzuweisung_rueckgang_haushaltsjahr(w: dict[str, int | float]) -> int | float:
    hh = int(w["jahr.haushaltsjahr"])
    vj = int(w["jahr.vorjahr"])
    return (
        w[f"vorbericht.zuwendungen.schluesselzuweisung.{vj}"]
        - w[f"vorbericht.zuwendungen.schluesselzuweisung.{hh}"]
    )


def _globaler_minderaufwand_betrag_haushaltsjahr(w: dict[str, int | float]) -> int | float:
    hh = int(w["jahr.haushaltsjahr"])
    return -w[f"gep.globaler_minderaufwand.{hh}"]


def _jahresergebnis_defizit_haushaltsjahr(w: dict[str, int | float]) -> int | float:
    hh = int(w["jahr.haushaltsjahr"])
    return -w[f"gep.ergebnis_nach_minderaufwand.{hh}"]


def _ausgleichsruecklage_minderung_haushaltsjahr(w: dict[str, int | float]) -> int | float:
    hh = int(w["jahr.haushaltsjahr"])
    stand_haushaltsjahr = w[f"eigenkapital.ausgleichsruecklage.{hh}"]
    stand_folgejahr = w[f"eigenkapital.ausgleichsruecklage.{hh + 1}"]
    return stand_haushaltsjahr - stand_folgejahr


def _planjahre(w: dict[str, int | float]) -> range:
    """Alle Jahre vom Haushaltsjahr bis zum letzten Planjahr (beide eingeschlossen)."""
    return range(int(w["jahr.haushaltsjahr"]), int(w["jahr.letztes_jahr"]) + 1)


def _ausgleichsruecklage_aufgebraucht_jahr(w: dict[str, int | float]) -> int | float:
    # S. 311 (Eigenkapitalübersicht): die Spalten sind Bestände zu Beginn des Jahres. Die
    # erste Spalte nach dem Haushaltsjahr mit Ausgleichsrücklage 0 ist also der Stand zu
    # Beginn jenes Jahres; aufgebraucht ist die Rücklage am Ende des Jahres davor (Research
    # Pattern 3). Gibt es keine Nullspalte, bricht Schritt 07 ab: der Satz könnte sonst
    # nicht mehr stimmen (Plan 06-04, ENTW-03).
    for jahr in range(int(w["jahr.haushaltsjahr"]) + 1, int(w["jahr.letztes_jahr"]) + 1):
        if w[f"eigenkapital.ausgleichsruecklage.{jahr}"] == 0:
            return jahr - 1
    raise TexteFehler(
        "Formel 'ausgleichsruecklage_aufgebraucht_jahr': keine Spalte der Ausgleichsrücklage "
        "nach dem Haushaltsjahr hat den Stand 0 – der Polster-Text muss überarbeitet werden"
    )


def _allgemeine_ruecklage_abbau(w: dict[str, int | float], jahr: int) -> int | float:
    # S. 23 (Vorbericht): Fehlbetrag des Jahres, soweit ihn die Ausgleichsrücklage nicht
    # deckt, mindert die allgemeine Rücklage; die Verrechnung der Bilanzierungshilfe (S. 311,
    # negativ gebucht) kommt hinzu. Alle Reihen sind Stände zu Beginn des Jahres.
    fehlbetrag = -w[f"eigenkapital.jahresergebnis.{jahr}"]
    ausgleich = w[f"eigenkapital.ausgleichsruecklage.{jahr}"]
    verrechnung = w[f"eigenkapital.verrechnung_bilanzierungshilfe.{jahr}"]
    return max(0, fehlbetrag - ausgleich) - verrechnung


def _allgemeine_ruecklage_ende_letztes_jahr(w: dict[str, int | float]) -> int | float:
    letztes = int(w["jahr.letztes_jahr"])
    return w[f"eigenkapital.allgemeine_ruecklage.{letztes}"] - _allgemeine_ruecklage_abbau(
        w, letztes
    )


def _allgemeine_ruecklage_rueckgang_bis_letztes_jahr(w: dict[str, int | float]) -> int | float:
    # Prozentpunkte (Formatkürzel "prozent"), bezogen auf den Stand der allgemeinen Rücklage
    # zu Beginn des Haushaltsjahrs (Bezugsgröße der Schwellen aus § 76 GO NRW, S. 23).
    anfang = w[f"eigenkapital.allgemeine_ruecklage.{int(w['jahr.haushaltsjahr'])}"]
    if anfang == 0:
        raise TexteFehler(
            "Formel 'allgemeine_ruecklage_rueckgang_bis_letztes_jahr': allgemeine Rücklage "
            "zu Beginn des Haushaltsjahrs ist 0, ein Rückgang in Prozent ist nicht definiert"
        )
    ende = _allgemeine_ruecklage_ende_letztes_jahr(w)
    return (anfang - ende) / anfang * 100


def _schulden_gesamt_vorjahr(w: dict[str, int | float]) -> int | float:
    return w[f"schulden.gesamt.{int(w['jahr.vorjahr'])}"]


def _schulden_gesamt_letztes_jahr(w: dict[str, int | float]) -> int | float:
    return w[f"schulden.gesamt.{int(w['jahr.letztes_jahr'])}"]


def _kreditaufnahme_ab_haushaltsjahr(w: dict[str, int | float]) -> int | float:
    # Gesamtfinanzplan Z. 33, Summe Haushaltsjahr bis letztes Planjahr; deckt sich mit der
    # Fortschreibung des Schuldenstands (schuldenstand.formel, S. 310).
    return sum(w[f"gfp.kreditaufnahme.{jahr}"] for jahr in _planjahre(w))


def _tilgung_ab_haushaltsjahr(w: dict[str, int | float]) -> int | float:
    # Gesamtfinanzplan Z. 35, Summe Haushaltsjahr bis letztes Planjahr.
    return sum(w[f"gfp.tilgung.{jahr}"] for jahr in _planjahre(w))


# Benannte, dokumentierte Formeln über die Werte aus `textwerte` (D-15): der Name
# verwendet relative Begriffe (Haushaltsjahr, Vorjahr), nie eine Jahreszahl. Jede
# Formel liest `jahr.haushaltsjahr`/`jahr.vorjahr` aus dem übergebenen Werte-Dict, um
# die konkreten Jahresschlüssel zur Laufzeit zu bilden.
_ABGELEITET_ROH: dict[str, Callable[[dict[str, int | float]], int | float]] = {
    # Rückgang der Schlüsselzuweisung Vorjahr -> Haushaltsjahr (Spez. 3.3, D-15-Beispiel).
    "schluesselzuweisung_rueckgang_haushaltsjahr": _schluesselzuweisung_rueckgang_haushaltsjahr,
    # Betrag des globalen Minderaufwands als positive Zahl (GEP-Zeile ist negativ gebucht).
    "globaler_minderaufwand_betrag_haushaltsjahr": _globaler_minderaufwand_betrag_haushaltsjahr,
    # Jahresergebnis nach Minderaufwand als positives Defizit (GEP-Zeile ist negativ).
    "jahresergebnis_defizit_haushaltsjahr": _jahresergebnis_defizit_haushaltsjahr,
    # Satzung § 4, Research Pitfall 4: Ausgleichsrücklage Stand Haushaltsjahr minus
    # Stand Folgejahr (NICHT der rohe Vorjahresdelta der Eigenkapitalübersicht).
    "ausgleichsruecklage_minderung_haushaltsjahr": _ausgleichsruecklage_minderung_haushaltsjahr,
    # Phase 6 (Plan 06-04, D-14): Polster der Rücklagen bis zum letzten Planjahr.
    "ausgleichsruecklage_aufgebraucht_jahr": _ausgleichsruecklage_aufgebraucht_jahr,
    "allgemeine_ruecklage_ende_letztes_jahr": _allgemeine_ruecklage_ende_letztes_jahr,
    "allgemeine_ruecklage_rueckgang_bis_letztes_jahr": (
        _allgemeine_ruecklage_rueckgang_bis_letztes_jahr
    ),
    # Phase 6 (Plan 06-04, D-09): Schuldenanstieg von Ende Vorjahr bis Ende letztes Planjahr.
    "schulden_gesamt_vorjahr": _schulden_gesamt_vorjahr,
    "schulden_gesamt_letztes_jahr": _schulden_gesamt_letztes_jahr,
    "kreditaufnahme_ab_haushaltsjahr": _kreditaufnahme_ab_haushaltsjahr,
    "tilgung_ab_haushaltsjahr": _tilgung_ab_haushaltsjahr,
}


def _mit_eingabepruefung(
    name: str, formel: Callable[[dict[str, int | float]], int | float]
) -> Callable[[dict[str, int | float]], int | float]:
    """Macht aus einem fehlenden Eingabewert (auch einem Nachbarjahr, WR-03) einen
    `TexteFehler`, der Formel und Schlüssel nennt, statt eines bloßen `KeyError` (D-20)."""

    def _ausgewertet(werte: dict[str, int | float]) -> int | float:
        try:
            return formel(werte)
        except KeyError as fehler:
            schluessel = fehler.args[0] if fehler.args else fehler
            raise TexteFehler(f"Formel {name!r}: Eingabewert {schluessel!r} fehlt") from fehler

    return _ausgewertet


ABGELEITET: dict[str, Callable[[dict[str, int | float]], int | float]] = {
    name: _mit_eingabepruefung(name, formel) for name, formel in _ABGELEITET_ROH.items()
}


def textwerte(
    haushalt: Mapping[str, object],
    investitionen: Mapping[str, object],
    produkte: Sequence[Mapping[str, object]],
    texte: Sequence[Erklaertext] | None = None,
) -> dict[str, int | float]:
    """Baut die kuratierte Werte-Namensraum für die Erklärtexte (D-15) aus den bereits
    gebauten App-Dictionaries (`haushalt.json`, `investitionen.json`, `produkte.json`).

    Mit `texte` werden nur die `abgeleitet.*`-Formeln ausgewertet, die ein Text tatsächlich
    verwendet; ohne `texte` alle. Fehlt einer Formel ein Eingabewert (z. B. eine Folgejahr-
    Reihe in einem anderen Jahrgang), bricht das mit `TexteFehler` ab, nie mit `KeyError`.

    Liest nie das PDF und nie eine CSV direkt (D-06) — die Eingaben sind dieselben
    Dictionaries, die `app_daten.erzeuge_app_daten` bereits aufgebaut hat, bevor sie
    geschrieben werden.
    """
    werte: dict[str, int | float] = {}
    jahre = list(haushalt["jahre"])  # type: ignore[arg-type]
    haushaltsjahr = int(haushalt["haushaltsjahr"])  # type: ignore[arg-type]
    vorjahr = haushaltsjahr - 1
    werte["jahr.haushaltsjahr"] = haushaltsjahr
    werte["jahr.vorjahr"] = vorjahr
    # Relative Jahre (D-02): wandern mit dem Jahrgang, nie als Jahreszahl getippt.
    werte["jahr.vorvorjahr"] = haushaltsjahr - 2
    werte["jahr.haushaltsjahr_plus_1"] = haushaltsjahr + 1
    werte["jahr.haushaltsjahr_plus_2"] = haushaltsjahr + 2
    # Letztes Planjahr des Jahrgangs (D-14): Grenze für Polster- und Schuldenformeln.
    werte["jahr.letztes_jahr"] = int(jahre[-1])

    # vorbericht.<tabelle>.<posten>.<jahr> und vorbericht.<tabelle>.gesamt_plan.<jahr>.
    vorbericht = haushalt["vorbericht"]  # type: ignore[index]
    for tabelle, inhalt in vorbericht.items():  # type: ignore[attr-defined]
        for posten in inhalt["posten"]:
            for jahr, wert in zip(jahre, posten["werte"], strict=True):
                if _ist_zahl(wert):
                    werte[f"vorbericht.{tabelle}.{posten['posten']}.{jahr}"] = wert
        if inhalt.get("gesamt_plan") is not None:
            for jahr, wert in zip(jahre, inhalt["gesamt_plan"], strict=True):
                if _ist_zahl(wert):
                    werte[f"vorbericht.{tabelle}.gesamt_plan.{jahr}"] = wert

    # gep.<kanonisch>.<jahr> -- GESAMT-Ebene des Ergebnisplans.
    ergebnisplan = haushalt["ergebnisplan"]  # type: ignore[index]
    _fuege_zeilen_hinzu(werte, "gep", ergebnisplan["GESAMT"]["zeilen"], jahre)

    # knoten.<code>.<kanonisch|berechnet>.<jahr> -- GESAMT und seine direkten Kinder
    # (die 15 PB inkl. KL, Spez. 3.4).
    knoten = haushalt["knoten"]  # type: ignore[index]
    eltern_je_code = {k["code"]: k["eltern"] for k in knoten}
    top_codes = {"GESAMT"} | {code for code, eltern in eltern_je_code.items() if eltern == "GESAMT"}
    for code in top_codes:
        eintrag = ergebnisplan.get(code)
        if eintrag is None:
            continue
        _fuege_zeilen_hinzu(werte, f"knoten.{code}", eintrag["zeilen"], jahre)
        for berechnet_schluessel in ("aufwand", "ertraege", "zuschussbedarf"):
            for jahr, wert in zip(jahre, eintrag["berechnet"][berechnet_schluessel], strict=True):
                if _ist_zahl(wert):
                    werte[f"knoten.{code}.{berechnet_schluessel}.{jahr}"] = wert

    # gfp.<kanonisch>.<jahr> und gfp_ve.<kanonisch> -- Gesamtfinanzplan, nur GESAMT.
    finanzplan_gesamt = haushalt["finanzplan"]["GESAMT"]  # type: ignore[index]
    _fuege_zeilen_hinzu(werte, "gfp", finanzplan_gesamt["zeilen"], jahre)
    for kanonisch, wert in finanzplan_gesamt["ve"].items():
        if _ist_zahl(wert):
            werte[f"gfp_ve.{kanonisch}"] = wert

    # meta.<pfad> (numerisch), plus .vorjahr, wo im Blatt vorhanden.
    meta = haushalt["meta"]  # type: ignore[index]
    _meta_eintragen(werte, "meta.einwohner", meta["einwohner"])
    _meta_eintragen(werte, "meta.flaeche", meta["flaeche"])
    for schluessel, blatt in meta["hebesaetze"].items():
        _meta_eintragen(werte, f"meta.hebesaetze.{schluessel}", blatt)
    for schluessel, blatt in meta["kreisumlage"].items():
        _meta_eintragen(werte, f"meta.kreisumlage.{schluessel}", blatt)
    for schluessel, blatt in meta["vorbericht_werte"].items():
        _meta_eintragen(werte, f"meta.vorbericht_werte.{schluessel}", blatt)

    # eigenkapital.<posten>.<jahr>.
    for posten in haushalt["eigenkapital"]["posten"]:  # type: ignore[index]
        for jahr, wert in zip(jahre, posten["werte"], strict=True):
            if _ist_zahl(wert):
                werte[f"eigenkapital.{posten['posten']}.{jahr}"] = wert

    # schulden.<reihe>.<jahr> (D-14).
    schuldenstand = investitionen["schuldenstand"]  # type: ignore[index]
    for reihe in ("investitionskredite", "nrw_bank", "gesamt", "pro_kopf"):
        for jahr, wert in zip(jahre, schuldenstand[reihe], strict=True):
            if _ist_zahl(wert):
                werte[f"schulden.{reihe}.{jahr}"] = wert

    # ve.gesamt und ve.faellig.<jahr>.
    ve_summe: int | float = 0
    ve_je_jahr: dict[int, int | float] = {}
    for zeile in investitionen["ve_faelligkeiten"]:  # type: ignore[index]
        ve_summe += zeile["betrag"]
        ve_je_jahr[zeile["jahr"]] = ve_je_jahr.get(zeile["jahr"], 0) + zeile["betrag"]
    werte["ve.gesamt"] = ve_summe
    for jahr, wert in ve_je_jahr.items():
        werte[f"ve.faellig.{jahr}"] = wert

    # grundzahlen.<produkt>.<position>.<jahr>.
    for produkt in produkte:
        for grundzahl in produkt["grundzahlen"]:  # type: ignore[index]
            for eintrag in grundzahl["werte"]:
                if _ist_zahl(eintrag["wert"]):
                    schluessel = (
                        f"grundzahlen.{produkt['code']}.{grundzahl['position']}.{eintrag['jahr']}"
                    )
                    werte[schluessel] = eintrag["wert"]

    # abgeleitet.<name> -- benannte Formeln, zuletzt ausgewertet (lesen die Werte oben).
    verwendete = (
        None
        if texte is None
        else {
            treffer.group(1)
            for text in texte
            for absatz in text.absaetze
            for treffer in PLATZHALTER_MUSTER.finditer(absatz)
        }
    )
    for name, formel in ABGELEITET.items():
        if verwendete is not None and f"abgeleitet.{name}" not in verwendete:
            continue
        werte[f"abgeleitet.{name}"] = formel(werte)

    return werte


def loese_auf(
    texte: Sequence[Erklaertext], werte: Mapping[str, int | float]
) -> dict[str, tuple[int | float, str]]:
    """Löst alle in `texte` verwendeten Platzhalter gegen `werte` auf (D-15).

    Liefert die verwendeten Schlüssel in erster Verwendungsreihenfolge, je mit Rohwert
    und Formatkürzel (`(wert, format)`). Ein Schlüssel, der in keinem Text in `werte`
    existiert, bricht mit `TexteFehler` ab (Schritt 07 darf nicht fortfahren, D-15).
    """
    verwendet: dict[str, tuple[int | float, str]] = {}
    for text in texte:
        for absatz in text.absaetze:
            for treffer in PLATZHALTER_MUSTER.finditer(absatz):
                schluessel, format_kuerzel = treffer.groups()
                if schluessel in verwendet:
                    continue
                if schluessel in werte:
                    verwendet[schluessel] = (werte[schluessel], format_kuerzel)
                    continue
                fest = festes_jahr(schluessel)
                if fest is None:
                    raise TexteFehler(
                        f"Unbekannter Datenschlüssel {schluessel!r} in Text "
                        f"{text.schluessel!r}: {absatz!r}"
                    )
                verwendet[schluessel] = (fest, format_kuerzel)
    return verwendet


# Platzhalter auf eine Grundzahl: grundzahlen.<produkt>.<position>.<jahr> (D-02).
_GRUNDZAHL_SCHLUESSEL_MUSTER = re.compile(r"^grundzahlen\.([0-9]+)\.([0-9]+)\.([0-9]{4})$")


def pruefe_grundzahl_jahre(
    texte: Sequence[Erklaertext],
    produkte: Sequence[Mapping[str, object]],
    erstes_planjahr: int,
) -> None:
    """D-02: Text und Diagramm zeigen für dasselbe Jahr denselben Wert.

    Für jedes Jahr ab dem ersten Planjahr gibt es Plan- bzw. Vorberichtswerte (D-01); ein
    Euro-Platzhalter auf eine Grundzahl dieses Jahres würde davon abweichen können. Bricht
    mit `TexteFehler` ab (Text und Platzhalter benannt), wenn ein Platzhalter
    `grundzahlen.<produkt>.<position>.<jahr>` ein Jahr >= `erstes_planjahr` meint und die
    Einheit dieser Grundzahl in `produkte` `EUR` ist. Grundzahlen anderer Einheiten und
    Jahre davor bleiben erlaubt; unbekannte Schlüssel prüft `loese_auf`.
    """
    einheiten: dict[tuple[str, int], object] = {}
    for produkt in produkte:
        for grundzahl in produkt["grundzahlen"]:  # type: ignore[attr-defined]
            einheiten[(str(produkt["code"]), int(grundzahl["position"]))] = grundzahl["einheit"]
    for text in texte:
        for absatz in text.absaetze:
            for treffer in PLATZHALTER_MUSTER.finditer(absatz):
                schluessel = treffer.group(1)
                teile = _GRUNDZAHL_SCHLUESSEL_MUSTER.match(schluessel)
                if teile is None:
                    continue
                code, position, jahr = teile.group(1), int(teile.group(2)), int(teile.group(3))
                if jahr >= erstes_planjahr and einheiten.get((code, position)) == "EUR":
                    raise TexteFehler(
                        f"Text {text.schluessel!r}: Platzhalter {{{{{schluessel}|...}}}} zitiert "
                        f"die Grundzahl in Euro für {jahr}; ab {erstes_planjahr} gilt die "
                        "Quelle der Zeitreihe (vorbericht.*, D-02)"
                    )


def vorschau(texte: Sequence[Erklaertext], werte: Mapping[str, int | float]) -> str:
    """Baut eine Review-Vorschau (D-17): jeder Platzhalter wird mit seinem Rohwert in
    eckigen Klammern annotiert, ohne jede Zahlenformatierung (reines Review-Hilfsmittel,
    die Pipeline formatiert nie, D-15)."""

    def _annotiere(treffer: re.Match[str]) -> str:
        schluessel, _format_kuerzel = treffer.groups()
        wert = werte.get(schluessel, festes_jahr(schluessel) or "???")
        return f"{treffer.group(0)}[{wert}]"

    zeilen: list[str] = []
    for text in texte:
        seiten = ", ".join(f"S. {seite}" for seite in text.quelle_seiten)
        zeilen.append(f"## {text.schluessel} — {text.titel} (Quelle: {seiten})")
        for absatz in text.absaetze:
            zeilen.append(PLATZHALTER_MUSTER.sub(_annotiere, absatz))
        zeilen.append("")
    return "\n".join(zeilen)
