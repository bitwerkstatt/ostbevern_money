"""Rendert Seiten des Haushalts-PDF als WebP-Belegbilder (Phase 7, DATA-04, Spez. 5.6).

Dieses Modul ist die einzige Stelle, die `pypdfium2` und `PIL` importiert. Maßstab (2 px je
PDF-Punkt) und Qualität (60) sind Konstanten aus Spez. 5.6, keine Jahrgangswerte.

Datenschutz: Eine Seite des Typs `produktinformationen` trägt Personenfelder
(Verantwortliche, Sachbearbeitung). Sie wird nur gerendert, wenn für sie Schwärzungsrechtecke
übergeben werden (eine leere Liste zählt nicht) oder der Aufrufer sie ausdrücklich als Seite
ohne Personenfelder freigibt (Fortsetzungsseite); sonst bricht `rendere_seiten` mit
`BelegbildFehler` ab, bevor irgendein Bild geschrieben wird. Die Rechtecke werden schwarz
gefüllt, mit einem Überstand von `SCHWAERZUNG_UEBERSTAND_PX`, damit die verlustbehaftete
WebP-Kompression keine hellen Pixel in das Rechteck selbst trägt.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Collection, Mapping, Sequence
from pathlib import Path

import pypdfium2 as pdfium
from PIL import ImageDraw

# Spez. 5.6: 2 Pixel je PDF-Punkt, WebP-Qualität 60.
RENDER_MASSSTAB = 2
WEBP_QUALITAET = 60
WEBP_METHODE = 6
_SCHWAERZUNG_FARBE = (0, 0, 0)
# Die schwarze Fläche reicht so viele Pixel über das übergebene Rechteck hinaus.
SCHWAERZUNG_UEBERSTAND_PX = 2
_PERSONEN_SEITENTYP = "produktinformationen"


class BelegbildFehler(ValueError):
    """Wird ausgelöst, wenn ein Belegbild nicht (sicher) gerendert werden kann."""


def bild_name(pdf_seite: int) -> str:
    """Dateiname des Belegbilds einer 1-basierten PDF-Seite, z. B. `s062.webp`."""
    if pdf_seite < 1:
        raise BelegbildFehler(f"PDF-Seite {pdf_seite} ist keine 1-basierte Seitennummer")
    return f"s{pdf_seite:03d}.webp"


def schwaerzung_fingerprint(rechtecke: Sequence[Sequence[float]]) -> str:
    """Kurzer Hash der Schwärzungsrechtecke einer Seite (Rechtecke auf 2 Dezimalstellen gerundet).

    Er hängt nur von Zahlen ab, nicht von der Plattform; eine leere Liste ergibt einen festen Wert.
    """
    normiert = sorted([round(float(wert), 2) for wert in rechteck] for rechteck in rechtecke)
    return hashlib.sha256(json.dumps(normiert).encode("utf-8")).hexdigest()[:16]


def _lies_fingerprints(pfad: Path | None) -> dict[str, str]:
    if pfad is None or not pfad.exists():
        return {}
    try:
        daten = json.loads(pfad.read_text(encoding="utf-8"))
    except (OSError, ValueError) as fehler:
        raise BelegbildFehler(
            f"{pfad.name}: nicht lesbar ({fehler}); aus Git wiederherstellen"
        ) from fehler
    if not isinstance(daten, dict) or not all(
        str(seite).isdecimal() and isinstance(wert, str) for seite, wert in daten.items()
    ):
        raise BelegbildFehler(f"{pfad.name}: erwartet ein JSON-Objekt Seite -> Fingerprint-String")
    return dict(daten)


def _schreibe_fingerprints(pfad: Path, fingerprints: Mapping[str, str]) -> None:
    inhalt = json.dumps(dict(sorted(fingerprints.items(), key=lambda e: int(e[0]))), indent=2)
    if pfad.exists() and pfad.read_text(encoding="utf-8") == inhalt + "\n":
        return
    pfad.parent.mkdir(parents=True, exist_ok=True)
    temp = pfad.with_name(pfad.name + ".tmp")
    try:
        temp.write_text(inhalt + "\n", encoding="utf-8")
        temp.replace(pfad)
    finally:
        temp.unlink(missing_ok=True)


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
    ohne_personenfelder: Collection[int] = (),
    fingerprint_pfad: Path | None = None,
) -> list[Path]:
    """Rendert `seiten` nach `ziel_wurzel/s{nnn}.webp`; liefert die geschriebenen Pfade.

    Eine Seite wird nur gerendert, wenn ihre Datei fehlt, `neu` gesetzt ist oder (mit
    `fingerprint_pfad`) sich ihre Schwärzungsrechtecke gegenüber dem dort gespeicherten
    Fingerprint geändert haben (die WebP-Bytes sind über Plattformen hinweg nicht als identisch
    belegt, deshalb gibt es sonst kein stilles Neurendern). Für ein vorhandenes Bild ohne
    gespeicherten Fingerprint wird der aktuelle Fingerprint übernommen, ohne neu zu rendern.
    Seiten des Typs `produktinformationen` verlangen mindestens ein Rechteck in
    `schwaerzungen` (Rechtecke `[x0, top, x1, bottom]` in PDF-Punkten) oder einen Eintrag in
    `ohne_personenfelder` (Seiten, für die der Aufrufer geprüft hat, dass sie kein Personenfeld
    zeigen); sonst löst die Funktion `BelegbildFehler` aus, bevor ein Bild geschrieben wird.
    """
    schwaerzungen = schwaerzungen or {}
    for seite in sorted(seiten):
        if (
            seitentypen.get(seite) == _PERSONEN_SEITENTYP
            and not schwaerzungen.get(seite)
            and seite not in ohne_personenfelder
        ):
            raise BelegbildFehler(
                f"PDF-Seite {seite} ist eine Produktinformationen-Seite mit Personenfeldern; "
                "ohne Schwärzungsrechtecke wird sie nicht gerendert"
            )

    geschrieben: list[Path] = []
    gespeichert = _lies_fingerprints(fingerprint_pfad)
    aktuell = {
        str(seite): schwaerzung_fingerprint(schwaerzungen.get(seite, ()))
        for seite in sorted(seiten)
    }
    offen = [
        seite
        for seite in sorted(seiten)
        if neu
        or not (ziel_wurzel / bild_name(seite)).exists()
        or gespeichert.get(str(seite), aktuell[str(seite)]) != aktuell[str(seite)]
    ]
    # Fingerprints der nicht angefragten Seiten bleiben erhalten; neu gerenderte Seiten bekommen
    # ihren Fingerprint erst nach erfolgreichem Schreiben (ein Abbruch lässt den alten stehen).
    vorab = {**gespeichert, **{k: f for k, f in aktuell.items() if k not in gespeichert}}
    if not offen:
        if fingerprint_pfad is not None:
            _schreibe_fingerprints(fingerprint_pfad, vorab)
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
                            x0 * RENDER_MASSSTAB - SCHWAERZUNG_UEBERSTAND_PX,
                            top * RENDER_MASSSTAB - SCHWAERZUNG_UEBERSTAND_PX,
                            x1 * RENDER_MASSSTAB + SCHWAERZUNG_UEBERSTAND_PX,
                            bottom * RENDER_MASSSTAB + SCHWAERZUNG_UEBERSTAND_PX,
                        ),
                        fill=_SCHWAERZUNG_FARBE,
                    )
            pfad = ziel_wurzel / bild_name(seite)
            # Atomar schreiben: Ein Abbruch mitten im Schreiben hinterlässt nie eine abgeschnittene
            # .webp unter dem Zielnamen (sie würde wegen `exists()` nie erneuert).
            temp = pfad.with_name(pfad.name + ".tmp")
            try:
                bild.save(temp, "WEBP", quality=WEBP_QUALITAET, method=WEBP_METHODE)
                temp.replace(pfad)
            finally:
                temp.unlink(missing_ok=True)
            geschrieben.append(pfad)
    finally:
        pdf.close()
    if fingerprint_pfad is not None:
        _schreibe_fingerprints(
            fingerprint_pfad, {**vorab, **{str(seite): aktuell[str(seite)] for seite in offen}}
        )
    return geschrieben
