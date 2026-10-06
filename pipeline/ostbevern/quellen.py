"""Schritt 08: Quellenbelege (Phase 7, DATA-04, Spez. 4.4 und 5.6).

Findet für gedruckte Werte die Zeile auf der PDF-Seite (Rechteck `bbox`), rendert die
referenzierten Seiten als WebP (`belegbilder`) und schreibt `app/src/data/quellen.json`.

Schlüsselgrammatik (identisch in `app/src/lib/quelle.ts`; dieser Plan baut `ep` und `fp`,
die übrigen Arten folgen mit den Konsumentenplänen):

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
Ein Rechteck wird nie geraten: Ohne eindeutigen Treffer (Zeilennummer und Betrag) ist `bbox`
`null`.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

import polars as pl

from ostbevern.app_daten import APP_DATEN_WURZEL, schreibe_app_json
from ostbevern.belegbilder import bild_name, rendere_seiten
from ostbevern.konfiguration import PROJEKT_WURZEL, Jahrgang, lade_jahrgang
from ostbevern.pdf import PdfDokument, RahmenZeile, WortRahmen
from ostbevern.schema import (
    DATEN_WURZEL,
    ERGEBNISPLAN_CSV,
    FINANZPLAN_CSV,
    SEITEN_CSV,
    lies_plan_csv,
    lies_seiten_csv,
    zerlege_spaltenkopf,
)
from ostbevern.zahlen import ZahlenFehler, lies_betrag

BELEGBILDER_WURZEL = PROJEKT_WURZEL / "app" / "public" / "quellen"
QUELLEN_JSON = Path("quellen.json")

GRUND_NICHT_GEFUNDEN = "nicht_gefunden"
GRUND_MEHRDEUTIG = "mehrdeutig"
GRUND_BETRAG_FEHLT = "betrag_fehlt"

# Ebene des Gesamtplans in den Plan-CSVs; zugleich der Knotencode in den Schlüsseln.
_GESAMT = "GESAMT"
# Wertart, die nur eine Verpflichtungsermächtigungs-Spalte beschreibt (nie das Haushaltsjahr).
_WERTART_VE = "ve"


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


def schluessel_ep(code: str, zeile: str) -> str:
    """Belegschlüssel einer Ergebnisplanzeile: `ep:{code}:{zeile}`."""
    return f"ep:{code}:{zeile}"


def schluessel_fp(code: str, zeile: str) -> str:
    """Belegschlüssel einer Finanzplanzeile: `fp:{code}:{zeile}`."""
    return f"fp:{code}:{zeile}"


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


def finde_planzeile(
    zeilen: Sequence[RahmenZeile],
    nummer: str,
    betrag: int,
    *,
    breite: float,
    hoehe: float,
) -> tuple[list[float] | None, str | None]:
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
    praefix: str
    zeile: str
    zeile_kanonisch: str
    betrag: int
    pdf_seite: int


def _lies_gesamt_zeilen(
    daten_wurzel: Path, jahrgang: Jahrgang, csv: Path, plantyp: str, praefix: str
) -> list[_Planzeile]:
    """Liest die GESAMT-Zeilen einer Plan-CSV für die Haushaltsjahr-Spalte, je Zeile genau eine."""
    wertart = _haushaltsjahr_wertart(jahrgang, plantyp)
    df = lies_plan_csv(daten_wurzel / csv).filter(pl.col("ebene") == _GESAMT)
    haushaltsjahr = df.filter(
        (pl.col("jahr") == jahrgang.haushaltsjahr) & (pl.col("wertart") == wertart)
    ).sort("zeile")
    kanonisch = df["zeile_kanonisch"].unique().to_list()
    if haushaltsjahr.height != len(kanonisch) or haushaltsjahr["zeile_kanonisch"].n_unique() != (
        haushaltsjahr.height
    ):
        raise QuellenFehler(
            f"{csv}: {haushaltsjahr.height} Haushaltsjahr-Zeilen für {len(kanonisch)} "
            "GESAMT-Zeilen (je Zeile wird genau ein Wert erwartet)"
        )
    return [
        _Planzeile(
            praefix=praefix,
            zeile=zeile["zeile"],
            zeile_kanonisch=zeile["zeile_kanonisch"],
            betrag=zeile["betrag"],
            pdf_seite=zeile["pdf_seite"],
        )
        for zeile in haushaltsjahr.iter_rows(named=True)
    ]


def erzeuge_quellen(
    jahr: int,
    *,
    daten_wurzel: Path = DATEN_WURZEL,
    app_daten_wurzel: Path = APP_DATEN_WURZEL,
    bild_wurzel: Path = BELEGBILDER_WURZEL,
    rendern: bool = True,
    neu_rendern: bool = False,
) -> QuellenErgebnis:
    """Erzeugt `quellen.json` (und, mit `rendern`, die fehlenden WebP-Seiten) für `jahr`.

    Zeilen des Gesamtergebnisplans (`ep:GESAMT:*`) und des Gesamtfinanzplans (`fp:GESAMT:*`)
    werden auf ihrer `pdf_seite` gesucht (Zeilennummer plus Haushaltsjahrbetrag). Ein Wert
    ohne eindeutigen Treffer bekommt `bbox: null` und steht in `QuellenErgebnis.ohne_bbox`.
    """
    jahrgang = lade_jahrgang(jahr)
    planzeilen = _lies_gesamt_zeilen(
        daten_wurzel, jahrgang, ERGEBNISPLAN_CSV, "ergebnisplan", "ep"
    ) + _lies_gesamt_zeilen(daten_wurzel, jahrgang, FINANZPLAN_CSV, "finanzplan", "fp")

    belege: dict[str, dict[str, object]] = {}
    masse: dict[int, tuple[float, float]] = {}
    ohne_bbox: dict[str, str] = {}

    with PdfDokument.oeffne(jahrgang.pdf_pfad) as pdf:
        for planzeile in planzeilen:
            schluessel = (
                schluessel_ep(_GESAMT, planzeile.zeile_kanonisch)
                if planzeile.praefix == "ep"
                else schluessel_fp(_GESAMT, planzeile.zeile_kanonisch)
            )
            if schluessel in belege:
                raise QuellenFehler(f"Beleg {schluessel} doppelt vergeben")
            seite = planzeile.pdf_seite
            if seite not in masse:
                masse[seite] = pdf.seitenmass(seite)
            breite, hoehe = masse[seite]
            bbox, grund = finde_planzeile(
                pdf.zeilen_mit_rahmen(seite),
                planzeile.zeile,
                planzeile.betrag,
                breite=breite,
                hoehe=hoehe,
            )
            if bbox is None and grund is not None:
                ohne_bbox[schluessel] = grund
            belege[schluessel] = {"pdf_seite": seite, "bild": bild_name(seite), "bbox": bbox}

    seiten_sortiert = tuple(sorted(masse))
    neu_gerendert = 0
    if rendern:
        seitentypen = {
            int(zeile["pdf_seite"]): str(zeile["typ"])
            for zeile in lies_seiten_csv(daten_wurzel / SEITEN_CSV).iter_rows(named=True)
        }
        neu_gerendert = len(
            rendere_seiten(
                jahrgang.pdf_pfad,
                seiten_sortiert,
                bild_wurzel,
                seitentypen=seitentypen,
                neu=neu_rendern,
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

    return QuellenErgebnis(
        pfad=pfad,
        anzahl_belege=len(belege),
        anzahl_ohne_bbox=len(ohne_bbox),
        seiten=seiten_sortiert,
        neu_gerendert=neu_gerendert,
        ohne_bbox=dict(sorted(ohne_bbox.items())),
    )
