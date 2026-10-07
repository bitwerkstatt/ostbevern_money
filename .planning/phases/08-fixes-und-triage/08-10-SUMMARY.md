---
phase: 08-fixes-und-triage
plan: 10
subsystem: app-lib
tags: [vue, typescript, refactoring, deduplication, vitest]

requires:
  - phase: 08-fixes-und-triage
    provides: "08-03 (kennzahlen.ts, StellenplanPage.vue) und 08-05 (zuschuesse.ts) als letzte Bearbeiter der hier erneut geaenderten Dateien"
provides:
  - "lib/jahr.ts: haushaltsjahrIndex() und wertartAn(index) als einzige Index-/Wertart-Helfer"
  - "lib/ruecklagen.ts: postenEintrag(tabelle, schluessel) als einzige Posten-Suche"
  - "Stellenplan-Seite nutzt anzahlText fuer Personenzahlen"
affects: [08-12 Dispositionen, 08-07 Tests der lib-Module]

actuals:
  tokens: 6500
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Ein gemeinsamer Helfer 'Index suchen, sonst werfen' in lib/jahr.ts statt privater Kopien"

key-files:
  created: []
  modified:
    - app/src/lib/jahr.ts
    - app/src/lib/__tests__/jahr.test.ts
    - app/src/lib/ruecklagen.ts
    - app/src/lib/investitionen.ts
    - app/src/lib/entwicklung.ts
    - app/src/lib/zuschuesse.ts
    - app/src/lib/kennzahlen.ts
    - app/src/lib/bindungsgrad.ts
    - app/src/pages/StellenplanPage.vue

key-decisions:
  - "06/IN-02: ausgleichsruecklageAufgebrauchtJahr nutzt haushaltsjahrIndex() statt ungeprueftem indexOf (umgestellt, nicht entfernt); menueLinks bleibt"
  - "06/WR-01 (D-17): Vorzeichen-Kommentar zu abbau() in ruecklagen.ts umgeschrieben; Code und Fussnotentext unveraendert"

patterns-established:
  - "Gemeinsame Jahres-Helfer liegen in lib/jahr.ts; lib/stellen.ts behaelt seine eigene Variante (anderer Input)"

requirements-completed: [TRI-04]

plan_head_before: d7e46f410d0503f7ae5b21d85919376c55857325
plan_head_after: 507d7872e2078c3f68d51de32290a612ec7268f8

coverage:
  - id: D1
    description: "haushaltsjahrIndex() und wertartAn() in lib/jahr.ts; private Kopien in zuschuesse, kennzahlen, bindungsgrad, ruecklagen, investitionen (planAb) und entwicklung entfernt (06/IN-03)"
    requirement: TRI-04
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/jahr.test.ts#haushaltsjahrIndex / wertartAn"
        status: pass
      - kind: unit
        ref: "npm run test (47 Dateien, 2022 Tests)"
        status: pass
    human_judgment: false
  - id: D2
    description: "ausgleichsruecklageAufgebrauchtJahr nutzt den gepruefte Index (06/IN-02); Tests und Zwillingsregel bleiben gruen"
    requirement: TRI-04
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/ruecklagen.test.ts"
        status: pass
    human_judgment: false
  - id: D3
    description: "postenEintrag() ersetzt postenWerte/postenName-Suche; personenText durch anzahlText ersetzt (06/IN-03)"
    requirement: TRI-04
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/ruecklagen.test.ts, stellen.test.ts"
        status: pass
      - kind: e2e
        ref: "scripts/e2e-wie-ci.sh e2e/smoke.spec.ts (33 passed)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Kommentar zum Abbau der allgemeinen Ruecklage nennt das Vorzeichen der Verrechnung eindeutig (06/WR-01, D-17)"
    requirement: TRI-04
    verification: []
    human_judgment: true
    rationale: "Verstaendlichkeit eines Code-Kommentars laesst sich nicht automatisch pruefen"

duration: 8min
completed: 2026-10-07
status: complete
---

# Phase 8 Plan 10: Gemeinsame Jahr-Helfer Summary

**Fuenf Varianten von "Index des Haushaltsjahrs suchen, sonst werfen" und zwei `wertartAn`-Kopien durch `haushaltsjahrIndex()`/`wertartAn()` in `lib/jahr.ts` ersetzt, dazu `postenEintrag()` und `anzahlText` — reine Deduplizierung, alle Zahlen und generierten Daten byte-identisch.**

## Performance

- **Duration:** ca. 8 min
- **Started:** 2026-10-07T18:50Z
- **Completed:** 2026-10-07T18:57Z
- **Tasks:** 3
- **Files modified:** 9

## Accomplishments

- `lib/jahr.ts` exportiert `haushaltsjahrIndex()` (wirft „Haushaltsjahr {Jahr} steht nicht in haushalt.jahre") und `wertartAn(index)`; `jahr.test.ts` testet beide.
- Entfernt: `jahrIndex` in zuschuesse/kennzahlen/bindungsgrad, `haushaltsjahrIndex` und `wertartAn` in ruecklagen, `planAb` in investitionen, `wertartAn` in entwicklung.
- `ausgleichsruecklageAufgebrauchtJahr` startet jetzt bei `haushaltsjahrIndex()` statt bei einem ungeprueften `indexOf` (-1 ist nicht mehr moeglich).
- `postenEintrag(tabelle, schluessel)` ersetzt die doppelte Suche samt Fehlermeldung in `postenWerte` und `postenName`.
- `personenText` in `StellenplanPage.vue` durch `anzahlText(anzahl, 'Person', 'Personen')` ersetzt; der Text fuer 2026 ist unveraendert.
- Der Kommentar zu `abbau()` erklaert: Verrechnung ist im Druck negativ gebucht, die Formel zieht sie ab, der Abbau steigt um ihren Betrag; „zuzueglich" meint Betraege (D-17).

## Task Commits

| Task | Finding-IDs | Commit |
|------|-------------|--------|
| 1: haushaltsjahrIndex und wertartAn in lib/jahr.ts, erste Kopien ersetzt | 06/IN-03, 06/IN-02 | `656c73e` (refactor) |
| 2: uebrige jahrIndex-Kopien ersetzt | 06/IN-03 | `fad1da9` (refactor) |
| 3: postenEintrag, anzahlText, Vorzeichen-Kommentar | 06/IN-03, 06/WR-01 | `507d787` (refactor) |

**Plan metadata:** folgt als `docs(08-10)`-Commit mit dieser Datei.

## Files Created/Modified

- `app/src/lib/jahr.ts` - neue Exporte `haushaltsjahrIndex`, `wertartAn`
- `app/src/lib/__tests__/jahr.test.ts` - Tests fuer beide Helfer
- `app/src/lib/ruecklagen.ts` - Helfer importiert, `postenEintrag`, Kommentar, gepruefter Start in `ausgleichsruecklageAufgebrauchtJahr`
- `app/src/lib/investitionen.ts`, `entwicklung.ts`, `zuschuesse.ts`, `kennzahlen.ts`, `bindungsgrad.ts` - private Kopien entfernt
- `app/src/pages/StellenplanPage.vue` - `anzahlText` statt `personenText`

## Decisions Made

- 06/IN-02: umgestellt statt entfernt (Plan-Entscheidung), weil die Funktion die Python-Zwillingsregel spiegelt und Tests hat; `menueLinks` bleibt.
- Der 06/WR-01-Kommentar steht im selben Commit wie `postenEintrag` (beide aendern `ruecklagen.ts`), nicht in einem eigenen `docs`-Commit wie im Plan vorgeschlagen; die Finding-ID steht im Commit-Text.

## Deviations from Plan

None - plan executed exactly as written (einzige Abweichung: Zusammenlegung des Kommentar-Commits mit Task 3, siehe Decisions Made).

## Issues Encountered

- Prettier meldete nach Task 1 einen umgebrochenen `throw` in `jahr.ts`; auf eine Zeile gebracht, danach `format:check` gruen.

## Verification

- Scratch-Kopie: `npm run test` 47 Dateien / 2022 Tests gruen, `type-check`, `lint`, `format:check`, `build-only` gruen.
- `scripts/e2e-wie-ci.sh <scratch>/app e2e/smoke.spec.ts`: 33 passed.
- `uv run --directory pipeline python alle.py --jahr 2026`: danach `git status --short` leer (daten/, app/src/data, app/public/quellen byte-identisch).
- Acceptance-Greps: keine privaten `planAb`/`haushaltsjahrIndex`/`wertartAn`/`jahrIndex`-Funktionen mehr in den lib-Modulen; `indexOf(haushalt.haushaltsjahr)` in ruecklagen.ts: 0.

## Known Stubs

None.

## Threat Flags

None.

## Notes for other plans

- Keine Test-Datei ausserhalb von `jahr.test.ts` musste angefasst werden; alle bisherigen Exporte (`abbau`, `rueckgang`, `ausgleichsruecklageAufgebrauchtJahr`, ...) behalten Namen und Signatur.
- Die Fehlermeldung in `ruecklagen.ts` (vorher „haushalt.haushaltsjahr steht nicht in haushalt.jahre") und `investitionen.ts` (vorher „haushaltsjahr steht nicht ...") lautet jetzt einheitlich „Haushaltsjahr {Jahr} steht nicht in haushalt.jahre"; kein Test pruefte die alten Texte.

## Self-Check: PASSED

- `app/src/lib/jahr.ts`, `app/src/lib/__tests__/jahr.test.ts`: vorhanden.
- Commits `656c73e`, `fad1da9`, `507d787`: auf HEAD erreichbar.

---
*Phase: 08-fixes-und-triage*
*Completed: 2026-10-07*
