---
gsd_state_version: "1.0"
current_phase: 4
current_phase_name: Manuelle Daten und App-Daten
status: planning
stopped_at: Phase 03 complete, ready to plan Phase 4
last_updated: "2026-10-02T11:53:41.999Z"
last_activity: 2026-10-02
last_activity_desc: Phase 03 complete, transitioned to Phase 4
state_head: 87f05805f29d5ece9131ce1d76bcd025b829849c
progress:
  total_phases: 7
  completed_phases: 3
  total_plans: 15
  completed_plans: 15
  percent: 43
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-10-02)

**Core value:** Jede Zahl in der App ist korrekt aus dem Haushalts-PDF abgeleitet und durch automatische Prüfungen belegt. Die Leitfragen „Woher?“ und „Wofür?“ sind für Laien verständlich beantwortet.
**Current focus:** Phase 4 — Manuelle Daten und App-Daten

## Current Position

Phase: 4 — Manuelle Daten und App-Daten
Plan: Not started
Status: Ready to plan
Last activity: 2026-10-02 — Phase 03 complete, transitioned to Phase 4

Progress: [████░░░░░░] 43%

## Performance Metrics

**Velocity:**
- Total plans completed: 15
- Average duration: -
- Total execution time: 0.0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1 | 5 | - | - |
| 2 | 5 | - | - |
| 03 | 5 | - | - |

**Recent Trend:**
- Last 5 plans: -
- Trend: -

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- [Roadmap]: Die Phasen folgen dem Spez.-Phasenplan in horizontalen Schichten (P0–P5, P7). Spiele (P6) sind v2.
- [Roadmap]: Die Teilfinanzpläne werden schon in Phase 2 extrahiert (gleicher Parser, Prüfregel 1 gilt für alle Pläne).
- [Roadmap]: Die App-JSON-Erzeugung und `alle.py` mit CI-Diff-Prüfung schließen die Pipeline in Phase 4 ab.
- [Roadmap]: Die CI (vue-tsc, ESLint, pytest) läuft ab Phase 1. Das Deployment auf GitHub Pages folgt erst in Phase 7.
- [Phase 1]: Jahrgangs- und Sollwertdatei sind vollständig und validiert; Phase 2 liest Seitenbereiche und Spaltenköpfe ausschließlich über `lade_jahrgang`.
- [Phase 1]: Nummerierte Pipeline-Skripte (01/02/06) entstehen erst in Phase 2 mit ihrer Logik.
- [Phase 1]: DatenTabelle zeigt `null`-Zellen leer mit „kein Wert“ für Screenreader — vorläufig, bis Phase 2+ weiß, welche Werte fehlen können.
- [Phase 2]: `alle.py` verkettet Schritt 01 → 02 → 06; Prüfregeln 1–4 grün (6550/7920/114/194 Werte), Regeneration von `daten/` ist deterministisch.
- [Quick 261001-oim]: Synthetische PG haben genau ein Produkt (D-14, sonst Fehler). PG 1502 „Tourismus“ (nur 150102) ist als Ausnahme in `jahrgaenge/2026.toml` deklariert, Werte gegen Querschnitt S. 299 geprüft.
- [Phase 2]: Anhang-B.3-Sollwerte PB 09/15 Z. 29 nach PDF-Prüfung (S. 296/299 GESAMTSUMME) korrigiert; 10 gedruckte Rundungsdifferenzen in `befunde.md` belegt.
- [Phase 3]: Schritte 03/04 und die Querschnitte laufen in `alle.py`; Regeln 1–4 und 6–8 grün (Regel 6: 1964, Regel 7: 1152, Regel 8: 820 Werte), 0 Lücken; 26 neue PDF-belegte Befunde (Regel 6: 8, Regel 7: 18).
- [Phase 3]: `produkte.json` (63 Produkte) ohne Personennamen, dreifach abgesichert; `grundzahlen.csv` 827 Zeilen/48 Produkte, `erlaeuterungen.csv` 229 Zeilen/50 Produkte (Sollwert von 51 auf 50 korrigiert, S. 120101 druckt leere Kopfzeile).

### Pending Todos

None yet.

### Blockers/Concerns

- [Phase 4]: Für Schuldenstand, Rücklagen und VE-Übersicht (S. 24/25, 309–311) gibt es keine eigene Datenanforderung. Das ist als Erfolgskriterium in Phase 4 aufgefangen. Bei Bedarf wird daraus eine eigene Anforderung (z. B. MANU-09).
- [Phase 1]: Die CI ist nur lokal nachgestellt; der erste Lauf auf GitHub steht aus, bis ein Remote angelegt ist.
- [Phase 1]: `app/node_modules` im gemounteten Repo enthält macOS-Binaries; im Linux-Sandbox App-Checks in einer Scratch-Kopie ausführen.
- [Phase 2]: Code-Review 02-REVIEW.md: 3 Warnungen offen (u. a. Vorzeichen-Beschreibung in `befunde.md`, Kommentar zu PB 09/15 sollte S. 296/299 zitieren).
- [Phase 2/4]: Die Anhang-B-Eckwerte (B.6), die von `meta.json` oder vom Stellenplan abhängen, lassen sich erst in Phase 4 prüfen. Phase 2 deckt B.1–B.3 und Satzung § 1 ab.

### Quick Tasks Completed

| # | Description | Date | Commit | Directory |
|---|-------------|------|--------|-----------|
| 261001-oim | Synthetische PG nach D-14: genau ein Produkt je PG, PG 1502 Tourismus | 2026-10-01 | 699eb9b | [261001-oim-synthetische-pg-nach-d-14-150102-in-eige](./quick/261001-oim-synthetische-pg-nach-d-14-150102-in-eige/) |

## Deferred Items

Items acknowledged and deferred at milestone close, most recent first:

| Category | Item | Status | Deferred At | Milestone |
|----------|------|--------|-------------|-----------|
| *(none)* | | | | |

## Session Continuity

Last session: 2026-10-02T08:00:00Z
Stopped at: Phase 03 complete, ready to plan Phase 4
Resume file: None
