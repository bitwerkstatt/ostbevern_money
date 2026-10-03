"""Zentrales CSV-Schema und -IO für alle generierten Dateien unter daten/ (D-21, D-22).

Schreiben und Lesen laufen ausschließlich über dieses Modul, auch in den Tests. So
wird z. B. der Code "01" nie als Zahl 1 interpretiert.
"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import polars as pl

from ostbevern.konfiguration import PROJEKT_WURZEL

DATEN_WURZEL = PROJEKT_WURZEL / "daten"

SEITEN_CSV = Path("zwischen/seiten.csv")
HIERARCHIE_CSV = Path("aufbereitet/hierarchie.csv")
ERGEBNISPLAN_CSV = Path("aufbereitet/ergebnisplan.csv")
FINANZPLAN_CSV = Path("aufbereitet/finanzplan.csv")
INVESTITIONEN_CSV = Path("aufbereitet/investitionen.csv")
VE_FAELLIGKEITEN_CSV = Path("aufbereitet/ve_faelligkeiten.csv")
# Produktbeschreibungen (Phase 3, 03-04, EXTR-06/08): eine JSON-Liste statt einer CSV,
# da `leistungen` und `erlaeuterungen` verschachtelte Listen sind (Spez. 4.2).
PRODUKTE_JSON = Path("aufbereitet/produkte.json")
ERLAEUTERUNGEN_CSV = Path("aufbereitet/erlaeuterungen.csv")
# Grundzahlen je Produkt (Phase 3, 03-05, EXTR-07): Kennzahlen mit Einheit, Jahr und
# per-Jahr-Hinweis (D-12/D-13), inkl. der Steuer-Istwerte 2022-2025 von 160101.
GRUNDZAHLEN_CSV = Path("aufbereitet/grundzahlen.csv")
# Kontrollquelle (nie Datenquelle der App), daher unter zwischen/ statt aufbereitet/ (D-14).
QUERSCHNITTE_CSV = Path("zwischen/querschnitte.csv")
# PB-Investitionslisten (Phase 3, 03-03, D-06): ebenfalls reine Kontrollquelle, nie
# Datenquelle der App (Spez. 3.8), daher unter zwischen/ wie querschnitte.csv.
INVESTITIONEN_PB_CSV = Path("zwischen/investitionen_pb.csv")
KONSISTENZ_MD = Path("pruefberichte/konsistenz.md")
BEFUNDE_MD = Path("pruefberichte/befunde.md")

# Manuell gepflegte Vorberichtstabellen (Phase 4, D-05, D-06, D-09): einmalig von Hand
# abgeschrieben, danach eingecheckte Handdaten, die kein Pipeline-Schritt überschreibt.
# Die Schreibfunktion `schreibe_vorbericht_csv` unten wird deshalb nur für diese einmalige
# Transkription und in Tests aufgerufen, nie aus einem Pipeline-Schritt heraus.
MANUELL_WURZEL = Path("manuell")
STEUERARTEN_CSV = MANUELL_WURZEL / "steuerarten.csv"
ZUWENDUNGEN_CSV = MANUELL_WURZEL / "zuwendungen.csv"
TRANSFERAUFWENDUNGEN_CSV = MANUELL_WURZEL / "transferaufwendungen.csv"
KITA_ZUSCHUESSE_CSV = MANUELL_WURZEL / "kita_zuschuesse.csv"
# Weitere Vorberichtstabellen (Phase 4, D-08, MANU-05): die fünf Tabellen Leistungs-
# entgelte (2.1.4), Kostenerstattungen (2.1.6), Personal (2.2.1), Sachaufwand (2.2.3)
# und Sonstige Aufwendungen (2.2.6) in einer Datei, Spalte `tabelle` unterscheidet sie.
WEITERE_VORBERICHTSTABELLEN_CSV = MANUELL_WURZEL / "weitere_vorberichtstabellen.csv"


class SchemaFehler(ValueError):
    """Wird ausgelöst, wenn eine CSV-Datei nicht dem zentralen Schema entspricht."""


EBENEN = ("GESAMT", "PB", "PG", "P")
WERTARTEN = ("ergebnis", "ansatz", "ve", "planung")

_EBENEN_RANG = {ebene: rang for rang, ebene in enumerate(EBENEN)}
_WERTART_LABEL = {"Ergebnis": "ergebnis", "Ansatz": "ansatz", "VE": "ve", "Planung": "planung"}


def zerlege_spaltenkopf(kopf: str) -> tuple[str, int]:
    """Zerlegt einen Spaltenkopf wie "Ergebnis 2024" in (wertart, jahr)."""
    teile = kopf.split()
    if len(teile) != 2 or teile[0] not in _WERTART_LABEL or not teile[1].isdigit():
        raise SchemaFehler(f"Unbekannter Spaltenkopf: {kopf!r}")
    return _WERTART_LABEL[teile[0]], int(teile[1])


PLAN_SPALTEN: dict[str, pl.PolarsDataType] = {
    "ebene": pl.Utf8,
    "code": pl.Utf8,
    "synthetisch": pl.Boolean,
    "zeile": pl.Utf8,
    "zeile_kanonisch": pl.Utf8,
    "zeile_name": pl.Utf8,
    "operator": pl.Utf8,
    "ist_summe": pl.Boolean,
    "jahr": pl.Int64,
    "wertart": pl.Utf8,
    "betrag": pl.Int64,
    "pdf_seite": pl.Int64,
}


def _pruefe_keine_leeren_strings(
    df: pl.DataFrame, spalten: dict[str, pl.PolarsDataType], pfad: Path
) -> None:
    for name, dtype in spalten.items():
        if dtype == pl.Utf8 and name in df.columns:
            leer = df.filter(pl.col(name) == "")
            if leer.height > 0:
                raise SchemaFehler(
                    f"{pfad}: Spalte {name!r} enthält leere Strings; kein Wert ist null, nicht ''"
                )


def schreibe_csv(
    df: pl.DataFrame,
    pfad: Path,
    spalten: dict[str, pl.PolarsDataType],
    sortierung: list[str],
) -> None:
    """Schreibt `df` nach `pfad` in fester Spaltenreihenfolge, UTF-8 ohne BOM, LF (D-21)."""
    _pruefe_keine_leeren_strings(df, spalten, pfad)
    sortiert = df.sort(sortierung, nulls_last=False)
    ausgewaehlt = sortiert.select(list(spalten.keys()))
    # strict=True (D-08): fail loud on Overflow/NaN/unparsable Input statt polars'
    # Standardverhalten (stille Coercion/Truncation). strict=True allein erkennt aber
    # KEINE Nachkommastellen-Truncation bei Float->Int (verifiziert gegen polars>=1.44.2:
    # pl.DataFrame({"x": [1234.5]}).cast({"x": pl.Int64}, strict=True) wirft nicht),
    # deshalb zusätzlich Round-Trip-Prüfung je Float-Spalte unten.
    geordnet = ausgewaehlt.cast(spalten, strict=True)
    for name, ziel_dtype in spalten.items():
        quelle_dtype = ausgewaehlt.schema[name]
        if quelle_dtype != ziel_dtype and quelle_dtype in (pl.Float32, pl.Float64):
            zurueck = geordnet[name].cast(quelle_dtype)
            if not zurueck.equals(ausgewaehlt[name], null_equal=True):
                raise SchemaFehler(
                    f"{pfad}: Spalte {name!r} verliert Genauigkeit beim Cast {quelle_dtype} -> "
                    f"{ziel_dtype}"
                )
    pfad.parent.mkdir(parents=True, exist_ok=True)
    geordnet.write_csv(pfad)


def lies_csv(pfad: Path, spalten: dict[str, pl.PolarsDataType]) -> pl.DataFrame:
    """Liest `pfad` mit festem Schema; lehnt eine abweichende Kopfzeile ab (D-22)."""
    df = pl.read_csv(pfad, schema_overrides=spalten)
    erwartet = list(spalten.keys())
    if df.columns != erwartet:
        raise SchemaFehler(f"{pfad}: Kopfzeile {df.columns} weicht vom Schema {erwartet} ab")
    return df


def schreibe_plan_csv(df: pl.DataFrame, pfad: Path) -> None:
    """Schreibt eine Plan-CSV sortiert nach (Ebenenrang, Code, Zeile, Jahr, Wertart)."""
    mit_rang = df.with_columns(
        pl.col("ebene").replace_strict(_EBENEN_RANG, return_dtype=pl.Int64).alias("_ebenenrang")
    )
    schreibe_csv(mit_rang, pfad, PLAN_SPALTEN, ["_ebenenrang", "code", "zeile", "jahr", "wertart"])


def lies_plan_csv(pfad: Path) -> pl.DataFrame:
    """Liest eine Plan-CSV über `lies_csv` mit PLAN_SPALTEN."""
    return lies_csv(pfad, PLAN_SPALTEN)


SEITEN_SPALTEN: dict[str, pl.PolarsDataType] = {
    "pdf_seite": pl.Int64,
    "typ": pl.Utf8,
    "pb": pl.Utf8,
    "pg": pl.Utf8,
    "produkt": pl.Utf8,
}


def schreibe_seiten_csv(df: pl.DataFrame, pfad: Path) -> None:
    """Schreibt seiten.csv sortiert nach pdf_seite (D-16, D-17, D-21)."""
    schreibe_csv(df, pfad, SEITEN_SPALTEN, ["pdf_seite"])


def lies_seiten_csv(pfad: Path) -> pl.DataFrame:
    """Liest seiten.csv über `lies_csv` mit SEITEN_SPALTEN."""
    return lies_csv(pfad, SEITEN_SPALTEN)


HIERARCHIE_SPALTEN: dict[str, pl.PolarsDataType] = {
    "ebene": pl.Utf8,
    "code": pl.Utf8,
    "name": pl.Utf8,
    "eltern_code": pl.Utf8,
    "pdf_seite_start": pl.Int64,
    "synthetisch": pl.Boolean,
}


def schreibe_hierarchie_csv(df: pl.DataFrame, pfad: Path) -> None:
    """Schreibt hierarchie.csv sortiert nach code, was Baumreihenfolge ergibt (D-14, D-15)."""
    schreibe_csv(df, pfad, HIERARCHIE_SPALTEN, ["code"])


def lies_hierarchie_csv(pfad: Path) -> pl.DataFrame:
    """Liest hierarchie.csv über `lies_csv` mit HIERARCHIE_SPALTEN."""
    return lies_csv(pfad, HIERARCHIE_SPALTEN)


# Haushaltsquerschnitte (Phase 3, D-14/D-15): Langformat, ein Wert je (PB, PG oder
# GESAMTSUMME, Plan, Kennzahl). `pg` ist null auf der GESAMTSUMME-Zeile.
QUERSCHNITTE_SPALTEN: dict[str, pl.PolarsDataType] = {
    "pb": pl.Utf8,
    "pg": pl.Utf8,
    "gesamtsumme": pl.Boolean,
    "plan": pl.Utf8,
    "kennzahl": pl.Utf8,
    "betrag": pl.Int64,
    "pdf_seite": pl.Int64,
}


def schreibe_querschnitte_csv(df: pl.DataFrame, pfad: Path) -> None:
    """Schreibt querschnitte.csv sortiert nach plan, pb, gesamtsumme, pg (nulls first),
    kennzahl (D-14, D-15)."""
    schreibe_csv(df, pfad, QUERSCHNITTE_SPALTEN, ["plan", "pb", "gesamtsumme", "pg", "kennzahl"])


def lies_querschnitte_csv(pfad: Path) -> pl.DataFrame:
    """Liest querschnitte.csv über `lies_csv` mit QUERSCHNITTE_SPALTEN."""
    return lies_csv(pfad, QUERSCHNITTE_SPALTEN)


# Investitionsmaßnahmen (Phase 3, 03-02, D-07/D-08, EXTR-09): ein Wert je Konto-Zeile
# und bespieltem Jahr. Nur Produktseiten (D-06); Finanzierungs-Konten (692/792) und
# Kassenwirksamkeit-Werte sind ausdrücklich nicht enthalten.
INVESTITIONEN_SPALTEN: dict[str, pl.PolarsDataType] = {
    "produkt": pl.Utf8,
    "massnahme_id": pl.Utf8,
    "massnahme_name": pl.Utf8,
    "konto": pl.Utf8,
    "konto_name": pl.Utf8,
    "richtung": pl.Utf8,
    "art": pl.Utf8,
    "jahr": pl.Int64,
    "wertart": pl.Utf8,
    "betrag": pl.Int64,
    "pdf_seite": pl.Int64,
}


def schreibe_investitionen_csv(df: pl.DataFrame, pfad: Path) -> None:
    """Schreibt investitionen.csv sortiert nach produkt, massnahme_id, konto, jahr,
    wertart, pdf_seite, betrag (D-21)."""
    schreibe_csv(
        df,
        pfad,
        INVESTITIONEN_SPALTEN,
        ["produkt", "massnahme_id", "konto", "jahr", "wertart", "pdf_seite", "betrag"],
    )


def lies_investitionen_csv(pfad: Path) -> pl.DataFrame:
    """Liest investitionen.csv über `lies_csv` mit INVESTITIONEN_SPALTEN."""
    return lies_csv(pfad, INVESTITIONEN_SPALTEN)


# VE-Fälligkeiten (Phase 3, 03-02, EXTR-09): eine Zeile je "(Kassenwirksamkeit)"-Wert
# einer Investitions-Kontozeile, nie in investitionen.csv oder einer Summe enthalten.
VE_FAELLIGKEITEN_SPALTEN: dict[str, pl.PolarsDataType] = {
    "produkt": pl.Utf8,
    "massnahme_id": pl.Utf8,
    "konto": pl.Utf8,
    "jahr": pl.Int64,
    "betrag": pl.Int64,
    "pdf_seite": pl.Int64,
}


def schreibe_ve_faelligkeiten_csv(df: pl.DataFrame, pfad: Path) -> None:
    """Schreibt ve_faelligkeiten.csv sortiert nach produkt, massnahme_id, konto, jahr,
    pdf_seite (D-21)."""
    schreibe_csv(
        df,
        pfad,
        VE_FAELLIGKEITEN_SPALTEN,
        ["produkt", "massnahme_id", "konto", "jahr", "pdf_seite"],
    )


def lies_ve_faelligkeiten_csv(pfad: Path) -> pl.DataFrame:
    """Liest ve_faelligkeiten.csv über `lies_csv` mit VE_FAELLIGKEITEN_SPALTEN."""
    return lies_csv(pfad, VE_FAELLIGKEITEN_SPALTEN)


# PB-Investitionslisten (Phase 3, 03-03, D-06): Kontrollquelle für die Regel-6-Gegenprobe
# zwischen PB-Listen und Produktseiten. Nie Datenquelle der App, deshalb unter zwischen/
# statt aufbereitet/ (wie querschnitte.csv). Granularität ist ein Wert je Konto-Zeile,
# bespieltem Jahr und PB-Listen-Block (ein (pb, massnahme_id) kann mehrere Blöcke haben,
# D-06, Research Pitfall 8 — nicht nach ID zusammengeführt).
INVESTITIONEN_PB_SPALTEN: dict[str, pl.PolarsDataType] = {
    "pb": pl.Utf8,
    "massnahme_id": pl.Utf8,
    "konto": pl.Utf8,
    "richtung": pl.Utf8,
    "jahr": pl.Int64,
    "wertart": pl.Utf8,
    "betrag": pl.Int64,
    "pdf_seite": pl.Int64,
}


def schreibe_investitionen_pb_csv(df: pl.DataFrame, pfad: Path) -> None:
    """Schreibt investitionen_pb.csv sortiert nach pb, massnahme_id, konto, jahr, wertart,
    pdf_seite, betrag (D-21)."""
    schreibe_csv(
        df,
        pfad,
        INVESTITIONEN_PB_SPALTEN,
        ["pb", "massnahme_id", "konto", "jahr", "wertart", "pdf_seite", "betrag"],
    )


def lies_investitionen_pb_csv(pfad: Path) -> pl.DataFrame:
    """Liest investitionen_pb.csv über `lies_csv` mit INVESTITIONEN_PB_SPALTEN."""
    return lies_csv(pfad, INVESTITIONEN_PB_SPALTEN)


# Produktbeschreibungen (Phase 3, 03-04, EXTR-06/08): die exakte, geordnete Schlüssel-
# menge jedes Datensatzes in produkte.json (Spez. 4.2). Kein Personenfeld (D-09) — die
# Felder "verantwortlich"/"sachbearbeiter" werden vor dem Schreiben verworfen.
PRODUKT_SCHLUESSEL: tuple[str, ...] = (
    "code",
    "name",
    "pb",
    "pg",
    "fachbereich",
    "gremium",
    "beschreibung",
    "leistungen",
    "auftragsgrundlage",
    "bindungsgrad",
    "bindungsgrad_original",
    "klassifizierung",
    "zielgruppe",
    "ziele",
    "erlaeuterungen",
    "pdf_seiten",
)


def schreibe_produkte_json(produkte: list[dict[str, object]], pfad: Path) -> None:
    """Schreibt produkte.json: sortiert nach `code`, Schlüssel in PRODUKT_SCHLUESSEL-
    Reihenfolge, atomar (temp-Datei + os.replace), UTF-8 ohne BOM, LF, mit abschließendem
    Zeilenumbruch (D-21-Stil, keine Personennamen, D-09)."""
    schluessel_menge = set(PRODUKT_SCHLUESSEL)
    for produkt in produkte:
        vorhandene = set(produkt)
        fehlend = schluessel_menge - vorhandene
        unerwartet = vorhandene - schluessel_menge
        if fehlend or unerwartet:
            raise SchemaFehler(
                f"produkte.json: Produkt {produkt.get('code')!r} hat abweichende Schlüssel "
                f"(fehlend: {sorted(fehlend)}, unerwartet: {sorted(unerwartet)})"
            )
    geordnet = [
        {schluessel: produkt[schluessel] for schluessel in PRODUKT_SCHLUESSEL}
        for produkt in sorted(produkte, key=lambda p: p["code"])
    ]
    inhalt = json.dumps(geordnet, ensure_ascii=False, indent=2) + "\n"
    pfad.parent.mkdir(parents=True, exist_ok=True)
    deskriptor, temp_pfad_str = tempfile.mkstemp(
        dir=pfad.parent, prefix=".produkte-", suffix=".tmp"
    )
    temp_pfad = Path(temp_pfad_str)
    try:
        with os.fdopen(deskriptor, "w", encoding="utf-8", newline="\n") as datei:
            datei.write(inhalt)
        os.replace(temp_pfad, pfad)
    finally:
        temp_pfad.unlink(missing_ok=True)


def lies_produkte_json(pfad: Path) -> list[dict[str, object]]:
    """Liest produkte.json; lehnt einen Datensatz mit abweichenden Schlüsseln ab."""
    produkte = json.loads(pfad.read_text(encoding="utf-8"))
    schluessel_menge = set(PRODUKT_SCHLUESSEL)
    for produkt in produkte:
        if set(produkt) != schluessel_menge:
            raise SchemaFehler(f"{pfad}: Produkt {produkt.get('code')!r} hat abweichende Schlüssel")
    return produkte


# Erläuterungsposten (Phase 3, 03-04, EXTR-08, D-01 bis D-04): ein Wert je Block-Eintrag
# (Posten oder Freitext) im Langformat. `zu_zeilen` ist "|"-verbunden (zweistellige
# Zeilennummern), null wenn der Block keine "zu Nr." trägt (D-02); `betrag` ist null für
# eine Freitextzeile.
ERLAEUTERUNGEN_SPALTEN: dict[str, pl.PolarsDataType] = {
    "produkt": pl.Utf8,
    "block": pl.Int64,
    "position": pl.Int64,
    "zu_zeilen": pl.Utf8,
    "betrag": pl.Int64,
    "text": pl.Utf8,
    "pdf_seite": pl.Int64,
}


def schreibe_erlaeuterungen_csv(df: pl.DataFrame, pfad: Path) -> None:
    """Schreibt erlaeuterungen.csv sortiert nach produkt, block, position (D-21)."""
    schreibe_csv(df, pfad, ERLAEUTERUNGEN_SPALTEN, ["produkt", "block", "position"])


def lies_erlaeuterungen_csv(pfad: Path) -> pl.DataFrame:
    """Liest erlaeuterungen.csv über `lies_csv` mit ERLAEUTERUNGEN_SPALTEN."""
    return lies_csv(pfad, ERLAEUTERUNGEN_SPALTEN)


# Grundzahlen (Phase 3, 03-05, EXTR-07, D-12/D-13): ein Wert je Produkt, Kennzahl (Zeile
# im gedruckten Sinn, `position`) und bespieltem Jahr. `wert` ist Float64, weil Grund-
# zahlen Dezimalwerte (Gebühren, Quoten) neben Ganzzahlen (Euro-Beträge) enthalten;
# `nachkommastellen` hält die gedruckte Anzahl Dezimalstellen (0 für Ganzzahlen wie
# Euro-Beträge, die Float64 exakt darstellt, CONTEXT Claude's Discretion). `gruppe` ist
# null ohne Gruppenüberschrift (D-13); `hinweis` ist null ohne Stichtag-/Fußnotentext
# (D-12).
GRUNDZAHLEN_SPALTEN: dict[str, pl.PolarsDataType] = {
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
}


def schreibe_grundzahlen_csv(df: pl.DataFrame, pfad: Path) -> None:
    """Schreibt grundzahlen.csv sortiert nach produkt, position, jahr (D-21)."""
    schreibe_csv(df, pfad, GRUNDZAHLEN_SPALTEN, ["produkt", "position", "jahr"])


def lies_grundzahlen_csv(pfad: Path) -> pl.DataFrame:
    """Liest grundzahlen.csv über `lies_csv` mit GRUNDZAHLEN_SPALTEN."""
    return lies_csv(pfad, GRUNDZAHLEN_SPALTEN)


# Manuelle Vorberichtstabellen (Phase 4, D-05, D-06, D-09, MANU-01 bis MANU-04): ein Wert
# je Posten, Jahr und Wertart (Langformat). `betrag_teur` ist T€ wie gedruckt (nie Euro,
# D-05) — erst Schritt 07 rechnet × 1000 und setzt das Kennzeichen `gerundet`. `quelle`
# ist die 1-basierte PDF-Seite der gedruckten Zeile (MANU-07); `anmerkung` ist null ohne
# Fußnotentext. `ist_gesamt` markiert die mit abgeschriebene, gedruckte Gesamtzeile
# (D-07 Stufe a); genau eine je (tabelle, jahr).
VORBERICHT_SPALTEN: dict[str, pl.PolarsDataType] = {
    "tabelle": pl.Utf8,
    "position": pl.Int64,
    "posten": pl.Utf8,
    "posten_name": pl.Utf8,
    "ist_gesamt": pl.Boolean,
    "jahr": pl.Int64,
    "wertart": pl.Utf8,
    "betrag_teur": pl.Int64,
    "anmerkung": pl.Utf8,
    "quelle": pl.Int64,
}


def schreibe_vorbericht_csv(df: pl.DataFrame, pfad: Path) -> None:
    """Schreibt eine manuelle Vorberichtstabelle sortiert nach tabelle, position, jahr
    (D-05, D-06). Nur für die einmalige Abschrift (D-09) und Tests — kein Pipeline-Schritt
    schreibt unter daten/manuell/."""
    schreibe_csv(df, pfad, VORBERICHT_SPALTEN, ["tabelle", "position", "jahr"])


def lies_vorbericht_csv(pfad: Path) -> pl.DataFrame:
    """Liest eine manuelle Vorberichtstabelle über `lies_csv` mit VORBERICHT_SPALTEN."""
    return lies_csv(pfad, VORBERICHT_SPALTEN)
