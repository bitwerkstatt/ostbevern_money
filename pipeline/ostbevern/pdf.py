"""Liest PDF-Wörter mit Koordinaten aus dem Haushalts-PDF.

Dieses Modul ist die einzige Stelle, die `pdfplumber` importiert.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from types import TracebackType

import pdfplumber

_ZEILEN_TOLERANZ = 2.0


class PdfFehler(ValueError):
    """Wird ausgelöst, wenn eine PDF-Seite nicht existiert oder nicht lesbar ist."""


@dataclass(frozen=True)
class Wort:
    """Ein einzelnes von pdfplumber erkanntes Wort mit Koordinaten und Schriftgröße."""

    text: str
    x0: float
    x1: float
    top: float
    groesse: float


@dataclass(frozen=True)
class Textzeile:
    """Eine Textzeile aus nach `top` gruppierten, nach `x0` sortierten Wörtern."""

    top: float
    woerter: tuple[Wort, ...]

    @property
    def text(self) -> str:
        """Wörter durch je ein Leerzeichen getrennt (für Kopfzeilen mit echten Lücken)."""
        return " ".join(wort.text for wort in self.woerter)

    @property
    def text_ohne_leerzeichen(self) -> str:
        """Wörter ohne Trennzeichen aneinandergereiht (wie pdfplumber Planzeilen liefert)."""
        return "".join(wort.text for wort in self.woerter)

    @property
    def x0(self) -> float:
        return self.woerter[0].x0

    @property
    def groesse(self) -> float:
        return self.woerter[0].groesse


class PdfDokument:
    """Wrapper um pdfplumber.open mit 1-basierten, zeilengruppierten Seitenzugriffen."""

    def __init__(self, pfad: Path) -> None:
        self._pfad = pfad
        self._pdf = pdfplumber.open(pfad)
        self._cache: dict[int, tuple[Textzeile, ...]] = {}

    @classmethod
    def oeffne(cls, pfad: Path) -> PdfDokument:
        """Öffnet das PDF unter `pfad`; Aufrufer sollten dies als Context Manager nutzen."""
        return cls(pfad)

    def __enter__(self) -> PdfDokument:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self._pdf.close()

    @property
    def seitenanzahl(self) -> int:
        return len(self._pdf.pages)

    def zeilen(self, pdf_seite: int) -> tuple[Textzeile, ...]:
        """Liefert die Textzeilen der 1-basierten Seite `pdf_seite`, nach `top` gruppiert."""
        if pdf_seite in self._cache:
            return self._cache[pdf_seite]
        if not (1 <= pdf_seite <= self.seitenanzahl):
            raise PdfFehler(
                f"{self._pfad}: Seite {pdf_seite} liegt außerhalb von 1..{self.seitenanzahl}"
            )
        seite = self._pdf.pages[pdf_seite - 1]
        rohe_woerter = seite.extract_words(extra_attrs=["size"])
        woerter = [
            Wort(text=w["text"], x0=w["x0"], x1=w["x1"], top=w["top"], groesse=w["size"])
            for w in rohe_woerter
        ]

        gruppen: list[list[Wort]] = []
        for wort in sorted(woerter, key=lambda w: w.top):
            if gruppen and abs(wort.top - gruppen[-1][0].top) <= _ZEILEN_TOLERANZ:
                gruppen[-1].append(wort)
            else:
                gruppen.append([wort])

        zeilen = tuple(
            Textzeile(top=gruppe[0].top, woerter=tuple(sorted(gruppe, key=lambda w: w.x0)))
            for gruppe in gruppen
        )
        zeilen = tuple(sorted(zeilen, key=lambda z: z.top))
        self._cache[pdf_seite] = zeilen
        return zeilen
