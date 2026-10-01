"""Pipeline-Einstiegspunkt (Spez. 5.2).

Prüft den gewählten Jahrgang (Jahrgangs- und Sollwertdatei, PDF-Existenz) und ist
die Stelle, an der spätere Phasen die nummerierten Schritte 01-07 in Reihenfolge
anhängen (D-10). Die eigentliche Logik lebt in `ostbevern/`; dieses Modul bleibt
ein dünner typer-Einstiegspunkt.
"""

from __future__ import annotations

from typing import Annotated

import typer

from ostbevern.konfiguration import (
    PROJEKT_WURZEL,
    STANDARD_JAHR,
    KonfigurationsFehler,
    lade_jahrgang,
    lade_sollwerte,
)

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


if __name__ == "__main__":
    app()
