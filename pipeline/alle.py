"""Pipeline-Einstiegspunkt (Spez. 5.2).

Prüft den gewählten Jahrgang (Jahrgangs- und Sollwertdatei, PDF-Existenz) und führt die
nummerierten Schritte in Reihenfolge aus (D-09, D-24): 01 (Seiten klassifizieren), 02
(Pläne extrahieren), 03 (Produktinformationen und Erläuterungen), 04
(Investitionsmaßnahmen), Querschnitte (Kontrollquelle, PDF-lesend, D-14), 05
(Stellenplan, EXTR-10), 06 (Konsistenzprüfung, liest danach nur noch CSVs, D-06), 07
(App-JSON-Erzeugung, nur nach einem grünen Bericht, D-24). Die eigentliche Logik lebt in
`ostbevern/`; dieses Modul bleibt ein dünner typer-Einstiegspunkt.
"""

from __future__ import annotations

from typing import Annotated

import typer

from ostbevern import (
    app_daten,
    investitionen,
    plaene,
    produkte,
    pruefung,
    querschnitte,
    seiten,
    stellenplan,
)
from ostbevern.app_daten import AppDatenFehler
from ostbevern.investitionen import InvestitionenFehler
from ostbevern.konfiguration import (
    PROJEKT_WURZEL,
    STANDARD_JAHR,
    KonfigurationsFehler,
    lade_jahrgang,
    lade_sollwerte,
)
from ostbevern.pdf import PdfFehler
from ostbevern.plaene import PlaeneFehler
from ostbevern.produkte import ProdukteFehler
from ostbevern.pruefung import PruefungsFehler
from ostbevern.querschnitte import QuerschnitteFehler
from ostbevern.schema import SchemaFehler
from ostbevern.seiten import SeitenFehler
from ostbevern.stellenplan import StellenplanFehler
from ostbevern.texte import TexteFehler

app = typer.Typer(
    add_completion=False,
    help="Prüft den Jahrgang und führt die Pipeline-Schritte aus.",
)


@app.command()
def main(
    jahr: Annotated[
        int,
        typer.Option("--jahr", help="Haushaltsjahr; lädt pipeline/jahrgaenge/{jahr}.toml"),
    ] = STANDARD_JAHR,
) -> None:
    try:
        jahrgang = lade_jahrgang(jahr)
        lade_sollwerte(jahr)
    except KonfigurationsFehler as fehler:
        typer.echo(f"Fehler: {fehler}", err=True)
        raise typer.Exit(code=1) from fehler

    if not jahrgang.pdf_pfad.is_file():
        pdf_relativ = jahrgang.pdf_pfad.relative_to(PROJEKT_WURZEL)
        typer.echo(f"Fehler: PDF nicht gefunden: {pdf_relativ}", err=True)
        raise typer.Exit(code=1)

    pdf_relativ = jahrgang.pdf_pfad.relative_to(PROJEKT_WURZEL)
    typer.echo(
        f"Jahrgang {jahrgang.haushaltsjahr}: {pdf_relativ} "
        f"({jahrgang.anzahlen.pdf_seiten} Seiten erwartet), "
        f"{len(jahrgang.seitenbereiche)} Seitenbereiche, Sollwerte geladen."
    )

    try:
        ergebnis_seiten = seiten.klassifiziere_seiten(jahrgang)
    except (PdfFehler, SeitenFehler, SchemaFehler) as fehler:
        typer.echo(f"Fehler: {fehler}", err=True)
        raise typer.Exit(code=1) from fehler
    typer.echo(
        f"Schritt 01: {ergebnis_seiten.anzahl_seiten} Seiten klassifiziert, "
        f"{len(ergebnis_seiten.unbekannte_seiten)} unbekannt, "
        f"{ergebnis_seiten.anzahl_pb} PB, {ergebnis_seiten.anzahl_pg} PG "
        f"({ergebnis_seiten.anzahl_pg_synthetisch} synthetisch), "
        f"{ergebnis_seiten.anzahl_p} Produkte."
    )

    try:
        ergebnisse_plaene = plaene.extrahiere_plaene(jahrgang)
    except (PdfFehler, PlaeneFehler, SchemaFehler) as fehler:
        typer.echo(f"Fehler: {fehler}", err=True)
        raise typer.Exit(code=1) from fehler
    zeilen_gesamt = sum(ergebnis.zeilen_geschrieben for ergebnis in ergebnisse_plaene)
    typer.echo(f"Schritt 02: {zeilen_gesamt} Planzeilen geschrieben.")

    try:
        ergebnisse_produkte = produkte.extrahiere_produkte(jahrgang)
    except (PdfFehler, ProdukteFehler, SchemaFehler) as fehler:
        typer.echo(f"Fehler: {fehler}", err=True)
        raise typer.Exit(code=1) from fehler
    for ergebnis in ergebnisse_produkte:
        pfad_relativ = ergebnis.pfad.relative_to(PROJEKT_WURZEL)
        typer.echo(
            f"Schritt 03: {ergebnis.zeilen_geschrieben} Einträge geschrieben: {pfad_relativ}"
        )

    try:
        ergebnisse_investitionen = investitionen.extrahiere_investitionen(jahrgang)
    except (PdfFehler, InvestitionenFehler, SchemaFehler) as fehler:
        typer.echo(f"Fehler: {fehler}", err=True)
        raise typer.Exit(code=1) from fehler
    for ergebnis in ergebnisse_investitionen:
        pfad_relativ = ergebnis.pfad.relative_to(PROJEKT_WURZEL)
        typer.echo(f"Schritt 04: {ergebnis.zeilen_geschrieben} Zeilen geschrieben: {pfad_relativ}")

    try:
        ergebnis_querschnitte = querschnitte.extrahiere_querschnitte(jahrgang)
    except (PdfFehler, QuerschnitteFehler, SchemaFehler, KonfigurationsFehler) as fehler:
        typer.echo(f"Fehler: {fehler}", err=True)
        raise typer.Exit(code=1) from fehler
    typer.echo(f"Querschnitte: {ergebnis_querschnitte.zeilen_geschrieben} Werte geschrieben.")

    try:
        ergebnis_stellenplan = stellenplan.extrahiere_stellenplan(jahrgang)
    except (PdfFehler, StellenplanFehler, SchemaFehler) as fehler:
        typer.echo(f"Fehler: {fehler}", err=True)
        raise typer.Exit(code=1) from fehler
    typer.echo(
        f"Schritt 05: {ergebnis_stellenplan.zeilen_geschrieben} Zeilen geschrieben: "
        f"{ergebnis_stellenplan.pfad.relative_to(PROJEKT_WURZEL)}"
    )

    try:
        bericht = pruefung.pruefe_alles(jahr)
    except (KonfigurationsFehler, PruefungsFehler, SchemaFehler) as fehler:
        typer.echo(f"Fehler: {fehler}", err=True)
        raise typer.Exit(code=1) from fehler
    pruefung.schreibe_konsistenzbericht(bericht)
    for regel in bericht.regeln:
        titel_kurz = regel.titel.split(" – ")[0]
        typer.echo(f"Schritt 06: {titel_kurz}: {regel.status} ({regel.geprueft} Werte)")
    typer.echo(f"Schritt 06: Veraltete Befunde: {len(bericht.veraltete_befunde)}")

    if not bericht.ist_gruen:
        typer.echo("Fehler: Konsistenzbericht rot oder veraltete Befunde.", err=True)
        raise typer.Exit(code=1)

    try:
        pfade_app_daten = app_daten.erzeuge_app_daten(jahr)
    except (
        AppDatenFehler,
        SchemaFehler,
        KonfigurationsFehler,
        PruefungsFehler,
        TexteFehler,
    ) as fehler:
        typer.echo(f"Fehler: {fehler}", err=True)
        raise typer.Exit(code=1) from fehler
    for pfad in pfade_app_daten:
        pfad_relativ = pfad.relative_to(PROJEKT_WURZEL)
        typer.echo(f"Schritt 07: geschrieben: {pfad_relativ}")


if __name__ == "__main__":
    app()
