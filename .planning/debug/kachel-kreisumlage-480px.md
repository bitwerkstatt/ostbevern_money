---
status: diagnosed
trigger: "UAT G-07-2: CI e2e kacheln.spec.ts fails on GitHub Actions: /rat-entscheidet @ 480 px: „Kreisumlage“: Betrag „rd. 10,1 Mio. €“ ragt 6.0 px über den Inhaltsbereich (Betrag 164.0 px, Inhalt 158.0 px)"
created: 2026-10-07T08:10:00Z
updated: 2026-10-07T08:55:00Z
goal: find_root_cause_only
---

## Current Focus

bug_class: Bohrbug (deterministic, environment-dependent: same build + same font set -> same width)
hypothesis: CONFIRMED. Tile amount width depends on the system font behind `system-ui`; the 13rem track was calibrated in a font environment (Playwright Docker image -> WenQuanYi Zen Hei) that does not match the GitHub runner (DejaVu Sans Bold). At every auto-fit column breakpoint the track is exactly 13rem = 208 px, minus 18 px inherited Web Awesome `li` margin-inline-start, minus 2 x 16 px padding = 158 px content; "rd. 10,1 Mio. €" in DejaVu Sans Bold 20 px = 164 px -> 6 px overflow.
test: done (see Evidence)
expecting: n/a
next_action: return ROOT CAUSE FOUND to orchestrator (goal: find_root_cause_only)

reasoning_checkpoint:
  hypothesis: "The CI failure occurs because on ubuntu-latest `ui-sans-serif, system-ui, sans-serif` resolves to DejaVu Sans Bold, which renders 'rd. 10,1 Mio. €' at 164 px, while the tile content box at the 2-column breakpoint (480 px) is only 158 px: 13rem track (208) - 18 px Web Awesome li margin-inline-start - 32 px padding. The 13rem value was calibrated in the Playwright Docker image, where the same text rendered in WenQuanYi Zen Hei at 141.1 px."
  confirming_evidence:
    - "CDP getPlatformFontsForNode: Docker image -> WenQuanYi Zen Hei, 141.1 px (matches 07-13 SUMMARY 141.1 px exactly)"
    - "Same image + DejaVu core fonts -> DejaVu Sans Bold, 164.0 px in 158.0 px, overflow 6.0 px; full kacheln.spec.ts -> 1 failed / 4 passed with byte-identical error text to the GitHub log"
    - "li computed margin-inline-start 18px (Web Awesome native.css `li { margin-inline-start: 1.125em }`, layer wa-native); tile 190 px in a 208 px track; injecting `.om-kachelraster > li { margin: 0 }` -> content 176 px, reserve +12 px with DejaVu"
  falsification_test: "If the GitHub runner did NOT use DejaVu Sans, the simulated container would not reproduce 164.0/158.0/6.0 exactly; it does."
  fix_rationale: "n/a (diagnose only) - see Suggested Fix Direction"
  blind_spots: "Runner font set inferred (fonts-dejavu-core via fontconfig-config dependency on ubuntu-24.04) and reproduced on aarch64, runner is x86_64; glyph advances are architecture-independent and the numbers match exactly. Not checked: Noto Sans present on runner (would win over DejaVu in 60-latin.conf) - exact numeric match says no."
  candidate_causes:
    - "environment: CI font (DejaVu Sans Bold) wider than calibration font (WenQuanYi Zen Hei) - CONFIRMED"
    - "code: 13rem min track leaves zero slack at each auto-fit breakpoint (480/720/952 px) and the inherited li margin-inline-start (18 px) silently shrinks the tile - CONFIRMED contributing"
    - "test infra/process: 07-13 calibration ran in mcr.microsoft.com/playwright image instead of the CI environment (ubuntu-latest + playwright install --with-deps) - CONFIRMED contributing"
    - "data: amount string 'rd. 10,1 Mio. €' (prefix 'rd. ') is the widest string - context, not a defect"
  and_gate: "yes - the overflow needs both (a) a font at least ~4 % wider than WenQuanYi in bold 20 px AND (b) the 158 px content box at an exact column breakpoint (13rem track minus 18 px li margin). Removing either (li margin 0 -> 176 px, or calibration font) removes the failure."

## Symptoms

expected: The CI e2e smoke test (Playwright, app/e2e/kacheln.spec.ts, "Kennzahl-Kacheln über alle Breiten (A11Y-03, 07-13)") passes on GitHub Actions.
actual: "[ci] › e2e/kacheln.spec.ts:324:5 › Kennzahl-Kacheln über alle Breiten (A11Y-03, 07-13) › Kacheln und Seitenbreite: /rat-entscheidet — Error: /rat-entscheidet @ 480 px: „Kreisumlage“: Betrag „rd. 10,1 Mio. €“ ragt 6.0 px über den Inhaltsbereich (Betrag 164.0 px, Inhalt 158.0 px). 1 failed, 80 passed (1.2m). Process completed with exit code 1."
errors: assertion at app/e2e/kacheln.spec.ts:343 (expect(befunde).toEqual([]))
reproduction: Push to main -> GitHub Actions job `app` -> `npx playwright install --with-deps chromium` -> `npm run test:e2e` (project ci). UAT test 2 in .planning/phases/07-feinschliff-und-ver-ffentlichung/07-UAT.md. Manual device check (360/400/600/768/1280) passed.
started: after plan 07-13 (tile fix); the 07-13 SUMMARY measured the same amount at 141.1 px (16.9 px reserve) in the local Playwright Docker image.

## Eliminated

## Evidence

- timestamp: 2026-10-07T08:10:00Z
  checked: .planning/debug/knowledge-base.md
  found: no knowledge base file exists (only two unrelated open sessions)
  implication: no known pattern candidate

- timestamp: 2026-10-07T08:10:00Z
  checked: 07-13-SUMMARY.md calibration tables
  found: 13rem min track chosen with smallest reserve 16.9 px at /rat-entscheidet @ 480 px ("rd. 10,1 Mio. €" 141.1 px in 158.0 px content). Measured in the Playwright Docker image ("System-Sans-Schrift"). CI measured the same string at 164.0 px (+22.9 px, +16 %), content width identical (158.0 px).
  implication: grid/content box is identical on CI and locally; only the rendered text width differs -> font environment difference, not layout math

- timestamp: 2026-10-07T08:10:00Z
  checked: .github/workflows/ci.yml job app
  found: runs on ubuntu-latest, installs browsers with `npx playwright install --with-deps chromium` (system fonts of the runner image), not inside the mcr.microsoft.com/playwright Docker image used for the 07-13 calibration
  implication: CI and calibration environment have different system font sets

- timestamp: 2026-10-07T08:25:00Z
  checked: font stack of .om-kennzahl__wert / .om-zahl
  found: Web Awesome default theme `--wa-font-family-body: ui-sans-serif, system-ui, sans-serif`; no self-hosted web font in the app (app/public has only icons, quellen). Amount: --wa-font-size-l = 20px, weight 600, white-space: nowrap (basis.css .om-zahl). Grid: repeat(auto-fit, minmax(min(100%, 13rem), 1fr)) -> at 480 px 2 columns, tile content 158.0 px.
  implication: the rendered width of the amount depends entirely on whatever system font the OS maps `system-ui` to

- timestamp: 2026-10-07T08:30:00Z
  checked: CDP CSS.getPlatformFontsForNode in mcr.microsoft.com/playwright:v1.63.0-noble (the 07-13 calibration environment), /rat-entscheidet @ 480 px, scratch build of HEAD
  found: all tile amounts render in "WenQuanYi Zen Hei" (a CJK font). "rd. 10,1 Mio. €" = 141.1 px, content 158.0 px. The image has no DejaVu / Noto Sans; fontconfig's 60-latin.conf prefer list (Noto Sans, DejaVu Sans, Verdana, Arial, ...) finds nothing, 64-wqy-zenhei.conf appends WenQuanYi -> `system-ui` = WenQuanYi. Probe: sans-serif/Arial/Liberation Sans = 132.3 px, system-ui = 141.1 px.
  implication: the 13rem calibration (16.9 px reserve) was measured with a CJK fallback font that no real user and not the CI runner uses

- timestamp: 2026-10-07T08:35:00Z
  checked: same container with DejaVu Sans/Serif/Mono (fonts-dejavu-core set, from npm dejavu-fonts-ttf 2.37.3) mounted at /usr/share/fonts/truetype/dejavu + fc-cache
  found: fc-match sans-serif -> DejaVu Sans; platform font of the amounts -> "DejaVu Sans [DejaVuSans-Bold]"; "rd. 10,1 Mio. €" = 164.0 px, content 158.0 px -> overflow 6.0 px. Exactly the CI numbers (Betrag 164.0 px, Inhalt 158.0 px, 6.0 px).
  implication: CI failure reproduced numerically; ubuntu-latest has fonts-dejavu-core (dependency of fontconfig-config), so `system-ui` = DejaVu Sans Bold on the runner

- timestamp: 2026-10-07T08:45:00Z
  checked: full `playwright test e2e/kacheln.spec.ts --project=ci` in Playwright image + DejaVu core fonts (CI=1)
  found: "1 failed, 4 passed"; only failure: "/rat-entscheidet @ 480 px: „Kreisumlage“: Betrag „rd. 10,1 Mio. €“ ragt 6.0 px über den Inhaltsbereich (Betrag 164.0 px, Inhalt 158.0 px)" - byte-identical to the GitHub log. Min reserves under DejaVu: / 24.4 px (-2,35 Mio. € 133.6), /investitionen 32.7, /stellenplan 42.3, /rat-entscheidet -6.0 - all at 480 px.
  implication: CI environment fully reproduced; only the widest string ("rd. " prefix) breaks

- timestamp: 2026-10-07T08:50:00Z
  checked: grid geometry at 400/480/560/768/1024 (DejaVu)
  found: 480 px: ul 432 px = exactly 2 x 208 + 16 gap -> tracks "208px 208px", but tile only 190 px. li computed margin-inline-start 18px from Web Awesome native.css (`@layer wa-native { li { margin-inline-start: 1.125em } }`); `.om-kachelraster > li` only sets min-width: 0. Tile starts at x=42 while ul starts at x=24 (tiles indented 18 px vs. heading). Pre-existing in the old local grids (771b795^) too.
  implication: the effective content width at a breakpoint is 13rem - 18 - 32 = 158 px, not 176 px; the indent was never intended (list-style: none)

- timestamp: 2026-10-07T08:55:00Z
  checked: same tile at 720 and 952 px (3- and 4-column breakpoints, not in BREITEN) with/without injected `.om-kachelraster > li { margin: 0 }`
  found: as-is: 720 and 952 px also 158 px content, 6.0 px overflow (untested widths). With li margin 0: content 176 px, reserve +12.0 px at 480/720/952.
  implication: defect is not specific to 480 px; every auto-fit breakpoint (track exactly 13rem) is a worst case; real Linux users with DejaVu at ~480-490, ~720-735, ~952-965 px see the overflow

## Resolution

root_cause: "Kachel-Betragsbreite hängt an der Systemschrift (`ui-sans-serif, system-ui, sans-serif`, kein Webfont). Die 13rem-Mindestspur aus 07-13 wurde im Playwright-Docker-Image kalibriert, in dem `system-ui` auf die CJK-Schrift WenQuanYi Zen Hei fällt ('rd. 10,1 Mio. €' = 141,1 px). Auf dem GitHub-Runner (ubuntu-latest, fonts-dejavu-core) ist es DejaVu Sans Bold = 164,0 px; AND an jedem auto-fit-Umbruch (480/720/952 px) ist die Spur genau 208 px, abzüglich 18 px geerbtem Web-Awesome-`li { margin-inline-start: 1.125em }` und 32 px Innenabstand bleiben nur 158 px Inhalt -> 6 px Überlauf."
fix:
verification:
files_changed: []
