---
phase: 01-setup
verified: 2026-10-02T09:35:14Z
status: passed
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
  - ".planning/phases/01-setup/01-CONTEXT.md"
  - ".planning/phases/01-setup/01-DISCUSSION-LOG.md"
  - ".planning/phases/01-setup/01-PATTERNS.md"
  - ".planning/phases/01-setup/01-RESEARCH.md"
  - ".planning/phases/01-setup/01-REVIEW-DISPOSITION.md"
  - ".planning/phases/01-setup/01-REVIEW-FIX.md"
  - ".planning/phases/01-setup/01-REVIEW.md"
  - ".planning/phases/01-setup/01-SECURITY.md"
  - ".planning/phases/01-setup/01-UAT.md"
  - ".planning/phases/01-setup/01-UI-REVIEW.md"
  - ".planning/phases/01-setup/01-UI-SPEC.md"
  - ".planning/phases/01-setup/01-VALIDATION.md"
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
  - "app/src/styles/basis.css"
  - "app/vite.config.ts"
  - "pipeline/alle.py"
  - "pipeline/jahrgaenge/2026.toml"
  - "pipeline/jahrgaenge/2026_sollwerte.toml"
  - "pipeline/ostbevern/__init__.py"
  - "pipeline/ostbevern/konfiguration.py"
  - "pipeline/pyproject.toml"
  - "pipeline/tests/test_alle.py"
  - "pipeline/tests/test_konfiguration.py"
  - "pipeline/tests/test_rauchtest.py"
covered_digest: "v2:sha256:2e6cb4a3180d4ce09f6f5dfc141de75f8ace4fb46593956dbf98ef8eb9fd6889"
behavior_unverified: 0
overrides_applied: 0
behavior_unverified_items: []
re_verification:
  previous_status: passed
  previous_score: "10/10"
  trigger: "Previous VERIFICATION.md (covered_digest v2:sha256:d8e7afdc…) went stale: six covered files (pipeline/alle.py, pipeline/ostbevern/konfiguration.py, pipeline/jahrgaenge/2026.toml, pipeline/jahrgaenge/2026_sollwerte.toml, pipeline/tests/test_alle.py, pipeline/tests/test_konfiguration.py) were legitimately extended by later phases (02-kernzahnen, 03-details)."
  gaps_closed: []
  gaps_remaining: []
  regressions: []
  files_changed_since_previous:
    - path: "pipeline/alle.py"
      change: "Phase 2/3 added pipeline step orchestration (seiten/plaene/produkte/investitionen/querschnitte/pruefung); Phase-1 contract (STANDARD_JAHR default, lade_jahrgang/lade_sollwerte call, KonfigurationsFehler handling, thin typer entry point) unchanged and still present verbatim"
      regression: false
    - path: "pipeline/ostbevern/konfiguration.py"
      change: "Added new dataclasses/validation for later phases; STANDARD_JAHR, JAHRGAENGE_VERZEICHNIS, lade_jahrgang, lade_sollwerte, KonfigurationsFehler all still present and exported"
      regression: false
    - path: "pipeline/jahrgaenge/2026.toml"
      change: "Later-phase config sections added (grown from 1 chapter group to the full set needed by Phase 2/3); Phase-1 structure (haushaltsjahr, pdf_pfad, [anzahlen], [spalten], [seitenbereiche], [kopfzeilen]) intact"
      regression: false
    - path: "pipeline/jahrgaenge/2026_sollwerte.toml"
      change: "Later-phase Sollwerte sections added; Phase-1 [satzung] block and existing keys intact"
      regression: false
    - path: "pipeline/tests/test_alle.py"
      change: "Tests added for later-phase pipeline steps; original Phase-1 assertions (default-year CLI run, KonfigurationsFehler exit code) still present and passing"
      regression: false
    - path: "pipeline/tests/test_konfiguration.py"
      change: "Tests added for later-phase config additions; original 12 Phase-1 test functions still present and passing"
      regression: false
advisory:
  - finding: "`.claude/CLAUDE.md` line 7 contains the substring \"hack\" inside the German word \"Münsterhack\" (the hackathon name, Münsterhack '26), which a case-insensitive debt-marker grep for `HACK` flags as a false positive"
    category: other
    reason: "Not a code comment, not in a source file, not a debt marker — it is prose naming the hackathon the project is inspired by. No action needed; noted only because the automated anti-pattern scan surfaces it."
    evidence_status: "observed directly: grep -n -ioE 'HACK' .claude/CLAUDE.md matches line 7 word boundary inside 'Münsterhack'"
---

# Phase 1: Setup Verification Report

**Phase Goal:** Pipeline und App lassen sich leer bauen und testen. Die Konventionen und die Jahrgangskonfiguration sind festgelegt, und die CI prüft jeden Push.
**Verified:** 2026-10-02T09:35:14Z
**Status:** passed
**Re-verification:** Yes — triggered by staleness (covered files changed after the 2026-10-01T13:15:00Z report, due to legitimate extension by Phase 2/kernzahlen and Phase 3/details). This re-verification confirms Phase 1's own goal, success criteria, and must_haves still hold against the current codebase; it does not re-review Phase 2/3's own work.

## Goal Achievement

### Observable Truths

| # | Truth (Roadmap Success Criterion) | Status | Evidence |
|---|---|---|---|
| 1 | Repo structure per Spez. 7 exists (`pipeline/`, `daten/{zwischen,aufbereitet,manuell,pruefberichte}`, `app/`); source PDF under `raw_data/` | ✓ VERIFIED | Structure unchanged since previous pass; re-confirmed `raw_data/haushalt-2026.pdf` present, `daten/` subdirectories exist |
| 2 | `uv run pytest` runs green in the uv project `pipeline/` (Python ≥3.12, pdfplumber, polars, typer, pytest) | ✓ VERIFIED | Re-ran independently: `uv run --directory pipeline pytest -q` → `295 passed in 187.54s` (growth from 17 to 295 is Phase 2/3 adding their own tests, not a Phase-1 regression); `pipeline/.python-version` = `3.12`; `uv run --directory pipeline ruff check .` → "All checks passed!"; `uv run --directory pipeline ruff format --check .` → "34 files already formatted" |
| 3 | `npm run build` builds the Vue 3 skeleton (TS, Vite, Web Awesome, vue-echarts, Hash-Router) with the Münster base components; `vue-tsc` and ESLint run clean (CI wires the same commands) | ✓ VERIFIED | `app/` is byte-identical to the previous verification pass (`git diff --stat <prev-verification-commit> -- app/` produced no output). Re-ran in a fresh scratch copy (git-archive extracted, isolated from the macOS-native `app/node_modules`): `npm ci` (EBADENGINE warnings only, expected), `npm run type-check` (vue-tsc --build, exit 0), `npm run lint` (eslint ., exit 0), `npm run format:check` (Prettier, exit 0, "All matched files use Prettier code style!"), `npm run build` (vite build, exit 0, 828 modules transformed — same module count as previous pass, `dist/index.html` emitted) |
| 4 | Haushaltsjahr, Spaltenköpfe, Seitenbereiche and PDF-Pfad live in a Jahrgangs-Konfigurationsdatei; the pipeline loads them from there, not from code | ✓ VERIFIED | `pipeline/jahrgaenge/2026.toml` grew (Phase 2/3 added sections) but still has `haushaltsjahr`, `pdf_pfad`, `[anzahlen]`, `[spalten]`, `[seitenbereiche]`, `[kopfzeilen]`; `konfiguration.py` still exports `STANDARD_JAHR`, `lade_jahrgang`, `lade_sollwerte`, `KonfigurationsFehler`, `Jahrgang`; `grep -rlw 2026 pipeline --include="*.py"` (excluding tests) → only `konfiguration.py` — no later-phase file hardcodes the Jahrgang; `alle.py`'s default-year flow (`lade_jahrgang(jahr)` / `lade_sollwerte(jahr)` with `--jahr` defaulting to `STANDARD_JAHR`) is unchanged in substance, just wrapped with additional pipeline-step orchestration |
| 5 | Project `.claude/CLAUDE.md` names pipeline/app commands and the six conventions | ✓ VERIFIED | `.claude/CLAUDE.md` unchanged since previous pass (`git diff --stat` empty); all 6 convention lead phrases and all command phrases (`lade_jahrgang`, `STANDARD_JAHR`, `uv run --directory pipeline pytest`, `npm --prefix app run build`/`lint`) still present verbatim |
| 6 (plan-level, SC3 CI detail) | `.github/workflows/ci.yml` has exactly two parallel jobs, no path filters, triggers on push+PR, `permissions: contents: read`, SHA-pinned actions | ✓ VERIFIED | File unchanged since previous pass (`git diff --stat` empty); re-confirmed directly: jobs = `pipeline app` (exactly two), no `needs:`/`paths:`, `contents: read` present, both `uses:` lines SHA-pinned with version-tag comments |
| 7 (plan-level) | Every CI `run:` command was executed locally and passed | ✓ VERIFIED | Independently re-ran both chains: pipeline (`uv sync --locked && uv run ruff check . && uv run ruff format --check . && uv run pytest` — all pass, now 295 tests) and app (`npm ci`, `type-check`, `lint`, `format:check`, `build` — all exit 0) |
| 8 (plan-level) | README.md names "Inspiriert von Münster Money (Code for Münster)" with a link; LICENSE is MIT | ✓ VERIFIED | Both files unchanged since previous pass (`git diff --stat` empty) |
| 9 (plan-level) | The running app requests nothing from a third-party host | ✓ VERIFIED | `app/` unchanged since previous pass; same self-hosted icon/no-autoloader/no-stray-hex-color/no-v-html evidence applies unmodified |
| 10 (plan-level) | `format.ts` formatting functions produce the exact specified output | ✓ VERIFIED | `app/src/charts/format.ts` unchanged since previous pass (byte-identical); behavior previously confirmed directly and is unaffected by Phase 2/3 work |

**Score:** 10/10 truths verified (0 present-but-behavior-unverified). No regressions found in the six Phase-1-owned files that Phase 2/3 legitimately extended: each retains its full original Phase-1 export surface and behavior, with the extensions being additive (new config sections, new CLI orchestration, new tests) rather than replacements of Phase-1 contracts.

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `pipeline/ostbevern/konfiguration.py` | `STANDARD_JAHR`, `lade_jahrgang`, `lade_sollwerte`, `KonfigurationsFehler`, `Jahrgang` dataclasses | ✓ VERIFIED | All exports still present (confirmed via direct `grep -n "^def \|^class \|^STANDARD_JAHR"`); file grew from Phase-1's scope to also support Phase 2/3 dataclasses (`Seitenbereich`, `Kopfzeilen`, `Anzahlen`, `SynthetischeProduktgruppe`), all additive |
| `pipeline/jahrgaenge/2026.toml` | All PDF-specific values of Haushalt 2026 | ✓ VERIFIED | Still contains `[seitenbereiche]` and all Phase-1-required tables, now also carrying Phase 2/3 sections |
| `pipeline/jahrgaenge/2026_sollwerte.toml` | Sollwerte Satzung §1, Gesamtergebnisplan head lines | ✓ VERIFIED | `[satzung]` block and `pdf_seite = 8`/`ertraege = 27_502_063` keys still present |
| `pipeline/tests/test_rauchtest.py` | D-12 Rauchtest | ✓ VERIFIED | Unchanged since previous pass; 3 test functions, all pass |
| `pipeline/alle.py` | Thin typer entry point with `--jahr` | ✓ VERIFIED | `STANDARD_JAHR` default still wired; `main()` still calls `lade_jahrgang`/`lade_sollwerte` and handles `KonfigurationsFehler`; grew to also invoke Phase 2/3 pipeline steps (`seiten`, `plaene`, `produkte`, `investitionen`, `querschnitte`, `pruefung`), which is the expected Phase-2/3 extension per `alle.py`'s own docstring ("Spätere Phasen hängen... an") |
| `pipeline/uv.lock` | Pinned dependency set | ✓ VERIFIED | Committed; `uv sync --locked` succeeds |
| `app/src/components/PageIntro.vue` | `titel`/`beschreibung` props, default slot | ✓ VERIFIED | Unchanged since previous pass |
| `app/src/router/index.ts` | Hash router, catch-all redirect | ✓ VERIFIED | Unchanged since previous pass |
| `app/src/lib/webawesome.ts` | Styles, German translation, self-hosted icon path | ✓ VERIFIED | Unchanged since previous pass |
| `app/src/main.ts` | Cherry-picked WA component registrations | ✓ VERIFIED | Unchanged since previous pass |
| `app/src/App.vue` | App shell: header/nav, RouterView, footer credit | ✓ VERIFIED | Unchanged since previous pass |
| `app/src/data/jahrgang.json` | Haushaltsjahr as data | ✓ VERIFIED | Unchanged since previous pass |
| `app/package.json` | Scripts type-check/lint/format:check/build, engines node | ✓ VERIFIED | Unchanged since previous pass |
| `app/src/charts/format.ts` | Number-formatting single source | ✓ VERIFIED | Unchanged since previous pass |
| `app/src/charts/echartsTheme.ts` | ECharts registration + WA-token theme | ✓ VERIFIED | Unchanged since previous pass |
| `app/src/components/BaseChart.vue` | vue-echarts wrapper, laedt/fehler/empty states | ✓ VERIFIED | Unchanged since previous pass |
| `app/src/components/ChartCard.vue` | Card chrome, CHART_KONTEXT, Beispieldaten notice | ✓ VERIFIED | Unchanged since previous pass |
| `app/src/components/DatenTabelle.vue` | Semantic table, slot + data mode, empty/loading states | ✓ VERIFIED | Unchanged since previous pass |
| `app/src/lib/bildschirm.ts` | Reactive narrow-screen flag | ✓ VERIFIED | Unchanged since previous pass |
| `app/src/data/beispieldaten.json` | Fictional demo fixture | ✓ VERIFIED | Unchanged since previous pass |
| `.github/workflows/ci.yml` | Two jobs, SHA-pinned actions | ✓ VERIFIED | Byte-identical to previous pass; replayed locally, passes with the current (larger) pipeline test suite |
| `.claude/CLAUDE.md` | Commands + 6 conventions | ✓ VERIFIED | Byte-identical to previous pass |
| `README.md` | Overview, quick start, license, credit | ✓ VERIFIED | Byte-identical to previous pass |
| `LICENSE` | MIT | ✓ VERIFIED | Byte-identical to previous pass |
| `app/vite.config.ts` | GitHub Pages-safe relative base (WR-01 fix) | ✓ VERIFIED | Byte-identical to previous pass; `base: './'` still present |
| `app/src/styles/basis.css` | `prefers-reduced-motion` honored for `wa-skeleton` (WR-02 fix) | ✓ VERIFIED | Byte-identical to previous pass |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| `test_rauchtest.py` | `konfiguration.py` | imports `lade_jahrgang`, `lade_sollwerte`, `STANDARD_JAHR` | ✓ WIRED | Tests pass |
| `konfiguration.py` | `jahrgaenge/2026.toml` | `tomllib.load` via `JAHRGAENGE_VERZEICHNIS / f"{jahr}.toml"` | ✓ WIRED | Re-confirmed by reading current `lade_jahrgang` |
| `jahrgaenge/2026.toml` | `raw_data/haushalt-2026.pdf` | `pdf_pfad` resolved against `PROJEKT_WURZEL` | ✓ WIRED | File exists; Rauchtest confirms page count |
| `alle.py` | `konfiguration.py` | `--jahr` defaults to `STANDARD_JAHR` | ✓ WIRED | `grep -q 'STANDARD_JAHR' pipeline/alle.py`; CLI contract still intact in current `main()` |
| `app/src/main.ts` | `app/src/lib/webawesome.ts` | first import, so `setIconPath` runs first | ✓ WIRED | Unchanged since previous pass |
| `app/src/router/index.ts` | `StartPage.vue` | route name `start` at `/` | ✓ WIRED | Unchanged since previous pass |
| `StartPage.vue` | `app/src/data/jahrgang.json` | `titel` interpolates `jahrgang.haushaltsjahr` | ✓ WIRED | Unchanged since previous pass |
| `vite.config.ts` | `wa-*` custom elements | `isCustomElement` | ✓ WIRED | Unchanged since previous pass |
| `BaseChart.vue` | `echartsTheme.ts` | imports `CHART_THEME`, passed to `VChart` | ✓ WIRED | Unchanged since previous pass |
| `BaseChart.vue` | `ChartCard.vue` | `inject(CHART_KONTEXT)` | ✓ WIRED | Unchanged since previous pass |
| `DatenTabelle.vue` | `charts/format.ts` | `wa-format-number` attrs from `EURO_OPTIONEN` | ✓ WIRED | Unchanged since previous pass |
| `.github/workflows/ci.yml` | `pipeline/uv.lock` | `uv sync --locked` | ✓ WIRED | Replayed locally, passes (295 tests now) |
| `.github/workflows/ci.yml` | `app/package.json` | npm scripts in job `app` | ✓ WIRED | Replayed locally (fresh scratch copy), passes |
| `.github/workflows/ci.yml` | `app/.nvmrc` | `node-version-file: app/.nvmrc` | ✓ WIRED | Confirmed |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|---|---|---|---|---|
| `StartPage.vue` PageIntro titel | `jahrgang.haushaltsjahr` | `app/src/data/jahrgang.json` import | Yes (not hardcoded) | ✓ FLOWING |
| `StartPage.vue` chart option | `beispieldaten.posten` | `app/src/data/beispieldaten.json` import | Yes (flagged fictional demo data, by design) | ✓ FLOWING |
| `StartPage.vue` DatenTabelle `zeilen` | computed from `beispieldaten.posten` | same JSON | Yes | ✓ FLOWING |
| `konfiguration.py` `Jahrgang` | TOML file contents | `tomllib.load` on `2026.toml` | Yes | ✓ FLOWING |
| `alle.py` CLI output | `lade_jahrgang(jahr)`/`lade_sollwerte(jahr)` | `konfiguration.py` | Yes | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Pipeline tests pass | `uv run --directory pipeline pytest -q` | `295 passed in 187.54s` | ✓ PASS |
| Pipeline lint/format clean | `uv run --directory pipeline ruff check .` / `ruff format --check .` | "All checks passed!" / "34 files already formatted" | ✓ PASS |
| App dependency install (fresh scratch copy, git-archive extracted, isolated from macOS-native `app/node_modules`) | `npm ci` | exit 0, EBADENGINE warnings only (expected) | ✓ PASS |
| App type-check | `npm run type-check` | exit 0, no output | ✓ PASS |
| App lint | `npm run lint` | exit 0, no output | ✓ PASS |
| App format check | `npm run format:check` | "All matched files use Prettier code style!" | ✓ PASS |
| App build | `npm run build` | exit 0, 828 modules, `dist/index.html` emitted | ✓ PASS |
| CI YAML structurally valid, two parallel SHA-pinned jobs | manual read + grep | jobs=`pipeline app`, no `needs:`, no path filter, `contents: read`, both `uses:` 40-hex SHA | ✓ PASS |
| CI commands replayed locally | both chains from `.github/workflows/ci.yml` | both exit 0 | ✓ PASS |
| Phase-1 config contract unbroken by Phase 2/3 extension | `grep -n "^def \|^class \|^STANDARD_JAHR"` on current `konfiguration.py`; `grep -rlw 2026 pipeline --include="*.py"` excluding tests | `STANDARD_JAHR`, `lade_jahrgang`, `lade_sollwerte`, `KonfigurationsFehler` all present; only `konfiguration.py` hardcodes `2026` | ✓ PASS |

### Probe Execution

No `scripts/*/tests/probe-*.sh` convention and no probe references found in PLAN/SUMMARY files for this phase. Step 7c: SKIPPED (no probes declared or discovered).

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| SETUP-01 | 01-02, 01-05 | Repo-Struktur nach Spez. 7, Quell-PDF unter raw_data/ | ✓ SATISFIED | Directory structure + README/LICENSE unchanged, still complete |
| SETUP-02 | 01-01, 01-02 | Pipeline uv-Projekt, `uv run pytest` läuft | ✓ SATISFIED | 295 tests pass (grown from 17 by Phase 2/3's own additions, no regression) |
| SETUP-03 | 01-01, 01-03, 01-04 | App-Grundgerüst mit Münster-Basiskomponenten, `npm run build` läuft | ✓ SATISFIED | Build green in fresh scratch copy; all 6 base component files present unchanged |
| SETUP-04 | 01-05 | Projekt-CLAUDE.md dokumentiert Befehle und Konventionen | ✓ SATISFIED | File byte-identical to previous pass, confirmed by direct read and grep |
| SETUP-05 | 01-02 | Jahrgangsspezifisches steht in Konfigurationsdatei | ✓ SATISFIED | `2026.toml`/`2026_sollwerte.toml` + loader still validated; no later-phase file reintroduces a hardcoded Jahrgang outside `konfiguration.py` |
| QUAL-01 | 01-03, 01-04, 01-05 | vue-tsc und ESLint laufen fehlerfrei in CI | ✓ SATISFIED | Local vue-tsc/ESLint clean (re-verified in a fresh scratch copy); `ci.yml` wires the identical commands, unchanged since previous pass |

No orphaned requirements found — REQUIREMENTS.md's Phase 1 mapping (SETUP-01..05, QUAL-01) matches exactly the `requirements:` fields declared across the five plans and the phase requirement IDs given for this verification run.

### Anti-Patterns Found

None blocking. Re-scanned all 25 non-doc covered files (app/src/*, pipeline/alle.py, pipeline/ostbevern/konfiguration.py, pipeline/ostbevern/__init__.py, pipeline/pyproject.toml, pipeline/tests/*, .github/workflows/ci.yml, .claude/CLAUDE.md, README.md, LICENSE) for `TBD|FIXME|XXX|TODO|HACK|PLACEHOLDER` and placeholder-style copy ("coming soon", "not yet implemented", etc.):

- One case-insensitive match of `HACK` surfaced in `.claude/CLAUDE.md` line 7, but it is the substring inside the German word "Münsterhack" (the hackathon the project is inspired by — "Münsterhack '26"), not a code comment or debt marker. Recorded under `advisory:` for transparency; not a gap.
- No other matches in any of the six Phase-1-owned files that Phase 2/3 extended, and no matches in any app/src or other pipeline file.

Code review (`01-REVIEW.md`, disposition `01-REVIEW-DISPOSITION.md`) is unchanged and final per the user's instruction for this re-verification: 0 critical findings; 5 warnings, all fixed and previously confirmed present (WR-01..WR-05, re-confirmed byte-identical this pass since `app/vite.config.ts`, `app/src/styles/basis.css`, and `app/src/components/DatenTabelle.vue` are unchanged); 5 info findings remain `open`, forward-looking, non-blocking.

### Human Verification Required

None. All Phase-1 visual/runtime items were already closed by `01-UAT.md` in the prior verification pass (18/18 passed, 0 issues) and are unaffected by the later-phase changes, since none of the files Phase 2/3 touched are UI/visual artifacts — the six changed files are all pipeline-side (`pipeline/alle.py`, `pipeline/ostbevern/konfiguration.py`, two TOML config files, two pipeline test files). No new visual surface was introduced in scope for this re-verification.

The GitHub Actions first-push confirmation remains the same contextual, non-blocking item noted in the prior report (D-18 — no GitHub remote created yet in this sandbox); unchanged assessment.

## Gaps Summary

No gaps found. Phase 1's goal — "Pipeline und App lassen sich leer bauen und testen. Die Konventionen und die Jahrgangskonfiguration sind festgelegt, und die CI prüft jeden Push." — still holds against the current codebase. The six covered files that Phase 2/3 extended (`pipeline/alle.py`, `pipeline/ostbevern/konfiguration.py`, `pipeline/jahrgaenge/2026.toml`, `pipeline/jahrgaenge/2026_sollwerte.toml`, `pipeline/tests/test_alle.py`, `pipeline/tests/test_konfiguration.py`) retain every Phase-1 export, convention, and behavior; the extensions are additive (new config sections, new CLI step orchestration, new tests), not replacements of the Phase-1 contract. All other covered files (`app/`, `.github/workflows/ci.yml`, `.claude/CLAUDE.md`, `README.md`, `LICENSE`) are byte-identical to the previous verification pass. Independently re-run: `uv run --directory pipeline pytest -q` (295 passed), `ruff check`/`ruff format --check` (clean), and the full app chain in a fresh scratch copy (`npm ci`, `type-check`, `lint`, `format:check`, `build` — all exit 0). Security (`01-SECURITY.md`: `threats_open: 0`) and the unchanged, final code-review disposition both corroborate this result. Status is `passed`.

---

_Verified: 2026-10-02T09:35:14Z_
_Verifier: Claude (gsd-verifier)_
