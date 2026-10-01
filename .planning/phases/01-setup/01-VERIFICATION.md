---
phase: 01-setup
verified: 2026-10-01T12:30:00Z
status: human_needed
score: 10/10 must-haves verified
covered_files:
  - ".claude/CLAUDE.md"
  - ".github/workflows/ci.yml"
  - ".planning/phases/01-setup/01-01-PLAN.md"
  - ".planning/phases/01-setup/01-01-SUMMARY.md"
  - ".planning/phases/01-setup/01-02-PLAN.md"
  - ".planning/phases/01-setup/01-02-SUMMARY.md"
  - ".planning/phases/01-setup/01-03-PLAN.md"
  - ".planning/phases/01-setup/01-03-SUMMARY.md"
  - ".planning/phases/01-setup/01-04-PLAN.md"
  - ".planning/phases/01-setup/01-04-SUMMARY.md"
  - ".planning/phases/01-setup/01-05-PLAN.md"
  - ".planning/phases/01-setup/01-05-SUMMARY.md"
  - "LICENSE"
  - "README.md"
  - "app/.nvmrc"
  - "app/index.html"
  - "app/package.json"
  - "app/src/App.vue"
  - "app/src/charts/echartsTheme.ts"
  - "app/src/charts/format.ts"
  - "app/src/components/BaseChart.vue"
  - "app/src/components/ChartCard.vue"
  - "app/src/components/DatenTabelle.vue"
  - "app/src/components/PageIntro.vue"
  - "app/src/components/chartKontext.ts"
  - "app/src/components/datenTabelle.ts"
  - "app/src/data/beispieldaten.json"
  - "app/src/data/jahrgang.json"
  - "app/src/lib/bildschirm.ts"
  - "app/src/lib/webawesome.ts"
  - "app/src/main.ts"
  - "app/src/pages/StartPage.vue"
  - "app/src/router/index.ts"
  - "app/vite.config.ts"
  - "pipeline/alle.py"
  - "pipeline/jahrgaenge/2026.toml"
  - "pipeline/jahrgaenge/2026_sollwerte.toml"
  - "pipeline/ostbevern/konfiguration.py"
  - "pipeline/tests/test_alle.py"
  - "pipeline/tests/test_konfiguration.py"
  - "pipeline/tests/test_rauchtest.py"
covered_digest: "v2:sha256:28eb71eb684b87ce469dfcf99aad68ccf786a46fd79de85df43dfd0d13a51af0"
behavior_unverified: 0
overrides_applied: 0
behavior_unverified_items: []
human_verification:
  - test: "Run `uv --prefix app run dev` resp. `npm --prefix app run dev` (StartPage), set a BaseChart to `:laedt=\"true\"` and to `:fehler=\"true\"` and observe the render"
    expected: "`laedt=true` shows `<wa-skeleton effect=\"sheen\">` filling the chart area, not the canvas; `fehler=true` shows the triangle-exclamation icon and the German fallback copy, not a broken/empty canvas"
    why_human: "01-04-PLAN.md explicitly tags these two truths `verification: backstop` — code presence/wiring is not accepted as proof; the v-if branches exist (confirmed by reading BaseChart.vue) but no test exercises `laedt`/`fehler` at runtime and no human has observed the actual render"
  - test: "Pass `:laedt=\"true\"` to DatenTabelle and observe the render"
    expected: "Three `<wa-skeleton effect=\"sheen\">` rows render in place of the table, not an empty or broken table"
    why_human: "01-04-PLAN.md tags this truth `verification: backstop` for the same reason as above"
  - test: "Open the dev server at a 360 px responsive viewport (DevTools), check the header/nav, PageIntro heading, and open `#/gibt-es-nicht`"
    expected: "Nav wraps, no horizontal page scroll, PageIntro heading wraps without overflow, active nav link is gold-brown, footer credit visible and working, unknown hash route redirects to start, Network tab shows no third-party host"
    why_human: "Deferred by 01-03-PLAN.md Task 2 `<human-check>` to end-of-phase UAT (layout/colour/network behaviour needs a browser; Playwright arrives only in Phase 7)"
  - test: "Open the start page at full width and at 360 px; inspect the Beispieldaten chart colours, the negative bar colour, axis/tooltip number formatting, the horizontal-bar switch at narrow width, the scrollable DatenTabelle with sticky label column, and the second card's empty state"
    expected: "First bars Ostbevern-Gold, negative 'Bereich D' bar in the danger colour, German amount formatting in tooltip/axis, bars turn horizontal at 360 px, callout/table never overflow sideways, 'Bereich' column stays sticky while scrolling, 'Echte Haushaltszahlen' card shows 'Noch keine Daten' instead of an empty chart"
    why_human: "Deferred by 01-04-PLAN.md Task 3 `<human-check>` to end-of-phase UAT (rendering, colour and narrow-viewport behaviour need a browser)"
---

# Phase 1: Setup Verification Report

**Phase Goal:** Pipeline und App lassen sich leer bauen und testen. Die Konventionen und die Jahrgangskonfiguration sind festgelegt, und die CI prüft jeden Push.
**Verified:** 2026-10-01T12:30:00Z
**Status:** human_needed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth (Roadmap Success Criterion) | Status | Evidence |
|---|---|---|---|
| 1 | Repo structure per Spez. 7 exists (`pipeline/`, `daten/{zwischen,aufbereitet,manuell,pruefberichte}`, `app/`); source PDF under `raw_data/` | ✓ VERIFIED | `ls` confirms all directories; `git ls-files -- 'raw_data/*.pdf' 'discussion/*.pdf'` returns exactly `raw_data/haushalt-2026.pdf`; `git log --follow` shows 2 commits (rename history preserved) |
| 2 | `uv run pytest` runs green in the uv project `pipeline/` (Python ≥3.12, pdfplumber, polars, typer, pytest) | ✓ VERIFIED | `uv run --directory pipeline pytest -q` → `17 passed`; `pipeline/.python-version` = `3.12`; `pipeline/pyproject.toml` lists pdfplumber, polars, typer as deps and pytest/ruff as dev deps; `uv run --directory pipeline ruff check .` and `ruff format --check .` both clean |
| 3 | `npm run build` builds the Vue 3 skeleton (TS, Vite, Web Awesome, vue-echarts, Hash-Router) with the Münster base components (`PageIntro`, `ChartCard`, `BaseChart`, `DatenTabelle`, `charts/format.ts`, `echartsTheme.ts` etc.); `vue-tsc` and ESLint run clean in GitHub Actions | ✓ VERIFIED (CI never executed on GitHub — see human item below for first-push confirmation) | `npm --prefix app run build` exits 0 (828 modules, dist/index.html emitted); `npm --prefix app run type-check` (vue-tsc --build) exits 0 with no output; `npm --prefix app run lint` exits 0; all 6 expected component files present (`BaseChart.vue`, `ChartCard.vue`, `DatenTabelle.vue`, `PageIntro.vue`, `chartKontext.ts`, `datenTabelle.ts` — exact match, no extra Phase 5/7 components per D-03); `.github/workflows/ci.yml` wires `npm run type-check`/`lint`/`format:check`/`build` in job `app`; both local CI replays pass (see below) |
| 4 | Haushaltsjahr, Spaltenköpfe, Seitenbereiche and PDF-Pfad live in a Jahrgangs-Konfigurationsdatei; the pipeline loads them from there, not from code | ✓ VERIFIED | `pipeline/jahrgaenge/2026.toml` contains `haushaltsjahr`, `pdf_pfad`, `[anzahlen]`, `[spalten]` (7 inline tables for ergebnisplan/finanzplan/investitionen), `[seitenbereiche]` (15 chapters), `[kopfzeilen]`; `pipeline/ostbevern/konfiguration.py::lade_jahrgang` is the only module importing `tomllib` (`grep -rl tomllib pipeline` → exactly this file) and validates every required key, rejects absolute/outside-root `pdf_pfad`, rejects `von > bis`, rejects mismatched `haushaltsjahr`; 12 tests in `test_konfiguration.py` plus 3 in `test_rauchtest.py` exercise this, all passing; `STANDARD_JAHR = 2026` is the only year literal in pipeline Python (`grep -rlw 2026 pipeline` → only `konfiguration.py`) |
| 5 | Project `.claude/CLAUDE.md` names pipeline/app commands and the six conventions (deutsche Bezeichner ohne Umlaute, Beträge als int-Euro, nur 1-basierte PDF-Seiten, keine Jahrgangswerte im Code, Du-Anrede, Zahlen in Texten aus Daten) | ✓ VERIFIED | `.claude/CLAUDE.md` Technology-Stack block lists all pipeline/app commands under "### Befehle"; Conventions block states all six D-17 lead phrases verbatim (confirmed by direct read); GSD-managed blocks (project/skills/workflow/profile) byte-identical to pre-edit state per the plan's own diff check; no root `CLAUDE.md` exists (D-17) |
| 6 (plan-level, SC3 CI detail) | `.github/workflows/ci.yml` has exactly two parallel jobs (`pipeline`, `app`), no path filters, triggers on push+PR, `permissions: contents: read`, SHA-pinned actions | ✓ VERIFIED | Read file: jobs `pipeline`/`app` only, no `needs:`, no `paths:`, `permissions: contents: read` present; both `uses:` lines pinned to 40-hex SHAs (`3d3c42e5aac5ba805825da76410c181273ba90b1`, `c18668ad3cf93ea998bef934396af7bb5c839dc7`, `820762786026740c76f36085b0efc47a31fe5020`) with version-tag comments |
| 7 (plan-level) | Every CI `run:` command was executed locally and passed (no GitHub remote yet, D-18) | ✓ VERIFIED | Independently re-ran both chains in this verification pass: `(cd pipeline && uv sync --locked && uv run ruff check . && uv run ruff format --check . && uv run pytest)` → all pass, 17 passed; `(cd app && npm ci ...)` superseded by direct `npm --prefix app run {type-check,lint,format:check,build}` → all exit 0 |
| 8 (plan-level) | README.md names "Inspiriert von Münster Money (Code for Münster)" with a link; LICENSE is MIT | ✓ VERIFIED | `head -1 LICENSE` = `MIT License`, contains copyright line; README.md contains all required phrases (`Inspiriert von`, Münster repo URL, MIT reference, quick-start commands, Font Awesome credit) |
| 9 (plan-level) | The running app requests nothing from a third-party host (self-hosted icons, cherry-picked WA imports) | ✓ VERIFIED | `grep -rhoE 'https?://[a-z0-9.-]+' app/src app/index.html` → only `https://github.com` (the credit link); `app/src/lib/webawesome.ts` calls `setIconPath` with `{BASE_URL}icons`; `app/src/main.ts` imports individual `dist/components/*/*.js` modules (no autoloader) |
| 10 (plan-level) | `format.ts` formatting functions produce the exact specified output | ✓ VERIFIED | Transpiled and ran `format.ts` directly: `euro(2353506)` = "2.353.506 €", `euroKurz(27502063)` = "27,5 Mio. €", `euroKurz(-2353506)` = "-2,35 Mio. €", `zahl(11741)` = "11.741", `prozent(0.341)` = "34,1 %" — all match spec exactly |

**Score:** 10/10 truths verified (0 present-but-behavior-unverified; 4 items below route to human verification for visual/runtime confirmation — see Human Verification Required)

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `pipeline/ostbevern/konfiguration.py` | `STANDARD_JAHR`, `lade_jahrgang`, `lade_sollwerte`, `KonfigurationsFehler`, `Jahrgang` dataclasses | ✓ VERIFIED | 252 lines, all exports present, full validation logic read and confirmed substantive |
| `pipeline/jahrgaenge/2026.toml` | All PDF-specific values of Haushalt 2026 | ✓ VERIFIED | Contains `[seitenbereiche]` and all required tables |
| `pipeline/jahrgaenge/2026_sollwerte.toml` | Sollwerte Satzung §1, Gesamtergebnisplan head lines | ✓ VERIFIED | Contains `[satzung]`, `pdf_seite = 8`, `ertraege = 27_502_063` |
| `pipeline/tests/test_rauchtest.py` | D-12 Rauchtest | ✓ VERIFIED | 3 tests, pdfplumber import present, all pass |
| `pipeline/alle.py` | Thin typer entry point with `--jahr` | ✓ VERIFIED | `STANDARD_JAHR` default, `typer.Option("--jahr"`, exits 1 with `Fehler:` on bad year (tested) |
| `pipeline/uv.lock` | Pinned dependency set | ✓ VERIFIED | Committed, `uv sync --locked` succeeds |
| `app/src/components/PageIntro.vue` | `titel`/`beschreibung` props, default slot | ✓ VERIFIED | 37 lines, `defineProps` present |
| `app/src/router/index.ts` | Hash router, catch-all redirect | ✓ VERIFIED | `createWebHashHistory`, `pathMatch(.*)*` → redirect to `start` |
| `app/src/lib/webawesome.ts` | Styles, German translation, self-hosted icon path | ✓ VERIFIED | `setIconPath`, `translations/de.js` imports present |
| `app/src/main.ts` | Cherry-picked WA component registrations | ✓ VERIFIED | First import is `./lib/webawesome`; imports `dist/components/{page,callout,icon,skeleton,format-number}/*.js` |
| `app/src/App.vue` | App shell: header/nav, RouterView, footer credit | ✓ VERIFIED | `wa-page` with header/footer slots, Münster credit link, wrapping nav (`flex-wrap: wrap`) |
| `app/src/data/jahrgang.json` | Haushaltsjahr as data | ✓ VERIFIED | `{"haushaltsjahr": 2026}`, no year literal elsewhere in `app/src` |
| `app/package.json` | Scripts type-check/lint/format:check/build, engines node | ✓ VERIFIED | All scripts present, `engines.node = "^22.18.0"` |
| `app/src/charts/format.ts` | Number-formatting single source | ✓ VERIFIED | All 5 functions + `LOCALE`/`EURO_OPTIONEN` exported, behaviorally confirmed (see truth #10) |
| `app/src/charts/echartsTheme.ts` | ECharts registration + WA-token theme | ✓ VERIFIED | `CHART_THEME`, `KATEGORIE_FARBEN`, `SEQUENZ_FARBEN`, `POL_FARBEN` exported; `registerTheme`, `echarts/core` import (no full-library import) |
| `app/src/components/BaseChart.vue` | vue-echarts wrapper, laedt/fehler/empty states | ✓ VERIFIED (structurally) | 127 lines, all v-if branches present, "Noch keine Daten" copy present; runtime render of laedt/fehler states is a flagged human item (backstop tag in plan) |
| `app/src/components/ChartCard.vue` | Card chrome, CHART_KONTEXT, Beispieldaten notice | ✓ VERIFIED | 80 lines, `provide(CHART_KONTEXT`, mandatory notice text present, `min-width: 0`, `hyphens: auto` |
| `app/src/components/DatenTabelle.vue` | Semantic table, slot + data mode, empty/loading states | ✓ VERIFIED (structurally) | 164 lines, sticky label column, `wa-format-number` wired to `EURO_OPTIONEN`, empty state copy present; loading-skeleton runtime render flagged as human item (backstop tag) |
| `app/src/lib/bildschirm.ts` | Reactive narrow-screen flag | ✓ VERIFIED | `SCHMAL_BIS = 699`, `useSchmalerBildschirm`, `onScopeDispose` present |
| `app/src/data/beispieldaten.json` | Fictional demo fixture | ✓ VERIFIED | `"beispieldaten": true`, fictional "Bereich A–D" labels |
| `.github/workflows/ci.yml` | Two jobs, SHA-pinned actions | ✓ VERIFIED | See truth #6 |
| `.claude/CLAUDE.md` | Commands + 6 conventions | ✓ VERIFIED | See truth #5 |
| `README.md` | Overview, quick start, license, credit | ✓ VERIFIED | See truth #8 |
| `LICENSE` | MIT | ✓ VERIFIED | See truth #8 |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `test_rauchtest.py` | `konfiguration.py` | imports `lade_jahrgang`, `lade_sollwerte`, `STANDARD_JAHR` | ✓ WIRED | Tests pass (3/3) |
| `konfiguration.py` | `jahrgaenge/2026.toml` | `tomllib.load` via `JAHRGAENGE_VERZEICHNIS / f"{jahr}.toml"` | ✓ WIRED | Confirmed by reading `lade_jahrgang` |
| `jahrgaenge/2026.toml` | `raw_data/haushalt-2026.pdf` | `pdf_pfad` resolved against `PROJEKT_WURZEL` | ✓ WIRED | `pdf_pfad = "raw_data/haushalt-2026.pdf"`; file exists and Rauchtest confirms page count |
| `alle.py` | `konfiguration.py` | `--jahr` defaults to `STANDARD_JAHR` | ✓ WIRED | `grep -q 'STANDARD_JAHR' pipeline/alle.py` and CLI test pass |
| `app/src/main.ts` | `app/src/lib/webawesome.ts` | first import, so `setIconPath` runs first | ✓ WIRED | Confirmed by reading `main.ts` import order |
| `app/src/router/index.ts` | `StartPage.vue` | route name `start` at `/` | ✓ WIRED | Confirmed |
| `StartPage.vue` | `app/src/data/jahrgang.json` | `titel` interpolates `jahrgang.haushaltsjahr` | ✓ WIRED | Confirmed; also `beispieldaten.json` flows into chart/table (data-flow trace below) |
| `vite.config.ts` | `wa-*` custom elements | `isCustomElement` | ✓ WIRED | Confirmed |
| `BaseChart.vue` | `echartsTheme.ts` | imports `CHART_THEME`, passed to `VChart` | ✓ WIRED | Confirmed |
| `BaseChart.vue` | `ChartCard.vue` | `inject(CHART_KONTEXT)` | ✓ WIRED | Confirmed |
| `DatenTabelle.vue` | `charts/format.ts` | `wa-format-number` attrs from `EURO_OPTIONEN` | ✓ WIRED | Confirmed |
| `.github/workflows/ci.yml` | `pipeline/uv.lock` | `uv sync --locked` | ✓ WIRED | Replayed locally, passes |
| `.github/workflows/ci.yml` | `app/package.json` | npm scripts in job `app` | ✓ WIRED | Replayed locally, passes |
| `.github/workflows/ci.yml` | `app/.nvmrc` | `node-version-file: app/.nvmrc` | ✓ WIRED | Confirmed |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|---|---|---|---|---|
| `StartPage.vue` PageIntro titel | `jahrgang.haushaltsjahr` | `app/src/data/jahrgang.json` import | Yes (not hardcoded in .vue/.ts) | ✓ FLOWING |
| `StartPage.vue` chart option | `beispieldaten.posten` | `app/src/data/beispieldaten.json` import | Yes (flagged fictional demo data, by design) | ✓ FLOWING |
| `StartPage.vue` DatenTabelle `zeilen` | computed from `beispieldaten.posten` | same JSON | Yes | ✓ FLOWING |
| `konfiguration.py` `Jahrgang` | TOML file contents | `tomllib.load` on `2026.toml` | Yes | ✓ FLOWING |
| `alle.py` CLI output | `lade_jahrgang(jahr)`/`lade_sollwerte(jahr)` | `konfiguration.py` | Yes | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Pipeline tests pass | `uv run --directory pipeline pytest -q` | `17 passed` | ✓ PASS |
| Pipeline lint/format clean | `uv run --directory pipeline ruff check .` / `ruff format --check .` | "All checks passed!" / "6 files already formatted" | ✓ PASS |
| App build | `npm --prefix app run build` | exit 0, `dist/index.html` emitted | ✓ PASS |
| App type-check | `npm --prefix app run type-check` | exit 0, no output | ✓ PASS |
| App lint | `npm --prefix app run lint` | exit 0, no output | ✓ PASS |
| App format check | `npm --prefix app run format:check` | "All matched files use Prettier code style!" | ✓ PASS |
| `format.ts` numeric output matches spec | inline Node transpile+run of `format.ts` | `2.353.506 €\|27,5 Mio. €\|-2,35 Mio. €\|11.741\|34,1 %` | ✓ PASS |
| CI YAML structurally valid, two parallel SHA-pinned jobs | manual read + grep | jobs=`pipeline app`, no `needs:`, no path filter, `contents: read`, 3 actions all 40-hex SHA | ✓ PASS |
| CI commands replayed locally | both chains from `.github/workflows/ci.yml` | both exit 0 | ✓ PASS |
| `laedt`/`fehler` prop visually render skeleton/error instead of canvas | — | not run (requires browser) | ? SKIP — routed to human verification (plan's own `backstop` tag) |
| DatenTabelle `laedt` visually renders skeleton rows | — | not run (requires browser) | ? SKIP — routed to human verification (plan's own `backstop` tag) |

### Probe Execution

No `scripts/*/tests/probe-*.sh` convention and no probe references found in PLAN/SUMMARY files for this phase. Step 7c: SKIPPED (no probes declared or discovered).

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| SETUP-01 | 01-02, 01-05 | Repo-Struktur nach Spez. 7, Quell-PDF unter raw_data/ | ✓ SATISFIED | Directory structure + README/LICENSE complete it |
| SETUP-02 | 01-01, 01-02 | Pipeline uv-Projekt, `uv run pytest` läuft | ✓ SATISFIED | 17 tests pass; package approval recorded |
| SETUP-03 | 01-01, 01-03, 01-04 | App-Grundgerüst mit Münster-Basiskomponenten, `npm run build` läuft | ✓ SATISFIED | Build green, all 6 base component files present |
| SETUP-04 | 01-05 | Projekt-CLAUDE.md dokumentiert Befehle und Konventionen | ✓ SATISFIED | Confirmed by direct read |
| SETUP-05 | 01-02 | Jahrgangsspezifisches steht in Konfigurationsdatei | ✓ SATISFIED | `2026.toml`/`2026_sollwerte.toml` + loader validated |
| QUAL-01 | 01-03, 01-04, 01-05 | vue-tsc und ESLint laufen fehlerfrei in CI | ✓ SATISFIED (local replay only — see human item for first-push GitHub confirmation) | Local vue-tsc/ESLint clean; ci.yml wires them; no GitHub remote exists yet to observe an actual Actions run |

No orphaned requirements found — REQUIREMENTS.md's Phase 1 mapping (SETUP-01..05, QUAL-01) matches exactly the `requirements:` fields declared across the five plans.

### Anti-Patterns Found

None. Scanned all phase-modified files under `app/src`, `pipeline/ostbevern`, `pipeline/alle.py`, `pipeline/tests`, `.github`, `.claude/CLAUDE.md`, `README.md`, `LICENSE` for `TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER` and placeholder-style copy — zero matches. No hardcoded-empty-prop stub patterns found in rendering paths (BaseChart/DatenTabelle empty states are real copy strings driven by computed conditions, not unconditional stubs).

Code review (`01-REVIEW.md`, disposition `01-REVIEW-DISPOSITION.md`) found 0 critical findings; 5 warnings (WR-01 GitHub Pages `base` path not yet set — correctly out of scope for Phase 1, no deploy job exists yet; WR-02 `prefers-reduced-motion` not implemented anywhere despite being a project constraint in `.claude/CLAUDE.md`; WR-03 unsafe `as number` casts in DatenTabelle; WR-04 echarts theme tokens read once, not reactive; WR-05 DatenTabelle `spalten`/`zeilen` prop coupling not enforced) and 5 info findings, all still `open` (not `fixed`/`skipped`/`deferred`). None are debt markers (no `TBD`/`FIXME`/`XXX` with or without issue references) and none are Critical/Blocker — they do not block this phase's goal (an empty-buildable, tested, CI-checked scaffold) but WR-02 is worth flagging because it contradicts a documented project constraint; it is forward-looking risk, not a phase-1 deliverable failure, since no Phase 1 success criterion mentions motion preferences.

### Human Verification Required

### 1. BaseChart `laedt`/`fehler` visual states

**Test:** Pass `:laedt="true"` and separately `:fehler="true"` to a `BaseChart` instance and observe the render in a browser.
**Expected:** `laedt=true` shows a `<wa-skeleton effect="sheen">` filling the chart area (not the canvas, not blank); `fehler=true` shows the `triangle-exclamation` icon with the German fallback copy, not a broken or empty canvas.
**Why human:** `01-04-PLAN.md`'s `must_haves.truths` explicitly tags both as `verification: backstop` — the planner deliberately marked these as requiring evidence beyond code presence. The `v-if`/`v-else-if` branches exist and read correctly (confirmed), but no test exercises them at runtime and no human has observed the actual render.

### 2. DatenTabelle `laedt` visual state

**Test:** Pass `:laedt="true"` to `DatenTabelle` and observe the render.
**Expected:** Three `<wa-skeleton effect="sheen">` rows render in place of the table.
**Why human:** Same `backstop` tag in `01-04-PLAN.md`.

### 3. 360 px responsive layout and no-third-party-request check (deferred from 01-03 Task 2)

**Test:** Run `npm --prefix app run dev`, open the printed URL, switch DevTools to a 360 px responsive viewport, then open `#/gibt-es-nicht`.
**Expected:** Header shows "Ostbevern Money" and nav item "Start"; nav wraps and the page never scrolls sideways; PageIntro heading wraps without overflow; active nav link is gold-brown; footer shows the Münster credit with a working link; `#/gibt-es-nicht` redirects to start; Network tab shows only local dev-server requests.
**Why human:** Explicitly deferred by `01-03-PLAN.md` Task 2's `<human-check>` block to end-of-phase UAT — layout, colour and network behaviour need a real browser; Playwright arrives only in Phase 7.

### 4. Demo chart/table visual rendering at full width and 360 px (deferred from 01-04 Task 3)

**Test:** Run `npm --prefix app run dev`, open the start page at full width and at 360 px.
**Expected:** Beispieldaten card shows the warning callout above a bar chart with Ostbevern-Gold bars and a red "Bereich D" negative bar; German amount formatting in tooltip/axis; bars turn horizontal at 360 px; callout and table never overflow sideways; table's "Bereich" column stays sticky while scrolling, amounts right-aligned; "Echte Haushaltszahlen" card shows "Noch keine Daten" instead of an empty chart.
**Why human:** Explicitly deferred by `01-04-PLAN.md` Task 3's `<human-check>` block — rendering, colour and narrow-viewport behaviour need a browser.

### 5. GitHub Actions first-run confirmation (contextual, not phase-blocking)

**Test:** After the user creates the GitHub remote and pushes, check the Actions tab.
**Expected:** Both `pipeline` and `app` jobs run green.
**Why human:** There is no git remote in this sandbox (D-18); `.github/workflows/ci.yml` has therefore never executed on GitHub. All its `run:` commands were independently re-verified by local replay in this verification pass (see Behavioral Spot-Checks), which is the accepted stand-in per `01-05-PLAN.md`'s own flagged assumption. This item is informational, carried over from the plan's own documented follow-up, not a new gap.

## Gaps Summary

No gaps found. All five ROADMAP Success Criteria and all plan-level must-haves are backed by passing automated evidence (pytest, ruff, vue-tsc, ESLint, Prettier, vite build, local CI replay, direct file/grep inspection, and a direct behavioral run of `format.ts`). Status is `human_needed` rather than `passed` solely because: (a) two truths in `01-04-PLAN.md` are explicitly tagged `verification: backstop` and have no behavioral test exercising them, and (b) two `<human-check>` blocks in `01-03-PLAN.md` and `01-04-PLAN.md` were deliberately deferred by the planner to end-of-phase UAT rather than mid-execution checkpoints. None of these represent missing, stub, or unwired artifacts — the code backing all four items is present, substantive, and wired; only the runtime/visual confirmation is outstanding.

---

_Verified: 2026-10-01T12:30:00Z_
_Verifier: Claude (gsd-verifier)_
