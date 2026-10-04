# Manuell abgeschriebene Vorberichtstabellen

Dieser Ordner enthält Vorberichtstabellen, die von Hand aus `raw_data/haushalt-2026.pdf`
abgeschrieben wurden (D-09, MANU-07), weil sie als reiner Fließtext mit Tabellenlayout
gedruckt sind und sich mit dem koordinatenbasierten Pipeline-Parser nicht zuverlässig
automatisiert extrahieren lassen. Die Abschrift ist **einmalig**: Nach dem Commit
überschreibt **kein Pipeline-Schritt** diese Dateien — `ostbevern.schema.schreibe_vorbericht_csv`
wird nur bei der Abschrift selbst und in Tests aufgerufen. Tippfehler fängt
[Regel 5](../pruefberichte/befunde.md) ab (zweistufiger Soll/Ist-Vergleich gegen die
gedruckte Gesamtzeile und den Gesamtergebnisplan); die CI prüft zusätzlich, dass sich
dieser Ordner bei einem erneuten Pipeline-Lauf nie ändert (D-24).

## Spaltenformat (`VORBERICHT_SPALTEN`, `ostbevern/schema.py`)

Jede Datei folgt demselben Langformat — eine Zeile je Posten, Jahr und Wertart:

| Spalte | Bedeutung |
|---|---|
| `tabelle` | Tabellenname, identisch zum Dateinamen ohne `.csv` |
| `position` | Gedruckte Reihenfolge der Zeile (1-basiert); die Gesamtzeile hat die höchste Position |
| `posten` | Schlüssel in Snake-Case ohne Umlaute, z. B. `grundsteuer_a` |
| `posten_name` | Gedruckter Name, wortwörtlich abgeschrieben (inkl. Abkürzungen wie „Krankenhausinvestitionsuml.“) |
| `ist_gesamt` | `true` für die gedruckte Gesamtzeile, sonst `false`; genau eine je (`tabelle`, `jahr`) |
| `jahr` | Haushaltsjahr der Spalte |
| `wertart` | `ergebnis` (Spalte „2024 vorl. RE“), `ansatz` oder `planung` — abgeleitet aus den Ergebnisplan-Spaltenköpfen der Jahrgangsdatei, nie von Hand eingetragen |
| `betrag_teur` | Betrag **in T€, exakt wie gedruckt** (D-05) — nie Euro, nie angepasst, auch wenn er von anderen Quellen abweicht |
| `anmerkung` | Fußnotentext oder sonstige Erläuterung zur Zeile, leer wenn keine vorhanden |
| `quelle` | 1-basierte PDF-Seite der gedruckten Zeile |

## Dateien

### `steuerarten.csv`

Vorbericht Tabelle 2.1.1 „Steuern und ähnliche Abgaben“ (S. 27): die acht Steuerarten
(Grundsteuer A/B, Gewerbesteuer, Anteil Einkommen-/Umsatzsteuer, Vergnügungs- und
Hundesteuer, Kompensationszahlungen) plus Gesamtzeile, für 2024–2029. Die Posten-Summe
trifft die gedruckte Gesamtzeile und die GEP-Zeile 01 in allen sechs Jahren exakt
(Regel 5 ohne Befund).

### `zuwendungen.csv`

Vorbericht Tabelle 2.1.2 „Zuwendungen und allgemeine Umlagen“ (S. 28): Schlüsselzuweisung,
Zuweisungen für lfd. Zwecke, Auflösung von Sonderposten, Gesamt. Zwei bekannte, im PDF
selbst liegende Abweichungen sind in `../pruefberichte/befunde.md` dokumentiert:

- 2025 ergibt die Posten-Summe 4.968 T€ gegenüber gedruckten 4.967 T€ (Δ 1 T€).
- 2026 ergibt die Posten-Summe 3.108 T€ gegenüber gedruckten 3.109 T€ (Δ 1 T€), und die
  gedruckte Gesamtzeile (3.109 T€ = 3.109.000 €) weicht um 4.200 € von der GEP-Zeile 02
  (3.113.200 €) ab (Spez. 3.8). Die App weist diese Differenz als eigenen, berechneten
  Posten „Sonstige“ aus (`ostbevern.app_daten.baue_vorbericht_tabelle`).

### `transferaufwendungen.csv`

Vorbericht Tabelle 2.2.5 „Transferaufwendungen“ (S. 45–46): zehn Posten (Wasser- und
Bodenverband, Zuschüsse an Kindertageseinrichtungen, Zuschuss an das Kinder- und
Jugendwerk, Zuschuss an die OGS, Zuschüsse für lfd. Zwecke, Sozialleistungen,
Gewerbesteuerumlage, Krankenhausinvestitionsumlage, Kreisumlage, Verlustübernahme BBO)
plus Gesamt.

**Kreisumlage, Fußnote (S. 46):** Der Vorbericht druckt den Betrag des Haushaltsjahrs als
„10.1473“ — die Fußnotenziffer 3 ist ohne Leerzeichen an 10.147 angeklebt. Gespeichert ist
der korrigierte Wert `10147` (T€) mit einer Anmerkung, die auf die Fußnote verweist: Zur
Entlastung des Haushalts 2026 wird eine Rückstellung aus dem Jahresabschluss 2024 in Höhe
von 1.325.478 € aufgelöst, die Umlage 2026 liegt bei rd. 11,5 Mio. € (Kreisumlage brutto =
netto + Rückstellungsauflösung, siehe `meta.json`, D-10). Der hier gespeicherte Betrag ist
die Kreisumlage **netto**.

Drei weitere Jahre (2027–2029) haben eine gedruckte Rundungsdifferenz von 1 T€ zwischen
Posten-Summe und Gesamtzeile; dokumentiert in `../pruefberichte/befunde.md`.

**Weitergabe an Kreis und Land (D-01):** Die drei Posten Kreisumlage, Gewerbesteuerumlage
und Krankenhausinvestitionsumlage ergeben in jedem Jahr 2024–2029 (× 1000, Toleranz
±3.000 €) die Zeile 15 des Teilergebnisplans von Produkt 160101 (S. 281) — geprüft von
Regel 5 über `[layout.weitergabe_kreis_land]` in `pipeline/jahrgaenge/2026.toml`.

### `kita_zuschuesse.csv`

Aufschlüsselung der sieben Kindertageseinrichtungen (S. 46) für das Haushaltsjahr 2026 —
die Tabelle druckt nur diese eine Spalte, nicht den ganzen Finanzplanungszeitraum
(MANU-04). Die Summe der sieben Einrichtungen (559 T€) entspricht sowohl der gedruckten
Gesamtzeile dieser Tabelle als auch dem Transferaufwendungen-Posten „Zuschüsse an
Kindertageseinr.“ desselben Jahres — beides prüft Regel 5.

### `investitionszuwendungen.csv`

Vorbericht S. 52 „Bei den Zuweisungen und Zuschüssen für Investitionen handelt es sich um:“
(EINN-06, Phase 5 D-03): die vier Pauschalen (Investitions-, Schul-, Sport- und
Feuerschutzpauschale) und die sechs Förderungen für einzelne Maßnahmen mit der gedruckten
Gesamtzeile 3.742 T€. Wie `kita_zuschuesse.csv` druckt die Tabelle nur **eine** Spalte, das
Haushaltsjahr (Wertart `ansatz`); für die übrigen Jahre gibt es keine Aufschlüsselung, die App
zeigt dort „–“ je Pauschale. Die Fördersätze stehen als Teil des gedruckten Namens im Posten
(z. B. „Förderung Wirtschaftswege (70 %)“, Schlüssel `foerderung_wirtschaftswege_70`). Die
Tabelle hat bewusst keine Ergebnisplan-Zeile (Spez. 3.1: Finanzplan-Betrag gehört nicht in
eine Ergebnisplan-Struktur); Regel 5 prüft in Stufe (a) die Summe der zehn Posten gegen die
gedruckte Gesamtzeile und in Stufe (b) die Gesamtzeile × 1000 gegen die Gesamtfinanzplan-Zeile
18 „Zuwendungen für Investitionsmaßnahmen“ desselben Jahres (Toleranz ±1.000 €). Beides trifft
auf den eingecheckten Daten exakt (Σ = 3.742 T€ = 3.742.000 €).

### `weitere_vorberichtstabellen.csv`

Die sechs weiteren Vorberichtstabellen (fünf aus Spez. 4.3, D-08, plus 2.1.7 seit Phase 5
D-04), jede mit Aufschlüsselung und Gesamtzeile für 2024–2029, Spalte `tabelle`
unterscheidet sie:

| `tabelle` | Vorbericht-Ziffer | Seiten |
|---|---|---|
| `leistungsentgelte` | 2.1.4 Öffentlich-rechtliche Leistungsentgelte | 29–30 |
| `kostenerstattungen` | 2.1.6 Kostenerstattungen und Kostenumlagen | 32 |
| `personal` | 2.2.1 Personalaufwendungen | 34 |
| `sachaufwand` | 2.2.3 Aufwendungen für Sach- und Dienstleistungen | 36–37 |
| `sonstige_aufwendungen` | 2.2.6 Sonstige ordentliche Aufwendungen | 48 |
| `sonstige_ertraege` | 2.1.7 Sonstige ordentliche Erträge | 33 |

Posten-Schlüssel folgen derselben Ableitungsregel wie in allen anderen manuellen
Dateien: gedruckter Name klein geschrieben, Umlaute ausgeschrieben (ä→ae, ö→oe, ü→ue,
ß→ss), jede Folge anderer nicht-alphanumerischer Zeichen wird zu `_`, führende/
abschließende `_` entfernt. Zwei Zeilen je Tabelle haben einen über zwei Textzeilen
umgebrochenen Namen (S. 30 „Auflösung von Sonderposten aus Beiträgen und Gebühren“,
S. 32 „Erst v. Gemeinden und sonst. öffentlicher Bereich“ und „Erst. für Essen in der
Mensa und den OGS“); der Name ist mit einem Leerzeichen zusammengefügt. Dasselbe gilt für
„Auflösung sonstiger Sonderposten“ in Tabelle 2.1.7 (S. 33).

**Tabelle 2.1.7 `sonstige_ertraege` (S. 33, EINN-04):** fünf Posten (Konzessionsabgaben,
Verkauf von Umlaufvermögen, Bußgelder / Säumniszuschläge, Auflösung sonstiger Sonderposten,
Herabsetzung Rückstellungen) plus Gesamtzeile, wie gedruckt. Die Tabelle wird gegen Zeile 07
des Gesamtergebnisplans geprüft (Regel 5, Stufe b). Vier gedruckte Abweichungen sind in
`../pruefberichte/befunde.md` dokumentiert: die Rundungsdifferenzen 2024 (Σ Posten 2.766 T€
gegenüber gedruckten 2.764 T€) und 2025 (2.107 gegenüber 2.106 T€) sowie ein **Druckfehler
2028**: die gedruckte Gesamtzeile nennt 2.396 T€, die Posten ergeben 2.345 T€, und die GEP-Zeile
07 liegt bei 2.346.161 €. Die CSV hält den gedruckten Wert 2.396 fest (D-05: nie
angepasst). Die App folgt der GEP-Zeile und weist die Differenz zwischen GEP-Zeile und
Summe der Posten als eigenen, berechneten Posten „Sonstige“ aus, und zwar genau in den
Jahren, in denen die gedruckte Gesamtzeile um mehr als 1.000 € von der GEP-Zeile abweicht
(`ostbevern.app_daten.baue_vorbericht_tabelle`, `sonstige=True`, wie bei `zuwendungen`).

Bewusst **nicht** abgeschrieben (D-08, MANU-05):

- 2.1.5 Privatrechtliche Leistungsentgelte, 2.1.9 Erträge aus internen Leistungsbeziehungen,
  2.2.2 Versorgungsaufwendungen und 2.2.5 Transferaufwendungen (separat in
  `transferaufwendungen.csv`, MANU-03) — Spez. 4.3 listet nur die fünf ursprünglichen
  Tabellen für Phase 4; 2.1.7 wurde in Phase 5 (EINN-04) nachgeholt.
- Die Objekt/Maßnahme-Detailtabelle „Gebäudeunterhaltung“ unter 2.2.3 (S. 37, unterhalb
  der Gesamtzeile): sie schlüsselt den Posten `gebaeudeunterhaltung` weiter auf,
  gehört aber nicht zur Haupttabelle (D-08) und wird nicht benötigt.

### `meta.json`

Einzelwerte aus der Haushaltssatzung (S. 8/9) und dem Vorbericht (S. 9/10/24-25/46-47),
validiert über `ostbevern.manuell.lies_meta_json` gegen eine strikte Schlüssel-Allowlist
(MANU-06): jeder Wert trägt `wert`, `einheit` und `quelle` (1-basierte PDF-Seite), optional
`stichtag`, `herkunft`, `berechnet`, `gerundet`, `formel`, `vorjahr`, `anmerkung`.

| Schlüssel | Wert | Quelle |
|---|---|---|
| `einwohner` | 11.741 (Stichtag 30.06.2024, Herkunft IT.NRW) | S. 25 |
| `flaeche` | 8.960 ha (= 89,6 qkm, wie gedruckt umgerechnet) | S. 10 |
| `hebesaetze.grundsteuer_a` / `_b` / `gewerbesteuer` | 242 / 554 / 418 v. H. | S. 9 (§ 6) |
| `kreisumlage.netto` | 10.147.000 € (T€-Wert aus `transferaufwendungen.csv`, gerundet) | S. 46 |
| `kreisumlage.rueckstellungsaufloesung` | 1.325.478 € (Fußnote 3) | S. 46 |
| `kreisumlage.brutto` | 11.472.478 € = netto + Rückstellungsauflösung (berechnet, gerundet) | S. 46 |
| `kreisumlage.hebesatz_kreisumlage` | 36,3 % (363 Promille, Vorjahr 33 % = 330) | S. 47 |
| `kreisumlage.hebesatz_jugendamtsumlage` | 21 % (210 Promille, Vorjahr 20,3 % = 203) | S. 47 |
| `vorbericht_werte.konzessionsabgabe_strom` / `_gas` / `_wasser` | 315.000 / 40.000 / 115.000 € (T€-Werte × 1000, gerundet) | S. 33 |
| `satzung.beschluss` | 2026-03-03 (Ratsbeschluss) | S. 8 |
| `satzung.ausfertigung` | 2026-03-04 (Unterschriftsdatum) | S. 9 |

**Konzessionsabgaben nach Sparten (S. 33, EINN-04):** Der Text unter Tabelle 2.1.7 nennt die
Aufteilung der Konzessionsabgaben des Haushaltsjahrs auf Strom (315 T€), Gas (40 T€) und
Wasser (115 T€). Die Aufteilung ist nur für das Haushaltsjahr gedruckt, für andere Jahre wird
nichts ergänzt. Regel 5 (`plan` `vorbericht_konzessionsabgaben`) prüft, dass die Summe der drei
Werte exakt dem Posten `konzessionsabgaben` von Tabelle 2.1.7 des Haushaltsjahrs entspricht
(470 T€).

**Warum `kreisumlage.brutto` berechnet ist:** Der Vorbericht druckt auf S. 46 nur den
**netto**-Betrag der Kreisumlage (10.1473 T€, mit angeklebter Fußnotenziffer 3 — siehe
`transferaufwendungen.csv` oben). Die Fußnote erklärt, dass eine Rückstellungsauflösung
von 1.325.478 € den Haushalt 2026 entlastet und die tatsächliche Umlage 2026 „bei rd.
11,5 Mio. €" liegt. `kreisumlage.brutto` bildet diese Rechnung nach (Regel 5,
`meta_kreisumlage`, D-10) und wird zusätzlich gegen die gerundete Fußnote geprüft
(±50.000 €, da der Fußnotentext selbst nur „rd." ist).

**Promille statt Prozent beim Kreis:** `hebesatz_kreisumlage`/`hebesatz_jugendamtsumlage`
stehen als int-Promille (36,3 % → 363), damit `meta.json` durchgängig ganzzahlig bleibt
(anders als `hebesaetze.*`, die als ganze Prozentpunkte bereits ganzzahlig sind).

**Bewusst nicht gespeichert (Datenschutz):** Die Unterschriftenzeile auf S. 9 druckt die
Namen der Kämmerin und des Bürgermeisters neben dem Ausfertigungsdatum — diese Namen
werden nicht abgeschrieben, nur das Datum selbst (`satzung.ausfertigung`).

### `verbindlichkeiten.csv`

Übersicht über den voraussichtlichen Stand der Verbindlichkeiten (S. 310, TEUR wie
gedruckt), drei Jahre (Stand Ende 2024, Ende 2025 = Beginn Haushaltsjahr, Ende 2026):
Kredite für Investitionen, Liquiditätskredite, Lieferungen und Leistungen,
Transferleistungen, Sonstige Verbindlichkeiten, Erhaltene Anzahlungen, Summe aller
Verbindlichkeiten (`tabelle` `verbindlichkeiten`, `position` = gedruckte Zeilennummer
2/3/5/6/7/8/9) sowie nachrichtlich die Bürgschaft für die Bäder- und
Beteiligungsgesellschaft Ostbevern mbH (`tabelle` `buergschaften`, keine Gesamtzeile,
`pruefung.REGEL5_TABELLEN_OHNE_GESAMT`). Gedruckte „--“-Zeilen (1. Anleihen; 4.
Verbindlichkeiten aus Vorgängen, die Kreditaufnahmen wirtschaftlich gleichkommen;
2.1–2.6, 3.1/3.2 Unterzeilen) werden nicht transkribiert.

**Transferleistungen enthalten die NRW.Bank-Mittel (D-14):** Zeile 6 „Verbindlichkeiten
aus Transferleistungen“ (1.221 / 831 / 746 T€) enthält die bislang abgerufenen Mittel
aus dem Kreditprogramm der NRW.Bank für Flüchtlingsunterkünfte, die haushaltsrechtlich
nicht als Kredit, sondern als Transferverbindlichkeit ausgewiesen werden (S. 24). Die
Vorbericht-Definition des Schuldenstands (`manuell.SCHULDEN_POSTEN`) ist deshalb
Kredite für Investitionen **plus** Transferleistungen, nicht nur die Kredite allein —
Ende 2025: 6.879 + 831 = 7.710 T€, bei 11.741 Einwohnern rund 656 € (Pro-Kopf-
Verschuldung, Regel 9, Anhang B.6).

Regel 5 prüft die Investitionskredit-Fortschreibung (`kredite_fortschreibung`): Ende
Haushaltsjahr = Ende Vorjahr + GFP-Kreditaufnahme (Z. 33) − GFP-Tilgung (Z. 35) =
6.879 + 5.200 − 450 = 11.629 T€, exakt wie gedruckt.

**Fortschreibungsbasis bestätigt (D-14, Plan 04-05 Task 2):** Der NRW.Bank-Anteil für
2027–2029 wird auf dem zuletzt gedruckten Stand (746 T€, Ende 2026, S. 310) konstant
gehalten, nicht auf dem Ende-2025-Wert (831 T€). Fachlich geprüft und bestätigt am
2026-10-03.

### `eigenkapital.csv`

Übersicht über die Entwicklung des Eigenkapitals (S. 311), sechs Jahre 2024–2029:
Allgemeine Rücklage, Einmalige Verrechnung Bilanzierungshilfe, Sonderrücklagen,
Ausgleichsrücklage, Bilanzieller Verlustvortrag, Jahresergebnis, Summe Eigenkapital.
Die all-null Zeile „Nicht durch Eigenkapital gedeckter Fehlbetrag“ wird nicht
transkribiert (D-11).

**Rundung (D-12):** S. 311 druckt Beträge mit Cent; `betrag` ist **kaufmännisch auf
int-Euro gerundet** (0,5 Cent aufwärts, von Null weg), z. B. Jahresergebnis 2026
−2.353.505,75 € → **−2.353.506 €**. Diese Rundung trifft sowohl Satzung § 4 als auch
Zeile 28 des Gesamtergebnisplans exakt — ein Beleg, dass kaufmännische Rundung (statt
z. B. Abschneiden) die richtige Wahl ist. Die T€-Werte aus S. 310 (`verbindlichkeiten.csv`)
bleiben dagegen `betrag_teur` wie gedruckt (D-05); nur S. 311 wird eurogenau gerundet.

**Dokumentierte Abweichung:** Das Jahresergebnis 2025 ist auf S. 311 mit „0,00 €“
gedruckt, während Zeile 28 des Gesamtergebnisplans für 2025 −1.331.520 € ausweist —
siehe [`../pruefberichte/befunde.md`](../pruefberichte/befunde.md). Alle anderen fünf
Jahre treffen Zeile 28 exakt.

**Satzung § 4 (Research Pitfall 4):** Die Verringerung der Ausgleichs- bzw. der
allgemeinen Rücklage (Satzung § 4, S. 9: 2.132.213 € / 221.293 €) ist **nicht** der
rohe Jahresdelta der Eigenkapitalübersicht — eine „Einmalige Verrechnung
Bilanzierungshilfe“ (−476.327 €) überlagert 2026 den reinen Rücklagenverzehr. Die
korrekte Prüfung (Regel 5, `plan` `satzung_paragraf4`) ist: Ausgleichsrücklage Stand
Haushaltsjahr − Stand Folgejahr = 2.132.213,17 − 0,00 = 2.132.213 € (gerundet) und die
Summe beider § 4-Beträge (2.132.213 + 221.293 = 2.353.506 €) entspricht exakt
|GEP Z. 28| des Haushaltsjahrs.

### `ve_uebersicht.csv`

Übersicht über die aus Verpflichtungsermächtigungen voraussichtlich fällig werdenden
Auszahlungen (S. 309): acht Fälligkeitszeilen (Produkt, Maßnahme, Fälligkeitsjahr,
Betrag) und drei Summenzeilen (`ist_gesamt` true, `produkt`/`massnahme` null):
VE-Gesamtbetrag (`faellig_jahr` null, 11.600 T€ — identisch mit der
Verpflichtungsermächtigung aus Satzung § 3 und GFP Z. 30), Summe fällig 2027
(9.400 T€) und Summe fällig 2028 (2.200 T€); 2029 und Folgejahre sind durchgängig „--“
und werden nicht transkribiert.

**Schreibweise Kohkamp:** S. 309 druckt „Kohkamp IIII“, S. 25 „Kohkamp III“ — beide
wortwörtlich wie gedruckt übernommen (D-09), mit Anmerkung bei der S.-309-Zeile.

Regel 5 prüft den VE-Gesamtbetrag gegen GFP Z. 30 (Wertart VE) und jedes
(Produkt, Fälligkeitsjahr)-Paar gegen die bereits extrahierte `ve_faelligkeiten.csv`
(Phase 3); ein Paar, das nur in einer der beiden Quellen vorkommt, wäre eine
strukturelle Lücke (wie bei Regel 6) — auf den eingecheckten Daten gibt es keine.

### Regel 9 – Eckwerte (Anhang B.6)

Neben Regel 5 prüft die neue, exakte Regel 9 die `[eckwerte.*]`-Sollwerte aus
`pipeline/jahrgaenge/2026_sollwerte.toml` (Anhang B.6) gegen `meta.json` bzw.
`zuwendungen.csv` (Schlüsselzuweisung des Haushaltsjahrs und Vorjahrs): Einwohner,
die drei Hebesätze, die Kreis-/Jugendamtsumlage-Hebesätze (je mit Vorjahr), die
Schlüsselzuweisung und (seit `verbindlichkeiten.csv`) die Pro-Kopf-Verschuldung Ende
Vorjahr — `manuell.pro_kopf_euro(manuell.schuldenstand_euro(verbindlichkeiten, Ende
Vorjahr), meta.einwohner)` = 7.710.000 // 11.741 = **656 €** (ganzzahlige Division,
abgerundet, reproduziert den gedruckten Vorbericht-Wert exakt). Ein `[eckwerte.*]`-
Name, der von keiner Regel konsumiert wird, bricht die Prüfung ab
(`pruefung.pruefe_eckwerte_konsumiert`) — kein Sollwert bleibt unbewacht.

**Dokumentierte Abweichungen** (Regel 5, Details in
[`../pruefberichte/befunde.md`](../pruefberichte/befunde.md)): Stufe (a, Posten-Summe
vs. gedruckte Gesamtzeile) weicht bei `leistungsentgelte` 2024/2029, `kostenerstattungen`
2025–2029 (außer 2028) und `sachaufwand`/`sonstige_aufwendungen` in mehreren Planungs-
jahren um 1–3 T€ ab — gedruckte Rundungsdifferenzen im Vorbericht selbst, wortweise
gegen das PDF verifiziert. Stufe (b, Gesamtzeile vs. Gesamtergebnisplan) weicht bei
`leistungsentgelte` 2029 (−1.035 €) und bei `sachaufwand` 2027–2029 (−3.021 € / −3.705 €
/ −3.846 €) über die ±1.000-€-Toleranz hinaus ab.

### `texte/erklaerungen.md`

Die zehn Erklärtexte des Vorberichts (MANU-08, D-15 bis D-17), die Phase 5/6 in der
App anzeigen. Die Datei folgt einem eigenen, von `ostbevern.texte` geparsten Format,
keinem CSV-Langformat:

```markdown
# Erklärtexte

## schluessel
Titel: Ein Titel
Quelle: S. 28

Ein Absatz mit {{meta.einwohner|zahl}} Platzhaltern. Jahreszahlen wie 2026, "§ 4"
und "S. 311" dürfen als bloße Ziffern stehen; jede andere Zahl muss ein Platzhalter
sein, sonst bricht die Pipeline ab.

Ein zweiter Absatz, durch eine Leerzeile getrennt.
```

**Platzhalter-Syntax (D-15):** `{{schluessel|formatkuerzel}}`. `schluessel` ist ein
Pfad in die kuratierte Werte-Namensraum, die `ostbevern.texte.textwerte` aus
`haushalt.json`/`investitionen.json`/`produkte.json` baut (z. B.
`vorbericht.zuwendungen.schluesselzuweisung.2026`, `meta.einwohner`,
`schulden.pro_kopf.2025`, `ve.gesamt`, `abgeleitet.<name>` für benannte, in
`ostbevern/texte.py::ABGELEITET` dokumentierte Formeln). `formatkuerzel` ist eines aus
`ostbevern.texte.FORMATKUERZEL` = `app/src/charts/format.ts::FormatKuerzel`: `euro`,
`mio`, `zahl`, `jahr`, `prozent`, `promille`, `vzae`. `zahl` gruppiert Tausender (z. B.
Einwohner), `jahr` gibt eine Jahreszahl ohne Tausendertrennung aus; Jahres-Platzhalter
wie `jahr.haushaltsjahr` stehen deshalb immer mit `jahr` (CR-01). Die Pipeline löst den
Schlüssel gegen den Rohwert auf und schreibt ihn unformatiert nach
`app/src/data/texte.json` — **formatiert wird ausschließlich in der App** über
`format.ts::formatiere` (D-15). Ein unbekannter Schlüssel oder ein unbekanntes
Formatkürzel bricht Schritt 07 mit `TexteFehler` ab.

**Ziffernregel:** Jede Zahl außerhalb eines Platzhalters ist ein Fehler, den
`ostbevern.texte.pruefe_text` findet — mit drei Ausnahmen: eine vierstellige
Jahreszahl (19xx/20xx), ein Paragraph (`§ n`) und ein Seitenverweis (`S. n`, auch als
Spanne wie `S. 24/25`). HTML-Zeichen (`<`, `>`) sind ebenfalls verboten, weil die App
die Texte als reinen Text rendert (T-04-17).

**Fachliche Prüfung vor Commit (D-17):** Der Executor entwirft die Texte auf Basis der
zitierten Vorbericht-Seiten; ein Checkpoint im Plan legt sie dem Nutzer zur fachlichen
Abnahme vor — Zahlen gegen das PDF, neutrale Formulierung (Einschätzungen der
Verwaltung werden dem Vorbericht zugeschrieben, nie als Aussage der App dargestellt).
Erst nach Freigabe werden `erklaerungen.md` und etwaige neue `meta.json`-Einträge
unter `vorbericht_werte` committet. Zwei solche Einträge — `bbo_verlustausgleich_wirtschaftsplan`
(S. 48) und `satzung_verringerung_allgemeine_ruecklage` (S. 9, § 4) — existieren in
keiner anderen Datei und sind deshalb hier statt in einer CSV gespeichert.

**Jahrneutrale Erklärtexte (Phase 5, D-02, D-19):** Seit Phase 5 enthält die Datei neben den
zehn Texten des Vorberichts sieben Abschnitte ohne jeden Platzhalter
(`steuern_selbst_festgelegt`, `zuwendungen_laufende_zwecke`, `ueberschuss_pb_16`,
`ueberschuss_pb_11`, `ueberschuss_allgemein`, `ueberschuss_ruecklage`,
`geldfluss_lesehilfe`). Sie gelten für jedes wählbare Jahr; ein Test hält sie
platzhalterfrei. **Quellenregel (D-02):** Für ein Jahr, in dem Plan oder Vorbericht einen Wert
haben (ab dem ersten Jahr von `haushalt.jahre`), zitiert ein Erklärtext nie eine Grundzahl in
Euro (`grundzahlen.<produkt>.<position>.<jahr>`), sondern den Wert aus `vorbericht.*` — so
zeigen Text und Diagramm für dasselbe Jahr denselben Wert. Schritt 07 und ein Test lehnen
einen solchen Platzhalter ab (`ostbevern.texte.pruefe_grundzahl_jahre`). Quellseiten werden
einzeln geschrieben (`Quelle: S. 24, S. 25`, nicht `S. 24/25`), weil der Parser bei einer
Spanne nur die erste Seite übernimmt.

### `texte/glossar.md`

Die Begriffsdefinitionen der Seite `/glossar` und der `GlossarBegriff`-Tooltips (GLOS-01,
D-14 bis D-16). Das Format gleicht `erklaerungen.md` (gleiche Platzhalter, gleiche
Ziffernregel, kein HTML), mit drei Unterschieden: die erste Zeile ist `# Glossar`, der
Kopfblock besteht aus der Zeile `Titel:` (der angezeigte Begriff) und einer **optionalen**
Zeile `Quelle:`, und die `Quelle:`-Zeile ist **Pflicht, sobald ein Absatz des Begriffs einen
Platzhalter enthält** (Seitenverweis bei Zahlen).

```markdown
# Glossar

## hebesatz
Titel: Hebesatz
Quelle: S. 9

Der erste Satz steht allein und dient als Tooltip. Er enthält nie eine Zahl.

Weitere Sätze dürfen Platzhalter wie {{meta.hebesaetze.gewerbesteuer|prozent}} enthalten.
```

Der Abschnittsschlüssel (`hebesatz`) ist der stabile Anker `/glossar#hebesatz`; er ändert
sich nie, auch wenn der Titel umformuliert wird. Mindestens die 22 Begriffe aus Spez. 6.14
müssen vorhanden sein (Test `test_glossar_pflichtbegriffe`). Schritt 07 schreibt das Glossar
als `glossar` nach `app/src/data/texte.json`; die Texte werden wie die Erklärtexte nach
fachlicher Abnahme (D-15) committet.
