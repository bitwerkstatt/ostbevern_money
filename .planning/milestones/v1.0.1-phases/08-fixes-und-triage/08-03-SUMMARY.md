---
phase: 08-fixes-und-triage
plan: 03
subsystem: ui
tags: [vue, typescript, vitest, stellenplan, einwohner, quellenangaben]

requires:
  - phase: 07-quellen-und-belege
    provides: KennzahlKachel mit berechnet/herleitung, Belegschluessel, Quellenleiste
provides:
  - Seiten je Stellenplan-Kachel (seitenHaushaltsjahr, seitenVorjahr, seitenBesetzt) in stellenSummen()
  - nachwuchs() mit Seiten nur der Jahre mit Personenzahl
  - alle drei Stellenplan-Kacheln mit Etikett berechnet und Herleitung
  - lib/einwohner.ts mit der einzigen Einwohnerzahl-Pruefung einwohnerZahl()
affects: [08-04, 08-05, 08-10]

actuals:
  tokens: 14000
  tasks: 2
  commits: 4

tech-stack:
  added: []
  patterns:
    - "Eine gemeinsame, laut werfende Pruefung fuer Metadaten (einwohnerZahl) statt privater Kopien"
    - "Seiten je Kachel aus den eigenen Zeilen, Belegschluessel bleibt auf der Vereinigung"

key-files:
  created:
    - app/src/lib/einwohner.ts
    - app/src/lib/__tests__/einwohner.test.ts
  modified:
    - app/src/lib/stellen.ts
    - app/src/lib/__tests__/stellen.test.ts
    - app/src/pages/StellenplanPage.vue
    - app/src/lib/kennzahlen.ts
    - app/src/lib/produkt.ts
    - app/src/components/EbenenTabelle.vue
    - app/e2e/quelle.spec.ts

key-decisions:
  - "einwohnerZahl nimmt ein Rest-Argument [wert?: unknown] statt eines Standardparameters, damit ein ausdruecklich uebergebenes undefined als fehlender Wert wirft"
  - "Der Belegschluessel der Stellenplan-Kacheln bleibt auf der Vereinigung pdfSeiten, damit quellen.json byte-identisch bleibt"
  - "Der e2e-Test fuer einen Beleg nur mit Seite nutzt die Zeile Weitergabe an Kreis und Land auf /ausgaben statt der nun berechneten Stellenplan-Kachel"

patterns-established:
  - "Kachel ohne Wert: kein Etikett, keine Herleitung, keine Seiten, nie eine erfundene 0"

requirements-completed: [TXT-05, TXT-06]

coverage:
  - id: D1
    description: "Alle drei Stellenplan-Kacheln tragen berechnet mit Herleitung; die Kachel Vorjahr ist nicht mehr ohne Etikett"
    requirement: TXT-05
    verification:
      - kind: e2e
        ref: "e2e/quelle.spec.ts, e2e/smoke.spec.ts (project ci, 81 passed)"
        status: pass
    human_judgment: true
    rationale: "Wortlaut der Herleitungen und Sichtbarkeit des Etiketts brauchen ein Auge; Texte stammen aus dem UI-SPEC-Default"
  - id: D2
    description: "stellenSummen() und nachwuchs() liefern Seiten je Kachel bzw. nur der Jahre mit Wert"
    requirement: TXT-05
    verification:
      - kind: unit
        ref: "src/lib/__tests__/stellen.test.ts#Seiten je Kachel (D-11, 06/IN-07)"
        status: pass
      - kind: unit
        ref: "src/lib/__tests__/stellen.test.ts#06/IN-07: zitiert nur die Seiten der Jahre mit Personenzahl"
        status: pass
    human_judgment: false
  - id: D3
    description: "einwohnerZahl() wirft bei fehlender oder ungueltiger Einwohnerzahl mit fehlt in haushalt.json; EbenenTabelle zeigt keine Strich-Spalte"
    requirement: TXT-06
    verification:
      - kind: unit
        ref: "src/lib/__tests__/einwohner.test.ts"
        status: pass
    human_judgment: false
  - id: D4
    description: "Bei 360 px laufen die Stellenplan-Kacheln nicht ueber, lange Quellzeilen brechen um"
    verification:
      - kind: e2e
        ref: "e2e/mobil.spec.ts, e2e/kacheln.spec.ts (project mobil 14 passed, ci 81 passed)"
        status: pass
    human_judgment: true
    rationale: "Backstop-Aussage aus dem Plan; die Playwright-Laeufe pruefen Ueberlauf, nicht die Lesbarkeit der Etiketten"

duration: 35min
completed: 2026-10-07
status: complete
plan_head_before: 93b0a61fc741d1cbc53e63ca5d16feb2060305e6
plan_head_after: 2a8e5a593f7d29ecc9ede4bf1024a4e5049f9268
---

# Phase 8 Plan 03: Stellenplan-Kacheln und Einwohnerzahl Summary

**Alle drei Stellenplan-Kacheln tragen jetzt "berechnet" samt Herleitung und nennen nur ihre eigenen PDF-Seiten; eine gemeinsame Pruefung `einwohnerZahl()` macht eine fehlende Einwohnerzahl zum lauten Datenfehler statt zur Spalte voller Striche.**

## Performance

- **Duration:** rund 35 min
- **Started:** 2026-10-07T20:10:00Z (geschaetzt)
- **Completed:** 2026-10-07T20:25:00Z
- **Tasks:** 2
- **Files modified:** 9 (2 neu)

## Accomplishments

- `stellenSummen()` liefert zusaetzlich `seitenHaushaltsjahr`, `seitenVorjahr`, `seitenBesetzt`, jeweils leer ohne Wert; `pdfSeiten` (Vereinigung) bleibt unveraendert.
- `nachwuchs()` zitiert nur Seiten der Jahre mit Personenzahl, der Satz der Seite folgt dadurch automatisch.
- `StellenplanPage.vue`: alle drei Kacheln `berechnet`, jede mit Herleitung fuer die Quellenleiste (Jahre ueber `formatiereJahr`), Quellzeile nur mit eigenen Seiten; Belegschluessel unveraendert, `quellen.json` und alle generierten Daten byte-identisch (`alle.py --jahr 2026`).
- `lib/einwohner.ts`: `einwohnerZahl()` ersetzt die privaten Kopien in `kennzahlen.ts` und `produkt.ts`; `EbenenTabelle` ruft sie nur im Modus `zuschussbedarf`.

## Task Commits

1. **Task 1: Kacheln berechnet und eigene Quellseiten (06/IN-07, D-10, D-11)** - `1d4e359` (fix)
   - Folgefix am e2e-Test: `c3b1406` (fix, 06/IN-07)
2. **Task 2: Gemeinsame Einwohnerzahl (05/IN-08, 06/IN-03, D-09, TXT-06)** - TDD
   - RED: `52c1ee7` (test)
   - GREEN: `2a8e5a5` (fix)

Commits je Finding-ID: 06/IN-07 `1d4e359`, `c3b1406`; 05/IN-08 und 06/IN-03 (Einwohner-Teil) `52c1ee7`, `2a8e5a5`.

## TDD Gate Compliance

- RED (`52c1ee7`): Test `einwohner.test.ts` mit Geruest ohne Pruefung. Die 8 Wurf-Tests (null, undefined, Text, NaN, 0, negativ, unendlich, Meldung mit Wert) schlugen an der Assertion `expected [Function] to throw an error` fehl, die zwei Positivtests liefen. Semantische Bewertung: Zieltests liefen und scheiterten an der geplanten Assertion, keine Lade- oder Importfehler. Der Klassifikator `check tdd-red-evidence` wurde nicht eingesetzt (tdd_mode nicht verlangt).
- GREEN (`2a8e5a5`): alle 10 Tests gruen, gesamte Suite 1982 Tests gruen.
- REFACTOR: nicht noetig.
- Task 1 (Typ tracer) schrieb die Tests vor dem Code (4 Tests schlugen gegen den alten Code fehl) und wurde mit einem Commit gebucht.

## Files Created/Modified

- `app/src/lib/einwohner.ts` - einzige Pruefung der Einwohnerzahl
- `app/src/lib/__tests__/einwohner.test.ts` - Wurf-Tests mit injizierten Werten
- `app/src/lib/stellen.ts` - Seiten je Kachel, eingeengte Nachwuchsseiten
- `app/src/lib/__tests__/stellen.test.ts` - konstruierter Stellenplan mit je Merkmal und Jahr anderen Seiten
- `app/src/pages/StellenplanPage.vue` - Etikett, Herleitungen, `kachelZeile(quelle, differenz, seiten)`
- `app/src/lib/kennzahlen.ts`, `app/src/lib/produkt.ts` - nutzen `einwohnerZahl`
- `app/src/components/EbenenTabelle.vue` - Einwohnerzahl nur im Modus `zuschussbedarf`
- `app/e2e/quelle.spec.ts` - Beleg-nur-mit-Seite-Test auf `/ausgaben`

## Decisions Made

- Rest-Argument statt Standardparameter bei `einwohnerZahl`, weil `einwohnerZahl(undefined)` laut Plan werfen muss und ein Standardparameter `undefined` durch den echten Wert ersetzt.
- Echtdaten haben alle Stellenplan-Zeilen auf 284 bis 286 und Nachwuchs auf 290, daher aendern sich die sichtbaren Quellzeilen nicht; das Verhalten ist durch konstruierte Daten belegt (RESEARCH Korrektur 3).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `einwohnerZahl(undefined)` warf nicht**
- **Found during:** Task 2 (GREEN)
- **Issue:** Die Signatur `wert: unknown = haushalt.meta.einwohner.wert` ersetzt ein ausdruecklich uebergebenes `undefined` durch den echten Wert; der geforderte Wurf blieb aus.
- **Fix:** Rest-Argument `[wert?: unknown]`, Standardwert nur bei fehlendem Argument.
- **Files modified:** app/src/lib/einwohner.ts
- **Verification:** einwohner.test.ts 10 von 10 gruen
- **Committed in:** 2a8e5a5

**2. [Rule 3 - Blocking] e2e-Test "Beleg nur mit Seite" brach durch Task 1**
- **Found during:** Task 2 (volle Playwright-Suite, project ci)
- **Issue:** Der Test nutzte die Stellenplan-Kachel als Beispiel fuer einen Beleg ohne Markierung. Sie ist nun berechnet und zeigt "Berechneter Wert", also fehlte "Zeile nicht automatisch markiert".
- **Fix:** Der Test verwendet die Zeile "Weitergabe an Kreis und Land" auf `/ausgaben` (per Probe als einziger Seitenbeleg ohne Markierung gefunden).
- **Files modified:** app/e2e/quelle.spec.ts (nicht in files_modified des Plans)
- **Verification:** volle Suite ci 81 passed, mobil 14 passed
- **Committed in:** c3b1406

---

**Total deviations:** 2 auto-fixed (1 Bug, 1 Blocking)
**Impact on plan:** beide fuer Korrektheit noetig, kein Scope Creep.

## Issues Encountered

- `vermerk` ist ein Pflichtfeld in `StellenplanZeile`; die konstruierten Testzeilen brauchten es (type-check hat es gefangen).
- Das Pre-Commit-Werkzeug der Umgebung verlangt einfache Befehle ohne Variablen in Pfaden; Scratch-Pfade wurden daher ausgeschrieben.

## Known Stubs

None.

## Threat Flags

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `EbenenTabelle.betragText` unberuehrt gelassen (Plan 08-04).
- Zuschuss-Zeile "Zusammen" und Uebersicht weiterer abgeleiteter Summen (D-12) folgen in 08-05.
- `personenText` bleibt fuer 08-10.

## Self-Check: PASSED

- Dateien vorhanden: einwohner.ts, einwohner.test.ts, stellen.ts, StellenplanPage.vue
- Commits `1d4e359`, `52c1ee7`, `c3b1406`, `2a8e5a5` liegen auf dem Branch
- Gesamtpruefung: Vitest 1982 gruen, type-check, lint, format:check, build-only gruen; Playwright ci 81 und mobil 14 gruen; `alle.py --jahr 2026` ohne Aenderung an `daten/`, `app/src/data/`, `app/public/quellen`

---
*Phase: 08-fixes-und-triage*
*Completed: 2026-10-07*
