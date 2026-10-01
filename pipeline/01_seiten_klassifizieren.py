"""Pipeline-Schritt 01: Seiten klassifizieren (Spez. 5.3).

Dünner typer-Einstieg; die Logik liegt in `ostbevern.seiten`.
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
from ostbevern.seiten import SeitenFehler, klassifiziere_seiten

app = typer.Typer(
    add_completion=False,
    help="Klassifiziert alle PDF-Seiten und leitet die PB/PG/Produkt-Hierarchie ab.",
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
        ergebnis = klassifiziere_seiten(jahrgang)
    except (KonfigurationsFehler, PdfFehler, SeitenFehler, SchemaFehler) as fehler:
        typer.echo(f"Fehler: {fehler}", err=True)
        raise typer.Exit(code=1) from fehler

    seiten_relativ = ergebnis.seiten_pfad.relative_to(PROJEKT_WURZEL)
    hierarchie_relativ = ergebnis.hierarchie_pfad.relative_to(PROJEKT_WURZEL)
    typer.echo(
        f"Seiten: {ergebnis.anzahl_seiten} klassifiziert, "
        f"{len(ergebnis.unbekannte_seiten)} unbekannt -> {seiten_relativ}"
    )
    if ergebnis.unbekannte_seiten:
        unbekannte_liste = ", ".join(str(seite) for seite in ergebnis.unbekannte_seiten)
        typer.echo(f"Unbekannte Seiten: {unbekannte_liste}")
    typer.echo(
        f"Hierarchie: {ergebnis.anzahl_pb} PB, {ergebnis.anzahl_pg} PG "
        f"({ergebnis.anzahl_pg_synthetisch} synthetisch), {ergebnis.anzahl_p} "
        f"Produkte -> {hierarchie_relativ}"
    )


if __name__ == "__main__":
    app()
