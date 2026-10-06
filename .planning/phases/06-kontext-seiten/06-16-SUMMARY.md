---
phase: 06-kontext-seiten
plan: 16
subsystem: ui
tags: [vue, typescript, vitest, schulden, stellenplan, gap-closure]

requires:
  - phase: 06-kontext-seiten
    provides: "Investitionen/Schulden-Seite (06-09) und Stellenplan-Seite (06-11) mit schulden.ts und stellen.ts"
provides:
  - "schuldenKacheln() und SchuldenKachel: beide Schuldenkacheln mit datengetriebenem berechnet-Flag (WR-03)"
  - "nachwuchs() ohne erfundene 0: ein Jahr mit fehlender Personenzahl ist null (WR-05)"
affects: [06-kontext-seiten, verification]

actuals:
  tokens: 9000
  tasks: 2
  commits: 4

tech-stack:
  added: []
  patterns:
    - "Kachel-Datensaetze entstehen in lib/, die Seite rendert sie nur (Quelltexttest sichert das)"
    - "Fehlender Einzelwert macht die Summe null statt sie still zu verkleinern"

key-files:
  created: []
  modified:
    - app/src/lib/schulden.ts
    - app/src/lib/__tests__/schulden.test.ts
    - app/src/pages/InvestitionenPage.vue
    - app/src/lib/stellen.ts
    - app/src/lib/__tests__/stellen.test.ts

key-decisions:
  - "Beide Schuldenkacheln folgen schuldenstand.berechnet des Vorjahrs; kein neues Datenfeld"
  - "WR-05 wird mit null statt mit einem Wurf geloest, weil StellenplanPage ein Jahr ohne Wert bereits auslaesst (UI-SPEC E10 partial)"

patterns-established:
  - "Quelltexttest per ?raw: InvestitionenPage enthaelt schuldenKacheln() und baut die Kacheln nicht selbst"

requirements-completed: [INV-04, STEL-01, STEL-02]

duration: 6min
completed: 2026-10-06
status: complete
plan_head_before: 8878f321a08314d99cc6781fd257d9afb061c958
plan_head_after: 6c0427cbaa39da6231c4dc9bfa64f1e4dba92226
---

# Phase 6 Plan 16: Ehrliche Datenflags (WR-03, WR-05) Summary

**schuldenKacheln() baut beide Schuldenkacheln mit dem berechnet-Flag aus schuldenstand.berechnet des Vorjahrs, und nachwuchs() liefert null statt einer erfundenen 0 bei fehlender Personenzahl.**

## Performance

- **Duration:** 6 min
- **Started:** 2026-10-06T07:58:00Z
- **Completed:** 2026-10-06T08:04:00Z
- **Tasks:** 2
- **Files modified:** 5

## Accomplishments
- WR-03 geschlossen: Die Kachel "Schuldenstand Ende {Vorjahr}" hat kein hartcodiertes `false` mehr. `schuldenKacheln()` in `lib/schulden.ts` setzt bei beiden Kacheln dasselbe, aus den Daten gelesene Flag. Die Seite rendert nur noch `[...schuldenKacheln(), VE-Kachel]`.
- WR-05 geschlossen: `personen()` in `lib/stellen.ts` liefert `null`, sobald eine Zeile keine Personenzahl hat. Die Seite nennt dann nur das andere Jahr (bestehender Zweig in `nachwuchsSatz`).
- Jahrgang 2026 unveraendert: 7,71 Mio. EUR und 656 EUR ohne "berechnet" (S. 310, S. 25), Nachwuchs 5 und 6 Personen (S. 290).

## Task Commits

1. **Task 1: Tracer WR-03 (schuldenKacheln)**
   - RED `d7a67af` (test): Stub plus 7 fehlschlagende Assertions
   - GREEN `4e5ae02` (fix): Implementierung und Umbau der Seite
2. **Task 2: WR-05 (Nachwuchs ohne erfundene 0)**
   - RED `be25b65` (test): zwei Null-Zeilen-Faelle
   - GREEN `6c0427c` (fix): `personen()` liefert null

**Plan metadata:** folgt im docs-Commit (SUMMARY).

## Files Created/Modified
- `app/src/lib/schulden.ts` - `SchuldenKachel`, `schuldenKacheln()`, erweiterter Kopfkommentar
- `app/src/lib/__tests__/schulden.test.ts` - describe "schuldenKacheln (WR-03, D-09, D-10)", Jahrgang-2026-Pin, Quelltexttest der Seite
- `app/src/pages/InvestitionenPage.vue` - Kachelliste aus `schuldenKacheln()`, ungenutzte Imports entfernt
- `app/src/lib/stellen.ts` - `personen()` ohne Rueckfall auf 0, Doc-Kommentare von `Nachwuchs`
- `app/src/lib/__tests__/stellen.test.ts` - WR-05-Faelle fuer beide Jahre, Erwartung ohne `?? 0`

## Decisions Made
- Beide Kacheln nutzen das vorhandene Vorjahr-Flag (kein neues Datenfeld).
- null statt Fehler bei fehlender Personenzahl: ein Wurf wuerde die ganze Stellenplan-Seite fuer eine fehlende Zelle blockieren; die gepinnten 2026-Werte machen einen Datenfehler im Test sichtbar.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
- Die automatische Verify-Zeile der Plaene nutzt `npm ci`; ohne Netz nicht moeglich. Die Checks liefen wie in den Plaenen 06-02 bis 06-12 in einem Scratch-Copy von `app/` mit symlinkter Linux-`node_modules` (identische Lockfile). Ergebnis: gesamte Vitest-Suite 1402 Tests gruen, type-check, lint, format:check und build gruen.

## TDD Gate Compliance

Beide Tasks mit RED (`test(06-16)`) vor GREEN (`fix(06-16)`). RED schlug jeweils an den Ziel-Assertions fehl (schuldenKacheln: leeres Array; nachwuchs: 0-Summe statt null), nicht an Syntax- oder Ladefehlern.

## Known Stubs

None. Der RED-Stub von `schuldenKacheln()` wurde im GREEN-Commit durch die Implementierung ersetzt.

## Threat Flags

None. T-06-36 und T-06-37 sind durch Tests mitigiert, es kam keine neue Angriffsflaeche hinzu.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- WR-03 und WR-05 sind geschlossen; die uebrigen Gap-Closure-Plaene (06-13 bis 06-15, 06-17) beruehren disjunkte Dateien.

## Self-Check: PASSED

- Dateien vorhanden: schulden.ts, stellen.ts, beide Testdateien, InvestitionenPage.vue
- Commits vorhanden: d7a67af, 4e5ae02, be25b65, 6c0427c
- Akzeptanzkriterien beider Tasks erfuellt (grep-Pruefungen und Tests)

---
*Phase: 06-kontext-seiten*
*Completed: 2026-10-06*
