---
phase: 08-fixes-und-triage
plan: 11
subsystem: app-lib
tags: [vue, refactor, vue-router, playwright, coupling]

requires:
  - phase: 08-fixes-und-triage
    provides: "08-05 MassnahmenFilter mit Etikett, 08-06 e2e-Hilfsdateien, 08-07 Testwächter, 08-10 gemeinsame Jahreshelfer"
provides:
  - "app/src/lib/hilfsfunktionen.ts mit quellenZeile, jahreListe, klickIndex (einzige Abhängigkeit charts/format.ts)"
  - "Typ MassnahmenSteuerung und Prop steuerung der Filterzeile; ein useMassnahmenFilter-Aufruf je Seite"
  - "Playwright-Test für den Maßnahmenfilter (gültiger pb, ungültiger pb)"
affects: [08-12]

actuals:
  tokens: 6000
  tasks: 3
  commits: 3
plan_head_before: 913027e620520a13cade22385c0b8669e86021d8
plan_head_after: af2f80bf68bd7bf1206e0c20bf64aa3ba107ac04

tech-stack:
  added: []
  patterns:
    - "Kleine Helfer ohne Datenzugriff liegen in lib/hilfsfunktionen.ts, nicht in Datenmodulen"
    - "Composable mit Router-Zustand wird je Seite einmal erzeugt und per Prop (ReturnType) weitergereicht"

key-files:
  created:
    - app/src/lib/hilfsfunktionen.ts
  modified:
    - app/src/lib/investitionen.ts
    - app/src/lib/schulden.ts
    - app/src/lib/kennzahlen.ts
    - app/src/components/ProduktBalkenListe.vue
    - app/src/components/MassnahmenListe.vue
    - app/src/components/FinanzierungsDiagramm.vue
    - app/src/components/NichtBeeinflussbarBlock.vue
    - app/src/components/MassnahmenFilter.vue
    - app/src/pages/StartPage.vue
    - app/src/pages/InvestitionenPage.vue
    - app/src/lib/__tests__/investitionen.test.ts
    - app/src/lib/__tests__/kennzahlen.test.ts
    - app/src/lib/__tests__/schulden.test.ts
    - app/e2e/interaktion.spec.ts

key-decisions:
  - "Modulname hilfsfunktionen.ts (D-13 ließ ihn offen)"
  - "MassnahmenSteuerung als ReturnType des Composables, damit die Filterzeile das Composable nicht importieren muss"

requirements-completed: [TRI-04]

coverage:
  - id: D1
    description: "quellenZeile, jahreListe und klickIndex liegen in lib/hilfsfunktionen.ts; ProduktBalkenListe und FinanzierungsDiagramm ziehen kein investitionen/schulden/vue-router mehr (06/IN-04)"
    requirement: TRI-04
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/kennzahlen.test.ts#quellenZeile"
        status: pass
      - kind: unit
        ref: "app/src/lib/__tests__/schulden.test.ts#jahreListe"
        status: pass
      - kind: unit
        ref: "app/src/lib/__tests__/investitionen.test.ts#klickIndex"
        status: pass
      - kind: other
        ref: "npm run type-check, lint, format:check, vitest (2153 Tests)"
        status: pass
    human_judgment: false
  - id: D2
    description: "useMassnahmenFilter läuft je Seite einmal; MassnahmenFilter.vue bekommt den Zustand als Prop steuerung (06/IN-05)"
    requirement: TRI-04
    verification:
      - kind: e2e
        ref: "app/e2e/interaktion.spec.ts#Maßnahmenfilter auf /investitionen"
        status: pass
      - kind: unit
        ref: "app/src/lib/__tests__/investitionen.test.ts#useMassnahmenFilter (D-06, Router-Zustand)"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-10-07
status: complete
---

# Phase 8 Plan 11: Hilfsfunktionen-Modul und einmaliger Maßnahmenfilter Summary

**Neues Modul lib/hilfsfunktionen.ts (quellenZeile, jahreListe, klickIndex ohne Datenzugriff) und ein einziger useMassnahmenFilter-Aufruf je Seite, den die Filterzeile als Prop steuerung erhält**

## Performance

- **Duration:** 25 min
- **Tasks:** 3
- **Files modified:** 15 (1 neu)

## Accomplishments
- 06/IN-04: Die drei kleinen Helfer wohnen in einem Modul, das nur `charts/format.ts` importiert. `/rat-entscheidet` lädt über `ProduktBalkenListe.vue` nicht mehr `lib/investitionen` samt vue-router, `FinanzierungsDiagramm.vue` nicht mehr `lib/schulden`. `kennzahlen.ts`, `schulden.ts` und `investitionen.ts` exportieren sie nicht mehr.
- 06/IN-05: `InvestitionenPage.vue` ruft `useMassnahmenFilter()` einmal auf; `MassnahmenFilter.vue` hat die Prop `steuerung: MassnahmenSteuerung` und kennt das Composable nicht mehr. Damit gibt es nur noch einen URL-Watcher und eine Berechnung.
- Neuer Playwright-Test: gültiger `pb` (Code aus den Optionen der Auswahl) verringert die Zahl in der Ergebniszeile, `?pb=zz` verschwindet aus der URL (T-08-18).
- Keine Zahl und kein Text geändert: vitest 2153 Tests grün, Playwright `ci` 87 grün (86 + 1 neu), `mobil` 39 grün, `alle.py --jahr 2026` lässt `daten/`, `app/src/data/` und `app/public/quellen` unverändert.

## Task Commits

1. **Task 1: klickIndex und jahreListe (06/IN-04)** - `487df23` (refactor)
2. **Task 2: quellenZeile (06/IN-04)** - `31d0334` (refactor)
3. **Task 3: Maßnahmenfilter einmal je Seite (06/IN-05)** - `af2f80b` (refactor)

## Decisions Made
- Modulname `hilfsfunktionen.ts` wie vom Plan vorgeschlagen.
- Der Playwright-Test wählt den ersten Aufgabenbereich aus den `wa-option`-Werten der Auswahl; er setzt voraus, dass mindestens zwei Aufgabenbereiche Maßnahmen haben (sonst schlägt er laut fehl).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] MassnahmenListe.vue importierte klickIndex aus lib/investitionen**
- **Found during:** Task 1
- **Issue:** `components/MassnahmenListe.vue` stand nicht in der Importeurliste des Plans, importierte aber `klickIndex` aus `@/lib/investitionen`; nach dem Verschieben wäre der Build gebrochen.
- **Fix:** Import auf `@/lib/hilfsfunktionen` umgestellt.
- **Files modified:** app/src/components/MassnahmenListe.vue
- **Verification:** type-check, lint, vitest, Playwright grün
- **Committed in:** 487df23

**2. [Rule 3 - Blocking] schulden.test.ts importierte jahreListe aus lib/schulden**
- **Found during:** Task 1
- **Issue:** Der Test stand erst in Task 2, brauchte aber den neuen Importpfad schon nach Task 1.
- **Fix:** `jahreListe`-Import in Task 1 umgestellt, `quellenZeile` folgte in Task 2.
- **Files modified:** app/src/lib/__tests__/schulden.test.ts
- **Committed in:** 487df23

---

**Total deviations:** 2 auto-fixed (2 blocking)
**Impact on plan:** Reine Importpfade, kein Umfang darüber hinaus.

## Issues Encountered
Keine. Der Plan-Verify hätte je Task eine neue Scratch-Kopie mit `npm ci` angelegt; stattdessen wurde eine Scratch-Kopie wiederverwendet und per `rsync` aktualisiert (gleiche Prüfungen).

## Known Stubs
None.

## Threat Flags
None. Die Allowlist-Auswertung in `leseMassnahmenFilter` blieb unverändert (T-08-18), der Playwright-Test belegt die URL-Bereinigung.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
Letzter Code-Plan der Phase; 08-12 (Dispositionen) kann 06/IN-04 und 06/IN-05 als behoben mit den Commits 487df23, 31d0334 und af2f80b eintragen.

## Self-Check: PASSED

- `app/src/lib/hilfsfunktionen.ts` vorhanden
- Commits 487df23, 31d0334, af2f80b liegen auf HEAD

---
*Phase: 08-fixes-und-triage*
*Completed: 2026-10-07*
