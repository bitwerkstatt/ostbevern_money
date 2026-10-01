"""Pipeline-Schritt 06: Konsistenzprüfung (Spez. 5.5).

Dünner typer-Einstieg; die Logik liegt in `ostbevern.pruefung`.
"""

from __future__ import annotations

from typing import Annotated

import typer

from ostbevern.konfiguration import STANDARD_JAHR, KonfigurationsFehler
from ostbevern.pruefung import PruefungsFehler, pruefe_alles, schreibe_konsistenzbericht
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
        bericht = pruefe_alles(jahr)
    except (KonfigurationsFehler, PruefungsFehler, SchemaFehler) as fehler:
        typer.echo(f"Fehler: {fehler}", err=True)
        raise typer.Exit(code=1) from fehler

    schreibe_konsistenzbericht(bericht)

    for regel in bericht.regeln:
        titel_kurz = regel.titel.split(" – ")[0]
        typer.echo(f"{titel_kurz}: {regel.status} ({regel.geprueft} Werte)")

    typer.echo(f"Veraltete Befunde: {len(bericht.veraltete_befunde)}")
    typer.echo(f"Seiten mit typ=unbekannt: {len(bericht.unbekannte_seiten)}")

    if not bericht.ist_gruen:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
