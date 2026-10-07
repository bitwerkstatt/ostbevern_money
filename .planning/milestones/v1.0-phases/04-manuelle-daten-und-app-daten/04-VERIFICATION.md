---
phase: 04-manuelle-daten-und-app-daten
verified: 2026-10-04T08:51:42Z
status: passed
score: 10/10 must-haves verified
covered_files:
  - ".github/workflows/ci.yml"
  - ".planning/phases/04-manuelle-daten-und-app-daten/04-01-PLAN.md"
  - ".planning/phases/04-manuelle-daten-und-app-daten/04-01-SUMMARY.md"
  - ".planning/phases/04-manuelle-daten-und-app-daten/04-02-PLAN.md"
  - ".planning/phases/04-manuelle-daten-und-app-daten/04-02-SUMMARY.md"
  - ".planning/phases/04-manuelle-daten-und-app-daten/04-03-PLAN.md"
  - ".planning/phases/04-manuelle-daten-und-app-daten/04-03-SUMMARY.md"
  - ".planning/phases/04-manuelle-daten-und-app-daten/04-04-PLAN.md"
  - ".planning/phases/04-manuelle-daten-und-app-daten/04-04-SUMMARY.md"
  - ".planning/phases/04-manuelle-daten-und-app-daten/04-05-PLAN.md"
  - ".planning/phases/04-manuelle-daten-und-app-daten/04-05-SUMMARY.md"
  - ".planning/phases/04-manuelle-daten-und-app-daten/04-06-PLAN.md"
  - ".planning/phases/04-manuelle-daten-und-app-daten/04-06-SUMMARY.md"
  - ".planning/phases/04-manuelle-daten-und-app-daten/04-REVIEW-DISPOSITION.md"
  - ".planning/phases/04-manuelle-daten-und-app-daten/04-REVIEW.md"
  - "app/.prettierignore"
  - "app/src/charts/format.ts"
  - "app/src/data/daten.ts"
  - "app/src/data/texte.json"
  - "app/src/data/typen.ts"
  - "daten/manuell/README.md"
  - "daten/manuell/texte/erklaerungen.md"
  - "pipeline/05_stellenplan.py"
  - "pipeline/07_app_daten.py"
  - "pipeline/alle.py"
  - "pipeline/ostbevern/app_daten.py"
  - "pipeline/ostbevern/konfiguration.py"
  - "pipeline/ostbevern/manuell.py"
  - "pipeline/ostbevern/pruefung.py"
  - "pipeline/ostbevern/schema.py"
  - "pipeline/ostbevern/stellenplan.py"
  - "pipeline/ostbevern/texte.py"
  - "pipeline/tests/test_formatiere.py"
covered_digest: "v2:sha256:c0d25de8b80abcea3dd297f318fd34e24cba96b9ada351fc5f03b86895dfa127"
behavior_unverified: 0
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 9/10
  gaps_closed:
    - "MANU-08/D-15: Jede Zahl in den Erklärtexten wird beim Rendern über formatiere() korrekt angezeigt (CR-01: Haushaltsjahr rendered as '2.026' via formatiere(…,'zahl'))"
  gaps_remaining: []
  regressions: []
---

# Phase 4: Manuelle Daten und App-Daten Verification Report

**Phase Goal:** Die Pipeline ist geschlossen. Die Vorberichtswerte sind manuell gepflegt und gegen den Plan geprüft, der Stellenplan ist extrahiert, und die App-JSON-Dateien entstehen reproduzierbar ohne Personennamen.
**Verified:** 2026-10-04T08:51:42Z
**Status:** passed
**Re-verification:** Yes — after gap closure (plan 04-06, CR-01)

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | SC1: Alle Tabellen in `daten/manuell/` haben eine `quelle`-Spalte und ein README begründet die Werte; Regel 5 grün inkl. Befunde | ✓ VERIFIED (regression) | `alle.py --jahr 2026` run shows `Regel 5: grün (133 Werte)`; files unchanged since last verification |
| 2 | SC2: `meta.json` enthält Einwohner 11.741, Hebesätze 242/554/418 %, Kreisumlage; `erklaerungen.md` enthält geprüfte Erklärtexte mit Seitenverweis | ✓ VERIFIED (regression) | `python3 -c "json.load(...)"`: einwohner.wert=11741, hebesaetze={242,554,418}; 10 `## <schluessel>` sections unchanged |
| 3 | SC2b: Schuldenstand/Rücklagen/VE-Übersicht liegen mit Quelle vor | ✓ VERIFIED (regression) | Files unchanged since last verification; not touched by 04-06 (`git diff --quiet f9e085d -- app/src/data/typen.ts app/src/data/daten.ts pipeline/ostbevern/app_daten.py pipeline/ostbevern/pruefung.py` exits 0 per 04-06 acceptance criteria) |
| 4 | SC3: `stellenplan.csv` Teil A/B + Stellenübersicht, Beamte 2026 = 8 | ✓ VERIFIED (regression) | `daten/aufbereitet/stellenplan.csv` re-checked: 162 rows; `Regel 9/10: grün` in `alle.py` output |
| 5 | SC4: `app/src/data/` enthält die vier JSON-Dateien ohne Personennamen; KL-Split; Zuschussbedarf berechnet | ✓ VERIFIED (regression) | `pytest tests/test_app_daten.py -k personennamen`: 1 passed; files present |
| 6 | SC5: `alle.py` läuft alle Schritte in Reihenfolge; CI schlägt bei Diff fehl | ✓ VERIFIED | Re-ran `uv run --directory pipeline python alle.py --jahr 2026` myself: exit 0, Schritte 01→07 in order; `git diff --stat --exit-code -- daten app/src/data` exits 0 with no output; `git status --porcelain --untracked-files=all -- daten app/src/data` empty; `.github/workflows/ci.yml:43` runs the identical check |
| 7 | Requirement coverage: all 14 declared IDs are claimed by a plan and have supporting evidence | ✓ VERIFIED | All 14 IDs (MANU-01..08, PRUEF-05, EXTR-10, DATA-01..03, PRUEF-10) present in REQUIREMENTS.md mapped to Phase 4; no orphans found |
| 8 | Full pipeline test suite green, lint/format clean, app checks green, pipeline reproducible | ✓ VERIFIED | I independently ran: `uv run --directory pipeline pytest -q` → **472 passed in 340.36s**; `ruff check .` → "All checks passed!"; `ruff format --check .` → "46 files already formatted"; scratch-copy (`tar` + `npm ci`) `type-check`/`lint`/`format:check`/`build` all exit 0, `dist/` produced |
| 9 | MANU-08/D-15: Jede Zahl in den Erklärtexten ist ein Platzhalter; kein nackter Ziffernlauf außer Jahren/§/S. | ✓ VERIFIED (regression) | `test_texte.py -k "formatkuerzel or erklaerungen"`: 15 passed |
| 10 | MANU-08/D-15: Jede Zahl in den Erklärtexten wird beim Rendern über `formatiere()` **korrekt** angezeigt (CR-01) | ✓ VERIFIED (gap closed) | `app/src/charts/format.ts` now has `jahr()`/`JAHR_FORMAT` (`useGrouping: false`) and `case 'jahr'` in `formatiere()`; `pipeline/ostbevern/texte.py` FORMATKUERZEL has `"jahr"` in the same position; all 10 `{{jahr.haushaltsjahr|zahl}}` placeholders in `erklaerungen.md`/`texte.json` changed to `|jahr}}`, byte-identical to `f9e085d` apart from the 10 suffixes (independently diffed); **I independently transpiled the real `format.ts` in a scratch `app/` copy with the app's own `typescript` devDependency and rendered all 10 `jahr.*` placeholders of the regenerated `texte.json` through the real `formatiere()`: all 10 render as bare 4-digit years ("2026"), not "2.026"**; `pipeline/tests/test_formatiere.py` (new, 16 tests) renders every placeholder of `erklaerungen.md` and `texte.json` through a Python port and proves the CR-01 pattern is mechanically detected — I ran it myself: **16 passed**, including `test_port_wie_format_ts` (the Node cross-check against the real `format.ts`, which actually executed because `app/node_modules/typescript` exists in this checkout) |

**Score:** 10/10 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `app/src/charts/format.ts` | `formatiere()`/`FormatKuerzel` dispatcher incl. ungrouped `jahr` kürzel | ✓ VERIFIED | `JAHR_FORMAT` constant, `jahr()` function, `'jahr'` in the `FormatKuerzel` union directly after `'zahl'`, `case 'jahr': return jahr(wert)` in `formatiere()` — all present and confirmed by direct `Read` |
| `pipeline/ostbevern/texte.py` | `FORMATKUERZEL` tuple incl. `"jahr"`, same order as the TS union | ✓ VERIFIED | `FORMATKUERZEL: tuple[str, ...] = ("euro", "mio", "zahl", "jahr", "prozent", "promille", "vzae")` confirmed by direct `Read` |
| `daten/manuell/texte/erklaerungen.md` | 10 `jahr.haushaltsjahr` placeholders using the `jahr` kürzel, wording unchanged | ✓ VERIFIED | `grep -c '{{jahr\.haushaltsjahr|jahr}}'` = 10, 0 remaining `|zahl}}` occurrences for this key; suffix-normalized diff against `f9e085d` is empty |
| `app/src/data/texte.json` | Regenerated with the corrected placeholders, raw `werte` unchanged | ✓ VERIFIED | Same 10/10 count; suffix-normalized diff against `f9e085d` is empty; regenerating via `alle.py` reproduces it byte-for-byte |
| `daten/manuell/README.md` | Format-kürzel vocabulary sentence extended with `jahr` | ✓ VERIFIED | `` `zahl`, `jahr`, `prozent` `` present in the vocabulary sentence |
| `pipeline/tests/test_formatiere.py` | Python port of `formatiere()`, rendering tests, CR-01 mutation test, Node cross-check | ✓ VERIFIED | File exists, 16 tests (`test_port_deckt_alle_formatkuerzel_ab`, `test_port_beispiele` ×11, `test_erklaerungen_rendern_korrekt`, `test_texte_json_rendert_korrekt`, `test_cr01_gruppiertes_haushaltsjahr_wird_erkannt`, `test_port_wie_format_ts`); all 16 pass when I ran them |
| `.planning/phases/04-manuelle-daten-und-app-daten/04-REVIEW-DISPOSITION.md` | CR-01 row set to `fixed` | ✓ VERIFIED | `\| CR-01 \| critical \| fixed \|` confirmed in the current file |
| `.github/workflows/ci.yml` | Reproducibility gate (D-24) | ✓ VERIFIED (regression) | `git diff --stat --exit-code -- daten app/src/data` step still present at line 43 |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `app/src/charts/format.ts` (`formatiere`) | `pipeline/ostbevern/texte.py` (`FORMATKUERZEL`) | Order-sensitive single-line sync, `test_formatkuerzel_wie_format_ts` | ✓ WIRED | Test passes (`test_texte.py -k formatkuerzel`: part of 15 passed); both lists read `euro, mio, zahl, jahr, prozent, promille, vzae` |
| `daten/manuell/texte/erklaerungen.md` | `app/src/data/texte.json` | Schritt 07 (`app_daten.erzeuge_app_daten`) regenerates texte.json from erklaerungen.md | ✓ WIRED | `alle.py --jahr 2026` output: "Schritt 07: geschrieben: app/src/data/texte.json"; regenerated file is byte-identical to the committed one (clean `git diff`) |
| `app/src/data/texte.json` | real `app/src/charts/format.ts::formatiere()` | Node subprocess transpile-and-import (test_port_wie_format_ts and my own independent scratch-copy check) | ✓ WIRED | Both my own ad-hoc Node check and `test_port_wie_format_ts` (ran, not skipped, because `app/node_modules/typescript` exists) confirm the real `formatiere()` renders all 10 `jahr.*` placeholders correctly |
| `pipeline/tests/test_formatiere.py` | `pipeline/ostbevern/texte.py` (`loese_auf`, `textwerte`, `lies_erklaerungen`) | Direct import and fixture use | ✓ WIRED | Imports confirmed in file; fixtures build `werte`/`echte_erklaerungen` from the real pipeline functions, not mocks |
| `pipeline/alle.py` | `pipeline/ostbevern/app_daten.py` / `stellenplan.py` | Unchanged since initial verification | ✓ WIRED (regression) | Not modified by 04-06; `alle.py` run confirms Schritt 05/07 output unchanged in structure |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|----------|---------------|--------|---------------------|--------|
| `app/src/data/texte.json` `werte["jahr.haushaltsjahr"]` | raw int (e.g. 2026) | `textwerte()` from `haushalt.json["haushaltsjahr"]` | Yes — regeneration via `alle.py` reproduces identical value, no static fallback | ✓ FLOWING |
| `formatiere(2026, 'jahr')` render | rendered string | `JAHR_FORMAT.format(wert)` (`Intl.NumberFormat` with `useGrouping: false`) | Yes — confirmed via transpiled real source in a scratch copy, output `"2026"` not a hardcoded literal | ✓ FLOWING |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Full pipeline test suite | `uv run --directory pipeline pytest -q` | `472 passed in 340.36s` | ✓ PASS |
| New gap-closure test module | `uv run --directory pipeline pytest tests/test_formatiere.py -q -rA` | `16 passed` (incl. `test_port_wie_format_ts` actually executed, not skipped) | ✓ PASS |
| Formatkürzel sync test | `uv run --directory pipeline pytest tests/test_texte.py -q -k "formatkuerzel or erklaerungen"` | `15 passed` | ✓ PASS |
| Person-name scan | `pytest tests/test_app_daten.py -q -k personennamen` | `1 passed` | ✓ PASS |
| Ruff lint/format | `ruff check . && ruff format --check .` | "All checks passed!", "46 files already formatted" | ✓ PASS |
| Reproducibility | `alle.py --jahr 2026 && git diff --stat --exit-code -- daten app/src/data` | exit 0, no diff, no untracked files (re-ran myself) | ✓ PASS |
| App type-check/lint/format/build (scratch copy, independently built) | `npm ci && npm run type-check && npm run lint && npm run format:check && npm run build` | all exit 0, `dist/` produced | ✓ PASS |
| **CR-01 fix confirmation** | Transpiled real `format.ts` in a scratch copy, rendered all 10 `jahr.*` placeholders of regenerated `texte.json` | `jahr-Platzhalter korrekt gerendert: 10` | ✓ PASS |
| **CR-01 regression guard** | `test_cr01_gruppiertes_haushaltsjahr_wird_erkannt` | Proves `_verstoesse` flags the old `zahl`-kürzel pattern and accepts the new `jahr`-kürzel pattern | ✓ PASS |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| MANU-01 | 04-01 | steuerarten.csv | ✓ SATISFIED | Unchanged since initial verification |
| MANU-02 | 04-01 | zuwendungen.csv | ✓ SATISFIED | Unchanged |
| MANU-03 | 04-01 | transferaufwendungen.csv | ✓ SATISFIED | Unchanged |
| MANU-04 | 04-01 | kita_zuschuesse.csv | ✓ SATISFIED | Unchanged |
| MANU-05 | 04-02 | weitere_vorberichtstabellen.csv | ✓ SATISFIED | Unchanged |
| MANU-06 | 04-02 | meta.json | ✓ SATISFIED | Unchanged |
| MANU-07 | 04-01/02/03 | `quelle` column + README | ✓ SATISFIED | Unchanged |
| MANU-08 | 04-05, 04-06 | Geprüfte Erklärtexte mit Seitenverweis, korrekt gerendert | ✓ SATISFIED (was PARTIALLY) | CR-01 fixed and independently confirmed (Truth 10) |
| PRUEF-05 | 04-01/02 | Regel 5 grün | ✓ SATISFIED | Unchanged |
| EXTR-10 | 04-03 | Stellenplan extrahiert | ✓ SATISFIED | Unchanged |
| DATA-01 | 04-01/03/04/05/06 | App-JSON-Dateien erzeugt | ✓ SATISFIED | texte.json regenerated with corrected placeholders, still only raw values |
| DATA-02 | 04-04 | "Weitergabe an Kreis und Land" separiert | ✓ SATISFIED | Unchanged |
| DATA-03 | 04-04 | Zuschussbedarf berechnet gekennzeichnet | ✓ SATISFIED | Unchanged |
| PRUEF-10 | 04-01/03/05/06 | alle.py + CI-Diff-Prüfung | ✓ SATISFIED | Re-confirmed green after the CR-01 fix |

No orphaned Phase-4 requirements found in REQUIREMENTS.md beyond the 14 declared. **Bookkeeping note (non-blocking):** `.planning/REQUIREMENTS.md`'s tracking table still shows all 14 Phase-4 rows as "Gaps Found" (set by commit `49e1caf` after the initial verification) and the checkbox list above it is still unchecked — this predates the gap-closure plan and was deliberately left untouched by the 04-06 worktree executor ("deferred to the orchestrator's centralized post-wave update", per 04-06-SUMMARY.md). It is stale documentation bookkeeping, not evidence of a code gap — every one of the 14 requirements is independently confirmed satisfied above. It should be updated to "Complete" as part of closing out this phase.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---|---|---|---|
| `pipeline/ostbevern/texte.py` | ~54, 122 (`_SEITENZAHL_MUSTER`) | WR-04 (new, 04-REVIEW.md): range-style `Quelle:` lines (`S. 24/25`) silently drop all but the first page | ⚠️ Warning | Latent — does not trigger on current data (all 10 sections repeat `S.` per page); would silently truncate `quelle_seiten` if a future edit used the compact range form |
| `pipeline/ostbevern/texte.py` | ~138-176 (`pruefe_text`) | WR-05 (new): the CR-01 jahr-namespace-vs-kürzel invariant is enforced only by the test suite (`test_formatiere.py::_verstoesse`), not by the pipeline's own fail-fast `pruefe_text` | ⚠️ Warning | A future `{{jahr.irgendwas\|zahl}}` edit would ship silently unless someone remembers to run pytest; overlaps conceptually with the already-open IN-01 |
| `app/src/charts/format.ts` | 80-97 (`formatiere`) | WR-06 (new): no `default`/exhaustiveness guard — an out-of-union runtime kürzel silently renders `undefined` | ⚠️ Warning | Same underlying gap as the already-open IN-01; not worsened by 04-06 |
| `app/src/data/texte.json` | 2, 118 | IN-02 (new): `haushaltsjahr` stored at both the top level and `werte["jahr.haushaltsjahr"]`, no cross-check | ℹ️ Info | Drift risk only on a future refactor; both values currently match |
| `pipeline/ostbevern/pruefung.py` | ~1555-1656 | WR-01 (carried forward, still open): per-year VE summary rows never cross-checked | ⚠️ Warning | Unchanged since initial verification; out of scope for 04-06 by explicit user decision 2026-10-03 |
| `pipeline/ostbevern/app_daten.py` | ~570-586 | WR-02 (carried forward, still open): unguarded negative-index fallback | ⚠️ Warning | Unchanged; out of scope by user decision |
| `pipeline/ostbevern/texte.py` | ~204-227 | WR-03 (carried forward, still open): unguarded neighbour-year lookups | ⚠️ Warning | Unchanged; out of scope by user decision |
| `app/src/charts/format.ts` | 68-97 | IN-01 (carried forward, still open): no fallback/exhaustiveness in `formatiere()` | ℹ️ Info | Unchanged; out of scope by user decision; functionally the same concern as the new WR-06 |

**No critical/blocker findings.** `04-REVIEW.md` (incremental review after 04-06) reports `critical: 0, warning: 3, info: 1` — consistent with my own reading of the diff. `04-REVIEW-DISPOSITION.md` records CR-01 as `fixed` and all eight warning/info rows (four carried forward, four new) as `open`, which the user explicitly scoped out of this gap-closure plan on 2026-10-03 ("WR/IN items (old and new) are advisory and out of scope for this gap closure by user decision"). None of these warnings reproduce on the currently-shipped data; none block the phase goal.

### Human Verification Required

None. CR-01's fix was independently confirmed through deterministic, reproducible evidence (direct code reading, a from-scratch rebuild of the app, and running the real `formatiere()` against the regenerated `texte.json` in a scratch copy) — not just by re-reading SUMMARY.md's narration. The remaining open warnings (WR-01..06, IN-01, IN-02) are non-blocking design/robustness gaps explicitly deferred by user decision, not uncertain judgment calls.

### Gaps Summary

No gaps remain. The single blocking gap from the initial verification — **CR-01** (the Haushaltsjahr rendering as "2.026" instead of "2026" through `formatiere(wert, 'zahl')`) — is closed by plan 04-06 and independently re-verified here, not merely trusted from SUMMARY.md:

- `app/src/charts/format.ts` and `pipeline/ostbevern/texte.py` both now carry an ungrouped `jahr` format kürzel, kept in sync by the pre-existing order-sensitive `test_formatkuerzel_wie_format_ts`.
- All ten `jahr.haushaltsjahr` placeholders in `erklaerungen.md` and the regenerated `app/src/data/texte.json` use the new kürzel; a suffix-normalized diff proves the approved D-17 wording is otherwise byte-identical to the base commit `f9e085d`.
- I independently transpiled the real, current `format.ts` in a from-scratch copy of `app/` (not the executor's claim) and rendered every one of the 10 `jahr.*` placeholders of the freshly regenerated `texte.json` through the real `formatiere()`: all render as bare four-digit years.
- The new `pipeline/tests/test_formatiere.py` (16 tests, all passing when I ran them myself, including the Node cross-check against the real TypeScript source) makes this a mechanically-guarded invariant going forward, including a mutation test that proves the exact CR-01 pattern is detected.
- The full reproducibility/quality gate — 472 pipeline tests, ruff check/format, `alle.py` regeneration with a clean `git diff` and no untracked files, and the app's type-check/lint/format:check/build — all pass, re-run independently in this verification rather than taken from the orchestrator's or executor's narration.

Eight warning/info-level findings remain open (WR-01..06, IN-01, IN-02; four carried forward from before 04-06, four newly surfaced by the incremental code review of 04-06's own diff). None are critical, none reproduce against the currently-shipped data, and all are explicitly scoped out of this gap-closure round by the user's 2026-10-03 decision. They are reported for visibility but do not block Phase 4's goal achievement.

One non-blocking bookkeeping item: `.planning/REQUIREMENTS.md`'s tracking table still reads "Gaps Found" for all 14 Phase-4 requirement IDs (set after the initial verification, intentionally left untouched through the gap-closure plan). It should be synced to "Complete" now that this re-verification passes.

---

_Verified: 2026-10-04T08:51:42Z_
_Verifier: Claude (gsd-verifier)_
