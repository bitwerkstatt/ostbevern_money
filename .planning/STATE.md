---
gsd_state_version: "1.0"
current_phase: 6
current_phase_name: Kontext-Seiten
status: planning
stopped_at: Phase 6 context gathered
last_updated: "2026-10-05T18:37:30.560Z"
last_activity: 2026-10-05
last_activity_desc: Phase 05 complete, transitioned to Phase 6
state_head: 4e74ecc4214a9a798c870efb9b5b458035fee1d4
progress:
  total_phases: 7
  completed_phases: 5
  total_plans: 37
  completed_plans: 37
  percent: 71
---

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-10-05)

**Core value:** Jede Zahl in der App ist korrekt aus dem Haushalts-PDF abgeleitet und durch automatische Prüfungen belegt. Die Leitfragen „Woher?“ und „Wofür?“ sind für Laien verständlich beantwortet.
**Current focus:** Phase 6 — Kontext-Seiten

## Current Position

Phase: 6 — Kontext-Seiten
Plan: Not started
Status: Ready to plan
Last activity: 2026-10-05 — Phase 05 complete, transitioned to Phase 6

Progress: [███████░░░] 71%

## Performance Metrics

**Velocity:**
- Total plans completed: 37
- Average duration: -
- Total execution time: 0.0 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1 | 5 | - | - |
| 2 | 5 | - | - |
| 03 | 5 | - | - |
| 04 | 6 | - | - |
| 05 | 16 | - | - |

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

- [Phase 4]: Prüfregeln 1–10 grün; Vorberichtswerte, `meta.json`, Schuldenstand/Rücklagen/VE mit Quelle; Stellenplan (Beamte 2026 = 8); App-JSON reproduzierbar über `alle.py` ohne Personennamen (472 Tests).
- [Phase 4]: Erklärtexte: Platzhalter `{{schluessel|kuerzel}}`, Jahreszahlen mit Kürzel `jahr` (CR-01 behoben in 04-06); `test_formatiere.py` rendert jede Zahl über eine `formatiere()`-Portierung mit Node-Gegenprobe.
- [Phase 5]: Leitfragen-Seiten Start, Einnahmen, Ausgaben (inkl. Produktseite), Geldfluss und Glossar fertig; vitest 5.0.3 als Testframework (1031 Tests), Zahlen nur aus Daten (Quelltext-Scan), kein `v-html`, Tooltips über `htmlSicher`/`tooltipZeilen`.
- [Phase 5]: Hash-Sprungziele berücksichtigen den sticky Header (`sprungziel.ts`); `stiltokens.test.ts` verbietet undefinierte `--wa-*`-Tokens (Lücken G-05-4/G-05-6, Plan 05-16).
- [Phase 5]: Fußzeilen-Kontakt und PDF-Link bleiben `.invalid`-Platzhalter bis Phase 7 (D-17).

### Pending Todos

None yet.

### Blockers/Concerns

- [Phase 1]: Die CI ist nur lokal nachgestellt; der erste Lauf auf GitHub steht aus, bis ein Remote angelegt ist.
- [Phase 1]: `app/node_modules` im gemounteten Repo enthält macOS-Binaries; im Linux-Sandbox App-Checks in einer Scratch-Kopie ausführen.
- [Phase 2]: Code-Review 02-REVIEW.md: 3 Warnungen offen (u. a. Vorzeichen-Beschreibung in `befunde.md`, Kommentar zu PB 09/15 sollte S. 296/299 zitieren).
- [Phase 4]: Code-Review 04-REVIEW-DISPOSITION.md: Befunde WR-01…WR-05, IN-02 offen, alle ohne Auswirkung auf die heutigen Daten (Nutzerentscheidung 2026-10-03). WR-06/IN-01 (`formatiere()`-Fallback) in Plan 05-01 behoben.
- [Phase 4]: `/gsd-secure-phase 04` steht aus (Sicherheitsprüfung aktiviert, noch kein 04-SECURITY.md).
- [Phase 5]: UI-Review 05-UI-REVIEW.md (16/24): Token-Hygiene offen — `font-weight: 600` fest in App.vue, `--wa-font-weight-semibold`, `--wa-font-size-xl`, `--wa-space-3xs`/`2xl` außerhalb der UI-SPEC-Skala; kosmetisch, vor/in Phase 7 bereinigen.

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

Last session: 2026-10-05T18:37:30.497Z
Stopped at: Phase 6 context gathered
Resume file: .planning/phases/06-kontext-seiten/06-CONTEXT.md
