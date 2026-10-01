"""Tests für ostbevern.plaene: Gesamtergebnisplan-Extraktion aus echten PDF-Seiten (D-07).

Liest nur das Original-PDF, nie daten/. Keine Jahrgangs-, Seiten- oder
Sollwert-Literale – alles kommt aus lade_jahrgang(STANDARD_JAHR) bzw.
lade_sollwerte(STANDARD_JAHR).
"""

from __future__ import annotations

import dataclasses

import pytest

from ostbevern.konfiguration import STANDARD_JAHR, Jahrgang, lade_jahrgang, lade_sollwerte
from ostbevern.pdf import PdfDokument, Textzeile
from ostbevern.plaene import PlaeneFehler, lies_abschnitte, lies_plantabelle
from ostbevern.schema import zerlege_spaltenkopf
from ostbevern.zeilen import ZEILEN, plantyp_fuer

_PLANTYP = plantyp_fuer("ergebnisplan", "GESAMT")
_FINANZPLANTYP = plantyp_fuer("finanzplan", "GESAMT")


def _gesamtergebnisplan_zeilen() -> tuple[tuple[Textzeile, ...], int, Jahrgang]:
    jahrgang = lade_jahrgang(STANDARD_JAHR)
    bereich = jahrgang.seitenbereiche["gesamtergebnisplan"]
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        return dokument.zeilen(bereich.von), bereich.von, jahrgang


def _gesamtfinanzplan_zeilen() -> tuple[tuple[Textzeile, ...], int, Jahrgang]:
    jahrgang = lade_jahrgang(STANDARD_JAHR)
    bereich = jahrgang.seitenbereiche["gesamtfinanzplan"]
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        return dokument.zeilen(bereich.von), bereich.von, jahrgang


def _gedruckte_zeilen_als_dict(
    zeilen: tuple[Textzeile, ...], pdf_seite: int, jahrgang: Jahrgang
) -> dict[str, object]:
    gedruckte_zeilen = lies_plantabelle(
        zeilen, plantyp=_PLANTYP, spalten=jahrgang.spalten["ergebnisplan"], pdf_seite=pdf_seite
    )
    return {z.zeile: z for z in gedruckte_zeilen}


def _gedruckte_finanzplan_zeilen_als_dict(
    zeilen: tuple[Textzeile, ...], pdf_seite: int, jahrgang: Jahrgang
) -> dict[str, object]:
    gedruckte_zeilen = lies_plantabelle(
        zeilen,
        plantyp=_FINANZPLANTYP,
        spalten=jahrgang.spalten["finanzplan"],
        pdf_seite=pdf_seite,
    )
    return {z.zeile: z for z in gedruckte_zeilen}


def test_gesamtergebnisplan_zeilen_entsprechen_woerterbuch() -> None:
    zeilen, pdf_seite, jahrgang = _gesamtergebnisplan_zeilen()
    gedruckte_zeilen = lies_plantabelle(
        zeilen, plantyp=_PLANTYP, spalten=jahrgang.spalten["ergebnisplan"], pdf_seite=pdf_seite
    )

    gefundene_nummern = {z.zeile for z in gedruckte_zeilen}
    assert gefundene_nummern == set(ZEILEN[_PLANTYP].keys())

    erwartete_laenge = len(jahrgang.spalten["ergebnisplan"])
    for gedruckt in gedruckte_zeilen:
        assert len(gedruckt.werte) == erwartete_laenge
        assert gedruckt.pdf_seite == pdf_seite


def test_gesamtergebnisplan_trifft_sollwerte_b1() -> None:
    zeilen, pdf_seite, jahrgang = _gesamtergebnisplan_zeilen()
    gedruckte_zeilen = _gedruckte_zeilen_als_dict(zeilen, pdf_seite, jahrgang)

    sollwerte = lade_sollwerte(STANDARD_JAHR)
    gesamtergebnisplan = sollwerte["gesamtergebnisplan"]
    for zeile, erwartete_werte in gesamtergebnisplan["zeilen"].items():
        assert list(gedruckte_zeilen[zeile].werte) == list(erwartete_werte)


def test_gesamtergebnisplan_operatoren_und_umbruch() -> None:
    zeilen, pdf_seite, jahrgang = _gesamtergebnisplan_zeilen()
    gedruckte_zeilen = _gedruckte_zeilen_als_dict(zeilen, pdf_seite, jahrgang)

    steuern_zeile = next(
        zeile for zeile, definition in ZEILEN[_PLANTYP].items() if definition.kanonisch == "steuern"
    )
    assert gedruckte_zeilen[steuern_zeile].operator is None

    bestandsveraenderung_zeile = next(
        zeile
        for zeile, definition in ZEILEN[_PLANTYP].items()
        if definition.kanonisch == "bestandsveraenderungen"
    )
    assert gedruckte_zeilen[bestandsveraenderung_zeile].operator == "+/-"

    nach_minderaufwand_zeile = next(
        zeile
        for zeile, definition in ZEILEN[_PLANTYP].items()
        if definition.kanonisch == "ergebnis_nach_minderaufwand"
    )
    nach_minderaufwand = gedruckte_zeilen[nach_minderaufwand_zeile]
    assert nach_minderaufwand.operator == "="
    assert len(nach_minderaufwand.werte) == len(jahrgang.spalten["ergebnisplan"])


def test_gesamtergebnisplan_unbekannte_zeile_bricht_ab() -> None:
    zeilen, pdf_seite, jahrgang = _gesamtergebnisplan_zeilen()
    steuern_zeile = next(
        zeile for zeile, definition in ZEILEN[_PLANTYP].items() if definition.kanonisch == "steuern"
    )

    zeilen_liste = list(zeilen)
    for index, zeile in enumerate(zeilen_liste):
        if zeile.woerter and zeile.woerter[0].text == steuern_zeile:
            woerter = list(zeile.woerter)
            woerter[0] = dataclasses.replace(woerter[0], text="99")
            zeilen_liste[index] = dataclasses.replace(zeile, woerter=tuple(woerter))
            break
    else:
        pytest.fail(f"Zeile {steuern_zeile!r} nicht gefunden")

    with pytest.raises(PlaeneFehler, match=rf"S\. {pdf_seite}, Zeile 99"):
        lies_plantabelle(
            tuple(zeilen_liste),
            plantyp=_PLANTYP,
            spalten=jahrgang.spalten["ergebnisplan"],
            pdf_seite=pdf_seite,
        )


def test_gesamtergebnisplan_falscher_text_bricht_ab() -> None:
    zeilen, pdf_seite, jahrgang = _gesamtergebnisplan_zeilen()
    steuern_zeile = next(
        zeile for zeile, definition in ZEILEN[_PLANTYP].items() if definition.kanonisch == "steuern"
    )

    zeilen_liste = list(zeilen)
    for index, zeile in enumerate(zeilen_liste):
        if zeile.woerter and zeile.woerter[0].text == steuern_zeile:
            woerter = list(zeile.woerter)
            label_index = next(
                i
                for i, w in enumerate(woerter)
                if w.text != steuern_zeile and not w.text[0].isdigit()
            )
            woerter[label_index] = dataclasses.replace(woerter[label_index], text="Unbekannttext")
            zeilen_liste[index] = dataclasses.replace(zeile, woerter=tuple(woerter))
            break
    else:
        pytest.fail(f"Zeile {steuern_zeile!r} nicht gefunden")

    with pytest.raises(PlaeneFehler, match=rf"S\. {pdf_seite}, Zeile {steuern_zeile}"):
        lies_plantabelle(
            tuple(zeilen_liste),
            plantyp=_PLANTYP,
            spalten=jahrgang.spalten["ergebnisplan"],
            pdf_seite=pdf_seite,
        )


def test_gesamtfinanzplan_zeilen_entsprechen_woerterbuch() -> None:
    zeilen, pdf_seite, jahrgang = _gesamtfinanzplan_zeilen()
    gedruckte_zeilen = lies_plantabelle(
        zeilen,
        plantyp=_FINANZPLANTYP,
        spalten=jahrgang.spalten["finanzplan"],
        pdf_seite=pdf_seite,
    )

    gefundene_nummern = {z.zeile for z in gedruckte_zeilen}
    assert gefundene_nummern == set(ZEILEN[_FINANZPLANTYP].keys())
    assert len(gefundene_nummern) == 41

    erwartete_laenge = len(jahrgang.spalten["finanzplan"])
    for gedruckt in gedruckte_zeilen:
        assert len(gedruckt.werte) == erwartete_laenge
        assert gedruckt.pdf_seite == pdf_seite


def test_gesamtfinanzplan_trifft_sollwerte_b2() -> None:
    zeilen, pdf_seite, jahrgang = _gesamtfinanzplan_zeilen()
    gedruckte_zeilen = _gedruckte_finanzplan_zeilen_als_dict(zeilen, pdf_seite, jahrgang)
    spalten = jahrgang.spalten["finanzplan"]

    sollwerte = lade_sollwerte(STANDARD_JAHR)
    gesamtfinanzplan = sollwerte["gesamtfinanzplan"]

    for zeile, erwarteter_wert in gesamtfinanzplan["ansatz"].items():
        index = next(
            i
            for i, kopf in enumerate(spalten)
            if zerlege_spaltenkopf(kopf) == ("ansatz", STANDARD_JAHR)
        )
        assert gedruckte_zeilen[zeile].werte[index] == erwarteter_wert

    for zeile, erwarteter_wert in gesamtfinanzplan["ve"].items():
        index = next(
            i
            for i, kopf in enumerate(spalten)
            if zerlege_spaltenkopf(kopf) == ("ve", STANDARD_JAHR)
        )
        assert gedruckte_zeilen[zeile].werte[index] == erwarteter_wert

    # Beweist, dass die doppelte Jahreszahl im Haushaltsjahr (Ansatz/VE) über x-Position
    # und nicht über Text aufgelöst wird: beide Werte der VE-Sollwertzeile
    # unterscheiden sich tatsächlich (EXTR-05, Pattern 1).
    ve_zeile = next(iter(gesamtfinanzplan["ve"]))
    ansatz_index = next(
        i
        for i, kopf in enumerate(spalten)
        if zerlege_spaltenkopf(kopf) == ("ansatz", STANDARD_JAHR)
    )
    ve_index = next(
        i for i, kopf in enumerate(spalten) if zerlege_spaltenkopf(kopf) == ("ve", STANDARD_JAHR)
    )
    assert (
        gedruckte_zeilen[ve_zeile].werte[ansatz_index] != gedruckte_zeilen[ve_zeile].werte[ve_index]
    )


def test_gesamtfinanzplan_falscher_spaltenkopf_bricht_ab() -> None:
    zeilen, pdf_seite, jahrgang = _gesamtfinanzplan_zeilen()

    zeilen_liste = list(zeilen)
    for index, zeile in enumerate(zeilen_liste):
        if any(wort.text == "VE" for wort in zeile.woerter):
            woerter = list(zeile.woerter)
            ve_index = next(i for i, w in enumerate(woerter) if w.text == "VE")
            woerter[ve_index] = dataclasses.replace(woerter[ve_index], text="XY")
            zeilen_liste[index] = dataclasses.replace(zeile, woerter=tuple(woerter))
            break
    else:
        pytest.fail("Kopfzeile mit 'VE' nicht gefunden")

    with pytest.raises(PlaeneFehler, match=rf"S\. {pdf_seite}"):
        lies_plantabelle(
            tuple(zeilen_liste),
            plantyp=_FINANZPLANTYP,
            spalten=jahrgang.spalten["finanzplan"],
            pdf_seite=pdf_seite,
        )


def _pb_teilplan_abschnitte(
    jahrgang: Jahrgang, dokument: PdfDokument, pdf_seite: int
) -> dict[str, object]:
    zeilen = dokument.zeilen(pdf_seite)
    abschnitte = lies_abschnitte(zeilen, jahrgang, pdf_seite)
    return {a.plantyp: a for a in abschnitte}


def test_pb_teilergebnisplan_trifft_b3() -> None:
    """Jede PB-Teilplan-Startseite (Anhang A) hat genau einen TEG- und einen TFP-Abschnitt;
    die Ansatz-Haushaltsjahr-Werte von Z. 10/17 stimmen mit Anhang B.3 überein (D-07)."""
    jahrgang = lade_jahrgang(STANDARD_JAHR)
    sollwerte = lade_sollwerte(STANDARD_JAHR)
    anhang_a = sollwerte["anhang_a"]
    teilergebnisplaene_pb = sollwerte["teilergebnisplaene_pb"]
    spalten = jahrgang.spalten["ergebnisplan"]
    index_ansatz_haushaltsjahr = next(
        i
        for i, kopf in enumerate(spalten)
        if zerlege_spaltenkopf(kopf) == ("ansatz", STANDARD_JAHR)
    )

    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        for pb_code, sollwert in teilergebnisplaene_pb.items():
            pdf_seite = anhang_a[pb_code]["pdf_seite"]
            zeilen = dokument.zeilen(pdf_seite)
            abschnitte = lies_abschnitte(zeilen, jahrgang, pdf_seite)
            teg_abschnitte = [a for a in abschnitte if a.plantyp == "teilergebnisplan"]
            tfp_abschnitte = [a for a in abschnitte if a.plantyp == "teilfinanzplan"]
            assert len(teg_abschnitte) == 1, pb_code
            assert len(tfp_abschnitte) == 1, pb_code

            gedruckt = {
                zeile.zeile: zeile
                for zeile in lies_plantabelle(
                    teg_abschnitte[0].zeilen,
                    plantyp="teilergebnisplan",
                    spalten=spalten,
                    pdf_seite=pdf_seite,
                )
            }
            for zeile, feld in (
                ("10", "ordentliche_ertraege"),
                ("17", "ordentliche_aufwendungen"),
            ):
                erwartet = sollwert[feld]
                if zeile not in gedruckt:
                    # Ein B.3-Wert 0 kann bedeuten, dass die Zeile nicht gedruckt ist (D-11).
                    assert erwartet == 0, pb_code
                    continue
                assert gedruckt[zeile].werte[index_ansatz_haushaltsjahr] == erwartet, pb_code


def test_pb_teilergebnisplan_bestandsveraenderung_geklebt() -> None:
    """Eine PB-Teilergebnisplan-Seite, die Zeile 09 druckt, liefert Operator "+/-" auch wenn
    er ohne Leerzeichen an die Bezeichnung angeklebt ist (Research Pattern 2)."""
    jahrgang = lade_jahrgang(STANDARD_JAHR)
    sollwerte = lade_sollwerte(STANDARD_JAHR)
    anhang_a = sollwerte["anhang_a"]
    teilergebnisplaene_pb = sollwerte["teilergebnisplaene_pb"]

    gefunden = False
    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        for pb_code in teilergebnisplaene_pb:
            pdf_seite = anhang_a[pb_code]["pdf_seite"]
            abschnitte = _pb_teilplan_abschnitte(jahrgang, dokument, pdf_seite)
            abschnitt = abschnitte["teilergebnisplan"]
            gedruckt = {
                zeile.zeile: zeile
                for zeile in lies_plantabelle(
                    abschnitt.zeilen,
                    plantyp="teilergebnisplan",
                    spalten=jahrgang.spalten["ergebnisplan"],
                    pdf_seite=pdf_seite,
                )
            }
            if "09" in gedruckt:
                assert gedruckt["09"].operator == "+/-", pb_code
                gefunden = True
    assert gefunden, "keine PB-Teilergebnisplan-Seite druckt Zeile 09 (Bestandsveränderungen)"


def test_pb_teilfinanzplan_hat_sieben_spalten() -> None:
    """Der PB-Teilfinanzplan hat dieselbe Spaltenzahl wie der Gesamtfinanzplan (inkl. VE,
    EXTR-05); die doppelte Haushaltsjahr-Kopfzeile (Ansatz/VE) wird über x-Position gelöst."""
    jahrgang = lade_jahrgang(STANDARD_JAHR)
    sollwerte = lade_sollwerte(STANDARD_JAHR)
    anhang_a = sollwerte["anhang_a"]
    pb_code = next(iter(sollwerte["teilergebnisplaene_pb"]))
    pdf_seite = anhang_a[pb_code]["pdf_seite"]
    erwartete_spaltenzahl = len(jahrgang.spalten["finanzplan"])

    with PdfDokument.oeffne(jahrgang.pdf_pfad) as dokument:
        abschnitte = _pb_teilplan_abschnitte(jahrgang, dokument, pdf_seite)
        abschnitt = abschnitte["teilfinanzplan"]
        gedruckte_zeilen = lies_plantabelle(
            abschnitt.zeilen,
            plantyp="teilfinanzplan",
            spalten=jahrgang.spalten["finanzplan"],
            pdf_seite=pdf_seite,
        )

    assert gedruckte_zeilen
    for gedruckt in gedruckte_zeilen:
        assert len(gedruckt.werte) == erwartete_spaltenzahl
