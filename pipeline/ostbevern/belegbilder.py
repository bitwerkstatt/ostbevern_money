"""Rendert Seiten des Haushalts-PDF als WebP-Belegbilder (Phase 7, DATA-04, Spez. 5.6).

Dieses Modul ist die einzige Stelle, die `pypdfium2` und `PIL` importiert. Maßstab (2 px je
PDF-Punkt) und Qualität (60) sind Konstanten aus Spez. 5.6, keine Jahrgangswerte.

Datenschutz: Eine Seite des Typs `produktinformationen` trägt Personenfelder
(Verantwortliche, Sachbearbeitung). Sie wird nur gerendert, wenn für sie Schwärzungsrechtecke
übergeben werden; sonst bricht `rendere_seiten` mit `BelegbildFehler` ab, bevor irgendein Bild
geschrieben wird.
"""

from __future__ import annotations

from collections.abc import Collection, Mapping, Sequence
from pathlib import Path

import pypdfium2 as pdfium
from PIL import ImageDraw

# Spez. 5.6: 2 Pixel je PDF-Punkt, WebP-Qualität 60.
RENDER_MASSSTAB = 2
WEBP_QUALITAET = 60
WEBP_METHODE = 6
_SCHWAERZUNG_FARBE = (0, 0, 0)
_PERSONEN_SEITENTYP = "produktinformationen"


class BelegbildFehler(ValueError):
    """Wird ausgelöst, wenn ein Belegbild nicht (sicher) gerendert werden kann."""


def bild_name(pdf_seite: int) -> str:
    """Dateiname des Belegbilds einer 1-basierten PDF-Seite, z. B. `s062.webp`."""
    if pdf_seite < 1:
        raise BelegbildFehler(f"PDF-Seite {pdf_seite} ist keine 1-basierte Seitennummer")
    return f"s{pdf_seite:03d}.webp"


def seitenmass_pdfium(pdf_pfad: Path, pdf_seite: int) -> tuple[float, float]:
    """Seitenmaß (Breite, Höhe) in PDF-Punkten laut pypdfium2, auf zwei Dezimalstellen gerundet.

    Nur für den Gegenprobe-Test gegen `PdfDokument.seitenmass` (pdfplumber).
    """
    pdf = pdfium.PdfDocument(str(pdf_pfad))
    try:
        breite, hoehe = pdf[pdf_seite - 1].get_size()
    finally:
        pdf.close()
    return round(float(breite), 2), round(float(hoehe), 2)


def rendere_seiten(
    pdf_pfad: Path,
    seiten: Collection[int],
    ziel_wurzel: Path,
    *,
    seitentypen: Mapping[int, str],
    neu: bool = False,
    schwaerzungen: Mapping[int, Sequence[Sequence[float]]] | None = None,
) -> list[Path]:
    """Rendert `seiten` nach `ziel_wurzel/s{nnn}.webp`; liefert die geschriebenen Pfade.

    Eine Seite wird nur gerendert, wenn ihre Datei fehlt oder `neu` gesetzt ist (die WebP-Bytes
    sind über Plattformen hinweg nicht als identisch belegt, deshalb gibt es kein stilles
    Neurendern). Seiten des Typs `produktinformationen` verlangen Einträge in `schwaerzungen`
    (Rechtecke `[x0, top, x1, bottom]` in PDF-Punkten); fehlen sie, löst die Funktion
    `BelegbildFehler` aus, bevor ein Bild geschrieben wird.
    """
    schwaerzungen = schwaerzungen or {}
    for seite in sorted(seiten):
        if seitentypen.get(seite) == _PERSONEN_SEITENTYP and not schwaerzungen.get(seite):
            raise BelegbildFehler(
                f"PDF-Seite {seite} ist eine Produktinformationen-Seite mit Personenfeldern; "
                "ohne Schwärzungsrechtecke wird sie nicht gerendert"
            )

    geschrieben: list[Path] = []
    offen = [
        seite for seite in sorted(seiten) if neu or not (ziel_wurzel / bild_name(seite)).exists()
    ]
    if not offen:
        return geschrieben

    ziel_wurzel.mkdir(parents=True, exist_ok=True)
    pdf = pdfium.PdfDocument(str(pdf_pfad))
    try:
        for seite in offen:
            bild = pdf[seite - 1].render(scale=RENDER_MASSSTAB).to_pil()
            rechtecke = schwaerzungen.get(seite, ())
            if rechtecke:
                zeichner = ImageDraw.Draw(bild)
                for x0, top, x1, bottom in rechtecke:
                    zeichner.rectangle(
                        (
                            x0 * RENDER_MASSSTAB,
                            top * RENDER_MASSSTAB,
                            x1 * RENDER_MASSSTAB,
                            bottom * RENDER_MASSSTAB,
                        ),
                        fill=_SCHWAERZUNG_FARBE,
                    )
            pfad = ziel_wurzel / bild_name(seite)
            bild.save(pfad, "WEBP", quality=WEBP_QUALITAET, method=WEBP_METHODE)
            geschrieben.append(pfad)
    finally:
        pdf.close()
    return geschrieben
