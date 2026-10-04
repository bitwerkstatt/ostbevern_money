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

# Ausnahmen der Ziffernregel (D-15): Jahreszahlen, Paragraphen, Seitenverweise
# (inkl. Spannen wie "S. 24/25" oder "S. 309-311").
_JAHR_MUSTER = re.compile(r"\b(?:19|20)\d{2}\b")
_PARAGRAF_MUSTER = re.compile(r"§\s*\d+")
_SEITE_MUSTER = re.compile(r"S\.\s*\d+(?:[-/]\d+)*")

# Format von erklaerungen.md: "## schluessel"-Abschnitte, je mit einer Titel- und einer
# Quelle-Zeile direkt danach (kein Leerzeilenabstand), dann eine Leerzeile, dann
# Absätze, durch Leerzeilen getrennt.
_ABSCHNITT_MUSTER = re.compile(r"^## (.+)$", re.MULTILINE)
_TITEL_MUSTER = re.compile(r"^Titel:\s*(.+)$")
_QUELLE_MUSTER = re.compile(r"^Quelle:\s*(.+)$")
_SEITENZAHL_MUSTER = re.compile(r"S\.\s*(\d+)")
_SCHLUESSEL_MUSTER = re.compile(r"^[a-z][a-z0-9_]*$")
_KOPFZEILE = "# Erklärtexte"


@dataclass(frozen=True)
class Erklaertext:
    """Ein geprüfter Erklärtext-Abschnitt (D-16): Schlüssel, Titel, Quellseiten, Absätze."""

    schluessel: str
    titel: str
    quelle_seiten: tuple[int, ...]
    absaetze: tuple[str, ...]


def lies_erklaerungen(pfad: Path) -> list[Erklaertext]:
    """Parst `erklaerungen.md` (D-16, D-17).

    Bricht mit `TexteFehler` ab, wenn: die erste Zeile nicht `# Erklärtexte` ist, ein
    Abschnitt keine `Titel:`- oder `Quelle:`-Zeile hat, ein Schlüssel nicht
    `^[a-z][a-z0-9_]*$` entspricht, ein Schlüssel doppelt vorkommt, eine Quelle-Zeile
    keine Seitenzahl enthält oder ein Abschnitt keinen Absatztext nach Titel/Quelle hat.
    """
    rohtext = pfad.read_text(encoding="utf-8")
    zeilen = rohtext.splitlines()
    if not zeilen or zeilen[0].strip() != _KOPFZEILE:
        raise TexteFehler(f"{pfad}: erste Zeile muss {_KOPFZEILE!r} sein")
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
        if len(kopf_zeilen) != 2:
            raise TexteFehler(
                f"{pfad}: Abschnitt {schluessel!r} braucht genau eine Titel- und eine "
                "Quelle-Zeile direkt nach der Überschrift"
            )
        titel_treffer = _TITEL_MUSTER.match(kopf_zeilen[0])
        if titel_treffer is None:
            raise TexteFehler(f"{pfad}: Abschnitt {schluessel!r} hat keine 'Titel:'-Zeile")
        quelle_treffer = _QUELLE_MUSTER.match(kopf_zeilen[1])
        if quelle_treffer is None:
            raise TexteFehler(f"{pfad}: Abschnitt {schluessel!r} hat keine 'Quelle:'-Zeile")

        titel = titel_treffer.group(1).strip()
        seiten = tuple(int(s) for s in _SEITENZAHL_MUSTER.findall(quelle_treffer.group(1)))
        if not seiten:
            raise TexteFehler(f"{pfad}: Abschnitt {schluessel!r}: Quelle ohne Seitenzahl")

        absaetze = tuple(
            " ".join(z.strip() for z in block.splitlines() if z.strip())
            for block in bloecke[1:]
            if block.strip()
        )
        if not absaetze:
            raise TexteFehler(f"{pfad}: Abschnitt {schluessel!r} hat keinen Absatztext")

        ergebnis.append(Erklaertext(schluessel, titel, seiten, absaetze))
    return ergebnis


def pruefe_text(text: str) -> None:
    """Prüft einen Absatz gegen die Ziffernregel und das HTML-Verbot (D-15).

    Bricht mit `TexteFehler` ab bei: einem unbekannten Formatkürzel in einem sonst
    wohlgeformten Platzhalter, einem unvollständigen/unverschachtelten Platzhalter
    (z. B. fehlende schließende Klammer), einem HTML-Zeichen ("<"/">") oder einer
    Ziffer außerhalb eines gültigen Platzhalters, einer Jahreszahl (19xx/20xx), eines
    Paragraphen ("§ n") oder eines Seitenverweises ("S. n", auch als Spanne).
    """
    if "<" in text or ">" in text:
        raise TexteFehler(f"Text enthält ein HTML-Zeichen: {text!r}")

    rest = text
    for span_treffer in _PLATZHALTER_SPAN_MUSTER.finditer(text):
        span = span_treffer.group(0)
        platzhalter_treffer = PLATZHALTER_MUSTER.fullmatch(span)
        if platzhalter_treffer is None:
            raise TexteFehler(f"Ungültiger Platzhalter: {span!r}")
        _, format_kuerzel = platzhalter_treffer.groups()
        if format_kuerzel not in FORMATKUERZEL:
            raise TexteFehler(f"Unbekanntes Formatkürzel in Platzhalter: {span!r}")
        rest = rest.replace(span, "", 1)

    if "{{" in rest or "}}" in rest:
        raise TexteFehler(f"Unvollständiger Platzhalter in Text: {text!r}")

    rest = _JAHR_MUSTER.sub("", rest)
    rest = _PARAGRAF_MUSTER.sub("", rest)
    rest = _SEITE_MUSTER.sub("", rest)

    ziffer_treffer = re.search(r"\d", rest)
    if ziffer_treffer is not None:
        start = max(0, ziffer_treffer.start() - 15)
        ende = min(len(rest), ziffer_treffer.start() + 15)
        raise TexteFehler(
            "Nackte Ziffer außerhalb Platzhalter/Jahreszahl/§/S.: "
            f"{rest[start:ende]!r} (voller Text: {text!r})"
        )


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


# Benannte, dokumentierte Formeln über die Werte aus `textwerte` (D-15): der Name
# verwendet relative Begriffe (Haushaltsjahr, Vorjahr), nie eine Jahreszahl. Jede
# Formel liest `jahr.haushaltsjahr`/`jahr.vorjahr` aus dem übergebenen Werte-Dict, um
# die konkreten Jahresschlüssel zur Laufzeit zu bilden.
ABGELEITET: dict[str, Callable[[dict[str, int | float]], int | float]] = {
    # Rückgang der Schlüsselzuweisung Vorjahr -> Haushaltsjahr (Spez. 3.3, D-15-Beispiel).
    "schluesselzuweisung_rueckgang_haushaltsjahr": _schluesselzuweisung_rueckgang_haushaltsjahr,
    # Betrag des globalen Minderaufwands als positive Zahl (GEP-Zeile ist negativ gebucht).
    "globaler_minderaufwand_betrag_haushaltsjahr": _globaler_minderaufwand_betrag_haushaltsjahr,
    # Jahresergebnis nach Minderaufwand als positives Defizit (GEP-Zeile ist negativ).
    "jahresergebnis_defizit_haushaltsjahr": _jahresergebnis_defizit_haushaltsjahr,
    # Satzung § 4, Research Pitfall 4: Ausgleichsrücklage Stand Haushaltsjahr minus
    # Stand Folgejahr (NICHT der rohe Vorjahresdelta der Eigenkapitalübersicht).
    "ausgleichsruecklage_minderung_haushaltsjahr": _ausgleichsruecklage_minderung_haushaltsjahr,
}


def textwerte(
    haushalt: Mapping[str, object],
    investitionen: Mapping[str, object],
    produkte: Sequence[Mapping[str, object]],
) -> dict[str, int | float]:
    """Baut die kuratierte Werte-Namensraum für die Erklärtexte (D-15) aus den bereits
    gebauten App-Dictionaries (`haushalt.json`, `investitionen.json`, `produkte.json`).

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
    for name, formel in ABGELEITET.items():
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
                if schluessel not in werte:
                    raise TexteFehler(
                        f"Unbekannter Datenschlüssel {schluessel!r} in Text "
                        f"{text.schluessel!r}: {absatz!r}"
                    )
                if schluessel not in verwendet:
                    verwendet[schluessel] = (werte[schluessel], format_kuerzel)
    return verwendet


def vorschau(texte: Sequence[Erklaertext], werte: Mapping[str, int | float]) -> str:
    """Baut eine Review-Vorschau (D-17): jeder Platzhalter wird mit seinem Rohwert in
    eckigen Klammern annotiert, ohne jede Zahlenformatierung (reines Review-Hilfsmittel,
    die Pipeline formatiert nie, D-15)."""

    def _annotiere(treffer: re.Match[str]) -> str:
        schluessel, _format_kuerzel = treffer.groups()
        wert = werte.get(schluessel, "???")
        return f"{treffer.group(0)}[{wert}]"

    zeilen: list[str] = []
    for text in texte:
        seiten = ", ".join(f"S. {seite}" for seite in text.quelle_seiten)
        zeilen.append(f"## {text.schluessel} — {text.titel} (Quelle: {seiten})")
        for absatz in text.absaetze:
            zeilen.append(PLATZHALTER_MUSTER.sub(_annotiere, absatz))
        zeilen.append("")
    return "\n".join(zeilen)
