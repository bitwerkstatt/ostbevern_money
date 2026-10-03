---
phase: 04-manuelle-daten-und-app-daten
verified: 2026-10-03T20:16:46Z
status: gaps_found
score: 9/10 must-haves verified
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
  - "app/.prettierignore"
  - "app/src/charts/format.ts"
  - "app/src/data/daten.ts"
  - "app/src/data/typen.ts"
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
covered_digest: "v2:sha256:2d13e05f8611cec30840b55cd430b7523fbd6dcf589b831755ba1f63ea8796c3"
behavior_unverified: 0
overrides_applied: 0
gaps:
  - truth: "Jede Zahl in den Erklärtexten (daten/manuell/texte/erklaerungen.md, app/src/data/texte.json) wird beim Rendern über formatiere()/FormatKuerzel korrekt angezeigt — keine falsch formatierte Zahl erreicht die Bürgerinnen und Bürger (MANU-08, D-15; Projekt-Kernwert 'Bürgerinformation muss stimmen')"
    status: failed
    reason: "CR-01 (04-REVIEW.md, disposition: open): format.ts::formatiere() dispatcht 'zahl' auf Intl.NumberFormat('de-DE',{maximumFractionDigits:0}), was Tausendertrennung erzwingt. Alle zehn Vorkommen von {{jahr.haushaltsjahr|zahl}} in erklaerungen.md (und damit in app/src/data/texte.json) rendern das Haushaltsjahr als '2.026' statt '2026', sobald eine künftige Phase formatiere() in die Vue-Templates verdrahtet. FORMATKUERZEL (texte.py) kennt kein ungruppiertes Jahres-Kürzel, sodass der Textautor 'zahl' missbrauchen musste. Reproduziert: `node -e \"console.log(new Intl.NumberFormat('de-DE',{maximumFractionDigits:0}).format(2026))\"` -> '2.026'. Der Fehler ist deterministisch und betrifft alle zehn Texte (schluesselzuweisung, gewerbesteuer, kreisumlage, grundsteuer_hebesaetze, sonderposten, globaler_minderaufwand, defizit_ruecklagen, schulden, verpflichtungsermaechtigungen, nicht_im_haushalt); er wurde vom Abnahme-Checkpoint (D-17, Task 2 von 04-05) nicht erkannt, weil `vorschau()` nur Rohwerte, nicht den über formatiere() gerenderten String zeigt."
    artifacts:
      - path: "app/src/charts/format.ts"
        issue: "FormatKuerzel-Union hat kein ungruppiertes Jahres-Kürzel; formatiere('zahl') gruppiert immer"
      - path: "pipeline/ostbevern/texte.py"
        issue: "FORMATKUERZEL = (euro, mio, zahl, prozent, promille, vzae) — kein 'jahr'-Kürzel"
      - path: "daten/manuell/texte/erklaerungen.md"
        issue: "10 Vorkommen von {{jahr.haushaltsjahr|zahl}} statt eines ungruppierten Formats"
    missing:
      - "Ein ungruppiertes Formatkürzel (z. B. 'jahr') in FormatKuerzel/formatiere() (format.ts) UND FORMATKUERZEL (texte.py), synchron gehalten durch test_formatkuerzel_wie_format_ts"
      - "Ersetzen aller zehn {{jahr.haushaltsjahr|zahl}}-Platzhalter in erklaerungen.md durch das neue Kürzel"
      - "Ein Test, der jedes aufgelöste (wert, format)-Paar aus loese_auf() tatsächlich durch eine Portierung/Nachbildung von formatiere() rendert, damit ein Regressionsfehler mechanisch statt durch PDF-Vergleich erkannt wird"
---

# Phase 4: Manuelle Daten und App-Daten Verification Report

**Phase Goal:** Die Pipeline ist geschlossen. Die Vorberichtswerte sind manuell gepflegt und gegen den Plan geprüft, der Stellenplan ist extrahiert, und die App-JSON-Dateien entstehen reproduzierbar ohne Personennamen.
**Verified:** 2026-10-03T20:16:46Z
**Status:** gaps_found
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | SC1: Alle Tabellen in `daten/manuell/` haben eine `quelle`-Spalte und ein README begründet die Werte; Regel 5 ist grün inkl. dokumentierter Befunde (Zuwendungen, Kreisumlage-Fußnote) | ✓ VERIFIED | Every manual CSV header ends in `...,quelle`; README.md has a `###` section per file; `konsistenz.md`: `Regel 5 – Manuelle Tabellen → Planzeilen \| grün \| 133 \| 0 \| 0 \| 25`; befunde.md documents the Zuwendungen 2026 Δ −4.200 € and the 1 T€ rounding rows |
| 2 | SC2: `meta.json` enthält Einwohner 11.741 (Stichtag, Quelle), Hebesätze 242/554/418 %, Fläche, Satzungsdatum, Kreisumlage brutto/netto, Umlage-Hebesätze 36,3 %/21 %; `texte/erklaerungen.md` enthält geprüfte Erklärtexte mit Seitenverweis | ✓ VERIFIED | `python3 -c "json.load(open('daten/manuell/meta.json'))"` confirms einwohner.wert=11741 (quelle 25), hebesaetze.{grundsteuer_a,grundsteuer_b,gewerbesteuer}={242,554,418}, kreisumlage.netto=10147000, kreisumlage.brutto=11472478 (berechnet); `erklaerungen.md` has 10 `## <schluessel>` sections each with a `Quelle: S. n` line |
| 3 | SC2b: Daten für Schuldenstand, Rücklagen und VE-Übersicht (S. 24/25, 309–311) liegen mit Quelle vor | ✓ VERIFIED | `verbindlichkeiten.csv`, `eigenkapital.csv`, `ve_uebersicht.csv` exist, each row carries `quelle`; `investitionen.json` key `schuldenstand` present with `berechnet`/`formel` fields |
| 4 | SC3: `stellenplan.csv` enthält Teil A (Beamte), Teil B (Tarif) und die Stellenübersicht nach PB mit Stellen 2026/2025, besetzt 30.06.2025 und Vermerken; Beamtenstellen 2026 = 8 | ✓ VERIFIED | `daten/aufbereitet/stellenplan.csv` header matches spec; Python query over the CSV: Σ beamte stellen 2026 (produktbereich null) = 8.0; `konsistenz.md`: `Regel 10 – Stellenplan: Stellenübersicht → Teil A/B \| grün \| 19 \| 0 \| 0 \| 0`, `Regel 9 – Eckwerte (Anhang B.6) \| grün` |
| 5 | SC4: `app/src/data/` enthält `haushalt.json`, `produkte.json`, `investitionen.json`, `stellenplan.json`; kein Personenname; "Weitergabe an Kreis und Land" eigene Kategorie, Rest von PB 16 "Allgemeine Finanzwirtschaft"; Zuschussbedarf je Knoten/Jahr als berechnet gekennzeichnet | ✓ VERIFIED | All four files present; `test_keine_personennamen_in_app_daten` passes (1 passed); `haushalt.json` knoten: `KL` eltern=GESAMT, synthetisch=True, `KL.kreisumlage` gerundet=True, node `16` name="Allgemeine Finanzwirtschaft"; `ergebnisplan.GESAMT.berechnet` present per node/year |
| 6 | SC5: `uv run pipeline/alle.py` führt alle Schritte in Reihenfolge aus; CI schlägt bei Diff fehl | ✓ VERIFIED | `alle.py --jahr 2026` ran Schritte 01→02→03→04→Querschnitte→05→06→07 to exit 0; `git diff --stat --exit-code -- daten app/src/data` exits 0, no untracked files; `.github/workflows/ci.yml:43` runs the identical `git diff --stat --exit-code -- daten app/src/data` |
| 7 | Requirement coverage: all 14 declared IDs (MANU-01..08, PRUEF-05, EXTR-10, DATA-01..03, PRUEF-10) are claimed by a plan and have supporting evidence | ✓ VERIFIED | Cross-referenced against REQUIREMENTS.md; all 14 marked `[x]`/`Complete`; no orphaned IDs found for Phase 4 |
| 8 | Full pipeline test suite green, lint/format clean, app checks green, pipeline reproducible | ✓ VERIFIED | `uv run --directory pipeline pytest -q`: 456 passed; `ruff check . && ruff format --check .`: clean; scratch-copy `npm ci`, `type-check`, `lint`, `format:check`, `build`: all exit 0 |
| 9 | MANU-08/D-15: Jede Zahl in den Erklärtexten ist ein Platzhalter `{{schluessel|format}}`; kein nackter Ziffernlauf außer Jahren/§/S. | ✓ VERIFIED | `grep -c '^## '` ≥ 10; `test_erklaerungen_keine_nackten_ziffern` and related texte-tests pass as part of the 456; this truth checks the *syntactic* contract only |
| 10 | MANU-08/D-15: Jede Zahl in den Erklärtexten wird beim Rendern über `formatiere()` **korrekt** angezeigt (kein falsches Format erreicht die Bürgerinnen) | ✗ FAILED | **CR-01** (04-REVIEW.md, disposition: open, still unresolved): `formatiere(2026, 'zahl')` groups thousands → renders "2.026" instead of "2026". Reproduced directly: `node -e "console.log(new Intl.NumberFormat('de-DE',{maximumFractionDigits:0}).format(2026))"` → `2.026`. All 10 occurrences of `{{jahr.haushaltsjahr\|zahl}}` in `erklaerungen.md` are affected |

**Score:** 9/10 truths verified (0 present, behavior-unverified)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `daten/manuell/{steuerarten,zuwendungen,transferaufwendungen,kita_zuschuesse,weitere_vorberichtstabellen,verbindlichkeiten,eigenkapital,ve_uebersicht}.csv` | Vorbericht tables, T€/Euro as printed, `quelle` column | ✓ VERIFIED | All 8 exist, correct headers, non-empty, byte-identical round-trip tests pass |
| `daten/manuell/meta.json` | Meta values with strict allowlist, `quelle` per value | ✓ VERIFIED | Present, validated structure, matches §6/§9/S.24-28/46-47 values |
| `daten/manuell/texte/erklaerungen.md` | 10 reviewed Erklärtexte with `Quelle:` lines, placeholders only | ✓ VERIFIED (syntax) / ✗ one rendering defect (see Truth 10) | File committed, 10 sections, D-17 checkpoint evidence in 04-05-SUMMARY.md |
| `daten/manuell/README.md` | Justification per manual file | ✓ VERIFIED | 9 `###` sections, one per file, plus Regel-9 paragraph |
| `pipeline/ostbevern/app_daten.py` | Schritt 07 writer, KL split, Zuschussbedarf | ✓ VERIFIED | `baue_knoten`, `baue_ergebnisplan`, `KL_CODE`, etc. present and exercised by tests |
| `pipeline/ostbevern/texte.py` | Placeholder parser/contract | ✓ VERIFIED | `FORMATKUERZEL`, `lies_erklaerungen`, `pruefe_text`, `textwerte`, `loese_auf` present |
| `app/src/data/{haushalt,produkte,investitionen,stellenplan,texte}.json` | Generated App-JSON | ✓ VERIFIED | All exist, structurally correct, person-name-free, reproducible |
| `app/src/data/typen.ts`, `daten.ts` | Typed contract for generated JSON | ✓ VERIFIED | `vue-tsc --build` passes against all five JSON files, no casts |
| `app/src/charts/format.ts` | `formatiere()`/`FormatKuerzel` dispatcher | ⚠️ ORPHANED-BY-DEFECT | Exists, exported, type-checks — but one of its 6 branches (`zahl`) produces an incorrect result for the one value class (bare years) it is used for in this phase's own data (see Truth 10 / CR-01) |
| `.github/workflows/ci.yml` | Reproducibility gate (D-24) | ✓ VERIFIED | `git diff --stat --exit-code -- daten app/src/data` step present in job `pipeline` |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `pipeline/alle.py` | `pipeline/ostbevern/app_daten.py` | `app_daten.erzeuge_app_daten(jahr)` after grün Prüfbericht | ✓ WIRED | `grep -q 'app_daten.erzeuge_app_daten(' pipeline/alle.py` exits 0; alle.py run confirms "Schritt 07: geschrieben: ..." x5 |
| `pipeline/alle.py` | `pipeline/ostbevern/stellenplan.py` | `stellenplan.extrahiere_stellenplan(jahrgang)` between Querschnitte and Schritt 06 | ✓ WIRED | `grep -q 'stellenplan.extrahiere_stellenplan(' pipeline/alle.py` exits 0; alle.py output shows "Schritt 05: 162 Zeilen geschrieben" before Schritt 06 |
| `pipeline/ostbevern/app_daten.py` | `pipeline/ostbevern/texte.py` | `texte.lies_erklaerungen`/`loese_auf` inside `erzeuge_app_daten` | ✓ WIRED | alle.py output includes "Schritt 07: geschrieben: app/src/data/texte.json" |
| `app/src/data/daten.ts` | `app/src/data/{haushalt,produkte,investitionen,stellenplan,texte}.json` | typed imports without cast | ✓ WIRED | `grep -q 'haushalt: Haushalt'` / `investitionen: Investitionen'` / `produkte: Produkt\[\]'` all present; `vue-tsc --build` green |
| `.github/workflows/ci.yml` | `pipeline/alle.py` | CI step runs alle.py then `git diff --stat --exit-code` | ✓ WIRED | Step present at ci.yml:43; reproduced locally with identical result |
| `pipeline/ostbevern/pruefung.py` (Regel 5 `_pruefe_regel5_ve_uebersicht`) | `daten/manuell/ve_uebersicht.csv` | per-(produkt, jahr) cross-check | ⚠️ PARTIAL | Wired for the VE-Gesamtbetrag and per-(produkt,jahr) rows, but the two per-year `ist_gesamt` summary rows (faellig 2027/2028) are read and never compared against anything (WR-01, open) |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|----------|---------|--------|--------|
| Full pipeline test suite | `uv run --directory pipeline pytest -q` | `456 passed in 337.35s` | ✓ PASS |
| Person-name scan (named test) | `pytest tests/test_app_daten.py -q -k personennamen` | `1 passed` | ✓ PASS |
| Reproducibility | `alle.py --jahr 2026 && git diff --stat --exit-code -- daten app/src/data` | exit 0, no diff, no untracked files | ✓ PASS |
| Ruff lint/format | `ruff check . && ruff format --check .` | "All checks passed!", "45 files already formatted" | ✓ PASS |
| App type-check | `npm run type-check` (scratch copy) | exit 0 | ✓ PASS |
| App lint | `npm run lint` (scratch copy) | exit 0 | ✓ PASS |
| App format:check | `npm run format:check` (scratch copy) | exit 0 | ✓ PASS |
| App build | `npm run build` (scratch copy) | exit 0, `dist/` produced | ✓ PASS |
| **CR-01 reproduction** | `node -e "console.log(new Intl.NumberFormat('de-DE',{maximumFractionDigits:0}).format(2026))"` | `2.026` | ✗ FAIL (confirms defect) |

### Requirements Coverage

| Requirement | Source Plan | Description | Status | Evidence |
|---|---|---|---|---|
| MANU-01 | 04-01 | steuerarten.csv (8 Steuerarten, T€, S.27) | ✓ SATISFIED | File present, 54 rows, Regel 5 grün |
| MANU-02 | 04-01 | zuwendungen.csv (S.28) | ✓ SATISFIED | File present, 24 rows, Regel 5 grün with befunde |
| MANU-03 | 04-01 | transferaufwendungen.csv incl. Kreisumlage-Fußnote | ✓ SATISFIED | 10147 with "10.1473" anmerkung present |
| MANU-04 | 04-01 | kita_zuschuesse.csv (Σ 559 T€) | ✓ SATISFIED | 8 rows, gesamt row = 559 |
| MANU-05 | 04-02 | weitere_vorberichtstabellen.csv (5 tables) | ✓ SATISFIED | All 5 tabellen present |
| MANU-06 | 04-02 | meta.json | ✓ SATISFIED | See Truth 2 |
| MANU-07 | 04-01/02/03 | `quelle` column + README | ✓ SATISFIED | See Truths 1/3 |
| MANU-08 | 04-05 | Geprüfte Erklärtexte mit Seitenverweis | ⚠️ PARTIALLY SATISFIED | Content/syntax satisfied; **rendering correctness defect open (CR-01)** |
| PRUEF-05 | 04-01/02 | Regel 5 grün, Toleranz ±1 T€, Befunde dokumentiert | ✓ SATISFIED | konsistenz.md Regel 5 grün |
| EXTR-10 | 04-03 | Stellenplan extrahiert | ✓ SATISFIED | See Truth 4 |
| DATA-01 | 04-01/03/04/05 | App-JSON-Dateien erzeugt | ✓ SATISFIED | See Truth 5 |
| DATA-02 | 04-04 | "Weitergabe an Kreis und Land" separiert | ✓ SATISFIED | See Truth 5 |
| DATA-03 | 04-04 | Zuschussbedarf berechnet gekennzeichnet | ✓ SATISFIED | `berechnet` dict present per node |
| PRUEF-10 | 04-01/03/05 | alle.py + CI-Diff-Prüfung | ✓ SATISFIED | See Truth 6 |

No orphaned Phase-4 requirements found in REQUIREMENTS.md beyond the 14 declared.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---|---|---|---|
| `app/src/charts/format.ts` / `pipeline/ostbevern/texte.py` / `daten/manuell/texte/erklaerungen.md` | format.ts:39-83, texte.py:28-30, 10 occurrences in erklaerungen.md | CR-01: `zahl` kuerzel groups thousands, mis-renders bare years | 🛑 Blocker | Confirmed reproducible; see Truth 10 |
| `pipeline/ostbevern/pruefung.py` | ~1555-1656 (`_pruefe_regel5_ve_uebersicht`) | WR-01: per-year VE summary rows never cross-checked | ⚠️ Warning | Latent verification gap; current data happens to be arithmetically correct, but a future typo in either summary cell would pass undetected |
| `pipeline/ostbevern/app_daten.py` | ~570-586 (`baue_investitionen_json`) | WR-02: negative-index fallback (`investitionskredite[index - 1]`) with no `AppDatenFehler` guard | ⚠️ Warning | Holds only by coincidence of the 2026 configuration; would raise raw `IndexError` for a different jahrgang shape |
| `pipeline/ostbevern/texte.py` | ~204-227 (`ABGELEITET` formulas) | WR-03: neighbour-year lookups (`hh+1`/`hh-1`) assume presence, no `TexteFehler` wrapping | ⚠️ Warning | Would raise raw `KeyError` for a jahrgang where haushaltsjahr is the first/last configured year |
| `app/src/charts/format.ts` | 68-83 (`formatiere` switch) | IN-01: no runtime fallback/exhaustive-check for an unknown kuerzel | ℹ️ Info | Silent `undefined` render instead of a loud failure |

All five findings were already identified by the Phase-4 code review (`04-REVIEW.md`) and remain **disposition: open** per `04-REVIEW-DISPOSITION.md` — none have been fixed, waived, or deferred since that review. This verifier independently reproduced CR-01, WR-01, WR-02 and WR-03 directly against the current code (not merely trusting the review document).

### Human Verification Required

None. CR-01 is a deterministically reproducible defect (confirmed above), not an uncertain or UI/real-time judgment call — it is recorded as a gap, not a human-verification item.

### Gaps Summary

Phase 4's data-generation goal is substantively achieved: all five ROADMAP success criteria
hold against the actual codebase (manual tables with sourced values and a green Regel 5,
`meta.json` with the correct figures, a correctly extracted Stellenplan with Beamte=8, four
name-free `app/src/data/*.json` files with the KL split and flagged Zuschussbedarf, and a
fully reproducible `alle.py` enforced by a CI diff gate). The full pipeline test suite (456
tests), ruff, and the app's type-check/lint/format/build all pass independently of the
SUMMARY.md claims — this verifier re-ran every one of them rather than trusting the executor's
narration.

One gap blocks a clean pass: **CR-01**, an open critical finding from the phase's own code
review, is a confirmed, deterministic defect in the number-formatting contract (D-15) that
this phase itself established and marked "reversibility: costly" (because Phase 5/6 will
consume it as-is). All ten Erklärtexte use `{{jahr.haushaltsjahr|zahl}}` to state the current
Haushaltsjahr, and the `zahl` format kuerzel groups thousands by design — so every one of the
ten citizen-facing explanatory texts will display "2.026" instead of "2026" once a later
phase wires `formatiere()` into the Vue templates. This directly contradicts the project's
explicit core value ("Jede Zahl in der App ist korrekt... Bürgerinformation muss stimmen")
and was not caught by the D-17 human checkpoint, because the checkpoint's preview showed raw
values, not values rendered through `formatiere()`. The fix is small and scoped (add an
ungrouped `jahr` format kuerzel to both `format.ts` and `texte.py`, repoint the ten
placeholders, and add a test that renders resolved values) but it was not applied before this
phase's commits were finalized, and the review disposition for CR-01 is still "open" — not
fixed, not waived, not deferred to a later phase's documented success criteria.

Three further open warnings (WR-01: unchecked VE-Übersicht summary rows; WR-02: an unguarded
negative-index fallback in the Schuldenstand-Fortschreibung; WR-03: unguarded neighbour-year
lookups in the `ABGELEITET` text formulas) do not currently produce incorrect output on the
committed 2026 data, but they are latent robustness/verification-coverage gaps consistent
with, yet slightly undercutting, the project's "jede Zahl ... ist durch automatische
Prüfungen ... belegt" guarantee. They are reported as warnings, not blockers, since no
demonstrated defect exists in the current data — but they should be dispositioned (fixed or
explicitly accepted) before later phases build further on these codepaths.

---

_Verified: 2026-10-03T20:16:46Z_
_Verifier: Claude (gsd-verifier)_
