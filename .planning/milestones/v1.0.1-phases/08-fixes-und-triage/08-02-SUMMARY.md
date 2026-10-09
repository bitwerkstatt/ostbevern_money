---
phase: 08-fixes-und-triage
plan: 02
subsystem: ui
tags: [vue, vitest, format, geldfluss, minderaufwand, lesehilfe]

requires:
  - phase: 05-ausgaben-und-geldfluss
    provides: Geldfluss-Modell, EuroBetrag, minderaufwandHinweis, Findings 05/WR-01, IN-03, IN-06, IN-07
provides:
  - "charts/format.ts als einzige Stelle der Regel rd./rund (RD_PRAEFIX, RUND_PRAEFIX, betragMitHinweis, kurzMitHinweis, rundMitHinweis, rundKurz)"
  - "lesehilfeSatz in vier Fällen A bis D, genau nur bei echtem Ausgleich"
  - "minderaufwandBetrag in lib/berechnung.ts als gemeinsame Minderaufwand-Regel"
affects: [08-04, 08-05, 08-07]

plan_head_before: 93b0a61fc741d1cbc53e63ca5d16feb2060305e6
plan_head_after: 9f9c3674c2e262955a17d8272ebb25de7fd8919a

actuals:
  tokens: 14000
  tasks: 3
  commits: 5

tech-stack:
  added: []
  patterns:
    - "Regel rd./rund nur in charts/format.ts; Komponenten und Modelle importieren sie"
    - "Fachliche Datenregel als reine Funktion in lib/berechnung.ts, Wurf bei Datenfehler, testbar ohne statischen Datenimport"

key-files:
  created:
    - app/src/components/__tests__/eurobetrag.test.ts
  modified:
    - app/src/charts/format.ts
    - app/src/charts/__tests__/format.test.ts
    - app/src/components/EuroBetrag.vue
    - app/src/lib/geldfluss.ts
    - app/src/lib/__tests__/geldfluss.test.ts
    - app/src/lib/berechnung.ts
    - app/src/lib/__tests__/berechnung.test.ts
    - app/src/lib/aufwandsarten.ts
    - app/src/lib/__tests__/aufwandsarten.test.ts

key-decisions:
  - "geldfluss.ts re-exportiert RD_PRAEFIX und betragMitHinweis nicht; die Tests importieren aus @/charts/format"
  - "Fall C setzt rund nur bei gerundetem Minderaufwand (UI-SPEC Offene Annahme 2), Satz 1 nutzt immer rundKurz mit U+00A0"
  - "Beim Jahr des Minderaufwand-Wurfs liest baueGeldfluss haushalt.jahre[jahrIndex] und wirft bei einem Index außerhalb"

patterns-established:
  - "Tracer: Regel zuerst durchverdrahtet bis EuroBetrag und Sankey-Labels, dann erst Fachtext und Datenregel"

requirements-completed: [TXT-01, TXT-02, TXT-04]

coverage:
  - id: D1
    description: "Die Regel rd./rund steht nur in charts/format.ts; EuroBetrag und Geldfluss (Labels, Tooltips, Satz 1) nutzen sie"
    requirement: TXT-04
    verification:
      - kind: unit
        ref: "app/src/charts/__tests__/format.test.ts#Regel „rd.“ und „rund“ (D-22, TXT-04)"
        status: pass
      - kind: unit
        ref: "app/src/components/__tests__/eurobetrag.test.ts#EuroBetrag"
        status: pass
      - kind: e2e
        ref: "scripts/e2e-wie-ci.sh app (project ci, 81 Tests inkl. smoke.spec.ts)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Die Lesehilfe auf /geldfluss unterscheidet vier Fälle und sagt genau nur bei echtem Ausgleich"
    requirement: TXT-01
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/geldfluss.test.ts#lesehilfeSatz: vier Fälle der Bilanz (D-06, TXT-01, 05/IN-06)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Eine Minderaufwand-Regel für /geldfluss und /ausgaben: nie ein Minuszeichen, 0 ohne Hinweis, Z. 27 > 0 wirft"
    requirement: TXT-02
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/berechnung.test.ts#minderaufwandBetrag (D-08, TXT-02)"
        status: pass
      - kind: unit
        ref: "app/src/lib/__tests__/aufwandsarten.test.ts#minderaufwandHinweis (AUSG-02, Pitfall 6)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Der Kanten-Tooltip-Test prüft für Gemeinde → Kreisumlage positiv den Kantenbetrag (05/IN-03)"
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/geldfluss.test.ts#zeigt Kanten mit „rd.“, wenn der Ertragsknoten gerundet ist, und sonst ohne"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-10-07
status: complete
---

# Phase 8 Plan 02: Regel rd./rund, Lesehilfe in vier Fällen, gemeinsame Minderaufwand-Regel Summary

**Die Regel „rd.“/„rund“ mit U+00A0 steht jetzt nur in charts/format.ts, die Geldfluss-Lesehilfe unterscheidet vier Bilanzfälle (genau nur ohne jeden Ausgleich), und /geldfluss und /ausgaben teilen sich minderaufwandBetrag, die bei Z. 27 > 0 laut wirft.**

## Performance

- **Duration:** 25 min
- **Started:** 2026-10-07T20:00:00Z
- **Completed:** 2026-10-07T20:30:00Z
- **Tasks:** 3 (Tracer, 2 TDD)
- **Files modified:** 10 (9 geändert, 1 neu)

## Accomplishments

- Tracer: `RD_PRAEFIX`, `RUND_PRAEFIX`, `betragMitHinweis`, `kurzMitHinweis`, `rundMitHinweis`, `rundKurz` in `charts/format.ts`; `geldfluss.ts` und `EuroBetrag` hängen daran, `EuroBetrag` hat den neuen Prop `kurz`. Die Kopplung EuroBetrag → geldfluss (06/IN-04) ist gelöst. Smoke-Test über alle Routen grün, bevor die Erweiterung folgte.
- `lesehilfeSatz`: Fall A Defizit (mit „ebenfalls“), B Überschuss (Minderaufwand-Satz ohne „ebenfalls“), C nur Minderaufwand („Die Aufwendungen sind höher als die Erträge. Erst der globale Minderaufwand von … gleicht beide Seiten aus. …“), D „genau“. Der Text `geldfluss_lesehilfe` in `texte.json` bleibt unverändert (D-07).
- `minderaufwandBetrag(zeile27, jahr)` in `lib/berechnung.ts`: fehlend oder 0 ergibt `null`, negativ den positiven Betrag, positiv einen Fehler „Globaler Minderaufwand ist positiv: Datenfehler (Jahr …, Z. 27 = …)“. `baueGeldfluss` und `minderaufwandHinweis` nutzen sie beide.
- Der Kanten-Tooltip-Test (05/IN-03) prüft für Gemeinde → Kreisumlage zusätzlich positiv den Betrag der Kante.

## Task Commits

Commits je Finding:

1. **Task 1 (Tracer): Regel nur in format.ts** — `dde7341` refactor, nennt 05/WR-01 (teilweise) und 05/IN-03
2. **Task 2 (TDD): Lesehilfe vier Fälle** — RED `5e959de` test (3 Tests schlagen fehl: Fall B „ebenfalls“, beide Fall-C-Tests), GREEN `d5f9cdf` fix, nennt 05/IN-06
3. **Task 3 (TDD): Minderaufwand-Regel** — RED `de7fe83` test (Wurf-Test schlägt fehl gegen die Platzhalter-Regel), GREEN `9f9c367` fix, nennt 05/IN-07

**Plan metadata:** folgt als docs-Commit (nur SUMMARY.md, STATE.md und ROADMAP.md gehören dem Orchestrator).

## Files Created/Modified

- `app/src/charts/format.ts` - die Regel rd./rund an einer Stelle
- `app/src/components/EuroBetrag.vue` - importiert aus `@/charts/format`, Prop `kurz`, neuer Doc-Kommentar
- `app/src/components/__tests__/eurobetrag.test.ts` - SSR-Test der Template-Form (neu)
- `app/src/lib/geldfluss.ts` - eigene Kopie der Regel entfernt, Sankey-Label über `kurzMitHinweis`, vier-Fälle-`lesehilfeSatz`, `minderaufwandBetrag`
- `app/src/lib/berechnung.ts` - `minderaufwandBetrag`
- `app/src/lib/aufwandsarten.ts` - `minderaufwandHinweis` über `minderaufwandBetrag`
- Tests: `format.test.ts`, `geldfluss.test.ts`, `berechnung.test.ts`, `aufwandsarten.test.ts`

## Decisions Made

- Kein Re-Export aus `geldfluss.ts` (wie im Plan): die Tests importieren aus `@/charts/format`.
- Das RED von Task 3 nutzt einen Platzhalter mit der alten Regel, damit der Test an der geplanten Zusicherung (Wurf bei positivem Z. 27) scheitert und nicht an einem fehlenden Import.

## Deviations from Plan

None - plan executed exactly as written.

Ergänzend ohne Abweichung: Task 2 und 3 bekamen je einen RED- und einen GREEN-Commit (TDD-Ablauf aus tdd.md), die Plan-Beispiele nennen nur den Fix-Commit. Zusätzlich ein Label-Test im Tracer (Sankey-Label mit „rd.“), der die verdrahtete Änderung in `geldflussOption` absichert.

## Issues Encountered

None

## Verification

- Scratch-Kopie (`npm ci`, Linux): `type-check`, `lint`, `format:check`, voller `vitest`-Lauf (1998 Tests), `build-only` grün.
- `scripts/e2e-wie-ci.sh` (Projekt `ci`): 81 Tests grün, davor Smoke-Test nach dem Tracer: 33 grün.
- `uv run --directory pipeline python alle.py --jahr 2026`: `git status` danach sauber, `daten/`, `app/src/data/` und `app/public/quellen` unverändert.

## User Setup Required

None - no external service configuration required.

## Threat Flags

Keine neue Angriffsfläche. T-08-04 und T-08-05 sind mit konstruierten Tests mitigiert.

## Next Phase Readiness

- Die Autorität für die Regel steht; 08-04 und 08-05 können die übrigen Kopien entfernen, 08-07 den Wächtertest ergänzen.

## Self-Check: PASSED

- app/src/charts/format.ts, app/src/components/__tests__/eurobetrag.test.ts: vorhanden
- Commits dde7341, 5e959de, d5f9cdf, de7fe83, 9f9c367: Vorfahren von HEAD

---
*Phase: 08-fixes-und-triage*
*Completed: 2026-10-07*
