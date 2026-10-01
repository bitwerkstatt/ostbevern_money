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
