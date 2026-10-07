---
phase: 06-kontext-seiten
plan: 01
subsystem: pipeline-data
tags: [pipeline, manuelle-daten, regel-5, meta-json, hsk, vorbericht]

requires:
  - phase: 04-manuelle-daten
    provides: kita_zuschuesse.csv-Muster, Regel 5, meta.json mit vorbericht_werte
  - phase: 05-einnahmen-investitionen
    provides: Einjahrestabellen-Muster (investitionszuwendungen), Regel-5-Erweiterungen
provides:
  - "daten/manuell/zuschuesse_lfd_zwecke.csv: acht Einzelzuschüsse und Gesamtzeile 120 T€ (Vorbericht S. 47)"
  - "haushalt.json vorbericht.zuschuesse_lfd_zwecke direkt nach kita_zuschuesse"
  - "Regel-5-Kreuzprüfung Gesamtzeile gegen Transferposten zuschuesse_laufende_zwecke"
  - "meta.json vorbericht_werte.hsk_schwelle_ein_jahr (25 %) und hsk_schwelle_zwei_jahre (5 %), Quelle S. 23"
affects: [06-02, 06-03, 06-04, rat-seite, entwicklung-seite]

actuals:
  tokens: 8000
  tasks: 3
  commits: 5
plan_head_before: 724fa45bf051bed5c07a034bac3e8560379aaa70
plan_head_after: 5d68b629a5dc27d6ffce4f3523f637e65ce9b164

tech-stack:
  added: []
  patterns:
    - "Gemeinsamer Regel-5-Helfer für Einjahrestabellen gegen einen Transferposten (Kita und lfd. Zwecke)"
    - "Sichtbarmachen geprüfter Punkte im Test über monkeypatch von TOLERANZ_EURO = -1"

key-files:
  created:
    - daten/manuell/zuschuesse_lfd_zwecke.csv
  modified:
    - daten/manuell/README.md
    - daten/manuell/meta.json
    - pipeline/ostbevern/schema.py
    - pipeline/ostbevern/app_daten.py
    - pipeline/ostbevern/pruefung.py
    - pipeline/tests/test_app_daten.py
    - pipeline/tests/test_manuell.py
    - app/src/data/haushalt.json
    - daten/pruefberichte/konsistenz.md

key-decisions:
  - "Kita- und lfd.-Zwecke-Kreuzprüfung teilen sich einen privaten Helfer; Kita-Fehlermeldungen und Pruefpunkt-Felder bleiben unverändert"
  - "HSK-Schwellen als ganze Prozentpunkte mit Seite 23 und Anmerkung mit dem Vorbericht-Wortlaut; die App zitiert nur und bewertet nichts"
  - "posten_name der JeKits-Zeile folgt dem gedruckten Wortlaut 'Eigenanteil JeKits-Pauschale an die Schule für Musik', der vom Plan vorgegebene Schlüssel bleibt"

patterns-established:
  - "Neue Einjahres-Vorberichtstabelle: CSV, Pfadkonstante in schema.py, Eintrag in vorbericht_quellen (app_daten) und im Loader von pruefe_alles, Ausnahme in _NUR_HAUSHALTSJAHR_CSVS"

requirements-completed: [RAT-03, ENTW-03]

coverage:
  - id: D1
    description: "Die acht Einzelzuschüsse aus S. 47 stehen geprüft in haushalt.json und ergeben 120 T€ wie Gesamtzeile und Transferposten"
    requirement: RAT-03
    verification:
      - kind: unit
        ref: "pipeline/tests/test_app_daten.py#test_zuschuesse_lfd_zwecke_in_haushalt_json"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_manuell.py#test_regel5_lfd_zwecke_gleich_transferposten"
        status: pass
    human_judgment: false
  - id: D2
    description: "Manipulierte Gesamtzeile oder manipulierter Einzelposten oder fehlender Transferposten lassen Regel 5 rot werden bzw. brechen ab"
    requirement: RAT-03
    verification:
      - kind: unit
        ref: "pipeline/tests/test_manuell.py#test_regel5_lfd_zwecke_erkennt_abweichung"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_manuell.py#test_regel5_lfd_zwecke_einzelposten_tippfehler"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_manuell.py#test_regel5_lfd_zwecke_fehlender_transferposten_bricht_ab"
        status: pass
    human_judgment: false
  - id: D3
    description: "HSK-Schwellen 25 % und 5 % mit Quelle S. 23 als meta.json-Werte, ausgeliefert in haushalt.json"
    requirement: ENTW-03
    verification:
      - kind: unit
        ref: "pipeline/tests/test_manuell.py#test_meta_hsk_schwellen"
        status: pass
    human_judgment: false
  - id: D4
    description: "Abschreibung der acht Posten und der HSK-Zitate stimmt mit dem gedruckten Wortlaut von S. 47 und S. 23 überein"
    verification: []
    human_judgment: true
    rationale: "Die Beträge wurden gegen den PDF-Text geprüft und per Regel 5 auf 120 T€ abgesichert; ob die Postenbezeichnungen für Laien passend gewählt sind, beurteilt ein Mensch"

duration: 35min
completed: 2026-10-06
status: complete
---

# Phase 6 Plan 01: Zuschüsse lfd. Zwecke und HSK-Schwellen Summary

**Einzelzuschüsse für laufende Zwecke (Vorbericht S. 47) als geprüfte Handtabelle bis in haushalt.json, mit Regel-5-Kreuzprüfung gegen den Transferposten, plus die zwei HSK-Schwellen (25 % / 5 %, S. 23) als meta.json-Werte mit Quelle.**

## Performance

- **Duration:** 35 min
- **Tasks:** 3 (Task 1 Tracer, Tasks 2 und 3 TDD)
- **Files modified:** 10 (1 neu)

## Accomplishments

- `zuschuesse_lfd_zwecke.csv` mit den acht Posten (23, 5, 8, 28, 23, 24, 8, 1 T€) und Gesamtzeile 120 T€, nur Haushaltsjahr (Wertart `ansatz`), Quelle 47. Der PDF-Text von S. 47 stimmte mit den Planzahlen überein.
- `haushalt.json` enthält `vorbericht.zuschuesse_lfd_zwecke` direkt nach `kita_zuschuesse`; Σ Posten = Gesamtzeile = Transferposten = 120.000 €.
- Regel 5: Stufe (a) über den Loader und neue Kreuzprüfung `transfer_lfd_zwecke` (Regel 5 jetzt 150 statt 148 geprüfte Werte, `konsistenz.md` bleibt Gesamtstatus grün).
- `meta.json` `hsk_schwelle_ein_jahr` (25) und `hsk_schwelle_zwei_jahre` (5), `prozent`, Quelle 23, Anmerkungen mit dem Vorbericht-Wortlaut und der Bezugsgröße.

## Task Commits

1. **Task 1: Tracer S. 47 bis haushalt.json** - `405fcf4` (feat)
2. **Task 2: Regel 5 lfd. Zwecke** - RED `d018f1e` (test), GREEN `fc73bc6` (feat)
3. **Task 3: HSK-Schwellen** - RED `94e4cfc` (test), GREEN `5d68b62` (feat)

**Plan metadata:** folgt als docs-Commit (SUMMARY.md). `commits: 5` zählt die fünf Task-Commits ohne diesen Metadaten-Commit.

## Tracer-Gate

Nach Task 1 wurde die `<verify>`-Kette erneut durchgeführt (alle.py, JSON-Assertion `ok 120000`, test_app_daten und test_manuell: 82 passed) und erst danach mit den Erweiterungen begonnen.

## TDD Gate Compliance

Task 2: RED (`d018f1e`) scheiterte an Assertions (Regel 5 blieb grün bei manipulierten Daten, Punkt `transfer_lfd_zwecke` fehlte); der Test für den fehlenden Transferposten scheiterte am nicht vorhandenen Helfer (AttributeError), was dem geplanten Verhalten entspricht. GREEN `fc73bc6`. Task 3: RED (`94e4cfc`, KeyError auf den fehlenden Schlüssel), GREEN `5d68b62`. Kein separater REFACTOR-Commit: die Zusammenführung der Kita-Prüfung in den gemeinsamen Helfer erfolgte im GREEN-Commit, Kita-Tests blieben unverändert grün.

## Files Created/Modified

- `daten/manuell/zuschuesse_lfd_zwecke.csv` - neun Zeilen aus S. 47
- `daten/manuell/README.md` - Abschnitt zur neuen Tabelle, HSK-Schwellen unter meta.json
- `daten/manuell/meta.json` - zwei neue `vorbericht_werte`
- `pipeline/ostbevern/schema.py` - `ZUSCHUESSE_LFD_ZWECKE_CSV`
- `pipeline/ostbevern/app_daten.py` - Eintrag in `vorbericht_quellen` nach `kita_zuschuesse`
- `pipeline/ostbevern/pruefung.py` - `REGEL5_LFD_ZWECKE_POSTEN`, gemeinsamer Helfer, `_pruefe_regel5_lfd_zwecke_gegen_transfer`, Loader-Eintrag, Aufruf
- `pipeline/tests/test_app_daten.py`, `pipeline/tests/test_manuell.py` - neue und erweiterte Tests
- `app/src/data/haushalt.json`, `daten/pruefberichte/konsistenz.md` - regeneriert

## Decisions Made

Siehe key-decisions. Besonders: gemeinsamer Helfer statt Geschwisterfunktion, weil die Kita-Meldungen identisch bleiben konnten.

## Deviations from Plan

None - plan executed exactly as written. Hinweis: Der Test `test_regel5_lfd_zwecke_gleich_transferposten` macht den geprüften Punkt über `TOLERANZ_EURO = -1` (monkeypatch) sichtbar, weil geprüfte, grüne Punkte sonst nirgends ausgegeben werden. Der Tracer-Verify-Befehl mit `S=$(mktemp -d) ... tar` der Task 3 wurde in einer gleichwertigen Schrittfolge ausgeführt (Scratch-Kopie von `app/` mit Linux-`node_modules` aus dem schreibgeschützten Install statt `npm ci`, gleiche Lockfile).

## Issues Encountered

None.

## Known Stubs

None.

## Threat Flags

None. Keine neue Angriffsfläche; T-06-01 und T-06-02 sind durch Regel 5 bzw. `test_meta_hsk_schwellen` abgedeckt.

## Verification

- `uv run --directory pipeline pytest -q`: 535 passed (mit temporär verlinktem Linux-`app/node_modules`, vor dem Commit entfernt).
- `ruff check .` und `ruff format --check .`: grün.
- App-Kette in Scratch-Kopie: type-check, lint, format:check, test (1031 passed), build: grün.
- Reproduzierbarkeitsgate: `alle.py --jahr 2026` hinterlässt weder Diff noch untracked Pfade unter `daten` und `app/src/data`.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Die Daten für RAT-03 (`vorbericht.zuschuesse_lfd_zwecke`) und ENTW-03 (`meta.vorbericht_werte.hsk_schwelle_*`) sind vorhanden; Folgepläne können sie in App und Texten verwenden. Die Textschlüssel `meta.vorbericht_werte.hsk_schwelle_*` tauchen in `texte.json` erst auf, wenn ein Text sie referiert (Plan 06-04).

## Self-Check: PASSED

---
*Phase: 06-kontext-seiten*
*Completed: 2026-10-06*
