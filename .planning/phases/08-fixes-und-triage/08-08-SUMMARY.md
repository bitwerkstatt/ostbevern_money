---
phase: 08-fixes-und-triage
plan: 08
subsystem: pipeline
tags: [python, pytest, texte, konfiguration, ci-doku]

requires:
  - phase: 08-fixes-und-triage
    provides: "08-01 (texte.py/test_texte.py), 08-04, 08-05"
provides:
  - "TexteFehler statt ZeroDivisionError in allgemeine_ruecklage_rueckgang_bis_letztes_jahr (06/IN-08)"
  - "Glossar-Invariante absaetze[0] ohne Platzhalter in lies_glossar (05/IN-11 c)"
  - "pdf_relativ in alle.py einmal berechnet (01/IN-02)"
  - "Nicht-negativ-Pruefung fuer anzahlen.* in lade_jahrgang (01/IN-04)"
  - "CLAUDE.md-CI-Block mit Reproduzierbarkeitspruefung und Playwright-Schritt, ci.yml-Kopfkommentar aktuell (05/IN-11 a, b)"
affects: [08-12 Triage-Dispositionen]

actuals:
  tokens: 9000
  tasks: 3
  commits: 5

plan_head_before: d7e46f410d0503f7ae5b21d85919376c55857325
plan_head_after: 28462a75a581817714cac230a0163fe20a6ef483

tech-stack:
  added: []
  patterns:
    - "Typisierte Fachfehler (TexteFehler, KonfigurationsFehler) statt roher Python-Ausnahmen"

key-files:
  created: []
  modified:
    - pipeline/ostbevern/texte.py
    - pipeline/tests/test_texte.py
    - pipeline/alle.py
    - pipeline/ostbevern/konfiguration.py
    - pipeline/tests/test_konfiguration.py
    - .claude/CLAUDE.md
    - .github/workflows/ci.yml

key-decisions:
  - "Glossar-Testfixture _GUELTIGES_GLOSSAR: Begriff B hat nun zwei Absaetze (Platzhalter erst im zweiten), damit die neue Invariante die gueltige Fixture nicht verwirft"
  - "anzahlen.pdf_seiten = 0 wird nicht als erlaubt getestet: 0 ist dort ohnehin durch die Seitenbereichspruefung unzulaessig; 0 bleibt fuer produktbereiche und produkte erlaubt"

requirements-completed: [TRI-04]

coverage:
  - id: D1
    description: "Formel allgemeine_ruecklage_rueckgang_bis_letztes_jahr wirft bei Anfangsstand 0 TexteFehler mit Formelnamen"
    requirement: TRI-04
    verification:
      - kind: unit
        ref: "pipeline/tests/test_texte.py#test_allgemeine_ruecklage_rueckgang_bei_anfangsstand_null_ist_texte_fehler"
        status: pass
    human_judgment: false
  - id: D2
    description: "lies_glossar lehnt Platzhalter im ersten Absatz ab; echtes Glossar erfuellt die Invariante"
    requirement: TRI-04
    verification:
      - kind: unit
        ref: "pipeline/tests/test_texte.py#test_lies_glossar_platzhalter_im_ersten_absatz_bricht_ab"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_texte.py#test_lies_glossar_echtes_glossar_erfuellt_die_invariante"
        status: pass
    human_judgment: false
  - id: D3
    description: "lade_jahrgang lehnt negative anzahlen.* ab, 0 bleibt fuer produktbereiche/produkte erlaubt"
    requirement: TRI-04
    verification:
      - kind: unit
        ref: "pipeline/tests/test_konfiguration.py#test_negative_anzahl_wird_abgelehnt"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_konfiguration.py#test_anzahl_null_bleibt_erlaubt"
        status: pass
    human_judgment: false
  - id: D4
    description: "alle.py berechnet den relativen PDF-Pfad einmal"
    requirement: TRI-04
    verification:
      - kind: unit
        ref: "pipeline/tests/test_alle.py (Meldung PDF nicht gefunden)"
        status: pass
    human_judgment: false
  - id: D5
    description: "CLAUDE.md-CI-Block und ci.yml-Kopfkommentar beschreiben den aktuellen Stand; keine Nicht-Kommentarzeile von ci.yml geaendert"
    requirement: TRI-04
    verification:
      - kind: other
        ref: "cmp der Nicht-Kommentarzeilen von ci.yml (HEAD vs. Arbeitskopie) = identisch; grep auf die neuen CLAUDE.md-Zeilen"
        status: pass
    human_judgment: true
    rationale: "Inhaltliche Richtigkeit der Dokumentationsformulierung ist nicht durch einen Test belegt"

duration: 40min
completed: 2026-10-07
status: complete
---

# Phase 8 Plan 08: Kleine Pipeline- und Doku-Befunde Summary

**Typisierte Fehler fuer Division durch 0 (06/IN-08) und negative Jahrgangs-Anzahlen (01/IN-04), Glossar-Invariante absaetze[0] (05/IN-11), einmaliges pdf_relativ (01/IN-02) sowie aktualisierter CI-Block in CLAUDE.md und ci.yml-Kopfkommentar, mit byte-identischer Pipeline-Ausgabe.**

## Performance

- **Duration:** ca. 40 min (davon rund 6 min Voll-pytest)
- **Tasks:** 3
- **Files modified:** 7

## Accomplishments

- `_allgemeine_ruecklage_rueckgang_bis_letztes_jahr` wirft bei Anfangsstand 0 einen `TexteFehler`, der den Formelnamen nennt (06/IN-08).
- `lies_glossar` bricht ab, wenn der erste Absatz eines Begriffs einen Platzhalter enthaelt; das echte Glossar (27 Begriffe) erfuellt die Invariante (05/IN-11 c).
- `lade_jahrgang` lehnt negative `anzahlen.pdf_seiten`, `produktbereiche`, `produkte` mit `KonfigurationsFehler` ab (01/IN-04, T-08-13).
- `alle.py` berechnet `pdf_relativ` einmal vor der `is_file()`-Pruefung (01/IN-02).
- CLAUDE.md-Block „CI lokal nachstellen“ enthaelt Reproduzierbarkeitspruefung und Playwright-Schritt; ci.yml-Kopf nennt das Repository `github.com/bitwerkstatt/ostbevern_money` (05/IN-11 a, b).

## Task Commits

1. **Task 1 (Tracer): 06/IN-08 + 05/IN-11 c** - `c1da62e` (fix)
2. **Task 2 (TDD): 01/IN-04 RED** - `35b3d51` (test); **GREEN** - `4c105ff` (fix); **01/IN-02** - `c18a032` (refactor)
3. **Task 3: 05/IN-11 a, b** - `28462a7` (docs)

Tracer-Gate nach Task 1: pytest `test_texte.py` (104 passed), ruff clean, `alle.py --jahr 2026` mit leerem `git diff`/`git status` auf `daten`, `app/src/data`, `app/public/quellen` - „Tracer verified end-to-end - expanding“.

## Files Created/Modified

- `pipeline/ostbevern/texte.py` - Guard fuer `anfang == 0`, Glossar-Invariante
- `pipeline/tests/test_texte.py` - Tests fuer beide Guards; Glossar-Fixture auf zwei Absaetze
- `pipeline/alle.py` - `pdf_relativ` einmal
- `pipeline/ostbevern/konfiguration.py` - Vorzeichenpruefung der Anzahlen
- `pipeline/tests/test_konfiguration.py` - parametrisierte Tests (negativ je Schluessel, 0 erlaubt)
- `.claude/CLAUDE.md` - CI-Block erweitert
- `.github/workflows/ci.yml` - nur Kopfkommentar

## Decisions Made

- Die Glossar-Fixture `_GUELTIGES_GLOSSAR` wurde angepasst (Begriff B mit zwei Absaetzen), weil sie sonst selbst die neue Invariante verletzt haette.
- `anzahlen.pdf_seiten = 0` wird nicht als gueltig getestet (die Seitenbereichspruefung lehnt es ohnehin ab); der Null-Fall gilt fuer `produktbereiche` und `produkte`.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Gueltige Glossar-Testfixture verletzte die neue Invariante**
- **Found during:** Task 1
- **Issue:** `_GUELTIGES_GLOSSAR` hatte bei Begriff B den Platzhalter im einzigen (ersten) Absatz.
- **Fix:** Begriff B in zwei Absaetze geteilt, Platzhalter im zweiten.
- **Files modified:** pipeline/tests/test_texte.py
- **Committed in:** c1da62e

**2. [Plan-Abweichung, Kriterium] Acceptance-Kriterium `grep -c "relative_to(PROJEKT_WURZEL)" pipeline/alle.py` = 1**
- **Issue:** Die Datei enthaelt vier weitere, fachfremde `relative_to(PROJEKT_WURZEL)`-Aufrufe (Zeilen 109, 120, 137, 167), sodass das woertliche Kriterium 5 liefert.
- **Einordnung:** Der Befund betrifft nur den PDF-Pfad; `grep -c "pdf_pfad.relative_to(PROJEKT_WURZEL)"` liefert 1. Die anderen Aufrufe wurden nicht angefasst (Scope).

**Total deviations:** 1 auto-fixed (Rule 1), 1 Kriterium-Praezisierung. **Impact:** keine Auswirkung auf Scope oder Daten.

## Issues Encountered

Keine. Voll-pytest: 677 passed, 1 skipped (`test_port_wie_format_ts`, da kein `app/node_modules/typescript` im Worktree - erwartet).

## Verification

- `uv run --directory pipeline pytest` (voll): 677 passed, 1 skipped
- `ruff check` und `ruff format --check`: sauber
- `alle.py --jahr 2026`: Pruefregeln gruen, `git diff --stat` auf `daten`/`app/src/data` leer, `git status --porcelain` auf `daten app/src/data app/public/quellen` leer (byte-identisch)
- ci.yml: Nicht-Kommentarzeilen mit `cmp` identisch zu HEAD vor der Aenderung

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Dispositionen fuer 01/IN-02, 01/IN-04, 05/IN-11, 06/IN-08 koennen in 08-12 als „fixed“ mit den obigen Commits eingetragen werden.

## Self-Check: PASSED

- Dateien vorhanden, Commits `c1da62e`, `35b3d51`, `4c105ff`, `c18a032`, `28462a7` im Branch; Arbeitsbaum nach `alle.py` sauber.

---
*Phase: 08-fixes-und-triage*
*Completed: 2026-10-07*
