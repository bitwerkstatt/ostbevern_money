---
phase: 08-fixes-und-triage
plan: 12
subsystem: planning-ledgers
tags: [review-ledger, triage, disposition, ci-gate, playwright, axe]

requires:
  - phase: 08-fixes-und-triage
    provides: "Fix-Commits der Pläne 08-01 bis 08-11, deren Betreff die Befund-Id nennt (z. B. 05/IN-06)"
provides:
  - "01-REVIEW-DISPOSITION.md, 05-REVIEW-DISPOSITION.md und 06-REVIEW-DISPOSITION.md auf open: 0, jede Zeile mit Plan, Commit-Hash oder Begründung"
  - "Fußtext in Ledger 05 zu den durch Id-Wiederverwendung verdrängten Befunden der ersten Review-Runde (ce51941)"
  - "Ergebnis des Abschlusslaufs der Querschnittsbedingung (Pipeline-CI, alle.py byte-identisch, App-CI, Playwright ci und mobil)"
affects: [phase-09-audit]

actuals:
  tokens: 4500
  tasks: 3
  commits: 3
plan_head_before: e844e5b4604793a37181e3881b1fe986d93e9e58
plan_head_after: 0ec7bc2a67d36eb4d9cab725c00be48bf5537145

tech-stack:
  added: []
  patterns:
    - "Ledger-Zeile eines behobenen Befunds: Source-Zelle 'fixed in 08-NN (hash, hash)' plus höchstens ein kurzer Zusatz, kein senkrechter Strich"

key-files:
  created: []
  modified:
    - .planning/milestones/v1.0-phases/01-setup/01-REVIEW-DISPOSITION.md
    - .planning/milestones/v1.0-phases/05-leitfragen-seiten/05-REVIEW-DISPOSITION.md
    - .planning/milestones/v1.0-phases/06-kontext-seiten/06-REVIEW-DISPOSITION.md

key-decisions:
  - "Alle 28 offenen Befunde sind mit Beleg entschieden: 27 fixed, 1 skipped (06/WR-01), 0 deferred; kein Plan der Phase hat einen Fix schuldig geblieben"
  - "Ledger 05 nennt im Fußtext zusätzlich zu den vier verdrängten Info-Befunden die zwei verdrängten Warnungen der ersten Runde (Sankey ohne rd./berechnet, Start-Satz zum größten Bereich); beide sind im Code erledigt"

requirements-completed: [TRI-01, TRI-02, TRI-03, TRI-04]

coverage:
  - id: D1
    description: "Ledger 01, 05 und 06 stehen auf open: 0; jede der 28 Zeilen nennt einen Commit oder eine Begründung; total, WR-Zeilen und Fußtexte sind unverändert (Fußtext 05 nur ergänzt)"
    requirement: "TRI-01, TRI-02, TRI-03, TRI-04"
    verification:
      - kind: other
        ref: "Task-Verify je Ledger: grep open: 0, kein disposition: open, awk-Prüfung der Source-Spalte, total unverändert"
        status: pass
    human_judgment: false
  - id: D2
    description: "Querschnittsbedingung am Ende der Phase: Pipeline-CI, alle.py --jahr 2026 byte-identisch, App-CI, Playwright ci und mobil grün"
    verification:
      - kind: integration
        ref: "uv run pytest (677 passed, 1 skipped; mit app/node_modules 23 passed in test_formatiere.py), alle.py --jahr 2026 mit git diff --exit-code"
        status: pass
      - kind: e2e
        ref: "scripts/e2e-wie-ci.sh <scratch>/app (87 passed) und --project=mobil (39 passed)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Screenreader-Check einer DatenTabelle bei 360 px: Name einmal oder zweimal angesagt (A1 aus 08-06)"
    verification: []
    human_judgment: true
    rationale: "Die Ansage durch VoiceOver oder NVDA lässt sich nicht automatisiert prüfen"

duration: 70min
completed: 2026-10-07
status: complete
---

# Phase 8 Plan 12: Ledger auf open 0 und Abschlusslauf Summary

**Die drei Review-Ledger (01, 05, 06) stehen auf `open: 0`: 27 der 28 offenen Befunde sind mit Plan und Commit-Hash als fixed belegt, 06/WR-01 ist mit UAT 06 Test 1 und PROJECT.md:138 als skipped begründet; die CI-identische Prüfkette ist auf dem Endstand der Phase grün.**

## Performance

- **Duration:** rund 70 min (davon etwa 6 min Voll-pytest, 2 min Playwright)
- **Started:** 2026-10-07T19:27:00Z (geschätzt)
- **Completed:** 2026-10-07T19:45:00Z
- **Tasks:** 3
- **Files modified:** 3 (Ledger) plus diese SUMMARY

## Accomplishments

- Ledger 01: IN-01 bis IN-05 fixed; IN-01 mit `1c14077` (bars.svg im Menüknopf, D-17), IN-02 `c18a032`, IN-03 `96a23de`, IN-04 `4c105ff`/`35b3d51`, IN-05 `fe416ab`.
- Ledger 05: WR-01, WR-02, IN-01 bis IN-11 fixed; IN-07 mit `53b96ac` plus `9f9c367`/`de7fe83` (08-02), IN-09 mit `1ab6b4b`, `b29be89`, `f4fad93`. Fußtext um den Absatz zu den verdrängten Befunden der ersten Runde (`ce51941`) ergänzt.
- Ledger 06: WR-01 skipped, IN-01 bis IN-09 fixed. Der Fußtext „Previous review“ bleibt.
- Abschlusslauf der Querschnittsbedingung auf dem Endstand: alles grün (Ergebnisse unten).

### Zählung je Ledger (nur die in Phase 8 entschiedenen Befunde)

| Ledger | Befunde in Phase 8 | fixed | skipped | deferred | open danach |
|--------|--------------------|-------|---------|----------|-------------|
| 01 | 5 (IN-01 bis IN-05) | 5 | 0 | 0 | 0 |
| 05 | 13 (WR-01, WR-02, IN-01 bis IN-11) | 13 | 0 | 0 | 0 |
| 06 | 10 (WR-01, IN-01 bis IN-09) | 9 | 1 (WR-01) | 0 | 0 |
| Summe | 28 | 27 | 1 | 0 | 0 |

Kein Befund ist `deferred`: Die SUMMARYs 08-01 bis 08-11 melden keinen nicht gelieferten Fix, und `deferred-items.md` ist in der Phase nirgends angelegt worden.

## Task Commits

1. **Task 1: Ledger 01 auf open: 0 (TRI-01)** - `3df6637` (docs)
2. **Task 2: Ledger 05 auf open: 0, verdrängte Befunde im Fußtext (TRI-02)** - `aae3f13` (docs)
3. **Task 3: Ledger 06 auf open: 0 (TRI-03, TRI-04)** - `0ec7bc2` (docs)

Task 1 war als Tracer markiert; seine scriptete Verify-Prüfung bestand, danach folgten die beiden weiteren Ledger. Der Abschlusslauf lief nach Task 3 auf dem fertigen Endstand.

## Files Created/Modified

- `.planning/milestones/v1.0-phases/01-setup/01-REVIEW-DISPOSITION.md` - IN-01 bis IN-05 mit Belegen, `open: 0`
- `.planning/milestones/v1.0-phases/05-leitfragen-seiten/05-REVIEW-DISPOSITION.md` - 13 Befunde mit Belegen, `open: 0`, Fußtext ergänzt
- `.planning/milestones/v1.0-phases/06-kontext-seiten/06-REVIEW-DISPOSITION.md` - WR-01 skipped, IN-01 bis IN-09 fixed, `open: 0`

## Ergebnis des Abschlusslaufs (Querschnittsbedingung, ROADMAP Kriterium 5)

| Prüfung | Ergebnis |
|---------|----------|
| `uv sync --locked` (offline), `ruff check`, `ruff format --check` | grün (All checks passed, 51 files already formatted) |
| `uv run pytest -q` im Worktree | 677 passed, 1 skipped (`test_port_wie_format_ts` braucht `app/node_modules/typescript`) |
| `pytest tests/test_formatiere.py` mit symlinkter Scratch-`node_modules` (danach wieder entfernt) | 23 passed, der übersprungene Port-Test läuft also grün; zusammen 678 |
| `alle.py --jahr 2026` | Prüfregeln 1 bis 10 grün, Veraltete Befunde: 0 |
| `git diff --stat --exit-code -- daten app/src/data` und `git status --porcelain --untracked-files=all -- daten app/src/data app/public/quellen` | beide leer, die Pipeline erzeugt alles byte-identisch neu |
| Scratch-Kopie: `npm ci`, `type-check`, `lint`, `format:check` | grün, keine Meldung |
| Scratch-Kopie: `npm run test` (vitest) | 49 Dateien, 2153 Tests grün |
| Scratch-Kopie: `npm run build` | gebaut (nur die bekannte Chunk-Größen-Warnung) |
| Playwright `ci` über `scripts/e2e-wie-ci.sh` (inkl. axe) | 87 passed |
| Playwright `mobil` (inkl. 360-px-Prüfungen) | 39 passed |

Die Zahlen entsprechen dem Stand vom Basis-Commit `e844e5b` (vitest 2153, pytest 678, ci 87, mobil 39). Die drei Ledger-Commits berühren keinen Code.

## Decisions Made

- 06/WR-01 ist `skipped`: UAT 06 Test 1 steht auf pass, PROJECT.md:138 hält fest, dass die Beträge-Lesart der Fußnote die gedruckten 1,77 % ergibt und ein Vorzeichen-Zusatz nicht nötig ist. Die Kommentare zum Vorzeichen sind in 08-07 (`81fcd86`) und 08-10 (`507d787`) präzisiert (D-17).
- 05/IN-07 und 05/IN-09 zitieren auch Phase-7-Commits (`53b96ac`, `1ab6b4b`, `b29be89`, `f4fad93`), weil dort die Teilfixes landeten, wie der Plan es vorgibt. `git cat-file -e` akzeptiert alle zitierten Hashes.
- 05/WR-01 nennt 08-02, 08-04 und 08-07. Die Commits von 08-05 tragen die Id 06/IN-07, nicht 05/WR-01; die Steuergruppen auf den Leitfragen-Seiten sind unten als offener Punkt geführt, nicht als Fix von 05/WR-01.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 2 - Missing Critical] Fußtext in Ledger 05 nennt zusätzlich die zwei verdrängten Warnungen**
- **Found during:** Task 2 (Lektüre von `ce51941:…/05-REVIEW.md`)
- **Issue:** Die erste Review-Runde hatte nicht nur IN-01 bis IN-04, sondern auch WR-01 (Sankey-Beträge ohne „rd.“/„berechnet“) und WR-02 (Start-Satz zum größten Aufgabenbereich) unter Ids gemeldet, die die aktuelle Review wiederverwendet. Beide fehlten im Plantext, wären aber ebenfalls ohne Spur aus dem Ledger verschwunden.
- **Fix:** Der Absatz nennt sie mit Stand: im Code erledigt (`GeldflussKnoten.gerundet/berechnet` in `lib/geldfluss.ts`, Start-Satz „Ohne die Weitergabe an Kreis und Land …“ in `StartPage.vue`).
- **Files modified:** `05-REVIEW-DISPOSITION.md`
- **Verification:** Task-2-Verify, Prüfung per grep gegen den Code
- **Committed in:** `aae3f13`

---

**Total deviations:** 1 auto-fixed (1 Rule 2)
**Impact on plan:** Nur eine vollständigere Aufzeichnung; keine Änderung am Ledger-Format, an `total` oder an anderen Zeilen.

## Issues Encountered

- Der Voll-pytest läuft im Worktree ohne `app/node_modules`; der Port-Test `test_port_wie_format_ts` wurde deshalb übersprungen und mit einer vorübergehend gesetzten Symlink-`node_modules` aus der Scratch-Kopie separat grün gefahren (Symlink danach entfernt, nichts davon liegt im Index).
- Der Lighthouse-Lauf (`scripts/lighthouse-a11y.sh`) war optional und wurde nicht ausgeführt.

## Offene Punkte für den Nutzer

1. **Vier (eigentlich sechs) durch Id-Wiederverwendung verdrängte Befunde der ersten Review-Runde von Phase 5 (`ce51941`).** Sie gehören nicht zu den 28 Befunden der Phase 8 und wurden in keinem Plan behoben; sie stehen im Fußtext von `05-REVIEW-DISPOSITION.md`. Stand im Code am Ende der Phase 8:
   - `-0 €` / `-0 %` aus `proKopf` und `Intl` (`lib/berechnung.ts:13`): vorhanden, aber ohne Datenfall im Jahrgang 2026 (latent, tritt mit dem nächsten Jahrgang auf, wenn ein Zuschussbedarf unter etwa 5.870 € negativ wird). Fix wäre `+ 0` auf dem gerundeten Wert.
   - Festes Superlativ „Der größte Einzelposten ist die Weitergabe an Kreis und Land“ in `KreisumlageCallout.vue:50`: vorhanden, in jedem Jahr wahr, aber nicht aus Daten abgeleitet oder getestet.
   - „PDF-Seite“ im Singular bei mehreren Seiten in `ErklaerText.vue:29` (`quelle_seiten.join(', ')`): vorhanden.
   - Weiterleitungs-Watcher in jedem `useJahr`-Aufruf (`lib/jahr.ts:114`): vorhanden, konvergiert, aber redundant.
   - Die beiden verdrängten Warnungen (Sankey ohne „rd.“/„berechnet“, Start-Satz) sind im Code erledigt.
   Entscheidung für den Nutzer: einzeln beheben (eigene kleine Pläne oder `/gsd-quick`), bewusst belassen oder in den Backlog.
2. **Etikett „berechnet“ für Steuergruppen auf den Leitfragen-Seiten (aus 08-05).** Die Gruppensummen wie „Grundsteuer (A+B)“ in `lib/geldfluss.ts:161/165` (Seiten `/geldfluss`, `/einnahmen`) tragen `berechnet: false`, `geldfluss.test.ts:169-178` sichert das ab. Das liegt außerhalb von D-12 (nur Kontextseiten) und wurde unverändert gelassen. Der Rest „Übrige Steuern“ ist dagegen `berechnet: true`. Soll die Summe ebenfalls „berechnet“ heißen, ändert das Code und diesen Test.
3. **Mensch-Check A1 aus 08-06:** Sagt ein Screenreader (VoiceOver oder NVDA) den Namen des Tabellenrahmens bei 360 px auf `/ausgaben` einmal oder zweimal an?
4. **Optional:** Lighthouse-Barrierefreiheit ≥ 95 über `scripts/lighthouse-a11y.sh`.
5. **Aus 08-01 für den nächsten Jahrgang:** Datenschlüssel in den Texten tragen noch feste Jahre (z. B. `…schluesselzuweisung.2025`) und müssen beim nächsten Jahrgang umgeschrieben werden.

## User Setup Required

None - no external service configuration required.

## Known Stubs

None. Diese Änderung berührt nur Ledger-Dateien.

## Next Phase Readiness

- Phase 9 (Audit) kann sich auf die drei Ledger stützen: kein Befund steht mehr auf `open`, jede Zeile nennt Beleg oder Grund.
- Die offenen Punkte oben sind Entscheidungen des Nutzers, keine Blocker für den Phasenabschluss.

## Self-Check: PASSED

- Ledger 01, 05, 06 vorhanden und je mit `open: 0` (grep geprüft).
- Commits `3df6637`, `aae3f13`, `0ec7bc2` liegen im Branch.
- Alle in den Ledgern zitierten Hashes stammen aus `git log` dieses Zweigs und sind per `git cat-file -e` bzw. als Vorfahren von HEAD auflösbar.

---
*Phase: 08-fixes-und-triage*
*Completed: 2026-10-07*
