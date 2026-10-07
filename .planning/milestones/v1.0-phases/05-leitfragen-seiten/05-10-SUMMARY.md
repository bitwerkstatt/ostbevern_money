---
phase: 05-leitfragen-seiten
plan: 10
subsystem: ui
tags: [vue, echarts, treemap, bar-chart, drilldown, vue-router, a11y, vitest]
status: complete

requires:
  - phase: 05-leitfragen-seiten
    provides: "05-04 useJahr/useAnsicht/ansagen, 05-05 PB_FARBEN/abstufung/KL_DECAL/PUNKT_DECAL/tooltipZeilen/BaseChart/DatenTabelle, 05-06 proKopf/anteil/findeText/rendereAbsatz/findeKlKnoten"
provides:
  - "lib/drilldown.ts: baueEbene, kinderVon, baueBrotkrumen, klickZiel, ebenenElternCode, eintragTooltip, codeAusParams, kachelBeschriftet, ueberschussTextSchluessel, zuschussBalkenOption, zuschussBalkenHoehe, type EbenenEintrag"
  - "AufwandTreemap, ZuschussBalken, EbenenTabelle, Brotkrumen components"
  - "ChartCard h2 focusable (tabindex -1) with exposed fokussiereTitel()"
  - "AusgabenPage: URL-driven drill-down (pb/pg), Aufwand/Zuschussbedarf switch, surplus callout"
affects: [05-14, 05-11, 05-12, phase-06]

actuals:
  tokens: 20000
  tasks: 2
  commits: 3
plan_head_before: 368177eb3ea48d6462b1a2d8b1d14dc3d3a6609b
plan_head_after: 68d23765592a6d21f2bd297f17057a7e2cc53ace

tech-stack:
  added: []
  patterns:
    - "One flat treemap level per view, navigation only via router (nodeClick/roam/breadcrumb off); click params pass a type guard (codeAusParams) and are checked against the codes of the current level"
    - "Zuschuss bars: value axis with fixed 'nice' limits that always contain 0 and leave room for labels; zero line drawn by a second unlabelled category axis (onZero) while the names sit on a first axis at the left edge"
    - "Table cells carry only primitives (DatenZeile); booleans as 0/1; the zelle slot renders button / RouterLink / text"
    - "String key in watch() so year/mode changes (new ansicht object) do not trigger the level-change focus move"

key-files:
  created:
    - app/src/lib/drilldown.ts
    - app/src/lib/__tests__/drilldown.test.ts
    - app/src/components/AufwandTreemap.vue
    - app/src/components/ZuschussBalken.vue
    - app/src/components/EbenenTabelle.vue
    - app/src/components/Brotkrumen.vue
  modified:
    - app/src/components/ChartCard.vue
    - app/src/pages/AusgabenPage.vue

key-decisions:
  - "Zero-valued nodes are dropped from a level; Anteil in mode Aufwand is wert / Σ values, in mode Zuschussbedarf wert / Σ positive values with null (shown as dash) for surplus rows"
  - "EbenenEintrag.ueberschuss is true only in mode Zuschussbedarf; in mode Aufwand a surplus node still has a positive Aufwand and must not be labelled Überschuss"
  - "Treemap label heuristic requires 2.5 x (72 x 44 px) of tile area instead of exactly 72 x 44 px (SVG probe showed 'Natu...' labels otherwise); names stay in tooltip and table"
  - "Wertachse of the bar chart gets explicit nice limits (steps 1/2/2.5/5/10 x 10^n), 30 % (45 % on narrow screens) head-room right of the largest value, so labels fit and a test can assert that 0 is on the axis"
  - "Surplus labels sit right of the zero line (position 'right'), where the empty part of the surplus row is, so they never collide with the category names"
  - "Brotkrumen keeps its UI-SPEC file name; the component name is OmBrotkrumen (defineOptions) to satisfy vue/multi-word-component-names"

patterns-established:
  - "Level builder is pure and reads only berechnet; the grep gate 'ertraege' must stay 0 in drilldown.ts"
  - "Tooltips of both chart types come from one eintragTooltip() built with tooltipZeilen (escaped)"

requirements-completed: [AUSG-01, AUSG-02, AUSG-03]

coverage:
  - id: D1
    description: "baueEbene: one level per view, sorted descending, sums of children equal the parent in every year (+-2 EUR, KL +-3.000 EUR), zero rows dropped, Anteil sums to 100 %"
    requirement: AUSG-01
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/drilldown.test.ts#baueEbene: oberste Ebene, #baueEbene: Kinder summieren sich zum Elternknoten, #baueEbene: Anteile im Modus Aufwand"
        status: pass
    human_judgment: false
  - id: D2
    description: "Colours: PB_FARBEN on top level, abstufung(PB colour, rank) below, KL and its Unterposten carry KL_DECAL; klickZiel drill / produkt / keins (KL children link nowhere)"
    requirement: AUSG-02
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/drilldown.test.ts#baueEbene: Farben (D-08), #klickZiel (D-06, D-08)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Mode Zuschussbedarf: every value and Überschuss flag equals berechnet exactly (all years, all levels); bars as negative values with PUNKT_DECAL and label 'Überschuss: {Betrag}', axis contains 0, zero line axis, escaped tooltips"
    requirement: AUSG-03
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/drilldown.test.ts#baueEbene: Modus Zuschussbedarf, #zuschussBalkenOption (AUSG-03, D-05)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Überschuss texts: ueberschuss_pb_<PB> when present, else ueberschuss_allgemein; both exist and render placeholder-free for every surplus node in every year and level"
    requirement: AUSG-03
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/drilldown.test.ts#ueberschussTextSchluessel (AUSG-03)"
        status: pass
    human_judgment: false
  - id: D5
    description: "Eingabeschutz: __proto__/constructor/unknown codes throw in baueEbene, kinderVon, baueBrotkrumen, ueberschussTextSchluessel; click params go through codeAusParams"
    requirement: AUSG-01
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/drilldown.test.ts#Eingabeschutz (T-05-26), #codeAusParams (Pitfall 16)"
        status: pass
    human_judgment: false
  - id: D6
    description: "AusgabenPage end to end (SSR probe in scratch copy, not committed): breadcrumb nav, table rows with rd./Überschuss/pro Einwohner, callout texts for PB 11, PB 16 and PB 14 (2024), invalid pb/pg ignored"
    requirement: AUSG-01
    verification:
      - kind: other
        ref: "ad-hoc vue/server-renderer probe with memory router for 7 URLs; ad-hoc ECharts SVG render of treemap and bars"
        status: pass
    human_judgment: true
    rationale: "Mouse/keyboard drill-down, focus movement, live-region announcements, Web Awesome radio-group events and the visual look (stripes, dots, label fit, 360 px) need a browser; the plan's human-check could not be run in this Linux sandbox"

duration: 55min
completed: 2026-10-04
---

# Phase 5 Plan 10: Ausgaben-Drilldown Summary

**Treemap (Aufwand) and horizontal bars with negative Überschuss bars (Zuschussbedarf) over one URL-driven level (Aufgabenbereich, Produktgruppe, Produkt), own breadcrumbs, an always-visible keyboard table, a striped pink KL tile and a callout that explains surplus areas.**

## Performance

- **Duration:** about 55 min
- **Tasks:** 2 (1 tracer, 1 TDD)
- **Files modified:** 8 (6 created, 2 modified)
- **Commits:** 3 code commits plus this SUMMARY

## Accomplishments

- `lib/drilldown.ts` builds every level from `ergebnisplan[code].berechnet` only (no `ertraege` in the file, grep gate 0): sorted, zero rows dropped, PB colours with `abstufung`, `KL_DECAL` on KL and its three Unterposten, click target per entry. Tests walk all years and all parents (sums within +-2 EUR, KL +-3.000 EUR; Zuschussbedarf and Überschuss flag equal to `berechnet`).
- `AufwandTreemap`: one flat level, `nodeClick: false`, `roam: false`, no breadcrumb, 2 px tile border, name 14/600 and amount 14/400 white labels hidden by an area heuristic, KL labels on a KL-coloured pill, `cursor: pointer` only on clickable tiles, escaped tooltips with the click hint.
- `ZuschussBalken`: Überschuss bars left of the zero line with `PUNKT_DECAL` and "Überschuss: {Betrag}", PB colours, height rows x 40 + 48 px. An ECharts SVG render showed the zero line at x = 0, the surplus labels right of it and one dot and one stripe pattern.
- `EbenenTabelle` (always visible): drill button, product `RouterLink` (`name: 'produkt'` with jahr/modus/pb/pg), plain text for KL Unterposten, "rd." for rounded rows, Anteil, and in mode Zuschussbedarf "pro Einwohner (berechnet)".
- `Brotkrumen`: `<nav aria-label="Ebene im Haushalt"><ol>`, earlier entries `wa-button appearance="plain"` (44 px), last entry `aria-current="location"`.
- `AusgabenPage`: card title switches between "Aufwand nach Aufgabenbereich {jahr}" and "Zuschussbedarf nach Aufgabenbereich {jahr}" plus " - {Ebenenname}"; `wa-radio-group` "Ansicht" with the UI-SPEC hint changes only `modus` (replace); focus moves to the card heading with "Ebene {Name}, {n} Eintrag/Einträge" after a level change, mode switch announces "Zeige Zuschussbedarf/Aufwand" and keeps focus; the "Warum manche Bereiche im Plus liegen" callout quotes `ueberschuss_pb_<PB>` or `ueberschuss_allgemein` per surplus node with its PDF pages.

## Task Commits

1. **Task 1: Tracer, drill-down end to end** - `57c9929` (feat). Tests and implementation were committed together as the tracer; tracer verification (full app chain in the scratch copy) passed before expansion.
2. **Task 2: Brotkrumen, Modus-Umschalter, Zuschuss-Balken, Überschuss-Erklärung (TDD)**
   - RED `cf0793f` (test): signature-only stubs, 16 new tests fail
   - GREEN `68d2376` (feat): 73 drilldown tests, full app suite 211 passed

**Plan metadata:** committed with this SUMMARY (docs: complete plan)

## Files Created/Modified

- `app/src/lib/drilldown.ts` - level builder, breadcrumbs, click targets, tooltip, surplus text key, bar option
- `app/src/lib/__tests__/drilldown.test.ts` - 73 tests
- `app/src/components/AufwandTreemap.vue`, `ZuschussBalken.vue`, `EbenenTabelle.vue`, `Brotkrumen.vue` - new components
- `app/src/components/ChartCard.vue` - h2 `tabindex="-1"`, exposed `fokussiereTitel()` (props unchanged)
- `app/src/pages/AusgabenPage.vue` - drill-down, switch, callout

## Decisions Made

See `key-decisions` in the frontmatter. The main product decisions: surplus rows have no Anteil (dash, announced as "kein Anteil"), the surplus flag exists only in mode Zuschussbedarf, and the bar axis uses explicit nice limits.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `Brotkrumen` fails `vue/multi-word-component-names`**
- **Found during:** Task 2 (lint)
- **Fix:** kept the UI-SPEC file name and set `defineOptions({ name: 'OmBrotkrumen' })` instead of touching the shared `eslint.config.ts`.
- **Files modified:** app/src/components/Brotkrumen.vue
- **Committed in:** 68d2376

**2. [Rule 1 - Bug] Label heuristic too lax**
- **Found during:** Task 2 (ECharts SVG probe of the treemap, uncommitted)
- **Issue:** with the plain 72 x 44 px area test, tiles of about 85 px width showed "Natu..." / "504....". `overflow: 'break'` was tried and rejected (breaks inside words and numbers).
- **Fix:** `FLAECHENFAKTOR = 2.5` in `kachelBeschriftet`; test updated. Still a heuristic (RESEARCH A3).
- **Committed in:** 68d2376

**3. [Rule 1 - Bug] "1 Einträge" in descriptions and announcement**
- **Found during:** Task 2 (SSR probe)
- **Fix:** chart descriptions carry no count (UI-SPEC E7 "kein Pluraltext"); the level announcement uses "Eintrag" for 1.
- **Committed in:** 68d2376

**4. [Rule 2 - Missing critical] Surplus flag in mode Aufwand**
- **Found during:** Task 1 (tooltip draft)
- **Issue:** copying `berechnet.ueberschuss` into entries of mode Aufwand would let the tooltip print "Überschuss: {Aufwand}" for PB 11/16.
- **Fix:** `ueberschuss` is only set in mode Zuschussbedarf.
- **Committed in:** 57c9929

### Plan wording / interpretation

- **Zero line:** the plan asks for a 1 px zero line; implemented as a second, unlabelled category axis with `onZero: true` (the first axis carries the names at the left edge). Verified in an SVG render.
- **Fixed axis limits** instead of ECharts auto limits, so surplus labels fit and "axis includes 0" is testable.
- **Local `token()` helper in `AufwandTreemap.vue`** for `--wa-color-surface-default` (tile border and label colour): `echartsTheme.ts` is a shared file this wave and exports no such constant.
- **Extra props** on `EbenenTabelle`: `jahr` (header "{Wertart} {jahr}") and `beschriftung`.
- **TDD:** Task 1 is a tracer (tests and code in one commit, no RED commit); Task 2 has RED and GREEN commits, no REFACTOR commit.

**Total deviations:** 4 auto-fixed (1 blocking, 2 bugs, 1 missing critical) plus the interpretation notes above.
**Impact on plan:** none on scope; no shared files touched (`main.ts`, router, `echartsTheme.ts`, `eslint.config.ts` unchanged). No new Web Awesome imports were needed (`button`, `radio-group`, `radio`, `callout`, `icon` are already in `main.ts`).

## Issues Encountered

- The plan's `human-check` (mouse/keyboard drill-down, Back button, 360 px, striped KL tile, dots) could not run in the sandbox; it remains for the end-of-phase check. Evidence available instead: ECharts SVG renders of treemap and bars, and an SSR render of the page for seven URLs (default, mode switch, PB 11, PG 0101, KL, 2024 PB 14, invalid pb/pg).
- Not verified in a browser: `cursor` on treemap nodes, `wa-radio-group` change event, focus ring on the card heading, announcements.

## Known Stubs

None. A `/ausgaben?pb=KL&pg=KL.kreisumlage` URL (valid per `useAnsicht`) shows the empty state "Keine Unterteilung" by design.

## Threat Flags

None. T-05-26 (URL values only via validated `useAnsicht`, Map lookups, `baueEbene` throws for unknown codes, clicks checked against the current level), T-05-27 (all tooltip text through `tooltipZeilen`) and T-05-28 (values only from `berechnet`, equality tests per row and year, `ertraege` absent from `drilldown.ts`) are implemented; T-05-SC: no dependency added.

## Notes for plan 05-14 (extends AusgabenPage)

- Page layout in order: `PageIntro`, control row (`JahrUmschalter` + mode `wa-radio-group`), `ChartCard ref="karte"` (breadcrumb, treemap or bars, table), surplus `wa-callout`. The KL callout, Minderaufwand hint and the Aufwandsart card can go between the `ChartCard` and the surplus callout or after it.
- Available helpers: `ebenenElternCode`, `baueEbene`, `ueberschussTextSchluessel`; page-level refs `modus`, `eintraege`, `elternCode`, `istOberste`, `ebenenName`.

## Self-Check: PASSED

- Files exist: drilldown.ts, drilldown.test.ts, AufwandTreemap.vue, ZuschussBalken.vue, EbenenTabelle.vue, Brotkrumen.vue, ChartCard.vue, AusgabenPage.vue.
- Commits `57c9929`, `cf0793f`, `68d2376` exist.
- Scratch-copy chain after the last change: vitest 12 files / 211 tests passed, type-check, lint, format:check and build green.
- All acceptance greps pass (`nodeClick: false`, `roam: false`, `KL_DECAL`, `name: 'produkt'`, `ertraege` count 0, `aria-label="Ebene im Haushalt"`, `aria-current="location"`, callout title, `Überschuss: `, `defineExpose`).

---
*Phase: 05-leitfragen-seiten*
*Completed: 2026-10-04*
