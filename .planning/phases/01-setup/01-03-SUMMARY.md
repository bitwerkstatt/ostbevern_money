---
phase: 01-setup
plan: 03
subsystem: ui
tags: [vue3, vite, typescript, web-awesome, vue-echarts, hash-router, eslint, prettier]

# Dependency graph
requires:
  - phase: 01-setup/01-01
    provides: "Human-approved npm package list (all 21 packages installed here match the approved list verbatim)"
provides:
  - "Vue 3 + TypeScript + Vite app skeleton under app/ with green build, type-check, lint and format:check"
  - "Web Awesome wiring (self-hosted icons, German translations, wa-brand-yellow accent) reusable by all later phases"
  - "Hash router with catch-all redirect, reusable route pattern for Phase 5/6"
  - "PageIntro base component (titel/beschreibung props, default slot) per D-01/D-02 naming contract"
  - "App shell (wa-page header/content/footer, wrapping nav, Münster credit footer)"
affects: ["01-setup/01-04", "01-setup/01-05", "05-leitfragen"]

# Actuals (#2632)
actuals:
  tokens: 38500
  tasks: 2
  commits: 2
  plan_head_before: cf45a669649dff8dcbdaa50c257d7778fecec889
  plan_head_after: 6553878af21d0088db331767017a0855bf423ef7

# Tech tracking
tech-stack:
  added: ["vue@3.5.43", "vue-router@5.3.1", "vite@8.3.1", "typescript@6.0.3", "eslint@10.11.0", "echarts@6.1.0", "vue-echarts@8.3.1", "@awesome.me/webawesome@3.14.0"]
  patterns:
    - "Web Awesome custom elements wired via vite.config.ts isCustomElement + src/lib/webawesome.ts (setIconPath, de translation, styles) imported first in main.ts"
    - "Hash router (createWebHashHistory) with static StartPage import and catch-all redirect to start"
    - "Münster base-component naming/props carryover (PageIntro) — names/interfaces adopted, implementation original (D-01/D-02)"
    - "ESLint flat-config rule override (ignoreParents) for native custom-element light-DOM slotting instead of inline disables"

key-files:
  created:
    - "app/package.json"
    - "app/package-lock.json"
    - "app/.nvmrc"
    - "app/index.html"
    - "app/vite.config.ts"
    - "app/eslint.config.ts"
    - "app/tsconfig.json"
    - "app/tsconfig.app.json"
    - "app/tsconfig.node.json"
    - "app/env.d.ts"
    - "app/.gitignore"
    - "app/.gitattributes"
    - "app/.prettierrc.json"
    - "app/.editorconfig"
    - "app/.vscode/extensions.json"
    - "app/.vscode/settings.json"
    - "app/public/favicon.ico"
    - "app/src/main.ts"
    - "app/src/App.vue"
    - "app/src/router/index.ts"
    - "app/src/lib/webawesome.ts"
    - "app/src/styles/basis.css"
    - "app/src/pages/StartPage.vue"
    - "app/src/components/PageIntro.vue"
    - "app/src/data/jahrgang.json"
    - "app/public/icons/solid/circle-info.svg"
    - "app/public/icons/solid/triangle-exclamation.svg"
    - "app/public/icons/solid/bars.svg"
  modified: []

key-decisions:
  - "oxlint, eslint-plugin-oxlint, vite-plugin-vue-devtools stripped from the create-vue scaffold before npm install, per 01-01's approved package list and D-15/D-16 (ESLint-only)"
  - "app/.vscode/settings.json force-added despite the scaffold's own .gitignore excluding .vscode/* (except extensions.json) — the plan's frontmatter explicitly lists this file under files_modified, intended for consistent format-on-save across contributors"
  - "vue/no-deprecated-slot-attribute scoped off for children of wa-page via eslint.config.ts ignoreParents, not inline disables — wa-page is a native custom element using light-DOM slot attributes, not Vue 2's deprecated slot syntax"

patterns-established:
  - "Pattern: Web Awesome bootstrap order — lib/webawesome.ts (styles + de translation + setIconPath) imported before styles/basis.css and before any dist/components/*/*.js registration, so icon path is set before any component evaluates"
  - "Pattern: single source of truth for year data — app/src/data/jahrgang.json is the only place the haushaltsjahr value is typed; StartPage interpolates it, no .vue/.ts file hardcodes 2026"

requirements-completed: [SETUP-03, QUAL-01]

coverage:
  - id: D1
    description: "Vue 3 app skeleton (TS, Vite, Web Awesome, vue-echarts, hash router) scaffolds and builds"
    requirement: "SETUP-03"
    verification:
      - kind: other
        ref: "npm --prefix app run build (vue-tsc --build + vite build)"
        status: pass
    human_judgment: false
  - id: D2
    description: "vue-tsc and ESLint run clean in the CI scripts (type-check, lint, format:check)"
    requirement: "QUAL-01"
    verification:
      - kind: other
        ref: "npm --prefix app run type-check"
        status: pass
      - kind: other
        ref: "npm --prefix app run lint"
        status: pass
      - kind: other
        ref: "npm --prefix app run format:check"
        status: pass
    human_judgment: false
  - id: D3
    description: "StartPage renders PageIntro with the year sourced from jahrgang.json through the hash router; unknown hash routes redirect to start"
    requirement: "SETUP-03"
    verification:
      - kind: other
        ref: "Task 1 acceptance criteria (grep assertions for createWebHashHistory, pathMatch catch-all, no hardcoded 2026 in src) + build"
        status: pass
    human_judgment: false
  - id: D4
    description: "App shell (wa-page header/nav/footer, Münster credit, Ostbevern-Gold accent, self-hosted icons, wrapping nav at 360px) renders correctly and makes no third-party network requests"
    requirement: "SETUP-03"
    verification:
      - kind: other
        ref: "Task 2 acceptance criteria (grep assertions for lang/brand-yellow/credit-link/flex-wrap/no-hex-colors/single-host) + build"
        status: pass
    human_judgment: true
    rationale: "360px responsive layout, gold accent rendering, active-nav-link color and the absence of third-party network requests in DevTools require visual/browser confirmation (Task 2's <verify><human-check>). Per workflow.human_verify_mode=end-of-phase, this check is harvested at end-of-phase UAT rather than executed as a runtime checkpoint by this executor."

# Metrics
duration: 35 min
completed: 2026-10-01
status: complete
---

# Phase 1 Plan 3: App Scaffold Summary

**Vue 3 + TypeScript + Vite app under `app/` with Web Awesome 3.14.0 (self-hosted icons, German translations, Ostbevern-Gold accent), vue-echarts, hash router with catch-all redirect, and a Münster-named `PageIntro` base component — build, type-check, lint and format:check all green.**

## Performance

- **Duration:** 35 min
- **Started:** 2026-10-01T11:12:00Z
- **Completed:** 2026-10-01T11:47:00Z
- **Tasks:** 2
- **Files modified:** 28 (all newly created — `app/` did not exist before this plan)

## Accomplishments

- Scaffolded `app/` with `npm create vue@3.24.0 -- --ts --router --eslint --prettier --bare`, stripped the unaudited oxlint/vite-plugin-vue-devtools extras per the 01-01 approval
- Installed echarts, vue-echarts and `@awesome.me/webawesome` exactly as approved; `vite.config.ts` wired with `isCustomElement` for `wa-*` tags
- `src/lib/webawesome.ts` sets up self-hosted icons (`setIconPath`), German UI translations and WA styles, imported first in `main.ts` before any component registration
- Hash router (`createWebHashHistory`) with a `start` route and a catch-all redirect back to start
- `PageIntro` base component written fresh with Münster's `titel`/`beschreibung` props and default slot (D-01/D-02); `StartPage` renders it with the year sourced from `src/data/jahrgang.json`
- App shell: `wa-page` with header (site name + wrapping nav), content and footer (Münster credit link to `codeformuenster/haushalt-muenster-2026`), gold accent via `wa-brand-yellow`, three self-hosted Font Awesome solid icons with their license headers intact
- Node 22 pin (`.nvmrc`, `engines.node`) and the four CI scripts (`lint`, `lint:fix`, `format`, `format:check`) plus the scaffold's `type-check`/`build`
- `npm run build`, `type-check`, `lint` and `format:check` all exit 0

## Task Commits

Each task was committed atomically:

1. **Task 1: Tracer — scaffold -> Web Awesome wiring -> hash router -> StartPage with PageIntro -> build** - `9ae2bb0` (feat)
2. **Task 2: App shell — wa-page with wrapping nav, Münster credit footer, German language, Ostbevern-Gold, self-hosted icons, Node 22 pin, CI scripts** - `6553878` (feat)

**Plan metadata:** commit created immediately after this SUMMARY (see below).

## Files Created/Modified

- `app/package.json` — scripts (`dev`, `build`, `build-only`, `preview`, `type-check`, `lint`, `lint:fix`, `format`, `format:check`), `engines.node: ^22.18.0`, name `ostbevern-money-app`
- `app/package-lock.json` — locked dependency tree for the approved package list
- `app/vite.config.ts` — `isCustomElement` for `wa-*` tags, `@` alias
- `app/eslint.config.ts` — oxlint stripped; `ignoreParents: ['wa-page']` override for `vue/no-deprecated-slot-attribute`
- `app/src/lib/webawesome.ts` — WA styles, brand.css, `de` translation, `setIconPath`
- `app/src/main.ts` — import order: webawesome → basis.css → component registrations (page, callout, icon, skeleton, format-number) → app mount
- `app/src/App.vue` — `wa-page` shell: header (site name + nav), `RouterView`, footer (Münster credit)
- `app/src/router/index.ts` — `createWebHashHistory`, `start` route, catch-all redirect
- `app/src/components/PageIntro.vue` — `titel`/`beschreibung` props, default slot, WA typography tokens
- `app/src/pages/StartPage.vue` — renders `PageIntro` with year from `jahrgang.json`
- `app/src/data/jahrgang.json` — `{ "haushaltsjahr": 2026 }`
- `app/src/styles/basis.css` — `color-scheme: light`, `.om-zahl`, `.om-visually-hidden`
- `app/public/icons/solid/{circle-info,triangle-exclamation,bars}.svg` — self-hosted Font Awesome Free SVGs with license comments
- `app/.nvmrc` — `22`
- `app/index.html` — `lang="de"`, `wa-brand-yellow`, title, description
- Scaffold passthrough files (tsconfig*.json, env.d.ts, .gitignore, .gitattributes, .prettierrc.json, .editorconfig, .vscode/*, public/favicon.ico)

## Decisions Made

- Kept the scaffold's TypeScript `~6.0.x` pin and vue-router major 5, per the 01-01 approval's drift policy (no new major accepted without re-approval)
- Force-added `app/.vscode/settings.json` despite the scaffold's own `.gitignore` excluding `.vscode/*` (except `extensions.json`) — the plan's frontmatter explicitly names this file, intended for consistent Prettier format-on-save across contributors
- Scoped `vue/no-deprecated-slot-attribute` off for `wa-page` children via ESLint flat-config `ignoreParents`, rather than inline `eslint-disable` comments, since `wa-page`'s light-DOM `slot` attribute is native custom-element behavior, not Vue 2's deprecated directive

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] ESLint false-flagged native custom-element slot attributes as deprecated Vue 2 syntax**
- **Found during:** Task 2 (`npm run lint` after writing the `wa-page` shell)
- **Issue:** `vue/no-deprecated-slot-attribute` flagged `slot="header"`/`slot="footer"` on the shell's `<div>` children of `<wa-page>` as the deprecated Vue 2 slot syntax. These are correct native HTML `slot` attributes for light-DOM slotting into a Web Awesome custom element (`wa-page` is not a Vue SFC component), not Vue directives.
- **Fix:** Added a scoped ESLint rule override in `eslint.config.ts` — `'vue/no-deprecated-slot-attribute': ['error', { ignoreParents: ['wa-page'] }]` — rather than an inline disable, per the plan's "clean without disabling rules inline" instruction.
- **Files modified:** `app/eslint.config.ts`
- **Verification:** `npm run lint` exits 0 with zero findings
- **Committed in:** `6553878` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug/correctness fix). **Impact:** Necessary for `npm run lint` to pass per the plan's own verify step; no scope creep — the rule override is narrowly scoped to `wa-page`'s children only.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `app/` builds, type-checks, lints and format-checks cleanly with the exact script names CI (01-05) will call
- `PageIntro` is the first of the Münster base components (D-03); `ChartCard`, `BaseChart`, `DatenTabelle`, `charts/format.ts`, `charts/echartsTheme.ts`, `lib/bildschirm.ts` remain for plan 01-04
- The app shell's nav currently has one item ("Start") — flagged in the plan as an unresolved zero-one-many assumption for Phase 5/6 route growth
- No blockers or concerns

---
*Phase: 01-setup*
*Completed: 2026-10-01*

## Self-Check: PASSED

- `FOUND: app/src/components/PageIntro.vue`
- `FOUND: app/src/router/index.ts`
- `FOUND: app/src/lib/webawesome.ts`
- `FOUND: app/src/App.vue`
- `FOUND: app/src/data/jahrgang.json`
- `FOUND: app/.nvmrc`
- `FOUND: app/public/icons/solid/bars.svg`
- `FOUND: 9ae2bb0` — commit exists in `git log --oneline --all`
- `FOUND: 6553878` — commit exists in `git log --oneline --all`
- Commit ledger: `plan_head_before=cf45a669649dff8dcbdaa50c257d7778fecec889`, `plan_head_after=6553878af21d0088db331767017a0855bf423ef7`, `git rev-list --count` = 2 (matches `actuals.commits: 2`)
- Acceptance criteria re-verified: all Task 1 and Task 2 acceptance criteria greps passed (see Task Commits); `npm --prefix app run build`, `type-check`, `lint`, `format:check` all exit 0
