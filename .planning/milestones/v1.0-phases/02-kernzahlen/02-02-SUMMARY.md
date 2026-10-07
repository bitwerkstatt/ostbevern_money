---
phase: 02-kernzahlen
plan: 02
subsystem: pipeline
tags: [pdfplumber, polars, typer, pytest, toml, csv]

requires:
  - phase: 02-01
    provides: "pdf.py (PdfDokument.zeilen mit Textzeile.groesse/x0/text_ohne_leerzeichen), schema.py (schreibe_csv/lies_csv generics), konfiguration.py (lade_jahrgang/lade_sollwerte)"
provides:
  - "ostbevern/seiten.py: Schritt-01-Logik — SeitenFehler, Seitenkopf, Seite, verbinde_namensteile, klassifiziere_dokument, baue_hierarchie, klassifiziere_seiten"
  - "01_seiten_klassifizieren.py: dünner typer-CLI (--jahr)"
  - "ostbevern/schema.py: SEITEN_SPALTEN/HIERARCHIE_SPALTEN + schreibe/lies-Helfer"
  - "ostbevern/konfiguration.py: kopfzeilen.produktgruppe/seitentypen (Pflicht), Seitenbereiche-Überlappungsprüfung, anhang_a-Validierung in lade_sollwerte"
  - "daten/zwischen/seiten.csv (400 Seiten, 0 unbekannt), daten/aufbereitet/hierarchie.csv (15 PB, 48 PG davon 40 synthetisch, 63 Produkte)"
  - "pipeline/jahrgaenge/2026_sollwerte.toml: [anhang_a] Produktverzeichnis (86 Einträge)"
affects: [02-04-teilplaene, 02-05-weitere-pruefregeln, 04-app-json]

actuals:
  tokens: 17189
  tasks: 2
  commits: 4
  plan_head_before: 25dca42f7c5b41b2fef9b0b7d14017f096523692
  plan_head_after: 91e39a1b885b4d9da2dc98516f2a35dfb1020559

tech-stack:
  added: []
  patterns:
    - "Kopfzeilen-Parsing über Font-Größe + x0-Einzug (Fortsetzungszeile vs. Abschnittstitel), mit expliziter Float-Toleranz statt exakter Gleichheit (pdfplumber liefert geringes Rauschen auf identischen x0-Werten)"
    - "D-17 Fortsetzungsseiten-Vererbung: eine Teilplanseite ohne passendes Seitentyp-Muster erbt typ/pb/pg/produkt der Vorgängerseite, sofern diese ebenfalls eine Teilplanseite mit identischem Knoten ist — sonst unbekannt statt Abbruch"
    - "Synthetische Produktgruppen (D-14) werden über eine zweistufige Gruppierung gebaut: erst alle Produkte je abgeleitetem PG-Code sammeln, dann Name vom niedrigstcodigen Produkt und pdf_seite_start als Minimum über die Gruppe bestimmen (robust gegen Einfüge-/Seitenreihenfolge)"

key-files:
  created:
    - pipeline/ostbevern/seiten.py
    - pipeline/01_seiten_klassifizieren.py
    - pipeline/tests/test_seiten.py
    - pipeline/tests/test_hierarchie.py
    - daten/zwischen/seiten.csv
    - daten/aufbereitet/hierarchie.csv
  modified:
    - pipeline/jahrgaenge/2026.toml
    - pipeline/jahrgaenge/2026_sollwerte.toml
    - pipeline/ostbevern/konfiguration.py
    - pipeline/ostbevern/schema.py
    - pipeline/tests/test_konfiguration.py

key-decisions:
  - "Seite 65 (Teilplan-Trennseite ohne Kopfzeile) bleibt außerhalb von [seitenbereiche].teilplaene (66-282) und fällt auf typ=sonstige, statt als unbekannt im Teilplanbereich zu erscheinen"
  - "kopfzeilen.seitentypen wurde von einer Liste zu einer TOML-Subtabelle (Name -> Regex) umgebaut, damit jeder Seitentyp ein eigenes, gegen den Inhaltstext geprüftes Muster trägt (nicht nur einen Titel-String)"
  - "Float-Toleranz (x0 + 5.0, Größe ± 0.5) für die Fortsetzungszeilen-Erkennung nötig: pdfplumber liefert für Abschnittstitel wie 'Produktinformationen' gelegentlich ein x0, das durch Rundungsfehler minimal über dem der Kopfzeile liegt, was eine exakte '>'-Prüfung fälschlich als Fortsetzung einstufte (Rule 1 Bugfix während Task 1)"

requirements-completed: [EXTR-02, EXTR-03]

coverage:
  - id: D1
    description: "seiten.csv klassifiziert alle 400 PDF-Seiten (Kapitelname außerhalb der Teilpläne, feines Typ-Vokabular innerhalb, Fortsetzungsseiten-Vererbung), 0 unbekannt für 2026"
    requirement: "EXTR-02"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_seiten.py (8 Testfunktionen, echte PDF-Seiten, D-07)"
        status: pass
      - kind: integration
        ref: "uv run --directory pipeline python 01_seiten_klassifizieren.py --jahr 2026"
        status: pass
    human_judgment: false
  - id: D2
    description: "hierarchie.csv mit 15 PB, 48 PG (40 synthetisch nach D-14) und 63 Produkten; alle Namen/Startseiten stimmen mit Anhang A überein (D-19, Roadmap SC 1)"
    requirement: "EXTR-03"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_hierarchie.py (5 Testfunktionen, eingecheckte CSVs, D-06)"
        status: pass
      - kind: integration
        ref: "uv run --directory pipeline python 01_seiten_klassifizieren.py --jahr 2026"
        status: pass
    human_judgment: false
  - id: D3
    description: "lade_sollwerte validiert Anhang A vollständig (2-/4-/6-stelliger Code, Name, pdf_seite >= 1); lade_jahrgang validiert kopfzeilen.produktgruppe/seitentypen und lehnt überlappende Seitenbereiche ab"
    requirement: "EXTR-03"
    verification:
      - kind: unit
        ref: "pipeline/tests/test_konfiguration.py (6 neue Testfunktionen)"
        status: pass
    human_judgment: false

duration: 70min
completed: 2026-10-01
status: complete
---

# Phase 2 Plan 2: Seitenklassifikation und PB/PG/Produkt-Hierarchie Summary

**Alle 400 PDF-Seiten werden aus den Kopfzeilen-Mustern der Jahrgangsdatei klassifiziert (0 unbekannt für 2026), und daraus entsteht hierarchie.csv mit 15 Produktbereichen, 48 Produktgruppen (40 synthetisch nach D-14) und 63 Produkten, deren Namen und Startseiten exakt gegen das transkribierte Anhang-A-Produktverzeichnis geprüft sind.**

## Performance

- **Duration:** ~70 min
- **Tasks:** 2
- **Commits:** 4
- **Files created:** 6
- **Files modified:** 5

## Accomplishments
- `ostbevern/seiten.py` klassifiziert jede der 400 PDF-Seiten: Kapitelname außerhalb der Teilpläne, feines Typ-Vokabular (`produktinformationen`, `grundzahlen`, `teilergebnisplan`, `erlaeuterungen`, `teilfinanzplan`, `investitionen_pb`/`investitionen_produkt`) innerhalb, mit Fortsetzungsseiten-Vererbung (D-17) und keiner einzigen `unbekannt`-Seite für 2026
- `baue_hierarchie` leitet aus den Kopfzeilen 15 PB, 8 gedruckte und 40 synthetische PG sowie 63 Produkte ab; alle Start-seiten und Namen (nach Entfernen von Leerzeichen, case-insensitiv) stimmen mit dem neu transkribierten Anhang-A-Produktverzeichnis (86 Einträge) in `2026_sollwerte.toml` überein
- `kopfzeilen.produktgruppe` und die `[kopfzeilen.seitentypen]`-Subtabelle wurden zu `2026.toml` hinzugefügt und werden von `lade_jahrgang` vollständig validiert (Pflichtschlüssel, Regex-Kompilierbarkeit je Muster, Seitenbereichs-Überlappung)
- `lade_sollwerte` validiert Anhang A vollständig: Code muss 2-, 4- oder 6-stellig sein, jeder Eintrag braucht einen nicht-leeren Namen und eine gültige `pdf_seite`

## Task Commits

Jede Aufgabe wurde über RED/GREEN-Paare atomar committet:

1. **Task 1: Tracer — Kopfzeilen-Konfiguration -> Seitenklassifikator -> seiten.csv** - `b11fcac` (test, RED) + `70d50cb` (feat, GREEN)
2. **Task 2: hierarchie.csv mit synthetischen Produktgruppen** - `bc8cf1e` (test, RED) + `91e39a1` (feat, GREEN)

_Kein REFACTOR-Commit nötig — die GREEN-Implementierungen blieben minimal._

## Files Created/Modified
- `pipeline/ostbevern/seiten.py` - Schritt-01-Logik: Kopfzeilen-Parsing, Seitenklassifikation, Hierarchie-Aufbau
- `pipeline/01_seiten_klassifizieren.py` - dünner typer-CLI
- `pipeline/ostbevern/schema.py` - `SEITEN_SPALTEN`/`HIERARCHIE_SPALTEN` + IO-Helfer
- `pipeline/ostbevern/konfiguration.py` - `Kopfzeilen.produktgruppe`/`seitentypen`, `PFLICHT_SEITENTYPEN`, Seitenbereichs-Überlappungsprüfung, `anhang_a`-Validierung
- `pipeline/jahrgaenge/2026.toml` - `kopfzeilen.produktgruppe`, `[kopfzeilen.seitentypen]`, korrigierte `teilplaene` (66-282) und `zuwendungen_fraktionen` (307-308)
- `pipeline/jahrgaenge/2026_sollwerte.toml` - `[anhang_a]` (86 Einträge)
- `pipeline/tests/test_seiten.py`, `test_hierarchie.py` - neue Testmodule
- `pipeline/tests/test_konfiguration.py` - 6 neue Tests
- `daten/zwischen/seiten.csv`, `daten/aufbereitet/hierarchie.csv` - generierte Daten

## Decisions Made
- Seite 65 (Teilplan-Trennseite) liegt außerhalb von `teilplaene` und wird `sonstige`, statt im Teilplanbereich als `unbekannt` zu erscheinen
- `kopfzeilen.seitentypen` ist jetzt eine TOML-Subtabelle (Name -> Regex gegen den Inhaltstext), nicht mehr eine Liste von Titel-Strings
- Fortsetzungszeilen-Erkennung braucht eine Float-Toleranz (x0 + 5.0, Größe ± 0.5), da pdfplumber für gleich positionierte Abschnittstitel gelegentlich minimal abweichende x0-Werte liefert (Rundungsrauschen)

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Abschnittstitel wurden durch Float-Rauschen fälschlich als Kopfzeilen-Fortsetzung erkannt**
- **Found during:** Task 1, erster Testlauf von `tests/test_seiten.py`
- **Issue:** `_lies_kopfzeilenblock` verglich `zeile.x0 > kopf_zeile.x0` exakt; auf S. 81 lieferte pdfplumber für den Abschnittstitel "Produktinformationen" x0=42.52000000000001 gegenüber x0=42.52 der Kopfzeile — der Titel wurde als Namensfortsetzung verschluckt, wodurch die erste echte Inhaltszeile kein Seitentyp-Muster mehr traf und die Seite als `unbekannt` endete (33 betroffene Seiten)
- **Fix:** Toleranzkonstanten `_KOPFZEILE_X_TOLERANZ = 5.0` und `_KOPFZEILE_GROESSE_TOLERANZ = 0.5` eingeführt; eine Zeile gilt nur noch als Fortsetzung, wenn ihr x0 den Kopfzeilen-x0 um mehr als 5 Punkte überschreitet (echte Einrückung liegt bei ~207 Punkten)
- **Files modified:** `pipeline/ostbevern/seiten.py`
- **Verification:** `test_keine_unbekannten_teilplanseiten` und die volle Suite (86 Tests) grün; `01_seiten_klassifizieren.py --jahr 2026` meldet 0 unbekannt
- **Committed in:** `70d50cb` (Teil des Task-1-GREEN-Commits, vor dem ersten erfolgreichen Testlauf korrigiert)

---

**Total deviations:** 1 auto-fixed (1 Bug)
**Impact on plan:** Notwendige Korrektur für korrekte Seitenklassifikation. Kein Scope Creep.

## Issues Encountered
None.

## User Setup Required
None - keine externen Dienste erforderlich.

## Next Phase Readiness
- `seiten.csv` und `hierarchie.csv` stehen für Plan 02-04 (Teilpläne) bereit: Typen `produktinformationen`, `grundzahlen`, `teilergebnisplan`, `erlaeuterungen`, `teilfinanzplan`, `investitionen_pb`/`investitionen_produkt` sowie die PB/PG(synthetisch)/Produkt-Knoten mit Eltern-Codes
- `kopfzeilen.seitentypen` (TOML-Subtabelle) und `Kopfzeilen.produktgruppe` sind stabile, validierte Konfigurationsschnittstellen für spätere Jahrgänge
- Dieser Plan modifiziert `pipeline/ostbevern/{pdf,plaene,pruefung,zeilen}.py`, `daten/aufbereitet/ergebnisplan.csv` und `daten/pruefberichte/*` nicht (Scope-Trennung zu 02-03); `git diff --exit-code daten/pruefberichte/` bestätigt das
- Keine Blocker für die nächsten Pläne dieser Phase

---
*Phase: 02-kernzahlen*
*Completed: 2026-10-01*

## Self-Check: PASSED

All files claimed as created/modified verified present on disk; all 4 commit hashes (b11fcac, 70d50cb, bc8cf1e, 91e39a1) verified present in `git log --oneline --all`.
