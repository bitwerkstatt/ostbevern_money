---
phase: 05-leitfragen-seiten
plan: 12
subsystem: ui
tags: [echarts, sankey, vue, vitest, a11y, geldfluss]

requires:
  - phase: 05-leitfragen-seiten
    provides: "05-04 useJahr/jahrLink and page shell; 05-05 palette, decals, tooltipZeilen, BaseChart, DatenTabelle zelle slot; 05-06 ErklaerText, textFuerJahr, findeKlKnoten, anteil"
provides:
  - "lib/geldfluss.ts: baueGeldfluss (balanced model per year), geldflussOption (Sankey), zielCodeAusKlick, geldflussZeilen, baueGeldflussBalken, balkenOption, lesehilfeSatz, welcheLesetexte"
  - "SankeyDiagramm.vue: 640 px Sankey with click navigation to /ausgaben?jahr&pb"
  - "GeldflussBalken.vue: two equally long stacked bars Woher/Wohin with always-visible legend tables"
  - "GeldflussPage.vue: complete /geldfluss page with Sankey/bars switch and reading-aid callout"
affects: [05-14, 05-15, phase-06, phase-07]

actuals:
  tokens: 12000
  tasks: 2
  commits: 4
plan_head_before: 368177eb3ea48d6462b1a2d8b1d14dc3d3a6609b
plan_head_after: 930d9c69cd02346d184637e5da0bb721c8f3f823

tech-stack:
  added: []
  patterns:
    - "Sankey balanced from data only: Defizit and Globaler Minderaufwand as left sources, Ueberschuss on the right; no year special case"
    - "Node ids are unique ECharts names, display names separate; click target resolved through a Map lookup (zielCodeAusKlick)"
    - "Mobile bars share the node model of the Sankey (same sums, colours, decals); axis max = own sum so both bars are equally long"
    - "Reading aid = curated texts filtered by textFuerJahr plus one sentence composed from the selected year's data"

key-files:
  created:
    - app/src/lib/geldfluss.ts
    - app/src/lib/__tests__/geldfluss.test.ts
    - app/src/components/SankeyDiagramm.vue
    - app/src/components/GeldflussBalken.vue
  modified:
    - app/src/pages/GeldflussPage.vue

key-decisions:
  - "Left Ertrag nodes darken by rank (abstufung) within their group so adjacent bar segments and the legend swatches stay distinguishable"
  - "Sankey labels use labelLayout moveOverlap shiftY so the many small right-hand nodes do not overprint each other (hideOverlap false: every label stays)"
  - "lesehilfeSatz takes the Wertart display name (Ist/Ansatz/Planung), not 'Ansatz 2026', to avoid repeating the year"
  - "Negative plug values (Uebrige Steuern, Sonstige Zuwendungen, Sonstige Ertraege) and a positive Globaler Minderaufwand throw instead of silently unbalancing the diagram"
  - "Separator colour of the mobile bars is read from --wa-color-surface-default in geldfluss.ts (token read with white fallback) because echartsTheme.ts is a frozen shared file in this wave"

requirements-completed: [FLUSS-01, FLUSS-02, FLUSS-03, FLUSS-04]

coverage:
  - id: D1
    description: "baueGeldfluss balances in every year of haushalt.jahre (sum left = sum right within 2 EUR), no node <= 0, Defizit/Ueberschuss/Minderaufwand exactly when their condition holds; 2026 Defizit 2.353.506, Minderaufwand 600.000, sum 30.455.569; 2024 Ueberschuss 191.990 on the right"
    requirement: FLUSS-02
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/geldfluss.test.ts#baueGeldfluss: Bilanz in jedem Jahr"
        status: pass
      - kind: unit
        ref: "app/src/lib/__tests__/geldfluss.test.ts#Geldfluss Haushalt 2026"
        status: pass
    human_judgment: false
  - id: D2
    description: "Sankey option: node width 16, gap 8, flow colour source at 35 %, focus adjacency, not draggable, labels width 160 with break; tooltips escaped"
    requirement: FLUSS-01
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/geldfluss.test.ts#geldflussOption"
        status: pass
      - kind: other
        ref: "ad-hoc ECharts SVG server render in the scratch copy (not committed): 2 decal patterns (KL, Minderaufwand) in 2026, 29 links, labels placed outside"
        status: pass
    human_judgment: true
    rationale: "Real label overlap, hover emphasis and the look of the 16 right-hand nodes at 700 to 1280 px need a browser"
  - id: D3
    description: "Only Aufgabenbereich and KL nodes carry a click target; zielCodeAusKlick ignores Ertrag nodes, edges, prototype keys and malformed input; SankeyDiagramm pushes /ausgaben with jahr and pb"
    requirement: FLUSS-03
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/geldfluss.test.ts#zielCodeAusKlick"
        status: pass
      - kind: unit
        ref: "app/src/lib/__tests__/geldfluss.test.ts#baueGeldfluss: Bilanz in jedem Jahr (Klickziel, D-10)"
        status: pass
    human_judgment: true
    rationale: "The actual canvas click and router navigation run in a browser"
  - id: D4
    description: "Mobile bars: Woher (Ertraege plus Defizit and Minderaufwand) and Wohin (KL, Aufgabenbereiche, Zinsen plus Ueberschuss) have equal sums in every year and use the node colours and decals; legend tables always visible with links to /ausgaben"
    requirement: FLUSS-04
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/geldfluss.test.ts#baueGeldflussBalken: Mobil-Alternative"
        status: pass
      - kind: other
        ref: "ad-hoc vue server render of GeldflussBalken and GeldflussPage (2024, 2025, 2026) plus ECharts SVG render of both bars (not committed)"
        status: pass
    human_judgment: true
    rationale: "Equal visual length, swatch patterns and no horizontal scrolling at 360 px need a browser"
  - id: D5
    description: "Reading aid: defizit_ruecklagen only in the Haushaltsjahr with a Defizit, ueberschuss_ruecklage in surplus years, plus a sentence from the selected year's data with amounts and PDF page; never NaN/undefined/{{"
    requirement: FLUSS-02
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/geldfluss.test.ts#lesehilfeSatz and #welcheLesetexte"
        status: pass
    human_judgment: false
  - id: D6
    description: "Prohibitions: no Finanzplan values and no PB-code or year literal in geldfluss.ts"
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/geldfluss.test.ts#geldfluss.ts: Verbote"
        status: pass
    human_judgment: false

duration: 10min
completed: 2026-10-04
status: complete
---

# Phase 5 Plan 12: Geldfluss Summary

**Balanced Sankey (Ertragsarten, Defizit and Globaler Minderaufwand left, Gemeindehaushalt, KL/Aufgabenbereiche/Zinsen/Ueberschuss right) built from the Ergebnisplan only, with click-through to /ausgaben, a two-bar mobile alternative with always-visible legend tables, and a per-year reading aid.**

## Performance

- **Duration:** 10 min
- **Started:** 2026-10-04T13:22:18Z
- **Completed:** 2026-10-04T13:31:52Z
- **Tasks:** 2 (1 tracer, 1 TDD)
- **Files modified:** 5 (4 created, 1 modified)

## Accomplishments

- `baueGeldfluss(jahrIndex)` derives every node from `haushalt.json` without year special cases: three Steuer groups plus "Uebrige Steuern" plug, Schluesselzuweisung plus plug, Gebuehren und Entgelte, Sonstige Ertraege plug, Finanzertraege, then Defizit (`-ergebnis_nach_minderaufwand`) and Globaler Minderaufwand (`-Z. 27`) on the left, and KL, every Aufgabenbereich with Z. 17 > 0, Zinsen (GEP Z. 20) and a conditional Ueberschuss on the right. The balance test passes for all six years (±2 EUR); 2026 gives Defizit 2.353.506, Minderaufwand 600.000, sum 30.455.569.
- `SankeyDiagramm` renders the contract from UI-SPEC (640 px, node width 16, gap 8, source-coloured flows at 35 %, `focus: 'adjacency'`, not draggable, 160 px label width with break, KL and Minderaufwand decals). A click on an Aufgabenbereich or KL pushes `/ausgaben` with the explicit year and `pb`; the tables under the chart offer "Im Detail ansehen" links for keyboard users.
- `GeldflussBalken` replaces the Sankey up to 699 px through `useSchmalerBildschirm()`: two 56 px stacked bars with 2 px separators and equal length, legend tables with colour swatch (striped for KL, dotted for Minderaufwand), Betrag, Anteil and links to `/ausgaben`.
- The callout "So liest du das Diagramm" shows `geldfluss_lesehilfe` always, `defizit_ruecklagen` only in the Haushaltsjahr with a Defizit, `ueberschuss_ruecklage` in surplus years, and a sentence composed from the selected year with amounts and PDF page.

## Task Commits

1. **Task 1: Tracer, Geldfluss end to end** - `e332a0f` (feat)
2. **Task 2: Mobile Alternative und Lesehilfe (TDD)**
   - RED: `da48992` (test)
   - GREEN: `445daa8` (feat: lib)
   - Components and page: `930d9c6` (feat)

**Plan metadata:** committed with this SUMMARY (docs: complete plan)

## Files Created/Modified

- `app/src/lib/geldfluss.ts` - model, Sankey and bar options, click target, table rows, reading aid
- `app/src/lib/__tests__/geldfluss.test.ts` - 71 tests: balance over all years, conditional nodes, click targets, options and escaping, mobile sums, reading aid, prohibitions
- `app/src/components/SankeyDiagramm.vue` - Sankey inside BaseChart with click navigation
- `app/src/components/GeldflussBalken.vue` - mobile bars with legend tables
- `app/src/pages/GeldflussPage.vue` - complete page

## Decisions Made

See `key-decisions`. Besides those: the 2026 plan wording "Sonstige Ertraege" was kept for the left plug (it also contains Kostenerstattungen and Z. 03/08/09), as flagged in the plan.

## Deviations from Plan

None - plan executed exactly as written.

Notes: the plan names `welcheLesetexte` in the artifact list although the must_haves export list omits it; it is exported. No shared file (`main.ts`, `router/index.ts`, `echartsTheme.ts`) and no Web Awesome import was touched: `wa-details`, `wa-callout`, `wa-icon` were already registered in `main.ts`.

## Issues Encountered

None. The tracer verification passed on the first complete run (vitest 12 files / 184 tests, then 209 with Task 2; type-check, lint, format:check and build green in a scratch copy with `node_modules` taken from a lockfile-identical earlier scratch).

## Verification

- Scratch copy chain after Task 2: `npm run test` (12 files, 209 tests), `type-check`, `lint`, `format:check`, `build` all green.
- Acceptance greps for both tasks pass (`focus: 'adjacency'`, no PB-code literals, no `haushalt.finanzplan`, "Im Detail ansehen", "So liest du das Diagramm", `useSchmalerBildschirm`, Woher/Wohin).
- Throw-away renders (not committed): ECharts SVG server render of the Sankey (2024, 2026) and of both bars, and a Vue SSR render of the page for 2024, 2025 and 2026. They confirmed the node/link counts, 2 decal patterns in 2026, full-width bars with 2 px separators, correct links (`/ausgaben?pb=KL&jahr=2026`), the surplus text in 2024 and the omission of `defizit_ruecklagen` in 2025.

## Human check (end of phase)

On the host (`npm --prefix app run dev`): /#/geldfluss at 1280 px (hover highlight, click on "Innere Verwaltung" opens /ausgaben with PB and year, labels of the small right-hand nodes not overprinting), 2026 vs 2024 (left Defizit/Minderaufwand vs right Ueberschuss and the changed reading aid), 360 px (two equally long bars, legend tables, no horizontal scrolling), reduced motion.

## Known Stubs

None.

## Threat Flags

None - no new network endpoint, auth path or trust-boundary file access; tooltip text goes through `tooltipZeilen` (T-05-33).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

`/geldfluss` is complete; ready for the remaining wave-3 plans and the end-of-phase human check.

## Self-Check: PASSED

- Created files exist: `app/src/lib/geldfluss.ts`, `app/src/lib/__tests__/geldfluss.test.ts`, `app/src/components/SankeyDiagramm.vue`, `app/src/components/GeldflussBalken.vue` (all present), `app/src/pages/GeldflussPage.vue` modified.
- Commits `e332a0f`, `da48992`, `445daa8`, `930d9c6` exist in the worktree history.
- TDD gate: `test(05-12)` RED commit `da48992` precedes `feat(05-12)` GREEN `445daa8`.

---
*Phase: 05-leitfragen-seiten*
*Completed: 2026-10-04*
