---
phase: 09-sicherheit-und-audit
plan: 13
subsystem: planning
tags: [milestone-audit, integration, e2e-flows, gap-triage, d-10, v1.0, v1.0.1]

requires:
  - phase: 09-sicherheit-und-audit
    provides: "09-12: Audit-Datei mit Kopf, Phasentabelle, 102 Anforderungszeilen und Nyquist-Befunden; 09-BASISLAUF.md als Laufevidenz; erneuerte VERIFICATION-Berichte"
provides:
  - "Abschnitt Integration: acht Glieder der Datenkette von PDF bis Deploy, alle wired, mit Datei:Zeile und Basislauf-Beleg"
  - "Abschnitt End-to-End-Flüsse: F1 bis F7, vier complete, drei partial, mit Playwright-Titeln aus dem Basislauf"
  - "Lückenliste (D-10) mit 23 Zeilen G-09-01 bis G-09-23, drei fix, CR-01 nach D-22 deferred"
  - "Tech Debt je Phase, Arbeitsliste Für 09-14 und aktualisierte Frontmatter (scores, gaps, tech_debt, status gaps_found)"
affects: [09-14, 09-15]

actuals:
  tokens: 13600
  tasks: 3
  commits: 4
plan_head_before: 0f01dea37a489a794c03eedeee3d581d944a243a
plan_head_after: 16f980fe783a14f35fe5e4cff4df05ae9f5aef71 (letzter Task-Commit; der SUMMARY-Commit folgt darauf und ist in commits mitgezählt)

tech-stack:
  added: []
  patterns:
    - "Eine schriftliche D-10-Regel für alle Kandidaten, Check je Zeile in der Spalte Kernaussage"
    - "Arbeitsliste als Aufzählung statt Tabelle, damit die Zeilenzählung der Lückenliste nicht doppelt zählt"

key-files:
  created:
    - .planning/phases/09-sicherheit-und-audit/09-13-SUMMARY.md
  modified:
    - .planning/v1.0-MILESTONE-AUDIT.md

key-decisions:
  - "Integration 8/8: kein Glied broken; Deploy nur im Quelltext (needs) bewertet, der Lauf selbst ist Nutzerbestätigung vom 2026-10-08"
  - "Flüsse 4/7: F2, F3, F4 partial, weil der Browser-Schritt (B1 bis B4) keinen automatischen Beleg hat; kein Fluss broken"
  - "D-10 gelesen als: sichtbarer Mangel in einem gezeigten Jahr (falsche Zahl, nicht abgeleitete Betragsaussage, falscher Text, Zugänglichkeit, Name) ist fix; Latentes und Testlücken ohne bekannten Defekt sind deferred mit Auslöser"
  - "Drei fix-Zeilen: fester Superlativ (wahr, aber nicht abgeleitet), PDF-Seite im Singular bei mehreren Seiten (18 von 21 Texten), Grundsteuer (A+B) ohne Etikett berechnet"
  - "-0 € bleibt deferred: kleinster negativer Zuschussbedarf ist −42.008 €, die Schwelle liegt bei −5.870 €"
  - "CR-01 (s009.webp) deferred nach Nutzerentscheidung 2026-10-07 (D-22)"

patterns-established:
  - "Jede Zeile der Lückenliste nennt den gemachten Check (Daten gezählt, Quelltext gelesen) statt einer Annahme"

requirements-completed: [AUD-01]

coverage:
  - id: D1
    description: "Integration der Datenkette in acht Gliedern, alle wired mit Datei:Zeile und Basislauf-Beleg; Authentifizierung und API als nicht zutreffend vermerkt"
    requirement: "AUD-01"
    verification:
      - kind: other
        ref: "bash-Prüfung der Task-1-verify (Glieder 8, ohne Urteil 0, scores.integration 8/8, Satz kein Backend)"
        status: pass
    human_judgment: false
  - id: D2
    description: "End-to-End-Flüsse F1 bis F7 mit Urteil und zitierten Playwright-Titeln, die wörtlich im Basislauf stehen"
    requirement: "AUD-01"
    verification:
      - kind: other
        ref: "bash-Prüfung der Task-2-verify (alle sieben Flüsse mit Urteil, scores.flows 4/7) und Titelabgleich gegen 09-BASISLAUF.md ohne Abweichung"
        status: pass
    human_judgment: false
  - id: D3
    description: "Lückenliste mit D-10-Einstufung, Tech Debt, CR-01 nach D-22 und Arbeitsliste für 09-14"
    requirement: "AUD-01"
    verification:
      - kind: other
        ref: "bash-Prüfung der Task-3-verify (23 Zeilen, 3 fix, 0 ungültig, CR-01 mit 2026-10-07, Status gaps_found passt zu fix gleich 3)"
        status: pass
    human_judgment: true
    rationale: "Die D-10-Einstufung ist die Lesart des Planers (Annahme des Plans 09-13); der Nutzer kann die Disposition einzelner Zeilen überstimmen, vor allem G-09-01 bis G-09-03 (fix) und G-09-06 bis G-09-10 (deferred)"

duration: 20min
completed: 2026-10-09
status: complete
---

# Phase 9 Plan 13: Milestone-Audit Teil 2 Summary

**Integration der Datenkette 8/8 wired, End-to-End-Flüsse 4/7 complete, und eine nach D-10 triagierte Lückenliste mit 23 Zeilen, aus der drei Kernaussage-Lücken (fester Superlativ, „PDF-Seite“ im Singular, Grundsteuer ohne „berechnet“) an Plan 09-14 gehen**

## Performance

- **Duration:** 20 min
- **Started:** 2026-10-09T06:45:00Z
- **Completed:** 2026-10-09T07:06:00Z
- **Tasks:** 3
- **Files modified:** 1 (`.planning/v1.0-MILESTONE-AUDIT.md`)

## Accomplishments

- **Integration (Task 1, tracer):** Die Kette PDF → `alle.py`-Schritte → `daten/` → `app/src/data/*.json` → `daten.ts`/`typen.ts` → `app/src/lib` → Seiten der elf Routen → `app/public/quellen` → CI und Deploy ist Glied für Glied bewertet. Im Lauf gezählt: 231 Seiten in `quellen.json` und 231 Bilder, 2496 Belege ohne tote Verweise, kein JSON ohne Importeur, keine Route ohne Seite, kein Modul ohne Importeur (die scheinbare Ausnahme `webawesome.ts` lädt `main.ts:1`). Authentifizierung und API sind als „nicht zutreffend, kein Backend“ vermerkt.
- **Flüsse (Task 2):** F1 (Quelle anzeigen), F5 (Kontextseiten mit „berechnet“), F6 (mobiles Menü) und F7 (rote Prüfregel stoppt CI und Deploy) sind complete. F2 (Drilldown), F3 (Geldfluss) und F4 (Glossar-Sprung) sind partial: Der jeweilige Browser-Schritt (Treemap-Klick, Sankey-Klick und Hover, Umschaltung unter 700 px, Sprung unter die Kopfzeile) hat keinen automatischen Beleg; Zustandslogik und Daten sind getestet, die Nutzerbelege aus `05-UAT.md` liegen vor Phase 7 und 8.
- **Lückenliste (Task 3):** 23 Kandidaten aus allen Quellen des Plans, je mit Check und Disposition. Drei `fix`, 18 `deferred`, 2 `v2-backlog` (ERW-03). Die fünf offenen Punkte aus `08-12-SUMMARY.md`, die Nyquist-Befunde zu Phase 4 und 5, die Dokumentationsabweichungen, `npm audit`, die D-20-Info-Befunde, die untracked-Dateien und CR-01 sind abgebildet. Das Ergebnis der Prüfung der fünf offenen Punkte: Superlativ, „PDF-Seite“ und Grundsteuer-Etikett sind `fix`; „-0 €“ und der `useJahr`-Watcher sind deferred, weil sie keine Wirkung auf die gezeigten Daten haben.

## Task Commits

1. **Task 1: Integration der Datenkette (tracer)** - `77e724f` (docs)
2. **Task 2: End-to-End-Flüsse F1 bis F7** - `bd75c1f` (docs)
3. **Task 3: Lückenliste nach D-10, Tech Debt, Status** - `16f980f` (docs)

**Plan metadata:** der Commit dieser SUMMARY-Datei (docs: complete plan)

Tracer-Gate nach Task 1 (Modus end-of-phase, `<verify>` nur automatisiert): `<verify>` erneut gelaufen, grün, danach Expansion (Tasks 2 und 3).

## Files Created/Modified

- `.planning/v1.0-MILESTONE-AUDIT.md` - Abschnitte Integration, End-to-End-Flüsse, Lückenliste (D-10) mit Arbeitsliste „Für 09-14“, Tech Debt; Frontmatter `scores.integration` 8/8, `scores.flows` 4/7, `gaps.flows`, `gaps.kernaussage`, `luecke`-Ids an den fünf Anforderungslücken, `tech_debt` mit Ids, `status: gaps_found`.

## Decisions Made

- **Lesart von D-10 für den Superlativ:** Er ist in allen sechs Jahren wahr (Weitergabe an Kreis und Land 2026: 11.001.181 € gegen 4.519.223 € beim größten Aufgabenbereich), aber eine Aussage über Beträge ohne Ableitung aus den Daten und ohne Test. Deshalb `fix`: Funktion `istGroessterEinzelposten` plus Test, damit der Satz nie falsch erscheinen kann. Das ist die strengere Lesart; sie steht in der Lückenliste offen, der Nutzer kann die Zeile auf `deferred` stellen.
- **Grundsteuer (A+B):** `fix`, weil die Projektkonvention jede von der App gebildete Summe als „berechnet“ kennzeichnet (DATA-03, AUSG-05, auf den Kontextseiten seit 08-03 umgesetzt) und die Leitfragen-Seite /geldfluss davon abweicht.
- **Verhaltenslücken B1 bis B4 und H2 bleiben deferred:** kein bekannter Defekt, der Code ist gelesen, Zustandslogik und Daten sind getestet, Nutzerbelege liegen vor. Ein Playwright-Test ist nur im Container ausführbar und gehört nicht in diese Phase.
- **`-0 €` latent:** Skript über alle Knoten und Jahre; kleinster negativer Zuschussbedarf −42.008 €, die Schwelle für „-0 €“ liegt bei −5.870 €.

## Deviations from Plan

None - plan executed exactly as written.

Hinweise zur Ausführung (keine Abweichungen vom Plan):

- Die Verify-Befehle der Tasks wurden als kleine Skripte in der Scratch-Ablage der Sitzung ausgeführt, weil die Sandbox verschachtelte Befehle in Worktrees ablehnt. Inhalt und Prüfmuster entsprechen den `<automated>`-Blöcken des Plans.
- Das Ledger `gsd-plan-head-before-09-13` ließ sich nicht im Git-Verzeichnis des Worktrees anlegen (Sandbox verbietet den Schreibzugriff auf den gemeinsamen Pfad). `plan_head_before` stammt aus dem HEAD beim Start des Plans (`0f01dea`, durch die Basisprüfung bestätigt); `commits` ist mit `git rev-list --count` gemessen (3 vor dem SUMMARY-Commit).
- `requirements.mark-complete` für AUD-01 wurde nicht ausgeführt: AUD-01 steht auch in 09-14 und 09-15, das Shared-ID-Gate hält die ID bis zum letzten Plan zurück; STATE.md und ROADMAP.md gehören dem Orchestrator.

## Issues Encountered

None

## User Setup Required

None - no external service configuration required.

## Known Stubs

None. Dieser Plan ändert nur die Audit-Datei.

## Threat Flags

None. Keine neue Angriffsfläche; der Plan ändert nur `.planning/`.

## Next Phase Readiness

- Plan 09-14 hat eine konkrete Arbeitsliste: drei `fix`-Zeilen (G-09-01 bis G-09-03) mit Dateien und Testnamen. Das liegt innerhalb der Grenze von 09-14 (höchstens vier Zeilen, höchstens fünf Dateien je Zeile; G-09-02 berührt fünf Dateien).
- Der Status der Audit-Datei ist `gaps_found`; 09-15 berechnet ihn nach dem Nachlauf neu.
- Offene Entscheidung für den Nutzer: die Lesart von D-10 bei G-09-01 bis G-09-03 (fix) und G-09-06 bis G-09-10 (deferred).

## Self-Check: PASSED

- `.planning/v1.0-MILESTONE-AUDIT.md` vorhanden, enthält `## Integration`, `## End-to-End-Flüsse`, `## Lückenliste (D-10)` und `## Tech Debt` (grep geprüft).
- Commits `77e724f`, `bd75c1f`, `16f980f` liegen im Zweig (`git merge-base --is-ancestor`).
- Alle drei automatisierten Prüfungen laufen grün (VERIFY1_OK, VERIFY_OK für Flüsse und Lückenliste).

---
*Phase: 09-sicherheit-und-audit*
*Completed: 2026-10-09*
