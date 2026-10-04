---
phase: 05-leitfragen-seiten
plan: 08
subsystem: ui
tags: [vue, typescript, vitest, startseite, kennzahlen, web-awesome]
status: complete

requires:
  - phase: 05-leitfragen-seiten
    provides: "05-04 wertartFuerJahr/wertartName and routes einnahmen/ausgaben; 05-06 proKopf, baueErtragsarten, findeKlKnoten, KreisumlageCallout (kurz), BerechnetEtikett"
provides:
  - "lib/kennzahlen.ts: Kennzahl, baueKennzahlen (seven Kennzahlen), quellenZeile, Einstiege, baueEinstiege (D-20)"
  - "KennzahlKachel.vue: one KPI tile with optional BerechnetEtikett"
  - "EinstiegsKachel.vue: Leitfrage wa-card with data sentence slot and one CTA"
  - "StartPage.vue: real start page (Kennzahlenband, two Einstiegskacheln, Kreisumlage hint), demo content removed"
affects: [05-14, 05-15, 06]

actuals:
  tokens: 5800
  tasks: 2
  commits: 4
plan_head_before: 368177eb3ea48d6462b1a2d8b1d14dc3d3a6609b
plan_head_after: 839148e16eb309e62c65c835dd094e49dfcd81d9

tech-stack:
  added: []
  patterns:
    - "RouterLink custom v-slot wrapping wa-button :href @click=navigate (RESEARCH Pattern 5) for CTA buttons"
    - "Page captions built by one helper (quellenZeile) from Wertart, year and PDF pages"
    - "Template gate test: ?raw import of .vue sources must not contain typed amounts"
    - "2026 success values only in describe.runIf(haushalt.haushaltsjahr === 2026), everything else derived from data"

key-files:
  created:
    - app/src/lib/kennzahlen.ts
    - app/src/lib/__tests__/kennzahlen.test.ts
    - app/src/components/KennzahlKachel.vue
    - app/src/components/EinstiegsKachel.vue
  modified:
    - app/src/pages/StartPage.vue

key-decisions:
  - "baueEinstiege returns the PDF page per entry (Ertragsplan page 62 for the Einnahmen sentence, the Produktbereich page for the Ausgaben sentence) instead of the single top-level pdfSeite sketched in the plan, because the two values sit on different pages"
  - "Per-capita tiles cite two pages (Ergebnisplan and the Einwohner source) and use the plural 'PDF-Seiten 62, 25'"
  - "Einstiegskachel 2 is chosen structurally: PB nodes below GESAMT that are not synthetisch, largest berechnet.aufwand; no code or name in the source"

requirements-completed: [START-01, START-02]

coverage:
  - id: D1
    description: "Kennzahlenband: seven tiles in the fixed order with values from the data fields, Wertart/year/PDF-page line, per-capita values rounded and marked 'berechnet'"
    requirement: START-01
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/kennzahlen.test.ts#baueKennzahlen (order, source fields, rounding, berechnet flags, pages) and Kennzahlen Haushalt 2026 (27,5 / 30,5 / -2,35 / 12,3 / 5,2 Mio. EUR, 2594, 1571)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Kennzahl values are never typed into templates (grep gate over StartPage/KennzahlKachel sources)"
    requirement: START-01
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/kennzahlen.test.ts#Vorlagen ohne eingetippte Betraege"
        status: pass
    human_judgment: false
  - id: D3
    description: "Einstiegskacheln: largest Ertragsart and largest non-synthetic Aufgabenbereich (2026: Innere Verwaltung, 4.519.223 EUR), Kreisumlage hint below"
    requirement: START-02
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/kennzahlen.test.ts#baueEinstiege (D-20) and Einstiege Haushalt 2026"
        status: pass
    human_judgment: false
  - id: D4
    description: "Layout and interaction of the start page: two columns at 360 px, no number breaking, CTA styling and navigation, tooltip on the 'berechnet' tag, Lighthouse-relevant focus behaviour"
    requirement: START-01
    verification: []
    human_judgment: true
    rationale: "No browser in the sandbox; markup was checked by an SSR render in a scratch copy, visual layout, wa-button as link and focus behaviour need a human check on the host (plan human-check)"

duration: 9min
completed: 2026-10-04
---

# Phase 5 Plan 08: Startseite Summary

**Start page with the seven checked Kennzahlen 2026 (each with Wertart, year and PDF page, per-capita values rounded and tagged 'berechnet'), two data-driven Leitfrage tiles with CTAs, and the Kreisumlage hint, all derived from haushalt.json**

## Performance

- **Duration:** 9 min
- **Started:** 2026-10-04T13:17Z
- **Completed:** 2026-10-04T13:26Z
- **Tasks:** 2 (tracer + TDD)
- **Files modified:** 5 (4 created, 1 rewritten)

## Accomplishments

- Kennzahlenband "Die wichtigsten Zahlen 2026": Erträge 27,5 Mio. €, Aufwendungen 30,5 Mio. €, "Defizit nach Minderaufwand" -2,35 Mio. €, Investitionen 12,3 Mio. €, Neue Kredite 5,2 Mio. €, Aufwand pro Einwohner 2.594 € and Steuern pro Einwohner 1.571 € (both with `BerechnetEtikett`). Values come only from `baueKennzahlen()` and `format.ts`; the label switches to "Überschuss ..." for a positive result.
- Two Einstiegskacheln ("Woher kommt das Geld?" / "Wofür wird das Geld ausgegeben?") with one data sentence each: Steuern und ähnliche Abgaben 18,4 Mio. € (67,1 %), and Innere Verwaltung 4,52 Mio. € (largest Aufgabenbereich without the synthetic KL node, D-20). CTAs "Einnahmen ansehen" / "Ausgaben ansehen" use `RouterLink custom` + `wa-button`.
- Short `KreisumlageCallout` below the tiles with the link to /ausgaben; the Phase-1 demo (beispieldaten chart, table, empty chart) is gone and the page no longer imports `jahrgang.json`.
- Tracer gate: Task 1 verified end to end (test, type-check, lint, format:check, build) before the Einstiegskacheln were added.

## Task Commits

1. **Task 1: Tracer, Kennzahlenband end-to-end** - `eb4658e` (feat)
2. **Task 2 RED: failing tests for baueEinstiege (D-20)** - `af30fbf` (test; `gsd_run check tdd-red-evidence` returned RED_EVIDENCE_OK on a TAP run of vitest)
3. **Task 2 GREEN: baueEinstiege** - `cd04d73` (feat)
4. **Task 2 UI: EinstiegsKachel, StartPage with entries and Kreisumlage hint** - `839148e` (feat)

**Plan metadata:** committed with this SUMMARY (docs).

## Files Created/Modified

- `app/src/lib/kennzahlen.ts` - Kennzahl, baueKennzahlen, quellenZeile, baueEinstiege
- `app/src/lib/__tests__/kennzahlen.test.ts` - 20 tests incl. the 2026 block, per-field source checks, rounding, D-20 and the template gate
- `app/src/components/KennzahlKachel.vue` - KPI tile (Secondary surface, Label 14/600, value Heading 20/600 up to 699 px and Display 32/600 above, `om-zahl`, caption)
- `app/src/components/EinstiegsKachel.vue` - `wa-card` with h2, slot sentence, caption and one CTA
- `app/src/pages/StartPage.vue` - the real start page

## Decisions Made

See `key-decisions` in the frontmatter. In addition: the Kennzahlen grid is a `<ul role="list">` with `repeat(auto-fit, minmax(160px, 1fr))` (two columns at 360 px); the Einstiegskacheln stack up to 699 px and sit side by side from 700 px.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing critical] Per-entry PDF page in baueEinstiege**
- **Found during:** Task 2
- **Issue:** The plan sketches one `pdfSeite` for the whole Einstiege result, but the Ertragsart value sits on the Ergebnisplan page (62) and the Aufgabenbereich value on its Produktbereich page (66 for Innere Verwaltung). One page would cite a wrong source for one sentence.
- **Fix:** `einnahmen.pdfSeite` and `ausgaben.pdfSeite`, both read from the knoten; tests cover both.
- **Files modified:** app/src/lib/kennzahlen.ts, app/src/lib/__tests__/kennzahlen.test.ts
- **Committed in:** cd04d73

### Unmet plan item (needs a user decision)

**2. `app/src/data/jahrgang.json` was NOT deleted**
- Task 2 step 5 and the acceptance criterion `test ! -e app/src/data/jahrgang.json` call for `git rm app/src/data/jahrgang.json`. The auto-mode permission classifier denied that command ("Irreversible Local Destruction"), so I did not delete the file and did not try another route.
- State: StartPage no longer imports it and `grep -rn "jahrgang.json" app/src pipeline .github` finds no reference, so the page reads the Haushaltsjahr only from `haushalt.json` (the goal of the step is met functionally). The tracked file `app/src/data/jahrgang.json` (`{"haushaltsjahr": 2026}`) is only an unused leftover.
- To finish: the user (or the orchestrator, with permission) runs `git rm app/src/data/jahrgang.json` and commits it.

---

**Total deviations:** 1 auto-fixed (Rule 2), 1 unmet item awaiting a user decision (file deletion denied by the permission classifier)
**Impact on plan:** All behavior is delivered; only the removal of one unused data file is pending.

## Issues Encountered

- `?raw` imports of `.vue` files work in vitest, so the template gate test reads the real sources (a mutation check with an inserted "27,5 Mio" made the test fail as intended).
- Prettier required a reformat of the test file once; fixed before the first commit.
- No browser is available in the sandbox. The markup was checked with a throwaway SSR render in the scratch copy (not committed): seven tiles with captions, tags with tooltips, `href="/einnahmen"` / `href="/ausgaben"` on the CTAs. `wa-button` as a link (`:href`) is the Pattern 5 route; the fallback (RouterLink styled as a button) was not needed in the render but its visual behavior still needs the human check.

## User Setup Required

None - no external service configuration required.

## Known Stubs

None. No placeholder text or hardcoded empty values in the new files.

## Threat Flags

None. No new network endpoints, auth paths or schema changes; T-05-21 (value integrity) is mitigated by per-field tests, the 2026 success-value block, the rounding test and the template gate; T-05-22 by the synthetic-node test.

## Next Phase Readiness

- Start page is ready for the human layout check (360 px and 1280 px): two tile columns at 360 px without horizontal scroll, "-2,35 Mio. €" next to "Defizit", tooltip on the "berechnet" tags, CTA navigation, Kreisumlage link. The `wa-button` link rendering is the one open assumption (A2).
- Shared files were not touched (`main.ts`, router, `echartsTheme.ts`); `wa-card`, `wa-button`, `wa-tag`, `wa-tooltip`, `wa-callout` were already imported in `main.ts`.

## Self-Check: PASSED

Verified: app/src/lib/kennzahlen.ts, app/src/lib/__tests__/kennzahlen.test.ts, app/src/components/KennzahlKachel.vue, app/src/components/EinstiegsKachel.vue and app/src/pages/StartPage.vue exist; commits eb4658e, af30fbf, cd04d73 and 839148e exist; scratch chain green (12 test files / 158 tests, type-check, lint, format:check, build). Acceptance criteria all pass except `test ! -e app/src/data/jahrgang.json` (see Deviations, item 2).

---
*Phase: 05-leitfragen-seiten*
*Completed: 2026-10-04*
