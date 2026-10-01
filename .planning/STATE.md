---
gsd_state_version: "1.0"
current_phase: 2
current_phase_name: Kernzahlen
status: planning
stopped_at: Phase 1 complete, ready to plan Phase 2
last_updated: "2026-10-01T10:51:21.105Z"
last_activity: 2026-10-01
last_activity_desc: Phase 1 complete, transitioned to Phase 2
state_head: c305a983ea31f7e143799da191dda509340194d5
progress:
  total_phases: 7
  completed_phases: 1
  total_plans: 5
  completed_plans: 5
  percent: 14
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-10-01)

**Core value:** Jede Zahl in der App ist korrekt aus dem Haushalts-PDF abgeleitet und durch automatische Prüfungen belegt. Die Leitfragen „Woher?“ und „Wofür?“ sind für Laien verständlich beantwortet.
**Current focus:** Phase 2 — Kernzahlen

## Current Position

Phase: 2 — Kernzahlen
Plan: Not started
Status: Ready to plan
Last activity: 2026-10-01 — Phase 1 complete, transitioned to Phase 2

Progress: [█░░░░░░░░░] 14%

## Performance Metrics

**Velocity:**
- Total plans completed: 5
- Average duration: -
- Total execution time: 0.0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1 | 5 | - | - |

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

### Pending Todos

None yet.

### Blockers/Concerns

- [Phase 4]: Für Schuldenstand, Rücklagen und VE-Übersicht (S. 24/25, 309–311) gibt es keine eigene Datenanforderung. Das ist als Erfolgskriterium in Phase 4 aufgefangen. Bei Bedarf wird daraus eine eigene Anforderung (z. B. MANU-09).
- [Phase 1]: Die CI ist nur lokal nachgestellt; der erste Lauf auf GitHub steht aus, bis ein Remote angelegt ist.
- [Phase 1]: `app/node_modules` im gemounteten Repo enthält macOS-Binaries; im Linux-Sandbox App-Checks in einer Scratch-Kopie ausführen.
- [Phase 2/4]: Die Anhang-B-Eckwerte (B.6), die von `meta.json` oder vom Stellenplan abhängen, lassen sich erst in Phase 4 prüfen. Phase 2 deckt B.1–B.3 und Satzung § 1 ab.

## Deferred Items

Items acknowledged and deferred at milestone close, most recent first:

| Category | Item | Status | Deferred At | Milestone |
|----------|------|--------|-------------|-----------|
| *(none)* | | | | |

## Session Continuity

Last session: 2026-10-01T13:30:00Z
Stopped at: Phase 1 complete, ready to plan Phase 2
Resume file: None
