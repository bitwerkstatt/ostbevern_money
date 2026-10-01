# Konsistenzbericht Haushalt 2026

Diese Datei wird von `pipeline/06_pruefen.py` und von pytest erzeugt und darf nicht von Hand bearbeitet werden.

Gesamtstatus: grün

## Übersicht

| Regel | Status | Geprüfte Werte | Abweichungen | Bekannte Befunde |
| --- | --- | --- | --- | --- |
| Regel 1 – Zeilenformeln | grün | 6550 | 0 | 3 |
| Regel 2 – Produkte → PG → PB | grün | 7920 | 0 | 6 |
| Regel 3 – Produktbereiche → Gesamtergebnisplan | grün | 114 | 0 | 1 |
| Regel 4 – Sollwerte (Anhang B, Satzung § 1-3) | grün | 147 | 0 | 0 |

## Abweichungen

Keine.

## Bekannte Befunde

| regel | plan | ebene | code | zeile | jahr | wertart | abweichung | pdf_seite | begruendung |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | teilergebnisplan | P | 080101 | 17 | 2024 | ergebnis | 2 | 206 | Dieselbe Rundungsdifferenz wie PB 08 Z. 17 2024 (siehe oben), hier auf der Produktseite selbst: S. 206 druckt Zeile 17 "186.499" für 2024, die Summe der gedruckten Zeilen 11, 13-16 ergibt 186.501. Wortweise gegen das PDF verifiziert; kein Extraktionsfehler. |
| 1 | teilergebnisplan | PB | 08 | 17 | 2024 | ergebnis | 2 | 203 | Teilergebnisplan PB 08 (Sportförderung), Spalte Ergebnis 2024: Summe der gedruckten Zeilen 11, 13-16 (12 nicht gedruckt, D-11) ergibt 186.501 C, gedruckt ist 186.499 C. Wortweise gegen das PDF verifiziert (Zeile 17 "186.499" exakt so gedruckt); kein Extraktionsfehler, sondern eine Rundungsdifferenz von 2 C im PDF selbst. |
| 1 | teilergebnisplan | PG | 0801 | 17 | 2024 | ergebnis | 2 | 206 | Dieselbe Rundungsdifferenz wie PB 08 Z. 17 2024 (siehe oben): PB 08 hat nur die synthetische PG 0801 mit dem einzigen Produkt 080101, daher druckt S. 206 (Produkt-Teilergebnisplan) dieselbe Zeile 17 "186.499" wie S. 203, und die synthetische PG 0801 ist nach D-14 eine Kopie dieser Produktzeile. |
| 2 | teilergebnisplan | PB | 01 | 29 | 2024 | ergebnis | -2 | 66 | Teilergebnisplan PB 01 (Innere Verwaltung), Spalte Ergebnis 2024: PB 01 druckt Zeile 29 als "-2.556.326" (S. 66). Die Summe der gedruckten Zeile 29 aller 12 Produktgruppen (S. 73, 75, 78, 80, 82, 83, 95, 97, 100, 102, 110, 112) ergibt -2.556.328. Ursache sind eigenständig gerundete Teilsummen auf den PG-Seiten (Zeile 10 und 17 weichen dort je 1 C vom PB-Wert ab); wortweise gegen das PDF verifiziert, kein Extraktionsfehler. |
| 2 | teilergebnisplan | PB | 01 | 31 | 2024 | ergebnis | -2 | 66 | Dieselbe Rundungsdifferenz wie PB 01 Zeile 29 2024 (siehe oben): der globale Minderaufwand (Zeile 30) ist 2024 bei PB 01 und allen seinen Produktgruppen 0, daher gilt Zeile 31 = Zeile 29 unverändert (S. 66, Formel Z.29+30). |
| 2 | teilergebnisplan | PB | 02 | 10 | 2024 | ergebnis | 2 | 124 | Teilergebnisplan PB 02 (Sicherheit und Ordnung), Spalte Ergebnis 2024: PB 02 druckt Zeile 10 als "334.222" (S. 124). Die Summe der gedruckten Zeile 10 der 7 Produkte (S. 129, 131, 133, 135, 137, 139, 141: 26.009+12.164+6.264+107.996+11.728+12.827+157.236 = 334.224) ergibt 334.224. Wortweise gegen das PDF verifiziert; kein Extraktionsfehler, sondern eine Rundungsdifferenz von 2 C im PDF selbst. |
| 2 | teilergebnisplan | PB | 02 | 29 | 2024 | ergebnis | -2 | 124 | Folge der Rundungsdifferenz bei PB 02 Zeile 10 2024 (siehe oben): die Summe der gedruckten Zeile 29 der 7 Produktgruppen (S. 129, 131, 133, 135, 137, 139, 141) ergibt -820.758, PB 02 druckt -820.756 (S. 124). |
| 2 | teilergebnisplan | PB | 02 | 31 | 2024 | ergebnis | -2 | 124 | Dieselbe Rundungsdifferenz wie PB 02 Zeile 29 2024 (siehe oben): der globale Minderaufwand (Zeile 30) ist 2024 bei PB 02 und allen seinen Produktgruppen 0, daher gilt Zeile 31 = Zeile 29 unverändert. |
| 2 | teilfinanzplan | PB | 01 | 09 | 2024 | ergebnis | 2 | 66 | Teilfinanzplan PB 01, Spalte Ergebnis 2024: PB 01 druckt Zeile 09 als "859.878" (S. 66). Die Summe der gedruckten Zeile 09 der 9 Produktgruppen, die diese Zeile drucken (PG 0104/0105/0108 drucken keine Zeile 09, D-11; S. 73, 75, 78, 83, 95, 100, 102, 110, 112), ergibt 859.880. Wortweise gegen das PDF verifiziert; kein Extraktionsfehler. |
| 3 | gesamtergebnisplan | GESAMT |  | 11 | 2024 | ergebnis | 3 | 62 | Gesamtergebnisplan (Anhang B.1), Spalte Ergebnis 2024: Zeile 11 (Personalaufwendungen) ist mit "4.629.147" gedruckt (S. 62). Die Summe der gedruckten Zeile 11 aller 15 Produktbereiche (S. 66, 124, 145, 169, 178, 192, 203, 208, 220, 231, 234, 255, 268, 271, 278) ergibt 4.629.150. Wortweise gegen das PDF verifiziert; kein Extraktionsfehler, sondern eine Rundungsdifferenz von 3 C im PDF selbst. |

## Veraltete Befunde

Keine.
