---
phase: 04-manuelle-daten-und-app-daten
reviewed: 2026-10-04T08:39:37Z
depth: standard
files_reviewed: 6
files_reviewed_list:
  - app/src/charts/format.ts
  - app/src/data/texte.json
  - daten/manuell/README.md
  - daten/manuell/texte/erklaerungen.md
  - pipeline/ostbevern/texte.py
  - pipeline/tests/test_formatiere.py
findings:
  critical: 0
  warning: 3
  info: 1
  total: 4
status: issues_found
---

# Phase 04: Code Review Report

**Reviewed:** 2026-10-04T08:39:37Z
**Depth:** standard
**Files Reviewed:** 6
**Status:** issues_found


> **ID-Hinweis (Orchestrator):** Inkrementeller Review nach Plan 04-06 (Diff-Basis 1485175). Die Befund-IDs wurden mechanisch auf WR-04…WR-06 und IN-02 umnummeriert, damit sie nicht mit CR-01, WR-01…WR-03 und IN-01 des vorherigen Reviews (Commit 1485175, Stand in 04-REVIEW-DISPOSITION.md) kollidieren. WR-06 überschneidet sich inhaltlich mit dem früheren IN-01 (kein Fallback in `formatiere()`), das per Nutzerentscheidung vom 2026-10-03 offen bleibt.

## Summary

Reviewed the format/text-placeholder subsystem (`format.ts`, `texte.py`, `test_formatiere.py`) plus the shipped text content (`texte.json`, `erklaerungen.md`, `README.md`). I independently re-derived every placeholder resolution in `erklaerungen.md` against `texte.json["werte"]` (no missing keys, no unknown format kürzel, no CR-01-style jahr-namespace violations), ran `pruefe_text` from the real pipeline module against every paragraph (no violations), and ran `pipeline/tests/test_formatiere.py` (16/16 pass). The currently-shipped data is internally consistent and correctly formatted — I did not find a currently-manifesting data-correctness bug.

What I did find are three design/robustness gaps that are "latent" in the sense that they don't trip on today's data but will silently produce wrong output or masked failures the next time someone edits `erklaerungen.md` or extends `format.ts`'s call sites — exactly the kind of regression this phase's own CR-01 fix was trying to prevent. I also flagged one data-duplication risk. No critical/blocking issues found.

## Warnings

### WR-04: `_SEITENZAHL_MUSTER` silently drops page numbers from range-style `Quelle:` lines

**File:** `pipeline/ostbevern/texte.py:54, 122`
**Issue:** `_SEITENZAHL_MUSTER = re.compile(r"S\.\s*(\d+)")` is used in `lies_erklaerungen` to extract `quelle_seiten` from a section's `Quelle:` line (line 122: `_SEITENZAHL_MUSTER.findall(quelle_treffer.group(1))`). This regex only captures the digits immediately following a single `S.` marker. The project's own documented convention for page references — used by the sibling `_SEITE_MUSTER` regex inside `pruefe_text` (line 46: `r"S\.\s*\d+(?:[-/]\d+)*"`) and explicitly called out in `daten/manuell/README.md:289` ("ein Seitenverweis (`S. n`, auch als Spanne wie `S. 24/25`)") — allows a compact range form like `S. 24/25` or `S. 309-311`. If an author ever writes a `Quelle:` line using that compact range form (instead of repeating `S.` per page, as all ten current sections do), `_SEITENZAHL_MUSTER.findall` only returns the first page and silently drops the rest — no error, no warning, just an incomplete `quelle_seiten` tuple. I confirmed this directly:
```
>>> _SEITENZAHL_MUSTER.findall("S. 24/25")
['24']
>>> _SEITENZAHL_MUSTER.findall("S. 309-311")
['309']
```
This violates the module's own stated fail-fast philosophy ("Pipeline formatiert nie... bricht Schritt 07 ab" / D-08) and the project's core value that every number is traceably sourced to a PDF page — a missing citation page would ship silently. It does not currently trigger because every existing `Quelle:` line in `erklaerungen.md` repeats `S.` per page (e.g. `S. 46, S. 47`), but nothing prevents the next editor from using the shorter, equally-valid-looking range form documented elsewhere in the same project.
**Fix:** Reuse the range-aware pattern for the `Quelle:` line too, e.g.:
```python
_SEITENZAHL_MUSTER = re.compile(r"S\.\s*(\d+(?:[-/]\d+)*)")
...
seiten = tuple(
    int(n)
    for gruppe in _SEITENZAHL_MUSTER.findall(quelle_treffer.group(1))
    for n in re.split(r"[-/]", gruppe)
)
```
or simply document/enforce (with a `TexteFehler`) that `Quelle:` lines must repeat `S.` per page and reject `/`/`-` ranges there.

### WR-05: CR-01 regression guard (jahr-namespace vs. `jahr` kürzel) exists only in the test suite, not in the pipeline's own validation

**File:** `pipeline/ostbevern/texte.py:138-176` (`pruefe_text`); guard logic actually lives in `pipeline/tests/test_formatiere.py:201-211` (`_verstoesse`)
**Issue:** The whole point of CR-01 (per the comments threaded through `format.ts`, `texte.py`, and `erklaerungen.md`) is that a value under the `jahr.*` namespace (e.g. `jahr.haushaltsjahr`) must always be rendered with the `jahr` format kürzel, never `zahl`, because `zahl` would wrongly group it as `"2.026"`. The only place that actually checks this invariant is `_verstoesse` in the test file (`ist_jahresnamensraum` check at line 201-211), which is test-only code. The production validation function `pruefe_text` in `texte.py` — the one that actually runs during the real pipeline step and is documented as failing fast on unknown kürzel/schema issues — has no equivalent check. It verifies the kürzel is a member of `FORMATKUERZEL` and that digits are only inside valid placeholders, but never checks the kürzel is semantically correct for the given schlüssel's namespace. If a future edit to `erklaerungen.md` introduces `{{jahr.irgendwas|zahl}}`, the pipeline will happily resolve and ship it (since `loese_auf` only checks the key exists in `werte`, not that the kürzel matches); the regression would only be caught if someone remembers to run `pytest`, not by the pipeline's own `TexteFehler` fail-fast gate that the rest of this module relies on for every other invariant.
**Fix:** Move the jahr-namespace-vs-kürzel check into `pruefe_text` (or a new `pruefe_platzhalter_kuerzel` called from `lies_erklaerungen`/the step-07 entry point), e.g.:
```python
if (schluessel == "jahr" or schluessel.startswith("jahr.")) and format_kuerzel != "jahr":
    raise TexteFehler(f"Jahresschlüssel {schluessel!r} muss Kürzel 'jahr' verwenden, nicht {format_kuerzel!r}")
if format_kuerzel == "jahr" and not (schluessel == "jahr" or schluessel.startswith("jahr.")):
    raise TexteFehler(f"Kürzel 'jahr' nur für 'jahr.*'-Schlüssel erlaubt, nicht {schluessel!r}")
```
so the invariant is enforced by the same fail-fast mechanism as every other rule in this file, not only by a test someone has to remember to run.

### WR-06: `formatiere()` has no default/exhaustiveness guard — an unexpected kürzel value silently returns `undefined` instead of failing loudly

**File:** `app/src/charts/format.ts:80-97`
**Issue:** `formatiere(wert, kuerzel)` switches over all seven `FormatKuerzel` members with no `default` branch. This type-checks today because TypeScript can prove exhaustiveness over the literal union when every member has a `case`. But the actual `kuerzel` value reaching this function at runtime does not originate as a `FormatKuerzel` — it is parsed out of a markdown-style placeholder string (`{{schluessel|kuerzel}}`) by a renderer that isn't in this review's scope, almost certainly via a regex match whose captured group is typed `string` and then narrowed/cast to `FormatKuerzel` (possibly with `as FormatKuerzel`, or no cast check at all). The pipeline side (`pruefe_text` in `texte.py`) explicitly fails fast (`TexteFehler`) on an unknown format kürzel before anything is written to `texte.json` — but there is no equivalent defensive fallback on the app side. If `texte.json` is ever hand-edited, generated by a future pipeline version with a kürzel typo, or if the renderer's cast is wrong, `formatiere()` silently falls through all cases and returns `undefined` (not a thrown error, not an empty string) — which would then typically get rendered into the DOM as the literal text `"undefined"` next to a budget figure, directly visible to end users of a municipal-finance transparency site. This is exactly the failure mode `test_formatiere.py`'s `_verstoesse` function treats as a hard violation (`"undefined" in gerendert`) — but only in the Python test, not as a runtime guard in the shipped TS code.
**Fix:** Add an exhaustiveness-enforcing default that throws, so a future change that adds a kürzel without updating the switch (or a corrupted runtime value) fails loudly instead of rendering `"undefined"`:
```typescript
export function formatiere(wert: number, kuerzel: FormatKuerzel): string {
  switch (kuerzel) {
    case 'euro': return euro(wert)
    case 'mio': return euroKurz(wert)
    case 'zahl': return zahl(wert)
    case 'jahr': return jahr(wert)
    case 'prozent': return prozent(wert / 100)
    case 'promille': return prozent(wert / 1000)
    case 'vzae': return vzae(wert)
    default: {
      const _exhaustive: never = kuerzel
      throw new Error(`Unbekanntes Formatkürzel: ${_exhaustive}`)
    }
  }
}
```

## Info

### IN-02: Haushaltsjahr is duplicated across two independent locations in `texte.json`

**File:** `app/src/data/texte.json:2, 118`
**Issue:** The budget year is stored both as the top-level `"haushaltsjahr": 2026` (line 2) and as `"werte"."jahr.haushaltsjahr": 2026` (line 118). Both are presumably derived from the same pipeline source today (values match), but having the same fact encoded twice in the same generated artifact is a drift risk: a future pipeline change that updates one derivation path but not the other (e.g. a refactor that changes how the top-level field is populated) would silently desynchronize the two without any structural signal that something is wrong, since nothing in this file cross-checks them.
**Fix:** Either derive the top-level `haushaltsjahr` field from `werte["jahr.haushaltsjahr"]` at write time (single source of truth), or add a pipeline-side assertion (in the step that writes `texte.json`) that the two values are equal before writing.

---

_Reviewed: 2026-10-04T08:39:37Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
