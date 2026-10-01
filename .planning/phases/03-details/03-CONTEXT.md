# Phase 3: Details - Context

**Gathered:** 2026-10-01
**Status:** Ready for planning

<domain>
## Phase Boundary

Die Pipeline beschreibt alle 63 Produkte inhaltlich vollständig und gleicht die Investitionsmaßnahmen mit den Finanzplänen ab:
- **03 Produktinfos** (`pipeline/03_produktinfos.py`): `daten/aufbereitet/produkte.json` (Fachbereich, Gremium, Beschreibung, Leistungen, Auftragsgrundlage, Bindungsgrad normalisiert und original, Klassifizierung, Zielgruppe, Ziele, PDF-Seiten, eingebettete Erläuterungen), `grundzahlen.csv` (inklusive Steuer-Istwerte 2022–2025 aus 160101) und `erlaeuterungen.csv`
- **04 Investitionen** (`pipeline/04_investitionen.py`): `investitionen.csv` nur aus den Produktseiten, `ve_faelligkeiten.csv` aus den „(Kassenwirksamkeit)“-Zeilen
- **Querschnitte:** `daten/zwischen/querschnitte.csv` (S. 291–300) als reine Kontrollquelle
- **06 Prüfen:** Prüfregeln 6, 7 und 8 kommen zu den Regeln 1–4 hinzu. `konsistenz.md` meldet 1–4 und 6–8 als grün.

Nicht in dieser Phase: manuelle Vorberichtstabellen und Prüfregel 5, Stellenplan, `meta.json`, App-JSON (`07_app_daten.py`) und die CI-Diff-Prüfung. All das gehört zu Phase 4.

</domain>

<decisions>
## Implementation Decisions

### Erläuterungsposten
- **D-01:** Ein **Posten** beginnt mit einem führenden Betrag und dem Eurozeichen `C`, z. B. „66.500 C Strom, Nahwärme, …“. Der Posten bekommt `betrag` (int) und `text`. Unterbeträge im Text, etwa „(zusätzlich 55.000 C aus Rückstellungen …)“, bleiben Teil des Textes und werden **nicht** als eigene Posten gezählt. Zeilen ohne führenden Betrag kommen als Freitext ohne Betrag in den Block, z. B. Einleitung „In den Ansätzen sind u. a. enthalten:“ oder Schlusssätze „u. a. Erstattungen an die BBO …“. Mehrzeilige Postentexte werden zusammengeführt.
- **D-02:** Blöcke **ohne „zu Nr. …“** (z. B. S. 184, Sozialhilfe nach SGB XII) werden mit **leerem `zu_zeilen`** übernommen. Sie gelten als allgemeiner Hinweis zum Produkt. Varianten der Kopfzeile wie „Zu Nr.“, „zu Nr. 02 und 13“ und „Nr. 13 und Nr. 16“ werden auf eine Liste von Zeilennummern normalisiert. Die Nummern sind Strings mit führender Null (Phase 2 D-21).
- **D-03:** Erläuterungen liegen an **zwei Stellen**. Die Quelle für Prüfungen und Diffs ist `daten/aufbereitet/erlaeuterungen.csv` im Langformat, sinngemäß mit den Spalten `produkt, block, position, zu_zeilen, betrag, text, pdf_seite`. Dabei ist `betrag` bei Freitextzeilen leer, `zu_zeilen` ist eine Liste in einer Spalte (Kodierung nach Claudes Ermessen). Zusätzlich wird alles wie in Spez. 4.2 unter `erlaeuterungen` in `produkte.json` eingebettet.
- **D-04:** Die Erläuterungen werden **nur auf Plausibilität** geprüft, nicht auf Summen, denn die Posten sind ausdrücklich „u. a. enthalten“. Erstens muss jede Zeile in `zu_zeilen` im Teilergebnisplan des Produkts gedruckt sein. Zweitens darf kein einzelner Posten die Summe der bezogenen Zeilen im Ansatz 2026 übersteigen. Ein Verstoß **bricht ab** (Phase 2 D-08), mit PDF-Seite.

### Investitionen
- **D-05:** **Regel 6 prüft alle sieben Spalten**: Ergebnis 2024, Ansatz 2025, Ansatz 2026, VE 2026, Planung 2027–2029. Erstens muss die Summe der Maßnahmen je Produkt die Teilfinanzplan-Zeilen Z. 23 (Einzahlungen) und Z. 30 (Auszahlungen) ergeben. Zweitens muss die Summe aller Maßnahmen die Gesamtfinanzplan-Zeilen Z. 23/30 ergeben (2026: 7.224.830 € / 12.280.484 €). Abweichungen über 1 € sind Fehler, außer sie stehen in `befunde.md` (Phase 2 D-02, D-04, D-05).
- **D-06:** Die **PB-Investitionslisten** (Seitentyp `investitionen_pb`) werden mit demselben Parser gelesen, aber **nicht ausgeliefert**. Sie sind Teil von Regel 6: Maßnahmen-IDs und Beträge je Maßnahme, Konto, Jahr und Wertart müssen mit den Produktseiten übereinstimmen. Eine Maßnahme, die nur in einer der beiden Quellen vorkommt, ist ein Fehler. Quelle für `investitionen.csv` sind weiterhin **ausschließlich die Produktseiten** (Spez. 3.8).
- **D-07:** `investitionen.csv` erhält eine Spalte **`art`**. Sie wird über eine feste Zuordnung der Kontengruppen nach NKF aus dem Konto abgeleitet, z. B. Baumaßnahmen, Grundstücke, bewegliches Vermögen/Fahrzeuge/Ausstattung, Investitionszuwendungen und Beiträge auf der Einzahlungsseite. Die Zuordnung ist eine **fachliche Regel im Code** (Phase 1 D-07), keine Jahrgangskonfiguration. Ein unbekanntes Konto **bricht ab** (D-08). Phase 5 nutzt `art` für den Filter auf `/investitionen` (Spez. 6.10). — **Reversibility:** costly — Die App-JSON (Phase 4) und der Filter in Phase 5 verlassen sich auf das Vokabular von `art`.
- **D-08:** Die gedruckten **Zwischen- und Saldozeilen** werden beim Parsen als **Gegenprobe geprüft, aber nicht gespeichert**. Gemeint sind „Einzahlungen/Auszahlungen aus Investitionstätigkeit“ je Maßnahme, „Saldo <ID>“ und am Ende „Saldo Investitionstätigkeit“. Kontozeilen müssen die Ein- und Auszahlungszeile ergeben, diese den Saldo der Maßnahme, und alle Maßnahmen zusammen den Saldo Investitionstätigkeit. Ein Verstoß bricht ab. Die Saldozeile „Saldo <ID>“ dient außerdem dazu, Maßnahmen-ID und Namen sicher zu trennen. Beispiel: „BGA0301014Betriebs-u.Geschäftsausst.…“ mit ID `BGA0301014`. In `investitionen.csv` stehen nur Kontozeilen.

### Personennamen und Freitexte
- **D-09:** **Personennamen** aus „Verantwortliche/r“ und „Sachbearbeiter/innen“ werden beim Parsen als Felder erkannt, damit die Struktur der Produktinformationen stimmt. Danach werden sie **verworfen** und nie in eine Datei geschrieben, auch nicht unter `daten/`. Grund: `daten/` wird eingecheckt, und das Repo liegt auf GitHub. Ein Test stellt sicher, dass `produkte.json` keine Schlüssel `verantwortlich` oder `sachbearbeiter` enthält und dass in `daten/` keine der gelesenen Namen vorkommen. Das ist eine **bewusste Verschärfung** gegenüber Spez. 4.2 und PROJECT.md („extrahiert, aber nicht ausgeliefert“). Phase 4 (DATA-01) muss dadurch nichts mehr entfernen. — **Reversibility:** reversible — Die Namen lassen sich jederzeit erneut aus dem PDF lesen.
- **D-10:** Freitexte werden als **lesbarer Fließtext** gespeichert. Gemeint sind Beschreibung, Auftragsgrundlage, Zielgruppe, Ziele, Leistungen und Erläuterungstexte. Die Leerzeichen werden wiederhergestellt, denn `extract_text()` liefert „DieGemeindeOstbevern…“. Mit `extract_words(x_tolerance=1)` klappt das in einer Stichprobe. PDF-Zeilen werden mit Leerzeichen verbunden. **Silbentrennung:** Ein „-“ am Zeilenende vor einem Kleinbuchstaben wird entfernt („Hochbaumaßnah-/men“ → „Hochbaumaßnahmen“). Vor einem Großbuchstaben oder vor „und/oder/sowie“ bleibt es stehen („Bildungs-, Generationen- und …“, Bindestrich-Komposita).
- **D-11:** **Feldtypen in `produkte.json`:** `leistungen` ist eine Liste, ein Eintrag je Aufzählungspunkt (Glyphe `(cid:15)`). Folgezeilen eines Punkts werden angehängt. `beschreibung`, `auftragsgrundlage`, `zielgruppe` und `ziele` sind **Strings**, wie in Spez. 4.2. Mehrere Zeilen ohne Aufzählungszeichen werden mit Leerzeichen verbunden, ohne Heuristik zur Aufteilung in Punkte.

### Grundzahlen
- **D-12:** `grundzahlen.csv` hat eine Spalte `hinweis` **je Wert, auf das betroffene Jahr bezogen**. Der Spaltenstichtag „Stand 30.06.“ gilt nur für jahr=2025. Eine überschreibende Fußnote wie „Ist-Wert 2025: Stand Ende 2025“ (S. 280) ersetzt ihn für dieses Produkt. Allgemeine Fußnoten wie „Das Schuljahr 2022/2023 wurde in Spalte 2022 eingetragen usw.“ stehen an allen Jahren des Produkts. Die App kann Teiljahreswerte so direkt kennzeichnen (z. B. Kfz-Abmeldungen 2025 = 172 bis 30.06.).
- **D-13:** Ein **„–“-Wert** erzeugt keine Zeile, analog zu Phase 2 D-11. Eine gedruckte 0 bleibt 0. **Gruppenüberschriften ohne Werte** (z. B. S. 265 „Nutzung Friedhofshalle“) kommen in eine Spalte **`gruppe`** der folgenden Zeilen und bilden keine eigene Zeile. Mehrzeilige Bezeichnungen werden zusammengeführt (S. 77, 85). Die Einheit „C“ wird zu `EUR`, andere Einheiten wie `Anz.` bleiben wie gedruckt. Die Steuer-Istwerte stehen mit Bezeichnung und Zeilenhinweis wie gedruckt, z. B. „Gewerbesteuer (Im Teilplan Zeile 01)“.

### Querschnitte und Regel 7
- **D-14:** Die Querschnitte S. 291–300 werden per Koordinaten nach `daten/zwischen/querschnitte.csv` extrahiert und **eingecheckt**, im Langformat, sinngemäß mit den Spalten `pb, pg, plan, kennzahl, betrag, pdf_seite`. Die Werte sind Ansatz 2026, die Zeile GESAMTSUMME bekommt einen eigenen Marker. Regel 7 liest die CSV wie die anderen Prüfregeln (Phase 2 D-06). Die Datei ist **reine Kontrollquelle** und nie Datenquelle für die App (Spez. 2).
- **D-15:** **Regel 7 prüft alle Spalten**. Das sind alle 7 Ergebnisplan-Kennzahlen (ordentliche Erträge, ordentliche Aufwendungen, ordentliches Ergebnis, Finanzergebnis, Ergebnis der lfd. Verwaltungstätigkeit, außerordentliches Ergebnis, Ergebnis des Teilhaushalts) und alle 11 Finanzplan-Kennzahlen inklusive VE. Je PG, gedruckt und synthetisch, werden sie gegen die eigenen PG-Teilpläne geprüft. Die Zeile GESAMTSUMME wird gegen den PB-Teilplan geprüft. Bekannte Abweichungen kommen nach dem Mechanismus aus Phase 2 D-02/D-05 in `befunde.md`.

### Claude's Discretion
- Genaue Spaltenlisten und Sortierung von `erlaeuterungen.csv`, `grundzahlen.csv`, `investitionen.csv`, `ve_faelligkeiten.csv` und `querschnitte.csv`. Sie stehen im zentralen Schema-Modul (Phase 2 D-22) und folgen den CSV-Konventionen (Phase 2 D-21).
- Kodierung von Listen in CSV-Zellen, z. B. für `zu_zeilen`
- Typ von `grundzahlen.wert`, falls Dezimalwerte vorkommen (die int-Konvention gilt für Euro-Beträge)
- Struktur von `ve_faelligkeiten.csv` (Zuordnung der Klammerwerte zu Jahren über x-Koordinaten) und ob deren Summe gegen die VE 2026 der Maßnahme geprüft wird
- Konkretes Vokabular von `art` und die Kontengruppen-Zuordnung (D-07)
- Mapping der Querschnitt-Kennzahlen auf Planzeilen (z. B. ob „ordentliche Erträge“ Z. 10 entspricht) und der Name der Spalte `kennzahl`
- Normalisierung des Bindungsgrads (`pflichtig | freiwillig | teils`); ein unbekannter Wert bricht ab
- Umgang mit Produktinformationen über zwei Seiten (64 Seiten `produktinformationen` bei 63 Produkten) und mit Investitionsmaßnahmen, die schon auf der Teilfinanzplan-Seite beginnen (S. 153)
- Modulaufteilung in `ostbevern/` (z. B. `produkte.py`, `investitionen.py`, `querschnitte.py`, `freitext.py`) und die Erweiterung von `alle.py` auf 01 → 02 → 03 → 04 → 06
- Ausgestaltung von Regel 8 (Vollständigkeit) auf Basis von `produkte.json`, `ergebnisplan.csv` und `finanzplan.csv`

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Fachliche Spezifikation
- `discussion/SPEZIFIKATION.md` §2, §2.1, §2.2 — PDF-Aufbau, Seitenfolge je Produkt (Produktinformationen, Grundzahlen, Erläuterungen, Investitionen), Spalten der Investitionstabellen (7 Werte inkl. VE)
- `discussion/SPEZIFIKATION.md` §3.8 — Datenauffälligkeiten: Investitionen dreifach im PDF, angeklebte Kontobezeichnungen, „(Kassenwirksamkeit)“, Querschnitte über Koordinaten, Stichtag der Grundzahlen
- `discussion/SPEZIFIKATION.md` §4.1, §4.2 — Schemas von `produkte.json`, `grundzahlen.csv`, `investitionen.csv` und `ve_faelligkeiten.csv` (D-09 verschärft den Datenschutz-Hinweis)
- `discussion/SPEZIFIKATION.md` §5.2–5.5 — Skripte 03/04/06, Parsen über x-Koordinaten, Prüfregeln 6–8
- `discussion/SPEZIFIKATION.md` §6.10, §6.11 — spätere Nutzung von `art` und Bindungsgrad (Kontext, nicht Scope)
- `discussion/SPEZIFIKATION.md` Anhang A — Produktverzeichnis (63 Produkte, Basis für Regel 8)

### Projektplanung
- `.planning/REQUIREMENTS.md` — EXTR-06 bis EXTR-09, PRUEF-06 bis PRUEF-08
- `.planning/ROADMAP.md` — Phase 3, Erfolgskriterien 1–4
- `.planning/phases/02-kernzahlen/02-CONTEXT.md` — D-02/D-04/D-05 (befunde.md), D-06/D-07 (Teststrategie), D-08 (Abbruch), D-11 (Fehlendes nicht schreiben), D-17 (Seitentypen), D-21/D-22 (CSV-Konventionen, Schema-Modul)
- `.planning/phases/01-setup/01-CONTEXT.md` — Jahrgangskonfiguration, `--jahr`, Skriptaufbau, fachliche Regeln im Code
- `.claude/CLAUDE.md` — Befehle und Konventionen

### Quelle und Daten
- `raw_data/haushalt-2026.pdf` — Quell-PDF. Beispielseiten: 151 (Produktinfo + Grundzahlen), 152 (Erläuterungen), 153/154 (Investitionen mit Kassenwirksamkeit), 184 (Erläuterung ohne „zu Nr.“), 265 (Gruppenüberschrift Grundzahlen), 280 (160101 Steuer-Istwerte), 291 (Querschnitt)
- `daten/zwischen/seiten.csv` — Seitentypen `produktinformationen`, `grundzahlen`, `teilergebnisplan`, `teilfinanzplan`, `investitionen_pb`, `investitionen_produkt`, `querschnitte`
- `daten/aufbereitet/{hierarchie,ergebnisplan,finanzplan}.csv` — Vergleichsbasis für Regeln 6–8
- `daten/pruefberichte/befunde.md` — Schlüsseltabelle für bekannte Abweichungen
- `pipeline/jahrgaenge/2026.toml`, `pipeline/jahrgaenge/2026_sollwerte.toml` — Seitenbereiche, Kopfzeilen, Anhang A/B

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `pipeline/ostbevern/zahlen.py`: deutscher Zahlenparser (Minus, „–“, `C`, angeklebte Beträge). Er gilt auch für Grundzahlen, Erläuterungsbeträge, Investitionen und Querschnitte.
- `pipeline/ostbevern/pdf.py`: PDF-Zugriff und Wortextraktion mit Koordinaten
- `pipeline/ostbevern/plaene.py`: Zuordnung der Spalten über x-Koordinaten und Fortsetzung über Seiten. Muster für den Investitions- und den Querschnitt-Parser.
- `pipeline/ostbevern/seiten.py`: Seitenklassifikation. `seiten.csv` liefert die Seitenmengen je Produkt.
- `pipeline/ostbevern/schema.py`: zentrale CSV-Schemas (Phase 2 D-22). Hier kommen die neuen Dateien hinzu.
- `pipeline/ostbevern/pruefung.py`: Regeln 1–4, Abgleich mit `befunde.md`, Bericht `konsistenz.md`. Hier kommen die Regeln 6–8 hinzu.
- `pipeline/ostbevern/konfiguration.py`: `lade_jahrgang`, `lade_sollwerte`

### Established Patterns
- Dünne typer-Skripte mit `--jahr`, die Logik liegt in `ostbevern/`
- Bei unlesbaren Daten wird sofort mit PDF-Seite abgebrochen (D-08). Seitenklassifikation und Plausibilitätsbefunde laufen über `konsistenz.md`.
- Prüftests lesen eingecheckte CSVs. Parser-Tests lesen ausgewählte echte PDF-Seiten.
- Deutsche Bezeichner ohne Umlaute, ruff mit Zeilenlänge 100

### PDF-Beobachtungen (Stichprobe)
- `extract_text()` liefert Freitext ohne Leerzeichen. `extract_words(x_tolerance=1)` stellt sie wieder her.
- Aufzählungspunkte der Leistungen erscheinen als `(cid:15)`.
- Der Erläuterungsblock folgt direkt auf den Teilergebnisplan, auf derselben Seite wie die Plantabelle (S. 152). Es gibt 51 Blöcke. Die Kopfzeile variiert („zu Nr.“, „Zu Nr.“, „Nr. 02 und 13“).
- Investitionsmaßnahmen beginnen teils auf der Teilfinanzplan-Seite (S. 153). Die Kontobezeichnung bricht um („Hochbaumaßnah-/men“, „über 800/EUR“). Es gibt 12 Zeilen „(Kassenwirksamkeit)“.
- Querschnitte: Ergebnisplan-Block und Finanzplan-Block je PB. Der Finanzplan-Kopf läuft über mehrere Zeilen, PG-Namen brechen um, und der Block läuft mit „Fortsetzung folgt“ auf die nächste Seite weiter.

### Integration Points
- Ausgaben: `daten/aufbereitet/{produkte.json, grundzahlen.csv, erlaeuterungen.csv, investitionen.csv, ve_faelligkeiten.csv}`, `daten/zwischen/querschnitte.csv`, `daten/pruefberichte/{konsistenz,befunde}.md`
- `pipeline/alle.py`: Schritte 03 und 04 werden vor 06 eingehängt.
- Phase 4 (`07_app_daten.py`) liest `produkte.json` ohne Namensfilter (D-09), dazu `investitionen.csv` mit `art` und die Grundzahlen mit Hinweisen.

</code_context>

<specifics>
## Specific Ideas

- Sollwerte: Gewerbesteuer 2023 = 4.771.497 € (160101, S. 280). Summe der Maßnahmen 2026 = 7.224.830 € (Einzahlungen) / 12.280.484 € (Auszahlungen).
- Kfz-Abmeldungen 2025 = 172 (Stand 30.06.) ist das Paradebeispiel dafür, warum der Stichtagshinweis am Jahreswert hängen muss (D-12).
- `BGA0301014` gegenüber `BGA030101` zeigt, warum die Saldozeile zur Trennung von ID und Name gebraucht wird (D-08).

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 03-details*
*Context gathered: 2026-10-01*
