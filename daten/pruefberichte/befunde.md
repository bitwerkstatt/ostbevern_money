# Befunde – bekannte Abweichungen im Haushalt

Diese Datei dokumentiert bekannte Abweichungen zwischen den aus dem Haushalts-PDF
extrahierten Planwerten und den von `pipeline/ostbevern/pruefung.py` berechneten Prüfsummen.
Abweichungen über 1 € gelten als Fehler (Spez. 5.5), außer sie sind hier mit Begründung und
PDF-Seite dokumentiert.

Ein Befund deckt eine Abweichung nur ab, wenn Regel, Plan, Ebene, Code, Zeile, Jahr und
Wertart übereinstimmen **und** die tatsächliche Abweichung um höchstens 1 € von der hier
dokumentierten abweicht (D-05). `abweichung = ist − soll`, je nach Regel in `pruefung.py`
berechnet (Regel 1: gedruckte Summe minus Formelkette; Regel 4: Pipeline-Wert minus Sollwert
aus Anhang B bzw. Satzung).

Ein Befund, der nicht mehr auftritt, gilt selbst als Fehler (D-04) — diese Datei darf keine
Fehler still verdecken. Einträge sind nur für Abweichungen erlaubt, die so im PDF gedruckt
sind (z. B. dokumentierte Rundungsdifferenzen), niemals zum Verdecken von Extraktions- oder
Parsing-Fehlern.

## Schlüsseltabelle

| regel | plan | ebene | code | zeile | jahr | wertart | abweichung | pdf_seite | begruendung |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | teilergebnisplan | PB | 08 | 17 | 2024 | ergebnis | 2 | 203 | Teilergebnisplan PB 08 (Sportförderung), Spalte Ergebnis 2024: Summe der gedruckten Zeilen 11, 13-16 (12 nicht gedruckt, D-11) ergibt 186.501 C, gedruckt ist 186.499 C. Wortweise gegen das PDF verifiziert (Zeile 17 "186.499" exakt so gedruckt); kein Extraktionsfehler, sondern eine Rundungsdifferenz von 2 C im PDF selbst. |
| 1 | teilergebnisplan | PG | 0801 | 17 | 2024 | ergebnis | 2 | 206 | Dieselbe Rundungsdifferenz wie PB 08 Z. 17 2024 (siehe oben): PB 08 hat nur die synthetische PG 0801 mit dem einzigen Produkt 080101, daher druckt S. 206 (Produkt-Teilergebnisplan) dieselbe Zeile 17 "186.499" wie S. 203, und die synthetische PG 0801 ist nach D-14 eine Kopie dieser Produktzeile. |
| 1 | teilergebnisplan | P | 080101 | 17 | 2024 | ergebnis | 2 | 206 | Dieselbe Rundungsdifferenz wie PB 08 Z. 17 2024 (siehe oben), hier auf der Produktseite selbst: S. 206 druckt Zeile 17 "186.499" für 2024, die Summe der gedruckten Zeilen 11, 13-16 ergibt 186.501. Wortweise gegen das PDF verifiziert; kein Extraktionsfehler. |

## Beobachtungen ohne Prüfregel

- Gesamtergebnisplan, Zeilen 29–33 (Nachrichtlich: Verrechnung von Erträgen und Aufwendungen
  mit der allgemeinen Rücklage, PDF-Seite des Seitenbereichs `gesamtergebnisplan`): weder
  Spez. 5.5 noch Anhang B führen diese Zeilen als Prüfregel. Zeile 33 (Verrechnungssaldo) ist
  mit umgekehrtem Vorzeichen der einfachen Summe 29+30-31-32 gedruckt. Die Zeilen werden
  extrahiert (D-08 löst hier nicht aus, siehe Zeilen-Wörterbuch), aber von Regel 1 und
  Regel 4 bewusst ausgenommen.
- Rundungsdifferenzen von genau 1 €, die innerhalb `TOLERANZ_EURO` bleiben und deshalb keinen
  Schlüsseltabelle-Eintrag benötigen (Regel 1 bleibt für sie grün): Gesamtfinanzplan Zeile 09
  (Einzahlungen aus lfd. Verw.-tätigkeit), Spalte Ergebnis des ersten Jahres (Summe der
  Zeilen 01–08 liegt 1 € unter dem gedruckten Wert), und Gesamtergebnisplan Zeile 21
  (Finanzergebnis), Spalte Ergebnis des ersten Jahres.
- PG 1501/1502 (Wirtschaftsförderung, PB 15): Produkt 150102 (Touristische Öffentlichkeitsarbeit)
  wird nach D-14 in die synthetische Produktgruppe 1501 (aus Produkt 150101) einsortiert, da
  `hierarchie.csv` nur eine PG je Produktgruppencode kennt und 1502 im Teilplanbereich (S. 66-282)
  nicht gedruckt ist. Die Haushaltsquerschnitt-Seiten 299/300 führen PG 1502 "Tourismus" jedoch als
  eigenen Posten. Vor Phase 3 Regel 7 (Produkt→PG→PB-Summen auf den Querschnittsseiten) muss
  entschieden werden, ob die App diese PG-Aufteilung übernimmt oder bei der synthetischen
  Zusammenfassung 1501 bleibt.
