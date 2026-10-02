"""Pipeline-Schritt 06: Konsistenzprüfung (Spez. 5.5).

Dünner typer-Einstieg; die Logik liegt in `ostbevern.pruefung`. Extrahiert zuerst die
Haushaltsquerschnitte als eigenen, PDF-lesenden Kontrollquellen-Schritt
(`ostbevern.querschnitte`), bevor die eigentliche Prüfung läuft, die ausschließlich
CSVs liest (D-14, D-06).
"""

from __future__ import annotations

from typing import Annotated

import typer

from ostbevern import querschnitte
from ostbevern.konfiguration import (
    PROJEKT_WURZEL,
    STANDARD_JAHR,
    KonfigurationsFehler,
    lade_jahrgang,
)
from ostbevern.pdf import PdfFehler
from ostbevern.pruefung import PruefungsFehler, pruefe_alles, schreibe_konsistenzbericht
from ostbevern.querschnitte import QuerschnitteFehler
from ostbevern.schema import SchemaFehler

app = typer.Typer(
    add_completion=False,
    help="Prüft den Jahrgang gegen Anhang B und schreibt daten/pruefberichte/konsistenz.md.",
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
        ergebnis_querschnitte = querschnitte.extrahiere_querschnitte(jahrgang)
    except (KonfigurationsFehler, PdfFehler, QuerschnitteFehler, SchemaFehler) as fehler:
        typer.echo(f"Fehler: {fehler}", err=True)
        raise typer.Exit(code=1) from fehler

    pfad_relativ = ergebnis_querschnitte.pfad.relative_to(PROJEKT_WURZEL)
    typer.echo(
        f"Querschnitte: {ergebnis_querschnitte.zeilen_geschrieben} Werte geschrieben: "
        f"{pfad_relativ}"
    )

    try:
        bericht = pruefe_alles(jahr)
    except (KonfigurationsFehler, PruefungsFehler, SchemaFehler) as fehler:
        typer.echo(f"Fehler: {fehler}", err=True)
        raise typer.Exit(code=1) from fehler

    schreibe_konsistenzbericht(bericht)

    for regel in bericht.regeln:
        titel_kurz = regel.titel.split(" – ")[0]
        if regel.luecken:
            typer.echo(
                f"{titel_kurz}: {regel.status} "
                f"({regel.geprueft} Werte, {len(regel.luecken)} Lücken)"
            )
        else:
            typer.echo(f"{titel_kurz}: {regel.status} ({regel.geprueft} Werte)")

    typer.echo(f"Veraltete Befunde: {len(bericht.veraltete_befunde)}")
    typer.echo(f"Seiten mit typ=unbekannt: {len(bericht.unbekannte_seiten)}")

    if not bericht.ist_gruen:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
