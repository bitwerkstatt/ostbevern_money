# Ostbevern Money

## What This Is

Eine statische Webanwendung, die den Bürgerinnen und Bürgern von Ostbevern den Haushalt 2026 der Gemeinde erklärt. Sie beantwortet zwei Leitfragen: **Wo kommt das Geld der Gemeinde her?** und **Wofür wird es ausgegeben?**. Ergänzend zeigt sie die Entwicklung 2024–2029, Investitionen und Schulden, den Gestaltungsspielraum des Rats und den Stellenplan. Die Daten stammen aus einer Python-Pipeline, die das 400-seitige ProFIS+-PDF ausliest und gegen die Planwerte prüft. Vorbild ist „Münster Money“ (Code for Münster, Münsterhack '26).

Die vollständige fachliche Spezifikation steht in `discussion/SPEZIFIKATION.md`. Sie ist die maßgebliche Detailquelle für Datenmodell, Prüfregeln, Seiteninhalte und Sollwerte (Anhang B).

## Current State

**Shipped:** v1.0 MVP am 2026-10-07. Öffentlich unter https://bitwerkstatt.github.io/ostbevern_money/ (11 Routen, Deploy über GitHub Actions nach grüner CI).

- Pipeline: ~25.500 LOC Python, Schritte 01–08 in `alle.py`, Prüfregeln 1–10 grün, Ausgabe byte-reproduzierbar
- App: ~29.900 LOC TypeScript/Vue, vitest und Playwright (axe-Smoke, 360 px, Kachel-Breitentest), Lighthouse-a11y 100
- Archiv: `.planning/milestones/v1.0-ROADMAP.md`, `v1.0-REQUIREMENTS.md`, `v1.0-phases/`

## Current Milestone: v1.0.1 Restpunkte

**Goal:** Die offenen Qualitätspunkte aus v1.0 abschließen, ohne neue Funktionen: jeder Review-Befund hat eine Disposition, Phase 4 ist sicherheitsgeprüft, v1.0 ist auditiert und gegen den aktuellen Stand verifiziert.

**Target features:**
- Triage der 28 offenen Review-Befunde aus Phase 1, 5 und 6 (Ledger in `milestones/v1.0-phases/*/…-REVIEW-DISPOSITION.md`), inkl. Bestätigung bereits behobener Befunde
- Befunde mit Wirkung auf Zahlen, Texte oder Barrierefreiheit beheben; reine Code-Hygiene beheben, wenn günstig, sonst begründet `deferred`
- Security-Prüfung für Phase 4 nachholen (`04-SECURITY.md`)
- Milestone-Audit für v1.0 nachholen und veraltete Verifikationen erneuern

Nicht enthalten: Deploy-/Gerätecheck aus Phase 7 (macht der Nutzer selbst), Spiele und Haushalt 2027 (bleiben v2-Backlog).

## Core Value

Jede Zahl in der App ist korrekt aus dem Haushalts-PDF abgeleitet und durch automatische Prüfungen gegen den Gesamtplan und die Satzung belegt. Die beiden Leitfragen „Woher?“ und „Wofür?“ sind für Laien verständlich beantwortet.

## Requirements

### Validated

- ✓ Seitenklassifikation aller PDF-Seiten (Typ, PB, PG, Produkt); Startseiten aller 63 Produkte stimmen mit Anhang A überein — v1.0 (Phase 2)
- ✓ Extraktion von Gesamtergebnisplan, Gesamtfinanzplan, Teilergebnis- und Teilfinanzplänen (PB, PG und Produkt) im Langformat, Spalten über x-Koordinaten — v1.0 (Phase 2)
- ✓ Produktinformationen (inkl. Bindungsgrad, Grundzahlen, Erläuterungsposten) für alle 63 Produkte — `produkte.json` ohne Personennamen, `grundzahlen.csv`, `erlaeuterungen.csv` — v1.0 (Phase 3)
- ✓ Investitionsmaßnahmen (nur aus Produktseiten) und VE-Fälligkeiten — `investitionen.csv`, `ve_faelligkeiten.csv`, PB-Listen als Kontrollquelle — v1.0 (Phase 3)
- ✓ Stellenplan (Teil A Beamte, Teil B Tarif, Stellenübersicht nach PB) — `stellenplan.csv`, Regel 10, Beamte 2026 = 8 — v1.0 (Phase 4)
- ✓ Manuell gepflegte Vorberichtstabellen und `meta.json` mit Quelle je Wert, automatisch gegen Planzeilen geprüft (Regel 5, Eckwerte Regel 9) — v1.0 (Phase 4)
- ✓ Konsistenzprüfung (Prüfregeln 1–10) in pytest und als Markdown-Bericht; bekannte Abweichungen in `befunde.md` — v1.0 (Phase 4)
- ✓ App-JSON-Dateien (`haushalt.json`, `produkte.json`, `investitionen.json`, `stellenplan.json`, `texte.json`) reproduzierbar über `alle.py`, ohne Personennamen, CI-Diff-Prüfung — v1.0 (Phase 4)
- ✓ Erklärtexte mit Datenplatzhaltern und Seitenverweis; jede Zahl rendert über `formatiere()` korrekt (Jahreszahlen mit Kürzel `jahr`, CR-01) — v1.0 (Phase 4)
- ✓ Start mit Kennzahlenband 2026 und Einstiegen zu den Leitfragen — v1.0 (Phase 5)
- ✓ Einnahmen: Ertragsarten → Steuerarten/Zuwendungen → Zeitreihen; investive Einnahmen separat — v1.0 (Phase 5)
- ✓ Ausgaben: Treemap mit Drilldown, „Weitergabe an Kreis und Land“ als eigene Kategorie, Umschalter Aufwand/Zuschussbedarf, Sicht nach Aufwandsart, Produktdetail — v1.0 (Phase 5)
- ✓ Geldfluss: Sankey 2024–2029 inkl. Defizit- und Minderaufwand-Ausgleich, mobile Alternative — v1.0 (Phase 5)
- ✓ Glossar mit allen Begriffen und allen 63 Produkten, GlossarBegriff-Links mit Tooltip und Sprungmarke — v1.0 (Phase 5)
- ✓ Entwicklung 2024–2029: Erträge/Aufwendungen, Jahresergebnis nach Wertart, Posten-Zeitreihen, Rücklagen mit Rückgang je Jahr (S. 23/311) — v1.0 (Phase 6)
- ✓ Investitionen und Schulden: Maßnahmen mit Filter (URL-Zustand), VE 11,6 Mio. € mit Fälligkeiten, Finanzierung, Schuldenstand gesamt/je Einwohner — v1.0 (Phase 6)
- ✓ Worüber entscheidet der Rat? Bindungsgrad-Balken mit Produkten, „Was der Rat nicht beeinflussen kann“, Einzelzuschüsse (Regel 5), Selbstauskunft-Hinweis — v1.0 (Phase 6)
- ✓ Stellenplan 2026/2025/besetzt, nach Aufgabenbereich und Gruppe, Personalaufwand je Aufgabenbereich — v1.0 (Phase 6)
- ✓ Hinweis „Was nicht im Haushalt steht“ (BBO, TEO AöR) — v1.0 (Phase 6)
- ✓ Quellenbelege: Zeilenrechteck + gerenderte WebP-Seiten, `quellen.json`, „Quelle anzeigen“-Leiste — v1.0 (Phase 7)
- ✓ Jahr-Umschalter, Fußzeile mit Datenstand, Hinweis „inoffizielles Projekt“, echte Kontakt-Adresse und PDF-Link der Gemeinde (D-17) — v1.0 (Phase 7)
- ✓ Barrierefreiheit (Lighthouse-a11y 100 auf allen 11 Routen), Tabellenalternative zu jedem Diagramm, responsiv ab 360 px (Kachel-Raster über alle Spaltensprünge geprüft) — v1.0 (Phase 7)
- ✓ Deployment über GitHub Actions auf GitHub Pages: https://bitwerkstatt.github.io/ostbevern_money/ — v1.0 (Phase 7)
- ✓ Pipeline ist für das ProFIS-Layout generisch konfigurierbar (Jahr, Spalten, Seitenbereiche in `jahrgaenge/{jahr}.toml`) — v1.0 (Phase 1); der Nachweis mit echtem Haushalt 2027 ist ERW-03 (v2)
- ✓ Alle 28 offenen Review-Befunde aus v1.0 haben eine Disposition (27 fixed, 1 skipped, 0 deferred); Ledger 01, 05 und 06 auf `open: 0` — v1.0.1 (Phase 8)
- ✓ Fachlich relevante Befunde (Zahlen, Texte, Barrierefreiheit) sind behoben, inkl. Screenreader-Prüfung der Tabellennamen bei 360 px (UAT 08) — v1.0.1 (Phase 8)


### Active

- [ ] Phase 4 ist sicherheitsgeprüft — v1.0.1
- [ ] v1.0 ist auditiert, Verifikationen sind aktuell — v1.0.1

### Out of Scope

- Spiele (Planspiel, Was kostet …?, Schätzduell) — auf v2 verschoben; v1 endet mit den Kontextseiten. Planspiel-Rechenregeln (Hebesatzwirkung auf Umlagen/Schlüsselzuweisung) müssen vorher fachlich geklärt werden
- Andere Haushaltsjahre außer den Spalten im PDF 2026 — v1 ist ein Jahrgang; die Pipeline wird aber für spätere Jahrgänge vorbereitet
- Backend, Nutzerkonten — alles statisch auf GitHub Pages
- Tiefe Darstellung der Wirtschaftspläne BBO (Hallenbad) und TEO AöR (Abwasser) — nur Hinweis „Was nicht im Haushalt steht“; eigene Seite ggf. in einer späteren Version
- Fachbereichsbudgets (S. 377–400) — organisatorische Doppelung der Produktsicht
- Gehaltsschätzung im Stellenplan — bewusst einfacher als Münsters Stellenatlas
- CSV-Verarbeitung im Browser — die App liest nur generierte JSON-Dateien
- Personennamen von Mitarbeitenden in der App — Datenschutz; nur Fachbereich und Gremium

## Context

- **Quelle:** `raw_data/haushalt-2026.pdf` (seit Phase 1 einzige eingecheckte Kopie; Pfad steht in `pipeline/jahrgaenge/2026.toml`), Gemeinde Ostbevern, 400 Seiten, ProFIS+, Satzungsbeschluss 03.03.2026. Im Code werden ausschließlich 1-basierte PDF-Seiten verwendet.
- **Vorbild:** https://github.com/codeformuenster/haushalt-muenster-2026. Die Erlaubnis von Code for Münster zur Übernahme von Code liegt vor. Komponenten (`PageIntro`, `ChartCard`, `BaseChart`, `DatenTabelle`, `GlossarBegriff`, `BegriffeListe`, `ProduktAkkordeon`, `QuelleSeitenleiste`, Sankey, `charts/format.ts`, `echartsTheme.ts`, `lib/bildschirm.ts`) können übernommen werden.
- **Fachliche Fallstricke** (Details in Spez. Abschnitt 3):
  - Der Ergebnisplan ist die Hauptsicht. Der Finanzplan wird nur für Investitionen, Kredite und Liquidität genutzt. Beide werden nie in einem Diagramm gemischt.
  - Zeilennummern unterscheiden sich zwischen Gesamt- und Teilplänen (Minderaufwand GP 27 / TP 30). Geschlüsselt wird über Zeilennummer + Plantyp.
  - Interne Leistungsbeziehungen (TP 27/28) gehen nie in Summen ein. Fehlende Zeilen bedeuten 0.
  - Globaler Minderaufwand (600 T€) wird als eigener, erklärter Posten gezeigt. Das Jahresergebnis von −2.353.506 € gilt nach Minderaufwand.
  - Die Kreisumlage (10.147 T€ netto) ist der größte Posten. In allen Ausgabensichten wird sie aus PB 16 als „Weitergabe an Kreis und Land“ herausgelöst.
  - Die Einnahmen liegen fast vollständig in PB 16. Die Einnahmenseite gliedert deshalb nach Ertrags- und Steuerart, nicht nach PB.
  - Sonderposten und Abschreibungen fließen nicht als Geld und werden gekennzeichnet.
  - Bekannte Datenauffälligkeiten stehen in Spez. 3.8 (Fußnotenziffer an 10.147, Zuwendungsdifferenz von ca. 4 T€, Investitionen dreifach im PDF, angeklebte Beträge, VE-Kassenwirksamkeitszeilen).
- **Sollwerte** für Tests stehen in Spez. Anhang B (Gesamtergebnisplan 2024–2029, Gesamtfinanzplan 2026, PB-Summen, Steuerarten, Transferaufwendungen, Eckwerte).
- **Konventionen:** Bezeichner auf Deutsch ohne Umlaute. Beträge als `int` in Euro, Formatierung nur in der App. Generierte Dateien werden eingecheckt, und die CI prüft, dass `pipeline/alle.py` keinen Diff erzeugt.

## Constraints

- **Tech stack Pipeline**: Python ≥ 3.12, uv, pdfplumber, polars, typer, pytest. Das entspricht dem Münster-Stack und erleichtert die Übernahme.
- **Tech stack App**: Vue 3, TypeScript, Vite, Web Awesome, ECharts (`vue-echarts`), Hash-Router. So lassen sich die Münster-Komponenten wiederverwenden.
- **Hosting**: GitHub Pages unter eigenem GitHub-Account, Deployment über GitHub Actions. Es gibt kein Backend.
- **Genauigkeit**: Abweichungen über 1 € gegenüber den Planwerten gelten als Fehler, außer sie sind in `befunde.md` dokumentiert. Bürgerinformation muss stimmen.
- **Datenschutz**: Mitarbeitendennamen werden extrahiert, aber nicht ausgeliefert.
- **Sprache**: Die App ist deutsch und durchgehend in der Du-Anrede.
- **Pro-Kopf-Werte**: Grundlage sind 11.741 Einwohner (IT.NRW, 30.06.2024, Vorbericht S. 24/25). Der Wert ist in `meta.json` konfigurierbar.
- **Barrierefreiheit**: Lighthouse a11y ≥ 95, Fokussteuerung, Kontraste, `prefers-reduced-motion`, responsiv ab 360 px.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Münster-Code übernehmen | Erlaubnis von Code for Münster liegt vor, spart Aufwand bei Charts und Komponenten | ✓ Good — v1.0 (Basiskomponenten mit Münster-Namen und -Props) |
| Einwohnerzahl 11.741 | Im Haushalt selbst begründet (Vorbericht), Stichtag bekannt | ✓ Good — v1.0 (in `meta.json`, Pro-Kopf-Werte als „berechnet“ markiert) |
| Du-Anrede überall | Einheitlich und nahbar, wird später auch für die Spiele passen | ✓ Good — v1.0 (Du-Anrede-Wächter in vitest) |
| GitHub Pages, eigener Account | Einfachstes Hosting, Umzug später möglich | ✓ Good — Phase 7 (Repo `ostbevern_money`, CI inkl. deploy grün) |
| Kämmerei erst nach Fertigstellung informieren | Kein Abstimmungs-Gate; Hinweis „inoffizielles Projekt“ | — Pending (App ist live, Information steht aus) |
| Pipeline generisch für ProFIS-Layout | Haushalt 2027 soll mit wenig Änderung verarbeitbar sein | — Pending (Struktur steht, Nachweis mit 2027 = ERW-03) |
| v1 = Pipeline + Leitfragen + Kontextseiten + Feinschliff; Spiele in v2 | Fokus auf korrekte Kernaussagen; Planspiel-Regeln brauchen fachliche Klärung | ✓ Good — v1.0 in 7 Tagen geliefert |
| Ergebnisplan als Hauptsicht, Kreisumlage herausgelöst | Fachlich korrekt für eine kreisangehörige Gemeinde (Spez. 3.1, 3.4) | ✓ Good — v1.0 |
| BBO/TEO nur als Hinweis | Außerhalb des Kernhaushalts; eigene Seite ggf. später | ✓ Good — v1.0 (Hinweisbox auf drei Seiten) |
| Paketliste vor Installation menschlich freigegeben (5 PyPI, 21 npm); Minor-/Patch-Drift ok, neue Major-Versionen brauchen erneute Freigabe | Supply-Chain-Schutz vor jeder Installation | ✓ Good — Phase 1 |
| Jahrgangswerte nur in `jahrgaenge/{jahr}.toml` und `{jahr}_sollwerte.toml`, gelesen über `lade_jahrgang`/`lade_sollwerte` mit vollständiger Validierung | Pipeline generisch für spätere Jahrgänge | ✓ Good — Phase 1 |
| Nummerierte Pipeline-Skripte entstehen erst mit ihrer Logik in der jeweiligen Phase; Phase 1 liefert nur `alle.py` | Keine leeren Platzhaltermodule | ✓ Good — Phase 1 |
| ESLint-only (oxlint und vue-devtools aus dem Scaffold entfernt) | Nur freigegebene Pakete | ✓ Good — Phase 1 |
| ECharts-Module nur in `echartsTheme.ts` registriert; Beispieldaten-Hinweis rendert ausschließlich `ChartCard` | Kleines Bundle; Demo-Zahlen können nie ohne Hinweis erscheinen | ✓ Good — Phase 1 |
| CI: zwei parallele Jobs, Actions SHA-gepinnt, `contents: read`, Installation nur aus Lockfiles | Lokal nachgestellte CI = Remote-CI | ✓ Good — Phase 1 (Remote-CI seit Phase 7 grün) |
| Anhang-B-Sollwerte sind unabhängige Referenz, aber nicht unfehlbar: Abweichungen werden erst gegen das PDF geprüft, dann korrigiert | Spez. Anhang B.3 hatte für PB 09/15 Z. 29 den Wert der ersten PG statt der GESAMTSUMME (S. 296/299) übernommen | ✓ Good — Phase 2 |
| Gedruckte Rundungsdifferenzen (2–3 €) gehen mit Seitenbeleg in `befunde.md`, nie in eine Toleranz | Toleranz bleibt strikt 1 €; jede Ausnahme ist einzeln belegt | ✓ Good — Phase 2 (10 Befunde) |
| Nicht gedruckte Produktgruppen werden synthetisch gebildet (`synthetisch=true`) | Teilplanbereich druckt nicht jede PG | ✓ Good — Phase 2; genau ein Produkt je synthetischer PG, PG 1502 „Tourismus“ als deklarierte Ausnahme in der Jahrgangsdatei (Quick 261001-oim) |
| PDF-lesende Kontrollquellen (Querschnitte, PB-Investitionslisten) laufen als eigene Extraktionsschritte vor der Prüfung; `pruefung.py` bleibt CSV/JSON-only | Prüfung bleibt PDF-unabhängig und testbar | ✓ Good — Phase 3 |
| Strukturelle Lücken (Maßnahme nur in einer Quelle) sind keine Betragsabweichung und können nicht über `befunde.md` entschuldigt werden | Fehlende Daten dürfen nie als „bekannt“ durchrutschen | ✓ Good — Phase 3 (0 Lücken) |
| Personennamen werden beim Parsen verworfen, bevor ein Datensatz entsteht; Schutz dreifach (Parse-Zeit, exakter Schlüsselsatz, Whole-Tree-Test) | Repo ist öffentlich (D-09) | ✓ Good — Phase 3 |
| Historische Ergebnis-Spalten-Differenzen der Investitionstabellen werden als Befund belegt, interne Gegenproben vergleichen nur Budgetspalten | Ist-Werte auf heute nicht mehr geführten Konten sind im PDF so gedruckt | ✓ Good — Phase 3 (8 Befunde Regel 6, 18 Befunde Regel 7) |
| Erklärtexte nutzen Platzhalter `{{schluessel\|kuerzel}}`; formatiert wird nur in `format.ts`, Jahreszahlen mit eigenem Kürzel `jahr` (ohne Tausendertrennung) | Pipeline formatiert nie (D-15); „2.026“ statt „2026“ war ein echter Fehler (CR-01) | ✓ Good — Phase 4 (Rendertest über `formatiere()`-Portierung mit Node-Gegenprobe) |
| Manuelle Vorberichtswerte sind unabhängige Transkription mit Seitenbeleg; Fußnoten werden als korrigierter Wert mit Anmerkung gespeichert, Cent-Beträge kaufmännisch gerundet | Regel 5/9 treffen GEP und Satzung exakt | ✓ Good — Phase 4 |
| „Weitergabe an Kreis und Land“ als eigener Knoten; Zuschussbedarf je Knoten als berechneter Wert gekennzeichnet | Fachlich korrekte Ausgabensicht für eine kreisangehörige Gemeinde | ✓ Good — Phase 4 |
| HSK-Schwellen und Rücklagen-Rückgang aus dem Vorbericht (S. 23) in `meta.json`, Rückgang in TS und Python nach derselben Regel | Polster-Aussage muss gedruckte Werte exakt treffen | ✓ Good — Phase 6 (1,77/4,23/4,73/10,04 %) |
| Rücklagen-Fußnote nennt Beträge ohne Vorzeichen („zuzüglich der Verrechnung“) | Beträge-Lesart ergibt die gedruckten 1,77 %; Vorzeichen-Zusatz nicht nötig (UAT 06, WR-01) | ✓ Good — Phase 6 |
| Kontextseiten über Menügruppe „Mehr wissen“ (Disclosure, Drawer-Gruppe mobil), Position rein rechnerisch | Navigation bleibt bei 360 px und nach Resize erreichbar | ✓ Good — Phase 6 |
| Phase-6-Dateien stehen unter einem Typografie-Wächter (`stiltokens.test.ts`), Bestand aus Phase 5 wird in Phase 7 bereinigt | UI-SPEC-Skala gilt für neuen Code ohne Ausnahme | ✓ Good — Quick 261006-f1w |
| Kachelraster gegen die CI-Schrift kalibriert: `li`-Einzug von Web Awesome zurückgesetzt, Mindestspalte neu gegen DejaVu Sans Bold, e2e prüft alle Spaltensprünge und loggt die gerenderte Schrift | Lokale Kalibrierung lief mit anderer Fallback-Schrift als der GitHub-Runner (G-07-2) | ✓ Good — Phase 7 (07-14, UAT 2/2) |
| Lighthouse nur als Einmal-Werkzeug im Scratch-Verzeichnis, nie in package.json/CI | Keine neue Abhängigkeit für einen einmaligen Nachweis | ✓ Good — Phase 7 (alle 11 Routen a11y 100) |
| `DatenTabelle`: `beschriftung`/`spalten`/`zeilen` als Pflicht-Props, Slot-Modus entfernt; Tabellenname nur aus der Caption, Scrollrahmen per `aria-labelledby` | Bewusste Abweichung von den Münster-Props; verhindert doppelte Screenreader-Ansage (A11Y-03) | ✓ Good — Phase 8 (UAT 1/1) |
| Feste Jahre in Texten über Schlüssel `jahr.fest_JJJJ`, aus dem Schlüsselnamen aufgelöst; relative Jahre stehen in `textwerte` | Kein Jahrgangswert im Code, Texte bleiben jahrneutral prüfbar | ✓ Good — Phase 8 |
| Gerundete und berechnete Werte tragen ihr Etikett aus den Daten (`gerundet`-Flag), nicht aus festen Annahmen im Code | Kennzeichnung bleibt korrekt, wenn sich Daten ändern (TXT-04/05) | ✓ Good — Phase 8 |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-10-08 after Phase 8*
