---
phase: 02-kernzahlen
plan: 01
subsystem: pipeline
tags: [pdfplumber, polars, typer, pytest, toml, csv]

requires:
  - phase: 01-setup
    provides: "lade_jahrgang/lade_sollwerte, STANDARD_JAHR, PROJEKT_WURZEL, KonfigurationsFehler"
provides:
  - "ostbevern/pdf.py: einziger pdfplumber-Wrapper, 1-basierte zeilengruppierte Seiten mit x/y-Koordinaten"
  - "ostbevern/zahlen.py: vollständiger EXTR-01-Zahlenparser (dt. Format, U+2212-Minus, kein Wert, C/EUR, angeklebte Beträge)"
  - "ostbevern/zeilen.py: Zeilen-Wörterbuch Gesamtergebnisplan (33 Zeilen, D-12) + Label-Normalisierung"
  - "ostbevern/schema.py: zentrales CSV-Schema/IO für Plan-CSVs (D-21, D-22)"
  - "ostbevern/plaene.py: x-Koordinaten-Plantabellen-Parser mit D-08-Abbruch, extrahiere_plaene für Gesamtergebnisplan"
  - "ostbevern/pruefung.py: Regel 4 (Anhang B.1) gegen ergebnisplan.csv, konsistenz.md aus einer Implementierung (D-01)"
  - "02_plaene_extrahieren.py, 06_pruefen.py: dünne typer-CLIs"
  - "daten/aufbereitet/ergebnisplan.csv (198 Zeilen GESAMT), daten/pruefberichte/konsistenz.md (Regel 4 grün, 126 Werte)"
  - "2026_sollwerte.toml: Anhang B.1 vollständig, B.2, B.3 je PB, validiert durch erweitertes lade_sollwerte"
affects: [02-02-seitenklassifikation, 02-03-gesamtfinanzplan, 02-04-teilplaene, 02-05-weitere-pruefregeln, 04-app-json]

actuals:
  tokens: 21170
  tasks: 3
  commits: 5
  plan_head_before: 95df46bcd33e24dbb8cea37bd1460adeb81c9dd9
  plan_head_after: 24d942caf11d812413967910c3efde826b81d97f

tech-stack:
  added: []
  patterns:
    - "Ein ValueError-Subtyp pro neuem Modul mit einzeiligem deutschem Docstring (PdfFehler, PlaeneFehler, PruefungsFehler, SchemaFehler, ZahlenFehler)"
    - "pdf.py als einzige pdfplumber-Importstelle, analog zu konfiguration.py für tomllib"
    - "x-Koordinaten-Spaltenzuordnung (nächstes Jahreswort per x1-Abstand) statt Text-Splitting"
    - "D-01: eine Prüflogik (pruefe_alles), zwei Aufrufer (CLI + pytest), atomare Dateischreibung via tempfile+os.replace"

key-files:
  created:
    - pipeline/ostbevern/zahlen.py
    - pipeline/ostbevern/pdf.py
    - pipeline/ostbevern/zeilen.py
    - pipeline/ostbevern/schema.py
    - pipeline/ostbevern/plaene.py
    - pipeline/ostbevern/pruefung.py
    - pipeline/02_plaene_extrahieren.py
    - pipeline/06_pruefen.py
    - pipeline/tests/test_zahlen.py
    - pipeline/tests/test_plaene.py
    - pipeline/tests/test_pruefung.py
    - daten/aufbereitet/ergebnisplan.csv
    - daten/pruefberichte/konsistenz.md
  modified:
    - pipeline/ostbevern/konfiguration.py
    - pipeline/jahrgaenge/2026_sollwerte.toml
    - pipeline/tests/test_konfiguration.py

key-decisions:
  - "Nachrichtlich-Zeilen 29-33 des Gesamtergebnisplans werden ins Zeilen-Wörterbuch aufgenommen (kein D-08-Abbruch), aber von Regel 4 und Anhang B vollständig ausgenommen (Research Open Question 1)"
  - "trenne_angeklebten_betrag wird in plaene.py ausschließlich auf Wörter angewendet, deren x1 in der Betragsspaltenzone liegt — die Funktion selbst kennt keine Spaltenposition und würde sonst Labels wie 'AVüber800' fälschlich aufspalten"
  - "Die Betragszone eines Worts wird über x1 > x0 der ersten Jahresspalte bestimmt, die Spaltenzuordnung über den kleinsten x1-Abstand zur jeweiligen Jahresspalte (Toleranz: halber kleinster Spaltenabstand)"

requirements-completed: [EXTR-01, EXTR-04, PRUEF-04, PRUEF-09]

coverage:
  - id: D1
    description: "Tracer: Gesamtergebnisplan-Seite vollständig von PDF über Spaltenzuordnung und Zeilen-Wörterbuch nach ergebnisplan.csv extrahiert (198 Zeilen, gedrucktes Vorzeichen, Operator-Spalte, ist_summe, pdf_seite)"
    requirement: "EXTR-04"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_plaene.py#test_gesamtergebnisplan_zeilen_entsprechen_woerterbuch"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_plaene.py#test_gesamtergebnisplan_trifft_sollwerte_b1"
        status: pass
      - kind: integration
        ref: "uv run --directory pipeline python 02_plaene_extrahieren.py --jahr 2026"
        status: pass
    human_judgment: false
  - id: D2
    description: "Regel 4 vergleicht ergebnisplan.csv gegen Anhang B.1 (126 Werte, grün); konsistenz.md wird byte-identisch von 06_pruefen.py und pytest erzeugt"
    requirement: "PRUEF-04"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_regel4_sollwerte_gesamtergebnisplan_gruen"
        status: pass
      - kind: integration
        ref: "pipeline/tests/test_pruefung.py#test_konsistenzbericht_wird_geschrieben"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_konsistenzbericht_meldet_abweichung_ueber_einem_euro"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_pruefung.py#test_konsistenzbericht_toleriert_einen_euro"
        status: pass
    human_judgment: false
  - id: D3
    description: "Vollständiger EXTR-01-Zahlenparser (dt. Tausenderformat, U+2212-Minus, kein Wert, C/EUR-Zeichen, angeklebte Beträge) mit reinen String-Tests"
    requirement: "EXTR-01"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_zahlen.py (21 Testfunktionen, teils parametrisiert)"
        status: pass
    human_judgment: false
  - id: D4
    description: "Sollwertdatei hält Anhang B.1 (komplett), B.2, B.3 je PB; lade_sollwerte validiert alle neuen Tabellen vollständig und meldet fehlende Schlüssel/Felder"
    requirement: "PRUEF-09"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_konfiguration.py#test_lade_sollwerte_gibt_alle_tabellen_vollstaendig_zurueck"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_konfiguration.py#test_sollwertdatei_ohne_gesamtfinanzplan_meldet_schluessel"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_konfiguration.py#test_teilergebnisplaene_pb_eintrag_ohne_ordentliche_aufwendungen_meldet_feld"
        status: pass
      - kind: unit
        ref: "pipeline/tests/test_konfiguration.py#test_gesamtfinanzplan_ansatz_schluessel_ohne_zweistellige_zeile_wird_abgelehnt"
        status: pass
    human_judgment: false

duration: 60min
completed: 2026-10-01
status: complete
---

# Phase 2 Plan 1: Gesamtergebnisplan Tracer Summary

**PDF-Seite 62 läuft vollständig durch pdf.py -> plaene.py -> ergebnisplan.csv -> pruefung.py Regel 4 -> konsistenz.md (198 Zeilen, Regel 4 grün mit 126 B.1-Werten), mit vollständigem EXTR-01-Zahlenparser und vollständigem Anhang B.1-B.3 in der Sollwertdatei.**

## Performance

- **Duration:** ~60 min
- **Tasks:** 3
- **Commits:** 5
- **Files created:** 13
- **Files modified:** 3

## Accomplishments
- Tracer-Kette PDF -> Wörter mit Koordinaten -> Zeilen-Wörterbuch-Abgleich -> Langformat-CSV -> Regel-4-Prüfung -> Markdown-Bericht funktioniert end-to-end, aus beiden CLIs und aus pytest (D-01, D-08, D-10, D-11, D-12)
- `ergebnisplan.csv` enthält alle 33 Gesamtergebnisplan-Zeilen (inkl. der 5 Nachrichtlich-Zeilen 29-33, extrahiert aber von allen Prüfregeln ausgenommen) mit gedrucktem Vorzeichen, eigener Operator-Spalte und `pdf_seite`
- `ostbevern/zahlen.py` deckt jetzt alle EXTR-01-Formen ab (deutsches Tausenderformat, ASCII- und U+2212-Minus, „–" als kein Wert, C/€ als Eurozeichen, angeklebte Beträge) mit 21 reinen String-Testfunktionen
- `pipeline/jahrgaenge/2026_sollwerte.toml` hält Anhang B.1 vollständig (21 Zeilen x 6 Jahre = 126 Werte), B.2 (Gesamtfinanzplan Ansatz/VE) und B.3 (15 Teilergebnispläne je PB + Summe); `lade_sollwerte` validiert alle Tabellen vollständig

## Task Commits

Jede Aufgabe wurde atomar committet:

1. **Task 1: Tracer — Gesamtergebnisplan end-to-end** - `80c5ad0` (feat)
2. **Task 2: Number parser complete per EXTR-01** - `676ae9e` (test, RED) + `2c48f60` (feat, GREEN)
3. **Task 3: Sollwerte Anhang B.1-B.3 transcribed** - `d351003` (test, RED) + `24d942c` (feat, GREEN)

_Kein REFACTOR-Commit nötig — die GREEN-Implementierungen blieben minimal und sauber._

## Files Created/Modified
- `pipeline/ostbevern/pdf.py` - einziger pdfplumber-Wrapper, 1-basierte zeilengruppierte Seiten
- `pipeline/ostbevern/zahlen.py` - vollständiger EXTR-01-Zahlenparser
- `pipeline/ostbevern/zeilen.py` - Zeilen-Wörterbuch Gesamtergebnisplan + Normalisierung
- `pipeline/ostbevern/schema.py` - zentrales CSV-Schema/IO
- `pipeline/ostbevern/plaene.py` - Plantabellen-Parser mit D-08-Abbruch
- `pipeline/ostbevern/pruefung.py` - Regel 4 + Berichtserzeugung (D-01)
- `pipeline/02_plaene_extrahieren.py`, `pipeline/06_pruefen.py` - dünne typer-CLIs
- `pipeline/ostbevern/konfiguration.py` - `lade_sollwerte` um B.2/B.3-Validierung erweitert
- `pipeline/jahrgaenge/2026_sollwerte.toml` - Anhang B.1 komplett, B.2, B.3
- `pipeline/tests/test_zahlen.py`, `test_plaene.py`, `test_pruefung.py` - neue Testmodule
- `pipeline/tests/test_konfiguration.py` - 4 neue Tests für erweiterte Sollwerte-Validierung
- `daten/aufbereitet/ergebnisplan.csv`, `daten/pruefberichte/konsistenz.md` - generierte Daten

## Decisions Made
- Nachrichtlich-Zeilen 29-33 werden extrahiert (kein Abbruch), aber von allen Prüfregeln und Anhang B ausgenommen (Research Open Question 1, bewusst gewählt statt Abbruch vor Zeile 29)
- `trenne_angeklebten_betrag` wird in `plaene.py` nur auf Wörter in der Betragsspaltenzone angewendet, nie auf das gesamte Label — die Funktion selbst ist spaltenblind (dokumentiert mit Regressionstest)
- Spaltenzuordnung über kleinsten x1-Abstand zur Jahresspalte, Toleranz = halber kleinster Spaltenabstand (verifiziert gegen echte PDF-Koordinaten der Seiten 62/66)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Zwischenüberschriften-Erkennung verglich normalisierten Text gegen unnormalisierte Wörterbuch-Strings**
- **Found during:** Task 1, erster Lauf von `02_plaene_extrahieren.py`
- **Issue:** `lies_plantabelle` verglich `normalisiere_bezeichnung(text)` gegen die rohen (mit Leerzeichen) `ZWISCHENUEBERSCHRIFTEN`-Strings, sodass die „Nachrichtlich: …"-Zeile nie erkannt wurde und stattdessen an Zeile 28 angehängt wurde
- **Fix:** `ZWISCHENUEBERSCHRIFTEN`-Einträge werden beim Aufbau der Vergleichsmenge ebenfalls durch `normalisiere_bezeichnung` geschickt
- **Files modified:** `pipeline/ostbevern/plaene.py`
- **Verification:** `02_plaene_extrahieren.py --jahr 2026` lief danach fehlerfrei durch, 198 Zeilen geschrieben
- **Committed in:** `80c5ad0` (Teil des Task-1-Commits, vor dem ersten erfolgreichen Lauf korrigiert)

---

**Total deviations:** 1 auto-fixed (1 Bug)
**Impact on plan:** Notwendige Korrektur für korrekte Funktion des Tracers. Kein Scope Creep.

## Issues Encountered
None.

## User Setup Required
None - keine externen Dienste erforderlich.

## Next Phase Readiness
- Module `pdf.py`, `schema.py`, `zeilen.py`, `plaene.py`, `pruefung.py` stehen für Plan 02-02 (Seitenklassifikation) und 02-03 (Gesamtfinanzplan) bereit; die Interfaces (`PdfDokument.zeilen`, `schema.schreibe_plan_csv`/`lies_plan_csv`, `plaene.lies_plantabelle`, `pruefung.pruefe_alles`) sind stabil gehalten
- `ZEILEN`-Wörterbuch deckt bislang nur `gesamtergebnisplan`; `teilergebnisplan`, `gesamtfinanzplan`, `teilfinanzplan` folgen in 02-03/02-04
- Keine Blocker für die nächsten Pläne dieser Phase

---
*Phase: 02-kernzahlen*
*Completed: 2026-10-01*

## Self-Check: PASSED

All 16 files claimed as created/modified verified present on disk; all 5 commit hashes (80c5ad0, 676ae9e, 2c48f60, d351003, 24d942c) verified present in `git log --oneline --all`.
