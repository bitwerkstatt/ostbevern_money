---
phase: 05-leitfragen-seiten
plan: 06
subsystem: ui
tags: [vue, typescript, vitest, texte, kreisumlage, ertragsarten, web-awesome]
status: complete

requires:
  - phase: 05-leitfragen-seiten
    provides: "05-01 formatiere()/KEIN_WERT and vitest runner; 05-02 haushalt.zeilen_namen"
provides:
  - "lib/texte.ts: rendereAbsatz, findeText, istJahrneutral, textFuerJahr, istFormatKuerzel (mirrors texte.py PLATZHALTER_MUSTER)"
  - "ErklaerText.vue: Erklaertext with 'Quelle: PDF-Seite n', year-bound, text interpolation only"
  - "lib/berechnung.ts: proKopf (Math.round), anteil, summe"
  - "lib/zeilen.ts: zeilenName, zeilenNummer from haushalt.zeilen_namen"
  - "lib/ertragsarten.ts: baueErtragsarten (Ebene 1, shared by Start and Einnahmen)"
  - "lib/kreisumlage.ts: findeKlKnoten, baueKreisumlage"
  - "KreisumlageCallout.vue (full and short form), BerechnetEtikett.vue"
affects: [05-07, 05-08, 05-09, 05-10]

actuals:
  tokens: 8500
  tasks: 3
  commits: 4
plan_head_before: 8403a43b4a14a6ce43ab467307a65386035a8b01
plan_head_after: 984a943c5d58b75f0dd199450cf177cebe1271a4

tech-stack:
  added: []
  patterns:
    - "Placeholder lookups via Object.hasOwn and Map, never plain object access (prototype keys)"
    - "KL node found structurally (only synthetic child of GESAMT), no Jahrgang code in components"
    - "Phase-5 success values (2026) in describe.runIf(haushalt.haushaltsjahr === 2026); everything else derived from data"

key-files:
  created:
    - app/src/lib/texte.ts
    - app/src/lib/__tests__/texte.test.ts
    - app/src/components/ErklaerText.vue
    - app/src/lib/berechnung.ts
    - app/src/lib/__tests__/berechnung.test.ts
    - app/src/lib/zeilen.ts
    - app/src/lib/__tests__/zeilen.test.ts
    - app/src/lib/ertragsarten.ts
    - app/src/lib/__tests__/ertragsarten.test.ts
    - app/src/lib/kreisumlage.ts
    - app/src/lib/__tests__/kreisumlage.test.ts
    - app/src/components/KreisumlageCallout.vue
    - app/src/components/BerechnetEtikett.vue
  modified: []

key-decisions:
  - "Texts containing placeholders are shown only for texte.haushaltsjahr; all ten current texts contain placeholders, so every one disappears for other years (Pitfall 6)"
  - "KreisumlageCallout cites two pages: the node's PDF page for the exact total and the Unterposten page (Vorbericht, rounded T-EUR values) for the split"
  - "Ertragsarten selected by printed row number 01-09 (not ist_summe) plus 19, Anteil base is berechnet.ertraege"

requirements-completed: [UI-05, START-02, EINN-01, AUSG-02]

coverage:
  - id: D1
    description: "rendereAbsatz/textFuerJahr/ErklaerText: placeholders formatted via formatiere(), every real paragraph renders clean, year binding enforced"
    requirement: UI-05
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/texte.test.ts (16 tests)"
        status: pass
    human_judgment: false
  - id: D2
    description: "proKopf/anteil/summe and zeilenName/zeilenNummer helpers"
    requirement: UI-05
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/berechnung.test.ts, zeilen.test.ts"
        status: pass
    human_judgment: false
  - id: D3
    description: "baueErtragsarten: sums equal berechnet.ertraege in every year, 8 rows 2024 / 7 rows 2026, shares sum to 100 %"
    requirement: EINN-01
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/ertragsarten.test.ts"
        status: pass
    human_judgment: false
  - id: D4
    description: "baueKreisumlage: total, rounded Unterposten within 3.000 EUR, KL largest top-level node in 2026"
    requirement: AUSG-02
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/kreisumlage.test.ts"
        status: pass
    human_judgment: false
  - id: D5
    description: "KreisumlageCallout (full/short) and BerechnetEtikett: markup, rd. amounts, tooltip reachable by keyboard focus, details open with Enter"
    requirement: START-02
    verification:
      - kind: other
        ref: "SSR render of all variants in the scratch copy shows expected markup; interactive keyboard behaviour not exercised"
        status: pass
    human_judgment: true
    rationale: "Keyboard/tooltip/details behaviour of Web Awesome elements needs a browser; check after plan 05-08 or in npm run dev"
---

# Phase 5 Plan 6: Gemeinsame Inhaltsbausteine Summary

**Placeholder renderer with year binding plus ErklaerText, per-capita/row-label helpers, the shared Ertragsarten builder, the Kreisumlage callout (full and short) and the "berechnet" tag, all fed only from the data files and `format.ts`.**

## Performance

- **Tasks:** 3 (1 tracer, 2 TDD)
- **Files:** 13 created, 0 modified
- **Commits:** 4 (tracer, RED, GREEN for Task 2, Task 3)

## Accomplishments

- `rendereAbsatz` mirrors `texte.py` `PLATZHALTER_MUSTER`, formats every value through `formatiere()`, renders a missing key as "–" and throws on an unknown Kuerzel; a test renders every paragraph of the real `texte.json` and rejects `{{`, `NaN`, `undefined`, `Infinity`.
- `textFuerJahr` returns placeholder texts only for `texte.haushaltsjahr` (RESEARCH Pitfall 6); `ErklaerText` renders title, paragraphs and "Quelle: PDF-Seite n" by interpolation only (no `v-html`).
- `proKopf(30.455.569, 11.741) = 2.594` and `proKopf(18.443.000, 11.741) = 1.571` (rounding, not flooring).
- `baueErtragsarten`: 8 rows for 2024, 7 for 2026, Σ = `berechnet.ertraege` in every year, first 2026 row "steuern" 18.443.000.
- `baueKreisumlage`: KL 11.001.181 in 2026, three Unterposten (all `gerundet`, page 46, shown as "rd."), Σ within 3.000 EUR in every year.

## Verification

Scratch copy (`npm ci` from the committed lockfile): `npm run test` 6 files / 60 tests passed, `type-check`, `lint`, `format:check`, `build` all green. No skipped tests (the 2026 `runIf` blocks run). A throw-away SSR render of both callout forms, `BerechnetEtikett` and `ErklaerText` produced the expected markup (not committed).

## Deviations from Plan

None - plan executed exactly as written.

Notes: Task 3 was committed as one `feat` commit (lib, test, components) instead of a separate RED commit; Task 2 has the separate RED commit. Task 1 is a tracer, committed once.

## Integration notes for other plans

- `KreisumlageCallout` links via `RouterLink :to="{ name: 'ausgaben' }"`; the route comes from plan 05-04. Until it is merged, the short form throws at render time (not at build time).
- `app/src/main.ts` was NOT edited. The components use `wa-tag`, `wa-tooltip`, `wa-details` (plus already imported `wa-callout`, `wa-icon`); whoever owns `main.ts` (05-04) must import `tag/tag.js`, `tooltip/tooltip.js` and `details/details.js`, otherwise these render as unknown elements.
- `wertart` for `KreisumlageCallout` is passed in by the page (from `lib/jahr.ts`, 05-04).
- `texte.json` / `typen.ts` were not touched; `lib/texte.ts` only uses `Texte` and `Erklaertext`.

## Known Stubs

None.

## Threat Flags

None. T-05-14 (no raw HTML, grep gate empty), T-05-15 (year binding with tests) and T-05-16 (`Object.hasOwn`/`Map`) are mitigated.

## Self-Check: PASSED

All 13 files exist, commits d9a24d0, e465c77, 7f79fae, 984a943 exist, acceptance greps pass.
