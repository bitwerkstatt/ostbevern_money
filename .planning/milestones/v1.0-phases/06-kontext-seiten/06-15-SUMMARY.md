---
phase: 06-kontext-seiten
plan: 15
subsystem: ui
tags: [vue, typescript, vitest, grammatik, aria-live, wr-02]

requires:
  - phase: 06-kontext-seiten
    provides: "MassnahmenFilter, ProduktBalkenListe, BindungsgradBalken (Plaene 06-06, 06-10, 06-12)"
provides:
  - "anzahlText() in format.ts (Singular nur fuer genau 1)"
  - "ergebnisText() fuer die aria-live-Ergebniszeile auf /investitionen"
  - "produkteText() und segmentZusammenfassung() fuer Aufklapper und Tooltip des Bindungsgrads"
affects: [06-verification, a11y]

plan_head_before: 8878f321a08314d99cc6781fd257d9afb061c958
plan_head_after: 834e0160ea100b36c77c3c454bbdfb4b112aac9f

actuals:
  tokens: 9000
  tasks: 2
  commits: 4

tech-stack:
  added: []
  patterns:
    - "Zaehltexte entstehen in getesteten lib-Funktionen ueber anzahlText(), nicht als Template-Literal mit festem Plural"

key-files:
  created: []
  modified:
    - app/src/charts/format.ts
    - app/src/charts/__tests__/format.test.ts
    - app/src/lib/investitionen.ts
    - app/src/lib/__tests__/investitionen.test.ts
    - app/src/components/MassnahmenFilter.vue
    - app/src/lib/bindungsgrad.ts
    - app/src/lib/__tests__/bindungsgrad.test.ts
    - app/src/components/ProduktBalkenListe.vue
    - app/src/components/BindungsgradBalken.vue

key-decisions:
  - "UI-SPEC E4/E7 zero-one-many sind durch den grammatikalischen Singular ersetzt (WR-02, Empfehlung aus 06-VERIFICATION.md)"
  - "FormatKuerzel und formatiere() in format.ts bleiben unveraendert, anzahlText ist ein reiner Zusatz ohne Import"

patterns-established:
  - "Quelltext-Test (import.meta.glob ?raw) verbietet feste Plural-Zaehltexte in den drei Komponenten"

requirements-completed: [INV-01, RAT-01]

coverage:
  - id: D1
    description: "Ergebniszeile auf /investitionen liest '1 Maßnahme · zusammen …' bei genau einer Maßnahme und '{n} Maßnahmen' sonst, fuer jede echte pb x art-Kombination"
    requirement: INV-01
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/investitionen.test.ts#ergebnisText (WR-02, INV-01)"
        status: pass
      - kind: unit
        ref: "app/src/charts/__tests__/format.test.ts#anzahlText (WR-02)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Aufklapper-Summary und Tooltip des Bindungsgrads lesen '1 Produkt' fuer ein Produkt und '{n} Produkte' sonst"
    requirement: RAT-01
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/bindungsgrad.test.ts#produkteText und segmentZusammenfassung (WR-02, RAT-01)"
        status: pass
      - kind: unit
        ref: "app/src/lib/__tests__/bindungsgrad.test.ts#Anzahltexte in den Komponenten (WR-02)"
        status: pass
    human_judgment: false
  - id: D3
    description: "FormatKuerzel und formatiere() unveraendert, Pipeline-Vertragstests bleiben gruen"
    verification:
      - kind: unit
        ref: "uv run --directory pipeline pytest tests/test_formatiere.py tests/test_texte.py"
        status: pass
    human_judgment: false

duration: 6min
completed: 2026-10-06
status: complete
---

# Phase 6 Plan 15: Singular fuer Anzahltexte (WR-02) Summary

**Neuer Helfer `anzahlText()` in format.ts plus getestete lib-Funktionen `ergebnisText`, `produkteText` und `segmentZusammenfassung`: die aria-live-Zeile auf /investitionen liest „1 Maßnahme“, Aufklapper und Tooltip des Bindungsgrads lesen „1 Produkt“.**

## Performance

- **Duration:** 6 min
- **Started:** 2026-10-06T08:01:07Z
- **Completed:** 2026-10-06T08:03:52Z (Code), SUMMARY danach
- **Tasks:** 2 (Tracer plus TDD-Task, je RED und GREEN)
- **Files modified:** 9

## Accomplishments

- `anzahlText(anzahl, einzahl, mehrzahl)` direkt nach `zahl()`: Zahl ueber `zahl()`, Singular nur fuer genau 1 ("0 Maßnahmen", "1.000 Maßnahmen").
- `ergebnisText()` speist die aria-live-Zeile von `MassnahmenFilter.vue`; ein Test laeuft ueber jede echte Kombination aus Aufgabenbereich und Art und pinnt fuer Jahrgang 2026 die vier Einzelfaelle (pb=04, pb=15, pb=13 mit grundstuecke, pb=06 mit bau).
- `produkteText()` und `segmentZusammenfassung()` ersetzen den festen Plural in `ProduktBalkenListe.vue` und `BindungsgradBalken.vue`; die komponentenlokale Hilfsfunktion entfaellt.
- Quelltext-Test verbietet in allen drei Komponenten Template-Literale der Form `${…} Maßnahmen|Produkte`.

## Task Commits

1. **Task 1 RED:** `bf159a1` (test) – Stubs, Tests schlagen auf Assertions fehl (12 failed)
2. **Task 1 GREEN:** `4c883f9` (fix) – anzahlText, ergebnisText, MassnahmenFilter umgestellt
3. **Task 2 RED:** `b41f94f` (test) – Stubs, 9 failed
4. **Task 2 GREEN:** `834e016` (fix) – produkteText, segmentZusammenfassung, zwei Komponenten umgestellt

**Plan metadata:** folgt als docs-Commit (SUMMARY).

## Files Created/Modified

- `app/src/charts/format.ts` – `anzahlText()`; FormatKuerzel und formatiere() unveraendert
- `app/src/lib/investitionen.ts` – `ergebnisText()`
- `app/src/lib/bindungsgrad.ts` – `produkteText()`, `segmentZusammenfassung()`
- `app/src/components/MassnahmenFilter.vue`, `ProduktBalkenListe.vue`, `BindungsgradBalken.vue` – nutzen die lib-Funktionen
- `app/src/charts/__tests__/format.test.ts`, `app/src/lib/__tests__/investitionen.test.ts`, `app/src/lib/__tests__/bindungsgrad.test.ts` – neue describe-Bloecke

## Decisions Made

- Dokumentierte Abweichung: Die UI-SPEC-Zeilen E4 und E7 zero-one-many ("{n} Produkte"/"{n} Maßnahmen" ohne Pluralfall) sind durch den grammatikalischen Singular ersetzt (Review WR-02, Empfehlung in 06-VERIFICATION.md; gleiche Regel wie `personenText` auf der Stellenplan-Seite).
- Der Nullfall bleibt wie bisher "0 Maßnahmen · zusammen 0 €"; nur der Singular wurde korrigiert.

## TDD Gate Compliance

Task 1 und Task 2 haben je einen `test(06-15)`-Commit vor dem `fix(06-15)`-Commit (RED: bf159a1, b41f94f; GREEN: 4c883f9, 834e016). Beide RED-Laeufe scheiterten auf den Assertions der Zielverhalten (leerer String von den Stubs bzw. fehlende Quelltext-Muster), nicht an Syntax- oder Ladefehlern. Kein REFACTOR-Commit noetig.

## Deviations from Plan

None - plan executed exactly as written.

Verifikations-Anpassung (keine Code-Abweichung): `npm ci` im Sandbox nicht moeglich (kein Netz, macOS-Binaries in `app/node_modules`). Alle App-Checks liefen in einem Scratch-Copy von `app/` mit Symlink auf die vorhandene Linux-`node_modules` (identische Lockfile). Der Test `test_port_wie_format_ts` wird im Worktree uebersprungen (kein `app/node_modules/typescript`); er wurde deshalb zusaetzlich in einem Scratch-Wurzelverzeichnis (pipeline, daten, app als Symlink auf die Scratch-Kopie) ausgefuehrt: `tests/test_formatiere.py` 23 passed, ohne Skip.

## Issues Encountered

None.

## Verification

- vitest (format, investitionen, bindungsgrad, quelltext): 4 Dateien, 210 Tests passed; gesamte App-Suite 1416 passed.
- `vue-tsc --build`, `eslint .`, `prettier --check src/`, `vite build`: gruen (Build-Hinweis zur Chunkgroesse ist vorbestehend).
- Pipeline: `tests/test_formatiere.py` und `tests/test_texte.py` im Worktree 97 passed, 1 skipped (fehlende node_modules, siehe oben); im Scratch-Wurzelverzeichnis ohne Skip gruen.
- Alle `acceptance_criteria` beider Tasks per grep geprueft: PASS.

## Known Stubs

None. Die temporaeren Stubs der RED-Commits sind in den GREEN-Commits ersetzt.

## Threat Flags

None. Keine neue Angriffsflaeche; T-06-35 (Integritaet des Buergertexts) ist durch die Tests mitigiert, T-06-SC: keine neue Abhaengigkeit.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

WR-02 ist geschlossen. `StellenplanPage.vue` behaelt bewusst sein eigenes `personenText` (Konsolidierung gehoert zur offenen Dopplungs-Findung IN-03).

## Self-Check: PASSED

- Alle 9 Dateien existieren; Commits bf159a1, 4c883f9, b41f94f, 834e016 im Log.

---
*Phase: 06-kontext-seiten*
*Completed: 2026-10-06*
