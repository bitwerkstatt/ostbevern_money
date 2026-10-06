---
phase: 06-kontext-seiten
plan: 03
subsystem: ui
tags: [vue, web-awesome, wa-callout, erklaertext, bbo, teo]

requires:
  - phase: 05-detailseiten
    provides: ErklaerText, findeText, KreisumlageCallout-Muster, quelltext.test.ts
provides:
  - "HinweisNichtImHaushalt.vue (Prop variante: ausgaben | einnahmen | kurz)"
  - "Hinweisbox am Ende von /ausgaben und /einnahmen"
  - "hinweis.test.ts (Strukturtest, von 06-07 und 06-12 zu erweitern)"
affects: [06-04, 06-07, 06-12]

actuals:
  tokens: 2500
  tasks: 2
  commits: 3
plan_head_before: 724fa45bf051bed5c07a034bac3e8560379aaa70
plan_head_after: 183216fc14ae513000e3130f4689abb62bb143dd

tech-stack:
  added: []
  patterns:
    - "Leitsaetze als ReadonlyMap Variante -> Text, ohne Ziffer; Zahlen nur aus Pipeline-Text"
    - "Aufklapper nur bei vorhandenem Text (findeText), Leitsatz bleibt"

key-files:
  created:
    - app/src/components/HinweisNichtImHaushalt.vue
    - app/src/lib/__tests__/hinweis.test.ts
  modified:
    - app/src/pages/AusgabenPage.vue
    - app/src/pages/EinnahmenPage.vue

key-decisions:
  - "Auf /einnahmen steht die Hinweisbox hinter dem Seitencontainer .om-einnahmen, nicht darin, damit sich der Abstand (margin-block-start) nicht mit dem Flex-Gap verdoppelt"
  - "Die Kurzform behaelt die Ueberschrift der Komponente; sie ersetzt nur Aufklapper durch Glossarlink"

patterns-established:
  - "Ziffernpruefung im Template ohne Markup (Tag-Namen wie h2 tragen Ziffern)"

requirements-completed: [UI-04]

coverage:
  - id: D1
    description: "Wiederverwendbare Hinweisbox 'Was nicht im Haushalt steht' mit den drei Varianten, Pipeline-Text nur ueber ErklaerText ohne jahr-Prop"
    requirement: UI-04
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/hinweis.test.ts#HinweisNichtImHaushalt auf /einnahmen und in der Kurzform"
        status: pass
      - kind: unit
        ref: "app/src/lib/__tests__/quelltext.test.ts#Keine getippten Zahlen in den Templates"
        status: pass
    human_judgment: false
  - id: D2
    description: "Hinweisbox steht am Ende von /ausgaben (variante ausgaben) und /einnahmen (variante einnahmen)"
    requirement: UI-04
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/hinweis.test.ts#AusgabenPage bindet die Hinweisbox mit variante=ausgaben ein"
        status: pass
      - kind: unit
        ref: "app/src/lib/__tests__/hinweis.test.ts#EinnahmenPage setzt die Hinweisbox hinter den Abschnitt Investive Einnahmen"
        status: pass
    human_judgment: false
  - id: D3
    description: "Optik und Umbruch bei 360 px und 1280 px (kein horizontales Scrollen, Aufklapper oeffnet und zeigt Text mit PDF-Seiten)"
    verification: []
    human_judgment: true
    rationale: "Kein Browser im Sandbox-Lauf; das Layout prueft kein Test (Plan: human-check im Dev-Server)"

duration: 8min
completed: 2026-10-06
status: complete
---

# Phase 6 Plan 03: Hinweisbox "Was nicht im Haushalt steht" Summary

**Wiederverwendbare Hinweisbox zu BBO und TEO (wa-callout, drei Varianten) mit dem geprueften Pipeline-Text nicht_im_haushalt, eingebaut am Ende von /ausgaben und /einnahmen**

## Performance

- **Duration:** 8 min
- **Started:** 2026-10-06T05:34:00Z
- **Completed:** 2026-10-06T05:42:00Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments
- `HinweisNichtImHaushalt.vue`: `wa-callout variant="neutral"` mit `circle-info`, Ueberschrift "Was nicht im Haushalt steht" (h2, `--wa-font-size-l`, `--wa-font-weight-bold`), Leitsatz je Variante (digit-frei, wortlich laut UI-SPEC), bei `ausgaben`/`einnahmen` ein geschlossener `wa-details` "Was sind BBO und TEO?" mit `ErklaerText schluessel="nicht_im_haushalt"` (S. 14/33/46/48, Zahlen aus der Pipeline), bei `kurz` der Link "Mehr dazu im Glossar" auf `{ name: 'glossar', hash: '#nicht_im_haushalt' }`.
- Fehlt der Pipeline-Text, entfaellt nur der Aufklapper; kein Laufzeitfehler (E11 empty).
- Einbau als letztes Element von `AusgabenPage.vue` (nach der Aufwandsart-Karte) und `EinnahmenPage.vue` (nach "Investive Einnahmen").
- `hinweis.test.ts`: 10 Strukturtests (Platzierung, Variante, Ueberschrift, Leitsaetze wortlich, Glossaranker, keine Ziffer im Template-Text und in den Leitsaetzen, Pipeline-Text vorhanden mit PDF-Seite).

## Task Commits

1. **Task 1: Tracer, Hinweisbox (Variante ausgaben) auf /ausgaben** - `f838023` (feat)
2. **Task 2 RED: fehlender Einbau auf /einnahmen** - `8612c0f` (test)
3. **Task 2 GREEN: Variante einnahmen auf /einnahmen** - `183216f` (feat)

Tracer-Gate: `<verify>` (Test, type-check, lint, format:check) nach Task 1 gruen, Ausbau fortgesetzt.

## Files Created/Modified
- `app/src/components/HinweisNichtImHaushalt.vue` - die Hinweisbox mit drei Varianten
- `app/src/lib/__tests__/hinweis.test.ts` - Strukturtest der Platzierung und der Texte
- `app/src/pages/AusgabenPage.vue` - Einbau `variante="ausgaben"`
- `app/src/pages/EinnahmenPage.vue` - Einbau `variante="einnahmen"`

## Decisions Made
- Auf /einnahmen steht die Box hinter dem Container `.om-einnahmen`, nicht darin: das Flex-Gap (xl) und der Eigenabstand der Komponente (xl) wuerden sich sonst verdoppeln.
- Die Kurzform behaelt die Ueberschrift, sie ersetzt nur den Aufklapper durch den Glossarlink.
- Die Leitsaetze liegen im Skript als `ReadonlyMap`, nicht im Template, damit der Ziffern-Test des Templates nur echten Text prueft.

## TDD Gate Compliance
Task 2 (`tdd="true"`): RED `8612c0f` (2 Assertions fehlgeschlagen, Ziel: Einbau auf /einnahmen), GREEN `183216f`. Der Rest der Task-2-Tests (Leitsaetze, Glossaranker) war bereits durch Task 1 erfuellt, wie der Plan erlaubt ("if Task 1 did not already"). Kein REFACTOR noetig.

## Deviations from Plan

None - plan executed exactly as written.

Hinweis: Der Test "keine Ziffer im Template" wurde nach dem ersten GREEN-Lauf auf den Text ohne Markup umgestellt, weil `<h2` selbst eine Ziffer enthaelt (Testfehler, nicht Produktcode).

## Issues Encountered
- Prettier verlangte den Zeilenumbruch der `wa-details`-Attribute; angepasst vor dem Commit.
- Die Sandbox hat keinen Browser: Sichtpruefung bei 360/1280 px (human-check aus Task 2) steht aus.

## Known Stubs
None.

## Threat Flags
None. Text laeuft nur ueber `ErklaerText` (Textinterpolation, kein Roh-HTML); `quelltext.test.ts` prueft jede .vue-Datei (T-06-07). Leitsaetze sind digit-frei (T-06-08). Keine neue Abhaengigkeit (T-06-SC).

## Verification
Im Scratch-Copy von `app/` (Linux-node_modules): `type-check`, `lint`, `format:check` ohne Befund, `test` 1042 bestanden (inkl. `hinweis.test.ts` und `quelltext.test.ts`), `build` erfolgreich. Alle Acceptance-Greps beider Tasks bestanden.

## Next Phase Readiness
- Variante `kurz` ist fuer /rat-entscheidet (06-07) bereit; der Glossaranker `nicht_im_haushalt` kommt mit 06-04 und wird in 06-12 geprueft.
- Offen: human-check Layout bei 360 px und 1280 px.

---
*Phase: 06-kontext-seiten*
*Completed: 2026-10-06*

## Self-Check: PASSED
