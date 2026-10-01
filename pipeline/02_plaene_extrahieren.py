"""Pipeline-Schritt 02: Pläne extrahieren (Spez. 5.4).

Dünner typer-Einstieg; die Logik liegt in `ostbevern.plaene`.
"""

from __future__ import annotations

from typing import Annotated

import typer

from ostbevern.konfiguration import (
    PROJEKT_WURZEL,
    STANDARD_JAHR,
    KonfigurationsFehler,
    lade_jahrgang,
)
from ostbevern.pdf import PdfFehler
from ostbevern.plaene import PlaeneFehler, extrahiere_plaene
from ostbevern.schema import SchemaFehler

app = typer.Typer(
    add_completion=False,
    help="Extrahiert Gesamt- und Teilpläne aus dem Haushalts-PDF ins Langformat.",
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
        ergebnis = extrahiere_plaene(jahrgang)
    except (KonfigurationsFehler, PdfFehler, PlaeneFehler, SchemaFehler) as fehler:
        typer.echo(f"Fehler: {fehler}", err=True)
        raise typer.Exit(code=1) from fehler

    pfad_relativ = ergebnis.pfad.relative_to(PROJEKT_WURZEL)
    typer.echo(f"{ergebnis.zeilen_geschrieben} Zeilen geschrieben: {pfad_relativ}")


if __name__ == "__main__":
    app()
