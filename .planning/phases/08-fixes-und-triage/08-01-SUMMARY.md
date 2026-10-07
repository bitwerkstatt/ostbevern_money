---
phase: 08-fixes-und-triage
plan: 01
subsystem: texte
tags: [pipeline, texte, platzhalter, jahreszahlen, vue, vitest, pytest]

requires:
  - phase: 05
    provides: Platzhalter-Vertrag der Erklärtexte (pruefe_text, texte.json, istJahrneutral)
provides:
  - Jahresregel in pruefe_text (getippte Jahreszahl 1900-2099 ist ein Fehler)
  - pruefe_titel für Abschnittstitel
  - relative Jahres-Schlüssel jahr.vorvorjahr, jahr.haushaltsjahr_plus_1, jahr.haushaltsjahr_plus_2
  - feste Ereignisjahre jahr.fest_JJJJ (festes_jahr, loese_auf, vorschau)
  - istJahrneutral ignoriert jahr.*-Platzhalter
affects: [naechster Jahrgang, erklaerungen.md, texte.json]

actuals:
  tokens: 14000
  tasks: 2
  commits: 4

tech-stack:
  added: []
  patterns:
    - "Jahreszahlen in Texten nur als {{jahr.…|jahr}}; feste Jahre aus dem Schlüsselnamen aufgelöst"

key-files:
  created: []
  modified:
    - pipeline/ostbevern/texte.py
    - pipeline/ostbevern/app_daten.py
    - pipeline/tests/test_texte.py
    - pipeline/tests/test_formatiere.py
    - daten/manuell/texte/erklaerungen.md
    - app/src/data/texte.json
    - app/src/lib/texte.ts
    - app/src/lib/__tests__/texte.test.ts

key-decisions:
  - "Relative Jahres-Schlüssel stehen immer in textwerte; feste Jahre jahr.fest_JJJJ werden nicht gespeichert, sondern aus dem Schlüsselnamen aufgelöst (kein Jahrgangswert im Code)"
  - "istJahrneutral: ein Text ist jahrneutral, wenn alle Platzhalter-Schlüssel mit jahr. beginnen; die Invariante in vitest und pytest verlangt für neutrale Texte nur jahr.fest_*"
  - "Im RED-Commit trägt texte.py ein Signatur-Skelett (abschnitt-Keyword, no-op pruefe_titel), damit der Import nicht scheitert und die Tests an der Aussage scheitern"

patterns-established:
  - "Fehlermeldung 'Handgetippte Jahreszahl' nennt Zahl, Abschnitt und den Platzhalter-Ausweg"

requirements-completed: [TXT-03]

coverage:
  - id: D1
    description: "pruefe_text lehnt getippte Jahreszahlen 1900 bis 2099 ab und nennt Zahl, Abschnitt und Platzhalter-Ausweg"
    requirement: TXT-03
    verification:
      - kind: unit
        ref: "pipeline/tests/test_texte.py#test_pruefe_text_lehnt_getippte_jahreszahl_ab"
        status: pass
    human_judgment: false
  - id: D2
    description: "Sieben Abschnitte nutzen Jahres-Platzhalter; der gerenderte 2026-Text und alle Nicht-jahr-Werte sind unverändert"
    requirement: TXT-03
    verification:
      - kind: other
        ref: "node-Vergleich gegen 0e7a642:app/src/data/texte.json (identisch: 21)"
        status: pass
    human_judgment: false
  - id: D3
    description: "Jahrneutrale Texte bleiben für jedes Jahr sichtbar (istJahrneutral ignoriert jahr.*)"
    requirement: TXT-03
    verification:
      - kind: unit
        ref: "app/src/lib/__tests__/texte.test.ts#istJahrneutral"
        status: pass
    human_judgment: false
  - id: D4
    description: "Titel laufen durch pruefe_titel (Platzhalter im Titel und getippte Jahre werden abgelehnt)"
    requirement: TXT-03
    verification:
      - kind: unit
        ref: "pipeline/tests/test_texte.py#test_pruefe_titel_lehnt_platzhalter_ab"
        status: pass
    human_judgment: false

duration: 8min
completed: 2026-10-07
status: complete
plan_head_before: 93b0a61fc741d1cbc53e63ca5d16feb2060305e6
plan_head_after: c27904b525a64ae3c81ad7ac81665be3db816605
commits: 4
---

# Phase 8 Plan 01: Jahreszahlen nur als Platzhalter Summary

**Jahreszahlen in den Erklärtexten sind nur noch `{{jahr.…|jahr}}`-Platzhalter (relative Schlüssel plus `jahr.fest_JJJJ`), `pruefe_text` und das neue `pruefe_titel` lehnen jede getippte Jahreszahl 1900-2099 ab, und die jahrneutralen Texte bleiben für jedes Jahr sichtbar.**

## Performance

- **Duration:** 8 min
- **Started:** 2026-10-07T18:16:40Z
- **Completed:** 2026-10-07T18:25:00Z
- **Tasks:** 2
- **Files modified:** 7

## Accomplishments

- Sieben Abschnitte (schluesselzuweisung, gewerbesteuer, kreisumlage, schulden, verpflichtungsermaechtigungen, ueberschuss_pb_11, ueberschuss_ruecklage) enthalten keine getippte Jahreszahl mehr; der gerenderte Text für 2026 ist Zeichen für Zeichen gleich, alle Nicht-jahr-Werte in `texte.json` und alle CSVs bleiben unverändert.
- `pruefe_text` hat keine Jahres-Ausnahme mehr; die Meldung beginnt mit „Handgetippte Jahreszahl“. `pruefe_titel` lehnt Platzhalter im Titel ab und wendet danach dieselbe Regel an.
- `istJahrneutral` ignoriert `jahr.*`-Platzhalter: `ueberschuss_ruecklage` und `ueberschuss_pb_11` sind für jedes Jahr sichtbar; Invariante in vitest und pytest, dass neutrale Texte nur `jahr.fest_*` nutzen.

## Task Commits

1. **Task 1: Jahres-Platzhalter von erklaerungen.md bis zur App (tracer)** - `7d4be31` (fix, 05/IN-10; regeneriert `texte.json`)
2. **Task 2: Jahresregel scharf schalten, Titel prüfen (TDD)**
   - RED: `57063a0` (test)
   - GREEN: `27e0be7` (fix, 05/IN-10)
3. **Folgefix Test-Helfer** - `c27904b` (fix, 05/IN-10)

**Plan metadata:** folgt als docs-Commit mit dieser SUMMARY.

## Files Created/Modified

- `pipeline/ostbevern/texte.py` - `festes_jahr`, relative Jahres-Schlüssel, Auflösung `jahr.fest_JJJJ`, Jahresregel in `pruefe_text`, `pruefe_titel`
- `pipeline/ostbevern/app_daten.py` - `pruefe_titel` je Abschnitt, `pruefe_text(..., abschnitt=...)`
- `pipeline/tests/test_formatiere.py` - `_pruefe_absaetze` löst `jahr.fest_JJJJ` über `festes_jahr` auf
- `pipeline/tests/test_texte.py` - Tests für `festes_jahr`, relative Jahre, Auflösung, Jahresregel, `pruefe_titel`; Invariante für jahrneutrale Texte
- `daten/manuell/texte/erklaerungen.md` - Jahres-Platzhalter statt getippter Jahre
- `app/src/data/texte.json` - regeneriert (beabsichtigter Diff, D-03)
- `app/src/lib/texte.ts` - `istJahrneutral` ignoriert `jahr.*`
- `app/src/lib/__tests__/texte.test.ts` - Sichtbarkeit und Invariante

## TDD Gate Compliance

- RED `57063a0`: acht Fälle scheitern an der geplanten Aussage (`Failed: DID NOT RAISE TexteFehler`, Ziel-Tests in `test_texte.py`); semantische Prüfung: die Tests liefen, scheiterten an der Jahresregel bzw. an `pruefe_titel`, nicht an Import oder Fixture. Ein erster Lauf ohne Skelett scheiterte beim Import (`ImportError`, INVALID_RED) und wurde nicht als RED gewertet; deshalb trägt der RED-Commit ein Signatur-Skelett in `texte.py`.
- GREEN `27e0be7`: alle Tests in `test_texte.py` und `test_app_daten.py` grün (143 passed).
- REFACTOR: keiner nötig.

## Decisions Made

- Relative Schlüssel stehen in `textwerte`, feste Jahre werden aus dem Schlüsselnamen aufgelöst (Annahme A4: keine Jahrgangswerte im Python-Code).
- Die Datenschlüssel in den Texten (zum Beispiel `…schluesselzuweisung.2025`) tragen weiter feste Jahre und müssen beim nächsten Jahrgang umgeschrieben werden (latente Abweichung laut RESEARCH Pattern 2, im Commit-Text von `7d4be31` vermerkt, D-02 ist gesperrt).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] test_formatiere kannte jahr.fest_JJJJ nicht**
- **Found during:** Plan-Verifikation (voller pytest-Lauf)
- **Issue:** `tests/test_formatiere.py::test_erklaerungen_rendern_korrekt` schlug mit `KeyError` fehl, weil `_pruefe_absaetze` jeden Platzhalter in `werte` nachschlug; `jahr.fest_JJJJ` steht aber nicht in `werte`.
- **Fix:** Der Helfer löst feste Jahre über `festes_jahr` auf.
- **Files modified:** `pipeline/tests/test_formatiere.py` (nicht in `files_modified` des Plans)
- **Verification:** `pytest tests/test_formatiere.py` 22 passed, 1 skipped (der Node-Port-Test braucht `app/node_modules`, in diesem Worktree nicht vorhanden)
- **Committed in:** `c27904b`

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Folge der Umstellung der Texte, nur ein Test-Helfer; kein Scope Creep. Das Signatur-Skelett im RED-Commit ist eine Umsetzungsentscheidung innerhalb von Task 2, keine Abweichung.

## Issues Encountered

None.

## Known Stubs

None.

## Threat Flags

None - keine neue Angriffsfläche; T-08-01 bis T-08-03 sind durch `pruefe_titel`, die Jahresregel und den engen `festes_jahr`-Resolver gemindert.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Bereit für die weiteren Pläne von Phase 8. `alle.py --jahr 2026` ist nach `7d4be31` byte-identisch; Prüfregeln 1-10 grün.

## Self-Check: PASSED

- `pipeline/ostbevern/texte.py`, `daten/manuell/texte/erklaerungen.md`, `app/src/lib/texte.ts`, `app/src/data/texte.json` vorhanden; Commits `7d4be31`, `57063a0`, `27e0be7`, `c27904b` im Zweig. Verifikation: voller pytest (668 passed vor dem Folgefix, der eine Fehlschlag ist behoben, 1 Skip wegen fehlender `app/node_modules`), vitest 1973 passed, type-check, lint und format:check im Scratch-Copy grün, ruff grün.

---
*Phase: 08-fixes-und-triage*
*Completed: 2026-10-07*
