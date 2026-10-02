"""Schritt 04: Investitionsmaßnahmen und VE-Fälligkeiten (Spez. 3.8, 4.2, 5.2).

Liest die "Investitionsmaßnahmen (in C)"-Tabellen der Produktseiten (Teilergebnisplan-,
Teilfinanzplan- und Investitionen-Produktseiten, Research Pitfall 7: die Tabelle kann
mitten auf einer als `teilfinanzplan` klassifizierten Seite beginnen) und schreibt
`investitionen.csv` (nur Kontozeilen, D-08) sowie `ve_faelligkeiten.csv` (die
"(Kassenwirksamkeit)"-Werte, nie in `investitionen.csv` oder einer Summe, EXTR-09).

Zusätzlich liest derselbe Parser (`lies_massnahmen`) die PB-Investitionslisten
(Seitentyp `investitionen_pb`, ebene="PB") und schreibt sie nach
`daten/zwischen/investitionen_pb.csv` (D-06). Das ist eine reine Kontrollquelle für die
Regel-6-Gegenprobe (pruefung.py) — nichts aus den PB-Listen fließt in `investitionen.csv`
oder `ve_faelligkeiten.csv` ein; Quelle für diese beiden Dateien bleiben ausschließlich
die Produktseiten (D-06, Spez. 3.8).

Jede gedruckte Zwischen- und Saldozeile (Einzahlungen/Auszahlungen aus Investitions-
tätigkeit, Saldo <ID>, Saldo Investitionstätigkeit) wird als Gegenprobe geprüft, aber
nicht gespeichert (D-08); ein Verstoß bricht mit `S. {pdf_seite}: ` ab.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, replace
from pathlib import Path

import polars as pl

from ostbevern.freitext import ersetze_eurozeichen, verbinde_zeilen
from ostbevern.konfiguration import Jahrgang, layout_text
from ostbevern.pdf import PdfDokument, Textzeile, Wort
from ostbevern.schema import (
    DATEN_WURZEL,
    FINANZPLAN_CSV,
    INVESTITIONEN_CSV,
    INVESTITIONEN_PB_CSV,
    SEITEN_CSV,
    VE_FAELLIGKEITEN_CSV,
    lies_plan_csv,
    lies_seiten_csv,
    schreibe_investitionen_csv,
    schreibe_investitionen_pb_csv,
    schreibe_ve_faelligkeiten_csv,
    zerlege_spaltenkopf,
)
from ostbevern.spalten import SpaltenFehler, ordne_spalten
from ostbevern.zahlen import ist_betrag, lies_betrag, trenne_angeklebten_betrag

# Interne Toleranz für Gegenproben (Saldo-Zeile, Summenzeile), identisch zu
# pruefung.TOLERANZ_EURO; eigenständig definiert, damit investitionen.py (Schritt 04)
# nicht von pruefung.py (Schritt 06) abhängt.
_TOLERANZ_EURO = 1

# Seitentypen, deren Zeilen nach einer Investitionsmaßnahmen-Tabelle durchsucht werden
# (Research Pitfall 7: die Tabelle kann auf einer teilfinanzplan-Seite beginnen).
_PRODUKTSEITEN_TYPEN = ("teilergebnisplan", "teilfinanzplan", "investitionen_produkt")

# Dieselbe Pitfall-7-Vorsicht für PB-Knoten (D-06): die PB-Investitionsliste trägt den
# Seitentyp `investitionen_pb`; `teilergebnisplan`/`teilfinanzplan` sind defensiv mit
# aufgenommen, auch wenn sie auf PB-Ebene im 2026er Jahrgang keine Tabelle enthalten.
_PBSEITEN_TYPEN = ("investitionen_pb", "teilergebnisplan", "teilfinanzplan")


class InvestitionenFehler(ValueError):
    """Wird ausgelöst, wenn eine Investitionsmaßnahmen-Seite oder -Zeile nicht lesbar ist."""


@dataclass(frozen=True)
class Kontengruppe:
    """Fachliche Zuordnung eines Kontengruppen-Präfixes (D-07, NKF-Kontenrahmen).

    `art` ist `None` für Finanzierungstätigkeit (692/792), die keinen Investitions-`art`-
    Wert trägt und nicht in investitionen.csv geschrieben wird (D-07/D-08).
    """

    richtung: str
    taetigkeit: str
    art: str | None


# Kontengruppen-Tabelle (D-07, fachliche Regel im Code, keine Jahrgangskonfiguration):
# längstes passendes Präfix gewinnt (klassifiziere_konto). Das `art`-Vokabular wird von
# Phase 4 (App-JSON) und Phase 6 (/investitionen-Filter, Spez. 6.10) konsumiert; eine
# spätere Umbenennung ist teuer (Reversibility: costly, D-07).
KONTENGRUPPEN: dict[str, Kontengruppe] = {
    "681": Kontengruppe("einzahlung", "investition", "zuwendungen"),
    "682": Kontengruppe("einzahlung", "investition", "grundstuecke"),
    "683": Kontengruppe("einzahlung", "investition", "ausstattung"),
    "684": Kontengruppe("einzahlung", "investition", "finanzanlagen"),
    "688": Kontengruppe("einzahlung", "investition", "beitraege"),
    "692": Kontengruppe("einzahlung", "finanzierung", None),
    "781": Kontengruppe("auszahlung", "investition", "investitionszuschuesse"),
    # 782111 (erworbene immaterielle Vermögensgegenstände) vor dem allgemeinen 782-Präfix
    # (Grundstücke), da das Präfix-Matching nach Länge sortiert ist (längstes gewinnt).
    "782111": Kontengruppe("auszahlung", "investition", "immaterielles"),
    "782": Kontengruppe("auszahlung", "investition", "grundstuecke"),
    "783": Kontengruppe("auszahlung", "investition", "ausstattung"),
    "784": Kontengruppe("auszahlung", "investition", "finanzanlagen"),
    "785": Kontengruppe("auszahlung", "investition", "bau"),
    "792": Kontengruppe("auszahlung", "finanzierung", None),
}


def klassifiziere_konto(konto: str, pdf_seite: int) -> Kontengruppe:
    """Ordnet `konto` über das längste passende Präfix aus KONTENGRUPPEN zu (D-07).

    Ein unbekanntes Konto bricht ab (D-08); kein stillschweigender Standardwert.
    """
    for praefix in sorted(KONTENGRUPPEN, key=len, reverse=True):
        if konto.startswith(praefix):
            return KONTENGRUPPEN[praefix]
    raise InvestitionenFehler(
        f"S. {pdf_seite}: Konto {konto} gehört zu keiner bekannten Kontengruppe (D-07)"
    )


@dataclass(frozen=True)
class Kontozeile:
    """Eine Konto-Zeile einer Investitionsmaßnahme (die einzige Granularität, die in
    investitionen.csv geschrieben wird, D-08)."""

    konto: str
    konto_name: str
    gruppe: Kontengruppe
    werte: tuple[int | None, ...]
    faelligkeiten: tuple[tuple[int, int], ...]
    pdf_seite: int


@dataclass(frozen=True)
class Massnahme:
    """Eine Investitionsmaßnahme (ein Block zwischen Kopfzeile und Saldo-Zeile, D-08)."""

    ebene: str
    code: str
    massnahme_id: str
    massnahme_name: str
    konten: tuple[Kontozeile, ...]
    saldo: tuple[int, ...]
    pdf_seite: int


@dataclass
class _RohKontozeile:
    """Veränderlicher Baustein für eine Kontozeile, während ihr Name noch wächst
    (Fortsetzungszeilen) und ihre Fälligkeiten noch gesammelt werden (Task 2)."""

    konto: str
    name_zeilen: list[str]
    gruppe: Kontengruppe
    werte: tuple[int | None, ...]
    faelligkeiten: list[tuple[int, int]]
    pdf_seite: int


@dataclass
class _OffenerBlock:
    """Zustand einer offenen Investitionsmaßnahme zwischen Kopfzeile und Saldo-Zeile.

    `header_erste_zeile` behält die Wort-Objekte der ERSTEN Kopfzeile (nicht schon zu
    Text zusammengefügt), damit die Maßnahmen-ID beim Blockschluss wortgenau von ihr
    abgetrennt werden kann (Research Pattern 4); `header_fortsetzung` sind bereits
    Zeilen-Text gewordene weitere Kopfzeilen (vor der ersten Kontozeile).
    """

    header_erste_zeile: list[Wort]
    pdf_seite: int
    header_fortsetzung: list[str] = None  # type: ignore[assignment]
    konten: list[_RohKontozeile] = None  # type: ignore[assignment]
    offene_einzahlung: list[int | None] | None = None
    offene_auszahlung: list[int | None] | None = None

    def __post_init__(self) -> None:
        if self.konten is None:
            self.konten = []
        if self.header_fortsetzung is None:
            self.header_fortsetzung = []

    def header_text_ns(self) -> str:
        """Space-freie Konkatenation aller Kopfzeilen (für die ID-Präfix-Prüfung)."""
        erste = "".join(w.text for w in self.header_erste_zeile)
        rest = "".join("".join(t.split()) for t in self.header_fortsetzung)
        return erste + rest


def _teile_feste_laenge(woerter: Sequence[Wort], laenge: int) -> tuple[str, list[Wort]]:
    """Konsumiert führende Wörter (space-frei), bis `laenge` Zeichen erreicht sind.

    Ein Wort, das die Grenze überschreitet, wird gesplittet: der Rest wird als
    Pseudo-Wort (gleiche Koordinaten, gekürzter Text) vorangestellt (Research Pattern 4).
    """
    konsumiert = ""
    for index, wort in enumerate(woerter):
        text = wort.text
        if len(konsumiert) + len(text) < laenge:
            konsumiert += text
            continue
        grenze = laenge - len(konsumiert)
        konto = konsumiert + text[:grenze]
        rest_text = text[grenze:]
        rest_woerter = list(woerter[index + 1 :])
        if rest_text:
            rest_woerter = [replace(wort, text=rest_text), *rest_woerter]
        return konto, rest_woerter
    return konsumiert, []


def _teile_bis_ziel(woerter: Sequence[Wort], ziel: str, *, pdf_seite: int) -> list[Wort]:
    """Konsumiert führende Wörter (space-frei), bis die Konkatenation `ziel` erreicht;
    gibt die restlichen Wörter zurück (Research Pattern 4, D-08)."""
    konsumiert = ""
    for index, wort in enumerate(woerter):
        text = wort.text
        neu = konsumiert + text
        if neu == ziel:
            return list(woerter[index + 1 :])
        if len(neu) > len(ziel):
            grenze = len(ziel) - len(konsumiert)
            if konsumiert + text[:grenze] != ziel:
                raise InvestitionenFehler(
                    f"S. {pdf_seite}: Kopfzeile beginnt nicht mit der Maßnahmen-ID {ziel!r}"
                )
            rest_text = text[grenze:]
            rest_woerter = list(woerter[index + 1 :])
            if rest_text:
                rest_woerter = [replace(wort, text=rest_text), *rest_woerter]
            return rest_woerter
        konsumiert = neu
    raise InvestitionenFehler(
        f"S. {pdf_seite}: Kopfzeile beginnt nicht mit der Maßnahmen-ID {ziel!r}"
    )


def _zeilentext(woerter: Sequence[Wort]) -> str:
    return " ".join(wort.text for wort in woerter)


def _addiere(
    summe: list[int | None], werte: dict[int, int | None], anzahl: int
) -> list[int | None]:
    ergebnis = list(summe) if summe else [0] * anzahl
    for index in range(anzahl):
        wert = werte.get(index)
        if wert is not None:
            ergebnis[index] = (ergebnis[index] or 0) + wert
    return ergebnis


def _werte_stimmen_ueberein(a: Sequence[int | None], b: Sequence[int | None]) -> bool:
    return all(abs((x or 0) - (y or 0)) <= _TOLERANZ_EURO for x, y in zip(a, b, strict=True))


def _ordne_investitionswerte(
    amount_woerter: list[Wort],
    anker_x1: tuple[float, ...],
    *,
    pdf_seite: int,
    bezeichner: str,
) -> dict[int, int | None]:
    try:
        zugeordnet = ordne_spalten(amount_woerter, anker_x1)
    except SpaltenFehler as fehler:
        raise InvestitionenFehler(f"S. {pdf_seite}: {bezeichner}: {fehler}") from fehler
    return {index: lies_betrag(wort.text) for index, wort in zugeordnet.items()}


def _trenne_label_und_betraege(
    zeile: Textzeile, *, erste_jahresspalte_x0: float
) -> tuple[list[Wort], list[Wort]]:
    """Trennt eine Zeile in Label- und Betragswörter (Research Pattern 1, plaene-Parität).

    Ein Label-Wort in der Betragszone mit angeklebtem Betrag (Spez. 3.8) wird aufgeteilt:
    der Textteil bleibt im Label, der Zahlenteil wird als eigenes Betragswort geführt.
    """
    amount_woerter = [
        w for w in zeile.woerter if w.x1 > erste_jahresspalte_x0 and ist_betrag(w.text)
    ]
    amount_set = set(amount_woerter)
    label_woerter: list[Wort] = []
    alle_amount_woerter = list(amount_woerter)
    for wort in zeile.woerter:
        if wort in amount_set:
            continue
        if wort.x1 > erste_jahresspalte_x0:
            rest_text, betrag_text = trenne_angeklebten_betrag(wort.text)
            if betrag_text is not None:
                if rest_text:
                    label_woerter.append(replace(wort, text=rest_text))
                alle_amount_woerter.append(replace(wort, text=betrag_text))
                continue
        label_woerter.append(wort)
    return label_woerter, alle_amount_woerter


def lies_massnahmen(
    dokument: PdfDokument,
    jahrgang: Jahrgang,
    seiten_nummern: Sequence[int],
    *,
    ebene: str,
    code: str,
) -> tuple[list[Massnahme], tuple[int, ...] | None]:
    """Parst alle Investitionsmaßnahmen-Tabellen der gegebenen Seiten eines Knotens.

    Gibt (Maßnahmen, Saldo-Investitionstätigkeit-Gesamtwert-oder-None) zurück. Trägt eine
    der gegebenen Seiten keine Tabelle, wird sie übersprungen; trägt keine, ist das
    Ergebnis ([], None) (EXTR-09, Flagged assumption).
    """
    tabellenkopf = layout_text(jahrgang, "investitionen", "tabellenkopf")
    einzahlungen_summe = layout_text(jahrgang, "investitionen", "einzahlungen_summe")
    auszahlungen_summe = layout_text(jahrgang, "investitionen", "auszahlungen_summe")
    saldo_praefix = layout_text(jahrgang, "investitionen", "saldo_praefix")
    saldo_gesamt = layout_text(jahrgang, "investitionen", "saldo_gesamt")
    kassenwirksamkeit = layout_text(jahrgang, "investitionen", "kassenwirksamkeit")
    spalten = jahrgang.spalten["investitionen"]
    anzahl_spalten = len(spalten)
    fortsetzung_normalisiert = "".join(jahrgang.kopfzeilen.fortsetzung.split())
    # "Saldo Investitionstätigkeit" (Knoten-Gesamtwert) wird nur in den Budget-Spalten
    # gegen die Summe der Maßnahmen-Saldi geprüft, nicht in "Ergebnis" (Ist-Werte des
    # Vorjahres): verifiziert gegen S. 157 (Produkt 030102) druckt die Zeile "Saldo
    # Investitionstätigkeit" in der Ergebnis-Spalte einen Wert, der exakt dem Teilfinanz-
    # plan Z. 31 entspricht, während die Summe der drei gedruckten Maßnahmen-Saldi
    # derselben Spalte deutlich abweicht — dieselbe Art Differenz wie bei den
    # Finanzierungs-Konten (siehe extrahiere_investitionen), eine echte, im PDF selbst so
    # gedruckte historische Ist-Differenz, kein Extraktionsfehler.
    budget_indizes = [
        index
        for index in range(anzahl_spalten)
        if zerlege_spaltenkopf(spalten[index])[0] != "ergebnis"
    ]

    massnahmen: list[Massnahme] = []
    # (gedruckte Werte, pdf_seite) der "Saldo Investitionstätigkeit"-Zeile, oder None, falls
    # sie nicht vorkommt; gegen die Summe ALLER Maßnahmen erst nach dem Lesen aller Seiten
    # geprüft (siehe Kommentar an der Fundstelle, Research Pitfall 8/D-08).
    saldo_gesamt_gedruckt: tuple[list[int | None], int] | None = None
    block: _OffenerBlock | None = None

    def _schliesse_block(ziel_id: str, saldo_werte: dict[int, int | None], pdf_seite: int) -> None:
        nonlocal block
        assert block is not None
        if block.offene_einzahlung is not None or block.offene_auszahlung is not None:
            raise InvestitionenFehler(
                f"S. {pdf_seite}: Saldo {ziel_id} schließt Maßnahme mit offener "
                "Kontogruppe ohne vorherige Summenzeile (taetigkeit investition)"
            )
        if not block.konten:
            raise InvestitionenFehler(f"S. {pdf_seite}: Saldo {ziel_id} ohne Kontozeilen")
        erwartete_saldo = [0] * anzahl_spalten
        for konto in block.konten:
            for index in range(anzahl_spalten):
                wert = konto.werte[index]
                if wert is None:
                    continue
                vorzeichen = 1 if konto.gruppe.richtung == "einzahlung" else -1
                erwartete_saldo[index] = (erwartete_saldo[index] or 0) + vorzeichen * wert
        gedruckter_saldo = [saldo_werte.get(index) for index in range(anzahl_spalten)]
        if not _werte_stimmen_ueberein(erwartete_saldo, gedruckter_saldo):
            raise InvestitionenFehler(
                f"S. {pdf_seite}: Saldo {ziel_id} ({gedruckter_saldo}) stimmt nicht mit der "
                f"Summe der Kontozeilen ({erwartete_saldo}) überein"
            )
        konten = tuple(
            Kontozeile(
                konto=roh.konto,
                konto_name=ersetze_eurozeichen(verbinde_zeilen(roh.name_zeilen))
                if roh.name_zeilen
                else "",
                gruppe=roh.gruppe,
                werte=roh.werte,
                faelligkeiten=tuple(roh.faelligkeiten),
                pdf_seite=roh.pdf_seite,
            )
            for roh in block.konten
        )
        rest_woerter = _teile_bis_ziel(block.header_erste_zeile, ziel_id, pdf_seite=pdf_seite)
        name_zeilen = [t for t in [_zeilentext(rest_woerter), *block.header_fortsetzung] if t]
        header_text = ersetze_eurozeichen(verbinde_zeilen(name_zeilen)) if name_zeilen else ""
        massnahmen.append(
            Massnahme(
                ebene=ebene,
                code=code,
                massnahme_id=ziel_id,
                massnahme_name=header_text,
                konten=konten,
                saldo=tuple(wert or 0 for wert in erwartete_saldo),
                pdf_seite=block.pdf_seite,
            )
        )
        block = None

    for pdf_seite in seiten_nummern:
        zeilen = dokument.zeilen_fein(pdf_seite)
        anker_x1: tuple[float, ...] | None = None
        erste_jahresspalte_x0: float | None = None
        index = 0

        while index < len(zeilen):
            zeile = zeilen[index]
            text_ns = zeile.text_ohne_leerzeichen

            if text_ns.startswith(tabellenkopf):
                # Jede Seite druckt den Tabellenkopf neu, auch bei einer zweiten,
                # eigenständigen Tabelle auf derselben Seite (Research: Produkt 160101,
                # S. 282, Finanzierungstätigkeit); Anker werden deshalb bei JEDEM
                # Vorkommen neu bestimmt, nicht nur beim ersten auf der Seite.
                jahreszeile = zeilen[index + 1]
                label_woerter = _teile_bis_ziel(zeile.woerter, tabellenkopf, pdf_seite=pdf_seite)
                jahreswoerter = jahreszeile.woerter
                if len(label_woerter) != anzahl_spalten or len(jahreswoerter) != anzahl_spalten:
                    raise InvestitionenFehler(
                        f"S. {pdf_seite}: {len(label_woerter)} Spaltenbezeichnungen, "
                        f"{len(jahreswoerter)} Jahreszahlen, erwartet {anzahl_spalten}"
                    )
                gelesene_spalten = [
                    f"{label.text} {jahr.text}"
                    for label, jahr in zip(label_woerter, jahreswoerter, strict=True)
                ]
                if tuple(gelesene_spalten) != tuple(spalten):
                    raise InvestitionenFehler(
                        f"S. {pdf_seite}: Spaltenköpfe {gelesene_spalten} weichen von "
                        f"{tuple(spalten)} ab"
                    )
                anker_x1 = tuple(wort.x1 for wort in jahreswoerter)
                erste_jahresspalte_x0 = jahreswoerter[0].x0
                index += 2
                continue

            if anker_x1 is None or erste_jahresspalte_x0 is None:
                # Noch vor dem (ersten) Tabellenkopf dieser Seite: regulärer Teilplan-
                # Inhalt, der hier nicht interessiert.
                index += 1
                continue

            if text_ns == str(pdf_seite) or text_ns.startswith(fortsetzung_normalisiert):
                break

            label_woerter_zeile, amount_woerter = _trenne_label_und_betraege(
                zeile, erste_jahresspalte_x0=erste_jahresspalte_x0
            )
            label_text_ns = "".join(w.text for w in label_woerter_zeile)

            if label_text_ns.startswith(kassenwirksamkeit):
                if block is None or not block.konten:
                    raise InvestitionenFehler(
                        f"S. {pdf_seite}: {kassenwirksamkeit} ohne vorherige Kontozeile"
                    )
                letzte_konto = block.konten[-1]
                # Rohwerte inkl. Klammern/"–" (ist_betrag lehnt "(...)" ab, daher eigene
                # Erkennung hier statt über _trenne_label_und_betraege).
                kasse_woerter = [
                    w
                    for w in zeile.woerter
                    if w.x1 > erste_jahresspalte_x0
                    and (
                        (w.text.startswith("(") and w.text.endswith(")") and len(w.text) > 2)
                        or w.text == "–"
                    )
                ]
                entpackt = [
                    replace(w, text=w.text[1:-1]) if w.text.startswith("(") else w
                    for w in kasse_woerter
                ]
                zugeordnet = _ordne_investitionswerte(
                    entpackt, anker_x1, pdf_seite=pdf_seite, bezeichner=kassenwirksamkeit
                )
                for spalten_index, betrag in zugeordnet.items():
                    if betrag is None:
                        continue
                    wertart, jahr = zerlege_spaltenkopf(spalten[spalten_index])
                    if wertart != "planung":
                        raise InvestitionenFehler(
                            f"S. {pdf_seite}: {kassenwirksamkeit} unter Spalte "
                            f"{spalten[spalten_index]!r} (nicht Planung)"
                        )
                    letzte_konto.faelligkeiten.append((jahr, betrag))
                index += 1
                continue

            ist_konto = (
                bool(label_woerter_zeile)
                and label_woerter_zeile[0].text[:1].isdigit()
                and len(amount_woerter) == anzahl_spalten
            )
            if ist_konto:
                if block is None:
                    raise InvestitionenFehler(f"S. {pdf_seite}: Kontozeile ohne Kopfzeile")
                konto, rest_woerter = _teile_feste_laenge(label_woerter_zeile, 6)
                if len(konto) != 6 or not konto.isdigit():
                    raise InvestitionenFehler(
                        f"S. {pdf_seite}: Kontozeile ohne 6-stelliges Konto: {label_text_ns!r}"
                    )
                gruppe = klassifiziere_konto(konto, pdf_seite)
                werte_dict = _ordne_investitionswerte(
                    amount_woerter, anker_x1, pdf_seite=pdf_seite, bezeichner=f"Konto {konto}"
                )
                if len(werte_dict) != anzahl_spalten:
                    raise InvestitionenFehler(
                        f"S. {pdf_seite}: Konto {konto} hat nur {len(werte_dict)} von "
                        f"{anzahl_spalten} Spalten zugeordnet"
                    )
                werte = tuple(werte_dict[index] for index in range(anzahl_spalten))

                if gruppe.taetigkeit == "investition":
                    if gruppe.richtung == "einzahlung":
                        if block.offene_auszahlung is not None:
                            raise InvestitionenFehler(
                                f"S. {pdf_seite}: Konto {konto} (einzahlung) während eine "
                                "offene Auszahlungsgruppe auf eine Summenzeile wartet"
                            )
                        block.offene_einzahlung = _addiere(
                            block.offene_einzahlung, werte_dict, anzahl_spalten
                        )
                    else:
                        if block.offene_einzahlung is not None:
                            raise InvestitionenFehler(
                                f"S. {pdf_seite}: Konto {konto} (auszahlung) während eine "
                                "offene Einzahlungsgruppe auf eine Summenzeile wartet"
                            )
                        block.offene_auszahlung = _addiere(
                            block.offene_auszahlung, werte_dict, anzahl_spalten
                        )

                block.konten.append(
                    _RohKontozeile(
                        konto=konto,
                        name_zeilen=[_zeilentext(rest_woerter)] if rest_woerter else [],
                        gruppe=gruppe,
                        werte=werte,
                        faelligkeiten=[],
                        pdf_seite=pdf_seite,
                    )
                )
                index += 1
                continue

            ist_summe = label_text_ns in (einzahlungen_summe, auszahlungen_summe) and bool(
                amount_woerter
            )
            if ist_summe:
                if block is None:
                    raise InvestitionenFehler(f"S. {pdf_seite}: Summenzeile ohne offenen Block")
                erwartete_richtung = (
                    "einzahlung" if label_text_ns == einzahlungen_summe else "auszahlung"
                )
                offene = (
                    block.offene_einzahlung
                    if erwartete_richtung == "einzahlung"
                    else block.offene_auszahlung
                )
                if offene is None:
                    raise InvestitionenFehler(
                        f"S. {pdf_seite}: Summenzeile {label_text_ns!r} ohne offene "
                        f"{erwartete_richtung}-Kontogruppe"
                    )
                summen_dict = _ordne_investitionswerte(
                    amount_woerter, anker_x1, pdf_seite=pdf_seite, bezeichner=label_text_ns
                )
                summen_werte = [summen_dict.get(index) for index in range(anzahl_spalten)]
                if not _werte_stimmen_ueberein(summen_werte, offene):
                    raise InvestitionenFehler(
                        f"S. {pdf_seite}: Summenzeile {label_text_ns!r} ({summen_werte}) "
                        f"stimmt nicht mit den Kontozeilen ({offene}) überein"
                    )
                if erwartete_richtung == "einzahlung":
                    block.offene_einzahlung = None
                else:
                    block.offene_auszahlung = None
                index += 1
                continue

            if label_text_ns.startswith(saldo_gesamt) and amount_woerter:
                if saldo_gesamt_gedruckt is not None:
                    raise InvestitionenFehler(f"S. {pdf_seite}: {saldo_gesamt} kommt zweimal vor")
                if block is not None:
                    raise InvestitionenFehler(
                        f"S. {pdf_seite}: {saldo_gesamt}, während ein Maßnahmenblock offen ist"
                    )
                gesamt_dict = _ordne_investitionswerte(
                    amount_woerter, anker_x1, pdf_seite=pdf_seite, bezeichner=saldo_gesamt
                )
                if len(gesamt_dict) != anzahl_spalten:
                    raise InvestitionenFehler(
                        f"S. {pdf_seite}: {saldo_gesamt} hat nur {len(gesamt_dict)} von "
                        f"{anzahl_spalten} Spalten zugeordnet"
                    )
                # Validierung gegen die Summe ALLER Maßnahmen-Saldi erst nach dem Lesen aller
                # Seiten (siehe unten): auf PB-Listen druckt diese Zeile den GESAMT-Saldo des
                # ganzen Knotens mitten in der Liste, vor noch nicht gelesenen Maßnahmen
                # (Research Pitfall 8/D-08, verifiziert gegen S. 235 PB 12 = TFP Z. 31).
                saldo_gesamt_gedruckt = (
                    [gesamt_dict[spalten_index] for spalten_index in range(anzahl_spalten)],
                    pdf_seite,
                )
                index += 1
                continue

            if label_text_ns.startswith(saldo_praefix) and amount_woerter:
                if block is None:
                    raise InvestitionenFehler(f"S. {pdf_seite}: Saldo-Zeile ohne offenen Block")
                ziel_id = label_text_ns[len(saldo_praefix) :]
                header_ns = block.header_text_ns()
                if not header_ns.startswith(ziel_id):
                    raise InvestitionenFehler(
                        f"S. {pdf_seite}: Kopfzeile {header_ns!r} beginnt nicht mit der "
                        f"Maßnahmen-ID {ziel_id!r}"
                    )
                saldo_dict = _ordne_investitionswerte(
                    amount_woerter, anker_x1, pdf_seite=pdf_seite, bezeichner=f"Saldo {ziel_id}"
                )
                if len(saldo_dict) != anzahl_spalten:
                    raise InvestitionenFehler(
                        f"S. {pdf_seite}: Saldo {ziel_id} hat nur {len(saldo_dict)} von "
                        f"{anzahl_spalten} Spalten zugeordnet"
                    )
                _schliesse_block(ziel_id, saldo_dict, pdf_seite)
                index += 1
                continue

            if not amount_woerter:
                if block is None:
                    # Kopfzeile einer neuen Maßnahme (am Tabellenanfang oder direkt nach
                    # einer Saldo-Zeile).
                    block = _OffenerBlock(
                        header_erste_zeile=list(label_woerter_zeile), pdf_seite=pdf_seite
                    )
                elif not block.konten:
                    # weitere Kopfzeile desselben (noch unvollständigen) Headers.
                    block.header_fortsetzung.append(_zeilentext(label_woerter_zeile))
                else:
                    # Fortsetzungszeile des Namens der letzten Kontozeile.
                    block.konten[-1].name_zeilen.append(_zeilentext(label_woerter_zeile))
                index += 1
                continue

            raise InvestitionenFehler(f"S. {pdf_seite}: unerwartete Zeile: {zeile.text!r}")

    if block is not None:
        raise InvestitionenFehler(
            f"S. {seiten_nummern[-1] if seiten_nummern else '?'}: Maßnahmenblock "
            f"{block.header_text_ns()!r} am Ende der Seiten noch offen"
        )

    saldo_gesamt_wert: tuple[int, ...] | None = None
    if saldo_gesamt_gedruckt is not None:
        gedruckt, saldo_pdf_seite = saldo_gesamt_gedruckt
        erwartet = [0] * anzahl_spalten
        for massnahme in massnahmen:
            if any(konto.gruppe.taetigkeit != "investition" for konto in massnahme.konten):
                # Finanzierungstätigkeit-Maßnahmen (692/792) zählen nicht zur "Saldo
                # Investitionstätigkeit" (eigener Tätigkeitsbereich im NKF-Finanzplan);
                # verifiziert gegen Produkt 160101/PB 16, S. 279/282, wo diese Zeile
                # zwischen den Investitions- und den Finanzierungs-Maßnahmen gedruckt wird.
                continue
            for spalten_index in range(anzahl_spalten):
                erwartet[spalten_index] += massnahme.saldo[spalten_index]
        erwartet_budget = [erwartet[i] for i in budget_indizes]
        gedruckt_budget = [gedruckt[i] for i in budget_indizes]
        if not _werte_stimmen_ueberein(erwartet_budget, gedruckt_budget):
            raise InvestitionenFehler(
                f"S. {saldo_pdf_seite}: {saldo_gesamt} ({gedruckt}) stimmt nicht mit der "
                f"Summe der Maßnahmen-Saldi ({erwartet}) überein"
            )
        saldo_gesamt_wert = tuple(wert or 0 for wert in erwartet)

    return massnahmen, saldo_gesamt_wert


@dataclass(frozen=True)
class ExtraktionsErgebnis:
    """Ergebnis von `extrahiere_investitionen`: Anzahl geschriebener CSV-Zeilen und Pfad."""

    zeilen_geschrieben: int
    pfad: Path


def _trenne_investitions_und_finanzierungskonten(
    massnahmen: Sequence[Massnahme], *, anzahl_spalten: int
) -> tuple[list[tuple[Massnahme, Kontozeile]], list[int], list[int], bool]:
    """Trennt die Kontozeilen aller Maßnahmen eines Knotens (Produkt oder PB) in
    Investitions-Kontozeilen (`gruppe.taetigkeit == "investition"`, D-08) und
    Finanzierungs-Summen (692/792, `gruppe.taetigkeit == "finanzierung"`); wiederverwendet
    von der Produkt- und der PB-Verarbeitung in `extrahiere_investitionen` (D-06)."""
    investitions_konten: list[tuple[Massnahme, Kontozeile]] = []
    finanzierung_einzahlung = [0] * anzahl_spalten
    finanzierung_auszahlung = [0] * anzahl_spalten
    hat_finanzierung = False

    for massnahme in massnahmen:
        for konto in massnahme.konten:
            if konto.gruppe.taetigkeit == "finanzierung":
                hat_finanzierung = True
                ziel = (
                    finanzierung_einzahlung
                    if konto.gruppe.richtung == "einzahlung"
                    else finanzierung_auszahlung
                )
                for index in range(anzahl_spalten):
                    wert = konto.werte[index]
                    if wert is not None:
                        ziel[index] += wert
                continue
            investitions_konten.append((massnahme, konto))

    return investitions_konten, finanzierung_einzahlung, finanzierung_auszahlung, hat_finanzierung


def _pruefe_finanzierungskonten(
    *,
    finanzplan: pl.DataFrame,
    spalten: tuple[str, ...],
    budget_indizes: Sequence[int],
    ebene: str,
    code: str,
    finanzierung_einzahlung: Sequence[int],
    finanzierung_auszahlung: Sequence[int],
    letzte_seite: int,
) -> None:
    """Prüft die Finanzierungs-Konten (692/792) eines Knotens (Produkt `ebene="P"` oder
    PB `ebene="PB"`) gegen die Teilfinanzplan-Zeilen 33 (Einzahlung) und 35 (Auszahlung) in
    den Budget-Spalten (Ansatz, VE, Planung; die Spalte "Ergebnis" bleibt ausgenommen, siehe
    `extrahiere_investitionen`-Docstring). Wiederverwendet von Produkt- und PB-Verarbeitung
    (D-06)."""

    def _finanzplan_wert(zeile: str, index: int) -> int:
        wertart, jahr = zerlege_spaltenkopf(spalten[index])
        treffer = finanzplan.filter(
            (pl.col("ebene") == ebene)
            & (pl.col("code") == code)
            & (pl.col("zeile") == zeile)
            & (pl.col("jahr") == jahr)
            & (pl.col("wertart") == wertart)
        )
        if treffer.height == 0:
            return 0
        return treffer["betrag"][0]

    for index in budget_indizes:
        soll_ein = _finanzplan_wert("33", index)
        soll_aus = _finanzplan_wert("35", index)
        if abs(finanzierung_einzahlung[index] - soll_ein) > _TOLERANZ_EURO:
            raise InvestitionenFehler(
                f"S. {letzte_seite}: {ebene} {code}: Finanzierungs-Konten "
                f"(692) Spalte {spalten[index]!r} = {finanzierung_einzahlung[index]}, "
                f"Teilfinanzplan Zeile 33 = {soll_ein}"
            )
        if abs(finanzierung_auszahlung[index] - soll_aus) > _TOLERANZ_EURO:
            raise InvestitionenFehler(
                f"S. {letzte_seite}: {ebene} {code}: Finanzierungs-Konten "
                f"(792) Spalte {spalten[index]!r} = {finanzierung_auszahlung[index]}, "
                f"Teilfinanzplan Zeile 35 = {soll_aus}"
            )


def extrahiere_investitionen(
    jahrgang: Jahrgang, *, daten_wurzel: Path = DATEN_WURZEL
) -> tuple[ExtraktionsErgebnis, ExtraktionsErgebnis, ExtraktionsErgebnis]:
    """Liest alle Investitionsmaßnahmen der Produktseiten und schreibt investitionen.csv
    sowie ve_faelligkeiten.csv (EXTR-09, D-06, D-07, D-08); liest zusätzlich die
    PB-Investitionslisten mit demselben Parser und schreibt sie als Kontrollquelle nach
    investitionen_pb.csv (D-06, Spez. 3.8) — nichts davon fließt in investitionen.csv oder
    ve_faelligkeiten.csv ein.

    Je Produkt: der Saldo-Investitionstätigkeit-Gesamtwert (falls Investitions-Konten
    vorhanden sind) wird innerhalb von `lies_massnahmen` bereits gegen die Summe der
    Maßnahmen-Saldi geprüft; hier zusätzlich die Finanzierungs-Konten (692/792, falls
    vorhanden) gegen die Teilfinanzplan-Zeilen 33 (Einzahlung) und 35 (Auszahlung) in
    allen Budget-Spalten (Ansatz, VE, Planung). Die Spalte "Ergebnis" (Ist-Werte des
    Vorjahres) bleibt bewusst ausgenommen: verifiziert gegen S. 281/282 (Produkt 160101)
    druckt die Investitionsmaßnahmen-Tabelle für Konto 792711 (Tilgung) in dieser Spalte
    0 C, während der Teilfinanzplan (S. 281, Zeile 35) über 400.000 C ausweist — eine
    echte, im PDF selbst so gedruckte Differenz (historische Ist-Buchung auf einem heute
    nicht mehr geführten Konto), kein Extraktionsfehler.
    """
    seiten = lies_seiten_csv(daten_wurzel / SEITEN_CSV)
    finanzplan = lies_plan_csv(daten_wurzel / FINANZPLAN_CSV)
    spalten = jahrgang.spalten["investitionen"]
    anzahl_spalten = len(spalten)
    budget_indizes = [
        index
        for index in range(anzahl_spalten)
        if zerlege_spaltenkopf(spalten[index])[0] != "ergebnis"
    ]

    produkt_seiten = seiten.filter(
        pl.col("produkt").is_not_null() & pl.col("typ").is_in(_PRODUKTSEITEN_TYPEN)
    ).sort("pdf_seite")
    produkte = sorted(produkt_seiten["produkt"].unique().to_list())

    # PB-Knoten (D-06): pb gesetzt, pg und produkt leer (die PB-Investitionsliste selbst
    # hat beide Spalten leer, Research Planning-time facts); alle 15 PB haben mindestens
    # eine teilergebnisplan-Seite, auch PB 11/14 ohne eigene Investitionsliste (dort liefert
    # lies_massnahmen ([], None), EXTR-09 Flagged assumption).
    pb_seiten = seiten.filter(
        pl.col("pb").is_not_null()
        & pl.col("pg").is_null()
        & pl.col("produkt").is_null()
        & pl.col("typ").is_in(_PBSEITEN_TYPEN)
    ).sort("pdf_seite")
    pb_codes = sorted(pb_seiten["pb"].unique().to_list())

    investitionen_zeilen: list[dict[str, object]] = []
    faelligkeiten_zeilen: list[dict[str, object]] = []
    investitionen_pb_zeilen: list[dict[str, object]] = []

    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        for produkt in produkte:
            seiten_nummern = tuple(
                produkt_seiten.filter(pl.col("produkt") == produkt)["pdf_seite"].to_list()
            )
            massnahmen, _saldo_gesamt = lies_massnahmen(
                dokument, jahrgang, seiten_nummern, ebene="P", code=produkt
            )
            investitions_konten, finanzierung_ein, finanzierung_aus, hat_finanzierung = (
                _trenne_investitions_und_finanzierungskonten(
                    massnahmen, anzahl_spalten=anzahl_spalten
                )
            )

            for massnahme, konto in investitions_konten:
                for index in range(anzahl_spalten):
                    betrag = konto.werte[index]
                    if betrag is None:
                        continue
                    wertart, jahr = zerlege_spaltenkopf(spalten[index])
                    investitionen_zeilen.append(
                        {
                            "produkt": produkt,
                            "massnahme_id": massnahme.massnahme_id,
                            "massnahme_name": massnahme.massnahme_name,
                            "konto": konto.konto,
                            "konto_name": konto.konto_name,
                            "richtung": konto.gruppe.richtung,
                            "art": konto.gruppe.art,
                            "jahr": jahr,
                            "wertart": wertart,
                            "betrag": betrag,
                            "pdf_seite": konto.pdf_seite,
                        }
                    )
                for jahr, betrag in konto.faelligkeiten:
                    faelligkeiten_zeilen.append(
                        {
                            "produkt": produkt,
                            "massnahme_id": massnahme.massnahme_id,
                            "konto": konto.konto,
                            "jahr": jahr,
                            "betrag": betrag,
                            "pdf_seite": konto.pdf_seite,
                        }
                    )

            if hat_finanzierung:
                _pruefe_finanzierungskonten(
                    finanzplan=finanzplan,
                    spalten=spalten,
                    budget_indizes=budget_indizes,
                    ebene="P",
                    code=produkt,
                    finanzierung_einzahlung=finanzierung_ein,
                    finanzierung_auszahlung=finanzierung_aus,
                    letzte_seite=seiten_nummern[-1] if seiten_nummern else 0,
                )

        for pb in pb_codes:
            seiten_nummern = tuple(pb_seiten.filter(pl.col("pb") == pb)["pdf_seite"].to_list())
            massnahmen, _saldo_gesamt = lies_massnahmen(
                dokument, jahrgang, seiten_nummern, ebene="PB", code=pb
            )
            investitions_konten, finanzierung_ein, finanzierung_aus, hat_finanzierung = (
                _trenne_investitions_und_finanzierungskonten(
                    massnahmen, anzahl_spalten=anzahl_spalten
                )
            )

            # Kassenwirksamkeit-Werte der PB-Listen (konto.faelligkeiten) werden bewusst
            # NICHT gespeichert (EXTR-09, Flagged assumption 2: nur die Produktseiten-
            # Fälligkeiten fließen in ve_faelligkeiten.csv ein, siehe 03-02).
            for massnahme, konto in investitions_konten:
                for index in range(anzahl_spalten):
                    betrag = konto.werte[index]
                    if betrag is None:
                        continue
                    wertart, jahr = zerlege_spaltenkopf(spalten[index])
                    investitionen_pb_zeilen.append(
                        {
                            "pb": pb,
                            "massnahme_id": massnahme.massnahme_id,
                            "konto": konto.konto,
                            "richtung": konto.gruppe.richtung,
                            "jahr": jahr,
                            "wertart": wertart,
                            "betrag": betrag,
                            "pdf_seite": konto.pdf_seite,
                        }
                    )

            if hat_finanzierung:
                _pruefe_finanzierungskonten(
                    finanzplan=finanzplan,
                    spalten=spalten,
                    budget_indizes=budget_indizes,
                    ebene="PB",
                    code=pb,
                    finanzierung_einzahlung=finanzierung_ein,
                    finanzierung_auszahlung=finanzierung_aus,
                    letzte_seite=seiten_nummern[-1] if seiten_nummern else 0,
                )

    investitionen_df = pl.DataFrame(
        investitionen_zeilen,
        schema={
            "produkt": pl.Utf8,
            "massnahme_id": pl.Utf8,
            "massnahme_name": pl.Utf8,
            "konto": pl.Utf8,
            "konto_name": pl.Utf8,
            "richtung": pl.Utf8,
            "art": pl.Utf8,
            "jahr": pl.Int64,
            "wertart": pl.Utf8,
            "betrag": pl.Int64,
            "pdf_seite": pl.Int64,
        },
    )
    faelligkeiten_df = pl.DataFrame(
        faelligkeiten_zeilen,
        schema={
            "produkt": pl.Utf8,
            "massnahme_id": pl.Utf8,
            "konto": pl.Utf8,
            "jahr": pl.Int64,
            "betrag": pl.Int64,
            "pdf_seite": pl.Int64,
        },
    )
    investitionen_pb_df = pl.DataFrame(
        investitionen_pb_zeilen,
        schema={
            "pb": pl.Utf8,
            "massnahme_id": pl.Utf8,
            "konto": pl.Utf8,
            "richtung": pl.Utf8,
            "jahr": pl.Int64,
            "wertart": pl.Utf8,
            "betrag": pl.Int64,
            "pdf_seite": pl.Int64,
        },
    )

    investitionen_pfad = daten_wurzel / INVESTITIONEN_CSV
    faelligkeiten_pfad = daten_wurzel / VE_FAELLIGKEITEN_CSV
    investitionen_pb_pfad = daten_wurzel / INVESTITIONEN_PB_CSV
    schreibe_investitionen_csv(investitionen_df, investitionen_pfad)
    schreibe_ve_faelligkeiten_csv(faelligkeiten_df, faelligkeiten_pfad)
    schreibe_investitionen_pb_csv(investitionen_pb_df, investitionen_pb_pfad)
    return (
        ExtraktionsErgebnis(zeilen_geschrieben=investitionen_df.height, pfad=investitionen_pfad),
        ExtraktionsErgebnis(zeilen_geschrieben=faelligkeiten_df.height, pfad=faelligkeiten_pfad),
        ExtraktionsErgebnis(
            zeilen_geschrieben=investitionen_pb_df.height, pfad=investitionen_pb_pfad
        ),
    )
