---
phase: 02-kernzahlen
plan: 03
subsystem: pipeline
tags: [pdfplumber, polars, pytest, formula-chain, befunde]

requires:
  - phase: 02-01
    provides: "ZEILEN-Wörterbuch (gesamtergebnisplan), plaene.lies_plantabelle (generische x-Koordinaten-Parsing), pruefung.pruefe_alles Regel 4 (B.1), schema.PLAN_SPALTEN"
provides:
  - "ostbevern/zeilen.py: ZEILEN['gesamtfinanzplan'] (41 Zeilen) und FORMELN (alle vier Plantypen, inkl. Dokumentation warum GEP Z.33 und TFP Z.09/16 keine Formel haben)"
  - "ostbevern/plaene.py: extrahiere_plaene extrahiert jetzt auch den Gesamtfinanzplan (finanzplan.csv, 7 Spalten inkl. VE, doppelte '2026'-Kopfzeile über x-Position aufgelöst)"
  - "ostbevern/pruefung.py: Planwerte (Formelketten-Resolver mit Memoisierung und Zyklus-Schutz), Regel 1 (Zeilenformeln, 118 Werte), Regel 4 erweitert um B.2/Satzung §1-3 (147 Werte gesamt), SATZUNG_FORMELN, Befund/Abgleich-Dataclasses, lies_befunde, gleiche_befunde_ab, _wende_befunde_an"
  - "daten/aufbereitet/finanzplan.csv (287 Zeilen GESAMT inkl. VE-Spalte)"
  - "daten/pruefberichte/befunde.md (Schlüsseltabelle, aktuell leer, plus Beobachtungen ohne Prüfregel)"
  - "daten/pruefberichte/konsistenz.md (Gesamtstatus-Zeile, Übersicht mit Bekannte-Befunde-Spalte, Abweichungen/Bekannte Befunde/Veraltete Befunde)"
affects: [02-04-teilplaene, 02-05-weitere-pruefregeln, 04-app-json]

actuals:
  tokens: 24360
  tasks: 3
  commits: 6
  plan_head_before: 25dca42f7c5b41b2fef9b0b7d14017f096523692
  plan_head_after: 49154166ce4e8b31009d4b43ddc85376d332b416

tech-stack:
  added: []
  patterns:
    - "RED-Stage-Stubs für TDD-Aufgaben: minimale, naive Implementierungen (FORMELN={}, Planwerte mit reinem Wörterbuch-Lookup ohne Formelkette, lies_befunde das nur Dateiexistenz prüft) halten das Modul importierbar, sodass neue Tests an echten Assertions scheitern statt an Import-/Collection-Fehlern"
    - "Formelketten-Resolver (Planwerte) mit Memoisierung und Zyklus-Schutz, von Regel 1 UND Regel 4 genutzt — D-11 (fehlende Zeile = 0) greift ausschließlich über einen FORMELN-Eintrag, nie durch stilles Weglassen"
    - "Ein globaler Befunde-Abgleich (_wende_befunde_an) über alle Regelergebnisse hinweg, danach pro Regel anhand punkt.regel zurückgeteilt — ein Befund mit falscher regel-Spalte kann keine fremde Regel abdecken, da der Schlüssel das regel-Feld einschließt"

key-files:
  created:
    - daten/pruefberichte/befunde.md
    - daten/aufbereitet/finanzplan.csv
  modified:
    - pipeline/ostbevern/zeilen.py
    - pipeline/ostbevern/plaene.py
    - pipeline/ostbevern/pruefung.py
    - pipeline/02_plaene_extrahieren.py
    - pipeline/06_pruefen.py
    - pipeline/tests/test_plaene.py
    - pipeline/tests/test_pruefung.py
    - daten/pruefberichte/konsistenz.md

key-decisions:
  - "Regel 4 (B.1/B.2/Satzung) von direkten CSV-Filtern auf Planwerte.wert umgestellt, obwohl das für GESAMT-Zeilen heute keinen Unterschied macht (alle Zeilen sind gedruckt) — damit die B.3-Teilplan-Prüfungen in 02-05 denselben Formelketten-Resolver für fehlende Zwischenzeilen nutzen können, ohne Regel 4 ein zweites Mal umzubauen"
  - "Befunde-Abgleich läuft einmal global über alle Pruefpunkt aus Regel 1 UND Regel 4 (_wende_befunde_an), dann pro Regelergebnis anhand punkt.regel zurückgeteilt — einfacher als ein Abgleich pro Regel und trotzdem eindeutig, da der Schlüssel das regel-Feld einschließt"
  - "02_plaene_extrahieren.py musste angepasst werden, weil extrahiere_plaene jetzt ein Tupel (Ergebnisplan-, Finanzplan-Ergebnis) statt eines einzelnen ExtraktionsErgebnis zurückgibt — nicht in der ursprünglichen files_modified-Liste des Plans, aber nötig, damit der CLI-Einstieg weiter funktioniert (Deviation, siehe unten)"

requirements-completed: [EXTR-05, PRUEF-01, PRUEF-04, PRUEF-09]

coverage:
  - id: D1
    description: "Gesamtfinanzplan inkl. VE-Spalte wird vollständig extrahiert (287 Zeilen, 41 Zeilen x 7 Spalten), die doppelte '2026'-Kopfzeile (Ansatz/VE) wird über x-Position statt Text aufgelöst"
    requirement: "EXTR-05"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_plaene.py#test_gesamtfinanzplan_zeilen_entsprechen_woerterbuch"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_plaene.py#test_gesamtfinanzplan_trifft_sollwerte_b2"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_plaene.py#test_gesamtfinanzplan_falscher_spaltenkopf_bricht_ab"
        status: pass
      - kind: integration
        ref: "uv run --directory pipeline python 02_plaene_extrahieren.py --jahr 2026"
        status: pass
    human_judgment: false
  - id: D2
    description: "Regel 1 prüft über einen Formelketten-Resolver (Planwerte) jede gedruckte Summenzeile aller vier Plantypen; fehlende Zwischenzeilen (Pitfall 1) werden korrekt über die Kette hergeleitet statt als 0 fehlinterpretiert; grün mit 118 Werten (Gesamtergebnisplan 8x6, Gesamtfinanzplan 10x7)"
    requirement: "PRUEF-01"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_regel1_sollwerte_gesamtplaene_gruen"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_regel1_formelkette_fuer_fehlende_zwischenzeilen"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_regel1_toleriert_einen_euro_sonst_rot"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_regel1_keine_formel_fuer_nachrichtlich_zeile_33"
        status: pass
      - kind: integration
        ref: "uv run --directory pipeline python 06_pruefen.py --jahr 2026"
        status: pass
    human_judgment: false
  - id: D3
    description: "Regel 4 deckt Anhang B.1 (Gesamtergebnisplan), B.2 (Gesamtfinanzplan Ansatz/VE) und Satzung §1-3 ab; 147 Werte insgesamt, grün"
    requirement: "PRUEF-04"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_regel4_sollwerte_gesamtergebnisplan_gruen"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_regel4_sollwerte_gesamtfinanzplan_und_satzung_gruen"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_regel4_satzung_ohne_formel_bricht_ab"
        status: pass
    human_judgment: false
  - id: D4
    description: "befunde.md mit maschinenlesbarer Schlüsseltabelle (D-02); D-04 (veraltete Befunde) und D-05 (Betragstoleranz) sind erzwungen und getestet; konsistenz.md zeigt Gesamtstatus, Übersicht, Abweichungen, Bekannte und Veraltete Befunde (D-03); pytest und 06_pruefen.py scheitern bei veralteten oder nicht passenden Befunden (PRUEF-09)"
    requirement: "PRUEF-09"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_befund_deckt_abweichung_innerhalb_toleranz_ab"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_veralteter_befund_wenn_abweichung_nicht_mehr_passt"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_veralteter_befund_ohne_passende_abweichung"
        status: pass
      - kind: integration
        ref: "pipeline/tests/test_pruefung.py#test_veralteter_befund_macht_bericht_nicht_gruen"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_kaputte_schluesseltabelle_falsche_zellenzahl"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_kaputte_schluesseltabelle_abweichung_nicht_int"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_kaputte_schluesseltabelle_abweichung_zu_klein"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_kaputte_schluesseltabelle_leere_begruendung"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_kaputte_schluesseltabelle_fehlende_ueberschrift"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_kaputte_schluesseltabelle_fehlende_datei"
        status: pass
      - kind: integration
        ref: "pipeline/tests/test_pruefung.py#test_konsistenzbericht_listet_bekannten_befund"
        status: pass
    human_judgment: false

duration: 25min
completed: 2026-10-01
status: complete
---

# Phase 2 Plan 3: Gesamtfinanzplan, Regel 1 Formelkette, befunde.md Summary

**Gesamtfinanzplan inkl. VE-Spalte extrahiert, Regel 1 prüft alle vier Plantypen über einen memoisierten Formelketten-Resolver mit Zyklus-Schutz (118 Werte grün), Regel 4 deckt B.1/B.2/Satzung §1-3 ab (147 Werte grün), und befunde.md erzwingt D-02 bis D-05 mit strenger Schlüsseltabellen-Validierung.**

## Performance

- **Duration:** ~25 min (Commit-Spanne)
- **Tasks:** 3
- **Commits:** 6 (inkl. 1 Zwischenfix)
- **Files created:** 2
- **Files modified:** 8

## Accomplishments
- `daten/aufbereitet/finanzplan.csv` enthält den vollständigen Gesamtfinanzplan (287 Zeilen = 41 Zeilen x 7 Spalten inkl. VE); die doppelte „2026"-Kopfzeile (Ansatz/VE) wird korrekt über x-Position statt Text aufgelöst (EXTR-05)
- `Planwerte` löst Formelketten rekursiv mit Memoisierung und Zyklus-Schutz auf; Regel 1 prüft jede gedruckte Summenzeile aller vier Plantypen (118 Werte, grün) und leitet fehlende Zwischenzeilen korrekt her statt sie als 0 misszuinterpretieren (Research Pitfall 1, PRUEF-01)
- Regel 4 deckt jetzt Anhang B.1, B.2 und Satzung §1-3 vollständig ab (147 Werte, grün); `SATZUNG_FORMELN` bildet alle 12 Satzungs-Schlüssel auf Ergebnis-/Finanzplan-Formeln ab
- `befunde.md` erzwingt D-02 (maschinenlesbare Schlüsseltabelle), D-04 (veraltete Befunde sind Fehler) und D-05 (Betragstoleranz ±1€) mit strenger Validierung (10 Zellen, bekannte Ebene/Wertart, Ganzzahlen, |Abweichung| > 1, nicht-leere Begründung); `konsistenz.md` zeigt Gesamtstatus, Übersicht mit Bekannte-Befunde-Spalte, sowie Abweichungen/Bekannte Befunde/Veraltete Befunde (D-03)

## Task Commits

Jede Aufgabe wurde atomar committet:

1. **Task 1: Tracer — Gesamtfinanzplan end-to-end** - `3986b53` (feat)
2. **Task 2: Regel 1 Formelketten-Resolver** - `655e9d4` (test, RED) + `95efa90` (feat, GREEN)
3. **Task 3: befunde.md policy und Berichtslayout** - `6adf713` (test, RED) + `4915416` (feat, GREEN)

Zwischen Task 2 und Task 3: `f7641b8` (fix) — entfernt einen in Task 1 eingeschleusten `2026`-Literal aus `test_plaene.py`, gefunden bei der Vorbereitung von Task 3's eigenem Literal-Check.

_Kein REFACTOR-Commit nötig — die GREEN-Implementierungen blieben minimal und sauber._

## Files Created/Modified
- `pipeline/ostbevern/zeilen.py` - `ZEILEN["gesamtfinanzplan"]` (41 Zeilen), `FORMELN` für alle vier Plantypen
- `pipeline/ostbevern/plaene.py` - `extrahiere_plaene` extrahiert jetzt Ergebnis- UND Finanzplan (Tupel-Rückgabe)
- `pipeline/ostbevern/pruefung.py` - `Planwerte`, Regel 1, `SATZUNG_FORMELN`, `Befund`/`Abgleich`, `lies_befunde`, `gleiche_befunde_ab`, `_wende_befunde_an`, erweitertes Berichtslayout
- `pipeline/02_plaene_extrahieren.py` - an die Tupel-Rückgabe von `extrahiere_plaene` angepasst
- `pipeline/06_pruefen.py` - echot jetzt auch die Anzahl veralteter Befunde
- `pipeline/tests/test_plaene.py` - 3 neue Finanzplan-Tests, Literal-Fix
- `pipeline/tests/test_pruefung.py` - 16 neue Tests (Regel 1, Planwerte, Befunde), tmp-Path-Helfer um `befunde.md` erweitert
- `daten/aufbereitet/finanzplan.csv` - generiert (neu)
- `daten/pruefberichte/befunde.md` - neu angelegt (Schlüsseltabelle aktuell leer)
- `daten/pruefberichte/konsistenz.md` - regeneriert (neues Layout)

## Decisions Made
- Regel 4 nutzt jetzt `Planwerte.wert` statt direkter CSV-Filter — für GESAMT-Zeilen heute identisches Verhalten, bereitet aber die B.3-Teilplan-Prüfungen in 02-05 vor, die denselben Formelketten-Resolver für fehlende Zwischenzeilen brauchen
- Befunde-Abgleich läuft einmal global über alle Abweichungen aus Regel 1 und Regel 4, dann pro Regelergebnis zurückgeteilt — der Schlüssel enthält das `regel`-Feld, daher ist die Zuordnung eindeutig
- RED-Stage-Stubs (leeres `FORMELN`, naive `Planwerte`, dateiexistenz-prüfendes `lies_befunde`) halten die Module importierbar, sodass neue Tests an echten Assertions scheitern statt an Import-Fehlern — konsistent mit dem in 02-01 etablierten Muster

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `02_plaene_extrahieren.py` an neue Tupel-Rückgabe von `extrahiere_plaene` angepasst**
- **Found during:** Task 1
- **Issue:** `extrahiere_plaene` gibt jetzt `tuple[ExtraktionsErgebnis, ExtraktionsErgebnis]` zurück (Ergebnis- und Finanzplan), der CLI-Einstieg erwartete noch ein einzelnes Objekt
- **Fix:** Schleife über beide Ergebnisse, eine Echo-Zeile je Datei
- **Files modified:** `pipeline/02_plaene_extrahieren.py` (nicht in der ursprünglichen `files_modified`-Liste des Plans)
- **Verification:** `uv run --directory pipeline python 02_plaene_extrahieren.py --jahr 2026` läuft fehlerfrei durch, beide CSVs werden geschrieben
- **Committed in:** `3986b53` (Teil des Task-1-Commits)

**2. [Rule 1 - Bug] Hardcodiertes `2026`-Literal aus `test_plaene.py` entfernt**
- **Found during:** Vorbereitung von Task 3 (dessen eigenes Akzeptanzkriterium `grep -rnwE '2026|400|2353506|18443000' pipeline/tests` schlug fehl)
- **Issue:** `test_gesamtfinanzplan_trifft_sollwerte_b2` (aus Task 1 dieses Plans) verglich Spaltenköpfe gegen das Literal `2026` statt `STANDARD_JAHR`, ein Verstoß gegen die Projektkonvention „keine Jahrgangswerte in Tests"
- **Fix:** `2026` durch `STANDARD_JAHR` ersetzt, Kommentar umformuliert
- **Files modified:** `pipeline/tests/test_plaene.py`
- **Verification:** `grep -rnwE '2026|400|2353506|18443000' pipeline/tests` liefert keinen Treffer mehr; volle Suite bleibt grün
- **Committed in:** `f7641b8`

---

**Total deviations:** 2 auto-fixed (1 blockierend, 1 Bug)
**Impact on plan:** Beide Fixes waren für korrekte Funktion bzw. Einhaltung der Projektkonventionen notwendig. Kein Scope Creep — beide direkt durch die Arbeit an diesem Plan verursacht bzw. aufgedeckt.

## Issues Encountered
- Beim Entwurf von `test_konsistenzbericht_listet_bekannten_befund` zeigte sich, dass jede Manipulation einer B.1-Zeile am GESAMT-Niveau zwangsläufig in mindestens eine Regel-1-Formelzeile kaskadiert (da jede Zeile eines vollständig summierten Haushaltsplans irgendwo in der Formelkette auftaucht). Gelöst, indem der Test zwei zusammenpassende Befunde registriert (einen für Regel 4, einen für die kaskadierte Regel-1-Formelzeile) statt eine isolierte, nicht-kaskadierende Zeile zu suchen (die es in diesem Datenmodell nicht gibt).

## User Setup Required
None - keine externen Dienste erforderlich.

## Next Phase Readiness
- `ZEILEN`, `FORMELN`, `Planwerte`, `lies_befunde`, `gleiche_befunde_ab` stehen für Plan 02-04 (Teilpläne) bereit; Teilplan-Formeln (`teilergebnisplan`, `teilfinanzplan`) sind bereits in `FORMELN` vorhanden, auch wenn Teilplan-Zeilen erst in 02-04 extrahiert werden
- Regel 4 nutzt bereits `Planwerte.wert`, sodass die B.3-Teilplan-Sollwertprüfungen in 02-05 denselben Resolver für fehlende Zwischenzeilen (Pitfall 1) wiederverwenden können, ohne Regel 4 erneut umzubauen
- `befunde.md`s Schlüsseltabelle ist aktuell leer; falls 02-04/02-05 bekannte Abweichungen in Teilplänen aufdecken, können sie dort direkt mit Begründung und PDF-Seite ergänzt werden
- Keine Blocker für die nächsten Pläne dieser Phase

---
*Phase: 02-kernzahlen*
*Completed: 2026-10-01*
