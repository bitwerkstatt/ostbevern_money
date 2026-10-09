---
phase: 08-fixes-und-triage
plan: 04
subsystem: ui
tags: [vue, format, euro-betrag, rd-regel, refactor]

requires:
  - phase: 08-fixes-und-triage
    provides: "08-02: charts/format.ts als einzige Stelle der Regel rd. (RD_PRAEFIX, betragMitHinweis, kurzMitHinweis), EuroBetrag mit kurz-Prop"
provides:
  - "Zwölf Altkopien der Regel rd. außerhalb ZuschussListe entfernt; Templates nutzen EuroBetrag, .ts-Texte betragMitHinweis/kurzMitHinweis"
affects: [08-05, 08-07]

plan_head_before: b3aec27fde1414fd0d766fec9e7682c3813a2de2
plan_head_after: fdd22d7d8eaad71976123a67f30e6b1d18afd634

actuals:
  tokens: 6000
  tasks: 3
  commits: 3

tech-stack:
  added: []
  patterns:
    - "Tabellenzellen mit Betrag rendern <EuroBetrag> (rd. und Etikett berechnet in einer Komponente)"
    - "Betragstexte in .ts und Template-Ausdrücken über betragMitHinweis/kurzMitHinweis"

key-files:
  created: []
  modified:
    - app/src/components/SteuerZeitreihe.vue
    - app/src/components/PostenZeitreihe.vue
    - app/src/pages/AusgabenPage.vue
    - app/src/pages/EinnahmenPage.vue
    - app/src/components/KreisumlageCallout.vue
    - app/src/components/AufwandTreemap.vue
    - app/src/components/EbenenTabelle.vue
    - app/src/components/NichtBeeinflussbarBlock.vue
    - app/src/lib/drilldown.ts
    - app/src/lib/zeitreihen.ts
    - app/src/lib/__tests__/quelltext.test.ts
    - app/src/lib/__tests__/drilldown.test.ts
    - app/src/lib/__tests__/zeitreihen.test.ts

key-decisions:
  - "NichtBeeinflussbarBlock nutzt das gerundet-Flag des Postens (Zuschuss.gerundet) statt eines festen true; für 2026 sind alle angezeigten Posten gerundet (Sozialleistungen und KL-Unterposten), die Anzeige bleibt gleich"
  - "drilldown.ts Balkenlabel ruft kurzMitHinweis(Math.abs(wert), eintrag.gerundet) einmal auf statt einer Verzweigung mit festem true"

requirements-completed: [TXT-04]

coverage:
  - id: D1
    description: "Tabellenzellen von SteuerZeitreihe, PostenZeitreihe, AusgabenPage und EinnahmenPage (2x) rendern EuroBetrag statt eigenem rd.-Markup"
    requirement: TXT-04
    verification:
      - kind: e2e
        ref: "scripts/e2e-wie-ci.sh (project ci, 81 Tests inkl. smoke.spec.ts mit axe)"
        status: pass
      - kind: unit
        ref: "app/src/lib/__tests__/quelltext.test.ts#lässt %s unbeanstandet"
        status: pass
    human_judgment: false
  - id: D2
    description: "KreisumlageCallout, AufwandTreemap, EbenenTabelle, NichtBeeinflussbarBlock, drilldown.ts und zeitreihen.ts bilden rd. nur über charts/format; Tests pinnen die U+00A0-Form"
    requirement: TXT-04
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/zeitreihen.test.ts#betragText; app/src/lib/__tests__/drilldown.test.ts#kennzeichnet gerundete Beträge mit rd."
        status: pass
      - kind: e2e
        ref: "scripts/e2e-wie-ci.sh (project ci, 81 Tests, darunter kacheln.spec.ts)"
        status: pass
    human_judgment: false

duration: 20min
completed: 2026-10-07
status: complete
---

# Phase 8 Plan 04: rd.-Altkopien durch die gemeinsame Regel ersetzt Summary

**Zwölf handgebaute „rd.“-Kopien in Tabellen, Kacheln, Treemap, Drilldown und Zeitreihen laufen jetzt über EuroBetrag bzw. betragMitHinweis/kurzMitHinweis aus charts/format.ts (05/WR-01, TXT-04).**

## Performance

- **Duration:** ca. 20 min
- **Completed:** 2026-10-07
- **Tasks:** 3
- **Files modified:** 13

## Accomplishments
- Task 1: fünf Tabellenzellen (SteuerZeitreihe, PostenZeitreihe, AusgabenPage, EinnahmenPage 2x) rendern `<EuroBetrag>`; auf EinnahmenPage ersetzt `:berechnet` das separate `BerechnetEtikett`.
- Task 2: KreisumlageCallout (EuroBetrag mit `gerundet kurz`), AufwandTreemap und NichtBeeinflussbarBlock (kurzMitHinweis), EbenenTabelle ohne lokale `betragText`.
- Task 3: drilldown.ts (Tooltip, Balkenlabel) und zeitreihen.ts (`betragText`, KEIN_WERT für null bleibt) über format.ts; Tests erwarten `RD_PRAEFIX`.
- Für Besucher ändert sich nur das Leerzeichen nach „rd.“ (U+00A0). Pipeline-Lauf `alle.py --jahr 2026` lässt `daten/`, `app/src/data/` und `app/public/quellen` unverändert.

## Task Commits

1. **Task 1: Tabellenzellen über EuroBetrag** - `d848102` (refactor, 05/WR-01)
2. **Task 2: Kacheln, Callout, Treemap** - `39efb8f` (refactor, 05/WR-01)
3. **Task 3: Drilldown und Zeitreihen** - `fdd22d7` (refactor, 05/WR-01)

**Plan metadata:** folgt (docs: complete plan)

## Files Created/Modified
- `app/src/components/SteuerZeitreihe.vue`, `PostenZeitreihe.vue`, `app/src/pages/AusgabenPage.vue`, `EinnahmenPage.vue` - Betragszellen über EuroBetrag, ungenutzte Importe (`euro`, `BerechnetEtikett`) entfernt
- `app/src/components/KreisumlageCallout.vue`, `AufwandTreemap.vue`, `EbenenTabelle.vue`, `NichtBeeinflussbarBlock.vue` - gemeinsame Regel
- `app/src/lib/drilldown.ts`, `zeitreihen.ts` - Hinweis über format.ts
- `app/src/lib/__tests__/quelltext.test.ts`, `drilldown.test.ts`, `zeitreihen.test.ts` - an die neue Form angepasst

## Decisions Made
- NichtBeeinflussbarBlock liest `p.gerundet` des Postens (Typ trägt das Flag). Geprüft: Sozialleistungen und KL-Unterposten sind 2026 gerundet, die Anzeige bleibt identisch.
- EbenenTabelle behält `betragMitHinweis(...)` als Template-Ausdruck, wie der Plan vorsieht.

## Deviations from Plan

None - plan executed exactly as written. (Prettier-Umbrüche in EinnahmenPage.vue und EbenenTabelle.vue wurden vor dem Commit angewendet.)

## Issues Encountered
None

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Verbleibend sind nur die drei Stellen in `ZuschussListe` (Plan 08-05); danach kann der Wächtertest aus 08-07 neue Kopien verbieten.

## Self-Check: PASSED
- Alle drei Commits (`d848102`, `39efb8f`, `fdd22d7`) sind Vorfahren von HEAD.
- Scratch-Kette grün: type-check, lint, format:check, 2017 Vitest-Tests, build-only, Playwright project ci 81 Tests.
- `grep -rn "rd\. "` außerhalb ZuschussListe und Tests listet nur Kommentarzeilen.

---
*Phase: 08-fixes-und-triage*
*Completed: 2026-10-07*
