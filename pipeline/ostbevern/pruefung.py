"""Schritt 06: Konsistenzprüfung gegen Anhang B (D-01).

Eine Implementierung, zwei Aufrufer: `06_pruefen.py` und pytest rufen `pruefe_alles`
identisch auf. Dieses Modul liest ausschließlich CSVs, nie das PDF (D-06).
"""

from __future__ import annotations

import os
import tempfile
from collections.abc import Sequence
from dataclasses import dataclass, replace
from pathlib import Path

import polars as pl

from ostbevern.konfiguration import JAHRGAENGE_VERZEICHNIS, Jahrgang, lade_jahrgang, lade_sollwerte
from ostbevern.schema import (
    BEFUNDE_MD,
    DATEN_WURZEL,
    EBENEN,
    ERGEBNISPLAN_CSV,
    FINANZPLAN_CSV,
    HIERARCHIE_CSV,
    INVESTITIONEN_CSV,
    INVESTITIONEN_PB_CSV,
    KONSISTENZ_MD,
    QUERSCHNITTE_CSV,
    SEITEN_CSV,
    VE_FAELLIGKEITEN_CSV,
    WERTARTEN,
    lies_hierarchie_csv,
    lies_investitionen_csv,
    lies_investitionen_pb_csv,
    lies_plan_csv,
    lies_querschnitte_csv,
    lies_seiten_csv,
    lies_ve_faelligkeiten_csv,
    zerlege_spaltenkopf,
)
from ostbevern.zeilen import FORMELN, plantyp_fuer

# Kopfzeile der maschinenlesbaren Schlüsseltabelle in befunde.md (D-02); wird sowohl beim
# Lesen (lies_befunde) als auch beim Schreiben des Konsistenzberichts verwendet, damit eine
# Zeile 1:1 zwischen beiden Dateien kopierbar bleibt.
_SCHLUESSELTABELLE_KOPF = (
    "| regel | plan | ebene | code | zeile | jahr | wertart | abweichung | pdf_seite | "
    "begruendung |"
)

TOLERANZ_EURO = 1

# Regel 3 (Spez. 5.5): nur diese Zeilen des Ergebnisplans werden über die 15 PB summiert und
# gegen den Gesamtergebnisplan geprüft. TP 27/28 (interne Leistungsbeziehungen) und der
# Minderaufwand (GEP 27, TP 30) sind absichtlich ausgenommen; Z. 18 (Ordentliches Ergebnis)
# ist bereits über Regel 1 als Formel aus Z. 10/17 abgesichert.
REGEL3_ZEILEN: tuple[str, ...] = tuple(f"{zeile:02d}" for zeile in range(1, 18)) + ("19", "20")

# Anhang B.3 (Spez. Anhang B.3, fachliche Regel): Sollwertfeld -> Teilergebnisplan-Zeile je PB.
B3_ZEILEN: dict[str, str] = {
    "ordentliche_ertraege": "10",
    "ordentliche_aufwendungen": "17",
    "ergebnis_mit_internen_verrechnungen": "29",
}

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

# Regel 7 (PRUEF-07, D-15): Kennzahl-Schlüssel (querschnitte.csv Spalte `kennzahl`) ->
# (Zieldatei, Wertart, Komponenten als (Vorzeichen, Zeile)). Fachliche Regel, verifiziert
# gegen ergebnisplan.csv: "Ergebnis des Teilhaushaltes" entspricht TP Z. 26
# (Jahresergebnis), NICHT Z. 29 (PG 0102 Ansatz Haushaltsjahr: Z. 26 = -178.200 =
# Querschnitt, Z. 29 = -174.000; Teilfinanzpläne drucken kein Z. 32, daher
# Finanzmittelüberschuss = Z. 17 + Z. 31; TFP Z. 34 = Z. 33 - Z. 35, Saldo Finanzierung).
REGEL7_KENNZAHLEN: dict[str, tuple[str, str, tuple[tuple[int, str], ...]]] = {
    "ordentliche_ertraege": ("ergebnisplan", "ansatz", ((1, "10"),)),
    "ordentliche_aufwendungen": ("ergebnisplan", "ansatz", ((1, "17"),)),
    "ordentliches_ergebnis": ("ergebnisplan", "ansatz", ((1, "18"),)),
    "finanzergebnis": ("ergebnisplan", "ansatz", ((1, "21"),)),
    "ergebnis_laufende_verwaltung": ("ergebnisplan", "ansatz", ((1, "22"),)),
    "ausserordentliches_ergebnis": ("ergebnisplan", "ansatz", ((1, "25"),)),
    "ergebnis_teilhaushalt": ("ergebnisplan", "ansatz", ((1, "26"),)),
    "einzahlungen_laufende_verwaltung": ("finanzplan", "ansatz", ((1, "09"),)),
    "auszahlungen_laufende_verwaltung": ("finanzplan", "ansatz", ((1, "16"),)),
    "saldo_laufende_verwaltung": ("finanzplan", "ansatz", ((1, "17"),)),
    "einzahlungen_investitionen": ("finanzplan", "ansatz", ((1, "23"),)),
    "auszahlungen_investitionen": ("finanzplan", "ansatz", ((1, "30"),)),
    "saldo_investitionen": ("finanzplan", "ansatz", ((1, "31"),)),
    "finanzmittelueberschuss": ("finanzplan", "ansatz", ((1, "17"), (1, "31"))),
    "einzahlungen_finanzierung": ("finanzplan", "ansatz", ((1, "33"),)),
    "auszahlungen_finanzierung": ("finanzplan", "ansatz", ((1, "35"),)),
    "saldo_finanzierung": ("finanzplan", "ansatz", ((1, "34"),)),
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

    @property
    def schluessel(self) -> tuple[int, str, str, str, str, int, str]:
        """Identifiziert den Soll/Ist-Vergleich unabhängig von Soll/Ist/PDF-Seite (D-05)."""
        return (self.regel, self.plan, self.ebene, self.code, self.zeile, self.jahr, self.wertart)


@dataclass(frozen=True)
class Befund:
    """Ein in `befunde.md` dokumentierter, bekannter Abweichungs-Befund (D-02)."""

    regel: int
    plan: str
    ebene: str
    code: str
    zeile: str
    jahr: int
    wertart: str
    abweichung: int
    pdf_seite: int
    begruendung: str

    @property
    def schluessel(self) -> tuple[int, str, str, str, str, int, str]:
        return (self.regel, self.plan, self.ebene, self.code, self.zeile, self.jahr, self.wertart)


@dataclass(frozen=True)
class Abgleich:
    """Ergebnis des Abgleichs von Abweichungen gegen bekannte Befunde (D-04, D-05)."""

    offen: tuple[Pruefpunkt, ...]
    bekannt: tuple[tuple[Pruefpunkt, Befund], ...]
    veraltet: tuple[Befund, ...]


@dataclass(frozen=True)
class Luecke:
    """Struktureller Befund (fehlender oder überzähliger Eintrag), nicht über befunde.md
    abdeckbar (03-03, D-06). Anders als eine Abweichung (Betrag falsch) ist eine Lücke ein
    Eintrag, der nur in einer von zwei Quellen vorkommt — das kann keine Rundungsdifferenz
    sein und darf deshalb nie durch eine Begründung "entschärft" werden."""

    regel: int
    ebene: str
    code: str
    merkmal: str
    pdf_seite: int | None


@dataclass(frozen=True)
class Regelergebnis:
    """Ergebnis einer einzelnen Prüfregel. `abweichungen` sind die offenen (D-04/D-05);
    `luecken` sind strukturelle Befunde (D-06, 03-03), nicht über befunde.md abdeckbar."""

    regel: int
    titel: str
    geprueft: int
    abweichungen: tuple[Pruefpunkt, ...]
    bekannte: tuple[tuple[Pruefpunkt, Befund], ...] = ()
    luecken: tuple[Luecke, ...] = ()

    @property
    def status(self) -> str:
        if (
            any(abs(punkt.abweichung) > TOLERANZ_EURO for punkt in self.abweichungen)
            or self.luecken
        ):
            return "rot"
        return "grün"


@dataclass(frozen=True)
class Bericht:
    """Gesamtergebnis aller implementierten Prüfregeln für ein Haushaltsjahr."""

    jahr: int
    regeln: tuple[Regelergebnis, ...]
    veraltete_befunde: tuple[Befund, ...] = ()
    unbekannte_seiten: tuple[int, ...] = ()

    @property
    def ist_gruen(self) -> bool:
        # unbekannte_seiten fliessen bewusst nicht ein (D-17): eine Seite ohne passendes
        # Muster listet der Bericht, macht den Lauf aber nicht rot.
        return all(regel.status == "grün" for regel in self.regeln) and not self.veraltete_befunde


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


def lies_befunde(pfad: Path) -> tuple[Befund, ...]:
    """Parst die maschinenlesbare Schlüsseltabelle aus befunde.md streng (D-02, D-08).

    Eine leere Schlüsseltabelle (nur Kopf- und Trennzeile) ist gültig. Jede Verletzung
    (fehlende Datei, fehlende Überschrift, abweichende Kopfzeile, falsche Zellenzahl,
    unbekannte Ebene/Wertart, nicht-ganzzahlige Zelle, Abweichung innerhalb der Toleranz,
    leere Begründung) bricht sofort mit Datei und Zeilennummer ab.
    """
    if not pfad.is_file():
        raise PruefungsFehler(f"Befunde-Datei nicht gefunden: {pfad}")
    zeilen = pfad.read_text(encoding="utf-8").splitlines()

    ueberschrift_index = next(
        (i for i, z in enumerate(zeilen) if z.strip() == "## Schlüsseltabelle"), None
    )
    if ueberschrift_index is None:
        raise PruefungsFehler(f"{pfad}: Überschrift '## Schlüsseltabelle' nicht gefunden")

    kopfzeile_index = next(
        (i for i in range(ueberschrift_index + 1, len(zeilen)) if zeilen[i].strip()), None
    )
    if kopfzeile_index is None or zeilen[kopfzeile_index].strip() != _SCHLUESSELTABELLE_KOPF:
        raise PruefungsFehler(
            f"{pfad}: Kopfzeile der Schlüsseltabelle fehlt oder weicht ab "
            f"(erwartet {_SCHLUESSELTABELLE_KOPF!r})"
        )

    befunde: list[Befund] = []
    for index in range(kopfzeile_index + 2, len(zeilen)):
        text = zeilen[index].strip()
        if not text.startswith("|"):
            break
        zeilennummer = index + 1  # 1-basiert für Fehlermeldungen
        zellen = [zelle.strip() for zelle in text.strip("|").split("|")]
        if len(zellen) != 10:
            raise PruefungsFehler(
                f"{pfad}:{zeilennummer}: Schlüsseltabelle-Zeile hat {len(zellen)} Zellen, "
                "erwartet 10"
            )
        (
            regel_text,
            plan,
            ebene,
            code,
            zeile,
            jahr_text,
            wertart,
            abweichung_text,
            pdf_seite_text,
            begruendung,
        ) = zellen

        if ebene not in EBENEN:
            raise PruefungsFehler(f"{pfad}:{zeilennummer}: unbekannte Ebene {ebene!r}")
        if wertart not in WERTARTEN:
            raise PruefungsFehler(f"{pfad}:{zeilennummer}: unbekannte Wertart {wertart!r}")
        if not begruendung:
            raise PruefungsFehler(f"{pfad}:{zeilennummer}: Begründung fehlt")

        try:
            regel = int(regel_text)
            jahr = int(jahr_text)
            abweichung = int(abweichung_text)
            pdf_seite = int(pdf_seite_text)
        except ValueError as fehler:
            raise PruefungsFehler(
                f"{pfad}:{zeilennummer}: Zelle ist keine Ganzzahl ({fehler})"
            ) from fehler

        if abs(abweichung) <= TOLERANZ_EURO:
            raise PruefungsFehler(
                f"{pfad}:{zeilennummer}: Abweichung {abweichung} liegt innerhalb der "
                f"Toleranz von {TOLERANZ_EURO} EUR; ein Befund ist dafür nicht nötig"
            )

        befunde.append(
            Befund(
                regel=regel,
                plan=plan,
                ebene=ebene,
                code=code,
                zeile=zeile,
                jahr=jahr,
                wertart=wertart,
                abweichung=abweichung,
                pdf_seite=pdf_seite,
                begruendung=begruendung,
            )
        )
    return tuple(befunde)


def gleiche_befunde_ab(abweichungen: Sequence[Pruefpunkt], befunde: Sequence[Befund]) -> Abgleich:
    """Ordnet Abweichungen bekannten Befunden zu (D-05) und markiert ungenutzte als veraltet (D-04).

    Ein Befund deckt eine Abweichung ab, wenn beide denselben Schlüssel tragen und sich ihre
    Abweichungsbeträge um höchstens TOLERANZ_EURO unterscheiden. Jeder Befund wird höchstens
    einmal verwendet; ungenutzte Befunde gelten als veraltet.
    """
    befunde_nach_schluessel: dict[tuple, list[Befund]] = {}
    for befund in befunde:
        befunde_nach_schluessel.setdefault(befund.schluessel, []).append(befund)

    offen: list[Pruefpunkt] = []
    bekannt: list[tuple[Pruefpunkt, Befund]] = []
    genutzt: set[int] = set()

    for punkt in abweichungen:
        kandidaten = befunde_nach_schluessel.get(punkt.schluessel, [])
        treffer = next(
            (
                kandidat
                for kandidat in kandidaten
                if id(kandidat) not in genutzt
                and abs(punkt.abweichung - kandidat.abweichung) <= TOLERANZ_EURO
            ),
            None,
        )
        if treffer is not None:
            bekannt.append((punkt, treffer))
            genutzt.add(id(treffer))
        else:
            offen.append(punkt)

    veraltet = tuple(befund for befund in befunde if id(befund) not in genutzt)
    return Abgleich(offen=tuple(offen), bekannt=tuple(bekannt), veraltet=veraltet)


def _wende_befunde_an(
    regelergebnisse: tuple[Regelergebnis, ...], befunde: tuple[Befund, ...]
) -> tuple[tuple[Regelergebnis, ...], tuple[Befund, ...]]:
    """Gleicht alle Abweichungen aller Regeln einmalig gegen die Befunde ab (D-04, D-05)."""
    alle_abweichungen = tuple(punkt for regel in regelergebnisse for punkt in regel.abweichungen)
    abgleich = gleiche_befunde_ab(alle_abweichungen, befunde)

    aktualisiert = tuple(
        replace(
            regel,
            abweichungen=tuple(p for p in abgleich.offen if p.regel == regel.regel),
            bekannte=tuple(paar for paar in abgleich.bekannt if paar[0].regel == regel.regel),
        )
        for regel in regelergebnisse
    )
    return aktualisiert, abgleich.veraltet


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


def _spalten_zu_wertart(spalten: tuple[str, ...]) -> list[tuple[str, int]]:
    """Zerlegt alle Spaltenköpfe eines Plantyps in (wertart, jahr)-Paare (Regel 2/3/4 B.1)."""
    return [zerlege_spaltenkopf(kopf) for kopf in spalten]


def _zeilen_eines_knotens(df: pl.DataFrame, *, ebene: str, code: str) -> set[str]:
    """Die Menge der tatsächlich gedruckten Zeilennummern eines Knotens (Regel 2)."""
    treffer = df.filter((pl.col("ebene") == ebene) & (pl.col("code") == code))
    return set(treffer["zeile"].unique().to_list())


def _pruefe_regel2_ebene(
    *,
    df: pl.DataFrame,
    planwerte: Planwerte,
    hierarchie: pl.DataFrame,
    eltern_ebene: str,
    kind_ebene: str,
    plantyp: str,
    spalten_zu_wertart: list[tuple[str, int]],
) -> tuple[int, list[Pruefpunkt]]:
    """Regel 2 für eine Hierarchiestufe: Σ Kinder == Eltern, je Zeile und Spalte (D-13)."""
    geprueft = 0
    abweichungen: list[Pruefpunkt] = []
    eltern = hierarchie.filter(pl.col("ebene") == eltern_ebene)
    for eltern_zeile in eltern.iter_rows(named=True):
        eltern_code = eltern_zeile["code"]
        kinder_codes = sorted(
            hierarchie.filter(
                (pl.col("ebene") == kind_ebene) & (pl.col("eltern_code") == eltern_code)
            )["code"].to_list()
        )
        eigene_zeilen = _zeilen_eines_knotens(df, ebene=eltern_ebene, code=eltern_code)
        kinder_zeilen: set[str] = set()
        for kind_code in kinder_codes:
            kinder_zeilen |= _zeilen_eines_knotens(df, ebene=kind_ebene, code=kind_code)
        pdf_seite = eltern_zeile["pdf_seite_start"]

        for zeile in sorted(eigene_zeilen | kinder_zeilen):
            for wertart, jahr in spalten_zu_wertart:
                soll = planwerte.wert(eltern_ebene, eltern_code, zeile, jahr, wertart)
                ist = sum(
                    planwerte.wert(kind_ebene, kind_code, zeile, jahr, wertart)
                    for kind_code in kinder_codes
                )
                geprueft += 1
                punkt = Pruefpunkt(
                    regel=2,
                    plan=plantyp,
                    ebene=eltern_ebene,
                    code=eltern_code,
                    zeile=zeile,
                    jahr=jahr,
                    wertart=wertart,
                    soll=soll,
                    ist=ist,
                    pdf_seite=pdf_seite,
                )
                if abs(punkt.abweichung) > TOLERANZ_EURO:
                    abweichungen.append(punkt)
    return geprueft, abweichungen


def _pruefe_regel2(
    *,
    ergebnisplan: pl.DataFrame,
    finanzplan: pl.DataFrame,
    hierarchie: pl.DataFrame,
    jahrgang: Jahrgang,
) -> Regelergebnis:
    """Regel 2 – zweistufig: Σ Produkte == PG (gedruckt und synthetisch) und Σ PG == PB (D-13)."""
    geprueft = 0
    abweichungen: list[Pruefpunkt] = []
    for datei, df, plantyp in (
        ("ergebnisplan", ergebnisplan, "teilergebnisplan"),
        ("finanzplan", finanzplan, "teilfinanzplan"),
    ):
        planwerte = Planwerte(df, datei=datei)
        spalten_zu_wertart = _spalten_zu_wertart(jahrgang.spalten[datei])
        for eltern_ebene, kind_ebene in (("PG", "P"), ("PB", "PG")):
            teil_geprueft, teil_abweichungen = _pruefe_regel2_ebene(
                df=df,
                planwerte=planwerte,
                hierarchie=hierarchie,
                eltern_ebene=eltern_ebene,
                kind_ebene=kind_ebene,
                plantyp=plantyp,
                spalten_zu_wertart=spalten_zu_wertart,
            )
            geprueft += teil_geprueft
            abweichungen += teil_abweichungen
    return Regelergebnis(
        regel=2,
        titel="Regel 2 – Produkte → PG → PB",
        geprueft=geprueft,
        abweichungen=tuple(abweichungen),
    )


def _pruefe_regel3(
    *,
    planwerte: Planwerte,
    hierarchie: pl.DataFrame,
    spalten: tuple[str, ...],
    pdf_seite: int | None,
) -> Regelergebnis:
    """Regel 3 – Σ der 15 PB == Gesamtergebnisplan, Z. 01-17/19/20, ohne TP 27/28 (Spez. 5.5)."""
    spalten_zu_wertart = _spalten_zu_wertart(spalten)
    pb_codes = sorted(hierarchie.filter(pl.col("ebene") == "PB")["code"].unique().to_list())
    plantyp = plantyp_fuer("ergebnisplan", "GESAMT")

    geprueft = 0
    abweichungen: list[Pruefpunkt] = []
    for zeile in REGEL3_ZEILEN:
        for wertart, jahr in spalten_zu_wertart:
            soll = planwerte.wert("GESAMT", "", zeile, jahr, wertart)
            ist = sum(planwerte.wert("PB", pb_code, zeile, jahr, wertart) for pb_code in pb_codes)
            geprueft += 1
            punkt = Pruefpunkt(
                regel=3,
                plan=plantyp,
                ebene="GESAMT",
                code="",
                zeile=zeile,
                jahr=jahr,
                wertart=wertart,
                soll=soll,
                ist=ist,
                pdf_seite=pdf_seite,
            )
            if abs(punkt.abweichung) > TOLERANZ_EURO:
                abweichungen.append(punkt)
    return Regelergebnis(
        regel=3,
        titel="Regel 3 – Produktbereiche → Gesamtergebnisplan",
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


def _pruefe_regel4_b3(
    *,
    planwerte: Planwerte,
    hierarchie: pl.DataFrame,
    sollwerte: dict,
    haushaltsjahr: int,
) -> tuple[int, list[Pruefpunkt]]:
    """Anhang B.3: je PB die 3 B3_ZEILEN-Felder, plus die beiden PB-Summenfelder."""
    teilergebnisplaene_pb = sollwerte["teilergebnisplaene_pb"]
    teilergebnisplaene_pb_summe = sollwerte["teilergebnisplaene_pb_summe"]
    pdf_seite = sollwerte["gesamtergebnisplan"].get("pdf_seite")
    hierarchie_pb_codes = set(hierarchie.filter(pl.col("ebene") == "PB")["code"].to_list())

    geprueft = 0
    abweichungen: list[Pruefpunkt] = []
    for pb_code, felder in sorted(teilergebnisplaene_pb.items()):
        if pb_code not in hierarchie_pb_codes:
            raise PruefungsFehler(
                f"Regel 4 B.3: PB {pb_code!r} aus teilergebnisplaene_pb hat keinen "
                "Teilergebnisplan in hierarchie.csv"
            )
        for feld, zeile in sorted(B3_ZEILEN.items()):
            soll = felder[feld]
            ist = planwerte.wert("PB", pb_code, zeile, haushaltsjahr, "ansatz")
            geprueft += 1
            punkt = Pruefpunkt(
                regel=4,
                plan="teilergebnisplaene_pb",
                ebene="PB",
                code=pb_code,
                zeile=zeile,
                jahr=haushaltsjahr,
                wertart="ansatz",
                soll=soll,
                ist=ist,
                pdf_seite=pdf_seite,
            )
            if abs(punkt.abweichung) > TOLERANZ_EURO:
                abweichungen.append(punkt)

    for feld, zeile in (
        ("ordentliche_ertraege", B3_ZEILEN["ordentliche_ertraege"]),
        ("ordentliche_aufwendungen", B3_ZEILEN["ordentliche_aufwendungen"]),
    ):
        soll = teilergebnisplaene_pb_summe[feld]
        ist = sum(
            planwerte.wert("PB", pb_code, zeile, haushaltsjahr, "ansatz")
            for pb_code in sorted(hierarchie_pb_codes)
        )
        geprueft += 1
        punkt = Pruefpunkt(
            regel=4,
            plan="teilergebnisplaene_pb_summe",
            ebene="PB",
            code="",
            zeile=zeile,
            jahr=haushaltsjahr,
            wertart="ansatz",
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
    hierarchie: pl.DataFrame,
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
    geprueft_b3, abweichungen_b3 = _pruefe_regel4_b3(
        planwerte=planwerte_ergebnisplan,
        hierarchie=hierarchie,
        sollwerte=sollwerte,
        haushaltsjahr=haushaltsjahr,
    )

    return Regelergebnis(
        regel=4,
        titel="Regel 4 – Sollwerte (Anhang B, Satzung § 1-3)",
        geprueft=geprueft_b1 + geprueft_b2 + geprueft_satzung + geprueft_b3,
        abweichungen=tuple(
            abweichungen_b1 + abweichungen_b2 + abweichungen_satzung + abweichungen_b3
        ),
    )


# Regel 6 (PRUEF-06, D-05): Teilfinanzplan-Zeile -> Richtung der Investitionsmaßnahmen.
REGEL6_ZEILEN: tuple[tuple[str, str], ...] = (("23", "einzahlung"), ("30", "auszahlung"))


def _produkt_zu_pb(hierarchie: pl.DataFrame) -> dict[str, str]:
    """Löst jedes Produkt über die Hierarchie (P -> PG -> PB) zu seinem PB-Code auf."""
    pg_zu_pb = {
        zeile["code"]: zeile["eltern_code"]
        for zeile in hierarchie.filter(pl.col("ebene") == "PG").iter_rows(named=True)
    }
    return {
        zeile["code"]: pg_zu_pb[zeile["eltern_code"]]
        for zeile in hierarchie.filter(pl.col("ebene") == "P").iter_rows(named=True)
        if zeile["eltern_code"] in pg_zu_pb
    }


def _pruefe_regel6_pb_gegenprobe(
    *,
    investitionen: pl.DataFrame,
    investitionen_pb: pl.DataFrame,
    hierarchie: pl.DataFrame,
) -> tuple[int, list[Pruefpunkt], list[Luecke]]:
    """Regel 6 (c) – PB-Gegenprobe (PRUEF-06, D-06, 03-03).

    Jedes Produkt wird über die Hierarchie auf seinen PB abgebildet; beide Quellen werden
    je (pb, massnahme_id, konto, jahr, wertart) summiert. Für die Vereinigung der Schlüssel
    beider Quellen ist `soll` die PB-Listen-Summe (0, falls dort nicht vorhanden) und `ist`
    die Produktseiten-Summe (0, falls dort nicht vorhanden) — die PB-Liste ist die
    Kontrollquelle (Spez. 3.8), die Produktseiten sind die zu prüfenden Pipeline-Daten.

    Zusätzlich, feiner als jede Abweichung: die Menge der (pb, massnahme_id)-Paare beider
    Quellen muss übereinstimmen. Eine Maßnahme, die nur in einer Quelle vorkommt, ist eine
    `Luecke` — eine strukturelle Lücke ist keine Betragsabweichung und kann daher nicht
    über befunde.md entschärft werden (D-06).
    """
    produkt_zu_pb = _produkt_zu_pb(hierarchie)
    unbekannt = set(investitionen["produkt"].unique().to_list()) - set(produkt_zu_pb)
    if unbekannt:
        raise PruefungsFehler(
            f"Regel 6: Produkt(e) {sorted(unbekannt)} haben keinen PB über die Hierarchie"
        )
    investitionen_mit_pb = investitionen.with_columns(
        pl.col("produkt").replace_strict(produkt_zu_pb, return_dtype=pl.Utf8).alias("pb")
    )

    schluessel_spalten = ["pb", "massnahme_id", "konto", "jahr", "wertart"]
    ist_gruppiert = investitionen_mit_pb.group_by(schluessel_spalten).agg(
        pl.col("betrag").sum().alias("betrag"), pl.col("pdf_seite").min().alias("pdf_seite")
    )
    soll_gruppiert = investitionen_pb.group_by(schluessel_spalten).agg(
        pl.col("betrag").sum().alias("betrag"), pl.col("pdf_seite").min().alias("pdf_seite")
    )
    ist_dict = {
        (z["pb"], z["massnahme_id"], z["konto"], z["jahr"], z["wertart"]): (
            z["betrag"],
            z["pdf_seite"],
        )
        for z in ist_gruppiert.iter_rows(named=True)
    }
    soll_dict = {
        (z["pb"], z["massnahme_id"], z["konto"], z["jahr"], z["wertart"]): (
            z["betrag"],
            z["pdf_seite"],
        )
        for z in soll_gruppiert.iter_rows(named=True)
    }

    geprueft = 0
    abweichungen: list[Pruefpunkt] = []
    for schluessel in sorted(set(ist_dict) | set(soll_dict)):
        pb, massnahme_id, konto, jahr, wertart = schluessel
        soll, soll_seite = soll_dict.get(schluessel, (0, None))
        ist, ist_seite = ist_dict.get(schluessel, (0, None))
        geprueft += 1
        punkt = Pruefpunkt(
            regel=6,
            plan="investitionen_pb_liste",
            ebene="PB",
            code=pb,
            zeile=f"{massnahme_id}/{konto}",
            jahr=jahr,
            wertart=wertart,
            soll=soll,
            ist=ist,
            pdf_seite=soll_seite if soll_seite is not None else ist_seite,
        )
        if abs(punkt.abweichung) > TOLERANZ_EURO:
            abweichungen.append(punkt)

    def _seite_je_massnahme(df: pl.DataFrame) -> dict[tuple[str, str], int | None]:
        gruppiert = df.group_by(["pb", "massnahme_id"]).agg(
            pl.col("pdf_seite").min().alias("pdf_seite")
        )
        return {
            (z["pb"], z["massnahme_id"]): z["pdf_seite"] for z in gruppiert.iter_rows(named=True)
        }

    massnahmen_pb_liste = set(investitionen_pb.select(["pb", "massnahme_id"]).unique().iter_rows())
    massnahmen_produktseiten = set(
        investitionen_mit_pb.select(["pb", "massnahme_id"]).unique().iter_rows()
    )
    seite_pb_liste = _seite_je_massnahme(investitionen_pb)
    seite_produktseiten = _seite_je_massnahme(investitionen_mit_pb)

    luecken: list[Luecke] = []
    for pb, massnahme_id in sorted(massnahmen_pb_liste - massnahmen_produktseiten):
        luecken.append(
            Luecke(
                regel=6,
                ebene="PB",
                code=pb,
                merkmal=f"Maßnahme {massnahme_id}: nur in der PB-Liste",
                pdf_seite=seite_pb_liste.get((pb, massnahme_id)),
            )
        )
    for pb, massnahme_id in sorted(massnahmen_produktseiten - massnahmen_pb_liste):
        luecken.append(
            Luecke(
                regel=6,
                ebene="PB",
                code=pb,
                merkmal=f"Maßnahme {massnahme_id}: nur auf Produktseiten",
                pdf_seite=seite_produktseiten.get((pb, massnahme_id)),
            )
        )

    return geprueft, abweichungen, luecken


def _pruefe_regel6(
    *,
    investitionen: pl.DataFrame,
    investitionen_pb: pl.DataFrame,
    ve_faelligkeiten: pl.DataFrame,
    planwerte_finanzplan: Planwerte,
    hierarchie: pl.DataFrame,
    jahrgang: Jahrgang,
) -> Regelergebnis:
    """Regel 6 – Investitionsmaßnahmen → Teil-/Gesamtfinanzplan (PRUEF-06, D-05, D-06).

    (a) Je Produkt und Richtung (Z. 23 Einzahlungen / Z. 30 Auszahlungen): Σ der in
    investitionen.csv gedruckten Beträge dieser Richtung gegen den Teilfinanzplan-Wert,
    in allen sieben Spalten von jahrgang.spalten["investitionen"] (Ergebnis, zwei Ansatz-,
    eine VE- und drei Planung-Spalten).
    (b) Dieselbe Prüfung gegen den Gesamtfinanzplan (Σ aller Produkte).
    (c) PB-Gegenprobe (03-03, D-06): investitionen.csv (über die Hierarchie auf PB
    abgebildet) gegen investitionen_pb.csv je (pb, massnahme_id, konto, jahr, wertart);
    eine Maßnahme, die nur in einer der beiden Quellen vorkommt, ist eine Lücke (siehe
    `_pruefe_regel6_pb_gegenprobe`).
    (d) Für jeden (produkt, massnahme_id, konto)-Schlüssel mit einem VE-Wert in
    investitionen.csv oder Zeilen in ve_faelligkeiten.csv: Σ der Fälligkeiten gegen den
    VE-Wert (0, falls keiner gedruckt ist).
    """
    spalten = jahrgang.spalten["investitionen"]
    spalten_zu_wertart = _spalten_zu_wertart(spalten)
    produkt_codes = sorted(hierarchie.filter(pl.col("ebene") == "P")["code"].unique().to_list())

    pdf_seite_je_produkt: dict[str, int] = {
        zeile["code"]: zeile["pdf_seite_start"]
        for zeile in hierarchie.filter(pl.col("ebene") == "P").iter_rows(named=True)
    }
    kleinste_seite_je_produkt = (
        investitionen.group_by("produkt")
        .agg(pl.col("pdf_seite").min().alias("pdf_seite"))
        .to_dict(as_series=False)
    )
    kleinste_seite_je_produkt = dict(
        zip(
            kleinste_seite_je_produkt["produkt"],
            kleinste_seite_je_produkt["pdf_seite"],
            strict=True,
        )
    )

    geprueft = 0
    abweichungen: list[Pruefpunkt] = []

    # (a) je Produkt
    for produkt in produkt_codes:
        investitionen_produkt = investitionen.filter(pl.col("produkt") == produkt)
        pdf_seite = kleinste_seite_je_produkt.get(produkt, pdf_seite_je_produkt.get(produkt))
        for zeile, richtung in REGEL6_ZEILEN:
            ist_je_spalte = investitionen_produkt.filter(pl.col("richtung") == richtung)
            for wertart, jahr in spalten_zu_wertart:
                soll = planwerte_finanzplan.wert("P", produkt, zeile, jahr, wertart)
                ist = (
                    ist_je_spalte.filter((pl.col("jahr") == jahr) & (pl.col("wertart") == wertart))[
                        "betrag"
                    ].sum()
                    or 0
                )
                geprueft += 1
                punkt = Pruefpunkt(
                    regel=6,
                    plan="investitionen_produkt",
                    ebene="P",
                    code=produkt,
                    zeile=zeile,
                    jahr=jahr,
                    wertart=wertart,
                    soll=soll,
                    ist=ist,
                    pdf_seite=pdf_seite,
                )
                if abs(punkt.abweichung) > TOLERANZ_EURO:
                    abweichungen.append(punkt)

    # (b) Gesamt
    gesamtfinanzplan_seite = jahrgang.seitenbereiche["gesamtfinanzplan"].von
    for zeile, richtung in REGEL6_ZEILEN:
        ist_je_spalte = investitionen.filter(pl.col("richtung") == richtung)
        for wertart, jahr in spalten_zu_wertart:
            soll = planwerte_finanzplan.wert("GESAMT", "", zeile, jahr, wertart)
            ist = (
                ist_je_spalte.filter((pl.col("jahr") == jahr) & (pl.col("wertart") == wertart))[
                    "betrag"
                ].sum()
                or 0
            )
            geprueft += 1
            punkt = Pruefpunkt(
                regel=6,
                plan="investitionen_gesamt",
                ebene="GESAMT",
                code="",
                zeile=zeile,
                jahr=jahr,
                wertart=wertart,
                soll=soll,
                ist=ist,
                pdf_seite=gesamtfinanzplan_seite,
            )
            if abs(punkt.abweichung) > TOLERANZ_EURO:
                abweichungen.append(punkt)

    # (c) PB-Gegenprobe (03-03, D-06)
    geprueft_pb, abweichungen_pb, luecken = _pruefe_regel6_pb_gegenprobe(
        investitionen=investitionen, investitionen_pb=investitionen_pb, hierarchie=hierarchie
    )
    geprueft += geprueft_pb
    abweichungen += abweichungen_pb

    # (d) VE-Fälligkeiten
    ve_investitionen = investitionen.filter(pl.col("wertart") == "ve")
    ve_schluessel = set(
        ve_investitionen.select(["produkt", "massnahme_id", "konto"]).unique().iter_rows()
    ) | set(ve_faelligkeiten.select(["produkt", "massnahme_id", "konto"]).unique().iter_rows())
    for produkt, massnahme_id, konto in sorted(ve_schluessel):
        ve_zeile = ve_investitionen.filter(
            (pl.col("produkt") == produkt)
            & (pl.col("massnahme_id") == massnahme_id)
            & (pl.col("konto") == konto)
        )
        soll = ve_zeile["betrag"].sum() or 0
        jahr = ve_zeile["jahr"][0] if ve_zeile.height else jahrgang.haushaltsjahr
        ist = (
            ve_faelligkeiten.filter(
                (pl.col("produkt") == produkt)
                & (pl.col("massnahme_id") == massnahme_id)
                & (pl.col("konto") == konto)
            )["betrag"].sum()
            or 0
        )
        pdf_seite = (
            ve_zeile["pdf_seite"][0]
            if ve_zeile.height
            else kleinste_seite_je_produkt.get(produkt, pdf_seite_je_produkt.get(produkt))
        )
        geprueft += 1
        punkt = Pruefpunkt(
            regel=6,
            plan="ve_faelligkeiten",
            ebene="P",
            code=produkt,
            zeile=f"{massnahme_id}/{konto}",
            jahr=jahr,
            wertart="ve",
            soll=soll,
            ist=ist,
            pdf_seite=pdf_seite,
        )
        if abs(punkt.abweichung) > TOLERANZ_EURO:
            abweichungen.append(punkt)

    return Regelergebnis(
        regel=6,
        titel="Regel 6 – Investitionsmaßnahmen → Teil-/Gesamtfinanzplan",
        geprueft=geprueft,
        abweichungen=tuple(abweichungen),
        luecken=tuple(luecken),
    )


def _pruefe_regel7(
    *,
    querschnitte: pl.DataFrame,
    planwerte_ergebnisplan: Planwerte,
    planwerte_finanzplan: Planwerte,
    haushaltsjahr: int,
) -> Regelergebnis:
    """Regel 7 – Haushaltsquerschnitte → PG-/PB-Teilpläne (PRUEF-07, D-15).

    Vergleicht jeden gedruckten Querschnittswert (CSV-only, `querschnitte.py` liest das
    PDF, dieses Modul nie) mit der über `REGEL7_KENNZAHLEN` hergeleiteten Formelkette aus
    den eigenen PG-Teilplänen (GESAMTSUMME-Zeilen gegen den PB-Teilplan).
    """
    planwerte_je_datei = {
        "ergebnisplan": planwerte_ergebnisplan,
        "finanzplan": planwerte_finanzplan,
    }
    plantyp = "querschnitt"

    geprueft = 0
    abweichungen: list[Pruefpunkt] = []
    for zeile in querschnitte.iter_rows(named=True):
        formel = REGEL7_KENNZAHLEN.get(zeile["kennzahl"])
        if formel is None:
            raise PruefungsFehler(f"Regel 7: keine Zuordnung für Kennzahl {zeile['kennzahl']!r}")
        datei, wertart, komponenten = formel
        planwerte = planwerte_je_datei[datei]
        if zeile["gesamtsumme"]:
            ebene, code = "PB", zeile["pb"]
        else:
            ebene, code = "PG", zeile["pg"]
        ist = sum(
            vorzeichen * planwerte.wert(ebene, code, komponente, haushaltsjahr, wertart)
            for vorzeichen, komponente in komponenten
        )
        soll = zeile["betrag"]
        geprueft += 1
        punkt = Pruefpunkt(
            regel=7,
            plan=f"{plantyp}_{zeile['plan']}",
            ebene=ebene,
            code=code,
            zeile=zeile["kennzahl"],
            jahr=haushaltsjahr,
            wertart=wertart,
            soll=soll,
            ist=ist,
            pdf_seite=zeile["pdf_seite"],
        )
        if abs(punkt.abweichung) > TOLERANZ_EURO:
            abweichungen.append(punkt)
    return Regelergebnis(
        regel=7,
        titel="Regel 7 – Haushaltsquerschnitte → PG-/PB-Teilpläne",
        geprueft=geprueft,
        abweichungen=tuple(abweichungen),
    )


def pruefe_alles(
    jahr: int,
    *,
    daten_wurzel: Path = DATEN_WURZEL,
    sollwerte_verzeichnis: Path = JAHRGAENGE_VERZEICHNIS,
    befunde_pfad: Path | None = None,
) -> Bericht:
    """Lädt Jahrgang/Sollwerte und führt alle implementierten Prüfregeln aus (D-01, D-06).

    `befunde_pfad` ist standardmäßig `daten_wurzel / BEFUNDE_MD`; jede Abweichung wird gegen
    die dort dokumentierten Befunde abgeglichen (D-04, D-05).
    """
    jahrgang = lade_jahrgang(jahr)
    sollwerte = lade_sollwerte(jahr, verzeichnis=sollwerte_verzeichnis)
    ergebnisplan = lies_plan_csv(daten_wurzel / ERGEBNISPLAN_CSV)
    finanzplan = lies_plan_csv(daten_wurzel / FINANZPLAN_CSV)
    hierarchie = lies_hierarchie_csv(daten_wurzel / HIERARCHIE_CSV)
    seiten = lies_seiten_csv(daten_wurzel / SEITEN_CSV)
    querschnitte = lies_querschnitte_csv(daten_wurzel / QUERSCHNITTE_CSV)
    investitionen = lies_investitionen_csv(daten_wurzel / INVESTITIONEN_CSV)
    investitionen_pb = lies_investitionen_pb_csv(daten_wurzel / INVESTITIONEN_PB_CSV)
    ve_faelligkeiten = lies_ve_faelligkeiten_csv(daten_wurzel / VE_FAELLIGKEITEN_CSV)
    pfad_befunde = befunde_pfad if befunde_pfad is not None else daten_wurzel / BEFUNDE_MD
    befunde = lies_befunde(pfad_befunde)

    regel1 = _pruefe_regel1(ergebnisplan=ergebnisplan, finanzplan=finanzplan)
    regel2 = _pruefe_regel2(
        ergebnisplan=ergebnisplan,
        finanzplan=finanzplan,
        hierarchie=hierarchie,
        jahrgang=jahrgang,
    )
    regel3 = _pruefe_regel3(
        planwerte=Planwerte(ergebnisplan, datei="ergebnisplan"),
        hierarchie=hierarchie,
        spalten=jahrgang.spalten["ergebnisplan"],
        pdf_seite=sollwerte["gesamtergebnisplan"].get("pdf_seite"),
    )
    regel4 = _pruefe_regel4(
        planwerte_ergebnisplan=Planwerte(ergebnisplan, datei="ergebnisplan"),
        planwerte_finanzplan=Planwerte(finanzplan, datei="finanzplan"),
        hierarchie=hierarchie,
        sollwerte=sollwerte,
        spalten=jahrgang.spalten["ergebnisplan"],
    )
    regel6 = _pruefe_regel6(
        investitionen=investitionen,
        investitionen_pb=investitionen_pb,
        ve_faelligkeiten=ve_faelligkeiten,
        planwerte_finanzplan=Planwerte(finanzplan, datei="finanzplan"),
        hierarchie=hierarchie,
        jahrgang=jahrgang,
    )
    regel7 = _pruefe_regel7(
        querschnitte=querschnitte,
        planwerte_ergebnisplan=Planwerte(ergebnisplan, datei="ergebnisplan"),
        planwerte_finanzplan=Planwerte(finanzplan, datei="finanzplan"),
        haushaltsjahr=jahrgang.haushaltsjahr,
    )

    regeln, veraltete_befunde = _wende_befunde_an(
        (regel1, regel2, regel3, regel4, regel6, regel7), befunde
    )
    unbekannte_seiten = tuple(
        sorted(seiten.filter(pl.col("typ") == "unbekannt")["pdf_seite"].to_list())
    )
    return Bericht(
        jahr=jahr,
        regeln=regeln,
        veraltete_befunde=veraltete_befunde,
        unbekannte_seiten=unbekannte_seiten,
    )


def _pruefpunkt_sortierschluessel(punkt: Pruefpunkt) -> tuple:
    return punkt.schluessel


def rendere_konsistenzbericht(bericht: Bericht) -> str:
    """Erzeugt den Markdown-Text von konsistenz.md deterministisch, ohne Zeitstempel (D-03)."""
    gesamtstatus = "grün" if bericht.ist_gruen else "rot"
    zeilen = [
        f"# Konsistenzbericht Haushalt {bericht.jahr}",
        "",
        "Diese Datei wird von `pipeline/06_pruefen.py` und von pytest erzeugt und darf "
        "nicht von Hand bearbeitet werden.",
        "",
        f"Gesamtstatus: {gesamtstatus}",
        "",
        "## Übersicht",
        "",
        "| Regel | Status | Geprüfte Werte | Abweichungen | Lücken | Bekannte Befunde |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for regel in bericht.regeln:
        zeilen.append(
            f"| {regel.titel} | {regel.status} | {regel.geprueft} | "
            f"{len(regel.abweichungen)} | {len(regel.luecken)} | {len(regel.bekannte)} |"
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
            alle_abweichungen, key=lambda rp: _pruefpunkt_sortierschluessel(rp[1])
        ):
            zeilen.append(
                f"| {punkt.regel} | {punkt.plan} | {punkt.ebene} | {punkt.code} | "
                f"{punkt.zeile} | {punkt.jahr} | {punkt.wertart} | {punkt.soll} | "
                f"{punkt.ist} | {punkt.abweichung} | {punkt.pdf_seite} |"
            )

    zeilen += ["", "## Lücken", ""]
    alle_luecken = [luecke for regel in bericht.regeln for luecke in regel.luecken]
    if not alle_luecken:
        zeilen.append("Keine.")
    else:
        zeilen.append("| Regel | Ebene | Code | Merkmal | PDF-Seite |")
        zeilen.append("| --- | --- | --- | --- | --- |")
        for luecke in sorted(
            alle_luecken,
            key=lambda luecke: (luecke.regel, luecke.ebene, luecke.code, luecke.merkmal),
        ):
            zeilen.append(
                f"| {luecke.regel} | {luecke.ebene} | {luecke.code} | {luecke.merkmal} | "
                f"{luecke.pdf_seite} |"
            )

    zeilen += ["", "## Bekannte Befunde", ""]
    alle_bekannten = [paar for regel in bericht.regeln for paar in regel.bekannte]
    if not alle_bekannten:
        zeilen.append("Keine.")
    else:
        zeilen.append(_SCHLUESSELTABELLE_KOPF)
        zeilen.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        for punkt, befund in sorted(
            alle_bekannten, key=lambda paar: _pruefpunkt_sortierschluessel(paar[0])
        ):
            zeilen.append(
                f"| {punkt.regel} | {punkt.plan} | {punkt.ebene} | {punkt.code} | "
                f"{punkt.zeile} | {punkt.jahr} | {punkt.wertart} | {punkt.abweichung} | "
                f"{punkt.pdf_seite} | {befund.begruendung} |"
            )

    zeilen += ["", "## Veraltete Befunde", ""]
    if not bericht.veraltete_befunde:
        zeilen.append("Keine.")
    else:
        zeilen.append(_SCHLUESSELTABELLE_KOPF)
        zeilen.append("| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |")
        for befund in sorted(bericht.veraltete_befunde, key=lambda b: b.schluessel):
            zeilen.append(
                f"| {befund.regel} | {befund.plan} | {befund.ebene} | {befund.code} | "
                f"{befund.zeile} | {befund.jahr} | {befund.wertart} | {befund.abweichung} | "
                f"{befund.pdf_seite} | {befund.begruendung} |"
            )

    zeilen += ["", "## Seiten mit typ=unbekannt", ""]
    if bericht.unbekannte_seiten:
        zeilen.append(", ".join(str(seite) for seite in bericht.unbekannte_seiten))
    else:
        zeilen.append("Keine.")

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
