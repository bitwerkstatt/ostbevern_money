# Ostbevern Money

## What This Is

Eine statische Webanwendung, die den Bürgerinnen und Bürgern von Ostbevern den Haushalt 2026 der Gemeinde erklärt. Sie beantwortet zwei Leitfragen: **Wo kommt das Geld der Gemeinde her?** und **Wofür wird es ausgegeben?**. Ergänzend zeigt sie die Entwicklung 2024–2029, Investitionen und Schulden, den Gestaltungsspielraum des Rats und den Stellenplan. Die Daten stammen aus einer Python-Pipeline, die das 400-seitige ProFIS+-PDF ausliest und gegen die Planwerte prüft. Vorbild ist „Münster Money“ (Code for Münster, Münsterhack '26).

Die vollständige fachliche Spezifikation steht in `discussion/SPEZIFIKATION.md`. Sie ist die maßgebliche Detailquelle für Datenmodell, Prüfregeln, Seiteninhalte und Sollwerte (Anhang B).

## Core Value

Jede Zahl in der App ist korrekt aus dem Haushalts-PDF abgeleitet und durch automatische Prüfungen gegen den Gesamtplan und die Satzung belegt. Die beiden Leitfragen „Woher?“ und „Wofür?“ sind für Laien verständlich beantwortet.

## Requirements

### Validated

(None yet — ship to validate)

### Active

**Pipeline (Python, uv):**
- [ ] Seitenklassifikation aller PDF-Seiten (Typ, PB, PG, Produkt); Startseiten aller 63 Produkte stimmen mit Anhang A überein
- [ ] Extraktion von Gesamtergebnisplan, Gesamtfinanzplan, Teilergebnis- und Teilfinanzplänen (PB und Produkt) im Langformat, Spalten über x-Koordinaten
- [ ] Produktinformationen (inkl. Bindungsgrad, Grundzahlen, Erläuterungsposten) für alle 63 Produkte
- [ ] Investitionsmaßnahmen (nur aus Produktseiten) und VE-Fälligkeiten
- [ ] Stellenplan (Teil A Beamte, Teil B Tarif, Stellenübersicht nach PB)
- [ ] Manuell gepflegte Vorberichtstabellen (Steuerarten, Zuwendungen, Transferaufwendungen, Kita-Zuschüsse, weitere) und `meta.json`, automatisch gegen Planzeilen geprüft
- [ ] Konsistenzprüfung (Prüfregeln 1–8 aus Spez. 5.5) in pytest und als Markdown-Bericht; bekannte Abweichungen in `befunde.md`
- [ ] Erzeugung der App-JSON-Dateien (ohne Personennamen)
- [ ] Quellenbelege: Zeilenrechteck + gerenderte WebP-Seiten, `quellen.json`
- [ ] Pipeline ist für das ProFIS-Layout generisch: Jahr, Spalten und Seitenbereiche konfigurierbar, sodass der Haushalt 2027 mit wenig Änderung verarbeitet werden kann

**App (Vue 3, TS, Vite, Web Awesome, ECharts):**
- [ ] Start mit Kennzahlenband 2026 und Einstiegen zu den Leitfragen
- [ ] Einnahmen: Ertragsarten → Steuerarten/Zuwendungen → Zeitreihen; investive Einnahmen separat
- [ ] Ausgaben: Treemap mit Drilldown, „Weitergabe an Kreis und Land“ als eigene Kategorie, Umschalter Aufwand/Zuschussbedarf, Sicht nach Aufwandsart, Produktdetail
- [ ] Geldfluss: Sankey 2026 inkl. Defizit- und Minderaufwand-Ausgleich, mobile Alternative
- [ ] Glossar mit allen Begriffen und allen 63 Produkten
- [ ] Entwicklung 2024–2029
- [ ] Investitionen und Schulden (Maßnahmen, VE, Finanzierung, Schuldenstand)
- [ ] Worüber entscheidet der Rat? (Bindungsgrad, nicht beeinflussbare Posten, Einzelzuschüsse)
- [ ] Stellenplan
- [ ] Jahr-Umschalter, „Quelle anzeigen“, Fußzeile mit Datenstand und Hinweis „inoffizielles Projekt“
- [ ] Barrierefreiheit (Lighthouse ≥ 95), Tabellenalternative zu jedem Diagramm, responsiv ab 360 px
- [ ] Deployment über GitHub Actions auf GitHub Pages (eigener Account)

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
| Münster-Code übernehmen | Erlaubnis von Code for Münster liegt vor, spart Aufwand bei Charts und Komponenten | — Pending |
| Einwohnerzahl 11.741 | Im Haushalt selbst begründet (Vorbericht), Stichtag bekannt | — Pending |
| Du-Anrede überall | Einheitlich und nahbar, wird später auch für die Spiele passen | — Pending |
| GitHub Pages, eigener Account | Einfachstes Hosting, Umzug später möglich | — Pending |
| Kämmerei erst nach Fertigstellung informieren | Kein Abstimmungs-Gate; Hinweis „inoffizielles Projekt“ | — Pending |
| Pipeline generisch für ProFIS-Layout | Haushalt 2027 soll mit wenig Änderung verarbeitbar sein | — Pending |
| v1 = Pipeline + Leitfragen + Kontextseiten + Feinschliff; Spiele in v2 | Fokus auf korrekte Kernaussagen; Planspiel-Regeln brauchen fachliche Klärung | — Pending |
| Ergebnisplan als Hauptsicht, Kreisumlage herausgelöst | Fachlich korrekt für eine kreisangehörige Gemeinde (Spez. 3.1, 3.4) | — Pending |
| BBO/TEO nur als Hinweis | Außerhalb des Kernhaushalts; eigene Seite ggf. später | — Pending |
| Paketliste vor Installation menschlich freigegeben (5 PyPI, 21 npm); Minor-/Patch-Drift ok, neue Major-Versionen brauchen erneute Freigabe | Supply-Chain-Schutz vor jeder Installation | ✓ Good — Phase 1 |
| Jahrgangswerte nur in `jahrgaenge/{jahr}.toml` und `{jahr}_sollwerte.toml`, gelesen über `lade_jahrgang`/`lade_sollwerte` mit vollständiger Validierung | Pipeline generisch für spätere Jahrgänge | ✓ Good — Phase 1 |
| Nummerierte Pipeline-Skripte entstehen erst mit ihrer Logik in der jeweiligen Phase; Phase 1 liefert nur `alle.py` | Keine leeren Platzhaltermodule | ✓ Good — Phase 1 |
| ESLint-only (oxlint und vue-devtools aus dem Scaffold entfernt) | Nur freigegebene Pakete | ✓ Good — Phase 1 |
| ECharts-Module nur in `echartsTheme.ts` registriert; Beispieldaten-Hinweis rendert ausschließlich `ChartCard` | Kleines Bundle; Demo-Zahlen können nie ohne Hinweis erscheinen | ✓ Good — Phase 1 |
| CI: zwei parallele Jobs, Actions SHA-gepinnt, `contents: read`, Installation nur aus Lockfiles | Lokal nachgestellte CI = Remote-CI | ✓ Good — Phase 1 (Remote-Lauf steht aus, noch kein GitHub-Remote) |

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
*Last updated: 2026-10-01 after Phase 1*
