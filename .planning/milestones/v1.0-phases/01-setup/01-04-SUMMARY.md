---
phase: 01-setup
plan: 04
subsystem: ui
tags: [vue3, echarts, vue-echarts, web-awesome, typescript, accessibility]

# Dependency graph
requires:
  - phase: 01-setup/01-03
    provides: "App scaffold under app/ (Vue 3 + TS + Vite + Web Awesome + vue-echarts, hash router, PageIntro base component, app shell)"
provides:
  - "Münster base components for number/chart/table rendering: charts/format.ts, charts/echartsTheme.ts, BaseChart.vue, ChartCard.vue, DatenTabelle.vue, lib/bildschirm.ts (plus support modules chartKontext.ts, datenTabelle.ts)"
  - "A real demo use on the start page: fictional beispieldaten.json flows through format.ts/echartsTheme.ts into a ChartCard-wrapped BaseChart and DatenTabelle, with a second ChartCard showing the empty state"
affects: ["05-leitfragen", "07-feinschliff"]

# Actuals (#2632)
actuals:
  tokens: 5500
  tasks: 3
  commits: 3
  plan_head_before: b3b58b86d4d64deb93ba2d6b4a43601e591e03eb
  plan_head_after: 3e8eb40d928aaa70ad0765263ae621394d73e99e

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "charts/format.ts: single source of number formatting — all Intl.NumberFormat instances created once at module load, every displayed number routes through euro/euroKurz/zahl/vzae/prozent or wa-format-number configured from EURO_OPTIONEN (UI-05)"
    - "charts/echartsTheme.ts: reads Web Awesome CSS custom properties via getComputedStyle at module load (with hex fallbacks copied from the installed WA CSS), registers only the echarts renderer/chart-types/components actually used (on-demand imports), registers the 'ostbevern-money' theme once"
    - "ChartCard provides CHART_KONTEXT (titelId + beschreibungId()); BaseChart and (future) slot content inject it for aria-labelledby when no own beschreibung/aria-label is given"
    - "A page cannot show beispieldaten without the mandatory notice: ChartCard itself renders the callout when beispieldaten=true, not the page — verified by a negative grep (StartPage.vue no longer contains the notice text) and a positive one (ChartCard.vue does)"
    - "BaseChart/DatenTabelle state priority: loading (wa-skeleton) > error > empty ('Noch keine Daten') > populated — never an empty/broken canvas or table"
    - "DatenTabelle data mode: SpaltenArt-typed columns (text/euro/zahl/prozent), euro columns read their currency/fraction-digit config from format.ts's EURO_OPTIONEN so wa-format-number and format.ts never drift apart"
    - "useSchmalerBildschirm(): matchMedia-backed readonly ref, listener cleanup via onScopeDispose, SSR-safe (false ref when window is undefined) — used by StartPage to swap chart orientation at the 699px floor"

key-files:
  created:
    - "app/src/charts/format.ts"
    - "app/src/charts/echartsTheme.ts"
    - "app/src/components/BaseChart.vue"
    - "app/src/components/ChartCard.vue"
    - "app/src/components/chartKontext.ts"
    - "app/src/components/DatenTabelle.vue"
    - "app/src/components/datenTabelle.ts"
    - "app/src/lib/bildschirm.ts"
    - "app/src/data/beispieldaten.json"
  modified:
    - "app/src/pages/StartPage.vue"
    - "app/eslint.config.ts"

key-decisions:
  - "echartsTheme.ts registers only CanvasRenderer, BarChart, GridComponent, TooltipComponent (on-demand imports per RESEARCH Pattern 5); later phases add further chart types to this one file rather than importing the full echarts bundle"
  - "ChartCard's pdf prop is { seite: number } (Münster's { band, seite} narrowed) since Ostbevern has exactly one PDF, per the plan's interfaces block"
  - "DatenTabelle keeps Münster's slot mode (beschriftung + default slot) for forward compatibility and adds a typed data mode (spalten/zeilen) for this phase's demo table and later phases' Langformat tables"
  - "Null cell values in DatenTabelle data mode render visually empty with a visually-hidden 'kein Wert' announcement — flagged as an explicit Phase 1 assumption (UI-SPEC E5 partial) pending Phase 2+'s knowledge of which values can actually be absent"

patterns-established:
  - "Pattern: WA token fallback helper — a private token(name, ersatz) in echartsTheme.ts reads getComputedStyle at call time with a documented hex fallback, reused by any future theme-reading module instead of hardcoding a second palette"
  - "Pattern: mandatory disclosure ownership — a flag prop (beispieldaten) on the chrome component (ChartCard) renders the compliance copy itself, so no page-level call site can accidentally omit it"

requirements-completed: [SETUP-03, QUAL-01]

coverage:
  - id: D1
    description: "format.ts is the single source of number formatting (euro, euroKurz, zahl, vzae, prozent, EURO_OPTIONEN) and matches the plan's golden values exactly"
    requirement: "SETUP-03"
    verification:
      - kind: other
        ref: "node -e transpile+eval check against format.ts (Task 1 <verify>, re-run after Task 3's comment-only edit)"
        status: pass
    human_judgment: false
  - id: D2
    description: "echartsTheme.ts registers CanvasRenderer/BarChart/GridComponent/TooltipComponent on demand (no full-library import) and registers the ostbevern-money theme reading WA tokens"
    requirement: "SETUP-03"
    verification:
      - kind: other
        ref: "Task 1 acceptance criteria (grep assertions for registerTheme/echarts/core import/no full-library import) + build"
        status: pass
    human_judgment: false
  - id: D3
    description: "BaseChart renders the chart, loading skeleton, error state, or 'Noch keine Daten' empty state in correct priority order, never a broken/empty canvas"
    requirement: "SETUP-03"
    verification:
      - kind: other
        ref: "Task 2 acceptance criteria (grep assertions for wa-skeleton/error copy/empty copy) + build; empty-state ChartCard on StartPage exercises the empty branch at build/type-check time"
        status: pass
    human_judgment: true
    rationale: "Visual rendering of the three BaseChart states (skeleton shimmer, error icon/copy layout, empty-state centering) and the loading/error backstop truths flagged 'verification: backstop' in the plan's must_haves require a browser. Per workflow.human_verify_mode=end-of-phase, harvested at end-of-phase UAT rather than executed as a runtime checkpoint by this executor."
  - id: D4
    description: "ChartCard renders title/description/source/pdf chrome and is the sole renderer of the mandatory Beispieldaten notice (a page cannot show flagged demo data without it)"
    requirement: "SETUP-03"
    verification:
      - kind: other
        ref: "Task 2 acceptance criteria (positive grep in ChartCard.vue, negative grep in StartPage.vue, :beispieldaten= wiring) + build"
        status: pass
    human_judgment: false
  - id: D5
    description: "DatenTabelle renders an accessible, scrollable table with sticky label column, formatted amounts via EURO_OPTIONEN, loading/empty states, and bildschirm.ts swaps the demo chart to horizontal bars on narrow screens"
    requirement: "QUAL-01"
    verification:
      - kind: other
        ref: "Task 3 acceptance criteria (full grep suite incl. no-toLocaleString, no-raw-hex, no-v-html, exact D-03 component-directory check) + type-check/lint/format:check/build all exit 0"
        status: pass
    human_judgment: true
    rationale: "360px responsive behaviour (horizontal bars, wrapping callout, scrollable table with sticky column, no page-level horizontal scroll) requires a browser/DevTools viewport check — the plan's own Task 3 <verify><human-check>. Per workflow.human_verify_mode=end-of-phase, harvested at end-of-phase UAT."

# Metrics
duration: 48 min
completed: 2026-10-01
status: complete
---

# Phase 1 Plan 4: Münster Base Components Summary

**The remaining Münster base modules (`format.ts`, `echartsTheme.ts`, `BaseChart`, `ChartCard`, `DatenTabelle`, `lib/bildschirm.ts`) built fresh and wired end-to-end on the start page through a fictional, clearly-flagged demo dataset — chart and table alternative, loading/error/empty states, and narrow-screen chart-orientation swap, all green on build/type-check/lint/format:check.**

## Performance

- **Duration:** 48 min
- **Started:** 2026-10-01T12:05:00Z
- **Completed:** 2026-10-01T12:53:00Z
- **Tasks:** 3
- **Files modified:** 11 (9 created, 2 modified)

## Accomplishments

- `charts/format.ts` written fresh as the single source of number formatting (`euro`, `euroKurz`, `zahl`, `vzae`, `prozent`, `EURO_OPTIONEN`), verified byte-for-byte against the plan's golden values via a Node transpile+eval check
- `charts/echartsTheme.ts` registers only the echarts pieces the app uses (`CanvasRenderer`, `BarChart`, `GridComponent`, `TooltipComponent`) and builds the `ostbevern-money` theme by reading Web Awesome CSS custom properties at runtime, with documented hex fallbacks — no second hardcoded palette
- `BaseChart.vue` wraps `vue-echarts` with `option`/`hoehe`/`beschreibung` props, a `chartClick` emit, and `laedt`/`fehler`/empty-series states rendered in strict priority (skeleton > error > empty > chart), injecting `ChartCard`'s `CHART_KONTEXT` for `aria-labelledby` when no own description is given
- `ChartCard.vue` provides the card chrome (title/description/source/pdf) and is the sole renderer of the mandatory "Beispieldaten — noch keine echten Haushaltszahlen." notice — a page can flag demo data but cannot omit the disclosure
- `DatenTabelle.vue` + `datenTabelle.ts` add a typed data mode (`spalten`/`zeilen`, `SpaltenArt` = text/euro/zahl/prozent) alongside Münster's slot mode, with a sticky label column, `wa-format-number` cells configured from `format.ts`'s `EURO_OPTIONEN`, loading skeleton rows and the shared "Noch keine Daten" empty state
- `lib/bildschirm.ts` exports `SCHMAL_BIS = 699` and `useSchmalerBildschirm()`, a `matchMedia`-backed readonly ref with `onScopeDispose` cleanup, used on the start page to swap the demo bar chart to horizontal orientation below 700px
- `StartPage.vue` now renders two `ChartCard`s: the flagged Beispieldaten chart + table, and an "Echte Haushaltszahlen" card exercising `BaseChart`'s empty state with a real (non-demo) title and no data
- `npm --prefix app run type-check`, `lint`, `format:check` and `build` all exit 0; the Task 1 format golden-value check prints `format ok`

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — Beispieldaten -> format.ts -> echartsTheme.ts -> BaseChart -> StartPage, one chart** - `98e072e` (feat)
2. **Task 2: ChartCard with mandatory Beispieldaten notice, chart context, and BaseChart loading/error/empty states** - `5774659` (feat)
3. **Task 3: DatenTabelle (slot and data mode) and bildschirm.ts, wired as the chart's table alternative** - `3e8eb40` (feat)

**Plan metadata:** commit created immediately after this SUMMARY (see below).

## Files Created/Modified

- `app/src/charts/format.ts` — `LOCALE`, `EURO_OPTIONEN`, `euro()`, `euroKurz()`, `zahl()`, `vzae()`, `prozent()`
- `app/src/charts/echartsTheme.ts` — `CHART_THEME`, `KATEGORIE_FARBEN`, `SEQUENZ_FARBEN`, `POL_FARBEN`; registers renderer/chart types/theme at module load
- `app/src/components/BaseChart.vue` — props `option`, `hoehe`, `beschreibung`, `laedt`, `fehler`; emit `chartClick`; slot `fehler`
- `app/src/components/ChartCard.vue` — props `titel`, `beschreibung`, `quelle`, `pdf { seite }`, `beispieldaten`; default slot, slot `fuss`; provides `CHART_KONTEXT`
- `app/src/components/chartKontext.ts` — `ChartKontext` interface, `CHART_KONTEXT` injection key
- `app/src/components/DatenTabelle.vue` — props `beschriftung`, `spalten`, `zeilen`, `laedt`; default slot (slot mode) and data mode
- `app/src/components/datenTabelle.ts` — `SpaltenArt`, `DatenSpalte`, `DatenZeile`
- `app/src/lib/bildschirm.ts` — `SCHMAL_BIS`, `useSchmalerBildschirm()`
- `app/src/data/beispieldaten.json` — fields `beispieldaten`, `titel`, `posten[{ name, wert }]`
- `app/src/pages/StartPage.vue` — wires everything above into two `ChartCard`s (demo + empty)
- `app/eslint.config.ts` — `ignoreParents` widened from `['wa-page']` to `['wa-page', 'wa-callout']`

## Decisions Made

- Kept `echartsTheme.ts`'s registered chart-type set minimal (`BarChart` only) per Anti-Pattern guidance in RESEARCH — later phases add `PieChart`/`TreemapChart`/etc. to this one file as needed
- `ChartCard`'s `pdf` prop narrowed to `{ seite: number }` (Münster's `{ band, seite }` drops `band`) since Ostbevern has exactly one PDF
- `DatenTabelle`'s null-cell rendering (visually empty + visually-hidden "kein Wert") is an explicit Phase 1 assumption per UI-SPEC's E5 partial — may be revisited once Phase 2+ pipeline output defines which cells can actually be absent

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `vue/no-deprecated-slot-attribute` false-flagged `wa-callout`'s native slot attribute**
- **Found during:** Task 3 (`npm run lint` after writing `ChartCard.vue`'s `wa-icon slot="icon"` inside `wa-callout`)
- **Issue:** The existing `ignoreParents: ['wa-page']` override from 01-03 did not cover `wa-callout`, another native Web Awesome custom element using the native HTML `slot` attribute for light-DOM slotting — not Vue 2's deprecated directive.
- **Fix:** Widened the existing override to `ignoreParents: ['wa-page', 'wa-callout']` in `app/eslint.config.ts`, following the same pattern 01-03 established rather than an inline disable.
- **Files modified:** `app/eslint.config.ts`
- **Verification:** `npm run lint` exits 0 with zero findings
- **Committed in:** `3e8eb40` (Task 3 commit)

**2. [Rule 1 - Bug] `format.ts`'s own header comment tripped Task 3's "no per-component number formatting" acceptance check**
- **Found during:** Task 3 acceptance criteria (`grep -rl 'toLocaleString' app/src` expected to find nothing)
- **Issue:** `format.ts`'s header comment explained what NOT to do by naming `toLocaleString()` literally, which the grep-based acceptance check (correctly) cannot distinguish from actual usage.
- **Fix:** Reworded the comment to describe the same constraint ("niemals mit einer eigenen, pro Komponente duplizierten Formatierungslogik") without the literal string. No functional change; the Task 1 golden-value check was re-run and still prints `format ok`.
- **Files modified:** `app/src/charts/format.ts`
- **Verification:** `grep -rl 'toLocaleString' app/src` now empty; format golden-value check re-run, passes; full build/type-check/lint/format:check re-run, all green
- **Committed in:** `3e8eb40` (Task 3 commit)

---

**Total deviations:** 2 auto-fixed (2 bug/correctness fixes, both minimal-scope). **Impact:** Both fixes necessary for the plan's own verify/acceptance gates to pass; no scope creep — one widens an existing, narrowly-scoped lint override by one tag, the other is a comment-only edit.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- All seven Münster base components named in D-03 now exist: `PageIntro` (01-03), `ChartCard`, `BaseChart`, `DatenTabelle`, `charts/format.ts`, `charts/echartsTheme.ts`, `lib/bildschirm.ts` — and nothing else in `app/src/components` (verified by an exact directory-listing acceptance check)
- `StartPage.vue` demonstrates the full chart+table+empty-state pattern later phases (05-leitfragen) will reuse for real budget data
- The two visual/responsive truths flagged `human_judgment: true` above (D3's BaseChart state rendering, D5's 360px responsive behaviour) are queued for end-of-phase UAT per `workflow.human_verify_mode=end-of-phase` — not yet manually verified in a browser
- `echartsTheme.ts` currently registers only `BarChart`; Phase 5/6 will need to add further series types (e.g. `TreemapChart`, Sankey) to this same file when those visualisations are built
- No blockers or concerns

---
*Phase: 01-setup*
*Completed: 2026-10-01*

## Self-Check: PASSED

- `FOUND: app/src/charts/format.ts`
- `FOUND: app/src/charts/echartsTheme.ts`
- `FOUND: app/src/components/BaseChart.vue`
- `FOUND: app/src/components/ChartCard.vue`
- `FOUND: app/src/components/chartKontext.ts`
- `FOUND: app/src/components/DatenTabelle.vue`
- `FOUND: app/src/components/datenTabelle.ts`
- `FOUND: app/src/lib/bildschirm.ts`
- `FOUND: app/src/data/beispieldaten.json`
- `FOUND: 98e072e` — commit exists in `git log --oneline --all`
- `FOUND: 5774659` — commit exists in `git log --oneline --all`
- `FOUND: 3e8eb40` — commit exists in `git log --oneline --all`
- Commit ledger: `plan_head_before=b3b58b86d4d64deb93ba2d6b4a43601e591e03eb`, `plan_head_after=3e8eb40d928aaa70ad0765263ae621394d73e99e`, `git rev-list --count` = 3 (matches `actuals.commits: 3`)
- Acceptance criteria re-verified: all Task 1, Task 2 and Task 3 acceptance criteria greps re-run and passed (see Task Commits); `npm --prefix app run type-check`, `lint`, `format:check`, `build` all exit 0; format golden-value check prints `format ok`
