# Requirements: Ostbevern Money

**Defined:** 2026-10-01
**Core Value:** Jede Zahl in der App ist korrekt aus dem Haushalts-PDF abgeleitet und durch automatische Prüfungen belegt; die Leitfragen „Woher?“ und „Wofür?“ sind für Laien verständlich beantwortet.

Detailquelle für alle Anforderungen: `discussion/SPEZIFIKATION.md` (Abschnittsnummern in Klammern).

## v1 Requirements

### Setup

- [x] **SETUP-01**: Repo-Struktur nach Spez. 7 existiert (`pipeline/`, `daten/{zwischen,aufbereitet,manuell,pruefberichte}`, `app/`), das Quell-PDF liegt unter `raw_data/`
- [x] **SETUP-02**: Pipeline ist ein uv-Projekt (Python ≥ 3.12, pdfplumber, polars, typer, pytest), `uv run pytest` läuft
- [x] **SETUP-03**: App-Grundgerüst (Vue 3, TS, Vite, Web Awesome, vue-echarts, Hash-Router) mit übernommenen Münster-Basiskomponenten, `npm run build` läuft
- [x] **SETUP-04**: Projekt-`CLAUDE.md` dokumentiert Befehle und Konventionen (deutsche Bezeichner ohne Umlaute, Beträge als int-Euro, nur PDF-Seiten 1-basiert)
- [x] **SETUP-05**: Jahrgangsspezifisches (Haushaltsjahr, Spaltenköpfe, Seitenbereiche, PDF-Pfad) steht in einer Konfigurationsdatei, nicht im Code, damit das ProFIS-Layout eines Folgejahres mit wenig Änderung verarbeitbar ist

### Extraktion

- [ ] **EXTR-01**: Zahlenparser verarbeitet deutsches Format, Minus, „–“ als „kein Wert“, an Bezeichnungen klebende Beträge und `C` als Eurozeichen (mit Unit-Tests)
- [x] **EXTR-02**: Seitenklassifikation erzeugt `daten/zwischen/seiten.csv` (Seite, Typ, PB, PG, Produkt); Fortsetzungsseiten erben den Kontext; Startseiten aller 63 Produkte stimmen mit Anhang A überein
- [x] **EXTR-03**: `hierarchie.csv` enthält 15 PB, alle PG (synthetische mit `synthetisch=true`) und 63 Produkte mit Namen aus der Produktseite
- [x] **EXTR-04**: Gesamtergebnisplan und alle Teilergebnispläne (PB, Produkt) stehen im Langformat in `ergebnisplan.csv` mit `zeile`, `zeile_kanonisch`, `ist_summe` und `pdf_seite`; Spalten werden über x-Koordinaten zugeordnet; fehlende Zeilen gelten als 0
- [x] **EXTR-05**: Gesamtfinanzplan und alle Teilfinanzpläne inklusive VE-Spalte stehen in `finanzplan.csv`
- [ ] **EXTR-06**: Produktinformationen aller 63 Produkte stehen in `produkte.json` (Fachbereich, Gremium, Beschreibung, Leistungen, Auftragsgrundlage, Bindungsgrad normalisiert und original, Klassifizierung, Zielgruppe, Ziele, PDF-Seiten)
- [ ] **EXTR-07**: Grundzahlen je Produkt stehen in `grundzahlen.csv` mit Einheit, Jahr und Stichtagshinweis; die Steuer-Istwerte 2022–2025 aus 160101 sind enthalten
- [ ] **EXTR-08**: Erläuterungsposten („Erläuterung zu Nr. …“) sind je Produkt mit Betrag, Text und Zeilenbezug extrahiert
- [ ] **EXTR-09**: Investitionsmaßnahmen werden nur aus den Produktseiten in `investitionen.csv` extrahiert (Konto, Richtung, Jahr, Wertart); „(Kassenwirksamkeit)“-Zeilen landen in `ve_faelligkeiten.csv` und nicht in Summen
- [ ] **EXTR-10**: Der Stellenplan (Teil A Beamte, Teil B Tarif, Stellenübersicht nach PB) steht in `stellenplan.csv` mit Stellen 2026, 2025, besetzt 30.06.2025 und Vermerken

### Manuelle Daten

- [ ] **MANU-01**: `steuerarten.csv` (8 Steuerarten, 2024–2029, T€) aus Vorbericht S. 27
- [ ] **MANU-02**: `zuwendungen.csv` (Schlüsselzuweisung, laufende Zwecke, Sonderposten) aus S. 28
- [ ] **MANU-03**: `transferaufwendungen.csv` inklusive Kreisumlage netto mit Fußnote (Rückstellungsauflösung 1.325.478 €) aus S. 45–46
- [ ] **MANU-04**: `kita_zuschuesse.csv` (7 Einrichtungen, Summe 559 T€) aus S. 46
- [ ] **MANU-05**: `weitere_vorberichtstabellen.csv` (Leistungsentgelte, Kostenerstattungen, Personal, Sachaufwand, Sonstige Aufwendungen) aus S. 29–50
- [ ] **MANU-06**: `meta.json` mit Einwohnerzahl 11.741 (Stichtag, Quelle), Hebesätzen, Fläche, Satzungsdatum, Kreisumlage brutto/netto und Kreisumlage-Hebesätzen
- [ ] **MANU-07**: Jede manuelle Datei hat eine Spalte `quelle` mit PDF-Seite; ein README begründet die Werte
- [ ] **MANU-08**: Geprüfte Erklärtexte (`texte/erklaerungen.md`) mit Seitenverweis, z. B. zu Schlüsselzuweisung, Gewerbesteuer und Kreisumlage

### Prüfung

- [x] **PRUEF-01**: Zeilenformeln jedes Ergebnis- und Finanzplans stimmen (Spez. 5.5 Regel 1)
- [ ] **PRUEF-02**: Summe der Produkt-Teilpläne = PG = PB-Teilplan, je Zeile und Jahr
- [ ] **PRUEF-03**: Summe der 15 PB = Gesamtergebnisplan (Z. 01–17, 19, 20; ohne TP 27/28)
- [ ] **PRUEF-04**: Sollwerte aus Anhang B (Gesamtergebnisplan, Gesamtfinanzplan/Satzung § 1, PB-Summen, Eckwerte) werden getroffen
- [ ] **PRUEF-05**: Manuelle Tabellen stimmen mit den jeweiligen Planzeilen überein (Toleranz ±1 T€ bei T€-Tabellen; bekannte Differenzen dokumentiert)
- [ ] **PRUEF-06**: Investitionssummen je Produkt = Teilfinanzplan Z. 23/30; Summe aller = Gesamtfinanzplan (2026: 7.224.830 € / 12.280.484 €)
- [ ] **PRUEF-07**: Querschnitte S. 291 ff. stimmen mit den eigenen PG-Aggregaten überein
- [ ] **PRUEF-08**: Vollständigkeit: 63 Produkte mit Produktinformationen, Bindungsgrad, Teilergebnisplan und Teilfinanzplan
- [ ] **PRUEF-09**: Alle Prüfungen laufen in pytest und erzeugen `daten/pruefberichte/konsistenz.md`; Abweichungen über 1 € sind Fehler, außer sie stehen in `befunde.md`
- [ ] **PRUEF-10**: `pipeline/alle.py` läuft alle Schritte in Reihenfolge; CI prüft, dass sie keinen Diff an eingecheckten Daten erzeugt

### App-Daten

- [ ] **DATA-01**: Das Build-Skript erzeugt `haushalt.json`, `produkte.json` (ohne Personennamen), `investitionen.json` und `stellenplan.json` in `app/src/data/`
- [ ] **DATA-02**: In allen Ausgabendaten ist „Weitergabe an Kreis und Land“ (Kreisumlage, Gewerbesteuerumlage, Krankenhausinvestitionsumlage) als eigene Kategorie aus PB 16 herausgelöst; der Rest bleibt „Allgemeine Finanzwirtschaft“
- [ ] **DATA-03**: Zuschussbedarf (Aufwand − Erträge) ist je Knoten und Jahr berechnet und als berechneter Wert gekennzeichnet
- [ ] **DATA-04**: Quellenbelege: Zu prominent gezeigten Werten werden PDF-Zeilenrechteck und gerenderte WebP-Seite erzeugt (`quellen.json`, `public/quellen/`)

### Start

- [ ] **START-01**: Die Startseite zeigt ein Kennzahlenband 2026 (Erträge, Aufwendungen, Defizit nach Minderaufwand, Investitionen, neue Kredite, Pro-Kopf-Werte)
- [ ] **START-02**: Die Startseite bietet zwei große Einstiege zu „Woher kommt das Geld?“ und „Wofür wird es ausgegeben?“ sowie einen Hinweis auf die Kreisumlage als größten Posten

### Einnahmen

- [ ] **EINN-01**: Nutzer sieht die Ertragsarten 2026 mit Betrag und Prozentanteil
- [ ] **EINN-02**: Nutzer kann Steuern nach Steuerart aufklappen, sieht die Hebesätze und erfährt, welche Steuern die Gemeinde selbst festlegt
- [ ] **EINN-03**: Nutzer kann Zuwendungen aufklappen (Schlüsselzuweisung, laufende Zwecke mit Beispielen, Sonderposten mit Hinweis „kein Geldfluss“)
- [ ] **EINN-04**: Nutzer sieht sonstige ordentliche Erträge mit Konzessionsabgaben, soweit belegbar
- [ ] **EINN-05**: Nutzer sieht je Steuerart eine Zeitreihe 2022–2029, Ist und Plan sind visuell unterscheidbar, mit Erklärtexten (Gewerbesteuer-Einbruch, Schlüsselzuweisung)
- [ ] **EINN-06**: Investive Einnahmen (Pauschalen, Grundstücksverkäufe, Beiträge, Kredite) stehen getrennt und klar abgegrenzt

### Ausgaben

- [ ] **AUSG-01**: Nutzer sieht eine Treemap der ordentlichen Aufwendungen mit Drilldown Aufgabenbereich → Produktgruppe → Produkt
- [ ] **AUSG-02**: „Weitergabe an Kreis und Land“ ist eine farblich abgesetzte Top-Kachel mit Info-Callout; der globale Minderaufwand erscheint als erklärter Hinweis unter dem Diagramm
- [ ] **AUSG-03**: Nutzer kann zwischen „Aufwand“ und „Zuschussbedarf“ umschalten; Überschüsse werden eigens erklärt
- [ ] **AUSG-04**: Nutzer sieht Aufwendungen nach Aufwandsart; Transferaufwendungen lassen sich mit der Vorberichtstabelle aufklappen, Abschreibungen tragen den Hinweis „kein Geldfluss“
- [ ] **AUSG-05**: Nutzer kann ein Produkt öffnen und sieht Beschreibung, Leistungen, Bindungsgrad, Gremium, den Teilergebnisplan 2024–2029, Erläuterungsposten, Grundzahlen mit gekennzeichneten berechneten Pro-Kopf-Werten, Investitionen und den Quellenlink

### Geldfluss

- [ ] **FLUSS-01**: Nutzer sieht einen Sankey 2026 (Ergebnisplan): Ertragsarten (Steuern nach Art) → Gemeindehaushalt → Weitergabe an Kreis und Land, Aufgabenbereiche, Zinsen
- [ ] **FLUSS-02**: Der Sankey bilanziert über einen erklärten Knoten „Defizit (Entnahme aus Rücklagen)“ und den Minderaufwand als Gegenposten
- [ ] **FLUSS-03**: Hover hebt Pfade hervor; ein Klick auf einen Aufgabenbereich führt zur Ausgabenseite
- [ ] **FLUSS-04**: Auf schmalen Bildschirmen erscheint statt des Sankeys eine Tabelle oder gestapelte Balken

### Entwicklung

- [ ] **ENTW-01**: Nutzer sieht Erträge, Aufwendungen und Jahresergebnis 2024–2029, Ist, Ansatz und Planung sind unterscheidbar
- [ ] **ENTW-02**: Nutzer sieht Zeitreihen für Kreisumlage, Gewerbesteuer, Schlüsselzuweisung, Personal und Zinsen
- [ ] **ENTW-03**: Nutzer sieht Ausgleichsrücklage und allgemeine Rücklage und wie lange das Polster reicht

### Investitionen und Schulden

- [ ] **INV-01**: Nutzer sieht Investitionsmaßnahmen 2026–2029 als Liste und Balken, filterbar nach Aufgabenbereich und Art (Bau, Grundstücke, Fahrzeuge/Ausstattung)
- [ ] **INV-02**: Nutzer sieht die Verpflichtungsermächtigungen (11,6 Mio. €) mit ihren Fälligkeiten
- [ ] **INV-03**: Nutzer sieht die Finanzierung (Investitionseinzahlungen, Kredite) und eine Zeitreihe von Kreditaufnahme und Tilgung 2024–2029
- [ ] **INV-04**: Nutzer sieht den Schuldenstand gesamt und je Einwohner

### Rat entscheidet

- [ ] **RAT-01**: Nutzer sieht den Zuschussbedarf 2026 nach Bindungsgrad (pflichtig / teils / freiwillig) als gestapelten Balken mit den Produkten je Kategorie
- [ ] **RAT-02**: Nutzer sieht einen Block „Was der Rat nicht beeinflussen kann“ (Kreisumlage, Gewerbesteuerumlage, gesetzliche Sozialleistungen)
- [ ] **RAT-03**: Nutzer sieht die Einzelzuschüsse aus dem Vorbericht (Kita-Träger einzeln, Kinder- und Jugendwerk, OGS, Vereine, VHS, Sport, Musikschule)
- [ ] **RAT-04**: Ein Hinweis erklärt, dass der Bindungsgrad eine Selbstauskunft der Verwaltung ist

### Stellenplan

- [ ] **STEL-01**: Nutzer sieht die Stellen 2026 gesamt im Vergleich zu 2025 und zu den besetzten Stellen am 30.06.2025
- [ ] **STEL-02**: Nutzer sieht die Verteilung nach Aufgabenbereich und nach Entgelt- bzw. Besoldungsgruppe
- [ ] **STEL-03**: Nutzer sieht daneben den Personalaufwand je Aufgabenbereich (TP Z. 11)

### Glossar

- [ ] **GLOS-01**: Das Glossar erklärt alle Begriffe aus Spez. 6.14 (mindestens 22 Begriffe)
- [ ] **GLOS-02**: Das Glossar listet alle 63 Produkte mit Beschreibung als Akkordeon
- [ ] **GLOS-03**: `GlossarBegriff`-Links auf allen Seiten führen zum jeweiligen Begriff

### Gemeinsame UI

- [ ] **UI-01**: Auf Einnahmen, Ausgaben und Geldfluss gibt es einen Jahr-Umschalter (2024 Ist … 2029 Planung), Standard ist 2026
- [ ] **UI-02**: „Quelle anzeigen“ öffnet an Kennzahlen und Tabellenzeilen eine Seitenleiste mit dem PDF-Ausschnitt
- [ ] **UI-03**: Die Fußzeile zeigt Datenstand, Link zum Original-PDF, den Hinweis „inoffizielles Projekt“ und einen Kontakt
- [ ] **UI-04**: Ein Hinweis „Was nicht im Haushalt steht“ erklärt BBO (Hallenbad) und TEO AöR (Abwasser)
- [ ] **UI-05**: Zahlen in Texten werden aus den Daten erzeugt, nicht fest eingetippt; jeder Erklärtext mit Zahl verweist auf eine PDF-Seite
- [ ] **UI-06**: Alle Texte sind deutsch und durchgehend in der Du-Anrede

### Barrierefreiheit und Qualität

- [ ] **A11Y-01**: Zu jedem Diagramm gibt es eine Tabellenalternative
- [ ] **A11Y-02**: Fokussteuerung beim Routenwechsel, ausreichende Kontraste und `prefers-reduced-motion` werden beachtet
- [ ] **A11Y-03**: Alle Seiten sind ab 360 px Breite nutzbar
- [ ] **A11Y-04**: Lighthouse-Barrierefreiheit ≥ 95 auf allen Routen
- [x] **QUAL-01**: `vue-tsc` und ESLint laufen fehlerfrei in der CI
- [ ] **QUAL-02**: Ein Playwright-Smoke-Test stellt sicher, dass jede Route ohne Konsolenfehler rendert und Diagramme Daten enthalten

### Deployment

- [ ] **DEPL-01**: GitHub Actions baut die App und deployt sie auf GitHub Pages (eigener Account)
- [ ] **DEPL-02**: Die App ist unter einer öffentlichen URL erreichbar

## v2 Requirements

### Spiele

- **SPIEL-01**: Planspiel „Bring das Minus auf null“ mit Hebelkarten in vier Gruppen, Fortschrittsbalken und Teilen per URL (Rechenregeln vorher fachlich prüfen lassen)
- **SPIEL-02**: „Was kostet …?“ mit wählbarem Betrag und Vergleichen (je Einwohner, Hebesatzpunkte)
- **SPIEL-03**: Schätzduell mit Produktpaaren nach Zuschussbedarf
- **SPIEL-04**: Teaser für die Spiele auf der Startseite
- **SPIEL-05**: Pipeline erzeugt `planspiel.json` in Anlehnung an Münsters Struktur

### Erweiterungen

- **ERW-01**: Eigene Seite für BBO (Hallenbad) und TEO AöR (Abwasser)
- **ERW-02**: Kennzeichnung „Ortsteil Brock“ für Investitionsmaßnahmen
- **ERW-03**: Haushalt 2027 mit derselben Pipeline verarbeiten

## Out of Scope

| Feature | Reason |
|---------|--------|
| Backend, Nutzerkonten | Rein statische App auf GitHub Pages |
| Fachbereichsbudgets (S. 377–400) | Organisatorische Doppelung der Produktsicht |
| Ergebnis-/Finanzrechnung und Bilanz 2024 als eigene Sicht | Optional in der Spec; v1 nutzt die Ist-Spalte der Pläne |
| Zuwendungen an Fraktionen (S. 307) | Optional, kein Bezug zu den Leitfragen |
| Gehaltsschätzung im Stellenplan | Bewusst einfacher als Münsters Stellenatlas |
| CSV-Verarbeitung im Browser | App liest nur generierte JSON-Dateien |
| Personennamen in der App | Datenschutz |
| Mischen von Ergebnis- und Finanzplan in einem Diagramm | Fachlich irreführend (Spez. 3.1) |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| SETUP-01 | Phase 1 | Complete |
| SETUP-02 | Phase 1 | Complete |
| SETUP-03 | Phase 1 | Complete |
| SETUP-04 | Phase 1 | Complete |
| SETUP-05 | Phase 1 | Complete |
| EXTR-01 | Phase 2 | Pending |
| EXTR-02 | Phase 2 | Complete |
| EXTR-03 | Phase 2 | Complete |
| EXTR-04 | Phase 2 | Complete |
| EXTR-05 | Phase 2 | Complete |
| EXTR-06 | Phase 3 | Pending |
| EXTR-07 | Phase 3 | Pending |
| EXTR-08 | Phase 3 | Pending |
| EXTR-09 | Phase 3 | Pending |
| EXTR-10 | Phase 4 | Pending |
| MANU-01 | Phase 4 | Pending |
| MANU-02 | Phase 4 | Pending |
| MANU-03 | Phase 4 | Pending |
| MANU-04 | Phase 4 | Pending |
| MANU-05 | Phase 4 | Pending |
| MANU-06 | Phase 4 | Pending |
| MANU-07 | Phase 4 | Pending |
| MANU-08 | Phase 4 | Pending |
| PRUEF-01 | Phase 2 | Complete |
| PRUEF-02 | Phase 2 | Pending |
| PRUEF-03 | Phase 2 | Pending |
| PRUEF-04 | Phase 2 | Pending |
| PRUEF-05 | Phase 4 | Pending |
| PRUEF-06 | Phase 3 | Pending |
| PRUEF-07 | Phase 3 | Pending |
| PRUEF-08 | Phase 3 | Pending |
| PRUEF-09 | Phase 2 | Pending |
| PRUEF-10 | Phase 4 | Pending |
| DATA-01 | Phase 4 | Pending |
| DATA-02 | Phase 4 | Pending |
| DATA-03 | Phase 4 | Pending |
| DATA-04 | Phase 7 | Pending |
| START-01 | Phase 5 | Pending |
| START-02 | Phase 5 | Pending |
| EINN-01 | Phase 5 | Pending |
| EINN-02 | Phase 5 | Pending |
| EINN-03 | Phase 5 | Pending |
| EINN-04 | Phase 5 | Pending |
| EINN-05 | Phase 5 | Pending |
| EINN-06 | Phase 5 | Pending |
| AUSG-01 | Phase 5 | Pending |
| AUSG-02 | Phase 5 | Pending |
| AUSG-03 | Phase 5 | Pending |
| AUSG-04 | Phase 5 | Pending |
| AUSG-05 | Phase 5 | Pending |
| FLUSS-01 | Phase 5 | Pending |
| FLUSS-02 | Phase 5 | Pending |
| FLUSS-03 | Phase 5 | Pending |
| FLUSS-04 | Phase 5 | Pending |
| ENTW-01 | Phase 6 | Pending |
| ENTW-02 | Phase 6 | Pending |
| ENTW-03 | Phase 6 | Pending |
| INV-01 | Phase 6 | Pending |
| INV-02 | Phase 6 | Pending |
| INV-03 | Phase 6 | Pending |
| INV-04 | Phase 6 | Pending |
| RAT-01 | Phase 6 | Pending |
| RAT-02 | Phase 6 | Pending |
| RAT-03 | Phase 6 | Pending |
| RAT-04 | Phase 6 | Pending |
| STEL-01 | Phase 6 | Pending |
| STEL-02 | Phase 6 | Pending |
| STEL-03 | Phase 6 | Pending |
| GLOS-01 | Phase 5 | Pending |
| GLOS-02 | Phase 5 | Pending |
| GLOS-03 | Phase 5 | Pending |
| UI-01 | Phase 5 | Pending |
| UI-02 | Phase 7 | Pending |
| UI-03 | Phase 5 | Pending |
| UI-04 | Phase 6 | Pending |
| UI-05 | Phase 5 | Pending |
| UI-06 | Phase 7 | Pending |
| A11Y-01 | Phase 7 | Pending |
| A11Y-02 | Phase 7 | Pending |
| A11Y-03 | Phase 7 | Pending |
| A11Y-04 | Phase 7 | Pending |
| QUAL-01 | Phase 1 | Complete |
| QUAL-02 | Phase 7 | Pending |
| DEPL-01 | Phase 7 | Pending |
| DEPL-02 | Phase 7 | Pending |

**Coverage:**
- v1 requirements: 85 total
- Mapped to phases: 85
- Unmapped: 0 ✓

---
*Requirements defined: 2026-10-01*
*Last updated: 2026-10-01 after roadmap creation*
