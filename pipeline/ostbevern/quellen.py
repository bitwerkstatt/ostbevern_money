"""Schritt 08: Quellenbelege (Phase 7, DATA-04, Spez. 4.4 und 5.6).

Findet für gedruckte Werte die Zeile auf der PDF-Seite (Rechteck `bbox`), rendert die
referenzierten Seiten als WebP (`belegbilder`) und schreibt `app/src/data/quellen.json` sowie
den Bericht `daten/pruefberichte/quellenbelege.md` (alle Belege ohne Rechteck).

Schlüsselgrammatik (identisch in `app/src/lib/quelle.ts`):

- `ep:{code}:{zeile}`: Ergebnisplanzeile eines Knotens
  (`haushalt.ergebnisplan[code].zeilen[zeile]`); Codes mit `KL` sind ausgeschlossen
- `fp:{code}:{zeile}`: Finanzplanzeile (`haushalt.finanzplan[code].zeilen[zeile]`, heute
  nur `GESAMT`)
- `vb:{tabelle}:{posten}`: Vorberichtsposten mit `quelle` ungleich null;
  `vb:{tabelle}:gesamt` für `gesamt_vorbericht`
- `meta:{pfad}`: MetaWert aus `haushalt.meta`, Pfad gepunktet (`einwohner`,
  `hebesaetze.gewerbesteuer`)
- `gz:{produkt}:{position}`: Grundzahl aus `produkte.json`
- `pr:{produkt}`: Startseite des Produkts (Kopfzeile)
- `inv:{produkt}:{massnahme_id}:{konto}:{richtung}`: Investitionsmaßnahme
- `ve:{produkt}:{massnahme_id}:{konto}`: VE-Fälligkeiten einer Kontozeile
- `sd:{reihe}`: Schuldenstandsreihe (`investitionskredite`, `nrw_bank`,
  `liquiditaetskredite`)
- `sp:{teil}:{position}:{produktbereich oder -}`: gedruckte Stellenplanzeile
- `seite:{n}`: Seitenbeleg ohne Zeile, `bbox` immer `null`

`quellen.json`: `{haushaltsjahr, seiten: {"<n>": {bild, breite, hoehe}}, belege: {"<schluessel>":
{pdf_seite, bild, bbox}}}`. `bbox` ist `[x0, top, x1, bottom]` in PDF-Punkten, Ursprung oben
links, mit 2 pt Rand, auf die Seite begrenzt und auf zwei Dezimalstellen gerundet, oder `null`.
Ein Rechteck wird nie geraten: Jede Suche prüft Bezeichnung (bzw. Zeilennummer, Konto) und den
Betrag des Haushaltsjahrs; ohne genau einen Treffer ist `bbox` `null`, mit einem Grund im
Bericht (D-03). Die Suche liest nur die App-JSONs und die CSVs und ändert sie nie.
"""

from __future__ import annotations

import json
import re
from collections import defaultdict
from collections.abc import Callable, Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path

import polars as pl

from ostbevern.app_daten import (
    APP_DATEN_WURZEL,
    HAUSHALT_JSON,
    INVESTITIONEN_JSON,
    PRODUKTE_APP_JSON,
    STELLENPLAN_JSON,
    TEXTE_JSON,
    schreibe_app_json,
)
from ostbevern.belegbilder import bild_name, rendere_seiten
from ostbevern.konfiguration import (
    PROJEKT_WURZEL,
    Jahrgang,
    lade_jahrgang,
    layout_liste,
    layout_text,
)
from ostbevern.pdf import PdfDokument, RahmenZeile, WortRahmen
from ostbevern.plaene import lies_abschnitte
from ostbevern.produkte import personenfeld_rechtecke
from ostbevern.pruefung import zerlege_weitere_vorberichtstabellen
from ostbevern.schema import (
    DATEN_WURZEL,
    EIGENKAPITAL_CSV,
    ERGEBNISPLAN_CSV,
    FINANZPLAN_CSV,
    HIERARCHIE_CSV,
    INVESTITIONSZUWENDUNGEN_CSV,
    KITA_ZUSCHUESSE_CSV,
    QUELLENBELEGE_MD,
    SEITEN_CSV,
    STEUERARTEN_CSV,
    TRANSFERAUFWENDUNGEN_CSV,
    VERBINDLICHKEITEN_CSV,
    WEITERE_VORBERICHTSTABELLEN_CSV,
    ZUSCHUESSE_LFD_ZWECKE_CSV,
    ZUWENDUNGEN_CSV,
    lies_eigenkapital_csv,
    lies_hierarchie_csv,
    lies_plan_csv,
    lies_seiten_csv,
    lies_vorbericht_csv,
    zerlege_spaltenkopf,
)
from ostbevern.zahlen import ZahlenFehler, lies_betrag, lies_kennzahl
from ostbevern.zeilen import normalisiere_bezeichnung

BELEGBILDER_WURZEL = PROJEKT_WURZEL / "app" / "public" / "quellen"
QUELLEN_JSON = Path("quellen.json")

GRUND_NICHT_GEFUNDEN = "nicht_gefunden"
GRUND_MEHRDEUTIG = "mehrdeutig"
GRUND_BETRAG_FEHLT = "betrag_fehlt"
GRUND_BERECHNET = "berechnet"
GRUND_SCHWAERZUNG = "ueberlappt_schwaerzung"

# Ebene des Gesamtplans in den Plan-CSVs; zugleich der Knotencode in den Schlüsseln.
_GESAMT = "GESAMT"
# Wertart, die nur eine Verpflichtungsermächtigungs-Spalte beschreibt (nie das Haushaltsjahr).
_WERTART_VE = "ve"
# Der Knotencode der synthetischen Weitergabe an Kreis und Land beginnt mit diesem Präfix.
_KL_PRAEFIX = "KL"
# Höchstzahl an Zeichen hinter der Beschriftung einer Grundzahl-Zeile (gedruckte Einheit).
_EINHEIT_MAX_ZEICHEN = 15
# Namen der Seitenfelder in den App-JSONs (Seitenzahl bzw. Liste von Seitenzahlen).
_SEITENFELD = ("pdf_seite", "quelle")
_SEITENLISTENFELD = ("pdf_seiten", "quelle_seiten")
_SEITENTYP_PRODUKTINFORMATIONEN = "produktinformationen"
# Toleranz beim Vergleich gedruckter Zahlen mit Euro-Werten: Cent-Beträge (Eigenkapital) sind in
# den Daten kaufmännisch auf ganze Euro gerundet.
_ZAHL_TOLERANZ = 0.51
# Zeilenabstand (Punkte), bis zu dem eine Folgezeile noch zur selben gedruckten Zeile gehört.
_UMBRUCH_ABSTAND = 14.0

# Zuordnung der Schuldenstandsreihen zu den Posten in `verbindlichkeiten.csv` (fachliche
# Regel, identisch zu `app_daten.baue_investitionen_json`).
_SCHULDENSTAND_POSTEN: dict[str, str] = {
    "investitionskredite": "kredite_investitionen",
    "nrw_bank": "transferleistungen",
    "liquiditaetskredite": "liquiditaetskredite",
}

_NUMMER_MUSTER = re.compile(r"^\d+(?:\.\d+)*\.?")
_PRODUKTBEREICH_MUSTER = re.compile(r"^\d{2}$")

_ART_TITEL: dict[str, str] = {
    "ep": "Ergebnisplanzeilen",
    "fp": "Finanzplanzeilen",
    "vb": "Vorberichtsposten",
    "meta": "Meta-Werte",
    "gz": "Grundzahlen",
    "pr": "Produktseiten",
    "inv": "Investitionsmaßnahmen",
    "ve": "VE-Fälligkeiten",
    "sd": "Schuldenstand",
    "sp": "Stellenplan",
    "seite": "Seitenbelege",
}


class QuellenFehler(ValueError):
    """Wird ausgelöst, wenn Quellenbelege nicht konsistent erzeugt werden können."""


@dataclass(frozen=True)
class QuellenErgebnis:
    """Ergebnis von `erzeuge_quellen`."""

    pfad: Path
    anzahl_belege: int
    anzahl_ohne_bbox: int
    seiten: tuple[int, ...]
    neu_gerendert: int
    ohne_bbox: dict[str, str]
    bericht: Path


Suche = tuple[list[float] | None, str | None]
Rechteck = tuple[float, float, float, float]


def schluessel_ep(code: str, zeile: str) -> str:
    """Belegschlüssel einer Ergebnisplanzeile: `ep:{code}:{zeile}`."""
    return f"ep:{code}:{zeile}"


def schluessel_fp(code: str, zeile: str) -> str:
    """Belegschlüssel einer Finanzplanzeile: `fp:{code}:{zeile}`."""
    return f"fp:{code}:{zeile}"


def schluessel_vb(tabelle: str, posten: str) -> str:
    """Belegschlüssel eines Vorberichtspostens: `vb:{tabelle}:{posten}`."""
    return f"vb:{tabelle}:{posten}"


def schluessel_vb_gesamt(tabelle: str) -> str:
    """Belegschlüssel der gedruckten Gesamtzeile einer Vorberichtstabelle."""
    return f"vb:{tabelle}:gesamt"


def schluessel_meta(pfad: str) -> str:
    """Belegschlüssel eines MetaWerts: `meta:{pfad}` (Pfad gepunktet)."""
    return f"meta:{pfad}"


def schluessel_gz(produkt: str, position: int | str) -> str:
    """Belegschlüssel einer Grundzahl: `gz:{produkt}:{position}`."""
    return f"gz:{produkt}:{position}"


def schluessel_pr(produkt: str) -> str:
    """Belegschlüssel der Startseite eines Produkts: `pr:{produkt}`."""
    return f"pr:{produkt}"


def schluessel_inv(produkt: str, massnahme_id: str, konto: str, richtung: str) -> str:
    """Belegschlüssel einer Maßnahme: `inv:{produkt}:{massnahme_id}:{konto}:{richtung}`."""
    return f"inv:{produkt}:{massnahme_id}:{konto}:{richtung}"


def schluessel_ve(produkt: str, massnahme_id: str, konto: str) -> str:
    """Belegschlüssel einer VE-Kontozeile: `ve:{produkt}:{massnahme_id}:{konto}`."""
    return f"ve:{produkt}:{massnahme_id}:{konto}"


def schluessel_sd(reihe: str) -> str:
    """Belegschlüssel einer Schuldenstandsreihe: `sd:{reihe}`."""
    return f"sd:{reihe}"


def schluessel_sp(teil: str, position: int | str, produktbereich: str | None) -> str:
    """Belegschlüssel einer Stellenplanzeile: `sp:{teil}:{position}:{produktbereich oder -}`."""
    return f"sp:{teil}:{position}:{produktbereich or '-'}"


def schluessel_seite(pdf_seite: int) -> str:
    """Belegschlüssel eines Seitenbelegs ohne Zeile: `seite:{n}`."""
    return f"seite:{pdf_seite}"


def bbox_mit_rand(
    woerter: Iterable[WortRahmen], breite: float, hoehe: float, rand: float = 2.0
) -> list[float]:
    """Umschließendes Rechteck `[x0, top, x1, bottom]` der Wörter mit `rand` pt Rand.

    Auf die Seite (`0..breite`, `0..hoehe`) begrenzt und auf zwei Dezimalstellen gerundet.
    """
    wortliste = list(woerter)
    if not wortliste:
        raise QuellenFehler("bbox_mit_rand: keine Wörter übergeben")
    x0 = max(0.0, min(w.x0 for w in wortliste) - rand)
    top = max(0.0, min(w.top for w in wortliste) - rand)
    x1 = min(breite, max(w.x1 for w in wortliste) + rand)
    bottom = min(hoehe, max(w.bottom for w in wortliste) + rand)
    return [round(x0, 2), round(top, 2), round(x1, 2), round(bottom, 2)]


def _parse_betrag(text: str) -> int | None:
    try:
        return lies_betrag(text)
    except ZahlenFehler:
        return None


def _zahl(text: str) -> float | None:
    """Liest ein gedrucktes Zahlwort (deutsches Tausenderformat, Komma-Dezimalteil).

    Umschließende Klammern (`(2.000.000)`) und ein angehängtes Satzzeichen werden ignoriert;
    jeder andere Text (auch `2.4.1` oder ein Datum) ist keine Zahl.
    """
    kandidat = text.strip("()").rstrip(",;:")
    try:
        ergebnis = lies_kennzahl(kandidat)
    except ZahlenFehler:
        return None
    return None if ergebnis is None else ergebnis[0]


def _wort_norm(text: str) -> str:
    """Wort ohne umschließende Klammern, Anführungszeichen und angehängte Satzzeichen."""
    return text.strip('()„“"').rstrip(",;:.")


def _gleich(gedruckt: float, soll: float) -> bool:
    return abs(gedruckt - soll) <= _ZAHL_TOLERANZ


def finde_planzeile(
    zeilen: Sequence[RahmenZeile],
    nummer: str,
    betrag: int,
    *,
    breite: float,
    hoehe: float,
) -> Suche:
    """Sucht die gedruckte Planzeile `nummer` mit dem Haushaltsjahrbetrag `betrag`.

    Eine Zeile gilt als gefunden, wenn ihr erstes Wort die gedruckte Zeilennummer ist und
    (bei einem Betrag ungleich null) ein weiteres Wort der Zeile von `zahlen.lies_betrag` zu
    `betrag` gelesen wird. Genau ein Treffer ergibt das Rechteck der ganzen Zeile; sonst
    `(None, grund)` mit `nicht_gefunden`, `mehrdeutig` oder `betrag_fehlt` (D-03: nie raten).
    """
    kandidaten = [z for z in zeilen if z.woerter and z.woerter[0].text == nummer]
    if not kandidaten:
        return None, GRUND_NICHT_GEFUNDEN
    if betrag != 0:
        kandidaten = [
            z for z in kandidaten if any(_parse_betrag(w.text) == betrag for w in z.woerter[1:])
        ]
        if not kandidaten:
            return None, GRUND_BETRAG_FEHLT
    if len(kandidaten) > 1:
        return None, GRUND_MEHRDEUTIG
    return bbox_mit_rand(kandidaten[0].woerter, breite, hoehe), None


def _norm(text: str) -> str:
    return normalisiere_bezeichnung(text)


def _zeilentext(zeile: RahmenZeile) -> str:
    """Wörter der Zeile ohne Trennzeichen, normalisiert (Leerzeichen und Bindestriche entfernt)."""
    return _norm("".join(wort.text for wort in zeile.woerter))


def _zerlege_tabellenzeile(zeile: RahmenZeile) -> tuple[str, list[float]]:
    """Trennt eine Tabellenzeile in Beschriftung (Wörter vor der ersten Zahl) und Zahlen."""
    erste_zahl = next((i for i, w in enumerate(zeile.woerter) if _zahl(w.text) is not None), None)
    if erste_zahl is None:
        return " ".join(w.text for w in zeile.woerter), []
    label = " ".join(w.text for w in zeile.woerter[:erste_zahl])
    zahlen = [z for w in zeile.woerter[erste_zahl:] if (z := _zahl(w.text)) is not None]
    return label, zahlen


def _label_passt(zeilenlabel: str, bezeichnung: str) -> bool:
    """Gleichheit, Präfix oder Suffix der normalisierten Beschriftungen (Umbruch, Nummerierung).

    Eine führende Gliederungsnummer der gedruckten Zeile (`9.`, `2.5.1`) bleibt außer Acht. Ein
    Präfix oder Suffix zählt nur ab vier Zeichen, damit ein kurzer Rest keine fremde Zeile trifft.
    """
    gedruckt = _NUMMER_MUSTER.sub("", _norm(zeilenlabel))
    soll = _norm(bezeichnung)
    if not gedruckt or not soll:
        return False
    if gedruckt == soll:
        return True
    kurz, lang = sorted((gedruckt, soll), key=len)
    return len(kurz) >= 4 and (lang.startswith(kurz) or lang.endswith(kurz))


def _ist_teilfolge(soll: Sequence[float], ist: Sequence[float]) -> bool:
    position = 0
    for wert in soll:
        while position < len(ist) and not _gleich(ist[position], wert):
            position += 1
        if position == len(ist):
            return False
        position += 1
    return True


def finde_tabellenzeile(
    zeilen: Sequence[RahmenZeile],
    bezeichnung: str,
    werte: Sequence[float | None],
    *,
    ziel_index: int,
    breite: float,
    hoehe: float,
) -> Suche:
    """Sucht die Tabellenzeile `bezeichnung` mit dem Wert des Haushaltsjahrs (`werte[ziel_index]`).

    `werte` stehen in der gedruckten Einheit (T€ oder Euro), `None` für ein Jahr ohne Wert.
    Beschriftung und Zielwert müssen zusammen eine Zeile ergeben; bei mehreren Zeilen entscheidet
    die vollständige Folge aller gedruckten Werte. Ohne Zielwert zählt die Beschriftung allein.
    Zwei oder mehr Treffer ergeben `mehrdeutig`, keiner `nicht_gefunden` bzw. `betrag_fehlt`.
    """
    kandidaten: list[tuple[RahmenZeile, list[float]]] = []
    for zeile in zeilen:
        label, zahlen = _zerlege_tabellenzeile(zeile)
        if _label_passt(label, bezeichnung):
            kandidaten.append((zeile, zahlen))
    if not kandidaten:
        return None, GRUND_NICHT_GEFUNDEN
    ziel = werte[ziel_index]
    if ziel is not None:
        kandidaten = [(z, b) for z, b in kandidaten if any(_gleich(x, ziel) for x in b)]
        if not kandidaten:
            return None, GRUND_BETRAG_FEHLT
        if len(kandidaten) > 1:
            gedruckt = [w for w in werte if w is not None]
            vollstaendig = [(z, b) for z, b in kandidaten if _ist_teilfolge(gedruckt, b)]
            if vollstaendig:
                kandidaten = vollstaendig
    if len(kandidaten) > 1:
        return None, GRUND_MEHRDEUTIG
    return bbox_mit_rand(kandidaten[0][0].woerter, breite, hoehe), None


def _deutsch(zahl: int) -> str:
    """Ganzzahl im deutschen Tausenderformat (`11.741`)."""
    return f"{zahl:,}".replace(",", ".")


def _dezimal(zahl: float) -> str:
    """Zahl mit Komma als Dezimaltrennzeichen und ohne überflüssige Nachkommastellen."""
    text = f"{zahl:.4f}".rstrip("0").rstrip(".")
    ganz, _, rest = text.partition(".")
    gruppiert = _deutsch(int(ganz)) if ganz.lstrip("-").isdigit() else ganz
    return gruppiert + ("," + rest if rest else "")


def meta_kandidaten(wert: int | float | str, einheit: str, gerundet: bool) -> list[str]:
    """Gedruckte Schreibweisen eines MetaWerts (deutsches Format, Datum `tt.mm.jjjj`).

    Ein gerundeter Eurobetrag steht im Vorbericht oft in T€ (`315.000` und `315`); Promille
    erscheinen als Prozent mit Komma (363 als `36,3`), Hektar als Quadratkilometer (8960 als
    `89,6`).
    """
    if isinstance(wert, str):
        if einheit == "datum":
            jahr, monat, tag = wert.split("-")
            return [f"{tag}.{monat}.{jahr}"]
        return [wert]
    if isinstance(wert, float) and not wert.is_integer():
        return [_dezimal(wert)]
    ganz = int(wert)
    formen = [_deutsch(ganz)]
    if gerundet and ganz % 1000 == 0 and ganz != 0:
        formen.append(_deutsch(ganz // 1000))
    if einheit == "promille":
        formen.append(_dezimal(ganz / 10))
    if einheit == "ha":
        formen.append(_dezimal(ganz / 100))
    return formen


def finde_wertzeile(
    zeilen: Sequence[RahmenZeile],
    kandidaten: Sequence[str],
    *,
    seite: int,
    breite: float,
    hoehe: float,
) -> Suche:
    """Sucht die eine Zeile, in der ein Wort genau einer der gedruckten Schreibweisen entspricht.

    Die Zeile, die nur die Seitenzahl enthält, zählt nicht. Mehrere Zeilen ergeben `mehrdeutig`.
    """
    treffer = []
    for zeile in zeilen:
        if len(zeile.woerter) == 1 and zeile.woerter[0].text == str(seite):
            continue
        woerter = {_wort_norm(w.text) for w in zeile.woerter}
        if any(kandidat in woerter for kandidat in kandidaten):
            treffer.append(zeile)
    if not treffer:
        return None, GRUND_NICHT_GEFUNDEN
    if len(treffer) > 1:
        return None, GRUND_MEHRDEUTIG
    return bbox_mit_rand(treffer[0].woerter, breite, hoehe), None


@dataclass(frozen=True)
class KontozeilenText:
    """Gedruckte Texte, die eine Kontozeile begrenzen (`layout.investitionen`)."""

    summen: tuple[str, ...]
    kassenwirksamkeit: str


def _kontozeilen_block(
    zeilen: Sequence[RahmenZeile],
    index: int,
    texte: KontozeilenText,
    *,
    mit_kassenwirksamkeit: bool,
) -> list[RahmenZeile]:
    """Die Kontozeile ab `index` samt Umbruchzeilen (Beschriftung, `(Kassenwirksamkeit)`)."""
    block = [zeilen[index]]
    for zeile in zeilen[index + 1 :]:
        text = _zeilentext(zeile)
        if zeile.top - block[-1].bottom > _UMBRUCH_ABSTAND:
            break
        if any(text.startswith(summe) for summe in texte.summen):
            break
        if re.match(r"\d{6}", zeile.woerter[0].text):
            break
        if text.startswith(texte.kassenwirksamkeit):
            if mit_kassenwirksamkeit:
                block.append(zeile)
            break
        if any(_zahl(w.text) is not None for w in zeile.woerter):
            break
        block.append(zeile)
    return block


def finde_kontozeile(
    zeilen: Sequence[RahmenZeile],
    massnahme_id: str,
    konto: str,
    betrag: float | None,
    *,
    texte: KontozeilenText,
    mit_kassenwirksamkeit: bool,
    pflicht_betraege: Sequence[float] = (),
    breite: float,
    hoehe: float,
) -> Suche:
    """Sucht die Kontozeile `konto` einer Maßnahme (Kontowort plus Betrag).

    Kandidaten sind Zeilen, deren erstes Wort mit dem sechsstelligen `konto` beginnt, mit dem
    `betrag` des Haushaltsjahrs (bei `None` ohne Betragsprüfung) und, für VE-Zeilen, mit allen
    `pflicht_betraege` in der Zeile samt Umbruch (`(Kassenwirksamkeit)`-Zeile). Mehrere Konten
    gleicher Nummer auf der Seite löst die Lage zwischen der Maßnahmen-Kopfzeile und ihrer
    Saldozeile; sonst `mehrdeutig`. Das Rechteck umschließt die Zeile samt Umbruchzeilen.
    """
    indizes = [i for i, z in enumerate(zeilen) if z.woerter[0].text.startswith(konto)]
    if not indizes:
        return None, GRUND_NICHT_GEFUNDEN
    if betrag is not None:
        indizes = [
            i
            for i in indizes
            if any(
                (zahl := _zahl(w.text)) is not None and _gleich(zahl, betrag)
                for w in zeilen[i].woerter[1:]
            )
        ]
        if not indizes:
            return None, GRUND_BETRAG_FEHLT
    if pflicht_betraege:
        indizes = [
            i
            for i in indizes
            if all(
                any(
                    (zahl := _zahl(w.text)) is not None and _gleich(zahl, soll)
                    for zeile in _kontozeilen_block(zeilen, i, texte, mit_kassenwirksamkeit=True)
                    for w in zeile.woerter
                )
                for soll in pflicht_betraege
            )
        ]
        if not indizes:
            return None, GRUND_BETRAG_FEHLT
    if len(indizes) > 1:
        indizes = _in_massnahme(zeilen, massnahme_id, indizes) or indizes
    if len(indizes) != 1:
        return None, GRUND_MEHRDEUTIG
    block = _kontozeilen_block(
        zeilen, indizes[0], texte, mit_kassenwirksamkeit=mit_kassenwirksamkeit
    )
    return bbox_mit_rand((w for zeile in block for w in zeile.woerter), breite, hoehe), None


def _in_massnahme(
    zeilen: Sequence[RahmenZeile], massnahme_id: str, indizes: list[int]
) -> list[int]:
    """Kandidaten zwischen der Kopfzeile der Maßnahme und ihrer Saldozeile."""
    kennung = _norm(massnahme_id)
    kopf = next(
        (
            i
            for i, z in enumerate(zeilen)
            if _zeilentext(z).startswith(kennung) and not _zeilentext(z).startswith("Saldo")
        ),
        None,
    )
    if kopf is None:
        return indizes
    ende = next(
        (i for i in range(kopf + 1, len(zeilen)) if _zeilentext(zeilen[i]).startswith("Saldo")),
        len(zeilen),
    )
    return [i for i in indizes if kopf < i < ende]


def _stellen_formen(wert: float) -> set[str]:
    """Gedruckte Schreibweisen einer Stellenzahl (`2,00`, `2`, `0,41`, `0,5`)."""
    return {f"{wert:.2f}".replace(".", ","), f"{wert:g}".replace(".", ",")}


def _beginnt_mit_woertern(zeile: RahmenZeile, text: str) -> bool:
    """True, wenn die ersten Wörter der Zeile zusammen genau `text` (normalisiert) ergeben."""
    soll = _norm(text)
    for k in range(1, min(len(zeile.woerter), 8) + 1):
        if _norm("".join(w.text for w in zeile.woerter[:k])) == soll:
            return True
    return False


def _ohne_seitenzahl(zeilen: Sequence[RahmenZeile], seite: int) -> list[RahmenZeile]:
    """Entfernt die am Zeilenanfang verschmolzene Seitenzahl (Querformat, gedreht gedruckt)."""
    bereinigt: list[RahmenZeile] = []
    for zeile in zeilen:
        if len(zeile.woerter) > 1 and zeile.woerter[0].text == str(seite):
            woerter = zeile.woerter[1:]
            zeile = RahmenZeile(
                top=min(w.top for w in woerter),
                bottom=max(w.bottom for w in woerter),
                woerter=woerter,
            )
        bereinigt.append(zeile)
    return bereinigt


def _enthaelt_stellen(woerter: Iterable[WortRahmen], formen: set[str]) -> bool:
    return any(_wort_norm(w.text) in formen for w in woerter)


def finde_stellenzeile(
    zeilen: Sequence[RahmenZeile],
    *,
    teil: str,
    gruppe: str,
    amtsbezeichnung: str | None,
    verguetung: str | None,
    produktbereich: str | None,
    stellen: float | None,
    seite: int,
    breite: float,
    hoehe: float,
) -> Suche:
    """Sucht die gedruckte Stellenplanzeile (Teil A/B, Nachwuchs oder Stellenübersicht).

    Teil A/B: die Zeile beginnt mit Amtsbezeichnung und Gruppe bzw. der Entgeltgruppe; bei einem
    Stellenwert des Haushaltsjahrs muss er (als Dezimalzahl mit Komma) in der Zeile stehen.
    Nachwuchskräfte: erstes Wort der Bezeichnung plus Art der Vergütung. Stellenübersicht: die
    Zeile des Produktbereichs samt Umbruchzeile; alle Zellen der Zeile teilen sich ihr Rechteck.
    """
    zeilen = _ohne_seitenzahl(zeilen, seite) if breite > hoehe else list(zeilen)
    formen = _stellen_formen(stellen) if stellen is not None else None

    if produktbereich is not None:
        kandidaten = []
        for index, zeile in enumerate(zeilen):
            if zeile.woerter[0].text != produktbereich:
                continue
            block = [zeile]
            for folge in zeilen[index + 1 :]:
                erstes = folge.woerter[0].text
                if (
                    folge.top - block[-1].bottom > _UMBRUCH_ABSTAND
                    or _PRODUKTBEREICH_MUSTER.match(erstes)
                    or _norm(erstes) in ("Summe", "insgesamt")
                ):
                    break
                block.append(folge)
            kandidaten.append(block)
        if formen is not None:
            kandidaten = [
                b
                for b in kandidaten
                if _enthaelt_stellen((w for z in b for w in z.woerter), formen)
            ]
            fehlt = GRUND_BETRAG_FEHLT
        else:
            fehlt = GRUND_NICHT_GEFUNDEN
        return _eindeutiger_block(kandidaten, breite, hoehe, fehlt)

    if teil == "nachwuchs":
        erstes_wort = _norm(gruppe.split()[0])
        art = _norm(verguetung or "")
        kandidaten = [
            [z]
            for z in zeilen
            if _norm(z.woerter[0].text).startswith(erstes_wort) and art in _zeilentext(z)
        ]
        return _eindeutiger_block(kandidaten, breite, hoehe, GRUND_NICHT_GEFUNDEN)

    beschriftung = _norm(amtsbezeichnung or "") + _norm(gruppe)
    kandidaten = [[z] for z in zeilen if _beginnt_mit_woertern(z, beschriftung)]
    if formen is not None:
        kandidaten = [b for b in kandidaten if _enthaelt_stellen(b[0].woerter, formen)]
        fehlt = GRUND_BETRAG_FEHLT
    else:
        fehlt = GRUND_NICHT_GEFUNDEN
    return _eindeutiger_block(kandidaten, breite, hoehe, fehlt)


def _eindeutiger_block(
    kandidaten: Sequence[Sequence[RahmenZeile]], breite: float, hoehe: float, fehlt: str
) -> Suche:
    if not kandidaten:
        return None, fehlt
    if len(kandidaten) > 1:
        return None, GRUND_MEHRDEUTIG
    return bbox_mit_rand((w for z in kandidaten[0] for w in z.woerter), breite, hoehe), None


def _gleich_stellen(gedruckt: float, soll: float, nachkommastellen: int) -> bool:
    """Gleichheit auf die gedruckten Nachkommastellen genau (Grundzahlen: Gebühren, Quoten)."""
    return abs(gedruckt - soll) < 0.5 * 10 ** (-nachkommastellen)


def finde_grundzahlzeile(
    zeilen: Sequence[RahmenZeile],
    bezeichnung: str,
    wert: float,
    nachkommastellen: int,
    *,
    breite: float,
    hoehe: float,
) -> Suche:
    """Sucht die Grundzahl-Zeile mit der Beschriftung `bezeichnung` und dem Wert `wert`.

    Die Beschriftung (normalisiert) muss am Zeilenanfang stehen, dahinter höchstens die
    gedruckte Einheit; ein über mehrere Zeilen umbrochener Name findet keine Zeile und ergibt
    `nicht_gefunden`. Der Wert muss unter den gedruckten Zahlen der Zeile vorkommen.
    """
    soll = _norm(bezeichnung)
    kandidaten: list[tuple[RahmenZeile, list[float]]] = []
    for zeile in zeilen:
        label, zahlen = _zerlege_tabellenzeile(zeile)
        gedruckt = _norm(label)
        if gedruckt.startswith(soll) and len(gedruckt) - len(soll) <= _EINHEIT_MAX_ZEICHEN:
            kandidaten.append((zeile, zahlen))
    if not kandidaten:
        return None, GRUND_NICHT_GEFUNDEN
    kandidaten = [
        (z, b) for z, b in kandidaten if any(_gleich_stellen(x, wert, nachkommastellen) for x in b)
    ]
    if not kandidaten:
        return None, GRUND_BETRAG_FEHLT
    if len(kandidaten) > 1:
        return None, GRUND_MEHRDEUTIG
    return bbox_mit_rand(kandidaten[0][0].woerter, breite, hoehe), None


# Folgezeilen mit höchstens diesem Abstand (Punkte) gehören noch zu einer umbrochenen Überschrift.
_UEBERSCHRIFT_ABSTAND = 6.0


def finde_produktzeile(
    zeilen: Sequence[RahmenZeile], produkt: str, kopf_muster: str, *, breite: float, hoehe: float
) -> Suche:
    """Sucht die Kopfzeile `Produkt {code} {Name}` (Muster `kopfzeilen.produkt`) der Seite.

    Eine eng folgende Umbruchzeile des Namens gehört zum Rechteck. Genau eine Kopfzeile des
    Produkts auf der Seite ist nötig.
    """
    muster = re.compile(kopf_muster)
    indizes = []
    for index, zeile in enumerate(zeilen):
        treffer = muster.match(zeile.text)
        if treffer is not None and treffer.group(1) == produkt:
            indizes.append(index)
    if not indizes:
        return None, GRUND_NICHT_GEFUNDEN
    if len(indizes) > 1:
        return None, GRUND_MEHRDEUTIG
    block = [zeilen[indizes[0]]]
    for folge in zeilen[indizes[0] + 1 :]:
        if folge.top - block[-1].bottom > _UEBERSCHRIFT_ABSTAND:
            break
        block.append(folge)
    return bbox_mit_rand((w for z in block for w in z.woerter), breite, hoehe), None


def finde_pruefwoerter(
    zeilen: Sequence[RahmenZeile], pruefwoerter: Sequence[str]
) -> list[tuple[str, int]]:
    """Stichwörter der Datenschutz-Prüfliste je Zeile: `(Stichwort, 1-basierter Zeilenindex)`.

    Liefert nie den Text der Zeile. Verglichen wird auf dem normalisierten, zusammengezogenen
    Zeilentext, damit auch die eng gesetzten Wörter des PDFs (`Bürgermeister`) treffen.
    """
    treffer: list[tuple[str, int]] = []
    normalisiert = [(wort, _norm(wort)) for wort in pruefwoerter]
    for index, zeile in enumerate(zeilen, start=1):
        text = _zeilentext(zeile)
        treffer.extend((wort, index) for wort, kurz in normalisiert if kurz and kurz in text)
    return treffer


def rechtecke_nach_etiketten(
    zeilen: Sequence[RahmenZeile], etiketten: Sequence[str], *, breite: float, hoehe: float
) -> list[list[float]]:
    """Schwärzungsrechtecke für die Zeile direkt nach einer Etikettzeile (`schwaerzen_nach`).

    Eine Etikettzeile ist eine Zeile, deren normalisierter Text genau dem Etikett entspricht.
    Das Rechteck umschließt alle Wörter der Folgezeile mit 1 pt Rand.
    """
    rechtecke: list[list[float]] = []
    for etikett in etiketten:
        soll = _norm(etikett)
        for index, zeile in enumerate(zeilen[:-1]):
            if _zeilentext(zeile) == soll:
                rechtecke.append(bbox_mit_rand(zeilen[index + 1].woerter, breite, hoehe, rand=1.0))
    return rechtecke


def _haushaltsjahr_wertart(jahrgang: Jahrgang, plantyp: str) -> str:
    """Wertart der Spalte des Haushaltsjahrs (ohne VE-Spalte) aus `jahrgang.spalten`."""
    wertarten: list[str] = []
    for kopf in jahrgang.spalten[plantyp]:
        wertart, jahr = zerlege_spaltenkopf(kopf)
        if jahr == jahrgang.haushaltsjahr and wertart != _WERTART_VE:
            wertarten.append(wertart)
    if len(wertarten) != 1:
        raise QuellenFehler(
            f"Plantyp {plantyp}: Spalte des Haushaltsjahrs {jahrgang.haushaltsjahr} nicht "
            f"eindeutig bestimmbar ({wertarten})"
        )
    return wertarten[0]


@dataclass(frozen=True)
class _Planzeile:
    ebene: str
    code: str
    zeile: str
    zeile_kanonisch: str
    betrag: int
    pdf_seite: int


def _lies_planzeilen(
    daten_wurzel: Path, jahrgang: Jahrgang, csv: Path, plantyp: str, *, nur_gesamt: bool
) -> list[_Planzeile]:
    """Liest die Haushaltsjahr-Zeilen einer Plan-CSV, je (Ebene, Code, Zeile) genau eine."""
    wertart = _haushaltsjahr_wertart(jahrgang, plantyp)
    df = lies_plan_csv(daten_wurzel / csv)
    if nur_gesamt:
        df = df.filter(pl.col("ebene") == _GESAMT)
    haushaltsjahr = df.filter(
        (pl.col("jahr") == jahrgang.haushaltsjahr) & (pl.col("wertart") == wertart)
    ).sort(["ebene", "code", "zeile"])
    schluessel = haushaltsjahr.select("ebene", "code", "zeile_kanonisch").unique().height
    if schluessel != haushaltsjahr.height:
        raise QuellenFehler(f"{csv}: Haushaltsjahr-Zeilen sind nicht eindeutig je Knoten und Zeile")
    if nur_gesamt:
        erwartet = df["zeile_kanonisch"].n_unique()
        if haushaltsjahr.height != erwartet:
            raise QuellenFehler(
                f"{csv}: {haushaltsjahr.height} Haushaltsjahr-Zeilen für {erwartet} "
                "GESAMT-Zeilen (je Zeile wird genau ein Wert erwartet)"
            )
    return [
        _Planzeile(
            ebene=zeile["ebene"],
            code=_GESAMT if zeile["ebene"] == _GESAMT else zeile["code"],
            zeile=zeile["zeile"],
            zeile_kanonisch=zeile["zeile_kanonisch"],
            betrag=zeile["betrag"],
            pdf_seite=zeile["pdf_seite"],
        )
        for zeile in haushaltsjahr.iter_rows(named=True)
    ]


class _Seiten:
    """Gemeinsamer Zugriff auf Zeilen, Abschnitte und Maße der PDF-Seiten (mit Zwischenspeicher)."""

    def __init__(self, pdf: PdfDokument, jahrgang: Jahrgang) -> None:
        self._pdf = pdf
        self._jahrgang = jahrgang
        self._masse: dict[int, tuple[float, float]] = {}
        self._teilergebnisplan: dict[int, tuple[RahmenZeile, ...]] = {}

    def masse(self, seite: int) -> tuple[float, float]:
        if seite not in self._masse:
            self._masse[seite] = self._pdf.seitenmass(seite)
        return self._masse[seite]

    @property
    def alle_masse(self) -> dict[int, tuple[float, float]]:
        return dict(sorted(self._masse.items()))

    def zeilen(self, seite: int) -> tuple[RahmenZeile, ...]:
        return self._pdf.zeilen_mit_rahmen(seite)

    def teilergebnisplan(self, seite: int) -> tuple[RahmenZeile, ...]:
        """Nur die Zeilen des Teilergebnisplan-Abschnitts der Seite (nie Teilfinanzplan)."""
        if seite not in self._teilergebnisplan:
            tops = {
                zeile.top
                for abschnitt in lies_abschnitte(self._pdf.zeilen(seite), self._jahrgang, seite)
                if abschnitt.plantyp == "teilergebnisplan"
                for zeile in abschnitt.zeilen
            }
            self._teilergebnisplan[seite] = tuple(
                z for z in self._pdf.zeilen_mit_rahmen(seite) if z.top in tops
            )
        return self._teilergebnisplan[seite]


class _Schwaerzung:
    """Schwärzungsrechtecke je Seite: Personenfelder plus Zeilen nach Etiketten."""

    def __init__(
        self, seiten: _Seiten, personen: Mapping[int, Sequence[Rechteck]], etiketten: Sequence[str]
    ) -> None:
        self._seiten = seiten
        self._personen = personen
        self._etiketten = etiketten
        self._zwischenspeicher: dict[int, tuple[Rechteck, ...]] = {}

    def fuer(self, seite: int) -> tuple[Rechteck, ...]:
        if seite not in self._zwischenspeicher:
            rechtecke = {tuple(r) for r in self._personen.get(seite, ())}
            if self._etiketten:
                breite, hoehe = self._seiten.masse(seite)
                rechtecke |= {
                    (r[0], r[1], r[2], r[3])
                    for r in rechtecke_nach_etiketten(
                        self._seiten.zeilen(seite), self._etiketten, breite=breite, hoehe=hoehe
                    )
                }
            self._zwischenspeicher[seite] = tuple(sorted(rechtecke))
        return self._zwischenspeicher[seite]


def _schneidet(bbox: Sequence[float], rechteck: Rechteck) -> bool:
    return not (
        bbox[2] <= rechteck[0]
        or rechteck[2] <= bbox[0]
        or bbox[3] <= rechteck[1]
        or rechteck[3] <= bbox[1]
    )


@dataclass
class _Sammler:
    """Sammelt die Belege einer Erzeugung und merkt sich die Gründe fehlender Rechtecke."""

    seiten: _Seiten
    schwaerzung: _Schwaerzung
    belege: dict[str, dict[str, object]] = field(default_factory=dict)
    ohne_bbox: dict[str, str] = field(default_factory=dict)

    def eintragen(
        self, schluessel: str, seite: int, bbox: list[float] | None, grund: str | None
    ) -> None:
        if schluessel in self.belege:
            raise QuellenFehler(f"Beleg {schluessel} doppelt vergeben")
        self.seiten.masse(seite)
        self.belege[schluessel] = {"pdf_seite": seite, "bild": bild_name(seite), "bbox": bbox}
        if bbox is None and grund is not None:
            self.ohne_bbox[schluessel] = grund

    def suche(self, schluessel: str, seite: int, finder: Callable[[float, float], Suche]) -> None:
        """Trägt den Beleg ein; `finder(breite, hoehe)` liefert `(bbox, grund)`.

        Ein Rechteck, das eine Schwärzung berührt, wird verworfen (`ueberlappt_schwaerzung`):
        Die Markierung darf nie über geschwärzten Text laufen.
        """
        breite, hoehe = self.seiten.masse(seite)
        bbox, grund = finder(breite, hoehe)
        if bbox is not None and any(_schneidet(bbox, r) for r in self.schwaerzung.fuer(seite)):
            bbox, grund = None, GRUND_SCHWAERZUNG
        self.eintragen(schluessel, seite, bbox, grund or GRUND_NICHT_GEFUNDEN)


def _lies_app_json(app_daten_wurzel: Path, datei: Path) -> dict:
    pfad = app_daten_wurzel / datei
    if not pfad.is_file():
        raise QuellenFehler(f"{pfad}: App-JSON fehlt (Schritt 07 muss vor Schritt 08 laufen)")
    return json.loads(pfad.read_text(encoding="utf-8"))


def _sammle_plaene(
    sammler: _Sammler, jahrgang: Jahrgang, daten_wurzel: Path, haushalt: Mapping[str, object]
) -> None:
    """ep für jede gedruckte Zeile jedes Knotens (außer KL), fp für jede GESAMT-Zeile."""
    app_zeilen = {code: set(werte["zeilen"]) for code, werte in haushalt["ergebnisplan"].items()}
    for csv, plantyp, art in (
        (ERGEBNISPLAN_CSV, "ergebnisplan", "ep"),
        (FINANZPLAN_CSV, "finanzplan", "fp"),
    ):
        planzeilen = _lies_planzeilen(daten_wurzel, jahrgang, csv, plantyp, nur_gesamt=art == "fp")
        for planzeile in planzeilen:
            if art == "ep":
                if planzeile.code.startswith(_KL_PRAEFIX):
                    continue
                if planzeile.zeile_kanonisch not in app_zeilen.get(planzeile.code, ()):
                    continue
                schluessel = schluessel_ep(planzeile.code, planzeile.zeile_kanonisch)
            else:
                schluessel = schluessel_fp(planzeile.code, planzeile.zeile_kanonisch)
            seite = planzeile.pdf_seite
            zeilen = (
                sammler.seiten.zeilen(seite)
                if planzeile.ebene == _GESAMT
                else sammler.seiten.teilergebnisplan(seite)
            )
            sammler.suche(
                schluessel,
                seite,
                lambda breite, hoehe, z=zeilen, p=planzeile: finde_planzeile(
                    z, p.zeile, p.betrag, breite=breite, hoehe=hoehe
                ),
            )


def _lies_vorbericht_tabellen(daten_wurzel: Path) -> dict[str, pl.DataFrame]:
    """Die manuellen Vorberichtstabellen wie in `app_daten.erzeuge_app_daten` (nur lesend)."""
    return {
        "steuerarten": lies_vorbericht_csv(daten_wurzel / STEUERARTEN_CSV),
        "zuwendungen": lies_vorbericht_csv(daten_wurzel / ZUWENDUNGEN_CSV),
        "transferaufwendungen": lies_vorbericht_csv(daten_wurzel / TRANSFERAUFWENDUNGEN_CSV),
        "kita_zuschuesse": lies_vorbericht_csv(daten_wurzel / KITA_ZUSCHUESSE_CSV),
        "zuschuesse_lfd_zwecke": lies_vorbericht_csv(daten_wurzel / ZUSCHUESSE_LFD_ZWECKE_CSV),
        "investitionszuwendungen": lies_vorbericht_csv(daten_wurzel / INVESTITIONSZUWENDUNGEN_CSV),
        **zerlege_weitere_vorberichtstabellen(
            lies_vorbericht_csv(daten_wurzel / WEITERE_VORBERICHTSTABELLEN_CSV)
        ),
        "eigenkapital": lies_eigenkapital_csv(daten_wurzel / EIGENKAPITAL_CSV),
    }


def _haushaltsjahr_index(jahrgang: Jahrgang, jahre: Sequence[int]) -> int:
    if jahrgang.haushaltsjahr not in jahre:
        raise QuellenFehler(
            f"Haushaltsjahr {jahrgang.haushaltsjahr} fehlt in den App-Jahren {jahre}"
        )
    return list(jahre).index(jahrgang.haushaltsjahr)


def _sammle_vorbericht(
    sammler: _Sammler, jahrgang: Jahrgang, daten_wurzel: Path, haushalt: Mapping[str, object]
) -> None:
    """vb für jeden Posten und jede gedruckte Gesamtzeile mit Quellseite (inkl. Eigenkapital)."""
    tabellen_df = _lies_vorbericht_tabellen(daten_wurzel)
    index = _haushaltsjahr_index(jahrgang, haushalt["jahre"])
    tabellen = {**haushalt["vorbericht"], "eigenkapital": haushalt["eigenkapital"]}
    for tabelle, daten in tabellen.items():
        df = tabellen_df[tabelle]
        teiler = 1000 if daten["quelle_einheit"] == "teur" else 1

        def _gedruckt(werte: Sequence[int | None], t: int = teiler) -> list[float | None]:
            return [None if w is None else w / t for w in werte]

        for posten in daten["posten"]:
            seite = posten["quelle"]
            if seite is None:
                continue
            schluessel = schluessel_vb(tabelle, posten["posten"])
            if posten["berechnet"]:
                sammler.eintragen(schluessel, seite, None, GRUND_BERECHNET)
                continue
            sammler.suche(
                schluessel,
                seite,
                lambda breite, hoehe, s=seite, p=posten, g=_gedruckt: finde_tabellenzeile(
                    sammler.seiten.zeilen(s),
                    p["name"],
                    g(p["werte"]),
                    ziel_index=index,
                    breite=breite,
                    hoehe=hoehe,
                ),
            )
        gesamt = daten["gesamt_vorbericht"]
        if gesamt["quelle"] is not None:
            gesamt_df = df.filter(pl.col("ist_gesamt"))
            bezeichnung = gesamt_df["posten_name"][0]
            sammler.suche(
                schluessel_vb_gesamt(tabelle),
                gesamt["quelle"],
                lambda breite, hoehe, g=gesamt, b=bezeichnung, f=_gedruckt: finde_tabellenzeile(
                    sammler.seiten.zeilen(g["quelle"]),
                    b,
                    f(g["werte"]),
                    ziel_index=index,
                    breite=breite,
                    hoehe=hoehe,
                ),
            )


def _meta_eintraege(meta: Mapping[str, object]) -> list[tuple[str, Mapping[str, object]]]:
    """Alle MetaWerte (Blätter mit `wert`) mit gepunktetem Pfad."""
    eintraege: list[tuple[str, Mapping[str, object]]] = []
    for name, eintrag in meta.items():
        if "wert" in eintrag:
            eintraege.append((name, eintrag))
        else:
            eintraege.extend((f"{name}.{unter}", wert) for unter, wert in eintrag.items())
    return eintraege


def _sammle_meta(sammler: _Sammler, haushalt: Mapping[str, object]) -> None:
    for pfad, meta in _meta_eintraege(haushalt["meta"]):
        seite = meta["quelle"]
        schluessel = schluessel_meta(pfad)
        if meta.get("berechnet"):
            sammler.eintragen(schluessel, seite, None, GRUND_BERECHNET)
            continue
        kandidaten = meta_kandidaten(meta["wert"], meta["einheit"], bool(meta.get("gerundet")))
        sammler.suche(
            schluessel,
            seite,
            lambda breite, hoehe, s=seite, k=kandidaten: finde_wertzeile(
                sammler.seiten.zeilen(s), k, seite=s, breite=breite, hoehe=hoehe
            ),
        )


def _sammle_schuldenstand(
    sammler: _Sammler,
    jahrgang: Jahrgang,
    daten_wurzel: Path,
    haushalt: Mapping[str, object],
    investitionen: Mapping[str, object],
) -> None:
    verbindlichkeiten = lies_vorbericht_csv(daten_wurzel / VERBINDLICHKEITEN_CSV).filter(
        pl.col("tabelle") == "verbindlichkeiten"
    )
    jahre = haushalt["jahre"]
    index = _haushaltsjahr_index(jahrgang, jahre)
    seite = investitionen["schuldenstand"]["quelle"]
    for reihe, posten in _SCHULDENSTAND_POSTEN.items():
        teil = verbindlichkeiten.filter(pl.col("posten") == posten)
        if teil.height == 0:
            raise QuellenFehler(f"verbindlichkeiten.csv: Posten {posten!r} fehlt")
        name = teil["posten_name"][0]
        je_jahr = {z["jahr"]: float(z["betrag_teur"]) for z in teil.iter_rows(named=True)}
        werte = [je_jahr.get(jahr) for jahr in jahre]
        sammler.suche(
            schluessel_sd(reihe),
            seite,
            lambda breite, hoehe, n=name, w=werte: finde_tabellenzeile(
                sammler.seiten.zeilen(seite), n, w, ziel_index=index, breite=breite, hoehe=hoehe
            ),
        )


def _kontozeilen_texte(jahrgang: Jahrgang) -> KontozeilenText:
    return KontozeilenText(
        summen=(
            _norm(layout_text(jahrgang, "investitionen", "einzahlungen_summe")),
            _norm(layout_text(jahrgang, "investitionen", "auszahlungen_summe")),
            _norm(layout_text(jahrgang, "investitionen", "saldo_praefix")),
        ),
        kassenwirksamkeit=_norm(layout_text(jahrgang, "investitionen", "kassenwirksamkeit")),
    )


def _sammle_investitionen(
    sammler: _Sammler,
    jahrgang: Jahrgang,
    haushalt: Mapping[str, object],
    investitionen: Mapping[str, object],
) -> None:
    index = _haushaltsjahr_index(jahrgang, haushalt["jahre"])
    texte = _kontozeilen_texte(jahrgang)
    for massnahme in investitionen["massnahmen"]:
        seite = massnahme["pdf_seite"]
        betrag = massnahme["werte"][index]
        sammler.suche(
            schluessel_inv(
                massnahme["produkt"],
                massnahme["massnahme_id"],
                massnahme["konto"],
                massnahme["richtung"],
            ),
            seite,
            lambda breite, hoehe, m=massnahme, s=seite, b=betrag: finde_kontozeile(
                sammler.seiten.zeilen(s),
                m["massnahme_id"],
                m["konto"],
                b,
                texte=texte,
                mit_kassenwirksamkeit=False,
                breite=breite,
                hoehe=hoehe,
            ),
        )
    faelligkeiten: dict[tuple[str, str, str], list[dict[str, object]]] = defaultdict(list)
    for ve in investitionen["ve_faelligkeiten"]:
        faelligkeiten[(ve["produkt"], ve["massnahme_id"], ve["konto"])].append(ve)
    for (produkt, massnahme_id, konto), zeilen in sorted(faelligkeiten.items()):
        seiten = {ve["pdf_seite"] for ve in zeilen}
        if len(seiten) != 1:
            raise QuellenFehler(f"VE {produkt}/{massnahme_id}/{konto}: mehrere PDF-Seiten {seiten}")
        seite = int(next(iter(seiten)))
        betraege = [float(ve["betrag"]) for ve in zeilen]
        sammler.suche(
            schluessel_ve(produkt, massnahme_id, konto),
            seite,
            lambda breite, hoehe, m=massnahme_id, k=konto, s=seite, b=betraege: finde_kontozeile(
                sammler.seiten.zeilen(s),
                m,
                k,
                None,
                texte=texte,
                mit_kassenwirksamkeit=True,
                pflicht_betraege=b,
                breite=breite,
                hoehe=hoehe,
            ),
        )


def _sammle_stellenplan(
    sammler: _Sammler, jahrgang: Jahrgang, stellenplan: Mapping[str, object]
) -> None:
    gruppen: dict[str, list[dict[str, object]]] = defaultdict(list)
    for zeile in stellenplan["zeilen"]:
        gruppen[schluessel_sp(zeile["teil"], zeile["position"], zeile["produktbereich"])].append(
            zeile
        )
    for schluessel, zeilen in gruppen.items():
        erste = zeilen[0]
        seiten = {z["pdf_seite"] for z in zeilen}
        if len(seiten) != 1:
            raise QuellenFehler(f"{schluessel}: mehrere PDF-Seiten {seiten}")
        seite = int(erste["pdf_seite"])
        stellen = next(
            (
                z["stellen"]
                for z in zeilen
                if z["merkmal"] == "stellen" and z["jahr"] == jahrgang.haushaltsjahr
            ),
            None,
        )
        sammler.suche(
            schluessel,
            seite,
            lambda breite, hoehe, e=erste, st=stellen, s=seite: finde_stellenzeile(
                sammler.seiten.zeilen(s),
                teil=e["teil"],
                gruppe=e["gruppe"],
                amtsbezeichnung=e["amtsbezeichnung"],
                verguetung=e["verguetung"],
                produktbereich=e["produktbereich"],
                stellen=st,
                seite=s,
                breite=breite,
                hoehe=hoehe,
            ),
        )


def seitenfelder(daten: object) -> set[int]:
    """Alle Seitenzahlen in den Seitenfeldern (`pdf_seite`, `quelle`, `pdf_seiten`,
    `quelle_seiten`) einer geladenen App-JSON-Struktur, rekursiv."""
    seiten: set[int] = set()
    if isinstance(daten, dict):
        for name, wert in daten.items():
            if name in _SEITENFELD and isinstance(wert, int) and not isinstance(wert, bool):
                seiten.add(wert)
            elif name in _SEITENLISTENFELD and isinstance(wert, list):
                seiten |= {s for s in wert if isinstance(s, int) and not isinstance(s, bool)}
            else:
                seiten |= seitenfelder(wert)
    elif isinstance(daten, list):
        for eintrag in daten:
            seiten |= seitenfelder(eintrag)
    return seiten


def _sammle_produkte(sammler: _Sammler, jahrgang: Jahrgang, produkte: Sequence[dict]) -> None:
    """pr für die Startseite jedes Produkts, gz für jede Grundzahl."""
    for produkt in produkte:
        code = produkt["code"]
        seite = produkt["pdf_seiten"][0]
        sammler.suche(
            schluessel_pr(code),
            seite,
            lambda breite, hoehe, c=code, s=seite: finde_produktzeile(
                sammler.seiten.zeilen(s),
                c,
                jahrgang.kopfzeilen.produkt,
                breite=breite,
                hoehe=hoehe,
            ),
        )
        for grundzahl in produkt["grundzahlen"]:
            werte = {w["jahr"]: w["wert"] for w in grundzahl["werte"]}
            if not werte:
                raise QuellenFehler(f"Grundzahl {code}/{grundzahl['position']} hat keinen Wert")
            ziel_jahr = jahrgang.haushaltsjahr if jahrgang.haushaltsjahr in werte else max(werte)
            seite_gz = grundzahl["pdf_seite"]
            sammler.suche(
                schluessel_gz(code, grundzahl["position"]),
                seite_gz,
                lambda breite, hoehe, g=grundzahl, w=werte[ziel_jahr], s=seite_gz: (
                    finde_grundzahlzeile(
                        sammler.seiten.zeilen(s),
                        g["bezeichnung"],
                        w,
                        g["nachkommastellen"],
                        breite=breite,
                        hoehe=hoehe,
                    )
                ),
            )


def _sammle_seiten(sammler: _Sammler, jahrgang: Jahrgang, app_json: Sequence[object]) -> None:
    """seite:{n} für die Vereinigung aller Seitenfelder der App-JSONs (nie mit Rechteck)."""
    vereinigung: set[int] = set()
    for daten in app_json:
        vereinigung |= seitenfelder(daten)
    ausserhalb = sorted(s for s in vereinigung if not 1 <= s <= jahrgang.anzahlen.pdf_seiten)
    if ausserhalb:
        raise QuellenFehler(
            f"App-JSONs verweisen auf PDF-Seiten außerhalb von 1..{jahrgang.anzahlen.pdf_seiten}: "
            f"{ausserhalb}"
        )
    for seite in sorted(vereinigung):
        sammler.eintragen(schluessel_seite(seite), seite, None, None)


def _art(schluessel: str) -> str:
    return schluessel.split(":", 1)[0]


def schreibe_quellenbericht(
    belege: Mapping[str, Mapping[str, object]],
    gruende: Mapping[str, str],
    pfad: Path,
    *,
    pruefliste: Sequence[tuple[int, str, int]] | None = None,
    schwaerzungen: Mapping[int, int] | None = None,
) -> None:
    """Schreibt den Bericht aller Belege ohne Rechteck (D-03), deterministisch sortiert.

    Seitenbelege (`seite:{n}`) stehen nie in den Tabellen: sie haben absichtlich kein Rechteck.
    Mit `pruefliste` (`(Seite, Stichwort, Zeilenindex)`) und `schwaerzungen` (Seite -> Anzahl
    Rechtecke) folgen die Datenschutz-Prüfliste und die Liste der geschwärzten Seiten, jeweils
    ohne Textauszug.
    """
    je_art: dict[str, list[str]] = defaultdict(list)
    for schluessel in belege:
        je_art[_art(schluessel)].append(schluessel)
    reihenfolge = [art for art in _ART_TITEL if art in je_art] + sorted(
        art for art in je_art if art not in _ART_TITEL
    )

    zeilen = [
        "# Quellenbelege – Werte ohne Markierung",
        "",
        "Schritt 08 (`pipeline/08_quellenbelege.py`) sucht zu jedem Wert mit PDF-Seite die Zeile",
        "auf der Seite (Beschriftung oder Zeilennummer plus Betrag des Haushaltsjahrs). Ohne genau",
        "einen Treffer bekommt der Beleg kein Rechteck; die App zeigt dann die Seite ohne",
        "Markierung mit einem Hinweis. Diese Datei wird bei jedem Lauf neu geschrieben.",
        "",
        "## Überblick",
        "",
        "| Art | Belege | ohne Markierung |",
        "|---|---|---|",
    ]
    ohne_je_art: dict[str, list[str]] = {}
    for art in reihenfolge:
        ohne = sorted(s for s in je_art[art] if belege[s]["bbox"] is None and art != "seite")
        ohne_je_art[art] = ohne
        anzahl = "–" if art == "seite" else str(len(ohne))
        zeilen.append(f"| {art} ({_ART_TITEL.get(art, art)}) | {len(je_art[art])} | {anzahl} |")
    for art in reihenfolge:
        ohne = ohne_je_art[art]
        if not ohne:
            continue
        zeilen += ["", f"## {art} – {_ART_TITEL.get(art, art)}", ""]
        zeilen += ["| Schlüssel | PDF-Seite | Grund |", "|---|---|---|"]
        for schluessel in ohne:
            grund = gruende.get(schluessel, GRUND_NICHT_GEFUNDEN)
            zeilen.append(f"| `{schluessel}` | {belege[schluessel]['pdf_seite']} | {grund} |")

    if pruefliste is not None:
        geschwaerzt = schwaerzungen or {}
        zeilen += [
            "",
            "## Datenschutz-Prüfliste",
            "",
            "Belegseiten, deren Text eines der Stichwörter aus `layout.quellenbelege.pruefwoerter`",
            "enthält (Seite, Stichwort, 1-basierter Zeilenindex auf der Seite; bewusst ohne",
            "Textauszug). Namen außerhalb der Personenfelder der Produktseiten werden nicht",
            "automatisch geschwärzt: Wer ein Etikett vor der zu schwärzenden Zeile kennt, trägt es",
            "in `layout.quellenbelege.schwaerzen_nach` ein.",
            "",
            "| Seite | Stichwort | Zeile | geschwärzt |",
            "|---|---|---|---|",
        ]
        for seite, wort, index in sorted(pruefliste):
            markiert = "ja" if seite in geschwaerzt else "nein"
            zeilen.append(f"| {seite} | {wort} | {index} | {markiert} |")
        zeilen += [
            "",
            "## Seiten mit Schwärzung",
            "",
            "Seiten, deren Belegbild schwarze Rechtecke über Personenfeldern trägt.",
            "",
            "| Seite | Rechtecke |",
            "|---|---|",
        ]
        zeilen += [f"| {seite} | {anzahl} |" for seite, anzahl in sorted(geschwaerzt.items())]

    pfad.parent.mkdir(parents=True, exist_ok=True)
    with pfad.open("w", encoding="utf-8", newline="\n") as datei:
        datei.write("\n".join(zeilen) + "\n")


def erzeuge_quellen(
    jahr: int,
    *,
    daten_wurzel: Path = DATEN_WURZEL,
    app_daten_wurzel: Path = APP_DATEN_WURZEL,
    bild_wurzel: Path = BELEGBILDER_WURZEL,
    rendern: bool = True,
    neu_rendern: bool = False,
) -> QuellenErgebnis:
    """Erzeugt `quellen.json`, den Bericht und (mit `rendern`) die fehlenden WebP-Seiten.

    Liest die App-JSONs aus `app_daten_wurzel` (Schritt 07 muss vorher gelaufen sein) und die
    CSVs aus `daten_wurzel`. Belege gibt es für jeden Wert mit Seitenfeld in den App-JSONs
    (Zeilenrechteck, sonst `bbox: null` mit Grund im Bericht) und je Seite einen `seite:{n}`.
    Jede referenzierte Seite wird gerendert, Produktinformationen-Seiten mit geschwärzten
    Personenfeldern; der Bericht `pruefberichte/quellenbelege.md` trägt auch die
    Datenschutz-Prüfliste.
    """
    jahrgang = lade_jahrgang(jahr)
    haushalt = _lies_app_json(app_daten_wurzel, HAUSHALT_JSON)
    investitionen = _lies_app_json(app_daten_wurzel, INVESTITIONEN_JSON)
    stellenplan = _lies_app_json(app_daten_wurzel, STELLENPLAN_JSON)
    produkte = _lies_app_json(app_daten_wurzel, PRODUKTE_APP_JSON)
    texte = _lies_app_json(app_daten_wurzel, TEXTE_JSON)
    seiten_df = lies_seiten_csv(daten_wurzel / SEITEN_CSV)
    hierarchie_df = lies_hierarchie_csv(daten_wurzel / HIERARCHIE_CSV)
    pruefwoerter = layout_liste(jahrgang, "quellenbelege", "pruefwoerter")
    schwaerzen_nach = layout_liste(jahrgang, "quellenbelege", "schwaerzen_nach")

    with PdfDokument.oeffne(jahrgang.pdf_pfad) as pdf:
        zugriff = _Seiten(pdf, jahrgang)
        personen = personenfeld_rechtecke(pdf, jahrgang, seiten_df, hierarchie_df)
        schwaerzung = _Schwaerzung(zugriff, personen, schwaerzen_nach)
        sammler = _Sammler(zugriff, schwaerzung)
        _sammle_plaene(sammler, jahrgang, daten_wurzel, haushalt)
        _sammle_vorbericht(sammler, jahrgang, daten_wurzel, haushalt)
        _sammle_meta(sammler, haushalt)
        _sammle_schuldenstand(sammler, jahrgang, daten_wurzel, haushalt, investitionen)
        _sammle_investitionen(sammler, jahrgang, haushalt, investitionen)
        _sammle_stellenplan(sammler, jahrgang, stellenplan)
        _sammle_produkte(sammler, jahrgang, produkte)
        _sammle_seiten(sammler, jahrgang, [haushalt, produkte, investitionen, stellenplan, texte])
        masse = zugriff.alle_masse
        pruefliste = [
            (seite, wort, index)
            for seite in masse
            for wort, index in finde_pruefwoerter(zugriff.zeilen(seite), pruefwoerter)
        ]
        schwaerzungen = {
            seite: len(rechtecke) for seite in masse if (rechtecke := schwaerzung.fuer(seite))
        }

    belege = sammler.belege
    seiten_sortiert = tuple(masse)
    neu_gerendert = 0
    if rendern:
        seitentypen = {
            int(zeile["pdf_seite"]): str(zeile["typ"]) for zeile in seiten_df.iter_rows(named=True)
        }
        # Fortsetzungsseiten der Produktinformationen (z. B. die zweite Seite von 010901) zeigen
        # kein Personenfeld; personenfeld_rechtecke hat geprüft, dass die erste Seite jedes
        # Produkts beide Felder trägt.
        ohne_personenfelder = [
            seite
            for seite in seiten_sortiert
            if seitentypen.get(seite) == _SEITENTYP_PRODUKTINFORMATIONEN
            and seite not in schwaerzungen
        ]
        neu_gerendert = len(
            rendere_seiten(
                jahrgang.pdf_pfad,
                seiten_sortiert,
                bild_wurzel,
                seitentypen=seitentypen,
                neu=neu_rendern,
                schwaerzungen={seite: schwaerzung.fuer(seite) for seite in schwaerzungen},
                ohne_personenfelder=ohne_personenfelder,
            )
        )

    daten = {
        "haushaltsjahr": jahrgang.haushaltsjahr,
        "seiten": {
            str(seite): {
                "bild": bild_name(seite),
                "breite": masse[seite][0],
                "hoehe": masse[seite][1],
            }
            for seite in seiten_sortiert
        },
        "belege": {schluessel: belege[schluessel] for schluessel in sorted(belege)},
    }
    pfad = app_daten_wurzel / QUELLEN_JSON
    schreibe_app_json(daten, pfad, praefix="quellen")

    bericht = daten_wurzel / QUELLENBELEGE_MD
    schreibe_quellenbericht(
        belege, sammler.ohne_bbox, bericht, pruefliste=pruefliste, schwaerzungen=schwaerzungen
    )

    return QuellenErgebnis(
        pfad=pfad,
        anzahl_belege=len(belege),
        anzahl_ohne_bbox=len(sammler.ohne_bbox),
        seiten=seiten_sortiert,
        neu_gerendert=neu_gerendert,
        ohne_bbox=dict(sorted(sammler.ohne_bbox.items())),
        bericht=bericht,
    )
