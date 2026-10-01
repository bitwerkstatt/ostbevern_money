# Konsistenzbericht Haushalt 2026

Diese Datei wird von `pipeline/06_pruefen.py` und von pytest erzeugt und darf nicht von Hand bearbeitet werden.

Gesamtstatus: grün

## Übersicht

| Regel | Status | Geprüfte Werte | Abweichungen | Bekannte Befunde |
| --- | --- | --- | --- | --- |
| Regel 1 – Zeilenformeln | grün | 6550 | 0 | 3 |
| Regel 4 – Sollwerte (Anhang B, Satzung § 1-3) | grün | 147 | 0 | 0 |

## Abweichungen

Keine.

## Bekannte Befunde

| regel | plan | ebene | code | zeile | jahr | wertart | abweichung | pdf_seite | begruendung |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | teilergebnisplan | P | 080101 | 17 | 2024 | ergebnis | 2 | 206 | Dieselbe Rundungsdifferenz wie PB 08 Z. 17 2024 (siehe oben), hier auf der Produktseite selbst: S. 206 druckt Zeile 17 "186.499" für 2024, die Summe der gedruckten Zeilen 11, 13-16 ergibt 186.501. Wortweise gegen das PDF verifiziert; kein Extraktionsfehler. |
| 1 | teilergebnisplan | PB | 08 | 17 | 2024 | ergebnis | 2 | 203 | Teilergebnisplan PB 08 (Sportförderung), Spalte Ergebnis 2024: Summe der gedruckten Zeilen 11, 13-16 (12 nicht gedruckt, D-11) ergibt 186.501 C, gedruckt ist 186.499 C. Wortweise gegen das PDF verifiziert (Zeile 17 "186.499" exakt so gedruckt); kein Extraktionsfehler, sondern eine Rundungsdifferenz von 2 C im PDF selbst. |
| 1 | teilergebnisplan | PG | 0801 | 17 | 2024 | ergebnis | 2 | 206 | Dieselbe Rundungsdifferenz wie PB 08 Z. 17 2024 (siehe oben): PB 08 hat nur die synthetische PG 0801 mit dem einzigen Produkt 080101, daher druckt S. 206 (Produkt-Teilergebnisplan) dieselbe Zeile 17 "186.499" wie S. 203, und die synthetische PG 0801 ist nach D-14 eine Kopie dieser Produktzeile. |

## Veraltete Befunde

Keine.
