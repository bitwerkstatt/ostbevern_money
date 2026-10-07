"""Pipeline-Schritt 08: Quellenbelege (Phase 7, DATA-04).

Dünner typer-Einstieg; die Logik liegt in `ostbevern.quellen` und `ostbevern.belegbilder`.
"""

from __future__ import annotations

from typing import Annotated

import typer

from ostbevern.belegbilder import BelegbildFehler
from ostbevern.konfiguration import (
    PROJEKT_WURZEL,
    STANDARD_JAHR,
    KonfigurationsFehler,
)
from ostbevern.pdf import PdfFehler
from ostbevern.produkte import ProdukteFehler
from ostbevern.quellen import QuellenFehler, erzeuge_quellen
from ostbevern.schema import SchemaFehler

app = typer.Typer(
    add_completion=False,
    help="Erzeugt app/src/data/quellen.json und die WebP-Belegseiten unter app/public/quellen/.",
)


@app.command()
def main(
    jahr: Annotated[
        int,
        typer.Option("--jahr", help="Haushaltsjahr; lädt pipeline/jahrgaenge/{jahr}.toml"),
    ] = STANDARD_JAHR,
    neu_rendern: Annotated[
        bool,
        typer.Option(
            "--neu-rendern",
            help=(
                "Alle Belegseiten neu rendern (sonst nur fehlende Bilder und Seiten, deren "
                "Schwärzungsrechtecke sich gegenüber daten/zwischen/belegbilder_schwaerzung.json "
                "geändert haben)."
            ),
        ),
    ] = False,
) -> None:
    try:
        ergebnis = erzeuge_quellen(jahr, neu_rendern=neu_rendern)
    except (
        QuellenFehler,
        BelegbildFehler,
        ProdukteFehler,
        PdfFehler,
        SchemaFehler,
        KonfigurationsFehler,
    ) as fehler:
        typer.echo(f"Fehler: {fehler}", err=True)
        raise typer.Exit(code=1) from fehler

    typer.echo(
        f"Geschrieben: {ergebnis.pfad.relative_to(PROJEKT_WURZEL)} "
        f"({ergebnis.anzahl_belege} Belege, {ergebnis.anzahl_ohne_bbox} ohne Markierung, "
        f"{len(ergebnis.seiten)} Seiten, {ergebnis.neu_gerendert} Bilder neu gerendert)"
    )
    typer.echo(f"Bericht: {ergebnis.bericht.relative_to(PROJEKT_WURZEL)}")


if __name__ == "__main__":
    app()
