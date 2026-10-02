# Roadmap: Ostbevern Money

## Overview

Der Weg führt in horizontalen Schichten vom PDF zur öffentlichen App, angelehnt an den Phasenplan der Spezifikation (Abschnitt 9). Zuerst entsteht das Gerüst für Pipeline, App und CI (Spez. P0). Danach liest die Pipeline die Plantabellen und trifft die Sollwerte aus Anhang B (P1). Es folgen Produktdetails und Investitionen (P2), dann die manuell gepflegten Vorberichtsdaten, der Stellenplan und die Erzeugung der App-JSON. Damit ist die Pipeline geschlossen und in der CI reproduzierbar (P3). Darauf baut die App auf: Zuerst kommen die beiden Leitfragen „Woher?“ und „Wofür?“ mit Start, Geldfluss und Glossar (P4), dann die Kontextseiten (P5). Zum Schluss folgen Quellenbelege, Barrierefreiheit, Mobilansicht, Textdurchgang und Deployment auf GitHub Pages (P7). Die Spiele (Spez. P6) sind auf v2 verschoben und gehören nicht zu dieser Roadmap.

Abweichungen vom Spez.-Phasenplan:
- Die Teilfinanzpläne kommen schon in Phase 2. Sie nutzen denselben Parser, und Prüfregel 1 gilt für alle Pläne.
- Die App-Daten (`07_app_daten.py`) und `alle.py` mit CI-Diff-Prüfung schließen Phase 4 ab.
- Die CI für Typprüfung und Lint gibt es schon ab Phase 1.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Setup** - Repo-Struktur, uv-Pipeline, Vue-Grundgerüst mit Münster-Komponenten, Jahrgangskonfiguration, CLAUDE.md und CI (Spez. P0) (completed 2026-10-01)
- [x] **Phase 2: Kernzahlen** - Seitenklassifikation, Hierarchie, alle Ergebnis- und Finanzpläne; Prüfregeln 1–4 grün, Anhang-B-Sollwerte getroffen (Spez. P1) (completed 2026-10-01)
- [ ] **Phase 3: Details** - Produktinformationen, Grundzahlen, Erläuterungen, Investitionen; Prüfregeln 6–8 grün, 63 Produkte vollständig (Spez. P2)
- [ ] **Phase 4: Manuelle Daten und App-Daten** - Vorberichtstabellen, meta.json, Erklärtexte, Stellenplan, App-JSON; Prüfregel 5 grün, `alle.py` reproduzierbar (Spez. P3)
- [ ] **Phase 5: Leitfragen-Seiten** - Start, Einnahmen, Ausgaben, Geldfluss und Glossar beantworten „Woher?“ und „Wofür?“ (Spez. P4)
- [ ] **Phase 6: Kontext-Seiten** - Entwicklung, Investitionen und Schulden, Rat entscheidet, Stellenplan, „Was nicht im Haushalt steht“ (Spez. P5)
- [ ] **Phase 7: Feinschliff und Veröffentlichung** - Quellenbelege, Barrierefreiheit, Mobilansicht, Textdurchgang, Smoke-Test, Deployment auf GitHub Pages (Spez. P7)

## Phase Details

### Phase 1: Setup

**Goal**: Pipeline und App lassen sich leer bauen und testen. Die Konventionen und die Jahrgangskonfiguration sind festgelegt, und die CI prüft jeden Push.
**Depends on**: Nothing (first phase)
**Requirements**: SETUP-01, SETUP-02, SETUP-03, SETUP-04, SETUP-05, QUAL-01
**Success Criteria** (what must be TRUE):
  1. Die Repo-Struktur nach Spez. 7 existiert (`pipeline/`, `daten/{zwischen,aufbereitet,manuell,pruefberichte}`, `app/`), und das Quell-PDF liegt unter `raw_data/`.
  2. `uv run pytest` läuft im uv-Projekt `pipeline/` (Python ≥ 3.12, pdfplumber, polars, typer, pytest) grün durch.
  3. `npm run build` baut das Vue-3-Grundgerüst (TS, Vite, Web Awesome, vue-echarts, Hash-Router) mit den übernommenen Münster-Basiskomponenten (`PageIntro`, `ChartCard`, `BaseChart`, `DatenTabelle`, `charts/format.ts`, `echartsTheme.ts` u. a.). `vue-tsc` und ESLint laufen in GitHub Actions fehlerfrei.
  4. Haushaltsjahr, Spaltenköpfe, Seitenbereiche und PDF-Pfad stehen in einer Jahrgangs-Konfigurationsdatei, und die Pipeline lädt sie von dort statt aus dem Code.
  5. Die Projekt-`CLAUDE.md` nennt die Befehle für Pipeline und App sowie die Konventionen: deutsche Bezeichner ohne Umlaute, Beträge als int-Euro, nur 1-basierte PDF-Seiten, keine Jahrgangswerte im Code, Du-Anrede, Zahlen in Texten aus Daten.

**Plans**: 5/5 plans complete

Plans:
**Wave 1**
- [x] 01-01-PLAN.md — Paketprüfung: Mensch bestätigt alle PyPI- und npm-Pakete vor jeder Installation (Wave 1, Checkpoint)

**Wave 2** *(blocked on Wave 1 completion)*
- [x] 01-02-PLAN.md — Pipeline: PDF umbenannt, uv-Projekt, Jahrgangs- und Sollwertdatei, Lader mit Prüfung, Rauchtest, alle.py --jahr, ruff, daten/ (Wave 2)
- [x] 01-03-PLAN.md — App-Gerüst: create-vue, Web Awesome, Hash-Router, PageIntro, Rahmen mit Navigation und Münster-Dank, Lint-/Format-Skripte (Wave 2)

**Wave 3** *(blocked on Wave 2 completion)*
- [x] 01-04-PLAN.md — Basiskomponenten: format.ts, echartsTheme.ts, BaseChart, ChartCard mit Beispieldaten-Hinweis, DatenTabelle, bildschirm.ts (Wave 3)

**Wave 4** *(blocked on Wave 3 completion)*
- [x] 01-05-PLAN.md — CI mit zwei Jobs (lokal nachgestellt), Befehle und Konventionen in .claude/CLAUDE.md, README, MIT-LICENSE (Wave 4)

### Phase 2: Kernzahlen

**Goal**: Alle Ergebnis- und Finanzpläne (Gesamt, PB, Produkt) liegen korrekt im Langformat vor. Die Pipeline weist das durch automatische Prüfungen und Anhang-B-Sollwerte nach.
**Depends on**: Phase 1
**Requirements**: EXTR-01, EXTR-02, EXTR-03, EXTR-04, EXTR-05, PRUEF-01, PRUEF-02, PRUEF-03, PRUEF-04, PRUEF-09
**Success Criteria** (what must be TRUE):
  1. `daten/zwischen/seiten.csv` ordnet jeder PDF-Seite Typ, PB, PG und Produkt zu, und Fortsetzungsseiten erben den Kontext. Ein Test bestätigt, dass die Startseiten aller 63 Produkte mit Anhang A übereinstimmen. `hierarchie.csv` enthält 15 PB, alle PG (synthetische mit `synthetisch=true`) und 63 Produkte mit Namen aus der Produktseite.
  2. Die Unit-Tests des Zahlenparsers sind grün. Abgedeckt sind deutsches Format, Minus, „–“ als „kein Wert“, angeklebte Beträge und `C` als Eurozeichen.
  3. `ergebnisplan.csv` und `finanzplan.csv` (inkl. VE-Spalte) enthalten Gesamt-, PB- und Produktpläne mit `zeile`, `zeile_kanonisch`, `ist_summe` und `pdf_seite`. Die Zeilenformeln sind für jeden Plan grün (Regel 1). Die Produkte summieren sich zu PG und PB (Regel 2), und die 15 PB ergeben ohne TP 27/28 den Gesamtergebnisplan (Regel 3).
  4. Die Anhang-B-Sollwerte werden auf den Euro getroffen:
     - B.1 Gesamtergebnisplan, alle Zeilen und Jahre (z. B. Z. 28 2026 = −2.353.506 €)
     - B.2 Gesamtfinanzplan (Z. 23 = 7.224.830 €, Z. 30 = 12.280.484 €, Z. 33 = 5.200.000 €, Z. 41 = 4.199.420 €)
     - B.3 PB-Summen (Σ Erträge 27.042.063 €, Σ Aufwendungen 30.255.569 €)
     - Satzung § 1 (Erträge 27.502.063 €, Aufwendungen 30.455.569 €)
  5. `uv run pytest` erzeugt `daten/pruefberichte/konsistenz.md`. Eine Abweichung über 1 €, die nicht in `befunde.md` steht, lässt den Lauf scheitern.

**Plans**: 5/5 plans complete

Plans:
**Wave 1**
- [x] 02-01-PLAN.md — Tracer Gesamtergebnisplan PDF → ergebnisplan.csv → Regel 4 (B.1) → konsistenz.md; Zahlenparser (EXTR-01); Sollwerte B.1–B.3 (Wave 1)

**Wave 2** *(blocked on Wave 1 completion)*
- [x] 02-02-PLAN.md — Seitenklassifikation seiten.csv und hierarchie.csv (synthetische PG), Anhang-A-Startseiten-Test (Wave 2)
- [x] 02-03-PLAN.md — Gesamtfinanzplan inkl. VE, Prüfregel 1 mit Formelkette, Regel 4 B.2/Satzung, befunde.md-Regeln D-02/D-04/D-05 (Wave 2)

**Wave 3** *(blocked on Wave 2 completion)*
- [x] 02-04-PLAN.md — Alle Teilergebnis- und Teilfinanzpläne (PB, PG, Produkt, synthetische PG), Fortsetzungsseiten, Regel 1 grün (Wave 3)

**Wave 4** *(blocked on Wave 3 completion)*
- [x] 02-05-PLAN.md — alle.py 01 → 02 → 06, Regel 2 (Produkte → PG → PB), Regel 3 (PB → Gesamt), Regel 4 B.3, unbekannte Seiten im Bericht (Wave 4)

### Phase 3: Details

**Goal**: Alle 63 Produkte sind inhaltlich vollständig beschrieben (Produktinformationen, Bindungsgrad, Grundzahlen, Erläuterungen), und die Investitionsmaßnahmen stimmen mit den Finanzplänen überein.
**Depends on**: Phase 2
**Requirements**: EXTR-06, EXTR-07, EXTR-08, EXTR-09, PRUEF-06, PRUEF-07, PRUEF-08
**Success Criteria** (what must be TRUE):
  1. `produkte.json` enthält alle 63 Produkte mit Fachbereich, Gremium, Beschreibung, Leistungen, Auftragsgrundlage, Klassifizierung, Zielgruppe, Zielen, PDF-Seiten und Bindungsgrad (normalisiert auf `pflichtig | freiwillig | teils` und im Original). Die Vollständigkeitsprüfung (Regel 8) ist grün.
  2. `grundzahlen.csv` führt die Kennzahlen je Produkt mit Einheit, Jahr und Stichtagshinweis, inklusive der Steuer-Istwerte 2022–2025 aus 160101 (z. B. Gewerbesteuer 2023 = 4.771.497 €). Die Erläuterungsposten stehen je Produkt mit Betrag, Text und Zeilenbezug bereit.
  3. `investitionen.csv` stammt nur aus den Produktseiten. Die Summe je Produkt entspricht Teilfinanzplan Z. 23/30, und die Summe aller Maßnahmen 2026 ergibt 7.224.830 € / 12.280.484 € (Regel 6). „(Kassenwirksamkeit)“-Zeilen stehen in `ve_faelligkeiten.csv` und nicht in den Summen.
  4. Die Querschnitte ab S. 291 stimmen mit den eigenen PG-Aggregaten überein (Regel 7). `konsistenz.md` meldet die Regeln 1–4 und 6–8 als grün.

**Plans**: 5/5 plans executed

Plans:
**Wave 1**
- [x] 03-01-PLAN.md — Tracer Querschnitte S. 291–300 → querschnitte.csv → Regel 7 → konsistenz.md; Layout-Tabellen der Jahrgangsdatei, spalten.py, Fail-fast-Prüfungen, alle.py (Wave 1)

**Wave 2** *(blocked on Wave 1 completion)*
- [x] 03-02-PLAN.md — Investitionen aus den Produktseiten → investitionen.csv (art, D-08-Saldenprüfung, Finanzierungskonten geprüft und ausgeschlossen), ve_faelligkeiten.csv, Schritt 04, Regel 6 (Wave 2)

**Wave 3** *(blocked on Wave 2 completion)*
- [x] 03-03-PLAN.md — PB-Investitionslisten → investitionen_pb.csv (Kontrollquelle), Regel 6 PB-Gegenprobe, Lücken im Prüfbericht (Wave 3)

**Wave 4** *(blocked on Wave 3 completion)*
- [x] 03-04-PLAN.md — Produktinformationen → produkte.json ohne Personennamen (D-09), Erläuterungen → erlaeuterungen.csv mit D-04-Plausibilität, Schritt 03 in alle.py (Wave 4)

**Wave 5** *(blocked on Wave 4 completion)*
- [x] 03-05-PLAN.md — Grundzahlen → grundzahlen.csv (Stichtag-Hinweise, Gruppen, Steuer-Istwerte 160101), Regel 8 Vollständigkeit, Phasen-Gate Regeln 1–4 und 6–8 grün (Wave 5)

### Phase 4: Manuelle Daten und App-Daten

**Goal**: Die Pipeline ist geschlossen. Die Vorberichtswerte sind manuell gepflegt und gegen den Plan geprüft, der Stellenplan ist extrahiert, und die App-JSON-Dateien entstehen reproduzierbar ohne Personennamen.
**Depends on**: Phase 3
**Requirements**: MANU-01, MANU-02, MANU-03, MANU-04, MANU-05, MANU-06, MANU-07, MANU-08, PRUEF-05, EXTR-10, DATA-01, DATA-02, DATA-03, PRUEF-10
**Success Criteria** (what must be TRUE):
  1. Alle Tabellen in `daten/manuell/` haben eine Spalte `quelle` mit PDF-Seite, und ein README begründet die Werte. Prüfregel 5 ist grün:
     - Die Steuerarten-Summe entspricht GEP Z. 01 je Jahr (±1 T€, B.4).
     - Die Transferaufwendungen summieren sich zu Z. 15 (13.764 T€, B.5).
     - Die Kita-Zuschüsse ergeben 559 T€.
     Die Zuwendungsdifferenz (rund 4 T€) und die Fußnote an 10.147 sind in `befunde.md` dokumentiert.
  2. `meta.json` enthält Einwohnerzahl 11.741 (mit Stichtag und Quelle), Hebesätze (242 % / 554 % / 418 %), Fläche, Satzungsdatum, Kreisumlage brutto/netto und die Kreisumlage-Hebesätze (36,3 % / 21 %). `texte/erklaerungen.md` enthält geprüfte Erklärtexte mit Seitenverweis (Schlüsselzuweisung, Gewerbesteuer, Kreisumlage). Die Daten für Schuldenstand, Rücklagen und VE-Übersicht (S. 24/25, 309–311) liegen mit Quelle vor.
  3. `stellenplan.csv` enthält Teil A (Beamte), Teil B (Tarif) und die Stellenübersicht nach PB mit Stellen 2026, 2025, besetzt 30.06.2025 und Vermerken. Beamtenstellen 2026 = 8.
  4. `app/src/data/` enthält `haushalt.json`, `produkte.json`, `investitionen.json` und `stellenplan.json`. Ein Test bestätigt, dass keine Personennamen enthalten sind. „Weitergabe an Kreis und Land“ (Kreisumlage, Gewerbesteuerumlage, Krankenhausinvestitionsumlage) ist eine eigene Kategorie, und der Rest von PB 16 heißt „Allgemeine Finanzwirtschaft“. Der Zuschussbedarf ist je Knoten und Jahr als berechneter Wert gekennzeichnet.
  5. `uv run pipeline/alle.py` führt alle Schritte in Reihenfolge aus. Die CI schlägt fehl, wenn danach eingecheckte Daten einen Diff zeigen.

**Plans**: TBD

### Phase 5: Leitfragen-Seiten

**Goal**: Bürgerinnen und Bürger finden in der App laienverständliche Antworten auf „Wo kommt das Geld her?“ und „Wofür wird es ausgegeben?“. Jede gezeigte Zahl stammt aus den generierten Daten.
**Depends on**: Phase 4
**Requirements**: START-01, START-02, EINN-01, EINN-02, EINN-03, EINN-04, EINN-05, EINN-06, AUSG-01, AUSG-02, AUSG-03, AUSG-04, AUSG-05, FLUSS-01, FLUSS-02, FLUSS-03, FLUSS-04, GLOS-01, GLOS-02, GLOS-03, UI-01, UI-03, UI-05
**Success Criteria** (what must be TRUE):
  1. Die Startseite zeigt das Kennzahlenband 2026: Erträge 27,5 Mio. €, Aufwendungen 30,5 Mio. €, Defizit 2,35 Mio. € nach Minderaufwand, Investitionen 12,3 Mio. €, neue Kredite 5,2 Mio. €, pro Kopf Aufwand ≈ 2.594 € und Steuern ≈ 1.571 €. Dazu kommen zwei Einstiege zu den Leitfragen und der Hinweis auf die Kreisumlage. Die Fußzeile nennt Datenstand, Link zum Original-PDF, „inoffizielles Projekt“ und einen Kontakt.
  2. Auf `/einnahmen` sieht man die Ertragsarten mit Betrag und Anteil. Die Ebenen lassen sich aufklappen:
     - Steuern nach Art mit Hebesätzen und dem Hinweis, welche Steuern die Gemeinde selbst festlegt
     - Zuwendungen; Sonderposten mit „kein Geldfluss“
     - sonstige Erträge mit Konzessionsabgaben
     Je Steuerart gibt es eine Zeitreihe 2022–2029, in der Ist und Plan unterscheidbar sind, mit Erklärtexten. Die investiven Einnahmen stehen klar getrennt.
  3. Auf `/ausgaben` gibt es eine Treemap mit Drilldown Aufgabenbereich → Produktgruppe → Produkt. „Weitergabe an Kreis und Land“ ist eine farblich abgesetzte Kachel mit Callout, und der Minderaufwand steht als erklärter Hinweis unter dem Diagramm. Weitere Funktionen:
     - Umschalter Aufwand/Zuschussbedarf; Überschüsse werden erklärt
     - Sicht nach Aufwandsart mit aufklappbaren Transferaufwendungen und Abschreibungen mit „kein Geldfluss“
     - Produktdetail mit Beschreibung, Bindungsgrad, Gremium, Teilergebnisplan 2024–2029, Erläuterungen, Grundzahlen (berechnete Pro-Kopf-Werte gekennzeichnet), Investitionen und Quellenlink
  4. `/geldfluss` zeigt einen Sankey 2026, der über „Defizit (Entnahme aus Rücklagen)“ und den Minderaufwand bilanziert. Hover hebt Pfade hervor, und ein Klick auf einen Aufgabenbereich öffnet die Ausgabenseite. Auf schmalen Bildschirmen erscheint stattdessen eine Tabelle oder ein gestapelter Balken. Einnahmen, Ausgaben und Geldfluss haben einen Jahr-Umschalter (2024 Ist … 2029 Planung, Standard 2026).
  5. `/glossar` erklärt mindestens die 22 Begriffe aus Spez. 6.14 und listet alle 63 Produkte als Akkordeon. `GlossarBegriff`-Links auf den Seiten führen zum jeweiligen Begriff. Zahlen in Erklärtexten werden aus den Daten erzeugt und verweisen auf eine PDF-Seite.

**Plans**: TBD
**UI hint**: yes

### Phase 6: Kontext-Seiten

**Goal**: Die App ordnet den Haushalt ein: Entwicklung bis 2029, Investitionen und Schulden, Gestaltungsspielraum des Rats, Personal und was außerhalb des Kernhaushalts liegt.
**Depends on**: Phase 5
**Requirements**: ENTW-01, ENTW-02, ENTW-03, INV-01, INV-02, INV-03, INV-04, RAT-01, RAT-02, RAT-03, RAT-04, STEL-01, STEL-02, STEL-03, UI-04
**Success Criteria** (what must be TRUE):
  1. `/entwicklung` zeigt Erträge, Aufwendungen und Jahresergebnis 2024–2029 mit unterscheidbarem Ist, Ansatz und Planung (Defizit 2029 −3,56 Mio. €). Dazu kommen Zeitreihen für Kreisumlage, Gewerbesteuer, Schlüsselzuweisung, Personal und Zinsen sowie Ausgleichsrücklage und allgemeine Rücklage mit der Angabe, wie lange das Polster reicht.
  2. `/investitionen` listet die Maßnahmen 2026–2029 als Liste und Balken, filterbar nach Aufgabenbereich und Art (Bau, Grundstücke, Fahrzeuge/Ausstattung). Die Seite zeigt außerdem:
     - die Verpflichtungsermächtigungen (11,6 Mio. €) mit Fälligkeiten
     - die Finanzierung samt Zeitreihe von Kreditaufnahme und Tilgung
     - den Schuldenstand gesamt und je Einwohner (≈ 7,7 Mio. € / ≈ 656 €)
  3. `/rat-entscheidet` zeigt den Zuschussbedarf 2026 nach Bindungsgrad als gestapelten Balken mit den Produkten je Kategorie. Es folgen der Block „Was der Rat nicht beeinflussen kann“, die Einzelzuschüsse aus dem Vorbericht und der Hinweis, dass der Bindungsgrad eine Selbstauskunft der Verwaltung ist.
  4. `/stellenplan` zeigt die Stellen 2026 im Vergleich zu 2025 und zu den besetzten Stellen am 30.06.2025, die Verteilung nach Aufgabenbereich und nach Entgelt- bzw. Besoldungsgruppe sowie daneben den Personalaufwand je Aufgabenbereich (TP Z. 11).
  5. Ein Hinweis „Was nicht im Haushalt steht“ erklärt BBO (Hallenbad) und TEO AöR (Abwasser).

**Plans**: TBD
**UI hint**: yes

### Phase 7: Feinschliff und Veröffentlichung

**Goal**: Die App ist belegbar, barrierefrei, mobil nutzbar und unter einer öffentlichen URL erreichbar.
**Depends on**: Phase 6
**Requirements**: DATA-04, UI-02, UI-06, A11Y-01, A11Y-02, A11Y-03, A11Y-04, QUAL-02, DEPL-01, DEPL-02
**Success Criteria** (what must be TRUE):
  1. „Quelle anzeigen“ an Kennzahlen und Tabellenzeilen öffnet eine Seitenleiste mit der gerenderten WebP-PDF-Seite und dem markierten Zeilenrechteck (`quellen.json`, `public/quellen/`).
  2. Zu jedem Diagramm gibt es eine Tabellenalternative. Beim Routenwechsel springt der Fokus, die Kontraste reichen aus, `prefers-reduced-motion` wird beachtet, und alle Seiten sind ab 360 px Breite nutzbar.
  3. Lighthouse-Barrierefreiheit erreicht auf allen Routen mindestens 95.
  4. Ein Playwright-Smoke-Test bestätigt, dass jede Route ohne Konsolenfehler rendert und die Diagramme Daten enthalten. Ein Textdurchgang bestätigt, dass alle Texte deutsch und durchgehend in der Du-Anrede sind.
  5. GitHub Actions baut die App und deployt sie auf GitHub Pages (eigener Account), und die App ist unter einer öffentlichen URL erreichbar.

**Plans**: TBD
**UI hint**: yes

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6 → 7

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Setup | 5/5 | Complete    | 2026-10-01 |
| 2. Kernzahlen | 5/5 | Complete    | 2026-10-01 |
| 3. Details | 5/5 | In Progress|  |
| 4. Manuelle Daten und App-Daten | 0/TBD | Not started | - |
| 5. Leitfragen-Seiten | 0/TBD | Not started | - |
| 6. Kontext-Seiten | 0/TBD | Not started | - |
| 7. Feinschliff und Veröffentlichung | 0/TBD | Not started | - |
