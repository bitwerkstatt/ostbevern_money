---
phase: 07-feinschliff-und-ver-ffentlichung
plan: 04
subsystem: ui
tags: [vue, web-awesome, design-tokens, a11y, vitest, source-guards]

requires:
  - phase: 07-feinschliff-und-ver-ffentlichung
    provides: plan 07-01 (Quelle components, DatenTabelle changes) already merged in the base
provides:
  - typography and spacing guard over every .vue style block and .css file (stiltokens.test.ts)
  - deprecated Web Awesome size guard over all .vue templates (quelltext.test.ts)
  - D-17/D-18 token cleanup, glossary h2 "Begriffe" (heading order h1 -> h2 -> h3)
affects: [07-11 smoke test (console check), 07-12 Lighthouse/a11y table]

actuals:
  tokens: 9000
  tasks: 2
  commits: 4
plan_head_before: 82a22f435c189de004f0db24fe85c06e946d3b5d
plan_head_after: 56119d0ad0dc40b8c7c32258764d600b70b9c48a

tech-stack:
  added: []
  patterns:
    - "Style guards run over import.meta.glob ?raw of all .vue/.css files, no per-file allowlist"
    - "Tag-aware template scan: WA_ELEMENT regex tolerates quoted attribute values containing >"

key-files:
  created: []
  modified:
    - app/src/lib/__tests__/stiltokens.test.ts
    - app/src/lib/__tests__/quelltext.test.ts
    - app/src/App.vue
    - app/src/pages/GlossarPage.vue
    - app/src/components/GlossarListe.vue
    - app/src/pages/EinnahmenPage.vue
    - app/src/pages/StellenplanPage.vue
    - app/src/components/ZuschussListe.vue
    - app/src/components/EinstiegsKachel.vue
    - app/src/components/BerechnetEtikett.vue
    - app/src/components/WertartEtikett.vue
    - app/src/pages/AusgabenPage.vue
    - app/src/pages/ProduktPage.vue

key-decisions:
  - "The h2 'Begriffe' reuses the .om-glossar-produkte class (same Heading role as 'Alle Produkte') instead of a new class"
  - "--wa-space-s and --wa-space-2xs stay allowed; only 3xs, 2xl, 5xl are forbidden (UI-SPEC open assumption 5)"

patterns-established:
  - "verstoesse(css) returns violations as readable strings; the guard test is it.each over every file"

requirements-completed: [A11Y-04, QUAL-02]

coverage:
  - id: D1
    description: "stiltokens.test.ts checks every .vue style block and .css file for font-size/font-weight/spacing violations; D-17 token cleanup applied"
    requirement: "A11Y-04"
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/stiltokens.test.ts#Typografie und Abstände aller Dateien (D-17, UI-SPEC 07)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Stellenplan group h3 and Zuschuss subtitle use the Heading role (D-18)"
    requirement: "A11Y-04"
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/stiltokens.test.ts#Überschriften-Rolle der Unterüberschriften (D-18)"
        status: pass
    human_judgment: false
  - id: D3
    description: "GlossarPage has an h2 'Begriffe' before the term list so term h3 headings follow an h2 (Lighthouse heading-order on /glossar)"
    requirement: "A11Y-04"
    verification: []
    human_judgment: true
    rationale: "The Lighthouse heading-order audit needs a browser run; it is produced in 07-12. Only the h2 presence is asserted statically (grep acceptance criterion)."
  - id: D4
    description: "No deprecated WA size names (small/medium/large) in any template; guard keeps it that way"
    requirement: "QUAL-02"
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/quelltext.test.ts#Keine veralteten Web-Awesome-Größen in den Templates (QUAL-02)"
        status: pass
    human_judgment: false

duration: 16min
completed: 2026-10-06
status: complete
---

# Phase 07 Plan 04: Token hygiene, glossary heading order, WA size deprecations Summary

**The typography and spacing guard now covers all 59 .vue/.css files (no per-file list), D-17/D-18 token violations are fixed in eleven files, /glossar gets an h2 "Begriffe" so headings run h1 -> h2 -> h3, and the deprecated Web Awesome long size names are replaced by `s`/`l` with a template guard.**

## Performance

- **Duration:** ~16 min
- **Started:** 2026-10-06T11:45Z
- **Completed:** 2026-10-06T12:02Z
- **Tasks:** 2 (both TDD)
- **Files modified:** 13

## Accomplishments

- `stiltokens.test.ts`: the six-file Phase-6 list (`PHASE_6_TYPOGRAFIE_DATEIEN`) and its describe block are replaced by `styleBloecke`, `verstoesse`, `ERLAUBTE_SCHRIFTGROESSEN` (s, m, l, 2xl), `ERLAUBTE_GEWICHTE` (normal, bold) and `VERBOTENE_SPACING_TOKENS` (3xs, 2xl, 5xl). Literals (`18px`, `600`, `bold`) and tokens outside the scale are reported. `.ts` files stay out (ECharts `fontSize` is not CSS). The G-05-6 undefined-token test is unchanged.
- Fixed violations: App.vue (2x `font-weight: 600` -> bold, `--wa-font-weight-body` -> normal, `--wa-space-3xs` -> 2xs), GlossarListe.vue (semibold -> bold, gap 2xl -> xl, focus offset 3xs -> 2xs), GlossarPage.vue and EinnahmenPage.vue headings (`xl`/semibold -> `l`/bold).
- D-18: `.om-stellenplan__gruppe h3` and `.om-zuschuesse__untertitel` now use `--wa-font-size-l` with bold weight and condensed line height; a test asserts the three declarations.
- GlossarPage.vue: `GlossarListe` is wrapped in `<section aria-labelledby="glossar-begriffe">` with `<h2 id="glossar-begriffe" class="om-glossar-produkte">Begriffe</h2>`.
- `quelltext.test.ts`: `veralteteGroessen(template)` finds `size="small|medium|large"` on `wa-*` elements (quote-aware, multi-line safe) with fail-first probes and an `it.each` over all templates. Seven template usages (five `wa-tag`, two `wa-button`; six files plus one repeated in AusgabenPage) now use `s`/`l`.

## Task Commits

1. Task 1 RED: `348040f` test(07-04): add failing guard for typography and spacing tokens in all style blocks
2. Task 1 GREEN: `bc89a33` feat(07-04): clean up typography and spacing tokens, add h2 Begriffe to glossary
3. Task 2 RED: `2d532bf` test(07-04): add failing guard against deprecated Web Awesome size names
4. Task 2 GREEN: `56119d0` feat(07-04): replace deprecated Web Awesome size names with short names

## TDD Gate Compliance

RED then GREEN commits exist for both tasks; no REFACTOR commits were needed.

- **RED task 1:** `stiltokens.test.ts` ran with 6 failing targets (App.vue, GlossarListe.vue, EinnahmenPage.vue, GlossarPage.vue per-file guard; Stellenplan and Zuschuss heading-role tests), 74 passing including all fail-first helper tests. The failures were the planned `toEqual([])` / `toContain('font-size: var(--wa-font-size-l)')` assertions on real violations (e.g. App.vue: `font-weight: 600` x2, `--wa-font-weight-body`, `--wa-space-3xs`). Semantic assessment: target tests executed and failed for the intended reason; no load/syntax faults.
- **RED task 2:** `quelltext.test.ts` ran with 6 failing targets (BerechnetEtikett, EinstiegsKachel, WertartEtikett, AusgabenPage, EinnahmenPage, ProduktPage), 146 passing including all fail-first probes. Same assessment.
- `gsd_run check tdd-red-evidence` returned `INVALID_RED / invalid_record` for the task-1 record because vitest's tap/tap-flat reporter emits multi-line `actual:` diffs that the TAP adapter reports as "Non-TAP data in report / Malformed TAP" (the parse still listed the six failing tests correctly). `workflow.tdd_mode` is `false` in this project, so the gate is advisory; the semantic inspection above was done manually. Not used to authorize anything the classifier forbids in tdd_mode.

## Deviations from Plan

None - plan executed exactly as written. Note on counts: the plan's "eleven style fixes" and "seven template places" were applied as listed (EinnahmenPage.vue and AusgabenPage.vue received both a style and a size fix respectively).

## Issues Encountered

- Sandbox rule: a Bash call combining a heredoc script with git or `gsd_run` was refused as "too complex"; commands were split into separate plain calls. No effect on the result.
- The verify commands tar the app into a scratch directory; because the worktree does not contain macOS binaries, `npm ci` was run directly in the worktree `app/` instead (Linux, ignored `node_modules`), then type-check, lint, format:check, test and build were run there. All green.

## Verification

- `npm run type-check`, `npm run lint`, `npm run format:check`: clean.
- `npm run test`: 38 files, 1756 tests pass (up from 1689 after task 1).
- `npm run build`: succeeds (only the existing chunk-size notice).
- Acceptance criteria: `VERBOTENE_SPACING_TOKENS` and `ERLAUBTE_SCHRIFTGROESSEN` present; `PHASE_6_TYPOGRAFIE_DATEIEN` count 0; `>Begriffe<` present in GlossarPage.vue; `veralteteGroessen`, `size="s"` in BerechnetEtikett.vue and `size="l"` in EinstiegsKachel.vue present.

## Known Stubs

None.

## Threat Flags

None - style and template attribute changes only.

## Next Phase Readiness

The Lighthouse heading-order result on /glossar and the console-warning check are measured in 07-12 and 07-11. STATE.md and ROADMAP.md were deliberately not touched (orchestrator-owned).

## Self-Check: PASSED

- All 13 files in key-files.modified exist and are committed (commits 348040f, bc89a33, 2d532bf, 56119d0 verified in `git log`).
