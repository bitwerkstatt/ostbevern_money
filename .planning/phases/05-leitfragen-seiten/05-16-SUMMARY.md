---
phase: 05-leitfragen-seiten
plan: 16
subsystem: ui
tags: [vue-router, scroll-behavior, scroll-margin-top, web-awesome, design-tokens, vitest]

requires:
  - phase: 05-leitfragen-seiten
    provides: GlossarListe, GlossarBegriff, router scrollBehavior (D-13/D-16), ProduktPage Blick block
provides:
  - "lib/sprungziel.ts: router scroll position with header offset taken from the target's scroll-margin-top"
  - "stiltokens.test.ts: guard that every var(--wa-*) in app/src is defined"
  - "Header-aware scroll margins in GlossarListe and EinnahmenPage; label/value gap in the product Blick list"
affects: [05-UAT retest of tests 4 and 6, phase 05 verification]

actuals:
  tokens: 3300
  tasks: 3
  commits: 4

plan_head_before: 4eebd57fc3c3055aff72dc2568e673b6e7e06874
plan_head_after: a39f998d85a1901c8b76aab1ab72af435d1821d8

tech-stack:
  added: []
  patterns:
    - "Router scroll logic lives in a pure, injectable function (sprungPosition) and passes the target's computed scroll-margin-top as the vue-router top offset"
    - "Source-scan guard test over import.meta.glob '?raw' plus Web Awesome stylesheet definitions with fail-first samples and sanity counts"

key-files:
  created:
    - app/src/lib/sprungziel.ts
    - app/src/lib/__tests__/sprungziel.test.ts
    - app/src/lib/__tests__/stiltokens.test.ts
  modified:
    - app/src/router/index.ts
    - app/src/components/GlossarListe.vue
    - app/src/pages/EinnahmenPage.vue
    - app/src/pages/ProduktPage.vue

key-decisions:
  - "Instant jump kept: sprungPosition returns exactly { el, top } with no behavior key, so prefers-reduced-motion needs no extra handling"
  - "GlossarBegriff underline offset (4px) and dt line-height left untouched, per UI-SPEC prohibitions; the gap is added on the dd instead"

requirements-completed: [GLOS-03, AUSG-05]

coverage:
  - id: D1
    description: "Router scrolls a hash target below the sticky wa-page header by passing its computed scroll-margin-top as the vue-router top offset (G-05-6)"
    requirement: GLOS-03
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/sprungziel.test.ts#sprungPosition liefert fuer ein Hash-Ziel exakt { el, top } mit dem Versatz"
        status: pass
    human_judgment: true
    rationale: "Real scroll landing position below the sticky header (1280 px and 360 px drawer header) can only be seen in a browser; no headless browser is available in the sandbox"
  - id: D2
    description: "GlossarListe scroll-margin-top is a valid declaration and no undefined --wa-* token remains in app/src; a guard test fails on new ones (G-05-6)"
    requirement: GLOS-03
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/stiltokens.test.ts#benutzt kein var(--wa-*), das weder Web Awesome noch die App definiert"
        status: pass
    human_judgment: false
  - id: D3
    description: "Einnahmen Aufschluesselung scroll target clears the sticky header (header height + --wa-space-m)"
    verification: []
    human_judgment: true
    rationale: "Visual landing position of scrollIntoView below the sticky header needs a browser"
  - id: D4
    description: "Label (dt) and value (dd) in the product 'Auf einen Blick' block are separated by --wa-space-2xs so the Bindungsgrad underline no longer touches the wa-tag (G-05-4)"
    requirement: AUSG-05
    verification: []
    human_judgment: true
    rationale: "Visual overlap of a dotted underline and a wa-tag border is a rendering judgment; automated checks only confirm the CSS declaration exists"

duration: 8min
completed: 2026-10-05
status: complete
---

# Phase 5 Plan 16: Gap closure G-05-4 and G-05-6 Summary

**Glossary jumps and the Einnahmen detail scroll now land below the sticky header (router offset from the target's scroll-margin-top, corrected --wa-space-m token, token guard test), and product Blick labels get a --wa-space-2xs gap to their values.**

## Performance

- **Duration:** about 8 min
- **Started:** 2026-10-05T17:44:00Z
- **Completed:** 2026-10-05T17:49:30Z
- **Tasks:** 3
- **Files modified:** 7

## Accomplishments

- G-05-6 root cause fixed at both levels: the router passes `{ el, top }` (top = computed `scroll-margin-top`) and GlossarListe's `scroll-margin-top` no longer names the undefined `--wa-space-md`.
- `stiltokens.test.ts` scans every `.vue`, `.css`, `.ts` in `app/src` (excluding `__tests__`) and fails on any `var(--wa-*)` that neither Web Awesome's stylesheets nor the app define. Proven to fail on the old typo (re-introduced in the scratch copy) and green on the current tree.
- EinnahmenPage `.om-einnahmen__aufklapper` uses the same header-aware rule as the glossary.
- G-05-4: `.om-produkt__blick dd` gets `margin-block-start: var(--wa-space-2xs)`, so the dotted underline of "Bindungsgrad" is separated from the wa-tag; Gremium and Fachbereich rows get the same gap.

## Task Commits

1. **Task 1: Tracer, glossary jump below the header** (TDD)
   - RED: `82bf1bb` (test) - sprungziel.test.ts, failed with module `@/lib/sprungziel` missing
   - GREEN: `0c757c0` (feat) - sprungziel.ts, router delegation, GlossarListe token fix
2. **Task 2: Token guard and Einnahmen scroll margin** - `d9f5008` (test)
3. **Task 3: Label/value gap in the product Blick block** - `a39f998` (fix)

**Plan metadata:** committed with this SUMMARY (docs).

## Files Created/Modified

- `app/src/lib/sprungziel.ts` - elementFuerHash (moved unchanged), versatzAusScrollMargin, scrollVersatz, sprungPosition
- `app/src/lib/__tests__/sprungziel.test.ts` - 11 node tests for offset parsing, `{ el, top: 96 }`, unknown hash, saved position, same-path query change
- `app/src/lib/__tests__/stiltokens.test.ts` - token guard with fail-first samples and sanity counts
- `app/src/router/index.ts` - scrollBehavior delegates to sprungPosition; local elementFuerHash removed
- `app/src/components/GlossarListe.vue` - `scroll-margin-top: calc(var(--scroll-margin-top, 0px) + var(--wa-space-m))`
- `app/src/pages/EinnahmenPage.vue` - same rule on `.om-einnahmen__aufklapper`
- `app/src/pages/ProduktPage.vue` - dd margin-block-start

## Decisions Made

- sprungPosition adds no `behavior` key: the jump stays instant, so reduced-motion users get no motion and `oeffneAufschluesselung` is unchanged.
- Underline offset (UI-SPEC 4px) and dt line-height (Label 14/600/1.2) are untouched; spacing is added on the dd.

## Deviations from Plan

### Judgment calls (not code deviations)

**1. Tracer feedback gate resolved as end-of-phase**
- Task 1 is `type="tracer"` and its `<verify>` carries a `<human-check>`. `human_verify_mode` is `end-of-phase` and the plan states human checks are collected at end of phase (no headless browser in the sandbox), so no mid-flight checkpoint was raised. The automated verify was re-run end to end (test, type-check, lint, format:check): passed, then expansion continued. The human check remains open.

**2. TDD cycle for Task 2 has no standalone RED commit**
- The guard passes on the tree after Task 1 (the plan states this). The fail-first proof was done by re-introducing `--wa-space-md` in the scratch copy: the main assertion failed with `expected [ '--wa-space-md' ] to deeply equal []`, then the scratch copy was re-synced. Test and the EinnahmenPage change are one commit `d9f5008`, as the plan specifies.

**3. GREEN commit type**
- GREEN of Task 1 is committed as `feat(05-16)` (tdd.md gate pattern) although it also fixes the token typo.

**Total deviations:** 0 auto-fixed. **Impact:** none on scope.

## Issues Encountered

- `prettier --check` flagged a line wrap in the first version of sprungziel.test.ts; fixed (single-line expect) before the GREEN commit.
- The worktree sandbox refused compound git commands and writing into the shared `.git` directory, so the plan commit ledger file could not be persisted; `commits:` was measured against the base `4eebd57` given in the dispatch prompt (`git rev-list --count 4eebd57..HEAD` = 4 before this SUMMARY commit).

## Verification (scratch copy of app/, Linux node_modules)

- sprungziel.test.ts 11 passed, stiltokens.test.ts 5 passed; full suite 25 files / 1031 tests passed
- type-check, lint, format:check, build: pass (build warns only about the existing 500 kB chunk size)

## Human checks still open (end of phase)

- /#/produkt/030101: click "Bindungsgrad": the term and its focus ring sit fully visible below the sticky header; also three Sprungmarken on /glossar at 1280 px and 360 px; instant jump under reduced motion.
- /einnahmen: click the "Steuern" bar at 1280 px and 360 px: summary row visible below the header.
- /#/produkt/030101 and /#/produkt/160101 at 360 px and 1280 px: 4 px gap between "Bindungsgrad" underline and the wa-tag; same gap on Gremium and Fachbereich.

## Known Stubs

None.

## Threat Flags

None. T-05-43 (elementFuerHash moved unchanged, getElementById only), T-05-44 (offset clamped, unknown hash stays at top) and T-05-45 (token guard) are implemented as planned.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

G-05-4 and G-05-6 are ready for re-test via /gsd-verify-work (UAT tests 4 and 6) once the open human checks are done.

## Self-Check: PASSED

- Created files present: sprungziel.ts, sprungziel.test.ts, stiltokens.test.ts
- Commits present: 82bf1bb, 0c757c0, d9f5008, a39f998
