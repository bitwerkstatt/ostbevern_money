"""Schritt 06: Konsistenzprüfung gegen Anhang B (D-01).

Eine Implementierung, zwei Aufrufer: `06_pruefen.py` und pytest rufen `pruefe_alles`
identisch auf. Dieses Modul liest ausschließlich CSVs, nie das PDF (D-06).
"""

from __future__ import annotations

import os
import tempfile
from dataclasses import dataclass
from pathlib import Path

import polars as pl

from ostbevern.konfiguration import JAHRGAENGE_VERZEICHNIS, lade_jahrgang, lade_sollwerte
from ostbevern.schema import (
    DATEN_WURZEL,
    ERGEBNISPLAN_CSV,
    FINANZPLAN_CSV,
    KONSISTENZ_MD,
    lies_plan_csv,
    zerlege_spaltenkopf,
)
from ostbevern.zeilen import FORMELN, plantyp_fuer

TOLERANZ_EURO = 1

# Satzung § 1-3 (PDF S. 8) als Formel aus Ergebnis-/Finanzplan-Zeilen (GESAMT, Haushaltsjahr):
# Schlüssel -> (Zieldatei, Wertart, Komponenten als (Vorzeichen, Zeile)).
SATZUNG_FORMELN: dict[str, tuple[str, str, tuple[tuple[int, str], ...]]] = {
    "ertraege": ("ergebnisplan", "ansatz", ((1, "10"), (1, "19"))),
    "aufwendungen": ("ergebnisplan", "ansatz", ((1, "17"), (1, "20"))),
    "globaler_minderaufwand": ("ergebnisplan", "ansatz", ((-1, "27"),)),
    "aufwendungen_nach_minderaufwand": (
        "ergebnisplan",
        "ansatz",
        ((1, "17"), (1, "20"), (1, "27")),
    ),
    "einzahlungen_laufende_verwaltung": ("finanzplan", "ansatz", ((1, "09"),)),
    "auszahlungen_laufende_verwaltung": ("finanzplan", "ansatz", ((1, "16"),)),
    "einzahlungen_investitionen": ("finanzplan", "ansatz", ((1, "23"),)),
    "auszahlungen_investitionen": ("finanzplan", "ansatz", ((1, "30"),)),
    "einzahlungen_finanzierung": ("finanzplan", "ansatz", ((1, "33"), (1, "34"))),
    "auszahlungen_finanzierung": ("finanzplan", "ansatz", ((1, "35"), (1, "36"))),
    "kredite_investitionen": ("finanzplan", "ansatz", ((1, "33"),)),
    "verpflichtungsermaechtigungen": ("finanzplan", "ve", ((1, "30"),)),
}


class PruefungsFehler(ValueError):
    """Wird ausgelöst, wenn ein Prüfwert fehlt oder nicht eindeutig bestimmbar ist."""


@dataclass(frozen=True)
class Pruefpunkt:
    """Ein Soll/Ist-Vergleich. `code` ist "" für GESAMT.

    `soll` ist der Referenzwert (PDF-Druck oder Sollwert), `ist` der Pipeline-Wert.
    """

    regel: int
    plan: str
    ebene: str
    code: str
    zeile: str
    jahr: int
    wertart: str
    soll: int
    ist: int
    pdf_seite: int | None

    @property
    def abweichung(self) -> int:
        return self.ist - self.soll


@dataclass(frozen=True)
class Regelergebnis:
    """Ergebnis einer einzelnen Prüfregel."""

    regel: int
    titel: str
    geprueft: int
    abweichungen: tuple[Pruefpunkt, ...]

    @property
    def status(self) -> str:
        if any(abs(punkt.abweichung) > TOLERANZ_EURO for punkt in self.abweichungen):
            return "rot"
        return "grün"


@dataclass(frozen=True)
class Bericht:
    """Gesamtergebnis aller implementierten Prüfregeln für ein Haushaltsjahr."""

    jahr: int
    regeln: tuple[Regelergebnis, ...]

    @property
    def ist_gruen(self) -> bool:
        return all(regel.status == "grün" for regel in self.regeln)


_PlanwerteSchluessel = tuple[str, str, str, int, str]


class Planwerte:
    """Löst Formelketten (FORMELN) für fehlende Zwischenzeilen einer Plan-CSV auf (D-11, Pitfall 1).

    `wert()` liefert den gedruckten Betrag, falls die Zeile existiert; sonst wertet sie die
    Formel aus `FORMELN[plantyp_fuer(datei, ebene)]` rekursiv über `wert()` aus; fehlt auch
    eine Formel, ist der Wert 0 (D-11, echte Leerzeile). Ergebnisse werden memoisiert; ein
    Formelzyklus (sollte nie vorkommen, schützt aber vor einer Endlosrekursion bei einem
    künftigen FORMELN-Tippfehler) bricht mit PruefungsFehler ab.
    """

    def __init__(self, df: pl.DataFrame, *, datei: str) -> None:
        self._datei = datei
        self._werte: dict[_PlanwerteSchluessel, int] = {
            (
                zeile["ebene"],
                zeile["code"] or "",
                zeile["zeile"],
                zeile["jahr"],
                zeile["wertart"],
            ): zeile["betrag"]
            for zeile in df.iter_rows(named=True)
        }
        self._cache: dict[_PlanwerteSchluessel, int] = {}

    def wert(self, ebene: str, code: str, zeile: str, jahr: int, wertart: str) -> int:
        return self._wert((ebene, code, zeile, jahr, wertart), unterwegs=frozenset())

    def _wert(self, schluessel: _PlanwerteSchluessel, *, unterwegs: frozenset) -> int:
        if schluessel in self._cache:
            return self._cache[schluessel]
        if schluessel in self._werte:
            betrag = self._werte[schluessel]
            self._cache[schluessel] = betrag
            return betrag
        if schluessel in unterwegs:
            raise PruefungsFehler(f"Regel 1: Formelzyklus bei {schluessel}")

        ebene, code, zeile, jahr, wertart = schluessel
        plantyp = plantyp_fuer(self._datei, ebene)
        formel = FORMELN.get(plantyp, {}).get(zeile)
        if formel is None:
            betrag = 0
        else:
            naechste_unterwegs = unterwegs | {schluessel}
            betrag = sum(
                vorzeichen
                * self._wert((ebene, code, komponente, jahr, wertart), unterwegs=naechste_unterwegs)
                for vorzeichen, komponente in formel
            )
        self._cache[schluessel] = betrag
        return betrag


def _pruefe_regel1(*, ergebnisplan: pl.DataFrame, finanzplan: pl.DataFrame) -> Regelergebnis:
    geprueft = 0
    abweichungen: list[Pruefpunkt] = []
    for datei, df in (("ergebnisplan", ergebnisplan), ("finanzplan", finanzplan)):
        planwerte = Planwerte(df, datei=datei)
        for zeile in df.iter_rows(named=True):
            plantyp = plantyp_fuer(datei, zeile["ebene"])
            formel = FORMELN.get(plantyp, {}).get(zeile["zeile"])
            if formel is None:
                continue
            code = zeile["code"] or ""
            soll = zeile["betrag"]
            ist = sum(
                vorzeichen
                * planwerte.wert(zeile["ebene"], code, komponente, zeile["jahr"], zeile["wertart"])
                for vorzeichen, komponente in formel
            )
            geprueft += 1
            punkt = Pruefpunkt(
                regel=1,
                plan=plantyp,
                ebene=zeile["ebene"],
                code=code,
                zeile=zeile["zeile"],
                jahr=zeile["jahr"],
                wertart=zeile["wertart"],
                soll=soll,
                ist=ist,
                pdf_seite=zeile["pdf_seite"],
            )
            if abs(punkt.abweichung) > TOLERANZ_EURO:
                abweichungen.append(punkt)
    return Regelergebnis(
        regel=1,
        titel="Regel 1 – Zeilenformeln",
        geprueft=geprueft,
        abweichungen=tuple(abweichungen),
    )


def _pruefe_regel4_b1(
    *, planwerte: Planwerte, sollwerte: dict, spalten: tuple[str, ...]
) -> tuple[int, list[Pruefpunkt]]:
    gesamtergebnisplan = sollwerte["gesamtergebnisplan"]
    jahre = gesamtergebnisplan["jahre"]
    pdf_seite = gesamtergebnisplan.get("pdf_seite")
    spalten_zu_wertart = [zerlege_spaltenkopf(kopf) for kopf in spalten]

    geprueft = 0
    abweichungen: list[Pruefpunkt] = []
    for zeile, sollwerte_je_jahr in sorted(gesamtergebnisplan["zeilen"].items()):
        if len(sollwerte_je_jahr) != len(jahre):
            raise PruefungsFehler(
                f"Regel 4: Zeile {zeile!r} hat {len(sollwerte_je_jahr)} Sollwerte, "
                f"erwartet {len(jahre)}"
            )
        for index, jahreszahl in enumerate(jahre):
            wertart, spalten_jahr = spalten_zu_wertart[index]
            if spalten_jahr != jahreszahl:
                raise PruefungsFehler(
                    f"Regel 4: Spaltenreihenfolge {spalten!r} passt nicht zu "
                    f"gesamtergebnisplan.jahre {jahre!r}"
                )
            soll = sollwerte_je_jahr[index]
            ist = planwerte.wert("GESAMT", "", zeile, jahreszahl, wertart)
            geprueft += 1
            punkt = Pruefpunkt(
                regel=4,
                plan="gesamtergebnisplan",
                ebene="GESAMT",
                code="",
                zeile=zeile,
                jahr=jahreszahl,
                wertart=wertart,
                soll=soll,
                ist=ist,
                pdf_seite=pdf_seite,
            )
            if abs(punkt.abweichung) > TOLERANZ_EURO:
                abweichungen.append(punkt)
    return geprueft, abweichungen


def _pruefe_regel4_b2(
    *, planwerte: Planwerte, sollwerte: dict, haushaltsjahr: int
) -> tuple[int, list[Pruefpunkt]]:
    gesamtfinanzplan = sollwerte["gesamtfinanzplan"]
    pdf_seite = gesamtfinanzplan.get("pdf_seite")

    geprueft = 0
    abweichungen: list[Pruefpunkt] = []
    for wertart in ("ansatz", "ve"):
        for zeile, soll in sorted(gesamtfinanzplan.get(wertart, {}).items()):
            ist = planwerte.wert("GESAMT", "", zeile, haushaltsjahr, wertart)
            geprueft += 1
            punkt = Pruefpunkt(
                regel=4,
                plan="gesamtfinanzplan",
                ebene="GESAMT",
                code="",
                zeile=zeile,
                jahr=haushaltsjahr,
                wertart=wertart,
                soll=soll,
                ist=ist,
                pdf_seite=pdf_seite,
            )
            if abs(punkt.abweichung) > TOLERANZ_EURO:
                abweichungen.append(punkt)
    return geprueft, abweichungen


def _pruefe_regel4_satzung(
    *,
    planwerte_ergebnisplan: Planwerte,
    planwerte_finanzplan: Planwerte,
    sollwerte: dict,
    haushaltsjahr: int,
) -> tuple[int, list[Pruefpunkt]]:
    satzung = sollwerte["satzung"]
    pdf_seite = satzung.get("pdf_seite")
    quellen = {"ergebnisplan": planwerte_ergebnisplan, "finanzplan": planwerte_finanzplan}

    geprueft = 0
    abweichungen: list[Pruefpunkt] = []
    for schluessel, soll in sorted(satzung.items()):
        if schluessel == "pdf_seite":
            continue
        formel = SATZUNG_FORMELN.get(schluessel)
        if formel is None:
            raise PruefungsFehler(f"Regel 4: keine Satzungsformel für Schlüssel {schluessel!r}")
        datei, wertart, komponenten = formel
        planwerte = quellen[datei]
        ist = sum(
            vorzeichen * planwerte.wert("GESAMT", "", zeile, haushaltsjahr, wertart)
            for vorzeichen, zeile in komponenten
        )
        geprueft += 1
        punkt = Pruefpunkt(
            regel=4,
            plan="satzung",
            ebene="GESAMT",
            code="",
            zeile=schluessel,
            jahr=haushaltsjahr,
            wertart=wertart,
            soll=soll,
            ist=ist,
            pdf_seite=pdf_seite,
        )
        if abs(punkt.abweichung) > TOLERANZ_EURO:
            abweichungen.append(punkt)
    return geprueft, abweichungen


def _pruefe_regel4(
    *,
    planwerte_ergebnisplan: Planwerte,
    planwerte_finanzplan: Planwerte,
    sollwerte: dict,
    spalten: tuple[str, ...],
) -> Regelergebnis:
    haushaltsjahr = sollwerte["haushaltsjahr"]

    geprueft_b1, abweichungen_b1 = _pruefe_regel4_b1(
        planwerte=planwerte_ergebnisplan, sollwerte=sollwerte, spalten=spalten
    )
    geprueft_b2, abweichungen_b2 = _pruefe_regel4_b2(
        planwerte=planwerte_finanzplan, sollwerte=sollwerte, haushaltsjahr=haushaltsjahr
    )
    geprueft_satzung, abweichungen_satzung = _pruefe_regel4_satzung(
        planwerte_ergebnisplan=planwerte_ergebnisplan,
        planwerte_finanzplan=planwerte_finanzplan,
        sollwerte=sollwerte,
        haushaltsjahr=haushaltsjahr,
    )

    return Regelergebnis(
        regel=4,
        titel="Regel 4 – Sollwerte (Anhang B, Satzung § 1-3)",
        geprueft=geprueft_b1 + geprueft_b2 + geprueft_satzung,
        abweichungen=tuple(abweichungen_b1 + abweichungen_b2 + abweichungen_satzung),
    )


def pruefe_alles(
    jahr: int,
    *,
    daten_wurzel: Path = DATEN_WURZEL,
    sollwerte_verzeichnis: Path = JAHRGAENGE_VERZEICHNIS,
) -> Bericht:
    """Lädt Jahrgang/Sollwerte und führt alle implementierten Prüfregeln aus (D-01, D-06)."""
    jahrgang = lade_jahrgang(jahr)
    sollwerte = lade_sollwerte(jahr, verzeichnis=sollwerte_verzeichnis)
    ergebnisplan = lies_plan_csv(daten_wurzel / ERGEBNISPLAN_CSV)
    finanzplan = lies_plan_csv(daten_wurzel / FINANZPLAN_CSV)

    regel1 = _pruefe_regel1(ergebnisplan=ergebnisplan, finanzplan=finanzplan)
    regel4 = _pruefe_regel4(
        planwerte_ergebnisplan=Planwerte(ergebnisplan, datei="ergebnisplan"),
        planwerte_finanzplan=Planwerte(finanzplan, datei="finanzplan"),
        sollwerte=sollwerte,
        spalten=jahrgang.spalten["ergebnisplan"],
    )
    return Bericht(jahr=jahr, regeln=(regel1, regel4))


def rendere_konsistenzbericht(bericht: Bericht) -> str:
    """Erzeugt den Markdown-Text von konsistenz.md deterministisch, ohne Zeitstempel (D-03)."""
    zeilen = [
        f"# Konsistenzbericht Haushalt {bericht.jahr}",
        "",
        "Diese Datei wird von `pipeline/06_pruefen.py` und von pytest erzeugt und darf "
        "nicht von Hand bearbeitet werden.",
        "",
        "## Übersicht",
        "",
        "| Regel | Status | Geprüfte Werte | Abweichungen |",
        "| --- | --- | --- | --- |",
    ]
    for regel in bericht.regeln:
        zeilen.append(
            f"| {regel.titel} | {regel.status} | {regel.geprueft} | {len(regel.abweichungen)} |"
        )
    zeilen += ["", "## Abweichungen", ""]

    alle_abweichungen = [(regel, punkt) for regel in bericht.regeln for punkt in regel.abweichungen]
    if not alle_abweichungen:
        zeilen.append("Keine.")
    else:
        zeilen.append(
            "| Regel | Plan | Ebene | Code | Zeile | Jahr | Wertart | Soll | Ist | "
            "Abweichung | PDF-Seite |"
        )
        zeilen.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        for _, punkt in sorted(
            alle_abweichungen,
            key=lambda rp: (
                rp[1].regel,
                rp[1].plan,
                rp[1].ebene,
                rp[1].code,
                rp[1].zeile,
                rp[1].jahr,
                rp[1].wertart,
            ),
        ):
            zeilen.append(
                f"| {punkt.regel} | {punkt.plan} | {punkt.ebene} | {punkt.code} | "
                f"{punkt.zeile} | {punkt.jahr} | {punkt.wertart} | {punkt.soll} | "
                f"{punkt.ist} | {punkt.abweichung} | {punkt.pdf_seite} |"
            )
    zeilen.append("")
    return "\n".join(zeilen)


def schreibe_konsistenzbericht(bericht: Bericht, *, daten_wurzel: Path = DATEN_WURZEL) -> Path:
    """Schreibt konsistenz.md atomar (temporäre Datei + os.replace), UTF-8, LF (PRUEF-09)."""
    pfad = daten_wurzel / KONSISTENZ_MD
    pfad.parent.mkdir(parents=True, exist_ok=True)
    inhalt = rendere_konsistenzbericht(bericht)
    deskriptor, temp_pfad_str = tempfile.mkstemp(
        dir=pfad.parent, prefix=".konsistenz-", suffix=".tmp"
    )
    temp_pfad = Path(temp_pfad_str)
    try:
        with os.fdopen(deskriptor, "w", encoding="utf-8", newline="\n") as datei:
            datei.write(inhalt)
        os.replace(temp_pfad, pfad)
    finally:
        temp_pfad.unlink(missing_ok=True)
    return pfad
