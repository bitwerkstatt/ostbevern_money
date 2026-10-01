---
phase: 01-setup
plan: 02
subsystem: pipeline
tags: [uv, python, pdfplumber, polars, typer, pytest, ruff, toml, tomllib, tdd]

# Dependency graph
requires:
  - phase: 01-setup
    provides: "01-01: human-approved PyPI package list (pdfplumber, polars, typer, pytest, ruff)"
provides:
  - "pipeline/ uv project: Python 3.12, pdfplumber/polars/typer runtime, pytest/ruff dev — `uv run pytest` and `ruff check`/`ruff format --check` all green"
  - "ostbevern.konfiguration: STANDARD_JAHR, lade_jahrgang(jahr), lade_sollwerte(jahr), KonfigurationsFehler — the single loader every later pipeline script and test must use"
  - "pipeline/jahrgaenge/2026.toml and 2026_sollwerte.toml: every PDF-specific value and the Anhang-B head figures for Haushalt 2026"
  - "pipeline/alle.py: thin typer entry point validating --jahr, ready for Phase 2+ to append numbered steps"
  - "daten/{zwischen,aufbereitet,manuell,pruefberichte}/ directory layout, tracked in git"
  - "raw_data/haushalt-2026.pdf as the single tracked source PDF (D-11 rename complete)"
affects: [01-setup/01-04, 01-setup/01-05, 02-extraktion]

# Actuals (#2632)
actuals:
  tokens: 39578
  tasks: 3
  commits: 4
  plan_head_before: cf45a669649dff8dcbdaa50c257d7778fecec889
  plan_head_after: f6c00308b48cff1cded69918e8ca39b01fe30487

# Tech tracking
tech-stack:
  added: ["pdfplumber 0.11.10", "polars 1.44.2", "typer 0.27.2", "pytest 9.1.1 (dev)", "ruff 0.16.9 (dev)"]
  patterns:
    - "Single-source Jahrgang/Sollwerte loader: ostbevern.konfiguration.lade_jahrgang/lade_sollwerte is the only place tomllib is imported; every script and test goes through it"
    - "Thin typer CLI wrapping library logic: alle.py holds only argument handling, all logic in ostbevern/"
    - "TDD fixtures as text variants of the real TOML files: tests derive tmp_path fixtures from the real 2026.toml/2026_sollwerte.toml via regex edits, never hardcode year/page/Sollwert literals"

key-files:
  created:
    - "pipeline/ostbevern/konfiguration.py"
    - "pipeline/ostbevern/__init__.py"
    - "pipeline/jahrgaenge/2026.toml"
    - "pipeline/jahrgaenge/2026_sollwerte.toml"
    - "pipeline/alle.py"
    - "pipeline/tests/test_rauchtest.py"
    - "pipeline/tests/test_konfiguration.py"
    - "pipeline/tests/test_alle.py"
    - "pipeline/pyproject.toml"
    - "pipeline/.python-version"
    - "pipeline/uv.lock"
    - ".gitignore"
    - "daten/zwischen/.gitkeep"
    - "daten/aufbereitet/.gitkeep"
    - "daten/manuell/.gitkeep"
    - "daten/pruefberichte/.gitkeep"
  modified:
    - "raw_data/haushalt-2026.pdf (renamed from raw_data/Haushalt 2026 komplett.pdf; discussion/ copy deleted, D-11)"

key-decisions:
  - "PDF rename executed as two explicit git operations (git mv + git rm) per D-11; git's content-based rename detection paired the final raw_data/haushalt-2026.pdf with the discussion/ copy rather than the raw_data/ original (both are byte-identical), but `git log --follow` still finds 2 ancestor commits either way — not a functional problem"
  - "Task 1 shipped as a type=tracer slice (minimal Jahrgangsdatei: haushaltsjahr/pdf_pfad/anzahlen.pdf_seiten only); the tracer feedback gate re-ran both automated <verify> commands after Task 1's commit and both passed, so Task 2 (TDD expansion) proceeded without a checkpoint per the end-of-phase/automated-only precedence rule"
  - "Task 2 followed RED-GREEN-REFACTOR: RED commit (32c3f8f) has 12 new tests that fail to import PFLICHT_SEITENBEREICHE/lade_sollwerte/extended dataclass fields (collection ImportError — the expected signal since this entire API surface is net-new); GREEN commit (7f12076) implements it, no REFACTOR commit needed (implementation was already clean)"
  - "Jahrgangsdatei/Sollwertdatei content (Seitenbereiche, Spaltenköpfe, Satzung §1-3, Gesamtergebnisplan head lines) transcribed directly from discussion/SPEZIFIKATION.md §2.2/§2 table and Anhang B.1/B.2, cross-checked against the PLAN.md's already-verified values"
  - "D-10: numbered step scripts (01_seiten_klassifizieren.py .. 08_quellenbelege.py) are NOT created in this phase — only alle.py exists as the orchestrator stub. Each numbered script arrives with its logic in the phase that implements it (Phase 2: 01/02/06; Phase 3: 03/04; Phase 4: 05/07; Phase 7: 08), so no empty placeholder module ships ahead of its behavior"
  - "ruff select = [E, F, I, UP, B], line-length 100, target py312, double-quote format — two E501 violations surfaced by the new config were fixed by wrapping f-string error messages across lines"

patterns-established:
  - "Pattern: single-source year config — pipeline/ostbevern/konfiguration.py is the only module that imports tomllib; lade_jahrgang/lade_sollwerte validate every required key at once and raise KonfigurationsFehler naming what's wrong"
  - "Pattern: TDD fixtures derived from real config files — tests never hardcode year/page-count/Sollwert literals (D-08); they read the real TOML, edit it via regex/tmp_path, and compare against the imported STANDARD_JAHR constant"

requirements-completed: [SETUP-01, SETUP-02, SETUP-05]

coverage:
  - id: D1
    description: "Tracer slice: renamed PDF -> minimal Jahrgangsdatei -> lade_jahrgang -> Rauchtest proves the PDF exists with the expected page count, all from config"
    requirement: "SETUP-02"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_rauchtest.py#test_jahrgangsdatei_laedt"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_rauchtest.py#test_pdf_existiert_mit_erwarteter_seitenzahl"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_rauchtest.py#test_sollwertdatei_laedt"
        status: pass
    human_judgment: false
  - id: D2
    description: "Jahrgangsdatei (D-07: Spaltenköpfe, Seitenbereiche, Kopfzeilen, Anzahlen) and Sollwertdatei (D-08: Satzung §1-3, Gesamtergebnisplan head lines) complete, with full key/type/bounds validation and a named German KonfigurationsFehler for every malformed case"
    requirement: "SETUP-05"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_konfiguration.py (12 tests: completeness, von<=bis bounds, missing-key errors, missing year file, haushaltsjahr mismatch, absolute/outside-project pdf_pfad rejection, Seitenbereich von>bis rejection, lade_sollwerte structure, float-Sollwert rejection, row-length rejection)"
        status: pass
    human_judgment: false
  - id: D3
    description: "alle.py validates any --jahr (default STANDARD_JAHR), ruff (check + format) is clean across pipeline/, daten/ layout exists and is tracked"
    requirement: "SETUP-01"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_alle.py#test_ohne_jahr_nutzt_standardjahr"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_alle.py#test_unbekannter_jahrgang_bricht_ab"
        status: pass
      - kind: other
        ref: "uv run --directory pipeline ruff check . && uv run --directory pipeline ruff format --check ."
        status: pass
    human_judgment: false

# Metrics
duration: 25 min
completed: 2026-10-01
status: complete
---

# Phase 1 Plan 2: Pipeline Scaffold Summary

**uv-managed Python 3.12 pipeline (`pdfplumber`/`polars`/`typer`, `pytest`/`ruff` dev) with a single `ostbevern.konfiguration` loader that validates the Jahrgangs- and Sollwertdatei for 2026 against a named German error, plus a thin `alle.py --jahr` entry point and the `daten/` layout — all 17 tests and both ruff checks green.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-10-01T08:58:00Z (approx.)
- **Completed:** 2026-10-01T09:22:59Z
- **Tasks:** 3 (Task 1 tracer, Task 2 TDD, Task 3 auto)
- **Files modified:** 18 (16 created, raw_data/haushalt-2026.pdf renamed, discussion/ duplicate deleted)

## Accomplishments

- Renamed `raw_data/Haushalt 2026 komplett.pdf` -> `raw_data/haushalt-2026.pdf` and deleted the `discussion/` duplicate (D-11), with git rename history preserved
- Built `pipeline/` as a uv project (Python 3.12, `pdfplumber`/`polars`/`typer` runtime, `pytest`/`ruff` dev) using exactly the versions approved in 01-01 (pdfplumber 0.11.10, polars 1.44.2, typer 0.27.2, pytest 9.1.1, ruff 0.16.9)
- Wrote `ostbevern.konfiguration` with `STANDARD_JAHR = 2026` as the single place the default year appears in Python code, `lade_jahrgang`/`lade_sollwerte` loaders, and `KonfigurationsFehler` for every malformed-input case (missing keys reported together, int-not-bool/float checks, haushaltsjahr match, pdf_pfad relative-and-inside-project, Seitenbereich bounds, row-length checks)
- Completed `pipeline/jahrgaenge/2026.toml` (Spaltenköpfe, 15 Seitenbereiche, Kopfzeilen-Muster, Anzahlen) and the new `2026_sollwerte.toml` (Satzung §1-3, Gesamtergebnisplan B.1 head lines) via a full RED-GREEN TDD cycle
- Added `pipeline/alle.py`, a thin typer CLI validating `--jahr` (default `STANDARD_JAHR`) against the Jahrgangs-/Sollwertdatei and PDF existence
- Configured ruff (`select = [E, F, I, UP, B]`, line-length 100, double quotes); `ruff check .` and `ruff format --check .` are both clean
- Created the `daten/{zwischen,aufbereitet,manuell,pruefberichte}/` layout with `.gitkeep` placeholders, all tracked in git

## Task Commits

Tasks were committed atomically, with Task 2 split into RED/GREEN per TDD:

1. **Task 1: Tracer — PDF -> Jahrgangsdatei -> lade_jahrgang -> Rauchtest** - `358a87b` (feat)
2. **Task 2 RED: failing tests for Jahrgangsdatei/Sollwertdatei validation** - `32c3f8f` (test)
3. **Task 2 GREEN: complete Jahrgangsdatei/Sollwertdatei with full validation** - `7f12076` (feat)
4. **Task 3: alle.py entry point, ruff rules, daten/ layout** - `f6c0030` (feat)

**Plan metadata:** commit created immediately after this SUMMARY (see below).

_Note: Task 2 (`tdd="true"`) produced two commits (RED test, then GREEN implementation); no REFACTOR commit was needed — the GREEN implementation was already clean on first pass._

## Files Created/Modified

- `pipeline/ostbevern/konfiguration.py` - Single Jahrgangs-/Sollwertdatei loader: dataclasses (`Jahrgang`, `Anzahlen`, `Seitenbereich`, `Kopfzeilen`), `lade_jahrgang`, `lade_sollwerte`, `KonfigurationsFehler`
- `pipeline/ostbevern/__init__.py` - Package marker
- `pipeline/jahrgaenge/2026.toml` - Haushaltsjahr, pdf_pfad, Anzahlen, Spalten, 15 Seitenbereiche, Kopfzeilen-Muster
- `pipeline/jahrgaenge/2026_sollwerte.toml` - Satzung §1-3 (PDF S. 8), Gesamtergebnisplan B.1 head lines (Zeilen 10/17/18/19/20/26/27/28)
- `pipeline/alle.py` - Thin typer entry point, `--jahr` option, validates and prints Jahrgang summary
- `pipeline/tests/test_rauchtest.py` - D-12 Rauchtest: Jahrgangsdatei lädt, PDF existiert mit erwarteter Seitenzahl, Sollwertdatei lädt
- `pipeline/tests/test_konfiguration.py` - 12 tests for `lade_jahrgang`/`lade_sollwerte` validation behavior
- `pipeline/tests/test_alle.py` - CliRunner tests for `alle.py` (default year, unknown-year abort)
- `pipeline/pyproject.toml` - uv project config, `[tool.pytest.ini_options]`, `[tool.ruff]`/`[tool.ruff.lint]`/`[tool.ruff.format]`
- `pipeline/.python-version` - "3.12"
- `pipeline/uv.lock` - Pinned, hashed dependency set
- `.gitignore` - Root gitignore (`.DS_Store`, caches, `.venv/`, `node_modules/`, `dist/`, `*.tsbuildinfo`); nothing under `daten/` ignored
- `daten/{zwischen,aufbereitet,manuell,pruefberichte}/.gitkeep` - Tracked empty directories
- `raw_data/haushalt-2026.pdf` - Renamed from `raw_data/Haushalt 2026 komplett.pdf`; `discussion/Haushalt 2026 komplett.pdf` deleted

## Decisions Made

- PDF rename as two explicit git operations (D-11); git's rename-pair detection (content-identical files) attributed the rename to the `discussion/` copy rather than the `raw_data/` original in the diff view, but `git log --follow -- raw_data/haushalt-2026.pdf` still returns 2 ancestor commits, satisfying the plan's acceptance criterion
- Task 1 (tracer) followed by the tracer feedback gate: both automated `<verify>` commands were re-run after the tracer commit and passed, so Task 2 proceeded directly (interactive, `human_verify_mode=end-of-phase`, automated-only verify — no checkpoint per the precedence chain)
- Task 2 TDD RED signal was a pytest collection `ImportError` (new symbols referenced by the tests did not exist yet) rather than a per-test assertion failure — treated as the correct and expected RED for net-new API surface, documented in the RED commit message
- Numbered pipeline step scripts (`01_seiten_klassifizieren.py` .. `08_quellenbelege.py`) deliberately not created (D-10 discretion) — only `alle.py` exists as the future orchestrator; each script arrives with its logic in the phase that implements it

## Deviations from Plan

None - plan executed exactly as written. The two ruff E501 line-length violations surfaced by adding `[tool.ruff.lint]` in Task 3 were anticipated by the plan's own action text ("fix everything `ruff check .` reports") and fixed inline as part of Task 3, not tracked as a separate deviation.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `pipeline/` is a green, ruff-clean uv project ready for Phase 2's extraction scripts (`01_seiten_klassifizieren.py`, `02_plaene_extrahieren.py`, `06_pruefen.py`) to be added as thin typer wrappers calling into `ostbevern/`
- `ostbevern.konfiguration.lade_jahrgang`/`lade_sollwerte` are the stable contract every future script and test must use — no script may call `tomllib.load()` directly or hardcode a year/page/Sollwert value
- `pipeline/jahrgaenge/2026_sollwerte.toml` holds only the Satzung and Gesamtergebnisplan head lines (B.1 partial); Phase 2 must complete B.1, add B.2 and B.3 per the file's own header comment
- No blockers or concerns; 01-03 (app scaffold) runs independently in a parallel worktree and does not depend on this plan's output

---
*Phase: 01-setup*
*Completed: 2026-10-01*

## Self-Check: PASSED

- `FOUND: pipeline/ostbevern/konfiguration.py`, `FOUND: pipeline/jahrgaenge/2026_sollwerte.toml`, `FOUND: pipeline/alle.py`, `FOUND: raw_data/haushalt-2026.pdf`, `FOUND: all 4 daten/*/.gitkeep` — all key created files verified on disk
- Commits verified in `git log --oneline --all`: `358a87b` (Task 1 tracer), `32c3f8f` (Task 2 RED), `7f12076` (Task 2 GREEN), `f6c0030` (Task 3)
- Re-ran `uv run --directory pipeline pytest -q`: 17 passed
- Re-ran `uv run --directory pipeline ruff check .` and `ruff format --check .`: both clean
- Re-ran `uv run --directory pipeline python alle.py --jahr 2026`: prints `Jahrgang 2026: raw_data/haushalt-2026.pdf (400 Seiten erwartet), 15 Seitenbereiche, Sollwerte geladen.`, exit 0
- `git ls-files -- 'raw_data/*.pdf' 'discussion/*.pdf'` returns exactly `raw_data/haushalt-2026.pdf`
- `git ls-files daten` returns exactly the 4 expected `.gitkeep` paths
- Commit ledger: `plan_head_before=cf45a669649dff8dcbdaa50c257d7778fecec889`, `plan_head_after=f6c00308b48cff1cded69918e8ca39b01fe30487`, `git rev-list --count` = 4 (matches `actuals.commits: 4`)
