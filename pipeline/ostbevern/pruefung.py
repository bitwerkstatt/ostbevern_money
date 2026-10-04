"""Schritt 06: Konsistenzprüfung gegen Anhang B (D-01).

Eine Implementierung, zwei Aufrufer: `06_pruefen.py` und pytest rufen `pruefe_alles`
identisch auf. Dieses Modul liest ausschließlich generierte Dateien unter `daten/`
(CSVs und, für Regel 8, `produkte.json`), nie das PDF (D-06).
"""

from __future__ import annotations

import os
import tempfile
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from pathlib import Path

import polars as pl

from ostbevern.konfiguration import (
    JAHRGAENGE_VERZEICHNIS,
    Jahrgang,
    lade_jahrgang,
    lade_sollwerte,
    layout_text,
)
from ostbevern.manuell import (
    investitionskredite_ende,
    lies_meta_json,
    pro_kopf_euro,
    schuldenstand_euro,
)
from ostbevern.schema import (
    BEFUNDE_MD,
    DATEN_WURZEL,
    EBENEN,
    EIGENKAPITAL_CSV,
    ERGEBNISPLAN_CSV,
    FINANZPLAN_CSV,
    HIERARCHIE_CSV,
    INVESTITIONEN_CSV,
    INVESTITIONEN_PB_CSV,
    KITA_ZUSCHUESSE_CSV,
    KONSISTENZ_MD,
    META_JSON,
    PRODUKTE_JSON,
    QUERSCHNITTE_CSV,
    SEITEN_CSV,
    STELLENPLAN_CSV,
    STEUERARTEN_CSV,
    TRANSFERAUFWENDUNGEN_CSV,
    VE_FAELLIGKEITEN_CSV,
    VE_UEBERSICHT_CSV,
    VERBINDLICHKEITEN_CSV,
    WEITERE_VORBERICHTSTABELLEN_CSV,
    WERTARTEN,
    ZUWENDUNGEN_CSV,
    lies_eigenkapital_csv,
    lies_hierarchie_csv,
    lies_investitionen_csv,
    lies_investitionen_pb_csv,
    lies_plan_csv,
    lies_produkte_json,
    lies_querschnitte_csv,
    lies_seiten_csv,
    lies_stellenplan_csv,
    lies_ve_faelligkeiten_csv,
    lies_ve_uebersicht_csv,
    lies_vorbericht_csv,
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

# Toleranz je Regel (Phase 4, D-14, D-20, Anhang B.6): Regel 9 (Eckwerte) und Regel 10
# (Stellenübersicht → Teil A/B, Hundertstel) sind exakt (0 Toleranz), jede andere Regel
# behält die strenge TOLERANZ_EURO = 1 €. `toleranz_fuer` ist die einzige Stelle, die
# diese Zuordnung kennt — Regelergebnis.status, lies_befunde und gleiche_befunde_ab
# lesen sie, statt TOLERANZ_EURO weiterhin hart zu verdrahten.
TOLERANZ_JE_REGEL: Mapping[int, int] = {9: 0, 10: 0}


def toleranz_fuer(regel: int) -> int:
    """Liefert die Toleranz (in Euro) einer Regel; Standard ist TOLERANZ_EURO."""
    return TOLERANZ_JE_REGEL.get(regel, TOLERANZ_EURO)


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
        toleranz = toleranz_fuer(self.regel)
        if any(abs(punkt.abweichung) > toleranz for punkt in self.abweichungen) or self.luecken:
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

        toleranz = toleranz_fuer(regel)
        if abs(abweichung) <= toleranz:
            raise PruefungsFehler(
                f"{pfad}:{zeilennummer}: Abweichung {abweichung} liegt innerhalb der "
                f"Toleranz von {toleranz} EUR (Regel {regel}); ein Befund ist dafür nicht nötig"
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
    Abweichungsbeträge um höchstens `toleranz_fuer(punkt.regel)` unterscheiden (Regel 9 ist
    exakt, jede andere Regel behält die strenge TOLERANZ_EURO = 1 €). Jeder Befund wird
    höchstens einmal verwendet; ungenutzte Befunde gelten als veraltet.
    """
    befunde_nach_schluessel: dict[tuple, list[Befund]] = {}
    for befund in befunde:
        befunde_nach_schluessel.setdefault(befund.schluessel, []).append(befund)

    offen: list[Pruefpunkt] = []
    bekannt: list[tuple[Pruefpunkt, Befund]] = []
    genutzt: set[int] = set()

    for punkt in abweichungen:
        kandidaten = befunde_nach_schluessel.get(punkt.schluessel, [])
        toleranz = toleranz_fuer(punkt.regel)
        treffer = next(
            (
                kandidat
                for kandidat in kandidaten
                if id(kandidat) not in genutzt
                and abs(punkt.abweichung - kandidat.abweichung) <= toleranz
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


def _pruefe_regel4_b4(
    *, steuerarten: pl.DataFrame, sollwerte: dict
) -> tuple[int, list[Pruefpunkt]]:
    """Anhang B.4 (unabhängige zweite Abschrift, Phase 4): je Posten und Jahr gegen
    daten/manuell/steuerarten.csv (PRUEF-05). Übersprungen, wenn die Sollwertdatei keine
    [anhang_b4_steuerarten]-Tabelle hat (anderer Jahrgang)."""
    anhang_b4 = sollwerte.get("anhang_b4_steuerarten")
    if not anhang_b4:
        return 0, []
    jahre = anhang_b4["jahre"]
    pdf_seite = anhang_b4["pdf_seite"]
    werte_teur = anhang_b4["werte_teur"]

    csv_posten = set(steuerarten["posten"].unique().to_list())
    sollwert_posten = set(werte_teur)
    if csv_posten != sollwert_posten:
        raise PruefungsFehler(
            f"Regel 4 B.4: Posten-Mengen weichen ab (CSV: {sorted(csv_posten)}, "
            f"Anhang B.4: {sorted(sollwert_posten)})"
        )

    geprueft = 0
    abweichungen: list[Pruefpunkt] = []
    for posten, soll_werte in sorted(werte_teur.items()):
        for index, jahr in enumerate(jahre):
            zeile = steuerarten.filter((pl.col("posten") == posten) & (pl.col("jahr") == jahr))
            if zeile.height != 1:
                raise PruefungsFehler(
                    f"Regel 4 B.4: Posten {posten!r} hat {zeile.height} Zeilen für Jahr "
                    f"{jahr}, erwartet genau 1"
                )
            row = zeile.row(0, named=True)
            geprueft += 1
            punkt = Pruefpunkt(
                regel=4,
                plan="anhang_b4",
                ebene="GESAMT",
                code="",
                zeile=posten,
                jahr=jahr,
                wertart=row["wertart"],
                soll=soll_werte[index] * 1000,
                ist=row["betrag_teur"] * 1000,
                pdf_seite=pdf_seite,
            )
            if abs(punkt.abweichung) > TOLERANZ_EURO:
                abweichungen.append(punkt)
    return geprueft, abweichungen


def _pruefe_regel4_b5(
    *, transferaufwendungen: pl.DataFrame, sollwerte: dict
) -> tuple[int, list[Pruefpunkt]]:
    """Anhang B.5 (unabhängige zweite Abschrift, Phase 4): je Posten des Haushaltsjahrs
    gegen daten/manuell/transferaufwendungen.csv (PRUEF-05). Übersprungen, wenn die
    Sollwertdatei keine [anhang_b5_transferaufwendungen]-Tabelle hat (anderer Jahrgang)."""
    anhang_b5 = sollwerte.get("anhang_b5_transferaufwendungen")
    if not anhang_b5:
        return 0, []
    jahr = anhang_b5["jahr"]
    pdf_seite = anhang_b5["pdf_seite"]
    werte_teur = anhang_b5["werte_teur"]

    jahr_df = transferaufwendungen.filter(pl.col("jahr") == jahr)
    csv_posten = set(jahr_df["posten"].unique().to_list())
    sollwert_posten = set(werte_teur)
    if csv_posten != sollwert_posten:
        raise PruefungsFehler(
            f"Regel 4 B.5: Posten-Mengen weichen ab (CSV: {sorted(csv_posten)}, "
            f"Anhang B.5: {sorted(sollwert_posten)})"
        )

    geprueft = 0
    abweichungen: list[Pruefpunkt] = []
    for posten, soll_teur in sorted(werte_teur.items()):
        zeile = jahr_df.filter(pl.col("posten") == posten)
        if zeile.height != 1:
            raise PruefungsFehler(
                f"Regel 4 B.5: Posten {posten!r} hat {zeile.height} Zeilen für Jahr "
                f"{jahr}, erwartet genau 1"
            )
        row = zeile.row(0, named=True)
        geprueft += 1
        punkt = Pruefpunkt(
            regel=4,
            plan="anhang_b5",
            ebene="GESAMT",
            code="",
            zeile=posten,
            jahr=jahr,
            wertart=row["wertart"],
            soll=soll_teur * 1000,
            ist=row["betrag_teur"] * 1000,
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
    steuerarten: pl.DataFrame,
    transferaufwendungen: pl.DataFrame,
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
    geprueft_b4, abweichungen_b4 = _pruefe_regel4_b4(steuerarten=steuerarten, sollwerte=sollwerte)
    geprueft_b5, abweichungen_b5 = _pruefe_regel4_b5(
        transferaufwendungen=transferaufwendungen, sollwerte=sollwerte
    )

    return Regelergebnis(
        regel=4,
        titel="Regel 4 – Sollwerte (Anhang B, Satzung § 1-3)",
        geprueft=(
            geprueft_b1 + geprueft_b2 + geprueft_satzung + geprueft_b3 + geprueft_b4 + geprueft_b5
        ),
        abweichungen=tuple(
            abweichungen_b1
            + abweichungen_b2
            + abweichungen_satzung
            + abweichungen_b3
            + abweichungen_b4
            + abweichungen_b5
        ),
    )


# Regel 5 (PRUEF-05, D-05 bis D-07): manuelle Vorberichtstabelle (schema.py-Tabellenname,
# z. B. "steuerarten") -> Gesamtergebnisplan-Zeile, gegen die die gedruckte Gesamtzeile der
# Tabelle in Stufe (b) geprüft wird (fachliche Regel, nicht jede Tabelle hat eine GEP-Zeile;
# kita_zuschuesse hat bewusst keine — sie wird stattdessen gegen einen Transferaufwendungen-
# Posten geprüft, siehe REGEL5_KITA_POSTEN).
REGEL5_GEP_ZEILEN: dict[str, str] = {
    "steuerarten": "01",
    "zuwendungen": "02",
    "transferaufwendungen": "15",
    "leistungsentgelte": "04",
    "kostenerstattungen": "06",
    "personal": "11",
    "sachaufwand": "13",
    "sonstige_aufwendungen": "16",
    "sonstige_ertraege": "07",
}
# weitere_vorberichtstabellen.csv (D-08, MANU-05): die Tabellenmenge dieser Datei muss
# exakt dieser Menge entsprechen; eine fehlende oder zusätzliche Tabelle bricht mit
# PruefungsFehler ab. D-08 (Phase 4) war eine abgeschlossene Liste von fünf Tabellen;
# Phase 5 D-04 ergänzt bewusst die sechste, 2.1.7 Sonstige ordentliche Erträge (EINN-04).
# Jede weitere Tabelle braucht wieder einen eigenen Review-Beschluss.
WEITERE_VORBERICHTSTABELLEN: tuple[str, ...] = (
    "leistungsentgelte",
    "kostenerstattungen",
    "personal",
    "sachaufwand",
    "sonstige_aufwendungen",
    "sonstige_ertraege",
)
# Stufe (b) vergleicht die gedruckte, nur in T€ geführte Gesamtzeile (×1000) gegen die
# eurogenaue GEP-Zeile; eine eigene, gröbere Toleranz als TOLERANZ_EURO (Stufe a bleibt
# bei der strengen 1-€-Toleranz, da dort beide Seiten aus derselben Tabelle stammen).
REGEL5_TOLERANZ_GEP_EURO = 1000
# Weitergabe an Kreis und Land (D-01, Spez. 3.4): TP <produkt> Z. 15 besteht ausschließlich
# aus diesen drei Transferaufwendungen-Posten (Posten-Schlüssel unserer eigenen CSV, keine
# GEP-/TP-Zeile — fachliche Regel, Produktcode kommt aus [layout.weitergabe_kreis_land]).
WEITERGABE_POSTEN: tuple[str, ...] = (
    "kreisumlage",
    "gewerbesteuerumlage",
    "krankenhausinvestitionsumlage",
)
# kita_zuschuesse (D-07): Posten in transferaufwendungen.csv, gegen den die Kita-Gesamtzeile
# desselben Jahres geprüft wird.
REGEL5_KITA_POSTEN = "zuschuesse_kindertageseinrichtungen"


def _pruefe_regel5_kita_gegen_transfer(
    *, kita_df: pl.DataFrame, transfer_df: pl.DataFrame
) -> tuple[int, list[Pruefpunkt]]:
    """Kita-Gesamtzeile je Jahr == Transferaufwendungen-Posten REGEL5_KITA_POSTEN desselben
    Jahres (D-07). Ein fehlender Posten oder ein fehlendes Jahr auf der Transfer-Seite ist
    strukturell (kein Rundungsfehler) und bricht mit PruefungsFehler ab."""
    transfer_posten_df = transfer_df.filter(pl.col("posten") == REGEL5_KITA_POSTEN)
    if transfer_posten_df.height == 0:
        raise PruefungsFehler(
            f"Regel 5: Posten {REGEL5_KITA_POSTEN!r} fehlt in transferaufwendungen.csv"
        )
    transfer_nach_jahr = {
        zeile["jahr"]: zeile for zeile in transfer_posten_df.iter_rows(named=True)
    }

    geprueft = 0
    abweichungen: list[Pruefpunkt] = []
    for jahr in sorted(kita_df.filter(pl.col("ist_gesamt"))["jahr"].unique().to_list()):
        kita_gesamt = kita_df.filter(pl.col("ist_gesamt") & (pl.col("jahr") == jahr)).row(
            0, named=True
        )
        transfer_zeile = transfer_nach_jahr.get(jahr)
        if transfer_zeile is None:
            raise PruefungsFehler(
                f"Regel 5: transferaufwendungen.csv hat keinen Posten "
                f"{REGEL5_KITA_POSTEN!r} für Jahr {jahr}"
            )
        geprueft += 1
        punkt = Pruefpunkt(
            regel=5,
            plan="vorbericht_kita_zuschuesse",
            ebene="GESAMT",
            code="",
            zeile="transfer_kita",
            jahr=jahr,
            wertart=kita_gesamt["wertart"],
            soll=transfer_zeile["betrag_teur"] * 1000,
            ist=kita_gesamt["betrag_teur"] * 1000,
            pdf_seite=kita_gesamt["quelle"],
        )
        if abs(punkt.abweichung) > TOLERANZ_EURO:
            abweichungen.append(punkt)
    return geprueft, abweichungen


def _pruefe_regel5_weitergabe(
    *,
    transfer_df: pl.DataFrame,
    planwerte_ergebnisplan: Planwerte,
    ergebnisplan: pl.DataFrame,
    produkt: str,
) -> tuple[int, list[Pruefpunkt]]:
    """Weitergabe an Kreis und Land (D-01): Σ WEITERGABE_POSTEN × 1000 == TP <produkt> Z. 15
    je Jahr, Toleranz ±(Anzahl Posten × REGEL5_TOLERANZ_GEP_EURO). Ein fehlender Posten
    bricht mit PruefungsFehler ab (D-01 ist eine vollständige Identität, kein Teilabgleich)."""
    fehlend = [
        posten
        for posten in WEITERGABE_POSTEN
        if transfer_df.filter(pl.col("posten") == posten).height == 0
    ]
    if fehlend:
        raise PruefungsFehler(
            f"Regel 5: Weitergabe-Posten {fehlend} fehlen in transferaufwendungen.csv"
        )

    weitergabe_df = transfer_df.filter(pl.col("posten").is_in(WEITERGABE_POSTEN))
    geprueft = 0
    abweichungen: list[Pruefpunkt] = []
    toleranz = len(WEITERGABE_POSTEN) * REGEL5_TOLERANZ_GEP_EURO
    for jahr in sorted(weitergabe_df["jahr"].unique().to_list()):
        jahr_df = weitergabe_df.filter(pl.col("jahr") == jahr)
        if jahr_df.height != len(WEITERGABE_POSTEN):
            raise PruefungsFehler(f"Regel 5: Weitergabe-Posten unvollständig für Jahr {jahr}")
        wertart = jahr_df["wertart"][0]
        summe = jahr_df["betrag_teur"].sum()
        tp_zeile = ergebnisplan.filter(
            (pl.col("ebene") == "P")
            & (pl.col("code") == produkt)
            & (pl.col("zeile") == "15")
            & (pl.col("jahr") == jahr)
            & (pl.col("wertart") == wertart)
        )
        if tp_zeile.height != 1:
            raise PruefungsFehler(
                f"Regel 5: Teilergebnisplan von Produkt {produkt!r} hat keine eindeutige "
                f"Zeile 15 für Jahr {jahr}"
            )
        pdf_seite = tp_zeile["pdf_seite"][0]

        geprueft += 1
        punkt = Pruefpunkt(
            regel=5,
            plan="weitergabe_kreis_land",
            ebene="P",
            code=produkt,
            zeile="tp_15",
            jahr=jahr,
            wertart=wertart,
            soll=planwerte_ergebnisplan.wert("P", produkt, "15", jahr, wertart),
            ist=summe * 1000,
            pdf_seite=pdf_seite,
        )
        if abs(punkt.abweichung) > toleranz:
            abweichungen.append(punkt)
    return geprueft, abweichungen


def zerlege_weitere_vorberichtstabellen(df: pl.DataFrame) -> dict[str, pl.DataFrame]:
    """Zerlegt `weitere_vorberichtstabellen.csv` nach Spalte `tabelle` (D-08, MANU-05).

    Die Tabellenmenge der Datei muss exakt `WEITERE_VORBERICHTSTABELLEN` entsprechen;
    eine abweichende Menge (fehlend oder zusätzlich) bricht mit `PruefungsFehler` ab —
    D-08 ist eine abgeschlossene Liste, keine Erweiterung ohne Review."""
    tatsaechlich = set(df["tabelle"].unique().to_list())
    erwartet = set(WEITERE_VORBERICHTSTABELLEN)
    if tatsaechlich != erwartet:
        raise PruefungsFehler(
            "Regel 5: weitere_vorberichtstabellen.csv hat eine abweichende Tabellenmenge "
            f"(gefunden: {sorted(tatsaechlich)}, erwartet: {sorted(erwartet)})"
        )
    return {
        tabelle: df.filter(pl.col("tabelle") == tabelle) for tabelle in WEITERE_VORBERICHTSTABELLEN
    }


# D-10 (Kreisumlage brutto/netto): eigene, grobere Toleranz für den Gegenabgleich gegen
# die gerundete Fußnote "rd. 11,5 Mio. €" (Anhang B.6); die beiden exakten Formel-Checks
# (brutto_formel, netto_transfer) bleiben bei TOLERANZ_EURO.
REGEL5_TOLERANZ_FUSSNOTE_EURO = 50000
# Eckwerte (Anhang B.6, D-10, D-14, D-20): welcher Name von welcher Regel konsumiert
# wird. pruefe_alles bricht ab, wenn ein [eckwerte.*]-Name in keiner der beiden Mengen
# steht (kein Sollwert bleibt unbewacht, D-20).
REGEL5_ECKWERTE: tuple[str, ...] = (
    "kreisumlage_umlage_fussnote",
    "verringerung_ausgleichsruecklage",
    "verringerung_allgemeine_ruecklage",
)
REGEL9_ECKWERTE: tuple[str, ...] = (
    "einwohner",
    "hebesatz_grundsteuer_a",
    "hebesatz_grundsteuer_b",
    "hebesatz_gewerbesteuer",
    "hebesatz_kreisumlage_promille",
    "hebesatz_kreisumlage_vorjahr_promille",
    "hebesatz_jugendamtsumlage_promille",
    "hebesatz_jugendamtsumlage_vorjahr_promille",
    "schluesselzuweisung_teur",
    "schluesselzuweisung_vorjahr_teur",
    "pro_kopf_verschuldung_vorjahr",
    "stellen_beamte",
)
# weitere_vorberichtstabellen-artige Tabellen ohne gedruckte Gesamtzeile (D-11): die
# generische Stufe (a)/(b)-Prüfung in _pruefe_regel5 wird für sie übersprungen.
REGEL5_TABELLEN_OHNE_GESAMT: tuple[str, ...] = ("buergschaften",)


def pruefe_eckwerte_konsumiert(eckwerte: Mapping[str, Mapping[str, int]]) -> None:
    """Bricht ab, wenn ein `[eckwerte.*]`-Name von keiner Regel konsumiert wird (D-20)."""
    konsumiert = set(REGEL9_ECKWERTE) | set(REGEL5_ECKWERTE)
    unkonsumiert = set(eckwerte) - konsumiert
    if unkonsumiert:
        raise PruefungsFehler(
            f"Eckwerte ohne Prüfregel (von weder Regel 5 noch Regel 9 konsumiert): "
            f"{sorted(unkonsumiert)}"
        )


def _pruefe_regel5_meta_kreisumlage(
    *,
    meta: Mapping,
    transfer_df: pl.DataFrame,
    eckwerte: Mapping[str, Mapping[str, int]],
    haushaltsjahr: int,
) -> tuple[int, list[Pruefpunkt]]:
    """D-10: Kreisumlage brutto/netto aus `meta.json` gegen den Transferaufwendungen-
    Posten `kreisumlage` und den Fußnoten-Eckwert (Anhang B.6) geprüft (`plan`
    `meta_kreisumlage`): `brutto_formel` (soll netto + Rückstellungsauflösung, exakt),
    `netto_transfer` (soll Transferposten × 1000, exakt) und `brutto_fussnote` (soll
    Eckwert `kreisumlage_umlage_fussnote`, Toleranz ±REGEL5_TOLERANZ_FUSSNOTE_EURO, da
    die Fußnote selbst nur "rd. 11,5 Mio. €" nennt)."""
    netto = meta["kreisumlage"]["netto"]
    rueckstellung = meta["kreisumlage"]["rueckstellungsaufloesung"]
    brutto = meta["kreisumlage"]["brutto"]
    pdf_seite = brutto["quelle"]

    kreisumlage_zeile = transfer_df.filter(
        (pl.col("posten") == "kreisumlage") & (pl.col("jahr") == haushaltsjahr)
    )
    if kreisumlage_zeile.height != 1:
        raise PruefungsFehler(
            "Regel 5: transferaufwendungen.csv hat keinen eindeutigen Posten "
            f"'kreisumlage' für Jahr {haushaltsjahr}"
        )
    wertart = kreisumlage_zeile["wertart"][0]

    geprueft = 0
    abweichungen: list[Pruefpunkt] = []

    geprueft += 1
    punkt_formel = Pruefpunkt(
        regel=5,
        plan="meta_kreisumlage",
        ebene="GESAMT",
        code="",
        zeile="brutto_formel",
        jahr=haushaltsjahr,
        wertart=wertart,
        soll=netto["wert"] + rueckstellung["wert"],
        ist=brutto["wert"],
        pdf_seite=pdf_seite,
    )
    if abs(punkt_formel.abweichung) > TOLERANZ_EURO:
        abweichungen.append(punkt_formel)

    geprueft += 1
    punkt_netto = Pruefpunkt(
        regel=5,
        plan="meta_kreisumlage",
        ebene="GESAMT",
        code="",
        zeile="netto_transfer",
        jahr=haushaltsjahr,
        wertart=wertart,
        soll=kreisumlage_zeile["betrag_teur"][0] * 1000,
        ist=netto["wert"],
        pdf_seite=pdf_seite,
    )
    if abs(punkt_netto.abweichung) > TOLERANZ_EURO:
        abweichungen.append(punkt_netto)

    fussnote = eckwerte["kreisumlage_umlage_fussnote"]
    geprueft += 1
    punkt_fussnote = Pruefpunkt(
        regel=5,
        plan="meta_kreisumlage",
        ebene="GESAMT",
        code="",
        zeile="brutto_fussnote",
        jahr=haushaltsjahr,
        wertart=wertart,
        soll=fussnote["wert"],
        ist=brutto["wert"],
        pdf_seite=fussnote["pdf_seite"],
    )
    if abs(punkt_fussnote.abweichung) > REGEL5_TOLERANZ_FUSSNOTE_EURO:
        abweichungen.append(punkt_fussnote)

    return geprueft, abweichungen


def _pruefe_regel5(
    *,
    vorbericht: Mapping[str, pl.DataFrame],
    planwerte_ergebnisplan: Planwerte,
    ergebnisplan: pl.DataFrame,
    jahrgang: Jahrgang,
    meta: Mapping | None = None,
    eckwerte: Mapping[str, Mapping[str, int]] | None = None,
) -> Regelergebnis:
    """Regel 5 – manuelle Vorberichtstabellen → Planzeilen (PRUEF-05, D-01, D-07).

    Zweistufig je (Tabelle, Jahr): Stufe (a) vergleicht die Summe der Nicht-Gesamt-Posten
    mit der mit abgeschriebenen, gedruckten Gesamtzeile (beide × 1000, damit eine 1-T€-
    Differenz zu 1.000 € wird und über TOLERANZ_EURO=1 dokumentierbar bleibt, D-07a). Stufe
    (b) vergleicht die Gesamtzeile × 1000 mit der über REGEL5_GEP_ZEILEN zugeordneten
    GEP-Zeile, mit der gröberen REGEL5_TOLERANZ_GEP_EURO-Toleranz (D-07b). `ebene`/`code`
    bleiben "GESAMT"/"" (Research Pattern 3 — Vorbericht-Tabellen sind kein PB/PG/P-Knoten),
    der fachliche Kontext steht in `plan` (`vorbericht_{tabelle}`), der Posten-/Vergleichs-
    schlüssel in `zeile` ("summe_posten" bzw. "gep_{nr}"). Zusätzlich, nur wenn vorhanden:
    der Kita/Transfer-Kreuzvergleich (`_pruefe_regel5_kita_gegen_transfer`) und die
    Weitergabe an Kreis und Land (`_pruefe_regel5_weitergabe`, D-01).
    """
    geprueft = 0
    abweichungen: list[Pruefpunkt] = []
    for tabelle, df in sorted(vorbericht.items()):
        if tabelle in REGEL5_TABELLEN_OHNE_GESAMT:
            continue
        gep_zeile = REGEL5_GEP_ZEILEN.get(tabelle)
        for jahr in sorted(df["jahr"].unique().to_list()):
            jahr_df = df.filter(pl.col("jahr") == jahr)
            gesamt_zeilen = jahr_df.filter(pl.col("ist_gesamt"))
            if gesamt_zeilen.height != 1:
                raise PruefungsFehler(
                    f"Regel 5: {tabelle} Jahr {jahr} hat {gesamt_zeilen.height} "
                    "ist_gesamt-Zeilen, erwartet genau 1"
                )
            gesamt = gesamt_zeilen.row(0, named=True)
            wertart = gesamt["wertart"]
            pdf_seite = gesamt["quelle"]
            posten_summe = jahr_df.filter(~pl.col("ist_gesamt"))["betrag_teur"].sum() or 0

            geprueft += 1
            punkt_a = Pruefpunkt(
                regel=5,
                plan=f"vorbericht_{tabelle}",
                ebene="GESAMT",
                code="",
                zeile="summe_posten",
                jahr=jahr,
                wertart=wertart,
                soll=gesamt["betrag_teur"] * 1000,
                ist=posten_summe * 1000,
                pdf_seite=pdf_seite,
            )
            if abs(punkt_a.abweichung) > TOLERANZ_EURO:
                abweichungen.append(punkt_a)

            if gep_zeile is not None:
                geprueft += 1
                punkt_b = Pruefpunkt(
                    regel=5,
                    plan=f"vorbericht_{tabelle}",
                    ebene="GESAMT",
                    code="",
                    zeile=f"gep_{gep_zeile}",
                    jahr=jahr,
                    wertart=wertart,
                    soll=planwerte_ergebnisplan.wert("GESAMT", "", gep_zeile, jahr, wertart),
                    ist=gesamt["betrag_teur"] * 1000,
                    pdf_seite=pdf_seite,
                )
                if abs(punkt_b.abweichung) > REGEL5_TOLERANZ_GEP_EURO:
                    abweichungen.append(punkt_b)

    if "kita_zuschuesse" in vorbericht and "transferaufwendungen" in vorbericht:
        geprueft_kita, abweichungen_kita = _pruefe_regel5_kita_gegen_transfer(
            kita_df=vorbericht["kita_zuschuesse"],
            transfer_df=vorbericht["transferaufwendungen"],
        )
        geprueft += geprueft_kita
        abweichungen += abweichungen_kita

    if "transferaufwendungen" in vorbericht:
        produkt = layout_text(jahrgang, "weitergabe_kreis_land", "produkt")
        geprueft_weitergabe, abweichungen_weitergabe = _pruefe_regel5_weitergabe(
            transfer_df=vorbericht["transferaufwendungen"],
            planwerte_ergebnisplan=planwerte_ergebnisplan,
            ergebnisplan=ergebnisplan,
            produkt=produkt,
        )
        geprueft += geprueft_weitergabe
        abweichungen += abweichungen_weitergabe

    if "transferaufwendungen" in vorbericht and meta is not None and eckwerte is not None:
        geprueft_meta, abweichungen_meta = _pruefe_regel5_meta_kreisumlage(
            meta=meta,
            transfer_df=vorbericht["transferaufwendungen"],
            eckwerte=eckwerte,
            haushaltsjahr=jahrgang.haushaltsjahr,
        )
        geprueft += geprueft_meta
        abweichungen += abweichungen_meta

    return Regelergebnis(
        regel=5,
        titel="Regel 5 – Manuelle Tabellen → Planzeilen",
        geprueft=geprueft,
        abweichungen=tuple(abweichungen),
    )


def _pruefe_regel5_eigenkapital_summe(
    *, eigenkapital: pl.DataFrame
) -> tuple[int, list[Pruefpunkt]]:
    """Stufe (a) für `eigenkapital.csv` (D-11, D-12): Summe der Posten gegen die
    gedruckte Gesamtzeile, beide bereits in int-Euro (kaufmännisch gerundete Cent,
    kein ×1000 nötig — anders als die T€-geführten Vorberichtstabellen)."""
    geprueft = 0
    abweichungen: list[Pruefpunkt] = []
    for jahr in sorted(eigenkapital["jahr"].unique().to_list()):
        jahr_df = eigenkapital.filter(pl.col("jahr") == jahr)
        gesamt_zeilen = jahr_df.filter(pl.col("ist_gesamt"))
        if gesamt_zeilen.height != 1:
            raise PruefungsFehler(
                f"Regel 5: eigenkapital Jahr {jahr} hat {gesamt_zeilen.height} "
                "ist_gesamt-Zeilen, erwartet genau 1"
            )
        gesamt = gesamt_zeilen.row(0, named=True)
        posten_summe = jahr_df.filter(~pl.col("ist_gesamt"))["betrag"].sum() or 0
        geprueft += 1
        punkt = Pruefpunkt(
            regel=5,
            plan="vorbericht_eigenkapital",
            ebene="GESAMT",
            code="",
            zeile="summe_posten",
            jahr=jahr,
            wertart=gesamt["wertart"],
            soll=gesamt["betrag"],
            ist=posten_summe,
            pdf_seite=gesamt["quelle"],
        )
        if abs(punkt.abweichung) > TOLERANZ_EURO:
            abweichungen.append(punkt)
    return geprueft, abweichungen


def _pruefe_regel5_kredite_fortschreibung(
    *, verbindlichkeiten: pl.DataFrame, planwerte_finanzplan: Planwerte, haushaltsjahr: int
) -> tuple[int, list[Pruefpunkt]]:
    """D-11, D-13: Investitionskredite Ende Haushaltsjahr = Ende Vorjahr + GFP-Kredit-
    aufnahme (Z. 33) − GFP-Tilgung (Z. 35), über `manuell.investitionskredite_ende`."""
    zeilen = verbindlichkeiten.filter(
        (pl.col("tabelle") == "verbindlichkeiten") & (pl.col("posten") == "kredite_investitionen")
    )
    nach_jahr = {zeile["jahr"]: zeile for zeile in zeilen.iter_rows(named=True)}
    vorjahr = nach_jahr.get(haushaltsjahr - 1)
    haushaltsjahr_zeile = nach_jahr.get(haushaltsjahr)
    if vorjahr is None or haushaltsjahr_zeile is None:
        raise PruefungsFehler(
            "Regel 5: verbindlichkeiten.csv hat keinen Posten 'kredite_investitionen' "
            f"für Vorjahr {haushaltsjahr - 1} oder Haushaltsjahr {haushaltsjahr}"
        )
    kreditaufnahme = planwerte_finanzplan.wert("GESAMT", "", "33", haushaltsjahr, "ansatz")
    tilgung = planwerte_finanzplan.wert("GESAMT", "", "35", haushaltsjahr, "ansatz")
    ist = investitionskredite_ende(vorjahr["betrag_teur"] * 1000, kreditaufnahme, tilgung)
    punkt = Pruefpunkt(
        regel=5,
        plan="verbindlichkeiten",
        ebene="GESAMT",
        code="",
        zeile="kredite_fortschreibung",
        jahr=haushaltsjahr,
        wertart=haushaltsjahr_zeile["wertart"],
        soll=haushaltsjahr_zeile["betrag_teur"] * 1000,
        ist=ist,
        pdf_seite=haushaltsjahr_zeile["quelle"],
    )
    abweichungen = [punkt] if abs(punkt.abweichung) > REGEL5_TOLERANZ_GEP_EURO else []
    return 1, abweichungen


def _pruefe_regel5_eigenkapital_jahresergebnis(
    *, eigenkapital: pl.DataFrame, planwerte_ergebnisplan: Planwerte
) -> tuple[int, list[Pruefpunkt]]:
    """D-11: Jahresergebnis (S. 311) == GEP Z. 28 je Jahr (`plan` `eigenkapital`,
    `zeile` `jahresergebnis_gep_28`)."""
    geprueft = 0
    abweichungen: list[Pruefpunkt] = []
    for zeile in eigenkapital.filter(pl.col("posten") == "jahresergebnis").iter_rows(named=True):
        soll = planwerte_ergebnisplan.wert("GESAMT", "", "28", zeile["jahr"], zeile["wertart"])
        geprueft += 1
        punkt = Pruefpunkt(
            regel=5,
            plan="eigenkapital",
            ebene="GESAMT",
            code="",
            zeile="jahresergebnis_gep_28",
            jahr=zeile["jahr"],
            wertart=zeile["wertart"],
            soll=soll,
            ist=zeile["betrag"],
            pdf_seite=zeile["quelle"],
        )
        if abs(punkt.abweichung) > TOLERANZ_EURO:
            abweichungen.append(punkt)
    return geprueft, abweichungen


def _pruefe_regel5_satzung_paragraf4(
    *,
    eigenkapital: pl.DataFrame,
    planwerte_ergebnisplan: Planwerte,
    eckwerte: Mapping[str, Mapping[str, int]],
    haushaltsjahr: int,
) -> tuple[int, list[Pruefpunkt]]:
    """D-11, Research Pitfall 4: Satzung § 4 ist NICHT der rohe Jahresdelta der
    Eigenkapital-Übersicht, sondern (a) Ausgleichsrücklage Stand Haushaltsjahr − Stand
    Folgejahr == Eckwert `verringerung_ausgleichsruecklage` (`zeile` `ausgleichsruecklage`)
    und (b) Σ beider Eckwerte (Ausgleichs- und allgemeine Rücklage) == −GEP Z. 28 des
    Haushaltsjahrs (`zeile` `summe_verringerung`)."""
    ausgleich = eigenkapital.filter(pl.col("posten") == "ausgleichsruecklage")
    hj_zeile = ausgleich.filter(pl.col("jahr") == haushaltsjahr)
    folge_zeile = ausgleich.filter(pl.col("jahr") == haushaltsjahr + 1)
    if hj_zeile.height != 1 or folge_zeile.height != 1:
        raise PruefungsFehler(
            "Regel 5: eigenkapital.csv hat keine eindeutige Ausgleichsrücklage-Zeile "
            f"für Haushaltsjahr {haushaltsjahr} oder Folgejahr {haushaltsjahr + 1}"
        )
    hj = hj_zeile.row(0, named=True)
    folge = folge_zeile.row(0, named=True)
    verringerung_ausgleich = hj["betrag"] - folge["betrag"]

    eckwert_ausgleich = eckwerte["verringerung_ausgleichsruecklage"]
    eckwert_allgemein = eckwerte["verringerung_allgemeine_ruecklage"]

    geprueft = 0
    abweichungen: list[Pruefpunkt] = []

    geprueft += 1
    punkt_ausgleich = Pruefpunkt(
        regel=5,
        plan="satzung_paragraf4",
        ebene="GESAMT",
        code="",
        zeile="ausgleichsruecklage",
        jahr=haushaltsjahr,
        wertart=hj["wertart"],
        soll=eckwert_ausgleich["wert"],
        ist=verringerung_ausgleich,
        pdf_seite=eckwert_ausgleich["pdf_seite"],
    )
    if abs(punkt_ausgleich.abweichung) > TOLERANZ_EURO:
        abweichungen.append(punkt_ausgleich)

    gep_28 = planwerte_ergebnisplan.wert("GESAMT", "", "28", haushaltsjahr, hj["wertart"])
    geprueft += 1
    punkt_summe = Pruefpunkt(
        regel=5,
        plan="satzung_paragraf4",
        ebene="GESAMT",
        code="",
        zeile="summe_verringerung",
        jahr=haushaltsjahr,
        wertart=hj["wertart"],
        soll=-gep_28,
        ist=eckwert_ausgleich["wert"] + eckwert_allgemein["wert"],
        pdf_seite=eckwert_ausgleich["pdf_seite"],
    )
    if abs(punkt_summe.abweichung) > TOLERANZ_EURO:
        abweichungen.append(punkt_summe)

    return geprueft, abweichungen


def _pruefe_regel5_ve_uebersicht(
    *,
    ve_uebersicht: pl.DataFrame,
    ve_faelligkeiten: pl.DataFrame,
    planwerte_finanzplan: Planwerte,
    haushaltsjahr: int,
) -> tuple[int, list[Pruefpunkt], list[Luecke]]:
    """D-11: VE-Gesamtbetrag == GFP-VE Z. 30 (`zeile` `summe_gfp_ve`) und je (Produkt,
    Fälligkeitsjahr) die VE-Übersicht gegen `ve_faelligkeiten.csv` (`zeile`
    `faellig_{produkt}`); ein Paar nur in einer Quelle ist eine `Luecke` (structural,
    keine Betragsabweichung, 03-03-Mechanismus)."""
    gesamtbetrag_zeilen = ve_uebersicht.filter(
        pl.col("ist_gesamt") & pl.col("faellig_jahr").is_null()
    )
    if gesamtbetrag_zeilen.height != 1:
        raise PruefungsFehler(
            "Regel 5: ve_uebersicht.csv hat keine eindeutige VE-Gesamtbetrag-Summenzeile"
        )
    gesamtbetrag = gesamtbetrag_zeilen.row(0, named=True)

    geprueft = 0
    abweichungen: list[Pruefpunkt] = []
    luecken: list[Luecke] = []

    soll_gfp_ve = planwerte_finanzplan.wert("GESAMT", "", "30", haushaltsjahr, "ve")
    geprueft += 1
    punkt_summe = Pruefpunkt(
        regel=5,
        plan="ve_uebersicht",
        ebene="GESAMT",
        code="",
        zeile="summe_gfp_ve",
        jahr=haushaltsjahr,
        wertart="ve",
        soll=soll_gfp_ve,
        ist=gesamtbetrag["betrag_teur"] * 1000,
        pdf_seite=gesamtbetrag["quelle"],
    )
    if abs(punkt_summe.abweichung) > TOLERANZ_EURO:
        abweichungen.append(punkt_summe)

    einzel = ve_uebersicht.filter(~pl.col("ist_gesamt"))
    ist_gruppiert = einzel.group_by(["produkt", "faellig_jahr"]).agg(
        pl.col("betrag_teur").sum().alias("betrag_teur"), pl.col("quelle").min().alias("quelle")
    )
    soll_gruppiert = ve_faelligkeiten.group_by(["produkt", "jahr"]).agg(
        pl.col("betrag").sum().alias("betrag"), pl.col("pdf_seite").min().alias("pdf_seite")
    )
    ist_dict = {
        (z["produkt"], z["faellig_jahr"]): (z["betrag_teur"] * 1000, z["quelle"])
        for z in ist_gruppiert.iter_rows(named=True)
    }
    soll_dict = {
        (z["produkt"], z["jahr"]): (z["betrag"], z["pdf_seite"])
        for z in soll_gruppiert.iter_rows(named=True)
    }

    for produkt, jahr in sorted(set(ist_dict) | set(soll_dict)):
        in_ve_uebersicht = (produkt, jahr) in ist_dict
        in_ve_faelligkeiten = (produkt, jahr) in soll_dict
        if in_ve_uebersicht and in_ve_faelligkeiten:
            ist, ist_seite = ist_dict[(produkt, jahr)]
            soll, soll_seite = soll_dict[(produkt, jahr)]
            geprueft += 1
            punkt = Pruefpunkt(
                regel=5,
                plan="ve_uebersicht",
                ebene="P",
                code=produkt,
                zeile=f"faellig_{produkt}",
                jahr=jahr,
                wertart="ve",
                soll=soll,
                ist=ist,
                pdf_seite=soll_seite,
            )
            if abs(punkt.abweichung) > TOLERANZ_EURO:
                abweichungen.append(punkt)
        elif in_ve_uebersicht:
            _, ist_seite = ist_dict[(produkt, jahr)]
            luecken.append(
                Luecke(
                    regel=5,
                    ebene="P",
                    code=produkt,
                    merkmal=f"Fälligkeit {jahr}: nur in ve_uebersicht.csv",
                    pdf_seite=ist_seite,
                )
            )
        else:
            _, soll_seite = soll_dict[(produkt, jahr)]
            luecken.append(
                Luecke(
                    regel=5,
                    ebene="P",
                    code=produkt,
                    merkmal=f"Fälligkeit {jahr}: nur in ve_faelligkeiten.csv",
                    pdf_seite=soll_seite,
                )
            )

    return geprueft, abweichungen, luecken


def pruefe_regel5_schulden_ruecklagen_ve(
    *,
    verbindlichkeiten: pl.DataFrame,
    eigenkapital: pl.DataFrame,
    ve_uebersicht: pl.DataFrame,
    ve_faelligkeiten: pl.DataFrame,
    planwerte_ergebnisplan: Planwerte,
    planwerte_finanzplan: Planwerte,
    eckwerte: Mapping[str, Mapping[str, int]],
    haushaltsjahr: int,
) -> tuple[int, list[Pruefpunkt], list[Luecke]]:
    """Orchestriert die D-11 bis D-14-Erweiterungen von Regel 5 (Schulden, Rücklagen,
    VE): Eigenkapital-Summe, Kredit-Fortschreibung, Jahresergebnis vs. GEP Z. 28,
    Satzung § 4 und die VE-Übersicht gegen `ve_faelligkeiten.csv`."""
    geprueft = 0
    abweichungen: list[Pruefpunkt] = []
    luecken: list[Luecke] = []

    geprueft_ek, abweichungen_ek = _pruefe_regel5_eigenkapital_summe(eigenkapital=eigenkapital)
    geprueft += geprueft_ek
    abweichungen += abweichungen_ek

    geprueft_kredite, abweichungen_kredite = _pruefe_regel5_kredite_fortschreibung(
        verbindlichkeiten=verbindlichkeiten,
        planwerte_finanzplan=planwerte_finanzplan,
        haushaltsjahr=haushaltsjahr,
    )
    geprueft += geprueft_kredite
    abweichungen += abweichungen_kredite

    (
        geprueft_jahresergebnis,
        abweichungen_jahresergebnis,
    ) = _pruefe_regel5_eigenkapital_jahresergebnis(
        eigenkapital=eigenkapital, planwerte_ergebnisplan=planwerte_ergebnisplan
    )
    geprueft += geprueft_jahresergebnis
    abweichungen += abweichungen_jahresergebnis

    geprueft_satzung, abweichungen_satzung = _pruefe_regel5_satzung_paragraf4(
        eigenkapital=eigenkapital,
        planwerte_ergebnisplan=planwerte_ergebnisplan,
        eckwerte=eckwerte,
        haushaltsjahr=haushaltsjahr,
    )
    geprueft += geprueft_satzung
    abweichungen += abweichungen_satzung

    geprueft_ve, abweichungen_ve, luecken_ve = _pruefe_regel5_ve_uebersicht(
        ve_uebersicht=ve_uebersicht,
        ve_faelligkeiten=ve_faelligkeiten,
        planwerte_finanzplan=planwerte_finanzplan,
        haushaltsjahr=haushaltsjahr,
    )
    geprueft += geprueft_ve
    abweichungen += abweichungen_ve
    luecken += luecken_ve

    return geprueft, abweichungen, luecken


# Eckwerte, deren Ist-Wert in einer feineren Einheit geführt wird als der gedruckte
# Sollwert (D-20, Plan 04-03): der Sollwert wird mit dem hier angegebenen Faktor
# multipliziert, bevor er gegen den Ist-Wert verglichen wird. `stellen_beamte` ist
# Stellen (ganzzahlig), Σ stellen_hundertstel ist Hundertstel.
_REGEL9_SOLL_FAKTOR: Mapping[str, int] = {"stellen_beamte": 100}


def _regel9_ist_werte(
    *,
    meta: Mapping,
    zuwendungen: pl.DataFrame,
    verbindlichkeiten: pl.DataFrame | None,
    stellenplan: pl.DataFrame | None,
    haushaltsjahr: int,
) -> dict[str, int]:
    """Ist-Werte der Regel-9-Eckwerte (D-10, D-14, D-20): `meta.json`-Pfade,
    `zuwendungen.csv`-Posten `schluesselzuweisung` des Haushaltsjahrs und Vorjahrs,
    (wenn `verbindlichkeiten` übergeben ist, 04-02 Task 3) die Pro-Kopf-Verschuldung
    des Vorjahrs nach der Vorbericht-Definition (D-14, `manuell.schuldenstand_euro`/
    `pro_kopf_euro`), und (wenn `stellenplan` übergeben ist, Plan 04-03) Σ Teil A
    (Beamte) Stellen des Haushaltsjahrs ohne Produktbereich."""

    def _zuwendung(posten: str, jahr: int) -> int:
        zeile = zuwendungen.filter((pl.col("posten") == posten) & (pl.col("jahr") == jahr))
        if zeile.height != 1:
            raise PruefungsFehler(
                f"Regel 9: Posten {posten!r} hat {zeile.height} Zeilen für Jahr {jahr}, "
                "erwartet genau 1"
            )
        return zeile["betrag_teur"][0]

    hebesaetze = meta["hebesaetze"]
    kreisumlage = meta["kreisumlage"]
    werte = {
        "einwohner": meta["einwohner"]["wert"],
        "hebesatz_grundsteuer_a": hebesaetze["grundsteuer_a"]["wert"],
        "hebesatz_grundsteuer_b": hebesaetze["grundsteuer_b"]["wert"],
        "hebesatz_gewerbesteuer": hebesaetze["gewerbesteuer"]["wert"],
        "hebesatz_kreisumlage_promille": kreisumlage["hebesatz_kreisumlage"]["wert"],
        "hebesatz_kreisumlage_vorjahr_promille": kreisumlage["hebesatz_kreisumlage"]["vorjahr"],
        "hebesatz_jugendamtsumlage_promille": kreisumlage["hebesatz_jugendamtsumlage"]["wert"],
        "hebesatz_jugendamtsumlage_vorjahr_promille": kreisumlage["hebesatz_jugendamtsumlage"][
            "vorjahr"
        ],
        "schluesselzuweisung_teur": _zuwendung("schluesselzuweisung", haushaltsjahr),
        "schluesselzuweisung_vorjahr_teur": _zuwendung("schluesselzuweisung", haushaltsjahr - 1),
    }
    if verbindlichkeiten is not None:
        schuldenstand_vorjahr = schuldenstand_euro(verbindlichkeiten, haushaltsjahr - 1)
        werte["pro_kopf_verschuldung_vorjahr"] = pro_kopf_euro(
            schuldenstand_vorjahr, meta["einwohner"]["wert"]
        )
    if stellenplan is not None:
        beamte_stellen = stellenplan.filter(
            (pl.col("teil") == "beamte")
            & (pl.col("merkmal") == "stellen")
            & (pl.col("jahr") == haushaltsjahr)
            & pl.col("produktbereich").is_null()
        )
        werte["stellen_beamte"] = beamte_stellen["stellen_hundertstel"].sum() or 0
    return werte


def _pruefe_regel9(
    *,
    eckwerte: Mapping[str, Mapping[str, int]],
    meta: Mapping,
    zuwendungen: pl.DataFrame,
    haushaltsjahr: int,
    verbindlichkeiten: pl.DataFrame | None = None,
    stellenplan: pl.DataFrame | None = None,
) -> Regelergebnis:
    """Regel 9 – Eckwerte (Anhang B.6, D-10, D-14, D-20): exakter Soll/Ist-Vergleich
    (Toleranz 0, `toleranz_fuer(9)`) für jeden Namen in `REGEL9_ECKWERTE`. Ein Soll-Faktor
    (`_REGEL9_SOLL_FAKTOR`) skaliert den gedruckten Sollwert auf die Ist-Einheit, wo diese
    feiner ist (D-20: `stellen_beamte` vergleicht Stellen gegen Hundertstel)."""
    ist_werte = _regel9_ist_werte(
        meta=meta,
        zuwendungen=zuwendungen,
        verbindlichkeiten=verbindlichkeiten,
        stellenplan=stellenplan,
        haushaltsjahr=haushaltsjahr,
    )

    geprueft = 0
    abweichungen: list[Pruefpunkt] = []
    for name in REGEL9_ECKWERTE:
        eckwert = eckwerte[name]
        geprueft += 1
        soll = eckwert["wert"] * _REGEL9_SOLL_FAKTOR.get(name, 1)
        punkt = Pruefpunkt(
            regel=9,
            plan="anhang_b6",
            ebene="GESAMT",
            code="",
            zeile=name,
            jahr=haushaltsjahr,
            wertart="ansatz",
            soll=soll,
            ist=ist_werte[name],
            pdf_seite=eckwert["pdf_seite"],
        )
        if punkt.abweichung != 0:
            abweichungen.append(punkt)
    return Regelergebnis(
        regel=9,
        titel="Regel 9 – Eckwerte (Anhang B.6)",
        geprueft=geprueft,
        abweichungen=tuple(abweichungen),
    )


def _pruefe_regel10(*, stellenplan: pl.DataFrame, haushaltsjahr: int) -> Regelergebnis:
    """Regel 10 – Stellenplan: Stellenübersicht → Teil A/B (D-20, Plan 04-03): je (teil,
    gruppe) muss Σ Stellenübersicht (über alle Produktbereiche) exakt der Teil-A/B-
    Stellenzeile des Haushaltsjahrs entsprechen (Toleranz 0, `toleranz_fuer(10)`). Eine
    Gruppe, die nur in einer der beiden Quellen vorkommt, zählt in der fehlenden Quelle
    als 0. Ein gedrucktes VZÄ-Rundungsdetail wäre hier als Befund zu belegen (D-20); auf
    den eingecheckten Daten gibt es keine Abweichung."""
    teil_ab = stellenplan.filter(
        (pl.col("merkmal") == "stellen")
        & (pl.col("jahr") == haushaltsjahr)
        & pl.col("produktbereich").is_null()
    )
    uebersicht = stellenplan.filter(
        (pl.col("merkmal") == "stellen")
        & (pl.col("jahr") == haushaltsjahr)
        & pl.col("produktbereich").is_not_null()
    )

    teil_ab_werte: dict[tuple[str, str], tuple[int, int]] = {
        (zeile["teil"], zeile["gruppe"]): (zeile["stellen_hundertstel"], zeile["pdf_seite"])
        for zeile in teil_ab.iter_rows(named=True)
    }
    uebersicht_summen: dict[tuple[str, str], int] = {}
    uebersicht_seiten: dict[tuple[str, str], int] = {}
    for zeile in uebersicht.iter_rows(named=True):
        schluessel = (zeile["teil"], zeile["gruppe"])
        uebersicht_summen[schluessel] = (
            uebersicht_summen.get(schluessel, 0) + zeile["stellen_hundertstel"]
        )
        uebersicht_seiten.setdefault(schluessel, zeile["pdf_seite"])

    alle_schluessel = set(teil_ab_werte) | set(uebersicht_summen)
    geprueft = 0
    abweichungen: list[Pruefpunkt] = []
    for teil, gruppe in sorted(alle_schluessel):
        soll, teil_ab_seite = teil_ab_werte.get((teil, gruppe), (0, None))
        ist = uebersicht_summen.get((teil, gruppe), 0)
        pdf_seite = uebersicht_seiten.get((teil, gruppe), teil_ab_seite)
        geprueft += 1
        punkt = Pruefpunkt(
            regel=10,
            plan=f"stellenuebersicht_{teil}",
            ebene="GESAMT",
            code="",
            zeile=gruppe,
            jahr=haushaltsjahr,
            wertart="ansatz",
            soll=soll,
            ist=ist,
            pdf_seite=pdf_seite,
        )
        if punkt.abweichung != 0:
            abweichungen.append(punkt)
    return Regelergebnis(
        regel=10,
        titel="Regel 10 – Stellenplan: Stellenübersicht → Teil A/B",
        geprueft=geprueft,
        abweichungen=tuple(abweichungen),
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


# Regel 8 (PRUEF-08, Spez. 5.5): Pflichtfelder, die jedes Produkt in produkte.json nicht-
# leer trägt. Jedes der 63 Produkte druckt auf seiner Produktinformationen-Seite alle
# zehn Feld-Labels (EXTR-06); die beiden Personenfelder (Verantwortliche/r, Sachbear-
# beiter/innen) sind D-09-bedingt nicht Teil von produkte.json und deshalb hier nicht
# geprüft. `bindungsgrad` (normalisiert), `leistungen` und `pdf_seiten` sind Listen bzw.
# ein Vokabular-Wert und werden separat geprüft (REGEL8_MERKMALE unten).
REGEL8_PFLICHTFELDER: tuple[str, ...] = (
    "fachbereich",
    "gremium",
    "beschreibung",
    "auftragsgrundlage",
    "klassifizierung",
    "zielgruppe",
    "ziele",
    "bindungsgrad_original",
)
# Normalisiertes Bindungsgrad-Vokabular: dieselben drei Werte wie
# produkte.BINDUNGSGRADE.values() (fachliche Regel hier eigenständig wiederholt, damit
# pruefung.py unabhängig von produkte.py bleibt, D-06-Architekturprinzip).
_REGEL8_BINDUNGSGRAD_VOKABULAR = frozenset({"pflichtig", "freiwillig", "teils"})
# Alle Merkmale, die Regel 8 je Produkt prüft: die acht Pflichtfelder oben plus
# Leistungen, Bindungsgrad, PDF-Seiten und je ein Teilergebnis-/Teilfinanzplan-
# Vorhandensein (fünf weitere Merkmale, Claude's Ermessen laut CONTEXT.md).
REGEL8_MERKMALE: tuple[str, ...] = REGEL8_PFLICHTFELDER + (
    "leistungen",
    "bindungsgrad",
    "pdf_seiten",
    "teilergebnisplan",
    "teilfinanzplan",
)


def _pruefe_regel8(
    *,
    produkte: Sequence[Mapping[str, object]],
    ergebnisplan: pl.DataFrame,
    finanzplan: pl.DataFrame,
    hierarchie: pl.DataFrame,
    jahrgang: Jahrgang,
) -> Regelergebnis:
    """Regel 8 – Vollständigkeit der Produkte (PRUEF-08, Spez. 5.5).

    Prüft zunächst (ein Check), dass produkte.json genau die P-Codes der Hierarchie in
    der erwarteten Anzahl (`jahrgang.anzahlen.produkte`) trägt: ein fehlender Code wird
    zu einer Lücke "produktinformationen", ein unbekannter Code zu "unbekanntes
    Produkt", eine falsche Gesamtanzahl zu "anzahl_produkte" (Ebene GESAMT). Prüft dann
    je Produkt, das in beiden Quellen vorkommt, `REGEL8_MERKMALE`: jedes
    `REGEL8_PFLICHTFELDER`-Feld eine nicht-leere Zeichenkette, `leistungen` eine nicht-
    leere Liste, `bindungsgrad` im normalisierten Vokabular, `pdf_seiten` nicht leer,
    sowie mindestens eine P-Zeile des Codes in `ergebnisplan`/`finanzplan`. Jeder
    Verstoß ist eine Lücke (03-03-Mechanismus) — ein fehlendes Pflichtfeld ist kein
    Rundungsfehler und kann nie über befunde.md entschärft werden. Regel 8 hat keine
    Abweichungen (kein Soll/Ist-Betragsvergleich).
    """
    hierarchie_p = hierarchie.filter(pl.col("ebene") == "P")
    hierarchie_codes = set(hierarchie_p["code"].to_list())
    pdf_seite_start_je_code = {
        zeile["code"]: zeile["pdf_seite_start"] for zeile in hierarchie_p.iter_rows(named=True)
    }
    produkte_codes = {produkt["code"] for produkt in produkte}
    produkt_je_code = {produkt["code"]: produkt for produkt in produkte}

    geprueft = 1  # die Mengen-/Anzahl-Prüfung ist EIN Check, unabhängig von der Lückenzahl
    luecken: list[Luecke] = []
    for code in sorted(hierarchie_codes - produkte_codes):
        luecken.append(
            Luecke(
                regel=8,
                ebene="P",
                code=code,
                merkmal="produktinformationen",
                pdf_seite=pdf_seite_start_je_code.get(code),
            )
        )
    for code in sorted(produkte_codes - hierarchie_codes):
        fremde_seiten = produkt_je_code[code].get("pdf_seiten") or []
        luecken.append(
            Luecke(
                regel=8,
                ebene="P",
                code=code,
                merkmal="unbekanntes Produkt",
                pdf_seite=min(fremde_seiten) if fremde_seiten else None,
            )
        )
    if len(produkte) != jahrgang.anzahlen.produkte:
        luecken.append(
            Luecke(regel=8, ebene="GESAMT", code="", merkmal="anzahl_produkte", pdf_seite=None)
        )

    for code in sorted(hierarchie_codes & produkte_codes):
        produkt = produkt_je_code[code]
        pdf_seiten = produkt.get("pdf_seiten") or []
        erste_seite = min(pdf_seiten) if pdf_seiten else None

        for feld in REGEL8_PFLICHTFELDER:
            geprueft += 1
            wert = produkt.get(feld)
            if not isinstance(wert, str) or not wert:
                luecken.append(
                    Luecke(regel=8, ebene="P", code=code, merkmal=feld, pdf_seite=erste_seite)
                )

        geprueft += 1
        leistungen = produkt.get("leistungen")
        if not isinstance(leistungen, list) or not leistungen:
            luecken.append(
                Luecke(regel=8, ebene="P", code=code, merkmal="leistungen", pdf_seite=erste_seite)
            )

        geprueft += 1
        if produkt.get("bindungsgrad") not in _REGEL8_BINDUNGSGRAD_VOKABULAR:
            luecken.append(
                Luecke(regel=8, ebene="P", code=code, merkmal="bindungsgrad", pdf_seite=erste_seite)
            )

        geprueft += 1
        if not pdf_seiten:
            luecken.append(
                Luecke(regel=8, ebene="P", code=code, merkmal="pdf_seiten", pdf_seite=None)
            )

        geprueft += 1
        if ergebnisplan.filter((pl.col("ebene") == "P") & (pl.col("code") == code)).height == 0:
            luecken.append(
                Luecke(
                    regel=8,
                    ebene="P",
                    code=code,
                    merkmal="teilergebnisplan",
                    pdf_seite=erste_seite,
                )
            )

        geprueft += 1
        if finanzplan.filter((pl.col("ebene") == "P") & (pl.col("code") == code)).height == 0:
            luecken.append(
                Luecke(
                    regel=8, ebene="P", code=code, merkmal="teilfinanzplan", pdf_seite=erste_seite
                )
            )

    return Regelergebnis(
        regel=8,
        titel="Regel 8 – Vollständigkeit der Produkte",
        geprueft=geprueft,
        abweichungen=(),
        luecken=tuple(luecken),
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
    produkte = lies_produkte_json(daten_wurzel / PRODUKTE_JSON)
    verbindlichkeiten_roh = lies_vorbericht_csv(daten_wurzel / VERBINDLICHKEITEN_CSV)
    erwartete_verbindlichkeiten_tabellen = {"verbindlichkeiten", "buergschaften"}
    tatsaechliche_verbindlichkeiten_tabellen = set(
        verbindlichkeiten_roh["tabelle"].unique().to_list()
    )
    if tatsaechliche_verbindlichkeiten_tabellen != erwartete_verbindlichkeiten_tabellen:
        raise PruefungsFehler(
            "Regel 5: verbindlichkeiten.csv hat eine abweichende Tabellenmenge (gefunden: "
            f"{sorted(tatsaechliche_verbindlichkeiten_tabellen)}, erwartet: "
            f"{sorted(erwartete_verbindlichkeiten_tabellen)})"
        )
    eigenkapital = lies_eigenkapital_csv(daten_wurzel / EIGENKAPITAL_CSV)
    ve_uebersicht = lies_ve_uebersicht_csv(daten_wurzel / VE_UEBERSICHT_CSV)
    stellenplan = lies_stellenplan_csv(daten_wurzel / STELLENPLAN_CSV)
    vorbericht = {
        "steuerarten": lies_vorbericht_csv(daten_wurzel / STEUERARTEN_CSV),
        "zuwendungen": lies_vorbericht_csv(daten_wurzel / ZUWENDUNGEN_CSV),
        "transferaufwendungen": lies_vorbericht_csv(daten_wurzel / TRANSFERAUFWENDUNGEN_CSV),
        "kita_zuschuesse": lies_vorbericht_csv(daten_wurzel / KITA_ZUSCHUESSE_CSV),
        **zerlege_weitere_vorberichtstabellen(
            lies_vorbericht_csv(daten_wurzel / WEITERE_VORBERICHTSTABELLEN_CSV)
        ),
        "verbindlichkeiten": verbindlichkeiten_roh.filter(pl.col("tabelle") == "verbindlichkeiten"),
        "buergschaften": verbindlichkeiten_roh.filter(pl.col("tabelle") == "buergschaften"),
    }
    meta = lies_meta_json(daten_wurzel / META_JSON)
    eckwerte = sollwerte.get("eckwerte", {})
    pruefe_eckwerte_konsumiert(eckwerte)
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
        steuerarten=vorbericht["steuerarten"],
        transferaufwendungen=vorbericht["transferaufwendungen"],
    )
    regel5 = _pruefe_regel5(
        vorbericht=vorbericht,
        planwerte_ergebnisplan=Planwerte(ergebnisplan, datei="ergebnisplan"),
        ergebnisplan=ergebnisplan,
        jahrgang=jahrgang,
        meta=meta,
        eckwerte=eckwerte,
    )
    geprueft_d11, abweichungen_d11, luecken_d11 = pruefe_regel5_schulden_ruecklagen_ve(
        verbindlichkeiten=vorbericht["verbindlichkeiten"],
        eigenkapital=eigenkapital,
        ve_uebersicht=ve_uebersicht,
        ve_faelligkeiten=ve_faelligkeiten,
        planwerte_ergebnisplan=Planwerte(ergebnisplan, datei="ergebnisplan"),
        planwerte_finanzplan=Planwerte(finanzplan, datei="finanzplan"),
        eckwerte=eckwerte,
        haushaltsjahr=jahrgang.haushaltsjahr,
    )
    regel5 = replace(
        regel5,
        geprueft=regel5.geprueft + geprueft_d11,
        abweichungen=regel5.abweichungen + tuple(abweichungen_d11),
        luecken=regel5.luecken + tuple(luecken_d11),
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
    regel8 = _pruefe_regel8(
        produkte=produkte,
        ergebnisplan=ergebnisplan,
        finanzplan=finanzplan,
        hierarchie=hierarchie,
        jahrgang=jahrgang,
    )
    regel9 = _pruefe_regel9(
        eckwerte=eckwerte,
        meta=meta,
        zuwendungen=vorbericht["zuwendungen"],
        verbindlichkeiten=vorbericht["verbindlichkeiten"],
        stellenplan=stellenplan,
        haushaltsjahr=jahrgang.haushaltsjahr,
    )
    regel10 = _pruefe_regel10(stellenplan=stellenplan, haushaltsjahr=jahrgang.haushaltsjahr)

    regeln, veraltete_befunde = _wende_befunde_an(
        (regel1, regel2, regel3, regel4, regel5, regel6, regel7, regel8, regel9, regel10),
        befunde,
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
