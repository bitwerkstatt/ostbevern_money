---
phase: 07-feinschliff-und-ver-ffentlichung
plan: 05
subsystem: ui
tags: [vue, vue-router, config, impressum, datenschutz, a11y, vitest, source-guards]

requires:
  - phase: 07-feinschliff-und-ver-ffentlichung
    provides: plan 07-04 token guards (stiltokens.test.ts, quelltext.test.ts) now enforced on every .vue file
provides:
  - real KONTAKT_EMAIL (D-07) and ORIGINAL_PDF_URL (D-06) in config.ts
  - IMPRESSUM_NAME / IMPRESSUM_ANSCHRIFT placeholders with istImpressumPlatzhalter / istAnschriftPlatzhalter
  - route ueber and UeberPage (Ein inoffizielles Projekt, Dank, Impressum, Datenschutz)
  - footer link "Über dieses Projekt, Impressum und Datenschutz"
  - FUSSZEILEN_ROUTEN exception list plus route-reachability test in menue.test.ts
affects: [07-10 text checkpoint (sets Impressum name and address, adds readiness assertion), 07-11 smoke test (.invalid check, /ueber route), 07-12 Lighthouse row for #/ueber]

actuals:
  tokens: 10500
  tasks: 2
  commits: 2
plan_head_before: a799ce0b63e5b0c7c9c4495564c479089661e7ae
plan_head_after: 5dbcc54c4fde682887dad13254fce4eacf92ed9c

tech-stack:
  added: []
  patterns:
    - "Placeholder detection through the reserved .invalid marker, one predicate for single fields and one for the address list (any placeholder line makes the whole address a placeholder)"
    - "Route reachability test: every route name in the router source is in MENUE, FUSSZEILEN_ROUTEN or the justified parameter-route exception"

key-files:
  created:
    - app/src/pages/UeberPage.vue
  modified:
    - app/src/config.ts
    - app/src/lib/__tests__/config.test.ts
    - app/src/lib/menue.ts
    - app/src/lib/__tests__/menue.test.ts
    - app/src/router/index.ts
    - app/src/App.vue

key-decisions:
  - "Impressum fields stay .invalid placeholders by design; the readiness assertion (no placeholder) is added in 07-10 so the suite stays green until the text checkpoint"
  - "dt uses font-weight bold instead of the UI-SPEC 600 because the 07-04 guard allows only normal and bold"
  - "The prose-wrapping source check normalises whitespace because Prettier wraps the Datenschutz paragraph over lines"

patterns-established:
  - "FUSSZEILEN_ROUTEN lists footer-only routes; adding a route outside MENUE and that list fails menue.test.ts"

requirements-completed: [UI-06, DEPL-02]

coverage:
  - id: D1
    description: "KONTAKT_EMAIL and ORIGINAL_PDF_URL hold the decided values and are not placeholders"
    requirement: "DEPL-02"
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/config.test.ts#Konfiguration (D-06, D-07)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Impressum name and address are detectable placeholders in both directions, including a partly filled address"
    requirement: "DEPL-02"
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/config.test.ts#istImpressumPlatzhalter (E4, D-08)"
        status: pass
      - kind: unit
        ref: "app/src/lib/__tests__/config.test.ts#istAnschriftPlatzhalter (E4 partial, zero-one-many)"
        status: pass
    human_judgment: false
  - id: D3
    description: "UeberPage with four sections, Impressum dl, Datenschutz text, config sourcing, non-official wording, safe external links"
    requirement: "UI-06"
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/config.test.ts#UeberPage.vue (Über dieses Projekt, D-08, T-07-14, T-07-16)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Footer link to the named route ueber between Kontakt and Inspiriert von; menu test keeps every route reachable"
    requirement: "UI-06"
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/menue.test.ts#Jede Route ist im Menü oder in der Fußzeile erreichbar"
        status: pass
      - kind: unit
        ref: "app/src/lib/__tests__/config.test.ts#App.vue (Fußzeilenlink auf Über dieses Projekt, D-08)"
        status: pass
    human_judgment: false
  - id: D5
    description: "Visual layout of /ueber at 360 px (no horizontal scroll, wrapping of long address lines and the e-mail) and the Du-Anrede wording"
    requirement: "UI-06"
    verification: []
    human_judgment: true
    rationale: "No browser run in this plan; the 360 px overflow check is produced by the 07-11 smoke test and the 07-12 Lighthouse table, wording approval is the 07-10 text checkpoint."

duration: 12min
completed: 2026-10-06
status: complete
---

# Phase 07 Plan 05: Real contact values, page "Über dieses Projekt", footer link Summary

**config.ts now carries the real contact address and the official Gemeinde PDF URL, and a new route `/ueber` shows the four sections (inoffizielles Projekt, Dank, Impressum, Datenschutz) with the Impressum name and address kept as `.invalid` placeholders that the tests detect until the 07-10 text checkpoint.**

## Performance

- **Duration:** ~12 min
- **Tasks:** 2 (both TDD, tests written and observed failing before the implementation)
- **Files modified:** 7 (1 created)

## Accomplishments

- `config.ts`: `KONTAKT_EMAIL = 'mail@thomas-manthey.de'` (D-07), `ORIGINAL_PDF_URL` = the official file on www.ostbevern.de (D-06, with `%20`). New `IMPRESSUM_NAME`, `IMPRESSUM_ANSCHRIFT` (readonly list), `istImpressumPlatzhalter` (blank or contains `.invalid`, case-insensitive) and `istAnschriftPlatzhalter` (empty list or any placeholder line).
- `UeberPage.vue`: `PageIntro` plus four `section aria-labelledby` blocks with `h2` in the D-08 order. The Impressum is a `dl` (`Verantwortlich`, `Anschrift` in an `address` with one `span` per list entry, `Kontakt` as mailto link). All values come from `config.ts`; the Haushaltsjahr comes from `jahr(haushalt.haushaltsjahr)`. External links carry `target="_blank" rel="noopener noreferrer"`, the icon and the hidden "(öffnet in neuem Tab)".
- Styles only through `--wa-*` tokens and `om-` classes: prose `max-width: 40rem`, section gap `--wa-space-3xl`, `hyphens: auto` on headings and text, `overflow-wrap: anywhere` on address lines and e-mail, `font-style: normal` on the address.
- Router: route `ueber` with `meta.titel` "Über dieses Projekt" before the catch-all; the existing `afterEach` handles title, focus and announcement.
- Footer: new paragraph with `RouterLink :to="{ name: 'ueber' }"` between Kontakt and "Inspiriert von", `inline-flex`, `min-height: 44px`, underlined through `.om-footer a`.
- `menue.ts`: `FUSSZEILEN_ROUTEN = ['ueber']`. `menue.test.ts` fails for any router route name that is not in `MENUE`, `FUSSZEILEN_ROUTEN` or the justified exception `produkt`.
- `config.test.ts`: new Konfiguration, `istImpressumPlatzhalter` and `istAnschriftPlatzhalter` tests; source checks for `UeberPage.vue` (config imports, no e-mail or URL literal, no "offizielle Seite/Veröffentlichung/Website", section order, Datenschutz text, `_blank` links) and for the footer (five lines, route link, position).

## Task Commits

1. Task 1: `1ab6b4b` feat(07-05): real contact and PDF URL, Impressum placeholder fields
2. Task 2: `5dbcc54` feat(07-05): page Ueber dieses Projekt with Impressum and Datenschutz, footer link

RED evidence (observed, not committed separately because the plan is `type: execute`): Task 1 failed 14 of 27 tests (missing functions, old placeholder values); Task 2 failed the new menue tests (`FUSSZEILEN_ROUTEN` undefined, route `ueber` missing) and `config.test.ts` could not load (`UeberPage.vue` ENOENT).

## Verification

Run in the worktree (not a scratch copy) after `npm --prefix app ci`: `type-check`, `lint`, `format:check`, `test` (39 files, 1792 tests, all pass) and `build` all green. All acceptance criteria of both tasks pass.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Whitespace-tolerant Datenschutz source check**
- **Found during:** Task 2
- **Issue:** Prettier wraps the Datenschutz paragraph over two lines, so the single-line literal assertion in `config.test.ts` failed although the text is correct.
- **Fix:** The assertion compares against the source with whitespace collapsed (`quelle.replace(/\s+/g, ' ')`). The plan's grep acceptance criterion (first sentence) still passes because that sentence sits on one line.
- **Files modified:** app/src/lib/__tests__/config.test.ts
- **Commit:** 5dbcc54

### Plan interpretation

- The App.vue footer expectations (five lines, "Über dieses Projekt, Impressum und Datenschutz") were moved from Task 1 to Task 2, so that the Task 1 commit stays green on its own. Plan Task 1 step 3 said to rename the test there; the footer text only exists after Task 2.
- Verification ran in the worktree instead of a `mktemp` scratch copy; the commands are identical and the worktree's `node_modules` and `dist` are gitignored.
- `dt` uses `--wa-font-weight-bold` (UI-SPEC says 600) because the 07-04 guard permits only `normal` and `bold`.

**Total deviations:** 1 auto-fixed (Rule 1). **Impact:** none on scope.

## Known Stubs

The Impressum fields are intentional placeholders, not forgotten stubs (D-08, D-15):

| File | Value | Resolved by |
|------|-------|-------------|
| app/src/config.ts `IMPRESSUM_NAME` | `name-noch-nicht-festgelegt.invalid` | 07-10 text checkpoint (user supplies the name; 07-10 also adds the "no placeholder" readiness assertion) |
| app/src/config.ts `IMPRESSUM_ANSCHRIFT` | `['anschrift-noch-nicht-festgelegt.invalid']` | 07-10 text checkpoint |

Not appended to `.planning/WINDOWS.md`: that shared file belongs to the orchestrator in a parallel wave; the orchestrator may record it after the merge.

## Threat Flags

None. No new network endpoints, auth paths or schema changes. T-07-14 (official appearance), T-07-15 (Impressum placeholders) and T-07-16 (tabnabbing) are mitigated by the source and config tests listed above.

## Issues Encountered

None.

## Next Phase Readiness

07-10 sets `IMPRESSUM_NAME` and `IMPRESSUM_ANSCHRIFT`, approves the `/ueber` texts (Datenschutz is a draft, including the open legal question about IP processing by GitHub Pages) and adds the readiness assertion. 07-11 should include route `ueber` and the `.invalid` check over the Impressum fields; 07-12 needs a Lighthouse row for `#/ueber`.

## Self-Check: PASSED

- FOUND: app/src/pages/UeberPage.vue
- FOUND commits: 1ab6b4b, 5dbcc54
