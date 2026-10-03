# Befunde – bekannte Abweichungen im Haushalt

Diese Datei dokumentiert bekannte Abweichungen zwischen den aus dem Haushalts-PDF
extrahierten Planwerten und den von `pipeline/ostbevern/pruefung.py` berechneten Prüfsummen.
Abweichungen über 1 € gelten als Fehler (Spez. 5.5), außer sie sind hier mit Begründung und
PDF-Seite dokumentiert.

Regel 7 (Haushaltsquerschnitte, S. 291-300, PRUEF-07): `abweichung = ist − soll`, wobei `soll`
der im Querschnitt gedruckte Wert ist und `ist` der über `Planwerte` aus den eigenen
PG-/PB-Teilplänen hergeleitete Wert (REGEL7_KENNZAHLEN-Formelkette); `zeile` trägt den
Kennzahl-Schlüssel (z. B. `ordentliche_ertraege`), `plan` ist `querschnitt_ergebnisplan` oder
`querschnitt_finanzplan`, `pdf_seite` ist die Querschnitt-Seite (291-300).

Regel 6 (Investitionsmaßnahmen → Teil-/Gesamtfinanzplan, PRUEF-06): `abweichung = ist − soll`;
bei `plan` `investitionen_produkt`/`investitionen_gesamt` ist `soll` die Teilfinanzplan- bzw.
Gesamtfinanzplan-Zeile 23 (Einzahlungen, `zeile` "23") oder 30 (Auszahlungen, `zeile` "30") und
`ist` die Summe der Maßnahmen in `investitionen.csv` dieser Richtung; bei `plan`
`ve_faelligkeiten` ist `soll` die VE einer Kontozeile und `ist` die Summe ihrer Fälligkeiten in
`ve_faelligkeiten.csv`, `zeile` = `Maßnahme/Konto`. Regel 6 (`plan` `investitionen_pb_liste`):
Summe der Produktseiten (`ist`) minus Summe der PB-Investitionsliste (`soll`) je Maßnahme/Konto
(`zeile` = `Maßnahme/Konto`). Lücken (Maßnahme nur in einer Quelle) sind keine Abweichungen und
können hier nicht dokumentiert werden (D-06, 03-03).

Regel 8 (Vollständigkeit der Produkte, PRUEF-08, Spez. 5.5) hat keine Abweichungen (keinen
Soll/Ist-Betragsvergleich), sondern meldet jeden Verstoß (fehlendes/unbekanntes Produkt, falsche
Gesamtanzahl, leeres Pflichtfeld, unbekannter Bindungsgrad, fehlende Teilergebnis-/
Teilfinanzplan-Zeile) als Lücke. Eine Lücke ist, wie bei Regel 6, nie über diese Datei
abdeckbar — ein fehlendes Produkt oder eine leere Produktbeschreibung ist kein Rundungsfehler.

Regel 5 (manuelle Vorberichtstabellen → Planzeilen, PRUEF-05, D-07) prüft vier Tabellen unter
`daten/manuell/` zweistufig: Stufe (a) `zeile` `summe_posten` vergleicht die Summe der Posten
mit der mit abgeschriebenen, gedruckten Gesamtzeile derselben Tabelle und desselben Jahres
(beide in T€, × 1000 in Euro umgerechnet; jede Differenz ab 1 T€ = 1.000 € überschreitet die
strenge TOLERANZ_EURO = 1 € und wird dokumentationspflichtig). Stufe (b) `zeile` `gep_NN`
vergleicht die gedruckte Gesamtzeile × 1000 mit der zugeordneten Zeile NN des
Gesamtergebnisplans (`plan` `vorbericht_{tabelle}`), Toleranz ±1.000 €. Für `kita_zuschuesse`
prüft `zeile` `transfer_kita` zusätzlich die Kita-Gesamtzeile gegen den Transferaufwendungen-
Posten „Zuschüsse an Kindertageseinr.“ desselben Jahres (strenge TOLERANZ_EURO = 1 €, D-07).
Die Weitergabe an Kreis und Land (D-01, `plan` `weitergabe_kreis_land`, `ebene` `P`, `code` der
Produktcode aus `[layout.weitergabe_kreis_land]`, `zeile` `tp_15`) vergleicht die Summe der drei
Transferaufwendungen-Posten Kreisumlage, Gewerbesteuerumlage und Krankenhausinvestitionsumlage
(× 1000) mit Zeile 15 des Teilergebnisplans dieses Produkts, Toleranz ±3.000 € (drei Posten ×
±1.000 €). In allen Fällen gilt `abweichung = ist − soll`, mit `ist` dem aus den Vorbericht-
Posten hergeleiteten Wert und `soll` dem jeweils gedruckten oder im Gesamtergebnisplan
ausgewiesenen Referenzwert.

Ein Befund deckt eine Abweichung nur ab, wenn Regel, Plan, Ebene, Code, Zeile, Jahr und
Wertart übereinstimmen **und** die tatsächliche Abweichung um höchstens 1 € von der hier
dokumentierten abweicht (D-05). `abweichung = ist − soll`, je nach Regel in `pruefung.py`
berechnet (Regel 1: Formelkette minus gedruckte Summe; Regel 2: Summe der Kinder minus
gedruckter Elternwert, je Ebene PG→P bzw. PB→PG; Regel 3: Summe der 15 PB minus gedrucktem
Gesamtergebnisplan; Regel 4: Pipeline-Wert minus Sollwert aus Anhang B bzw. Satzung).

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
| 2 | teilergebnisplan | PB | 01 | 29 | 2024 | ergebnis | -2 | 66 | Teilergebnisplan PB 01 (Innere Verwaltung), Spalte Ergebnis 2024: PB 01 druckt Zeile 29 als "-2.556.326" (S. 66). Die Summe der gedruckten Zeile 29 aller 12 Produktgruppen (S. 73, 75, 78, 80, 82, 83, 95, 97, 100, 102, 110, 112) ergibt -2.556.328. Ursache sind eigenständig gerundete Teilsummen auf den PG-Seiten (Zeile 10 und 17 weichen dort je 1 C vom PB-Wert ab); wortweise gegen das PDF verifiziert, kein Extraktionsfehler. |
| 2 | teilergebnisplan | PB | 01 | 31 | 2024 | ergebnis | -2 | 66 | Dieselbe Rundungsdifferenz wie PB 01 Zeile 29 2024 (siehe oben): der globale Minderaufwand (Zeile 30) ist 2024 bei PB 01 und allen seinen Produktgruppen 0, daher gilt Zeile 31 = Zeile 29 unverändert (S. 66, Formel Z.29+30). |
| 2 | teilergebnisplan | PB | 02 | 10 | 2024 | ergebnis | 2 | 124 | Teilergebnisplan PB 02 (Sicherheit und Ordnung), Spalte Ergebnis 2024: PB 02 druckt Zeile 10 als "334.222" (S. 124). Die Summe der gedruckten Zeile 10 der 7 Produkte (S. 129, 131, 133, 135, 137, 139, 141: 26.009+12.164+6.264+107.996+11.728+12.827+157.236 = 334.224) ergibt 334.224. Wortweise gegen das PDF verifiziert; kein Extraktionsfehler, sondern eine Rundungsdifferenz von 2 C im PDF selbst. |
| 2 | teilergebnisplan | PB | 02 | 29 | 2024 | ergebnis | -2 | 124 | Folge der Rundungsdifferenz bei PB 02 Zeile 10 2024 (siehe oben): die Summe der gedruckten Zeile 29 der 7 Produktgruppen (S. 129, 131, 133, 135, 137, 139, 141) ergibt -820.758, PB 02 druckt -820.756 (S. 124). |
| 2 | teilergebnisplan | PB | 02 | 31 | 2024 | ergebnis | -2 | 124 | Dieselbe Rundungsdifferenz wie PB 02 Zeile 29 2024 (siehe oben): der globale Minderaufwand (Zeile 30) ist 2024 bei PB 02 und allen seinen Produktgruppen 0, daher gilt Zeile 31 = Zeile 29 unverändert. |
| 2 | teilfinanzplan | PB | 01 | 09 | 2024 | ergebnis | 2 | 66 | Teilfinanzplan PB 01, Spalte Ergebnis 2024: PB 01 druckt Zeile 09 als "859.878" (S. 66). Die Summe der gedruckten Zeile 09 der 9 Produktgruppen, die diese Zeile drucken (PG 0104/0105/0108 drucken keine Zeile 09, D-11; S. 73, 75, 78, 83, 95, 100, 102, 110, 112), ergibt 859.880. Wortweise gegen das PDF verifiziert; kein Extraktionsfehler. |
| 3 | gesamtergebnisplan | GESAMT |  | 11 | 2024 | ergebnis | 3 | 62 | Gesamtergebnisplan (Anhang B.1), Spalte Ergebnis 2024: Zeile 11 (Personalaufwendungen) ist mit "4.629.147" gedruckt (S. 62). Die Summe der gedruckten Zeile 11 aller 15 Produktbereiche (S. 66, 124, 145, 169, 178, 192, 203, 208, 220, 231, 234, 255, 268, 271, 278) ergibt 4.629.150. Wortweise gegen das PDF verifiziert; kein Extraktionsfehler, sondern eine Rundungsdifferenz von 3 C im PDF selbst. |
| 7 | querschnitt_finanzplan | PG | 0110 | einzahlungen_laufende_verwaltung | 2026 | ansatz | -300 | 291 | Haushaltsquerschnitt PG 0110 (Finanzmanagement und Rechnungswesen), Spalte "Einzahlungen aus lfd. Verwaltungstätigkeit" (S. 291): gedruckt "157.900". Der eigene Teilfinanzplan der PG 0110 (S. 102) druckt Zeile 09 "Einzahlungen aus lfd. Verw.-tätigkeit" Ansatz 2026 = "157.600". Wortweise gegen beide PDF-Seiten verifiziert; eine echte Differenz zwischen Teilfinanzplan- und Querschnittseite im PDF selbst, kein Extraktions- oder Zuordnungsfehler. |
| 7 | querschnitt_finanzplan | PG | 0110 | saldo_laufende_verwaltung | 2026 | ansatz | -300 | 291 | Folge derselben Differenz wie PG 0110 "einzahlungen_laufende_verwaltung" oben (S. 291 vs. S. 102 Zeile 09): "Saldo aus lfd. Verwaltungstätigkeit" ist Einzahlungen minus Auszahlungen (Zeile 17 = Z.09-Z.16); die Auszahlungenseite stimmt überein, daher trägt der Saldo dieselbe Differenz von -300 C weiter. |
| 7 | querschnitt_finanzplan | PG | 0110 | finanzmittelueberschuss | 2026 | ansatz | -300 | 291 | Folge derselben Differenz wie PG 0110 "einzahlungen_laufende_verwaltung" oben: "Finanzmittelüberschuss/-fehlbetrag" ist Saldo lfd. Verwaltung plus Saldo Investitionstätigkeit (Z.17+Z.31); die Investitionsseite stimmt überein, daher trägt auch dieser Wert dieselbe Differenz von -300 C weiter. |
| 7 | querschnitt_finanzplan | PB | 01 | einzahlungen_laufende_verwaltung | 2026 | ansatz | -300 | 292 | Haushaltsquerschnitt PB 01 (Innere Verwaltung), GESAMTSUMME-Zeile "Einzahlungen aus lfd. Verwaltungstätigkeit" (S. 292): gedruckt "433.150". PB 01 hat nur eine Produktgruppe mit abweichender Teilfinanzplan-Einzahlung, PG 0110 (siehe oben, S. 291/102, -300 C); alle anderen Produktgruppen von PB 01 stimmen überein, daher trägt die GESAMTSUMME dieselbe Differenz von -300 C weiter (Regel 2 bleibt grün, da Teilfinanzplan-intern Σ PG == PB gilt). |
| 7 | querschnitt_finanzplan | PB | 01 | saldo_laufende_verwaltung | 2026 | ansatz | -300 | 292 | Folge derselben Differenz wie PB 01 "einzahlungen_laufende_verwaltung" oben (S. 292, Ursache PG 0110 S. 291/102). |
| 7 | querschnitt_finanzplan | PB | 01 | finanzmittelueberschuss | 2026 | ansatz | -300 | 292 | Folge derselben Differenz wie PB 01 "einzahlungen_laufende_verwaltung" oben (S. 292, Ursache PG 0110 S. 291/102). |
| 7 | querschnitt_finanzplan | PG | 0207 | verpflichtungsermaechtigungen | 2026 | ve | 3200000 | 292 | Haushaltsquerschnitt PG 0207 (Feuer- und Bevölkerungsschutz), Spalte "Verpflichtungsermächtigung" (S. 292): gedruckt "0". Der eigene Teilfinanzplan der PG 0207 (S. 142) druckt Zeile 30 "Auszahlungen aus Investitionstätigkeit" in der zweiten "2026"-Spalte (VE) = "3.200.000" (Baumaßnahmenzeile 25 trägt dieselbe VE). Der Haushaltsquerschnitt druckt in dieser Spalte durchgängig "0" für alle 64 PB-/PG-Zeilen (geprüft gegen querschnitte.csv), auch dort, wo wie hier eine reale Verpflichtungsermächtigung besteht; die Summe der drei betroffenen Produktgruppen (0207, 0301, 1201) ergibt exakt die Satzungs-Verpflichtungsermächtigung von 11.600.000 C (Anhang, § 1-3, S. 8). Wortweise gegen beide PDF-Seiten verifiziert; eine echte, systematisch leere Spalte im Querschnitt, kein Extraktions- oder Zuordnungsfehler (die Zuordnung ist durch die Spaltenkopf-Zusammensetzung "Verpflich-"+"tungser-"+"mächtigung" eindeutig belegt). |
| 7 | querschnitt_finanzplan | PB | 02 | verpflichtungsermaechtigungen | 2026 | ve | 3200000 | 292 | Folge derselben leeren VE-Spalte wie PG 0207 oben: PB 02 (Sicherheit und Ordnung) hat nur die eine Produktgruppe 0207 mit einer Verpflichtungsermächtigung, daher trägt die GESAMTSUMME (S. 292) dieselbe Differenz von 3.200.000 C. |
| 7 | querschnitt_finanzplan | PG | 0301 | verpflichtungsermaechtigungen | 2026 | ve | 5700000 | 293 | Haushaltsquerschnitt PG 0301 (Schulische Einrichtungen und schülerbezogene Leistungen), Spalte "Verpflichtungsermächtigung" (S. 293): gedruckt "0". Der eigene Teilfinanzplan der PG 0301 (S. 150) druckt Zeile 30 "Auszahlungen aus Investitionstätigkeit" in der VE-Spalte "2026" = "5.700.000" (Baumaßnahmenzeile 25 trägt dieselbe VE). Dieselbe systematisch leere VE-Spalte des Querschnitts wie bei PG 0207 (siehe dort); wortweise gegen beide PDF-Seiten verifiziert. |
| 7 | querschnitt_finanzplan | PB | 03 | verpflichtungsermaechtigungen | 2026 | ve | 5700000 | 293 | Folge derselben leeren VE-Spalte wie PG 0301 oben: PB 03 (Schulträgeraufgaben) hat nur die eine Produktgruppe 0301 mit einer Verpflichtungsermächtigung, daher trägt die GESAMTSUMME (S. 293) dieselbe Differenz von 5.700.000 C. |
| 7 | querschnitt_finanzplan | PG | 1201 | auszahlungen_investitionen | 2026 | ansatz | 100000 | 298 | Haushaltsquerschnitt PG 1201 (Öffentliche Verkehrsflächen und Verkehrsanlagen), Spalte "Auszahlungen aus Investitionstätigkeit" (S. 298): gedruckt "2.510.000". Der eigene Teilfinanzplan der PG 1201 (S. 240) druckt Zeile 30 "Auszahlungen aus Investitionstätigkeit" Ansatz 2026 = "2.610.000". Wortweise gegen beide PDF-Seiten verifiziert; eine echte Differenz zwischen Teilfinanzplan- und Querschnittseite im PDF selbst, kein Extraktions- oder Zuordnungsfehler. |
| 7 | querschnitt_finanzplan | PG | 1201 | saldo_investitionen | 2026 | ansatz | -100000 | 298 | Folge derselben Differenz wie PG 1201 "auszahlungen_investitionen" oben: "Saldo aus Investitionstätigkeit" ist Einzahlungen minus Auszahlungen (Zeile 31 = Z.23-Z.30); die Einzahlungenseite stimmt überein, daher trägt der Saldo dieselbe Differenz von -100.000 C weiter. |
| 7 | querschnitt_finanzplan | PG | 1201 | finanzmittelueberschuss | 2026 | ansatz | -100000 | 298 | Folge derselben Differenz wie PG 1201 "auszahlungen_investitionen" oben: "Finanzmittelüberschuss/-fehlbetrag" ist Saldo lfd. Verwaltung plus Saldo Investitionstätigkeit (Z.17+Z.31); die lfd.-Verwaltungsseite stimmt überein, daher trägt auch dieser Wert dieselbe Differenz von -100.000 C weiter. |
| 7 | querschnitt_finanzplan | PG | 1201 | verpflichtungsermaechtigungen | 2026 | ve | 2700000 | 298 | Haushaltsquerschnitt PG 1201, Spalte "Verpflichtungsermächtigung" (S. 298): gedruckt "0". Der eigene Teilfinanzplan der PG 1201 (S. 240) druckt Zeile 30 in der VE-Spalte "2026" = "2.700.000" (Baumaßnahmenzeile 25 trägt dieselbe VE). Dieselbe systematisch leere VE-Spalte des Querschnitts wie bei PG 0207/0301 (siehe dort); wortweise gegen beide PDF-Seiten verifiziert. |
| 7 | querschnitt_finanzplan | PB | 12 | auszahlungen_investitionen | 2026 | ansatz | 100000 | 298 | Folge derselben Differenz wie PG 1201 "auszahlungen_investitionen" oben: PB 12 (Verkehrsflächen und -anlagen) hat nur die eine Produktgruppe 1201, daher trägt die GESAMTSUMME (S. 298) dieselbe Differenz von 100.000 C (eigener Teilfinanzplan PB 12 S. 234, Zeile 30 Ansatz 2026 = "3.440.000" gegen Querschnitt "3.340.000"). |
| 7 | querschnitt_finanzplan | PB | 12 | saldo_investitionen | 2026 | ansatz | -100000 | 298 | Folge derselben Differenz wie PB 12 "auszahlungen_investitionen" oben. |
| 7 | querschnitt_finanzplan | PB | 12 | finanzmittelueberschuss | 2026 | ansatz | -100000 | 298 | Folge derselben Differenz wie PB 12 "auszahlungen_investitionen" oben. |
| 7 | querschnitt_finanzplan | PB | 12 | verpflichtungsermaechtigungen | 2026 | ve | 2700000 | 298 | Folge derselben leeren VE-Spalte wie PG 1201 oben: PB 12 hat nur die eine Produktgruppe 1201 mit einer Verpflichtungsermächtigung, daher trägt die GESAMTSUMME (S. 298) dieselbe Differenz von 2.700.000 C. |
| 6 | investitionen_produkt | P | 011201 | 23 | 2024 | ergebnis | -36145 | 115 | Produkt 011201 (Bauunterhaltung von kommunal genutzten Gebäuden), Teilfinanzplan Zeile 23 (Einzahlungen aus Investitionstätigkeit), Spalte Ergebnis 2024 (S. 115): gedruckt 36.145 C. Die Summe der in der Investitionsmaßnahmen-Tabelle (ab S. 115) gedruckten Einzahlungs-Kontozeilen ergibt für dieselbe Spalte 0 C. Wortweise gegen das PDF verifiziert: die 2024 tatsächlich gebuchte Einzahlung ist im aktuellen Haushalt keiner der dort aufgeführten, 2026 laufenden Maßnahmen mehr zugeordnet (historische Ist-Buchung auf einer inzwischen abgeschlossenen Maßnahme), kein Extraktionsfehler. |
| 6 | investitionen_produkt | P | 020701 | 30 | 2024 | ergebnis | -6328 | 142 | Produkt 020701 (Feuer- und Bevölkerungsschutz), Teilfinanzplan Zeile 30 (Auszahlungen aus Investitionstätigkeit), Spalte Ergebnis 2024 (S. 142): gedruckt 253.204 C. Die Summe der in der Investitionsmaßnahmen-Tabelle (ab S. 143) gedruckten Auszahlungs-Kontozeilen derselben Spalte ergibt 246.876 C. Wortweise gegen das PDF verifiziert: dieselbe Art historischer Ist-Differenz wie bei Produkt 011201 (siehe oben), kein Extraktionsfehler. |
| 6 | investitionen_produkt | P | 030102 | 23 | 2024 | ergebnis | -30940 | 157 | Produkt 030102 (Franz-von-Assisi-Grundschule), Teilfinanzplan Zeile 23, Spalte Ergebnis 2024 (S. 157): gedruckt 36.444 C. Die Summe der Einzahlungs-Kontozeilen der Investitionsmaßnahmen-Tabelle (ab S. 157) ergibt 5.504 C für dieselbe Spalte. Wortweise gegen das PDF verifiziert: dieselbe Art historischer Ist-Differenz wie bei Produkt 011201 (siehe oben), kein Extraktionsfehler. |
| 6 | investitionen_produkt | P | 050201 | 23 | 2024 | ergebnis | 2322 | 185 | Produkt 050201 (Zuschüsse an Dritte im Bereich des sozialen Lebens), Teilfinanzplan Zeile 23, Spalte Ergebnis 2024 (S. 185): gedruckt -2.322 C. Das Produkt druckt im aktuellen Haushalt keine Investitionsmaßnahmen-Tabelle mehr (EXTR-09, Flagged assumption: ohne Tabelle 0 C), die Summe ist daher 0 C. Wortweise gegen das PDF verifiziert: eine 2024 gebuchte, im aktuellen Haushalt nicht mehr geführte historische Ist-Buchung, kein Extraktionsfehler. |
| 6 | investitionen_produkt | P | 120101 | 23 | 2024 | ergebnis | -425849 | 243 | Produkt 120101 (Bau von Straßen, Wegen, Plätzen und sonstigen Verkehrsanlagen), Teilfinanzplan Zeile 23, Spalte Ergebnis 2024 (S. 243): gedruckt 1.335.695 C. Die Summe der Einzahlungs-Kontozeilen der Investitionsmaßnahmen-Tabelle (ab S. 245) ergibt 909.846 C für dieselbe Spalte. Wortweise gegen das PDF verifiziert: dieselbe Art historischer Ist-Differenz wie bei Produkt 011201 (siehe oben), kein Extraktionsfehler. |
| 6 | investitionen_produkt | P | 120102 | 30 | 2024 | ergebnis | -134535 | 249 | Produkt 120102 (Unterhaltung von Straßen, Wegen, Plätzen und sonstigen Verkehrsanlagen), Teilfinanzplan Zeile 30, Spalte Ergebnis 2024 (S. 249): gedruckt 134.535 C. Das Produkt druckt im aktuellen Haushalt keine Investitionsmaßnahmen-Tabelle mehr (EXTR-09, Flagged assumption: ohne Tabelle 0 C), die Summe ist daher 0 C. Wortweise gegen das PDF verifiziert: eine 2024 gebuchte, im aktuellen Haushalt nicht mehr geführte historische Ist-Buchung, kein Extraktionsfehler. |
| 6 | investitionen_gesamt | GESAMT |  | 23 | 2024 | ergebnis | -490612 | 63 | Gesamtfinanzplan Zeile 23, Spalte Ergebnis 2024 (S. 63): Summe der sechs produktweisen Ergebnis-2024-Differenzen bei Zeile 23 (011201, 030102, 050201, 120101, siehe oben), da alle anderen Produkte exakt übereinstimmen. Folge derselben historischen Ist-Differenzen, kein Extraktionsfehler. |
| 6 | investitionen_gesamt | GESAMT |  | 30 | 2024 | ergebnis | -142826 | 63 | Gesamtfinanzplan Zeile 30, Spalte Ergebnis 2024 (S. 63): Summe der produktweisen Ergebnis-2024-Differenzen bei Zeile 30 (020701, 120102, siehe oben), da alle anderen Produkte exakt übereinstimmen. Folge derselben historischen Ist-Differenzen, kein Extraktionsfehler. |
| 5 | vorbericht_zuwendungen | GESAMT |  | summe_posten | 2025 | ansatz | 1000 | 28 | Zuwendungen und allgemeine Umlagen, Spalte Ansatz 2025 (S. 28): Summe der Posten Schlüsselzuweisung (2.807), Zuweisungen für lfd. Zwecke (936) und Auflösung von Sonderposten (1.225) ergibt 4.968 T€, gedruckt ist die Gesamtzeile mit 4.967 T€. Wortweise gegen das PDF verifiziert; kein Extraktionsfehler, sondern eine Rundungsdifferenz von 1 T€ im Vorbericht selbst. |
| 5 | vorbericht_zuwendungen | GESAMT |  | summe_posten | 2026 | ansatz | -1000 | 28 | Zuwendungen und allgemeine Umlagen, Spalte Ansatz 2026 (S. 28): Summe der Posten (890 + 1.323 + 895 = 3.108 T€) liegt 1 T€ unter der gedruckten Gesamtzeile von 3.109 T€. Wortweise gegen das PDF verifiziert; kein Extraktionsfehler, sondern eine Rundungsdifferenz im Vorbericht selbst. |
| 5 | vorbericht_zuwendungen | GESAMT |  | gep_02 | 2026 | ansatz | -4200 | 28 | Zuwendungen und allgemeine Umlagen, Spalte Ansatz 2026 (S. 28): Die gedruckte Gesamtzeile von 3.109 T€ (= 3.109.000 €) weicht um 4.200 € von der Zeile 02 des Gesamtergebnisplans ab (3.113.200 €, S. 62, Spez. 3.8). Die App weist die Differenz als eigenen, berechneten Posten "Sonstige" aus. |
| 5 | vorbericht_transferaufwendungen | GESAMT |  | summe_posten | 2027 | planung | -1000 | 46 | Transferaufwendungen, Spalte Planung 2027 (S. 45-46): Summe der zehn Posten ergibt 15.756 T€, gedruckt ist die Gesamtzeile mit 15.757 T€. Wortweise gegen das PDF verifiziert; kein Extraktionsfehler, sondern eine Rundungsdifferenz von 1 T€ im Vorbericht selbst. |
| 5 | vorbericht_transferaufwendungen | GESAMT |  | summe_posten | 2028 | planung | -1000 | 46 | Transferaufwendungen, Spalte Planung 2028 (S. 45-46): Summe der zehn Posten ergibt 16.232 T€, gedruckt ist die Gesamtzeile mit 16.233 T€. Wortweise gegen das PDF verifiziert; kein Extraktionsfehler, sondern eine Rundungsdifferenz von 1 T€ im Vorbericht selbst. |
| 5 | vorbericht_transferaufwendungen | GESAMT |  | summe_posten | 2029 | planung | -1000 | 46 | Transferaufwendungen, Spalte Planung 2029 (S. 45-46): Summe der zehn Posten ergibt 16.746 T€, gedruckt ist die Gesamtzeile mit 16.747 T€. Wortweise gegen das PDF verifiziert; kein Extraktionsfehler, sondern eine Rundungsdifferenz von 1 T€ im Vorbericht selbst. |

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
