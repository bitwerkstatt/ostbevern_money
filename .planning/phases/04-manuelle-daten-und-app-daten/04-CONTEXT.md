# Phase 4: Manuelle Daten und App-Daten - Context

**Gathered:** 2026-10-02
**Status:** Ready for planning

<domain>
## Phase Boundary

Phase 4 schließt die Pipeline ab. Sie liefert:

- die manuell gepflegten Vorberichtstabellen und `meta.json` unter `daten/manuell/`, mit README und Spalte `quelle`
- die Daten für Schuldenstand, Rücklagen und VE-Übersicht (S. 24/25, 309–311)
- geprüfte Erklärtexte (`texte/erklaerungen.md`)
- die Stellenplan-Extraktion (Schritt 05, `stellenplan.csv`)
- Prüfregel 5 (manuelle Tabellen gegen Planzeilen)
- die App-JSON-Erzeugung (Schritt 07) nach `app/src/data/` mit der Herauslösung „Weitergabe an Kreis und Land“ und dem Zuschussbedarf je Knoten
- ein reproduzierbares `alle.py` (01 → 07) mit CI-Diff-Prüfung

Nicht in dieser Phase: App-Seiten (Phase 5/6), Quellenbelege mit WebP und `quellen.json` (DATA-04, Phase 7) und `planspiel.json` (v2).

</domain>

<decisions>
## Implementation Decisions

### Weitergabe an Kreis und Land (DATA-02)
- **D-01:** Der Block „Weitergabe an Kreis und Land“ ist **eurogenau gleich TP 160101 Z. 15**, für alle Jahre 2024–2029. Geprüft ist: In 160101 steht in Z. 15 ausschließlich Kreisumlage, Gewerbesteuerumlage und Krankenhausinvestitionsumlage, z. B. 2026: 11.001.181 € = 10.147 + 654 + 200 T€, 2024: 12.114.264 € = 11.212 + 706 + 196 T€. Eine Prüfung (Teil von Regel 5) stellt sicher, dass TP 160101 Z. 15 je Jahr der Summe der drei Vorberichtsposten aus `transferaufwendungen.csv` entspricht (×1000, Toleranz ±1.000 € je Posten, also ±3.000 € für die Summe).
- **D-02:** Die **drei Unterposten** im Block sind die Vorberichtswerte × 1000. Sie sind **als gerundet gekennzeichnet**, z. B. mit `gerundet: true` bzw. Quelleinheit T€, und haben die PDF-Seite 46. Die App zeigt sie als „rd.“. Die Blocksumme bleibt der eurogenaue Planwert aus D-01.
- **D-03:** Der Block ist ein **eigener synthetischer Top-Knoten** auf PB-Ebene neben den 15 PB, z. B. `code: "KL"`, `synthetisch: true`. Seine Kinder sind die drei Umlagen. PB 16, PG 1601 und Produkt 160101 werden **um TP Z. 15 reduziert**, und PB 16 heißt in den App-Daten „Allgemeine Finanzwirtschaft“. Treemap-Drilldown (AUSG-01/02) und Sankey (FLUSS-01) funktionieren dann ohne Sonderlogik. — **Reversibility:** costly — Phase 5 (Treemap, Sankey, Ausgabenseite) und Phase 6 (Rat entscheidet) bauen auf dieser Knotenstruktur auf.
- **D-04:** Der **Zuschussbedarf** wird für jeden Knoten ohne Ausnahme rein nach Formel berechnet (D-23). „Allgemeine Finanzwirtschaft“ bekommt dadurch einen großen negativen Wert, weil hier die Steuern und die Schlüsselzuweisung liegen. Solche Werte werden mit `ueberschuss: true` gekennzeichnet. Es gibt keine Sonderregel für allgemeine Deckungsmittel. Die Erklärung folgt in Phase 5 (AUSG-03).

### Manuelle Tabellen (MANU-01 bis MANU-07, PRUEF-05)
- **D-05:** Die Vorberichtstabellen werden **in T€ wie gedruckt** gespeichert, in einer Spalte mit eindeutigem Namen `betrag_teur` (int). Erst Schritt 07 rechnet × 1000 und setzt das Kennzeichen `gerundet`. So kann eine T€-Zahl nie mit einem Euro-Betrag verwechselt werden.
- **D-06:** Die manuellen CSVs stehen im **Langformat**: eine Zeile je Posten, Jahr und Wertart, sinngemäß `tabelle/posten, jahr, wertart, betrag_teur, anmerkung, quelle`. Sie folgen den CSV-Konventionen aus Phase 2 (D-21) und laufen über das zentrale Schema-Modul (D-22). Die Spalte „2024 vorl. RE“ des Vorberichts wird auf `wertart=ergebnis` abgebildet.
- **D-07:** **Regel 5 prüft zweistufig:**
  (a) Die Summe der Posten muss die **gedruckte Gesamtzeile** exakt in T€ treffen. Die Gesamtzeile wird deshalb mit abgeschrieben, als eigener Posten oder als Kennzeichen.
  (b) Gesamtzeile × 1000 wird gegen die **Planzeile des GEP** geprüft, mit einer Toleranz von ±1.000 €.
  Abweichungen jenseits davon sind Befunde in `befunde.md`, mit PDF-Seite und mit dem Betragsabgleich aus Phase 2 D-05. Bekannt sind:
  - Zuwendungen 2026, Stufe (a): Σ 3.108 gegenüber gedrucktem „Gesamt“ 3.109.
  - Zuwendungen 2026, Stufe (b): 3.109 T€ gegenüber 3.113.200 €, eine Differenz von 4.200 €. Die App weist sie als „Sonstige“ aus (Spez. 3.8).
  Die Kita-Tabelle wird gegen den Posten „Zuschüsse an Kindertageseinr.“ (559) in `transferaufwendungen.csv` geprüft. Die Fußnote an 10.147 wird korrigiert und steht als Anmerkung in der Datei.
- **D-08:** `weitere_vorberichtstabellen.csv` enthält **genau die fünf Tabellen aus Spez. 4.3**, jeweils mit Aufschlüsselung und Gesamtzeile, geprüft gegen die jeweilige GEP-Zeile:
  - Leistungsentgelte (2.1.4)
  - Kostenerstattungen (2.1.6)
  - Personal (2.2.1)
  - Sachaufwand (2.2.3)
  - Sonstige Aufwendungen (2.2.6)

  2.1.7 (Sonstige Erträge und Konzessionsabgaben) gehört nicht zu Phase 4. EINN-04 klärt das in Phase 5 „soweit belegbar“.
- **D-09:** Die manuellen Dateien werden **einmal abgeschrieben**. Der Executor darf dabei pdfplumber zum Ablesen nutzen. Danach sind die Dateien eingecheckte Handdaten, die **kein Pipeline-Schritt überschreibt**. Regel 5 und die Gesamtzeilen fangen Tippfehler ab. Ein README unter `daten/manuell/` begründet die Werte je Datei (MANU-07).
- **D-10:** In `meta.json` gilt als **Kreisumlage brutto** der errechnete Wert aus netto plus Rückstellungsauflösung: 10.147.000 + 1.325.478 = **11.472.478 €**. Er ist als berechnet und gerundet gekennzeichnet, mit Quelle S. 46. Eine Gegenprüfung vergleicht ihn mit dem Fußnotentext „11,5 Mio. €“ (±50 T€). Jeder Wert in `meta.json` trägt seine Quelle, also PDF-Seite und bei der Einwohnerzahl auch Stichtag und Herkunft (IT.NRW, 30.06.2024).

### Schulden, Rücklagen, VE (S. 24/25, 309–311)
- **D-11:** Verbindlichkeiten (S. 310), Eigenkapital (S. 311) und VE-Übersicht (S. 309, S. 25) werden wie die Vorberichtstabellen **manuell** nach `daten/manuell/` abgeschrieben (D-09). Regel 5 prüft sie **quer gegen Extrahiertes**:
  - Investitionskredite Ende 2026 = Ende 2025 + GFP Z. 33 − GFP Z. 35, also 6.879 + 5.200 − 450 = 11.629 T€.
  - Das Jahresergebnis auf S. 311 entspricht GEP Z. 28 je Jahr.
  - Die Verringerung der Ausgleichs- und der allgemeinen Rücklage entspricht Satzung § 4 (2.132.213 € / 221.293 €).
  - Die VE-Fälligkeiten von S. 309 entsprechen `ve_faelligkeiten.csv`, und die VE-Summe beträgt 11.600 T€ = GFP-VE 2026.
- **D-12:** Die Cent-Beträge von S. 311 werden **kaufmännisch auf int-Euro gerundet**. −2.353.505,75 wird so zu −2.353.506 und trifft genau Satzung und GEP Z. 28. Das README begründet die Rundung. Die TEUR-Werte von S. 310 bleiben `betrag_teur` (D-05).
- **D-13:** Der **Schuldenstand 2027–2029** wird fortgeschrieben: Investitionskredite Ende Jahr = Vorjahr + GFP Z. 33 − Z. 35. Die Werte sind als `berechnet: true` mit Formelhinweis gekennzeichnet. 2024–2026 kommen gedruckt von S. 310, und für 2026 wird die Formel dagegen geprüft (D-11).
- **D-14:** Für Schuldenstand und Pro-Kopf-Wert gilt die **Definition des Vorberichts**: Investitionskredite plus abgerufene NRW.Bank-Mittel für Flüchtlingsunterkünfte, die haushaltsrechtlich als Transferverbindlichkeit gebucht sind. Ende 2025 sind das 6.879 + 831 = 7.710 T€, bei 11.741 Einwohnern ≈ 656 € (S. 24/25, Anhang B.6). Der Pro-Kopf-Wert ist ein Sollwert-Test. Für die Fortschreibung bleibt der NRW.Bank-Anteil konstant (berechnet). Liquiditätskredite (S. 310 Z. 3) stehen getrennt.

### Erklärtexte (MANU-08, Vorbereitung UI-05)
- **D-15:** Zahlen in `texte/erklaerungen.md` sind **ausschließlich Platzhalter mit Datenschlüssel und Formathinweis**, sinngemäß `{{zuwendungen.schluesselzuweisung.2026|mio}}`. Schritt 07 parst die Texte und prüft, dass jeder Schlüssel existiert, sonst bricht er ab. Er schreibt Text und Werte als JSON. **Die App setzt die Werte ein und formatiert sie mit `format.ts`.** Die Pipeline formatiert nie. Abgeleitete Zahlen aus dem Vorbericht, z. B. „bricht um 1,9 Mio. € ein“ oder „2023: 4,8 Mio. €“, werden in Schritt 07 als **benannte, berechnete Werte** erzeugt, z. B. `abgeleitet.schluesselzuweisung_rueckgang_2026`. Ein Test findet nackte Ziffern in den Texten und schlägt dann fehl. Ausnahmen sind Jahreszahlen, Paragraphen und Seitenverweise. Jeder Text verweist auf eine PDF-Seite. — **Reversibility:** costly — Die Platzhalter-Syntax ist ein Vertrag zwischen Pipeline, Textdatei und App-Komponente (Phase 5/6).
- **D-16 (Umfang):** Phase 4 schreibt **alle Vorbericht-Erklärtexte für Phase 5 und 6**, etwa 8–10 Texte: Schlüsselzuweisung, Gewerbesteuer, Kreisumlage (netto/brutto, Hebesätze), Grundsteuer/Hebesätze, Sonderposten (kein Geldfluss), globaler Minderaufwand, Defizit/Rücklagen, Schulden, VE, BBO/TEO („Was nicht im Haushalt steht“). Glossarbegriffe bleiben in Phase 5. Alle Texte sind in Du-Anrede.
- **D-17:** „Geprüft“ heißt: Der Executor **entwirft** die Texte auf Basis der Vorberichtsstellen. Ein **Checkpoint im Plan** legt sie dem Nutzer zur fachlichen Abnahme vor, bevor sie committet werden. Die Zahlen sichern der Platzhalter-Test und der Ziffern-Test.

### Stellenplan (EXTR-10)
- **D-18:** Stellenwerte werden als **int in Hundertstel** gespeichert, Spalte `stellen_hundertstel`, z. B. 52,26 → 5226. Damit sind Summen exakt und es gibt keine Float-Rundungsfehler. In der JSON-Datei und in der App wird durch 100 geteilt. — **Reversibility:** costly — Schritt 07, `stellenplan.json` und die Stellenplanseite in Phase 6 hängen an der Einheit.
- **D-19:** **Umfang S. 284–290:**
  - Teil A Beamte (S. 284)
  - Teil B Tarif (S. 285)
  - Teil B Sozial- und Erziehungsdienst (S. 286)
  - die drei PB-Übersichten (S. 287–289)

  Für Teil A/B gibt es je Gruppe Stellen 2026, Stellen 2025, besetzt am 30.06.2025, „davon ausgesondert“ (Beamte) und Vermerke wie „künftig wegfallend (05.2029)“ oder „0,46 VZÄ mit Sperrvermerk“ in einer eigenen Spalte. **S. 290 (Nachwuchskräfte)** kommt als eigener `teil` dazu: Personen „vorgesehen 2026“ und „beschäftigt am 01.10.2025“, mit eigenem Stichtag. Diese Werte zählen **nicht** zur Stellensumme.
- **D-20:** **Prüfung wie Phase 3 D-08:** Gedruckte „insgesamt“- und „Summe“-Zeilen werden beim Parsen gegengeprüft und nicht gespeichert, ein Verstoß bricht mit PDF-Seite ab. Dazu kommt eine **Kreuzprüfung**: Die Summe der PB-Übersicht je Gruppe muss den Stellen 2026 aus Teil A/B entsprechen. Gedruckte Rundungsdifferenzen der VZÄ-Anteile gehen nach dem befunde-Mechanismus mit Seitenbeleg in `befunde.md`. Hinzu kommt der Sollwert **Beamte 2026 = 8** in `2026_sollwerte.toml` (B.6). Außerdem kommen die weiteren B.6-Eckwerte dazu, die von `meta.json` abhängen (Hebesätze, Schlüsselzuweisung, Pro-Kopf-Verschuldung).

### App-Daten (DATA-01, DATA-03)
- **D-21:** **Dateischnitt** in `app/src/data/`:
  - `haushalt.json`: Hierarchie inkl. KL-Knoten, Planwerte je Knoten, Steuerarten, Zuwendungen inkl. „Sonstige“, Transferaufschlüsselung, Kita-Zuschüsse, weitere Vorberichtstabellen, meta, Rücklagen/Eigenkapital
  - `produkte.json`: aus `daten/aufbereitet/`, schon ohne Namen (Phase 3 D-09)
  - `investitionen.json`: Maßnahmen mit `art`, VE und Fälligkeiten, Finanzierung, Schuldenstand
  - `stellenplan.json`
  - eine kleine Zusatzdatei für die Erklärtexte, z. B. `texte.json`

  Die TypeScript-Typen stehen zentral, z. B. in `app/src/data/typen.ts`. Ein Test bestätigt, dass in keiner App-Datei Personennamen stehen (Erfolgskriterium 4). — **Reversibility:** costly — Phase 5–7 importieren diese Dateien und Typen.
- **D-22:** `haushalt.json` trennt Ergebnis- und Finanzplan in **getrennten Schlüsseln**:
  - `ergebnisplan`: je Knoten (PB, PG, P, KL, GESAMT) die Zeilen 01–17, 19, 20, Minderaufwand (TP 30 / GEP 27) und die nötigen Summen, für alle Jahre und Wertarten (Spez. 4.4)
  - `finanzplan`: nur auf GESAMT-Ebene die Investitions- und Finanzierungszeilen (u. a. Z. 23, 25, 30, 33, 35, VE, Liquide Mittel) für Phase 6

  Interne Leistungsbeziehungen (TP 27/28) gehen nicht in die App. So kann kein Diagramm die beiden Pläne versehentlich mischen (Spez. 3.1).
- **D-23:** **Aufwand, Erträge und Zuschussbedarf je Knoten:**
  - Aufwand = Z. 17 + Z. 20
  - Erträge = Z. 10 + Z. 19
  - Zuschussbedarf = Aufwand − Erträge (= −Z. 26), **vor Minderaufwand** und ohne TP 27/28

  Für 2026 ergibt das in Summe 30.455.569 € Aufwand wie in der Satzung. Die Zinsen bleiben als Posten sichtbar. Der Minderaufwand ist ein eigener, erklärter Posten (Spez. 3.3). Zuschussbedarf und alle anderen berechneten Werte sind als berechnet gekennzeichnet (DATA-03), z. B. mit `berechnet: true` oder durch einen eigenen Schlüssel. Ein Test prüft, dass die Summe der Top-Knoten (15 PB, wobei PB 16 reduziert ist, plus KL) dem GESAMT entspricht.

### CI-Diff (PRUEF-10)
- **D-24:** `alle.py` führt alle Schritte in Reihenfolge aus: 01 → 02 → 03 → 04 → Querschnitte → 05 → 06 → 07. Die CI prüft das in einem **eigenen Schritt im bestehenden `pipeline`-Job** nach pytest:
  1. `uv run python alle.py`
  2. `git diff --exit-code -- daten app/src/data` plus eine Prüfung auf ungetrackte Dateien in diesen Pfaden

  `daten/manuell/` ist eingeschlossen, denn es darf sich nie verändern. Bei einem Diff schlägt der Schritt fehl und zeigt `git diff --stat`. Die JSON-Ausgabe muss deterministisch sein (feste Schlüsselreihenfolge, UTF-8, LF, abschließender Zeilenumbruch).

### Claude's Discretion
- Genaue Spaltenlisten und Sortierung aller neuen CSVs (`steuerarten.csv`, `zuwendungen.csv`, `transferaufwendungen.csv`, `kita_zuschuesse.csv`, `weitere_vorberichtstabellen.csv`, Dateien für Verbindlichkeiten, Eigenkapital und VE-Übersicht, `stellenplan.csv`) im Rahmen von D-05/D-06/D-18 und Phase 2 D-21/D-22
- Ob Schulden, Eigenkapital und VE-Übersicht eigene Dateien oder Tabellen in `weitere_vorberichtstabellen.csv` sind
- Feldstruktur von `meta.json` (Wert + Quelle je Feld)
- Konkrete JSON-Struktur von `haushalt.json` usw. Werte z. B. je Jahr als Objekt oder als Arrays entlang einer `jahre`-Liste. Münster dient nur als Vorlage (Phase 1 D-01).
- Konkrete Platzhalter-Syntax und Formatkürzel (D-15), Name und Struktur der Text-JSON
- Aufbau des README unter `daten/manuell/`
- Modulaufteilung in `ostbevern/` (z. B. `manuell.py`, `stellenplan.py`, `app_daten.py`, `texte.py`) und neue Skripte `05_stellenplan.py` und `07_app_daten.py` als dünne typer-Einstiege mit `--jahr`
- Ob Regel 5 eine Regel mit Unterprüfungen ist oder in 5a/5b/… aufgeteilt wird, im Rahmen von `konsistenz.md` (Phase 2 D-03)
- Codevergabe für den KL-Knoten und die drei Unterposten

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Fachliche Spezifikation
- `discussion/SPEZIFIKATION.md` §3.1 — Ergebnis- und Finanzplan nie mischen (D-22)
- `discussion/SPEZIFIKATION.md` §3.2, §3.3 — Zeilennummern GEP/TP, Minderaufwand GEP 27 / TP 30, TP 27/28 nie in Summen
- `discussion/SPEZIFIKATION.md` §3.4 — Kreisumlage, „Weitergabe an Kreis und Land“ (D-01 bis D-03)
- `discussion/SPEZIFIKATION.md` §3.6, §3.7 — Sonderposten, BBO/TEO (Erklärtexte D-16)
- `discussion/SPEZIFIKATION.md` §3.8 — Fußnote 10.1473, Zuwendungsdifferenz, Einwohnerzahl
- `discussion/SPEZIFIKATION.md` §4.2 (`stellenplan.csv`), §4.3 (manuelle Tabellen), §4.4 (App-Daten)
- `discussion/SPEZIFIKATION.md` §5.2, §5.5 Regel 5 — Skripte 05/07, Prüfregel 5
- `discussion/SPEZIFIKATION.md` §6.10–6.13 — spätere Nutzung von Schulden, VE, Rücklagen und Stellenplan (Kontext, nicht Scope)
- `discussion/SPEZIFIKATION.md` §7, §8 — CI-Diff-Konvention, Zahlen in Texten aus Daten
- `discussion/SPEZIFIKATION.md` Anhang B.4, B.5, B.6 — Sollwerte Steuerarten, Transferaufwendungen, Eckwerte

### Projektplanung
- `.planning/REQUIREMENTS.md` — MANU-01 bis MANU-08, PRUEF-05, PRUEF-10, EXTR-10, DATA-01 bis DATA-03
- `.planning/ROADMAP.md` — Phase 4, Erfolgskriterien 1–5
- `.planning/STATE.md` — Blocker zu Schulden, Rücklagen und VE sowie zu B.6-Eckwerten (durch D-11 bis D-14 und D-20 aufgefangen)
- `.planning/phases/03-details/03-CONTEXT.md` — D-07 (`art`-Vokabular), D-08 (Gegenprobe beim Parsen), D-09 (keine Namen in `daten/`)
- `.planning/phases/02-kernzahlen/02-CONTEXT.md` — D-01 bis D-05 (befunde.md, Bericht), D-06 (Tests lesen CSVs), D-08 (Abbruch), D-10 (Vorzeichen), D-21/D-22 (CSV-Konventionen, Schema-Modul)
- `.planning/phases/01-setup/01-CONTEXT.md` — D-01 (Münster nur als Vorlage), Jahrgangskonfiguration, dünne Skripte
- `.claude/CLAUDE.md` — Befehle und Konventionen

### Quelle und Daten
- `raw_data/haushalt-2026.pdf` — Vorbericht S. 24/25 (Rücklagen, Kredite, VE), S. 27 (Steuerarten), S. 28 (Zuwendungen), S. 29–50 (weitere Tabellen), S. 45/46 (Transfers, Kita, Fußnote 3), S. 8–10 (Hebesätze, Fläche, Satzung), S. 284–290 (Stellenplan), S. 309 (VE), S. 310 (Verbindlichkeiten), S. 311 (Eigenkapital)
- `daten/aufbereitet/{hierarchie,ergebnisplan,finanzplan}.csv`, `produkte.json`, `investitionen.csv`, `ve_faelligkeiten.csv`, `grundzahlen.csv`, `erlaeuterungen.csv` — Eingaben für Schritt 07 und die Querprüfungen
- `daten/pruefberichte/befunde.md` — Schlüsseltabelle für neue Befunde aus Regel 5 und dem Stellenplan
- `pipeline/jahrgaenge/2026.toml` (`stellenplan = 284–290`, `verpflichtungen_schulden = 309–311`), `pipeline/jahrgaenge/2026_sollwerte.toml` — hier kommen B.4–B.6 dazu
- `.github/workflows/ci.yml` — Job `pipeline` bekommt den Diff-Schritt (D-24)

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `pipeline/ostbevern/schema.py`: zentrale CSV-Schemas. Hier kommen die neuen manuellen Dateien und `stellenplan.csv` hinzu.
- `pipeline/ostbevern/pruefung.py`: Regeln 1–4 und 6–8, befunde-Abgleich, `konsistenz.md`. Hier kommt Regel 5 dazu.
- `pipeline/ostbevern/plaene.py`, `spalten.py`, `pdf.py`, `zahlen.py`: Spaltenzuordnung über x-Koordinaten und deutscher Zahlenparser (Dezimalkomma). Das ist das Muster für den Stellenplan-Parser.
- `pipeline/ostbevern/investitionen.py`: Gegenprobe von Zwischensummen beim Parsen (Phase 3 D-08). Das ist das Muster für D-20.
- `pipeline/ostbevern/konfiguration.py`: `lade_jahrgang`, `lade_sollwerte`, `STANDARD_JAHR`, `PROJEKT_WURZEL`
- `pipeline/alle.py`: Schrittkette mit typer und einheitlicher Fehlerbehandlung je Schritt. 05 und 07 werden eingehängt.
- `app/src/data/jahrgang.json`, `beispieldaten.json`: bestehende Datenimporte der App (StartPage). Die neuen JSON-Dateien kommen daneben.
- `app/src/charts/format.ts`: einzige Formatierungsstelle. Hier kommen die Formatkürzel der Platzhalter an (D-15).

### Established Patterns
- Dünne typer-Skripte mit `--jahr`, Logik in `ostbevern/`, keine Jahrgangswerte im Code
- Abbruch mit PDF-Seite bei unlesbaren Daten. Bekannte Abweichungen nur über `befunde.md` mit passendem Betrag. Veraltete Befunde gelten als Fehler.
- Prüftests lesen eingecheckte CSVs, Parser-Tests lesen ausgewählte echte PDF-Seiten.
- Personennamen gelangen nie nach `daten/`, dreifach abgesichert (Phase 3).

### PDF-Beobachtungen (aus der Diskussion)
- Die TP 160101 Z. 15 entspricht in allen Jahren Kreisumlage + GewSt-Umlage + KH-Umlage (D-01).
- S. 28: Die Zuwendungen 2026 ergeben in Einzelwerten 3.108, gedruckt sind 3.109, der GEP nennt 3.113.200 €. Die übrigen Jahre gehen auf.
- Einige Vorbericht-Gesamtzeilen weichen von der GEP-Zeile ab. 2.1.7 Sonstige ordentliche Erträge 2028 = 2.396 T€ gegenüber GEP Z. 07 2.346.161 € (Δ 50 T€, vermutlich ein Druckfehler). 2.1.7 wird in Phase 4 nicht abgeschrieben (D-08), der Wert ist nur ein Hinweis für später.
- Bei 2.2.3 Sachaufwand 2027–2029 liegen gedruckt 6.575 / 6.655 / 6.710 T€ gegenüber GEP Z. 13 6.578.021 / 6.658.705 / 6.713.846 €, also Δ 3–4 T€. Das ergibt **Befunde nach D-07** mit S. 37.
- Die Kita-Einzelwerte S. 46 ergeben 559 T€. Die Kreisumlage 2026 ist im Text als „10.1473“ gedruckt (Fußnote 3).
- S. 284: Spalten Stellen 2026 insgesamt, davon ausgesondert, Stellen 2025, besetzt 30.06.2025, Erläuterungen. Vermerke sind mehrzeilig. Die Summenzeile lautet „insgesamt 8 1 8 6,9“.
- S. 285/286: Viele Entgeltgruppen sind ohne Werte gedruckt, also leer und nicht 0. Ein Vermerk steht direkt hinter den Werten („0,46 VZÄ mit Sperrvermerk“).
- S. 287/288: Mehrzeilige PB-Namen, und Werte rutschen teils in die erste Zeile (PB 09 auf S. 288). Manche Zeilen zeigen nur einen Wert (PB 11, 16 auf S. 287). Ob das die Spalte Summe ist, ist über x-Koordinaten zu klären.
- S. 310: Werte in TEUR, Zeilentext teils doppelt gerendert („VVeerbrbininddlilcichhkkeeitietenn“). Weil manuell erfasst wird, ist das unkritisch.
- S. 311: Euro mit Cent, Jahre 2024–2029.
- S. 24/25: „ungefähr 7,7 Mio. €“ = 6.879 T€ Kredite + rd. 831 T€ NRW.Bank. Das entspricht 656 € je Einwohner. Der NRW.Bank-Anteil ist nur für Ende 2025 im Text genannt. Die Verbindlichkeiten aus Transferleistungen auf S. 310 liegen bei 1.221 / 831 / 746 T€. Ob 746 T€ Ende 2026 der NRW.Bank-Anteil ist, muss die Recherche klären, bevor D-14 „konstant“ fortschreibt.

### Integration Points
- Neu: `pipeline/05_stellenplan.py`, `pipeline/07_app_daten.py`, `daten/manuell/*`, `daten/aufbereitet/stellenplan.csv`, `app/src/data/{haushalt,produkte,investitionen,stellenplan,texte}.json`, App-Typen
- Geändert: `pipeline/alle.py` (05, 07), `pruefung.py` (Regel 5, Stellenplan-Kreuzprüfung), `2026_sollwerte.toml` (B.4–B.6), `befunde.md`, `.github/workflows/ci.yml`
- Phase 5/6 importieren die JSON-Dateien. `beispieldaten.json` bleibt für das `ChartCard`-Flag bestehen.

</code_context>

<specifics>
## Specific Ideas

- „Weitergabe an Kreis und Land“ muss eurogenau aufgehen. Die Unterposten sind ehrlich als „rd.“ markiert, statt eine Genauigkeit vorzutäuschen.
- Die Schuldenzahl soll die sein, die die Gemeinde selbst nennt (656 € je Einwohner), damit Bürger sie im Vorbericht wiederfinden.
- Der Nutzer liest die Erklärtexte vor dem Commit fachlich gegen (Checkpoint).

</specifics>

<deferred>
## Deferred Ideas

- Abschreiben von 2.1.7 (Sonstige ordentliche Erträge, Konzessionsabgaben) und weiterer Vorberichtstabellen (Privatrechtliche Entgelte, Finanzerträge, Versorgung, Abschreibungen, Zinsen, Investitionstabellen 3.2–3.4). Bei Bedarf in Phase 5 für EINN-04 bzw. EINN-06.
- Kreisumlage brutto/netto in der Anzeige: Darstellung in Phase 5 (Callout AUSG-02)

</deferred>

---

*Phase: 04-manuelle-daten-und-app-daten*
*Context gathered: 2026-10-02*
