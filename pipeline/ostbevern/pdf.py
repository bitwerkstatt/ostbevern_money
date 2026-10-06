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
    """Ein einzelnes von pdfplumber erkanntes Wort mit Koordinaten und Schriftgröße.

    `fett` (Phase 3, D-10) ist nur bei der feinen Extraktion (`zeilen_fein`) gesetzt,
    wenn der Fontname "Bold" enthält; bei `zeilen()` ist er immer False (letztes Feld,
    damit bestehende positionale Konstruktionen gültig bleiben).
    """

    text: str
    x0: float
    x1: float
    top: float
    groesse: float
    fett: bool = False


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


@dataclass(frozen=True)
class WortRahmen:
    """Ein Wort mit vollem Rahmen (`x0`, `x1`, `top`, `bottom`) in PDF-Punkten (Phase 7).

    Ursprung oben links wie bei pdfplumber; gedacht für Quellenbelege (Zeilenrechtecke).
    """

    text: str
    x0: float
    x1: float
    top: float
    bottom: float


@dataclass(frozen=True)
class RahmenZeile:
    """Eine Textzeile aus `WortRahmen`, nach `top` gruppiert und nach `x0` sortiert."""

    top: float
    bottom: float
    woerter: tuple[WortRahmen, ...]

    @property
    def text(self) -> str:
        """Wörter durch je ein Leerzeichen getrennt."""
        return " ".join(wort.text for wort in self.woerter)


class PdfDokument:
    """Wrapper um pdfplumber.open mit 1-basierten, zeilengruppierten Seitenzugriffen."""

    def __init__(self, pfad: Path) -> None:
        self._pfad = pfad
        self._pdf = pdfplumber.open(pfad)
        self._cache: dict[int, tuple[Textzeile, ...]] = {}
        self._cache_fein: dict[int, tuple[Textzeile, ...]] = {}
        self._cache_rahmen: dict[tuple[int, bool], tuple[RahmenZeile, ...]] = {}

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

    def _pruefe_seite(self, pdf_seite: int) -> None:
        if not (1 <= pdf_seite <= self.seitenanzahl):
            raise PdfFehler(
                f"{self._pfad}: Seite {pdf_seite} liegt außerhalb von 1..{self.seitenanzahl}"
            )

    @staticmethod
    def _gruppiere_zeilen(woerter: list[Wort]) -> tuple[Textzeile, ...]:
        """Gruppiert Wörter nach `top` (Toleranz `_ZEILEN_TOLERANZ`), sortiert jede Gruppe
        nach `x0` und die Zeilen selbst nach `top` (gemeinsame Logik für `zeilen`/`zeilen_fein`)."""
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
        return tuple(sorted(zeilen, key=lambda z: z.top))

    def zeilen(self, pdf_seite: int) -> tuple[Textzeile, ...]:
        """Liefert die Textzeilen der 1-basierten Seite `pdf_seite`, nach `top` gruppiert.

        Nutzt `extract_words(extra_attrs=["size"])` (kein `x_tolerance`, kein `fontname`);
        dieses Verhalten bleibt byte-für-byte gleich, unabhängig von `zeilen_fein` (Phase 3).
        """
        if pdf_seite in self._cache:
            return self._cache[pdf_seite]
        self._pruefe_seite(pdf_seite)
        seite = self._pdf.pages[pdf_seite - 1]
        rohe_woerter = seite.extract_words(extra_attrs=["size"])
        woerter = [
            Wort(text=w["text"], x0=w["x0"], x1=w["x1"], top=w["top"], groesse=w["size"])
            for w in rohe_woerter
        ]
        zeilen = self._gruppiere_zeilen(woerter)
        self._cache[pdf_seite] = zeilen
        return zeilen

    def zeilen_fein(self, pdf_seite: int) -> tuple[Textzeile, ...]:
        """Liefert die Textzeilen von `pdf_seite` mit feiner Worttrennung (Phase 3, D-10).

        Nutzt `extract_words(x_tolerance=1, extra_attrs=["size", "fontname"])`: trennt eng
        stehende Wörter (Freitext, Namen, Investitionsmaßnahmen-Tabellen) deutlich feiner
        als `zeilen()` und setzt `Wort.fett`, wenn der Fontname "Bold" enthält. Eigener
        Cache; `zeilen()` bleibt davon unberührt (fordert kein `fontname` an).
        """
        if pdf_seite in self._cache_fein:
            return self._cache_fein[pdf_seite]
        self._pruefe_seite(pdf_seite)
        seite = self._pdf.pages[pdf_seite - 1]
        rohe_woerter = seite.extract_words(x_tolerance=1, extra_attrs=["size", "fontname"])
        woerter = [
            Wort(
                text=w["text"],
                x0=w["x0"],
                x1=w["x1"],
                top=w["top"],
                groesse=w["size"],
                fett="Bold" in w["fontname"],
            )
            for w in rohe_woerter
        ]
        zeilen = self._gruppiere_zeilen(woerter)
        self._cache_fein[pdf_seite] = zeilen
        return zeilen

    def zeilen_mit_rahmen(self, pdf_seite: int, *, fein: bool = False) -> tuple[RahmenZeile, ...]:
        """Liefert die Textzeilen von `pdf_seite` mit vollem Wortrahmen (Phase 7, Quellenbelege).

        Dieselben `extract_words`-Argumente wie `zeilen()` (`fein=False`) bzw. `zeilen_fein()`
        (`fein=True`), dazu `bottom`; gruppiert nach `top` mit `_ZEILEN_TOLERANZ`. Eigener
        Cache je (Seite, fein); `zeilen()` und `zeilen_fein()` bleiben unberührt.
        """
        schluessel = (pdf_seite, fein)
        if schluessel in self._cache_rahmen:
            return self._cache_rahmen[schluessel]
        self._pruefe_seite(pdf_seite)
        seite = self._pdf.pages[pdf_seite - 1]
        if fein:
            rohe_woerter = seite.extract_words(x_tolerance=1, extra_attrs=["size", "fontname"])
        else:
            rohe_woerter = seite.extract_words(extra_attrs=["size"])
        woerter = sorted(
            (
                WortRahmen(text=w["text"], x0=w["x0"], x1=w["x1"], top=w["top"], bottom=w["bottom"])
                for w in rohe_woerter
            ),
            key=lambda w: w.top,
        )
        gruppen: list[list[WortRahmen]] = []
        for wort in woerter:
            if gruppen and abs(wort.top - gruppen[-1][0].top) <= _ZEILEN_TOLERANZ:
                gruppen[-1].append(wort)
            else:
                gruppen.append([wort])
        zeilen = tuple(
            RahmenZeile(
                top=min(w.top for w in gruppe),
                bottom=max(w.bottom for w in gruppe),
                woerter=tuple(sorted(gruppe, key=lambda w: w.x0)),
            )
            for gruppe in gruppen
        )
        ergebnis = tuple(sorted(zeilen, key=lambda z: z.top))
        self._cache_rahmen[schluessel] = ergebnis
        return ergebnis

    def seitenmass(self, pdf_seite: int) -> tuple[float, float]:
        """Liefert (Breite, Höhe) der Seite in PDF-Punkten, auf zwei Dezimalstellen gerundet."""
        self._pruefe_seite(pdf_seite)
        seite = self._pdf.pages[pdf_seite - 1]
        return round(float(seite.width), 2), round(float(seite.height), 2)
