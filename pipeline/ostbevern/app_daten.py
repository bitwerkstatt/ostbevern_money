"""Schritt 07: deterministische App-JSON-Erzeugung (D-21, D-24).

Liest ausschließlich bereits generierte Dateien unter `daten/` (CSVs), nie das
Haushalts-PDF (D-06) — die Weitergabe an die App ist eine reine Datentransformation.
Schreibt `app/src/data/haushalt.json` atomar und deterministisch (fester
Schlüsselreihenfolge, UTF-8 ohne BOM, LF, abschließendem Zeilenumbruch), nach demselben
Muster wie `ostbevern.schema.schreibe_produkte_json` (Research Pattern 4).
"""

from __future__ import annotations

import json
import os
import tempfile
from collections.abc import Mapping, Sequence
from pathlib import Path

import polars as pl

from ostbevern.konfiguration import PROJEKT_WURZEL, lade_jahrgang, layout_text
from ostbevern.manuell import investitionskredite_ende, lies_meta_json, pro_kopf_euro
from ostbevern.pruefung import (
    REGEL5_GEP_ZEILEN,
    REGEL5_TOLERANZ_GEP_EURO,
    WEITERGABE_POSTEN,
    Planwerte,
    zerlege_weitere_vorberichtstabellen,
)
from ostbevern.schema import (
    DATEN_WURZEL,
    EIGENKAPITAL_CSV,
    ERGEBNISPLAN_CSV,
    ERKLAERUNGEN_MD,
    FINANZPLAN_CSV,
    GRUNDZAHLEN_CSV,
    HIERARCHIE_CSV,
    INVESTITIONEN_CSV,
    INVESTITIONSZUWENDUNGEN_CSV,
    KITA_ZUSCHUESSE_CSV,
    META_JSON,
    PRODUKT_SCHLUESSEL,
    PRODUKTE_JSON,
    STELLENPLAN_CSV,
    STEUERARTEN_CSV,
    TRANSFERAUFWENDUNGEN_CSV,
    VE_FAELLIGKEITEN_CSV,
    VERBINDLICHKEITEN_CSV,
    WEITERE_VORBERICHTSTABELLEN_CSV,
    ZUWENDUNGEN_CSV,
    lies_eigenkapital_csv,
    lies_grundzahlen_csv,
    lies_hierarchie_csv,
    lies_investitionen_csv,
    lies_plan_csv,
    lies_produkte_json,
    lies_stellenplan_csv,
    lies_ve_faelligkeiten_csv,
    lies_vorbericht_csv,
    zerlege_spaltenkopf,
)
from ostbevern.texte import lies_erklaerungen, loese_auf, pruefe_text, textwerte
from ostbevern.zeilen import ZEILEN


class AppDatenFehler(ValueError):
    """Wird ausgelöst, wenn die Eingabedaten für die App-JSON-Erzeugung inkonsistent sind."""


APP_DATEN_WURZEL = PROJEKT_WURZEL / "app" / "src" / "data"
HAUSHALT_JSON = Path("haushalt.json")
STELLENPLAN_JSON = Path("stellenplan.json")
TEXTE_JSON = Path("texte.json")

# Knoten-/Zeilenkonstanten der KL-Herauslösung (D-01 bis D-04, Spez. 3.4). Fachliche
# Regel, kein Jahrgangswert -- nur der Produktcode selbst kommt aus
# [layout.weitergabe_kreis_land] (jahrgangsabhängig).
GESAMT_CODE = "GESAMT"
GESAMT_NAME = "Gesamthaushalt"
KL_CODE = "KL"
KL_NAME = "Weitergabe an Kreis und Land"
# Schlüssel müssen exakt pruefung.WEITERGABE_POSTEN entsprechen (Reihenfolge = App-
# Kinderreihenfolge); geprüft zur Laufzeit in baue_knoten (AppDatenFehler sonst).
KL_POSTEN_NAMEN: dict[str, str] = {
    "kreisumlage": "Kreisumlage",
    "gewerbesteuerumlage": "Gewerbesteuerumlage",
    "krankenhausinvestitionsumlage": "Krankenhausinvestitionsumlage",
}

# Vorbericht-Tabellen mit einem berechneten Posten "Sonstige" (Spez. 3.8): dort, wo die
# gedruckte Gesamtzeile um mehr als REGEL5_TOLERANZ_GEP_EURO von der GEP-Zeile abweicht,
# schließt "Sonstige" die Lücke, sodass Σ Posten exakt die (maßgebliche) GEP-Zeile ergibt.
TABELLEN_MIT_SONSTIGE: frozenset[str] = frozenset({"zuwendungen", "sonstige_ertraege"})

# App-Zeilenmenge des Ergebnisplans je Knoten (D-22, D-23): GEP-Zeilen 01-26 (gleiche
# kanonische Schlüssel in GEP und TP), dann der Minderaufwand und das Ergebnis danach
# (GEP 27/28, TP 30/31 -- Lookup über ZEILEN, nie hartkodierte Zeilennummern unten).
ERGEBNISPLAN_APP_ZEILEN: tuple[str, ...] = tuple(
    ZEILEN["gesamtergebnisplan"][f"{nummer:02d}"].kanonisch for nummer in range(1, 27)
) + (
    ZEILEN["gesamtergebnisplan"]["27"].kanonisch,
    ZEILEN["gesamtergebnisplan"]["28"].kanonisch,
)

# Die beiden Aufwand-Zeilen und die vier Ergebnis-Zeilen, die die KL-Herauslösung
# verschiebt (D-01 bis D-04): Δ wird von den Aufwand-Zeilen abgezogen und auf die
# Ergebnis-Zeilen addiert (Produkt/PG/PB-Kette), bzw. umgekehrt auf KL/KL.<posten>.
_KL_AUFWAND_ZEILEN: tuple[str, ...] = ("transferaufwendungen", "ordentliche_aufwendungen")
_KL_ERGEBNIS_ZEILEN: tuple[str, ...] = (
    "ordentliches_ergebnis",
    "ergebnis_laufende_verwaltung",
    "jahresergebnis",
    "ergebnis_nach_minderaufwand",
)


def _pruefe_kl_posten_namen() -> None:
    if tuple(KL_POSTEN_NAMEN) != WEITERGABE_POSTEN:
        raise AppDatenFehler(
            "KL_POSTEN_NAMEN-Schlüssel weichen von pruefung.WEITERGABE_POSTEN ab: "
            f"{tuple(KL_POSTEN_NAMEN)!r} != {WEITERGABE_POSTEN!r}"
        )


def _pruefe_ergebnisplan_app_zeilen() -> None:
    """D-22: die Zeilen 01-26 müssen in GEP und TP denselben kanonischen Schlüssel
    tragen, sonst würde `baue_ergebnisplan` beim Nachschlagen in ZEILEN["teilergebnisplan"]
    eine falsche Zeile treffen."""
    for nummer in range(1, 27):
        zeile = f"{nummer:02d}"
        gep_kanonisch = ZEILEN["gesamtergebnisplan"][zeile].kanonisch
        tp_kanonisch = ZEILEN["teilergebnisplan"][zeile].kanonisch
        if gep_kanonisch != tp_kanonisch:
            raise AppDatenFehler(
                f"Zeile {zeile}: GEP-Schlüssel {gep_kanonisch!r} != TP-Schlüssel {tp_kanonisch!r}"
            )


def _zeile_fuer_kanonisch(plantyp: str) -> dict[str, str]:
    """Kehrt ZEILEN[plantyp] um: kanonischer Schlüssel -> Zeilennummer."""
    return {definition.kanonisch: zeile for zeile, definition in ZEILEN[plantyp].items()}


def baue_knoten(
    hierarchie: pl.DataFrame,
    *,
    ergebnisplan: pl.DataFrame,
    transfer_df: pl.DataFrame,
    produkt: str,
    gep_pdf_seite: int,
) -> list[dict[str, object]]:
    """Baut die Knotenliste von `haushalt.json` (D-03, D-21): GESAMT, dann jede
    hierarchie.csv-Zeile in Dateireihenfolge, dann der synthetische KL-Knoten und seine
    drei Unterposten-Kinder (D-02). Mutiert `hierarchie` nie; die Herauslösung lebt
    ausschließlich in dieser Funktion und in `baue_ergebnisplan` (nie in
    `daten/aufbereitet/hierarchie.csv`)."""
    _pruefe_kl_posten_namen()

    tp_zeile = ergebnisplan.filter(
        (pl.col("ebene") == "P") & (pl.col("code") == produkt) & (pl.col("zeile") == "15")
    )
    if tp_zeile.height == 0:
        raise AppDatenFehler(f"Teilergebnisplan von Produkt {produkt!r} hat keine Zeile 15")
    kl_pdf_seite = tp_zeile["pdf_seite"][0]

    knoten: list[dict[str, object]] = [
        {
            "code": GESAMT_CODE,
            "ebene": "GESAMT",
            "name": GESAMT_NAME,
            "eltern": None,
            "synthetisch": False,
            "gerundet": False,
            "pdf_seite": gep_pdf_seite,
        }
    ]
    for zeile in hierarchie.iter_rows(named=True):
        eltern = zeile["eltern_code"]
        if eltern is None and zeile["ebene"] == "PB":
            eltern = GESAMT_CODE
        knoten.append(
            {
                "code": zeile["code"],
                "ebene": zeile["ebene"],
                "name": zeile["name"],
                "eltern": eltern,
                "synthetisch": zeile["synthetisch"],
                "gerundet": False,
                "pdf_seite": zeile["pdf_seite_start"],
            }
        )

    knoten.append(
        {
            "code": KL_CODE,
            "ebene": "PB",
            "name": KL_NAME,
            "eltern": GESAMT_CODE,
            "synthetisch": True,
            "gerundet": False,
            "pdf_seite": kl_pdf_seite,
        }
    )
    for posten in WEITERGABE_POSTEN:
        posten_df = transfer_df.filter(pl.col("posten") == posten)
        if posten_df.height == 0:
            raise AppDatenFehler(f"Weitergabe-Posten {posten!r} fehlt in transferaufwendungen.csv")
        knoten.append(
            {
                "code": f"{KL_CODE}.{posten}",
                "ebene": "PG",
                "name": KL_POSTEN_NAMEN[posten],
                "eltern": KL_CODE,
                "synthetisch": True,
                "gerundet": True,
                "pdf_seite": posten_df["quelle"][0],
            }
        )
    return knoten


def baue_ergebnisplan(
    knoten: list[dict[str, object]],
    *,
    ergebnisplan: pl.DataFrame,
    transfer_df: pl.DataFrame,
    hierarchie: pl.DataFrame,
    produkt: str,
    jahre: list[int],
    wertarten: list[str],
) -> dict[str, dict[str, object]]:
    """Baut `ergebnisplan` von `haushalt.json` (D-01 bis D-04, D-22, D-23): je Knoten
    die Ergebnisplan-Zeilen (`ERGEBNISPLAN_APP_ZEILEN`) nach der KL-Herauslösung, plus
    die daraus abgeleiteten `berechnet`-Werte (Aufwand, Erträge, Zuschussbedarf,
    Überschuss). Die Herauslösung arbeitet ausschließlich auf In-Memory-DataFrames/
    Listen; `daten/aufbereitet/ergebnisplan.csv` bleibt unverändert."""
    _pruefe_ergebnisplan_app_zeilen()
    planwerte = Planwerte(ergebnisplan, datei="ergebnisplan")

    eltern_je_code = {
        zeile["code"]: zeile["eltern_code"] for zeile in hierarchie.iter_rows(named=True)
    }
    kette: list[str] = []
    code = produkt
    while True:
        kette.append(code)
        eltern = eltern_je_code.get(code)
        if eltern is None:
            break
        code = eltern
    if len(kette) != 3:
        raise AppDatenFehler(
            f"Weitergabe-Produkt {produkt!r}: unerwartete Hierarchietiefe {kette!r}"
        )
    kette_menge = set(kette)

    delta = [
        planwerte.wert("P", produkt, "15", jahr, wertart)
        for jahr, wertart in zip(jahre, wertarten, strict=True)
    ]

    posten_delta: dict[str, list[int]] = {}
    for posten in WEITERGABE_POSTEN:
        posten_df = transfer_df.filter(pl.col("posten") == posten)
        nach_jahr = {
            zeile["jahr"]: zeile["betrag_teur"] for zeile in posten_df.iter_rows(named=True)
        }
        posten_delta[posten] = [nach_jahr[jahr] * 1000 for jahr in jahre]

    reverse_gesamt = _zeile_fuer_kanonisch("gesamtergebnisplan")
    reverse_teil = _zeile_fuer_kanonisch("teilergebnisplan")

    ergebnisplan_app: dict[str, dict[str, object]] = {}
    for eintrag in knoten:
        code_wert = str(eintrag["code"])
        ebene = str(eintrag["ebene"])
        plantyp_code = "" if ebene == "GESAMT" else code_wert
        reverse = reverse_gesamt if ebene == "GESAMT" else reverse_teil

        zeilen_werte: dict[str, list[int]] = {
            kanonisch: [
                planwerte.wert(ebene, plantyp_code, reverse[kanonisch], jahr, wertart)
                for jahr, wertart in zip(jahre, wertarten, strict=True)
            ]
            for kanonisch in ERGEBNISPLAN_APP_ZEILEN
        }

        if code_wert in kette_menge:
            for index in range(len(jahre)):
                for zeile_kanonisch in _KL_AUFWAND_ZEILEN:
                    zeilen_werte[zeile_kanonisch][index] -= delta[index]
                for zeile_kanonisch in _KL_ERGEBNIS_ZEILEN:
                    zeilen_werte[zeile_kanonisch][index] += delta[index]
        elif code_wert == KL_CODE:
            for index in range(len(jahre)):
                for zeile_kanonisch in _KL_AUFWAND_ZEILEN:
                    zeilen_werte[zeile_kanonisch][index] += delta[index]
                for zeile_kanonisch in _KL_ERGEBNIS_ZEILEN:
                    zeilen_werte[zeile_kanonisch][index] -= delta[index]
        elif code_wert.startswith(f"{KL_CODE}."):
            posten = code_wert.removeprefix(f"{KL_CODE}.")
            werte_posten = posten_delta[posten]
            for index in range(len(jahre)):
                for zeile_kanonisch in _KL_AUFWAND_ZEILEN:
                    zeilen_werte[zeile_kanonisch][index] += werte_posten[index]
                for zeile_kanonisch in _KL_ERGEBNIS_ZEILEN:
                    zeilen_werte[zeile_kanonisch][index] -= werte_posten[index]

        aufwand = [
            zeilen_werte["ordentliche_aufwendungen"][i] + zeilen_werte["zinsaufwendungen"][i]
            for i in range(len(jahre))
        ]
        ertraege = [
            zeilen_werte["ordentliche_ertraege"][i] + zeilen_werte["finanzertraege"][i]
            for i in range(len(jahre))
        ]
        zuschussbedarf = [aufwand[i] - ertraege[i] for i in range(len(jahre))]
        ueberschuss = [wert < 0 for wert in zuschussbedarf]

        ergebnisplan_app[code_wert] = {
            "zeilen": zeilen_werte,
            "berechnet": {
                "aufwand": aufwand,
                "ertraege": ertraege,
                "zuschussbedarf": zuschussbedarf,
                "ueberschuss": ueberschuss,
            },
        }
    return ergebnisplan_app


def baue_finanzplan(
    finanzplan: pl.DataFrame,
    *,
    jahre: list[int],
    wertarten: list[str],
    haushaltsjahr: int,
) -> dict[str, dict[str, object]]:
    """Baut `finanzplan` von `haushalt.json` (D-22): nur die GESAMT-Ebene, alle
    Gesamtfinanzplan-Zeilen 01-41 (`zeilen`, entlang `jahre`) sowie die VE-Werte zum
    Haushaltsjahr (`ve`, ein int je Zeile mit gedruckter VE-Zeile -- nicht entlang
    `jahre`, VE wird nur für das Haushaltsjahr geführt)."""
    planwerte = Planwerte(finanzplan, datei="finanzplan")

    zeilen_werte: dict[str, list[int]] = {
        kanonisch: [
            planwerte.wert("GESAMT", "", zeile, jahr, wertart)
            for jahr, wertart in zip(jahre, wertarten, strict=True)
        ]
        for kanonisch, zeile in ((d.kanonisch, z) for z, d in ZEILEN["gesamtfinanzplan"].items())
    }

    # `.unique()` auf einer polars-Series ist hash-basiert und NICHT reihenfolgestabil
    # (verifiziert: wiederholte Läufe lieferten unterschiedliche Reihenfolgen) — würde
    # D-24 (deterministisches JSON) verletzen. Deshalb nur als Mengentest verwendet; die
    # Ausgabereihenfolge kommt aus der festen Einfügereihenfolge von ZEILEN (D-21).
    ve_zeilen_menge = set(
        finanzplan.filter((pl.col("ebene") == "GESAMT") & (pl.col("wertart") == "ve"))[
            "zeile"
        ].to_list()
    )
    ve_werte: dict[str, int] = {
        definition.kanonisch: planwerte.wert("GESAMT", "", zeile, haushaltsjahr, "ve")
        for zeile, definition in ZEILEN["gesamtfinanzplan"].items()
        if zeile in ve_zeilen_menge
    }

    return {"GESAMT": {"zeilen": zeilen_werte, "ve": ve_werte}}


def baue_zeilen_namen(finanzplan_zeilen: Sequence[str]) -> dict[str, list[dict[str, object]]]:
    """Baut `zeilen_namen` von `haushalt.json` (Phase 5, RESEARCH Pitfall 9): der gedruckte
    Zeilenname, die Zeilennummer und das Summenflag je Ergebnisplan-Zeile
    (`ERGEBNISPLAN_APP_ZEILEN`, Reihenfolge wie dort) und je Zeile von `finanzplan_zeilen`
    (die Schlüssel von `finanzplan.GESAMT.zeilen`, Reihenfolge wie dort). Liest nur `ZEILEN`
    -- die App führt keine zweite Namenstabelle. Ein Schlüssel ohne Eintrag in `ZEILEN`
    bricht mit `AppDatenFehler` ab."""

    def _eintraege(plantyp: str, schluessel: Sequence[str]) -> list[dict[str, object]]:
        nummer_je_schluessel = _zeile_fuer_kanonisch(plantyp)
        eintraege: list[dict[str, object]] = []
        for kanonisch in schluessel:
            nummer = nummer_je_schluessel.get(kanonisch)
            if nummer is None:
                raise AppDatenFehler(
                    f"zeilen_namen: {plantyp} kennt den Schlüssel {kanonisch!r} nicht"
                )
            definition = ZEILEN[plantyp][nummer]
            eintraege.append(
                {
                    "schluessel": kanonisch,
                    "nummer": nummer,
                    "name": definition.name,
                    "ist_summe": definition.ist_summe,
                }
            )
        return eintraege

    return {
        "ergebnisplan": _eintraege("gesamtergebnisplan", ERGEBNISPLAN_APP_ZEILEN),
        "finanzplan": _eintraege("gesamtfinanzplan", finanzplan_zeilen),
    }


# produkte.json / investitionen.json (D-13, D-14, D-21, Plan 04-04 Task 2).
PRODUKTE_APP_JSON = Path("produkte.json")
APP_PRODUKT_SCHLUESSEL: tuple[str, ...] = PRODUKT_SCHLUESSEL + ("grundzahlen",)
INVESTITIONEN_JSON = Path("investitionen.json")

# Schuldenstand-Formel (D-14), identisch für jedes Jahr -- Rohtext statt Formatierung
# (D-15 verbietet Formatierung in der Pipeline).
_SCHULDENSTAND_FORMEL = (
    "Investitionskredite Ende Jahr = Vorjahr + Kreditaufnahme (GFP Z. 33) − Tilgung "
    "(GFP Z. 35); NRW.Bank-Anteil konstant auf dem zuletzt gedruckten Stand; "
    "Pro-Kopf abgerundet."
)


def _eltern_kette(eltern_je_code: Mapping[str, str | None], code: str) -> list[str]:
    """Liefert [code, eltern, elternseltern, ...] bis zum Wurzelknoten (eltern None)."""
    kette = [code]
    aktuell = code
    while True:
        eltern = eltern_je_code.get(aktuell)
        if eltern is None:
            break
        kette.append(eltern)
        aktuell = eltern
    return kette


def baue_produkte_json(
    produkte: list[dict[str, object]], grundzahlen: pl.DataFrame
) -> list[dict[str, object]]:
    """Baut `produkte.json` der App (D-13, D-21): jedes Produkt aus
    `daten/aufbereitet/produkte.json` (bereits namensfrei, Phase 3 D-09) plus seine
    Grundzahlen, gruppiert nach `position`. Ein Produkt ohne exakt
    `APP_PRODUKT_SCHLUESSEL`-Schlüsselmenge bricht mit `AppDatenFehler` ab (Allowlist
    wie `schema.schreibe_produkte_json`)."""
    schluessel_menge = set(APP_PRODUKT_SCHLUESSEL)
    ergebnis: list[dict[str, object]] = []
    for produkt in sorted(produkte, key=lambda p: p["code"]):
        code = produkt["code"]
        eigene = grundzahlen.filter(pl.col("produkt") == code)
        positionen = sorted(eigene["position"].unique().to_list())
        grundzahlen_liste: list[dict[str, object]] = []
        for position in positionen:
            teil = eigene.filter(pl.col("position") == position)
            erste = teil.row(0, named=True)
            werte = [
                {
                    "jahr": zeile["jahr"],
                    "wert": (
                        int(zeile["wert"])
                        if zeile["nachkommastellen"] == 0
                        else round(zeile["wert"], zeile["nachkommastellen"])
                    ),
                    "hinweis": zeile["hinweis"],
                }
                for zeile in teil.sort("jahr").iter_rows(named=True)
            ]
            grundzahlen_liste.append(
                {
                    "position": position,
                    "gruppe": erste["gruppe"],
                    "bezeichnung": erste["bezeichnung"],
                    "einheit": erste["einheit"],
                    "nachkommastellen": erste["nachkommastellen"],
                    "pdf_seite": erste["pdf_seite"],
                    "werte": werte,
                }
            )

        eintrag = {**produkt, "grundzahlen": grundzahlen_liste}
        vorhandene = set(eintrag)
        if vorhandene != schluessel_menge:
            raise AppDatenFehler(
                f"produkte.json: Produkt {code!r} hat abweichende Schlüssel "
                f"(fehlend: {sorted(schluessel_menge - vorhandene)}, "
                f"unerwartet: {sorted(vorhandene - schluessel_menge)})"
            )
        ergebnis.append({schluessel: eintrag[schluessel] for schluessel in APP_PRODUKT_SCHLUESSEL})
    return ergebnis


def _baue_massnahmen(
    investitionen: pl.DataFrame,
    *,
    hierarchie: pl.DataFrame,
    jahre: list[int],
) -> list[dict[str, object]]:
    eltern_je_code = {
        zeile["code"]: zeile["eltern_code"] for zeile in hierarchie.iter_rows(named=True)
    }
    pb_je_produkt: dict[str, str] = {}

    gruppen = sorted(
        investitionen.select("produkt", "massnahme_id", "konto").unique().iter_rows(named=True),
        key=lambda z: (z["produkt"], z["massnahme_id"], z["konto"]),
    )
    massnahmen: list[dict[str, object]] = []
    for schluessel in gruppen:
        produkt = schluessel["produkt"]
        massnahme_id = schluessel["massnahme_id"]
        konto = schluessel["konto"]
        teil = investitionen.filter(
            (pl.col("produkt") == produkt)
            & (pl.col("massnahme_id") == massnahme_id)
            & (pl.col("konto") == konto)
        )
        erste = teil.row(0, named=True)
        if produkt not in pb_je_produkt:
            pb_je_produkt[produkt] = _eltern_kette(eltern_je_code, produkt)[-1]

        werte_df = teil.filter(pl.col("wertart") != "ve")
        werte_nach_jahr = {
            zeile["jahr"]: zeile["betrag"] for zeile in werte_df.iter_rows(named=True)
        }
        werte = [werte_nach_jahr.get(jahr) for jahr in jahre]

        ve_zeile = teil.filter(pl.col("wertart") == "ve")
        ve_betrag = ve_zeile["betrag"][0] if ve_zeile.height > 0 else None

        massnahmen.append(
            {
                "produkt": produkt,
                "pb": pb_je_produkt[produkt],
                "massnahme_id": massnahme_id,
                "massnahme_name": erste["massnahme_name"],
                "konto": konto,
                "konto_name": erste["konto_name"],
                "richtung": erste["richtung"],
                "art": erste["art"],
                "werte": werte,
                "ve": ve_betrag,
                "pdf_seite": int(teil["pdf_seite"].min()),
            }
        )
    return massnahmen


def baue_investitionen_json(
    *,
    investitionen: pl.DataFrame,
    ve_faelligkeiten: pl.DataFrame,
    hierarchie: pl.DataFrame,
    verbindlichkeiten: pl.DataFrame,
    finanzplan: pl.DataFrame,
    meta: Mapping[str, object],
    haushaltsjahr: int,
    jahre: list[int],
    wertarten: list[str],
) -> dict[str, object]:
    """Baut `investitionen.json` der App (D-13, D-14, D-21): Maßnahmen (gruppiert nach
    Produkt/Maßnahme/Konto), VE-Fälligkeiten, Finanzierung (GFP), Schuldenstand
    (fortgeschrieben ab dem letzten gedruckten Stand, D-14) und Bürgschaften."""
    massnahmen = _baue_massnahmen(investitionen, hierarchie=hierarchie, jahre=jahre)

    ve_faelligkeiten_liste = [
        {
            "produkt": zeile["produkt"],
            "massnahme_id": zeile["massnahme_id"],
            "konto": zeile["konto"],
            "jahr": zeile["jahr"],
            "betrag": zeile["betrag"],
            "pdf_seite": zeile["pdf_seite"],
        }
        for zeile in ve_faelligkeiten.sort(["produkt", "massnahme_id", "konto", "jahr"]).iter_rows(
            named=True
        )
    ]

    planwerte_finanzplan = Planwerte(finanzplan, datei="finanzplan")
    gfp_pdf_seite = int(finanzplan.filter(pl.col("ebene") == "GESAMT")["pdf_seite"][0])
    finanzierung_zeile_je_kanonisch = {
        "einzahlungen_investitionen": "23",
        "auszahlungen_investitionen": "30",
        "kreditaufnahme": "33",
        "tilgung": "35",
    }
    finanzierung = {
        "quelle": gfp_pdf_seite,
        "zeilen": {
            kanonisch: [
                planwerte_finanzplan.wert("GESAMT", "", zeile, jahr, wertart)
                for jahr, wertart in zip(jahre, wertarten, strict=True)
            ]
            for kanonisch, zeile in finanzierung_zeile_je_kanonisch.items()
        },
    }

    verbindlichkeiten_df = verbindlichkeiten.filter(pl.col("tabelle") == "verbindlichkeiten")
    einwohner = meta["einwohner"]["wert"]
    quelle_310 = int(verbindlichkeiten_df["quelle"][0])

    def _posten_nach_jahr(posten: str) -> dict[int, int]:
        teil = verbindlichkeiten_df.filter(pl.col("posten") == posten)
        return {zeile["jahr"]: zeile["betrag_teur"] * 1000 for zeile in teil.iter_rows(named=True)}

    investitionskredite_gedruckt = _posten_nach_jahr("kredite_investitionen")
    nrw_bank_gedruckt = _posten_nach_jahr("transferleistungen")
    liquiditaetskredite_gedruckt = _posten_nach_jahr("liquiditaetskredite")

    letztes_gedrucktes_jahr = max(nrw_bank_gedruckt)
    nrw_bank_letzter_wert = nrw_bank_gedruckt[letztes_gedrucktes_jahr]

    investitionskredite: list[int] = []
    nrw_bank: list[int] = []
    liquiditaetskredite: list[int | None] = []
    berechnet: list[bool] = []
    for index, jahr in enumerate(jahre):
        if jahr in investitionskredite_gedruckt:
            investitionskredite.append(investitionskredite_gedruckt[jahr])
            nrw_bank.append(nrw_bank_gedruckt[jahr])
            berechnet.append(False)
        else:
            vorjahr_euro = investitionskredite[index - 1]
            investitionskredite.append(
                investitionskredite_ende(
                    vorjahr_euro,
                    finanzierung["zeilen"]["kreditaufnahme"][index],
                    finanzierung["zeilen"]["tilgung"][index],
                )
            )
            nrw_bank.append(nrw_bank_letzter_wert)
            berechnet.append(True)
        liquiditaetskredite.append(liquiditaetskredite_gedruckt.get(jahr))

    gesamt = [investitionskredite[i] + nrw_bank[i] for i in range(len(jahre))]
    pro_kopf = [pro_kopf_euro(wert, einwohner) for wert in gesamt]

    schuldenstand = {
        "quelle": quelle_310,
        "einwohner": einwohner,
        "investitionskredite": investitionskredite,
        "nrw_bank": nrw_bank,
        "liquiditaetskredite": liquiditaetskredite,
        "gesamt": gesamt,
        "pro_kopf": pro_kopf,
        "berechnet": berechnet,
        "formel": _SCHULDENSTAND_FORMEL,
    }

    buergschaften_df = verbindlichkeiten.filter(pl.col("tabelle") == "buergschaften")
    buergschaften: dict[str, object] = {}
    for posten in sorted(buergschaften_df["posten"].unique().to_list()):
        teil = buergschaften_df.filter(pl.col("posten") == posten)
        name = teil["posten_name"][0]
        nach_jahr = {
            zeile["jahr"]: zeile["betrag_teur"] * 1000 for zeile in teil.iter_rows(named=True)
        }
        buergschaften[posten] = {
            "name": name,
            "werte": [nach_jahr.get(jahr) for jahr in jahre],
        }

    return {
        "haushaltsjahr": haushaltsjahr,
        "jahre": jahre,
        "wertarten": wertarten,
        "massnahmen": massnahmen,
        "ve_faelligkeiten": ve_faelligkeiten_liste,
        "finanzierung": finanzierung,
        "schuldenstand": schuldenstand,
        "buergschaften": buergschaften,
    }


def schreibe_app_json(daten: Mapping[str, object], pfad: Path, *, praefix: str) -> None:
    """Schreibt `daten` atomar nach `pfad` (D-24): tempfile + os.replace, UTF-8 ohne BOM,
    LF, feste Schlüsselreihenfolge (Einfügereihenfolge der übergebenen dicts), mit
    abschließendem Zeilenumbruch — dasselbe Muster wie `schema.schreibe_produkte_json`."""
    inhalt = json.dumps(daten, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    pfad.parent.mkdir(parents=True, exist_ok=True)
    deskriptor, temp_pfad_str = tempfile.mkstemp(
        dir=pfad.parent, prefix=f".{praefix}-", suffix=".tmp"
    )
    temp_pfad = Path(temp_pfad_str)
    try:
        with os.fdopen(deskriptor, "w", encoding="utf-8", newline="\n") as datei:
            datei.write(inhalt)
        os.replace(temp_pfad, pfad)
    finally:
        temp_pfad.unlink(missing_ok=True)


def baue_vorbericht_tabelle(
    df: pl.DataFrame,
    *,
    jahre: list[int],
    planwerte: Planwerte,
    gep_zeile: str | None,
    sonstige: bool = False,
) -> dict[str, object]:
    """Baut die App-JSON-Struktur einer manuellen Vorberichtstabelle (D-02, D-21).

    `gesamt_plan` ist die eurogenaue GEP-Zeile (D-01), `gesamt_vorbericht` die gedruckte,
    nur in T€ geführte Gesamtzeile × 1000 (als `gerundet` gekennzeichnet). Jeder Posten
    trägt seine Werte × 1000, ebenfalls `gerundet: true`, `berechnet: false` (D-02, D-10).
    Eine Tabelle ohne `gep_zeile` (z. B. kita_zuschuesse) hat `planzeile`/`gesamt_plan`
    `null`; druckt sie nicht jedes Jahr aus `jahre` (MANU-04: nur das Haushaltsjahr), sind
    die fehlenden Jahre in `gesamt_vorbericht.werte` ebenfalls `null` — fehlt die
    Gesamtzeile für JEDES Jahr, bricht die Funktion mit `AppDatenFehler` ab.

    `sonstige=True` (zuwendungen und sonstige_ertraege, Spez. 3.8, Phase 5 D-04) hängt
    einen letzten, rein berechneten Posten "Sonstige" an: nicht-`null` genau in den
    Jahren, in denen die gedruckte Gesamtzeile um mehr als REGEL5_TOLERANZ_GEP_EURO von
    der GEP-Zeile abweicht, und dort so bemessen, dass Σ Posten + Sonstige exakt die
    GEP-Zeile ergibt (die Planzeile bleibt maßgeblich, D-07b).
    """
    tabelle = df["tabelle"][0]
    gesamt_df = df.filter(pl.col("ist_gesamt"))
    gesamt_nach_jahr = {zeile["jahr"]: zeile for zeile in gesamt_df.iter_rows(named=True)}
    if len(gesamt_nach_jahr) != gesamt_df.height:
        raise AppDatenFehler(f"{tabelle}: mehrere Gesamtzeilen für dasselbe Jahr")
    if not gesamt_nach_jahr:
        raise AppDatenFehler(f"{tabelle}: keine Gesamtzeile vorhanden")

    gesamt_werte: list[int | None] = []
    gesamt_quelle: int | None = None
    for jahr in jahre:
        zeile = gesamt_nach_jahr.get(jahr)
        if zeile is None:
            gesamt_werte.append(None)
            continue
        gesamt_werte.append(zeile["betrag_teur"] * 1000)
        gesamt_quelle = zeile["quelle"]

    if gep_zeile is not None:
        planzeile = ZEILEN["gesamtergebnisplan"][gep_zeile].kanonisch
        gesamt_plan: list[int | None] | None = [
            planwerte.wert("GESAMT", "", gep_zeile, jahr, gesamt_nach_jahr[jahr]["wertart"])
            if jahr in gesamt_nach_jahr
            else None
            for jahr in jahre
        ]
    else:
        planzeile = None
        gesamt_plan = None

    posten_df = df.filter(~pl.col("ist_gesamt"))
    positionen = sorted(posten_df["position"].unique().to_list())
    posten_liste: list[dict[str, object]] = []
    for position in positionen:
        teil = posten_df.filter(pl.col("position") == position)
        name = teil["posten_name"][0]
        posten_schluessel = teil["posten"][0]
        zeilen_nach_jahr = {zeile["jahr"]: zeile for zeile in teil.iter_rows(named=True)}
        if len(zeilen_nach_jahr) != teil.height:
            raise AppDatenFehler(
                f"{tabelle}: Posten {posten_schluessel!r} hat mehrere Zeilen für dasselbe Jahr"
            )

        werte: list[int | None] = []
        quelle: int | None = None
        anmerkung: str | None = None
        for jahr in jahre:
            zeile = zeilen_nach_jahr.get(jahr)
            if zeile is None:
                werte.append(None)
                continue
            werte.append(zeile["betrag_teur"] * 1000)
            quelle = zeile["quelle"]
            anmerkung = zeile["anmerkung"]

        posten_liste.append(
            {
                "posten": posten_schluessel,
                "name": name,
                "werte": werte,
                "gerundet": True,
                "berechnet": False,
                "quelle": quelle,
                "anmerkung": anmerkung,
            }
        )

    if sonstige:
        if gesamt_plan is None:
            raise AppDatenFehler(f"{tabelle}: sonstige=True verlangt eine GEP-Zeile")
        sonstige_werte: list[int | None] = []
        for index in range(len(jahre)):
            plan_wert = gesamt_plan[index]
            gesamt_wert = gesamt_werte[index]
            if plan_wert is None or gesamt_wert is None:
                sonstige_werte.append(None)
                continue
            if abs(plan_wert - gesamt_wert) <= REGEL5_TOLERANZ_GEP_EURO:
                sonstige_werte.append(None)
                continue
            posten_summe = sum(
                posten["werte"][index] or 0  # type: ignore[index]
                for posten in posten_liste
            )
            sonstige_werte.append(plan_wert - posten_summe)
        posten_liste.append(
            {
                "posten": "sonstige",
                "name": "Sonstige",
                "werte": sonstige_werte,
                "gerundet": False,
                "berechnet": True,
                "quelle": gesamt_quelle,
                "anmerkung": (
                    "Differenz zwischen der eurogenauen Planzeile des Gesamtergebnisplans "
                    "und der Summe der gedruckten Vorbericht-Posten (Spez. 3.8); die "
                    "Planzeile ist maßgeblich."
                ),
            }
        )

    return {
        "tabelle": tabelle,
        "quelle_einheit": "teur",
        "planzeile": planzeile,
        "gesamt_plan": gesamt_plan,
        "gesamt_vorbericht": {
            "werte": gesamt_werte,
            "gerundet": True,
            "quelle": gesamt_quelle,
        },
        "posten": posten_liste,
    }


def baue_eigenkapital_tabelle(df: pl.DataFrame, *, jahre: list[int]) -> dict[str, object]:
    """Baut die App-JSON-Struktur von `eigenkapital.csv` (D-11, D-21): wie eine
    manuelle Vorberichtstabelle (`baue_vorbericht_tabelle`), aber `quelle_einheit`
    "euro" (bereits kaufmännisch gerundete Cent, kein ×1000, D-12), `planzeile`/
    `gesamt_plan` `null` (kein GEP-Bezug — die GEP-Z.-28-Prüfung läuft über Regel 5,
    nicht über die App-Daten)."""
    gesamt_df = df.filter(pl.col("ist_gesamt"))
    gesamt_nach_jahr = {zeile["jahr"]: zeile for zeile in gesamt_df.iter_rows(named=True)}
    if not gesamt_nach_jahr:
        raise AppDatenFehler("eigenkapital: keine Gesamtzeile vorhanden")

    gesamt_werte: list[int | None] = []
    gesamt_quelle: int | None = None
    for jahr in jahre:
        zeile = gesamt_nach_jahr.get(jahr)
        if zeile is None:
            gesamt_werte.append(None)
            continue
        gesamt_werte.append(zeile["betrag"])
        gesamt_quelle = zeile["quelle"]

    posten_df = df.filter(~pl.col("ist_gesamt"))
    positionen = sorted(posten_df["position"].unique().to_list())
    posten_liste: list[dict[str, object]] = []
    for position in positionen:
        teil = posten_df.filter(pl.col("position") == position)
        name = teil["posten_name"][0]
        posten_schluessel = teil["posten"][0]
        zeilen_nach_jahr = {zeile["jahr"]: zeile for zeile in teil.iter_rows(named=True)}

        werte: list[int | None] = []
        quelle: int | None = None
        anmerkung: str | None = None
        for jahr in jahre:
            zeile = zeilen_nach_jahr.get(jahr)
            if zeile is None:
                werte.append(None)
                continue
            werte.append(zeile["betrag"])
            quelle = zeile["quelle"]
            anmerkung = zeile["anmerkung"]

        posten_liste.append(
            {
                "posten": posten_schluessel,
                "name": name,
                "werte": werte,
                "gerundet": True,
                "berechnet": False,
                "quelle": quelle,
                "anmerkung": anmerkung,
            }
        )

    return {
        "tabelle": "eigenkapital",
        "quelle_einheit": "euro",
        "planzeile": None,
        "gesamt_plan": None,
        "gesamt_vorbericht": {
            "werte": gesamt_werte,
            "gerundet": True,
            "quelle": gesamt_quelle,
        },
        "posten": posten_liste,
    }


def baue_stellenplan_json(df: pl.DataFrame, *, haushaltsjahr: int) -> dict[str, object]:
    """Baut die App-JSON-Struktur von `stellenplan.csv` (D-18, D-21, Plan 04-03): eine
    Zeile je CSV-Zeile (bereits in CSV-Reihenfolge, teil/produktbereich/position/
    merkmal/jahr), `stellen_hundertstel` durch 100 geteilt (VZÄ, `einheit_stellen`
    "vzae"); `personen` bleibt unverändert (D-19: Nachwuchskräfte sind keine Stellen)."""

    def _stellen(hundertstel: int | None) -> float | None:
        return hundertstel / 100 if hundertstel is not None else None

    zeilen = [
        {
            "teil": zeile["teil"],
            "position": zeile["position"],
            "gruppe": zeile["gruppe"],
            "amtsbezeichnung": zeile["amtsbezeichnung"],
            "verguetung": zeile["verguetung"],
            "produktbereich": zeile["produktbereich"],
            "merkmal": zeile["merkmal"],
            "jahr": zeile["jahr"],
            "stichtag": zeile["stichtag"],
            "stellen": _stellen(zeile["stellen_hundertstel"]),
            "personen": zeile["personen"],
            "vermerk": zeile["vermerk"],
            "pdf_seite": zeile["pdf_seite"],
        }
        for zeile in df.iter_rows(named=True)
    ]
    return {
        "haushaltsjahr": haushaltsjahr,
        "einheit_stellen": "vzae",
        "zeilen": zeilen,
    }


def erzeuge_app_daten(
    jahr: int,
    *,
    daten_wurzel: Path = DATEN_WURZEL,
    app_daten_wurzel: Path = APP_DATEN_WURZEL,
) -> list[Path]:
    """Schritt 07 (D-21, D-24): baut `app/src/data/haushalt.json` aus `daten/` auf.

    Liest nur CSVs unter `daten_wurzel` (nie das PDF, D-06). `jahre`/`wertarten` kommen
    aus den Ergebnisplan-Spaltenköpfen des Jahrgangs (D-21), nie hartkodiert.
    """
    jahrgang = lade_jahrgang(jahr)
    ergebnisplan = lies_plan_csv(daten_wurzel / ERGEBNISPLAN_CSV)
    finanzplan = lies_plan_csv(daten_wurzel / FINANZPLAN_CSV)
    hierarchie = lies_hierarchie_csv(daten_wurzel / HIERARCHIE_CSV)
    planwerte = Planwerte(ergebnisplan, datei="ergebnisplan")

    spalten_zu_wertart = [zerlege_spaltenkopf(kopf) for kopf in jahrgang.spalten["ergebnisplan"]]
    jahre = [jahr_wert for _wertart, jahr_wert in spalten_zu_wertart]
    wertarten = [wertart for wertart, _jahr_wert in spalten_zu_wertart]

    weitergabe_produkt = layout_text(jahrgang, "weitergabe_kreis_land", "produkt")
    gep_pdf_seite = ergebnisplan.filter(pl.col("ebene") == "GESAMT")["pdf_seite"][0]

    # Reihenfolge ist Teil des App-JSON-Vertrags (D-21): steuerarten, zuwendungen,
    # transferaufwendungen, kita_zuschuesse, investitionszuwendungen (Phase 5 D-03, ohne
    # GEP-Zeile: die App liest GFP Z. 18 aus `finanzplan`), dann die sechs weiteren Tabellen
    # (leistungsentgelte, kostenerstattungen, personal, sachaufwand, sonstige_aufwendungen,
    # zuletzt sonstige_ertraege, Phase 5 D-04) — dict-
    # Einfügereihenfolge bleibt beim Schreiben erhalten (schreibe_app_json/json.dumps,
    # keine sort_keys).
    transferaufwendungen_df = lies_vorbericht_csv(daten_wurzel / TRANSFERAUFWENDUNGEN_CSV)
    vorbericht_quellen = {
        "steuerarten": lies_vorbericht_csv(daten_wurzel / STEUERARTEN_CSV),
        "zuwendungen": lies_vorbericht_csv(daten_wurzel / ZUWENDUNGEN_CSV),
        "transferaufwendungen": transferaufwendungen_df,
        "kita_zuschuesse": lies_vorbericht_csv(daten_wurzel / KITA_ZUSCHUESSE_CSV),
        "investitionszuwendungen": lies_vorbericht_csv(daten_wurzel / INVESTITIONSZUWENDUNGEN_CSV),
        **zerlege_weitere_vorberichtstabellen(
            lies_vorbericht_csv(daten_wurzel / WEITERE_VORBERICHTSTABELLEN_CSV)
        ),
    }
    vorbericht = {
        tabelle: baue_vorbericht_tabelle(
            df,
            jahre=jahre,
            planwerte=planwerte,
            gep_zeile=REGEL5_GEP_ZEILEN.get(tabelle),
            sonstige=(tabelle in TABELLEN_MIT_SONSTIGE),
        )
        for tabelle, df in vorbericht_quellen.items()
    }

    meta = lies_meta_json(daten_wurzel / META_JSON)
    eigenkapital_df = lies_eigenkapital_csv(daten_wurzel / EIGENKAPITAL_CSV)
    eigenkapital = baue_eigenkapital_tabelle(eigenkapital_df, jahre=jahre)

    knoten = baue_knoten(
        hierarchie,
        ergebnisplan=ergebnisplan,
        transfer_df=transferaufwendungen_df,
        produkt=weitergabe_produkt,
        gep_pdf_seite=gep_pdf_seite,
    )
    ergebnisplan_app = baue_ergebnisplan(
        knoten,
        ergebnisplan=ergebnisplan,
        transfer_df=transferaufwendungen_df,
        hierarchie=hierarchie,
        produkt=weitergabe_produkt,
        jahre=jahre,
        wertarten=wertarten,
    )
    finanzplan_app = baue_finanzplan(
        finanzplan,
        jahre=jahre,
        wertarten=wertarten,
        haushaltsjahr=jahrgang.haushaltsjahr,
    )

    daten = {
        "haushaltsjahr": jahrgang.haushaltsjahr,
        "jahre": jahre,
        "wertarten": wertarten,
        "meta": meta,
        "knoten": knoten,
        "ergebnisplan": ergebnisplan_app,
        "finanzplan": finanzplan_app,
        "vorbericht": vorbericht,
        "eigenkapital": eigenkapital,
        "zeilen_namen": baue_zeilen_namen(list(finanzplan_app["GESAMT"]["zeilen"])),
    }

    pfad = app_daten_wurzel / HAUSHALT_JSON
    schreibe_app_json(daten, pfad, praefix="haushalt")

    stellenplan_df = lies_stellenplan_csv(daten_wurzel / STELLENPLAN_CSV)
    stellenplan_daten = baue_stellenplan_json(stellenplan_df, haushaltsjahr=jahrgang.haushaltsjahr)
    stellenplan_pfad = app_daten_wurzel / STELLENPLAN_JSON
    schreibe_app_json(stellenplan_daten, stellenplan_pfad, praefix="stellenplan")

    produkte = lies_produkte_json(daten_wurzel / PRODUKTE_JSON)
    grundzahlen = lies_grundzahlen_csv(daten_wurzel / GRUNDZAHLEN_CSV)
    produkte_daten = baue_produkte_json(produkte, grundzahlen)
    produkte_pfad = app_daten_wurzel / PRODUKTE_APP_JSON
    schreibe_app_json(produkte_daten, produkte_pfad, praefix="produkte")

    investitionen_df = lies_investitionen_csv(daten_wurzel / INVESTITIONEN_CSV)
    ve_faelligkeiten_df = lies_ve_faelligkeiten_csv(daten_wurzel / VE_FAELLIGKEITEN_CSV)
    verbindlichkeiten_df = lies_vorbericht_csv(daten_wurzel / VERBINDLICHKEITEN_CSV)
    investitionen_daten = baue_investitionen_json(
        investitionen=investitionen_df,
        ve_faelligkeiten=ve_faelligkeiten_df,
        hierarchie=hierarchie,
        verbindlichkeiten=verbindlichkeiten_df,
        finanzplan=finanzplan,
        meta=meta,
        haushaltsjahr=jahrgang.haushaltsjahr,
        jahre=jahre,
        wertarten=wertarten,
    )
    investitionen_pfad = app_daten_wurzel / INVESTITIONEN_JSON
    schreibe_app_json(investitionen_daten, investitionen_pfad, praefix="investitionen")

    # texte.json (D-15 bis D-17, MANU-08, Plan 04-05): parst erklaerungen.md, prüft jeden
    # Absatz gegen die Ziffernregel und löst alle verwendeten Platzhalter gegen die oben
    # gebauten App-Dictionaries auf -- ein unbekannter Schlüssel oder ein unbekanntes
    # Formatkürzel bricht Schritt 07 mit TexteFehler ab (fail-fast, D-08-Stil). Die
    # Pipeline formatiert nie (D-15): texte.json trägt nur Rohtexte und Rohwerte.
    erklaerungen = lies_erklaerungen(daten_wurzel / ERKLAERUNGEN_MD)
    for erklaertext in erklaerungen:
        for absatz in erklaertext.absaetze:
            pruefe_text(absatz)
    alle_werte = textwerte(daten, investitionen_daten, produkte_daten)
    verwendet = loese_auf(erklaerungen, alle_werte)
    texte_daten = {
        "haushaltsjahr": jahrgang.haushaltsjahr,
        "texte": [
            {
                "schluessel": erklaertext.schluessel,
                "titel": erklaertext.titel,
                "quelle_seiten": list(erklaertext.quelle_seiten),
                "absaetze": list(erklaertext.absaetze),
            }
            for erklaertext in erklaerungen
        ],
        "werte": {schluessel: wert for schluessel, (wert, _format) in verwendet.items()},
    }
    texte_pfad = app_daten_wurzel / TEXTE_JSON
    schreibe_app_json(texte_daten, texte_pfad, praefix="texte")

    return [pfad, stellenplan_pfad, produkte_pfad, investitionen_pfad, texte_pfad]
