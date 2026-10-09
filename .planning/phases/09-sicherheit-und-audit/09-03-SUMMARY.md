---
phase: 09-sicherheit-und-audit
plan: 03
subsystem: testing
tags: [ci-baseline, pytest, vitest, playwright, npm-audit, evidence]

requires:
  - phase: 09-sicherheit-und-audit
    provides: Code nach Welle 1 (Pläne 09-01 und 09-02)
provides:
  - "09-BASISLAUF.md: ein gepinnter, vollständiger Lauf der CI-Kette als gemeinsame Evidenz für die Re-Verifikationen"
affects: [09-04, 09-05, 09-06, 09-07, 09-08, 09-09, 09-10, 09-15]

actuals:
  tokens: 12000
  tasks: 2
  commits: 2

plan_head_before: 1d0df35da1842daec515b40dd62f8d918e240105
plan_head_after: c9f4883a6f250af2e5863d13bd78b91cfbce02e7
commits: 2

tech-stack:
  added: []
  patterns:
    - "Basislauf einmal, nicht siebenmal: ein Evidenzdokument mit head-Hash, das Verifier per git diff gegen den Code prüfen"

key-files:
  created:
    - .planning/phases/09-sicherheit-und-audit/09-BASISLAUF.md
  modified: []

key-decisions:
  - "Die volle pytest-Suite wurde nach einem Skip (fehlendes app/node_modules/typescript) mit installiertem node_modules wiederholt, damit pytest_skipped: 0 wahr ist"

requirements-completed: [AUD-02]

coverage:
  - id: D1
    description: "09-BASISLAUF.md hält einen vollständigen CI-Lauf (Pipeline, App-Scratch-Kopie, Playwright ci/mobil/texte) auf gepinntem head fest"
    requirement: AUD-02
    verification:
      - kind: other
        ref: "uv run --directory pipeline python alle.py --jahr 2026 && git diff --stat --exit-code -- daten app/src/data"
        status: pass
      - kind: other
        ref: "Frontmatter-Prüfung von 09-BASISLAUF.md (head 40 Hex, pytest_skipped 0, Zähler numerisch, Abschnitte vorhanden, git diff <head> HEAD leer)"
        status: pass
    human_judgment: false
  - id: D2
    description: "Verifikationsstatus der Phasen 01-08 und npm-audit-Zahlen als Eingabe für 09-04 bis 09-13"
    requirement: AUD-02
    verification: []
    human_judgment: true
    rationale: "Die Zahlen sind Eingabe für spätere Bewertungen; ob 4 hohe Entwicklungsfunde akzeptabel sind, entscheiden die Re-Verifikationspläne"

duration: 25min
completed: 2026-10-09
status: complete
---

# Phase 9 Plan 03: Basislauf Summary

**Ein gepinnter CI-Gesamtlauf (681 pytest-Tests ohne Skip, alle.py mit Regeln 1-10 grün und byte-identisch, 2162 Vitest-Tests, Playwright ci 89, mobil 41, texte 1) als gemeinsame Evidenz in 09-BASISLAUF.md**

## Performance

- **Duration:** 25 min (davon rund 12 min zwei volle pytest-Läufe)
- **Started:** 2026-10-09T06:00:00Z
- **Completed:** 2026-10-09T06:27:00Z
- **Tasks:** 2
- **Files modified:** 1 (neu: 09-BASISLAUF.md)

## Accomplishments

- Pipeline-Kette auf `head` 1d0df35: `uv sync --locked`, ruff check, ruff format --check grün; pytest `681 passed in 350.31s` ohne Skip; `alle.py --jahr 2026` mit Prüfregeln 1-10 grün (Zähler 6593, 7994, 114, 259, 150, 1964, 1152, 820, 12, 19) und „Veraltete Befunde: 0“; `git diff` über `daten` und `app/src/data` sowie `git status` über `daten`, `app/src/data`, `app/public/quellen` leer.
- App-Kette in der Scratch-Kopie: npm ci, type-check, lint, format:check, 2162 Vitest-Tests in 49 Dateien, Build; Playwright `ci` 89, `mobil` 41, `texte` 1 bestanden, mit den Testtiteln jedes Projekts in der Datei.
- Verifikationsstatus vor der Re-Verifikation: Phasen 01-07 `stale`, Phase 08 `passed`. npm audit: 0 Funde in Produktionsabhängigkeiten, 4 hohe Funde in Entwicklungsabhängigkeiten (Kette braces → micromatch → fast-glob → @vue/eslint-config-typescript).
- Abschnitt „Hinweise für die Verifier“ legt fest: nur lesende Prüfungen, kein alle.py, keine volle pytest-Suite, kein Playwright.

## Task Commits

1. **Task 1: Pipeline-Kette einmal fahren und als Evidenz mit head festhalten** - `323f962` (docs)
2. **Task 2: App-Kette, Playwright, Verifikationsstatus und npm audit festhalten** - `c9f4883` (docs)

**Plan metadata:** wird mit diesem SUMMARY committet (docs: complete plan)

## Files Created/Modified

- `.planning/phases/09-sicherheit-und-audit/09-BASISLAUF.md` - Gepinnte Lauf-Evidenz mit head, Zählern, Testtiteln, Statusübersicht und npm-audit-Zahlen

## Decisions Made

- Der erste pytest-Lauf ergab `680 passed, 1 skipped` (`tests/test_formatiere.py:463`, `test_port_wie_format_ts`, weil `app/node_modules/typescript` im frischen Worktree fehlt). Ein Skip widerspricht der Planvorgabe „zero skips“. Deshalb wurde `npm ci` in `app/` des Worktrees ausgeführt (Linux, `node_modules` ist gitignored) und die volle Suite erneut gefahren: `681 passed`. Beide Läufe sind in der Datei benannt; maßgeblich ist der zweite.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Fehlendes app/node_modules ließ einen Test überspringen**
- **Found during:** Task 1 (pytest)
- **Issue:** `test_port_wie_format_ts` übersprang sich ohne `app/node_modules/typescript`; der Plan verlangt `pytest_skipped: 0`.
- **Fix:** `npm ci` in `app/` des Worktrees (nur `node_modules`, gitignored), danach volle Suite erneut.
- **Files modified:** keine getrackten Dateien
- **Verification:** `681 passed`, keine `SKIPPED`-Zeile, `git status --porcelain -- pipeline app daten scripts .github` leer
- **Committed in:** 323f962 (dokumentiert in 09-BASISLAUF.md)

**2. [Plan-Hinweis] Playwright mobil und texte beim ersten Versuch parallel gestartet**
- **Found during:** Task 2
- **Issue:** Zwei Aufrufe liefen gleichzeitig auf derselben Scratch-Kopie.
- **Fix:** `texte` allein wiederholt (`1 passed`); die dokumentierte Zahl stammt aus dem Einzellauf. In der Datei vermerkt.
- **Committed in:** c9f4883

---

**Total deviations:** 1 auto-fixed (1 blocking), 1 Verfahrenshinweis
**Impact on plan:** Beide stützen die Evidenzintegrität, keine Änderung am Code.

## Issues Encountered

- `gsd-tools.cjs` liegt nur im Haupt-Checkout (`.claude/gsd-core` ist untracked); die Statusabfrage lief mit dessen absolutem Pfad, aber im Worktree als Arbeitsverzeichnis.
- Die Dauern von `uv sync` und ruff sind nur als „unter 1 s“ erfasst (Cache warm, ganze Sekunden).

## Known Stubs

None.

## Threat Flags

None - kein neuer Netzwerk-, Auth- oder Dateizugriffspfad; `uv sync --locked` und `npm ci` nur gegen die eingecheckten Lockfiles, keine Abhängigkeit hinzugefügt.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Die Re-Verifikationen 09-04 bis 09-10 können `09-BASISLAUF.md` zitieren; `head` ist 1d0df35da1842daec515b40dd62f8d918e240105 und über `git diff --quiet <head> HEAD -- pipeline app daten scripts .github` prüfbar.
- Offene Bewertung für die Audit-Pläne: vier hohe npm-Funde in Entwicklungsabhängigkeiten, sieben Phasen mit Status `stale`.

## Self-Check: PASSED

- 09-BASISLAUF.md vorhanden, Frontmatter vollständig, 131 Testtitel (89, 41, 1) entsprechen den e2e-Zählern.
- Commits 323f962 und c9f4883 liegen auf dem Branch.

---
*Phase: 09-sicherheit-und-audit*
*Completed: 2026-10-09*
