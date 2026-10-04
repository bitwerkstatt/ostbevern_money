---
phase: 05-leitfragen-seiten
plan: 05
subsystem: ui
tags: [echarts, vue, vitest, a11y, wcag, palette, tooltip, reduced-motion]

requires:
  - phase: 05-leitfragen-seiten
    provides: "05-01: vitest runner, formatiere() with KEIN_WERT fallback"
provides:
  - "echartsTheme.ts: Treemap/Sankey/Line/Legend/Aria registered; PB_FARBEN, KL_FARBE, farbeFuerPb, abstufung, KL_DECAL, PUNKT_DECAL, semantic colours; chart text >= 14 px"
  - "charts/tooltip.ts: htmlSicher, tooltipZeilen (escaped ECharts tooltip HTML)"
  - "lib/bewegung.ts: useReducedMotion, ohneAnimation"
  - "BaseChart: leerTitel/leerText, UI-SPEC error text, Sankey-aware empty check, reduced motion"
  - "DatenTabelle: visible dash for null + 'kein Wert', zelle slot, fussnote, leerTitel/leerText"
  - "05-UI-SPEC.md amended for D-19, D-20 and research findings"
affects: [05-07, 05-08, 05-09, 05-10, 05-11, 05-12, 05-13, 05-14, 05-15]

actuals:
  tokens: 17000
  tasks: 3
  commits: 3
plan_head_before: 8403a43b4a14a6ce43ab467307a65386035a8b01
plan_head_after: 57b3b036db65667b351cb2da10aed0c4e355d092

tech-stack:
  added: []
  patterns:
    - "Chart colours only via token() with UI-SPEC hex fallback; single use() call in echartsTheme.ts"
    - "Every dynamic tooltip string goes through htmlSicher/tooltipZeilen"
    - "Non-colour encoding: KL_DECAL stripes, PUNKT_DECAL dots, always with text"
    - "Composables mirror bildschirm.ts (SSR guard, onScopeDispose cleanup)"

key-files:
  created:
    - app/src/charts/tooltip.ts
    - app/src/charts/__tests__/farben.test.ts
    - app/src/charts/__tests__/tooltip.test.ts
    - app/src/lib/bewegung.ts
    - app/src/lib/__tests__/bewegung.test.ts
  modified:
    - app/src/charts/echartsTheme.ts
    - app/src/components/BaseChart.vue
    - app/src/components/DatenTabelle.vue
    - .planning/phases/05-leitfragen-seiten/05-UI-SPEC.md

key-decisions:
  - "Decal type derived from TreemapSeriesOption['itemStyle']['decal'] because echarts does not export DecalObject"
  - "Theme font size parsed only from a resolved px token value; WA's unresolved round(calc()) text falls back to 14, result is max(14, value)"
  - "UI-SPEC export name UEBERSCHUSS_DECAL renamed to PUNKT_DECAL (also marks Minderaufwand), documented in UI-SPEC"

patterns-established:
  - "Palette completeness test keyed on haushalt.json knoten with ebene PB (fails on missing or surplus code)"
  - "DatenTabelle zelle slot wraps only the cell content; th/td stay owned by the table"

requirements-completed: [AUSG-01, AUSG-02, FLUSS-01, FLUSS-04]

coverage:
  - id: D1
    description: "PB_FARBEN covers exactly the 16 PB-level codes of haushalt.json, farbeFuerPb throws on unknown codes, colours unique"
    requirement: AUSG-01
    verification:
      - kind: unit
        ref: "app/src/charts/__tests__/farben.test.ts#PB_FARBEN (D-08)"
        status: pass
    human_judgment: false
  - id: D2
    description: "abstufung only darkens (rank 0/1/2, repeating) and gives contrast >= 4.5:1 vs white for all 16 colours x 3 ranks"
    requirement: AUSG-02
    verification:
      - kind: unit
        ref: "app/src/charts/__tests__/farben.test.ts#abstufung"
        status: pass
    human_judgment: false
  - id: D3
    description: "Tooltip helpers escape all dynamic text (T-05-12)"
    requirement: FLUSS-04
    verification:
      - kind: unit
        ref: "app/src/charts/__tests__/tooltip.test.ts"
        status: pass
    human_judgment: false
  - id: D4
    description: "ohneAnimation returns an animation-free copy and leaves the input untouched; useReducedMotion is false without window"
    requirement: FLUSS-01
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/bewegung.test.ts"
        status: pass
    human_judgment: false
  - id: D5
    description: "BaseChart empty/error states and DatenTabelle dash/zelle slot/fussnote render per UI-SPEC"
    verification:
      - kind: other
        ref: "ad-hoc SSR render in scratch copy (not committed): dash+kein Wert, button via zelle slot, fussnote, empty texts, Sankey empty, error text"
        status: pass
    human_judgment: true
    rationale: "No committed component test; visual layout (Caption style, sticky label cell) needs a browser check at end of phase"
  - id: D6
    description: "05-UI-SPEC.md amended for D-19, D-20, wa-radio, Ist=vorläufig, row counts, E6, text year-binding, skip link, product Grundzahlen, footer config"
    verification:
      - kind: other
        ref: "grep markers (D-19, D-20, wa-radio appearance=\"button\", vorläufige, ueberschuss_allgemein, config.ts); 18 lines carry 'geändert 2026-10-04'"
        status: pass
    human_judgment: false

duration: 14min
completed: 2026-10-04
status: complete
---

# Phase 5 Plan 05: Chart foundation and UI-SPEC amendments Summary

**Central Aufgabenbereich palette (16 colours, darkening steps with proven WCAG contrast, KL/dot decals), escaped ECharts tooltips, reduced-motion handling, UI-SPEC empty/error/missing-value states in BaseChart and DatenTabelle, and a UI-SPEC amended for D-19/D-20.**

## Performance

- **Duration:** 14 min
- **Started:** 2026-10-04T12:44:00Z
- **Completed:** 2026-10-04T12:58:00Z
- **Tasks:** 3
- **Files modified:** 9 (5 created, 4 modified)

## Accomplishments
- `echartsTheme.ts` is now the only `use()` call and registers Treemap, Sankey, Line, Legend and Aria; exports the D-08 palette, `abstufung`, `KL_DECAL`/`PUNKT_DECAL` and the semantic colours; chart text is at least 14 px.
- A test ties `PB_FARBEN` to the PB-level knoten of `haushalt.json` (15 PB plus KL) and proves contrast >= 4.5:1 for all 16 colours x 3 ranks.
- `tooltip.ts` (`htmlSicher`, `tooltipZeilen`) closes the tooltip XSS threat for later plans.
- `BaseChart` and `DatenTabelle` lose the Phase-1 placeholder wording and gain the UI-SPEC states; `DatenTabelle` has a `zelle` scoped slot for buttons/links/tags.
- `05-UI-SPEC.md` now matches D-19 (Minderaufwand as left Sankey source, in the mobile "Woher" bar), D-20 and the research findings.

## Task Commits

1. **Task 1: Tracer, Palette/Registrierung/Tooltips** - `b29cad7` (feat)
2. **Task 2: BaseChart/DatenTabelle/Bewegung** - `169b2b2` (feat)
3. **Task 3: UI-SPEC-Anpassungen** - `57b3b03` (docs)

**Plan metadata:** committed with this SUMMARY (docs: complete plan)

## Files Created/Modified
- `app/src/charts/echartsTheme.ts` - module registration, palette, decals, semantic colours, 14 px theme text
- `app/src/charts/tooltip.ts` - `htmlSicher`, `tooltipZeilen`
- `app/src/charts/__tests__/farben.test.ts`, `tooltip.test.ts` - palette/contrast/escaping tests
- `app/src/lib/bewegung.ts`, `__tests__/bewegung.test.ts` - reduced-motion composable and option helper
- `app/src/components/BaseChart.vue` - `leerTitel`/`leerText`, error text, Sankey empty check, `ohneAnimation`
- `app/src/components/DatenTabelle.vue` - dash for null, `zelle` slot, `fussnote`, empty texts
- `.planning/phases/05-leitfragen-seiten/05-UI-SPEC.md` - amendments

## Decisions Made
- Decal type derived from `TreemapSeriesOption['itemStyle']['decal']` since echarts does not export `DecalObject`.
- Font size is only taken from a resolved `px` token value (WA defines `--wa-font-size-s` as unresolved `round(calc())` text), otherwise 14; never below 14.
- Renamed the UI-SPEC's `UEBERSCHUSS_DECAL` to `PUNKT_DECAL` (the plan names it so; same pattern marks Minderaufwand) and updated the UI-SPEC accordingly.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `DecalObject` is not exported by echarts**
- **Found during:** Task 1 (type-check)
- **Issue:** `import type { DecalObject } from 'echarts'` fails with TS2305.
- **Fix:** Exported a `Decal` type derived from `TreemapSeriesOption`'s `itemStyle.decal`.
- **Files modified:** app/src/charts/echartsTheme.ts
- **Verification:** type-check, lint, build green
- **Committed in:** b29cad7

**2. [Process] Task 2 (tdd="true") committed as one feat commit**
- Tests were written first and verified failing (module not found) in the scratch copy, but test and implementation share one task commit as the plan specifies a single commit per task. No separate RED commit exists.

**3. [Scope-compatible extra] UI-SPEC naming alignment**
- `UEBERSCHUSS_DECAL` references in the UI-SPEC were renamed to `PUNKT_DECAL` and the export list in the component table was completed (part of Task 3 commit).

---

**Total deviations:** 1 auto-fixed (1 blocking), 2 process/scope notes
**Impact on plan:** None on scope; `datenTabelle.ts` (listed in `files_modified`) needed no change because `SpaltenArt` was not extended.

## Issues Encountered
- Sandbox git-guard refused compound shell commands; commands were split. No code impact.
- No committed component-level test for BaseChart/DatenTabelle (no DOM test infrastructure in the plan); verified via an uncommitted SSR render in the scratch copy.

## Known Stubs
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Wave-3 page plans can colour any Aufgabenbereich through `farbeFuerPb`/`abstufung`, build tooltips with `tooltipZeilen`, pass `leerTitel`/`leerText` to `BaseChart`/`DatenTabelle`, and read one consistent UI-SPEC.
- `app/src/main.ts` and other shared files were not touched.

## Self-Check: PASSED

- Created files exist (tooltip.ts, bewegung.ts, farben/tooltip/bewegung tests, this SUMMARY).
- Commits b29cad7, 169b2b2, 57b3b03 present in `git log`.
- Scratch-copy chain: vitest 31/31 passed (4 files), type-check, lint, format:check, build all green.
- Task acceptance greps pass (no `ab Phase 2`, Fußzeilen-Kontakt text, `name="zelle"`, `ohneAnimation`, no `color.lift(`).

---
*Phase: 05-leitfragen-seiten*
*Completed: 2026-10-04*
