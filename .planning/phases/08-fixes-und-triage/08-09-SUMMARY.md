---
phase: 08-fixes-und-triage
plan: 09
subsystem: ui
tags: [vue, echarts, web-awesome, theme, refactor]

requires:
  - phase: 08-fixes-und-triage
    provides: "08-02/08-04: geldfluss.ts und AufwandTreemap.vue ohne Altkopien der Regel rd."
provides:
  - "ChartCard-Beispieldaten-Callout mit Icon triangle-exclamation, per SSR-Test gepinnt"
  - "Verwaiste app/src/data/beispieldaten.json entfernt"
  - "flaechenFarbe() als einzige Flächenfarb-Quelle in charts/echartsTheme.ts"
  - "alsRgb mit zwei Ablehnungsmarkern"
  - "Key-Trenner, strikte null/undefined-Vergleiche, zweizeilig() in den Balkenbeschriftungen"
affects: [08-12]

plan_head_before: d7e46f410d0503f7ae5b21d85919376c55857325
plan_head_after: 7f850704b973a3e560e01507d21152c373d2bda8

actuals:
  tokens: 5000
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Flächenfarbe nur über flaechenFarbe() aus echartsTheme.ts (lazy, Token zur Aufrufzeit); wertartStil.ts reicht sie durch"
    - "Balkenbeschriftungen über zweizeilig() aus charts/beschriftung.ts"

key-files:
  created:
    - app/src/components/__tests__/chartcard.test.ts
  modified:
    - app/src/components/ChartCard.vue
    - app/src/charts/echartsTheme.ts
    - app/src/charts/wertartStil.ts
    - app/src/lib/geldfluss.ts
    - app/src/components/AufwandTreemap.vue
    - app/src/components/SchuldenstandDiagramm.vue
    - app/src/components/VeFaelligkeiten.vue
    - app/src/components/EntwicklungsDiagramm.vue
    - app/src/pages/EntwicklungPage.vue
    - app/src/components/RuecklagenBalken.vue
    - app/src/components/ErgebnisBalken.vue
  deleted:
    - app/src/data/beispieldaten.json

key-decisions:
  - "flaechenFarbe() ist eine Funktion statt Modulkonstante, weil der Token erst zur Aufrufzeit gelesen werden darf; die drei Decals in echartsTheme.ts nutzen sie ebenfalls statt der drei token()-Kopien"
  - "alsRgb: zwei Marker (#010203, #030201); abgelehnt nur, wenn beide Read-backs beim eigenen Marker bleiben, kein Stringvergleich mit dem Eingabewert mehr"

patterns-established:
  - "Außerhalb von echartsTheme.ts steht kein Hex- oder white-Ersatz für die Flächenfarbe"

requirements-completed: [TRI-04]

coverage:
  - id: D1
    description: "Beispieldaten-Callout der ChartCard zeigt triangle-exclamation bei unverändertem Text; Icon-Datei vorhanden (01/IN-03)"
    requirement: TRI-04
    verification:
      - kind: unit
        ref: "app/src/components/__tests__/chartcard.test.ts#ChartCard Beispieldaten-Callout"
        status: pass
    human_judgment: false
  - id: D2
    description: "Verwaiste beispieldaten.json gelöscht, alle.py erzeugt sie nicht neu, sonst bleiben daten/ app/src/data/ app/public/quellen byte-identisch (D-15)"
    requirement: TRI-04
    verification:
      - kind: other
        ref: "uv run --directory pipeline python alle.py --jahr 2026 && git status --porcelain -- daten app/src/data app/public/quellen"
        status: pass
    human_judgment: false
  - id: D3
    description: "Eine Flächenfarb-Quelle flaechenFarbe() in echartsTheme.ts; keine Hex-/white-Ersatzwerte außerhalb (06/IN-01)"
    requirement: TRI-04
    verification:
      - kind: e2e
        ref: "scripts/e2e-wie-ci.sh (ci, 81 Tests) und vitest 2022 Tests, type-check, lint, build-only"
        status: pass
    human_judgment: false
  - id: D4
    description: "alsRgb mit zwei Ablehnungsmarkern (05/IN-01); canvas-only, daher ohne vitest"
    requirement: TRI-04
    verification:
      - kind: other
        ref: "vue-tsc --build, build-only und Playwright-Smoke (Diagrammrouten rendern ohne Konsolenmeldung)"
        status: pass
    human_judgment: true
    rationale: "Das Verhalten bei einer vom Browser abgelehnten Farbe ist unter environment node nicht prüfbar; praktisches Risiko nahe null (Review)."
  - id: D5
    description: "Nits aus 06/IN-06: Key mit Trenner, strikte Vergleiche, zweizeilig() in Rücklagen- und Ergebnisbalken"
    requirement: TRI-04
    verification:
      - kind: e2e
        ref: "scripts/e2e-wie-ci.sh (ci, 81 Tests), grep-Akzeptanzkriterien"
        status: pass
    human_judgment: true
    rationale: "Beträge unter 1 Mio. € brechen jetzt zweizeilig um (RESEARCH A5); ob das optisch passt, beurteilt ein Mensch."

duration: 8min
completed: 2026-10-07
status: complete
---

# Phase 8 Plan 09: Kleine Darstellungsbefunde Summary

**Warn-Icon im Beispieldaten-Callout, verwaiste beispieldaten.json entfernt, eine Flächenfarbe (`flaechenFarbe()`) nur aus echartsTheme.ts, zwei-Marker-`alsRgb` und die Markup-/Vergleichs-Nits aus 06/IN-06.**

## Performance

- **Duration:** 8 min
- **Started:** 2026-10-07T18:49:00Z
- **Completed:** 2026-10-07T18:57:00Z
- **Tasks:** 3
- **Files modified:** 13 (12 geändert, 1 gelöscht, 1 neu)

## Accomplishments
- 01/IN-03: Der Callout mit `variant="warning"` trägt `triangle-exclamation`; Text und Flag unverändert; neuer SSR-Test pinnt Icon-Name, Text, fehlenden Callout ohne Flag und die Icon-Datei unter `public/icons/solid/`.
- D-15: `app/src/data/beispieldaten.json` entfernt (kein Importeur, `alle.py` erzeugt sie nicht); `alle.py --jahr 2026` lässt danach `daten/`, `app/src/data/`, `app/public/quellen` unverändert.
- 06/IN-01: `flaechenFarbe()` in echartsTheme.ts ist die einzige Quelle; wertartStil.ts reicht sie durch (vier Importeure unverändert), geldfluss.ts, AufwandTreemap.vue und SchuldenstandDiagramm.vue nutzen sie; die lokalen Kopien `trennerFarbe()` und `token()` sind weg.
- 05/IN-01: `alsRgb` prüft die Ablehnung über zwei verschiedene Marker.
- 06/IN-06: Key `produkt/massnahmeId`, strikte Vergleiche in EntwicklungsDiagramm und EntwicklungPage, `zweizeilig()` in RuecklagenBalken und ErgebnisBalken.

## Task Commits

1. **Task 1: Warn-Icon, verwaiste Beispieldaten (01/IN-03, D-15)** - `96a23de` (fix)
2. **Task 2: Flächenfarbe aus echartsTheme, zwei Marker (06/IN-01, 05/IN-01)** - `b9d3a68` (refactor)
3. **Task 3: Key-Trenner, strikte Vergleiche, zweizeilig (06/IN-06)** - `7f85070` (fix)

**Plan metadata:** folgt als docs-Commit (SUMMARY.md)

## Files Created/Modified
- `app/src/components/ChartCard.vue` - Callout-Icon `triangle-exclamation`
- `app/src/components/__tests__/chartcard.test.ts` - SSR-Test des Beispieldaten-Callouts
- `app/src/data/beispieldaten.json` - gelöscht (Phase-1-Überbleibsel)
- `app/src/charts/echartsTheme.ts` - `flaechenFarbe()`, zwei Marker in `alsRgb`, Decals nutzen `flaechenFarbe()`
- `app/src/charts/wertartStil.ts` - reicht `flaechenFarbe` aus echartsTheme durch
- `app/src/lib/geldfluss.ts` - `trennerFarbe()` entfernt, `flaechenFarbe()` genutzt
- `app/src/components/AufwandTreemap.vue` - lokale `token()`-Kopie entfernt
- `app/src/components/SchuldenstandDiagramm.vue` - Streifen-Rückfall über `flaechenFarbe()`
- `app/src/components/VeFaelligkeiten.vue`, `EntwicklungsDiagramm.vue`, `app/src/pages/EntwicklungPage.vue`, `RuecklagenBalken.vue`, `ErgebnisBalken.vue` - 06/IN-06

## Decisions Made
- `flaechenFarbe()` bleibt eine Funktion (lazy), die drei Decals in echartsTheme.ts rufen sie statt dreier `token(...)`-Kopien.
- Kein neuer Token, keine neue Farbe, keine neue Icon-Datei (Verbot aus dem Plan eingehalten).

## Deviations from Plan

None - plan executed exactly as written. (Zwei Prettier-Umbrüche in SchuldenstandDiagramm.vue, EntwicklungsDiagramm.vue und EntwicklungPage.vue wurden nach dem Format-Check übernommen; reine Formatierung.)

## Issues Encountered

None.

## Known Stubs

None.

## Threat Flags

None. Keine neue Netzwerk-, Auth- oder Dateizugriffsfläche; kein Paket installiert (T-08-SC), die einzige Datenänderung ist die geplante Löschung (T-08-16).

## Next Phase Readiness
- Beträge unter 1 Mio. € in Rücklagen- und Ergebnisbeschriftung brechen jetzt zweizeilig (A5); für die Disposition in 08-12 vermerkt.
- 05/IN-01 hat bewusst keinen vitest-Test (canvas-only); Evidenz sind type-check, build und Smoke.
- Verifikation: vitest 2022 Tests, type-check, lint, format:check, build-only und Playwright `ci` (81 Tests) grün in der Scratch-Kopie; `--project=mobil` wurde nicht gelaufen (nicht Teil der Plan-Verify-Befehle).

## Self-Check: PASSED

- Dateien vorhanden: chartcard.test.ts, echartsTheme.ts (mit `export function flaechenFarbe`), Commits `96a23de`, `b9d3a68`, `7f85070` liegen auf dem Branch; `beispieldaten.json` nicht mehr vorhanden.

---
*Phase: 08-fixes-und-triage*
*Completed: 2026-10-07*
