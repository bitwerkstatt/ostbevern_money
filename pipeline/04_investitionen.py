"""Pipeline-Schritt 04: Investitionsmaßnahmen und VE-Fälligkeiten (Spez. 5.2).

Dünner typer-Einstieg; die Logik liegt in `ostbevern.investitionen`.
"""

from __future__ import annotations

from typing import Annotated

import typer

from ostbevern.investitionen import InvestitionenFehler, extrahiere_investitionen
from ostbevern.konfiguration import (
    PROJEKT_WURZEL,
    STANDARD_JAHR,
    KonfigurationsFehler,
    lade_jahrgang,
)
from ostbevern.pdf import PdfFehler
from ostbevern.schema import SchemaFehler

app = typer.Typer(
    add_completion=False,
    help="Extrahiert Investitionsmaßnahmen und VE-Fälligkeiten aus den Produktseiten.",
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
        ergebnisse = extrahiere_investitionen(jahrgang)
    except (KonfigurationsFehler, PdfFehler, InvestitionenFehler, SchemaFehler) as fehler:
        typer.echo(f"Fehler: {fehler}", err=True)
        raise typer.Exit(code=1) from fehler

    for ergebnis in ergebnisse:
        pfad_relativ = ergebnis.pfad.relative_to(PROJEKT_WURZEL)
        typer.echo(f"{ergebnis.zeilen_geschrieben} Zeilen geschrieben: {pfad_relativ}")


if __name__ == "__main__":
    app()
