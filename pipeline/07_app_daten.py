"""Pipeline-Schritt 07: App-JSON-Erzeugung (D-21, D-24).

Dünner typer-Einstieg; die Logik liegt in `ostbevern.app_daten`.
"""

from __future__ import annotations

from typing import Annotated

import typer

from ostbevern.app_daten import AppDatenFehler, erzeuge_app_daten
from ostbevern.konfiguration import (
    PROJEKT_WURZEL,
    STANDARD_JAHR,
    KonfigurationsFehler,
)
from ostbevern.pruefung import PruefungsFehler
from ostbevern.schema import SchemaFehler

app = typer.Typer(
    add_completion=False,
    help="Erzeugt app/src/data/haushalt.json aus den Dateien unter daten/.",
)


@app.command()
def main(
    jahr: Annotated[
        int,
        typer.Option("--jahr", help="Haushaltsjahr; lädt pipeline/jahrgaenge/{jahr}.toml"),
    ] = STANDARD_JAHR,
) -> None:
    try:
        pfade = erzeuge_app_daten(jahr)
    except (AppDatenFehler, SchemaFehler, KonfigurationsFehler, PruefungsFehler) as fehler:
        typer.echo(f"Fehler: {fehler}", err=True)
        raise typer.Exit(code=1) from fehler

    for pfad in pfade:
        pfad_relativ = pfad.relative_to(PROJEKT_WURZEL)
        typer.echo(f"Geschrieben: {pfad_relativ}")


if __name__ == "__main__":
    app()
