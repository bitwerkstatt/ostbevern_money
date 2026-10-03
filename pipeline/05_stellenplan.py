"""Pipeline-Schritt 05: Stellenplan (Spez. 5.2, EXTR-10).

Dünner typer-Einstieg; die Logik liegt in `ostbevern.stellenplan`.
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
from ostbevern.schema import SchemaFehler
from ostbevern.stellenplan import StellenplanFehler, extrahiere_stellenplan

app = typer.Typer(
    add_completion=False,
    help="Extrahiert den Stellenplan (Teil A/B, Stellenübersicht, Nachwuchskräfte).",
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
        ergebnis = extrahiere_stellenplan(jahrgang)
    except (KonfigurationsFehler, PdfFehler, StellenplanFehler, SchemaFehler) as fehler:
        typer.echo(f"Fehler: {fehler}", err=True)
        raise typer.Exit(code=1) from fehler

    pfad_relativ = ergebnis.pfad.relative_to(PROJEKT_WURZEL)
    typer.echo(f"{ergebnis.zeilen_geschrieben} Zeilen geschrieben: {pfad_relativ}")


if __name__ == "__main__":
    app()
