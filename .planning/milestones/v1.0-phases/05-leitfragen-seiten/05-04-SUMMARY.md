---
phase: 05-leitfragen-seiten
plan: 04
subsystem: ui
tags: [vue-router, hash-router, url-state, web-awesome, accessibility, vitest]

requires:
  - phase: 05-leitfragen-seiten
    provides: "05-01 vitest runner (npm run test), formatiere fallback"
provides:
  - "lib/jahr.ts: leseJahr allowlist parser, WERTART_NAMEN/wertartName/wertartFuerJahr, useJahr (jahr, index, wertart, setzeJahr, jahrLink), jahrLinkFuer"
  - "lib/ansicht.ts: Modus/Ansicht types, leseAnsicht, bereinigteQuery, findeKnoten, findeProdukt, useAnsicht (ansicht, setzeModus, oeffne, zurueck, ansichtsQuery)"
  - "lib/ansage.ts: ansagen(text) polite live region"
  - "JahrUmschalter (wa-radio-group with wa-radio appearance=button from 700 px, wa-select up to 699 px) with Wertart label and explanation; WertartEtikett"
  - "Router with six named routes, RouteMeta.titel, scrollBehavior, afterEach (title, focus, announcement)"
  - "Page shells EinnahmenPage, AusgabenPage, ProduktPage (not-found state), GeldflussPage, GlossarPage"
affects: [05-07, 05-08, 05-09, 05-10, 05-11, 05-12, 05-13, 05-14, 05-15, phase-06]

actuals:
  tokens: 8800
  tasks: 3
  commits: 5
plan_head_before: 8403a43b4a14a6ce43ab467307a65386035a8b01
plan_head_after: f3d6630aa4539c0b8ff7f3cec9e11f4cec5f6d76

tech-stack:
  added: []
  patterns:
    - "URL as single source of truth: composables read route.query defensively through allowlists (haushalt.jahre, Map/Set of knoten/produkt codes) and clean invalid parts with router.replace"
    - "URL-derived strings are only ever looked up in Map/Set, never used as plain-object keys; query copies use Object.fromEntries"
    - "Pure parsers (leseJahr, leseAnsicht, bereinigteQuery, jahrLinkFuer) are unit-tested; composables are thin wrappers"
    - "Year/Wertart text always from haushalt.json via format.jahr(); no year literal in components"

key-files:
  created:
    - app/src/lib/jahr.ts
    - app/src/lib/ansicht.ts
    - app/src/lib/ansage.ts
    - app/src/lib/__tests__/jahr.test.ts
    - app/src/lib/__tests__/ansicht.test.ts
    - app/src/components/JahrUmschalter.vue
    - app/src/components/WertartEtikett.vue
    - app/src/pages/EinnahmenPage.vue
    - app/src/pages/AusgabenPage.vue
    - app/src/pages/ProduktPage.vue
    - app/src/pages/GeldflussPage.vue
    - app/src/pages/GlossarPage.vue
  modified:
    - app/src/router/index.ts
    - app/src/main.ts
    - app/src/components/PageIntro.vue
    - app/eslint.config.ts

key-decisions:
  - "Invalid ?jahr= is removed from the URL (not rewritten to the Haushaltsjahr); the page shows the Haushaltsjahr meanwhile"
  - "jahrLink only propagates an explicit valid year; pure logic lives in the exported jahrLinkFuer(ziel, jahr|null) so it is testable without a router"
  - "useAnsicht.zurueck(ebene) takes the code of the breadcrumb target (GESAMT, the current pb); other codes are ignored"
  - "Page title and 'Seite {Titel} geladen' for /produkt/:code come from the router (product name or 'Dieses Produkt gibt es nicht') instead of a watcher inside ProduktPage, so title and announcement agree and cannot race the afterEach hook"
  - "scrollBehavior returns false for same-path changes and honours a saved position, so a year/mode switch never jumps to the top"
  - "afterEach only sets the title on the very first navigation (START_LOCATION); focus and announcement are left to the browser then"

patterns-established:
  - "RED commit for TDD tasks includes a signature-only stub so the target tests fail on assertions (21 of 29), not on a missing import"
  - "Scratch-copy workflow: rsync app/ (without node_modules) into the scratch dir, run the app chain there, run prettier --write there and copy the formatted file back"

requirements-completed: [UI-01, AUSG-05]

coverage:
  - id: D1
    description: "?jahr= end to end: useJahr parses via allowlist from haushalt.jahre, invalid values (abc, 2023, 2030, empty, __proto__) fall back to the Haushaltsjahr and are removed with router.replace; JahrUmschalter writes the year with router.replace"
    requirement: UI-01
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/jahr.test.ts#leseJahr (UI-01, D-10)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Year list and Wertart names come from haushalt.jahre/haushalt.wertarten (ergebnis -> Ist, ansatz -> Ansatz, planung -> Planung); no year literal in JahrUmschalter"
    requirement: UI-01
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/jahr.test.ts#wertartName, #wertartFuerJahr"
        status: pass
      - kind: other
        ref: "grep -cE '20[0-9]{2}' app/src/components/JahrUmschalter.vue prints 0"
        status: pass
    human_judgment: false
  - id: D3
    description: "Validated Ausgaben view state: modus only from {aufwand, zuschussbedarf}, pb only as direct child of GESAMT (incl. KL), pg only under pb, product code only from produkte; Map/Set lookups only"
    requirement: AUSG-05
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/ansicht.test.ts#leseAnsicht (D-06, D-09), #findeKnoten, #findeProdukt (AUSG-05)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Six named routes before the catch-all; /produkt/<unknown> renders the not-found state in the route itself (no redirect), code shown as text"
    requirement: AUSG-05
    verification:
      - kind: other
        ref: "grep acceptance criteria (6 route names, path /produkt/:code, 'Dieses Produkt gibt es nicht') plus vue-tsc/eslint/prettier/vite build in scratch copy"
        status: pass
    human_judgment: true
    rationale: "Rendering of the not-found callout and the redirect-vs-page behaviour needs a browser; the plan's human-check step could not be run in this sandbox"
  - id: D5
    description: "Route change handling: document.title '{Titel} – Ostbevern Money', focus on h1 (tabindex -1) or hash target, polite announcement, focus kept on pure query changes, JahrUmschalter announcement 'Zeige {Wertart} {jahr}' with focus staying on the control"
    requirement: UI-01
    verification: []
    human_judgment: true
    rationale: "Focus movement, screen-reader announcements and Web Awesome event wiring (change event on wa-radio-group/wa-select, wa-details) are DOM/AT behaviour with no browser available here; covered by the plan's human-check at end of phase"

duration: 9min
completed: 2026-10-04
status: complete
---

# Phase 5 Plan 04: URL-State Backbone Summary

**Hash router with six named routes, a validated `?jahr=` year switch (Wertart labels from haushalt.json), allowlist-checked `modus`/`pb`/`pg`/product-code state, and title/focus/live-region handling after every page change**

## Performance

- **Duration:** 9 min
- **Started:** 2026-10-04T12:51:26Z
- **Completed:** 2026-10-04T13:00:18Z
- **Tasks:** 3
- **Files modified:** 16 (12 created, 4 modified)

## Accomplishments
- `useJahr()` makes `?jahr=` the single source of truth: only digits that are in `haushalt.jahre` are accepted, everything else (`abc`, `2023`, `2030`, empty, `__proto__`, bare `?jahr`) falls back to the Haushaltsjahr and is removed with `router.replace`. `jahrLink` carries an explicit valid year into internal links.
- `JahrUmschalter` renders a `wa-radio-group` of `wa-radio appearance="button"` from 700 px and a `wa-select` up to 699 px, option text "{jahr} · {Wertart}", 44 px target heights, neutral `WertartEtikett`, a closed `wa-details` "Was bedeuten Ist, Ansatz und Planung?" (mentions the vorläufiges Rechnungsergebnis of the first Ist year, taken from data) and a polite "Zeige {Wertart} {jahr}" announcement.
- `lib/ansicht.ts` validates `modus`, `pb`, `pg` and product codes through `Map`/`Set` built from the data (prototype keys such as `__proto__`/`constructor`/`toString` are rejected) and offers `useAnsicht` with replace for the mode and push for drilldown.
- Router: `start`, `einnahmen`, `ausgaben`, `produkt` (`/produkt/:code`), `geldfluss`, `glossar` before the catch-all; `/produkt/<unknown>` stays on a not-found page. `scrollBehavior` scrolls to an existing hash element and leaves the position alone on query-only changes. `afterEach` sets the title, focuses the h1 (or the hash target) and announces "Seite {Titel} geladen".

## Task Commits

1. **Task 1: Tracer, ?jahr= end to end** - `22b3de0` (feat)
2. **Task 2: Wertart label, live announcements, validated view state (TDD)**
   - RED `1ab6dd0` (test) - 21 of 29 tests fail on assertions
   - GREEN `c2a665c` (feat)
   - REFACTOR `3c2792d` (refactor) - one `ohne()` helper replaces four inline filters
3. **Task 3: Remaining routes as shells, title, focus, hash target** - `f3d6630` (feat)

**Plan metadata:** committed with this SUMMARY (docs: complete plan)

## Files Created/Modified
- `app/src/lib/jahr.ts` - year parsing, Wertart names, `useJahr`, `jahrLinkFuer`
- `app/src/lib/ansicht.ts` - validated Ausgaben state, node/product lookup, `useAnsicht`
- `app/src/lib/ansage.ts` - polite live region
- `app/src/components/JahrUmschalter.vue`, `WertartEtikett.vue` - year switch and Wertart tag
- `app/src/router/index.ts` - routes, `RouteMeta.titel`, `scrollBehavior`, `afterEach`
- `app/src/pages/*Page.vue` (Einnahmen, Ausgaben, Produkt, Geldfluss, Glossar) - shells with final titles and leads
- `app/src/main.ts` - Web Awesome imports (button, details, tooltip, drawer, radio-group, radio, select, option, tag, card, divider); shared file, touched additively
- `app/src/components/PageIntro.vue` - h1 `tabindex="-1"`
- `app/eslint.config.ts` - `ignoreParents` extended (wa-details, wa-drawer, wa-card, wa-select, wa-button, wa-radio-group, wa-tooltip, wa-tag)
- `app/src/lib/__tests__/jahr.test.ts` (32 tests), `ansicht.test.ts` (29 tests)

## Decisions Made
See `key-decisions` in the frontmatter. In short: invalid `jahr` is removed, not rewritten; the pure link logic is exported for tests; the product-page title and announcement live in the router.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing critical] Scroll position preserved on query-only navigation**
- **Found during:** Task 3 (scrollBehavior)
- **Issue:** The plan only said "hash -> element, else `{ top: 0 }`". With a year or mode switch (`router.replace` on the same path) that would scroll the page to the top while the user is working at the control, contradicting "focus stays on the control".
- **Fix:** `scrollBehavior` returns the saved position when present and `false` for same-path navigations; the hash target still wins.
- **Files modified:** `app/src/router/index.ts`
- **Committed in:** `f3d6630`

**2. [Rule 1 - Bug avoided] Initial navigation handled separately in `afterEach`**
- **Found during:** Task 3
- **Issue:** On first load of `/` the plan's rule "same path and no hash -> do nothing" would leave the document title unset and moving focus/announcing on first load would disturb the skip link.
- **Fix:** For `from === START_LOCATION` only the title is set.
- **Files modified:** `app/src/router/index.ts`
- **Committed in:** `f3d6630`

**3. [Plan wording] Product page title via router instead of the page**
- **Found during:** Task 3
- **Issue:** The plan has `ProduktPage` set `document.title`. A page-level watcher would run after `afterEach` and the announcement would only say "Seite Produkt geladen".
- **Fix:** The router resolves the title for `produkt` from `findeProdukt` (product name, or "Dieses Produkt gibt es nicht"), used for both title and announcement. Observable behaviour is the one the plan describes.
- **Files modified:** `app/src/router/index.ts`
- **Committed in:** `f3d6630`

**4. [Rule 3 - Blocking] Stub commit in the RED step**
- **Found during:** Task 2
- **Issue:** Without a module the new test file fails on import, which the TDD reference classes as INVALID_RED.
- **Fix:** The RED commit contains a signature-only `lib/ansicht.ts` so 21 of 29 tests fail on assertions.
- **Committed in:** `1ab6dd0`

---

**Total deviations:** 4 (1 missing critical, 1 bug avoided, 1 plan-wording choice, 1 blocking)
**Impact on plan:** No scope creep; all stay inside the plan's files. `app/src/main.ts` (shared) was changed only by adding the planned imports.

## Issues Encountered
- Two composables that clean the URL at the same time (e.g. `useJahr` and `useAnsicht` on `/ausgaben?jahr=abc&pb=__proto__`) each compute a `router.replace` from the same stale query. A scratch probe (memory history, not committed) showed the URL converges to the clean state after the follow-up watcher run (`/x?foo=bar`); valid URLs stay untouched. No serialization was added.
- The `check tdd-red-evidence` verifier was not invoked (the RED run is documented here: 21 failing tests, all `AssertionError` on `leseAnsicht`/`bereinigteQuery`/`findeKnoten`/`findeProdukt`).
- The plan's `human-check` (dev server, keyboard, screen reader) could not be executed in the Linux sandbox; it remains for the end-of-phase verification.

## TDD Gate Compliance
RED (`test(05-04)` `1ab6dd0`) precedes GREEN (`feat(05-04)` `c2a665c`); REFACTOR (`refactor(05-04)` `3c2792d`) kept all 75 tests green. Task 1 is a `tracer` task: the tests were written first and run red (module missing), then implemented in one commit.

## Known Stubs

| File | Reason |
|------|--------|
| `app/src/pages/EinnahmenPage.vue`, `AusgabenPage.vue`, `GeldflussPage.vue`, `GlossarPage.vue` | Intentional page shells (PageIntro, plus JahrUmschalter where applicable). Content comes from 05-09, 05-10, 05-13, 05-12 and 05-14/15. |
| `app/src/pages/ProduktPage.vue` | Shows only the header line for a found product; the sections (Leistungen, Teilergebnisplan, ...) are plan 05-11. The not-found state is complete. For the not-found case `PageIntro` receives an empty `beschreibung`. |

## Threat Flags
None. The planned mitigations T-05-09 (allowlists, prototype keys tested), T-05-10 (code rendered by text interpolation only), T-05-11 (hash used only for `getElementById`, only named internal routes) are implemented; no new network surface.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Page plans can import `useJahr`, `jahrLink`, `useAnsicht`, `findeKnoten`, `findeProdukt`, `wertartName`, `wertartFuerJahr` and `ansagen`.
- Plan 05-07 still has to handle the skip link (RESEARCH Pitfall 2) and the navigation links that carry `jahr` (`jahrLink`).
- End-of-phase human check: `/#/produkt/999999`, `/#/einnahmen?jahr=abc`, keyboard year switch with announcement, focus on h1 after link navigation.

## Self-Check: PASSED
All 16 files exist, commits `22b3de0`, `1ab6dd0`, `c2a665c`, `3c2792d`, `f3d6630` exist; full app chain (type-check, lint, format:check, test 75/75, build) green in the scratch copy.

---
*Phase: 05-leitfragen-seiten*
*Completed: 2026-10-04*
