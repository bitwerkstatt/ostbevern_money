---
phase: 06-kontext-seiten
plan: 13
subsystem: ui
tags: [vue, vitest, ruecklagen, entwicklung, gap-closure]

requires:
  - phase: 06-kontext-seiten
    provides: "ruecklagen.ts mit abbau()/rueckgang() und die Rücklagen-Tabelle auf /entwicklung (06-08, 06-12)"
provides:
  - "rueckgangFormelText(): Fußnotenklausel, die jeden Term der Rückgang-Formel nennt, auch die Verrechnung der Bilanzierungshilfe (CR-01)"
  - "baueRuecklagen() ohne Teilsumme: summe ist null, sobald eine der beiden Rücklagen fehlt (WR-04)"
affects: [06-kontext-seiten, verification-06]

actuals:
  tokens: 9000
  tasks: 2
  commits: 4
plan_head_before: 8878f321a08314d99cc6781fd257d9afb061c958
plan_head_after: 5e9286d3344e49743b2b80e15cc1a72d89b9ed03

tech-stack:
  added: []
  patterns:
    - "Bürgertext aus denselben Konstanten wie die Formel (Text und Rechnung nebeneinander, Nachrechentest je Planjahr)"
    - "Quelltexttest per import.meta.glob ?raw pinnt, dass die Seite die Lib-Funktion statt Handtext nutzt"

key-files:
  created: []
  modified:
    - app/src/lib/ruecklagen.ts
    - app/src/lib/__tests__/ruecklagen.test.ts
    - app/src/pages/EntwicklungPage.vue

key-decisions:
  - "Verrechnungs-Klausel zitiert den gedruckten Postennamen aus den Daten (Einmalige Verrechnung Bilanzierungshilfe) statt einer Paraphrase"
  - "postenName() wird auch ohne Verrechnung aufgerufen, damit ein fehlender Posten immer als Datenfehler auffällt"

patterns-established:
  - "Nachrechentest: der Test rechnet nur aus den Termen, die der Text nennt, und vergleicht auf 12 Nachkommastellen mit rueckgang()"

requirements-completed: [ENTW-03]

duration: 12min
completed: 2026-10-06
status: complete
---

# Phase 6 Plan 13: Fußnote nennt die Verrechnung, keine Teilsumme der Rücklagen Summary

**Die Fußnote unter der Rücklagen-Tabelle auf /entwicklung entsteht jetzt aus `rueckgangFormelText()` neben `abbau()`, nennt die Verrechnung der Bilanzierungshilfe mit ihrem gedruckten Postennamen und reproduziert damit die gezeigten 1,77 % statt 0,56 %; `baueRuecklagen()` liefert nie mehr eine Teilsumme.**

## Performance

- **Duration:** 12 min
- **Tasks:** 2 (Tracer + WR-04)
- **Files modified:** 3

## Accomplishments

- CR-01 geschlossen: Die Fußnote beschreibt die implementierte Formel `max(0, −Jahresergebnis − Ausgleichsrücklage) − Verrechnung` vollständig. Die Verrechnungs-Klausel erscheint genau dann, wenn mindestens ein Jahr von `verrechnung_bilanzierungshilfe` weder `null` noch 0 ist (Jahrgang 2026: Wert -476327 im Haushaltsjahr). Der Text enthält keine Ziffer; die einzige Zahl in der Fußnote bleibt die PDF-Seite aus den Daten.
- Nachrechentest: Für jedes Planjahr wird der Rückgang allein aus den im Text genannten Termen berechnet und stimmt auf 12 Nachkommastellen mit `rueckgang()` überein (echte Daten und Tabelle ohne Verrechnung). Der 2026-Regressionsschutz belegt, dass ohne Verrechnungsterm 0,56 % herauskäme, die Seite aber 1,77 % zeigt.
- `EntwicklungPage.vue` baut `tabellenFussnote` aus Quellpräfix, PDF-Seite der Schwellen und `rueckgangFormelText()`; ein Quelltexttest pinnt, dass die Formelprosa nicht mehr in der Seite steht.
- WR-04 geschlossen: `summe` ist `null`, wenn `allgemeine` oder `ausgleich` fehlt; mit beiden Werten ist es die exakte Summe, eine echte 0 zählt als Wert. `RuecklagenBalken.vue` blieb unverändert (blendet bei `null` das Label aus und zeigt „–“).
- Keine angezeigte Zahl hat sich geändert: `abbau()`/`rueckgang()` unangetastet, S.-23-Test (1,77 / 4,23 / 4,73 / 10,04 %) und S.-311-Spaltenidentität grün.

## Task Commits

1. **Task 1: Tracer CR-01** - `9fcdfe2` (test, RED: Platzhalter + 7 Assertion-Fehlschläge), `8bc9369` (fix, GREEN)
2. **Task 2: WR-04** - `c574519` (test, RED: 2 Assertion-Fehlschläge), `5e9286d` (fix, GREEN)

**Plan metadata:** folgt als docs-Commit (SUMMARY.md).

## Files Created/Modified

- `app/src/lib/ruecklagen.ts` - `rueckgangFormelText()`, private `postenName()`/`hatVerrechnung()`, `summe` ohne Teilsumme, Kopfkommentar und Doc-Kommentar
- `app/src/lib/__tests__/ruecklagen.test.ts` - Describe-Block `rueckgangFormelText (CR-01, S. 23)`, angepasste und neue WR-04-Tests
- `app/src/pages/EntwicklungPage.vue` - `tabellenFussnote` mit `rueckgangFormelText()`

## Decisions Made

- Die Klausel zitiert den Postennamen aus den Daten, damit der Begriff genau der Zeile entspricht, die Leserinnen und Leser auf S. 311 finden.
- `postenName()` für die Verrechnung läuft unbedingt, damit ein fehlender Posten immer wirft (Datenfehler statt stiller Auslassung).
- Wortlaut „zuzüglich der Verrechnung aus der Zeile …“ wie im Plan vorgegeben. Hinweis für die menschliche Sichtprüfung: Die Verrechnung steht im Druck negativ gebucht, der Abbau erhöht sich um ihren Betrag; „zuzüglich“ ist als Betrag gemeint. Wenn das zu missverständlich wirkt, kann der Wortlaut an genau einer Stelle (`rueckgangFormelText()`) geschärft werden; der Nachrechentest bleibt gültig.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Format der Testdatei im GREEN-Commit**
- **Found during:** Task 1 (format:check)
- **Issue:** Die im RED-Commit eingecheckte Testdatei war nicht prettier-konform.
- **Fix:** Prettier im Scratch-Copy ausgeführt, Datei zurückkopiert; die formatierte Testdatei ist Teil des GREEN-Commits `8bc9369` (nur Formatierung).
- **Files modified:** app/src/lib/__tests__/ruecklagen.test.ts
- **Verification:** `format:check` grün

**2. [Verify-Umgebung] `npm ci` ersetzt durch Wiederverwendung des Linux-`node_modules`**
- Das Netz fehlt in der Sandbox; wie in den Plänen 06-02 … 06-12 und laut Auftrag wurde ein Scratch-Copy von `app/` mit Symlink auf das vorhandene Linux-`node_modules` (identische Lockfile) genutzt. Es wurde nichts im Worktree oder im Haupt-Checkout installiert.

**Total deviations:** 1 auto-fixed (Rule 3), 1 Umgebungsabweichung. **Impact:** keine fachliche Auswirkung.

## Issues Encountered

None.

## TDD Gate Compliance

Task 1: RED `9fcdfe2` (7 Tests schlagen auf Assertions fehl, u. a. Nachrechentest liefert 0,56 % statt 1,77 %), GREEN `8bc9369`. Task 2: RED `c574519` (2 Assertion-Fehlschläge: `expected 39522991 to be null`, `expected 1940223 to be null`), GREEN `5e9286d`. Kein REFACTOR nötig.

## Verification

- Vitest (gesamte Suite im Scratch-Copy): 1405 Tests grün, darunter `ruecklagen.test.ts` und `quelltext.test.ts`.
- `type-check`, `lint`, `format:check`, `build`: grün.
- Akzeptanzkriterien beider Tasks per grep geprüft (kein Jahreszahl-Literal in Codezeilen von `ruecklagen.ts`; `RuecklagenBalken.vue` unverändert und in keinem Commit).

## User Setup Required

None - no external service configuration required.

## Known Stubs

None.

## Next Phase Readiness

- Die Lücke SC1 / ENTW-03 (CR-01) aus 06-VERIFICATION.md ist aus Code und Tests wiederverifizierbar; die visuelle Sichtprüfung der Fußnote im Browser bleibt ein menschlicher Check am Phasenende.

## Self-Check: PASSED

- Commits `9fcdfe2`, `8bc9369`, `c574519`, `5e9286d` vorhanden; geänderte Dateien vorhanden.

---
*Phase: 06-kontext-seiten*
*Completed: 2026-10-06*
