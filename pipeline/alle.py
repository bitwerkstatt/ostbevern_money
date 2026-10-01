"""Pipeline-Einstiegspunkt (Spez. 5.2).

Prüft den gewählten Jahrgang (Jahrgangs- und Sollwertdatei, PDF-Existenz) und führt die
nummerierten Schritte in Reihenfolge aus (D-09): 01 (Seiten klassifizieren), 02 (Pläne
extrahieren), Querschnitte (Kontrollquelle, PDF-lesend, D-14), 06 (Konsistenzprüfung, liest
danach nur noch CSVs, D-06). Spätere Phasen hängen 03-05 und 07 zwischen bzw. nach diesen
Schritten an. Die eigentliche Logik lebt in `ostbevern/`; dieses Modul bleibt ein dünner
typer-Einstiegspunkt.
"""

from __future__ import annotations

from typing import Annotated

import typer

from ostbevern import plaene, pruefung, querschnitte, seiten
from ostbevern.konfiguration import (
    PROJEKT_WURZEL,
    STANDARD_JAHR,
    KonfigurationsFehler,
    lade_jahrgang,
    lade_sollwerte,
)
from ostbevern.pdf import PdfFehler
from ostbevern.plaene import PlaeneFehler
from ostbevern.pruefung import PruefungsFehler
from ostbevern.querschnitte import QuerschnitteFehler
from ostbevern.schema import SchemaFehler
from ostbevern.seiten import SeitenFehler

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
        ergebnis_querschnitte = querschnitte.extrahiere_querschnitte(jahrgang)
    except (PdfFehler, QuerschnitteFehler, SchemaFehler, KonfigurationsFehler) as fehler:
        typer.echo(f"Fehler: {fehler}", err=True)
        raise typer.Exit(code=1) from fehler
    typer.echo(
        f"Schritt 06: Querschnitte: {ergebnis_querschnitte.zeilen_geschrieben} Werte geschrieben."
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


if __name__ == "__main__":
    app()
